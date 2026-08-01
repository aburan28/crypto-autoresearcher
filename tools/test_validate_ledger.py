#!/usr/bin/env python3
"""Integration tests for legacy-ledger and knowledge validation coverage."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
INVENTORY = REPO / "tools" / "legacy_ledger_inventory.yaml"
RUN_INVENTORY = REPO / "tools" / "legacy_run_inventory.yaml"


class LedgerCoverageTests(unittest.TestCase):
    def test_legacy_inventory_covers_and_freezes_every_root_record(self) -> None:
        document = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(document["schema"], "legacy-ledger-inventory-v1")
        expected = document["records"]
        observed = {
            path.relative_to(REPO).as_posix()
            for pattern in ("RQ-*.yaml", "H-*.yaml", "EV-*.yaml", "DEC-*.yaml")
            for path in (REPO / "ledger").glob(pattern)
        }
        self.assertEqual(set(expected), observed)
        for relative, digest in expected.items():
            actual = hashlib.sha256((REPO / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, relative)

    def test_repository_validator_indexes_legacy_and_knowledge_records(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO / "tools" / "validate_ledger.py")],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("frozen root-level ledger records were indexed", result.stdout)
        self.assertIn("no new violations", result.stdout)

    def test_legacy_run_inventory_freezes_imported_manifests(self) -> None:
        document = yaml.safe_load(RUN_INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(document["schema"], "legacy-run-inventory-v1")
        self.assertTrue(document["records"])
        for relative, digest in document["records"].items():
            path = REPO / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             digest, relative)

    def test_legacy_id_remaps_resolve_to_canonical_records(self) -> None:
        document = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        for source, target_id in document.get("remapped_ids", {}).items():
            self.assertIn(source, document["records"])
            target = REPO / "ledger" / "decisions" / f"{target_id}.yaml"
            self.assertTrue(target.is_file(), target_id)
            body = yaml.safe_load(target.read_text(encoding="utf-8"))
            self.assertEqual(body["coordinator_decision"]["id"], target_id)


if __name__ == "__main__":
    unittest.main()
