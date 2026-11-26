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
3. Run every direction that the project workflow makes applicable. Assign each to
   a separate reviewer in a fresh, read-only context when delegation is available
   and allowed. Pass the same candidate, requirements, applicable references and
   raw evidence. Give each reviewer its own question and the
   [report contract](references/report.md). If a separate reviewer or required
   evidence is unavailable, report the resulting gap. For an assigned direction,
   use its skill directly and return its findings without dispatching another review.
4. Consolidate findings and coverage, retaining disagreements, failed checks,
   missing evidence and reasons for inapplicability. Tie each result to the
   candidate and report documentation impact. Repeat affected directions when
   the candidate or decision-relevant inputs change.
5. When the project requires integration review, obtain it separately for the
   actual target, merge method and resulting tree. Record the owner's disposition
   of any open finding under project policy. Review and reporting do not authorize
   source edits, publication or deployment.
