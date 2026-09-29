"""Schema checks for the obstruction block and citation provenance.

Both fields are optional-when-absent by construction: the validator baseline is
prune-only, so a newly-required field on immutable records could never be
grandfathered. These tests pin both halves of that contract -- absence is
silent, and a record that CLAIMS the new schema must complete it.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import obstruction_registry                      # noqa: E402
import validate_ledger                           # noqa: E402


def _ctx() -> validate_ledger.Ctx:
    return validate_ledger.Ctx(legacy_paths=set())


def _errors(body: dict, rec_type: str) -> list[str]:
    ctx = _ctx()
    validate_ledger.check_citations("r.yaml", body, rec_type, ctx)
    if rec_type in ("evidence", "coordinator_decision"):
        validate_ledger.check_obstruction("r.yaml", body, ctx)
    return ctx.errors


COMPLETE_OBSTRUCTION = {
    "statement": "summation-polynomial degree grows as 2^{n-1} in the index",
    "quantity": "degree of S_{n+1} in each variable",
    "value": "2^{n-1}, exact, n = 3..6",
    "scope": "F_{2^m} Semaev descent, m in [41, 163]",
    "measured_by": ["RUN-SEMAEV-004"],
    "resource_check": {
        "examined": True,
        "reading": "the growth bounds the object it grows in; a degree cap "
                   "turns the same count into a feasibility test",
        "spawned_ids": [],
    },
}


class ObstructionBlockTests(unittest.TestCase):
    def test_absent_block_is_silent(self) -> None:
        self.assertEqual(_errors({"id": "EV-X-000000"}, "evidence"), [])

    def test_complete_block_passes(self) -> None:
        body = {"id": "EV-X-000000", "obstruction": dict(COMPLETE_OBSTRUCTION)}
        self.assertEqual(_errors(body, "evidence"), [])

    def test_prose_only_obstruction_is_rejected(self) -> None:
        body = {"id": "EV-X-000000",
                "obstruction": {"statement": "descent did not work"}}
        errors = " ".join(_errors(body, "evidence"))
        for field in ("quantity", "value", "scope", "measured_by"):
            self.assertIn(field, errors)

    def test_measured_by_must_be_nonempty(self) -> None:
        block = dict(COMPLETE_OBSTRUCTION, measured_by=[])
        errors = _errors({"id": "EV-X-000000", "obstruction": block},
                         "evidence")
        self.assertTrue(any("measured_by" in e for e in errors))

    def test_missing_resource_check_is_rejected(self) -> None:
        block = {k: v for k, v in COMPLETE_OBSTRUCTION.items()
                 if k != "resource_check"}
        errors = _errors({"id": "EV-X-000000", "obstruction": block},
                         "evidence")
        self.assertTrue(any("resource_check" in e for e in errors))

    def test_unexamined_resource_check_is_rejected(self) -> None:
        block = dict(COMPLETE_OBSTRUCTION,
                     resource_check={"examined": False, "reading": None})
        errors = _errors({"id": "EV-X-000000", "obstruction": block},
                         "evidence")
        self.assertTrue(any("examined" in e for e in errors))

    def test_examined_with_no_resource_found_is_accepted(self) -> None:
        """'None found' is a complete answer, not a failure."""
        block = dict(COMPLETE_OBSTRUCTION, resource_check={
            "examined": True,
            "reading": "checked against the operator-theory and rigidity "
                       "lenses; neither takes this growth as a hypothesis",
            "spawned_ids": [],
        })
        self.assertEqual(
            _errors({"id": "EV-X-000000", "obstruction": block}, "evidence"),
            [])


class CitationProvenanceTests(unittest.TestCase):
    def test_entry_without_provenance_is_silent(self) -> None:
        body = {"id": "H-X-000000",
                "structural_ingredients": [{"citation": "arXiv:2306.04799"}]}
        self.assertEqual(_errors(body, "hypothesis"), [])

    def test_bad_provenance_value_is_rejected(self) -> None:
        body = {"id": "EV-X-000000",
                "citations": [{"ref": "x", "provenance": "remembered"}]}
        errors = _errors(body, "evidence")
        self.assertTrue(any("provenance" in e for e in errors))

    def test_retrieved_requires_verified_by(self) -> None:
        body = {"id": "EV-X-000000",
                "citations": [{"ref": "arXiv:2306.04799",
                               "provenance": "retrieved"}]}
        errors = _errors(body, "evidence")
        self.assertTrue(any("verified_by" in e for e in errors))

    def test_retrieved_with_verified_by_passes(self) -> None:
        body = {"id": "EV-X-000000",
                "citations": [{"ref": "arXiv:2306.04799",
                               "provenance": "retrieved",
                               "verified_by": "TASK-20260814-abc123"}]}
        self.assertEqual(_errors(body, "evidence"), [])

    def test_recalled_needs_no_verified_by(self) -> None:
        body = {"id": "EV-X-000000",
                "citations": [{"ref": "Montgomery 1973",
                               "provenance": "recalled"}]}
        self.assertEqual(_errors(body, "evidence"), [])

    def test_recalled_may_not_back_a_decision(self) -> None:
        body = {"id": "DEC-20260814-000000",
                "citations": [{"ref": "Montgomery 1973",
                               "provenance": "recalled"}]}
        errors = _errors(body, "coordinator_decision")
        self.assertTrue(any("may not back a decision" in e for e in errors))

    def test_recalled_may_not_support_a_literature_novelty_claim(self) -> None:
        for status in ("known", "adaptation"):
            with self.subTest(status=status):
                body = {"id": "IDEA-20260814-000000",
                        "novelty_status": status,
                        "citations": [{"ref": "Semaev 2004",
                                       "provenance": "recalled"}]}
                errors = _errors(body, "idea")
                self.assertTrue(any("unverified" in e for e in errors))

    def test_recalled_is_fine_on_an_unverified_idea(self) -> None:
        body = {"id": "IDEA-20260814-000000",
                "novelty_status": "unverified",
                "citations": [{"ref": "Semaev 2004",
                               "provenance": "recalled"}]}
        self.assertEqual(_errors(body, "idea"), [])


class RegistryTests(unittest.TestCase):
    """The registry derives state; it must read both ledger layouts."""

    def test_committed_corpus_scan_runs(self) -> None:
        self.assertIsInstance(obstruction_registry.collect(), list)

    def test_debt_scan_finds_the_pre_schema_backlog(self) -> None:
        debt = obstruction_registry.collect_debt()
        self.assertTrue(debt, "expected negative records predating the block")
        self.assertTrue(all(e["direction"] in ("weakens", "contradicts")
                            for e in debt))

    def test_debt_reads_both_ledger_layouts(self) -> None:
        """Top-level records are frozen legacy; subdirectories are live."""
        paths = [e["path"] for e in obstruction_registry.collect_debt()]
        self.assertTrue(any(p.startswith("ledger/evidence/") for p in paths))
        self.assertTrue(any(p.count("/") == 1 for p in paths))

    def test_resource_state_classification(self) -> None:
        cases = [
            ({}, "open"),
            ({"resource_check": {"examined": False}}, "open"),
            ({"resource_check": {"examined": True, "reading": ""}}, "open"),
            ({"resource_check": {"examined": True, "reading": "r"}}, "checked"),
            ({"resource_check": {"examined": True, "reading": "r",
                                 "spawned_ids": ["H-X-000000"]}}, "spawned"),
        ]
        for block, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(
                    obstruction_registry._resource_state(block), expected)

    def test_registry_picks_up_a_complete_block(self) -> None:
        """A written block is discoverable by the rerank pass."""
        with tempfile.TemporaryDirectory() as tmp:
            evidence = os.path.join(tmp, "ledger", "evidence")
            os.makedirs(evidence)
            record = {"evidence": {"id": "EV-TMP-000000",
                                   "direction": "weakens",
                                   "obstruction": dict(COMPLETE_OBSTRUCTION)}}
            with open(os.path.join(evidence, "EV-TMP-000000.yaml"), "w",
                      encoding="utf-8") as handle:
                yaml.safe_dump(record, handle)
            original = obstruction_registry.REPO
            try:
                obstruction_registry.REPO = tmp
                entries = obstruction_registry.collect()
            finally:
                obstruction_registry.REPO = original
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["record_id"], "EV-TMP-000000")
        self.assertEqual(entries[0]["resource_state"], "checked")


if __name__ == "__main__":
    unittest.main()
