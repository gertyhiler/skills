# Operation-owned worktrees

Inspect refs, history and trees without a checkout when that is enough.
When a synthetic candidate or baseline needs checked-out files, create a unique
temporary detached Git worktree at the pinned revision. The project and machine
rules determine where it may live. Never reuse a task checkout for a synthetic
candidate. An existing clean and idle checkout already at the exact required
revision may be used when the project permits it and its state is preserved.

Keep temporary checkouts and their dependencies isolated from ongoing work.
For an authorized delivery, create the candidate from the pinned target and
preserve its history using the project's permitted integration method.

Before reporting, including after failure, move to a surviving directory and
check that no unique edits or valuable ignored files would be lost. Remove each
disposable worktree created for this operation with Git worktree removal without
force or the supported managed-worktree lifecycle. A temporary path does not
unregister it. Retain unique unfinished work and report its exact location and
reason. Before resuming after interruption, inspect actual Git state. CI waiting
alone does not need a temporary checkout.

This cleanup is part of the authorized operation. Pre-existing worktrees require
the standalone cleanup process before removal.
