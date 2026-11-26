---
name: review-code
description: Review code or tooling for correctness, regressions, solution placement, and effects on consumers.
---

# Review the implementation

1. Read the project review workflow and the relevant implementation contracts.
   Trace the change from an actual entry point through its processing to the
   observable result. Establish why the operation belongs at the chosen boundary
   and where its frequency, dependencies or failures affect other consumers.
2. For each material changed contract, use the approved expectation to derive a
   successful case and a risk-relevant counterexample. Run both through the entry
   point or a direct consumer where the project permits it. Record the setup,
   command or action, expected and observed results. Keep supplied results
   distinct from your own runs. Name any material case you could not exercise.
3. Inspect correctness, affected contracts, error handling, unnecessary complexity
   and relevant project conventions. Check whether technical descriptions,
   commands, paths or runbooks became stale because of the change.
4. Return findings with location, trigger, expected and observed behavior and
   impact, followed by scenario evidence, documentation impact and review limits.
