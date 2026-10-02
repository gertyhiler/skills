---
name: organize-module-code
description: Place files by ownership, distinguish UI primitives from composed components and organize mixed model/helper/lib folders. Use for module-structure changes and reuse decisions; follow the project's architecture rather than imposing FSD.
---

# Organize code by responsibility

Read the project's architecture and code-organization contract through AGENTS.md.
Inspect the actual module, consumers and neighboring implementations first. If
FSD is the project architecture, respect its layer direction, slice boundaries
and public APIs. Otherwise use the declared boundaries; do not add FSD layers.

Find the narrowest owner of the behavior. Search existing primitives, components,
hooks and helpers before introducing a new abstraction. Promote code to shared
only when there is a stable cross-domain contract and a credible additional
consumer. Keep feature orchestration local even when it uses shared primitives.

## Distinguish responsibilities

- UI primitives: foundational controls and presentation, such as a link or button.
- Components: reusable compositions of primitives or more involved behavior.
- Utilities: domain-independent pure operations.
- Helpers: pure operations expressed in the owning domain's contracts.
- Hooks: React lifecycle or local-state behavior, when React is in use.
- Contexts: dependency provision across a component subtree.
- Stores: actual shared mutable state or state machines.
- Libraries: cohesive internal subsystems with their own boundary, not a bucket
  for unrelated helpers or mappers.

Keep a small cohesive module flat. When a model folder contains multiple concerns,
group/names should expose constants, calculations, lifecycle, stores and transport
responsibilities. A generic state folder is not a substitute for identifying an
owner. Do not introduce a store directory for pure state calculations.

Expose a public API where cross-module consumers need it, following the project's
existing import contract. Keep implementation folders private. A widget may keep
its composition root at the slice root while local visual parts live in ui; this
is a project choice, not a universal directory rule.

For structural changes, verify imports and affected consumers. Explain what moved,
why its new owner is correct and how behavior was preserved. Do not make a
repository-wide refactor, new framework or mandatory review chain part of a
small organization task.
