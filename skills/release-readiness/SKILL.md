---
name: release-readiness
description: Assess production release go/no-go for a branch or merge request by verifying its integration candidate against the current target and preserving intended changes. Use for release readiness, delivery into the release target, or explicit $release-readiness requests. Does not merge or deploy.
---

# Release readiness: verify the integration candidate

Assess a specific source SHA (`S`) against the current target SHA (`M`).
The object of verification is their integration candidate, not the source branch
alone. Record its tree ID (`T`) and the intended merge method. GO means this
candidate is ready for delivery into the release target; it does not mean
production is updated.

## Scope and access

- Read applicable `AGENTS.md` instructions. Follow its **Release readiness**,
  **Verification**, and hosting-access runbook pointers (for example, **GitLab access**). Paths are project-defined;
  this skill has no fixed runbook location. Direct instructions or explicit user
  inputs can supply the same contract.
- Resolve the release target, allowed merge method, mandatory checks/review gates,
  access procedure, and worktree/resource rules. Check instructions against live
  repository and server configuration. If required information is missing or
  contradictory, name it and pause only dependent steps; continue safe diagnostics.
  Never infer a release target or waive a gate because a document is absent.
- Assessment permits reading the hosting service, fetching remote-tracking refs, calculating
  candidate objects, creating an isolated temporary worktree, and suitable checks.
  Preserve existing worktrees, local branches, and unrelated changes.
- Updating the source branch, resolving conflicts, publishing commits, merging,
  triggering CI jobs, deploying, or writing to a task tracker requires the corresponding
  user instruction. An assessment request does not authorize these actions.
- Apply the project's required approvals and pipelines. Where no such gate is
  required, use actual review and verification evidence. If the server blocks
  the chosen merge method, report the specific active rule rather than inventing
  a gate from `approved: false` or an optional job being `manual`.

## 1. Pin the inputs and release scope

For a branch-only request without an MR, use the explicitly requested source and
project release target, verify both through live remote refs, and record the
remote/branch URLs instead of an MR URL. Mark MR-specific fields as not applicable;
do not require creating an MR just to assess the candidate. Still obtain actual
review evidence and enforce applicable project/server delivery gates. The MR
steps below apply when an MR exists.

1. Identify the Git root, branch, and worktree status. Read the live MR: project,
   source and target branches, source SHA, draft/state, and mergeability. Resolve
   ambiguity if several MRs match the branch.
2. Read the task requirements, MR, and available review from the project's
   declared task tracker and review sources.
   Identify intended changes and unrelated scope. No comments does not prove review.
3. Fetch source and target from verified remotes. Record full SHAs `S` and `M`,
   merge-base `B`, timestamp, MR URL, and intended merge method. Match `S` against
   the hosting service; a fork may require a different source remote/project. Unavailable live
   refs leave current readiness unproven. Multiple merge bases require inspecting
   the actual merge result rather than treating an arbitrary base as authoritative.
4. Confirm that the MR target matches the declared release target. Report a
   mismatch instead of silently substituting one. Uncommitted local edits are not
   part of the remote MR.

## 2. Inspect divergence and construct the candidate

After assigning verified full SHAs to `M` and `S`:

```bash
git merge-base "$M" "$S"
git rev-list --left-right --count "$M...$S"
git merge-base --is-ancestor "$M" "$S"
git diff --stat "$M...$S"
git diff --name-status "$M...$S"
git log --oneline "$M..$S"
```

The first count is target-only commits (source behind); the second is source-only.
Ancestor check exit 1 means false; other errors are not ordinary divergence.

**Being behind target is not an automatic NO-GO.** It means source-only checks
cannot establish integration readiness. Require a candidate built against `M`,
inspect its content, and verify it. A clean merge simulation alone is insufficient.

For an ordinary merge, calculate the target-first result:

```bash
git merge-tree --write-tree "$M" "$S"
```

This creates Git objects without changing the index, working files, or branch
pointers. Exit 0 means a clean merge; capture its tree ID as `T`. Conflicts or
calculation errors block readiness. Do not treat a conflicted output tree as a
release candidate or resolve conflicts automatically during assessment.

When target is already an ancestor of source, verify that `T` equals the source tree:

```bash
git diff --exit-code "$S^{tree}" "$T"
```

Otherwise, verify `T` itself. If runnable checks are needed, create a temporary
candidate commit from `T` with parents `M` and `S` using `git commit-tree`, then
check out that commit in a unique detached worktree at the location permitted by
applicable project/machine instructions.
Record its SHA and tree. This is a local assessment artifact, not a published
commit or an update to either branch. Use isolated dependencies/configuration as
needed; keep secrets out of output and preserve existing worktrees.

