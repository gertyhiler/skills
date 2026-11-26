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
3. Assign one fresh, read-only reviewer session to each applicable direction,
   including implementation correctness when selected. The coordinator handles
   applicability, handoff and synthesis. Each reviewer receives its own question,
   the same candidate and approved requirements, exact applicable project document
   paths, relevant rules, raw evidence and
   the [report contract](references/report.md). Start without the author's context
   or other reviewers' conclusions. Use the
   [code and specification workflow](references/code-and-spec.md) for those
   directions and the implementation pass, including the prescribed use of Matt
   Pocock's `code-review`.
   Use the workflow's named specialist skill for other assigned directions.
   Load [specialist directions](references/specialists.md) only when applicable.
   If native delegation is unavailable, use a separate read-only reviewer session
   when supported and allowed. An assigned reviewer performs its own direction
   directly and returns findings and the project rules it applied to the
   coordinator. Use the project-selected reviewer model and effort when available
   and report a fallback explicitly. If an applicable direction
   has no independent result, record the coverage gap and its reason.
4. Consolidate findings and coverage, retaining disagreements, failed checks,
   missing evidence and reasons for inapplicability. Tie each result to the
   candidate and report documentation impact. Repeat affected directions when
   the candidate or decision-relevant inputs change.
5. When the project requires integration review, obtain it separately for the
   actual target, merge method and resulting tree. Record the owner's disposition
   of any open finding under project policy. Review and reporting do not authorize
   source edits, publication or deployment.
