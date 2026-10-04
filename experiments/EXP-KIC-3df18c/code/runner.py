#!/usr/bin/env python3
"""One-owner process supervisor and immutable custody for EXP-KIC-3df18c.

The build phase compiles only. Controls, science and checker require distinct
root-named committed admissions and are not invoked by the Executor in Stage A.
"""
from __future__ import annotations
import argparse
import ctypes
import datetime as dt
import fcntl
import gzip
import hashlib
import json
import math
import os
import platform
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import traceback
from pathlib import Path
from typing import Any

CODE = Path(__file__).resolve().parent
EXP = CODE.parent
REPO = EXP.parents[1]
RUN = EXP / "runs/RUN-KIC-234d11"
POOL = REPO / "research/admissible_affine_factor_base_20260921/inputs/pool.json"
HISTORICAL = REPO / "research/admissible_affine_factor_base_20260921/inputs/orbit-global-n19.jsonl"
PROTOCOL = REPO / "research/admissible_affine_factor_base_20260921/protocol.json"
AMENDMENT = REPO / "research/admissible_affine_factor_base_20260921/baseline_amendment.json"
SPEC = EXP / "specification.yaml"
POOL_SHA = "023e512c29db5fe1d23cc32740db0f4ce418f5920d6feed06c74f6e42df2ed6f"
HISTORICAL_SHA = "c94567b1257a7137c05174c656f7397b694b6bcc6612d9a9dca9095595781151"
PROTOCOL_SHA = "2e81c0908e759287c9edb52fd5e9e92ff2fc631353d49d07b3c0cca1132d7355"
AMENDMENT_SHA = "36612217268aef24dbcebe122ec057e71a6bb7c4d3d15fd90af7e17e0cb0b9c3"
TASK = "TASK-20260921-5c43c7"
EXPERIMENT = "EXP-KIC-3df18c"
RUN_ID = "RUN-KIC-234d11"
SOURCE_FILES = ("search.cpp", "check.py", "runner.py", "README.md")
BINARY = RUN / "build_v2/search_final"
CLOSURE = RUN / "source_closure_v2.json"
ENVIRONMENT = RUN / "environment_v2.json"
READINESS = RUN / "implementation_readiness_v2.json"
OLD_COMMIT = "917ed4d0f7"
OLD_CLOSURE_SHA = "0eb4532ef27bea873746cef570b7a9e60103aaa94a64094895b905531ba3341f"
OLD_BINARY_SHA = "a7ba20a3b4d228b6a03218a399a1950cbb5e3f2f8a0740af788206c11e0a10d7"
CAP_BYTES = 8 * 1024**3
WATCHDOG = {"controls": 900, "science": 1800, "checker": 1800}
PHASE_FILES = {
    "controls": ("controls.json",),
    "science": ("geometry.json", "plane_catalogue.json", "base_scores.json",
                "support_cache.bin", "support_cache_manifest.json", "selected.json",
                "progress.jsonl"),
    "checker": ("independent_replay.json",),
}

def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)

def code_hashes() -> dict[str, str]:
    return {name: sha(CODE / name) for name in SOURCE_FILES}

def verify_inputs() -> None:
    for path, expected in ((POOL, POOL_SHA), (HISTORICAL, HISTORICAL_SHA),
                           (PROTOCOL, PROTOCOL_SHA), (AMENDMENT, AMENDMENT_SHA)):
        require(path.is_file() and sha(path) == expected, f"frozen input hash mismatch: {path}")

def rows(path: Path) -> list[dict[str, Any]]:
    return [] if not path.exists() else [json.loads(line) for line in path.read_text().splitlines() if line]

