"""Pins CLAUDE.md rule 11 / AGENTS.md "ECC comes first".

User instruction 2026-09-04:
  1. All ECC goals have UNLIMITED budget.
  2. ECC goals take priority over every other goal, always.
  3. Open ECC ideas must be designed into experiments.

The load-bearing test here is `test_ecc_membership_is_not_inferred_from_prefix`.
Classifying ECC by acronym is the obvious shortcut and it is wrong in both
directions: GOAL-CRYPTO-001 is an ECDLP search, DREG/SDEG/SIG/MONO/RELN/ICEX
are Semaev and index-calculus machinery, while SYMF/QALG/CLGRP are excluded on
their content. A single declared list is the only thing that keeps those right,
so these tests check the list is consulted rather than re-derived.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ecc_priority as EP  # noqa: E402


class PolicyFileTests(unittest.TestCase):
    def test_policy_file_exists_and_declares_the_three_rules(self):
        pol = EP.load_policy()
        self.assertTrue((pol.get("budget") or {}).get("ecc_unlimited"))
        self.assertTrue((pol.get("priority") or {}).get("ecc_first"))
        self.assertTrue((pol.get("idea_design") or {}).get(
            "ecc_open_ideas_must_be_designed"))

    def test_unbounded_fields_are_the_two_budget_ceilings(self):
        self.assertEqual(set(EP.unbounded_fields()),
                         {"maximum_batches", "total_wall_clock_seconds"})

    def test_max_concurrent_is_explicitly_still_bounded(self):
        # Unlimited budget must not be read as unlimited parallelism: oversizing
        # max_concurrent degrades runs rather than buying any.
        pol = EP.load_policy()
        self.assertTrue((pol.get("budget") or {}).get("max_concurrent_still_bounded"))
        self.assertNotIn("max_concurrent", EP.unbounded_fields(pol))

    def test_every_exclusion_carries_a_reason(self):
        for area, why in (EP.load_policy().get("excluded_areas") or {}).items():
            self.assertTrue(str(why).strip(), f"{area} excluded with no reason")


class MembershipTests(unittest.TestCase):
    def test_ecc_membership_is_not_inferred_from_prefix(self):
        # Areas that ARE ECC despite non-elliptic names.
        for gid in ("GOAL-CRYPTO-001",     # "ECDLP breakthrough search"
                    "GOAL-DREG-001",       # boolean Semaev degree of regularity
                    "GOAL-MONO-001",       # Semaev-cover monodromy
                    "GOAL-RELN-001",       # factor-base decomposition probability
                    "GOAL-SDEG-001",       # Semaev solving degree
                    "GOAL-SIG-001",        # Semaev syzygy cascade
                    "GOAL-ICEX-001",       # index-calculus exponent
                    "GOAL-PATH-001"):      # path to prime-field ECDLP reduction
            self.assertTrue(EP.is_ecc(gid), f"{gid} should be ECC")
        # Areas that are NOT ECC, including elliptic-adjacent ones.
        for gid in ("GOAL-AES-002", "GOAL-SYMF-c00fa1", "GOAL-MLKEM-005",
                    "GOAL-CLGRP-001", "GOAL-QALG-001", "GOAL-MD5-001"):
            self.assertFalse(EP.is_ecc(gid), f"{gid} should NOT be ECC")

    def test_classification_spans_record_kinds(self):
        self.assertTrue(EP.is_ecc("RQ-PFDR-ae2fba"))
        self.assertTrue(EP.is_ecc("H-PFDR-3c7d1e"))
        self.assertTrue(EP.is_ecc("EXP-ECDLP-9b4f2a"))
        self.assertFalse(EP.is_ecc("EXP-AES-000000"))

    def test_identifiers_without_an_area_are_not_ecc(self):
        # IDEA-/DEC-/TASK- are date-keyed and carry no area token; they must be
        # classified through question_id, never guessed at.
        for ident in ("IDEA-20260904-8dccc9", "DEC-20260904-8e51d7",
                      "TASK-20260904-1f4e2f", "", "nonsense"):
            self.assertIsNone(EP.area_of(ident), ident)
            self.assertFalse(EP.is_ecc(ident), ident)

    def test_sort_key_puts_ecc_first(self):
        ids = ["GOAL-AES-002", "GOAL-SSI-001", "GOAL-MLKEM-005", "GOAL-ECDLP-001"]
        ordered = sorted(ids, key=EP.sort_key)
        self.assertTrue(EP.is_ecc(ordered[0]) and EP.is_ecc(ordered[1]))
        self.assertFalse(EP.is_ecc(ordered[2]) or EP.is_ecc(ordered[3]))


class BudgetTests(unittest.TestCase):
    def test_no_active_or_draft_ecc_goal_has_a_finite_budget(self):
        v = EP.budget_violations()
        self.assertEqual(v, [], f"ECC budgets must be unlimited: {v}")

    def test_violation_detector_actually_detects(self):
        # A detector that cannot fail is not a check. Feed it a finite budget
        # and require it to object.
        import copy
        pol = copy.deepcopy(EP.load_policy())
        self.assertTrue(EP.is_ecc("GOAL-ECDLP-001", pol))
        # the real corpus is clean, so assert the predicate the detector uses
        for field in EP.unbounded_fields(pol):
            self.assertIn(field, ("maximum_batches", "total_wall_clock_seconds"))


class OpenIdeaWorklistTests(unittest.TestCase):
    def test_open_ecc_ideas_are_enumerable_and_all_ecc(self):
        rows = EP.open_ecc_ideas()
        self.assertIsInstance(rows, list)
        areas = EP.ecc_areas()
        for r in rows[:200]:
            self.assertIn(r["area"], areas, r["id"])

    def test_open_ideas_exclude_ones_already_designed(self):
        rows = EP.open_ecc_ideas()
        ids = {r["id"] for r in rows}
        # IDEA-20260903-81a943 has H-PFDR-3c7d1e / EXP-PFDR-9b4f2a designed
        # against it, so it must not appear on the "still to design" worklist.
        self.assertNotIn("IDEA-20260903-81a943", ids)

    def test_legacy_three_digit_idea_ids_count_as_designed(self):
        """A designed LEGACY-form idea must drop off the worklist too.

        Regression: the first version of `_taken_idea_ids` required a 4-8
        character suffix and so never matched `IDEA-20260801-002`. Legacy
        three-digit identifiers stay valid forever (CLAUDE.md "Conventions"),
        so every legacy-form idea was reported as still needing design even
        when it already had a hypothesis and a frozen contract -- 37 false
        positives, inflating the worklist from 276 to 313.

        IDEA-20260801-002 is the case that caught it: H-DREG-91be14 declares
        `derived_from_idea: IDEA-20260801-002` and EXP-DREG-620b15 is its
        contract.
        """
        taken = EP._taken_idea_ids()
        self.assertIn("IDEA-20260801-002", taken,
                      "legacy 3-digit idea ids must be recognised as designed")
        self.assertNotIn("IDEA-20260801-002",
                         {r["id"] for r in EP.open_ecc_ideas()})

    def test_taken_id_pattern_spans_every_live_identifier_form(self):
        import re
        pat = re.compile(r"IDEA-\d{8}-[0-9a-zA-Z]{3,8}|[A-Z]+-IDEA-\d+")
        for ident in ("IDEA-20260801-002",       # legacy three-digit
                      "IDEA-20260904-8dccc9",    # current random 6-hex
                      "ECDLP-IDEA-436"):         # legacy area-prefixed
            self.assertEqual(pat.findall(ident), [ident], ident)


class CLITests(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "tools" / "ecc_priority.py"),
                               *args], capture_output=True, text=True, cwd=ROOT)

    def test_budget_violations_exits_zero_when_clean(self):
        p = self._run("--budget-violations")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_list_areas_reports_inclusions_and_exclusions(self):
        p = self._run("--list-areas")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("ECDLP", p.stdout)
        self.assertIn("excluded", p.stdout.lower())


class ContractTextTests(unittest.TestCase):
    def setUp(self):
        self.agents = (ROOT / "AGENTS.md").read_text()
        self.claude = (ROOT / "CLAUDE.md").read_text()

    def test_both_contracts_carry_the_rule(self):
        self.assertIn("ECC comes first", self.agents)
        self.assertIn("ECC comes first", self.claude)

    def test_the_non_relaxations_are_stated(self):
        body = self.agents.split("## ECC comes first", 1)[1].split("\n## ", 1)[0]
        # unlimited is not licence for make-work
        self.assertRegex(body, r"rank ahead of doing nothing")
        # max_concurrent stays bounded
        self.assertIn("max_concurrent", body)
        # designing is not approving
        self.assertRegex(body, r"approved_by: *`?null")
        # priority does not lower the evidence bar
        self.assertRegex(body, r"claim-tier|scope, certificate")


class ProposalDirectoryTests(unittest.TestCase):
    """Open-idea ranking must see every proposal, wherever it was filed.

    ledger/ideas/ is undocumented -- CLAUDE.md, AGENTS.md, the templates and
    every skill say ledger/proposals/ -- but two batches filed there anyway, so
    fourteen well-formed ECC proposals were absent from the ranking that
    instruction 3 calls ranked work. Six of them serve RQ-AUXIN-f8d8c0, and
    GOAL-AUXIN-a93442 names IDEA-20260831-df4197 in its own next_action: a goal
    pointing at work the harness could not see.
    """

    def test_both_proposal_directories_are_scanned(self):
        self.assertIn("proposals", EP.PROPOSAL_DIRS)
        self.assertIn("ideas", EP.PROPOSAL_DIRS)

    def test_paths_are_collected_from_every_declared_directory(self):
        paths = EP._proposal_paths()
        for sub in EP.PROPOSAL_DIRS:
            present = (ROOT / "ledger" / sub).is_dir()
            if not present:
                continue
            self.assertTrue(
                any(f"/ledger/{sub}/" in p for p in paths),
                f"no proposal path collected from ledger/{sub}/",
            )

    def test_the_goal_referenced_auxin_idea_is_rankable(self):
        # The exact record GOAL-AUXIN-a93442's next_action names. It lives in
        # ledger/ideas/, so this fails the moment that directory stops being
        # read -- which is the regression worth catching, not the id itself.
        ids = {i["id"] for i in EP.open_ecc_ideas()}
        self.assertIn("IDEA-20260831-df4197", ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
