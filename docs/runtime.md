# Python runtime contract

All executable helpers, repository checks and tests use Python 3.12+. uv manages
Python and dependencies; Git and Make remain external utilities. Instruction-only
skills do not need a runtime. No Node, npm, shell env loader or consumer application
package is required for execution. The optional third-party Skills CLI is an
installation convenience, not a runtime requirement; copying a skill folder works.

## Generated project instrumentation

The Python rule applies to executable helpers shipped in this repository.
`debug` generates temporary collectors and trace calls in the
consumer project's own stack (for example TypeScript or Go). Those adapters use
the project's runtime and are removed after the debug session. They are not
additional runtimes required to install this skill collection.

## Independently installed skills

Keep the entire selected skill directory. Each CLI declares pinned dependencies
using PEP 723 metadata and carries a neighboring .py.lock file. Run from the
consumer checkout, specifying the actual installed path:

```sh
uv run --locked .agents/skills/grafana-access/scripts/grafana.py logs --expr '{service_name="example-api"}' --limit 100
uv run --locked .agents/skills/postgresql-access/scripts/postgres.py query --sql 'SELECT current_timestamp;'
```

uv creates an isolated dependency environment rather than modifying the consumer
project. First execution may download Python and packages; provision the cache
before offline work. Locked execution fails if metadata and lockfile disagree.
Use uv's --offline mode when network access is forbidden. This repository supports
macOS and Linux; platform-specific binary availability remains a prerequisite.

Both CLIs provide subcommand --help, JSON on stdout, safe diagnostics on stderr,
exit 0 for success, 1 for configuration/access/runtime failure and 2 for invalid
arguments or blocked SQL. --json is accepted for clarity; JSON is the default.
All access subcommands accept --env-file after the subcommand. Discovery uses the
nearest checkout's .agents/local/.env.agents and never application .env or ambient
credentials. The PostgreSQL CLI also clears ambient libpq PG* controls during
connection/query execution, so PGHOSTADDR or PGSERVICE cannot redirect it.
Environment parsing does not execute shell text or expand variables.

The small access_common.py module is vendored into each skill to avoid cross-skill
imports. Tests check they remain equal. Do not create a shared package dependency
just to install one skill. HTTP uses verified TLS, a total per-request deadline including response body and
no automatic redirects or ambient proxy settings. PostgreSQL uses verified TLS by
default, a 10-second connection timeout, 15-second server statement timeout and 20-second
client query timeout.
Read-only transactions and one-statement execution remain mandatory. Raw service
errors are suppressed; returned evidence can still contain sensitive application data.

## Repository maintenance

make setup runs uv sync --locked. make verify runs the structural validator and
Python unittest contracts. CI includes a disposable PostgreSQL fixture; local
integration requires SKILLS_TEST_DATABASE_URL pointing only to a disposable DB.
Repository dependencies are locked in uv.lock; script dependencies are locked per
CLI for independent installation. When updating a dependency, update both relevant
metadata and locks, then verify the isolated copied skill as well as the repository.

## Migration from the Node version

| Previous script | Python subcommand |
| --- | --- |
| grafana-env.mjs | grafana.py config |
| check-connection.mjs (Grafana) | grafana.py check |
| query-logs.mjs / export-logs.mjs | grafana.py logs, with --output for export |
| query-metrics.mjs | grafana.py metrics; --instant or range by default |
| inspect-metric.mjs | grafana.py labels |
| probe-runner.mjs | postgres.py config; no consumer pg dependency |
| check-connection.mjs (PostgreSQL) | postgres.py check |
| run-query.mjs | postgres.py query |
| dump-schema.mjs --catalog | postgres.py schema |

Use --datasource-uid instead of --loki-uid / --prometheus-uid. The Grafana shell
wrapper is removed; pass --env-file directly. JSON remains the output format,
but callers should migrate against the new subcommand output rather than assume
all legacy field names. PostgreSQL check now returns the same row envelope as
query. Private source repositories and their installed skills are not changed.