def normalized_tar(files: list[tuple[Path, str]], destination: Path) -> None:
    temporary = destination.with_name(destination.name + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for source, name in sorted(files, key=lambda item: item[1]):
                    info = archive.gettarinfo(str(source), arcname=name)
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    with source.open("rb") as stream:
                        archive.addfile(info, stream)
        raw.flush()
        os.fsync(raw.fileno())
    os.replace(temporary, destination)

def build() -> None:
    verify_inputs()
    RUN.mkdir(parents=True, exist_ok=True)
    folder = RUN / "build_v2"
    folder.mkdir(parents=True, exist_ok=True)
    require(not BINARY.exists() and not CLOSURE.exists(),
            "v2 build already exists; preserve it and request additive correction")
    require(sha(RUN / "source_closure.json") == OLD_CLOSURE_SHA and
            sha(RUN / "build/search_final") == OLD_BINARY_SHA,
            "immutable original source/binary custody changed")
    compiler = Path("/usr/bin/clang++")
    require(compiler.is_file(), "Apple clang++ absent")
    version = subprocess.run([str(compiler), "--version"], capture_output=True, check=False)
    require(version.returncode == 0, "compiler version read failed")
    (folder / "compiler.version.stdout").write_bytes(version.stdout)
    (folder / "compiler.version.stderr").write_bytes(version.stderr)
    argv = [str(compiler), "-O3", "-std=c++20", "-DNDEBUG", "-Wall", "-Wextra",
            "-Wpedantic", "-o", str(BINARY), str(CODE / "search.cpp")]
    before_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic_ns()
    result = subprocess.run(argv, capture_output=True, check=False, cwd=REPO)
    after_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
    wall = (time.monotonic_ns() - started) / 1e9
    (folder / "compile.stdout").write_bytes(result.stdout)
    (folder / "compile.stderr").write_bytes(result.stderr)
    receipt = {"schema": "crypto.autoresearch.n19_build_receipt.v1", "argv": argv,
               "exit_code": result.returncode, "wall_seconds": wall,
               "source_sha256": sha(CODE / "search.cpp"),
               "compiler_sha256": sha(compiler), "compiler_version_stdout_sha256": sha(folder / "compiler.version.stdout"),
               "compiler_process_cpu_scope": "RUSAGE_CHILDREN delta across clang++ invocation, inclusive of compiler subprocesses if reported by OS",
               "compiler_process_cpu_user_seconds": after_cpu.ru_utime - before_cpu.ru_utime,
               "compiler_process_cpu_system_seconds": after_cpu.ru_stime - before_cpu.ru_stime,
               "compiler_process_peak_rss_before": before_cpu.ru_maxrss,
               "compiler_process_peak_rss_after": after_cpu.ru_maxrss,
               "compiler_process_peak_rss_scope": "RUSAGE_CHILDREN high-water marks; their difference is not a per-build peak",
               "compiler_version_stderr_sha256": sha(folder / "compiler.version.stderr"),
               "compile_stdout_sha256": sha(folder / "compile.stdout"),
               "compile_stderr_sha256": sha(folder / "compile.stderr"),
               "binary_sha256": sha(BINARY) if BINARY.is_file() else None,
               "binary_bytes": BINARY.stat().st_size if BINARY.is_file() else None,
               "controls_launched": 0, "science_launched": 0, "checker_launched": 0}
    atomic_json(folder / "build_receipt.json", receipt)
    require(result.returncode == 0 and BINARY.is_file(), "C++ compilation failed; receipt preserved")
    binary_file = subprocess.run(["file", str(BINARY)], capture_output=True, check=False)
    deps = subprocess.run(["otool", "-L", str(BINARY)], capture_output=True, check=False)
    require(binary_file.returncode == 0 and deps.returncode == 0,
            "binary architecture/dependency inspection failed")
    (folder / "binary.file.stdout").write_bytes(binary_file.stdout)
    (folder / "binary.file.stderr").write_bytes(binary_file.stderr)
    (folder / "binary.otool.stdout").write_bytes(deps.stdout)
    (folder / "binary.otool.stderr").write_bytes(deps.stderr)
    require(b"arm64" in binary_file.stdout, "compiled binary architecture is not arm64")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip()
    closure = {"schema": "crypto.autoresearch.n19_source_closure.v2",
               "task_id": TASK, "experiment_id": EXPERIMENT, "run_id": RUN_ID,
               "source_sha256": code_hashes(), "binary_sha256": sha(BINARY),
               "binary_bytes": BINARY.stat().st_size,
               "input_sha256": {"pool": POOL_SHA, "historical_global_jsonl": HISTORICAL_SHA,
                                "protocol": PROTOCOL_SHA, "amendment": AMENDMENT_SHA,
                                "specification": sha(SPEC)},
               "compiler_sha256": sha(compiler),
               "compiler_version_stdout_sha256": sha(folder / "compiler.version.stdout"),
               "build_receipt_sha256": sha(folder / "build_receipt.json"),
               "binary_file_sha256": sha(folder / "binary.file.stdout"),
               "binary_otool_sha256": sha(folder / "binary.otool.stdout"),
               "execution_head_at_build": head,
               "scientific_processes": 0, "native_control_processes": 0,
               "independent_checker_processes": 0}
    atomic_json(CLOSURE, closure)
    atomic_json(ENVIRONMENT, {
        "schema": "crypto.autoresearch.n19_environment.v2",
        "platform": platform.platform(), "machine": platform.machine(),
        "python": sys.version, "compiler": version.stdout.decode(errors="replace").strip(),
        "python_executable": str(Path(sys.executable).resolve()),
        "python_executable_sha256": sha(Path(sys.executable).resolve()),
        "binary_file": binary_file.stdout.decode(errors="replace").strip(),
        "binary_otool_sha256": sha(folder / "binary.otool.stdout"),
        "build_head": head, "model_policy": "executor-implementation",
        "resolved_model_id": "gpt-5.6-sol", "reasoning_effort": "high",
        "fallback_used": False, "degraded_used": False, "model_verified": False,
    })
    atomic_json(READINESS, {
        "schema": "crypto.autoresearch.n19_implementation_readiness.v2",
        "status": "SOURCE_AND_BUILD_READY_NO_PROCESS_ADMISSION",
        "source_closure_sha256": sha(CLOSURE),
        "environment_sha256": sha(ENVIRONMENT),
        "binary_sha256": sha(BINARY),
        "holds": {"controls": "committed process admission and explicit root sole launch",
                  "science": "accepted controls plus committed science admission",
                  "checker": "science completion plus committed checker admission"},
        "planned_processes": {"native_controls": 1, "science": 1, "checker": 1},
    })
    old = json.loads((RUN / "source_closure.json").read_text())
    atomic_json(RUN / "source_custody_supersession.json", {
        "schema": "crypto.autoresearch.n19_preadmission_source_supersession.v1",
        "reason": "add triple-region, pair-region, and sorted-target-key custody before first native process",
        "original_implementation_commit": OLD_COMMIT,
        "preserved_predecessor_manifest_path": "build/preserved_pre_cache_manifest/preservation.json",
        "preserved_predecessor_manifest_sha256": sha(RUN / "build/preserved_pre_cache_manifest/preservation.json"),
        "original": {"source_closure_path": "source_closure.json", "source_closure_sha256": OLD_CLOSURE_SHA,
                     "binary_path": "build/search_final", "binary_sha256": OLD_BINARY_SHA,
                     "source_sha256": old["source_sha256"],
                     "build_receipt_path": "build/build_receipt.json",
                     "build_receipt_sha256": sha(RUN / "build/build_receipt.json"),
                     "readiness_path": "implementation_readiness.json",
                     "readiness_sha256": sha(RUN / "implementation_readiness.json")},
        "successor": {"source_closure_path": CLOSURE.name, "source_closure_sha256": sha(CLOSURE),
                      "binary_path": BINARY.relative_to(RUN).as_posix(), "binary_sha256": sha(BINARY),
                      "source_sha256": code_hashes(),
                      "build_receipt_path": "build_v2/build_receipt.json",
                      "build_receipt_sha256": sha(folder / "build_receipt.json"),
                      "environment_path": ENVIRONMENT.name, "environment_sha256": sha(ENVIRONMENT),
                      "readiness_path": READINESS.name, "readiness_sha256": sha(READINESS)},
        "native_control_processes_before_successor": 0,
        "science_processes_before_successor": 0,
        "checker_processes_before_successor": 0,
    })
    print(json.dumps({"status": "implementation_ready_only_v2",
                      "source_closure_sha256": sha(CLOSURE),
                      "binary_sha256": sha(BINARY)}, sort_keys=True))

def verify_closure() -> dict[str, Any]:
    verify_inputs()
    closure = json.loads(CLOSURE.read_text())
    require(closure["source_sha256"] == code_hashes(), "live source changed after build")
    require(closure["binary_sha256"] == sha(BINARY), "compiled binary changed")
    require(closure["input_sha256"]["specification"] == sha(SPEC), "specification changed")
    require(closure["build_receipt_sha256"] == sha(RUN / "build_v2/build_receipt.json"),
            "build receipt changed")
    return closure

def verify_admission(path: Path, commit: str, phase: str) -> dict[str, Any]:
    closure = verify_closure()
    relative = path.relative_to(REPO).as_posix()
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"],
                              cwd=REPO, capture_output=True, check=False)
    require(ancestry.returncode == 0, "admission commit is not reachable")
    blob = subprocess.run(["git", "show", f"{commit}:{relative}"], cwd=REPO,
                          capture_output=True, check=False)
    require(blob.returncode == 0 and blob.stdout == path.read_bytes(),
            "admission blob differs from named commit")
    admission = json.loads(blob.stdout)
    require(admission.get("status") == "admitted" and admission.get("phase") == phase and
            admission.get("task_id") == TASK and admission.get("run_id") == RUN_ID and
            admission.get("source_closure_sha256") == sha(CLOSURE),
            "admission role/phase/source mismatch")
    for current in [CLOSURE, BINARY] + [CODE / name for name in SOURCE_FILES]:
        item = current.relative_to(REPO).as_posix()
        committed = subprocess.run(["git", "show", f"{commit}:{item}"], cwd=REPO,
                                   capture_output=True, check=False)
        require(committed.returncode == 0 and committed.stdout == current.read_bytes(),
                f"named-commit readback mismatch: {item}")
    if phase in ("science", "checker"):
        require(admission.get("controls_sha256") == sha(RUN / "controls.json"),
                "admission native-control hash mismatch")
    if phase == "checker":
        frozen = admission.get("science_artifact_sha256", {})
        for name in PHASE_FILES["science"]:
            require(frozen.get(name) == sha(RUN / name),
                    f"checker admission science artifact mismatch: {name}")
    return admission

