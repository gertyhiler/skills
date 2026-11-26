# Review handoff and report

Give each reviewer the direction, candidate commit or tree, target and comparison
base, approved requirements, scope, project references, and raw verification
evidence. Include previous findings for the same direction when repeating a review.

Use the project's report language. A direction's report contains:

- **Scope** — direction, target/ref SHA, base, candidate and reviewed area.
- **Findings** — severity, location or reproducible evidence, trigger, expected and
  observed behavior, and impact. Identify baseline debt where it matters.
- **Verification** — commands or actions you ran, conditions and outcomes.
  Identify inspected results separately. For a changed contract with scenario
  evidence, give entry point, scenario, setup, action, expectation and result.
- **Documentation** — canonical source and status: current, update required, or
  unaffected. Explain how the change affects the source, including outside the diff.
- **Conclusion** — GO when material risks were checked and no material finding
  remains. NO-GO when a material defect or evidence gap remains. State which part
  was unverified and why.

The consolidated report includes the applicability of each project direction,
independent findings and conclusions, gaps, and any unresolved differences.
If a project requires a separate integration report, identify its target and
source SHAs, method, result tree and checks on that tree. Record any owner
decision with the original finding and the exact candidate.
