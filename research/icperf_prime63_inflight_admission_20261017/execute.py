"""Prime63 panel launcher with supervisor-bound in-flight admission.

An approved future supervisor creates launch.json before invoking this driver.
The parent and each worker verify that exact record, plan, trial, run, claim,
and source closure before a task output or Sage worker is started.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / "research/icperf_prime63_pilot_launcher_20261017"
sys.path.insert(0, str(ROOT / "tools"))
import experiment_execution as execution  # noqa: E402
import newest_experiments  # noqa: E402
BACKEND = ROOT / "research/icperf_prime_wide_backend_retry_20261017/backend.py"
NATURAL = ROOT / "research/icperf_prime_475_target_systems_20261017/systems.json.gz"
SAGE = Path("/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage")
SCRATCH = Path("/Volumes/SSD990-2/crypto/.scratch/icperf_prime63_inflight_TASK-20261017-7fbab5")
RSS_CAP = 8 * 1024**3
SCRATCH_CAP = 8 * 1024**3
START_FREE = 16 * 1024**3
CONTINUE_FREE = 8 * 1024**3
CALL_SECONDS = 300
PANEL_SECONDS = 4 * 3600
MODEL_CAP = 64
POLL_SECONDS = 0.2


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as stream:
        return json.load(stream, parse_int=int, parse_float=Decimal)


def schedule():
    positive = read(OLD / "planted_public.json.gz")["systems"]
    archive = read(NATURAL)
    natural = archive["systems"]
    scan = read(ROOT / "research/icperf_prime_coset_896_20261017/scan.json")
    controls = read(ROOT / "research/icperf_prime_475_controls_20261017/controls.json")
    coset = next(a for a in scan["attempts"] if a["base_parameters"]["seed"] == scan["selected_seed"])
    bases = {"coset": (coset["points"], coset["base_parameters"])}
    bases.update({r["kind"]: (r["points"], r["parameters"]) for r in controls["controls"]})
    if len(positive) != 6 or len(natural) != 21:
        raise ValueError("panel cell count")
    rows = []
    for cell in positive:
        rows.append({"id": cell["cell"], "kind": "positive", "arm": cell["arm"],
                     "m": cell["m"], "request": cell})
    for cell in natural:
        encoder = "quadratic_lift" if cell["arm"] == "coset" else "direct"
        encoded = cell["encodings"][encoder]
        rows.append({"id": f"natural-{cell['arm']}-m{cell['m']}", "kind": "natural",
                     "arm": cell["arm"], "m": cell["m"],
                     "request": {"p": str(archive["curve"]["p"]),
                                 "curve": archive["curve"], "arm": cell["arm"], "m": cell["m"],
                                 "base_points": [[str(v) for v in point] for point in bases[cell["arm"]][0]],
                                 "base_parameters": bases[cell["arm"]][1],
                                 "variables": encoded["variables"],
                                 "equations": encoded["equations"],
                                 "target_point": [str(v) for v in cell["target_point"]],
                                 "encoder": encoder}})
    expected = {(arm, m) for arm in ("coset", "random", "small_x") for m in range(2, 9)}
    assert {(r["arm"], r["m"]) for r in rows if r["kind"] == "natural"} == expected
    assert len(rows) == 27
    return rows


def standard_monomial_count(gb, ring, cap=MODEL_CAP):
    """Count standard monomials of the leading ideal, stopping at cap+1.

    A finite quotient has exactly this many algebraic solutions with
    multiplicity.  Infinite quotients also exceed cap, eventually.  Thus a
    count <= cap is a sound pre-variety upper bound on distinct roots.
    """
    if any(f == ring.one() for f in gb):
        return 0, False
    leading = []
    for f in gb:
        if not f:
            continue
        exponent = f.lm().exponents()[0]
        try:
            iter(exponent)
        except TypeError:
            exponent = (exponent,)
        leading.append(tuple(int(x) for x in exponent))
    n = ring.ngens()
    zero = (0,) * n
    queue, seen = [zero], {zero}
    cursor = 0
    while cursor < len(queue):
        mono = queue[cursor]
        cursor += 1
        for i in range(n):
            nxt = list(mono)
            nxt[i] += 1
            nxt = tuple(nxt)
            if nxt in seen or any(all(a >= b for a, b in zip(nxt, lead)) for lead in leading):
                continue
            seen.add(nxt)
            if len(seen) > cap:
                return cap + 1, True
            queue.append(nxt)
    return len(seen), False


def worker(request):
    """Sage-only worker.  Guard is executed before any ideal.variety call."""
    spec = importlib.util.spec_from_file_location("pinned_backend", BACKEND)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    t0 = time.monotonic()
    ring, polynomials = module._polynomial_ring(request)
    ideal = ring.ideal(polynomials)
    gb = ideal.groebner_basis()
    count, capped = standard_monomial_count(gb, ring)
    if capped:
        return {"status": "model_cap_censored", "quotient_lower_bound": 65,
                "roots": [], "variety_called": False, "seconds": time.monotonic() - t0}
    if count == 0:
        return {"status": "certified_no_solution", "roots": [],
                "certificate": "Groebner basis contains 1", "variety_called": False,
                "seconds": time.monotonic() - t0}
    dimension = int(ideal.dimension())
    if dimension != 0:
        return {"status": "invalid", "reason": "standard_monomial_dimension_mismatch",
                "variety_called": False, "seconds": time.monotonic() - t0}
    roots = []
    for entry in ideal.variety():
        roots.append({"variables": {name: str(int(entry[ring.gen(i)]))
                                    for i, name in enumerate(request["variables"])}})
    roots.sort(key=lambda row: tuple(int(row["variables"][n]) for n in request["variables"]))
    return {"status": "ok", "roots": roots, "root_count": len(roots),
            "quotient_dimension": count, "variety_called": True,
            "seconds": time.monotonic() - t0}


def scratch_bytes(path):
    total = 0
    for item in path.rglob("*"):
        try:
            if item.is_file():
                total += item.stat().st_size
        except FileNotFoundError:
            continue
    return total


def terminate_tree(child):
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait(timeout=5)


def supervise(command, env, stdout_path, stderr_path, deadline,
              *, scratch=SCRATCH, poll=POLL_SECONDS):
    import psutil
    import resource

    start, started = time.monotonic(), utc()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak_rss = peak_scratch = 0
    min_free = shutil.disk_usage(scratch).free
    child = None
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        try:
            child = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                     env=env, start_new_session=True)
            root = psutil.Process(child.pid)  # failure falls into fail-closed cleanup
            reason = None
            while True:
                now = time.monotonic()
                if now >= deadline:
                    reason = "timeout_censored"
                    break
                try:
                    processes = [root] + root.children(recursive=True)
                    rss = 0
                    for proc in processes:
                        try:
                            rss += proc.memory_info().rss
                        except (psutil.NoSuchProcess, psutil.ZombieProcess):
                            if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                                raise
                    bytes_used = scratch_bytes(scratch)
                    free = shutil.disk_usage(scratch).free
                except (psutil.NoSuchProcess, psutil.ZombieProcess):
                    if child.poll() is None:
                        raise RuntimeError("rss_monitor_unavailable_for_live_child")
                    rss, bytes_used, free = 0, scratch_bytes(scratch), shutil.disk_usage(scratch).free
                peak_rss, peak_scratch = max(peak_rss, rss), max(peak_scratch, bytes_used)
                min_free = min(min_free, free)
                if rss > RSS_CAP:
                    reason = "memory_censored"
                elif bytes_used > SCRATCH_CAP or free < CONTINUE_FREE:
                    reason = "scratch_censored"
                if reason:
                    break
                if child.poll() is not None:
                    reason = "exited"
                    break
                time.sleep(min(poll, max(0, deadline - now)))
            if reason != "exited":
                terminate_tree(child)
            else:
                child.wait(timeout=2)
        except Exception as exc:
            reason = f"infrastructure_monitor_error:{type(exc).__name__}:{exc}"
            if child is not None:
                terminate_tree(child)
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"stop": reason, "command": command, "started_utc": started,
            "ended_utc": utc(), "wall_seconds": time.monotonic() - start,
            "cpu_user_seconds": usage_after.ru_utime - usage_before.ru_utime,
            "cpu_system_seconds": usage_after.ru_stime - usage_before.ru_stime,
            "peak_tree_rss_bytes_sampled": peak_rss,
            "peak_scratch_bytes_sampled": peak_scratch,
            "minimum_free_bytes_sampled": min_free,
            "poll_seconds": poll, "exit_code": None if child is None else child.returncode,
            "stdout_sha256": sha(stdout_path), "stderr_sha256": sha(stderr_path)}


def admit(plan_path: Path, owner: str, epoch: int, *, root: Path = ROOT,
          run_dir: Path | None = None, trial_id: str | None = None) -> dict:
    """Admit either pre-dispatch readiness or an exact supervisor in-flight run.

    An unbound ``needs_reconciliation`` selector row never grants authority.
    The only in-flight exception is the one already authorized by the standard
    supervisor and bound in its write-once launch.json. Both phases call the
    repository's exact load_plan and authorize functions.
    """
    if not owner or type(epoch) is not int or epoch < 1:
        raise execution.ExecutionError("owner and positive claim epoch required")
    root = root.resolve()
    path = Path(plan_path)
    if not path.is_absolute():
        path = root / path
    path = path.absolute()
    plan = execution.load_plan(root, path)
    relative = path.relative_to(root).as_posix()
    required = {
        "research/icperf_prime63_inflight_admission_20261017/execute.py",
        "research/icperf_prime63_inflight_admission_20261017/driver.py",
        "research/icperf_prime63_inflight_admission_20261017/check.py",
        "research/icperf_prime63_inflight_admission_20261017/input_manifest.json",
        "research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz",
        "research/icperf_prime63_pilot_launcher_20261017/planted_witnesses.json",
        "research/icperf_prime63_pilot_launcher_20261017/input_replay.json",
        "research/icperf_prime63_pilot_launcher_20261017/verify_run.py",
        "research/icperf_prime_wide_backend_retry_20261017/backend.py",
        "research/icperf_prime_475_target_systems_20261017/systems.json.gz",
    }
    if not required <= set(plan["source_sha256"]):
        raise execution.ExecutionError("trial plan lacks required launcher/input/checker source closure")
    admitted = execution.authorize(root, path, plan, owner, epoch)
    digest = sha(path)
    if run_dir is None:
        if trial_id is not None:
            raise execution.ExecutionError("trial ID without run directory")
        # Exact public selector core, including its approved-status filter.
        selected = newest_experiments.newest_runnable(repo=root,
                            experiment_ids={plan["experiment_id"]})
        selector = selected[0] if len(selected) == 1 else {}
        if (selector.get("id") != plan["experiment_id"]
                or selector.get("execution_state") != "ready"
                or selector.get("trial_plan") != relative
                or (selector.get("coverage") or {}).get("plan_sha256") != digest):
            raise execution.ExecutionError("ordinary experiment selector is not ready for this exact plan")
        return {"plan": plan, "plan_path": str(path), "plan_sha256": digest,
                "owner": owner, "epoch": epoch, "authorization": admitted,
                "selector_execution_state": "ready"}

    trial = next((t for t in plan["trials"] if t["id"] == trial_id), None)
    if len(plan["trials"]) != 1 or trial is None:
        raise execution.ExecutionError("expected exact one-trial plan and trial ID")
    expected_dir = execution.run_root(root, plan, trial)
    if Path(run_dir).resolve() != expected_dir.resolve() or expected_dir.is_symlink():
        raise execution.ExecutionError("run directory does not match frozen trial")
    if (expected_dir / "execution-receipt.json").exists():
        raise execution.ExecutionError("prior attempt exists; reconcile without rerun")
    launch_path = execution.safe_path(expected_dir, "launch.json")
    launch = execution.read_json(launch_path)
    launched = datetime.fromisoformat(str(launch.get("started_at", "")).replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - launched).total_seconds()
    if launched.tzinfo is None or not -5 <= age <= PANEL_SECONDS + CALL_SECONDS + 60:
        raise execution.ExecutionError("stale or future supervisor launch")
    pid = launch.get("supervisor_pid")
    if type(pid) is not int or pid <= 1:
        raise execution.ExecutionError("invalid supervisor PID")
    try:
        os.kill(pid, 0)
    except OSError as error:
        raise execution.ExecutionError("supervisor process is not live") from error
    argv = [a.replace("{run_dir}", str(expected_dir)) for a in trial["argv"]]
    check_argv = [a.replace("{run_dir}", str(expected_dir)) for a in trial["check_argv"]]
    def binds_plan(command: list[str]) -> bool:
        positions = [i for i, token in enumerate(command) if token == "--plan"]
        if len(positions) != 1 or positions[0] + 1 >= len(command):
            return False
        token = Path(command[positions[0] + 1])
        try:
            candidate = (execution.safe_path(root, token.as_posix())
                         if not token.is_absolute() else
                         execution.safe_path(root, token.relative_to(root).as_posix()))
        except (ValueError, execution.ExecutionError):
            return False
        return candidate == path
    if (launch.get("plan_sha256") != digest or launch.get("trial_id") != trial_id
            or launch.get("run_id") != trial["run_id"]
            or launch.get("authority") != admitted
            or launch.get("argv") != argv or launch.get("check_argv") != check_argv
            or not binds_plan(argv) or not binds_plan(check_argv)):
        raise execution.ExecutionError("supervisor launch does not bind exact plan/trial/authority/commands")
    progress = newest_experiments.execution_progress(path.parent, root)
    coverage = progress.get("coverage") or {}
    if (progress.get("execution_state") != "needs_reconciliation"
            or progress.get("trial_plan") != relative
            or coverage.get("plan_sha256") != digest
            or coverage.get("trials", {}).get(trial_id) != "needs_reconciliation"
            or coverage.get("required") != 1):
        raise execution.ExecutionError("in-flight coverage is not the exact supervisor-created run")
    return {"plan": plan, "plan_path": str(path), "plan_sha256": digest,
            "owner": owner, "epoch": epoch, "authorization": admitted,
            "selector_execution_state": "needs_reconciliation",
            "run_id": trial["run_id"], "trial_id": trial_id,
            "launch_sha256": sha(launch_path)}


def create_panel(plan_path: Path, owner: str, epoch: int, run_dir: Path, trial_id: str):
    """Future approved run; admission precedes every additional task output."""
    authority = admit(plan_path, owner, epoch, run_dir=run_dir, trial_id=trial_id)
    output = Path(run_dir) / "panel"
    import psutil  # fail before any call if monitor unavailable
    _ = psutil.Process(os.getpid())
    if sha(SAGE) != "b190e6cec5027031be752260d9b21a8e23f11a313cc620e5dcd1be28390643c1":
        raise ValueError("Sage binary hash changed")
    manifest = read(HERE / "input_manifest.json")
    for source, expected in manifest["source_sha256"].items():
        if sha(ROOT / source) != expected:
            raise ValueError(f"pinned source/input changed: {source}")
    for source, expected in manifest.get("launcher_sources_sha256", {}).items():
        if sha(HERE / source) != expected:
            raise ValueError(f"launcher source changed: {source}")
    if sha(OLD / "planted_public.json.gz") != manifest["public_sha256"]:
        raise ValueError("public positives changed")
    if sha(OLD / "planted_witnesses.json") != manifest["private_witness_sha256"]:
        raise ValueError("checker witnesses changed")
    if sha(OLD / "input_replay.json") != manifest["input_replay_sha256"] \
            or read(OLD / "input_replay.json").get("status") != "pass":
        raise ValueError("independent input replay failed or changed")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    sage_dir, tmp_dir = SCRATCH / "sage", SCRATCH / "tmp"
    for path in (sage_dir, tmp_dir):
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        probe = path / f"probe-{os.getpid()}"
        probe.write_text("ok")
        if probe.read_text() != "ok":
            raise OSError("scratch probe mismatch")
        probe.unlink()
    if shutil.disk_usage(SCRATCH).free < START_FREE:
        raise OSError("less than 16 GiB SSD scratch free")
    if scratch_bytes(SCRATCH) > SCRATCH_CAP:
        raise OSError("scratch already exceeds 8 GiB")
    output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env["DOT_SAGE"], env["TMPDIR"] = str(sage_dir), str(tmp_dir)
    panel_started, start = utc(), time.monotonic()
    rows = schedule()
    witnesses = {r["cell"]: r["root"] for r in read(OLD / "planted_witnesses.json")["witnesses"]}
    results = []
    fatal = None
    for row in rows:
        cell = row["id"]
        if fatal or time.monotonic() - start >= PANEL_SECONDS:
            results.append({"cell": cell, "attempted": False,
                            "reason": fatal or "panel_wall_censored"})
            continue
        cell_dir = output / cell
        cell_dir.mkdir()
        request = cell_dir / "request.json"
        response = cell_dir / "response.json"
        stdout, stderr = cell_dir / "stdout.log", cell_dir / "stderr.log"
        request.write_text(json.dumps(row["request"], sort_keys=True, separators=(",", ":")) + "\n")
        command = [str(SAGE), "-python", str(Path(__file__).resolve()),
                   "--worker-request", str(request), "--worker-output", str(response),
                   "--plan", authority["plan_path"], "--owner", owner,
                   "--epoch", str(epoch), "--run-dir", str(run_dir),
                   "--trial-id", trial_id]
        record = supervise(command, env, stdout, stderr,
                           min(start + PANEL_SECONDS, time.monotonic() + CALL_SECONDS))
        record.update({"cell": cell, "kind": row["kind"], "attempted": True,
                       "request_sha256": sha(request), "response_sha256": sha(response) if response.exists() else None})
        if record["stop"] != "exited" or record["exit_code"] != 0 or not response.exists():
            record["status"] = record["stop"] if record["stop"] != "exited" else "crashed"
        else:
            parsed = read(response)
            record["status"] = parsed.get("status", "invalid")
            if row["kind"] == "positive" and record["status"] in {"ok", "certified_no_solution"}:
                planted = witnesses[cell]
                if record["status"] != "ok" or planted not in [r.get("variables") for r in parsed.get("roots", [])]:
                    record["status"] = "invalid_positive_control"
        results.append(record)
        if record["status"] in {"invalid", "crashed", "invalid_positive_control"} \
                or record["status"].startswith("infrastructure"):
            fatal = "failed_independent_control_or_execution"
    coverage = []
    for path in sorted(output.rglob("*")):
        if path.is_file():
            coverage.append({"path": str(path.relative_to(output)), "sha256": sha(path), "bytes": path.stat().st_size})
    with tarfile.open(output / "raw.tar.gz", "w:gz") as tar:
        for entry in coverage:
            tar.add(output / entry["path"], arcname=entry["path"])
    receipt = {"schema": "icperf-prime63-panel-raw-v1", "task_id": authority["plan"]["task_id"],
               "experiment_id": authority["plan"]["experiment_id"],
               "plan_sha256": authority["plan_sha256"],
               "claim_owner": owner, "claim_epoch": epoch,
               "selector_execution_state": authority["selector_execution_state"],
               "run_id": authority["run_id"], "trial_id": trial_id,
               "launch_sha256": authority["launch_sha256"],
               "input_manifest_sha256": sha(HERE / "input_manifest.json"),
               "source_sha256": manifest["source_sha256"],
               "launcher_sources_sha256": manifest.get("launcher_sources_sha256", {}),
               "sage_binary_sha256": sha(SAGE),
               "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               "dirty_tree": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
               "started_utc": panel_started, "ended_utc": utc(),
               "wall_seconds": time.monotonic() - start,
               "cells": results, "attempted": sum(x["attempted"] for x in results),
               "unattempted": sum(not x["attempted"] for x in results),
               "verification_status": "pending_independent_verify_run",
               "raw_files": coverage, "raw_tar_sha256": sha(output / "raw.tar.gz")}
    (output / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-request", type=Path)
    parser.add_argument("--worker-output", type=Path)
    parser.add_argument("--run-approved", action="store_true")
    parser.add_argument("--pre-dispatch", action="store_true")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--owner")
    parser.add_argument("--epoch", type=int)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--trial-id")
    args = parser.parse_args()
    if args.worker_request and args.worker_output and not args.run_approved \
            and args.plan and args.owner and args.epoch and args.run_dir and args.trial_id:
        admit(args.plan, args.owner, args.epoch,
              run_dir=args.run_dir, trial_id=args.trial_id)
        request = read(args.worker_request)
        result = worker(request)
        args.worker_output.write_text(json.dumps(result, sort_keys=True) + "\n")
        print(json.dumps({"status": result["status"], "root_count": len(result.get("roots", []))}))
    elif args.run_approved and args.plan and args.owner and args.epoch and args.run_dir and args.trial_id \
            and not args.worker_request:
        print(json.dumps(create_panel(args.plan, args.owner, args.epoch,
                                      args.run_dir, args.trial_id), sort_keys=True))
    elif args.pre_dispatch and args.plan and args.owner and args.epoch \
            and not args.run_dir and not args.worker_request:
        print(json.dumps(admit(args.plan, args.owner, args.epoch), sort_keys=True))
    else:
        parser.error("choose a complete worker request or approved panel with --plan, --owner and --epoch")


if __name__ == "__main__":
    main()
