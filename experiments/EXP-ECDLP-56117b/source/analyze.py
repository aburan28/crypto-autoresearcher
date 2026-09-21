"""Pool EXP-ECDLP-56117b measurement runs into g3_verdict_table.json.

BCa resampling unit is THE SEED (specification.yaml `bootstrap`).
Numeric results are read from runs/; this script does not re-enumerate basins.
"""

from __future__ import annotations

import itertools
import json
import math
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import yaml

from run_cell import (
    INFERENCE,
    REPO_ROOT,
    collect_environment,
    git_state,
    independence_attestation,
    peak_rss_bytes,
    py_json,
    write_json,
    write_yaml,
    cpu_seconds,
    utc_now,
)

RUNS_ROOT = REPO_ROOT / "experiments" / "EXP-ECDLP-56117b" / "runs"

CELLS_FIVE = ["a16r2", "a4r2", "a16r4", "a16r8", "a8r4", "a8r8"]
CELL_A8R2 = "a8r2"
FIVE_SEEDS = [1, 2, 3, 4, 5]
TWENTY_SEEDS = list(range(1, 21))

BCA_RESAMPLES = 10000
BCA_GENERATOR_SEED = 20260907
BCA_UNIT = "seed"


def ndtri(p: float) -> float:
    """Inverse standard-normal CDF (Acklam's rational approximation)."""
    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")
    a = [
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    ]
    b = [
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    ]
    c = [
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    ]
    d = [
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    ]
    plow = 0.02425
    phigh = 1.0 - plow
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (
            (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        ) / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(
        (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
        / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    )


def norm_cdf(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def bca_mean_ci(
    values: list[float],
    *,
    n_boot: int = BCA_RESAMPLES,
    seed: int = BCA_GENERATOR_SEED,
    alpha: float = 0.05,
) -> dict[str, Any]:
    x = np.asarray(values, dtype=np.float64)
    n = int(x.size)
    out: dict[str, Any] = {
        "resampling_unit": BCA_UNIT,
        "resamples": int(n_boot),
        "generator_seed": int(seed),
        "n": n,
        "method": "BCa 95%",
    }
    if n == 0:
        out["error"] = "empty sample"
        out["mean"] = None
        out["ci_low"] = None
        out["ci_high"] = None
        return out
    theta = float(x.mean())
    out["mean"] = theta
    if n == 1 or float(x.std(ddof=0)) == 0.0:
        out["ci_low"] = theta
        out["ci_high"] = theta
        out["degenerate"] = True
        out["note"] = "zero sample variance; BCa interval collapses to the mean"
        return out
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([int(seed)])))
    idx = rng.integers(0, n, size=(n_boot, n))
    theta_b = x[idx].mean(axis=1)
    prop = float(np.mean(theta_b < theta))
    prop_c = min(max(prop, 1.0 / (n_boot + 1.0)), n_boot / (n_boot + 1.0))
    z0 = ndtri(prop_c)
    loo = np.empty(n, dtype=np.float64)
    total = float(x.sum())
    for i in range(n):
        loo[i] = (total - float(x[i])) / (n - 1)
    loo_mean = float(loo.mean())
    d = loo_mean - loo
    num = float(np.sum(d ** 3))
    den = float(np.sum(d ** 2))
    acc = 0.0 if den == 0.0 else num / (6.0 * (den ** 1.5))

    def adj(z: float) -> float:
        den_a = 1.0 - acc * (z0 + z)
        if den_a == 0.0:
            return z0
        return z0 + (z0 + z) / den_a

    a1 = norm_cdf(adj(ndtri(alpha / 2.0)))
    a2 = norm_cdf(adj(ndtri(1.0 - alpha / 2.0)))
    a1 = min(max(a1, 0.0), 1.0)
    a2 = min(max(a2, 0.0), 1.0)
    out["ci_low"] = float(np.quantile(theta_b, a1))
    out["ci_high"] = float(np.quantile(theta_b, a2))
    out["z0"] = z0
    out["acceleration"] = acc
    out["alpha1"] = a1
    out["alpha2"] = a2
    out["degenerate"] = False
    return out


def load_summary(cell: str, seed: int) -> dict[str, Any] | None:
    path = RUNS_ROOT / f"RUN-ECDLP-56117b-{cell}-s{seed}" / "summary.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw(cell: str, seed: int) -> dict[str, Any] | None:
    path = RUNS_ROOT / f"RUN-ECDLP-56117b-{cell}-s{seed}" / "raw-result.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def seed_record(summary: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "seed": summary.get("seed"),
        "run_id": summary.get("run_id"),
        "status": summary.get("status"),
        "valid": summary.get("valid"),
        "margin": summary.get("margin"),
        "top_share_Tsel": summary.get("top_share_Tsel"),
        "static_cov": summary.get("static_cov"),
        "g3_s": summary.get("g3_s"),
        "wall_seconds": summary.get("wall_seconds"),
        "peak_rss_bytes": summary.get("peak_rss_bytes"),
    }
    if summary.get("margin_null") is not None:
        rec["margin_null"] = summary.get("margin_null")
        rec["static_cov_null"] = summary.get("static_cov_null")
    return rec


