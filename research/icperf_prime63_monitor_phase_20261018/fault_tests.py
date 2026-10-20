"""Deterministic synthetic fault suite. No Sage algebra is invoked."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

import driver
import monitor
from phase import inspect

HERE = Path(__file__).resolve().parent


class MonitorTests(unittest.TestCase):
    def temporary(self):
        return tempfile.TemporaryDirectory(prefix="synthetic-", dir=HERE)

    def check_call(self, command, **kwargs):
        with self.temporary() as tmp:
            output = Path(tmp) / "call"
            result = monitor.supervise(command, output, seconds=kwargs.pop("seconds", 1.0),
                                       rss_cap_bytes=kwargs.pop("rss_cap", 8*1024**3),
                                       scratch_cap_bytes=8*1024**3,
                                       poll_seconds=0.005, **kwargs)
            self.assertEqual(result["trace"]["sha256"],
                             hashlib.sha256((output/"phase.jsonl").read_bytes()).hexdigest())
            self.assertTrue((output/"stdout.raw").exists())
            self.assertTrue((output/"stderr.raw").exists())
            return result, (output/"phase.jsonl").read_text()

    def test_normal_exit(self):
        result, trace = self.check_call([sys.executable, "-c", "print('normal')"])
        self.assertEqual((result["stop"], result["exit_code"]), ("exited", 0))
        self.assertIn('"event":"terminal"', trace)

    def test_abrupt_exit(self):
        result, _ = self.check_call([sys.executable, "-c", "import os; os._exit(7)"])
        self.assertEqual((result["stop"], result["exit_code"]), ("exited", 7))

    def test_zombie_during_sampling(self):
        class FakePsutil:
            class NoSuchProcess(Exception): pass
            class ZombieProcess(Exception): pass
            class AccessDenied(Exception): pass
            STATUS_ZOMBIE = "zombie"
            def Process(self, pid): return self
            def status(self): return "zombie"
            def process_iter(self): return []
        class Child:
            pid = 999999
            def __init__(self): self.calls = 0
            def poll(self):
                self.calls += 1
                return 0 if self.calls > 2 else None
        child = Child()
        self.assertEqual(monitor._root_lifecycle(child, FakePsutil()), "zombie_or_exited")

    def test_nosuchprocess_reap_race(self):
        class FakePsutil:
            class NoSuchProcess(Exception): pass
            class ZombieProcess(Exception): pass
            class AccessDenied(Exception): pass
            STATUS_ZOMBIE = "zombie"
            def Process(self, pid): return self
            def status(self): raise self.NoSuchProcess()
        class Child:
            pid = 999999
            def __init__(self): self.calls = 0
            def poll(self):
                self.calls += 1
                return 0 if self.calls > 1 else None
        self.assertEqual(monitor._root_lifecycle(Child(), FakePsutil()), "exited")

    def test_live_unreadable_fail_closed(self):
        def unreadable(child):
            self.assertIsNone(child.poll())
            raise monitor.MonitorFault("unreadable_live_root", "injected")
        result, trace = self.check_call([sys.executable, "-c", "import time; time.sleep(0.5)"],
                                        probe=unreadable)
        self.assertEqual(result["stop"], "infrastructure_monitor_error")
        self.assertEqual(result["fault"]["code"], "unreadable_live_root")
        self.assertIsNone(result["peak_tree_rss_bytes_sampled"])
        self.assertIn('"event":"sample_unavailable"', trace)
        self.assertNotIn('"rss_bytes":0', trace)

    def test_reaped_group_membership_permission_fail_closed(self):
        import psutil
        class Child:
            pid = 999999
            def poll(self): return 0
        class Process:
            pid = 888888
        with mock.patch.object(psutil, "process_iter", return_value=[Process()]):
            with mock.patch.object(monitor.os, "getpgid", side_effect=PermissionError("injected")):
                with self.assertRaises(monitor.MonitorFault) as context:
                    monitor._terminate_group(Child())
        self.assertEqual(context.exception.code, "group_teardown_unverified")

    def test_teardown_fault_retains_raw_custody(self):
        with self.temporary() as tmp:
            output = Path(tmp) / "call"
            error = monitor.MonitorFault("group_teardown_unverified", "injected")
            with mock.patch.object(monitor, "_terminate_group", side_effect=error):
                result = monitor.supervise([sys.executable, "-c", "print('done')"],
                                           output, seconds=1.0,
                                           rss_cap_bytes=8*1024**3,
                                           scratch_cap_bytes=8*1024**3,
                                           poll_seconds=0.005)
            self.assertEqual(result["stop"], "infrastructure_monitor_error")
            self.assertEqual(result["fault"]["code"], "group_teardown_unverified")
            self.assertEqual(result["trace"]["sha256"],
                             hashlib.sha256((output/"phase.jsonl").read_bytes()).hexdigest())
            self.assertEqual(result["stdout_sha256"],
                             hashlib.sha256((output/"stdout.raw").read_bytes()).hexdigest())
            self.assertTrue(result["trace"]["valid"])
            self.assertIn('"event":"terminal"', (output/"phase.jsonl").read_text())

    def test_rss_cap_termination(self):
        result, _ = self.check_call([sys.executable, "-c", "import time; time.sleep(0.5)"],
                                    rss_cap=1)
        self.assertEqual(result["stop"], "memory_censored")
        self.assertGreater(result["peak_tree_rss_bytes_sampled"], 1)

    def test_repeated_fast_exit_reap(self):
        for _ in range(20):
            result, _ = self.check_call([sys.executable, "-c", "pass"])
            self.assertEqual(result["stop"], "exited")
            self.assertIsNone(result["fault"])

    def test_partial_phase_trace_after_timeout(self):
        with self.temporary() as tmp:
            root = Path(tmp) / "dry"
            record = driver.dry_run(root, "timeout")
            trace_path = root / "call/phase.jsonl"
            rows = [json.loads(line) for line in trace_path.read_text().splitlines()]
            self.assertEqual(record["stop"], "timeout_censored")
            self.assertEqual(record["trace"]["sha256"], inspect(trace_path)["sha256"])
            self.assertTrue(inspect(trace_path)["valid"])
            by_stream = {}
            for row in rows:
                previous = by_stream.get(row["stream"])
                if previous is not None:
                    self.assertGreaterEqual(row["monotonic_ns"], previous)
                by_stream[row["stream"]] = row["monotonic_ns"]
            self.assertEqual(record["files_sha256"]["phase.jsonl"], inspect(trace_path)["sha256"])
            self.assertTrue(any(r["event"] == "sample" for r in rows))
            self.assertTrue(any(r["phase"] == "groebner" and r["event"] == "begin" for r in rows))
            self.assertFalse(any(r["phase"] == "groebner" and r["event"] == "end" for r in rows))
            self.assertTrue((root / "custody.json").exists())
            self.assertTrue(record["trace"]["records"] >= 5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validation", type=Path, required=True)
    args = parser.parse_args()
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(MonitorTests)
    class Capture(unittest.TextTestResult):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.cases = []
        def addSuccess(self, test):
            super().addSuccess(test)
            self.cases.append({"name": test._testMethodName, "status": "pass"})
        def addFailure(self, test, err):
            super().addFailure(test, err)
            self.cases.append({"name": test._testMethodName, "status": "fail", "detail": self._exc_info_to_string(err,test)})
        def addError(self, test, err):
            super().addError(test, err)
            self.cases.append({"name": test._testMethodName, "status": "error", "detail": self._exc_info_to_string(err,test)})
    runner = unittest.TextTestRunner(verbosity=2, resultclass=Capture)
    started = time.time_ns()
    result = runner.run(tests)
    record = {"schema": "icperf-prime63-synthetic-validation-v1",
              "scientific_trials": 0, "interpreter": sys.executable,
              "started_unix_ns": started, "ended_unix_ns": time.time_ns(),
              "tests_run": result.testsRun, "ok": result.wasSuccessful(),
              "cases": result.cases,
              "source_sha256": {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                                 for name in ("monitor.py", "phase.py", "instrumented_backend.py",
                                              "driver.py", "fault_tests.py")}}
    with args.validation.open("x") as stream:
        json.dump(record, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
