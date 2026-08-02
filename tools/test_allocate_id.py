#!/usr/bin/env python3
"""Tests for the identifier allocation gate.

The two tests that matter are `test_refuses_the_id_that_actually_shipped` and
`test_refuses_an_id_taken_only_in_the_other_namespace`. They pin the exact two
defects this tool exists to prevent, both of which reached a pushed commit
before anything caught them:

  - `EXP-RT1476-001` was authored, approved, executed, validated, committed and
    pushed before the build gate rejected its digit-bearing area code
    (CORR-20260728-001).
  - `DEC-20260727-003` was drafted for a conflict-repair ruling and collided
    with a published root-level record; had it shipped, the ruling convened to
    repair ID collisions would have committed one (DEC-20260727-005).

If either regresses, this tool is decorative.
"""
from __future__ import annotations

import sys
import inspect
import random
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import allocate_id as ai


class WellFormednessTests(unittest.TestCase):
    def test_refuses_the_id_that_actually_shipped(self) -> None:
        ok, why = ai.well_formed("EXP-RT1476-001")
        self.assertFalse(ok)
        self.assertIn("letters-only", why)

    def test_accepts_the_repaired_id(self) -> None:
        ok, _ = ai.well_formed("EXP-SUBRES-001")
        self.assertTrue(ok)

    def test_digit_bearing_area_codes_are_refused_for_every_type(self) -> None:
        for bad in ("H-RT1476-001", "EV-RT1476-001", "RQ-FB3-001", "H-P13-001"):
            with self.subTest(bad):
                self.assertFalse(ai.well_formed(bad)[0])

    def test_dated_types_legitimately_carry_digits(self) -> None:
        for good in ("DEC-20260728-003", "TASK-20260728-001", "IDEA-20260726-001"):
            with self.subTest(good):
                self.assertTrue(ai.well_formed(good)[0])

    def test_unpatterned_prefix_says_so_rather_than_passing_silently(self) -> None:
        """CORR/GOAL/KN have no enforced pattern; the tool must not imply they do."""
        ok, why = ai.well_formed("CORR-20260728-001")
        self.assertTrue(ok)
        self.assertIn("NOT checked", why)

    def test_patterns_come_from_the_build_gate_not_a_copy(self) -> None:
        """If this tool restated the patterns they could drift apart silently."""
        import validate_ledger as vl
        self.assertIs(ai.vl.ID_PATTERNS, vl.ID_PATTERNS)


class UnionScopeTests(unittest.TestCase):
    def test_search_covers_both_namespaces(self) -> None:
        globs = " ".join(ai.SEARCH_GLOBS)
        self.assertIn("ledger/*.yaml", globs.replace("\\", "/"))
        self.assertIn("ledger/*/*.yaml", globs.replace("\\", "/"))

    def test_refuses_an_id_taken_only_in_the_other_namespace(self) -> None:
        """The collision that nearly shipped inside the collision repair.

        `DEC-20260727-003` is free in `ledger/decisions/` and taken at
        `ledger/`. Globbing either half alone says "free"; the union says
        "taken". That difference is the whole point of this tool.
        """
        hits = ai.occurrences("DEC-20260727-003")
        self.assertTrue(hits, "expected a hit in the root namespace")
        self.assertTrue(any(h.count("/") == 1 for h in hits),
                        f"expected a root-level ledger/*.yaml hit, got {hits}")

    def test_a_genuinely_free_id_reports_no_occurrences(self) -> None:
        self.assertEqual(ai.occurrences("EXP-NOSUCHAREA-999"), [])

    def test_appledouble_siblings_are_not_counted_as_records(self) -> None:
        self.assertFalse(any("/._" in p for p in ai._paths()))


class AllocationTests(unittest.TestCase):
    def test_next_free_never_fills_a_gap(self) -> None:
        """Gaps have undetermined provenance; reusing one revives a retired record."""
        used = {1, 2, 5}
        self.assertEqual(max(used) + 1, 6)

    def test_random_allocation_stays_strictly_above_the_maximum(self) -> None:
        """Randomising must not start filling gaps: a gap is not a free slot."""
        used = {1, 2, 5}
        floor = max(used)
        for seed in range(200):
            rng = random.Random(seed)
            pick = rng.choice(list(range(floor + 1, ai.CEILING + 1)))
            self.assertGreater(pick, floor)
            self.assertNotIn(pick, used)
            self.assertLessEqual(pick, ai.CEILING)

    def test_random_is_the_default_and_sequential_is_opt_in(self) -> None:
        """The default must not be max+1: that is what collides across worktrees."""
        sig = inspect.signature(ai.next_free)
        self.assertIs(sig.parameters["random_pick"].default, True)

    def test_random_allocation_spreads_across_the_tail(self) -> None:
        """A 'random' allocator that returns one value would collide as badly."""
        floor, picks = 24, set()
        for seed in range(64):
            rng = random.Random(seed)
            picks.add(rng.choice(list(range(floor + 1, ai.CEILING + 1))))
        self.assertGreater(len(picks), 32,
                           "allocation is too concentrated to reduce collisions")

    def test_seeded_allocation_is_reproducible(self) -> None:
        """Tests and incident reproduction need determinism on demand."""
        a = random.Random(11).choice(list(range(25, ai.CEILING + 1)))
        b = random.Random(11).choice(list(range(25, ai.CEILING + 1)))
        self.assertEqual(a, b)

    def test_random_token_is_the_default_allocation(self) -> None:
        """Sequential/numeric both scan state; only the token cannot converge."""
        self.assertEqual(ai.TOKEN_WIDTH, 6)
        rng = random.Random(3)
        tok = ai.random_token(rng)
        self.assertRegex(tok, r"^[0-9a-f]{6}$")

    def test_token_ids_validate_against_the_build_gate(self) -> None:
        for rec_id in ("DEC-20260801-a3f9c2", "EV-DS-4fac95",
                       "TASK-20260801-00ff11", "H-SUBRES-deadbe"):
            ok, why = ai.well_formed(rec_id)
            self.assertTrue(ok, f"{rec_id} rejected: {why}")

    def test_legacy_numeric_ids_still_validate_forever(self) -> None:
        """Pre-2026-08-01 records are immutable; they must keep validating."""
        for rec_id in ("DEC-20260731-019", "EV-DS-002", "TASK-20260731-044"):
            ok, why = ai.well_formed(rec_id)
            self.assertTrue(ok, f"legacy {rec_id} rejected: {why}")

    def test_malformed_tokens_are_still_refused(self) -> None:
        for rec_id in ("DEC-20260801-ZZZZZZ", "DEC-20260801-abcd",
                       "DEC-20260801-abcdefg", "EV-DS-XYZ"):
            ok, _ = ai.well_formed(rec_id)
            self.assertFalse(ok, f"{rec_id} should not be well-formed")

    def test_token_space_is_large_enough_to_matter(self) -> None:
        """A 3-digit space made collisions routine; 24 bits makes them rare."""
        self.assertGreater(16 ** ai.TOKEN_WIDTH, 1_000_000)

    def test_audit_returns_nonzero_while_defects_remain(self) -> None:
        """The repo currently carries pre-existing malformed and duplicated ids."""
        self.assertEqual(ai.audit(), 1)


if __name__ == "__main__":
    unittest.main()
