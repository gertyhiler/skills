# Scope and provenance

This is Andrew's personal collection, adapted from procedures written for daily
engineering work. It includes newly extracted workflows and procedures revised
for use outside their original project.

- The verification, delivery, release and worktree procedures came from repeated
  Git/integration work. Their source version was extracted on October 1, 2026.
- Runtime tracing was adapted from a Next.js debugging procedure. The public
  version keeps the evidence cycle but requires a host-specific local adapter;
  it does not pretend one route implementation works in every framework.
- Testing and module-ownership guidance was adapted from personal procedures used
  across client projects. Mandatory dependencies on other skills, fixed viewport
  matrices, private paths and project-specific approval policies were removed.
- Delivery review and runtime investigation were extracted from project-specific
  procedures. Grafana and PostgreSQL helpers preserve the investigation contracts while removing private service
  maps, paths and fixtures. Their original Node implementations were migrated to
  Python with isolated uv script dependencies. The public PostgreSQL
  adapter deliberately supports investigation reads only.
- Upstream community skills and vendor manuals are not bundled or relabeled as
  personal work. This repository does not copy corporate templates, assets,
  credentials, client data or internal access instructions.

The public adaptations are maintained here. They are not automatically installed
into private projects, nor do updates silently replace existing consumer copies.
The source repositories remain independent. Attribution does not imply employer
or client endorsement.

## Boundary

The repository contains selected reusable procedures. It is not a replacement
for project documentation, a task tracker, an agent daemon, or a collection of
all prompts on my machine. Architecture choices such as FSD remain project-owned.
