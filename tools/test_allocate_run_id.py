#!/usr/bin/env python3
"""Offline CLI regression tests for prospective RUN identifier allocation.

All collision checks use temporary trees. No research records are allocated or
modified in the checkout, and no scientific experiment is executed.
"""
from __future__ import annotations

import random
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import allocate_id as ai


class RunAllocationTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        patch = mock.patch.object(ai, "REPO", self.root)
        patch.start()
        self.addCleanup(patch.stop)

    def cli(self, *arguments: str) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                status = ai.main(list(arguments))
            except SystemExit as exc:
                status = exc.code
        return status, stdout.getvalue(), stderr.getvalue()

    def test_historical_pattern_is_the_validator_object(self) -> None:
        self.assertEqual(ai.PREFIX_TYPE["RUN"], "run")
        self.assertIs(ai.SUPPLEMENTAL_ID_PATTERNS["run"], ai.vl.RUN_ID)

    def test_historical_and_new_names_check_with_validator_grammar(self) -> None:
        for identifier in (
            "RUN-ECDLP-001",
            "RUN-20260907T001122Z-seed_7",
            "RUN-mixed.Case_legacy-01",
            "RUN-ECDLP-abcdef",
        ):
            with self.subTest(identifier=identifier):
                self.assertIsNotNone(ai.vl.RUN_ID.match(identifier))
                status, stdout, stderr = self.cli("--check", identifier)
                self.assertEqual(status, 0, stderr)
                self.assertIn("matches run pattern", stdout)
                self.assertIn("well-formed and free", stdout)

    def test_malformed_names_fail_check(self) -> None:
        for identifier in ("RUN-", "RUN-area/one", "RUN-area one", "RUN-ECC-!"):
            with self.subTest(identifier=identifier):
                self.assertIsNone(ai.vl.RUN_ID.match(identifier))
                status, stdout, _ = self.cli("--check", identifier)
                self.assertEqual(status, 1)
                self.assertIn("REFUSE: malformed", stdout)

    def test_random_allocation_checks_free_and_creates_no_files(self) -> None:
        status, stdout, stderr = self.cli(
            "--next", "run", "--area", "ECDLP", "--seed", "11")
        self.assertEqual(status, 0, stderr)
        match = re.search(r"^free run id for 'ECDLP': (RUN-ECDLP-[0-9a-f]{6})$",
                          stdout, flags=re.MULTILINE)
        self.assertIsNotNone(match, stdout)
        identifier = match.group(1)
        self.assertEqual(identifier, "RUN-ECDLP-" + ai.random_token(random.Random(11)))
        self.assertIn("VERIFY BEFORE USE:", stdout)
        self.assertEqual(self.cli("--check", identifier)[0], 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_single_equals_area_is_accepted(self) -> None:
        status, stdout, stderr = self.cli(
            "--next", "run", "--area=ECDLP", "--seed", "11")
        self.assertEqual(status, 0, stderr)
        self.assertIn("RUN-ECDLP-", stdout)

    def test_nested_run_directory_is_taken_and_seeded_allocation_retries(self) -> None:
        rng = random.Random(11)
        occupied = "RUN-ECDLP-" + ai.random_token(rng)
        expected = "RUN-ECDLP-" + ai.random_token(rng)
        relative = Path("experiments/EXP-ECDLP-abcdef/runs") / occupied
        (self.root / relative).mkdir(parents=True)
        self.assertIn(relative.as_posix(), ai.occurrences(occupied))
        status, stdout, _ = self.cli("--check", occupied)
        self.assertEqual(status, 1)
        self.assertIn("REFUSE: taken", stdout)
        self.assertIn(relative.as_posix(), stdout)

        status, stdout, stderr = self.cli(
            "--next", "run", "--area", "ECDLP", "--seed", "11")
        self.assertEqual(status, 0, stderr)
        self.assertIn("free run id for 'ECDLP': " + expected, stdout)
        self.assertNotIn(occupied, stdout)
        self.assertFalse((self.root / relative.parent / expected).exists())

    def test_historical_directory_is_checked_for_collisions(self) -> None:
        identifier = "RUN-mixed.Case_legacy-01"
        relative = Path("coordination/batches/legacy/runs") / identifier
        (self.root / relative).mkdir(parents=True)
        status, stdout, _ = self.cli("--check", identifier)
        self.assertEqual(status, 1)
        self.assertIn("well-formed: YES", stdout)
        self.assertIn(relative.as_posix(), stdout)
        self.assertIn("REFUSE: taken", stdout)

    def test_missing_or_invalid_new_area_is_refused(self) -> None:
        arguments = [()]
        arguments.extend(("--area", area) for area in (
            "", "ecdlp", "ECDLP3", "EC-DLP", "EC_DLP", "ÉCC", " ECC", "ECC "))
        for area_args in arguments:
            with self.subTest(arguments=area_args):
                status, stdout, stderr = self.cli("--next", "run", *area_args)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertIn("exactly one letters-only uppercase --area", stderr)

    def test_repeated_area_is_refused_including_parser_abbreviations(self) -> None:
        for area_args in (
            ("--area", "ECC", "--area", "ECC"),
            ("--area=ECC", "--area=ECDLP"),
            ("--area", "ECC", "--are", "ECDLP"),
        ):
            with self.subTest(arguments=area_args):
                status, stdout, stderr = self.cli("--next", "run", *area_args)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertIn("exactly one letters-only uppercase --area", stderr)

    def test_date_is_refused_even_when_empty_or_with_valid_area(self) -> None:
        for middle_args in (
            ("--date", "20260907"),
            ("--area", "ECDLP", "--date", "20260907"),
            ("--area", "ECDLP", "--date="),
        ):
            with self.subTest(arguments=middle_args):
                status, stdout, stderr = self.cli("--next", "run", *middle_args)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertIn("does not accept --date", stderr)

    def test_sequential_cli_allocation_is_refused(self) -> None:
        status, stdout, stderr = self.cli(
            "--next", "run", "--area", "ECDLP", "--sequential")
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("sequential RUN allocation is prohibited", stderr)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_direct_helpers_cannot_allocate_invalid_or_sequential_run_ids(self) -> None:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(ai.token_id("run", "ECDLP3", seed=11), 1)
            self.assertEqual(ai.next_free("run", "ECDLP"), 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("letters-only uppercase", stderr.getvalue())
        self.assertIn("sequential RUN allocation is prohibited", stderr.getvalue())

    def test_other_record_types_keep_last_area_behavior(self) -> None:
        status, stdout, stderr = self.cli(
            "--next", "experiment", "--area", "ECC", "--area", "ECDLP",
            "--date", "20260907", "--seed", "11")
        self.assertEqual(status, 0, stderr)
        self.assertIn("EXP-ECDLP-", stdout)


if __name__ == "__main__":
    unittest.main()
