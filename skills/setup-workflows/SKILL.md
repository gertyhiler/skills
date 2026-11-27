---
name: setup-workflows
description: Audit installed SkillsX skills against their exact project documentation contracts and reconcile missing documents, sections, or links. Use when explicitly setting up or repairing the project workflows for a skill installation.
---

# Set up project workflows

Read the [project contract](references/project-contract.md). Resolve the consumer
Git root and the applicable agent instructions. This workflow handles project
documentation only. Installing packages, changing CI or transport permissions,
reading credentials, and executing the workflows need their own authorization.

## Audit the installation

From the consumer Git root, run the project's pinned `skillsx verify` to
validate the registry and installed payloads. Treat a failed verification as
an inventory gap. The read-only documentation analyzer can still identify
independent document gaps, but its result does not certify the installation.
Run it using the installed skill's absolute path:

```sh
python3 /absolute/path/to/setup-workflows/scripts/audit.py --root .
```

Use its registry IDs, installed paths, required paths, anchors and findings.
An invalid inventory is a prerequisite gap. Report it without repairing the
registry or inventing a path. A package without a manifest contributes no
required document. A registered package missing from its installed path is an
inventory finding. Do not list global skills or import requirements from
uninstalled packages.

## Reconcile the findings

1. Read the required documents, relevant existing documentation and candidate
   sources of truth. Follow scoped instructions. Confirm actual inputs against
   repository code, commands, CI and authorized read-only metadata. Distinguish a
   documented decision, a fact, a contradiction and an owner decision still open.
   A script, branch or optional job does not establish policy by itself.
2. Use the [document templates](references/section-seeds.md) for the active
   requirements. Put authoritative material in the designated document and link
   existing sources. Preserve substantive project text, existing ownership,
   scoped rules and names. Supply fixed anchors for localized headings. Avoid
   creating documents or sections solely because they are listed in a template.
3. Preview by file. Show each missing or conflicting item, the source or owner
   decision that resolves it, and the proposed diff or exact outline. Include
   each decision that needs user input and the step it blocks. If all active
   contracts are satisfied, report the reviewed scope and make no edits.
4. Apply the preview after the user confirms the changes or when a prior approval
   already covers that exact scope. Recheck files immediately before editing and
   keep any intervening changes. Reuse existing headings and managed entrypoint
   blocks in place. If a new material decision appears, leave it open and apply
   confirmed independent changes. Never draft a policy from an example.
5. Rerun the analyzer and check rendered links, heading anchors, the scoped agent
   entrypoint, and agreement with actual project configuration. Report the diff,
   checked paths, outcomes and remaining decisions. On repeat, healthy documents
   are a no-op. Verification of document structure does not establish that a
   project workflow ran or is ready to execute.

The setup process takes inspiration from
[setup-matt-pocock-skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills).
