#!/usr/bin/env python3
"""Four-cell occupancy and CS-ingredient audit.

Authorized only under v1_stage2_occupancy_authorized / DEC-20260907-7914ac.
Rebuilds floor(Mx/p) labels from the Stage 2 recipe on four frozen cells.
Does not import stage2_exact.py, stage2_cs_audit.py, stage2.py,
stage2_floor_miss.py, or stage2_slack_census.py. Does not classify W.
Does not fit a. Certificate kind none. No a98ea9 Stage 5.
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

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[3]
O2 = REPO / "analysis" / "o2-sum-compatible-filters"
sys.path.insert(0, str(O2))
from fourier_obstruction import dlog_table  # noqa: E402

EXP = REPO / "experiments" / "EXP-ECDLP-5cad48"
AUTH = EXP / "amendments" / "v1_stage2_occupancy_authorized.yaml"
S2G_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S2G" / "raw-result.json"

ARM = "floor(Mx/p)"
FIELDS = ("G_exact", "M_delta_exact", "W_exact", "min_q", "cs_bound_exact")
CELLS = (
    {"id": "S2-P8219", "p": 8219, "a": 1, "b": 1, "N": 8117, "M": 9, "role": "miss"},
    {"id": "S2-P8219", "p": 8219, "a": 1, "b": 1, "N": 8117, "M": 20, "role": "same_cell_hold"},
    {"id": "S2-P8219", "p": 8219, "a": 1, "b": 1, "N": 8117, "M": 37, "role": "same_cell_hold"},
    {"id": "S2-P32779", "p": 32779, "a": 3, "b": 5, "N": 32909, "M": 13, "role": "next_tightest_hold"},
)


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
    if not block.get("occupancy_execution_authorized"):
        raise SystemExit("refuse: occupancy_execution_authorized is not true")
    if block.get("SMALL_W_or_LARGE_W"):
        raise SystemExit("refuse: authorization classified W")
    if block.get("fit_of_a"):
        raise SystemExit("refuse: authorization set fit_of_a true")
    if block.get("cs_bound_official_supported"):
        raise SystemExit("refuse: authorization set an official bound claim")


def occupancy_stats(hv: np.ndarray, m: int, n: int) -> dict:
    counts_before = np.bincount(hv, minlength=m)
    n_empty_before_remap = int(np.sum(counts_before == 0))
    used = np.flatnonzero(counts_before > 0)
    if len(used) < m:
        remap = -np.ones(m, dtype=np.int64)
        remap[used] = np.arange(len(used))
        hv = remap[hv]
        m = int(len(used))
    if m < 2:
        raise RuntimeError("M_eff < 2")
    hv = hv.astype(np.int64, copy=False)
    ind = np.zeros((m, n))
    for bucket in range(m):
        ind[bucket] = hv == bucket
    counts = ind.sum(axis=1)
    fourier = np.fft.rfft(ind, axis=1)
    fourier_s = np.fft.fft(fourier, axis=0)
    w_s = np.fft.ifft(fourier_s * fourier_s, axis=0)
    w = np.fft.irfft(w_s, n=n, axis=1).real
    num = np.stack([w[:, hv == c].sum(axis=1) for c in range(m)], axis=1)
    den = np.real(np.fft.ifft(np.fft.fft(counts) ** 2))
    pi = num / np.maximum(den[:, None], 1e-12)
    g = m * float(pi.max())
    tot = float(n) ** 2
    deltas = [sum(num[(c - d) % m, c] for c in range(m)) / tot for d in range(m)]
    dstar = int(np.argmax(deltas))
    delta = float(deltas[dstar])
    q = counts / n
    pi_c = pi[(np.arange(m) - dstar) % m, np.arange(m)]
    w_rel = float(np.sum(q * (pi_c / delta - 1.0) ** 2))
    min_q = float(q.min())
    return {
        "q": [float(x) for x in q],
        "n_empty_before_remap": n_empty_before_remap,
        "M_eff": int(m),
        "max_q": float(q.max()),
        "min_q": min_q,
        "dstar": dstar,
        "pi_c": [float(x) for x in pi_c],
        "max_pi_c": float(pi_c.max()),
        "G_exact": g,
        "M_delta_exact": m * delta,
        "W_exact": w_rel,
        "cs_bound_exact": 1.0 + (w_rel / max(min_q, 1e-18)) ** 0.5,
        "dstar_exact": dstar,
    }


def s2g_row(cell_id: str, m: int) -> dict:
    raw = json.loads(S2G_RAW.read_text())
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S2G":
        raise SystemExit("refuse: unexpected S2G run_id")
    for cell in raw.get("cells") or []:
        if cell.get("id") != cell_id:
            continue
        for ms in cell.get("Ms") or []:
            if int(ms["M"]) != m:
                continue
            rec = (ms.get("arms") or {}).get(ARM)
            if rec is None:
                raise SystemExit(f"refuse: S2G missing {cell_id} M={m} {ARM}")
            missing = [f for f in FIELDS if f not in rec]
            if missing:
                raise SystemExit(f"refuse: S2G missing {missing}")
            return {f: float(rec[f]) for f in FIELDS}
    raise SystemExit(f"refuse: {cell_id} M={m} not in S2G")


def close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-12 * max(1.0, abs(b))


def main() -> int:
    t0 = time.time()
    refuse_unless_authorized()
    cells_out = []
    xs_cache: dict[tuple[int, int, int, int], np.ndarray] = {}
    for cell in CELLS:
        p, a, b, n, m = cell["p"], cell["a"], cell["b"], cell["N"], cell["M"]
        key = (p, a, b, n)
        if key not in xs_cache:
            _g0, pts = dlog_table(p, a, b, n)
            if len(pts) != n:
                raise SystemExit(f"refuse: dlog table length {len(pts)} != {n}")
            xs_cache[key] = np.array(
                [0 if pt is None else pt[0] for pt in pts], dtype=np.int64
            )
        labels = (xs_cache[key] * m) // p
        exact = occupancy_stats(labels, m, n)
        aligned = exact["G_exact"] / exact["M_delta_exact"]
        aligned_holds = aligned <= exact["cs_bound_exact"]
        archived = s2g_row(cell["id"], m)
        match = all(close(exact[f], archived[f]) for f in FIELDS)
        cells_out.append(
            {
                "id": cell["id"],
                "p": p,
                "a": a,
                "b": b,
                "N": n,
                "M": m,
                "role": cell["role"],
                "arm": ARM,
                "occupancy": {
                    "q": exact["q"],
                    "n_empty_before_remap": exact["n_empty_before_remap"],
                    "M_eff": exact["M_eff"],
                    "max_q": exact["max_q"],
                    "min_q": exact["min_q"],
                    "dstar": exact["dstar"],
                    "pi_c": exact["pi_c"],
                    "max_pi_c": exact["max_pi_c"],
                },
                "exact": {f: exact[f] for f in FIELDS},
                "aligned_ratio": aligned,
                "aligned_holds": aligned_holds,
                "archived_s2g": archived,
                "matches_s2g": match,
            }
        )
    elapsed = time.time() - t0
    git = _git_info()
    all_match = all(row["matches_s2g"] for row in cells_out)
    payload = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2OC",
        "package": "stage2_occupancy",
        "certificate_kind": "none",
        "n_cells": len(cells_out),
        "arm": ARM,
        "label_definition": "(x*M)//p on dlog-table x-coordinates, identity at 0",
        "imported_forbidden_producers": False,
        "cells": cells_out,
        "all_match_s2g": all_match,
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
    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S2OC"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    recorded_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S2OC",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-9fb238",
            "stage": 2,
            "status": "completed_valid",
            "recorded_at": recorded_at,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": git["dirty_summary"],
                "command": "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_occupancy.py",
                "source_path": "experiments/EXP-ECDLP-5cad48/implementation/stage2_occupancy.py",
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
                    "n_cells": len(cells_out),
                    "arm": ARM,
                    "authorized_by": "DEC-20260907-7914ac",
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
                "validity_reason": "Four-cell occupancy and CS-ingredient package complete.",
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only occupancy audit; no discrete log.",
                },
                "metrics": {
                    "n_cells": len(cells_out),
                    "all_match_s2g": all_match,
                    "not_a_W_decay_claim": True,
                    "cs_bound_official_supported": False,
                },
                "scientific_boundary": (
                    "Four frozen floor cells only. Occupancy is recorded, "
                    "not a W class. No official bound. No a98ea9 Stage 5."
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
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_occupancy.py\n"
    )
    (run_dir / "stdout.log").write_text(
        f"n_cells={len(cells_out)} all_match_s2g={all_match} raw_sha={raw_sha}\n"
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
        "run_id": "RUN-ECDLP-5cad48-S2OC",
        "package": "stage2_occupancy",
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "n_cells": len(cells_out),
        "all_match_s2g": all_match,
        "raw_result_sha256": raw_sha,
        "not_a_W_decay_claim": True,
    }
    (EXP / "execution-report-s2oc.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(json.dumps({
        "valid": True,
        "n_cells": len(cells_out),
        "all_match_s2g": all_match,
        "raw_sha": raw_sha,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
