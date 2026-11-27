# Project document templates

Use only the active paths and fixed sections from the audit or an approved setup
scope. Replace each prompt with verified project facts or an explicit owner
decision. Keep meaningful existing content and link its canonical source. In
commands, identify the working directory, required configuration, ordered steps,
observed success criteria and cleanup. Preserve the project's language.

## Entry points and paired documents

| Path | Write this |
| --- | --- |
| `AGENTS.md` | Project boundary, scope rules, links to the active workflow documents and the current-candidate evidence rule. Keep check commands in the verification workflow. |
| `CONTRIBUTING.md` | Human onboarding, bootstrap, normal contribution flow and links to the applicable architecture, testing and coding standards documents. Link existing handling for issues, review and delivery when relevant. |
| `docs/ARCHITECTURE.md` | System/module ownership, dependencies and public entrypoints. Link existing source and applicable ADRs. State conventions only where real project decisions exist. |
| `docs/agents/architecture.md` | Decisions that guide file placement, import boundaries and verification of consumers. Link directly to the human architecture document. Keep important scoped pointers. |
| `docs/TESTING.md` | What tests are worth writing, observable behavior, regression examples, boundaries, test levels, mocks and any browser/visual requirements. Link existing runner configuration and explain how to locate a relevant suite. |
| `docs/agents/testing.md` | Concise criteria for selecting, writing and reviewing a test. Link directly to the human testing policy and the verification workflow for execution and evidence. |
| `docs/CODING_STANDARDS.md` | Project conventions for implementation, errors, contracts, documentation updates and tooling. Link authoritative tools and decisions. |
| `docs/agents/coding-standards.md` | Applicable Standards and implementation review rules, coverage of nested rules and direct link to the human coding standards. |

## Workflow documents

### review.md

Write `docs/agents/workflows/review.md` with reviewer directions, conditions and
roles; accepted requirement/evidence sources; model/runtime settings when the
project has selected them; report and output language; project approval, finding
and handoff policy. Link shared review for procedure and format.

Add fixed headings only for applicable declared directions.

| Anchor | Inputs and project evidence |
| --- | --- |
| `implementation` | Entry points, conventions, related consumers and scope. Route approval/evidence needed to exercise expected and risk-relevant scenarios. |
| `spec` | Approved requirements, precedence of issue/spec/user approval, and relevant domain authority. |
| `documentation` | Documentation index, canonical sources and maintenance trigger. |
| `design` | Approved references, relevant tokens and supported render setup. |
| `accessibility` | Relevant policy, keyboard and focus requirements and supported tools. |
| `seo` | Indexing intent and authorized public surface/configuration. |

Link the project testing document for test review and the selected coding
standards for Standards review. Existing domain/security rules stay at their
authoritative locations.

### verification.md

Write `docs/agents/workflows/verification.md`. Under `checks`, describe mandatory
checks, conditions selecting them, exact commands or owning targets, working
directory and authoritative configuration. Identify evidence for both changed
and preserved behavior, baseline and candidate selection, failure attribution,
limits for resource-heavy work and exact conditions for reusing results. Link
workspace and project test policy when applicable.

### delivery.md

Write `docs/agents/workflows/delivery.md` with the applicable sections.

| Anchor | Inputs and project evidence |
| --- | --- |
| `production` | Release target, source/ref checks, allowed merge mode, exact candidate checks and review/gate sources, deployment steps if relevant, authorization and stop conditions. |
| `non-production` | Named environments mapped to verified remotes and refs, integration method, order, candidate preflight, jobs and permissions. |
| `compatibility` | Changed external/API/data/artifact boundaries, authoritative deployed and planned revisions, migration and rollout order, evidence before and after deployment. |
| `evidence` | Report destination and content, exact SHA/tree/artifact and stages, runtime acceptance, exclusions and any agreed gap disposition. |

### worktrees.md

Write `docs/agents/workflows/worktrees.md` with roots, permitted locations and
reuse, isolation and ownership rules. Identify release and environment refs,
ignored config/dependency handling, managed lifecycle, temporary operation
cleanup and agreed cleanup of completed tasks. Capture ordering and how to
preserve unique or active work.

### access.md

Write `docs/agents/workflows/access.md` with only the applicable entry points.

| Anchor | Inputs and project evidence |
| --- | --- |
| `hosting` | Hosting CLI, explicit host/project selection, authorized reads and escalation for missing access. Link existing issue workflow rather than declaring new permissions. |
| `postgresql` | Environment identity, allowed credentials adapter and config location, schema/code sources, least-privileged read scope and evidence limits. |
| `grafana` | Environment/instance routing, datasources and service labels, supported adapter, bounded read and export rules. |

Use parameter names and paths. Never populate real credential material.

### investigation.md

Write `docs/agents/workflows/investigation.md` with known entry points and
service mapping, correlation identifiers, source authority, allowed evidence
reads, retention/redaction and where findings go. Link the matching access
sections and authoritative issue/policy documents.

### debugging.md

Write `docs/agents/workflows/debugging.md` with project stack, local reproduction
entrypoint, launch/stop commands, collector route, safe fields and evidence
location. State reproduction/confirmation ownership and cleanup.

## Matt's shared project inputs

- `docs/agents/issue-tracker.md` records the tracker, issue/spec workflow, read
  and write authority, and applicable publication steps.
- `docs/agents/domain.md` points at the existing `CONTEXT.md` or
  `CONTEXT-MAP.md`, appropriate ADRs, and relevant domain documents.
- `docs/agents/triage-labels.md` records the project's labels or equivalent
  roles when a selected workflow requires them.

Reuse these files if they already exist. Keep issue and domain policy current
there instead of creating another copy in a workflow.
