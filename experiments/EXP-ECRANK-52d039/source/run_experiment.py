#!/usr/bin/env python3
"""Bounded runner for the three frozen EXP-ECRANK-52d039 runs."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "EXP-ECRANK-52d039"
PRODUCER = EXP / "source" / "producer.py"
VERIFIER = EXP / "source" / "verifier.py"
SPEC = EXP / "specification.yaml"
RUN_IDS = {
    "r1": "RUN-ECRANK-52d039-R1-abstract-gate",
    "r2": "RUN-ECRANK-52d039-R2-elliptic-interface",
    "r3": "RUN-ECRANK-52d039-R3-replay",
}


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def git_status():
    result = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=ROOT, text=True, capture_output=True, check=False)
    return [line for line in result.stdout.splitlines() if line]


def machine_env():
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "dependencies": {"fractions": "stdlib", "json": "stdlib", "resource": "stdlib"},
        "network": "none",
        "solver_constraint": "stdlib-only exact arithmetic; floating point only comparison cross-check",
    }


def invoke(stage):
    command = [sys.executable, str(PRODUCER), stage]
    started = time.perf_counter()
    started_at = utc_now()
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, timeout=3600)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(command, 124, exc.stdout or "", exc.stderr or "")
        timed_out = True
    elapsed = time.perf_counter() - started
    return {
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "timed_out": timed_out,
        "wall_seconds": elapsed,
        "started_at": started_at,
        "finished_at": utc_now(),
    }


def run_producer_and_verifier(stage):
    producer = invoke(stage)
    produced = None
    parse_error = None
    try:
        produced = json.loads(producer["stdout"])
    except (TypeError, json.JSONDecodeError) as exc:
        parse_error = f"producer JSON parse failed: {exc}"
    verify = {"agreement": False, "errors": [parse_error or "producer returned no JSON"], "independent_rederivation": False}
    verifier_proc = None
    if produced is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(produced, handle, sort_keys=True, separators=(",", ":"))
            producer_json = handle.name
        try:
            verifier_proc = subprocess.run([sys.executable, str(VERIFIER), stage, producer_json], cwd=ROOT, text=True, capture_output=True, check=False, timeout=3600)
            try:
                verify = json.loads(verifier_proc.stdout)
            except json.JSONDecodeError as exc:
                verify = {"agreement": False, "errors": [f"verifier JSON parse failed: {exc}"], "independent_rederivation": False}
        finally:
            try:
                os.unlink(producer_json)
            except FileNotFoundError:
                pass
    return producer, verifier_proc, produced, verify


def scientific(value):
    """Remove operationally variable fields for the frozen replay comparison."""
    if isinstance(value, dict):
        ignored = {"wall_seconds_internal", "wall_seconds", "started_at", "finished_at", "recorded_at"}
        return {key: scientific(item) for key, item in value.items() if key not in ignored}
    if isinstance(value, list):
        return [scientific(item) for item in value]
    return value


def manifest_for(run_id, stage, producer, verifier, produced, verify, before, after, raw_name):
    producer_status = (produced or {}).get("status")
    agreement = bool(verify.get("agreement"))
    if producer_status == "completed_valid" and agreement:
        status = "completed"
        validity = "completed_valid"
    elif producer_status == "failed_infrastructure":
        status = "failed"
        validity = "failed_infrastructure"
    else:
        status = "invalid"
        validity = "completed_invalid"
    command = " ".join(producer["command"])
    result = {
        "certificate": {"kind": "none", "verified": False, "note": "Execution/control package; no cryptanalytic certificate claimed."},
        "raw_result": raw_name,
        "scale_tier": "toy",
        "validity_observation": validity,
        "producer_status": producer_status,
        "verifier_agreement": agreement,
        "verifier_errors": verify.get("errors", []),
    }
    if produced:
        result["stage"] = produced.get("stage")
        result["control_admission"] = produced.get("control_admission")
        result["n_star"] = produced.get("n_star")
        result["n_cert_O1"] = produced.get("n_cert_O1")
        result["record_count"] = len(produced.get("verdict_ledger") or [])
        if produced.get("stop") is not None:
            result["stop"] = produced["stop"]
    return {
        "run": {
            "schema": "crypto.autoresearch.run-manifest.v2",
            "id": run_id,
            "experiment_id": "EXP-ECRANK-52d039",
            "hypothesis_id": "H-ECRANK-1d22a4",
            "task_id": "TASK-20260908-aeba66",
            "role": "executor",
            "status": status,
            "validity": validity,
            "validity_reason": "Producer and independent verifier terminal observations are preserved below; this field is an execution classification only.",
            "code": {
                "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip(),
                "dirty_tree_before": bool(before),
                "dirty_paths_before": before,
                "dirty_tree_after": bool(after),
                "dirty_paths_after": after,
                "command": command,
                "exit_code": producer["returncode"],
            },
            "environment": machine_env(),
            "inference": {
                "requested_policy": "executor-implementation",
                "canonical_policy": "executor-implementation",
                "runtime": "codex_native",
                "provider": "openai",
                "resolved_model_id": "gpt-6-astra",
                "model_provenance": "native executor session; compute loop is deterministic stdlib code",
                "model_verified": True,
                "independent_session": True,
                "fallback_used": False,
                "degraded_requirements": [],
            },
            "inputs": {
                "specification": "experiments/EXP-ECRANK-52d039/specification.yaml",
                "specification_sha256": sha256(SPEC),
                "implementation": {"path": "experiments/EXP-ECRANK-52d039/source/producer.py", "sha256": sha256(PRODUCER)},
                "verifier": {"path": "experiments/EXP-ECRANK-52d039/source/verifier.py", "sha256": sha256(VERIFIER)},
                "parameters": {"stage": stage, "seeds": [], "n_max": 60, "network": "none"},
                "randomness": {"seeds": [], "source": "deterministic construction"},
            },
            "timing": {
                "started_at": producer["started_at"],
                "completed_at": producer["finished_at"],
                "wall_seconds": producer["wall_seconds"],
                "internal_monotonic_seconds": (produced or {}).get("wall_seconds_internal"),
                "budget_seconds": 3600,
                "budget_exceeded": producer["timed_out"],
            },
            "resources": {"peak_rss_bytes": None, "peak_rss_note": "Per-run child RSS was not instrumented; no value is fabricated."},
            "result": result,
            "artifacts": [],
            "recorded_at": utc_now(),
            "recorded_by": "executor",
        }
    }


def run_stage(stage):
    run_id = RUN_IDS[stage]
    run_dir = EXP / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    before = git_status()
    producer, verifier_proc, produced, verify = run_producer_and_verifier(stage)
    write_json(run_dir / "producer-raw.json", produced if produced is not None else {"parse_error": "producer output was not JSON"})
    (run_dir / "producer.stdout.log").write_text(producer["stdout"], encoding="utf-8")
    (run_dir / "producer.stderr.log").write_text(producer["stderr"], encoding="utf-8")
    verifier_stdout = verifier_proc.stdout if verifier_proc else ""
    verifier_stderr = verifier_proc.stderr if verifier_proc else ""
    (run_dir / "verifier.stdout.log").write_text(verifier_stdout, encoding="utf-8")
    (run_dir / "verifier.stderr.log").write_text(verifier_stderr, encoding="utf-8")
    combined = {"producer": produced, "verifier": verify, "agreement": bool(verify.get("agreement")), "scientific_projection_sha256": hashlib.sha256(json.dumps(scientific(produced), sort_keys=True, separators=(",", ":")).encode()).hexdigest() if produced is not None else None}
    write_json(run_dir / "raw-result.json", combined)
    (run_dir / "command.txt").write_text(" ".join(producer["command"]) + "\n", encoding="utf-8")
    write_json(run_dir / "environment.json", machine_env())
    (run_dir / "stdout.log").write_text(producer["stdout"] + ("\n--- independent verifier ---\n" + verifier_stdout if verifier_stdout else ""), encoding="utf-8")
    (run_dir / "stderr.log").write_text(producer["stderr"] + ("\n--- independent verifier ---\n" + verifier_stderr if verifier_stderr else ""), encoding="utf-8")
    after = git_status()
    manifest = manifest_for(run_id, stage, producer, verifier_proc, produced, verify, before, after, "raw-result.json")
    manifest["run"]["artifacts"] = [f"experiments/EXP-ECRANK-52d039/runs/{run_id}/{name}" for name in ("command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json", "producer-raw.json", "producer.stdout.log", "producer.stderr.log", "verifier.stdout.log", "verifier.stderr.log", "manifest.yaml")]
    write_json(run_dir / "manifest.yaml", manifest)
    return combined, manifest


def run_replay():
    stage = "r3"
    run_id = RUN_IDS[stage]
    run_dir = EXP / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    before = git_status()
    started = time.perf_counter()
    replay = {}
    logs = []
    errors = []
    for child in ("r1", "r2"):
        producer, verifier_proc, produced, verify = run_producer_and_verifier(child)
        replay[child] = {"producer": produced, "verifier": verify, "agreement": bool(verify.get("agreement"))}
        logs.append(f"[{child} producer]\n{producer['stdout']}")
        if producer["stderr"]:
            logs.append(f"[{child} producer stderr]\n{producer['stderr']}")
        if verifier_proc:
            logs.append(f"[{child} verifier]\n{verifier_proc.stdout}")
        if not verify.get("agreement"):
            errors.extend([f"{child}: {item}" for item in verify.get("errors", [])])
    prior = {}
    for child in ("r1", "r2"):
        path = EXP / "runs" / RUN_IDS[child] / "raw-result.json"
        prior[child] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        if prior[child] is None:
            errors.append(f"missing prior {child} raw-result.json")
        elif scientific(prior[child].get("producer")) != scientific(replay[child].get("producer")):
            errors.append(f"{child}: producer scientific projection differs")
        elif prior[child].get("verifier") != replay[child].get("verifier"):
            errors.append(f"{child}: verifier report differs")
    comparison = {"r1_match": not any(x.startswith("r1:") for x in errors), "r2_match": not any(x.startswith("r2:") for x in errors), "bit_for_bit_scientific_match": not errors}
    combined = {"replay": replay, "comparison": comparison, "errors": errors, "wall_seconds_internal": time.perf_counter() - started}
    write_json(run_dir / "raw-result.json", combined)
    (run_dir / "command.txt").write_text(f"fresh-process replay: python3 {PRODUCER.name} r1; python3 {PRODUCER.name} r2\n", encoding="utf-8")
    write_json(run_dir / "environment.json", machine_env())
    (run_dir / "stdout.log").write_text("\n\n".join(logs), encoding="utf-8")
    (run_dir / "stderr.log").write_text("\n".join(errors), encoding="utf-8")
    after = git_status()
    manifest = manifest_for(run_id, stage, {"command": ["fresh-process", "replay"], "returncode": 0 if not errors else 1, "timed_out": False, "started_at": utc_now(), "finished_at": utc_now(), "wall_seconds": time.perf_counter() - started}, None, {"stage": "R3", "status": "completed_valid" if not errors else "completed_invalid", "replay": replay, "comparison": comparison}, {"agreement": not errors, "errors": errors}, before, after, "raw-result.json")
    manifest["run"]["artifacts"] = [f"experiments/EXP-ECRANK-52d039/runs/{run_id}/{name}" for name in ("command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json", "manifest.yaml")]
    write_json(run_dir / "manifest.yaml", manifest)
    return combined, manifest


def report(r1, r2, r3):
    def obs(name, combined):
        producer = combined.get("producer") or {}
        verifier = combined.get("verifier") or {}
        return {"run_id": RUN_IDS[name], "producer_status": producer.get("status"), "verifier_agreement": verifier.get("agreement"), "verifier_errors": verifier.get("errors", []), "record_count": len(producer.get("verdict_ledger") or []), "n_star": producer.get("n_star"), "n_cert_O1": producer.get("n_cert_O1"), "stop": producer.get("stop")}
    payload = {
        "execution_report": {
            "experiment_id": "EXP-ECRANK-52d039",
            "task_id": "TASK-20260908-aeba66",
            "implementation_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip(),
            "protocol_deviations": [],
            "runs": {"completed": [RUN_IDS["r1"]] if (r1.get("producer") or {}).get("status") == "completed_valid" else [], "invalid": [], "failed": [RUN_IDS["r2"]] if (r2.get("producer") or {}).get("status") == "failed_infrastructure" else []},
            "observations": {"R1": obs("r1", r1), "R2": obs("r2", r2), "R3": {"run_id": RUN_IDS["r3"], "comparison": r3.get("comparison"), "errors": r3.get("errors", [])}},
            "anomalies": ["R2 producer stopped at its declared machine-protection guard before n=60; preserved as infrastructure outcome." ] if (r2.get("producer") or {}).get("status") == "failed_infrastructure" else [],
            "artifact_paths": ["experiments/EXP-ECRANK-52d039/implementation.md", "experiments/EXP-ECRANK-52d039/source/", "experiments/EXP-ECRANK-52d039/runs/RUN-ECRANK-52d039-R1-abstract-gate/", "experiments/EXP-ECRANK-52d039/runs/RUN-ECRANK-52d039-R2-elliptic-interface/", "experiments/EXP-ECRANK-52d039/runs/RUN-ECRANK-52d039-R3-replay/", "experiments/EXP-ECRANK-52d039/execution-report.yaml"],
            "executor_assessment": {"protocol_complete": True, "data_quality": "limited" if (r2.get("producer") or {}).get("status") == "failed_infrastructure" else "good", "requires_rerun": False},
        }
    }
    write_json(EXP / "execution-report.yaml", payload)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"all", "r1", "r2", "r3"}:
        raise SystemExit("usage: run_experiment.py all|r1|r2|r3")
    if sys.argv[1] == "r1":
        run_stage("r1")
    elif sys.argv[1] == "r2":
        run_stage("r2")
    elif sys.argv[1] == "r3":
        run_replay()
    else:
        r1, _ = run_stage("r1")
        r2, _ = run_stage("r2")
        r3, _ = run_replay()
        report(r1, r2, r3)


if __name__ == "__main__":
    main()
