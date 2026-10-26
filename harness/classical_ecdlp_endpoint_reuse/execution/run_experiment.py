#!/usr/bin/env python3
"""Execute the frozen endpoint-reuse cells on an authorized isolated worker.

This is a producer adapter, not an isolation grader or scientific reviewer.
Clocks are retained with wall_valid=false. It never retries a native outcome.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import re
import signal
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cohort.public_inputs import load_inputs, write_cell
from protocol.seed_rules import public_seed, arm_order

ARMS = ["static_small", "static_full", "static_filled", "harvest", "harvest_disabled", "rho_reference"]
ROW_SCHEMA = "classical.ecdlp.endpoint-reuse.row.v1"
ROW_KINDS = {"fixture_validation", "setup", "initial_endpoint", "terminal", "lookup",
             "lookup_witness", "verified_solution", "harvest_proposal", "harvest_commit_ready", "target"}
PART_LIMIT = 61440
STOP = {"signal": None}


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def json_write(path, obj):
    with Path(path).open("x") as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write("\n")


def protocol_read(path):
    value = json.loads(Path(path).read_text())
    if value.get("schema") != "experiment.protocol/v1":
        raise ValueError("the official experiment.protocol/v1 record is required")
    frozen = value.get("freeze", {})
    body = {k: v for k, v in value.items() if k != "freeze"}
    actual = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    if frozen.get("status") != "frozen" or frozen.get("protocol_sha256") != actual or frozen.get("filed_before_affected_data") is not True:
        raise ValueError("protocol is draft, changed after freeze, or not filed before affected data")
    if set(a["id"] for a in value["arms"]) != set(ARMS):
        raise ValueError("protocol arm set differs from the six production arms")
    if value["execution"]["measurement_class"] != "measurement" or value["execution"]["backend"] not in ("isolab", "isolab-k8s", "taskq"):
        raise ValueError("this measurement requires its declared isolated backend")
    if value["execution"]["checkpoint"]["policy"] != "none" or value["execution"]["retries"]["max_attempts"] != 1:
        raise ValueError("this producer implements no restore and no outcome retry")
    return value, actual


def selected_text(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def host_facts():
    affinity = sorted(os.sched_getaffinity(0))
    cpu_model = None
    for line in (selected_text("/proc/cpuinfo") or "").splitlines():
        if line.startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    return {
        "recorded_at": utc(), "cpu_model": cpu_model,
        "kernel": platform.release(), "system": platform.system(), "machine": platform.machine(),
        "affinity_cpus": affinity,
        "cpu_max": selected_text("/sys/fs/cgroup/cpu.max"),
        "cpuset_effective": selected_text("/sys/fs/cgroup/cpuset.cpus.effective"),
        "memory_max": selected_text("/sys/fs/cgroup/memory.max"),
        "cpu_pressure": selected_text("/proc/pressure/cpu"),
        "memory_pressure": selected_text("/proc/pressure/memory"),
        "loadavg": selected_text("/proc/loadavg"),
        "cpu_stat": selected_text("/proc/stat").splitlines()[0] if selected_text("/proc/stat") else None,
        "governors": {str(c): selected_text(f"/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_governor") for c in affinity},
        "turbo_no_turbo": selected_text("/sys/devices/system/cpu/intel_pstate/no_turbo"),
        "pod_uid": os.getenv("POD_UID"), "node_name": os.getenv("NODE_NAME"),
        "job_id": os.getenv("ISOLAB_JOB_ID"), "pid": os.getpid(),
        "isolation_level": "unknown", "contended": None,
        "isolation_blockers": ["Generic worker placement is not an observed native L2 isolation grade.",
                               "Hypervisor neighbours, IRQ placement and frequency qualification are not established here."],
    }


def wait_child(argv, stdout_path, stderr_path, timeout_seconds, deadline=None):
    """One native invocation; obtain this child's rusage directly from wait4."""
    started = utc()
    mono = time.monotonic()
    reason = None
    observed_threads = []
    with Path(stdout_path).open("xb") as stdout, Path(stderr_path).open("xb") as stderr:
        child = subprocess.Popen(argv, stdout=stdout, stderr=stderr, start_new_session=True)
        terminate_at = None
        while True:
            pid, wait_status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                child.returncode = os.waitstatus_to_exitcode(wait_status)
                break
            text = selected_text(f"/proc/{child.pid}/status") or ""
            for line in text.splitlines():
                if line.startswith("Threads:"):
                    observed_threads.append(int(line.split()[1]))
                    break
            now = time.monotonic()
            if terminate_at is None:
                if STOP["signal"] is not None:
                    reason = "interrupted"
                elif now - mono >= timeout_seconds:
                    reason = "child_timeout"
                elif deadline is not None and now >= deadline:
                    reason = "global_timeout"
                if reason:
                    terminate_at = now
                    try:
                        os.killpg(child.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
            elif now - terminate_at >= 20:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            time.sleep(0.01)
    return {
        "started_at": started, "finished_at": utc(), "exitcode": child.returncode,
        "termination_reason": reason, "attempts": 1, "resumed": False,
        "rusage": {"user_seconds": usage.ru_utime, "system_seconds": usage.ru_stime,
                   "maxrss_raw": usage.ru_maxrss, "maxrss_raw_unit": "KiB" if sys.platform.startswith("linux") else "platform_specific",
                   "maxrss_bytes": usage.ru_maxrss * 1024 if sys.platform.startswith("linux") else None,
                   "minor_faults": usage.ru_minflt, "major_faults": usage.ru_majflt,
                   "voluntary_context_switches": usage.ru_nvcsw, "involuntary_context_switches": usage.ru_nivcsw,
                   "scope": "whole native child, including common validation, parsing, setup, all 64 targets, output and teardown"},
        "clock": {"wall_seconds": time.monotonic() - mono, "wall_valid": False,
                  "cpu_seconds": usage.ru_utime + usage.ru_stime,
                  "wall_scope": "parent observation interval including output-file opening and process launch/reap",
                  "reason": "No observed L2 isolation qualification is supplied by this producer."},
        "sampled_native_process_threads": {"min": min(observed_threads) if observed_threads else None,
                                           "max": max(observed_threads) if observed_threads else None,
                                           "sampling_interval_seconds": 0.01, "peak_guaranteed": False},
    }


def shape_check(path, cell_id, setting, arm, targets):
    seen, kinds, indices = set(), {}, []
    known = None
    rows = 0
    with Path(path).open() as stream:
        for number, line in enumerate(stream, 1):
            row = json.loads(line)
            rows += 1
            if (row.get("schema"), row.get("scope"), row.get("cell_id"), row.get("fixture"),
                row.get("replicate"), row.get("arm")) != (
                ROW_SCHEMA, "classical_ecdlp_endpoint_reuse", cell_id, setting["fixture_id"], int(setting["replicate"]), arm):
                raise ValueError(f"row identity mismatch at line {number}")
            kind = row.get("row_kind")
            if kind not in ROW_KINDS:
                raise ValueError(f"unknown native row kind at line {number}")
            kinds[kind] = kinds.get(kind, 0) + 1
            if kind == "setup":
                known = row["known_count"]
            elif kind == "initial_endpoint":
                indices.append(row["index"])
            elif kind == "target":
                key = row["target_id"], row["target_ordinal"]
                if key in seen:
                    raise ValueError("duplicate final target row")
                seen.add(key)
    expected = {(r["target_id"], int(r["target_ordinal"])) for r in targets}
    if kinds.get("fixture_validation") != 1 or kinds.get("setup") != 1 or seen != expected or indices != list(range(known if known is not None else -1)):
        raise ValueError("native stream is incomplete or has duplicate setup/initial/target rows")
    return {"raw_rows": rows, "row_kind_counts": kinds, "final_target_rows": len(seen),
            "output_shape_complete": True, "independent_equation_verification": False}


def split_stream(path, relative_root=None):
    """Retain the original and lossless line-complete parts for Git-sized archival."""
    path = Path(path)
    folder = path.with_name(path.name + ".parts")
    folder.mkdir()
    parts, current, ordinal = [], bytearray(), 0
    def flush():
        nonlocal ordinal, current
        name = folder / f"part-{ordinal:05d}.bin"
        name.write_bytes(current)
        parts.append({"path": name.relative_to(relative_root).as_posix() if relative_root else name.as_posix(), "bytes": len(current), "sha256": sha_file(name)})
        ordinal += 1
        current = bytearray()
    with path.open("rb") as stream:
        for line in stream:
            if len(line) > PART_LIMIT:
                return {"logical_bytes": path.stat().st_size, "logical_sha256": sha_file(path),
                        "parts": parts, "complete": False, "reason": "one producer line exceeds part size; retain original in artifact store"}
            if current and len(current) + len(line) > PART_LIMIT:
                flush()
            current.extend(line)
    if current or not parts:
        flush()
    return {"logical_bytes": path.stat().st_size, "logical_sha256": sha_file(path), "parts": parts, "complete": True}


def build_schedule(cohort):
    cells = sorted(cohort.settings)
    seed = public_seed(cohort.protocol_sha256, cohort.nonce_hex, "cohort", 0, "cell_order")
    random.Random(seed).shuffle(cells)
    schedule = []
    for cell in cells:
        setting = cohort.settings[cell]
        arms = arm_order(ARMS, cohort.protocol_sha256, cohort.nonce_hex, setting["fixture_id"], int(setting["replicate"]))
        for arm in arms:
            schedule.append((cell, arm))
    return schedule


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-root", required=True, type=Path)
    parser.add_argument("--inputs-manifest-sha256", required=True)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--binary-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    protocol, protocol_hash = protocol_read(args.protocol)
    if not re.fullmatch(r"[a-f0-9]{40}", args.source_revision) or sha_file(args.binary) != args.binary_sha256:
        parser.error("observed source/binary identity differs from the declared launch pins")
    for arm in protocol["arms"]:
        if arm["instrument"]["commit"] != args.source_revision or arm["instrument"]["binary_sha256"] != args.binary_sha256 or arm["instrument"]["threads"] != 1:
            parser.error("protocol instrument must pin the actual production binary/source and one compute worker")
    cohort = load_inputs(args.public_root, args.inputs_manifest_sha256)
    if cohort.protocol_sha256 != protocol_hash:
        parser.error("public inputs belong to another frozen protocol")
    schedule = build_schedule(cohort)
    if len(schedule) != 768:
        parser.error("the fixed 128-cell/six-arm schedule is incomplete")
    if args.plan_only:
        print(json.dumps({"schema": "classical.ecdlp.endpoint-reuse.execution-plan-preview/v1",
                          "measurement_started": False, "protocol_sha256": protocol_hash,
                          "inputs_manifest_sha256": args.inputs_manifest_sha256,
                          "commands": [{"cell_id": c, "arm": a} for c, a in schedule]}, indent=2))
        return 0
    required_env = ("ISOLAB_JOB_ID", "POD_UID", "NODE_NAME", "ISOLAB_RESULTS_URI")
    if any(not os.getenv(k) for k in required_env):
        parser.error("authorized isolated-worker provenance/environment is missing; local measurement is refused")
    if args.out.exists():
        parser.error("fresh output directory required")
    args.out.mkdir(parents=True)
    json_write(args.out / "protocol.json", protocol)
    json_write(args.out / "schedule.json", {"protocol_sha256": protocol_hash,
                                           "inputs_manifest_sha256": args.inputs_manifest_sha256,
                                           "cells_and_arms": [{"cell_id": c, "arm": a} for c, a in schedule]})
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda number, frame: STOP.__setitem__("signal", number))
    timeout = float(protocol["execution"]["placement"]["child_timeout_seconds"])
    global_timeout = float(protocol["execution"]["timeout_seconds"])
    deadline = time.monotonic() + global_timeout
    records = []
    slices = {}
    for ordinal, (cell, arm) in enumerate(schedule):
        setting = cohort.settings[cell]
        dest = args.out / "cells" / cell / arm
        dest.mkdir(parents=True)
        record = {"schema": "classical.ecdlp.endpoint-reuse.child-execution.v1",
                  "ordinal": ordinal, "cell_id": cell, "fixture_id": setting["fixture_id"],
                  "replicate": int(setting["replicate"]), "arm": arm, "solver_seed": int(setting["seed"]),
                  "source_revision": args.source_revision, "binary_sha256": sha_file(args.binary),
                  "protocol_sha256": protocol_hash, "inputs_manifest_sha256": args.inputs_manifest_sha256,
                  "retries": 0, "resumed": False, "attempts": 0,
                  "started_at": None, "finished_at": None}
        if STOP["signal"] is not None or time.monotonic() >= deadline:
            record.update({"status": "not_attempted", "reason": "interrupted" if STOP["signal"] else "global_timeout",
                           "attempts": 0, "argv": None, "started_at": None, "finished_at": None,
                           "exitcode": None, "rusage": None, "clock": {"wall_valid": False}})
        else:
            if cell not in slices:
                slices[cell] = write_cell(cohort, cell, args.out / "inputs" / cell)
            files = slices[cell]
            raw, stdout, stderr = dest / "raw.jsonl", dest / "stdout.log", dest / "stderr.log"
            argv = [str(args.binary.resolve()), "--run", files["fixtures.tsv"]["path"],
                    files["targets.tsv"]["path"], files["settings.tsv"]["path"], arm, str(raw.resolve())]
            record.update({"argv": argv, "input_slices": files, "host_before": host_facts(),
                           "raw_output": str(raw.relative_to(args.out)), "stdout": str(stdout.relative_to(args.out)),
                           "stderr": str(stderr.relative_to(args.out)), "timeout_seconds": timeout})
            try:
                record.update(wait_child(argv, stdout, stderr, timeout, deadline))
                if record["termination_reason"]:
                    record["status"] = "interrupted" if record["termination_reason"] == "interrupted" else "timed_out"
                elif record["exitcode"]:
                    record["status"] = "native_nonzero"
                else:
                    try:
                        record["shape_check"] = shape_check(raw, cell, setting, arm, cohort.targets[cell])
                        native_summary = json.loads(stdout.read_text())
                        if native_summary.get("cells") != 1 or native_summary.get("targets") != 64 or native_summary.get("rows") != record["shape_check"]["raw_rows"] or native_summary.get("clocks_emitted") is not False:
                            raise ValueError("native stdout summary differs from its complete clock-free raw stream")
                        record["native_stdout_summary"] = native_summary
                        record["status"] = "completed"
                    except (OSError, ValueError, KeyError, TypeError) as error:
                        record.update({"status": "invalid_output", "shape_error": str(error)})
                record["host_after"] = host_facts()
                record["streams"] = {}
                for path in (raw, stdout, stderr):
                    if path.exists():
                        record["streams"][str(path.relative_to(args.out))] = split_stream(path, args.out)
            except (OSError, ValueError, KeyError, TypeError) as error:
                record.update({"status": "infrastructure_error", "error": str(error), "exitcode": None,
                               "clock": {"wall_valid": False}, "finished_at": utc()})
        json_write(dest / "execution.json", record)
        records.append(record)
    attempted = sum(r.get("attempts", 0) > 0 for r in records)
    summary = {"schema": "classical.ecdlp.endpoint-reuse.execution-summary.v1", "planned": 768,
               "attempted": attempted, "completed": sum(r["status"] == "completed" for r in records),
               "status_counts": {s: sum(r["status"] == s for r in records) for s in sorted({r["status"] for r in records})},
               "protocol_sha256": protocol_hash, "inputs_manifest_sha256": args.inputs_manifest_sha256,
               "clock_qualification": "none; wall_valid is false on all producer records",
               "independent_public_equation_verification": False, "scientific_review": False}
    json_write(args.out / "summary.json", summary)
    manifest = {"schema": "classical.ecdlp.endpoint-reuse.raw-manifest.v1", "protocol_sha256": protocol_hash,
                "inputs_manifest_sha256": args.inputs_manifest_sha256, "source_revision": args.source_revision,
                "binary_sha256": sha_file(args.binary), "flow": summary,
                "files": [{"path": p.relative_to(args.out).as_posix(), "bytes": p.stat().st_size, "sha256": sha_file(p)}
                          for p in sorted(args.out.rglob("*")) if p.is_file()]}
    json_write(args.out / "algorithm-raw-manifest.json", manifest)
    print(json.dumps(summary))
    return 0 if summary["completed"] == 768 else 1


if __name__ == "__main__":
    raise SystemExit(main())
