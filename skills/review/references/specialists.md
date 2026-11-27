# Optional review directions

Use the directions selected by the project workflow. Give each reviewer the
fixed candidate and comparison base, applicable requirements, changed paths and
raw evidence from the [review handoff](report.md). For work in progress, include
the complete intended snapshot, including selected new files. If a chosen
reviewer is unavailable, report the coverage gap.

## Test coverage review

Use `review-tests` when the workflow names it. Follow the entrypoint's independent
or explicitly requested direct mode. The review maps changed behavior to specific
failing assertions and confirms which tests the runner discovers and executes.
[Upstream method](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/pr-review-toolkit/agents/pr-test-analyzer.md)

## Defensive security review

When the workflow selects defensive review, scope it to the affected component
and its callers. The read-only checks below
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
