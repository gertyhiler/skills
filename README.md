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
| [setup-runbooks](skills/setup-runbooks/SKILL.md) | Configure or reconcile project runbooks: inspect, preview, confirm, then write. |
| [verify-changes](skills/verify-changes/SKILL.md) | Choose proportionate checks and tie evidence to the actual diff or candidate. |
| [deliver-to](skills/deliver-to/SKILL.md) | Deliver into a named non-production environment without overwriting its history. |
| [check-release](skills/check-release/SKILL.md) | Assess the actual integration candidate; distinguish readiness from deployment. |
| [release-readiness](skills/release-readiness/SKILL.md) | Keep the existing release assessment entry point with the same `check-release` procedure. |
| [clean-worktrees](skills/clean-worktrees/SKILL.md) | Analyze all worktrees, present a cleanup plan in chat, then remove after confirmation. |
| [debug](skills/debug/SKILL.md) | Run a project-native debug session with a temporary collector, reproduction pauses, confirmation and marked cleanup. |
| [design-tests](skills/design-tests/SKILL.md) | Choose tests that protect observable behavior at the right level. |
| [review](skills/review/SKILL.md) | Coordinate independent review of one candidate through the project's workflow. |
| [review-spec](skills/review-spec/SKILL.md) | Trace implementation to approved requirements and domain rules. |
| [review-code](skills/review-code/SKILL.md) | Check implementation, placement, regressions and affected consumers. |
| [review-compatibility](skills/review-compatibility/SKILL.md) | Compare the candidate with the exact dependency revisions in the intended environment. |
| [review-tests](skills/review-tests/SKILL.md) | Review the confidence a test suite actually provides. |
| [review-design](skills/review-design/SKILL.md) | Compare a rendered interface with an approved design. |
| [review-accessibility](skills/review-accessibility/SKILL.md) | Review semantics, keyboard interaction and focus. |
| [review-seo](skills/review-seo/SKILL.md) | Review public routes and indexing behavior. |
| [review-docs](skills/review-docs/SKILL.md) | Verify affected documentation against its canonical sources. |
| [organize-code](skills/organize-code/SKILL.md) | Place code by ownership and keep primitives, compositions and internal modules distinct. |
| [review-delivery](skills/review-delivery/SKILL.md) | Review evidence behind a delivery or runtime-readiness claim. |
| [grafana-access](skills/grafana-access/SKILL.md) | Read bounded Loki logs and Prometheus metrics through a project-local access contract. |
| [postgresql-access](skills/postgresql-access/SKILL.md) | Read schema first, select the intended database and run bounded read-only queries. |
| [investigate](skills/investigate/SKILL.md) | Correlate code, logs and persisted state into facts, hypotheses and next actions. |

See [the investigation workflow](docs/investigation-workflow.md) for how I connect
skills with AGENTS.md, runbooks and ignored `.agents/local/.env.agents` files.

## Install only what you need

For skills without package dependencies, use the
[Skills CLI](https://github.com/vercel-labs/skills) from your consumer repository:

```sh
npx skills add gertyhiler/skills --list
npx skills add gertyhiler/skills --skill design-tests -a codex
```

### Install the review coordinator

Use [SkillsX 0.2.0 or later](https://github.com/gertyhiler/skillsx/releases/tag/v0.2.0)
in the consumer repository. Run `skillsx init` first if the project has no SkillsX
registry. Register each source URL once and reuse its existing source ID if
already registered.

```sh
skillsx source personal --url https://github.com/gertyhiler/skills.git --ref main
skillsx source matt --url https://github.com/mattpocock/skills.git
skillsx install review --source personal --path skills/review
skillsx verify
```

The [review manifest](skills/review/agents/skillsx.json) pins Matt Pocock's
`code-review` by Git URL, path and commit. SkillsX installs it alongside `review`
or reuses a matching entry. When a global or legacy skill also uses `code-review`,
resolve the project entry in `.agents/skills.registry.json` and open its installed
`SKILL.md`. A fresh dependency install uses `.agents/skills/code-review/SKILL.md`.

The project workflow selects any additional review directions and supporting
documents. Existing directions, including `review-code`, can be installed and
invoked directly. To control updates to your selected packages, use an approved
source ref or explicitly adopt updates from a tracked ref with `skillsx update`.

For a manual installation of a standalone skill, copy the entire selected
`skills/<name>/` directory to your agent's configured location. Review any existing
copy before replacing it.

Use `release-readiness` when the project already calls that entry point. Its
manifest installs the compatible `check-release` revision and its dependencies.
Install the listed dependencies explicitly when using an installer that does
not resolve the manifest.

`clean-worktrees` retains explicit-only invocation in its Codex metadata. Its
instructions require a cleanup request and scoped authorization in every runtime.

## Connect your project

Use `setup-runbooks` when you want help configuring or reconciling these pointers
and their project instructions. It inspects the repository and presents a concrete
draft for confirmation before writing. Existing runbooks can also satisfy the
contract directly; setup is not a prerequisite for using other skills.

Add pointers to the process documents you already maintain. Paths below are
examples, not required filenames:

```markdown
## Project workflow runbooks

- Review workflow: docs/workflows/review.md
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
$review — review this candidate using the project's workflow.
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

Repository checks and bundled helpers use **Python 3.12+ through uv**. Git and
Make are used for repository maintenance. See [the runtime contract](docs/runtime.md)
for isolated installation, locked execution and migration from the earlier Node
commands.

```sh
make setup
make verify
```

Checks validate skill metadata, local documentation links and invocation metadata.
`make test` runs isolated helper tests with fictional configuration and a local HTTP fixture.
CI also runs `make test-integration`: disposable Docker PostgreSQL servers with
and without TLS, certificate verification, schema selection and read-only checks.
Run that target locally with Docker and openssl; it owns and removes its containers
and fictional configuration. Ordinary `make test` skips live DB tests unless the
fixture variables are set. Never point them at a real project database.
These tests do not execute workflows against your real environments.
For behavioral changes, use a small representative scenario and record what was
actually verified. Keep improvements driven by repeated work rather than growing
a universal rulebook. See [contributing](CONTRIBUTING.md) and
[scope and provenance](docs/scope.md).

MIT licensed. More of my tools and setup: [gertyhiler](https://github.com/gertyhiler).
