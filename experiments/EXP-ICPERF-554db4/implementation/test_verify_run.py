"""Synthetic retained-call regressions; no solver or experiment is launched.

These tests use the independent formula/model parser. Point-row calculation is
stubbed only to exercise terminal classification; it is not a curve certificate.
"""

from __future__ import annotations

import gzip
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("m8_verify_run", Path(__file__).with_name("verify_run.py"))
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
prior = checker.old_independent_checker()


class CallStatusTest(unittest.TestCase):
    def check(self, status, outcomes=(), *, elapsed=1.0, certified=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = b"p cnf 454 0\n"
            packed = gzip.compress(raw, mtime=0)
            (root / "formula.gz").write_bytes(packed)
            arm = {"formula_path": "formula.gz", "formula_gzip_sha256": checker.sha(packed),
                   "raw_xcnf_sha256": checker.sha(raw), "target_coordinate": 1}
            host = {"available_memory_bytes": 12 << 30, "free_disk_bytes": 10**10,
                    "declared_raw_reserve_bytes": 1, "load_average": [0, 0, 0]}
            call = root / "calls" / "weighted_sorted"
            call.mkdir(parents=True)
            attempts, blocked = [], []
            rows = [{"synthetic_terminal_test": True}] if certified else []
            for index, outcome in enumerate(outcomes, 1):
                attempt_dir = call / f"attempt-{index:04d}"
                attempt_dir.mkdir()
                exact = prior.add_blocks(raw, blocked)
                input_path = attempt_dir / "input.xcnf"
                input_path.write_bytes(exact)
                attempt = {"input_sha256": checker.sha(exact), "blocked_primary": len(blocked),
                           "command": ["unused-solver", "--verb", "0", "--threads", "1",
                                       "--maxsol", "1", "--random", "20261018", str(input_path)],
                           "outcome": outcome}
                if outcome == "solver_launch_failure":
                    attempt.update(error_type="OSError", error="synthetic launch failure")
                else:
                    sat = outcome in ("rejected_primary", "point_relation_certified",
                                      "point_relation_certified_after_wall_cap")
                    returncode = 10 if sat else 0
                    stdout = b""
                    if sat:
                        primary = index - 1
                        model = " ".join(str(j if primary >> (j - 1) & 1 else -j)
                                         for j in range(1, 455))
                        stdout = f"s SATISFIABLE\nv {model} 0\n".encode()
                        cert = {"assignment_hex": hex(primary), "base_kind": "weighted",
                                "encoding": "sorted", "result": {"full_point_certificates": rows}}
                        blob = json.dumps(cert).encode()
                        (attempt_dir / "certificate.json").write_bytes(blob)
                        attempt.update(primary_assignment_hex=hex(primary),
                                       certificate_sha256=checker.sha(blob))
                        if not rows:
                            blocked.append(primary)
                    elif outcome == "solver_reported_exhausted_unvalidated":
                        returncode, stdout = 20, b"s UNSATISFIABLE\n"
                    elif outcome == "solver_unknown_censored":
                        stdout = b"s UNKNOWN\n"
                    (attempt_dir / "stdout.txt").write_bytes(stdout)
                    (attempt_dir / "stderr.txt").write_bytes(b"")
                    attempt["solver_status_lines"] = [line for line in stdout.decode().splitlines()
                                                       if line.startswith("s ")]
                    attempt["process"] = {"wall_timeout": outcome == "wall_censored",
                                          "rss_watchdog_tripped": outcome == "memory_censored",
                                          "returncode": returncode,
                                          "stdout_sha256": checker.sha(stdout),
                                          "stderr_sha256": checker.sha(b"")}
                (attempt_dir / "attempt.json").write_text(json.dumps(attempt))
                attempts.append(attempt)
            summary = {"name": "weighted_sorted", "host": host, "status": status,
                       "input_sha256": checker.sha(raw), "attempts": attempts,
                       "limits": {"seed": 20261018, "memory_bytes": 8 << 30,
                                  "max_models": 64, "wall_seconds": 1200},
                       "blocked_primary_count": len(blocked), "total_wall_seconds": elapsed}
            blob = json.dumps(summary).encode()
            (call / "summary.json").write_bytes(blob)
            row = {"name": summary["name"], "host": host, "status": status,
                   "attempts": len(attempts), "summary_sha256": checker.sha(blob)}
            with patch.object(checker, "ROOT", root), \
                    patch.object(prior, "exact_point_rows", return_value=rows), \
                    patch("subprocess.Popen", side_effect=AssertionError("solver launch forbidden")):
                return checker.check_call(root, row, {}, arm, {}, {}, prior)

    def test_empty_certified_summary_rejected(self):
        for status in ("point_relation_certified", "point_relation_certified_after_wall_cap"):
            with self.subTest(status=status), self.assertRaises(ValueError):
                self.check(status)

    def test_censor_cannot_be_relabelled_as_certified(self):
        with self.assertRaisesRegex(ValueError, "call status differs"):
            self.check("point_relation_certified", ["memory_censored"])

    def test_attempt_after_terminal_rejected(self):
        for terminal in ("memory_censored", "solver_launch_failure", "point_relation_certified"):
            with self.subTest(terminal=terminal), self.assertRaisesRegex(ValueError, "after terminal"):
                self.check(terminal, [terminal, "memory_censored"], certified=True)

    def test_process_terminal_statuses_retained(self):
        for status in ("wall_censored", "memory_censored", "solver_launch_failure",
                       "solver_reported_exhausted_unvalidated", "solver_unknown_censored",
                       "solver_failure_or_unclassified"):
            with self.subTest(status=status):
                result = self.check(status, [status], elapsed=1200)
                self.assertEqual(result["status"], status)
                self.assertEqual(result["independent_certified_attempts"], 0)

    def test_independently_checked_certificate_retained(self):
        for status in ("point_relation_certified", "point_relation_certified_after_wall_cap"):
            with self.subTest(status=status):
                result = self.check(status, [status], elapsed=1201, certified=True)
                self.assertEqual(result["independent_certified_attempts"], 1)

    def test_model_cap_requires_all_64_rejected_models(self):
        result = self.check("model_cap_censored", ["rejected_primary"] * 64)
        self.assertEqual(result["checked_attempts"], 64)
        for count in (0, 1, 63, 65):
            with self.subTest(count=count), self.assertRaises(ValueError):
                self.check("model_cap_censored", ["rejected_primary"] * count)

    def test_wall_budget_can_expire_between_attempts(self):
        for outcomes in ([], ["rejected_primary"]):
            with self.subTest(outcomes=outcomes):
                self.assertEqual(self.check("wall_censored", outcomes, elapsed=1200)["status"],
                                 "wall_censored")
                with self.assertRaises(ValueError):
                    self.check("wall_censored", outcomes, elapsed=1199)

    def test_wall_capped_terminal_requires_elapsed_budget(self):
        with self.assertRaisesRegex(ValueError, "elapsed wall budget"):
            self.check("wall_censored", ["wall_censored"], elapsed=1199)
        with self.assertRaisesRegex(ValueError, "elapsed wall budget"):
            self.check("point_relation_certified_after_wall_cap",
                       ["point_relation_certified_after_wall_cap"], elapsed=1199, certified=True)

    def test_invalid_elapsed_time_rejected(self):
        for elapsed in (-1, float("nan"), float("inf")):
            with self.subTest(elapsed=elapsed), self.assertRaisesRegex(ValueError, "call duration"):
                self.check("memory_censored", ["memory_censored"], elapsed=elapsed)


if __name__ == "__main__":
    unittest.main()
