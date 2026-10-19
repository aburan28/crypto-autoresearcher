"""validate_ledger indexes every run, experiment and amendment that exists.

Sheriff case SHF-20261016-3caa6f finding M2: records citing runs whose
manifest is flat (no `run:` envelope) or JSON-only, experiments whose
specification has the wrong shape, and protocol amendments, were reported as
citing an *unknown* record. The cited artifact exists; its own schema defect is
reported once, against itself. These tests pin both halves: the defect still
fails, and the citation resolves.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import validate_ledger                           # noqa: E402


def _ctx() -> validate_ledger.Ctx:
    return validate_ledger.Ctx(legacy_paths=set())


class _Tree(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        patcher = mock.patch.object(validate_ledger, "REPO", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)

    def write(self, rel: str, text: str) -> str:
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path


class FlatRunManifestTests(_Tree):
    RUN = "experiments/EXP-QSP-70b731/runs/RUN-QSP-327529/manifest.yaml"

    def test_flat_manifest_is_reported_once_and_indexed(self) -> None:
        path = self.write(self.RUN, yaml.safe_dump(
            {"experiment_id": "EXP-QSP-70b731", "run_id": "RUN-QSP-327529"}))
        ctx = _ctx()
        validate_ledger.check_run(path, ctx)
        self.assertEqual(len(ctx.errors), 1)
        self.assertIn("expected top-level key 'run'", ctx.errors[0])
        self.assertIn("RUN-QSP-327529", ctx.legacy_aliases)

    def test_flat_manifest_without_run_id_uses_directory(self) -> None:
        path = self.write(self.RUN, yaml.safe_dump(
            {"experiment_id": "EXP-QSP-70b731", "stage": 0}))
        ctx = _ctx()
        validate_ledger.check_run(path, ctx)
        self.assertIn("RUN-QSP-327529", ctx.legacy_aliases)

    def test_contradicting_run_id_is_not_indexed(self) -> None:
        path = self.write(self.RUN, yaml.safe_dump(
            {"experiment_id": "EXP-QSP-70b731", "run_id": "RUN-QSP-000000"}))
        ctx = _ctx()
        validate_ledger.check_run(path, ctx)
        self.assertEqual(ctx.legacy_aliases, set())

    def test_contradicting_experiment_is_not_indexed(self) -> None:
        path = self.write(self.RUN, yaml.safe_dump(
            {"experiment_id": "EXP-QSP-111111"}))
        ctx = _ctx()
        validate_ledger.check_run(path, ctx)
        self.assertEqual(ctx.legacy_aliases, set())

    def test_evidence_citing_flat_run_resolves(self) -> None:
        path = self.write(self.RUN, yaml.safe_dump(
            {"experiment_id": "EXP-QSP-70b731", "run_id": "RUN-QSP-327529"}))
        ctx = _ctx()
        validate_ledger.check_run(path, ctx)
        ctx.register("EV-QSP-abcdef", "ev.yaml",
                     {"id": "EV-QSP-abcdef", "run_ids": ["RUN-QSP-327529",
                                                         "RUN-QSP-999999"]},
                     "evidence")
        validate_ledger.check_cross_refs(ctx)
        unknown = [e for e in ctx.errors if "unknown run" in e]
        self.assertEqual(len(unknown), 1)
        self.assertIn("RUN-QSP-999999", unknown[0])


class JsonOnlyRunTests(_Tree):
    def test_json_only_run_is_advised_and_indexed(self) -> None:
        self.write("experiments/EXP-ECDLP-f49f75/runs/RUN-ECDLP-f49f75-01/"
                   "manifest.json",
                   json.dumps({"run_id": "RUN-ECDLP-f49f75-01",
                               "experiment_id": "EXP-ECDLP-f49f75"}))
        ctx = _ctx()
        validate_ledger.check_json_only_runs(ctx)
        self.assertEqual(ctx.errors, [])
        self.assertEqual(len(ctx.advisories), 1)
        self.assertIn("json-only run", ctx.advisories[0])
        self.assertIn("RUN-ECDLP-f49f75-01", ctx.legacy_aliases)

    def test_json_beside_yaml_manifest_is_not_scanned(self) -> None:
        run = "experiments/EXP-ECDLP-f49f75/runs/RUN-ECDLP-f49f75-01/"
        self.write(run + "manifest.json", "{}")
        self.write(run + "manifest.yaml", "run: {}\n")
        ctx = _ctx()
        validate_ledger.check_json_only_runs(ctx)
        self.assertEqual(ctx.advisories, [])

    def test_legacy_json_manifest_is_left_to_the_inventory(self) -> None:
        path = self.write("experiments/EXP-ECDLP-f49f75/runs/RUN-ECDLP-f49f75-01/"
                          "manifest.json", json.dumps({"run_id": "x"}))
        ctx = validate_ledger.Ctx(legacy_paths={os.path.abspath(path)})
        validate_ledger.check_json_only_runs(ctx)
        self.assertEqual(ctx.advisories, [])
        self.assertEqual(ctx.legacy_aliases, set())


class MalformedSpecificationTests(_Tree):
    def test_wrong_shape_spec_is_reported_once_and_indexed(self) -> None:
        path = self.write("experiments/EXP-AUXIN-339fb0/specification.yaml",
                          yaml.safe_dump({"successor_contract": {"fresh": {}}}))
        ctx = _ctx()
        validate_ledger.check_experiment(path, ctx)
        self.assertEqual(len(ctx.errors), 1)
        self.assertIn("expected top-level key 'experiment'", ctx.errors[0])
        self.assertIn("EXP-AUXIN-339fb0", ctx.legacy_aliases)


class AmendmentAndFindingTests(_Tree):
    AMD = "AMD-EXP-BINSTD-8bdf86-20261003-ell89"

    def _finding(self, refs: list[str]) -> None:
        self.write("knowledge/findings/KN-FIND-00dada.md",
                   "---\n" + yaml.safe_dump({
                       "id": "KN-FIND-00dada", "type": "internal_finding",
                       "title": "t", "tags": ["x"], "confidence": "low",
                       "added": "2026-10-16", "internal_refs": refs,
                       "proof_status": "empirical_only", "proof_refs": [],
                   }) + "---\nbody\n")

    def test_amendment_is_indexed_and_resolves_from_a_finding(self) -> None:
        self.write(f"experiments/EXP-BINSTD-8bdf86/amendments/{self.AMD}.yaml",
                   yaml.safe_dump({"amendment": {
                       "id": self.AMD, "experiment_id": "EXP-BINSTD-8bdf86"}}))
        self._finding([self.AMD, "TASK-20261003-6e0c8a"])
        ctx = _ctx()
        validate_ledger.check_amendments(ctx)
        self.assertEqual(ctx.amendment_ids, {self.AMD})
        validate_ledger.check_knowledge_entries(ctx)
        unknown = [e for e in ctx.errors if "unknown record" in e]
        self.assertEqual(len(unknown), 1)
        self.assertIn("TASK-20261003-6e0c8a", unknown[0])

    def test_amendment_whose_id_disagrees_with_its_file_is_not_indexed(self) -> None:
        self.write(f"experiments/EXP-BINSTD-8bdf86/amendments/{self.AMD}.yaml",
                   yaml.safe_dump({"amendment": {"id": "AMD-other"}}))
        ctx = _ctx()
        validate_ledger.check_amendments(ctx)
        self.assertEqual(ctx.amendment_ids, set())

    def test_finding_may_cite_an_indexed_unschematized_run(self) -> None:
        self._finding(["RUN-BINSTD-2b5b2c"])
        ctx = _ctx()
        ctx.legacy_aliases.add("RUN-BINSTD-2b5b2c")
        validate_ledger.check_knowledge_entries(ctx)
        self.assertEqual([e for e in ctx.errors if "unknown record" in e], [])


if __name__ == "__main__":
    unittest.main()
