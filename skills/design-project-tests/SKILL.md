---
name: design-project-tests
description: Choose meaningful regression coverage for a change, including unit, integration, browser and visual tests. Use when adding tests, selecting a test level, or replacing tests coupled to implementation details.
---

# Design tests around observable contracts

Read the project's testing policy through AGENTS.md and inspect its actual test
commands and discovery configuration. Name the failure a test should detect
before choosing a framework or writing assertions.

- Use pure tests for business rules, calculations and non-trivial transformations.
- Use integration tests for persistence, security and adapter boundaries.
- Exercise real browser interactions for navigation, focus, state transitions and
  user flows. Use semantic roles and accessible names where available.
- Use reviewed screenshots of the real route/components for visible fidelity.
  They complement behavior tests, not replace them.
- Skip a test that only restates static markup or a trivial implementation without
  protecting a meaningful contract.

Keep mocks at unstable or expensive boundaries and assert the system's observable
outcome. Deterministic browser fixtures should still render production components.
Do not use a pile of mocked return values as evidence of integration.

CSS classes, DOM nesting, node counts and copied source fragments do not establish
visual quality. Semantic link destinations, disabled states or ARIA state can be
valid assertions when they are the actual navigation/accessibility contract.
File/schema assertions are useful when the file format itself is the public
contract; explain that contract rather than asserting incidental source wording.

Select scenarios from affected behavior and risks, including relevant failure
paths. Confirm each new browser spec is discovered by the configured runner.
Use the project's chosen viewports and baseline runtime; inspect intentional
baseline changes. Do not silently create missing images in comparison-only CI.

Run the focused tests and required project checks. Expand for failures, shared
behavior, required gates or unresolved risk. Existing weak tests are not a reason
to add more; repair them only within the requested scope. Report missing evidence
honestly. No TDD ritual, additional reviewer or repository-wide cleanup is implied.
