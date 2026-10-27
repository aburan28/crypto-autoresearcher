#!/usr/bin/env python3
"""Produce counted endpoint-reuse records inside a source-pinned Modal VM.

The native algorithm, public input reader, randomization, wait4, stream splitting
and output-shape checks are the original source-A implementations. This module
owns Modal admission and provenance; it does not call the Isolab entry point or
alter its guards. Controller-supplied SDK identities are not guest attestations.
All clocks are retained with wall_valid=false, including failed executions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import signal
import sys
import time

STUDY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY_ROOT))
from execution import run_experiment as original

ARMS = original.ARMS
STOP = original.STOP
sha_file = original.sha_file
json_write = original.json_write
utc = original.utc
selected_text = original.selected_text
load_inputs = original.load_inputs
write_cell = original.write_cell
build_schedule = original.build_schedule
wait_child = original.wait_child
shape_check = original.shape_check
split_stream = original.split_stream

HEX64 = re.compile(r"[a-f0-9]{64}")
REVISION = re.compile(r"[a-f0-9]{40}")
CONTEXT_SCHEMA = "classical.ecdlp.endpoint-reuse.modal-provider-context/v1"
SOURCE_A = "fe01ccd832832488c58abeef17548b0a8db6035f"
REUSED_SHA256 = {
    "execution/run_experiment.py": "e2f03b383fa9a21e984b8648e3700db7834954e26f3f30e86b7addf2f5b2f48d",
    "cohort/public_inputs.py": "2577dd4568efd53e4b74150e5b8b0f0a5767d240d471f0110e0b1d178b750829",
    "protocol/seed_rules.py": "d1348c404cf9c7a90d7c70abf7f23797ac49c132b555f75f3065f9fc92421b4c",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    value = json.loads(Path(path).read_text(), object_pairs_hook=unique)
    require(isinstance(value, dict), "JSON object required")
    return value


def protocol_read(path):
    """Validate frozen Modal admission without weakening the original guard."""
    value = json_read(path)
    require(value.get("schema") == "experiment.protocol/v1", "official protocol required")
    body = {k: v for k, v in value.items() if k != "freeze"}
    actual = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    freeze = value.get("freeze", {})
    require(freeze.get("status") == "frozen" and freeze.get("protocol_sha256") == actual
            and freeze.get("filed_before_affected_data") is True,
            "protocol is draft, changed after freeze, or not filed before affected data")
    arms = [a["id"] for a in value["arms"]]
    require(len(arms) == 6 and set(arms) == set(ARMS), "exact six production arms required")
    execution = value["execution"]
    require(execution["measurement_class"] == "measurement" and execution["backend"] == "modal",
            "a prospective Modal measurement protocol is required")
    require(execution["checkpoint"]["policy"] == "none"
            and execution["retries"]["max_attempts"] == 1,
            "this producer implements no restore and no outcome retry")
    placement = execution["placement"]
    require(placement.get("runtime") == "vm" and placement.get("block_network") is True,
            "the protocol must declare the network-blocked VM runtime")
    for seconds in (execution["timeout_seconds"], placement["child_timeout_seconds"]):
        require(isinstance(seconds, (int, float)) and not isinstance(seconds, bool)
                and math.isfinite(seconds) and seconds > 0, "positive finite watchdog required")
    return value, actual


def provider_context_read(path, source_revision, binary_sha256, protocol_sha256,
                          inputs_manifest_sha256):
    value = json_read(path)
    require(value.get("schema") == CONTEXT_SCHEMA and value.get("provider") == "modal",
            "the actual Modal provider context is required")
    for key, prefix in (("app_id", "ap"), ("sandbox_id", "sb"), ("image_id", "im")):
        require(isinstance(value.get(key), str)
                and re.fullmatch(prefix + r"-[A-Za-z0-9]+", value[key]) is not None,
                "actual SDK object IDs are required; OCI/Kubernetes labels are not substitutes")
    require(value.get("runtime") == "vm" and value.get("block_network") is True,
            "network-blocked VM creation options required")
    require(value.get("requested_cpu") == [2, 2]
            and value.get("requested_memory_mib") == [12288, 12288],
            "the registered CPU/memory request and limit are required")
    for key, expected in (("source_revision", source_revision), ("source_a_revision", source_revision),
                          ("binary_sha256", binary_sha256), ("protocol_sha256", protocol_sha256),
                          ("inputs_manifest_sha256", inputs_manifest_sha256)):
        require(value.get(key) == expected, "provider context differs from launch pin: " + key)
    require(REVISION.fullmatch(value.get("source_b_revision", "")) is not None,
            "immutable Modal adapter source revision B required")
    require(value.get("adapter_revision") == value["source_b_revision"],
            "adapter revision must name the committed source-B closure")
    for key in ("build_info_sha256", "adapter_manifest_sha256"):
        require(HEX64.fullmatch(value.get(key, "")) is not None, "actual build/source SHA-256 required")
    return value


def source_path(root, relative):
    name = PurePosixPath(relative)
    require(not name.is_absolute() and ".." not in name.parts and str(name) == relative,
            "unsafe packaged code path")
    path = root / relative
    require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),
            "packaged source escapes image root")
    return path


def protocol_context_bindings(protocol, context):
    """Require the frozen prospective protocol to name this exact adapter/image."""
    route = protocol["extensions"]["modal_vm_route"]
    for key, observed_key in (("native_source_a", "source_a_revision"),
                              ("adapter_source_b", "source_b_revision"),
                              ("adapter_manifest_sha256", "adapter_manifest_sha256")):
        require(route.get(key) == context[observed_key], "frozen Modal route differs: " + key)
    require(route["build_info"]["sha256"] == context["build_info_sha256"],
            "frozen build-info differs from the actual image")
    for key in ("app_id", "image_id"):
        require(protocol["execution"]["placement"].get(key) == context[key],
                "frozen Modal placement differs: " + key)


def verify_build(context, binary, root=STUDY_ROOT):
    """Read back every packaged code hash, including this independent adapter."""
    root = Path(root).resolve()
    info_path = Path(context.get("build_info_path", "/opt/study/build-info.json"))
    require(info_path.resolve() == root / "build-info.json", "build-info must belong to this code image")
    require(sha_file(info_path) == context["build_info_sha256"], "build-info differs from launch pin")
    info = json_read(info_path)
    require(info.get("schema") == "classical.ecdlp.endpoint-reuse.image-build/v1"
            and info.get("source_revision") == context["source_revision"] == SOURCE_A,
            "original native source A identity required")
    require(info.get("confirmation_inputs_baked") is False
            and info.get("scientific_workload_executed") is False, "code-only build required")
    require(Path(info["binary"]).resolve() == Path(binary).resolve()
            and info["binary_sha256"] == context["binary_sha256"] == sha_file(binary),
            "observed executable differs from its build/source pins")
    files = info["source_and_public_input_sha256"]
    require(isinstance(files, dict), "packaged source hash map required")
    for relative, expected in files.items():
        require(isinstance(expected, str) and HEX64.fullmatch(expected) is not None,
                "invalid packaged source SHA-256")
        require(sha_file(source_path(root, relative)) == expected,
                "a code-image file differs from build-info: " + relative)
    for relative, expected in REUSED_SHA256.items():
        require(files.get(relative) == expected, "source-A helper bytes differ: " + relative)
    require(files.get("modal/engine.py") == sha_file(root / "modal/engine.py"),
            "this Modal adapter must be included in the source hash map")
    manifest_path = Path(context.get("adapter_manifest_path", "/opt/study/adapter-manifest.json"))
    require(manifest_path.resolve() == root / "adapter-manifest.json", "adapter manifest must belong to code image")
    require(sha_file(manifest_path) == context["adapter_manifest_sha256"]
            == files.get("adapter-manifest.json"), "adapter source manifest differs from launch pin")
    adapter = json_read(manifest_path)
    require(adapter.get("schema") == "classical.ecdlp.endpoint-reuse.modal-adapter-manifest/v1"
            and adapter.get("source_a_revision") == context["source_a_revision"]
            and adapter.get("source_b_revision") == context["source_b_revision"]
            and adapter.get("adapter_revision") == context["adapter_revision"],
            "adapter manifest source revisions differ from launch pins")
    adapter_files = adapter["files"]
    require(isinstance(adapter_files, dict) and "modal/engine.py" in adapter_files,
            "the committed adapter source closure must include this engine")
    for relative, expected in adapter_files.items():
        require(isinstance(relative, str) and relative.startswith("modal/")
                and expected == files.get(relative)
                and sha_file(source_path(root, relative)) == expected,
                "adapter file differs from committed source-B closure: " + relative)
    return info


def host_facts(context):
    """Observed guest facts and separately identified controller SDK provenance."""
    affinity = sorted(os.sched_getaffinity(0))
    cpu_model = None
    for line in (selected_text("/proc/cpuinfo") or "").splitlines():
        if line.startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    cpu_stat = selected_text("/proc/stat")
    return {
        "recorded_at": utc(), "cpu_model": cpu_model, "kernel": platform.release(),
        "system": platform.system(), "machine": platform.machine(), "affinity_cpus": affinity,
        "cpu_max": selected_text("/sys/fs/cgroup/cpu.max"),
        "cpuset_effective": selected_text("/sys/fs/cgroup/cpuset.cpus.effective"),
        "memory_max": selected_text("/sys/fs/cgroup/memory.max"),
        "cpu_pressure": selected_text("/proc/pressure/cpu"),
        "memory_pressure": selected_text("/proc/pressure/memory"),
        "loadavg": selected_text("/proc/loadavg"),
        "cpu_stat": cpu_stat.splitlines()[0] if cpu_stat else None,
        "governors": {str(c): selected_text(f"/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_governor")
                      for c in affinity},
        "turbo_no_turbo": selected_text("/sys/devices/system/cpu/intel_pstate/no_turbo"),
        "pid": os.getpid(), "uid": os.getuid(), "euid": os.geteuid(),
        "gid": os.getgid(), "egid": os.getegid(), "supplementary_groups": os.getgroups(),
        "backend": "modal", "runtime": context["runtime"],
        "controller_supplied_sdk_identity": {k: context[k] for k in ("app_id", "sandbox_id", "image_id")},
        "isolation_level": "unknown", "contended": None,
        "isolation_blockers": ["Modal VM identity is not an observed native L2 isolation grade.",
                               "Physical host exclusivity, neighbours, IRQ placement and frequency qualification are not established."],
    }


def execute(args, protocol, protocol_hash, cohort, context):
    """Execute the registered schedule; tests replace child I/O, never science."""
    schedule = build_schedule(cohort)
    require(len(schedule) == 768 and len(set(schedule)) == 768, "fixed 128-cell/six-arm schedule required")
    require(not args.out.exists(), "fresh output directory required")
    args.out.mkdir(parents=True)
    (args.out / "launch-protocol-bytes.json").write_bytes(args.protocol.read_bytes())
    if hasattr(args, "provider_context"):
        (args.out / "launch-provider-context-bytes.json").write_bytes(args.provider_context.read_bytes())
    json_write(args.out / "protocol.json", protocol)
    json_write(args.out / "provider-context.json", context)
    json_write(args.out / "schedule.json", {"protocol_sha256": protocol_hash,
               "inputs_manifest_sha256": args.inputs_manifest_sha256,
               "cells_and_arms": [{"cell_id": c, "arm": a} for c, a in schedule]})
    timeout = float(protocol["execution"]["placement"]["child_timeout_seconds"])
    deadline = time.monotonic() + float(protocol["execution"]["timeout_seconds"])
    records, slices = [], {}
    launch_stop_reason = None
    for ordinal, (cell, arm) in enumerate(schedule):
        setting = cohort.settings[cell]
        dest = args.out / "cells" / cell / arm
        dest.mkdir(parents=True)
        record = {"schema": "classical.ecdlp.endpoint-reuse.child-execution.v1",
                  "ordinal": ordinal, "cell_id": cell, "fixture_id": setting["fixture_id"],
                  "replicate": int(setting["replicate"]), "arm": arm, "solver_seed": int(setting["seed"]),
                  "source_revision": args.source_revision, "binary_sha256": args.binary_sha256,
                  "source_b_revision": context["source_b_revision"],
                  "adapter_revision": context["adapter_revision"],
                  "protocol_sha256": protocol_hash, "inputs_manifest_sha256": args.inputs_manifest_sha256,
                  "backend": "modal", "runtime": "vm",
                  "provider_identity": {k: context[k] for k in ("app_id", "sandbox_id", "image_id")},
                  "target_ids": [t["target_id"] for t in cohort.targets[cell]],
                  "retries": 0, "resumed": False, "attempts": 0,
                  "native_spawn_observation": "not_started",
                  "started_at": None, "finished_at": None}
        if launch_stop_reason is not None or STOP["signal"] is not None or time.monotonic() >= deadline:
            reason = launch_stop_reason or ("interrupted" if STOP["signal"] else "global_timeout")
            record.update({"status": "not_attempted", "reason": reason,
                           "argv": None, "exitcode": None, "rusage": None, "clock": {"wall_valid": False}})
        else:
            raw, stdout, stderr = dest / "raw.jsonl", dest / "stdout.log", dest / "stderr.log"
            try:
                if cell not in slices:
                    slices[cell] = write_cell(cohort, cell, args.out / "inputs" / cell)
                files = slices[cell]
                argv = [str(args.binary.resolve()), "--run", files["fixtures.tsv"]["path"],
                        files["targets.tsv"]["path"], files["settings.tsv"]["path"], arm, str(raw.resolve())]
                record.update({"argv": argv, "input_slices": files, "host_before": host_facts(context),
                               "raw_output": str(raw.relative_to(args.out)), "stdout": str(stdout.relative_to(args.out)),
                               "stderr": str(stderr.relative_to(args.out)), "timeout_seconds": timeout})
                # The unchanged helper confirms a spawn only when it returns.
                # If it raises after Popen, a zero-attempt claim would be false.
                record["native_spawn_observation"] = "unresolved"
                record["attempts"] = None
                record.update(wait_child(argv, stdout, stderr, timeout, deadline))
                record["native_spawn_observation"] = "wait4_reaped_child"
                require(record["clock"]["wall_valid"] is False, "clock cannot be qualified by this producer")
                if record["termination_reason"]:
                    record["status"] = "interrupted" if record["termination_reason"] == "interrupted" else "timed_out"
                elif record["exitcode"]:
                    record["status"] = "native_nonzero"
                else:
                    try:
                        record["shape_check"] = shape_check(raw, cell, setting, arm, cohort.targets[cell])
                        native_summary = json_read(stdout)
                        require(native_summary.get("cells") == 1 and native_summary.get("targets") == 64
                                and native_summary.get("rows") == record["shape_check"]["raw_rows"]
                                and native_summary.get("clocks_emitted") is False,
                                "native stdout summary differs from its complete clock-free raw stream")
                        record["native_stdout_summary"] = native_summary
                        record["status"] = "completed"
                    except (OSError, ValueError, KeyError, TypeError) as error:
                        record.update({"status": "invalid_output", "shape_error": str(error)})
            except (OSError, ValueError, KeyError, TypeError) as error:
                record.update({"status": "infrastructure_error", "error": str(error),
                               "clock": {"wall_valid": False}, "finished_at": utc()})
                record.setdefault("exitcode", None)
                if record["native_spawn_observation"] == "unresolved":
                    # The original helper does not expose a PID on exception.
                    # Do not overlap a possible live child or retry it.
                    launch_stop_reason = "unresolved_native_child"
            finally:
                record["host_after"] = host_facts(context)
                record["streams"] = {}
                for path in (raw, stdout, stderr):
                    if path.exists():
                        try:
                            record["streams"][str(path.relative_to(args.out))] = split_stream(path, args.out)
                        except (OSError, ValueError) as error:
                            record["streams"][str(path.relative_to(args.out))] = {
                                "complete": False, "reason": str(error), "original_retained": True}
        json_write(dest / "execution.json", record)
        records.append(record)
    summary = {"schema": "classical.ecdlp.endpoint-reuse.execution-summary.v1", "planned": 768,
               "attempted": sum(isinstance(r.get("attempts"), int) and r["attempts"] > 0 for r in records),
               "attempts_unresolved": sum(r.get("attempts") is None for r in records),
               "launch_stop_reason": launch_stop_reason,
               "completed": sum(r["status"] == "completed" for r in records),
               "status_counts": {s: sum(r["status"] == s for r in records) for s in sorted({r["status"] for r in records})},
               "protocol_sha256": protocol_hash, "inputs_manifest_sha256": args.inputs_manifest_sha256,
               "backend": "modal", "runtime": "vm",
               "clock_qualification": "none; wall_valid is false on all producer records",
               "independent_public_equation_verification": False, "scientific_review": False}
    json_write(args.out / "summary.json", summary)
    manifest = {"schema": "classical.ecdlp.endpoint-reuse.raw-manifest.v1", "protocol_sha256": protocol_hash,
                "inputs_manifest_sha256": args.inputs_manifest_sha256, "source_revision": args.source_revision,
                "binary_sha256": args.binary_sha256, "source_b_revision": context["source_b_revision"],
                "adapter_revision": context["adapter_revision"],
                "provider_context_sha256": sha_file(args.out / "provider-context.json"), "flow": summary,
                "files": [{"path": p.relative_to(args.out).as_posix(), "bytes": p.stat().st_size, "sha256": sha_file(p)}
                          for p in sorted(args.out.rglob("*")) if p.is_file()]}
    json_write(args.out / "algorithm-raw-manifest.json", manifest)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("public-root", "protocol", "binary", "out", "provider-context"):
        parser.add_argument("--" + name, required=True, type=Path)
    for name in ("inputs-manifest-sha256", "source-revision", "binary-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        protocol, protocol_hash = protocol_read(args.protocol)
        require(args.source_revision == SOURCE_A and HEX64.fullmatch(args.binary_sha256) is not None
                and sha_file(args.binary) == args.binary_sha256, "observed native identity differs from launch pins")
        for arm in protocol["arms"]:
            instrument = arm["instrument"]
            require(instrument["commit"] == args.source_revision
                    and instrument["binary_sha256"] == args.binary_sha256 and instrument["threads"] == 1,
                    "protocol must pin the production binary/source and one compute worker")
        context = provider_context_read(args.provider_context, args.source_revision, args.binary_sha256,
                                        protocol_hash, args.inputs_manifest_sha256)
        protocol_context_bindings(protocol, context)
        verify_build(context, args.binary)
        cohort = load_inputs(args.public_root, args.inputs_manifest_sha256)
        require(cohort.protocol_sha256 == protocol_hash, "public inputs belong to another frozen protocol")
        schedule = build_schedule(cohort)
        require(len(schedule) == 768 and len(set(schedule)) == 768, "fixed schedule incomplete")
        if args.plan_only:
            print(json.dumps({"schema": "classical.ecdlp.endpoint-reuse.execution-plan-preview/v1",
                              "measurement_started": False, "protocol_sha256": protocol_hash,
                              "inputs_manifest_sha256": args.inputs_manifest_sha256,
                              "commands": [{"cell_id": c, "arm": a} for c, a in schedule]}, indent=2))
            return 0
        require(sys.platform.startswith("linux") and hasattr(os, "wait4"), "Linux wait4 is required")
        require((os.getuid(), os.geteuid(), os.getgid(), os.getegid()) == (1000, 1000, 1000, 1000)
                and set(os.getgroups()) <= {1000}, "actual unprivileged UID/GID 1000 is required")
        STOP["signal"] = None
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda number, frame: STOP.__setitem__("signal", number))
        summary = execute(args, protocol, protocol_hash, cohort, context)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(summary))
    return 0 if summary["completed"] == 768 else 1


if __name__ == "__main__":
    raise SystemExit(main())
