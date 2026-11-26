# Optional review directions

Use the directions selected by the project workflow. Give each reviewer the
fixed candidate and comparison base, applicable requirements, changed paths and
raw evidence from the [review handoff](report.md). For work in progress, include
the complete intended patch, including staged changes and new files. If a chosen
reviewer is unavailable, use the workflow's fallback or report the coverage gap.

## Test coverage review

Assign the workflow's test skill to its own reviewer. When the workflow selects
test review without naming a skill, use installed `review-tests`, a portable
adaptation of Anthropic's method. If the chosen skill is unavailable and the
workflow allows a direct brief, assign a reviewer to map changed behavior to the
tests that would fail on a concrete regression. Inspect test location, runner
discovery, assertions and the actual interaction or integration boundary.
Identify uncovered behavior and distinguish static coverage from executed tests.
[Upstream method](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/pr-review-toolkit/agents/pr-test-analyzer.md)

## Defensive security review

When the workflow selects a security-sensitive change, assign a separate
reviewer for the affected component and its callers. The read-only checks below
draw on history and impact analysis from the [Trail of Bits differential review
skill](https://github.com/trailofbits/skills/tree/main/plugins/differential-review).

- Compare the candidate and base to identify changed or removed safeguards.
- Trace affected callers and verify that the expected safeguards still apply.
- For changed public data, trace its origin, transformations and response fields
  against the project's rules for what may be disclosed. Use synthetic examples.
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
