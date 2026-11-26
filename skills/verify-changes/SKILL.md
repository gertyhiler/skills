---
name: verify-changes
description: Choose and execute proportionate verification for a code diff or integration candidate, distinguish regressions from baseline failures, and report evidence tied to the checked revision. Use when asked to verify changes, run checks, or establish implementation readiness.
---

# Verify changes

This skill verifies changes; it does not authorize publishing, merging, deployment,
or task-tracker mutations. Execute requested checks under the project contract
and return the final evidence report; no separate plan-approval pause is required.

## Resolve the project contract

Read applicable `AGENTS.md` instructions and follow the **Verification** runbook
pointer. The path is project-defined. Direct project instructions or explicit
user inputs can supply the same contract. Obtain required checks, authoritative
command/configuration sources, test-writing conventions when relevant, and build
resource/worktree policies. Validate commands against the current repository.

If a required input is absent or conflicts with current configuration, state the
specific missing decision and pause the dependent check. Continue safe diff and
configuration inspection. Do not guess commands, budgets, or treat absent
instructions as permission to skip required checks.

## Worktree lifecycle

Resolve the installed `clean-worktrees` dependency through the consumer's
registry or catalog. Read its `references/lifecycle.md` before selecting a
workspace. If unavailable, name the missing dependency and continue inspection
that does not need a checkout.

## Procedure

1. Pin the baseline and candidate SHA/tree, or explicitly describe uncommitted
   changes being checked. Inspect the actual diff and affected consumers. Identify
   the behaviors and integration risks that require evidence.
2. Select the smallest sufficient checks satisfying the project contract: relevant
   unit tests, types/lint, and affected integration or UI scenarios. Read the
   project's test-writing instructions before adding/editing tests. Avoid tests
   that merely mirror implementation. Documentation-only changes normally need
   links/format/registry checks rather than application builds.
3. Execute focused checks first. Expand for required project gates, changed shared
   behavior, failures, explicit requests, or unresolved risk. Resolve executable
   commands from the documented source, such as package scripts or build targets.
   For an added or changed required check, verify the clean case and an isolated
   intentional violation through its real hook, job or command entry point.
   Record which check failed and how the caller reported the failure.
   Do not assume a command named `verify` includes a production build. A required
   delivery preflight is a separate obligation handled by deliver-to.
4. Before a heavy local build, resolve applicable project/machine resource policy
   and enforce its limits on the actual build workers. If required enforcement is
   unavailable, stop that build and report the blocker. Apply limits and concurrency
   rules to their declared scope; a build-only rule does not automatically apply
   to tests, lint, or typecheck. Do not invent a company-wide memory budget.
5. Distinguish regressions from baseline failures by reproducing the same command
   under equivalent conditions on the pinned baseline when attribution matters.
   Use a temporary isolated worktree only when needed under the lifecycle above;
   preserve existing dirty work.
   Do not label failures pre-existing based only on unchanged filenames. Baseline
   failures that prevent validating affected behavior remain an evidence gap.
6. Record command/job, revision, outcome, and limitations. Reuse evidence only
   when relevant content, dependencies, configuration and environment still match.
   Passing source tests do not automatically cover a different integration tree.
7. Report passed, failed, and unrun checks separately. State whether essential
   risks and required gates are covered, explain any blocker, and stop once
   sufficient evidence is obtained. Verification success is not proof of
   deployment or product acceptance.
