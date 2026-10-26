# /// script
# requires-python = ">=3.12"
# dependencies = ["psycopg[binary]==3.3.6", "python-dotenv==1.2.4"]
# ///
"""Read-only PostgreSQL CLI; never imports dependencies from the consumer project."""
import argparse
import asyncio
import os
import re
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, unquote
import psycopg
from psycopg.rows import dict_row
from access_common import AccessError, PolicyError, load_env, write_private, run

DSN_KEYS = ("DATABASE_URL", "DATABASE_DSN", "DB_DSN", "DSN", "DB", "POSTGRES_DSN", "POSTGRES_URL", "PGURL")
WRITE = re.compile(r"\b(insert|update|delete|merge|alter|drop|create|truncate|grant|revoke|vacuum|call|do|copy|comment|reindex|cluster|refresh|analyze|begin|start\s+transaction|commit|rollback|savepoint|release|lock|set|reset|discard|prepare|execute|deallocate)\b", re.I)

# Explicit-file configuration only. Never accept endpoint overrides in URL query
# parameters or arbitrary libpq options which could replace read-only settings.
PG_FIELDS = {
    "PGHOST": "host", "PGPORT": "port", "PGDATABASE": "dbname",
    "PGUSER": "user", "PGPASSWORD": "password", "PGSSLMODE": "sslmode",
    "PGSSLROOTCERT": "sslrootcert", "PGSSLCERT": "sslcert", "PGSSLKEY": "sslkey",
    "PGAPPNAME": "application_name", "PGCONNECT_TIMEOUT": "connect_timeout",
}
TLS_MODES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
URL_FIELDS = {"sslmode", "sslrootcert", "sslcert", "sslkey", "application_name",
              "connect_timeout", "schema", "uselibpqcompat", "pgbouncer",
              "connection_limit", "pool_timeout"}


def has_transaction_end(sql):
    """Distinguish transaction END from CASE endings, ignoring quoted content."""
    index, cases = 0, 0
    while index < len(sql):
        rest = sql[index:]
        if rest.startswith("--"):
            end = sql.find("\n", index + 2)
            index = len(sql) if end < 0 else end + 1
            continue
        if rest.startswith("/*"):
            depth, index = 1, index + 2
            while index < len(sql) and depth:
                if sql.startswith("/*", index):
                    depth, index = depth + 1, index + 2
                elif sql.startswith("*/", index):
                    depth, index = depth - 1, index + 2
                else:
                    index += 1
            continue
        quote = sql[index]
        if quote in ("'", '"'):
            escaped = quote == "'" and index > 0 and sql[index-1:index].lower() == "e"
            index += 1
            while index < len(sql):
                if escaped and sql[index] == "\\":
                    index += 2
                elif sql[index] == quote:
                    index += 1
                    if index < len(sql) and sql[index] == quote:
                        index += 1
                    else:
                        break
                else:
                    index += 1
            continue
        dollar = re.match(r"\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$", rest)
        if dollar:
            tag = dollar.group()
            end = sql.find(tag, index + len(tag))
            index = len(sql) if end < 0 else end + len(tag)
            continue
        word = re.match(r"[A-Za-z_][A-Za-z_0-9$]*", rest)
        if word:
            token = word.group().lower()
            if token == "case":
                cases += 1
            elif token == "end":
                if not cases:
                    return True
                cases -= 1
            index += len(word.group())
        else:
            index += 1
    return False


