---
name: review
description: Coordinate independent review of a candidate diff using the project's review workflow. Use for complete diff or change-readiness review.
---

# Review a candidate

1. Read applicable agent instructions and `docs/agents/workflows/review.md` at
   the consumer repository root. Use it to select directions and companion
   skills and resolve the project's authoritative documents. Honor an explicit
   request to review only named applicable directions. Record missing documents
   or evidence for the affected direction and continue independent work.
2. Record the target ref and SHA, comparison base, and candidate commit or tree.
   Identify the review mode as **committed** or **WIP** and the directions in scope.
   For WIP, capture the intended staged, unstaged and selected untracked content
   as one exact snapshot. State what the snapshot includes. Resolve the approved
   requirements and verification evidence. Reuse evidence only for matching
   content and relevant inputs.
3. Normally assign one fresh, read-only reviewer session to each applicable
   direction. Each receives its own question, the same candidate and approved
   requirements, exact applicable project document paths, relevant rules, raw
   evidence and the [report contract](references/report.md). Start without the author's context
   or other reviewers' conclusions. Use the
   [Standards and Spec workflow](references/standards-and-spec.md) for those
   directions, including the prescribed use of Matt Pocock's `code-review`. Use the
   [Implementation correctness brief](references/implementation-correctness.md)
   when that direction applies.
   Use the workflow's named specialist skill for other assigned directions.
   Load [specialist directions](references/specialists.md) only when applicable.
   Follow the project's selected independent reviewer runtime, model and effort.
   An assigned reviewer performs its own direction and returns findings and
   applied rules to the coordinator. When explicitly asked to run a direct pass,
   execute the requested directions in the current read-only session and label
   the results as direct. A request for a single direction still uses an
   independent reviewer unless direct execution was requested. A direct pass
   leaves any independent review required by the release workflow outstanding.
   Record missing independent results and their reasons.
4. Consolidate findings and coverage, retaining disagreements, failed checks,
   missing evidence and reasons for inapplicability. Tie each result to the
   candidate and report documentation impact. Repeat affected directions when
   the candidate or decision-relevant inputs change.
5. For an integration candidate, bind the findings to its source and target
   SHAs, merge method and resulting tree. Preserve any documented decision on an
   open finding under project policy. The scope of review is read-only.
