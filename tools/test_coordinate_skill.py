"""Pins the public Coordinator skill and its split from /run.

`/coordinate` is the discoverable coordination front door. It must stay out of
the harness plugin (that package is `run` only) and must not revive the retired
execution-skill adapter paths.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "crypto-autoresearcher-harness" / "scripts"))

import entrypoints  # noqa: E402

CANONICAL = ROOT / ".claude" / "skills" / "coordinate" / "SKILL.md"
ADAPTER = ROOT / ".agents" / "skills" / "coordinate" / "SKILL.md"
RETIRED = (
    ROOT / ".claude" / "skills" / "coordinate-research-goal" / "SKILL.md",
    ROOT / ".claude" / "skills" / "launch-research-harness" / "SKILL.md",
    ROOT / ".claude" / "skills" / "crypto-autoresearcher-harness" / "SKILL.md",
    ROOT / ".agents" / "skills" / "crypto-autoresearcher-harness" / "SKILL.md",
)


def _frontmatter_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^name:\s*(\S+)\s*$", text)
    if match is None:
        raise AssertionError(f"{path} has no frontmatter name")
    return match.group(1)


class CoordinateSkillTests(unittest.TestCase):
    def test_canonical_skill_is_coordinate_not_run(self) -> None:
        self.assertTrue(CANONICAL.is_file(), f"missing {CANONICAL}")
        body = CANONICAL.read_text(encoding="utf-8")
        self.assertEqual(_frontmatter_name(CANONICAL), "coordinate")
        self.assertIn("Not an execution skill", body)
        self.assertIn("/run", body)
        self.assertRegex(body, r"never launches scientific trials|Do not launch scientific trials")
        self.assertIn("paused", body)
        self.assertIn("blocked", body)
        self.assertIn("agents/coordinator.md", body)

    def test_host_adapter_delegates_to_canonical(self) -> None:
        self.assertTrue(ADAPTER.is_file(), f"missing {ADAPTER}")
        self.assertEqual(_frontmatter_name(ADAPTER), "coordinate")
        body = ADAPTER.read_text(encoding="utf-8")
        self.assertIn(".claude/skills/coordinate/SKILL.md", body)
        self.assertIn("$run", body)

    def test_retired_execution_adapters_stay_gone(self) -> None:
        for path in RETIRED:
            self.assertFalse(path.exists(), f"retired adapter reappeared: {path}")

    def test_not_packaged_inside_run_plugin(self) -> None:
        plugin_skills = ROOT / "plugins" / "crypto-autoresearcher-harness" / "skills"
        extras = [
            path for path in plugin_skills.rglob("SKILL.md")
            if path != plugin_skills / "run" / "SKILL.md"
        ]
        self.assertEqual(extras, [])
        self.assertEqual(entrypoints.check(ROOT), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
