---
name: runtime-trace-debug
description: Investigate intermittent or state-dependent runtime bugs with scoped local traces, a repeatable failure predicate, post-fix evidence and instrumentation cleanup. Use when static inspection or existing tests cannot establish the cause.
---

# Debug from runtime evidence

Read the project's debugging/launch runbook linked from AGENTS.md, or its direct
instructions. Resolve the actual route or entrypoint, environment, evidence path
and permitted changes. Use existing logs/traces first. Analysis-only authorization
permits inspection, not instrumentation or a fix; continue useful diagnostics and
identify any action that needs authorization.

## Establish the failure

Record the user action/input, expected result and actual broken state. Trace the
code path from input through transformations to the effective output. Form a few
falsifiable hypotheses and choose the minimal fields that distinguish them.
Screenshots or a plausible explanation alone do not establish a cause.

Use the same reproducible input and observation window for before/after evidence.
When the user must reproduce the issue, give exact steps and wait for their report
or an actual trace showing the failure. Do not treat elapsed time as reproduction.

## Collect scoped evidence

Use the framework's own local route, middleware, event hook or logger. A browser
application may need a temporary dev-only POST endpoint; a CLI or backend often
only needs local structured logs. Do not introduce an HTTP server without need.

For a temporary collector:

- Enable it explicitly in the local development environment; it must be absent
  or reject requests in production and shared environments.
- Use a fixed ignored output file chosen by the investigator, never a caller's
  arbitrary path. Follow the project's evidence-directory policy.
- Accept only the selected event fields; bound payload size and event/file growth.
  An HTTP collector must restrict callers to the intended local session/origin,
  reject other callers and avoid permissive CORS. Localhost alone is not a complete
  access boundary for a browser-reachable endpoint.
- Record run/correlation ID, sequence or monotonic time, event, relevant state and
  sanitized context. Avoid relying on unsynchronized clocks across processes.
- Never collect credentials, cookies, raw private payloads, full URLs with tokens
  or unnecessary personal identifiers. Use synthetic/opaque identifiers when possible.
- Keep logging best-effort and separate from fix logic so it does not change the
  application's success/failure behavior. Check whether instrumentation affects timing.

Capture decision inputs and effective results, including lifecycle boundaries
when order matters. Compare a good run with a failing run; distinguish normal
transient state from the stable failure predicate. Report which hypotheses the
trace supports, rejects, or leaves unresolved. Failed reproduction is uncertainty.

## Fix and prove

When implementation is authorized, make a narrow change supported by the evidence.
Repeat the original failing path with fresh traces. Check the same predicate,
not merely that the page loads or a screenshot looks different. Add a focused
regression test when it can protect the demonstrated behavior meaningfully.

## Remove temporary instrumentation

After sufficient post-fix proof, remove only instrumentation and generated files
owned by this investigation: collectors, emitters, flags and trace outputs.
Preserve existing observability and user data. Retain sanitized evidence only
when the user/project asks for it. Search for the actual markers/routes introduced,
inspect the final diff and run relevant checks after removal.

If a collector must remain for unfinished diagnosis, keep it local and explicitly
report its location, access boundary and pending cleanup. Do not publish temporary
instrumentation as part of the fix. Report reproduction, evidence, fix, post-fix
result and cleanup separately; no automatic reviewer or deployment is required.
