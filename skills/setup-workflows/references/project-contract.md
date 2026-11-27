# Project workflow contract

A reusable skill declares the project documents it needs. The project owns the
content, commands, named targets, scope and approvals. The relevant project
instructions are loaded at the repository root and again when entering a nested
scope. Apply the source precedence and boundaries stated there.

## Declarative requirements

A skill may ship `agents/project-docs.json` beside its invocation metadata.
The manifest accepts exactly version 1 and a required array. Each string is an
exact repository-relative Markdown path under `docs/agents/`, or
`CONTRIBUTING.md`, optionally followed by a fixed anchor.

```json
{
  "version": 1,
  "required": [
    "docs/agents/workflows/verification.md#checks"
  ]
}
```

Every declared path and anchor is required for its dependent operation. Use a
stable Markdown heading slug, or insert an explicit ASCII `<a id="checks"></a>`
at the corresponding heading when the heading is translated. An empty array
means the skill needs no prescribed project document. Upstream packages without
this manifest contribute no declared requirement. A direct user-provided spec or
candidate can supply evidence. Missing project documents remain visible and block
only dependent operations.

The [setup analyzer](../scripts/audit.py) reads the SkillsX v1 registry at
`.agents/skills.registry.json`. It expands each ID and its recorded category to
the canonical installed copy under `.agents/skills/`. It examines both registered
and present copies there, tracks a documentation requirement only when the
registered skill is present, and reports unregistered and missing payloads.
Runtime projections, untrusted aliases and user-global installations are outside
this inventory. Use the project's SkillsX verifier separately for registry
validity, installed bytes and projections.

## Single owners

| Project authority | Location |
| --- | --- |
| Contribution and local development entrypoint | `CONTRIBUTING.md` |
| Agent instructions, nested scope, completion evidence and pointers | `AGENTS.md` |
| Architecture and module boundaries | `docs/ARCHITECTURE.md` |
| Testing policy and test design | `docs/TESTING.md` |
| Coding conventions | `docs/CODING_STANDARDS.md` |
| Agent-facing extraction and links for those policies | `docs/agents/{architecture,testing,coding-standards}.md` |
| Git message rules, validation and commit authority | `docs/agents/git.md` |
| Workflow decisions and project execution details | `docs/agents/workflows/` |
| Issue routing and domain vocabulary/decisions | Matt's `docs/agents/issue-tracker.md` and `docs/agents/domain.md` |
| Tracker triage labels when a selected skill needs them | Matt's `docs/agents/triage-labels.md` |

An active agent-facing architecture, testing or coding standards document needs
its human counterpart and a direct Markdown link to it. The testing document
also links the executable checks in the verification workflow. For an active
contract, keep a usable `AGENTS.md` and `CONTRIBUTING.md`. Human-facing documents
and runbooks use the project's language. Keep machine-facing identifiers stable.
Use existing domain and ADR records through Matt's domain pointers. Create only
the documents and sections selected by the installed contracts and actual project
workflows.

The analyzer reports structural findings and the skills that require each
document. Inspect the substance separately. Verify evidence against the exact
candidate, compare instructions with executable configuration, and surface
disagreements for the owner. A healthy structure does not prove that a command is
safe, that approval exists, or that the configured job has run.

## Execution boundaries

Versioned project instructions require applicable verification on the current
candidate before reporting completion. Name the checked SHA or diff, actual
commands and results, and the reason for any failed or unrun required check.
Reuse evidence only for matching content and relevant conditions. Keep concrete
checks and commands in the verification workflow.

Delivery, assessment, investigation, and cleanup retain their authorization
boundaries. A review, a green pipeline, or a written runbook grants no separate
permission. Operation-owned temporary worktrees belong to their invoking
operation. Complete their documented cleanup or report a concrete reason they
remain. Clean up active or retained project worktrees only under the agreed scope.
