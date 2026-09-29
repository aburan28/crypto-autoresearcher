#!/usr/bin/env python3
"""Stage 1 CS-aligned audit of EXP-ECDLP-5cad48.

Authorized computation only under DEC-20260907-818215 /
v1_stage1_cs_aligned_authorized. Consumes recorded Stage 1
raw-result.json exact fields. Does not classify W. Does
not fit a. Certificate kind none. No a98ea9 Stage 5.
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
AUTH = EXP / "amendments" / "v1_stage1_cs_aligned_authorized.yaml"
S1_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S1" / "raw-result.json"
REQUIRED_CELLS = {
    "S1-P523": (5, 8, 12),
    "S1-P1033": (6, 10, 16),
}
REQUIRED_ARMS = ("floor(Mx/p)", "x mod M", "sha", "shuffle", "P2")
REQUIRED_FIELDS = ("G_exact", "M_delta_exact", "W_exact", "min_q", "cs_bound_exact")


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
    raw = json.loads(S1_RAW.read_text())
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S1":
        raise SystemExit("refuse: unexpected Stage 1 run_id")

    cells_in = {cell["id"]: cell for cell in raw.get("cells") or []}
    missing_cells = [cid for cid in REQUIRED_CELLS if cid not in cells_in]
    if missing_cells:
        raise SystemExit(f"refuse: missing Stage 1 cells {missing_cells}")

    out_cells = []
    all_holds = True
    units_mismatches = []
    n_rows = 0
    for cid, ms_needed in REQUIRED_CELLS.items():
        cell = cells_in[cid]
        ms_in = {int(ms["M"]): ms for ms in cell.get("Ms") or []}
        missing_m = [m for m in ms_needed if m not in ms_in]
        if missing_m:
            raise SystemExit(f"refuse: cell {cid} missing M {missing_m}")
        out_ms = []
        for m in ms_needed:
            arms_in = ms_in[m].get("arms") or {}
            missing_arms = [a for a in REQUIRED_ARMS if a not in arms_in]
            if missing_arms:
                raise SystemExit(f"refuse: {cid} M={m} missing arms {missing_arms}")
            out_arms = {}
            for name in REQUIRED_ARMS:
                rec = arms_in[name]
                missing = [f for f in REQUIRED_FIELDS if f not in rec]
                if missing:
                    raise SystemExit(f"refuse: {cid} M={m} arm {name} missing {missing}")
                g = float(rec["G_exact"])
                m_delta = float(rec["M_delta_exact"])
                w = float(rec["W_exact"])
                min_q = float(rec["min_q"])
                cs = float(rec["cs_bound_exact"])
                aligned = g / m_delta
                cs_re = 1.0 + math.sqrt(w / max(min_q, 1e-18))
                aligned_holds = aligned <= cs
                raw_g_holds = g <= cs
                all_holds = all_holds and aligned_holds
                n_rows += 1
                if not raw_g_holds:
                    units_mismatches.append(
                        {
                            "cell": cid,
                            "M": m,
                            "arm": name,
                            "note": "units_mismatch_not_cs_falsification",
                        }
                    )
                out_arms[name] = {
                    "G_exact": g,
                    "M_delta_exact": m_delta,
                    "W_exact": w,
                    "min_q": min_q,
                    "cs_bound_recorded": cs,
                    "cs_bound_recomputed": cs_re,
                    "aligned_ratio": aligned,
                    "aligned_holds": aligned_holds,
                    "raw_G_versus_cs_bound": raw_g_holds,
                    "raw_G_versus_cs_bound_is_units_mismatch": True,
                }
            out_ms.append({"M": m, "arms": out_arms})
        out_cells.append({"id": cid, "p": cell.get("p"), "Ms": out_ms})

    elapsed = time.time() - t0
    git = _git_info()
    payload = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S1CS",
        "package": "stage1_cs_aligned_audit",
        "certificate_kind": "none",
        "consumed_run_id": "RUN-ECDLP-5cad48-S1",
        "consumed_path": "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S1/raw-result.json",
        "n_exact_rows": n_rows,
        "cells": out_cells,
        "all_cells_aligned_holds": all_holds,
        "units_mismatch_rows": units_mismatches,
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

    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S1CS"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    recorded_at = datetime.now(timezone.utc).isoformat()

    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S1CS",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-986bad",
            "stage": 1,
            "status": "completed_valid",
            "recorded_at": recorded_at,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": git["dirty_summary"],
                "command": "python3 experiments/EXP-ECDLP-5cad48/implementation/stage1_cs_audit.py",
                "source_path": "experiments/EXP-ECDLP-5cad48/implementation/stage1_cs_audit.py",
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
                    "consumed_run_id": "RUN-ECDLP-5cad48-S1",
                    "authorized_by": "DEC-20260907-818215",
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
                "validity_reason": "Consume-only aligned G_exact/M_delta_exact versus cs_bound_exact package complete.",
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only aligned comparison; no discrete log.",
                },
                "metrics": {
                    "all_cells_aligned_holds": all_holds,
                    "n_exact_rows": n_rows,
                    "not_a_W_decay_claim": True,
                    "cs_bound_official_supported": False,
                },
                "scientific_boundary": (
                    "Aligned Stage 1 exact-field audit only. W is recorded, not classified. "
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
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage1_cs_audit.py\n"
    )
    (run_dir / "stdout.log").write_text(
        f"all_cells_aligned_holds={all_holds} n_exact_rows={n_rows} raw_sha={raw_sha}\n"
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
        "run_id": "RUN-ECDLP-5cad48-S1CS",
        "package": "stage1_cs_aligned_audit",
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "all_cells_aligned_holds": all_holds,
        "n_exact_rows": n_rows,
        "raw_result_sha256": raw_sha,
        "not_a_W_decay_claim": True,
    }
    (EXP / "execution-report-s1cs.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(json.dumps({"valid": True, "all_cells_aligned_holds": all_holds, "n_exact_rows": n_rows, "raw_sha": raw_sha}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
