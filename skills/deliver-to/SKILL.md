---
name: deliver-to
description: Deliver a branch or selected commits to a non-production environment using merge or scoped cherry-pick, required preflight checks, push, and deployment tracking. Use when asked to update a development, test, or staging environment while preserving its existing changes.
---

# Deliver to a non-production environment

Use `$deliver-to stage` (or another project-defined environment) to name the
target. Resolve that name through the project runbook; it is not automatically a
Git branch or deployment command.

## Resolve the project contract

Read applicable `AGENTS.md` instructions and follow the **Environment delivery**,
**Verification**, and hosting-access runbook pointers (for example, **GitLab access**). Paths are project-defined;
direct project instructions or explicit user inputs can supply the same contract.
Obtain:

- environment names and their target refs/remotes;
- whether targets accumulate changes, and the permitted integration method;
- required preflight commands, target build configuration, and resource limits;
- automatic/manual pipeline behavior, required build/deploy jobs, and how to
  identify the deployed revision;
- runtime acceptance requirements and any authorized task-tracker handoff;
- the permitted worktree location.

Check these inputs against current repository/CI configuration. Missing or
contradictory information blocks only its dependent steps: name the exact gap and
continue safe diagnostics. Never guess an environment ref, build command, deploy
job, or a policy exemption. This skill does not establish shared environment
branches, Docker preflights, a memory budget, or lean verification as company-wide
requirements.

## Scope

Deliver into existing target history using a normal merge or scoped cherry-pick.
Preserve existing target changes. Resetting/repointing a target to feature HEAD or
force-pushing is outside this workflow. If project topology requires a different
mechanism, report the mismatch before mutation. Production delivery is outside
this skill.

An explicit request to deliver to a named environment authorizes necessary local
integration, required preflight, normal push, and observing deployment within that
scope. Follow declared authorization for manual pipeline/deployment actions.
Unrelated targets and source changes remain outside scope. Task-tracker mutations
follow the project's separate workflow and authorization; deployment alone does
not authorize closing an issue.

## Procedure

1. Resolve the requested source SHA/commit range and named targets. Fetch current
   refs. Record source and target SHAs, check whether changes are already delivered,
   and preserve dirty worktrees. Use an isolated clean target worktree.
2. State source -> target topology before branch mutation. Prefer a normal merge
   when the complete source-only scope is intended. Inspect commits and diff;
   divergence alone is not an error. Use cherry-pick when only identified commits
   are authorized or merging would import unrelated history. Record the ordered
   commit list and dependencies. Pause if scope or conflict resolution is unclear.
3. Prepare the candidate from the current target. Preserve existing target changes
   and intended source behavior; inspect the delivery diff and conflict resolutions.
   For merge, check source ancestry. For cherry-pick, map original to resulting
   commits and verify patch/content equivalence instead of expecting original SHAs
   to become ancestors.
4. Perform the project's required preflight on the integrated candidate with the
   target configuration. If a build is required, enforce the declared resource
   limits on the actual workers before starting. Record SHA/tree, command, build
   inputs, result, and enforced limits. Reuse evidence only for matching relevant
   content, inputs and configuration. Failed required checks or unavailable required
   enforcement block publication.
5. Follow the project's verification policy. A lean delivery policy may reuse
   earlier unit/lint/typecheck evidence and omit an automatic full verification
   pass; it must be explicitly selected by the project. Even then, integration
   edits/conflicts or unresolved risks require proportionate additional checks.
   Missing policy is not permission to skip preflight or essential verification.
6. Recheck the remote target before a normal push. If it advanced, integrate its
   new state and reassess candidate/preflight evidence; never overwrite concurrent
   work. Push only requested targets and verify remote SHAs. Preserve source history.
7. Locate the pipeline for the exact pushed SHA AND target ref using the project's
   access procedure. Observe required build/deploy jobs from that revision. For
   automatic delivery, wait for its pipeline rather than starting a duplicate.
   Execute manual steps only within declared authorization. Push, pipeline creation,
   and image build do not prove deployment. Report missing/manual/failed/cancelled
   jobs or superseding deliveries; an older successful pipeline is not evidence.
8. Apply project runtime acceptance requirements after deployment. If the project
   explicitly uses a lean workflow without runtime checks, report runtime as
   unverified. Otherwise obtain required runtime evidence or report delivery as
   deployed with acceptance incomplete. Follow the separate task-tracker workflow
   only when its prerequisites and authorization are satisfied.
9. Report each target, delivered SHA, merge/cherry-pick mapping, preflight results,
   pipeline/deploy evidence, runtime acceptance, and tracker updates separately.
   One environment's success does not prove another. Do not claim deployment while
   it is pending or product acceptance based solely on a successful deploy job.
