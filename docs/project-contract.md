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
| Worktrees | Allowed location, active task ownership, integration target, treatment of ignored files, available managed-worktree lifecycle. |
| Runtime debugging | Reproduction route or entrypoint, local launch command, evidence directory, permitted instrumentation and sensitive fields. |
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

## Small example

A project's single runbook might state:

- Verification: run make check and affected tests; application builds are separate.
- Delivery: stage accumulates completed features; ordinary merge is permitted.
- Deployment: a push triggers CI, but deployment requires the documented manual job.
- Runtime: confirm the health endpoint reports the deployed revision.
- Worktrees: preserve workspaces owned by active tasks and inspect ignored files.

These are illustrative choices. The skills do not create these policies for a
consumer, turn a check into deployment authorization, or require these branch names.
