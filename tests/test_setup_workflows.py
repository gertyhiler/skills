import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/setup-workflows/scripts/audit.py"
CONTRACT = "agents/project-docs.json"
CHECKS = "docs/agents/workflows/verification.md"
TESTING = "docs/agents/testing.md"


class SetupWorkflowsTest(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def registry(self, skills):
        self.write(
            ".agents/skills.registry.json",
            json.dumps({"version": 1, "categories": {"review": {}},
                        "sources": {"fixture": {"type": "git", "url": "https://example.invalid/skills.git"}},
                        "agents": {}, "skills": skills}),
        )

    def skill(self, name, required=None, category=None):
        location = f".agents/skills/{category}/{name}" if category else f".agents/skills/{name}"
        self.write(f"{location}/SKILL.md", f"---\nname: {name}\n---\n")
        if required is not None:
            self.write(f"{location}/{CONTRACT}", json.dumps({"version": 1, "required": required}))
        return location

    def run_audit(self, status):
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, status, run.stdout + run.stderr)
        self.assertEqual(run.stderr, "")
        return json.loads(run.stdout)

    def entrypoints(self):
        self.write("AGENTS.md", "# Agent instructions\n")
        self.write("CONTRIBUTING.md", "# Contributing\n")

    def test_audit_detects_missing_section_and_pair_without_inferring_other_workflows(self):
        skill_dir = self.skill("review-tests", [TESTING, f"{CHECKS}#checks"], category="review")
        self.registry({"review-tests": {"categoryId": "review", "source": {
            "id": "fixture", "path": "skills/review-tests", "revision": "a" * 40
        }}})
        self.entrypoints()
        self.write(CHECKS, "# Verification\n\n```md\n## Checks\n```\n")
        self.write(TESTING, "# Testing\n\n[Workflow](workflows/verification.md)\n")

        result = self.run_audit(1)
        self.assertEqual(result["skills"], [
            {"id": "review-tests", "path": f"{skill_dir}/SKILL.md",
             "authority": "managed", "contract": "declared"}
        ])
        self.assertEqual(set(item["path"] for item in result["documents"]), {
            "AGENTS.md", "docs/TESTING.md", TESTING, CHECKS
        })
        self.assertEqual({item["kind"] for item in result["findings"]},
                         {"missing-document", "missing-pair-link", "missing-anchor", "missing-verification-link"})

    def test_fixed_anchor_and_pair_links_pass_and_two_reads_are_noop(self):
        self.skill("design-tests", [TESTING])
        self.registry({"design-tests": {}})
        self.entrypoints()
        self.write("docs/TESTING.md", "# Test policy\n")
        self.write(CHECKS, '# Verification\n\n<a id="checks"></a>\n## Проверки\n')
        self.write(TESTING, f"# Testing\n\n[Policy](../TESTING.md)\n"
                            f"[Checks](workflows/verification.md#checks)\n"
                            "```md\n[Template](no-such-template.md)\n```\n")

        def project_bytes():
            return {str(path.relative_to(self.root)): path.read_bytes()
                    for path in self.root.rglob("*") if path.is_file()}

        before = project_bytes()
        result = self.run_audit(0)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result, self.run_audit(0))
        self.assertEqual(before, project_bytes())

    def test_broken_link_and_pair_link_are_reported(self):
        self.skill("design-tests", [TESTING])
        self.registry({"design-tests": {}})
        self.entrypoints()
        self.write("docs/TESTING.md", "# Test policy\n")
        self.write(CHECKS, "## Checks\n")
        self.write(TESTING, "# Agent testing\n\n[Policy](../TESTING.md#missing)\n"
                            "[Checks](workflows/verification.md#checks)\n")

        result = self.run_audit(1)
        self.assertEqual({item["kind"] for item in result["findings"]}, {"missing-pair-link", "broken-link"})

    def test_undeclared_and_uninstalled_skills_do_not_activate_requirements(self):
        self.registry({"code-review": {}, "no-copy": {}})
        installed = self.skill("code-review")
        self.write(f"{installed}/references/example/SKILL.md", "# Bundled example\n")
        self.write(f".agents/skills/no-copy/{CONTRACT}",
                   json.dumps({"version": 1, "required": [TESTING]}))
        rogue = self.skill("rogue", [TESTING])
        self.write(".claude/skills/projected/SKILL.md", "# Projection\n")

        result = self.run_audit(1)
        self.assertEqual(result["documents"], [])
        self.assertEqual(result["findings"], [
            {"kind": "unregistered-skill", "path": f"{rogue}/SKILL.md"},
            {"kind": "missing-skill", "path": ".agents/skills/no-copy/SKILL.md", "skill": "no-copy"},
        ])

    def test_invalid_manifest_does_not_choose_an_alternative_path(self):
        self.registry({"design-tests": {}})
        self.skill("design-tests", ["docs/agents/../TESTING.md", TESTING])

        result = self.run_audit(1)
        self.assertEqual(result["skills"][0]["contract"], "invalid")
        self.assertEqual(result["documents"], [])
        self.assertEqual(result["findings"][0]["kind"], "invalid-contract")

    def test_incomplete_link_and_wrong_existing_fragment_do_not_satisfy_contract(self):
        self.skill("design-tests", [TESTING])
        self.registry({"design-tests": {}})
        self.entrypoints()
        self.write("docs/TESTING.md", "# Test policy\n")
        self.write(CHECKS, "## Setup\n\n## Checks\n")
        self.write(TESTING, "[Policy](../TESTING.md\n[Verification](workflows/verification.md#setup)\n")
        result = self.run_audit(1)
        self.assertEqual({item["kind"] for item in result["findings"]},
                         {"missing-pair-link", "missing-verification-link"})

    def test_invalid_source_and_empty_skill_are_reported(self):
        skill = self.skill("design-tests", [TESTING])
        self.registry({"design-tests": {"source": False}})
        self.assertEqual(self.run_audit(2)["findings"][0]["kind"], "invalid-inventory")
        self.registry({"design-tests": {}})
        self.write(f"{skill}/SKILL.md", "")
        self.assertEqual(self.run_audit(1)["findings"][0]["kind"], "empty-skill")

    def test_missing_registry_has_no_global_fallback(self):
        self.skill("design-tests", [TESTING])
        result = self.run_audit(2)
        self.assertEqual(result["findings"][0]["kind"], "invalid-inventory")
        self.assertEqual(result["skills"], [])
