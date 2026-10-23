"""Write-once phased runner for an admitted graph-wide prepared relation arm.

Scientific mode requires a frozen Coordinator admission binding. Control mode
accepts at most 128 fixed public targets and cannot produce scientific records.
The repository's experiment runner remains the authority for dispatch.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
LEGACY = ROOT / "research/conductor_relation_yield_20261014"
sys.path.insert(0, str(LEGACY))
from execute_prepared import GIB, run_phase
from prepare_graph_input import ARMS, SCHEDULE


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def require_scientific_seed_mode(manifest):
    digests = [manifest.get(key) for key in
               ("base_root_sha256", "target_root_sha256", "verifier_root_sha256")]
    if (manifest.get("seed_mode") != "independent_verifier_root" or
            any(not isinstance(value, str) or len(value) != 64 or
                any(char not in "0123456789abcdef" for char in value)
                for value in digests) or len(set(digests)) != 3):
        raise ValueError("scientific graph input requires three distinct committed roots")


def bindings(args, manifest, head):
    values = {
        "source_commit": head,
        "input_sha256": sha(args.input),
        "manifest_sha256": sha(args.manifest),
        "wrapper_sha256": sha(__file__),
        "graph_preparer_sha256": sha(STUDY / "preparation/prepare_graph_input.py"),
        "graph_verifier_sha256": sha(STUDY / "preparation/verify_prepared_graph.py"),
        "collector_binary_sha256": sha(args.collector),
        "count_binary_sha256": sha(args.count_verifier),
        "collector_source_sha256": sha(LEGACY / "collector.rs"),
        "count_source_sha256": sha(LEGACY / "count_verify.cpp"),
        "rank_verifier_sha256": sha(LEGACY / "verify_collector.py"),
        "phase_runner_sha256": sha(LEGACY / "execute_prepared.py"),
        "graph_sha256": manifest["graph_sha256"],
        "commitment_sha256": manifest.get("commitment_sha256"),
        "stratum": manifest["stratum"], "index": manifest["index"],
        "arm": manifest["arm"], "stage": manifest["stage"],
        "target_count": manifest["target_count"],
    }
    if manifest["arm"] == "graph_transport":
        values.update({key: manifest[key] for key in
                       ("checkpoint_sha256", "checkpoint_manifest_sha256", "checkpoint_terminal_sha256")})
    if manifest.get("seed_mode") == "independent_verifier_root":
        values["verifier_root_sha256"] = manifest["verifier_root_sha256"]
    return values


def execute(args):
    args.input = args.input.resolve()
    args.manifest = args.manifest.resolve()
    args.collector = args.collector.resolve()
    args.count_verifier = args.count_verifier.resolve()
    manifest = json.loads(args.manifest.read_text())
    if manifest.get("schema") != "isogeny-relation-input/v1" or sha(args.input) != manifest.get("input_sha256"):
        raise ValueError("prepared graph input identity differs")
    stratum, stage, arm = manifest["stratum"], manifest["stage"], manifest["arm"]
    if stratum not in SCHEDULE or stage not in ("discovery", "confirmation") or arm not in ARMS:
        raise ValueError("unsupported graph arm schedule")
    if (arm in ("power_x", "graph_transport") and
            manifest["index"] % SCHEDULE[stratum]["power_stride"]):
        raise ValueError("arm outside check-vertex schedule")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
    if args.control:
        if manifest["target_count"] > 128:
            raise ValueError("implementation controls are capped at 128 targets")
    else:
        require_scientific_seed_mode(manifest)
        if (dirty or not manifest.get("schedule_conformant") or
                not manifest.get("commitment_sha256") or
                manifest["target_count"] != SCHEDULE[stratum][stage]):
            raise ValueError("scientific graph input requires clean frozen source and exact quota")
        admission = json.loads(args.admission.read_text())
        if (admission.get("schema") != "ectd.graph-arm-admission.v1" or
                admission.get("status") != "approved" or not admission.get("experiment_id") or
                not admission.get("approved_by")):
            raise ValueError("missing Coordinator-approved graph admission")
        if any(admission.get(key) != value for key, value in bindings(args, manifest, head).items()):
            raise ValueError("graph admission digest or schedule binding differs")
    if shutil.disk_usage(args.output.parent).free < GIB:
        raise OSError("less than 1 GiB free at output filesystem")
    out = args.output.resolve()
    out.mkdir(mode=0o700, parents=False, exist_ok=False)
    events = out / "events.jsonl"

    def event(record):
        with events.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    started = now()
    receipt = {
        "schema": "ectd.graph-arm-execution-attempt.v1",
        "mode": "implementation_control" if args.control else "scientific_trial",
        "status": "running", "started_utc": started, "source_commit": head,
        "git_status_porcelain": dirty, "input_sha256": sha(args.input),
        "manifest_sha256": sha(args.manifest),
        "admission_sha256": None if args.control else sha(args.admission),
        "bindings": bindings(args, manifest, head),
        "platform": platform.platform(), "python_version": platform.python_version(),
        "limits": {"wall_seconds_total": args.watchdog_seconds,
                   "sampled_rss_bytes": args.memory_gib * GIB}, "phases": [],
    }
    event({"kind": "attempt_started", "time": started, "receipt_header": receipt})
    deadline = time.monotonic() + args.watchdog_seconds
    try:
        phases = [
            ("input_verify", [sys.executable, str(STUDY / "preparation/verify_prepared_graph.py"),
                              "--prepared", str(args.input), "--manifest", str(args.manifest)]),
            ("collector", [str(args.collector), str(args.input)]),
            ("count", [str(args.count_verifier), str(args.input)]),
            ("rank_verify", [sys.executable, str(LEGACY / "verify_collector.py"),
                             str(args.input), str(out / "collector.stdout"),
                             "--gx", str(manifest["generator"][0]), "--gy", str(manifest["generator"][1]),
                             "--qx", str(manifest["Q"][0]), "--qy", str(manifest["Q"][1]),
                             "--count-output", str(out / "count.stdout")]),
        ]
        for name, command in phases:
            result = run_phase(name, command, out, deadline, args.memory_gib * GIB, event)
            receipt["phases"].append(result)
            if result["status"] != "completed":
                raise RuntimeError(f"{name}: {result['status']}")
            if not args.control and sys.platform == "darwin" and name in ("collector", "count") and result["rss_sample_count"] == 0:
                raise RuntimeError(f"{name}: memory watchdog lacked live RSS samples")
        prepared_check = json.loads((out / "input_verify.stdout").read_text())
        rank_check = json.loads((out / "rank_verify.stdout").read_text())
        if (prepared_check["status"] != "pass" or rank_check["status"] != "valid" or
                not rank_check["independent_ordered_count_match"]):
            raise ValueError("prepared input, rank, or independent count verification differs")
        if not args.control:
            prefixes = {min(manifest["target_count"], n) for n in (512, 2048, 8192, 32768)}
            if any(str(n) not in rank_check["rank_prefix"] for n in prefixes):
                raise ValueError("fixed rank prefix missing")
        receipt["status"] = "completed_control" if args.control else "completed_unreviewed"
    except Exception as error:
        receipt["status"] = "failed_infrastructure_or_validation"
        receipt["error"] = f"{type(error).__name__}: {error}"
        event({"kind": "attempt_error", "time": now(), "error": receipt["error"]})
    receipt["ended_utc"] = now()
    receipt["rusage_self_maxrss_raw"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    with (out / "receipt.json").open("x") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    event({"kind": "attempt_finished", "time": receipt["ended_utc"], "status": receipt["status"]})
    print(json.dumps({"status": receipt["status"], "output": str(out)}, sort_keys=True))
    return 0 if receipt["status"].startswith("completed") else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--collector", type=Path, required=True)
    parser.add_argument("--count-verifier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--watchdog-seconds", type=int, default=1800)
    parser.add_argument("--memory-gib", type=int, default=4)
    args = parser.parse_args()
    if not args.control and args.admission is None:
        parser.error("scientific mode requires --admission")
    if args.control and args.admission is not None:
        parser.error("control mode does not accept scientific admission")
    if args.watchdog_seconds < 1 or args.memory_gib < 1:
        parser.error("positive resource limits required")
    raise SystemExit(execute(args))


if __name__ == "__main__":
    main()
