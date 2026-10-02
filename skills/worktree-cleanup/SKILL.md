---
name: worktree-cleanup
description: Inventory and safely remove explicitly approved completed local worktrees and branches, checking dirty files and unpublished or unmerged commits first. Use when the user requests worktree cleanup; remote deletion is separate.
---

# Worktree cleanup

Default to a read-only inventory. Creating this skill or approving its publication
does not authorize any cleanup. Separate worktree removal, local branch deletion,
and remote branch deletion; approval for one does not imply the others.

## Inventory

1. Resolve the repository and list registered worktrees with `git worktree list
   --porcelain -z`. Parse records safely; paths may contain spaces. Check current
   working directory, branch, full HEAD SHA, lock/prunable state, and owning task.
   Preserve the primary checkout, the executing worktree, and active tasks.
2. Fetch current refs from the verified remote. Pin the agreed integration target
   SHA from the user request or repository instructions; do not assume a branch name. A branch name, closed issue status, or merged MR
   label alone is not proof of safe deletion. If fetch fails, report stale evidence.
3. For each candidate inspect `git status --porcelain=v1 --untracked-files=all`,
   ongoing merge/rebase/cherry-pick state, and ignored files using
   `git ls-files --others --ignored --exclude-standard`. Inspect names only,
   never secret contents. Ignored env files, artifacts and local notes can be
   valuable even when git status is clean. A missing directory is not proof
   that its Git registration can be discarded safely.
4. Check HEAD ancestry against the pinned target with
   `git merge-base --is-ancestor <HEAD> <target>` and review
   `git log <target>..<HEAD>` plus `git cherry <target> <HEAD>`.
   Treat command errors separately from a negative ancestry result. Reflogs,
   detached HEADs and unpushed branch tips may contain unique work.
5. Classify candidates: safe after approval, needs investigation, or preserve.
   For rebased/squashed/cherry-picked histories, patch equivalence alone does not
   prove all content was delivered. Require reviewed content equivalence and
   explicit acceptance of losing unique history; never automatically force-delete.
6. Present exact path, branch, SHA, dirty/untracked/ignored-file findings,
   integration evidence and proposed operations. Obtain approval for the exact
   list unless the user already authorized those specific objects. Treat broad
   "clean up worktrees" as permission to inventory and propose, not discard work.

If the agent runtime manages a worktree, use its supported archive/removal lifecycle
instead of bypassing its registry with shell deletion. Verify what its snapshot
preserves; ignored files may need separate preservation.

## Execute approved removals

1. Immediately recheck candidate HEAD, target SHA, worktree state, ignored files,
   locks and active use. If anything changed, stop for that candidate and reassess.
2. Preserve needed files/history by a user-approved method before removal. Do not
   silently stash, delete env files, unlock a worktree, or discard ignored content.
3. From a surviving directory, use `git worktree remove <exact-path>` without
   force. Then, only if separately approved and no worktree uses the branch,
   use `git branch -d <exact-branch>`. A refusal is a blocker, not permission for
   `-D`, `--force`, `reset --hard`, `git clean`, or recursive directory deletion.
4. Detached worktree removal still needs proof that HEAD is safely retained;
   there is no local branch deletion step. Locked/prunable registrations require
   explicit investigation; do not run blanket `git worktree prune`.
5. Remote branch deletion is outside this default workflow and needs explicit
   named authorization plus a fresh remote SHA/use check. Never delete main or
   shared environment branches as routine cleanup.
6. Re-list worktrees and local refs, verify only approved objects were removed,
   and report removed, preserved and blocked items. Do not conflate local cleanup
   with remote deletion or issue completion.
