"""Skill routing controls; no cataloged program is imported or executed."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repo_skill_catalog", ROOT / "tools/skill_catalog.py")
catalog_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog_tool)


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.catalog = catalog_tool.load_catalog(ROOT)

    def test_every_execution_topic_preserves_run(self):
        for topic in self.catalog["topics"]:
            with self.subTest(topic=topic):
                result = catalog_tool.route(self.catalog, "run", topic)
                self.assertEqual(result["primary_skill"], "run")
                self.assertTrue(result["selection_only"])
                self.assertIn("no assessment preflight", result["execution"])

    def test_lifecycle_is_not_overridden_by_domain(self):
        for intent, expected in {"design": "design-experiment", "review": "review-evidence",
                                 "coordinate": "coordinate", "status": "research-status",
                                 "ideas": "propose-ideas", "curate": "curate-knowledge"}.items():
            result = catalog_tool.route(self.catalog, intent, "solver")
            self.assertEqual(result["primary_skill"], expected)
            self.assertEqual(result["supporting_profiles"], ["solver"])

    def test_topic_only_actions_use_profiles(self):
        self.assertEqual(catalog_tool.route(self.catalog, "inspect", "endo")["primary_skill"], "endo")
        self.assertEqual(catalog_tool.route(self.catalog, "implement", "gpu")["primary_skill"], "gpu")
        self.assertEqual(catalog_tool.route(self.catalog, "maintain", "ui")["primary_skill"], "ui")
        self.assertEqual(catalog_tool.route(self.catalog, "choose", "all")["primary_skill"], "route")

    def test_invalid_selection_refused(self):
        for intent, topic in [("attack", "solver"), ("run", "unknown")]:
            with self.assertRaises(ValueError):
                catalog_tool.route(self.catalog, intent, topic)

    def test_missing_skill_cannot_be_routed(self):
        broken = copy.deepcopy(self.catalog)
        broken["skills"] = [s for s in broken["skills"] if s["name"] != "run"]
        with self.assertRaises(ValueError):
            catalog_tool.route(broken, "run", "solver")

    def test_catalog_adapters_and_metadata(self):
        # Snapshot scope is deliberate: fixtures and this API-created branch need
        # not contain all producing repositories/runtime dependencies.
        result = catalog_tool.check(ROOT, self.catalog, snapshot_only=True)
        self.assertTrue(result["ok"], result["errors"])
        self.assertFalse(result["runtime_verified"])

    def test_stale_description_and_duplicate_names_fail(self):
        broken = copy.deepcopy(self.catalog)
        broken["skills"][0]["description"] = "stale"
        broken["skills"].append(copy.deepcopy(broken["skills"][0]))
        result = catalog_tool.check(ROOT, broken, snapshot_only=True)
        self.assertFalse(result["ok"])
        self.assertTrue(any("stale catalog" in e for e in result["errors"]))
        self.assertTrue(any("duplicate skill" in e for e in result["errors"]))

    def test_unsafe_paths_refused(self):
        for path in ["/tmp/source", "../source", "tools/../../source"]:
            with self.assertRaises(ValueError):
                catalog_tool.safe_path(ROOT, path)

    def test_duplicate_keys_and_nonfinite_json_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"data.json"
            for content in ['{"a":1,"a":2}', '{"a":NaN}']:
                path.write_text(content)
                with self.assertRaises(ValueError):
                    catalog_tool.read_json(path)

    def test_drift_is_static_and_reports_parse_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/"tools").mkdir()
            (root/"tools/unsafe.py").write_text("def main():\n    raise RuntimeError('must never execute')\n")
            (root/"tools/broken.py").write_text("def :\n")
            (root/"tools/library.py").write_text("VALUE=1\n")
            result = catalog_tool.drift(root, {"entries": []})
            self.assertEqual(result["uncataloged_entrypoints"], ["tools/unsafe.py"])
            self.assertEqual(result["inspection_failures"][0]["path"], "tools/broken.py")
            self.assertEqual(result["execution"], "none")

    def test_pending_tool_is_not_promised_as_installed(self):
        inventory = catalog_tool.read_json(ROOT / self.catalog["inventory"])
        pending = [row for row in inventory["entries"] if row.get("availability") == "pending-pr"]
        self.assertEqual([row["pending_pr"] for row in pending], [1909])
        self.assertTrue(all(row["owner_skill"] == "transfer" for row in pending))


if __name__ == "__main__":
    unittest.main()
