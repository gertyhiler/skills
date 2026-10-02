---
name: postgresql-access
description: Read PostgreSQL evidence using project-local env configuration and Node pg. Use to recover schema from code, verify the selected database and run narrow investigation queries; bundled helpers do not support mutations.
---

# PostgreSQL access

Use the consumer AGENTS.md/runbook to identify the database environment, schema
source and access policy. Read [the access contract](references/access.md) before
first use. Load `.agents/local/.env.agents` as data, never through shell source.
Do not print env files, full DSNs, passwords or raw authentication errors.

## Schema-first sequence

1. Identify symptom, IDs, time window and intended environment. Read repository
   schema/models/migrations and query code before contacting the database.
2. Decide which evidence requires a live read. Do not dump the catalog when code
   already provides the relevant schema. Runtime-only objects or schema drift
   justify targeted catalog inspection.
3. Resolve the selected env file and consumer `pg` dependency with probe-runner.
   Verify connection; compare database/user metadata with the project's intended
   environment. Stop on a mismatch or failed connection, without falling back.
4. Draft a narrow SELECT from known columns and IDs, bounded by LIMIT/time range.
   Inspect suspiciously expensive reads with plain EXPLAIN, not EXPLAIN ANALYZE.
   Avoid invoking unfamiliar functions: even SELECT can trigger side effects.
5. Execute through the read-only helper. Report query, retrieval time and relevant
   rows, distinguishing current state from persisted event history. Current data
   cannot establish the full historical sequence on its own.
6. Cross-check with code and logs when needed. If mutation is necessary, describe
   it separately and use the project's authorized mutation workflow. This helper
   has no write override, even when credentials are more privileged.

## Commands

Node 22+ and `pg` installed/resolvable from the consumer Git root are required.
Run from that checkout; set `skill_dir` to the installed location. If `pg` is
missing, report the prerequisite; do not silently install a dependency.

```sh
skill_dir=.agents/skills/postgresql-access
node "$skill_dir/scripts/probe-runner.mjs" --json
node "$skill_dir/scripts/check-connection.mjs" --json
node "$skill_dir/scripts/run-query.mjs" --sql 'SELECT current_timestamp;'
node "$skill_dir/scripts/run-query.mjs" --file .agents/local/evidence/query.sql
```

Each accepts `--env-file PATH`. `dump-schema.mjs --catalog` reads catalog columns
when necessary; it is not a DDL/backup exporter. `--output PATH` creates a new
private file rather than overwriting existing evidence. Query output may contain
personal data: select only required fields and redact before publication.

The runner uses a read-only transaction and the extended query protocol (one SQL
statement), with bounded connection/query timeouts. Its conservative keyword
filter can reject harmless SQL containing write-related words. It is not a SQL
sandbox: use a least-privileged read-only role and do not call side-effecting
functions. Do not weaken restrictions to make an investigation query pass.
