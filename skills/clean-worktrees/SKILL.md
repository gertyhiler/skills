---
name: clean-worktrees
description: Analyze all project worktrees, explain their contents and propose removals in chat, then execute after the user confirms or adjusts the plan. Use when asked to clean up worktrees; branch deletion is separate.
---

# Worktree cleanup

A cleanup request starts the complete analysis, not deletion. Read applicable
AGENTS.md and the project worktree/hosting runbooks first. Resolve repository
roots, worktree locations, release and environment targets, ownership, ignored-file
policy and managed-worktree lifecycle. Never assume a branch name or directory.
Skills supply decision criteria; the runbook supplies project commands and execution
order. Missing inputs block only dependent conclusions, not independent inspection.

## Analyze all worktrees before asking for approval

1. Inventory all registered worktrees in scope with `git worktree list --porcelain
   -z`, parsing paths safely. Include primary, detached, locked and missing
   directories. Identify ownership, current cwd, active processes/editor use and
   dependencies between directories, including node_modules links. Do not create
   a checkout merely to match the number of open MRs. Read-only history/diff
   analysis needs no new worktree. Delegate bounded content analysis to a subagent
   when useful and available; consolidate its evidence into this chat.
2. Fetch refs from verified remotes and read current open MRs/PRs. Pin relevant
   release/environment SHAs and record stale or unavailable evidence. Inspect
   tracked/untracked changes, ongoing Git operations and ignored-file names.
   Distinguish generated caches/dependencies from valuable settings, notes and
   env files; never print secrets or read secret contents for this inventory.
3. Establish purpose and actual content: product task, delivery, synchronization,
   baseline or release candidate. Names and MR labels are clues, not proof.
   Explain what the work does and where it is retained. A completed delivery
   retained in an environment branch can lose its checkout without claiming the
   feature reached release; preserve the source of an open release MR or unique
   unfinished work. Preserve the primary checkout even when dirty.
4. Investigate uniqueness using ancestry, history, patches and resulting content
   against relevant retained refs. Distinguish command errors from negative
   ancestry results. For squash/rebase/cherry-pick, differing SHAs alone do not
   establish unique work. Review merge resolutions and reflog-only commits for
   useful changes versus reproducible temporary integration. Neither reflog
   presence nor patch equivalence alone decides removal. For forgotten work,
   explain the behavior missing from published refs and whether it could form a
   separate MR; do not create one without authorization.
5. Complete available investigation before presenting decisions. Preserve genuine
   unique work and active tasks; propose removing completed task checkouts after
   confirmed release integration and completed temporary checkouts once useful
   work is retained or demonstrably reproducible. Current cwd alone is not a
   retention reason: plan to move to a surviving checkout. An unavailable source
   must be a specific evidence gap, not a generic "needs investigation" verdict.

## Present the plan and wait

Return a self-contained table in the current chat; do not create a Markdown report
unless requested. Every directory must be identifiable, even when grouping similar
deliveries. Show full paths/SHAs only where needed to distinguish objects or decide.

| Worktree / task | What it contains | MR and where work is retained | Unique local changes | Keep/remove and reason |
| --- | --- | --- | --- | --- |

Include the concrete removal list, preservation steps, dependency order and any
specific questions about possible data loss. Do not substitute "not in release"
or "has reflog" for explaining the actual work. Separate worktree removal, local
branch deletion and remote branch deletion; approval for one does not imply another.

Stop after this analysis and plan, including for a broad cleanup request. Wait for
user confirmation or corrections before deleting. An analysis-only request remains
read-only and does not require prompting the user to authorize execution. Incorporate corrections into
the scope; do not ask again for each already-approved directory or dependency.

## Execute the agreed plan

1. Recheck candidate HEADs, relevant refs, files, Git operations, locks, active use
   and directory dependencies immediately before removal. Reassess changed items;
   pause affected removals for newly discovered data-loss risk or expanded scope.
   Continue the independent approved portion. Never kill another user's processes.
2. Preserve needed files/history by the agreed method. Do not silently stash,
   discard settings/env files, unlock worktrees or treat all ignored files as
   disposable. Include dependent directories in the agreed ordering and verify
   retained checkouts do not depend on removed dependencies.
3. Move out of a checkout before removing it. For ordinary Git worktrees use
   `git worktree remove <exact-path>` without force. For runtime-managed worktrees
   use the supported archive/removal lifecycle and verify what its snapshot
   preserves; needed ignored files may require separate preservation. Refusal is
   not permission for force, reset, git clean or recursive directory deletion.
4. Detached HEADs and reflog-only work need evidence of retention or reviewed
   reproducibility, not an automatic permanent checkout. Investigate locked or
   missing registrations explicitly; do not use blanket prune. Delete local or
   remote branches only within separately authorized scope and fresh use checks.
5. Verify registrations, directory removal and surviving dependencies. Report
   removed, kept and blocked items in chat. Do not equate cleanup with feature
   delivery, issue completion or a background cleanup service.
