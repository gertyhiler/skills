# Review handoff and report

Give each reviewer the direction, candidate commit or tree, target and comparison
base, approved requirements, scope, project references, and raw verification
evidence. Include previous findings for the same direction when repeating a review.
Keep reviewer handoffs independent. Pass raw evidence and the agreed brief without
the author's reasoning or other directions' findings.

Use the project's report language. A direction's report contains:

- **Scope** — direction, target/ref SHA, base, candidate and reviewed area.
  Identify the candidate mode and the brief or upstream package used.
- **Reviewer** — independent or explicitly requested direct execution, session
  identifier and runtime. Record model, reasoning effort and elapsed time when
  observed. Mark unavailable metadata as unknown.
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
Record the completed independent result, the labeled direct result or the gap for
each applicable direction. A direct pass leaves required independent review open.
Distinguish a direction that timed out or lacked a reviewer from one outside
scope. Preserve findings and verdicts by direction and any unresolved differences.
For an integration candidate, identify the target and source SHAs, merge method,
resulting tree and checks on that tree. Record any owner decision beside the
original finding and exact candidate.