def five_seed_block(cell: str) -> dict[str, Any]:
    recs = []
    missing = []
    invalid = []
    for s in FIVE_SEEDS:
        sm = load_summary(cell, s)
        if sm is None:
            missing.append(s)
            continue
        recs.append(seed_record(sm))
        if not sm.get("valid"):
            invalid.append(s)
    valid_recs = [r for r in recs if r.get("valid") and r.get("margin") is not None]
    margins = [float(r["margin"]) for r in valid_recs]
    g3_flags = [bool(r["g3_s"]) for r in valid_recs]
    pass_count = int(sum(g3_flags))
    n = len(valid_recs)
    verdict = None
    if n == 5 and not missing and not invalid:
        verdict = "PASS" if pass_count >= 4 else "FAIL"
    block = {
        "cell": cell,
        "verdict_rule": "frozen_4_of_5",
        "seeds_declared": FIVE_SEEDS,
        "n_valid": n,
        "missing_seeds": missing,
        "invalid_seeds": invalid,
        "pass_count": pass_count,
        "pass_count_out_of": n,
        "verdict": verdict,
        "per_seed": recs,
        "pooled_mean_margin": float(np.mean(margins)) if margins else None,
        "bca_95": bca_mean_ci(margins) if margins else None,
        "min_margin": min(margins) if margins else None,
        "max_margin": max(margins) if margins else None,
        "resampling_unit": BCA_UNIT,
        "resamples": BCA_RESAMPLES,
    }
    if cell == "a16r2":
        nulls = [float(r["margin_null"]) for r in valid_recs if r.get("margin_null") is not None]
        pairs = [
            {
                "seed": r["seed"],
                "margin": r["margin"],
                "margin_null": r.get("margin_null"),
                "null_larger": (
                    r.get("margin_null") is not None
                    and r["margin"] is not None
                    and r["margin_null"] > r["margin"]
                ),
            }
            for r in recs
        ]
        block["null_a"] = {
            "n": len(nulls),
            "per_seed": pairs,
            "n_null_strictly_larger": int(sum(1 for p in pairs if p["null_larger"])),
        }
    return block


