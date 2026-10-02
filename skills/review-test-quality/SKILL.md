---
name: review-test-quality
description: Review whether tests protect meaningful behavior at the right level and whether their results support the claimed confidence. Use for test diffs, mock-heavy suites, browser discovery and visual evidence; do not edit tests during review.
---

# Review the evidence tests provide

Read the project's testing policy and inspect the changed behavior, its direct
consumers, relevant tests and runner configuration. Stay within the requested
scope. This is a read-only review of implementation; do not repair tests or update
baselines while reviewing them.

For each relied-upon test ask:

1. What practical regression would make it fail?
2. Does it test a public/observable contract or incidental implementation?
3. Is its level appropriate: pure logic, integration, browser interaction or visual?
4. Are mocks limited to unstable or expensive boundaries?
5. Could the feature be broken while the test remained green?
6. Is the test actually discovered and run by the cited command/CI project?
7. Are the important affected failure paths represented?

Source-string checks, CSS classes or DOM shape are not visual evidence. A semantic
navigation/accessibility state is valid when it is the protected behavior. A file
format can itself be a contract; distinguish that from checking copied source.
For fidelity inspect screenshots of real components/routes. For meaningful UI
controls require interaction evidence; do not invent interactions for static text.
For rules/calculations prefer deterministic assertions over screenshot inference.

Do not demand a coverage percentage, mandatory reviewer chain or a test for every
line. Treat legacy low-value tests as debt, not a precedent or permission for a
broad cleanup. Flag only relevant gaps and explain their practical consequence.

Return findings with test/behavior locations, severity and evidence, then checks
actually run, unresolved questions and limits. A test existing is not evidence it
passed; a passing suite does not prove deployment or visual acceptance. If no
material finding exists, say so. Accepted fixes return to normal implementation.
