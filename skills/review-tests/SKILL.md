---
name: review-tests
description: Review whether tests protect meaningful behavior at the right level and whether their results support the claimed confidence. Use for test diffs, mock-heavy suites, browser discovery and visual evidence; do not edit tests during review.
---

# Review the evidence tests provide

Read `docs/agents/testing.md` and the policy it links. Use
`docs/agents/workflows/verification.md#checks` when identifying the required
runner or CI job. Inspect the changed behavior, its direct consumers, relevant
tests and runner configuration. Keep source, tests and baselines unchanged.

Map the material behavior changes to assertions in the existing tests, including
relevant suites outside the diff. Look for gaps in critical outcomes, boundary
and rejection cases, and recovery from errors. Consider partial failure and the
order of asynchronous or concurrent operations when they affect the contract.
For an order-sensitive change, name the required sequence and a material
reordering. Identify the assertion on the visible result, persisted state or
external boundary that would fail under that reordering. A mock call's order is
evidence only when the boundary contract requires that order.

For each relied-upon test ask:

1. Which exact observable assertion fails if the protected behavior changes?
2. Does it test a public/observable contract or incidental implementation?
3. Is its level appropriate: pure logic, integration, browser interaction or visual?
4. Are mocks limited to unstable or expensive boundaries?
5. Could the feature be broken while the test remained green?
6. Is the test actually discovered and run by the cited command/CI project?
7. Is the test's intended behavior clear, and would the test survive a refactor
   that preserves that behavior?
8. Would removing this test leave the same regression covered at the same boundary?
9. Do removed, weakened or skipped assertions leave an important scenario unprotected?

Source-string checks, CSS classes or DOM shape are not visual evidence. A semantic
navigation/accessibility state is valid when it is the protected behavior. A file
format can itself be a contract; distinguish that from checking copied source.
For fidelity inspect screenshots of real components/routes. For meaningful UI
controls require interaction evidence; do not invent interactions for static text.
For an interaction regression trace the actual user action and exact affected
state or target. For example, a modal rendering test does not prove focus
returns to the triggering control on close. Identify the assertion that would
fail under that specific regression, or report the coverage gap.
For rules/calculations prefer deterministic assertions over screenshot inference.

Do not demand a coverage percentage, mandatory reviewer chain or a test for every
line. Treat legacy low-value tests as debt, not a precedent or permission for a
broad cleanup. Flag only relevant gaps and prioritize them by the consequence of
a regression. For each gap, state the scenario that could fail while the suite
stays green and the test boundary where an assertion would catch it.

Identify the candidate and reviewed scope. Return findings with test/behavior
locations, severity, the regression at stake and evidence, then checks
actually run, unresolved questions and limits. A test existing is not evidence it
passed; a passing suite does not prove deployment or visual acceptance. If no
material finding exists, say so. Accepted fixes return to normal implementation.

The behavior mapping and gap prioritization are adapted from Anthropic's
[`pr-test-analyzer`](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/pr-review-toolkit/agents/pr-test-analyzer.md).
