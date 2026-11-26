---
name: review-spec
description: Review whether a change implements approved requirements, acceptance criteria, and domain rules.
---

# Review specification compliance

1. Resolve the project workflow's requirement sources and any approved changes to
   scope. List the material requirements that the candidate changes or must preserve.
2. Trace each requirement through the entry point and the observable result.
   Review omissions, incompatible behavior, unapproved scope and affected boundary
   cases. Distinguish a missing requirement from a defect against an approved one.
3. Check whether affected domain descriptions and terms still agree with the
   approved rule. Cite the canonical location. Surface contradictions between
   implementation and approved sources without resolving the policy yourself.
4. Return the candidate and scope, then findings with requirement, case, expected
   behavior, observed behavior and impact. Include evidence gaps and a conclusion
   about the reviewed requirements.