def connection_config(env, base_dir=None):
    config = {dest: env[key] for key, dest in PG_FIELDS.items() if env.get(key)}
    params = {}
    dsn = next((env[k] for k in DSN_KEYS if env.get(k)), None)
    if dsn:
        try:
            if re.search(r"%(?![0-9a-fA-F]{2})", dsn):
                raise ValueError()
            url = urlsplit(dsn)
            if url.scheme not in ("postgres", "postgresql") or url.fragment or not url.hostname:
                raise ValueError()
            pairs = parse_qsl(url.query, strict_parsing=True, keep_blank_values=True,
                              encoding="utf-8", errors="strict")
            params = dict(pairs)
            if len(params) != len(pairs):
                raise ValueError()
            config.update(host=url.hostname, port=url.port if url.port is not None else 5432)
            for name, value in (("user", url.username), ("password", url.password),
                                ("dbname", url.path[1:] or None)):
                if value is not None:
                    config[name] = unquote(value, errors="strict")
        except (ValueError, UnicodeError):
            raise AccessError("[configuration] Invalid PostgreSQL URL, encoding or duplicate parameters.") from None
        unknown = set(params) - URL_FIELDS
        if unknown:
            names = [key if re.fullmatch(r"[A-Za-z_]{1,40}", key) else "<invalid-name>"
                     for key in sorted(unknown)]
            raise AccessError("[configuration] Unsupported URL parameter(s): " + ", ".join(names))
        if "uselibpqcompat" in params and params["uselibpqcompat"] != "true":
            raise AccessError("[configuration] uselibpqcompat must be true when provided.")
        if "pgbouncer" in params and params["pgbouncer"] not in ("true", "false"):
            raise AccessError("[configuration] pgbouncer must be true or false.")
        # This CLI opens one connection, not an ORM connection pool.
        for key in ("connection_limit", "pool_timeout"):
            if key in params and (not params[key].isdigit() or
                                  (key == "connection_limit" and int(params[key]) < 1)):
                raise AccessError("[configuration] Invalid ORM pool setting: " + key)
        config.update({key: value for key, value in params.items()
                       if key in set(PG_FIELDS.values())})
    if not all(config.get(key) for key in ("host", "dbname", "user", "password")):
        raise AccessError("[configuration] Supply host, database, user and password via DATABASE_URL or PG* in the selected env file.")
    if any("\0" in str(value) for value in config.values()):
        raise AccessError("[configuration] Connection fields cannot contain NUL bytes.")
    try:
        config["port"] = int(config.get("port", 5432))
        config["connect_timeout"] = int(config.get("connect_timeout", 10))
        if not 1 <= config["port"] <= 65535 or not 1 <= config["connect_timeout"] <= 60:
            raise ValueError()
    except (ValueError, TypeError):
        raise AccessError("[configuration] Port must be 1..65535; connect_timeout must be 1..60 seconds.") from None
    config.setdefault("sslmode", "verify-full" if config.get("sslrootcert") == "system" else "prefer")
    if config["sslmode"] not in TLS_MODES:
        raise AccessError("[configuration] Unsupported sslmode; use a standard libpq TLS mode.")
    for key in ("sslrootcert", "sslcert", "sslkey"):
        if key in config:
            if key == "sslrootcert" and config[key] == "system":
                continue
            path = Path(config[key]).expanduser()
            path = path if path.is_absolute() else Path(base_dir or Path.cwd()) / path
            if not path.is_file():
                raise AccessError("[configuration] Certificate file is missing or not a file: " + key)
            config[key] = str(path.resolve())
    if "schema" in params:
        if not params["schema"] or "\0" in params["schema"]:
            raise AccessError("[configuration] schema must be a nonempty PostgreSQL identifier.")
        config["_schema"] = params["schema"]
    config.setdefault("application_name", "agent-investigation")
    config["options"] = "-c statement_timeout=15000 -c default_transaction_read_only=on"
    return config


def database_error(error):
    """Classify privately; never return server messages, SQL or parameter values."""
    state = getattr(error, "sqlstate", None)
    if state and not re.fullmatch(r"[A-Z0-9]{5}", state):
        state = None
    categories = {"28": ("authentication", "Check the selected credentials and authentication policy."),
                  "3D": ("database", "The requested database does not exist."),
                  "3F": ("schema", "The requested schema does not exist."),
                  "08": ("connection", "The server connection failed."),
                  "53": ("server-capacity", "The server cannot accept this operation now.")}
    exact = {"42501": ("permissions", "The role lacks permission for this operation."),
             "25006": ("read-only", "The server rejected a write in the read-only transaction."),
             "57014": ("timeout", "The statement was cancelled or exceeded its time limit."),
             "42P01": ("schema", "Relation not found; check the selected schema and code model."),
             "42703": ("schema", "Column not found; check the query against the database schema.")}
    if state:
        category, hint = exact.get(state, categories.get(state[:2], ("sql", "The server rejected the SQL statement.")))
    else:
        message = str(error).lower()  # internal only
        if "password authentication" in message or "authentication failed" in message:
            category, hint = "authentication", "Check the selected credentials and authentication policy."
        elif "does not exist" in message and "database" in message:
            # libpq can combine an IPv6 refusal with an IPv4 server response.
            # Prefer the substantive server error over transport failures.
            category, hint = "database", "The requested database does not exist."
        elif "no pg_hba.conf entry" in message:
            category, hint = "authentication", "The server authentication policy rejects this connection."
        elif "certificate" in message or "ssl" in message or "tls" in message:
            category, hint = "tls", "Check sslmode, CA/client certificate files and server hostname; explicit TLS requirements were preserved."
        elif "translate host" in message or "name or service" in message or "nodename" in message:
            category, hint = "dns", "The selected hostname could not be resolved."
        elif "timeout" in message or "timed out" in message:
            category, hint = "timeout", "The connection or query exceeded its time limit."
        elif "refused" in message:
            category, hint = "connection-refused", "Check server availability and the selected host/port."
        else:
            category, hint = "connection", "Check network reachability and the server's connection policy."
    return AccessError(f"[{category}] {hint}" + (f" SQLSTATE={state}" if state else ""))

