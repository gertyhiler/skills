---
name: review-design
description: Review whether a rendered interface matches its approved design or other agreed visual reference.
---

# Review design fidelity

1. Read `docs/agents/workflows/review.md#design`. Identify the agreed reference
   and the affected route or component. Compare like-for-like data, states and
   viewport dimensions using the linked design rules.
2. Inspect an actual render at the affected viewports. Compare composition,
   spacing, typography, tokens and state transitions that affect what the user
   sees. Inspect existing regression screenshots when relevant. Their baselines
   and the approved design are separate evidence.
3. Return the reference, route, viewports, states, render evidence, and specific
   discrepancies with user impact. An unavailable reference or render for an
   applicable comparison leaves that comparison unverified.
