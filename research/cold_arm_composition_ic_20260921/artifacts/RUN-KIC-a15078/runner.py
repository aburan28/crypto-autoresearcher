#!/usr/bin/env python3
"""Frozen four-arm process runner for RUN-KIC-a15078."""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
import platform
import signal
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any, Iterable

import certificate_checker
import prefix_checker
import receipt_parser
import rho_semantics_checker

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parents[1]
REPO = PACKAGE.parents[1]
PROTOCOL = PACKAGE / "protocol.json"
PROTOCOL_SHA256 = "1e43ef6fd838b622af98f160a4e4c61cd27794e79b81747364d7f86550c4879a"
EXPERIMENT_ID = "RUN-KIC-a15078"
TASK_ID = "TASK-20260921-b5b7ec"
BASELINE_BINARY = ROOT / "custody/ic_baseline/koblitz_rank_fixture"
CANDIDATE_BINARY = ROOT / "custody/ic_candidate/koblitz_rank_fixture"
RHO_BINARY = ROOT / "custody/rho_baseline/koblitz_rho_fixture"
RHO_CANDIDATE_BINARY = ROOT / "custody/rho_candidate/koblitz_rho_fixture"
CASE_MANIFEST = ROOT / "case_manifest.json"
PREFLIGHT = ROOT / "preflight.json"
SEMANTIC_CONTROLS = ROOT / "semantic_controls.json"
CERTIFICATE_CONTROLS = ROOT / "certificate_controls.json"
ANALYZER = ROOT / "analyze.py"
CERTIFICATE_CHECKER = ROOT / "certificate_checker.py"
PREFIX_CHECKER = ROOT / "prefix_checker.py"
RECEIPT_PARSER = ROOT / "receipt_parser.py"
RHO_SEMANTICS_CHECKER = ROOT / "rho_semantics_checker.py"
CONFORMANCE_ROOT = ROOT / "conformance/attempt1"
RECEIPTS = ROOT / "receipts"
PROCESSES = RECEIPTS / "processes.jsonl"
RAW_ROOT = RECEIPTS / "raw"
MEASUREMENT_ADMISSION = PACKAGE / "measurement_admission.json"
WATCHDOG_SECONDS = 240.0
MEMORY_LIMIT_BYTES = 8 * 1024**3
DIRECT_ENV = {
    "RAYON_NUM_THREADS": "1", "KIC_INCREMENTAL_RANK_CROSSCHECK": "0",
    "KIC_RANK_SURPLUS": "0", "KIC_RANK_AWARE_PAIR_SCAN": "1",
    "KIC_PARALLEL_SUPPORT_EXPANSION": "0", "KIC_PIPELINED_SUPPORT_EXPANSION": "0",
}
RHO_ENV = dict(DIRECT_ENV)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def digest_value(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def write_once_json(path: Path, value: Any) -> None:
    data = json.dumps(value, sort_keys=True, indent=2) + "\n"
    if path.exists():
        require(path.read_text() == data, f"immutable artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        stream.flush(); os.fsync(stream.fileno())


def git_blob_matches_head(path: Path) -> bool:
    relative = path.relative_to(REPO).as_posix()
    result = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.returncode == 0 and result.stdout == path.read_bytes()


def validate_stage_b_references(preflight: dict[str, Any]) -> None:
    required = {
        "case_manifest_sha256": CASE_MANIFEST,
        "field_controls_sha256": ROOT / "field_controls.json",
        "batch_controls_sha256": ROOT / "batch_controls.json",
        "certificate_controls_sha256": CERTIFICATE_CONTROLS,
        "semantic_controls_sha256": SEMANTIC_CONTROLS,
        "source_closure_sha256": ROOT / "source_closure.json",
        "source_delta_audit_sha256": ROOT / "source_delta_audit.json",
        "build_toolchain_sha256": ROOT / "build_toolchain.json",
        "runner_analyzer_closure_sha256": ROOT / "runner_analyzer_closure.json",
    }
    for key, path in required.items():
        require(path.is_file(), f"Stage B input missing: {path}")
        require(preflight.get(key) == sha256_file(path), f"Stage B {key} mismatch")
    code_files = ("runner.py", "analyze.py", "prepare.py", "receipt_parser.py",
                  "certificate_checker.py", "prefix_checker.py", "rho_semantics_checker.py")
    for name in code_files:
        path = ROOT / name
        require(path.is_file(), f"Stage B code missing: {name}")
        require(preflight.get("code_sha256", {}).get(name) == sha256_file(path), f"Stage B code hash mismatch: {name}")
    for arm in ("ic_baseline", "ic_candidate", "rho_baseline", "rho_candidate"):
        path = binary_for_arm(arm)
        require(path.is_file(), f"Stage B binary missing: {arm}")
        require(preflight.get("binary_sha256", {}).get(arm) == sha256_file(path), f"Stage B binary hash mismatch: {arm}")
    require(preflight.get("protocol_sha256") == PROTOCOL_SHA256, "Stage B protocol hash mismatch")


def clean_environment(work: Path, direct: bool) -> dict[str, str]:
    home, temporary = work / "home", work / "tmp"
    home.mkdir(); temporary.mkdir()
    environment = {"PATH": os.defpath, "HOME": str(home), "TMPDIR": str(temporary), "LANG": "C", "LC_ALL": "C"}
    environment.update(DIRECT_ENV if direct else RHO_ENV)
    return environment


class DarwinMemorySampler:
    class RusageInfoV2(ctypes.Structure):
        _fields_ = [("ri_uuid", ctypes.c_ubyte * 16)] + [(name, ctypes.c_uint64) for name in (
            "ri_user_time", "ri_system_time", "ri_pkg_idle_wkups", "ri_interrupt_wkups", "ri_pageins",
            "ri_wired_size", "ri_resident_size", "ri_phys_footprint", "ri_proc_start_abstime",
            "ri_proc_exit_abstime", "ri_child_user_time", "ri_child_system_time", "ri_child_pkg_idle_wkups",
            "ri_child_interrupt_wkups", "ri_child_pageins", "ri_child_elapsed_abstime",
            "ri_diskio_bytesread", "ri_diskio_byteswritten")]

    def __init__(self) -> None:
        self.method, self.detail, self.function = "unavailable", None, None
        if platform.system() != "Darwin":
            self.detail = "Darwin-only proc_pid_rusage sampler"; return
        try:
            function = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True).proc_pid_rusage
            function.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]; function.restype = ctypes.c_int
            self.function = function; self.method = "proc_pid_rusage.RUSAGE_INFO_V2.ri_phys_footprint_sampled"
        except Exception as exc:
            self.detail = repr(exc)

    def sample(self, pid: int) -> int | None:
        if self.function is None:
            return None
        info = self.RusageInfoV2()
        if self.function(pid, 2, ctypes.byref(info)) != 0:
            self.detail = f"proc_pid_rusage errno={ctypes.get_errno()}"; return None
        return int(info.ri_phys_footprint)


