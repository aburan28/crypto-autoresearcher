#!/usr/bin/env python3
"""Run only the frozen F2 panel after root release and the real S3 gate.

Import and --help perform no panel. Source/input identity and release failures
refuse the launch before its output directory exists.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import gzip
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
TASK = "TASK-20261026-e8fd72"


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")


def git(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=REPO, text=True).strip()


def verify_frozen_source(protocol):
    freeze = protocol["freeze"]
    if freeze["status"] != "frozen":
        raise RuntimeError("protocol is not frozen")
    canonical = {key: value for key, value in protocol.items() if key != "freeze"}
    actual_hash = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"),
                                            ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    if freeze["protocol_sha256"] != actual_hash or not freeze["filed_before_affected_data"]:
        raise RuntimeError("protocol hash/preregistration does not validate")
    instrument = protocol["arms"][0]["instrument"]
    source_commit = instrument["commit"]
    if not source_commit:
        raise RuntimeError("source commit is not pinned")
    interpreter = Path(sys.executable).resolve()
    observed_binary = digest(interpreter)
    if observed_binary != instrument["binary_sha256"]:
        raise RuntimeError("observed interpreter differs from pinned instrument binary")
    locked = []
    for lock_name in ("source-lock.json", "input-lock.json"):
        lock_path = HERE/lock_name
        relative = str(lock_path.relative_to(REPO))
        committed = subprocess.check_output(["git", "show", source_commit+":"+relative], cwd=REPO)
        if committed != lock_path.read_bytes():
            raise RuntimeError("lock file differs from pinned source commit: "+lock_name)
        for entry in json.loads(committed)["files"]:
            path = REPO/entry["path"]
            if path.is_symlink() or digest(path) != entry["sha256"]:
                raise RuntimeError("locked bytes changed: "+entry["path"])
            source_bytes = subprocess.check_output(
                ["git", "show", source_commit+":"+entry["path"]], cwd=REPO)
            if hashlib.sha256(source_bytes).hexdigest() != entry["sha256"]:
                raise RuntimeError("source commit does not bind locked bytes: "+entry["path"])
            locked.append(entry)
    analysis = protocol["analysis_plan"]["script"]
    if not analysis or digest(HERE/analysis["path"]) != analysis["sha256"]:
        raise RuntimeError("analysis is not pinned to the frozen script")
    return {
        "instrument_commit": source_commit, "runtime_head": git("rev-parse", "HEAD"),
        "tracked_tree_dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
        "interpreter": str(interpreter), "interpreter_sha256": observed_binary,
        "entrypoint_sha256": digest(__file__), "locked_files_checked": len(locked),
        "model": "native inherited Codex model; binding unprobed",
        "model_verified": False,
    }


def actual_gate(release, protocol):
    path = HERE.parents[1]/"runtime/checkpoint_gate.py"
    spec = importlib.util.spec_from_file_location("p256_pass2_checkpoint_gate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.require_gate(REPO, release, protocol, TASK)


def host_facts():
    cpu_model = None
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    memory_bytes = None
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            memory_bytes = int(line.split()[1])*1024
    return {
        "cpu_model": cpu_model, "logical_cpus": os.cpu_count(), "memory_bytes": memory_bytes,
        "kernel": platform.release(), "hypervisor": None, "isolation_tier_max": "L0",
        "blockers": ["shared host; no isolated-clock admission"],
        "python": sys.version, "platform": platform.platform(), "worker": platform.node(),
    }


class PanelWatchdog(TimeoutError):
    pass


def watchdog(_signum, _frame):
    raise PanelWatchdog("115-second panel watchdog; five seconds reserved for sealing")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--protocol", type=Path, default=HERE/"protocol.json")
    parser.add_argument("--release", type=Path, default=HERE/"phase-b-release.json")
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise RuntimeError("--out must be a fresh path inside this assigned track")
    protocol = json.loads(args.protocol.read_text())
    if args.seed != 2026102602:
        raise RuntimeError("seed differs from the prospective task card")
    source = verify_frozen_source(protocol)
    gate = actual_gate(args.release, protocol)
    # No observation data, output directory or mathematical module precedes
    # the validated source, explicit release and actual canonical checkpoint.
    out.mkdir(parents=True)
    write_json(out/"gate-receipt.json", gate)
    write_json(out/"source-observed.json", source)
    host = host_facts()
    write_json(out/"host.json", host)
    started = now()
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_SELF)
    command = [sys.executable, *sys.argv]
    write_json(out/"command.json", {"argv": command, "cwd": str(REPO), "started_at": started,
                                    "seed": args.seed, "task": TASK})
    # This protects the shared host; it is not a research budget or cost claim.
    old_limit = resource.getrlimit(resource.RLIMIT_AS)
    limit = 2*1024**3
    hard = old_limit[1]
    if hard != resource.RLIM_INFINITY:
        limit = min(limit, hard)
    resource.setrlimit(resource.RLIMIT_AS, (limit, hard))
    state = {"counts": {}, "oracle_counts": {}, "queries": [], "completed_queries": 0}
    result = None
    trace = None
    status, verification, error = "failed", "error", None
    prior_alarm = signal.signal(signal.SIGALRM, watchdog)
    signal.alarm(115)
    try:
        sys.path.insert(0, str(HERE))
        from failclosed import guarded_call
        from panel import run_panel
        result = guarded_call(lambda: run_panel(out, args.seed, state))
        status, verification = "succeeded", "verified"
    except PanelWatchdog as exception:
        status, verification, error = "timeout", "error", str(exception)
        trace = traceback.format_exc()
    except (KeyboardInterrupt, InterruptedError) as exception:
        status, verification, error = "interrupted", "error", str(exception)
        trace = traceback.format_exc()
    except (ImportError, FileNotFoundError) as exception:
        status, verification, error = "infra_error", "error", str(exception)
        trace = traceback.format_exc()
    except AssertionError as exception:
        status, verification, error = "failed", "refuted", str(exception)
        trace = traceback.format_exc()
    except BaseException as exception:
        status, verification, error = "failed", "error", str(exception)
        trace = traceback.format_exc()
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, prior_alarm)
    finished = now()
    after = resource.getrusage(resource.RUSAGE_SELF)
    elapsed = time.monotonic()-start
    if result is None:
        pending = state.pop("pending_full_fibre_rows", [])
        if pending:
            partial_path = out/"full-fibre"/"partial-at-stop.json.gz"
            partial_path.parent.mkdir(exist_ok=True)
            with partial_path.open("xb") as handle:
                handle.write(gzip.compress(
                    (json.dumps(pending, sort_keys=True, separators=(",", ":"))+"\n").encode(),
                    mtime=0))
            state["partial_fibre_chunk_at_stop"] = str(partial_path.relative_to(out))
        result = {"schema": "p256-pass2-f2-panel/v1", "task": TASK, "status": status,
                  "error": error, "traceback": trace, "partial_state": state,
                  "interpretation": "not a complete mathematical solution set; preserve all partial artifacts"}
        with (out/"failure.txt").open("x") as handle:
            handle.write(trace or error or "producer failed without error text\n")
    write_json(out/"summary.json", result)
    counts = state.get("counts", {})
    oracle_counts = state.get("oracle_counts", {})
    # These are actual implementation traversals of the same fixed panel,
    # not two statistically independent experiments or separate clock samples.
    rows = []
    for arm, native in (("producer", counts), ("oracle", oracle_counts)):
        rows.append({
            "run_id": "F2-pass2-"+out.name+"-"+arm, "arm": arm, "instance_id": "0",
            "seed": args.seed, "replicate": 0, "warmup": False, "status": status,
            "verification": verification,
            "classified_x": native.get("classified_x" if arm == "producer" else "coset_rows_replayed", 0),
            "completed_queries": state.get("completed_queries", 0),
            "solution_count": sum(query["counts"]["solutions"] if arm == "producer"
                                  else query["oracle_solution_count"]
                                  for query in state.get("queries", [])),
            "controls_passed": sum(control.get("owner") == arm for control in state.get("controls", [])),
            "pair_states": native.get("pair_table_states" if arm == "producer" else "oracle_pair_states", 0),
            "native_counters": native,
            "wall_seconds": None, "wall_valid": False,
            "cpu_user_seconds": None, "cpu_sys_seconds": None, "max_rss_bytes": None,
            "started_at": None, "finished_at": None, "worker": host["worker"],
            "attempts": 1, "resumed": 0,
            "exclusion_rule": "invalid_certificate" if verification == "refuted" else None,
            "error": error,
        })
    write_json(out/"package-resources.json", {
        "scope": "joint wrapper only, not per-arm observations or a cost comparison",
        "wall_seconds": elapsed, "wall_valid": False,
        "cpu_user_seconds": after.ru_utime-before.ru_utime,
        "cpu_sys_seconds": after.ru_stime-before.ru_stime,
        "max_rss_bytes": after.ru_maxrss*1024, "started_at": started, "finished_at": finished})
    with (out/"rows.jsonl").open("x") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":"), sort_keys=True)+"\n")
    files = []
    for path in sorted(out.rglob("*")):
        if path.is_file():
            files.append({"path": str(path.relative_to(out)), "bytes": path.stat().st_size,
                          "sha256": digest(path)})
    write_json(out/"manifest.json", {"schema": "p256-f2-raw-seal/v1", "files": files,
                                      "status": status, "task": TASK})
    print(json.dumps({"status": status, "classified_x": rows[0]["classified_x"],
                      "completed_queries": rows[0]["completed_queries"], "out": str(out),
                      "wall_valid": False}))
    return 0 if status == "succeeded" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as exception:
        print("F2 launch refused: "+str(exception), file=sys.stderr)
        raise SystemExit(2)