class Sampler:
    class Info(ctypes.Structure):
        _fields_ = [("uuid", ctypes.c_ubyte * 16)] + [
            (name, ctypes.c_uint64) for name in
            ("user", "system", "pkg", "interrupt", "pageins", "wired",
             "resident", "footprint", "start", "exit", "child_user",
             "child_system", "child_pkg", "child_interrupt", "child_pageins",
             "child_elapsed", "disk_read", "disk_write")]
    def __init__(self) -> None:
        self.method = "unavailable"
        self.error = None
        self.function = None
        if platform.system() == "Darwin":
            try:
                fn = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True).proc_pid_rusage
                fn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
                fn.restype = ctypes.c_int
                self.function = fn
                self.method = "proc_pid_rusage.RUSAGE_INFO_V2.ri_phys_footprint"
            except Exception as exc:
                self.error = repr(exc)
    def sample(self, pid: int) -> int | None:
        if self.function is None:
            return None
        info = self.Info()
        if self.function(pid, 2, ctypes.byref(info)) != 0:
            self.error = f"errno={ctypes.get_errno()}"
            return None
        return int(info.footprint)

def fresh_env(raw: Path) -> dict[str, str]:
    home, temp = raw / "home", raw / "tmp"
    home.mkdir()
    temp.mkdir()
    return {"PATH": os.defpath, "HOME": str(home), "TMPDIR": str(temp),
            "LANG": "C", "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1"}

