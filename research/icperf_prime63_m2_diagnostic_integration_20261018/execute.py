"""Prospective admitted three-cell prime63 m=2 diagnostic launcher.

No experiment is approved by this source. Both parent and Sage worker call the
repository plan/dispatcher/claim authorization before any task output or solver.
The only in-flight exception is a supervisor-owned launch.json whose exact
plan, trial, commands and authority are independently rebound here.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import experiment_execution as execution  # noqa: E402
import newest_experiments  # noqa: E402

MONITOR_DIR = ROOT / "research/icperf_prime63_monitor_phase_20261018"
PUBLIC = ROOT / "research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz"
WITNESSES = ROOT / "research/icperf_prime63_pilot_launcher_20261017/planted_witnesses.json"
SAGE = Path("/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage")
SCRATCH = Path("/Volumes/SSD990-2/crypto/.scratch/icperf_prime63_m2_diagnostic")
CELLS = ("coset-m2", "random-m2", "small_x-m2")
CALL_SECONDS = 600
TOTAL_SECONDS = 2100
RSS_CAP = 8 * 1024**3
SCRATCH_CAP = 8 * 1024**3
INITIAL_FREE = 16 * 1024**3
MINIMUM_FREE = 8 * 1024**3
MODEL_CAP = 64
PINNED_UPSTREAM = {
    "research/icperf_prime63_monitor_phase_20261018/monitor.py": "e788c7f08f6d32e1ca910627559ff923ff01899a5769f1d74fbc309b06663c8a",
    "research/icperf_prime63_monitor_phase_20261018/phase.py": "f91b6725c83e4aec3340080ca14a091c66a4e9e12f29ac9042d54f853a3262d0",
    "research/icperf_prime63_monitor_phase_20261018/instrumented_backend.py": "ad90753f42135bc2aeb0c3af12acf85289ae46b3ecc85afec8babafad2179c82",
    "research/icperf_prime63_monitor_phase_20261018/diagnostic-design.md": "12d8c4efbedb6e3e58ebdc1c42059101f644f805da96d626716d8c3a08ba3efd",
    "research/icperf_prime63_inflight_admission_20261017/execute.py": "7823909bf40cd0cd5ed8e0e1c1e630a622aed7e95a9d35720456cb24ade886fa",
    "research/icperf_prime63_inflight_admission_20261017/check.py": "d4c5ecec423308d9d6dfb64f553765196b1f00254315ff8aa67d789d432ee651",
    "research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz": "0e86d86ff133870829c5432e58d08c0907e5e8940c149799b68299c65cfb7309",
    "research/icperf_prime63_pilot_launcher_20261017/planted_witnesses.json": "c9049b0c4fac1c83ca057d6da27e0c4a2cbfe52272aeab113beb419e068a2c0c",
    "research/icperf_prime_475_target_systems_20261017/systems.json.gz": "4bb75b65b843a4b7ce8c0b7d8521d80a95b958f061e0ddf516639296a15fb589",
    "research/icperf_prime_wide_backend_retry_20261017/backend.py": "30f9310997833836b0ca7a080a84b5b4b2fcc4231167045d9636596dbd46b7c5",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode()


def exact_json(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as stream:
        return json.load(stream, parse_int=int, parse_float=Decimal)


def fixed_requests() -> list[dict]:
    cells = exact_json(PUBLIC)["systems"]
    selected = [r for name in CELLS for r in cells if r["cell"] == name]
    if len(selected) != 3 or [r["cell"] for r in selected] != list(CELLS):
        raise ValueError("three fixed m2 positives missing or reordered")
    if [(r["arm"], r["m"], r["encoder"]) for r in selected] != [
            ("coset", 2, "quadratic_lift"), ("random", 2, "direct"),
            ("small_x", 2, "direct")]:
        raise ValueError("positive-cell identity changed")
    return selected


def manifest_bindings(root: Path = ROOT) -> dict:
    manifest = json.loads((root / HERE.relative_to(ROOT) / "input_manifest.json").read_text())
    if manifest.get("schema") != "icperf-prime63-m2-integration-input-v1":
        raise execution.ExecutionError("integration input manifest schema")
    if any(manifest.get("source_sha256", {}).get(p) != d for p, d in PINNED_UPSTREAM.items()):
        raise execution.ExecutionError("decision-pinned source binding mismatch")
    own = {(HERE / name).relative_to(ROOT).as_posix()
           for name in ("execute.py", "check.py", "test_integration.py")}
    if set(manifest["source_sha256"]) != set(PINNED_UPSTREAM) | own:
        raise execution.ExecutionError("integration source closure incomplete")
    for rel, digest in manifest["source_sha256"].items():
        if sha(root / rel) != digest:
            raise execution.ExecutionError(f"integration source/input hash changed: {rel}")
    return manifest


def _plan_path(root: Path, path: Path) -> Path:
    root = root.resolve()
    candidate = path if path.is_absolute() else root / path
    candidate = candidate.absolute()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise execution.ExecutionError("plan outside checkout") from exc
    return candidate


def _entrypoint_bound(plan: dict, root: Path) -> bool:
    trial = plan["trials"][0]
    def contains_exact(command, source: Path, mode: str | None):
        paths = []
        for token in command:
            if not isinstance(token, str):
                return False
            if token.endswith(".py"):
                paths.append(Path(token).resolve())
        return paths.count(source.resolve()) == 1 and (mode is None or command.count(mode) == 1)
    return (contains_exact(trial["argv"], HERE / "execute.py", "--run-approved")
            and contains_exact(trial["check_argv"], HERE / "check.py", None))


def admit(plan_path: Path, owner: str, epoch: int, *, root: Path = ROOT,
          run_dir: Path | None = None, trial_id: str | None = None) -> dict:
    """Read-only task admission; call before any task output or Sage creation."""
    if not owner or type(epoch) is not int or epoch < 1:
        raise execution.ExecutionError("owner and positive epoch required")
    root = root.resolve()
    path = _plan_path(root, Path(plan_path))
    plan = execution.load_plan(root, path)
    manifest = manifest_bindings(root)
    required = dict(manifest["source_sha256"])
    required[(HERE / "input_manifest.json").relative_to(ROOT).as_posix()] = sha(HERE / "input_manifest.json")
    if any(plan["source_sha256"].get(rel) != digest for rel, digest in required.items()):
        raise execution.ExecutionError("plan lacks exact m2 integration source closure")
    if len(plan["trials"]) != 1:
        raise execution.ExecutionError("diagnostic requires exactly one frozen trial")
    if not _entrypoint_bound(plan, root):
        raise execution.ExecutionError("plan is not bound to diagnostic launcher/checker")
    authority = execution.authorize(root, path, plan, owner, epoch)
    relative = path.relative_to(root).as_posix()
    digest = sha(path)
    if run_dir is None:
        if trial_id is not None:
            raise execution.ExecutionError("trial ID without run directory")
        selected = newest_experiments.newest_runnable(repo=root,
                                                      experiment_ids={plan["experiment_id"]})
        selector = selected[0] if len(selected) == 1 else {}
        if (selector.get("id") != plan["experiment_id"]
                or selector.get("execution_state") != "ready"
                or selector.get("trial_plan") != relative
                or (selector.get("coverage") or {}).get("plan_sha256") != digest):
            raise execution.ExecutionError("exact diagnostic ready selector absent")
        return {"plan": plan, "plan_path": str(path), "plan_sha256": digest,
                "authorization": authority, "selector_state": "ready"}
    trial = plan["trials"][0]
    if trial_id != trial["id"]:
        raise execution.ExecutionError("trial ID mismatch")
    expected = execution.run_root(root, plan, trial)
    if Path(run_dir).resolve() != expected.resolve() or expected.is_symlink():
        raise execution.ExecutionError("run directory mismatch")
    if (expected / "execution-receipt.json").exists():
        raise execution.ExecutionError("prior attempt exists")
    launch_path = execution.safe_path(expected, "launch.json")
    launch = execution.read_json(launch_path)
    launched = datetime.fromisoformat(str(launch.get("started_at", "")).replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - launched).total_seconds()
    if launched.tzinfo is None or not -5 <= age <= TOTAL_SECONDS + CALL_SECONDS + 60:
        raise execution.ExecutionError("stale supervisor launch")
    pid = launch.get("supervisor_pid")
    if type(pid) is not int or pid <= 1:
        raise execution.ExecutionError("invalid supervisor PID")
    try:
        os.kill(pid, 0)
    except OSError as exc:
        raise execution.ExecutionError("supervisor not live") from exc
    argv = [a.replace("{run_dir}", str(expected)) for a in trial["argv"]]
    check_argv = [a.replace("{run_dir}", str(expected)) for a in trial["check_argv"]]
    def binds_plan(command):
        positions = [i for i, token in enumerate(command) if token == "--plan"]
        if len(positions) != 1 or positions[0] + 1 >= len(command):
            return False
        try:
            token = Path(command[positions[0] + 1])
            return _plan_path(root, token) == path
        except (ValueError, execution.ExecutionError):
            return False
    if (launch.get("plan_sha256") != digest or launch.get("trial_id") != trial_id
            or launch.get("run_id") != trial["run_id"]
            or launch.get("authority") != authority
            or launch.get("argv") != argv or launch.get("check_argv") != check_argv
            or not binds_plan(argv) or not binds_plan(check_argv)):
        raise execution.ExecutionError("supervisor launch binding mismatch")
    progress = newest_experiments.execution_progress(path.parent, root)
    coverage = progress.get("coverage") or {}
    if (progress.get("execution_state") != "needs_reconciliation"
            or progress.get("trial_plan") != relative
            or coverage.get("plan_sha256") != digest
            or coverage.get("trials", {}).get(trial_id) != "needs_reconciliation"
            or coverage.get("required") != 1):
        raise execution.ExecutionError("in-flight selector/coverage mismatch")
    return {"plan": plan, "plan_path": str(path), "plan_sha256": digest,
            "authorization": authority, "selector_state": "needs_reconciliation",
            "run_id": trial["run_id"], "trial_id": trial_id,
            "run_dir": str(expected), "launch_sha256": sha(launch_path)}


def _worker_paths(authority: dict, cell: str, request: Path, response: Path, trace: Path):
    if cell not in CELLS:
        raise execution.ExecutionError("unknown m2 cell")
    base = Path(authority["run_dir"]) / "diagnostic" / cell
    expected_request = base / "request.json"
    expected_call = base / "call"
    if (request.resolve() != expected_request.resolve()
            or response.resolve() != (expected_call / "response.json").resolve()
            or trace.resolve() != (expected_call / "phase.jsonl").resolve()):
        raise execution.ExecutionError("worker paths outside frozen cell layout")


def worker(plan: Path, owner: str, epoch: int, run_dir: Path, trial_id: str,
           cell: str, request: Path, response: Path, trace: Path) -> dict:
    authority = admit(plan, owner, epoch, run_dir=run_dir, trial_id=trial_id)
    _worker_paths(authority, cell, request, response, trace)
    fixed = {r["cell"]: r for r in fixed_requests()}[cell]
    if request.read_bytes() != canonical(fixed):
        raise execution.ExecutionError("worker request differs from fixed archived cell")
    # This is the first possible scientific call. The separate phase worker's
    # self-written approved-launch JSON is not used as authority.
    sys.path.insert(0, str(MONITOR_DIR))
    import instrumented_backend
    return instrumented_backend.solve(request, response, trace)


def _scratch_bytes(path: Path) -> int:
    total = 0
    for item in path.rglob("*"):
        try:
            if item.is_file():
                total += item.stat().st_size
        except FileNotFoundError:
            continue
    return total


def run_diagnostic(plan: Path, owner: str, epoch: int, run_dir: Path, trial_id: str) -> dict:
    authority = admit(plan, owner, epoch, run_dir=run_dir, trial_id=trial_id)
    if sha(SAGE) != "b190e6cec5027031be752260d9b21a8e23f11a313cc620e5dcd1be28390643c1":
        raise execution.ExecutionError("pinned Sage executable changed")
    sys.path.insert(0, str(MONITOR_DIR))
    import monitor
    scratch = SCRATCH
    scratch.mkdir(parents=True, exist_ok=True)
    for item in (scratch / "sage", scratch / "tmp"):
        item.mkdir(mode=0o700, parents=True, exist_ok=True)
    if shutil.disk_usage(scratch).free < INITIAL_FREE or _scratch_bytes(scratch) > SCRATCH_CAP:
        raise OSError("scratch admission limit")
    output = Path(run_dir) / "diagnostic"
    output.mkdir(exist_ok=False)
    env = os.environ.copy()
    env["DOT_SAGE"], env["TMPDIR"] = str(scratch / "sage"), str(scratch / "tmp")
    started = datetime.now(timezone.utc).isoformat()
    deadline = time.monotonic() + TOTAL_SECONDS
    rows = []
    fatal = None
    def monitor_fault(child):
        raise monitor.MonitorFault("unreadable_live_root", "prospective_null_injected")
    null_dir = output / "monitor-null" / "call"
    null_record = monitor.supervise([sys.executable, "-c", "import time;time.sleep(2)"],
                                    null_dir, seconds=15, rss_cap_bytes=RSS_CAP,
                                    scratch_cap_bytes=SCRATCH_CAP,
                                    minimum_free_bytes=MINIMUM_FREE, probe=monitor_fault,
                                    env=env)
    rows.append({"cell": "monitor-null", "kind": "synthetic_null", "attempted": True,
                 **null_record})
    if null_record["stop"] != "infrastructure_monitor_error" or \
            (null_record["fault"] or {}).get("code") != "unreadable_live_root" or \
            not null_record["trace"]["valid"]:
        fatal = "monitor_null_control_failed"
    for fixed in fixed_requests():
        cell = fixed["cell"]
        if fatal or time.monotonic() >= deadline:
            rows.append({"cell": cell, "kind": "positive", "attempted": False,
                         "reason": fatal or "total_wall_censored"})
            continue
        cell_dir = output / cell
        cell_dir.mkdir()
        request = cell_dir / "request.json"
        request.write_bytes(canonical(fixed))
        call_dir = cell_dir / "call"
        response = call_dir / "response.json"
        trace = call_dir / "phase.jsonl"
        command = [str(SAGE), "-python", str(HERE / "execute.py"),
                   "--worker-request", str(request), "--worker-response", str(response),
                   "--worker-trace", str(trace), "--cell", cell,
                   "--plan", authority["plan_path"], "--owner", owner,
                   "--epoch", str(epoch), "--run-dir", str(run_dir),
                   "--trial-id", trial_id]
        seconds = min(CALL_SECONDS, max(0.001, deadline - time.monotonic()))
        record = monitor.supervise(command, call_dir, seconds=seconds,
                                   rss_cap_bytes=RSS_CAP, scratch_cap_bytes=SCRATCH_CAP,
                                   minimum_free_bytes=MINIMUM_FREE, env=env,
                                   poll_seconds=0.2)
        record.update({"cell": cell, "kind": "positive", "attempted": True,
                       "request_sha256": sha(request),
                       "response_sha256": sha(response) if response.exists() else None})
        rows.append(record)
        if record["stop"] == "infrastructure_monitor_error" or \
                record["stop"] in ("memory_censored", "scratch_censored") or \
                not record["trace"]["valid"] or \
                (record["stop"] == "exited" and record["exit_code"] != 0):
            fatal = "instrumentation_or_resource_stop"
    coverage = []
    for path in sorted(output.rglob("*")):
        if path.is_file():
            coverage.append({"path": path.relative_to(output).as_posix(),
                             "sha256": sha(path), "bytes": path.stat().st_size})
    with tarfile.open(output / "raw.tar.gz", "x:gz") as archive:
        for row in coverage:
            archive.add(output / row["path"], arcname=row["path"], recursive=False)
    receipt = {"schema": "icperf-prime63-m2-diagnostic-raw-v1",
               "experiment_id": authority["plan"]["experiment_id"],
               "run_id": authority["run_id"], "trial_id": trial_id,
               "plan_sha256": authority["plan_sha256"],
               "launch_sha256": authority["launch_sha256"],
               "source_manifest_sha256": sha(HERE / "input_manifest.json"),
               "claim_owner": owner, "claim_epoch": epoch,
               "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
               "cells": rows, "raw_files": coverage, "raw_tar_sha256": sha(output / "raw.tar.gz"),
               "verification_status": "pending_independent_checker"}
    with (output / "receipt.json").open("x") as stream:
        stream.write(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    return receipt


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--owner", required=True)
    p.add_argument("--epoch", required=True, type=int)
    p.add_argument("--run-dir", type=Path)
    p.add_argument("--trial-id")
    p.add_argument("--cell")
    p.add_argument("--worker-request", type=Path)
    p.add_argument("--worker-response", type=Path)
    p.add_argument("--worker-trace", type=Path)
    p.add_argument("--pre-dispatch", action="store_true")
    p.add_argument("--run-approved", action="store_true")
    a = p.parse_args(argv)
    if a.pre_dispatch and not a.run_dir and not a.trial_id and not a.worker_request and not a.run_approved:
        result = admit(a.plan, a.owner, a.epoch)
        print(json.dumps({"status": "admitted", "plan_sha256": result["plan_sha256"]}))
    elif a.run_approved and a.run_dir and a.trial_id and not a.worker_request and not a.pre_dispatch:
        result = run_diagnostic(a.plan, a.owner, a.epoch, a.run_dir, a.trial_id)
        print(json.dumps({"status": "recorded", "cells": len(result["cells"])}))
    elif a.worker_request and a.worker_response and a.worker_trace and a.cell \
            and a.run_dir and a.trial_id and not a.run_approved and not a.pre_dispatch:
        result = worker(a.plan, a.owner, a.epoch, a.run_dir, a.trial_id,
                        a.cell, a.worker_request, a.worker_response, a.worker_trace)
        print(json.dumps({"status": result["status"]}))
        if result["status"] not in ("ok", "certified_no_solution", "model_cap_censored"):
            raise SystemExit(2)
    else:
        p.error("exactly one complete pre-dispatch, run or worker mode required")


if __name__ == "__main__":
    main()
