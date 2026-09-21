#!/usr/bin/env python3
"""Independent fixed offline source-conformance controls, TASK-20260911-a210d2.

No campaign launch or producer test/controller execution. Only the frozen
adapter is imported. Fixture authority is a local placeholder passed directly
to execute_trial; authorization preservation is checked by exact source/AST
comparison. resource.setrlimit alone is simulated for fixture subprocesses,
and its actual requested arguments are retained. This is not a memory guard
or platform-readiness test. Each named case is counted, including failures.
"""
from __future__ import annotations

import argparse
import ast
import base64
import ctypes
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

TASK = "TASK-20260911-a210d2"
PREFIX = "coordination/adapter-empty-artifacts/TASK-20260911-04819a/"
SNAPSHOT = "c5ab6cd7c2461ea527dbe02663294336f3b9765f"
BINDING = "2c16904721fe8a412eda44e01313883a40bb31cd"
BASELINE = "3bc7f516ec721beae236164cf4bd22118610edd1"
ARTIFACT = "nested/payload.bin"
MISSING = object()
MAX_CASES = 64
MAX_TOTAL = 128


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    with Path(path).open("x") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def pack(path):
    data = path.read_bytes()
    return {"sha256": digest(data), "bytes": len(data),
            "content_base64": base64.b64encode(data).decode()}