def phase_argv(phase: str, raw: Path) -> list[str]:
    if phase in ("controls", "science"):
        return [str(BINARY), "--controls" if phase == "controls" else "--science",
                str(POOL), str(raw), str(HISTORICAL)]
    return [sys.executable, str(CODE / "check.py"), "--pool", str(POOL),
            "--run", str(RUN), "--historical", str(HISTORICAL),
            "--output", str(raw / "independent_replay.json")]

def append_receipt(record: dict[str, Any]) -> None:
    path = RUN / "process_receipts.jsonl"
    with path.open("a") as stream:
        stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        stream.flush()
        os.fsync(stream.fileno())

def archive_partial(phase: str) -> None:
    raw = RUN / "raw" / phase
    if not raw.exists():
        return
    files = [(p, p.relative_to(RUN).as_posix()) for p in raw.rglob("*") if p.is_file()]
    normalized_tar(files, RUN / f"raw_{phase}.tar.gz")
    atomic_json(RUN / f"raw_{phase}_manifest.json",
                {"phase": phase, "files": [{"path": name, "bytes": p.stat().st_size,
                                            "sha256": sha(p)} for p, name in sorted(files, key=lambda x: x[1])],
                 "archive_sha256": sha(RUN / f"raw_{phase}.tar.gz")})

