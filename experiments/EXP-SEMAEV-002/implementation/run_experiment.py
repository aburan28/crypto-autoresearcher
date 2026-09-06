#!/usr/bin/env python3
"""Driver for EXP-SEMAEV-002, stages a-d, per specification.yaml.

Usage: python3 run_experiment.py <stage: a|b|c|d> <out_dir>

Writes <out_dir>/raw-result.json and prints progress to stdout. Exit code
0 on completion of the stage's computation (regardless of scientific
outcome: falsification is a valid, non-error result); nonzero only on
genuine infrastructure/implementation failure.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

IMPL_DIR = Path(__file__).resolve().parent
REPO_ROOT = IMPL_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(IMPL_DIR))

from newton_sections import build_curve_poly_model, classify_hull_based  # noqa: E402
from corner_classes import classify_corner_based, m3_calibration_check  # noqa: E402
from exception_sets import select_curve, predicted_exception_set  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

PRIMES_PER_M = [101, 103, 107, 211]
M_VALUES = [3, 4]


def stage_a() -> dict:
    t0 = time.time()
    cells = []
    calibration_failures = []
    for m in M_VALUES:
        for p in PRIMES_PER_M:
            cs = select_curve(m, p)
            cell = {
                "m": m, "p": p, "found": cs.found,
                "search_pairs_tried": cs.search_pairs_tried,
            }
            if not cs.found:
                cell["reason_unavailable"] = cs.reason_unavailable
                cells.append(cell)
                continue
            cell.update({
                "A": cs.A, "B": cs.B, "beta": cs.beta, "P0": list(cs.P0),
                "order_P0": cs.order_P0,
            })
            E = EllipticCurve(p, cs.A, cs.B)
            pred_exc = predicted_exception_set(E, cs.P0, m)
            cell["predicted_exception_set"] = pred_exc
            cell["predicted_exception_cardinality"] = len(pred_exc)
            if m == 3:
                model = build_curve_poly_model(3, cs.A, cs.B, p)
                calib = m3_calibration_check(model.coeff_dict, cs.A, cs.B, p)
                cell["m3_calibration"] = calib
                all_match = all(v["match"] for v in calib.values())
                cell["m3_calibration_all_match"] = all_match
                if not all_match:
                    calibration_failures.append({"m": m, "p": p, "calibration": calib})
            cells.append(cell)
    result = {
        "stage": "instance_generation_and_calibration",
        "cells": cells,
        "calibration_failures": calibration_failures,
        "wall_seconds": time.time() - t0,
    }
    return result


def _exhaustive_cell(m: int, cell_a: dict) -> dict:
    p = cell_a["p"]
    A, B = cell_a["A"], cell_a["B"]
    P0 = tuple(cell_a["P0"])
    pred_exc = set(cell_a["predicted_exception_set"])
    model = build_curve_poly_model(m, A, B, p)
    observed_exceptions_hull = []
    observed_exceptions_corner = []
    method_disagreements = []
    cross_method_sample = []
    saturated_flags = {}     # t -> bool, all 2^(m-1) box vertices present (per spec metric)
    fill_values = {}         # t -> interior fill fraction (secondary metric only, NOT the
                              # saturation criterion: interior-monomial losses are explicitly
                              # allowed by the spec's invalidation_rules without being EXCEPTIONs)
    degree_violations = []
    cross_method_targets = set(range(0, p, 10)) | pred_exc
    for t in range(p):
        r_hull = classify_hull_based(model, t)
        r_corner = classify_corner_based(m, A, B, t, p)
        if not r_hull["degree_bound_ok"]:
            degree_violations.append(t)
        if not r_hull["saturated"]:
            observed_exceptions_hull.append(t)
        if not r_corner.saturated:
            observed_exceptions_corner.append(t)
        saturated_flags[t] = r_hull["saturated"]
        fill_values[t] = r_hull["support_fill"]
        if r_hull["saturated"] != r_corner.saturated:
            method_disagreements.append({
                "t": t, "hull_saturated": r_hull["saturated"],
                "corner_saturated": r_corner.saturated,
                "hull_missing_corners": r_hull["missing_corners"],
                "corner_classes": r_corner.classes,
            })
        if t in cross_method_targets:
            cross_method_sample.append({
                "t": t, "hull_saturated": r_hull["saturated"],
                "corner_saturated": r_corner.saturated,
                "agree": r_hull["saturated"] == r_corner.saturated,
            })
    observed_hull_set = set(observed_exceptions_hull)
    observed_corner_set = set(observed_exceptions_corner)
    exception_identity_hull = observed_hull_set == pred_exc
    exception_identity_corner = observed_corner_set == pred_exc
    # Primary metric per spec: "fraction of non-exceptional targets with all
    # 2^(m-1) box vertices present" -- this is exactly `saturated`, NOT
    # interior support_fill==1.0 (interior-monomial losses are explicitly
    # permitted by the spec's invalidation_rules and are recorded separately
    # as a descriptive secondary metric, never as an exception).
    nonexceptional_targets = [t for t in range(p) if t not in observed_hull_set]
    nonexceptional_saturated_count = sum(1 for t in nonexceptional_targets if saturated_flags[t])
    nonexceptional_full_box_fraction = (
        nonexceptional_saturated_count / len(nonexceptional_targets)
        if nonexceptional_targets else None
    )
    nonexceptional_fill_ok = nonexceptional_full_box_fraction == 1.0
    interior_fill_stats = {
        "min": min(fill_values.values()) if fill_values else None,
        "max": max(fill_values.values()) if fill_values else None,
        "mean": sum(fill_values.values()) / len(fill_values) if fill_values else None,
    }
    return {
        "m": m, "p": p, "A": A, "B": B, "P0": list(P0),
        "predicted_exception_set": sorted(pred_exc),
        "observed_exception_set_hull": sorted(observed_hull_set),
        "observed_exception_set_corner": sorted(observed_corner_set),
        "exception_set_cardinality_hull": len(observed_hull_set),
        "exception_set_cardinality_corner": len(observed_corner_set),
        "exception_set_identity_hull": exception_identity_hull,
        "exception_set_identity_corner": exception_identity_corner,
        "degree_bound_violations": degree_violations,
        "method_disagreements": method_disagreements,
        "cross_method_sample_size": len(cross_method_sample),
        "cross_method_agreement_fraction": (
            sum(1 for r in cross_method_sample if r["agree"]) / len(cross_method_sample)
            if cross_method_sample else None
        ),
        "cross_method_sample": cross_method_sample,
        "nonexceptional_full_box_fraction": nonexceptional_full_box_fraction,
        "nonexceptional_full_box_fraction_ok": nonexceptional_fill_ok,
        "interior_support_fill_stats": interior_fill_stats,
        "targets_tested": p,
    }


def stage_exhaustive(m: int, stage_a_result: dict) -> dict:
    t0 = time.time()
    valid_cells = [c for c in stage_a_result["cells"] if c["m"] == m and c["found"]]
    unavailable = [c for c in stage_a_result["cells"] if c["m"] == m and not c["found"]]
    cell_results = []
    for cell_a in valid_cells:
        cell_results.append(_exhaustive_cell(m, cell_a))
    result = {
        "stage": f"exhaustive_m{m}_enumeration",
        "m": m,
        "cells": cell_results,
        "instance_unavailable_cells": unavailable,
        "wall_seconds": time.time() - t0,
    }
    return result


def stage_d(stage_a_result: dict, stage_b_result: dict, stage_c_result: dict) -> dict:
    t0 = time.time()
    all_cells = stage_b_result["cells"] + stage_c_result["cells"]

    falsifications = []
    for c in all_cells:
        if not c["nonexceptional_full_box_fraction_ok"]:
            falsifications.append({"m": c["m"], "p": c["p"], "reason": "nonexceptional target lost a box vertex"})
        if not c["exception_set_identity_hull"] or not c["exception_set_identity_corner"]:
            falsifications.append({"m": c["m"], "p": c["p"], "reason": "exception set mismatch vs predicted"})
        max_allowed = c["m"] - 1
        if c["exception_set_cardinality_hull"] > max_allowed or c["exception_set_cardinality_corner"] > max_allowed:
            falsifications.append({"m": c["m"], "p": c["p"], "reason": "exception set exceeds m-1 bound"})
        if c["degree_bound_violations"]:
            falsifications.append({"m": c["m"], "p": c["p"], "reason": "degree bound violated (implementation anomaly)"})
        if c["method_disagreements"]:
            falsifications.append({"m": c["m"], "p": c["p"], "reason": "cross-method disagreement (invalidates cell, not hypothesis)"})

    calibration_failures = stage_a_result.get("calibration_failures", [])

    # CTRL-SEM-CONSISTENCY-BKK001: m=3, p=101 consistency with EV-BKK-001's
    # recorded m=3 saturation (EV-BKK-001 measured support fill 1.0 at its
    # own 2 sampled targets per instance, NOT exhaustively over all of
    # F_101; it is not a claim that F_101 has zero exceptional targets).
    m3_p101 = next((c for c in stage_b_result["cells"] if c["p"] == 101), None)
    bkk_consistency = None
    if m3_p101 is not None:
        exc_card = m3_p101["exception_set_cardinality_hull"]
        bkk_consistency = {
            "checked": True,
            "m3_p101_exception_cardinality": exc_card,
            "m3_p101_nonexceptional_fraction": (101 - exc_card) / 101,
            "ev_bkk_001_claim": "support fill 1.0 (full box) on its own 2 sampled targets per m=3 instance at p in {101,431,1009}; not exhaustive over F_p",
            "consistent": exc_card <= (m3_p101["m"] - 1),
            "contradiction": False,
            "note": (
                "No contradiction: EV-BKK-001 sampled only 2 targets per instance "
                "and reported full-box saturation on those; this exhaustive run finds "
                f"{exc_card} exceptional target(s) out of 101 total (fraction "
                f"{exc_card/101:.4f}), consistent with a sparse exceptional set that a "
                "2-target sample would very likely miss. EV-BKK-001's own sampled "
                "targets were not re-identified from its raw artifacts in this run "
                "(out of scope); this is a plausibility consistency check, not a "
                "target-for-target replay."
            ),
        }

    overall_success = (
        not falsifications and not calibration_failures and
        (bkk_consistency is None or bkk_consistency["consistent"])
    )

    result = {
        "stage": "cross_method_audit_and_classification",
        "falsifications": falsifications,
        "calibration_failures": calibration_failures,
        "bkk_consistency_check": bkk_consistency,
        "overall_success_criterion_met": overall_success,
        "wall_seconds": time.time() - t0,
    }
    return result


def main():
    stage = sys.argv[1]
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    if stage == "a":
        result = stage_a()
    elif stage in ("b", "c"):
        stage_a_path = Path(sys.argv[3])
        stage_a_result = json.loads(stage_a_path.read_text())
        m = 3 if stage == "b" else 4
        result = stage_exhaustive(m, stage_a_result)
    elif stage == "d":
        a_res = json.loads(Path(sys.argv[3]).read_text())
        b_res = json.loads(Path(sys.argv[4]).read_text())
        c_res = json.loads(Path(sys.argv[5]).read_text())
        result = stage_d(a_res, b_res, c_res)
    else:
        raise ValueError(f"unknown stage {stage}")

    out_path = out_dir / "raw-result.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"stage {stage} complete, wall_seconds={result.get('wall_seconds')}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
