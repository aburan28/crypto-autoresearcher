#!/usr/bin/env python3
"""Safety tests for hash-pinned non-run schema supersession."""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ledger as vl


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SchemaSupersessionFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="schema-supersession-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.original = self.tmp / "ledger" / "evidence" / "EV-TST-abcdef.yaml"
        self.original.parent.mkdir(parents=True)
        self.original.write_text(
            yaml.safe_dump({"evidence": {"id": "EV-TST-abcdef"}},
                           sort_keys=False), encoding="utf-8")
        self.replacement = (self.tmp / "ledger" / "corrections" /
                            "schema-supersessions" / "EV-TST-abcdef.v2.yaml")
        self.replacement.parent.mkdir(parents=True)
        self.replacement.write_text(yaml.safe_dump({"evidence": {
            "id": "EV-TST-abcdef",
            "hypothesis_id": None,
            "hypothesis_id_note": "Instrument-only evidence.",
            "run_ids": [],
            "direction": "neutral",
            "strength": "inconclusive",
            "claim_tier": "toy",
            "proof_status": "not_applicable",
            "proof_refs": [],
        }}, sort_keys=False), encoding="utf-8")

    def entries(self, **over) -> dict[str, dict]:
        entry = {
            "kind": "ledger",
            "superseded_path": str(self.original),
            "superseded_sha256": digest(self.original),
            "superseding_path": str(self.replacement),
            "superseding_sha256": digest(self.replacement),
            "replacement_id": None,
        }
        entry.update(over)
        return {os.path.abspath(self.original): entry}

    def test_registered_record_is_validated_from_complete_replacement(self) -> None:
        entries = self.entries()
        ctx = vl.Ctx(set(), schema_supersessions=entries)
        vl.check_schema_supersessions(ctx, entries)
        vl.check_ledger_record(str(self.original), "evidence", ctx)
        self.assertEqual(ctx.errors, [])
        self.assertEqual(ctx.ids["EV-TST-abcdef"], str(self.original))

    def test_unregistered_record_keeps_original_errors(self) -> None:
        ctx = vl.Ctx(set())
        vl.check_ledger_record(str(self.original), "evidence", ctx)
        self.assertTrue(any("missing required field" in e for e in ctx.errors))

    def test_replacement_defect_is_not_suppressed(self) -> None:
        body = yaml.safe_load(self.replacement.read_text())
        body["evidence"].pop("proof_status")
        self.replacement.write_text(yaml.safe_dump(body, sort_keys=False))
        entries = self.entries()
        ctx = vl.Ctx(set(), schema_supersessions=entries)
        vl.check_ledger_record(str(self.original), "evidence", ctx)
        self.assertTrue(any("missing required field 'proof_status'" in e
                            for e in ctx.errors), ctx.errors)

    def test_hash_drift_is_always_an_error(self) -> None:
        entries = self.entries(superseding_sha256="0" * 64)
        ctx = vl.Ctx({os.path.abspath(self.replacement)},
                     schema_supersessions=entries)
        vl.check_schema_supersessions(ctx, entries)
        self.assertTrue(ctx.errors)
        self.assertEqual(ctx.legacy_warnings, [])


def registry_document(**over) -> dict:
    record = {
        "kind": "ledger",
        "superseded_path": "ledger/evidence/EV-TST-abcdef.yaml",
        "superseded_sha256": "a" * 64,
        "superseding_path": (
            "ledger/corrections/schema-supersessions/EV-TST-abcdef.v2.yaml"),
        "superseding_sha256": "b" * 64,
        "defect": "missing proof metadata",
        "registered": "2026-08-08",
    }
    record.update(over)
    return {"schema": vl.SCHEMA_SUPERSESSION_SCHEMA, "records": [record]}


class SchemaRegistryLoaderTests(unittest.TestCase):
    def load(self, document) -> dict[str, dict]:
        tmp = Path(tempfile.mkdtemp(prefix="schema-registry-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        path = tmp / "registry.yaml"
        path.write_text(yaml.safe_dump(document, sort_keys=False))
        return vl.load_schema_supersessions(str(path))

    def test_valid_registry_is_keyed_by_original_absolute_path(self) -> None:
        entries = self.load(registry_document())
        expected = os.path.abspath(os.path.join(
            vl.REPO, "ledger/evidence/EV-TST-abcdef.yaml"))
        self.assertEqual(list(entries), [expected])

    def test_wrong_kind_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.load(registry_document(kind="knowledge"))

    def test_replacement_must_be_outside_discovery_globs(self) -> None:
        with self.assertRaises(ValueError):
            self.load(registry_document(
                superseding_path="ledger/evidence/EV-TST-fedcba.yaml"))

    def test_escaping_path_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.load(registry_document(
                superseding_path="ledger/corrections/../../etc/passwd"))

    def test_duplicate_source_is_refused(self) -> None:
        document = registry_document()
        document["records"].append(dict(document["records"][0]))
        with self.assertRaises(ValueError):
            self.load(document)

    def test_redirect_must_target_same_discovered_kind(self) -> None:
        with self.assertRaises(ValueError):
            self.load(registry_document(
                superseding_path="experiments/EXP-TST-abcdef/specification.yaml",
                redirect_id="EXP-TST-abcdef"))

    def test_redirect_and_replacement_id_are_mutually_exclusive(self) -> None:
        with self.assertRaises(ValueError):
            self.load(registry_document(
                superseding_path="ledger/evidence/EV-TST-fedcba.yaml",
                redirect_id="EV-TST-fedcba",
                replacement_id="EV-TST-abcdef"))


if __name__ == "__main__":
    unittest.main()
