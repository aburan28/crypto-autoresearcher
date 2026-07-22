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


if __name__ == "__main__":
    unittest.main()
