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
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

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

    def test_goal_uses_the_authoritative_combined_pattern(self) -> None:
        for rec_id in ("GOAL-ECDLP-001", "GOAL-ERANK-a1b2c3"):
            with self.subTest(rec_id):
                ok, why = ai.well_formed(rec_id)
                self.assertTrue(ok, why)
                self.assertIn("goal pattern", why)

    def test_malformed_goal_suffixes_are_refused(self) -> None:
        for rec_id in ("GOAL-ERANK-01", "GOAL-ERANK-abcd",
                       "GOAL-ERANK-ABCDEF", "GOAL-erank-a1b2c3"):
            with self.subTest(rec_id):
                self.assertFalse(ai.well_formed(rec_id)[0])

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

    def test_deep_task_directory_is_seen_as_taken(self) -> None:
        hits = ai.occurrences("TASK-20260811-338053")
        self.assertTrue(
            any("/tasks/TASK-20260811-338053" in "/" + path
                for path in hits),
            f"deep task directory was not collision-scanned: {hits}")

    def test_check_refuses_deep_task_id(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            status = ai.check("TASK-20260811-338053")
        self.assertEqual(status, 1)
        self.assertIn("REFUSE: taken", output.getvalue())

    def test_batch_local_task_card_is_seen_as_taken(self) -> None:
        hits = ai.occurrences("TASK-20260811-6830b6")
        self.assertTrue(
            any(path.endswith(
                "BATCH-080a9c/task-cards/TASK-20260811-6830b6.md")
                for path in hits),
            f"batch-local task card was not collision-scanned: {hits}")

    def test_deep_scan_does_not_create_false_hits_for_free_task_id(self) -> None:
        self.assertEqual(ai.occurrences("TASK-20991231-abcdef"), [])

    def test_recursive_scan_covers_each_allocated_record_prefix(self) -> None:
        for rec_id in (
            "GOAL-MONO-001",
            "TASK-20260811-338053",
            "EXP-ALMIG-001",
            "EV-ECDLP-2a7e77",
            "DEC-20260811-7dcb39",
            "CORR-20260811-63f18a",
            "BATCH-080a9c",
        ):
            with self.subTest(rec_id):
                self.assertTrue(
                    ai.occurrences(rec_id),
                    f"recursive collision scan missed {rec_id}")

    def test_appledouble_siblings_are_not_counted_as_records(self) -> None:
        self.assertFalse(any("/._" in p for p in ai._paths()))
        self.assertFalse(any("/._" in p for p in ai._identifier_paths()))

    def test_recursive_scan_excludes_git_and_other_worktrees(self) -> None:
        paths = [path.replace("\\", "/") for path in ai._identifier_paths()]
        self.assertFalse(any("/.git/" in path for path in paths))
        self.assertFalse(any("/.worktrees/" in path for path in paths))


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

    def test_seeded_goal_allocation_uses_area_and_six_hex_token(self) -> None:
        output = StringIO()
        with mock.patch.object(ai, "occurrences", return_value=[]):
            with redirect_stdout(output):
                status = ai.main([
                    "--next", "goal", "--area", "ERANK", "--seed", "11",
                ])
        self.assertEqual(status, 0)
        self.assertRegex(
            output.getvalue(),
            r"free goal id for 'ERANK': GOAL-ERANK-[0-9a-f]{6}",
        )

    def test_free_legacy_goal_fails_prospective_check(self) -> None:
        output = StringIO()
        with mock.patch.object(ai, "occurrences", return_value=[]):
            with redirect_stdout(output):
                status = ai.check("GOAL-FREE-999")
        self.assertEqual(status, 1)
        self.assertIn("free legacy-form GOAL id cannot be minted", output.getvalue())
        self.assertTrue(ai.well_formed("GOAL-FREE-999")[0])

    def test_free_random_goal_passes_prospective_check(self) -> None:
        output = StringIO()
        with mock.patch.object(ai, "occurrences", return_value=[]):
            with redirect_stdout(output):
                status = ai.check("GOAL-FREE-a1b2c3")
        self.assertEqual(status, 0)
        self.assertIn("well-formed and free", output.getvalue())

    def test_existing_legacy_goal_remains_unavailable(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            status = ai.check("GOAL-BLAKE-001")
        self.assertEqual(status, 1)
        self.assertIn("REFUSE: taken", output.getvalue())

    def test_goal_next_rejects_date_scope(self) -> None:
        error = StringIO()
        with redirect_stderr(error), self.assertRaises(SystemExit) as raised:
            ai.main(["--next", "goal", "--date", "20260822"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("requires exactly --area", error.getvalue())

    def test_goal_next_rejects_simultaneous_area_and_date(self) -> None:
        error = StringIO()
        with redirect_stderr(error), self.assertRaises(SystemExit) as raised:
            ai.main([
                "--next", "goal", "--area", "ERANK",
                "--date", "20260822",
            ])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("does not accept --date", error.getvalue())

    def test_goal_next_requires_area_scope(self) -> None:
        error = StringIO()
        with redirect_stderr(error), self.assertRaises(SystemExit) as raised:
            ai.main(["--next", "goal"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("requires exactly --area", error.getvalue())

    def test_unrelated_area_and_date_scoped_types_retain_behavior(self) -> None:
        output = StringIO()
        with mock.patch.object(ai, "occurrences", return_value=[]):
            with redirect_stdout(output):
                evidence = ai.main([
                    "--next", "evidence", "--area", "TEST", "--seed", "7",
                ])
                decision = ai.main([
                    "--next", "coordinator_decision", "--date", "20260822",
                    "--seed", "7",
                ])
                legacy_simultaneous = ai.main([
                    "--next", "evidence", "--area", "TEST",
                    "--date", "20260822", "--seed", "7",
                ])
        self.assertEqual((evidence, decision, legacy_simultaneous), (0, 0, 0))
        self.assertIn("EV-TEST-", output.getvalue())
        self.assertIn("DEC-20260822-", output.getvalue())

    def test_sequential_goal_allocation_is_prohibited(self) -> None:
        error = StringIO()
        with redirect_stderr(error):
            status = ai.main([
                "--next", "goal", "--area", "ERANK", "--sequential",
            ])
        self.assertEqual(status, 1)
        self.assertIn("sequential GOAL allocation is prohibited", error.getvalue())

    def test_sharded_goal_directory_is_seen_as_taken(self) -> None:
        hits = ai.occurrences("GOAL-MONO-001")
        self.assertTrue(any(path.endswith("ledger/goals/GOAL-MONO-001")
                            for path in hits), hits)

    def test_flat_goal_file_is_seen_as_taken(self) -> None:
        hits = ai.occurrences("GOAL-BLAKE-001")
        self.assertTrue(any(path.endswith("ledger/goals/GOAL-BLAKE-001.yaml")
                            for path in hits), hits)

    def test_sharded_goal_audit_uses_directory_identifier(self) -> None:
        path = next(
            candidate for candidate in ai._paths()
            if candidate.replace("\\", "/").endswith(
                "ledger/goals/GOAL-MONO-001/goal.yaml")
        )
        self.assertEqual(ai._record_identifier(path), "GOAL-MONO-001")

    def test_audit_returns_nonzero_while_defects_remain(self) -> None:
        """The repo currently carries pre-existing malformed and duplicated ids."""
        self.assertEqual(ai.audit(), 1)


class CorrectionIdentifierTests(unittest.TestCase):
    def test_correction_is_a_registered_dated_type(self) -> None:
        self.assertEqual(ai.PREFIX_TYPE["CORR"], "correction")
        self.assertNotIn("correction", ai.NO_MIDDLE)

    def test_random_and_legacy_correction_ids_validate(self) -> None:
        for rec_id in ("CORR-20260811-88a263", "CORR-20260728-001"):
            with self.subTest(rec_id):
                ok, why = ai.well_formed(rec_id)
                self.assertTrue(ok, f"{rec_id} rejected: {why}")

    def test_malformed_correction_ids_are_refused(self) -> None:
        for rec_id in ("CORR-2026081-88a263", "CORR-20260811-ZZZZZZ",
                       "CORR-20260811-abcd", "CORR-ECDLP-88a263"):
            with self.subTest(rec_id):
                self.assertFalse(ai.well_formed(rec_id)[0])

    def test_correction_pattern_reuses_validator_suffix(self) -> None:
        pattern = ai.SUPPLEMENTAL_ID_PATTERNS["correction"].pattern
        self.assertIn(ai.vl.SUFFIX, pattern)

    def test_batch_local_correction_is_seen_as_taken(self) -> None:
        hits = ai.occurrences("CORR-20260811-63f18a")
        self.assertTrue(
            any(path.endswith(
                "BATCH-080a9c/corrections/CORR-20260811-63f18a.yaml")
                for path in hits),
            f"batch-local correction was not collision-scanned: {hits}")

    def test_experiment_local_correction_is_seen_as_taken(self) -> None:
        hits = ai.occurrences("CORR-ALMIG-001")
        self.assertTrue(
            any(path.endswith(
                "experiments/EXP-ALMIG-001/corrections/CORR-ALMIG-001.yaml")
                for path in hits),
            f"experiment-local correction was not collision-scanned: {hits}")

    def test_legacy_nondated_correction_remains_reported_debt(self) -> None:
        ok, why = ai.well_formed("CORR-ALMIG-001")
        self.assertFalse(ok)
        self.assertIn("CORR-", why)

    def test_seeded_next_correction_uses_date_and_six_hex_token(self) -> None:
        output = StringIO()
        with mock.patch.object(ai, "occurrences", return_value=[]):
            with redirect_stdout(output):
                status = ai.main([
                    "--next", "correction",
                    "--date", "20260811",
                    "--seed", "11",
                ])
        self.assertEqual(status, 0)
        self.assertRegex(
            output.getvalue(),
            r"free correction id for '20260811': CORR-20260811-[0-9a-f]{6}")

    def test_check_rejects_existing_correction_collision(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            status = ai.check("CORR-20260811-63f18a")
        self.assertEqual(status, 1)
        self.assertIn("REFUSE: taken", output.getvalue())


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
