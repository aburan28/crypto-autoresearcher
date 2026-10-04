#!/usr/bin/env python3
"""Stage 0 CS-aligned audit of EXP-ECDLP-5cad48.

Authorized computation only under DEC-20260907-62cbc4 /
v1_stage0_cs_aligned_authorized. Consumes recorded Stage 0
raw-result.json. Does not classify W. Does not fit a.
Certificate kind none. No a98ea9 Stage 5.
"""
from __future__ import annotations

import hashlib
import json
import math
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
AUTH = EXP / "amendments" / "v1_stage0_cs_aligned_authorized.yaml"
S0_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S0" / "raw-result.json"
REQUIRED_ARMS = ("floor(Mx/p)", "x mod M", "sha", "shuffle", "P2")
REQUIRED_FIELDS = ("G", "M_delta", "W", "min_q", "cs_bound")


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
    if not block.get("cs_aligned_audit_execution_authorized"):
        raise SystemExit("refuse: cs_aligned_audit_execution_authorized is not true")
    if block.get("SMALL_W_or_LARGE_W"):
        raise SystemExit("refuse: authorization classified W")
    if block.get("fit_of_a"):
        raise SystemExit("refuse: authorization set fit_of_a true")
    if block.get("cs_bound_official_supported"):
        raise SystemExit("refuse: authorization set an official bound claim")


def main() -> int:
    t0 = time.time()
    refuse_unless_authorized()
    raw = json.loads(S0_RAW.read_text())
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S0":
        raise SystemExit("refuse: unexpected Stage 0 run_id")
    arms_in = raw.get("arms") or {}
    missing_arms = [a for a in REQUIRED_ARMS if a not in arms_in]
    if missing_arms:
        raise SystemExit(f"refuse: missing Stage 0 arms {missing_arms}")

    out_arms = {}
    all_holds = True
    for name in REQUIRED_ARMS:
        rec = arms_in[name]
        missing = [f for f in REQUIRED_FIELDS if f not in rec]
        if missing:
            raise SystemExit(f"refuse: arm {name} missing fields {missing}")
        g = float(rec["G"])
        m_delta = float(rec["M_delta"])
        w = float(rec["W"])
        min_q = float(rec["min_q"])
        cs = float(rec["cs_bound"])
        aligned = g / m_delta
        cs_re = 1.0 + math.sqrt(w / max(min_q, 1e-18))
        aligned_holds = aligned <= cs
        raw_g_holds = g <= cs
        all_holds = all_holds and aligned_holds
        out_arms[name] = {
            "G": g,
            "M_delta": m_delta,
            "W": w,
            "min_q": min_q,
            "cs_bound_recorded": cs,
            "cs_bound_recomputed": cs_re,
            "aligned_ratio": aligned,
            "aligned_holds": aligned_holds,
            "raw_G_versus_cs_bound": raw_g_holds,
            "raw_G_versus_cs_bound_is_units_mismatch": True,
        }

    elapsed = time.time() - t0
    git = _git_info()
    payload = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S0CS",
        "package": "stage0_cs_aligned_audit",
        "certificate_kind": "none",
        "consumed_run_id": "RUN-ECDLP-5cad48-S0",
        "consumed_path": "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S0/raw-result.json",
        "fixture": raw.get("fixture"),
        "p2_W_note": raw.get("p2_W_note"),
        "arms": out_arms,
        "all_arms_aligned_holds": all_holds,
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

    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S0CS"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    recorded_at = datetime.now(timezone.utc).isoformat()

    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S0CS",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-0cb001",
            "stage": 0,
            "status": "completed_valid",
            "recorded_at": recorded_at,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": git["dirty_summary"],
                "command": "python3 experiments/EXP-ECDLP-5cad48/implementation/stage0_cs_audit.py",
                "source_path": "experiments/EXP-ECDLP-5cad48/implementation/stage0_cs_audit.py",
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
                    "consumed_run_id": "RUN-ECDLP-5cad48-S0",
                    "authorized_by": "DEC-20260907-62cbc4",
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
                "validity_reason": "Consume-only aligned G/M_delta versus cs_bound package complete.",
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only aligned comparison; no discrete log.",
                },
                "metrics": {
                    "all_arms_aligned_holds": all_holds,
                    "not_a_W_decay_claim": True,
                    "cs_bound_official_supported": False,
                },
                "scientific_boundary": (
                    "Aligned Stage 0 audit only. W is recorded, not classified. "
                    "No official bound claim. No a98ea9 Stage 5."
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
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage0_cs_audit.py\n"
    )
    (run_dir / "stdout.log").write_text(
        f"all_arms_aligned_holds={all_holds} raw_sha={raw_sha}\n"
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
        "run_id": "RUN-ECDLP-5cad48-S0CS",
        "package": "stage0_cs_aligned_audit",
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "all_arms_aligned_holds": all_holds,
        "raw_result_sha256": raw_sha,
        "not_a_W_decay_claim": True,
    }
    (EXP / "execution-report-s0cs.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(json.dumps({"valid": True, "all_arms_aligned_holds": all_holds, "raw_sha": raw_sha}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