def kill_group(process: subprocess.Popen[Any]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def binary_for_arm(arm: str) -> Path:
    return {"ic_baseline": BASELINE_BINARY, "ic_candidate": CANDIDATE_BINARY,
            "rho_baseline": RHO_BINARY, "rho_candidate": RHO_CANDIDATE_BINARY}[arm]


def argv_for(arm: str, n: int, seed: int, scalar: int, denominator: int = 256) -> list[str]:
    if arm in ("ic_baseline", "ic_candidate"):
        return [str(n), "0", "1", str(denominator), str(seed), "signed_expanded", "independent", "pair_pair_parallel_4096", "1", str(scalar)]
    return [str(n), "0", "signed_frobenius", "1", "packed", str(seed), str(scalar)]


def parse_output(arm: str, data: bytes, scalar: int, n: int, k: int | None) -> dict[str, Any]:
    if arm.startswith("rho_"):
        backend="aarch64_pmull_n53_fused_reduce" if arm=="rho_candidate" and n==53 else "aarch64_pmull"
        return receipt_parser.parse_rho_output(data, expected_scalar=scalar, expected_n=n,
                                               expected_backend=backend)
    if arm == "ic_candidate":
        modulus = 2003 if n == 13 else 21044858204113
        return receipt_parser.parse_target_output(data, expected_scalar=scalar, expected_n=n, expected_k=k, modulus=modulus)
    return receipt_parser.parse_direct_output(data, expected_scalar=scalar, expected_n=n, expected_k=k)


def run_untimed_control(arm: str, n: int) -> dict[str, Any]:
    case_root = CONFORMANCE_ROOT / f"n{n}" / arm
    require(not case_root.exists(), f"fresh conformance directory exists: {case_root}")
    case_root.mkdir(parents=True); work = case_root / "cwd"; work.mkdir()
    stdout_path, stderr_path = case_root / "stdout.jsonl", case_root / "stderr.txt"
    seed=13001 if n==13 else 53001
    binary = binary_for_arm(arm); argv = argv_for(arm, n, seed, 17, 2 if n==13 else 256)
    environment = clean_environment(work, arm.startswith("ic_"))
    status = None; popen_error = None; timeout = False; cap = False
    sample_count = 0; sampler = DarwinMemorySampler(); last_sample_ns = 0
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        protection_start = time.monotonic_ns()
        try:
            process = subprocess.Popen([str(binary), *argv], cwd=work, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=True, close_fds=True)
        except Exception as exc:
            popen_error = f"{type(exc).__name__}: {exc}"
        if popen_error is None:
            while True:
                waited_pid, waited_status, _usage = os.wait4(process.pid, os.WNOHANG)
                if waited_pid == process.pid:
                    status = waited_status; break
                now = time.monotonic_ns()
                if now - last_sample_ns >= 50_000_000:
                    current = sampler.sample(process.pid); last_sample_ns = now
                    if current is not None:
                        sample_count += 1
                        if current >= MEMORY_LIMIT_BYTES:
                            cap = True; kill_group(process)
                if (now - protection_start) / 1e9 >= WATCHDOG_SECONDS:
                    timeout = True; kill_group(process)
                if timeout or cap:
                    _, status, _usage = os.wait4(process.pid, 0); break
                time.sleep(0.001)
            process.returncode = os.waitstatus_to_exitcode(status)
        stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
    exit_code = os.waitstatus_to_exitcode(status) if status is not None else None
    parsed = None; error = popen_error
    if timeout or cap:
        error = "untimed control resource protection triggered"
    elif popen_error is None and exit_code == 0:
        try:
            parsed = parse_output(arm, stdout_path.read_bytes(), 17, n, None if arm.startswith("rho_") else 1 if n==13 else 75)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
    elif error is None:
        error = f"child exited {exit_code}"
    receipt = {
        "schema": "crypto.autoresearch.arm_composition_conformance_receipt.v1", "arm": arm,"n":n,
        "argv": [str(binary), *argv], "binary_sha256": sha256_file(binary), "cwd": str(work),
        "environment": environment, "exit_code": exit_code, "valid": parsed is not None,
        "validation_error": error, "parsed_receipt": parsed,
        "stdout_sha256": sha256_file(stdout_path), "stderr_sha256": sha256_file(stderr_path),
        "parent_wall_cpu_rss_not_retained": True,
        "raw_solver_internal_timing": "present in raw/parsed child output as diagnostic fields; excluded from conformance and science analysis",
        "protections": {"watchdog_seconds": WATCHDOG_SECONDS, "watchdog_reached": timeout,
                        "memory_cap_bytes": MEMORY_LIMIT_BYTES, "memory_cap_reached": cap,
                        "memory_sampling_method": sampler.method, "successful_sample_count": sample_count},
    }
    write_once_json(case_root / "receipt.json", receipt)
    require(receipt["valid"], f"conformance {arm} failed: {error}")
    return receipt


def conformance() -> None:
    require(not CONFORMANCE_ROOT.exists(), "conformance attempt already exists")
    require(PREFLIGHT.is_file() and git_blob_matches_head(PREFLIGHT), "committed implementation preflight absent")
    validate_stage_b_references(json.loads(PREFLIGHT.read_text()))
    admission = PACKAGE / "implementation_admission.json"
    require(admission.is_file() and git_blob_matches_head(admission), "committed Stage-B implementation admission absent")
    CONFORMANCE_ROOT.mkdir(parents=True)
    arms=("ic_baseline","ic_candidate","rho_baseline","rho_candidate")
    receipts={f"n{n}":{arm:run_untimed_control(arm,n) for arm in arms} for n in (13,53)}
    controls={}
    for n in (13,53):
        group=receipts[f"n{n}"]
        baseline_raw=(CONFORMANCE_ROOT/f"n{n}/ic_baseline/stdout.jsonl").read_bytes()
        candidate_raw=(CONFORMANCE_ROOT/f"n{n}/ic_candidate/stdout.jsonl").read_bytes()
        prefix=prefix_checker.check(baseline_raw,candidate_raw)
        certificate=certificate_checker.check(candidate_raw,expected_scalar=17,modulus=2003 if n==13 else 21044858204113,expected_k=1 if n==13 else 75)
        rho=rho_semantics_checker.check(group["rho_baseline"]["parsed_receipt"],group["rho_candidate"]["parsed_receipt"])
        points={tuple(group[arm]["parsed_receipt"]["published_q"]) for arm in arms}
        require(len(points)==1,"conformance public point mismatch")
        controls[f"n{n}"]={"prefix":prefix,"certificate":certificate,"rho_semantics":rho}
    summary = {
        "schema": "crypto.autoresearch.arm_composition_conformance_summary.v1", "valid": True,
        "children": 8, "parent_wall_cpu_rss_not_retained": True,
        "raw_solver_internal_timing": "diagnostic only; excluded from science analysis",
        "parsed": {n:{arm:receipt["parsed_receipt"] for arm,receipt in group.items()} for n,group in receipts.items()},
        "controls":controls,
        "semantic_controls_sha256": sha256_file(SEMANTIC_CONTROLS),
        "certificate_controls_sha256": sha256_file(CERTIFICATE_CONTROLS),
        "preflight_sha256": sha256_file(PREFLIGHT), "scientific_children": 0,
    }
    write_once_json(CONFORMANCE_ROOT / "summary.json", summary)


def telemetry_error(usage: Any, sample_count: int, sampled_peak: int | None) -> str | None:
    if usage is None:
        return "missing per-PID wait4 usage"
    values = (usage.ru_utime, usage.ru_stime, usage.ru_maxrss)
    if not all(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0 for value in values):
        return "nonfinite or negative wait4 telemetry"
    if usage.ru_maxrss <= 0:
        return "missing or zero wait4 peak RSS"
    if sample_count <= 0 or sampled_peak is None or sampled_peak <= 0:
        return "missing or zero per-PID physical-footprint samples"
    return None


def run_scientific_child(case: dict[str, Any]) -> dict[str, Any]:
    case_root = RAW_ROOT / f"{case['ordinal']:03d}_{case['id']}"
    require(not case_root.exists(), f"fresh process directory exists: {case_root}")
    case_root.mkdir(parents=True); work = case_root / "cwd"; work.mkdir()
    stdout_path, stderr_path = case_root / "stdout.jsonl", case_root / "stderr.txt"
    arm, scalar, seed = case["arm"], case["scalar"], case["seed"]
    binary = binary_for_arm(arm); argv = argv_for(arm, 53, seed, scalar)
    environment = clean_environment(work, arm.startswith("ic_")); sampler = DarwinMemorySampler()
    started_at = None; start_ns = None; reaped_ns = status = usage = None
    timeout = cap = False; sampled_peak = None; sample_count = 0; last_sample_ns = 0; popen_error = None
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        started_at, start_ns = utc_now(), time.monotonic_ns()
        try:
            process = subprocess.Popen([str(binary), *argv], cwd=work, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=True, close_fds=True)
        except Exception as exc:
            popen_error = f"{type(exc).__name__}: {exc}"; reaped_ns = time.monotonic_ns()
        if popen_error is None:
            while True:
                waited_pid, waited_status, waited_usage = os.wait4(process.pid, os.WNOHANG)
                if waited_pid == process.pid:
                    status, usage, reaped_ns = waited_status, waited_usage, time.monotonic_ns(); break
                now = time.monotonic_ns()
                if now - last_sample_ns >= 50_000_000:
                    current = sampler.sample(process.pid); last_sample_ns = now
                    if current is not None:
                        sample_count += 1; sampled_peak = current if sampled_peak is None else max(sampled_peak, current)
                        if current >= MEMORY_LIMIT_BYTES:
                            cap = True; kill_group(process)
                if (now - start_ns) / 1e9 >= WATCHDOG_SECONDS:
                    timeout = True; kill_group(process)
                if timeout or cap:
                    _, status, usage = os.wait4(process.pid, 0); reaped_ns = time.monotonic_ns(); break
                time.sleep(0.001)
            process.returncode = os.waitstatus_to_exitcode(status)
        stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
    durable_ns, ended_at = time.monotonic_ns(), utc_now()
    exit_code = os.waitstatus_to_exitcode(status) if status is not None else None
    unexpected_files = sorted(path.relative_to(work).as_posix() for path in work.rglob("*") if path.is_file() and not path.relative_to(work).as_posix().startswith(("home/", "tmp/")))
    parsed = None; error = popen_error; unexpected = bool(unexpected_files)
    terminal = "completed_valid"
    if popen_error is not None: terminal = "failed_infrastructure"
    elif timeout or cap: terminal = "resource_exhaustion"
    elif exit_code != 0: terminal = "failed_implementation"
    else:
        try:
            parsed = parse_output(arm, stdout_path.read_bytes(), scalar, 53, None if arm.startswith("rho_") else 75)
        except receipt_parser.ValidationError as exc:
            error, unexpected, terminal = str(exc), unexpected or exc.unexpected, "completed_invalid"
        except Exception as exc:
            error, terminal = f"parser {type(exc).__name__}: {exc}", "failed_implementation"
    if unexpected_files:
        error, terminal = f"unexpected cwd files: {unexpected_files}", "completed_invalid"
    missing_telemetry = telemetry_error(usage, sample_count, sampled_peak)
    if terminal == "completed_valid" and missing_telemetry is not None:
        error, terminal = missing_telemetry, "completed_invalid"
    return {
        "schema": "crypto.autoresearch.arm_composition_process_receipt.v1", "experiment_id": EXPERIMENT_ID,
        "task_id": TASK_ID, **{key: case[key] for key in ("ordinal", "case_index", "position", "id", "arm", "scalar_label", "scalar", "seed_label", "seed")},
        "case_id": case["id"], "argv": [str(binary), *argv], "binary_sha256": sha256_file(binary),
        "cwd": str(work), "environment": environment, "started_at": started_at, "ended_at": ended_at,
        "wall_monotonic_ns": reaped_ns - start_ns, "wall_seconds": (reaped_ns - start_ns) / 1e9,
        "parent_output_durability_seconds": (durable_ns - reaped_ns) / 1e9,
        "wall_interval_note": "observed spawn-to-wait4-reap interval; includes polling and scheduler delay",
        "reap_poll_interval_requested_seconds": 0.001, "memory_sample_interval_requested_seconds": 0.05,
        "user_cpu_seconds": usage.ru_utime if usage else None, "system_cpu_seconds": usage.ru_stime if usage else None,
        "wait4_ru_maxrss": usage.ru_maxrss if usage else None, "wait4_ru_maxrss_unit": "bytes" if platform.system() == "Darwin" else "platform-dependent",
        "resource_collection": "os.wait4 per PID; Popen.poll unused",
        "memory_sampling": {"method": sampler.method, "detail": sampler.detail, "sample_count": sample_count,
                            "sampled_peak_bytes": sampled_peak, "limit_bytes": MEMORY_LIMIT_BYTES,
                            "cooperative_cap_enforced": sample_count > 0, "cap_reached": cap},
        "watchdog_seconds": WATCHDOG_SECONDS, "watchdog_reached": timeout, "exit_code": exit_code,
        "terminal_state": terminal, "valid": terminal == "completed_valid", "validation_error": error,
        "unexpected_stop_condition": unexpected, "retained_state_detected": bool(unexpected_files),
        "stdout_path": stdout_path.relative_to(ROOT).as_posix(), "stdout_sha256": sha256_file(stdout_path),
        "stderr_path": stderr_path.relative_to(ROOT).as_posix(), "stderr_sha256": sha256_file(stderr_path),
        "parsed_receipt": parsed,
    }


def load_processes() -> list[dict[str, Any]]:
    return [] if not PROCESSES.exists() else [json.loads(line) for line in PROCESSES.read_text().splitlines() if line]


def apply_prefix_control(receipt: dict[str, Any], existing: list[dict[str, Any]]) -> None:
    if receipt["arm"] not in ("ic_baseline", "ic_candidate"):
        return
    mate_arm = "ic_candidate" if receipt["arm"] == "ic_baseline" else "ic_baseline"
    mate = next((row for row in existing if row["case_index"] == receipt["case_index"] and row["arm"] == mate_arm), None)
    if mate is None:
        return
    baseline = receipt if receipt["arm"] == "ic_baseline" else mate
    candidate = receipt if receipt["arm"] == "ic_candidate" else mate
    try:
        result = prefix_checker.check((ROOT / baseline["stdout_path"]).read_bytes(), (ROOT / candidate["stdout_path"]).read_bytes())
        receipt["prefix_control"] = result
    except Exception as exc:
        receipt["prefix_control"] = {"valid": False, "error": f"{type(exc).__name__}: {exc}"}
        receipt["terminal_state"] = "completed_invalid"; receipt["valid"] = False
        receipt["validation_error"] = receipt["prefix_control"]["error"]
        receipt["unexpected_stop_condition"] = True


def apply_rho_control(receipt: dict[str, Any], existing: list[dict[str, Any]]) -> None:
    if receipt["arm"] not in ("rho_baseline", "rho_candidate"):
        return
    mate_arm="rho_candidate" if receipt["arm"]=="rho_baseline" else "rho_baseline"
    mate=next((row for row in existing if row["case_index"]==receipt["case_index"] and row["arm"]==mate_arm),None)
    if mate is None:return
    old=receipt if receipt["arm"]=="rho_baseline" else mate
    new=receipt if receipt["arm"]=="rho_candidate" else mate
    try:receipt["rho_semantics_control"]=rho_semantics_checker.check(old["parsed_receipt"],new["parsed_receipt"])
    except Exception as exc:
        receipt["rho_semantics_control"]={"valid":False,"error":f"{type(exc).__name__}: {exc}"}
        receipt["terminal_state"]="completed_invalid";receipt["valid"]=False
        receipt["validation_error"]=receipt["rho_semantics_control"]["error"]
        receipt["unexpected_stop_condition"]=True


def validate_admission_record(admission: dict[str, Any], expected: dict[str, Any]) -> None:
    for key, value in expected.items():
        require(admission.get(key) == value, f"admission {key} mismatch")


def verify_admission(commit: str) -> dict[str, Any]:
    require(subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=REPO).returncode == 0, "named admission commit not reachable")
    require(MEASUREMENT_ADMISSION.is_file(), "measurement admission absent from worktree")
    relative = MEASUREMENT_ADMISSION.relative_to(REPO).as_posix()
    blob = subprocess.run(["git", "show", f"{commit}:{relative}"], cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    require(blob.returncode == 0, "measurement admission absent from named commit")
    require(blob.stdout == MEASUREMENT_ADMISSION.read_bytes(), "worktree admission differs from named commit blob")
    admission = json.loads(blob.stdout)
    expected = {
        "schema": "crypto.autoresearch.arm_composition_measurement_admission.v1", "status": "admitted",
        "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID, "protocol_sha256": PROTOCOL_SHA256,
        "runner_sha256": sha256_file(Path(__file__)), "analyze_sha256": sha256_file(ANALYZER),
        "certificate_checker_sha256": sha256_file(CERTIFICATE_CHECKER),
        "prefix_checker_sha256": sha256_file(PREFIX_CHECKER),
        "receipt_parser_sha256": sha256_file(RECEIPT_PARSER),
        "rho_semantics_checker_sha256":sha256_file(RHO_SEMANTICS_CHECKER),
        "case_manifest_sha256": sha256_file(CASE_MANIFEST),
        "preflight_sha256": sha256_file(PREFLIGHT), "conformance_sha256": sha256_file(CONFORMANCE_ROOT / "summary.json"),
    }
    validate_admission_record(admission, expected)
    require(admission.get("binary_sha256") == {"ic_baseline": sha256_file(BASELINE_BINARY), "ic_candidate": sha256_file(CANDIDATE_BINARY), "rho_baseline": sha256_file(RHO_BINARY), "rho_candidate":sha256_file(RHO_CANDIDATE_BINARY)}, "admission binary hashes mismatch")
    require(admission.get("scientific_children") == 96 and admission.get("sole_launch_task") == TASK_ID, "admission launch binding mismatch")
    return admission


def scientific(admission_commit: str | None) -> None:
    require(admission_commit is not None, "explicit --admission-commit from root assignment is required")
    verify_admission(admission_commit)
    manifest = json.loads(CASE_MANIFEST.read_text()); cases = manifest["cases"]
    require(len(cases) == 96, "case manifest count mismatch")
    existing = load_processes(); require(len(existing) <= 96, "receipt count exceeds 96")
    for index, row in enumerate(existing):
        require((row["ordinal"], row["case_id"]) == (cases[index]["ordinal"], cases[index]["id"]), "receipt prefix mismatch")
        require(row.get("unexpected_stop_condition") is not True, f"prior anomaly at {row['case_id']}")
    for case in cases[len(existing):]:
        receipt = run_scientific_child(case)
        apply_prefix_control(receipt, existing)
        apply_rho_control(receipt, existing)
        append_jsonl(PROCESSES, receipt); existing.append(receipt)
        if receipt["unexpected_stop_condition"]:
            raise RuntimeError(f"unexpected observation at {case['id']}: {receipt['validation_error']}")
    require(len(load_processes()) == 96, "schedule did not reach 96 terminal receipts")
    result = subprocess.run([sys.executable, str(ANALYZER)], cwd=ROOT, check=False)
    require(result.returncode == 0, f"analyzer exited {result.returncode}")
    finalize()


def normalized_tar(paths: Iterable[tuple[Path, str]], destination: Path) -> None:
    temporary = destination.with_name(destination.name + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path, arcname in sorted(paths, key=lambda item: item[1]):
                    info = archive.gettarinfo(str(path), arcname=arcname); info.uid = info.gid = 0; info.uname = info.gname = ""; info.mtime = 0
                    with path.open("rb") as source: archive.addfile(info, source)
        raw.flush(); os.fsync(raw.fileno())
    os.replace(temporary, destination)


def finalize() -> None:
    rows = load_processes(); require(len(rows) == 96, "finalize requires 96 receipts")
    raw_files = sorted(path for path in RAW_ROOT.rglob("*") if path.is_file())
    raw_manifest = {"schema": "crypto.autoresearch.raw_processes_manifest.v1",
                    "files": [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in raw_files]}
    raw_manifest["tree_digest"] = digest_value(raw_manifest["files"])
    atomic_json(RECEIPTS / "raw_processes_manifest.json", raw_manifest)
    normalized_tar([(path, path.relative_to(ROOT).as_posix()) for path in raw_files], RECEIPTS / "raw_processes.tar.gz")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    atomic_json(ROOT / "environment.json", {
        "schema": "crypto.autoresearch.arm_composition_environment.v1", "git_head": head,
        "platform": platform.platform(), "machine": platform.machine(), "python": sys.version,
        "direct_environment": {"PATH": os.defpath, "HOME": "<fresh>/home", "TMPDIR": "<fresh>/tmp", "LANG": "C", "LC_ALL": "C", **DIRECT_ENV},
        "rho_environment": {"PATH": os.defpath, "HOME": "<fresh>/home", "TMPDIR": "<fresh>/tmp", "LANG": "C", "LC_ALL": "C", **RHO_ENV},
        "capture": "explicit whitelist templates; parent environment not dumped",
    })
    terminal_counts: dict[str, int] = {}
    for row in rows: terminal_counts[row["terminal_state"]] = terminal_counts.get(row["terminal_state"], 0) + 1
    anomalies = [{"case_id": row["case_id"], "state": row["terminal_state"], "error": row.get("validation_error")} for row in rows if not row["valid"] or row.get("unexpected_stop_condition")]
    atomic_json(ROOT / "execution_receipt.json", {
        "execution_report": {"experiment_id": EXPERIMENT_ID, "task_id": TASK_ID, "implementation_commit": head,
            "protocol_deviations": [], "runs": {"terminal_counts": terminal_counts,
            "completed": [row["case_id"] for row in rows if row["valid"]], "invalid": [row["case_id"] for row in rows if row["terminal_state"] == "completed_invalid"],
            "failed": [row["case_id"] for row in rows if row["terminal_state"].startswith("failed_") or row["terminal_state"] == "resource_exhaustion"]},
            "observations": [{"analysis": "analysis.json", "prediction": "protocol.json#measurement"}],
            "anomalies": anomalies, "executor_assessment": {"protocol_complete": True, "data_quality": "good" if not anomalies else "limited", "requires_rerun": False},
            "claim_boundary": "executor observation only; no status transition"}
    })
    declared = ["source_closure.json", "source_delta_audit.json", "build_toolchain.json", "preflight.json", "case_manifest.json", "field_controls.json", "batch_controls.json", "certificate_controls.json", "semantic_controls.json", "runner_analyzer_closure.json", "runner.py", "analyze.py", "prepare.py", "certificate_checker.py", "prefix_checker.py", "receipt_parser.py", "rho_semantics_checker.py", "candidate.patch", "candidate_source.tar.gz", "receipts/processes.jsonl", "receipts/raw_processes.tar.gz", "receipts/raw_processes_manifest.json", "analysis.json", "analysis.md", "environment.json", "execution_receipt.json", "conformance/attempt1/summary.json", "custody/ic_baseline/koblitz_rank_fixture", "custody/ic_candidate/koblitz_rank_fixture", "custody/rho_baseline/koblitz_rho_fixture", "custody/rho_candidate/koblitz_rho_fixture"]
    missing = [name for name in declared if not (ROOT / name).is_file()]; require(not missing, f"snapshot files missing: {missing}")
    atomic_json(ROOT / "snapshot_manifest.json", {"schema": "crypto.autoresearch.arm_composition_snapshot_manifest.v1",
        "self_hash_omitted": True, "artifacts": [{"path": name, "bytes": (ROOT / name).stat().st_size, "sha256": sha256_file(ROOT / name)} for name in declared]})


def self_test() -> None:
    if PREFLIGHT.exists():
        binding = json.loads(PREFLIGHT.read_text())
        validate_stage_b_references(binding)
        missing = dict(binding); missing.pop("semantic_controls_sha256", None)
        try:
            validate_stage_b_references(missing)
            raise RuntimeError("missing semantic control binding accepted")
        except RuntimeError as exc:
            require("Stage B semantic_controls_sha256 mismatch" in str(exc), "semantic control negative test did not fail at the bound reference")
    manifest = json.loads(CASE_MANIFEST.read_text()) if CASE_MANIFEST.exists() else None
    if manifest:
        require(len(manifest["cases"]) == 96 and manifest["position_counts"] == {arm: [6, 6, 6, 6] for arm in ("ic_baseline", "ic_candidate", "rho_baseline", "rho_candidate")}, "manifest self-test failed")
    require(argv_for("ic_candidate", 53, 7, 11)[0:4] == ["53", "0", "1", "256"], "direct argv failed")
    require(argv_for("rho_candidate", 53, 7, 11) == ["53", "0", "signed_frobenius", "1", "packed", "7", "11"], "rho argv failed")
    require(RHO_ENV == DIRECT_ENV and len(RHO_ENV) == 6, "rho environment does not carry all frozen flags")
    class Usage:
        ru_utime = 1.0; ru_stime = 0.5; ru_maxrss = 1024
    require(telemetry_error(Usage(), 1, 2048) is None, "valid telemetry rejected")
    require(telemetry_error(Usage(), 0, None) is not None, "missing samples accepted")
    good_admission = {"schema": "x", "status": "admitted"}; validate_admission_record(good_admission, dict(good_admission))
    try:
        validate_admission_record({"schema": "x"}, good_admission)
        raise RuntimeError("bad admission accepted")
    except RuntimeError as exc:
        require("admission status mismatch" in str(exc), "admission failure path mismatch")
    parent_stdout = REPO / "research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/conformance/attempt3/baseline_ic/stdout.jsonl"
    bad_backend = parent_stdout.read_bytes().replace(b"aarch64_pmull", b"wrong_backend")
    try:
        receipt_parser.parse_direct_output(bad_backend, expected_scalar=17, expected_n=13, expected_k=1)
        raise RuntimeError("bad backend accepted")
    except receipt_parser.ValidationError as exc:
        require(exc.unexpected, "backend mismatch did not request anomaly stop")
    prefix_row = {"kind":"relation_rank_receipt","accepted_relation":1,"trial":3,
                  "coefficient_a":5,"coefficient_b":7,"target_point_key":[1,2],
                  "factor_point_indices":[0,1],"orbit_labels":[],"sparse_row":[1,2],
                  "relation_hash":"a"*64,"verified_group_identity":True}
    prefix_bytes = (json.dumps(prefix_row)+"\n").encode()
    require(prefix_checker.check(prefix_bytes, prefix_bytes)["valid"], "matching prefix rejected")
    mismatched = dict(prefix_row); mismatched["coefficient_a"] = 6
    try:
        prefix_checker.check(prefix_bytes, (json.dumps(mismatched)+"\n").encode())
        raise RuntimeError("mismatched prefix accepted")
    except prefix_checker.PrefixError:
        pass
    try:
        prefix_checker.check(prefix_bytes, b"")
        raise RuntimeError("unavailable prefix accepted")
    except prefix_checker.PrefixError:
        pass
    missing_field = dict(prefix_row); missing_field.pop("sparse_row")
    try:
        prefix_checker.check((json.dumps(missing_field)+"\n").encode(), (json.dumps(missing_field)+"\n").encode())
        raise RuntimeError("matching malformed prefixes accepted")
    except prefix_checker.PrefixError:
        pass
    print(json.dumps({"self_test": "PASS", "tests": 15}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", choices=("conformance", "scientific", "finalize", "self-test"), required=True); parser.add_argument("--admission-commit"); args = parser.parse_args()
    {"conformance": conformance, "scientific": lambda: scientific(args.admission_commit), "finalize": finalize, "self-test": self_test}[args.phase]()


if __name__ == "__main__": main()
