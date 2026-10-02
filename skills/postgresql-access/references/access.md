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

TLS defaults to certificate verification (`verify-full`). The helper accepts only
`verify-full` or `disable`; use disable solely for the documented local connection
or tunnel. Private CA or other authentication requirements belong in the project's
adapter. Never disable verification to work around an unexplained TLS error.
The optional application_name URL parameter is supported; other URL parameters
are rejected to avoid hidden connection overrides.

Use a dedicated role with only the required SELECT permissions. Read-only
transactions and a keyword check are defense in depth, not a boundary against
arbitrary functions or external side effects. Statement timeout is 15 seconds;
client query timeout 20 seconds and connection timeout 10 seconds. Split or
optimize queries rather than automatically removing these bounds.

Diagnostics omit credentials and URL query parameters, but database/host names
and returned rows may still be sensitive. Raw database errors are suppressed.
If a query fails, inspect its schema and use approved local diagnostics; do not
print a full connection object to debug access.