def run_phase(phase: str, admission_path: Path, commit: str) -> None:
    require(phase in WATCHDOG, "unknown process phase")
    RUN.mkdir(parents=True, exist_ok=True)
    with (RUN / "parent.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("another parent owns the experiment process lock")
        receipts = rows(RUN / "process_receipts.jsonl")
        expected_prefix = {"controls": [], "science": ["controls"],
                           "checker": ["controls", "science"]}[phase]
        require([row["phase"] for row in receipts] == expected_prefix,
                "phase order/reentry mismatch; no automatic retry")
        verify_admission(admission_path, commit, phase)
        raw = RUN / "raw" / phase
        require(not raw.exists(), "immutable raw phase directory already exists")
        raw.mkdir(parents=True)
        env = fresh_env(raw)
        launch = {"schema": "crypto.autoresearch.n19_launch.v1", "phase": phase,
                  "admission_commit": commit,
                  "admission_path": admission_path.relative_to(REPO).as_posix(),
                  "argv": phase_argv(phase, raw), "started_at": utc()}
        atomic_json(raw / "launch.json", launch)
        stdout, stderr = raw / "stdout.log", raw / "stderr.log"
        sampler = Sampler()
        peak = None
        samples = 0
        cap = watchdog = False
        status = usage = None
        popen_error = None
        started = utc()
        with stdout.open("xb") as out, stderr.open("xb") as err:
            begin = time.monotonic_ns()
            try:
                p = subprocess.Popen(launch["argv"], cwd=raw, env=env,
                                     stdin=subprocess.DEVNULL, stdout=out,
                                     stderr=err, start_new_session=True,
                                     close_fds=True)
            except Exception as exc:
                popen_error = f"{type(exc).__name__}: {exc}"
            if popen_error is None:
                last_sample = 0
                while True:
                    pid, status, usage = os.wait4(p.pid, os.WNOHANG)
                    if pid == p.pid:
                        stop = time.monotonic_ns()
                        break
                    now = time.monotonic_ns()
                    if now - last_sample >= 50_000_000:
                        value = sampler.sample(p.pid)
                        last_sample = now
                        if value is not None:
                            samples += 1
                            peak = value if peak is None else max(peak, value)
                            if value >= CAP_BYTES:
                                cap = True
                    if (now - begin) / 1e9 >= WATCHDOG[phase]:
                        watchdog = True
                    if cap or watchdog:
                        try:
                            os.killpg(p.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        _, status, usage = os.wait4(p.pid, 0)
                        stop = time.monotonic_ns()
                        break
                    time.sleep(.001)
                p.returncode = os.waitstatus_to_exitcode(status)
            else:
                stop = time.monotonic_ns()
            out.flush(); err.flush()
            os.fsync(out.fileno()); os.fsync(err.fileno())
        process_wall = (stop - begin) / 1e9
        after = time.monotonic_ns()
        missing_telemetry = (usage is None or usage.ru_maxrss <= 0 or
                             not all(math.isfinite(v) and v >= 0
                                     for v in (usage.ru_utime, usage.ru_stime)))
        process_valid = (popen_error is None and not cap and not watchdog and
                         p.returncode == 0 and not missing_telemetry)
        output_error = None
        copied = {}
        if process_valid:
            for name in PHASE_FILES[phase]:
                source = raw / name
                if not source.is_file():
                    output_error = f"required {phase} output absent: {name}"
                    break
                if name.endswith(".json"):
                    try:
                        json.loads(source.read_text())
                    except Exception as exc:
                        output_error = f"malformed {name}: {exc}"
                        break
            if output_error is None:
                for name in PHASE_FILES[phase]:
                    source = raw / name
                    destination = RUN / name
                    require(not destination.exists(), f"immutable output already exists: {name}")
                    shutil.copyfile(source, destination)
                    copied[name] = sha(destination)
        valid = process_valid and output_error is None
        record = {"schema": "crypto.autoresearch.n19_process_receipt.v1",
                  "phase": phase, "valid": valid,
                  "classification": "completed_valid" if valid else
                      "censored_watchdog" if watchdog else "censored_memory" if cap else
                      "failed_process_or_output",
                  "error": popen_error or output_error or
                      ("missing or nonfinite wait4 CPU/RSS" if missing_telemetry else None),
                  "argv": launch["argv"], "environment": env,
                  "admission_commit": commit, "started_at": started, "ended_at": utc(),
                  "wall_seconds": process_wall, "wait4": {
                      "exit_code": os.waitstatus_to_exitcode(status) if status is not None else None,
                      "user_seconds": usage.ru_utime if usage else None,
                      "system_seconds": usage.ru_stime if usage else None,
                      "peak_rss": usage.ru_maxrss if usage else None,
                      "rss_unit": "bytes" if platform.system() == "Darwin" else "platform-dependent"},
                  "sampling": {"method": sampler.method, "samples": samples,
                               "peak_bytes": peak, "error": sampler.error,
                               "cap_reached": cap, "continuous_bound": False},
                  "watchdog_reached": watchdog, "watchdog_limit_seconds": WATCHDOG[phase],
                  "copied_output_sha256": copied,
                  "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr),
                  "parent_promotion_seconds": (time.monotonic_ns() - after) / 1e9,
                  "primary_timing_scope": "owned child Popen launch to wait4 reap; parent hashing and promotion excluded"}
        append_receipt(record)
        archive_partial(phase)
        require(valid, f"{phase} process/output invalid; frozen raw evidence preserved")
        if phase == "controls":
            control = json.loads((RUN / "controls.json").read_text())
            require(control.get("status") == "passed", "native controls did not pass")
        elif phase == "science":
            require(json.loads((RUN / "base_scores.json").read_text())["count"] == 66045,
                    "frontier length invalid")
        else:
            require(json.loads((RUN / "independent_replay.json").read_text())["status"] == "passed",
                    "independent checker did not pass")
            finalize()

def finalize() -> None:
    receipts = rows(RUN / "process_receipts.jsonl")
    require([r["phase"] for r in receipts] == ["controls", "science", "checker"] and
            all(r["valid"] for r in receipts), "not all fixed processes valid")
    files = [(p, p.relative_to(RUN).as_posix()) for p in (RUN / "raw").rglob("*") if p.is_file()]
    normalized_tar(files, RUN / "raw_outputs.tar.gz")
    atomic_json(RUN / "raw_manifest.json", {"schema": "crypto.autoresearch.n19_raw_manifest.v1",
                "files": [{"path": name, "bytes": p.stat().st_size, "sha256": sha(p)}
                          for p, name in sorted(files, key=lambda x: x[1])],
                "archive_sha256": sha(RUN / "raw_outputs.tar.gz")})
    selected = json.loads((RUN / "selected.json").read_text())
    replay = json.loads((RUN / "independent_replay.json").read_text())
    phase_order = ("controls", "science", "checker")
    (RUN / "stdout.log").write_bytes(b"".join((RUN / "raw" / phase / "stdout.log").read_bytes()
                                              for phase in phase_order))
    (RUN / "stderr.log").write_bytes(b"".join((RUN / "raw" / phase / "stderr.log").read_bytes()
                                              for phase in phase_order))
    with (RUN / "command.txt").open("w") as stream:
        for receipt in receipts:
            stream.write(json.dumps(receipt["argv"], separators=(",", ":")) + "\n")
    atomic_json(RUN / "raw-result.json", {
        "schema": "crypto.autoresearch.n19_aggregate_raw_result.v1",
        "selected_sha256": sha(RUN / "selected.json"),
        "independent_replay_sha256": sha(RUN / "independent_replay.json"),
        "process_receipts_sha256": sha(RUN / "process_receipts.jsonl"),
        "geometry_sha256": sha(RUN / "geometry.json"),
        "plane_catalogue_sha256": sha(RUN / "plane_catalogue.json"),
        "base_scores_sha256": sha(RUN / "base_scores.json"),
        "support_cache_sha256": sha(RUN / "support_cache.bin"),
        "selected": selected,
        "independent_replay_status": replay["status"],
        "native_control_status": json.loads((RUN / "controls.json").read_text())["status"],
    })
    implementation_commit = receipts[0]["admission_commit"]
    dirty = subprocess.run(["git", "status", "--porcelain", "--",
                            str(EXP.relative_to(REPO))], cwd=REPO, capture_output=True,
                           text=True, check=True).stdout.splitlines()
    manifest = {"run": {
        "id": RUN_ID, "experiment_id": EXPERIMENT, "status": "completed_valid",
        "code": {"commit": implementation_commit, "source_sha256": code_hashes(),
                 "binary_sha256": sha(BINARY), "dirty_scope_at_finalize": dirty,
                 "command": [r["argv"] for r in receipts]},
        "environment": {"path": ENVIRONMENT.name, "sha256": sha(ENVIRONMENT)},
        "inputs": {"parameters": {"n": 19, "pool_orbits": 37,
                                   "public_target_orbits": 6909, "four_orbit_bases": 66045},
                   "pool_sha256": POOL_SHA, "historical_global_jsonl_sha256": HISTORICAL_SHA,
                   "protocol_sha256": PROTOCOL_SHA, "amendment_sha256": AMENDMENT_SHA},
        "timing": {"process_wall_seconds": {r["phase"]: r["wall_seconds"] for r in receipts},
                   "scope": "three distinct owned child Popen-to-wait4-reap intervals, excluding supervisor verification/archive",
                   "parent_promotion_seconds": {r["phase"]: r["parent_promotion_seconds"] for r in receipts},
                   "supervisor_total_wall_cpu_rss": "external root phase measurements; child wall sum is not whole cold search"},
        "artifacts": {"command": "command.txt", "environment": ENVIRONMENT.name,
                      "stdout": "stdout.log", "stderr": "stderr.log",
                      "raw_result": "raw-result.json",
                      "stdout_stderr_scope": "byte-exact concatenation of actual child streams in controls, science, checker order"},
        "result": {"selected": selected, "independent_replay_status": replay["status"],
                   "certificate": {"kind": "decomposition" if selected["candidate_exists"] else "none",
                                   "verified": True,
                                   "verifier": "independent_replay.json",
                                   "scope": "finite coordinate MITM for existing selected/prior/null bases"}},
    }}
    # JSON is a YAML 1.2 subset; the official reader accepts this canonical file.
    (RUN / "manifest.yaml").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    (RUN / "execution_report.md").write_text(
        f"# {RUN_ID} execution report\n\n"
        "Finite public-synthetic N19 coordinate geometry and support only.\n\n"
        f"Native controls, science, and checker process receipts: `process_receipts.jsonl` "
        f"(SHA-256 `{sha(RUN / 'process_receipts.jsonl')}`).\n"
        f"Independent replay: `independent_replay.json` "
        f"(SHA-256 `{sha(RUN / 'independent_replay.json')}`).\n"
        "The Executor records observations and makes no hypothesis, security, "
        "asymptotic, SAT, IC, rho, or status claim.\n")
    print(json.dumps({"status": "all_fixed_processes_complete",
                      "raw_archive_sha256": sha(RUN / "raw_outputs.tar.gz"),
                      "replay_sha256": sha(RUN / "independent_replay.json")}, sort_keys=True))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("build", "controls", "science", "checker"), required=True)
    parser.add_argument("--admission")
    parser.add_argument("--admission-commit")
    args = parser.parse_args()
    if args.phase == "build":
        build()
        return
    require(args.admission and args.admission_commit,
            "root-named committed process admission required")
    run_phase(args.phase, Path(args.admission).resolve(), args.admission_commit)

if __name__ == "__main__":
    main()
