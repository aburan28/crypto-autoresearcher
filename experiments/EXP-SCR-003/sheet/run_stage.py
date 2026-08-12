#!/usr/bin/env python3
"""EXP-SCR-003 per-run driver.

Executes one planned run of the frozen screen: spawns sheet/apply_screen.py
for the declared stage under a hard 1800 s wall-clock timeout, captures
stdout/stderr byte-exactly, measures wall-clock, CPU seconds, and peak RSS,
enforces the 4 GB memory budget post-hoc against the measured peak RSS
(darwin rejects setrlimit(RLIMIT_AS); mechanism recorded in the manifest),
maps the outcome to a lifecycle terminal status, and writes the immutable run
record.

Artifact naming: the frozen specification's required_artifacts names
{manifest.yaml, command.txt, environment.json, raw-result.json, stdout.log,
stderr.log}; the handoff deliverables name {manifest.yaml, command.txt,
environment.json, raw.json, summary.json, stdout.txt, stderr.txt}. Both sets
are emitted; paired files are byte-identical (raw.json == raw-result.json,
stdout.txt == stdout.log, stderr.txt == stderr.log). The deviation is recorded
in the manifest and the execution report.

Terminal-status mapping:
  exit 0 + result.valid           -> completed_valid
  exit 0 + not result.valid       -> completed_invalid
  exit 3 (control failure)        -> completed_invalid
  exit 4 (undecidable_with_reason)-> completed_valid, inconclusive=true
  exit 2 / other                  -> failed_implementation
  wall-clock timeout (1800 s)     -> resource_exhaustion
  peak RSS > 4 GB (post-hoc)      -> resource_exhaustion

stdlib + PyYAML only.
"""

import argparse
import hashlib
import json
import platform
import resource
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

EXP_DIR_REL = "experiments/EXP-SCR-003"
TIMEOUT_SECONDS = 1800
MEMORY_CAP_BYTES = 4 * 1024 ** 3

STAGE_BY_RUN = {
    "RUN-SCR-003-A": "freeze_and_calibrate",
    "RUN-SCR-003-A-b": "freeze_and_calibrate",
    "RUN-SCR-003-B": "dedup_classification",
    "RUN-SCR-003-C": "ns_tx_application_and_aggregate",
}

# Repaired re-executions (failure taxonomy: implementation_error requires
# repair; the failed attempt's run record is preserved, never overwritten).
REPAIR_OF = {
    "RUN-SCR-003-A-b": {
        "repair_of": "RUN-SCR-003-A",
        "repair_reason": ("RUN-SCR-003-A terminated failed_implementation "
                          "(KeyError: 'calibration_fixtures' — wrong spec key "
                          "path in run_calibration). Implementation repaired; "
                          "frozen protocol unchanged; no completed run "
                          "re-scored."),
    },
}

NAMING_DEVIATION = (
    "Handoff TASK-20260727-008 deliverables name per-run artifacts raw.json, "
    "summary.json, stdout.txt, stderr.txt; frozen specification "
    "required_artifacts names raw-result.json, stdout.log, stderr.log. Both "
    "naming sets emitted; paired files are byte-identical "
    "(raw.json==raw-result.json, stdout.txt==stdout.log, "
    "stderr.txt==stderr.log); summary.json is handoff-only. Recorded per "
    "executor instruction; no protocol content changed."
)

DIRTY_BASIS = (
    "git status --porcelain over the worktree at run start; lines whose path "
    "has any component beginning '._' (exFAT AppleDouble artifacts of this "
    "volume) excluded; untracked ('??') lines excluded per task basis "
    "'non-._ tracked paths'. dirty=true iff any tracked, non-._ path is "
    "modified."
)

PEAK_RSS_BASIS = (
    "max(resource.getrusage(RUSAGE_SELF).ru_maxrss, "
    "resource.getrusage(RUSAGE_CHILDREN).ru_maxrss) sampled after child "
    "exit; on darwin ru_maxrss is bytes. Bounds the screen process peak RSS."
)

