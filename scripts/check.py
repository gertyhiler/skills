"""Validate the published skill structure; this does not execute skill workflows."""
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []
skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
if not skills:
    errors.append("No skills found")
for path in skills:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", content, re.S)
    try:
        metadata = yaml.safe_load(match[1]) if match else None
        if not isinstance(metadata, dict):
            raise ValueError("missing YAML frontmatter")
        if metadata.get("name") != path.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.parent.name):
            raise ValueError("name must match the kebab-case directory")
        if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
            raise ValueError("description must be nonempty text")
        if not content[match.end():].strip():
            raise ValueError("missing instructions")
        agent_file = path.parent / "agents/openai.yaml"
        if agent_file.exists():
            agent = yaml.safe_load(agent_file.read_text(encoding="utf-8"))
            policy = agent.get("policy", {})
            if "allow_implicit_invocation" in policy and type(policy["allow_implicit_invocation"]) is not bool:
                raise ValueError("allow_implicit_invocation must be boolean")
    except (ValueError, yaml.YAMLError, AttributeError, TypeError) as error:
        errors.append(f"{path.relative_to(ROOT)}: {error}")

# Only maintained documentation, never local scratch or installed dependencies.
for path in [*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md"), *(ROOT / "skills").rglob("*.md")]:
    content = path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", content):
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            continue
        local = target.split("#", 1)[0]
        resolved = (path.parent / local).resolve()
        if not resolved.is_relative_to(ROOT) or not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken or external local link {target}")
if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Validated {len(skills)} skills and local documentation links (structural checks only).")
