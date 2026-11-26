# Review handoff and report

Give each reviewer the direction, candidate commit or tree, target and comparison
base, approved requirements, scope, project references, and raw verification
evidence. Include previous findings for the same direction when repeating a review.
Keep reviewer handoffs independent. Pass raw evidence and the agreed brief without
the author's reasoning or other directions' findings.

Use the project's report language. A direction's report contains:

- **Scope** — direction, target/ref SHA, base, candidate and reviewed area.
  Identify the upstream reviewer package used, or the fallback and its reason.
- **Reviewer** — separate session identifier and runtime. Record model, reasoning
  effort and elapsed time when observed. Mark unavailable metadata as unknown.
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

The consolidated report lists each direction with its applicability and reason.
Record the completed independent result or the gap for each applicable direction.
Distinguish a direction that timed out or lacked a reviewer from one outside
scope. Preserve findings and verdicts by direction and any unresolved differences.
If a project requires a separate integration report, identify its target and
source SHAs, method, result tree and checks on that tree. Record any owner
decision with the original finding and the exact candidate.
