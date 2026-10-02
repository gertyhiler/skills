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
WRITE = re.compile(r"\b(insert|update|delete|merge|alter|drop|create|truncate|grant|revoke|vacuum|call|do|copy|comment|reindex|cluster|refresh|analyze|begin|start\s+transaction|commit|rollback|savepoint|release|lock|set|reset|discard|end|prepare|execute|deallocate)\b", re.I)

def connection_config(env):
    dsn = next((env[k] for k in DSN_KEYS if env.get(k)), None)
    if not dsn:
        raise AccessError("Set DATABASE_URL in the selected env file.")
    try:
        url = urlsplit(dsn)
        port = url.port or 5432
        if url.scheme not in ("postgres", "postgresql") or not all((url.hostname, url.username, url.password, url.path.strip('/'))) or url.fragment:
            raise ValueError()
        pairs = parse_qsl(url.query, strict_parsing=True)
        params = dict(pairs)
        if len(params) != len(pairs) or set(params) - {"sslmode", "application_name"}:
            raise ValueError()
    except ValueError:
        raise AccessError("Invalid PostgreSQL URL or unsupported connection parameters.") from None
    mode = params.get("sslmode", env.get("PGSSLMODE", "verify-full"))
    if mode not in ("verify-full", "disable"):
        raise AccessError("Use sslmode=verify-full; disable is only for a documented local connection/tunnel.")
    return dict(host=url.hostname, port=port, dbname=unquote(url.path[1:]),
                user=unquote(url.username), password=unquote(url.password),
                sslmode=mode, connect_timeout=10,
                application_name=params.get("application_name", "agent-investigation"),
                options="-c statement_timeout=15000 -c default_transaction_read_only=on")

async def _read_query(config, sql):
    # Explicit parameters prevent ambient PG credential fallback. Server enforces
    # read-only; prepare=True selects extended protocol and rejects multi-statements.
    conn = await psycopg.AsyncConnection.connect(**config, row_factory=dict_row)
    try:
        await conn.set_read_only(True)
        async def execute():
            async with conn.cursor() as cursor:
                await cursor.execute(sql, prepare=True)
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
        return asyncio.run(_read_query(config, sql))
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
        sql = args.sql if args.sql is not None else args.file.read_text(encoding="utf-8")
        if not sql.strip() or WRITE.search(sql):
            raise PolicyError("Blocked empty or write-capable SQL. Use the project's mutation workflow for writes.")
        if args.explain:
            sql = "EXPLAIN " + sql.rstrip().rstrip(';')
    config = connection_config(load_env(args.env_file))
    if args.command == "config":
        return {"runner": "python_psycopg", "host": config['host'], "database": config['dbname'], "sslmode": config['sslmode']}
    if args.command == "check":
        sql = "SELECT current_database() AS current_database, current_user AS current_user, current_setting('server_version') AS server_version"
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
