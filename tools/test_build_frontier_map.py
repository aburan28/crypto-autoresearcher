#!/usr/bin/env python3
"""Tests for the ECDLP known-results map and the idea `prior_art` gate.

Counts are FLOORS read per area (CLAUDE.md): the map grows, and an exact
count would fail on every branch that adds a row.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_frontier_map as bfm  # noqa: E402
import validate_ledger as vl  # noqa: E402

FLOOR_PER_AREA = 20


class MapTests(unittest.TestCase):
    def test_committed_rows_pass_the_check(self) -> None:
        self.assertEqual(bfm.check_rows(bfm.load_rows()), [])

    def test_every_area_is_populated(self) -> None:
        rows = bfm.load_rows()
        for area in bfm.AREAS:
            with self.subTest(area):
                self.assertGreaterEqual(
                    sum(r.get("area") == area for r in rows), FLOOR_PER_AREA)

    def test_render_lists_every_live_row(self) -> None:
        rows = bfm.load_rows()
        text = bfm.render(rows)
        for r in rows:
            if not r.get("superseded_by"):
                self.assertIn(r["id"], text)

    def test_match_finds_the_known_rederivation(self) -> None:
        """IDEA-20260915-8fe0ef re-derived GGMP; the map must catch it."""
        hits = bfm.match(bfm.load_rows(),
                         "Frobenius-stable factor base for Koblitz curves")
        self.assertTrue(hits)
        self.assertIn("subfield", hits[0][1]["title"].lower())

    def test_check_rejects_ungrounded_and_malformed_rows(self) -> None:
        bad = {"_path": "x/index-calculus/KR-IC-000000.yaml",
               "_area_dir": "index-calculus", "id": "KR-RHO-000000",
               "area": "index-calculus", "kind": "nonsense", "title": "t",
               "claim": "c", "status": "proven", "added": "2026-09-26",
               "superseded_by": None, "forecloses": [],
               "sources": [{"ref": "KN-LIT-001", "locator": "abstract",
                            "verification_state": "recalled_unverified"}]}
        errors = " ".join(bfm.check_rows([bad]))
        for fragment in ("does not match directory", "kind 'nonsense'",
                         "recalled_unverified", "forecloses", "filename stem"):
            self.assertIn(fragment, errors)


class _Ctx:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def err(self, path: str, msg: str, **_: object) -> None:
        self.errors.append(msg)


class PriorArtGateTests(unittest.TestCase):
    ROW = sorted(bfm.row_ids())[0]

    def _run(self, body: dict) -> list[str]:
        ctx = _Ctx()
        vl.check_prior_art("p.yaml", body, ctx)  # type: ignore[arg-type]
        return ctx.errors

    def test_pre_cutover_idea_without_block_is_untouched(self) -> None:
        self.assertEqual(self._run({"id": "IDEA-20260901-abcdef",
                                    "novelty_status": "screened"}), [])

    def test_post_cutover_idea_requires_block(self) -> None:
        errors = self._run({"id": "IDEA-20261002-abcdef",
                            "novelty_status": "unverified"})
        self.assertTrue(any("prior_art is required" in e for e in errors))

    def test_post_cutover_idea_rejects_nonstandard_novelty(self) -> None:
        errors = self._run({"id": "IDEA-20261002-abcdef",
                            "novelty_status": "screened"})
        self.assertTrue(any("novelty_status" in e for e in errors))

    def test_complete_block_passes(self) -> None:
        body = {"id": "IDEA-20261002-abcdef", "novelty_status": "known",
                "prior_art": {
                    "frontier_map": "knowledge/frontiers/ecdlp",
                    "rows_checked": [self.ROW],
                    "nearest": [{"ref": self.ROW, "provenance": "kb",
                                 "relation": "same", "delta": "none"}]}}
        self.assertEqual(self._run(body), [])

    def test_known_needs_a_grounded_same_relation(self) -> None:
        body = {"id": "IDEA-20261002-abcdef", "novelty_status": "known",
                "prior_art": {
                    "frontier_map": "knowledge/frontiers/ecdlp",
                    "rows_checked": [self.ROW],
                    "nearest": [{"ref": self.ROW, "provenance": "recalled",
                                 "relation": "same", "delta": "none"}]}}
        self.assertTrue(any("requires a prior_art.nearest" in e
                            for e in self._run(body)))

    def test_unknown_rows_are_rejected(self) -> None:
        body = {"id": "IDEA-20261002-abcdef", "novelty_status": "unverified",
                "prior_art": {"frontier_map": "knowledge/frontiers/ecdlp",
                              "rows_checked": ["KR-IC-ffffff"],
                              "none_found_after": ["grep"]}}
        self.assertTrue(any("not a known-result row" in e
                            for e in self._run(body)))


if __name__ == "__main__":
    unittest.main()
