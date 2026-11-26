# Runbook section seeds

Use only sections relevant to the project. Replace these prompts with verified
facts and agreed decisions; do not publish empty headings or invented defaults.
Existing runbooks remain the preferred destination. One document can cover several
processes. Follow the project's documentation language.

For an executable process, describe: scope and prerequisites; exact working
directory and ordered commands; evidence of success; stop conditions; cleanup.
Link the command's authoritative implementation instead of maintaining a second
copy of script internals. Distinguish unknown, not applicable and verified.

## Verification — verify-changes

- Required checks and conditions selecting them; owning scripts/targets and cwd.
- How baseline/candidate inputs are selected, including uncommitted changes.
- Configuration and resource limits where applicable; whether builds are separate.
- Evidence reuse conditions and treatment of baseline failures.
- Temporary checkout/configuration lifecycle and final evidence format.

## Change review — review

- Project directions and what makes each applicable, skill IDs and companion skills.
- Requirement, architecture, testing, documentation and design sources selected
  per direction. Name concrete project risks and how to obtain local evidence.
- Report language, destination, integration requirements and owner responsibility.
  Link the installed review skill for execution order and report format.

## Environment delivery — deliver-to

- Named environments mapped to verified remote/target refs; accumulated history.
- Allowed integration methods and source scope; preflight commands/configuration.
- Ordered integration, checks, push and deployment observation; concurrency checks.
- Automatic versus manual jobs, authorization and deployed-revision evidence.
- Runtime acceptance, handoff boundaries and temporary worktree cleanup.

## Release readiness — check-release

- Release target and intended merge method; authoritative review/gate sources.
- Candidate construction and verification commands; matching evidence rules.
- Required content-preservation review and reasons to stop or withhold readiness.
- GO/NO-GO handoff tied to exact inputs; assessment does not authorize release.

## Worktrees — clean-worktrees and operation-owned temporary checkouts

- Repository roots, permitted locations, ownership and active-use checks.
- When to reuse a checkout versus isolate; ordinary versus managed lifecycle.
- Release/environment refs relevant to retention, MR source and access procedure.
- Local settings, ignored files and dependency treatment; secret-safe inspection.
- Cleanup: analyze all, present contents/decisions and plan, wait for confirmation,
  recheck and execute agreed removals in dependency order, verify survivors.
- Temporary execution checkout: remove within its owning operation or explain
  retained unique work/blockers. No background cleanup promise.
- Task completion cleanup after release integration; branch deletion is distinct.

## Access and investigation — investigate, grafana-access, postgresql-access

- Environment selection, supported access tools and non-secret configuration paths.
- Code/schema sources, datasource/service identifiers and allowed read-only scope.
- Bounded queries, sensitive-output handling, evidence location and access failures.
- Link existing tracker/hosting instructions when needed; do not create a tracker
  or read credentials as part of runbook setup.

## Runtime debugging — debug

- Reproduction entrypoint and project-native instrumentation/collector approach.
- Launch/stop commands, ownership, evidence paths and sensitive-field exclusions.
- User reproduction and confirmation pauses; removal of temporary instrumentation.

## Tests, architecture and evidence review

- design-tests/review-tests: valuable behaviors, test conventions, commands,
  external boundaries and applicable browser/visual expectations.
- organize-code: owning modules, dependency rules and existing architecture docs.
- review-delivery: claimed revision/environment, required evidence sources,
  publication/deployment/acceptance distinctions and unresolved gaps.

## Agent entrypoint rules and links

Add concise process names, scope and links to authoritative sections in the
project's existing versioned agent entrypoint. Update the existing block and
preserve nested-scope rules. Link existing or approved new documents.

For Verification, add or reconcile the rule requiring the project's applicable
checks on the current candidate before reporting completion. Record the checked
SHA or diff, commands, observed results, and any failed or unrun required check
with its reason. Reuse evidence only for matching content and relevant conditions.
Keep command details and reproduction conditions in the linked project runbook.
