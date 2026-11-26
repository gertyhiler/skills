# Personal engineering skills

This repository publishes Andrew's reusable engineering procedures. Documentation,
skills and commit messages are English. Keep skills flat under skills/<name>/.

Read README.md and docs/project-contract.md before changing a skill. Preserve the
split between a reusable procedure and a consumer project's commands, targets,
authorization and workflow. Do not introduce a mandatory agent daemon, private
service, fixed branch name or hidden company default.

Treat skills as source material while editing this repository. Apply delivery and
cleanup procedures only when requested. Keep skills self-contained by default.
Declare required skill dependencies in `agents/skillsx.json` and pin upstream
packages to their exact Git URL, path and commit. Keep project-selected companions
in the consumer workflow. Preserve explicit invocation policy when adapting an
existing skill.

Run `make verify` on the current candidate after edits and before reporting
completion. Report the checked SHA or diff, commands and observed outcomes.
Reuse evidence only when the checked content and relevant conditions match.
Report any failed or unrun required check and its reason as an unresolved check.
Test access helpers with isolated fixtures and fictional credentials. Review
risky workflow changes against realistic scenarios alongside structural checks.
No automatic multi-agent fanout, review loop, publishing or baseline acceptance.
No application build or deployment exists in this documentation repository.
Local research and evidence belong in ignored .agents/work/.
