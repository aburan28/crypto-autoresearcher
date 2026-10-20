"""Synthetic admission and exact archived-witness controls; zero solver calls."""
from __future__ import annotations

import copy
import hashlib
import json
import tarfile
import tempfile
import unittest
import sys
from pathlib import Path
from unittest import mock

import check
import execute


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=execute.HERE)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.plan_path = self.base / "plan.json"
        self.plan_path.write_text("{}\n")
        manifest_rel = (execute.HERE / "input_manifest.json").relative_to(execute.ROOT).as_posix()
        self.plan = {"experiment_id": "EXP-SYNTHETIC",
                     "source_sha256": {manifest_rel: execute.sha(execute.HERE / "input_manifest.json")},
                     "trials": [{"id": "trial-1", "run_id": "run-1",
                                 "argv": ["python3", str(execute.HERE / "execute.py"), "--run-approved"],
                                 "check_argv": ["python3", str(execute.HERE / "check.py")]}]}

    def test_missing_plan_refuses_before_authority_or_output(self):
        with mock.patch.object(execute.execution, "load_plan", side_effect=execute.execution.ExecutionError("absent")), \
             mock.patch.object(execute.execution, "authorize") as auth:
            with self.assertRaises(execute.execution.ExecutionError):
                execute.admit(self.plan_path, "owner", 1)
            auth.assert_not_called()
        self.assertFalse((self.base / "diagnostic").exists())

    def test_forged_claim_refuses_before_side_effects(self):
        with mock.patch.object(execute.execution, "load_plan", return_value=self.plan), \
             mock.patch.object(execute, "manifest_bindings", return_value={"source_sha256": {}}), \
             mock.patch.object(execute.execution, "authorize", side_effect=execute.execution.ExecutionError("forged claim")):
            with self.assertRaisesRegex(execute.execution.ExecutionError, "forged claim"):
                execute.run_diagnostic(self.plan_path, "owner", 1, self.base, "trial-1")
        self.assertFalse((self.base / "diagnostic").exists())

    def test_worker_wrong_owner_refuses_before_solver(self):
        request = self.base / "request.json"
        def authorization(root, path, plan, owner, epoch):
            if owner != "authorized-owner":
                raise execute.execution.ExecutionError("wrong owner")
            return {"owner": owner, "epoch": epoch}
        with mock.patch.object(execute.execution, "load_plan", return_value=self.plan), \
             mock.patch.object(execute, "manifest_bindings", return_value={"source_sha256": {}}), \
             mock.patch.object(execute.execution, "authorize", side_effect=authorization), \
             mock.patch.dict("sys.modules", {"instrumented_backend": mock.Mock()}) as modules:
            with self.assertRaisesRegex(execute.execution.ExecutionError, "wrong owner"):
                execute.worker(self.plan_path, "wrong", 1, self.base, "trial-1",
                               "random-m2", request, self.base / "response.json",
                               self.base / "trace.jsonl")
            modules["instrumented_backend"].solve.assert_not_called()
        self.assertFalse(request.exists())

    def test_worker_stale_launch_refuses_before_solver(self):
        (self.base / "launch.json").write_text('{"started_at":"2000-01-01T00:00:00+00:00","supervisor_pid":1}\n')
        with mock.patch.object(execute.execution, "load_plan", return_value=self.plan), \
             mock.patch.object(execute, "manifest_bindings", return_value={"source_sha256": {}}), \
             mock.patch.object(execute.execution, "authorize", return_value={"owner": "owner", "epoch": 1}), \
             mock.patch.object(execute.execution, "run_root", return_value=self.base), \
             mock.patch.dict("sys.modules", {"instrumented_backend": mock.Mock()}) as modules:
            with self.assertRaisesRegex(execute.execution.ExecutionError, "stale"):
                execute.worker(self.plan_path, "owner", 1, self.base, "trial-1",
                               "random-m2", self.base / "request.json",
                               self.base / "response.json", self.base / "trace.jsonl")
            modules["instrumented_backend"].solve.assert_not_called()

    def test_mocked_worker_forwards_exact_bytes(self):
        cell = "random-m2"
        call = self.base / "diagnostic" / cell / "call"
        call.mkdir(parents=True)
        request = call.parent / "request.json"
        response, trace = call / "response.json", call / "phase.jsonl"
        request.write_bytes(execute.canonical(next(r for r in execute.fixed_requests() if r["cell"] == cell)))
        backend = mock.Mock()
        backend.solve.return_value = {"status": "ok"}
        with mock.patch.object(execute, "admit", return_value={"run_dir": str(self.base)}), \
             mock.patch.dict("sys.modules", {"instrumented_backend": backend}):
            self.assertEqual(execute.worker(self.plan_path, "owner", 1, self.base,
                                            "trial-1", cell, request, response, trace),
                             {"status": "ok"})
        backend.solve.assert_called_once_with(request, response, trace)

    def test_manifest_source_mismatch(self):
        if not (execute.HERE / "input_manifest.json").exists():
            self.skipTest("manifest generated after source freeze")
        original = execute.sha
        def corrupt(path):
            if Path(path).name == "monitor.py":
                return "0" * 64
            return original(path)
        with mock.patch.object(execute, "sha", side_effect=corrupt):
            with self.assertRaisesRegex(execute.execution.ExecutionError, "hash changed"):
                execute.manifest_bindings()

    def test_synthetic_monitor_fault_retains_trace_and_raw(self):
        sys.path.insert(0, str(execute.MONITOR_DIR))
        import monitor
        def fault(_child):
            raise monitor.MonitorFault("unreadable_live_root", "synthetic_control")
        output = self.base / "monitor-null"
        record = monitor.supervise([sys.executable, "-c", "import time; time.sleep(2)"],
                                   output, seconds=5, rss_cap_bytes=execute.RSS_CAP,
                                   scratch_cap_bytes=execute.SCRATCH_CAP, probe=fault)
        self.assertEqual(record["stop"], "infrastructure_monitor_error")
        self.assertEqual(record["fault"]["code"], "unreadable_live_root")
        self.assertTrue(record["trace"]["valid"])
        self.assertTrue((output / "phase.jsonl").is_file())
        self.assertTrue((output / "stdout.raw").is_file())
        self.assertTrue((output / "stderr.raw").is_file())


class CheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.systems = {r["cell"]: r for r in execute.fixed_requests()}
        cls.witnesses = check.archived_witnesses()

    def witness(self, cell="random-m2"):
        return copy.deepcopy(self.systems[cell]), copy.deepcopy(self.witnesses[cell])

    def test_all_archived_witnesses_exact(self):
        for cell in execute.CELLS:
            with self.subTest(cell=cell):
                s, w = self.witness(cell)
                result = check.verify_selected(s, {"variables": w["root"]}, w["selected"])
                self.assertEqual(result["status"], "checked_full_point_relation")
                self.assertEqual(len(result["selected"]), 2)

    def test_coordinate_sign_target_and_index_mutations(self):
        for mutation in ("coordinate", "sign", "target", "index"):
            s, w = self.witness()
            if mutation == "coordinate": w["selected"][0]["point"][1] += 1
            if mutation == "sign": w["selected"][1]["sign"] *= -1
            if mutation == "target": s["target_point"][1] = str((int(s["target_point"][1])+1) % int(s["p"]))
            if mutation == "index": w["selected"][0]["index"] = 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                check.verify_selected(s, {"variables": w["root"]}, w["selected"])

    def _trace(self, stop, source, sample=True, solver_status=None):
        events = [("launch", "start", {}),
                  *(([("resource", "sample", {"rss_bytes": None})]) if sample else []),
                  ("watchdog", "terminal", {"stop": stop})]
        rows = [{"schema": "icperf-prime63-phase-v1", "stream": "supervisor",
                 "sequence": i, "monotonic_ns": i+1, "source_sha256": source,
                 "phase": phase, "event": event, "fields": fields}
                for i, (phase, event, fields) in enumerate(events)]
        if solver_status is not None:
            rows.append({"schema": "icperf-prime63-phase-v1", "stream": "solver",
                         "sequence": 0, "monotonic_ns": len(rows)+1,
                         "source_sha256": "b"*64, "phase": "solver",
                         "event": "terminal", "fields": {"status": solver_status}})
        return b"".join((json.dumps(r, sort_keys=True)+"\n").encode() for r in rows)

    def fixture(self, response=True, stop="exited", status="ok"):
        source = "a"*64
        manifest = {"source_sha256": {
            "research/icperf_prime63_monitor_phase_20261018/monitor.py": source,
            "research/icperf_prime63_monitor_phase_20261018/instrumented_backend.py": "b"*64}}
        archived = {}
        rows = []
        for cell, kind, this_stop in [("monitor-null", "synthetic_null", "infrastructure_monitor_error"),
                                      ("random-m2", "positive", stop)]:
            base = cell+"/call/"
            trace = self._trace(this_stop, source, sample=cell != "monitor-null",
                                solver_status=status if cell != "monitor-null" and response else None)
            archived[base+"phase.jsonl"] = trace
            archived[base+"stdout.raw"] = b""
            archived[base+"stderr.raw"] = b""
            row = {"cell": cell, "kind": kind, "attempted": True, "stop": this_stop,
                   "trace": {"sha256": check.sha_bytes(trace)},
                   "stdout_sha256": check.sha_bytes(b""), "stderr_sha256": check.sha_bytes(b""),
                   "fault": {"code": "unreadable_live_root"} if cell == "monitor-null" else None,
                   "exit_code": 0}
            if cell != "monitor-null":
                fixed = self.systems[cell]
                request = execute.canonical(fixed)
                archived[cell+"/request.json"] = request
                row["request_sha256"] = check.sha_bytes(request)
                if response:
                    body = {"status": status, "roots": [{"variables": self.witnesses[cell]["root"]}],
                            "root_count": 1, "quotient_dimension": 1,
                            "variety_called": True, "seconds": 1.25}
                    if status == "certified_no_solution": body = {"status": status, "roots": []}
                    raw = (json.dumps(body)+"\n").encode()
                    archived[base+"response.json"] = raw
                    row["response_sha256"] = check.sha_bytes(raw)
                else:
                    row["response_sha256"] = None
            rows.append(row)
        for cell in ("coset-m2", "small_x-m2"):
            rows.append({"cell": cell, "kind": "positive", "attempted": False,
                         "reason": "total_wall_censored"})
        rows = [rows[0], rows[2], rows[1], rows[3]]
        return {"schema": "icperf-prime63-m2-diagnostic-raw-v1", "cells": rows}, archived, manifest

    def test_response_and_bounded_censor(self):
        r, a, m = self.fixture()
        self.assertEqual(check.verify_result(r, a, m, list(self.systems.values()), self.witnesses)["positive_verified"], 1)
        r, a, m = self.fixture(response=False, stop="timeout_censored")
        self.assertEqual(check.verify_result(r, a, m, list(self.systems.values()), self.witnesses)["positive_censored"], 1)

    def test_missing_response_without_censor_and_missing_raw(self):
        r, a, m = self.fixture(response=False)
        with self.assertRaisesRegex(ValueError, "missing response"):
            check.verify_result(r, a, m, list(self.systems.values()), self.witnesses)
        r, a, m = self.fixture()
        del a["random-m2/call/stderr.raw"]
        with self.assertRaisesRegex(ValueError, "missing required raw member"):
            check.verify_result(r, a, m, list(self.systems.values()), self.witnesses)

    def test_false_no_solution_and_source_mismatch(self):
        r, a, m = self.fixture(status="certified_no_solution")
        with self.assertRaisesRegex(ValueError, "contradicted"):
            check.verify_result(r, a, m, list(self.systems.values()), self.witnesses)
        r, a, m = self.fixture()
        m["source_sha256"]["research/icperf_prime63_monitor_phase_20261018/monitor.py"] = "c"*64
        with self.assertRaisesRegex(ValueError, "phase source"):
            check.verify_result(r, a, m, list(self.systems.values()), self.witnesses)

    def test_archive_missing_member(self):
        with tempfile.TemporaryDirectory(dir=execute.HERE) as directory:
            output = Path(directory)
            (output / "one.raw").write_bytes(b"one")
            (output / "two.raw").write_bytes(b"two")
            with tarfile.open(output / "raw.tar.gz", "w:gz") as archive:
                archive.add(output / "one.raw", arcname="one.raw")
            receipt = {"raw_tar_sha256": execute.sha(output / "raw.tar.gz"),
                       "raw_files": [{"path": name, "sha256": check.sha_bytes(value),
                                      "bytes": len(value)}
                                     for name, value in (("one.raw", b"one"), ("two.raw", b"two"))]}
            with self.assertRaisesRegex(ValueError, "coverage"):
                check.verify_archive(output, receipt)


if __name__ == "__main__":
    unittest.main()
