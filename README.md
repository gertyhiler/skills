# Skills from everyday engineering

Reusable workflows I use with coding agents: verifying changes, delivering to an
environment, assessing releases, cleaning up worktrees, debugging runtime behavior,
and keeping tests and module boundaries useful.

These grew out of my project work. I share the procedures here so they can travel
between repositories without carrying company infrastructure or private context.

**The skill supplies the method. Your project supplies the operating contract.**
Commands, branches, environments, access and approval rules belong in your
repository's runbook, linked from `AGENTS.md`, or in direct project instructions.
Installing a skill never grants permission to deploy or discard work.

## Pick a skill

| Skill | When it helps |
| --- | --- |
| [verify-changes](skills/verify-changes/SKILL.md) | Choose proportionate checks and tie evidence to the actual diff or candidate. |
| [deliver-to](skills/deliver-to/SKILL.md) | Deliver into a named non-production environment without overwriting its history. |
| [check-release](skills/check-release/SKILL.md) | Assess the actual integration candidate; distinguish readiness from deployment. |
| [clean-worktrees](skills/clean-worktrees/SKILL.md) | Inventory completed worktrees and preserve unique history and local files. |
| [debug](skills/debug/SKILL.md) | Run a project-native debug session with a temporary collector, reproduction pauses, confirmation and marked cleanup. |
| [design-tests](skills/design-tests/SKILL.md) | Choose tests that protect observable behavior at the right level. |
| [review-tests](skills/review-tests/SKILL.md) | Review the confidence a test suite actually provides, without editing it. |
| [organize-code](skills/organize-code/SKILL.md) | Place code by ownership and keep primitives, compositions and internal modules distinct. |
| [review-delivery](skills/review-delivery/SKILL.md) | Review evidence behind a delivery or runtime-readiness claim. |
| [grafana-access](skills/grafana-access/SKILL.md) | Read bounded Loki logs and Prometheus metrics through a project-local access contract. |
| [postgresql-access](skills/postgresql-access/SKILL.md) | Read schema first, select the intended database and run bounded read-only queries. |
| [investigate](skills/investigate/SKILL.md) | Correlate code, logs and persisted state into facts, hypotheses and next actions. |

See [the investigation workflow](docs/investigation-workflow.md) for how I connect
skills with AGENTS.md, runbooks and ignored `.agents/local/.env.agents` files.

## Install only what you need

Use the [Skills CLI](https://github.com/vercel-labs/skills) from your consumer
repository:

```sh
npx skills add gertyhiler/skills --list
npx skills add gertyhiler/skills --skill verify-changes -a codex
```

Other supported agents can use the same Markdown skills. Alternatively, copy the
whole selected `skills/<name>/` directory into your agent's configured skill
location, including any supporting files. Never silently overwrite a local skill
with the same name. Review updates before replacing an installed copy.

The procedures are independently installable; no other skill in this repository
is required. `clean-worktrees` retains explicit-only invocation in its Codex
metadata. Other agent runtimes may not enforce that metadata; its instructions
still require a cleanup request and scoped authorization.

## Connect your project

Add pointers to the process documents you already maintain. Paths below are
examples, not required filenames:

```markdown
## Project workflow runbooks

- Verification: docs/runbooks/verification.md
- Environment delivery: docs/runbooks/delivery.md
- Release readiness: docs/runbooks/release.md
- Hosting access: docs/runbooks/hosting.md
- Runtime debugging: docs/runbooks/debugging.md
- Worktrees: docs/runbooks/worktrees.md
- Testing: docs/testing.md
- Architecture: docs/architecture.md
```

Link only documents that exist and that your selected skills need. A single
runbook with sections is enough. See [the project contract](docs/project-contract.md)
for the information each procedure needs. If a required input is missing, the
agent should identify the gap and continue independent inspection rather than
invent a branch, command or approval.

## How I use them

```text
Verify this diff against the project's testing policy.
Assess this branch against the current release target; do not merge it.
$deliver-to stage — deliver these commits using the project runbook.
Investigate this intermittent bug using temporary local traces.
Inventory completed worktrees; show what would be removed before deleting anything.
```

These are instruction workflows, not an autonomous platform or a guarantee of
correctness. Review their assumptions against your project and agent runtime.
Verification, review, publication, deployment and runtime acceptance are separate
claims, each requiring its own evidence.

## Maintain

Maintenance and executable skills use **Python 3.12+ through uv**. No Node runtime
or consumer application dependency is required. Git and Make are used for repository
maintenance. See [the runtime contract](docs/runtime.md) for isolated installation,
locked execution and migration from the earlier Node commands.

```sh
make setup
make verify
```

Checks validate skill metadata, local documentation links and invocation metadata.
`make test` runs isolated helper tests with fictional configuration and a local HTTP fixture.
An additional PostgreSQL integration test runs in CI against a disposable database.
Locally it runs only when `SKILLS_TEST_DATABASE_URL` points to a disposable test DB;
otherwise it is reported as skipped. Never set it to a real project database.
These tests do not execute workflows against your real environments.
For behavioral changes, use a small representative scenario and record what was
actually verified. Keep improvements driven by repeated work rather than growing
a universal rulebook. See [contributing](CONTRIBUTING.md) and
[scope and provenance](docs/scope.md).

MIT licensed. More of my tools and setup: [gertyhiler](https://github.com/gertyhiler).
