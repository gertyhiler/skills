# Code and specification workflow

Use the [report contract](report.md) for each applicable direction.

## Route Standards and Spec

- For a committed candidate with both directions selected and fresh read-only
  delegation available, use the installed `code-review` from
  `mattpocock/skills` at the revision in
  [the SkillsX manifest](../agents/skillsx.json). Resolve the installed package
  from its registry source, path, and revision or the project's explicit verified
  mapping. Invoke the identified package by its `SKILL.md` path when another
  installed skill has the same name.
- Confirm the upstream command `git diff <fixed-point>...HEAD` describes exactly
  the approved candidate and comparison. Inspect candidate blobs or a matching
  tree for source evidence. Execute scenarios only in a verified matching
  checkout or fixture. Report when candidate-bound execution is unavailable.
  Pass the supplied requirement source and project rules explicitly. A supplied
  source is sufficient when Pocock's tracker setup is missing or inapplicable.
  Project rules govern source precedence, applicable directions and review scope.
- Coordinate Pocock's Standards and Spec briefs once from the top-level review.
  Before dispatch, tell each reviewer to carry out its assigned brief directly
  and return findings. Use separate fresh, read-only contexts when available;
  each reviewer inspects the candidate without invoking review again or delegating.
  Preserve the two conclusions and record the upstream package used.
- For an uncommitted or otherwise nonmatching candidate, a single selected
  direction, or unavailable upstream package or delegation, use the project's
  selected standalone `review-code` or `review-spec` when present. Otherwise
  apply the relevant brief below to the exact supplied patch or tree. Report
  the fallback and any limitation on independence, inputs, or coverage.

## Review behavior and requirements

- For implementation correctness, trace material changes through the actual
  entry point and affected consumers. Check ownership, failure paths, and effects
  on adjacent contracts. For each material behavior change, use the approved
  expectation to choose a successful case and a risk-relevant counterexample.
  Exercise the cases through the normal entry point when authorized. Identify
  the source of each observation and state which cases were inspected only or
  could not be exercised. This check applies when implementation correctness is
  in scope, including when upstream handles Standards and Spec.
- For a direct Standards pass, inspect applicable written conventions,
  boundaries, and implementation quality under the project's rules. For a direct
  Spec pass, trace changed or preserved approved requirements to observable
  results. Distinguish missing authority from a defect against an approved rule.
