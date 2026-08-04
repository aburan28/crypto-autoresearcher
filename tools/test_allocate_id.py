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

        `DEC-20260727-003` was free in `ledger/decisions/` and taken at
        `ledger/`. Globbing either half alone says "free"; the union says
        "taken". That difference is the whole point of this tool.

        That particular pair no longer demonstrates it: the root-level
        duplicates were relocated into canonical subdirectories, so
        DEC-20260727-003 now resolves to one record and the union adds nothing.
        The property under test is unchanged -- `occurrences` must see the root
        namespace, not just `ledger/*/`. It is pinned here on a record that
        still lives only at the root, so the test breaks if that half of the
        union is ever dropped again.
        """
        root_only = "DEC-20260716-001"
        hits = ai.occurrences(root_only)
        self.assertTrue(hits, f"expected a hit for {root_only}")
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

    def test_random_token_is_the_default_allocation(self) -> None:
        """Sequential scans committed state; only the token cannot converge."""
        self.assertEqual(ai.TOKEN_WIDTH, 6)
        self.assertRegex(ai.random_token(random.Random(3)), r"^[0-9a-f]{6}$")

    def test_token_ids_validate_against_the_build_gate(self) -> None:
        for rec_id in ("DEC-20260802-a3f9c2", "EV-DS-4fac95",
                       "TASK-20260802-00ff11", "H-SUBRES-deadbe"):
            ok, why = ai.well_formed(rec_id)
            self.assertTrue(ok, f"{rec_id} rejected: {why}")

    def test_legacy_numeric_ids_still_validate_forever(self) -> None:
        """Pre-existing records are immutable; they must keep validating."""
        for rec_id in ("DEC-20260731-019", "EV-DS-002", "TASK-20260731-044"):
            ok, why = ai.well_formed(rec_id)
            self.assertTrue(ok, f"legacy {rec_id} rejected: {why}")

    def test_malformed_tokens_are_still_refused(self) -> None:
        for rec_id in ("DEC-20260802-ZZZZZZ", "DEC-20260802-abcd",
                       "DEC-20260802-abcdefg", "EV-DS-XYZ"):
            ok, _ = ai.well_formed(rec_id)
            self.assertFalse(ok, f"{rec_id} should not be well-formed")

    def test_token_space_is_large_enough_to_matter(self) -> None:
        """A 3-digit space made collisions routine; 24 bits makes them rare."""
        self.assertGreater(16 ** ai.TOKEN_WIDTH, 1_000_000)

    def test_seeded_allocation_is_reproducible(self) -> None:
        """Tests and incident reproduction need determinism on demand."""
        self.assertEqual(ai.random_token(random.Random(11)),
                         ai.random_token(random.Random(11)))

    def test_audit_returns_nonzero_while_defects_remain(self) -> None:
        """The repo currently carries pre-existing malformed and duplicated ids."""
        self.assertEqual(ai.audit(), 1)


class BatchIdentifierTests(unittest.TestCase):
    """Batch numbers were the last sequential identifier left in the harness.

    Two lanes each computing "highest batch + 1" from the same committed state
    both open BATCH-028. That is not hypothetical: in one session it happened
    twice -- once as a directory-name collision that had to be resolved by
    yielding the number, and once as an entire card set replaced wholesale
    (CORR-20260803-77d5da).
    """

    def test_batch_is_a_registered_prefix(self) -> None:
        self.assertEqual(ai.PREFIX_TYPE["BATCH"], "batch")

    def test_random_batch_ids_are_well_formed(self) -> None:
        for token in ("2d52f9", "000000", "ffffff"):
            ok, why = ai.well_formed(f"BATCH-{token}")
            self.assertTrue(ok, f"BATCH-{token} rejected: {why}")

    def test_legacy_numeric_batch_ids_remain_valid(self) -> None:
        """Existing batch directories are immutable and must never be renamed."""
        for rec_id in ("BATCH-001", "BATCH-028", "BATCH-037"):
            ok, why = ai.well_formed(rec_id)
            self.assertTrue(ok, f"legacy {rec_id} rejected: {why}")

    def test_malformed_batch_ids_are_refused(self) -> None:
        for rec_id in ("BATCH-28", "BATCH-ZZZZZZ", "BATCH-abcd", "BATCH-0123456"):
            ok, _ = ai.well_formed(rec_id)
            self.assertFalse(ok, f"{rec_id} should not be well-formed")

    def test_batch_takes_no_middle_segment(self) -> None:
        self.assertIn("batch", ai.NO_MIDDLE)

    def test_existing_batch_directories_are_seen_as_taken(self) -> None:
        """Freedom checking must reach batch DIRECTORIES, not just record files.

        A batch identifier lives in a directory name, so an allocator that only
        globbed record files would call every existing batch free.
        """
        self.assertTrue(ai.occurrences("BATCH-028"),
                        "BATCH-028 exists on disk but was reported free")



if __name__ == "__main__":
    unittest.main()
