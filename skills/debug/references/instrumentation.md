# Session instrumentation contract

Read before adding traces and again before cleanup. The agent creates the adapter
inside the consumer project using its language/framework; this is not a packaged
cross-framework collector or a Python server injected into every project.

## Manifest

Use the project's ignored local evidence location, for example
`.agents/local/debug/<session-id>/session.json`. The exact path is project-owned.
Keep enough state to resume after a turn/context boundary:

- Session ID, current phase, symptom and stable failure predicate.
- Reproduction steps, hypotheses and fields needed to distinguish them.
- Collector kind, endpoint, fixed JSONL path, local enablement and launch/stop commands.
- Owned process/task handle plus identifying command, cwd and start information.
- Each created file and each marked insertion into an existing file.
- For changed settings/imports/dependencies: the exact added entry and previous
  value where relevant. Record pre-existing dirty work without copying secrets.
- Baseline/reproduction/post-fix run IDs, evidence conclusions and user reports.
- Confirmation, any explicit waiver, requested retention and cleanup status.

Update the manifest when instrumentation changes. Do not store tokens, credentials
or full private payloads in it. A manifest is an ownership ledger, not permission
to discard a file whose contents have since been changed by someone else.

## Trace markers

Every temporary insertion in an existing source file uses a paired marker with
the unique session ID. Use valid comment syntax for the project's language:

```ts
// DEBUG_TRACE_BEGIN session-opaque-id
try {
  void fetch(traceEndpoint, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      sessionId: "session-opaque-id",
      runId: activeRunId,
      hypothesisId: "H1",
      event: "state-applied",
      source: "component:state-transition",
      data: { expectedState, effectiveState },
    }),
  }).catch(() => {});
} catch {
  // Temporary tracing must not interrupt application behavior.
}
// DEBUG_TRACE_END session-opaque-id
```

This illustrates a removable block, not a drop-in universal emitter. The project
adapter supplies endpoint/session access controls, run selection, payload bounds
and safe serialization. Guard the whole trace operation (including payload
construction) against exceptions and enable it only in the local session.
Instrument immutable snapshots where deferred serialization would distort evidence.
Include sequence/monotonic time for each source when needed. Session access tokens,
if used, stay local and out of report output.

Keep real fixes outside these blocks. Mark temporary imports/helpers too. For
formats without comments, record exact structural additions in the manifest;
do not insert invalid comments just to create a marker. Newly created collector
files carry a session header where valid and are listed as session-owned files.

## Collector lifecycle

Use an explicit local enablement check for an integrated route. A companion server
uses the project's language/runtime, a documented available port, loopback binding
and a recorded stop mechanism. Never kill every process on a port to stop one
session. Restrict browser origins/session access, enforce an event schema and
size/growth bounds, and keep output at the investigator-selected local path.

Smoke-test from each source that needs to emit (browser/server/worker), including
collector-down behavior. Remove or label smoke events. Allocate fresh run IDs for
each reproduction; drain pending events or distinguish them by run ID rather than
mixing old events into a post-fix result. Do not change run ID retroactively on an
in-flight emitter. Retain the active run in a stable snapshot at event creation.

## Mechanical cleanup

1. Read the manifest and current diff. Verify each owned process identity before
   stopping it; do not trust a stale PID that may now belong to another process.
2. Locate exact BEGIN/END pairs for this session. If pairs are missing, duplicated,
   nested or edited ambiguously, inspect before removal; do not run a broad regex
   over unrelated code. A future cleanup helper must fail closed on ambiguity.
3. Remove marked blocks and specifically recorded structural additions. If a fix
   or user edit has entered a marked block, preserve it and separate it first.
4. Delete created collector/helper files only after checking they still contain
   solely session-owned work. Restore only the session's setting changes when the
   current value still matches what the session wrote. Preserve concurrent edits.
5. Remove owned launch artifacts and raw traces unless retention was requested.
   Keep a compact sanitized outcome if requested. Remove the manifest last, after
   successful cleanup, unless the project asks to retain it; if anything remains,
   keep it with the unresolved ownership/cleanup details.
6. Search tracked and untracked relevant paths (including the ignored session
   directory explicitly) for this session's markers, endpoint and helper names.
   Inspect the final diff; rerun relevant checks and a normal-path smoke test.

Mechanical means every temporary change is enumerated and identifiable; it does
not mean deleting unmatched text blindly. Preserve pre-existing observability,
project configuration and user evidence. If cleanup cannot safely remove one item,
report the exact remaining item and reason rather than declaring completion.
