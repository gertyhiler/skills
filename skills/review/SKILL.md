---
name: review
description: Coordinate independent review of a candidate diff using the project's review workflow. Use for complete diff or change-readiness review.
---

# Review a candidate

1. Read the applicable agent instructions and their **Review workflow** pointer. The
   project workflow selects directions and companion skills, identifies documents
   and risks, and defines release and approval policy. Resolve only the inputs this
   review needs. If a missing input prevents a decision, identify it and continue
   with the review that the available evidence supports.
2. Record the target ref and SHA, comparison base, and candidate commit or tree.
   For uncommitted work, capture the complete intended patch, including new files.
   Resolve the approved requirements, source access, and verification results.
   Reuse results only for matching content and relevant inputs.
3. Run the applicable directions in fresh, read-only reviewer contexts when
   delegation is available and allowed. Pass each its question, the same candidate
   and approved requirements, relevant rules and raw evidence, and the
   [report contract](references/report.md). Use the
   [code and specification workflow](references/code-and-spec.md) for those
   directions, including the prescribed use of Matt Pocock's `code-review`.
   Use the workflow's named specialist skill for other assigned directions.
   Load [specialist directions](references/specialists.md) only when applicable.
   Report unavailable reviewer or evidence coverage. An assigned reviewer performs
   its own direction directly and returns findings to the coordinator.
4. Consolidate findings and coverage, retaining disagreements, failed checks,
   missing evidence and reasons for inapplicability. Tie each result to the
   candidate and report documentation impact. Repeat affected directions when
   the candidate or decision-relevant inputs change.
5. When the project requires integration review, obtain it separately for the
   actual target, merge method and resulting tree. Record the owner's disposition
   of any open finding under project policy. Review and reporting do not authorize
   source edits, publication or deployment.
