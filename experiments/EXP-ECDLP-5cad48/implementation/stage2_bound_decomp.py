#!/usr/bin/env python3
"""Consume-only bound-decomposition of archived Stage 2 occupancy cells.

Authorized only under v1_stage2_bound_decomp_authorized / DEC-20260907-bec1d1.
Consumes RUN-ECDLP-5cad48-S2OC raw-result.json. Does not rebuild labels.
Does not classify W. Does not fit a. Certificate kind none. No a98ea9 Stage 5.
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
AUTH = EXP / "amendments" / "v1_stage2_bound_decomp_authorized.yaml"
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
    if not block.get("bound_decomp_execution_authorized"):
        raise SystemExit("refuse: bound_decomp_execution_authorized is not true")
    if block.get("SMALL_W_or_LARGE_W"):
        raise SystemExit("refuse: authorization classified W")
    if block.get("fit_of_a"):
        raise SystemExit("refuse: authorization set fit_of_a true")
    if block.get("cs_bound_official_supported"):
        raise SystemExit("refuse: authorization set an official bound claim")


def close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-12 * max(1.0, abs(b))


def rebuilt_cs_bound(w_exact: float, min_q: float) -> float:
    return 1.0 + math.sqrt(w_exact / max(min_q, 1e-18))


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
        missing = [f for f in ("id", "M", "role", "aligned_holds") if f not in cell]
        for key, src in (
            ("G_exact", exact),
            ("M_delta_exact", exact),
            ("W_exact", exact),
            ("cs_bound_exact", exact),
            ("min_q", occ),
            ("M_eff", occ),
        ):
            if key not in src:
                missing.append(key)
        if missing:
            raise SystemExit(f"refuse: cell missing {missing}")
        g = float(exact["G_exact"])
        m_delta = float(exact["M_delta_exact"])
        w = float(exact["W_exact"])
        cs_rec = float(exact["cs_bound_exact"])
        min_q = float(occ["min_q"])
        m_eff = float(occ["M_eff"])
        if m_delta == 0.0:
            raise SystemExit("refuse: M_delta_exact is zero")
        aligned = g / m_delta
        rebuilt = rebuilt_cs_bound(w, min_q)
        cells_out.append(
            {
                "cell": cell["id"],
                "M": int(cell["M"]),
                "arm": cell.get("arm", "floor(Mx/p)"),
                "role": cell["role"],
                "aligned_holds": bool(cell["aligned_holds"]),
                "G_exact": g,
                "M_delta_exact": m_delta,
                "W_exact": w,
                "min_q": min_q,
                "M_eff": m_eff,
                "min_q_times_M_eff": min_q * m_eff,
                "aligned_ratio": aligned,
                "cs_bound_recorded": cs_rec,
                "cs_bound_rebuilt": rebuilt,
                "rebuild_matches": close(rebuilt, cs_rec),
                "slack": cs_rec - aligned,
            }
        )
    if len(cells_out) != N_EXPECTED:
        raise SystemExit(f"refuse: n_cells {len(cells_out)} != {N_EXPECTED}")
    misses = [c for c in cells_out if c["role"] == "miss"]
    nexts = [c for c in cells_out if c["role"] == "next_tightest_hold"]
    if len(misses) != 1 or len(nexts) != 1:
        raise SystemExit("refuse: expected one miss and one next_tightest_hold")
    miss = misses[0]
    nxt = nexts[0]
    min_bound = min(c["cs_bound_rebuilt"] for c in cells_out)
    max_aligned = max(c["aligned_ratio"] for c in cells_out)
    n_tightest = sum(close(c["cs_bound_rebuilt"], min_bound) for c in cells_out)
    n_highest = sum(close(c["aligned_ratio"], max_aligned) for c in cells_out)
    elapsed = time.time() - t0
    git = _git_info()
    payload = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2BD",
        "package": "stage2_bound_decomp",
        "certificate_kind": "none",
        "consumed_run_id": "RUN-ECDLP-5cad48-S2OC",
        "rebuilt_cs_bound_definition": "1 + sqrt(W_exact / min_q)",
        "aligned_ratio_definition": "G_exact / M_delta_exact",
        "n_cells": len(cells_out),
        "cells": cells_out,
        "all_rebuild_matches": all(c["rebuild_matches"] for c in cells_out),
        "miss_unique_tightest_cs_bound": (
            close(miss["cs_bound_rebuilt"], min_bound) and n_tightest == 1
        ),
        "miss_unique_highest_aligned_ratio": (
            close(miss["aligned_ratio"], max_aligned) and n_highest == 1
        ),
        "next_tightest_more_uniform_than_miss": (
            nxt["min_q_times_M_eff"] > miss["min_q_times_M_eff"]
        ),
        "miss_cell": {
            "cell": miss["cell"],
            "M": miss["M"],
            "arm": miss["arm"],
            "aligned_ratio": miss["aligned_ratio"],
            "cs_bound_rebuilt": miss["cs_bound_rebuilt"],
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
    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S2BD"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    recorded_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S2BD",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-a7db21",
            "stage": 2,
            "status": "completed_valid",
            "recorded_at": recorded_at,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": git["dirty_summary"],
                "command": "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_bound_decomp.py",
                "source_path": "experiments/EXP-ECDLP-5cad48/implementation/stage2_bound_decomp.py",
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
                    "authorized_by": "DEC-20260907-bec1d1",
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
                "validity_reason": "Consume-only bound-decomposition of four archived occupancy cells.",
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only bound ranking; no discrete log.",
                },
                "metrics": {
                    "n_cells": len(cells_out),
                    "all_rebuild_matches": payload["all_rebuild_matches"],
                    "miss_unique_tightest_cs_bound": payload["miss_unique_tightest_cs_bound"],
                    "miss_unique_highest_aligned_ratio": payload["miss_unique_highest_aligned_ratio"],
                    "next_tightest_more_uniform_than_miss": payload["next_tightest_more_uniform_than_miss"],
                    "not_a_W_decay_claim": True,
                    "cs_bound_official_supported": False,
                },
                "scientific_boundary": (
                    "Archived four-cell S2OC table only. Rebuilt cs_bound is "
                    "1 + sqrt(W_exact / min_q). W is recorded, not classified. "
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
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_bound_decomp.py\n"
    )
    (run_dir / "stdout.log").write_text(
        f"n={len(cells_out)} rebuild={payload['all_rebuild_matches']} "
        f"unique_align={payload['miss_unique_highest_aligned_ratio']} raw_sha={raw_sha}\n"
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
        "run_id": "RUN-ECDLP-5cad48-S2BD",
        "package": "stage2_bound_decomp",
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "n_cells": len(cells_out),
        "all_rebuild_matches": payload["all_rebuild_matches"],
        "miss_unique_tightest_cs_bound": payload["miss_unique_tightest_cs_bound"],
        "miss_unique_highest_aligned_ratio": payload["miss_unique_highest_aligned_ratio"],
        "next_tightest_more_uniform_than_miss": payload["next_tightest_more_uniform_than_miss"],
        "raw_result_sha256": raw_sha,
        "not_a_W_decay_claim": True,
    }
    (EXP / "execution-report-s2bd.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(
        json.dumps(
            {
                "valid": True,
                "n_cells": len(cells_out),
                "all_rebuild_matches": payload["all_rebuild_matches"],
                "miss_unique_tightest_cs_bound": payload["miss_unique_tightest_cs_bound"],
                "miss_unique_highest_aligned_ratio": payload["miss_unique_highest_aligned_ratio"],
                "next_tightest_more_uniform_than_miss": payload["next_tightest_more_uniform_than_miss"],
                "raw_sha": raw_sha,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
