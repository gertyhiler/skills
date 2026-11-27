---
name: review-docs
description: Review whether changed behavior and documentation agree with their canonical sources.
---

# Review documentation

1. Use `docs/agents/workflows/review.md#documentation` and its linked index to
   identify canonical sources for changed behavior, commands or decisions. Include
   affected documents outside the diff.
2. Verify requirement claims against approved decisions and implementation
   claims against code or observed behavior. Check affected links, paths and
   commands at the authoritative source. Distinguish introduced staleness from
   existing debt and current implementation from historical decisions.
3. Return affected documents with evidence and one status for each relevant scope:
   current, update required, or unaffected. State any missing authority or evidence.
