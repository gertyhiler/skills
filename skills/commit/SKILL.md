---
name: commit
description: Prepare focused Git commits, group a mixed diff, and draft project-compliant commit messages. Use when asked to commit, split changes into commits, or prepare a message for a human.
---

# Prepare or create logical commits

Read applicable `AGENTS.md` and the declared [project documents](agents/project-docs.json).
`docs/agents/git.md` sets the commit format, work-item references, validation,
and who may stage and create commits. Follow those rules and the scope the
user authorized.

1. Inspect the current branch, `git status --short`, staged and unstaged
   diffs, and relevant untracked paths. Identify unrelated work and existing
   staged changes before touching the index.
2. Group the requested change by purpose. Keep the implementation, its
   regression tests, and documentation required by the same behavior together.
   Split independent concerns. Draft a specific subject in the project's
   format and add a body if the reason or impact needs explanation. Leave
   agent, editor and vendor signatures out of the message.
3. When the request or project calls for preparation, return the proposed
   groups, messages and relevant checks for the committer. For authorized
   execution, apply the project's review and commit checks. Stage the selected
   paths or hunks and inspect the actual input to each commit. Create the commit
   only when that input matches the authorized group. Preserve unrelated staged
   work. If the group cannot be isolated without disturbing the existing index,
   report the overlap before modifying the index.
4. Verify each resulting commit and the remaining index and working tree.
   Report the SHA, subject and checks for each commit and identify remaining
   changes. A commit request grants no separate authority for push or release.
