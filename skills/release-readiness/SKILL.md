---
name: release-readiness
description: Assess production release readiness for the exact integration candidate. Use when a project invokes `$release-readiness` as its release assessment entry point.
---

# Release readiness

Resolve the declared `check-release` package through the consumer registry
at the same source and commit as this entry point. Follow that exact
`SKILL.md`. For a manual installation, use both packages from the same verified
commit. Keep the requesting project's
release workflow, verification requirements and evidence authority in scope.
Report a missing dependency if it cannot be resolved.
