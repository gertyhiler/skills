# PostgreSQL configuration

Only the consumer checkout's `.agents/local/.env.agents` is discovered. Git's
nearest root includes worktrees and nested repositories; outside Git use cwd.
Pass `--env-file PATH` for another documented file. No application `.env`, parent
checkout or inherited database credential fallback is used. Values are parsed
without shell execution or interpolation. The skill uses its own locked Python dependencies through uv, independent of the
consumer's language, package manager or project environment.

Copy [the example](../assets/env.agents.example) into the ignored local directory.
Use DATABASE_URL with an explicit host, database, username and password. Legacy
DSN aliases are accepted, but DATABASE_URL takes precedence; keep one connection
per file. Configure separate files for separate environments and select explicitly.

TLS defaults to certificate and hostname verification (`verify-full`). Explicit
`sslmode` in the URL takes precedence over `PGSSLMODE` in the selected env file.
Supported modes are `verify-full`, `verify-ca`, `require` and `disable`, with native
[libpq semantics](https://www.postgresql.org/docs/current/libpq-ssl.html).
`require` requires encryption but does not generally verify the server identity;
`disable` is for a documented local connection or tunnel. Preserve the consumer's
explicit mode; never retry with weaker TLS after a connection error. Opportunistic
`allow`/`prefer` modes are rejected. Private CA configuration still belongs in the
project's adapter.

The optional `application_name` URL parameter is supported. Node connection URLs
may also contain `uselibpqcompat=true`: it is accepted and removed because Psycopg
already uses libpq. Other values (including false or empty) are rejected rather
than guessing Node-specific TLS semantics. Unknown or duplicate URL parameters
are rejected to avoid hidden connection overrides. Credentials need not be
rewritten when migrating a compatible Node URL to this Python helper.

Use a dedicated role with only the required SELECT permissions. Read-only
transactions and a keyword check are defense in depth, not a boundary against
arbitrary functions or external side effects. Statement timeout is 15 seconds;
client query timeout 20 seconds and connection timeout 10 seconds. Split or
optimize queries rather than automatically removing these bounds.

Diagnostics omit credentials and URL query parameters, but database/host names
and returned rows may still be sensitive. Raw database errors are suppressed.
If a query fails, inspect its schema and use approved local diagnostics; do not
print a full connection object to debug access.