Match the candidate to the intended delivery method. Rebase applies a commit
sequence and is not equivalent to an ordinary three-way merge in every history.
For squash/rebase, verify the actual proposed result; do not assume an ordinary
merge tree proves another method. An enforced fast-forward policy may require
updating source even though an ordinary merge candidate is clean.

Merging target into source and checking the updated branch is a valid alternative
when separately authorized, not a prerequisite for assessment. Recompute and
verify the candidate after any such update.

## 3. Prove content preservation

Inspect both inputs and the resulting delivery diff:

```bash
git diff "$B" "$S"
git diff "$B" "$M"
git diff "$M" "$T"
git diff "$S" "$T"
```

- Account for each intended source change: present in the candidate, already
  present in target, or explicitly adapted with agreement. Review missing or
  replaced behavior against the task, not only against commit lists.
- Preserve target-side changes too, unless the release intentionally supersedes
  them. An accidental return to an old source version is a blocker.
- Inspect overlapping edits, deletions, renames, reverts, previous merges,
  dependencies, and production configuration. Merge combines endpoint changes
  relative to a base; it does not replay every source commit. A previously merged
  change later reverted in target may not be restored by merging source again.
- Commit reachability, textually clean merges, and matching trees do not prove
  behavioral correctness. Test interacting changes and critical affected flows.
  An unexplained loss, replacement, or rollback of intended behavior is NO-GO.

### If source was updated or rewritten

When an update is separately authorized, capture old source `S0`, old base `B0`,
its intended diff, and target `M` before it starts. Afterward record `S1` and `B1`.
For an already completed update, recover relevant before/after points from
verified history or reflog. If a required preservation comparison cannot be
reconstructed, report that evidence gap; do not invent a baseline.

Compare `B0..S0`, `B0..M`, and `M..S1`. For merge updates, check that both `S0`
and `M` remain ancestors of `S1`, then inspect content and conflict resolutions.
For rebase/cherry-pick, use `git range-diff "$B0..$S0" "$B1..$S1"` to locate
changed/dropped patches, followed by content review. Range-diff is not a semantic
proof and does not replace reviewing merge commits. Accepting an entire file
with ours/theirs does not demonstrate preservation of either side's intent.

## 4. Verify the candidate, not just the branch

Choose checks according to the delivery diff, risk, and project verification
contract: affected tests, types/lint, critical user flows, and integration. Use
verified repository commands. Enforce applicable resource limits on the actual
build workers; if a required limit cannot be enforced, stop that build and name
the missing mechanism. Resolve an unspecified build resource policy before a
heavy local build rather than guessing a safe budget.

- Tie evidence to the candidate SHA/tree, command or CI job, result, and covered
  risk. Source tests may cover candidate content when the trees match and the
  relevant environment/configuration is equivalent. Otherwise run or obtain
  candidate checks; old source results are not automatically transferable.
- When project/server rules allow alternative evidence, a dedicated MR pipeline
  is unnecessary if suitable evidence exists elsewhere.
  Optional manual jobs do not block by themselves. Missing essential verification
  means NO-GO naming that missing check, not a demand to run every pipeline job.
- Separate baseline failures from regressions using the same command/environment
  on pinned target and candidate, in isolated worktrees when needed. If baseline
  failures prevent checking affected behavior, the evidence gap remains open.
- Accept actual review in MR discussions, chat, or confirmed manual checks.
  Formal approvals remain mandatory when project/server rules require them.
  Missing review is not successful review; unresolved substantive findings block readiness.
- Inspect affected production CI/config and external dependencies. Pre-merge
  readiness does not require an already completed production deployment.

## 5. Bind the verdict to delivery

Reread source and target from the server before the verdict. If either SHA changed,
recalculate the candidate and reassess evidence; GO does not transfer to new refs.

Start with **GO** or **NO-GO** for `source@S → target@M`, identifying the MR,
merge method, and candidate tree `T`. Then report briefly:

1. Blockers and the minimum actions needed to remove them.
2. Evidence: release scope, candidate content preservation, checks, and review.
3. Warnings and verification limits, separate from blockers.

GO requires a verified candidate against the current target, preserved intended changes
on both sides, appropriate candidate checks, no substantive unresolved findings,
all project-required gates satisfied, and no active server restriction
preventing the proposed delivery method. Source may still be behind target. Unverified mandatory evidence means NO-GO due to an
evidence gap, not a claim that a defect was found.

At actual delivery, recheck both input SHAs and confirm the resulting target tree
matches `T`. A changed input, merge method, or result invalidates the old verdict
and requires reassessment. State this condition in the handoff; the assessment
itself does not authorize delivery. Production completion remains separate:
merge → build → deploy → runtime acceptance.
