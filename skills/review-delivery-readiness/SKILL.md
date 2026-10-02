---
name: review-delivery-readiness
description: Review evidence for delivery, deployment, migration or external runtime readiness. Use when checking whether a claimed delivery is supported by the exact revision, checks, target and runtime evidence; does not deliver or close work.
---

# Review delivery readiness

Stay read-only. Review the requested delivery claim against the consumer project's
runbook and the supplied artifacts. Do not dispatch another reviewer or require
another skill. Unlike release-readiness, this is an evidence review rather than
a procedure for assembling and validating a release integration candidate.

1. Identify the exact claim: implemented, verified, published, deployed, migrated
   or accepted at runtime. Record revision, target environment and deferred scope.
2. Inspect the relevant diff, command results and pipeline jobs. For commands you
   execute, retain exit codes. For supplied logs, distinguish observed outcomes
   from an author's summary; missing exit status is an evidence gap, not proof of
   failure. Reuse evidence only when revision and relevant inputs match.
3. Compare required checks with executed checks, including skipped, manual and
   allowed-to-fail jobs. Do not invent a build, browser check, publication or
   clean-tree gate when the task does not claim or require it.
4. If deployment is claimed, connect the artifact and environment to the exact
   revision. A successful push or aggregate pipeline is insufficient on its own.
   If runtime acceptance is claimed, inspect the relevant behavior, not only a
   health endpoint. Check migration compatibility and irreversibility when relevant.
5. Assess rollback only where the project requires it or the actual change makes
   recovery a concern. Do not add a rollback plan contrary to the agreed scope.

Return findings first, with artifact/line references and practical consequences.
Use critical for probable serious data/security/service damage, high for a
material delivery blocker, and medium/low for bounded gaps or improvements.
Then list verified evidence, missing evidence, residual risk and a compact verdict:
ready for the stated step, not ready, or insufficient evidence. Separate observed
failure from unavailable evidence. Do not accept/close an issue, merge or deploy.
