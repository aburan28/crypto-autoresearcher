#!/usr/bin/env python3
"""Consume-only tight-pair G / M_delta swap of archived Stage 2 bound-decomp cells.

Authorized only under v1_stage2_tight_pair_authorized / DEC-20260907-2d1d35.
Consumes RUN-ECDLP-5cad48-S2BD raw-result.json. Does not rebuild labels.
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
AUTH = EXP / "amendments" / "v1_stage2_tight_pair_authorized.yaml"
S2BD_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S2BD" / "raw-result.json"
N_EXPECTED_SOURCE = 4
N_PAIR = 2


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
    if not block.get("tight_pair_execution_authorized"):
        raise SystemExit("refuse: tight_pair_execution_authorized is not true")
    if block.get("SMALL_W_or_LARGE_W"):
        raise SystemExit("refuse: authorization classified W")
    if block.get("fit_of_a"):
        raise SystemExit("refuse: authorization set fit_of_a true")
    if block.get("cs_bound_official_supported"):
        raise SystemExit("refuse: authorization set an official bound claim")


def cell_by_role(cells: list[dict], role: str) -> dict:
    hits = [c for c in cells if c.get("role") == role]
    if len(hits) != 1:
        raise SystemExit(f"refuse: expected exactly one cell with role={role}, got {len(hits)}")
    return hits[0]


def main() -> int:
    t0 = time.time()
    refuse_unless_authorized()
    raw = json.loads(S2BD_RAW.read_text())
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S2BD":
        raise SystemExit("refuse: unexpected S2BD run_id")
    cells = raw.get("cells") or []
    if len(cells) != N_EXPECTED_SOURCE:
        raise SystemExit(f"refuse: S2BD n_cells {len(cells)} != {N_EXPECTED_SOURCE}")
    miss = cell_by_role(cells, "miss")
    nxt = cell_by_role(cells, "next_tightest_hold")
    if miss.get("cell") != "S2-P8219" or int(miss.get("M")) != 9:
        raise SystemExit("refuse: miss cell is not S2-P8219 M=9")
    if nxt.get("cell") != "S2-P32779" or int(nxt.get("M")) != 13:
        raise SystemExit("refuse: next_tightest_hold cell is not S2-P32779 M=13")
    for key in ("G_exact", "M_delta_exact", "cs_bound_recorded"):
        if key not in miss or key not in nxt:
            raise SystemExit(f"refuse: pair missing {key}")
    g_miss = float(miss["G_exact"])
    md_miss = float(miss["M_delta_exact"])
    g_next = float(nxt["G_exact"])
    md_next = float(nxt["M_delta_exact"])
    if md_miss == 0.0 or md_next == 0.0:
        raise SystemExit("refuse: M_delta_exact is zero")
    cs_miss = float(miss["cs_bound_recorded"])
    aligned_miss = g_miss / md_miss
    aligned_next = g_next / md_next
    cf_next_g = g_next / md_miss
    cf_next_md = g_miss / md_next
    hold_next_g = bool(cf_next_g <= cs_miss)
    hold_next_md = bool(cf_next_md <= cs_miss)
    pair = [
        {
            "cell": miss["cell"],
            "M": int(miss["M"]),
            "arm": miss.get("arm", "floor(Mx/p)"),
            "role": "miss",
            "aligned_holds": bool(miss["aligned_holds"]),
            "G_exact": g_miss,
            "M_delta_exact": md_miss,
            "aligned_ratio": aligned_miss,
            "cs_bound_recorded": cs_miss,
            "source_run_id": "RUN-ECDLP-5cad48-S2BD",
        },
        {
            "cell": nxt["cell"],
            "M": int(nxt["M"]),
            "arm": nxt.get("arm", "floor(Mx/p)"),
            "role": "next_tightest_hold",
            "aligned_holds": bool(nxt["aligned_holds"]),
            "G_exact": g_next,
            "M_delta_exact": md_next,
            "aligned_ratio": aligned_next,
            "cs_bound_recorded": float(nxt["cs_bound_recorded"]),
            "source_run_id": "RUN-ECDLP-5cad48-S2BD",
        },
    ]
    elapsed = time.time() - t0
    git = _git_info()
    payload = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2TP",
        "package": "stage2_tight_pair",
        "certificate_kind": "none",
        "consumed_run_id": "RUN-ECDLP-5cad48-S2BD",
        "aligned_ratio_definition": "G_exact / M_delta_exact",
        "counterfactual_aligned_with_pair_G": "pair G_exact / self M_delta_exact",
        "counterfactual_aligned_with_pair_M_delta": "self G_exact / pair M_delta_exact",
        "hold_definition": "counterfactual aligned_ratio <= miss cs_bound_recorded",
        "n_pair_cells": N_PAIR,
        "pair": pair,
        "miss_would_hold_if_next_G": hold_next_g,
        "miss_would_hold_if_next_M_delta": hold_next_md,
        "counterfactual_aligned_miss_with_next_G": cf_next_g,
        "counterfactual_aligned_miss_with_next_M_delta": cf_next_md,
        "miss_cell": {
            "cell": miss["cell"],
            "M": int(miss["M"]),
            "arm": miss.get("arm", "floor(Mx/p)"),
            "aligned_ratio": aligned_miss,
            "cs_bound_recorded": cs_miss,
            "aligned_holds": bool(miss["aligned_holds"]),
        },
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
    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S2TP"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    recorded_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S2TP",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-7c945d",
            "stage": 2,
            "status": "completed_valid",
            "recorded_at": recorded_at,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": git["dirty_summary"],
                "command": "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_tight_pair.py",
                "source_path": "experiments/EXP-ECDLP-5cad48/implementation/stage2_tight_pair.py",
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
                    "consumed_run_id": "RUN-ECDLP-5cad48-S2BD",
                    "authorized_by": "DEC-20260907-2d1d35",
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
                "validity_reason": "Consume-only tight-pair G / M_delta swap of archived S2BD cells.",
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only pair swap; no discrete log.",
                },
                "metrics": {
                    "n_pair_cells": N_PAIR,
                    "miss_would_hold_if_next_G": hold_next_g,
                    "miss_would_hold_if_next_M_delta": hold_next_md,
                    "not_a_W_decay_claim": True,
                    "cs_bound_official_supported": False,
                },
                "scientific_boundary": (
                    "Archived S2BD miss and next-tightest cells only. "
                    "A pair ingredient is not a W class. No official bound. "
                    "No a98ea9 Stage 5."
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
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_tight_pair.py\n"
    )
    (run_dir / "stdout.log").write_text(
        f"n={N_PAIR} hold_G={hold_next_g} hold_Md={hold_next_md} raw_sha={raw_sha}\n"
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
        "run_id": "RUN-ECDLP-5cad48-S2TP",
        "package": "stage2_tight_pair",
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "n_pair_cells": N_PAIR,
        "miss_would_hold_if_next_G": hold_next_g,
        "miss_would_hold_if_next_M_delta": hold_next_md,
        "raw_result_sha256": raw_sha,
        "not_a_W_decay_claim": True,
    }
    (EXP / "execution-report-s2tp.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(
        json.dumps(
            {
                "valid": True,
                "n_pair_cells": N_PAIR,
                "miss_would_hold_if_next_G": hold_next_g,
                "miss_would_hold_if_next_M_delta": hold_next_md,
                "raw_sha": raw_sha,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
