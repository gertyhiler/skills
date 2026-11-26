---
name: review-compatibility
description: Evaluate whether a pinned change candidate can operate with the service revisions and contracts in a target environment. Use when preparing or reviewing delivery across a changed service, API, migration, or artifact boundary.
---

# Review compatibility at the delivery boundary

1. Read the consumer project's release or environment delivery workflow. Identify
   the exact candidate and the changed behavior that crosses a service, data or
   artifact boundary. The project identifies authoritative records, required
   evidence, and permitted checks. Work read-only during assessment.
2. Find the revision actually deployed for each affected service in the intended
   environment. Associate it with its successful deploy job, environment and
   timestamp or a verified runtime artifact. Follow the actual consumer route
   when it points to another environment. A branch head, package version, image
   build or green pipeline alone is insufficient. For an explicitly historical
   assessment, use only records available at the given instant and name the cutoff.
3. Trace the candidate's affected entry point through the consumer and the pinned
   provider revision. Compare the relevant routes, methods, request and response
   contracts, configuration, state changes and migrations. Use read-only code,
   approved isolated scenarios or matching evidence to show a concrete successful
   path or failure. When the release is coordinated, pin each planned revision and
   verify the order and the compatibility during the transition.
4. Report the candidate tree, deployed and proposed dependency SHAs, environment,
   sources, specific result, and any step still blocked by missing evidence.
   Distinguish a demonstrated mismatch from an unverified dependency. A deployment
   or infrastructure smoke result proves only the scope it actually exercised.
