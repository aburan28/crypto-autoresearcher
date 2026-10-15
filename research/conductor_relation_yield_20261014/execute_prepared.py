"""Bounded, write-once execution component for an admitted prepared input.

This is a process wrapper. Formal experiment approval and dispatch remain the
repository runner's responsibility; without an admission binding it only runs
with --control and labels all output as an implementation control.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import platform
import resource
import shutil
import subprocess
import sys
import time

import psutil

HERE = pathlib.Path(__file__).resolve().parent
GIB = 1024**3


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def run_phase(name, command, output_dir, deadline, memory_limit, event):
    stdout_path = output_dir / f"{name}.stdout"
    stderr_path = output_dir / f"{name}.stderr"
    started = utc_now()
    event({"kind": "phase_started", "phase": name, "command": command, "time": started})
    tick = time.monotonic()
    status = "running"
    peak_rss = 0
    rss_samples = 0
    last_cpu = None
    def address_space_limit():
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                   stdin=subprocess.DEVNULL, cwd=HERE,
                                   preexec_fn=address_space_limit if sys.platform == "linux" else None)
        try:
            observer = psutil.Process(process.pid)
        except (psutil.Error, PermissionError, OSError):
            observer = None
        if observer is None and sys.platform != "linux":
            process.kill()
            process.wait()
            raise RuntimeError("RSS watchdog unavailable for child process")
        while process.poll() is None:
            processes = [] if observer is None else [observer]
            try:
                if observer is not None:
                    processes += observer.children(recursive=True)
            except (psutil.Error, PermissionError, OSError):
                pass
            rss = 0
            cpu = 0.0
            for watched in processes:
                try:
                    rss += watched.memory_info().rss
                    rss_samples += 1
                    times = watched.cpu_times()
                    cpu += times.user + times.system
                except (psutil.Error, PermissionError, OSError):
                    pass
            peak_rss = max(peak_rss, rss)
            last_cpu = cpu
            if rss > memory_limit:
                status = "memory_watchdog"
                process.kill()
            elif time.monotonic() >= deadline:
                status = "wall_watchdog"
                process.kill()
            else:
                time.sleep(0.05)
        return_code = process.wait()
    if status == "running":
        status = "completed" if return_code == 0 else "process_error"
    child_maxrss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    child_maxrss_bytes = child_maxrss if sys.platform == "darwin" else child_maxrss * 1024
    if child_maxrss_bytes > memory_limit:
        status = "memory_limit_exceeded_after_exit"
    result = {
        "phase": name, "command": command, "started_utc": started,
        "ended_utc": utc_now(), "elapsed_seconds": time.monotonic() - tick,
        "return_code": return_code, "status": status,
        "peak_sampled_rss_bytes": peak_rss, "last_sampled_cpu_seconds": last_cpu,
        "rss_sample_count": rss_samples,
        "stdout_sha256": sha256(stdout_path), "stderr_sha256": sha256(stderr_path),
        "rusage_children_maxrss_raw": child_maxrss,
        "rusage_children_maxrss_bytes": child_maxrss_bytes,
    }
    event({"kind": "phase_finished", **result})
    return result


def execute(args):
    input_path = args.input.resolve()
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text())
    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True, text=True, check=True).stdout.strip()
    git_status = subprocess.run(["git", "status", "--porcelain"], cwd=HERE, capture_output=True, text=True, check=True).stdout
    if sha256(input_path) != manifest["input_sha256"]:
        raise ValueError("prepared input digest mismatch")
    if not args.control:
        admission = json.loads(args.admission.read_text())
        if admission.get("schema") != "arity3-admission/v1" or admission.get("status") != "approved":
            raise ValueError("missing approved admission binding")
        bindings = {
            "input_sha256": sha256(input_path), "manifest_sha256": sha256(manifest_path),
            "collector_sha256": sha256(args.collector), "count_verify_sha256": sha256(args.count_verifier),
            "collector_source_sha256": sha256(HERE / "collector.rs"),
            "count_source_sha256": sha256(HERE / "count_verify.cpp"),
            "verifier_sha256": sha256(HERE / "verify_collector.py"),
            "inference_sha256": sha256(HERE / "exact_interval.py"),
            "execute_sha256": sha256(HERE / "execute_prepared.py"),
            "preparer_sha256": sha256(HERE / "prepare_input.py"),
            "plan_sha256": sha256(HERE / "plan.json"),
        }
        if any(admission.get(key) != value for key, value in bindings.items()):
            raise ValueError("admission digest binding mismatch")
        if not manifest["protocol_conformant_target_count"] or manifest["target_count"] != 32768:
            raise ValueError("scientific target schedule mismatch")
    if shutil.disk_usage(args.output.parent).free < GIB:
        raise OSError("less than 1 GiB free at output filesystem")
    output_dir = args.output.resolve()
    output_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
    event_path = output_dir / "events.jsonl"

    def event(record):
        with event_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    started = utc_now()
    deadline = time.monotonic() + args.watchdog_seconds
    receipt = {
        "schema": "arity3-execution-attempt/v1", "started_utc": started,
        "mode": "implementation_control" if args.control else "scientific_trial",
        "input_sha256": sha256(input_path), "manifest_sha256": sha256(manifest_path),
        "collector_sha256": sha256(args.collector), "count_verifier_sha256": sha256(args.count_verifier),
        "collector_source_sha256": sha256(HERE / "collector.rs"),
        "count_source_sha256": sha256(HERE / "count_verify.cpp"),
        "verifier_sha256": sha256(HERE / "verify_collector.py"),
        "inference_sha256": sha256(HERE / "exact_interval.py"),
        "execute_sha256": sha256(HERE / "execute_prepared.py"),
        "preparer_sha256": sha256(HERE / "prepare_input.py"),
        "admission_sha256": None if args.control else sha256(args.admission),
        "git_head": git_head, "git_status_porcelain": git_status.splitlines(),
        "target_seed_sha256": manifest.get("target_seed_sha256"),
        "k_seed_sha256": manifest.get("k_seed_sha256"),
        "platform": platform.platform(), "python_version": platform.python_version(),
        "psutil_version": psutil.__version__,
        "limits": {"wall_seconds_total": args.watchdog_seconds, "sampled_rss_bytes": args.memory_gib * GIB,
                   "rss_poll_seconds": 0.05},
        "phases": [], "status": "running",
        "limits_note": "Linux RLIMIT_AS enforces address space; macOS requires readable child RSS and uses a sampled watchdog",
    }
    event({"kind": "attempt_started", "time": started, "receipt_header": receipt})
    try:
        phases = [
            ("collector", [str(args.collector.resolve()), str(input_path)]),
            ("count", [str(args.count_verifier.resolve()), str(input_path)]),
            ("verify", [sys.executable, str(HERE / "verify_collector.py"), str(input_path),
                        str(output_dir / "collector.stdout"), "--gx", str(manifest["generator"][0]),
                        "--gy", str(manifest["generator"][1]), "--qx", str(manifest["Q"][0]),
                        "--qy", str(manifest["Q"][1]), "--count-output", str(output_dir / "count.stdout")]),
        ]
        for name, command in phases:
            result = run_phase(name, command, output_dir, deadline, args.memory_gib * GIB, event)
            receipt["phases"].append(result)
            if not args.control and sys.platform == "darwin" and name in ("collector", "count") and result["rss_sample_count"] == 0:
                raise RuntimeError(f"{name}: no live RSS samples for memory watchdog")
            if result["status"] != "completed":
                raise RuntimeError(f"{name}: {result['status']}")
        verified = json.loads((output_dir / "verify.stdout").read_text())
        if verified["status"] != "valid" or not verified["independent_ordered_count_match"]:
            raise ValueError("independent verification did not pass")
        if not args.control:
            command = [sys.executable, str(HERE / "exact_interval.py"),
                       "--population", str(manifest["r"] - 1),
                       "--draws", str(manifest["target_count"]),
                       "--observed", str(verified["useful_targets"])]
            result = run_phase("interval", command, output_dir, deadline, args.memory_gib * GIB, event)
            receipt["phases"].append(result)
            if result["status"] != "completed":
                raise RuntimeError(f"interval: {result['status']}")
        receipt["status"] = "completed_control" if args.control else "completed_unreviewed"
    except Exception as error:
        receipt["status"] = "failed_infrastructure_or_validation"
        receipt["error"] = f"{type(error).__name__}: {error}"
        event({"kind": "attempt_error", "time": utc_now(), "error": receipt["error"]})
    receipt["ended_utc"] = utc_now()
    receipt["rusage_self_maxrss_raw"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    with (output_dir / "receipt.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    event({"kind": "attempt_finished", "time": receipt["ended_utc"], "status": receipt["status"]})
    print(json.dumps({"status": receipt["status"], "output": str(output_dir)}, sort_keys=True))
    return 0 if receipt["status"].startswith("completed") else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--collector", type=pathlib.Path, required=True)
    parser.add_argument("--count-verifier", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--admission", type=pathlib.Path)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--watchdog-seconds", type=int, default=1800)
    parser.add_argument("--memory-gib", type=int, default=4)
    args = parser.parse_args()
    if not args.control and args.admission is None:
        parser.error("scientific mode requires --admission")
    if args.watchdog_seconds < 1 or args.memory_gib < 1:
        parser.error("positive resource limits required")
    raise SystemExit(execute(args))


if __name__ == "__main__":
    main()
