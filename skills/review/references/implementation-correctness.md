# Implementation correctness

Use `docs/agents/workflows/review.md#implementation`, the applicable contracts
it identifies and the approved expectations for the exact candidate. Follow the
entrypoint's independent or explicitly requested direct mode. This direction
applies alongside Standards and Spec when all three are in scope.

1. Trace the changed behavior from the normal entry point to the observable
   effect. Identify affected consumers, ownership and how invocation frequency,
   state changes or dependency failures affect adjacent contracts.
2. For each material changed contract, derive a successful case and a
   risk-relevant counterexample. Consider existing consumers and data, retries,
   partial failure, concurrency and operation order when they can change the
   outcome. Exercise both cases through the real entry point or direct consumer
   in an authorized fixture matching the candidate.
3. Record the setup, command or action, expected and observed result for each
   case you ran. Identify inspected evidence separately. Explain which material
   case could not be exercised and its effect on the verdict.
4. Cite the affected contract, trigger and impact for each finding. Check
   whether technical descriptions, commands or runbooks became stale. Return
   the findings, scenario evidence and limits using the [report contract](report.md).