def bindings(repo):
    handoff = json.loads((repo / "ledger/handoffs/TASK-20260911-a210d2.yaml").read_text())["handoff"]
    rows = []
    for entry in handoff["source_bindings"]:
        path = entry["path"]
        commit = BINDING if path.endswith(("review-plan-final.yaml", "review-source-binding.json")) else SNAPSHOT
        live = digest((repo / path).read_bytes())
        archived = digest(git(repo, "show", commit + ":" + path))
        assert live == archived == entry["sha256"], path
        rows.append({**entry, "commit": commit, "live_and_committed_match": True})
    assert len(rows) == 19
    assert git(repo, "show", "-s", "--format=%P", SNAPSHOT).decode().strip() == "9473baa74a5ee1ace169a9d6fbf417e2fc79f57d"
    for commit in (SNAPSHOT, BINDING):
        git(repo, "merge-base", "--is-ancestor", commit, "HEAD")
    snapshot = json.loads((repo / PREFIX / "archives/TASK-20260911-7fd8e9/snapshot.json").read_text())
    expected = set(snapshot["source_path_sha256"]) | {PREFIX + "archives/TASK-20260911-7fd8e9/snapshot.json"}
    changed = set(git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", SNAPSHOT).decode().splitlines())
    assert expected == changed
    message = git(repo, "show", "-s", "--format=%B", SNAPSHOT).decode()
    assert all(x in message for x in snapshot["record_ids"])
    plan = json.loads((repo / PREFIX / "review-plan-final.yaml").read_text())["review_plan"]
    assert plan == handoff["review_plan"]
    return {"source_bindings": rows, "exact_snapshot_paths": sorted(changed), "snapshot_parent_and_message_match": True}


def source_preservation(repo):
    old_text = git(repo, "show", BASELINE + ":tools/experiment_execution.py").decode()
    new_text = git(repo, "show", SNAPSHOT + ":tools/experiment_execution.py").decode()
    old_nodes = {n.name: n for n in ast.parse(old_text).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    new_nodes = {n.name: n for n in ast.parse(new_text).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    changed = [n for n in old_nodes if ast.dump(old_nodes[n]) != ast.dump(new_nodes[n])]
    assert changed == ["load_plan", "execute_trial"], changed
    intact = [n for n in old_nodes if n not in changed]
    for name in intact:
        assert ast.get_source_segment(old_text, old_nodes[name]) == ast.get_source_segment(new_text, new_nodes[name]), name
    tests_old = ast.parse(git(repo, "show", BASELINE + ":tests/test_experiment_execution.py"))
    tests_new = ast.parse(git(repo, "show", SNAPSHOT + ":tests/test_experiment_execution.py"))
    def methods(tree):
        return {(c.name, m.name): ast.dump(m) for c in tree.body if isinstance(c, ast.ClassDef)
                for m in c.body if isinstance(m, ast.FunctionDef) and m.name.startswith("test_")}
    a, b = methods(tests_old), methods(tests_new)
    assert len(a) == 41 and len(b) == 47
    assert all(b[k] == v for k, v in a.items())
    return {"changed_functions": changed, "byte_identical_functions": intact,
            "original_methods_preserved": 41, "final_methods": 47,
            "new_methods": sorted(n for c, n in b.keys() - a.keys())}


def custody(repo):
    receipt = json.loads((repo / PREFIX / "check-receipt.json").read_text())
    files = {}
    for f in receipt["retained_files"]:
        content = base64.b64decode(f["content_base64"], validate=True)
        assert len(content) == f["bytes"] and digest(content) == f["sha256"], f["path"]
        key = (Path(f["directory"]).name, f["path"])
        assert key not in files
        files[key] = content
    results = []
    for i, attempt in enumerate(receipt["attempts"], 1):
        key = f"empty048-attempt{i}"
        events = [json.loads(line) for line in files[key, "case-events.jsonl"].splitlines()]
        controls = [{k: v for k, v in e.items() if k not in ("event", "monotonic_ns")}
                    for e in events if e["event"] == "control_result"]
        assert controls == attempt["suite"]["controls"]
        assert len(controls) == attempt["suite"]["expanded_controls"] == 93
        assert sum(e["event"] == "test_start" for e in events) == attempt["suite"]["tests_run"] == 47
        assert sum(e["event"] == "test_end" for e in events) == 47
        assert base64.b64decode(attempt["raw_stdout_base64"]) == files[key, "stdout"]
        assert base64.b64decode(attempt["raw_stderr_base64"]) == files[key, "stderr"]
        assert json.loads(files[key, "suite.json"]) == attempt["suite"]
        assert json.loads(files[key, "attempt.json"]) == attempt
        reservation = attempt["reservation"]
        assert all(digest(files[key, "source/" + p]) == h for p, h in reservation["source_sha256"].items())
        for kind in ("worker", "controller"):
            assert digest(files[key, kind + ".py"]) == reservation[kind + "_sha256"]
        assert reservation["prior_expanded_controls"] == 93 * (i - 1)
        assert attempt["peak_sampled_checker_rss_bytes"] == max(s["rss_bytes"] for s in attempt["samples"] if s["rss_bytes"] is not None)
        assert all(s["pid"] == attempt["checker_pid"] for s in attempt["samples"])
        assert attempt["checker_exit_code"] == (0 if i == 4 else 1)
        assert reservation["mocked_resource_setrlimit"] == (i >= 3)
        assert attempt["suite"]["mocked_resource_setrlimit"] == (i >= 3)
        fixture_rows = None
        retained_inner_files = None
        if (key, "fixture-observations.jsonl") in files:
            inner = [json.loads(line) for line in files[key, "fixture-observations.jsonl"].splitlines()]
            fixture_rows, retained_inner_files = len(inner), sum(len(x["files"]) for x in inner)
            for x in inner:
                for f in x["files"]:
                    if "content_base64" in f:
                        assert digest(base64.b64decode(f["content_base64"])) == f["sha256"]
        failed = len(controls) - sum(c["passed"] for c in controls)
        assert failed == len(attempt["suite"]["failures"]) + len(attempt["suite"]["errors"])
        results.append({"attempt": i, "controls": len(controls), "passed": sum(c["passed"] for c in controls),
                        "failed": failed, "test_methods": 47, "fixture_observation_rows": fixture_rows,
                        "inner_files": retained_inner_files, "exit": attempt["checker_exit_code"],
                        "simulated_setrlimit": i >= 3, "pid": attempt["checker_pid"],
                        "sampled_checker_rss_bytes": attempt["peak_sampled_checker_rss_bytes"]})
    assert [r["passed"] for r in results] == [72, 73, 92, 93]
    assert sum(r["controls"] for r in results) == receipt["expanded_controls"] == 372
    assert sum(r["passed"] for r in results) == receipt["passed_controls"] == 330
    assert sum(r["failed"] for r in results) == receipt["failed_controls"] == 42
    assert ("empty048-attempt1", "fixture-observations.jsonl") not in files
    limits = [json.loads(line) for line in files["empty048-attempt2", "limit-observations.jsonl"].splitlines()]
    assert len(limits) == 24
    assert all(x["outcome"] == "raised" and x["error_type"] == "ValueError" and x["message"] == "current limit exceeds maximum limit" for x in limits)
    first = files["empty048-attempt1", "source/tests/test_experiment_execution.py"].decode()
    second = files["empty048-attempt2", "source/tests/test_experiment_execution.py"].decode()
    third = files["empty048-attempt3", "source/tests/test_experiment_execution.py"].decode()
    fourth = files["empty048-attempt4", "source/tests/test_experiment_execution.py"].decode()
    a = '                self.write_plan_queue()\n                with self.assertRaises(execution.ExecutionError):\n                    execution.load_plan(self.root, self.path)'
    b = '                self.path.write_text(json.dumps(self.plan))\n                with self.assertRaises(execution.ExecutionError):\n                    execution.load_plan(self.root, self.path)'
    assert first.replace(a, b, 1) == second == third
    a = '                self.assertFalse(self.run_plan()["measurement_complete"])\n                receipt = execution.read_json(self.directory() / "execution-receipt.json")'
    b = '                if mode == "symlink":\n                    with self.assertRaisesRegex(execution.ExecutionError, "symlink not allowed"):\n                        self.run_plan()\n                else:\n                    self.assertFalse(self.run_plan()["measurement_complete"])\n                receipt = execution.read_json(self.directory() / "execution-receipt.json")'
    assert third.replace(a, b, 1) == fourth
    assert digest(fourth.encode()) == digest((repo / "tests/test_experiment_execution.py").read_bytes())
    return {"retained_outer_files": len(files), "all_present_hashes_verified": True,
            "attempts": results, "expanded": 372, "passed": 330, "failed": 42,
            "real_limit_failures_observed_attempt2": 24, "first_fixture_transcripts": "unavailable",
            "all_original_test_methods_unchanged": True, "both_fixture_corrections_exact": True,
            "hard_memory_guard_verified": False, "aggregate_descendant_resources_verified": False}


DRIVER = '''import json, os, pathlib, sys
mode, target, scenario = sys.argv[1:4]
p = pathlib.Path(target)
print(json.dumps({"mode": mode, "pid": os.getpid(), "pgid": os.getpgrp(), "scenario": scenario}), flush=True)
if mode == "check":
    print("independent fixed semantic checker invoked", file=sys.stderr, flush=True)
    sys.exit(7 if scenario == "checker_bad" else 0)
if scenario == "producer_failure":
    sys.exit(9)
(p / "manifest.yaml").write_text("offline_fixture: true\\n")
(p / "raw-result.json").write_text("{}")
f = p / "nested/payload.bin"
f.parent.mkdir()
if scenario == "directory":
    f.mkdir()
elif scenario == "symlink":
    f.symlink_to(p / "raw-result.json")
elif scenario != "allowed_missing":
    f.write_bytes(b"data" if scenario == "declared_nonempty" else b"")
if scenario == "missing_required":
    (p / "raw-result.json").unlink()
if scenario == "empty_other":
    (p / "manifest.yaml").write_bytes(b"")
'''


def fixture(ex, root, scenario="declared_empty"):
    root.mkdir()
    exp = root / "experiments/EXP-FIXTURE-aabbcc"
    exp.mkdir(parents=True)
    spec = exp / "specification.yaml"
    spec.write_text(json.dumps({"id": exp.name, "status": "approved", "frozen": True, "approved_by": "offline_fixture"}))
    (root / "fixture.py").write_text(DRIVER)
    trial = {"id": "offline_fixed_case", "run_id": "RUN-FIXTURE-aabbcc",
             "argv": [sys.executable, "-B", "-S", "fixture.py", "write", "{run_dir}", scenario],
             "check_argv": [sys.executable, "-B", "-S", "fixture.py", "check", "{run_dir}", scenario],
             "memory_mb": 256, "watchdog_seconds": 5, "watchdog_reason": "fixed offline fixture protection",
             "artifacts": ["manifest.yaml", "raw-result.json", ARTIFACT], "allow_empty_artifacts": [ARTIFACT]}
    plan = {"schema": ex.PLAN_SCHEMA, "experiment_id": exp.name, "task_id": TASK, "frozen": True,
            "approved_by": "offline_fixture", "specification": str(spec.relative_to(root)),
            "specification_sha256": digest(spec.read_bytes()), "queue": "fixture_queue.json",
            "source_sha256": {"fixture.py": digest((root / "fixture.py").read_bytes())}, "trials": [trial]}
    path = exp / "plan.json"
    return plan, trial, path


def cases():
    invalid = [None, "nested/payload.bin", {}, True, False, 0, [None], [True], [1], [{}], [[]], [""], [ARTIFACT, ARTIFACT], ["absent"]]
    result = [(f"allow_type_{i:02d}", "bad_allow", x) for i, x in enumerate(invalid)]
    unsafe = ["/tmp/outside", "../outside", "a/../b", "./payload", "a//b", "a/", "a\\b", "a\x00b", "a\nb", "a/./b"]
    result += [(f"path_{i:02d}", "bad_path", x) for i, x in enumerate(unsafe)]
    reserved = ["launch.json", "execution-receipt.json", "command.txt", "environment.json", "stdout.log", "stderr.log", "check.stdout.log", "check.stderr.log"]
    result += [(f"reserved_{i}", "bad_path", x) for i, x in enumerate(reserved)]
    result += [(f"artifact_type_{i}", "bad_artifacts", x) for i, x in enumerate([None, "manifest.yaml", ["manifest.yaml", "raw-result.json", {}], ["manifest.yaml", "raw-result.json", "raw-result.json"]])]
    result += [("parser_omitted", "good", MISSING), ("parser_explicit_empty", "good", []), ("parser_required_names", "good", ["manifest.yaml", "raw-result.json"])]
    result += [(name, "symlink_path", name) for name in ["leaf_dangling", "leaf_contained", "component_escape", "plan_symlink"]]
    scenarios = ["declared_empty", "declared_nonempty", "undeclared_empty", "explicit_empty_list", "allowed_missing", "checker_bad", "missing_required", "empty_other", "directory", "symlink", "producer_failure", "tamper_bytes", "tamper_delete", "tamper_receipt_hash", "tamper_plan_hash"]
    result += [(s, "execution", s) for s in scenarios]
    result += [("exact_subset_no_wildcard", "bad_allow", ["*"]), ("requested_limit_arguments", "limit", None),
               ("source_authorization_cleanup_preserved", "source", None), ("producer_custody", "custody", None),
               ("nineteen_bindings", "bindings", None), ("direct_safe_contained_path", "safe", None)]
    assert len(result) == 64, len(result)
    return result


def perform(ex, repo, attempt, index, kind, value):
    if kind == "source":
        return source_preservation(repo)
    if kind == "custody":
        return custody(repo)
    if kind == "bindings":
        return bindings(repo)
    if kind == "safe":
        root = attempt / f"case-{index:02d}"
        root.mkdir()
        assert ex.safe_path(root, "a/b.bin") == root / "a/b.bin"
        return {"contained_canonical_path_accepted": True}
    root = attempt / f"case-{index:02d}"
    plan, trial, path = fixture(ex, root, value if kind == "execution" else "declared_empty")
    if kind == "bad_allow":
        trial["allow_empty_artifacts"] = value
    elif kind == "bad_path":
        trial["artifacts"].append(value)
        trial["allow_empty_artifacts"] = [value]
    elif kind == "bad_artifacts":
        trial["artifacts"] = value
    elif kind == "good":
        if value is MISSING:
            trial.pop("allow_empty_artifacts")
        else:
            trial["allow_empty_artifacts"] = value
    path.write_text(json.dumps(plan))
    directory = ex.run_root(root, plan, trial)
    if kind == "symlink_path":
        directory.mkdir(parents=True)
        if value == "plan_symlink":
            alternate = root / "alias.json"
            alternate.symlink_to(path)
            path = alternate
        elif value == "component_escape":
            (directory / "nested").symlink_to(root, target_is_directory=True)
        else:
            (directory / "nested").mkdir()
            (directory / ARTIFACT).symlink_to(root / ("fixture.py" if value == "leaf_contained" else "absent"))
    if kind in ("bad_allow", "bad_path", "bad_artifacts", "symlink_path"):
        try:
            ex.load_plan(root, path)
        except ex.ExecutionError as error:
            assert not (directory / "launch.json").exists()
            return {"refused_as": "ExecutionError", "detail": str(error), "launch_absent": True}
        raise AssertionError("invalid input accepted")
    ex.load_plan(root, path)
    if kind == "good":
        assert not directory.exists()
        return {"plan_accepted_without_launch": True}
    if kind == "execution":
        if value == "undeclared_empty":
            trial.pop("allow_empty_artifacts")
        elif value == "explicit_empty_list":
            trial["allow_empty_artifacts"] = []
        path.write_text(json.dumps(plan))
        ex.load_plan(root, path)
    authority = {"commit": "offline_fixture_no_git", "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()}
    limit_log = root / "setrlimit-calls.jsonl"
    def simulated_setrlimit(which, requested):
        # Executes in the fixture child before exec. No production code edits.
        fd = os.open(limit_log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(fd, (json.dumps({"pid": os.getpid(), "resource": which, "requested": requested, "simulated": True}) + "\n").encode())
        finally:
            os.close(fd)
    with open(os.devnull, "rb") as lock, patch.object(resource, "setrlimit", side_effect=simulated_setrlimit):
        if kind == "limit":
            directory.mkdir(parents=True)
            state, code = ex.run_process([sys.executable, "-B", "-S", "-c", "print('limit-request-only')"], root, directory, "", trial, authority, lock.fileno())
            assert (state, code) == ("exited", 0)
        else:
            status = ex.execute_trial(root, path, plan, trial, authority, lock.fileno())
    requests = [json.loads(line) for line in limit_log.read_text().splitlines()]
    assert len(requests) == (1 if kind == "limit" or value == "producer_failure" else 2)
    assert all(r["resource"] == resource.RLIMIT_AS and r["requested"] == [256 * 1024 * 1024] * 2 for r in requests)
    if kind == "limit":
        return {"status": state, "returncode": code, "requests": requests, "hard_guard_verified": False}
    receipt_path = directory / "execution-receipt.json"
    before = receipt_path.read_bytes()
    receipt = json.loads(before)
    expected = "infrastructure_error" if value == "producer_failure" else "output_validated" if value in ("declared_empty", "declared_nonempty") or value.startswith("tamper_") else "invalid_output"
    assert status == receipt["status"] == expected, (value, status, receipt)
    assert receipt["returncode"] == (9 if value == "producer_failure" else 0)
    assert receipt["check_returncode"] == (None if value == "producer_failure" else 7 if value == "checker_bad" else 0)
    if value != "producer_failure":
        assert b"independent fixed semantic checker invoked" in (directory / "check.stderr.log").read_bytes()
    if expected == "output_validated":
        want = b"data" if value == "declared_nonempty" else b""
        assert receipt["artifact_sha256"][ARTIFACT] == digest(want)
        assert ex.trial_state(root, plan, trial, digest(path.read_bytes())) == "output_validated"
    if value == "symlink":
        try:
            ex.coverage(root, path)
        except ex.ExecutionError as error:
            assert "symlink" in str(error)
        else:
            raise AssertionError("coverage must refuse existing output symlink")
    if value == "tamper_bytes":
        (directory / ARTIFACT).write_bytes(b"changed")
    elif value == "tamper_delete":
        (directory / ARTIFACT).unlink()
    elif value == "tamper_receipt_hash":
        receipt["artifact_sha256"][ARTIFACT] = "0" * 64
        receipt_path.write_text(json.dumps(receipt))
    elif value == "tamper_plan_hash":
        path.write_text(path.read_text() + "\n")
    if value.startswith("tamper_"):
        assert ex.trial_state(root, plan, trial, digest(path.read_bytes())) == "needs_reconciliation"
        if value != "tamper_receipt_hash":
            assert receipt_path.read_bytes() == before
    return {"initial_status": status, "returncode": receipt["returncode"],
            "check_returncode": receipt["check_returncode"], "requests": requests,
            "initial_receipt_base64": base64.b64encode(before).decode(),
            "final_state": ex.trial_state(root, plan, trial, digest(path.read_bytes()))}


def worker(repo, attempt):
    spec = importlib.util.spec_from_file_location("independent_frozen_adapter", attempt / "adapter.py")
    ex = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ex)
    rows = []
    with (attempt / "case-events.jsonl").open("x") as journal:
        for index, (name, kind, value) in enumerate(cases()):
            started = utc()
            journal.write(json.dumps({"event": "case_start", "index": index, "name": name, "at": started}) + "\n")
            journal.flush()
            try:
                observation = perform(ex, repo, attempt, index, kind, value)
                row = {"index": index, "name": name, "passed": True, "observation": observation}
            except BaseException:
                error = traceback.format_exc()
                print(error, file=sys.stderr, flush=True)
                row = {"index": index, "name": name, "passed": False, "error": error}
            row.update(started_at=started, finished_at=utc())
            journal.write(json.dumps({"event": "case_result", **row}) + "\n")
            journal.flush()
            os.fsync(journal.fileno())
            rows.append(row)
            print(json.dumps({"case": name, "passed": row["passed"]}), flush=True)
    suite = {"task_id": TASK, "cases": rows, "expanded_controls": len(rows),
             "passed": sum(r["passed"] for r in rows), "failed": sum(not r["passed"] for r in rows),
             "scientific_runs": 0, "simulated_resource_setrlimit": True,
             "production_authorization_exercised": False, "hard_memory_guard_verified": False}
    write_json(attempt / "suite.json", suite)
    return int(suite["failed"] != 0)


def sampled_rss(pid):
    if sys.platform != "darwin":
        return None
    # Read only this owned checker PID's task info; no machine-wide enumeration.
    class TaskInfo(ctypes.Structure):
        _fields_ = [(str(i), ctypes.c_uint64) for i in range(6)] + [(str(i), ctypes.c_int32) for i in range(6, 18)]
    data = TaskInfo()
    lib = ctypes.CDLL("/usr/lib/libproc.dylib")
    lib.proc_pidinfo.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_int]
    size = lib.proc_pidinfo(pid, 4, 0, ctypes.byref(data), ctypes.sizeof(data))
    return getattr(data, "1") if size == ctypes.sizeof(data) else None


def supervise(repo, work, number):
    assert 1 <= number <= 2
    prior = []
    for n in range(1, number):
        attempt = json.loads((work / f"attempt-{n}/attempt.json").read_text())
        prior.append(attempt["expanded_controls_reserved"])
    assert sum(prior) + MAX_CASES <= MAX_TOTAL
    work.mkdir(parents=True, exist_ok=True)
    directory = work / f"attempt-{number}"
    directory.mkdir()
    (directory / "checks.py").write_bytes(Path(__file__).read_bytes())
    (directory / "adapter.py").write_bytes(git(repo, "show", SNAPSHOT + ":tools/experiment_execution.py"))
    argv = [sys.executable, "-B", str(directory / "checks.py"), "--repo", str(repo), "--worker", str(directory)]
    write_json(directory / "reservation.json", {"task_id": TASK, "at": utc(), "argv": argv,
               "source_sha256": {"checks.py": digest((directory / "checks.py").read_bytes()),
                                  "adapter.py": digest((directory / "adapter.py").read_bytes())},
               "maximum_controls": MAX_CASES, "prior_reserved": sum(prior), "maximum_cumulative": MAX_TOTAL,
               "watchdog_seconds": 1800, "checker_sampled_rss_limit_bytes": 4 * 1024**3,
               "aggregate_or_hard_memory_guard": False, "scientific_runs": 0})
    started = utc()
    tick = time.monotonic()
    samples, stop = [], None
    errors = []
    process = None
    with (directory / "stdout.log").open("xb") as stdout, (directory / "stderr.log").open("xb") as stderr:
        try:
            process = subprocess.Popen(argv, cwd=directory, stdout=stdout, stderr=stderr,
                                       stdin=subprocess.DEVNULL, start_new_session=True,
                                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            write_json(directory / "launch.json", {"pid": process.pid, "pgid": process.pid, "argv": argv, "at": utc()})
            while process.poll() is None:
                rss = sampled_rss(process.pid)
                samples.append({"at": utc(), "pid": process.pid, "rss_bytes": rss, "scope": "checker_only"})
                if rss is not None and rss > 4 * 1024**3:
                    stop = "sampled_checker_memory"
                if time.monotonic() - tick > 1800:
                    stop = "suite_watchdog"
                if stop:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                    break
                time.sleep(0.05)
            process.wait()
        except BaseException:
            errors.append(traceback.format_exc())
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    suite = json.loads((directory / "suite.json").read_text()) if (directory / "suite.json").exists() else None
    retained = {}
    for p in sorted(directory.rglob("*")):
        name = p.relative_to(directory).as_posix()
        if p.is_symlink():
            retained[name] = {"symlink": os.readlink(p)}
        elif p.is_file():
            retained[name] = pack(p)
    record = {"task_id": TASK, "attempt": number, "argv": argv, "cwd": str(directory),
              "started_at": started, "finished_at": utc(), "wall_seconds": time.monotonic() - tick,
              "checker_pid": process.pid if process is not None else None,
              "checker_exit_code": process.returncode if process is not None else None,
              "expanded_controls_reserved": MAX_CASES, "suite": suite,
              "errors": errors, "watchdog_stop": stop, "samples": samples,
              "peak_sampled_checker_rss_bytes": max((s["rss_bytes"] for s in samples if s["rss_bytes"] is not None), default=None),
              "retained_files": retained}
    write_json(directory / "attempt.json", record)
    print(json.dumps({"attempt_directory": str(directory), "pid": record["checker_pid"],
                      "exit": record["checker_exit_code"], "passed": suite["passed"] if suite else None,
                      "failed": suite["failed"] if suite else None, "errors": errors, "stop": stop}))
    return int(suite is None or bool(suite["failed"]) or bool(errors) or stop is not None or record["checker_exit_code"] != 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--attempt", type=int)
    parser.add_argument("--worker", type=Path)
    args = parser.parse_args()
    if args.worker:
        return worker(args.repo.resolve(), args.worker.resolve())
    if args.work is None or args.attempt is None:
        parser.error("supervision requires --work and --attempt")
    return supervise(args.repo.resolve(), args.work.resolve(), args.attempt)


if __name__ == "__main__":
    raise SystemExit(main())
