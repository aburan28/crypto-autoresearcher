#!/usr/bin/env python3
"""Consume-only slack census of archived Stage 2 aligned CS rows.

Authorized only under v1_stage2_slack_census_authorized / DEC-20260907-76a399.
Consumes RUN-ECDLP-5cad48-S2CS raw-result.json. Does not re-run Stage 2.
Does not classify W. Does not fit a. Certificate kind none. No a98ea9 Stage 5.
"""
from __future__ import annotations

import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
EXP = REPO / "experiments" / "EXP-ECDLP-5cad48"
AUTH = EXP / "amendments" / "v1_stage2_slack_census_authorized.yaml"
S2CS_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S2CS" / "raw-result.json"
FLOOR = "floor(Mx/p)"
N_EXPECTED = 168


def _git_info() -> dict:
    def _run(args):
        try:
            return subprocess.run(
                ["git"] + args, cwd=REPO, capture_output=True, text=True, timeout=30
            ).stdout.strip()
        except Exception as exc:
            return f"error: {exc}"

    dirty = _run(["status", "--porcelain"])
    return {
        "commit": _run(["rev-parse", "HEAD"]),
        "dirty": dirty != "",
        "dirty_summary": dirty[:2000],
    }


def peak_rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def refuse_unless_authorized() -> None:
    rec = yaml.safe_load(AUTH.read_text())
    block = rec.get("protocol_amendment", rec)
    if not block.get("slack_census_execution_authorized"):
        raise SystemExit("refuse: slack_census_execution_authorized is not true")
    if block.get("SMALL_W_or_LARGE_W"):
        raise SystemExit("refuse: authorization classified W")
    if block.get("fit_of_a"):
        raise SystemExit("refuse: authorization set fit_of_a true")
    if block.get("cs_bound_official_supported"):
        raise SystemExit("refuse: authorization set an official bound claim")


def slack_of(rec: dict) -> float:
    return float(rec["cs_bound_recorded"]) - float(rec["aligned_ratio"])


