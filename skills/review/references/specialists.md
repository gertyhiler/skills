# Optional review directions

Use the directions selected by the project workflow. Give each reviewer the
fixed candidate and comparison base, applicable requirements, changed paths and
raw evidence from the [review handoff](report.md). For work in progress, include
the complete intended patch, including staged changes and new files. If a chosen
reviewer is unavailable, use the workflow's fallback or report the coverage gap.

## Anthropic PR Review Toolkit

Use the native Claude Code agents when the toolkit is already available and the
workflow selects them. Preserve the candidate and keep the review read-only.

- `pr-test-analyzer` assesses whether tests catch meaningful regressions. Ask it
  to consider test level, mock boundaries, duplicate coverage and removed, skipped
  or weakened assertions. Verify actual runner discovery and execution separately.
  For visual claims, require render evidence for the affected state. Preserve
  existing tests and baselines. [Upstream agent](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/pr-review-toolkit/agents/pr-test-analyzer.md)
- `code-reviewer` is an optional second opinion on a specific defect question.
  Name the behavior and risk for it to inspect and supply the exact candidate
  scope. Preserve its confidence scores and the distinction between its findings
  and the Standards and Spec results. [Upstream agent](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/pr-review-toolkit/agents/code-reviewer.md)

## Defensive security review

When the workflow selects a security-sensitive change, scope the review to the
affected component and its callers. Give the reviewer only the read-only checks
below, adapted from the history and impact analysis in the [Trail of Bits
differential review skill](https://github.com/trailofbits/skills/tree/main/plugins/differential-review).

- Compare the candidate and base to identify changed or removed safeguards.
- Trace affected callers and verify that the expected safeguards still apply.
- Inspect permitted existing test results and identify coverage gaps for those
  safeguards. Cite the changed lines, affected behavior, evidence and limits in
  the review response.

## Documentation and public interfaces

- Documentation. Check changes to behavior, commands and decisions against their
  canonical sources, including affected documents outside the diff.
- Accessibility. For changed interactions, exercise keyboard operation and focus
  placement and restoration. Inspect accessible names, roles and states.
- SEO. Check the affected public routes' status, redirects and rendered metadata
  against the project's intended indexing behavior.