def a8r2_block() -> dict[str, Any]:
    recs = []
    missing = []
    invalid = []
    for s in TWENTY_SEEDS:
        sm = load_summary(CELL_A8R2, s)
        if sm is None:
            missing.append(s)
            continue
        recs.append(seed_record(sm))
        if not sm.get("valid"):
            invalid.append(s)
    valid_recs = [r for r in recs if r.get("valid") and r.get("margin") is not None]
    margins = [float(r["margin"]) for r in valid_recs]
    n_nonneg = int(sum(1 for m in margins if m >= 0.0))
    n_pos = int(sum(1 for m in margins if m > 0.0))
    n_neg = int(sum(1 for m in margins if m < 0.0))
    n_zero = int(sum(1 for m in margins if m == 0.0))
    subset_frac = None
    subset_n_pass = None
    if len(valid_recs) == 20:
        flags = [1 if r["g3_s"] else 0 for r in valid_recs]
        n_pass_sub = 0
        n_sub = 0
        for comb in itertools.combinations(flags, 5):
            n_sub += 1
            if sum(comb) >= 4:
                n_pass_sub += 1
        subset_n_pass = n_pass_sub
        subset_frac = n_pass_sub / float(n_sub)
    block = {
        "cell": CELL_A8R2,
        "verdict_rule": "distribution_only_no_binary_threshold",
        "binary_g3_verdict": None,
        "note": (
            "No binary G3 PASS/FAIL threshold is applied at this cell. "
            "pass_count/20 is the count of non-negative margins, a descriptive "
            "statistic, not a verdict."
        ),
        "seeds_declared": TWENTY_SEEDS,
        "n_valid": len(valid_recs),
        "missing_seeds": missing,
        "invalid_seeds": invalid,
        "per_seed": recs,
        "margins": margins,
        "pass_count_nonnegative": n_nonneg,
        "pass_count_out_of": len(margins),
        "n_strictly_positive_margins": n_pos,
        "n_negative_margins": n_neg,
        "n_zero_margins": n_zero,
        "min_margin": min(margins) if margins else None,
        "median_margin": float(np.median(margins)) if margins else None,
        "max_margin": max(margins) if margins else None,
        "pooled_mean_margin": float(np.mean(margins)) if margins else None,
        "bca_95": bca_mean_ci(margins) if margins else None,
        "resampling_unit": BCA_UNIT,
        "resamples": BCA_RESAMPLES,
        "five_seed_subset_descriptive": {
            "n_combinations": 15504 if len(valid_recs) == 20 else None,
            "n_that_would_g3_pass_under_frozen_4_of_5": subset_n_pass,
            "fraction": subset_frac,
            "note": (
                "Secondary, non-criterion descriptive statistic. MUST NOT be "
                "used as a success or falsification criterion."
            ),
        },
        "tail_check": {
            "n_negative_margins": n_neg,
            "smallest_margin": min(margins) if margins else None,
        },
    }
    return block


def decay_block(a_label: str, cells: list[str]) -> dict[str, Any]:
    """cells ordered r=2,4,8."""
    per_seed = []
    n_nonincreasing = 0
    n_pairs = 0
    for s in FIVE_SEEDS:
        row = {"seed": s, "by_r": {}}
        margins = []
        ok = True
        for cell, r in zip(cells, [2, 4, 8]):
            sm = load_summary(cell, s)
            if sm is None or not sm.get("valid") or sm.get("margin") is None:
                ok = False
                row["by_r"][r] = None
                margins.append(None)
            else:
                row["by_r"][r] = {
                    "cell": cell,
                    "margin": sm["margin"],
                    "g3_s": sm["g3_s"],
                }
                margins.append(float(sm["margin"]))
        if ok:
            n_pairs += 1
            noninc = margins[0] >= margins[1] >= margins[2]
            row["nonincreasing"] = bool(noninc)
            if noninc:
                n_nonincreasing += 1
        else:
            row["nonincreasing"] = None
        per_seed.append(row)
    verdicts = {}
    for cell in cells:
        block = five_seed_block(cell)
        verdicts[cell] = {
            "verdict": block["verdict"],
            "pass_count": block["pass_count"],
        }
    return {
        "a": a_label,
        "cells_r2_r4_r8": cells,
        "per_seed": per_seed,
        "n_complete_triples": n_pairs,
        "n_nonincreasing": n_nonincreasing,
        "cell_verdicts": verdicts,
        "requirement": "margin_s non-increasing in r; cell verdict FAIL by r=8",
    }


def raw_summary_agree(cell: str, seed: int) -> dict[str, Any]:
    sm = load_summary(cell, seed)
    raw = load_raw(cell, seed)
    if sm is None or raw is None:
        return {"ok": False, "reason": "missing file"}
    payload = raw.get("payload") or {}
    checks = {
        "margin": sm.get("margin") == payload.get("margin"),
        "top_share_Tsel": sm.get("top_share_Tsel") == payload.get("top_share_Tsel"),
        "static_cov": sm.get("static_cov") == payload.get("static_cov"),
        "g3_s": sm.get("g3_s") == payload.get("g3_s"),
        "status": sm.get("status") == raw.get("status"),
    }
    return {"ok": all(checks.values()), "checks": checks}


