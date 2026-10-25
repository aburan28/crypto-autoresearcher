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
import re
import resource
import shutil
import subprocess
import sys
import time

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
LEGACY = ROOT / "research/conductor_relation_yield_20261014"
STUDY_PLAN = STUDY / "graph_plan_20261023"
sys.path.insert(0, str(LEGACY))
from execute_prepared import GIB, run_phase
from prepare_graph_input import ARMS, SCHEDULE

SOLVE_TARGETS = {"P29": 32768, "P37": 32768}


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


def source_paths():
    return {
        "wrapper_sha256": Path(__file__),
        "graph_preparer_sha256": STUDY / "preparation/prepare_graph_input.py",
        "graph_verifier_sha256": STUDY / "preparation/verify_prepared_graph.py",
        "preparation_lift_sha256": LEGACY / "prepare_input.py",
        "collector_source_sha256": LEGACY / "collector.rs",
        "count_source_sha256": LEGACY / "count_verify.cpp",
        "rank_verifier_sha256": LEGACY / "verify_collector.py",
        "phase_runner_sha256": LEGACY / "execute_prepared.py",
        "group_replay_sha256": ROOT / "harness/toycurve.py",
        "graph_materializer_sha256": STUDY / "graph_input_schedule_20261023/materialize.py",
        "study_admission_sha256": STUDY_PLAN / "study_admission.py",
        "prepared_worker_sha256": STUDY_PLAN / "prepared_worker.py",
        "graph_trial_driver_sha256": STUDY / "graph_trial_adapter_20261023/trial_driver.py",
        "graph_worker_catalog_sha256": STUDY_PLAN / "prepare_worker_catalog.py",
        "graph_trial_checker_sha256": STUDY / "graph_trial_adapter_20261023/trial_check.py",
    }


def check_frozen_sources(root, paths, source_commit):
    """Bind source bytes to a frozen ancestor, allowing later run commits."""
    if not isinstance(source_commit, str) or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None:
        raise ValueError("scientific source commit must be a full SHA-1 commit id")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source_commit, "HEAD"],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        check=False)
    if ancestor.returncode != 0:
        raise ValueError("scientific source commit is not an ancestor of execution HEAD")
    for path in paths:
        relative = Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
        try:
            committed = subprocess.check_output(
                ["git", "show", f"{source_commit}:{relative}"], cwd=root,
                stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as error:
            raise ValueError(f"scientific source is not committed: {relative}") from error
        if hashlib.sha256(committed).hexdigest() != sha(path):
            raise ValueError(f"scientific source differs from HEAD: {relative}")


def bindings(args, manifest, source_commit):
    values = {
        "source_commit": source_commit,
        "input_sha256": sha(args.input),
        "manifest_sha256": sha(args.manifest),
        "collector_binary_sha256": sha(args.collector),
        "count_binary_sha256": sha(args.count_verifier),
        "graph_sha256": manifest["graph_sha256"],
        "commitment_sha256": manifest.get("commitment_sha256"),
        "stratum": manifest["stratum"], "index": manifest["index"],
        "arm": manifest["arm"], "stage": manifest["stage"],
        "target_count": manifest["target_count"],
    }
    values.update({name: sha(path) for name, path in source_paths().items()})
    if manifest["stage"] == "solve":
        values["solve_preparer_sha256"] = sha(
            STUDY / "preparation/prepare_graph_solve_input.py")
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
    if args.admission is not None:
        args.admission = args.admission.resolve()
    if args.binding is not None:
        args.binding = args.binding.resolve()
    manifest = json.loads(args.manifest.read_text())
    if manifest.get("schema") != "isogeny-relation-input/v1" or sha(args.input) != manifest.get("input_sha256"):
        raise ValueError("prepared graph input identity differs")
    stratum, stage, arm = manifest["stratum"], manifest["stage"], manifest["arm"]
    if stratum not in SCHEDULE or stage not in ("discovery", "confirmation", "solve") or arm not in ARMS:
        raise ValueError("unsupported graph arm schedule")
    if (arm in ("power_x", "graph_transport") and
            manifest["index"] % SCHEDULE[stratum]["power_stride"]):
        raise ValueError("arm outside check-vertex schedule")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
    source_commit = head
    study_bindings = {}
    if args.control:
        if manifest["target_count"] > 128:
            raise ValueError("implementation controls are capped at 128 targets")
    else:
        require_scientific_seed_mode(manifest)
        if (not manifest.get("schedule_conformant") or
                not manifest.get("commitment_sha256") or
                manifest["target_count"] != (SOLVE_TARGETS[stratum] if stage == "solve"
                                               else SCHEDULE[stratum][stage])):
            raise ValueError("scientific graph input requires a frozen commitment and exact quota")
        admission = json.loads(args.admission.read_text())
        if admission.get("schema") == "ectd.graph-study-admission.v1":
            if args.binding is None:
                raise ValueError("study admission requires a materializer binding")
            sys.path.insert(0, str(STUDY_PLAN))
            from study_admission import verify_study_admission
            source_commit, study_bindings = verify_study_admission(
                args.admission, args.binding, args, manifest,
                source_paths(), check_frozen_sources)
        elif admission.get("schema") == "ectd.graph-worker-admission.v1":
            if args.binding is None:
                raise ValueError("worker admission requires a public prepared binding")
            sys.path.insert(0, str(STUDY_PLAN))
            from prepared_worker import verify_worker_documents
            study_bindings = verify_worker_documents(
                args.admission, args.binding, args.input, args.manifest,
                args.collector, args.count_verifier, args.output)
            source_commit = admission["source_commit"]
        else:
            if args.binding is not None:
                raise ValueError("per-arm admission does not accept a study materializer binding")
            if (admission.get("schema") != "ectd.graph-arm-admission.v1" or
                    admission.get("status") != "approved" or not admission.get("experiment_id") or
                    not admission.get("approved_by")):
                raise ValueError("missing Coordinator-approved graph admission")
            source_commit = admission.get("source_commit")
            check_frozen_sources(ROOT, source_paths().values(), source_commit)
            if any(admission.get(key) != value for key, value in bindings(args, manifest, source_commit).items()):
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
        "status": "running", "started_utc": started, "source_commit": source_commit,
        "execution_head": head,
        "git_status_porcelain": dirty, "input_sha256": sha(args.input),
        "manifest_sha256": sha(args.manifest),
        "admission_sha256": None if args.control else sha(args.admission),
        "bindings": bindings(args, manifest, source_commit),
        "platform": platform.platform(), "python_version": platform.python_version(),
        "limits": {"wall_seconds_total": args.watchdog_seconds,
                   "sampled_rss_bytes": args.memory_gib * GIB}, "phases": [],
    }
    if study_bindings:
        receipt["study_admission"] = study_bindings
        receipt["bindings"].update(study_bindings)
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
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--watchdog-seconds", type=int, default=1800)
    parser.add_argument("--memory-gib", type=int, default=4)
    args = parser.parse_args()
    if not args.control and args.admission is None:
        parser.error("scientific mode requires --admission")
    if not args.control and args.binding is not None and args.admission is None:
        parser.error("--binding requires --admission")
    if args.control and args.binding is not None:
        parser.error("control mode does not accept a scientific binding")
    if args.control and args.admission is not None:
        parser.error("control mode does not accept scientific admission")
    if args.watchdog_seconds < 1 or args.memory_gib < 1:
        parser.error("positive resource limits required")
    raise SystemExit(execute(args))


if __name__ == "__main__":
    main()
