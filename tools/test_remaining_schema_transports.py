"""Archive fidelity and canonical validation for the remaining schema repair."""
import hashlib
import json
from pathlib import Path
import unittest

import yaml

from tools import validate_ledger as ledger


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/ci-remaining-ledger-schema-20261030/transport-preservation.json"


class RemainingSchemaTransportTests(unittest.TestCase):
    def report(self):
        return json.loads(REPORT.read_text())

    def test_frozen_originals_remain_byte_exact(self):
        for name, expected in self.report()["frozen_originals"].items():
            with self.subTest(path=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_no_unrelated_record_fields_or_citation_provenance_change(self):
        for row in self.report()["changes"]:
            if "original" not in row:
                continue
            old = next(iter(yaml.safe_load((ROOT / row["original"]).read_text()).values()))
            new = next(iter(yaml.safe_load((ROOT / row["replacement"]).read_text()).values()))
            allowed = row["allowed_top_level_changes"]
            self.assertEqual({k: v for k, v in old.items() if k not in allowed},
                             {k: v for k, v in new.items() if k not in allowed})
            if "prior_art" in allowed:
                internal = [x for x in old["prior_art"]["nearest"] if x["ref"].startswith("IDEA-")]
                known = [x for x in old["prior_art"]["nearest"] if x not in internal]
                self.assertEqual(new["prior_art"]["nearest"], known)
                self.assertEqual(new["prior_art"]["related_internal_proposals"], internal)

    def test_external_plans_are_not_inlined_into_handoffs(self):
        for row in self.report()["changes"]:
            if "original" not in row or "/handoffs/" not in row["original"]:
                continue
            old = yaml.safe_load((ROOT / row["original"]).read_text())["handoff"]
            new = yaml.safe_load((ROOT / row["replacement"]).read_text())["handoff"]
            self.assertIsInstance(new["review_plan"], str)
            self.assertEqual(new["schema_transport"]["original_reference"], old["review_plan"])
            self.assertNotIn("coordinator_prior", new["schema_transport"])

    def test_every_source_bound_nonrun_record_passes_native_validation(self):
        baseline = json.loads((REPORT.parent / "original32-focused-errors.json").read_text())
        entries = ledger.load_schema_supersessions(str(ROOT / "tools/schema_supersession_registry.yaml"))
        ctx = ledger.Ctx(set(), schema_supersessions=entries)
        for name in baseline["sources"]:
            kind = next(iter(yaml.safe_load((ROOT / name).read_text())))
            ledger.check_ledger_record(str(ROOT / name), kind, ctx)
        self.assertEqual(ctx.errors, [])
        self.assertEqual(len(ctx.records), 13)

    def test_all_original_and_replacement_hash_bindings_are_valid(self):
        entries = ledger.load_schema_supersessions(str(ROOT / "tools/schema_supersession_registry.yaml"))
        ctx = ledger.Ctx(set(), schema_supersessions=entries)
        ledger.check_schema_supersessions(ctx, entries)
        self.assertEqual(ctx.errors, [])
        self.assertGreaterEqual(len(entries), self.report()["registry_after"])


if __name__ == "__main__":
    unittest.main()