def build_table() -> dict[str, Any]:
    five = {c: five_seed_block(c) for c in CELLS_FIVE}
    a8 = a8r2_block()
    decay_a16 = decay_block("1/16", ["a16r2", "a16r4", "a16r8"])
    # decay at a=1/8 uses a8r2 seeds 1-5, not a separate cell id for r=2
    decay_a8 = {
        "a": "1/8",
        "cells_r2_r4_r8": ["a8r2 (seeds 1-5 only)", "a8r4", "a8r8"],
        "per_seed": [],
        "n_complete_triples": 0,
        "n_nonincreasing": 0,
        "cell_verdicts": {
            "a8r4": {"verdict": five["a8r4"]["verdict"], "pass_count": five["a8r4"]["pass_count"]},
            "a8r8": {"verdict": five["a8r8"]["verdict"], "pass_count": five["a8r8"]["pass_count"]},
        },
        "requirement": "margin_s non-increasing in r; cell verdict FAIL by r=8",
        "a8r2_note": (
            "r=2 at a=1/8 uses the first five seeds of the 20-seed a8r2 cell, "
            "not a separate five-seed verdict."
        ),
    }
    n_pairs = 0
    n_noninc = 0
    for s in FIVE_SEEDS:
        sm2 = load_summary("a8r2", s)
        sm4 = load_summary("a8r4", s)
        sm8 = load_summary("a8r8", s)
        row: dict[str, Any] = {"seed": s, "by_r": {}}
        ok = True
        ms = []
        for r, sm, cell in [(2, sm2, "a8r2"), (4, sm4, "a8r4"), (8, sm8, "a8r8")]:
            if sm is None or not sm.get("valid") or sm.get("margin") is None:
                ok = False
                row["by_r"][r] = None
                ms.append(None)
            else:
                row["by_r"][r] = {"cell": cell, "margin": sm["margin"], "g3_s": sm["g3_s"]}
                ms.append(float(sm["margin"]))
        if ok:
            n_pairs += 1
            noninc = ms[0] >= ms[1] >= ms[2]
            row["nonincreasing"] = bool(noninc)
            if noninc:
                n_noninc += 1
        else:
            row["nonincreasing"] = None
        decay_a8["per_seed"].append(row)
    decay_a8["n_complete_triples"] = n_pairs
    decay_a8["n_nonincreasing"] = n_noninc

    agree = []
    all_ok = True
    for cell, seeds in (
        [("a16r2", FIVE_SEEDS), ("a8r2", TWENTY_SEEDS)]
        + [(c, FIVE_SEEDS) for c in ["a4r2", "a16r4", "a16r8", "a8r4", "a8r8"]]
    ):
        for s in seeds:
            r = raw_summary_agree(cell, s)
            r["cell"] = cell
            r["seed"] = s
            agree.append(r)
            if not r["ok"]:
                all_ok = False

    det = None
    raw1 = load_raw("a16r2", 1)
    if raw1 is not None:
        det = raw1.get("determinism_check")

    walls = []
    rss = []
    statuses: dict[str, int] = {}
    for cell, seeds in (
        [("a16r2", FIVE_SEEDS), ("a8r2", TWENTY_SEEDS)]
        + [(c, FIVE_SEEDS) for c in ["a4r2", "a16r4", "a16r8", "a8r4", "a8r8"]]
    ):
        for s in seeds:
            sm = load_summary(cell, s)
            if sm is None:
                statuses["not_run"] = statuses.get("not_run", 0) + 1
                continue
            st = sm.get("status") or "unknown"
            statuses[st] = statuses.get(st, 0) + 1
            if sm.get("wall_seconds") is not None:
                walls.append(float(sm["wall_seconds"]))
            if sm.get("peak_rss_bytes") is not None:
                rss.append(int(sm["peak_rss_bytes"]))

    table = {
        "experiment_id": "EXP-ECDLP-56117b",
        "analysis_run_id": "RUN-ECDLP-56117b-analysis-001",
        "claim_tier": "toy",
        "bootstrap": {
            "method": "BCa 95%",
            "resampling_unit": BCA_UNIT,
            "resamples": BCA_RESAMPLES,
            "generator_seed": BCA_GENERATOR_SEED,
            "note": (
                "THE SEED is the resampling unit. Each cell holds exactly one "
                "margin per seed."
            ),
        },
        "frozen_prediction_reference": {
            "source": "experiments/EXP-ECDLP-56117b/specification.yaml preregistered_prediction",
            "provenance": "internal",
            "quantity": (
                "Sign of margin_s at a=1/16, r=2, N=2^24, T_sel=128 on this "
                "independent instrument family over seeds {1..5}; and the shape "
                "of the margin distribution at a=1/8, r=2 over seeds {1..20}."
            ),
            "formula_as_registered": (
                "Under the frozen >= 4/5 rule, a=1/16 is predicted G3 PASS. "
                "a=1/8 is predicted to have a small positive population margin "
                "with instrument-family variance straddling zero. THIS "
                "PREDICTION MAY FAIL and is not a success criterion. a=1/4 is "
                "predicted G3 FAIL. Decay is predicted FAIL by r=8."
            ),
        },
        "five_seed_cells": five,
        "a8r2_distribution": a8,
        "decay": {"a_1_16": decay_a16, "a_1_8": decay_a8},
        "known_false_a4r2": {
            "cell": "a4r2",
            "expected_outcome": "G3 FAIL",
            "verdict": five["a4r2"]["verdict"],
            "pass_count": five["a4r2"]["pass_count"],
            "per_seed_margins": [r.get("margin") for r in five["a4r2"]["per_seed"]],
        },
        "raw_summary_agreement": {"all_ok": all_ok, "n_checked": len(agree)},
        "determinism_check_from_a16r2_s1": det,
        "resource_ranges_measured": {
            "wall_seconds_min": min(walls) if walls else None,
            "wall_seconds_max": max(walls) if walls else None,
            "peak_rss_bytes_min": min(rss) if rss else None,
            "peak_rss_bytes_max": max(rss) if rss else None,
        },
        "run_status_tally": statuses,
        "interpretation": "observations_only_no_hypothesis_conclusion",
    }
    return table


