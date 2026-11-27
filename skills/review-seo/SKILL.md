---
name: review-seo
description: Review changes that affect discoverability, rendered metadata or indexing of public routes.
---

# Review discoverability

1. Read `docs/agents/workflows/review.md#seo` and the approved requirements.
   Resolve affected public URLs and their intended indexing behavior.
2. Compare observable responses and rendered metadata with that intent. Check
   affected status codes, redirects, canonical URLs, robots directives, sitemap
   entries and structured data. Derive expected values from the approved
   policy and route relationship.
3. Return affected URLs, expected and observed behavior, findings with evidence
   and impact, and any part of the deployed configuration you could not verify.
