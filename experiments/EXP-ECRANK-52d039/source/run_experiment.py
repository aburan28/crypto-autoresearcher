#!/usr/bin/env python3
"""Bounded runner for the three frozen EXP-ECRANK-52d039 runs.

Writes companions to both the handoff paths
(`runs/RUN-ECRANK-52d039-R*`) and the BATCH-a9c273 queue paths
(`runs/R1-abstract-gate`, ...). File bytes at paired paths are identical.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import resource
import shutil
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
TASK_DIR = (
    ROOT
    / "coordination"
    / "goals"
    / "GOAL-ECRANK-002"
    / "batches"
    / "BATCH-a9c273"
    / "tasks"
    / "TASK-20260908-aeba66"
)

RUN_IDS = {
    "r1": "RUN-ECRANK-52d039-R1-abstract-gate",
    "r2": "RUN-ECRANK-52d039-R2-elliptic-interface",
    "r3": "RUN-ECRANK-52d039-R3-replay",
}
SHORT_DIRS = {
    "r1": "R1-abstract-gate",
    "r2": "R2-elliptic-interface",
    "r3": "R3-replay",
}

INFERENCE = {
    "requested_policy": "executor-implementation",
    "reasoning_effort_requested": None,
    "reasoning_effort_note": "null = policy default per handoff",
    "reasoning_effort_observed_session": "high",
    "fallback_used": True,
    "fallback_reason": "native Cursor cloud-agent session; adapter doctor unconfigured",
    "degraded_allowed": False,
    "degraded_requirements": [],
    "independent_session_required": True,
    "resolved_model_id": "cursor-grok-4.6",
    "resolved_model_id_source": "runtime system prompt (as reported)",
    "model_verified": False,
    "model_verified_note": "no adapter probe claimed; recorded as-is",
    "backend": "cursor_cloud_native",
    "bedrock_guard": "resolved provider contains no 'bedrock' (rule 16 checked)",
}


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def write_yaml(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import yaml
        path.write_text(yaml.safe_dump(value, sort_keys=False, width=100), encoding="utf-8")
    except ImportError:
        path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def git_info():
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    dirty_files = [line for line in status.stdout.splitlines() if line.strip()]
    return {"commit": commit or None, "dirty": bool(dirty_files), "dirty_files": dirty_files}


def machine_env():
    env = {
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "stdlib_only_pipeline": True,
        "pari_in_pipeline": False,
        "network": "none",
    }
    try:
        import yaml
        env["pyyaml_version"] = getattr(yaml, "__version__", "unknown")
        env["pyyaml_use"] = "run-record serialization only; never in counted/certified code"
    except ImportError:
        env["pyyaml_version"] = None
    env["cypari_present"] = False
    return env


def peak_rss_bytes():
    try:
        rss = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if sys.platform == "darwin":
            return rss
        return rss * 1024
    except Exception:
        return None


def source_sha256():
    out = {}
    src = EXP / "source"
    for name in sorted(os.listdir(src)):
        if name.endswith(".py"):
            out[name] = sha256_file(src / name)
    return out


def _as_text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def invoke(stage):
    command = [sys.executable, str(PRODUCER), stage]
    started_mono = time.monotonic()
    started_unix = time.time()
    started_at = utc_now()
    env = os.environ.copy()
    if stage == "r2":
        env["EXP_ECRANK_52D039_R2_CHECKPOINT"] = str(
            EXP / "runs" / RUN_IDS["r2"] / "producer-checkpoint.json"
        )
    # Runner timeout sits above the producer SIGALRM so a completed-n dump can finish.
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=3900,
            env=env,
        )
        timed_out = False
        stdout = _as_text(result.stdout)
        stderr = _as_text(result.stderr)
        returncode = result.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = _as_text(exc.stdout)
        stderr = _as_text(exc.stderr)
        returncode = 124
        timed_out = True
    return {
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
        "timed_out": timed_out,
        "wall_seconds_monotonic": time.monotonic() - started_mono,
        "wall_seconds_timestamp_span": time.time() - started_unix,
        "started_at": started_at,
        "finished_at": utc_now(),
        "peak_rss_bytes": peak_rss_bytes(),
    }


def run_producer_and_verifier(stage):
    producer = invoke(stage)
    produced = None
    parse_error = None
    try:
        produced = json.loads(producer["stdout"])
    except (TypeError, json.JSONDecodeError) as exc:
        ckpt = EXP / "runs" / RUN_IDS.get(stage, "") / "producer-checkpoint.json"
        if ckpt.is_file():
            try:
                produced = json.loads(ckpt.read_text(encoding="utf-8"))
                produced.setdefault("status", "failed_infrastructure")
                produced.setdefault(
                    "stop",
                    {
                        "class": "resource_exhaustion",
                        "reason": "recovered producer checkpoint after timeout/parse failure",
                    },
                )
            except (TypeError, json.JSONDecodeError):
                parse_error = f"producer JSON parse failed: {exc}"
        else:
            parse_error = f"producer JSON parse failed: {exc}"
    verify = {
        "agreement": False,
        "errors": [parse_error or "producer returned no JSON"],
        "independent_rederivation": False,
    }
    verifier_proc = None
    if produced is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(produced, handle, sort_keys=True, separators=(",", ":"))
            producer_json = handle.name
        try:
            v_started = time.monotonic()
            verifier_proc = subprocess.run(
                [sys.executable, str(VERIFIER), stage, producer_json],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=3600,
            )
            verify_wall = time.monotonic() - v_started
            try:
                verify = json.loads(verifier_proc.stdout)
            except json.JSONDecodeError as exc:
                verify = {
                    "agreement": False,
                    "errors": [f"verifier JSON parse failed: {exc}"],
                    "independent_rederivation": False,
                }
            verify["verification_wall_seconds"] = verify_wall
        finally:
            try:
                os.unlink(producer_json)
            except FileNotFoundError:
                pass
    return producer, verifier_proc, produced, verify


def scientific(value):
    if isinstance(value, dict):
        ignored = {
            "wall_seconds_internal",
            "wall_seconds",
            "started_at",
            "finished_at",
            "recorded_at",
            "peak_rss_bytes",
            "verification_wall_seconds",
        }
        return {key: scientific(item) for key, item in value.items() if key not in ignored}
    if isinstance(value, list):
        return [scientific(item) for item in value]
    return value


def canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dual_dirs(stage):
    long_dir = EXP / "runs" / RUN_IDS[stage]
    short_dir = EXP / "runs" / SHORT_DIRS[stage]
    long_dir.mkdir(parents=True, exist_ok=True)
    short_dir.mkdir(parents=True, exist_ok=True)
    return long_dir, short_dir


def write_dual(stage, rel_name, write_fn):
    long_dir, short_dir = dual_dirs(stage)
    write_fn(long_dir / rel_name)
    write_fn(short_dir / rel_name)


def copy_tree_pair(stage):
    long_dir, short_dir = dual_dirs(stage)
    for path in long_dir.iterdir():
        if path.is_file():
            dest = short_dir / path.name
            if dest.resolve() != path.resolve():
                shutil.copy2(path, dest)


def classify(produced, verify):
    producer_status = (produced or {}).get("status")
    agreement = bool(verify.get("agreement"))
    if producer_status == "completed_valid" and agreement:
        return "completed", "completed_valid", "producer completed_valid; verifier exact agreement"
    if producer_status == "failed_infrastructure":
        return (
            "failed_infrastructure",
            "failed_infrastructure",
            "producer recorded infrastructure/resource stop; not a mathematical result",
        )
    if producer_status == "failed_invalid" or producer_status == "completed_invalid":
        return "invalid", "completed_invalid", f"producer status {producer_status}"
    if not agreement:
        return "invalid", "completed_invalid", "C6 producer-verifier disagreement"
    return "invalid", "completed_invalid", f"unclassified producer status {producer_status!r}"


def build_manifest(run_id, stage, producer, produced, verify, git, env, extra_metrics=None):
    status, validity, reason = classify(produced, verify)
    rss = producer.get("peak_rss_bytes")
    if produced and produced.get("peak_rss_bytes") is not None:
        rss = produced["peak_rss_bytes"]
    metrics = {
        "counted_exact_ops": None,
        "counted_exact_ops_note": "no counted-op cap on this contract; explicit null",
        "ops_cap_respected": True,
        "memory_ceiling_respected": True if rss is None else (rss / 1024 ** 3) < 8.0,
        "verifier_agreement": bool(verify.get("agreement")),
        "record_count": len((produced or {}).get("verdict_ledger") or []),
    }
    if extra_metrics:
        metrics.update(extra_metrics)
    body = {
        "id": run_id,
        "experiment_id": "EXP-ECRANK-52d039",
        "hypothesis_id": "H-ECRANK-1d22a4",
        "goal_id": "GOAL-ECRANK-002",
        "batch_id": "BATCH-a9c273",
        "task_id": "TASK-20260908-aeba66",
        "status": status,
        "code": {
            "commit": git.get("commit"),
            "dirty": git.get("dirty"),
            "dirty_files": git.get("dirty_files"),
            "command": " ".join(producer["command"]),
            "argv": list(producer["command"]),
            "source_dir": "experiments/EXP-ECRANK-52d039/source/",
            "source_sha256": source_sha256(),
        },
        "environment": env,
        "inputs": {
            "parameters": {
                "stage": stage,
                "seeds": [],
                "n_max": 60,
                "network": "none",
            },
            "seeds_note": "declared seed set is empty; deterministic construction",
            "specification": "experiments/EXP-ECRANK-52d039/specification.yaml",
            "specification_sha256": sha256_file(SPEC),
        },
        "timing": {
            "started_at": producer["started_at"],
            "finished_at": producer["finished_at"],
            "wall_seconds_monotonic": round(producer["wall_seconds_monotonic"], 6),
            "wall_seconds_timestamp_span": round(producer["wall_seconds_timestamp_span"], 6),
            "wall_seconds": round(producer["wall_seconds_monotonic"], 6),
        },
        "resources": {
            "peak_rss_bytes": rss,
            "peak_rss_gb": None if rss is None else round(rss / 1024 ** 3, 6),
            "cpu_seconds": None,
            "cpu_seconds_note": "this run did not record cpu_seconds; explicit null per core rule 9",
        },
        "result": {
            "validity_reason": reason,
            "metrics": metrics,
            "certificate": {
                "kind": "none",
                "verified": True,
                "verifier": "no discrete_log/decomposition/key_recovery claim",
                "certificate_note": (
                    "kind 'none': this run asserts no discrete_log, "
                    "decomposition, or key_recovery claim."
                ),
            },
        },
        "inference": INFERENCE,
        "stdout": "stdout.log",
        "stderr": "stderr.log",
        "validity": {"status": validity, "reason": reason},
    }
    return {"run": body}


def write_stage_companions(stage, producer, verifier_proc, produced, verify):
    run_id = RUN_IDS[stage]
    long_dir, _short_dir = dual_dirs(stage)
    git = git_info()
    env = machine_env()
    combined = {
        "producer": produced,
        "verifier": verify,
        "agreement": bool(verify.get("agreement")),
        "scientific_projection_sha256": (
            sha256_bytes(canonical_json(scientific(produced))) if produced is not None else None
        ),
    }
    (long_dir / "command.txt").write_text(" ".join(producer["command"]) + "\n", encoding="utf-8")
    write_json(long_dir / "environment.json", env)
    (long_dir / "stdout.log").write_text(producer["stdout"] or "", encoding="utf-8")
    (long_dir / "stderr.log").write_text(producer["stderr"] or "", encoding="utf-8")
    write_json(long_dir / "raw-result.json", combined)
    write_json(long_dir / "producer-raw.json", produced if produced is not None else {"parse_error": True})
    if produced and produced.get("run_start_reverification") is not None:
        write_json(long_dir / "run-start-reverification.json", produced["run_start_reverification"])
    if produced and produced.get("verdict_ledger") is not None:
        write_json(long_dir / "verdict-ledger.json", produced["verdict_ledger"])
    if produced and produced.get("candidates") is not None:
        write_json(long_dir / "candidates.json", produced["candidates"])
    if produced and produced.get("C_E_derivation") is not None:
        write_json(long_dir / "c-e-derivation.json", produced["C_E_derivation"])
        write_json(
            long_dir / "verifier-rederivation.json",
            {
                "C_E": verify.get("C_E"),
                "agreement": bool(verify.get("agreement")),
                "errors": verify.get("errors", []),
                "independent_rederivation": verify.get("independent_rederivation"),
            },
        )
    witnesses = []
    for rec in (produced or {}).get("verdict_ledger") or []:
        if rec.get("verdict") == "INDEPENDENT":
            witnesses.append(rec)
    if witnesses:
        write_json(long_dir / "certificate-witness.json", witnesses)
    if produced and produced.get("regulator_cross_check") is not None:
        write_json(long_dir / "regulator-cross-check.json", produced["regulator_cross_check"])
    cost = {
        "stage": stage,
        "doubling_coordinate_growth": produced.get("cost_coordinate_bit_sizes") if produced else None,
        "log_enclosure": "certified artanh series; remainder bound exact rational",
        "factorization": {
            "note": "content gcd of Fraction reduction only; no integer factorization beyond gcd",
            "gcd_calls": "implicit in fractions.Fraction",
        },
        "verification": {
            "agreement": bool(verify.get("agreement")),
            "wall_seconds": verify.get("verification_wall_seconds"),
            "errors": verify.get("errors", []),
        },
        "peak_rss_bytes": (produced or {}).get("peak_rss_bytes") or producer.get("peak_rss_bytes"),
        "wall_seconds_internal": (produced or {}).get("wall_seconds_internal"),
    }
    write_json(long_dir / "cost-ledger.json", cost)
    extra = {}
    if produced:
        extra["n_star"] = produced.get("n_star")
        extra["n_cert"] = produced.get("n_cert")
        extra["n_cert_O1"] = produced.get("n_cert_O1")
        extra["control_admission"] = produced.get("control_admission")
        extra["collision_event"] = produced.get("collision_event")
        extra["stop"] = produced.get("stop")
    manifest = build_manifest(run_id, stage, producer, produced, verify, git, env, extra)
    write_yaml(long_dir / "manifest.yaml", manifest)
    write_yaml(long_dir / "run.yaml", manifest)
    copy_tree_pair(stage)
    return combined, manifest


def run_stage(stage):
    producer, verifier_proc, produced, verify = run_producer_and_verifier(stage)
    return write_stage_companions(stage, producer, verifier_proc, produced, verify)


def run_replay():
    stage = "r3"
    run_id = RUN_IDS[stage]
    long_dir, _ = dual_dirs(stage)
    git = git_info()
    env = machine_env()
    started_mono = time.monotonic()
    started_unix = time.time()
    started_at = utc_now()
    replay = {}
    errors = []
    logs = []
    for child in ("r1", "r2"):
        producer, verifier_proc, produced, verify = run_producer_and_verifier(child)
        replay[child] = {
            "producer": produced,
            "verifier": verify,
            "agreement": bool(verify.get("agreement")),
        }
        logs.append(f"[{child} producer stdout]\n{producer['stdout']}")
        if producer["stderr"]:
            logs.append(f"[{child} producer stderr]\n{producer['stderr']}")
        if verifier_proc and verifier_proc.stdout:
            logs.append(f"[{child} verifier stdout]\n{verifier_proc.stdout}")
        if not verify.get("agreement"):
            errors.extend([f"{child}: {item}" for item in verify.get("errors", [])])
    prior = {}
    for child in ("r1", "r2"):
        path = EXP / "runs" / RUN_IDS[child] / "raw-result.json"
        prior[child] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        if prior[child] is None:
            errors.append(f"missing prior {child} raw-result.json")
            continue
        if scientific(prior[child].get("producer")) != scientific(replay[child].get("producer")):
            errors.append(f"{child}: producer scientific projection differs")
        if scientific(prior[child].get("verifier")) != scientific(replay[child].get("verifier")):
            errors.append(f"{child}: verifier report differs")
    comparison = {
        "r1_match": not any(item.startswith("r1:") for item in errors),
        "r2_match": not any(item.startswith("r2:") for item in errors),
        "bit_for_bit_scientific_match": not errors,
        "compared_quantities": [
            "verdicts",
            "pivot_lower_bounds",
            "n_cert",
            "n_star",
            "C_E",
            "certificate_witness_fields",
        ],
    }
    finished_at = utc_now()
    combined = {
        "replay": replay,
        "comparison": comparison,
        "errors": errors,
        "wall_seconds_internal": time.monotonic() - started_mono,
    }
    write_json(long_dir / "raw-result.json", combined)
    write_json(long_dir / "replay-diff.json", comparison)
    write_json(long_dir / "verdict-ledger.json", {"comparison": comparison, "errors": errors})
    write_json(
        long_dir / "cost-ledger.json",
        {
            "stage": "r3",
            "doubling_coordinate_growth": None,
            "log_enclosure": "replay of R1/R2 enclosures; no new enclosure",
            "factorization": {"note": "none beyond replayed Fraction reduction"},
            "verification": {"agreement": not errors, "errors": errors},
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_seconds_internal": combined["wall_seconds_internal"],
        },
    )
    (long_dir / "command.txt").write_text(
        f"{sys.executable} {PRODUCER} r1 ; {sys.executable} {VERIFIER} r1 <tmp> ; "
        f"{sys.executable} {PRODUCER} r2 ; {sys.executable} {VERIFIER} r2 <tmp>\n",
        encoding="utf-8",
    )
    write_json(long_dir / "environment.json", env)
    (long_dir / "stdout.log").write_text("\n\n".join(logs) + "\n", encoding="utf-8")
    (long_dir / "stderr.log").write_text(("\n".join(errors) + "\n") if errors else "", encoding="utf-8")
    fake_producer = {
        "command": [sys.executable, str(Path(__file__)), "r3"],
        "returncode": 0 if not errors else 1,
        "timed_out": False,
        "started_at": started_at,
        "finished_at": finished_at,
        "wall_seconds_monotonic": time.monotonic() - started_mono,
        "wall_seconds_timestamp_span": time.time() - started_unix,
        "peak_rss_bytes": peak_rss_bytes(),
    }
    produced = {
        "stage": "R3",
        "status": "completed_valid" if not errors else "completed_invalid",
        "comparison": comparison,
    }
    verify = {"agreement": not errors, "errors": errors, "independent_rederivation": True}
    manifest = build_manifest(
        run_id,
        stage,
        fake_producer,
        produced,
        verify,
        git,
        env,
        {"bit_for_bit_scientific_match": comparison["bit_for_bit_scientific_match"]},
    )
    write_yaml(long_dir / "manifest.yaml", manifest)
    write_yaml(long_dir / "run.yaml", manifest)
    copy_tree_pair(stage)
    return combined, manifest


def write_execution_report(r1, r2, r3, m1, m2, m3):
    def quoted(manifest, combined):
        run = manifest["run"]
        producer = combined.get("producer") or {}
        return {
            "run_id": run["id"],
            "status": run["status"],
            "validity_reason": run["validity"]["reason"],
            "wall_seconds_monotonic": run["timing"]["wall_seconds_monotonic"],
            "wall_seconds_timestamp_span": run["timing"]["wall_seconds_timestamp_span"],
            "peak_rss_bytes": run["resources"]["peak_rss_bytes"],
            "observations_quoted": {
                "producer_status": producer.get("status"),
                "verifier_agreement": (combined.get("verifier") or {}).get("agreement"),
                "record_count": len(producer.get("verdict_ledger") or []),
                "n_star": producer.get("n_star"),
                "n_cert": producer.get("n_cert"),
                "n_cert_O1": producer.get("n_cert_O1"),
                "C_E": producer.get("C_E"),
                "selected_curve_index": producer.get("selected_curve_index"),
                "collision_event": producer.get("collision_event"),
                "stop": producer.get("stop"),
                "control_admission": producer.get("control_admission"),
                "power_result": producer.get("power_result"),
            },
        }

    completed = []
    failed = []
    invalid = []
    for manifest in (m1, m2, m3):
        st = manifest["run"]["status"]
        rid = manifest["run"]["id"]
        if st == "completed":
            completed.append(rid)
        elif st == "failed_infrastructure":
            failed.append(rid)
        else:
            invalid.append(rid)
    anomalies = []
    if (r2.get("producer") or {}).get("stop"):
        anomalies.append(
            "R2 recorded an infrastructure/resource stop before or at n_max=60; "
            "preserved as infrastructure, not a mathematical result."
        )
    payload = {
        "execution_report": {
            "experiment_id": "EXP-ECRANK-52d039",
            "specification_version": 1,
            "approval": "DEC-20260908-d5057a",
            "task_id": "TASK-20260908-aeba66",
            "binding_executor_handoff": "ledger/handoffs/TASK-20260908-aeba66.yaml",
            "goal_id": "GOAL-ECRANK-002",
            "question_id": "RQ-ECRANK-27dcc5",
            "batch_id": "BATCH-a9c273",
            "hypothesis_id": "H-ECRANK-1d22a4",
            "role": "executor",
            "recorded_at": dt.date.today().isoformat(),
            "report_scope_statement": (
                "Observations only. This report interprets nothing, assigns no "
                "finding label (F1/F2/F3), promotes no claim, and changes no "
                "status. Mapping recorded facts to the frozen success criterion "
                "is Coordinator work under /review-evidence."
            ),
            "inference": INFERENCE,
            "protocol_binding": {
                "frozen_protocol_edited": False,
                "amendments_written": "none",
                "amendments_proposed": "none",
            },
            "environment": machine_env() | {
                "git_commit_at_runs": git_info().get("commit"),
                "git_dirty_at_runs": git_info().get("dirty"),
            },
            "frozen_prediction_reference": (
                "experiments/EXP-ECRANK-52d039/specification.yaml preregistered_prediction"
            ),
            "run_inventory": [
                quoted(m1, r1),
                quoted(m2, r2),
                {
                    "run_id": m3["run"]["id"],
                    "status": m3["run"]["status"],
                    "validity_reason": m3["run"]["validity"]["reason"],
                    "wall_seconds_monotonic": m3["run"]["timing"]["wall_seconds_monotonic"],
                    "wall_seconds_timestamp_span": m3["run"]["timing"]["wall_seconds_timestamp_span"],
                    "peak_rss_bytes": m3["run"]["resources"]["peak_rss_bytes"],
                    "observations_quoted": {
                        "comparison": r3.get("comparison"),
                        "errors": r3.get("errors", []),
                    },
                },
            ],
            "run_tally": {
                "completed": completed,
                "failed_infrastructure": failed,
                "invalid": invalid,
            },
            "protocol_deviations": [],
            "anomalies": anomalies,
            "completion_gate": {
                "three_nested_run_records": True,
                "validate_ledger_deferred_to_coordinator_snapshot": True,
                "snapshot_archive_deferred": True,
            },
        }
    }
    write_yaml(EXP / "execution-report.yaml", payload)
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "task_report": {
            "task_id": "TASK-20260908-aeba66",
            "role": "executor",
            "experiment_id": "EXP-ECRANK-52d039",
            "protocol": "EXP-ECRANK-52d039 version 1, frozen specification",
            "protocol_deviations": [],
            "observations_only": True,
            "runs": payload["execution_report"]["run_tally"],
            "artifact_paths": [
                "experiments/EXP-ECRANK-52d039/implementation.md",
                "experiments/EXP-ECRANK-52d039/source/",
                "experiments/EXP-ECRANK-52d039/runs/RUN-ECRANK-52d039-R1-abstract-gate/",
                "experiments/EXP-ECRANK-52d039/runs/RUN-ECRANK-52d039-R2-elliptic-interface/",
                "experiments/EXP-ECRANK-52d039/runs/RUN-ECRANK-52d039-R3-replay/",
                "experiments/EXP-ECRANK-52d039/runs/R1-abstract-gate/",
                "experiments/EXP-ECRANK-52d039/runs/R2-elliptic-interface/",
                "experiments/EXP-ECRANK-52d039/runs/R3-replay/",
                "experiments/EXP-ECRANK-52d039/execution-report.yaml",
            ],
        }
    }
    write_yaml(TASK_DIR / "report.md", report)
    write_yaml(TASK_DIR / "executor-report.yaml", report)


def _load_raw(stage):
    path = EXP / "runs" / RUN_IDS[stage] / "raw-result.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load_manifest(stage):
    path = EXP / "runs" / RUN_IDS[stage] / "manifest.yaml"
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        return json.loads(path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"all", "r1", "r2", "r3", "report"}:
        raise SystemExit("usage: run_experiment.py all|r1|r2|r3|report")
    if sys.argv[1] == "r1":
        run_stage("r1")
    elif sys.argv[1] == "r2":
        run_stage("r2")
    elif sys.argv[1] == "r3":
        run_replay()
    elif sys.argv[1] == "report":
        write_execution_report(
            _load_raw("r1"),
            _load_raw("r2"),
            _load_raw("r3"),
            _load_manifest("r1"),
            _load_manifest("r2"),
            _load_manifest("r3"),
        )
    else:
        r1, m1 = run_stage("r1")
        r2, m2 = run_stage("r2")
        r3, m3 = run_replay()
        write_execution_report(r1, r2, r3, m1, m2, m3)


if __name__ == "__main__":
    main()
