"""Inspect installed SkillsX documentation contracts without modifying the project."""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote, urlsplit


REGISTRY = ".agents/skills.registry.json"
STORE = ".agents/skills"
MANIFEST = "agents/project-docs.json"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
ANCHOR = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*\Z")
PAIRS = {
    "docs/agents/architecture.md": "docs/ARCHITECTURE.md",
    "docs/agents/coding-standards.md": "docs/CODING_STANDARDS.md",
    "docs/agents/testing.md": "docs/TESTING.md",
}
INLINE_LINK = re.compile(
    r"""(?<!!)\[[^\]\n]*\]\(\s*(?:<([^>\n]*)>|([^\s)]+))(?:\s+(?:"[^"\n]*"|'[^'\n]*'))?\s*\)"""
)
EXPLICIT_ID = re.compile(r'''<a\s+(?:id|name)=["']([^"']+)["']\s*>\s*</a>''', re.IGNORECASE)
HEADING = re.compile(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def object_without_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON has a duplicate key")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=object_without_duplicate_keys)


def exact_path(root, relative):
    path = root
    for component in PurePosixPath(relative).parts:
        path /= component
        if path.is_symlink():
            raise ValueError(f"symbolic link at {path.relative_to(root).as_posix()}")
    return path


def read_lines(markdown):
    """Return lines outside fenced code and HTML comments."""
    fence = None
    markdown = re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)
    for line in markdown.splitlines():
        marker = FENCE.match(line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if fence is None:
            yield line


def markdown_data(path):
    headings, links, pending_ids = set(), [], set()
    for line in read_lines(path.read_text(encoding="utf-8")):
        ids = set(EXPLICIT_ID.findall(line))
        line = EXPLICIT_ID.sub("", line)
        match = HEADING.match(line)
        if match:
            title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", match[1])
            title = re.sub(r"[^\w\s-]", "", title.lower()).replace(" ", "-")
            headings.update({title, *ids, *pending_ids})
            pending_ids.clear()
        elif line.strip():
            pending_ids.clear()
        else:
            pending_ids.update(ids)
        line = re.sub(r"(`+).*?\1", "", line)
        links.extend((match[1] or match[2]) for match in INLINE_LINK.finditer(line))
    return headings, links


def requested_document(reference):
    if not isinstance(reference, str):
        raise ValueError("required entries must be strings")
    project_path, delimiter, anchor = reference.partition("#")
    parts = project_path.split("/")
    if (
        any(not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", part) for part in parts)
        or not project_path.endswith(".md")
        or not (project_path == "CONTRIBUTING.md" or parts[:2] == ["docs", "agents"] and len(parts) > 2)
        or delimiter and not ANCHOR.fullmatch(anchor)
    ):
        raise ValueError("expected an exact docs/agents Markdown path or CONTRIBUTING.md with a fixed anchor")
    return project_path, anchor


def inventory(root, findings):
    """Use the SkillsX v1 store layout and configured categories."""
    registry_path = exact_path(root, REGISTRY)
    if not registry_path.is_file():
        raise ValueError("SkillsX project registry is missing")
    registry = read_json(registry_path)
    if (
        not isinstance(registry, dict)
        or type(registry.get("version")) is not int
        or registry["version"] != 1
        or any(not isinstance(registry.get(key), dict)
               for key in ("skills", "categories", "sources", "agents"))
    ):
        raise ValueError("expected a SkillsX v1 registry")
    installed = {}
    for skill_id, entry in sorted(registry["skills"].items()):
        if not NAME.fullmatch(skill_id) or not isinstance(entry, dict):
            raise ValueError("invalid skill ID or record in the SkillsX registry")
        if "source" in entry:
            source = entry["source"]
            if (
                not isinstance(source, dict)
                or any(not isinstance(source.get(key), str) or not source[key]
                       for key in ("id", "path", "revision"))
                or source["id"] not in registry["sources"]
            ):
                raise ValueError(f"invalid recorded source for {skill_id}")
        category = entry.get("categoryId")
        if "categoryId" in entry and (
            not isinstance(category, str) or not NAME.fullmatch(category) or category not in registry["categories"]
        ):
            raise ValueError(f"invalid recorded category for {skill_id}")
        directory = f"{STORE}/{category}/{skill_id}" if category else f"{STORE}/{skill_id}"
        installed[directory] = (skill_id, entry)
    store = exact_path(root, STORE)
    discovered = set()
    if store.is_dir():
        for item in sorted(store.iterdir()):
            if item.is_symlink() or not item.is_dir() or not NAME.fullmatch(item.name):
                continue
            if (item / "SKILL.md").is_file():
                discovered.add(item.relative_to(root).as_posix())
                continue
            for child in sorted(item.iterdir()):
                if not child.is_symlink() and child.is_dir() and (child / "SKILL.md").is_file():
                    discovered.add(child.relative_to(root).as_posix())
    for directory in sorted(discovered - installed.keys()):
        findings.append({"kind": "unregistered-skill", "path": f"{directory}/SKILL.md"})
    return installed


def audit(root):
    root = root.resolve(strict=True)
    findings = []
    skills = []
    required = {}

    def record(kind, path, **metadata):
        findings.append({"kind": kind, "path": path, **metadata})

    def require(path, skill_id, anchor=""):
        anchors = required.setdefault(path, {})
        anchors.setdefault(anchor, set()).add(skill_id)

    try:
        installed = inventory(root, findings)
    except (ValueError, OSError) as error:
        record("invalid-inventory", REGISTRY, reason=str(error))
        return {"status": "invalid-inventory", "skills": [], "documents": [], "findings": findings}

    for directory, (skill_id, entry) in sorted(installed.items(), key=lambda item: item[1][0]):
        skill = {"id": skill_id, "path": f"{directory}/SKILL.md",
                 "authority": "managed" if "source" in entry else "repository"}
        skills.append(skill)
        manifest_path = f"{directory}/{MANIFEST}"
        try:
            skill_file = exact_path(root, skill["path"])
            if not skill_file.is_file():
                skill["contract"] = "unavailable"
                record("missing-skill", skill["path"], skill=skill_id)
                continue
            if not skill_file.read_text(encoding="utf-8").strip():
                skill["contract"] = "unavailable"
                record("empty-skill", skill["path"], skill=skill_id)
                continue
            manifest = exact_path(root, manifest_path)
            if not manifest.exists():
                skill["contract"] = "undeclared"
                continue
            data = read_json(manifest)
            if (not isinstance(data, dict) or set(data) != {"version", "required"}
                    or type(data["version"]) is not int or data["version"] != 1
                    or not isinstance(data["required"], list)):
                raise ValueError("expected version 1 and a required array")
            references = [requested_document(item) for item in data["required"]]
            if len(set(references)) != len(references):
                raise ValueError("duplicate required document entry")
            skill["contract"] = "declared"
            for path, anchor in references:
                require(path, skill_id, anchor)
                if path in PAIRS:
                    require(PAIRS[path], skill_id)
                if path == "docs/agents/testing.md":
                    require("docs/agents/workflows/verification.md", skill_id, "checks")
        except (ValueError, OSError) as error:
            skill["contract"] = "invalid"
            record("invalid-contract", manifest_path, skill=skill_id, reason=str(error))

    if required:
        require("AGENTS.md", "setup-workflows")

    documents = []
    markdown_cache = {}

    def markdown_at(path):
        if path not in markdown_cache:
            markdown_cache[path] = markdown_data(path)
        return markdown_cache[path]

    def resolve_link(document, raw):
        if raw.startswith("//"):
            return None
        try:
            location = urlsplit(raw)
            if location.scheme or location.netloc:
                return None
            if location.path.startswith("/"):
                return None  # The hosting site, not this repository.
            target = (document.parent / unquote(location.path)).resolve() if location.path else document
            if not target.is_relative_to(root):
                return False
            if not target.exists():
                return False
            if location.fragment and target.is_file() and target.suffix == ".md":
                if unquote(location.fragment) not in markdown_at(target)[0]:
                    return False
            return target.relative_to(root).as_posix(), unquote(location.fragment)
        except (OSError, ValueError):
            return False

    for path, inputs in sorted(required.items()):
        document = {"path": path, "requiredBy": sorted(set().union(*inputs.values())),
                    "anchors": sorted(set(inputs) - {""})}
        documents.append(document)
        try:
            actual = exact_path(root, path)
            if not actual.is_file():
                record("missing-document", path)
                continue
            headings, links = markdown_at(actual)
        except (ValueError, OSError) as error:
            record("invalid-document", path, reason=str(error))
            continue
        for anchor in document["anchors"]:
            if anchor not in headings:
                record("missing-anchor", path, anchor=anchor, skills=sorted(inputs[anchor]))
        targets = set()
        for link in sorted(set(links)):
            target = resolve_link(actual, link)
            if target is False:
                record("broken-link", path, link=link)
            elif target is not None:
                targets.add(target)
        if path in PAIRS and (PAIRS[path], "") not in targets:
            record("missing-pair-link", path, target=PAIRS[path])
        if path == "docs/agents/testing.md":
            if ("docs/agents/workflows/verification.md", "checks") not in targets:
                record("missing-verification-link", path, target="docs/agents/workflows/verification.md#checks")

    return {"status": "needs-attention" if findings else "ready",
            "skills": skills, "documents": documents, "findings": findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="consumer repository root")
    args = parser.parse_args()
    try:
        result = audit(args.root)
    except OSError as error:
        parser.exit(2, f"{error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"ready": 0, "needs-attention": 1, "invalid-inventory": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