async def _read_query(config, sql):
    # Explicit parameters prevent ambient PG credential fallback. Server enforces
    # read-only; pipeline mode selects extended protocol and rejects multi-statements.
    config = dict(config)
    schema = config.pop("_schema", None)
    conn = await psycopg.AsyncConnection.connect(**config, row_factory=dict_row,
                                                prepare_threshold=None)
    try:
        await conn.set_read_only(True)
        async def execute():
            async with conn.cursor() as cursor:
                if schema is not None:
                    await cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_namespace WHERE nspname = %s) AS present", (schema,))
                    if not (await cursor.fetchone())["present"]:
                        raise AccessError("[schema] The requested schema does not exist.")
                    await cursor.execute("SELECT pg_catalog.has_schema_privilege(current_user, %s, 'USAGE') AS allowed", (schema,))
                    if not (await cursor.fetchone())["allowed"]:
                        raise AccessError("[permissions] The role lacks USAGE on the requested schema.")
                    # Quote the identifier, not SQL text or libpq startup options.
                    quoted = '"' + schema.replace('"', '""') + '"'
                    await cursor.execute("SELECT pg_catalog.set_config('search_path', %s, true)", (quoted,))
                # Pipeline mode forces extended protocol even without parameters;
                # empty bindings alone would allow Psycopg to use simple protocol.
                async with conn.pipeline() as pipeline:
                    await cursor.execute(sql, prepare=False)
                    await pipeline.sync()
                    rows = await cursor.fetchall()
                return {"rowCount": cursor.rowcount, "rows": rows}
        return await asyncio.wait_for(execute(), timeout=20)
    finally:
        try:
            await asyncio.wait_for(conn.rollback(), timeout=5)
        finally:
            await conn.close()


def read_query(config, sql):
    # libpq merges PGHOSTADDR/PGSERVICE/etc even with explicit host credentials.
    # This is a dedicated CLI, not a concurrent in-process application library.
    ambient = {key: value for key, value in os.environ.items() if key.startswith("PG")}
    try:
        for key in ambient:
            del os.environ[key]
        try:
            return asyncio.run(_read_query(config, sql))
        except psycopg.Error as error:
            raise database_error(error) from None
        except TimeoutError:
            raise AccessError("[timeout] Query exceeded the client time limit.") from None
    finally:
        os.environ.update(ambient)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("config", "check", "query", "schema"):
        p = sub.add_parser(name)
        p.add_argument("--env-file")
        p.add_argument("--json", action="store_true", help="JSON is always the output format")
        if name == "query":
            source = p.add_mutually_exclusive_group(required=True)
            source.add_argument("--sql")
            source.add_argument("--file", type=Path)
            p.add_argument("--explain", action="store_true")
        if name == "schema":
            p.add_argument("--output", type=Path)
    args = parser.parse_args()
    sql = None
    if args.command == "query":
        try:
            sql = args.sql if args.sql is not None else args.file.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            raise AccessError("[configuration] Cannot read the selected SQL file as UTF-8.") from None
        if not sql.strip() or WRITE.search(sql) or has_transaction_end(sql):
            raise PolicyError("Blocked empty or write-capable SQL. Use the project's mutation workflow for writes.")
        if args.explain:
            sql = "EXPLAIN " + sql.rstrip().rstrip(';')
    env, env_path = load_env(args.env_file, with_path=True)
    config = connection_config(env, env_path.parent)
    if args.command == "config":
        return {"runner": "python_psycopg", "host": config['host'], "database": config['dbname'], "sslmode": config['sslmode'], "schema": config.get("_schema"),
                "tlsPolicy": "opportunistic" if config["sslmode"] in ("prefer", "allow") else "explicit"}
    if args.command == "check":
        sql = "SELECT current_database() AS current_database, current_user AS current_user, current_setting('server_version') AS server_version, current_schema() AS current_schema, current_setting('transaction_read_only') AS transaction_read_only, (SELECT ssl FROM pg_catalog.pg_stat_ssl WHERE pid = pg_backend_pid()) AS tls_active"
    elif args.command == "schema":
        sql = Path(__file__).with_name('catalog.sql').read_text(encoding="utf-8")
    result = read_query(config, sql)
    if args.command == "schema" and args.output:
        import json
        write_private(args.output, json.dumps(result['rows'], indent=2, default=str) + '\n')
        return {"output": str(args.output), "rowCount": result['rowCount']}
    return result

if __name__ == "__main__":
    raise SystemExit(run(main))
