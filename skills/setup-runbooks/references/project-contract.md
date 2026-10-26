# Project contract

Skills reuse a procedure; the consumer repository owns the operating details.
Read applicable AGENTS.md files, follow their document links and compare them
with the current repository configuration. Explicit user instructions can provide
missing details. A document is not permission to take an action the user did not
request.

| Procedure | Project inputs |
| --- | --- |
| Verification | Required checks, authoritative scripts/Make targets, baseline, candidate, test conventions, applicable build limits. |
| Environment delivery | Named target and remote, merge/cherry-pick policy, required preflight, automatic/manual deployment behavior, runtime acceptance, access procedure. |
| Release readiness | Release target, intended merge method, required checks/review, hosting restrictions and acceptable evidence. |
| Delivery review | Claimed step, exact revision/environment, required evidence, actual command/job outcomes and deferred scope. |
| Investigations and access | Intended environment, schema/code sources, service labels/datasources, ignored local configuration, read-only role and evidence handling. |
| Worktrees | Repository roots and allowed locations, reuse/isolation policy, active task ownership, release and environment targets, treatment of ignored files and dependencies, cleanup commands/order and available managed-worktree lifecycle. |
| Runtime debugging | Project stack and reproduction entrypoint, collector route/server choice, launch/stop commands, session manifest/evidence directory, sensitive fields and user reproduction/confirmation steps. |
| Tests | Valuable behaviors, test commands/frameworks, browser/visual requirements and external boundaries. |
| Module organization | Architecture and import rules, existing public APIs, ownership and styling conventions. |

Only resolve inputs relevant to the requested operation. A documentation check
need not discover a staging environment. A missing deployment contract does not
prevent reading the diff. Explain which particular step depends on a missing
input; do not demand an entire documentation suite as a preliminary gate.

If project docs conflict with code, report the concrete discrepancy. An optional
CI job is not automatically mandatory; a green pipeline does not prove a required
job ran. Evidence can be reused when the relevant revision, dependencies,
configuration and environment match.

## Execution and cleanup boundaries

The runbook owns concrete paths, commands, targets and execution order. Each skill
provides its decision framework, not a replacement project runbook. A cleanup
request triggers analysis of all worktrees and an in-chat table/removal plan, then
waits for confirmation or corrections. Once agreed, execute that scope without
per-directory approvals. Delivery, verification and release assessment execute
the requested operation without a generic plan-approval gate, subject to actual
project authorization and missing-input boundaries.

Temporary delivery/check/candidate worktrees are operation-owned: create only when
needed and remove before reporting, or explain the concrete retained work/blocker.
The project completion workflow should remove a merged task checkout after checking
for additional unique work and active use. Assessment alone does not merge or
schedule future cleanup; runtime actions occur only in the authorized operation.

## Small example

A project's single runbook might state:

- Verification: run make check and affected tests; application builds are separate.
- Delivery: stage accumulates completed features; ordinary merge is permitted.
- Deployment: a push triggers CI, but deployment requires the documented manual job.
- Runtime: confirm the health endpoint reports the deployed revision.
- Worktrees: preserve workspaces owned by active tasks and inspect ignored files.

These are illustrative choices. The skills do not create these policies for a
consumer, turn a check into deployment authorization, or require these branch names.
