"""Tests for tools/tune_skill_batch.py against a small fixture ledger."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tune_skill_batch as tsb  # noqa: E402


def _write(root: Path, rel: str, doc: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


class FixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # Four ideas: structured chain to a strong EV; free-text-only EV hit;
        # mentioned only in a decision; and never picked up.
        for tok, claim in (("aaaaaa", "structured"), ("bbbbbb", "free text"),
                           ("cccccc", "mentioned"), ("dddddd", "derived only"),
                           ("eeeeee", "uncovered")):
            _write(self.root, f"ledger/proposals/IDEA-20260901-{tok}.yaml",
                   {"idea": {"id": f"IDEA-20260901-{tok}", "status": "proposed",
                             "added": "2026-09-01", "claim": claim}})
        _write(self.root, "ledger/hypotheses/H-FX-000001.yaml",
               {"hypothesis": {"id": "H-FX-000001", "status": "approved",
                               "source_idea_id": "IDEA-20260901-aaaaaa"}})
        _write(self.root, "experiments/EXP-FX-000001/specification.yaml",
               {"experiment": {"id": "EXP-FX-000001", "hypothesis_id": "H-FX-000001",
                               "status": "completed", "designed_at": "2026-09-02"}})
        _write(self.root, "experiments/EXP-FX-000002/specification.yaml",
               {"experiment": {"id": "EXP-FX-000002", "hypothesis_id": None,
                               "derived_from_idea": "IDEA-20260901-dddddd", "status": "draft"}})
        _write(self.root, "ledger/evidence/EV-FX-000001.yaml",
               {"evidence": {"id": "EV-FX-000001", "hypothesis_id": "H-FX-000001",
                             "experiment_ids": ["EXP-FX-000001"], "strength": "strong",
                             "direction": "weakens"}})
        _write(self.root, "ledger/evidence/EV-FX-000002.yaml",
               {"evidence": {"id": "EV-FX-000002", "hypothesis_id": "H-FX-999999",
                             "experiment_ids": [], "strength": "moderate", "direction": "supports",
                             "observations": "derived from IDEA-20260901-bbbbbb"}})
        _write(self.root, "ledger/decisions/DEC-20260903-000001.yaml",
               {"decision": {"id": "DEC-20260903-000001", "evidence_refs": ["EV-FX-000001"],
                             "rationale": "the claim overclaims; dominated_by was left null"}})
        _write(self.root, "ledger/decisions/DEC-20260903-000002.yaml",
               {"decision": {"id": "DEC-20260903-000002", "evidence_refs": [],
                             "rationale": "considered IDEA-20260901-cccccc and deprioritised it"}})
        (self.root / "ledger" / ".index").mkdir(parents=True)
        import build_ledger_index
        build_ledger_index.build(self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_propose_ideas_chain_statuses_and_rewards(self) -> None:
        batch = tsb.collect("propose-ideas", self.root, None, None)
        by_id = {r["id"]: r for r in batch["items"]}
        a = by_id["IDEA-20260901-aaaaaa"]
        self.assertEqual(a["status"], "terminal")
        self.assertEqual(a["match_method"], "structured")
        self.assertEqual(a["reward"], 2)
        self.assertEqual(a["chain"], {"H": ["H-FX-000001"], "EXP": ["EXP-FX-000001"],
                                      "EV": ["EV-FX-000001"], "DEC": ["DEC-20260903-000001"]})
        self.assertEqual(a["decision_flags"], [{"dec": "DEC-20260903-000001",
                                                "flags": ["overclaim", "dominated_by"]}])
        b = by_id["IDEA-20260901-bbbbbb"]
        self.assertEqual(b["status"], "terminal_unscored")
        self.assertEqual(b["match_method"], "free_text")
        self.assertTrue(b["needs_review"])
        self.assertIsNone(b["reward"])
        self.assertEqual(by_id["IDEA-20260901-cccccc"]["status"], "mentioned_only")
        # derived_from_idea alone (no hypothesis) still counts as picked up.
        self.assertEqual(by_id["IDEA-20260901-dddddd"]["status"], "in_flight")
        rs = batch["reward_summary"]
        self.assertEqual((rs["terminal_n"], rs["scored_n"], rs["unscored_n"]), (2, 1, 1))
        self.assertEqual(rs["unscored_values"], [{"value": "moderate", "n": 1}])
        self.assertEqual(rs["histogram"], {"plus2": 1, "plus1": 0, "zero": 0})
        self.assertEqual(rs["by_match_method"], {"structured": 1, "free_text": 1})
        self.assertTrue(batch["thin"])
        self.assertIn("1 scored terminal item(s) < 5", batch["thin_reasons"][0])

    def test_design_experiment_chain_and_window(self) -> None:
        batch = tsb.collect("design-experiment", self.root, None, None)
        by_id = {r["id"]: r for r in batch["items"]}
        self.assertEqual(by_id["EXP-FX-000001"]["status"], "terminal")
        self.assertEqual(by_id["EXP-FX-000001"]["reward"], 2)
        self.assertEqual(by_id["EXP-FX-000002"]["status"], "uncovered")
        # A lower bound excludes undated items; EXP-FX-000002 has no date.
        windowed = tsb.collect("design-experiment", self.root, "2026-09-02", None)
        self.assertEqual([r["id"] for r in windowed["items"]], ["EXP-FX-000001"])

    def test_direction_never_changes_the_reward(self) -> None:
        for direction in ("supports", "weakens", "contradicts", "neutral"):
            sc = tsb.score_evidence([{"id": "EV-x", "strength": "replicated", "direction": direction}])
            self.assertEqual(sc["reward"], 2)
        sc = tsb.score_evidence([{"id": "EV-x", "strength": "n/a", "direction": "supports"},
                                 {"id": "EV-y", "strength": None, "direction": None}])
        self.assertIsNone(sc["reward"])
        self.assertEqual(sc["unscored_values"], ["n/a", "null"])

    def test_round_record_is_written_with_caveats(self) -> None:
        out = self.root / "coordination" / "skill-tuning"
        rc = tsb.main(["propose-ideas", "--repo-root", str(self.root), "--write-round", str(out),
                       "--decision", "deferred", "--caveat", "fixture"])
        self.assertEqual(rc, 0)
        files = list((out / "propose-ideas").glob("round-*.yaml"))
        self.assertEqual(len(files), 1)
        rec = yaml.safe_load(files[0].read_text(encoding="utf-8"))["round"]
        self.assertEqual(rec["decision"], "deferred")
        self.assertEqual(rec["files_changed"], [])
        self.assertIn("fixture", rec["caveats"])
        self.assertTrue(any("thin-data" in c for c in rec["caveats"]))
        self.assertTrue(any("no session receipts" in c for c in rec["caveats"]))
        self.assertTrue(any("free text only" in c for c in rec["caveats"]))
        # Only terminal items are written in full; the recorded argv (batch
        # definition only, no prose) reproduces the rest.
        self.assertTrue(rec["batch_source"]["uncovered_ids_omitted"])
        self.assertEqual(rec["batch_source"]["argv"], ["propose-ideas", "--json"])
        self.assertEqual({i["id"] for i in rec["batch_items"]},
                         {"IDEA-20260901-aaaaaa", "IDEA-20260901-bbbbbb"})
        free = next(i for i in rec["batch_items"] if i["id"] == "IDEA-20260901-bbbbbb")
        self.assertTrue(free["needs_review"])
        self.assertEqual(free["strength"], ["moderate"])
        self.assertEqual(rec["reward_summary"]["uncovered_n"], 1)
        self.assertEqual(rec["reward_summary"]["in_flight_n"], 1)
        self.assertEqual(rec["reward_summary"]["mentioned_only_n"], 1)


if __name__ == "__main__":
    unittest.main()