def main() -> int:
    outdir = RUNS_ROOT / "RUN-ECDLP-56117b-analysis-001"
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = (
        "python3 experiments/EXP-ECDLP-56117b/source/analyze.py "
        f"--outdir {outdir.as_posix()}"
    )
    (outdir / "command.txt").write_text(cmd + "\n", encoding="utf-8")
    started = utc_now()
    t0 = time.perf_counter()
    stdout_lines = [f"analysis start {started}"]
    stderr_text = ""
    git = git_state(REPO_ROOT)
    env = collect_environment()
    try:
        table = build_table()
        status = "completed_valid"
        invalid_reason = None
        failure_class = None
        stdout_lines.append(
            "a16r2 verdict={0} pass_count={1}".format(
                table["five_seed_cells"]["a16r2"]["verdict"],
                table["five_seed_cells"]["a16r2"]["pass_count"],
            )
        )
        a8 = table["a8r2_distribution"]
        stdout_lines.append(
            "a8r2 n_nonneg={0}/{1} min={2} median={3} max={4} mean={5}".format(
                a8["pass_count_nonnegative"],
                a8["pass_count_out_of"],
                a8["min_margin"],
                a8["median_margin"],
                a8["max_margin"],
                a8["pooled_mean_margin"],
            )
        )
        stdout_lines.append(
            "a4r2 verdict={0} pass_count={1}".format(
                table["known_false_a4r2"]["verdict"],
                table["known_false_a4r2"]["pass_count"],
            )
        )
    except Exception as exc:
        import traceback

        table = {"error": f"{type(exc).__name__}: {exc}"}
        status = "failed_infrastructure"
        failure_class = "infrastructure_error"
        invalid_reason = f"{type(exc).__name__}: {exc}"
        stderr_text = traceback.format_exc()
        stdout_lines.append(f"FAILED {invalid_reason}")

    wall = time.perf_counter() - t0
    finished = utc_now()
    rss = peak_rss_bytes()
    cpu = cpu_seconds()
    valid = status == "completed_valid"

    raw = {
        "run_id": "RUN-ECDLP-56117b-analysis-001",
        "experiment_id": "EXP-ECDLP-56117b",
        "status": status,
        "failure_class": failure_class,
        "invalid_reason": invalid_reason,
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "g3_verdict_table": table,
        "timing": {"started_at": started, "finished_at": finished, "wall_seconds": wall},
        "resources": {"peak_rss_bytes": rss, "cpu_seconds": cpu},
    }
    summary = {
        "run_id": "RUN-ECDLP-56117b-analysis-001",
        "status": status,
        "valid": valid,
        "resampling_unit": BCA_UNIT,
        "resamples": BCA_RESAMPLES,
        "a16r2_verdict": (table.get("five_seed_cells") or {}).get("a16r2", {}).get("verdict")
        if isinstance(table, dict)
        else None,
        "a16r2_pass_count": (table.get("five_seed_cells") or {}).get("a16r2", {}).get("pass_count")
        if isinstance(table, dict)
        else None,
        "a8r2_n_nonnegative": (table.get("a8r2_distribution") or {}).get("pass_count_nonnegative")
        if isinstance(table, dict)
        else None,
        "a4r2_verdict": (table.get("known_false_a4r2") or {}).get("verdict")
        if isinstance(table, dict)
        else None,
        "wall_seconds": wall,
        "peak_rss_bytes": rss,
    }
    cost = {
        "run_id": "RUN-ECDLP-56117b-analysis-001",
        "modeled": {
            "bca_resamples": BCA_RESAMPLES,
            "bca_generator_seed": BCA_GENERATOR_SEED,
            "resampling_unit": BCA_UNIT,
        },
        "measured": {
            "wall_seconds": wall,
            "peak_rss_bytes": rss,
            "cpu_seconds": cpu,
            "n_measurement_summaries_read": (table.get("raw_summary_agreement") or {}).get(
                "n_checked"
            )
            if isinstance(table, dict)
            else None,
        },
        "note": "Analysis enumerates nothing; BCa resamples and unit are modeled/declared, read metrics are measured from run files.",
    }
    manifest = {
        "run": {
            "id": "RUN-ECDLP-56117b-analysis-001",
            "experiment_id": "EXP-ECDLP-56117b",
            "task_id": "TASK-20260907-b407d8",
            "status": status,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_tree": git["dirty_tree"],
                "branch": git["branch"],
                "command": cmd,
            },
            "inference": INFERENCE,
            "environment": env,
            "inputs": {
                "seed": BCA_GENERATOR_SEED,
                "parameters": {
                    "resampling_unit": BCA_UNIT,
                    "resamples": BCA_RESAMPLES,
                },
            },
            "timing": {
                "started_at": started,
                "finished_at": finished,
                "wall_seconds": wall,
            },
            "resources": {"peak_rss_bytes": rss, "cpu_seconds": cpu},
            "result": {
                "metrics": {
                    "resampling_unit": BCA_UNIT,
                    "a16r2_verdict": summary["a16r2_verdict"],
                    "a8r2_n_nonnegative": summary["a8r2_n_nonnegative"],
                    "a4r2_verdict": summary["a4r2_verdict"],
                },
                "valid": valid,
                "invalid_reason": invalid_reason,
                "failure_class": failure_class,
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "independence_attestation": independence_attestation(),
            "artifacts": {
                "g3_verdict_table.json": "g3_verdict_table.json",
                "raw-result.json": "raw-result.json",
                "summary.json": "summary.json",
                "cost_table.json": "cost_table.json",
            },
            "claim_tier": "toy",
        }
    }
    write_json(outdir / "g3_verdict_table.json", table)
    write_json(outdir / "raw-result.json", raw)
    write_json(outdir / "summary.json", summary)
    write_json(outdir / "cost_table.json", cost)
    write_json(outdir / "environment.json", env)
    write_yaml(outdir / "manifest.yaml", manifest)
    (outdir / "stdout.log").write_text("\n".join(stdout_lines) + "\n", encoding="utf-8")
    (outdir / "stderr.log").write_text(stderr_text, encoding="utf-8")
    print("\n".join(stdout_lines), flush=True)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
