#!/usr/bin/env python3
"""Independent arithmetic for TASK-20260823-80125f.

Reads only snapshot-frozen Phase-2 JSON/YAML inputs named by task-brief.md and
prints one machine-readable summary.  It never writes or mutates an artifact.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[7]
B6 = ROOT / "coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02"
B5 = ROOT / "coordination/goals/GOAL-MD5-001/batches/BATCH-7215fa"
RUN_ROOT = B6 / "tasks/TASK-20260822-767bb1/runs"
THRESHOLD = 12


def raw(object_kind: str, primitive: str) -> dict:
    path = RUN_ROOT / (
        f"RUN-MDFIVE-b6-{object_kind}-{primitive}-prod/raw-result.json"
    )
    return json.loads(path.read_text())


def manifest(object_kind: str, primitive: str) -> dict:
    path = RUN_ROOT / (
        f"RUN-MDFIVE-b6-{object_kind}-{primitive}-prod/manifest.yaml"
    )
    return yaml.safe_load(path.read_text())["run"]


def binom_tail_ge(n: int, x: int, p: float) -> float:
    return sum(
        math.comb(n, k) * p**k * (1.0 - p) ** (n - k)
        for k in range(x, n + 1)
    )


def binom_tail_le(n: int, x: int, p: float) -> float:
    return sum(
        math.comb(n, k) * p**k * (1.0 - p) ** (n - k)
        for k in range(0, x + 1)
    )


def clopper_pearson_95(x: int, n: int) -> tuple[float, float]:
    """Two-sided exact 95% interval, inverted with binomial tails."""
    alpha_half = 0.025
    if x == 0:
        lower = 0.0
    else:
        lo, hi = 0.0, x / n
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if binom_tail_ge(n, x, mid) > alpha_half:
                hi = mid
            else:
                lo = mid
        lower = (lo + hi) / 2.0
    if x == n:
        upper = 1.0
    else:
        lo, hi = x / n, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if binom_tail_le(n, x, mid) > alpha_half:
                lo = mid
            else:
                hi = mid
        upper = (lo + hi) / 2.0
    return lower, upper


def exact_two_sided_p_at_half(x: int, n: int) -> float:
    # At p=1/2 the equal-or-less-likely definition is equivalent to doubling
    # the smaller tail for x != n/2.
    if x == n / 2:
        return 1.0
    if x > n / 2:
        return min(1.0, 2.0 * binom_tail_ge(n, x, 0.5))
    return min(1.0, 2.0 * binom_tail_le(n, x, 0.5))


def gate_counts(result: dict) -> dict:
    f32 = [r["direction_A_rows"][0]["distinct_fwd_32bit"]
           for r in result["per_seed"]]
    f12 = [r["direction_A_rows"][0]["distinct_fwd_12bit"]
           for r in result["per_seed"]]
    b32 = [
        max(row["distinct_bwd_32bit"] for row in r["direction_B_rows"])
        for r in result["per_seed"]
    ]
    b12 = [
        max(row["distinct_bwd_12bit"] for row in r["direction_B_rows"])
        for r in result["per_seed"]
    ]
    return {
        "n": len(f12),
        "forward_32bit_passes": sum(v >= THRESHOLD for v in f32),
        "forward_12bit_passes": sum(v >= THRESHOLD for v in f12),
        "backward_32bit_max_passes": sum(v >= THRESHOLD for v in b32),
        "backward_12bit_max_passes": sum(v >= THRESHOLD for v in b12),
        "forward_32bit_range": [min(f32), max(f32)],
        "forward_12bit_range": [min(f12), max(f12)],
        "backward_32bit_max_range": [min(b32), max(b32)],
        "backward_12bit_max_range": [min(b12), max(b12)],
    }


def rc4_failures(result: dict) -> dict:
    rows = []
    modeled_disagreements = 0
    for record in result["per_seed"]:
        rc4 = record["rc4"]
        bound = rc4["implied_distinct_32bit_bound"]
        observed32 = record["direction_A_rows"][0]["distinct_fwd_32bit"]
        observed12 = record["direction_A_rows"][0]["distinct_fwd_12bit"]
        modeled_disagreements += len(rc4["modeled_vs_measured_adjudications"])
        if observed32 > bound or observed12 > bound:
            rows.append({
                "seed": record["seed"],
                "measured_surviving_bits":
                    rc4["low_bit_positions_surviving_into_component"],
                "claimed_bound": bound,
                "observed_distinct_32bit": observed32,
                "observed_distinct_12bit": observed12,
            })
    return {
        "claimed_bound_violation_count": len(rows),
        "claimed_bound_violations": rows,
        "modeled_vs_two_point_bit_disagreements": modeled_disagreements,
    }


def main() -> None:
    results = {
        f"{obj}-{primitive}": raw(obj, primitive)
        for obj in ("primary", "null")
        for primitive in ("md4", "md5")
    }
    manifests = {
        f"{obj}-{primitive}": manifest(obj, primitive)
        for obj in ("primary", "null")
        for primitive in ("md4", "md5")
    }

    pass_confidence = {}
    for primitive in ("md4", "md5"):
        r = results[f"primary-{primitive}"]
        x = sum(
            row["direction_A_rows"][0]["distinct_fwd_12bit"] >= THRESHOLD
            for row in r["per_seed"]
        )
        lo, hi = clopper_pearson_95(x, len(r["per_seed"]))
        pass_confidence[primitive] = {
            "passes": x,
            "n": len(r["per_seed"]),
            "two_sided_exact_95pct_interval": [lo, hi],
            "two_sided_exact_p_against_p_equals_half":
                exact_two_sided_p_at_half(x, len(r["per_seed"])),
        }

    sixty_lo, sixty_hi = clopper_pearson_95(60, 100)
    minimum_n_for_exact_60pct_lower_above_half = None
    for n in range(5, 5001):
        x = round(0.60 * n)
        if abs(x / n - 0.60) > 1e-12:
            continue
        if clopper_pearson_95(x, n)[0] > 0.5:
            minimum_n_for_exact_60pct_lower_above_half = n
            break

    cost = {}
    for name, m in manifests.items():
        measured = float(m["cost_model"]["measured_wall_seconds"])
        ceiling = float(m["cost_model"]["declared_ceiling_seconds"])
        cost[name] = {
            "manifest_measured_wall_seconds": measured,
            "declared_ceiling_seconds": ceiling,
            "ceiling_over_measured_ratio": ceiling / measured,
            "ten_x_measured_seconds": 10.0 * measured,
            "would_10x_reach_ceiling": 10.0 * measured >= ceiling,
        }

    report = yaml.safe_load(
        (B6 / "tasks/TASK-20260822-767bb1/execution-report.yaml").read_text()
    )["execution_report"]
    report_production = [
        float(item["wrapper_measured_wall_seconds"])
        for item in report["runs"]["completed"][:4]
    ]
    manifest_production = [
        cost[name]["manifest_measured_wall_seconds"]
        for name in ("primary-md4", "primary-md5", "null-md4", "null-md5")
    ]

    b5 = json.loads((
        B5 / "tasks/TASK-20260821-372d67/runs/"
        "RUN-MDFIVE-b5-gate_and_controls/raw-result.json"
    ).read_text())
    ctl5 = b5["raw"]["k1_k2_6_controls"]["CTL_PO5_raw_set_degeneracy"]

    output = {
        "injectivity_threshold": THRESHOLD,
        "criterion_counts": {name: gate_counts(result)
                             for name, result in results.items()},
        "primary_forward_12bit_pass_confidence": pass_confidence,
        "sixty_forty_sensitivity": {
            "passes": 60,
            "n": 100,
            "two_sided_exact_95pct_interval": [sixty_lo, sixty_hi],
            "two_sided_exact_p_against_p_equals_half":
                exact_two_sided_p_at_half(60, 100),
            "minimum_n_at_exactly_60pct_for_exact_95pct_lower_above_half":
                minimum_n_for_exact_60pct_lower_above_half,
        },
        "rc4_primary": {
            primitive: rc4_failures(results[f"primary-{primitive}"])
            for primitive in ("md4", "md5")
        },
        "cost": cost,
        "production_wall_clock_reconciliation": {
            "execution_report_seconds": report_production,
            "execution_report_sum_seconds": sum(report_production),
            "frozen_manifest_seconds": manifest_production,
            "frozen_manifest_sum_seconds": sum(manifest_production),
            "difference_seconds":
                sum(manifest_production) - sum(report_production),
        },
        "batch5_ctl_po5b": {
            "raw_candidate_count": ctl5["raw_candidate_count"],
            "declared_ceiling": 4,
            "distinct_wA": ctl5["distinct_wA_in_raw_set"],
            "distinct_wB": ctl5["distinct_wB_in_raw_set"],
            "passed": ctl5["passed"],
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