def main() -> int:
    t0 = time.time()
    refuse_unless_authorized()
    raw = json.loads(S2CS_RAW.read_text())
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S2CS":
        raise SystemExit("refuse: unexpected S2CS run_id")
    rows = []
    for cell in raw.get("cells") or []:
        cid = cell["id"]
        for ms in cell.get("Ms") or []:
            m = int(ms["M"])
            for arm, rec in (ms.get("arms") or {}).items():
                missing = [
                    f
                    for f in (
                        "aligned_ratio",
                        "cs_bound_recorded",
                        "aligned_holds",
                        "min_q",
                        "W_exact",
                    )
                    if f not in rec
                ]
                if missing:
                    raise SystemExit(f"refuse: {cid} M={m} {arm} missing {missing}")
                rows.append(
                    {
                        "cell": cid,
                        "M": m,
                        "arm": arm,
                        "aligned_ratio": float(rec["aligned_ratio"]),
                        "cs_bound_recorded": float(rec["cs_bound_recorded"]),
                        "aligned_holds": bool(rec["aligned_holds"]),
                        "min_q": float(rec["min_q"]),
                        "W_exact": float(rec["W_exact"]),
                        "slack": slack_of(rec),
                    }
                )
    if len(rows) != N_EXPECTED:
        raise SystemExit(f"refuse: n_exact_rows {len(rows)} != {N_EXPECTED}")
    misses = [r for r in rows if not r["aligned_holds"]]
    floor_rows = sorted(
        [r for r in rows if r["arm"] == FLOOR], key=lambda r: r["slack"]
    )
    ranked = sorted(rows, key=lambda r: r["slack"])
    elapsed = time.time() - t0
    git = _git_info()
    payload = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2DX",
        "package": "stage2_slack_census",
        "certificate_kind": "none",
        "consumed_run_id": "RUN-ECDLP-5cad48-S2CS",
        "n_exact_rows": len(rows),
        "n_aligned_false": len(misses),
        "n_floor_rows": len(floor_rows),
        "unique_miss": misses[0] if len(misses) == 1 else None,
        "n_misses_is_one": len(misses) == 1,
        "tightest_floor": floor_rows[0] if floor_rows else None,
        "next_tightest_floor": floor_rows[1] if len(floor_rows) > 1 else None,
        "tightest_five": ranked[:5],
        "floor_slack_ascending": [
            {
                "cell": r["cell"],
                "M": r["M"],
                "slack": r["slack"],
                "aligned_holds": r["aligned_holds"],
                "min_q": r["min_q"],
            }
            for r in floor_rows
        ],
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "not_a_W_decay_claim": True,
        "h_ecdlp_07c7c6_unchanged": True,
        "git": git,
        "wall_clock_seconds": elapsed,
        "peak_rss_bytes": peak_rss_bytes(),
        "python": sys.version,
        "platform": platform.platform(),
    }
    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S2DX"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    recorded_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S2DX",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-f1b693",
            "stage": 2,
            "status": "completed_valid",
            "recorded_at": recorded_at,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": git["dirty_summary"],
                "command": "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_slack_census.py",
                "source_path": "experiments/EXP-ECDLP-5cad48/implementation/stage2_slack_census.py",
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": "cursor-grok-4.6-cloud-agent",
                "model_provenance": "cursor cloud agent session acting as executor",
                "model_verified": False,
                "reasoning_effort": "medium",
                "fallback_used": False,
                "degraded_requirements": None,
            },
            "environment": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "machine": platform.machine(),
            },
            "inputs": {
                "parameters": {
                    "consumed_run_id": "RUN-ECDLP-5cad48-S2CS",
                    "authorized_by": "DEC-20260907-76a399",
                },
                "seeds": {"declared": []},
            },
            "timing": {"wall_clock_seconds": elapsed},
            "resources": {
                "wall_clock_seconds": elapsed,
                "peak_rss_bytes": peak_rss_bytes(),
            },
            "result": {
                "validity_status": "valid",
                "valid": True,
                "validity_reason": "Consume-only slack census of 168 archived Stage 2 aligned rows.",
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only slack ranking; no discrete log.",
                },
                "metrics": {
                    "n_exact_rows": len(rows),
                    "n_aligned_false": len(misses),
                    "n_misses_is_one": len(misses) == 1,
                    "not_a_W_decay_claim": True,
                    "cs_bound_official_supported": False,
                },
                "scientific_boundary": (
                    "Archived Stage 2 aligned table only. Slack is "
                    "cs_bound_recorded minus aligned_ratio. W is recorded, "
                    "not classified. No official bound. No a98ea9 Stage 5."
                ),
            },
            "artifacts": {
                "raw_result": "raw-result.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "environment": "environment.json",
                "command": "command.txt",
            },
        }
    }
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    (run_dir / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_slack_census.py\n"
    )
    miss_id = f"{misses[0]['cell']} M={misses[0]['M']} {misses[0]['arm']}" if misses else "none"
    (run_dir / "stdout.log").write_text(
        f"n={len(rows)} misses={len(misses)} unique={miss_id} raw_sha={raw_sha}\n"
    )
    (run_dir / "stderr.log").write_text("")
    (run_dir / "environment.json").write_text(
        json.dumps(
            {
                "python": sys.version,
                "platform": platform.platform(),
                "machine": platform.machine(),
            },
            indent=2,
        )
        + "\n"
    )
    report = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2DX",
        "package": "stage2_slack_census",
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "n_exact_rows": len(rows),
        "n_aligned_false": len(misses),
        "n_misses_is_one": len(misses) == 1,
        "raw_result_sha256": raw_sha,
        "not_a_W_decay_claim": True,
    }
    (EXP / "execution-report-s2dx.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(
        json.dumps(
            {
                "valid": True,
                "n_exact_rows": len(rows),
                "n_aligned_false": len(misses),
                "n_misses_is_one": len(misses) == 1,
                "raw_sha": raw_sha,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
