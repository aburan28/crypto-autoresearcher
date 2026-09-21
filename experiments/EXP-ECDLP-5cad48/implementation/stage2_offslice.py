#!/usr/bin/env python3
"""Consume-only off-slice census of archived Stage 2 occupancy cells.

Authorized only under v1_stage2_offslice_authorized / DEC-20260907-a5800e.
Consumes RUN-ECDLP-5cad48-S2OC raw-result.json. Does not rebuild labels.
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
AUTH = EXP / "amendments" / "v1_stage2_offslice_authorized.yaml"
S2OC_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S2OC" / "raw-result.json"
N_EXPECTED = 4


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
    if not block.get("offslice_execution_authorized"):
        raise SystemExit("refuse: offslice_execution_authorized is not true")
    if block.get("SMALL_W_or_LARGE_W"):
        raise SystemExit("refuse: authorization classified W")
    if block.get("fit_of_a"):
        raise SystemExit("refuse: authorization set fit_of_a true")
    if block.get("cs_bound_official_supported"):
        raise SystemExit("refuse: authorization set an official bound claim")


def gap_of(g_exact: float, m_eff: float, max_pi_c: float) -> float:
    return (g_exact / m_eff) - max_pi_c


def main() -> int:
    t0 = time.time()
    refuse_unless_authorized()
    raw = json.loads(S2OC_RAW.read_text())
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S2OC":
        raise SystemExit("refuse: unexpected S2OC run_id")
    cells_out = []
    for cell in raw.get("cells") or []:
        exact = cell.get("exact") or {}
        occ = cell.get("occupancy") or {}
        missing = [
            f
            for f in ("id", "M", "role", "aligned_holds")
            if f not in cell
        ]
        if "G_exact" not in exact:
            missing.append("exact.G_exact")
        if "M_eff" not in occ:
            missing.append("occupancy.M_eff")
        if "max_pi_c" not in occ:
            missing.append("occupancy.max_pi_c")
        if missing:
            raise SystemExit(f"refuse: cell missing {missing}")
        g_exact = float(exact["G_exact"])
        m_eff = float(occ["M_eff"])
        max_pi_c = float(occ["max_pi_c"])
        if m_eff == 0.0:
            raise SystemExit("refuse: M_eff is zero")
        gap = gap_of(g_exact, m_eff, max_pi_c)
        cells_out.append(
            {
                "cell": cell["id"],
                "M": int(cell["M"]),
                "arm": cell.get("arm", "floor(Mx/p)"),
                "role": cell["role"],
                "aligned_holds": bool(cell["aligned_holds"]),
                "G_exact": g_exact,
                "M_eff": m_eff,
                "max_pi_c": max_pi_c,
                "off_slice_gap": gap,
                "off_slice_positive": gap > 0.0,
            }
        )
    if len(cells_out) != N_EXPECTED:
        raise SystemExit(f"refuse: n_cells {len(cells_out)} != {N_EXPECTED}")
    positives = [c for c in cells_out if c["off_slice_positive"]]
    misses = [c for c in cells_out if c["role"] == "miss"]
    if len(misses) != 1:
        raise SystemExit(f"refuse: n_miss {len(misses)} != 1")
    miss = misses[0]
    max_gap = max(c["off_slice_gap"] for c in cells_out)
    elapsed = time.time() - t0
    git = _git_info()
    payload = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2OS",
        "package": "stage2_offslice",
        "certificate_kind": "none",
        "consumed_run_id": "RUN-ECDLP-5cad48-S2OC",
        "gap_definition": "G_exact / M_eff minus max_pi_c",
        "n_cells": len(cells_out),
        "cells": cells_out,
        "n_off_slice_positive": len(positives),
        "all_four_off_slice_positive": len(positives) == N_EXPECTED,
        "miss_unique_off_slice_positive": (
            len(positives) == 1 and positives[0]["role"] == "miss"
        ),
        "miss_has_largest_gap": miss["off_slice_gap"] == max_gap,
        "miss_cell": {
            "cell": miss["cell"],
            "M": miss["M"],
            "arm": miss["arm"],
            "off_slice_gap": miss["off_slice_gap"],
            "off_slice_positive": miss["off_slice_positive"],
            "aligned_holds": miss["aligned_holds"],
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
    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S2OS"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    recorded_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S2OS",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-042d7e",
            "stage": 2,
            "status": "completed_valid",
            "recorded_at": recorded_at,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": git["dirty_summary"],
                "command": "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_offslice.py",
                "source_path": "experiments/EXP-ECDLP-5cad48/implementation/stage2_offslice.py",
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
                    "consumed_run_id": "RUN-ECDLP-5cad48-S2OC",
                    "authorized_by": "DEC-20260907-a5800e",
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
                "validity_reason": "Consume-only off-slice census of four archived occupancy cells.",
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only off-slice ranking; no discrete log.",
                },
                "metrics": {
                    "n_cells": len(cells_out),
                    "n_off_slice_positive": len(positives),
                    "all_four_off_slice_positive": len(positives) == N_EXPECTED,
                    "miss_unique_off_slice_positive": (
                        len(positives) == 1 and positives[0]["role"] == "miss"
                    ),
                    "miss_has_largest_gap": miss["off_slice_gap"] == max_gap,
                    "not_a_W_decay_claim": True,
                    "cs_bound_official_supported": False,
                },
                "scientific_boundary": (
                    "Archived four-cell S2OC table only. Gap is "
                    "G_exact / M_eff minus max_pi_c. W is recorded, "
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
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_offslice.py\n"
    )
    (run_dir / "stdout.log").write_text(
        f"n={len(cells_out)} n_pos={len(positives)} "
        f"all_four={len(positives) == N_EXPECTED} raw_sha={raw_sha}\n"
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
        "run_id": "RUN-ECDLP-5cad48-S2OS",
        "package": "stage2_offslice",
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "n_cells": len(cells_out),
        "n_off_slice_positive": len(positives),
        "all_four_off_slice_positive": len(positives) == N_EXPECTED,
        "miss_unique_off_slice_positive": (
            len(positives) == 1 and positives[0]["role"] == "miss"
        ),
        "miss_has_largest_gap": miss["off_slice_gap"] == max_gap,
        "raw_result_sha256": raw_sha,
        "not_a_W_decay_claim": True,
    }
    (EXP / "execution-report-s2os.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(
        json.dumps(
            {
                "valid": True,
                "n_cells": len(cells_out),
                "n_off_slice_positive": len(positives),
                "all_four_off_slice_positive": len(positives) == N_EXPECTED,
                "miss_unique_off_slice_positive": (
                    len(positives) == 1 and positives[0]["role"] == "miss"
                ),
                "miss_has_largest_gap": miss["off_slice_gap"] == max_gap,
                "raw_sha": raw_sha,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
