#!/usr/bin/env python3
"""Tests for the ECDLP lead atlas (knowledge/leads/ecdlp/, tools/lead_atlas.py).

Counts are floors: the atlas grows, and an exact count would fail on every
branch that adds a lead.
"""
from __future__ import annotations

import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lead_atlas as la  # noqa: E402
import validate_ledger as vl  # noqa: E402

FLOOR_PER_FAMILY = 3


class AtlasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = la.load_leads()

    def test_committed_rows_pass_the_check(self) -> None:
        errors, _warnings = la.check_leads(self.rows)
        self.assertEqual(errors, [])

    def test_every_family_is_populated(self) -> None:
        for fam in la.FAMILIES:
            with self.subTest(fam):
                self.assertGreaterEqual(
                    sum(r.get("family") == fam for r in self.rows),
                    FLOOR_PER_FAMILY)

    def test_closure_without_obstruction_fails(self) -> None:
        row = copy.deepcopy(next(r for r in self.rows
                                 if r["disposition"] in la.CLOSED))
        row.pop("obstruction")
        errors, _ = la.check_leads([row])
        self.assertTrue(any("requires an obstruction" in e for e in errors))

    def test_open_lead_without_next_step_fails(self) -> None:
        row = copy.deepcopy(next(r for r in self.rows
                                 if r["disposition"] in la.OPEN))
        row.pop("next_action", None)
        errors, _ = la.check_leads([row])
        self.assertTrue(any("next_action.step" in e for e in errors))

    def test_unknown_ledger_ref_fails(self) -> None:
        row = copy.deepcopy(self.rows[0])
        row["ledger_refs"] = ["H-NOPE-000000"]
        errors, _ = la.check_leads([row])
        self.assertTrue(any("H-NOPE-000000" in e for e in errors))

    def test_coverage_has_no_dangling_lead(self) -> None:
        self.assertEqual(la.coverage_report(self.rows)["dangling"], [])

    def test_match_finds_the_frobenius_factor_base_lead(self) -> None:
        """The GGMP re-derivation (DEC-20260916-3c0cf5) must hit a lead."""
        hits = la.match("Frobenius-invariant factor base for Koblitz subfield "
                        "curve index calculus")
        self.assertTrue(hits)
        self.assertTrue(any(h[1].startswith("LEAD-ICB-") for h in hits[:3]),
                        hits[:3])

    def test_brief_never_raises(self) -> None:
        self.assertIn("lead atlas", la.brief())

    def test_render_lists_every_lead(self) -> None:
        text = la.render(self.rows)
        for r in self.rows:
            self.assertIn(r["id"], text)


class PriorArtLeadTests(unittest.TestCase):
    def _errors(self, rec_id: str, block: dict) -> list[str]:
        ctx = vl.Ctx(set())
        body = {"id": rec_id, "novelty_status": "unverified",
                "prior_art": block}
        vl.check_prior_art("x.yaml", body, ctx)
        return ctx.errors

    def _block(self, **extra) -> dict:
        return {"frontier_map": "knowledge/frontiers/ecdlp",
                "rows_checked": [sorted(vl._frontier_row_ids())[0]],
                "none_found_after": ["q"], **extra}

    def test_lead_required_after_cutover(self) -> None:
        errs = self._errors(f"IDEA-{vl.LEAD_CUTOVER}-abc123", self._block())
        self.assertTrue(any("prior_art.lead is required" in e for e in errs))

    def test_lead_optional_before_cutover(self) -> None:
        errs = self._errors("IDEA-20261010-abc123", self._block())
        self.assertFalse(any("prior_art.lead" in e for e in errs))

    def test_known_lead_and_new_lead_pass(self) -> None:
        lead = la.load_leads()[0]["id"]
        rid = f"IDEA-{vl.LEAD_CUTOVER}-abc123"
        self.assertFalse(any("prior_art.lead" in e for e in
                             self._errors(rid, self._block(lead=lead))))
        self.assertFalse(any("prior_art.lead" in e for e in self._errors(
            rid, self._block(lead="new", new_lead_reason="no lead covers it"))))
        self.assertTrue(any("new_lead_reason" in e for e in
                            self._errors(rid, self._block(lead="new"))))
        self.assertTrue(any("is not a lead" in e for e in self._errors(
            rid, self._block(lead="LEAD-ICB-does-not-exist"))))


class RecordAreaTests(unittest.TestCase):
    """ecdlp_records() must see records the id prefix or line regex miss."""

    def _area(self, fn, text: str, suffix: str = ".yaml") -> str | None:
        with tempfile.NamedTemporaryFile("w", suffix=suffix,
                                         delete=False) as fh:
            fh.write(text)
        try:
            return fn(fh.name)
        finally:
            os.unlink(fh.name)

    def test_one_line_json_idea(self) -> None:
        text = ('{"idea":{"id":"IDEA-20261030-a62c58",'
                '"question_id":"RQ-PFDR-ae2fba","status":"proposed"}}')
        self.assertEqual(self._area(la._idea_area, text), "PFDR")

    def test_yaml_idea_still_uses_the_line_form(self) -> None:
        text = "idea:\n  id: IDEA-x\n  question_id: RQ-ECDLP-002\n"
        self.assertEqual(self._area(la._idea_area, text), "ECDLP")

    def test_hypothesis_area_from_its_question(self) -> None:
        text = ("hypothesis:\n  id: H-SEMAEV-94dab2\n"
                "  question_id: RQ-ECDLP-002\n")
        self.assertEqual(self._area(la._record_area, text), "ECDLP")

    def test_prefix_outside_areas_is_classified_by_question(self) -> None:
        recs = la.ecdlp_records()
        for rid in ("H-SEMAEV-94dab2", "H-PFIVE-6510c2",
                    "IDEA-20261030-a62c58"):
            with self.subTest(rid):
                self.assertIn(rid, recs)


if __name__ == "__main__":
    unittest.main()
