# PostgreSQL configuration

Run the bundled script with uv; pinned Python and binary Psycopg dependencies are
installed in isolation, without application dependencies or a local PostgreSQL SDK.
Keep the script lockfile and sibling resources when installing the skill.

Only `.agents/local/.env.agents` in the nearest consumer Git checkout is discovered.
Pass `--env-file PATH` for any other file. Parse it as dotenv data, never source it.
No application env, parent checkout or ambient credential fallback is used.

## Connection inputs

Supply DATABASE_URL (or DATABASE_DSN, DB_DSN, DSN, DB, POSTGRES_DSN, POSTGRES_URL,
PGURL in that priority order), or PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.
Host, database, user and password are required. URL fields override matching PG*
fields; missing URL fields can use fields from the same selected env file.
A URL without a port uses 5432. Percent-encoded credentials are decoded literally.
Each env file selects one environment; never retry against another file or host.

Supported URL parameters:

- `schema`: select exactly this PostgreSQL schema, including quoted identifiers.
  It must exist and allow USAGE. The helper sets a transaction-local search_path;
  it does not create a schema or rewrite the env file. Without schema, use the
  database role's search_path. Qualified SQL names still select their own schema.
- `sslmode`, `sslrootcert`, `sslcert`, `sslkey`: native libpq TLS settings.
- `application_name`, `connect_timeout`: connection metadata and timeout (1–60
  seconds; default 10). Query timeouts remain bounded independently.
- `uselibpqcompat=true`: accepted Node compatibility marker, not passed to libpq.
- `pgbouncer=true|false`: accepted; all reads use extended protocol without named
  prepared statements. This is suitable for transaction pooling, not statement pooling.
- `connection_limit` (positive integer), `pool_timeout` (nonnegative integer):
  accepted Prisma pool settings, irrelevant to this single-connection CLI.

Duplicate or unknown parameters produce a configuration error naming the parameter
without its value. Arbitrary options and URL query endpoint/credential overrides
are rejected; use URL authority/path or PG* fields instead.

## TLS

URL TLS parameters override PGSSLMODE, PGSSLROOTCERT, PGSSLCERT and PGSSLKEY in the
selected file. Relative certificate paths resolve against that env file's directory;
absolute paths and `sslrootcert=system` are supported. System trust selects
`verify-full` when no mode was supplied, as required by libpq. Missing files are reported
before connection. PGAPPNAME and PGCONNECT_TIMEOUT are also supported.

With no explicit mode, use standard libpq `prefer`: try TLS, but allow a non-TLS
server. This is opportunistic encryption, not authenticated TLS. Choose explicit
`verify-full` with a trusted CA for certificate/hostname verification. `require`
requires encryption; `verify-ca` verifies the chain; `disable` disables TLS.
Explicit `allow` and `prefer` retain their native negotiation behavior. Never retry
with a weaker mode after an explicit require/verify failure. See
[libpq TLS semantics](https://www.postgresql.org/docs/current/libpq-ssl.html).
System libpq defaults such as ~/.postgresql certificate files can still apply;
explicit certificate paths make trust selection reproducible. No project adapter
is required to pass supported TLS settings.

## Queries and diagnostics

Use a least-privileged role. Every query runs in a read-only transaction, with
15-second server and 20-second client query timeouts; extended protocol rejects
multiple statements. No write override is available. The conservative keyword
filter may reject harmless SQL containing write-related words; it is not a SQL
sandbox. Do not invoke side-effecting functions during investigation.

`config` reports non-secret selection metadata and effective TLS policy. `check`
reports database/user, schema, read-only state and whether the connection uses TLS.
Errors distinguish configuration, DNS, connection refusal, authentication, TLS,
timeout, database/schema, permissions and SQL failures, with SQLSTATE when available.
Raw server messages, SQL values, passwords and full DSNs are never error output.
Some network/server failures can only be classified as connection failures.

Schema catalog output is metadata, not a DDL backup. Query rows can contain sensitive
information: select only required data and redact before publication.
