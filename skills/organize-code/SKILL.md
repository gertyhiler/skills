---
name: organize-code
description: Locate responsibilities at the right module boundary and reorganize code while preserving behavior. Use for module-structure changes and reuse decisions.
---

# Organize code by responsibility

Read `docs/agents/architecture.md`, `docs/agents/coding-standards.md`,
`docs/agents/testing.md`, root `CONTRIBUTING.md` and their applicable linked rules.
Inspect the current module, callers and neighboring examples. The project defines
its layers, imports, naming and public APIs.

1. Identify the behavior and its narrowest owner. Check whether an existing API
   or module can serve current consumers. Keep cohesive code together and expose
   only what other modules need. Extract shared behavior when its contract is
   stable and a concrete additional consumer needs it.
2. Use [Fowler's refactoring catalog](https://refactoring.com/catalog/) to choose
   the smallest behavior-preserving move. Consider **Move Function** when a
   responsibility follows another module's data, **Extract Function** when a
   distinct operation needs a name, and **Inline Function** when indirection adds
   no useful boundary. Treat a smell as a reason to inspect ownership and change
   cost. Verify the problem and the expected improvement before reorganizing.
3. Keep changes small enough to verify each move. Confirm imports and public
   entry points still work. Exercise the affected consumers with the project
   checks and report what moved, its new owner and evidence of preserved behavior.

Keep module organization within the requested scope. For a change that needs a
new project-wide convention, identify the decision and its affected consumers.
