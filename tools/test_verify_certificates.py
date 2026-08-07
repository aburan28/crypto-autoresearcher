#!/usr/bin/env python3
"""Tests for tools/verify_certificates.py.

Two layers, matching why the tool exists: unit tests that the arithmetic
itself catches tampering (a solver bug or a fabricated certificate must fail
independent reverification even when the run self-reports verified: true),
and an integration test that the full repository sweep is currently clean.
"""
from __future__ import annotations

import copy
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import verify_certificates as vc  # noqa: E402


VALID_DLOG = {
    "curve": {"p": 223, "a": 0, "b": 171},
    "P": [105, 42],
    "Q": [81, 42],
    "k": 2,
}

VALID_DECOMP = {
    "curve": {"p": 137, "a": 52, "b": 49},
    "target": [27, 60],
    "summands": [[99, 78], [67, 108]],
}


class DiscreteLogTests(unittest.TestCase):
    def test_valid_statement_verifies(self) -> None:
        vc.verify_statement("discrete_log", VALID_DLOG)  # must not raise

    def test_wrong_k_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DLOG)
        bad["k"] = VALID_DLOG["k"] + 1
        with self.assertRaises(Exception):
            vc.verify_statement("discrete_log", bad)

    def test_off_curve_Q_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DLOG)
        bad["Q"] = [bad["Q"][0], bad["Q"][1] + 1]
        with self.assertRaises(Exception):
            vc.verify_statement("discrete_log", bad)

    def test_off_curve_P_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DLOG)
        bad["P"] = [bad["P"][0], bad["P"][1] + 1]
        with self.assertRaises(Exception):
            vc.verify_statement("discrete_log", bad)

    def test_missing_field_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DLOG)
        del bad["k"]
        with self.assertRaises(Exception):
            vc.verify_statement("discrete_log", bad)

    def test_missing_curve_field_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DLOG)
        del bad["curve"]["b"]
        with self.assertRaises(Exception):
            vc.verify_statement("discrete_log", bad)

    def test_fabricated_certificate_with_self_reported_verified_true_fails(self) -> None:
        # The exact failure mode this tool exists for: a run manifest can say
        # certificate.verified: true regardless of what verify_statement
        # thinks. This asserts the independent recomputation still catches a
        # bad witness -- the self-reported flag carries no weight here.
        forged = copy.deepcopy(VALID_DLOG)
        forged["k"] = 999
        with self.assertRaises(Exception):
            vc.verify_statement("discrete_log", forged)


class DecompositionTests(unittest.TestCase):
    def test_valid_statement_verifies(self) -> None:
        vc.verify_statement("decomposition", VALID_DECOMP)  # must not raise

    def test_wrong_target_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DECOMP)
        bad["target"] = [bad["target"][0], bad["target"][1] + 1]
        with self.assertRaises(Exception):
            vc.verify_statement("decomposition", bad)

    def test_tampered_summand_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DECOMP)
        bad["summands"][1] = [bad["summands"][1][0], bad["summands"][1][1] - 1]
        with self.assertRaises(Exception):
            vc.verify_statement("decomposition", bad)

    def test_dropped_summand_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DECOMP)
        bad["summands"] = bad["summands"][:1]
        with self.assertRaises(Exception):
            vc.verify_statement("decomposition", bad)

    def test_extra_summand_is_rejected(self) -> None:
        bad = copy.deepcopy(VALID_DECOMP)
        bad["summands"] = bad["summands"] + [bad["summands"][0]]
        with self.assertRaises(Exception):
            vc.verify_statement("decomposition", bad)


class KindHandlingTests(unittest.TestCase):
    def test_none_kind_is_rejected_by_verify_statement(self) -> None:
        # verify_statement is only ever called on claim-bearing kinds by the
        # sweep; calling it on "none" directly is a caller bug, and it must
        # say so rather than silently accepting an empty statement.
        with self.assertRaises(Exception):
            vc.verify_statement("none", {})

    def test_unknown_kind_is_rejected(self) -> None:
        with self.assertRaises(Exception):
            vc.verify_statement("wormhole", VALID_DLOG)


class RepositorySweepTests(unittest.TestCase):
    def test_full_repository_sweep_is_currently_clean(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO / "tools" / "verify_certificates.py")],
            cwd=REPO, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0,
                         f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        self.assertIn("every claimed certificate independently reverifies",
                      result.stdout)

    def test_baseline_is_prune_only_no_stale_entries(self) -> None:
        # Every grandfathered path must still actually be unparseable; a
        # stale entry would mean a repaired file is silently unwatched.
        errors, unparseable = vc.check()
        baseline = vc._baseline()
        stale = baseline - unparseable
        self.assertFalse(
            stale,
            f"stale baseline entries (now parse; remove from "
            f"tools/verify_certificates_baseline.txt): {sorted(stale)}")

    def test_baseline_only_covers_known_preexisting_files(self) -> None:
        # Guards against the baseline quietly growing to cover a *new*
        # failure introduced by some future change, rather than shrinking as
        # documented.
        baseline = vc._baseline()
        self.assertEqual(
            baseline,
            {
                "experiments/EXP-DREG-001/runs/RUN-DREG-001-DFF-N12-SEM/raw-result.json",
                "experiments/EXP-DREG-001/runs/RUN-DREG-001-DFF-N12-SEM-b/raw-result.json",
            },
        )


if __name__ == "__main__":
    unittest.main()