CPU_BASIS = (
    "RUSAGE_CHILDREN ru_utime+ru_stime delta around the child, plus driver "
    "RUSAGE_SELF ru_utime+ru_stime delta; seconds."
)


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_commit(repo_root):
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root,
                          capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else None


def git_dirty(repo_root):
    proc = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        if line.startswith("??"):
            continue  # untracked excluded per disclosed basis
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        components = path.replace('"', "").split("/")
        if any(c.startswith("._") for c in components):
            continue  # exFAT AppleDouble excluded per disclosed basis
        return True
    return False


def environment_record(repo_root):
    git_ver = subprocess.run(["git", "--version"], cwd=repo_root,
                             capture_output=True, text=True)
    return {
        "operating_system": "%s %s" % (platform.system(), platform.release()),
        "os_product_version": platform.mac_ver()[0] or None,
        "architecture": platform.machine(),
        "sage_version": None,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "dependencies": {"pyyaml": yaml.__version__},
        "git_version": (git_ver.stdout.strip() if git_ver.returncode == 0
                        else None),
        "cwd": repo_root,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="EXP-SCR-003 run driver")
    parser.add_argument("--repo-root",
                        default=str(Path(__file__).resolve().parents[3]))
    parser.add_argument("--run-id", required=True, choices=sorted(STAGE_BY_RUN))
    parser.add_argument("--stage", default=None)
    args = parser.parse_args(argv)

    repo_root = str(Path(args.repo_root).resolve())
    run_id = args.run_id
    stage = args.stage or STAGE_BY_RUN[run_id]
    if stage != STAGE_BY_RUN[run_id]:
        print("stage %r does not match planned stage %r for %s"
              % (stage, STAGE_BY_RUN[run_id], run_id), file=sys.stderr)
        return 2

    run_dir = Path(repo_root) / EXP_DIR_REL / "runs" / run_id
    if run_dir.exists():
        print("run directory %s already exists; run records are immutable"
              % run_dir, file=sys.stderr)
        return 2
    run_dir.mkdir(parents=True)

    result_rel = "%s/runs/%s/raw-result.json" % (EXP_DIR_REL, run_id)
    screen_argv = [sys.executable,
                   "%s/sheet/apply_screen.py" % EXP_DIR_REL,
                   "--repo-root", repo_root,
                   "--stage", stage,
                   "--run-id", run_id,
                   "--result-path", result_rel]
    command_str = " ".join(shlex.quote(a) for a in screen_argv)
    driver_argv = [sys.executable] + sys.argv
    driver_str = " ".join(shlex.quote(a) for a in driver_argv)

    (run_dir / "command.txt").write_text(command_str + "\n", encoding="utf-8")
    env = environment_record(repo_root)
    env["driver_command"] = driver_str
    (run_dir / "environment.json").write_text(
        json.dumps(env, indent=2) + "\n", encoding="utf-8")

    commit = git_commit(repo_root)
    dirty = git_dirty(repo_root)

    self0 = resource.getrusage(resource.RUSAGE_SELF)
    child0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    started_at = utcnow()
    t0 = time.monotonic()
    timed_out = False
    proc = None
    stdout_bytes = b""
    stderr_bytes = b""
    try:
        proc = subprocess.run(screen_argv, cwd=repo_root, capture_output=True,
                              timeout=TIMEOUT_SECONDS)
        stdout_bytes = proc.stdout or b""
        stderr_bytes = proc.stderr or b""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout_bytes = exc.stdout or b""
        stderr_bytes = exc.stderr or b""
        if isinstance(stdout_bytes, str):
            stdout_bytes = stdout_bytes.encode("utf-8", "replace")
        if isinstance(stderr_bytes, str):
            stderr_bytes = stderr_bytes.encode("utf-8", "replace")
    except Exception as exc:  # driver-level infrastructure failure
        stderr_bytes = ("driver infrastructure error: %s: %s"
                        % (type(exc).__name__, exc)).encode("utf-8")
    wall = time.monotonic() - t0
    finished_at = utcnow()
    self1 = resource.getrusage(resource.RUSAGE_SELF)
    child1 = resource.getrusage(resource.RUSAGE_CHILDREN)

    cpu_seconds = ((child1.ru_utime + child1.ru_stime)
                   - (child0.ru_utime + child0.ru_stime)
                   + (self1.ru_utime + self1.ru_stime)
                   - (self0.ru_utime + self0.ru_stime))
    peak_rss = max(self1.ru_maxrss, child1.ru_maxrss)  # darwin: bytes

    (run_dir / "stdout.log").write_bytes(stdout_bytes)
    (run_dir / "stderr.log").write_bytes(stderr_bytes)

    result_path = run_dir / "raw-result.json"
    result_synthesized = False
    if result_path.is_file():
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception:
            result = None
    else:
        result = None
    if result is None:
        result_synthesized = True
        result = {"run_id": run_id, "experiment_id": "EXP-SCR-003",
                  "stage": stage, "valid": False,
                  "invalid_reason": "implementation_error",
                  "error": "screen process produced no parseable raw-result.json",
                  "synthesized_by_driver": True}
        result_path.write_text(json.dumps(result, indent=2) + "\n",
                               encoding="utf-8")

    exit_code = None if proc is None else proc.returncode

    # Terminal-status classification (failure taxonomy, agents/executor.md).
    if timed_out:
        status = "resource_exhaustion"
        valid, inconclusive = False, False
        invalid_reason = "timeout_exceeded_%ds" % TIMEOUT_SECONDS
    elif peak_rss > MEMORY_CAP_BYTES:
        status = "resource_exhaustion"
        valid, inconclusive = False, False
        invalid_reason = "memory_cap_exceeded_posthoc_peak_rss_%d_bytes" % peak_rss
    elif proc is None:
        status = "failed_infrastructure"
        valid, inconclusive = False, False
        invalid_reason = "driver_spawn_failure"
    elif exit_code == 0 and result.get("valid"):
        status = "completed_valid"
        valid = True
        inconclusive = bool(result.get("inconclusive"))
        invalid_reason = None
    elif exit_code == 0:
        status = "completed_invalid"
        valid, inconclusive = False, False
        invalid_reason = result.get("invalid_reason") or "result_validity_false"
    elif exit_code == 3:
        status = "completed_invalid"
        valid, inconclusive = False, False
        invalid_reason = result.get("invalid_reason") or "control_failure"
    elif exit_code == 4:
        # Spec stage stop rule: run inconclusive (not negative, not invalid);
        # undecidable_with_reason recorded per family.
        status = "completed_valid"
        valid, inconclusive = True, True
        invalid_reason = None
    else:
        status = "failed_implementation"
        valid, inconclusive = False, False
        invalid_reason = result.get("invalid_reason") or "implementation_error"

    # Handoff-only naming set: byte-identical pairs plus summary.json.
    (run_dir / "raw.json").write_bytes(result_path.read_bytes())
    (run_dir / "stdout.txt").write_bytes(stdout_bytes)
    (run_dir / "stderr.txt").write_bytes(stderr_bytes)
    summary = {
        "run_id": run_id,
        "experiment_id": "EXP-SCR-003",
        "stage": stage,
        "status": status,
        "valid": valid,
        "inconclusive": inconclusive,
        "invalid_reason": invalid_reason,
        "metrics": result.get("metrics"),
        "calibration_accuracy": (result.get("calibration") or {}).get("accuracy"),
        "admitted_family_count": result.get("admitted_family_count"),
        "corpus_pass": (result.get("corpus") or {}).get("pass"),
        "wall_seconds": wall,
        "cpu_seconds": cpu_seconds,
        "peak_rss_bytes": peak_rss,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    artifacts = {}
    for name in ("command.txt", "environment.json", "raw-result.json",
                 "raw.json", "summary.json", "stdout.log", "stdout.txt",
                 "stderr.log", "stderr.txt"):
        artifacts["%s/runs/%s/%s" % (EXP_DIR_REL, run_id, name)] = \
            sha256_file(run_dir / name)
    for rel, produced in ((EXP_DIR_REL + "/corpus_manifest.json",
                           stage == "freeze_and_calibrate"),
                          (EXP_DIR_REL + "/sheet/calibration_receipt.json",
                           stage == "freeze_and_calibrate"),
                          (EXP_DIR_REL + "/family_table.json",
                           stage == "ns_tx_application_and_aggregate"),
                          (EXP_DIR_REL + "/admission_decision.json",
                           stage == "ns_tx_application_and_aggregate")):
        p = Path(repo_root) / rel
        if produced and p.is_file():
            artifacts[rel] = sha256_file(p)

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-SCR-003",
            "hypothesis_id": "H-SCR-003",
            "handoff_id": "TASK-20260727-008",
            "stage": stage,
            "status": status,
            "repair": REPAIR_OF.get(run_id),
            "code": {
                "commit": commit,
                "dirty": dirty,
                "dirty_basis": DIRTY_BASIS,
                "command": command_str,
                "argv": screen_argv,
                "driver_command": driver_str,
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "degraded_allowed": False,
                "adapter_version": None,
                "model_verified": False,
                "note": ("Deterministic stdlib+PyYAML screen; the run itself "
                         "performs no model inference. Policy recorded from "
                         "handoff TASK-20260727-008."),
            },
            "environment": {
                "operating_system": env["operating_system"],
                "os_product_version": env["os_product_version"],
                "architecture": env["architecture"],
                "sage_version": None,
                "python_version": env["python_version"],
                "dependencies": env["dependencies"],
                "git_version": env["git_version"],
            },
            "inputs": {
                "curve_id": None,
                "seed": None,
                "seeds": [],
                "seed_policy": "deterministic audit, no randomness",
                "parameters": {
                    "stage": stage,
                    "pinned_commit": "b8af1551e45fbe4435745239d29f4d141eea3356",
                    "specification": EXP_DIR_REL + "/specification.yaml",
                },
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": wall,
            },
            "resources": {
                "peak_rss_bytes": peak_rss,
                "peak_rss_basis": PEAK_RSS_BASIS,
                "cpu_seconds": cpu_seconds,
                "cpu_basis": CPU_BASIS,
                "memory_cap_bytes": MEMORY_CAP_BYTES,
                "memory_cap_enforcement": (
                    "post-hoc: measured peak RSS compared against the 4 GB "
                    "cap after child exit; darwin rejects setrlimit(RLIMIT_AS) "
                    "so no pre-hoc address-space limit was installed"),
                "timeout_seconds": TIMEOUT_SECONDS,
                "timeout_enforcement": (
                    "subprocess hard timeout (kill on expiry), enforced by "
                    "sheet/run_stage.py"),
                "timed_out": timed_out,
            },
            "result": {
                "metrics": {
                    "calibration_accuracy": summary["calibration_accuracy"],
                    "corpus_pass": summary["corpus_pass"],
                    "admitted_family_count": summary["admitted_family_count"],
                    "metrics": result.get("metrics"),
                },
                "valid": valid,
                "inconclusive": inconclusive,
                "invalid_reason": invalid_reason,
                "raw_result_synthesized_by_driver": result_synthesized,
                "screen_exit_code": exit_code,
                "certificate": {"kind": "none", "verified": None,
                                "verifier": None},
            },
            "artifacts": artifacts,
            "protocol_deviations": (
                [NAMING_DEVIATION]
                + ([REPAIR_OF[run_id]["repair_reason"]]
                   if run_id in REPAIR_OF else [])),
            "anomalies": [],
        },
    }
    with open(run_dir / "manifest.yaml", "w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=100)

    print(json.dumps({"run_id": run_id, "stage": stage, "status": status,
                      "valid": valid, "inconclusive": inconclusive,
                      "wall_seconds": wall, "cpu_seconds": cpu_seconds,
                      "peak_rss_bytes": peak_rss}, sort_keys=True))
    return 0 if status in ("completed_valid", "completed_invalid") else 1


if __name__ == "__main__":
    sys.exit(main())
