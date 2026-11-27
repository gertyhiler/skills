# Coordinate an integrated release

1. Pin the requested environment, each candidate, authoritative requirements
   and the release scope using the consuming project's production and
   compatibility workflow. Collect issue links, agreed decisions, repository
   refs, deployed-revision records, and relevant verification results once.
   Record what each source proves and retain the raw references.
2. Determine which affected dependencies will stay deployed and which need
   their own release. Verify the compatible deployed revision for the first
   group. For the second group, resolve its exact candidate using the declared
   project sources. Do not substitute a branch head when the release candidate
   is unresolved. Identify a component assessment by repository, target
   environment, source and target SHAs, merge method, and candidate tree.
3. Assign a fresh independent read-only assessor a full `check-release`
   component assessment for each participating candidate, including the
   requested component. Reuse a recorded independent component verdict only
   when the same inputs, scope, and applicable evidence match. Run independent
   assessments in parallel when the inputs allow it. Hand off the exact
   candidate, effective target, agreed requirements, project rules and raw
   evidence. A component
   assessor coordinates applicable `review` directions and candidate checks
   under that project's policy. If a component is already integrated, verify
   the historical input and actual integration tree, then assess its next
   outstanding release step. A component assessor reports additional
   dependencies to the top coordinator instead of reassigning the entire
   release.
4. The top coordinator assigns one separate independent
   `review-compatibility` assessment of the planned transition states.
   Run it alongside component assessment once the inputs are pinned.
   Identify the actual deployed combination, every
   intermediate combination used by the planned order, and the final
   combination. Include applicable migrations, shared artifacts, configuration
   and external dependencies. For a dependency staying deployed, reuse
   matching evidence for that exact boundary when available. Record the shared
   compatibility decision with each affected component. Component assessors
   evaluate their own readiness and report dependencies or assumptions. The
   compatibility assessor owns the verdict for the planned combinations.
5. Return one integration report with separate component readiness decisions,
   compatibility, and the prerequisites for each step. Preserve technical
   findings, missing required evidence and infrastructure status as separate
   facts. Link the independent results and give the verified identities.
   A release GO requires all participating independent component decisions,
   compatibility evidence for the required transitions, and project and server
   gates. Reassess affected conclusions when a candidate, deployed dependency, or
   required rule changes. Any later report publication, merge or deploy uses
   the project's authorization.
