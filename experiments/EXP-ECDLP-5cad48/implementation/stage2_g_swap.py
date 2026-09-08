#!/usr/bin/env python3
"""Consume-only G-swap of archived Stage 2 bound-decomp cells.

Authorized only under v1_stage2_g_swap_authorized / DEC-20260907-963413.
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
AUTH = EXP / "amendments" / "v1_stage2_g_swap_authorized.yaml"
S2BD_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S2BD" / "raw-result.json"
N_EXPECTED_SOURCE = 4
N_HOLDS = 3


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
    if not block.get("g_swap_execution_authorized"):
        raise SystemExit("refuse: g_swap_execution_authorized is not true")
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
    if miss.get("cell") != "S2-P8219" or int(miss.get("M")) != 9:
        raise SystemExit("refuse: miss cell is not S2-P8219 M=9")
    for key in ("G_exact", "M_delta_exact", "cs_bound_recorded"):
        if key not in miss:
            raise SystemExit(f"refuse: miss missing {key}")
    g_miss = float(miss["G_exact"])
    md_miss = float(miss["M_delta_exact"])
    cs_miss = float(miss["cs_bound_recorded"])
    if md_miss == 0.0:
        raise SystemExit("refuse: miss M_delta_exact is zero")
    holds_src = [c for c in cells if c.get("role") != "miss"]
    if len(holds_src) != N_HOLDS:
        raise SystemExit(f"refuse: expected {N_HOLDS} holds, got {len(holds_src)}")
    roles = [c.get("role") for c in holds_src]
    if roles.count("next_tightest_hold") != 1:
        raise SystemExit("refuse: expected exactly one next_tightest_hold")
    if roles.count("same_cell_hold") != 2:
        raise SystemExit("refuse: expected exactly two same_cell_hold cells")
    holds = []
    n_this_g_that_would_make_miss_hold = 0
    n_holds_flipped_by_miss_g = 0
    flipped_roles = []
    for src in holds_src:
        for key in ("G_exact", "M_delta_exact", "cs_bound_recorded", "cell", "M"):
            if key not in src:
                raise SystemExit(f"refuse: hold missing {key}")
        g_h = float(src["G_exact"])
        md_h = float(src["M_delta_exact"])
        cs_h = float(src["cs_bound_recorded"])
        if md_h == 0.0:
            raise SystemExit("refuse: hold M_delta_exact is zero")
        miss_would_hold_if_this_g = bool((g_h / md_miss) <= cs_miss)
        this_would_hold_if_miss_g = bool((g_miss / md_h) <= cs_h)
        currently_holds = bool(src.get("aligned_holds"))
        flipped = currently_holds and (not this_would_hold_if_miss_g)
        if miss_would_hold_if_this_g:
            n_this_g_that_would_make_miss_hold += 1
        if flipped:
            n_holds_flipped_by_miss_g += 1
            flipped_roles.append(src.get("role"))
        holds.append(
            {
                "cell": src["cell"],
                "M": int(src["M"]),
                "arm": src.get("arm", "floor(Mx/p)"),
                "role": src.get("role"),
                "aligned_holds": currently_holds,
                "G_exact": g_h,
                "M_delta_exact": md_h,
                "aligned_ratio": g_h / md_h,
                "cs_bound_recorded": cs_h,
                "counterfactual_aligned_miss_with_this_G": g_h / md_miss,
                "counterfactual_aligned_this_with_miss_G": g_miss / md_h,
                "miss_would_hold_if_this_G": miss_would_hold_if_this_g,
                "this_would_hold_if_miss_G": this_would_hold_if_miss_g,
                "source_run_id": "RUN-ECDLP-5cad48-S2BD",
            }
        )
    miss_g_flips_only_next_tightest = (
        n_holds_flipped_by_miss_g == 1
        and flipped_roles.count("next_tightest_hold") == 1
    )
    elapsed = time.time() - t0
    git = _git_info()
    payload = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2GX",
        "package": "stage2_g_swap",
        "certificate_kind": "none",
        "consumed_run_id": "RUN-ECDLP-5cad48-S2BD",
        "aligned_ratio_definition": "G_exact / M_delta_exact",
        "miss_would_hold_if_this_G_definition": "hold G_exact / miss M_delta_exact <= miss cs_bound_recorded",
        "this_would_hold_if_miss_G_definition": "miss G_exact / hold M_delta_exact <= hold cs_bound_recorded",
        "n_holds": N_HOLDS,
        "holds": holds,
        "n_this_G_that_would_make_miss_hold": n_this_g_that_would_make_miss_hold,
        "n_holds_flipped_by_miss_G": n_holds_flipped_by_miss_g,
        "miss_G_flips_only_next_tightest": miss_g_flips_only_next_tightest,
        "miss_cell": {
            "cell": miss["cell"],
            "M": int(miss["M"]),
            "arm": miss.get("arm", "floor(Mx/p)"),
            "G_exact": g_miss,
            "M_delta_exact": md_miss,
            "aligned_ratio": g_miss / md_miss,
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
    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S2GX"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    recorded_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S2GX",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-56e53a",
            "stage": 2,
            "status": "completed_valid",
            "recorded_at": recorded_at,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": git["dirty_summary"],
                "command": "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_g_swap.py",
                "source_path": "experiments/EXP-ECDLP-5cad48/implementation/stage2_g_swap.py",
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
                    "authorized_by": "DEC-20260907-963413",
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
                "validity_reason": "Consume-only G-swap of archived S2BD cells.",
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only G-swap; no discrete log.",
                },
                "metrics": {
                    "n_holds": N_HOLDS,
                    "n_this_G_that_would_make_miss_hold": n_this_g_that_would_make_miss_hold,
                    "n_holds_flipped_by_miss_G": n_holds_flipped_by_miss_g,
                    "miss_G_flips_only_next_tightest": miss_g_flips_only_next_tightest,
                    "not_a_W_decay_claim": True,
                    "cs_bound_official_supported": False,
                },
                "scientific_boundary": (
                    "Archived S2BD four-cell table only. "
                    "A G-swap uniqueness or sharing is not a W class. "
                    "No official bound. No a98ea9 Stage 5."
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
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_g_swap.py\n"
    )
    (run_dir / "stdout.log").write_text(
        f"n={N_HOLDS} n_this_G={n_this_g_that_would_make_miss_hold} "
        f"n_flipped={n_holds_flipped_by_miss_g} raw_sha={raw_sha}\n"
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
        "run_id": "RUN-ECDLP-5cad48-S2GX",
        "package": "stage2_g_swap",
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "n_holds": N_HOLDS,
        "n_this_G_that_would_make_miss_hold": n_this_g_that_would_make_miss_hold,
        "n_holds_flipped_by_miss_G": n_holds_flipped_by_miss_g,
        "miss_G_flips_only_next_tightest": miss_g_flips_only_next_tightest,
        "raw_result_sha256": raw_sha,
        "not_a_W_decay_claim": True,
    }
    (EXP / "execution-report-s2gx.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(
        json.dumps(
            {
                "valid": True,
                "n_holds": N_HOLDS,
                "n_this_G_that_would_make_miss_hold": n_this_g_that_would_make_miss_hold,
                "n_holds_flipped_by_miss_G": n_holds_flipped_by_miss_g,
                "miss_G_flips_only_next_tightest": miss_g_flips_only_next_tightest,
                "raw_sha": raw_sha,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
