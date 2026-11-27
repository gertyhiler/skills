# Standards and Spec

Use the [report contract](report.md). Read the pinned Matt Pocock `code-review`
declared in the [SkillsX manifest](../agents/skillsx.json). Resolve it through
the consumer registry by source URL, package path and revision. Open the exact
`SKILL.md` if multiple installed packages share the name. If the pinned package
cannot be resolved, record the affected coverage gap.

## Bind the inputs

- **Standards:** read `docs/agents/coding-standards.md` and the applicable human
  standards it links. Include the governing root `CONTRIBUTING.md` and explicit
  scope-specific standards from the project workflow. Send the upstream smell
  guidance with the Standards brief. Apply written project rules first. Ground
  each smell in the change and its maintainability impact.
- **Spec:** use `docs/agents/workflows/review.md#spec` and the approved
  requirements supplied for this candidate. Use `docs/agents/issue-tracker.md`
  for tracker access and `docs/agents/domain.md` for contextual rules and terms.
  Give the reviewer the actual authoritative paths or issue identifiers and the
  approved scope. If authority is missing or contradictory, name the affected
  claim and source gap. Follow explicit sources instead of deriving a spec from
  branch names, nearby files or plausible issue references.

## Run the selected directions

- **Committed:** confirm the exact candidate and comparison base. Use upstream's
  `git diff <fixed-point>...HEAD` when `HEAD` is the candidate and that command
  has the agreed base. Otherwise use `git diff <base-sha> <candidate-sha> --`
  and `git log <base-sha>..<candidate-sha>` with the recorded objects, then read
  files with `git show <candidate-sha>:<path>`. Scope any execution to an
  authorized checkout or fixture whose content matches the candidate.
- **Integration tree without a candidate commit:** use the recorded tree ID
  in `git diff <base-sha> <tree-id> --` and `git show <tree-id>:<path>`. Provide
  the source and target revisions with the tree and report the comparison used.
- **WIP:** use the captured patch and candidate file content for the supplied
  snapshot. Include all selected staged, unstaged and new files.

Apply only the requested pinned briefs. Supply the matching diff, available
commit list and project inputs. For independently reviewed Standards and Spec,
use separate fresh reviewers and retain both reports. For an explicitly requested
direct pass, record the direction, candidate mode and brief used in the pass.

Each reviewer completes its direction directly and returns its report. For Spec,
trace material changed and preserved requirements to the entry point and
observable outcome. Check omissions, incompatible behavior, unapproved scope
and affected boundary cases. Cite the approved requirement per finding and flag
relevant stale domain descriptions. For Standards, cite the violated project
rule or explain the impact of the named heuristic. Execute scenarios only in a
matching checkout or fixture and report any missing execution evidence.
