---
name: setup-runbooks
description: Set up or reconcile a project's runbooks and agent entrypoint against its engineering skills contract. Inspect existing code and instructions, propose concrete documentation changes, then write after confirmation. Use when asked to configure project workflows for skills or repair missing or contradictory runbooks.
---

# Set up project runbooks

Configure project-owned operating instructions, not the installed skills themselves.
Read the bundled [project contract](references/project-contract.md). Use the
[section seeds](references/section-seeds.md) only for applicable gaps; they are
prompts for concrete project instructions, not defaults to copy blindly.

This is a documentation setup workflow. It does not authorize installations,
changes to CI or application code, tracker labels, secrets, delivery, cleanup or
execution of the operations being documented. A request to set up runbooks starts
research and a draft; wait for confirmation of that draft before writing.

## 1. Explore the actual project

- Resolve the requested repository and applicable AGENTS.md, CLAUDE.md and other
  existing agent entrypoints. Follow their links to runbooks, testing guidance,
  architecture decisions and access documentation. Respect nested scopes.
- Inspect relevant package scripts, Make targets and their implementations, CI
  definitions, Git remotes/branch topology and non-secret configuration. A command
  name is not evidence of what it executes. Do not run builds, deployment scripts
  or credential-loading helpers merely to discover their behavior.
- Identify requested workflows and installed/intended consumer skills. Installation
  is evidence of relevance, not a requirement to configure everything. Include an
  intended workflow even if its skill has not yet been installed.
- Distinguish documented policy, observed configuration, contradictions and unknown
  decisions. A branch's existence does not establish its release role; a CI job
  does not establish whether it is mandatory. Use authorized read-only external
  metadata when necessary; report inaccessible evidence without inventing it.
- Discover existing paths and conventions before proposing new ones. Use per-package
  sections only where commands or policies actually differ; monorepo structure
  alone does not require duplicate runbooks. Never read/copy secrets for setup.

## 2. Present coverage and resolve decisions

Return findings in this chat:

| Process / consumer skill | Existing source | Confirmed facts | Missing decision or conflict | Proposed change |
| --- | --- | --- | --- | --- |

Cover only relevant processes. Mark others not applicable rather than generating
empty documents. Reuse one existing authoritative source for each rule; references
are preferable to copying commands or policies into several files.

Ask only questions that exploration cannot settle. Lead with a recommendation and
its evidence, explain meaningful alternatives briefly, and group related decisions.
Do not re-ask established rules. Resolve dependent decisions in order rather than
presenting an indiscriminate questionnaire. For contradictions show both sources
and the affected action; do not silently promote observed behavior to policy.

If an answer is unavailable, draft independent sections and mark the precise gap
and dependent operation. Never fill unknown branches, budgets, acceptance criteria
or authorization with a plausible default. Partial setup must be reported as partial.

## 3. Show the concrete draft and wait

Show exact proposed paths and new section text or focused edits, including the
entrypoint links. Keep the preview self-contained in chat. Explain what existing
text remains authoritative and what contradiction the proposed edit resolves.

Prefer existing document organization. For a new project, suggest a small runbook
with sections or docs/runbooks/ when justified; neither path nor file count is
mandatory. Update the actual entrypoint(s) the project uses. Do not prefer CLAUDE.md
or AGENTS.md solely by filename, create a competing entrypoint, or erase unrelated
instructions. If neither exists, agree on the appropriate entrypoint in the draft.

Wait for the user to approve or adjust the draft. Approval of this setup skill's
implementation/publication is not approval to change a consumer project. After
approval, apply the agreed changes without separate confirmation for every file.

## 4. Write and verify

- Recheck the affected documents before editing. Reconcile concurrent edits and
  stop only the conflicting portion when a new decision is needed.
- Update existing sections and links in place. Preserve user customizations and
  unrelated material. On repeat runs, propose only justified changes; if coverage
  is already correct, report no changes rather than reformatting everything.
- Write project-native commands, working directories, ordered actions, expected
  evidence, stop conditions and cleanup where relevant. Cite their owning files
  or authoritative scripts. Record access configuration locations, never values.
- Verify links resolve, commands/targets exist and their inspected implementation
  matches the prose. Check CI/environment mappings and authorization boundaries.
  Validate with safe documentation checks where available. Do not execute delivery,
  cleanup, heavy verification or external writes to validate their documentation.
- Report changed files, which skills can now use them, remaining gaps and the
  checks actually performed. Static consistency is not proof that a workflow ran.
  Users can edit runbooks directly; rerunning setup reconciles later changes.

## Provenance

The explore, recommend, preview, confirm and update-in-place approach is inspired
by Matt Pocock's [setup-matt-pocock-skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills).
These instructions and section seeds are written for this repository's project
contract; they do not bundle his tracker or domain-document templates.
