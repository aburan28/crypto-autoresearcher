"""Assembly script for RUN-RELN-82f487-N14-sigma8-seed2: turns
work/all_arms.json (produced by driver_run_full_cell_seed2.py, which calls
source/run_cell.py's run_arm_cell unchanged) into the full artifact set
matching RUN-RELN-82f487-N14-sigma8-seed1's layout. This script itself is a
one-off assembly/glue script for this run directory (analogous, unsaved
glue used to build the first cell's run directory); every substantive
computation (fixtures, metrics, nulls, leak audit, cost instrumentation) is
delegated to unchanged experiments/EXP-RELN-82f487/source/ modules.
"""
import hashlib
import json
import os
import sys
import time

_RUN_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.abspath(os.path.join(_RUN_DIR, "..", "..", "source"))
_REPO_ROOT = os.path.abspath(os.path.join(_RUN_DIR, "..", "..", "..", ".."))
sys.path.insert(0, _SRC_DIR)
sys.path.insert(0, _REPO_ROOT)

import numpy as np
from harness.toycurve import EllipticCurve
import curve_gen
import enumerate_counts as ec
import features as feat
import lookup_labels
import leak_audit
import cost_instrumentation as costi
import run_stage4_analysis as s4

WORK = os.path.join(_RUN_DIR, "work")
CURVE_INDEX_J = 2
CURVE_SEED = 102
BASE_SEED = 202
TRAINING_SEED = 302
RUNG_K = 14
SIGMA = 0.125

ARMS = ["E_x_interval", "E_random_matched", "ZN_interval", "ZN_random", "E_log_interval_canary"]


def load_all_arms():
    with open(os.path.join(WORK, "all_arms.json")) as f:
        return json.load(f)


def main():
    all_arms = load_all_arms()
    with open(os.path.join(WORK, "curve.json")) as f:
        curve_rec = json.load(f)

    # --- 1. Stage 0: leak audit + planted-leak diagnostic (deterministic,
    # unchanged source, not seed-dependent; re-run cheaply for this run's own
    # record rather than referencing stage0's immutable file by pointer) ---
    audit = leak_audit.audit_all(_SRC_DIR)
    diagnostic = leak_audit.run_planted_leak_diagnostic()
    with open(os.path.join(_RUN_DIR, "leak_audit.json"), "w") as f:
        json.dump({"leak_audit": audit, "planted_leak_diagnostic": diagnostic}, f, indent=2)
    with open(os.path.join(_RUN_DIR, "planted_leak_diagnostic.json"), "w") as f:
        json.dump(diagnostic, f, indent=2)
    assert audit["overall_verdict"] == "pass"
    assert diagnostic["audit_correctly_rejected_planted_leak"]

    # --- 2. Stage 4 analysis (fixtures, positive control, permutation/canary
    # verdicts, E_random_vs_ZN_random, gnn_minus_trees, E_x_interval_excess,
    # branch classification) ---
    stage4 = s4.analyze(all_arms)
    with open(os.path.join(_RUN_DIR, "stage4_analysis.json"), "w") as f:
        json.dump(stage4, f, indent=2)

    # --- 3. fixtures.json (subset view, matching seed1 layout) ---
    with open(os.path.join(_RUN_DIR, "fixtures.json"), "w") as f:
        json.dump({"fixtures": stage4["fixtures"], "fixtures_all_pass": stage4["fixtures_all_pass"]}, f, indent=2)

    # --- 4. curves.json ---
    with open(os.path.join(_RUN_DIR, "curves.json"), "w") as f:
        json.dump(curve_rec, f, indent=2)

    # --- 5. inputs.json ---
    inputs = {
        "specification_ref": "experiments/EXP-RELN-82f487/specification.yaml",
        "handoff_ref": "ledger/handoffs/TASK-20260907-8b29e0.yaml",
        "hypothesis_ref": "ledger/hypotheses/H-RELN-10ad6b.yaml",
        "proposal_refs": ["ledger/proposals/IDEA-20260906-79ff48.yaml", "ledger/proposals/IDEA-20260830-c5c614.yaml"],
        "finding_ref": "knowledge/findings/KN-FIND-007.md",
        "prior_run_ref": "experiments/EXP-RELN-82f487/runs/RUN-RELN-82f487-N14-sigma8-seed1/ (first-seed cell, compared against)",
        "prior_evidence_ref": "ledger/evidence/EV-RELN-cc045d.yaml",
        "exhaustive_label_source_used": "fallback_in_run_enumeration",
        "exhaustive_label_source_reason": (
            "Identical to the first cell: EXP-RELN-f202be's committed count "
            "vectors were built under a different curve-seed convention and "
            "geometry panel; no identical (p,a,b,N,base_seed,arm,convention) "
            "cell exists for curve_seed=102 either. source/enumerate_counts.py "
            "fallback used, unchanged from the first cell."
        ),
    }
    with open(os.path.join(_RUN_DIR, "inputs.json"), "w") as f:
        json.dump(inputs, f, indent=2)

    # --- 6. feature_manifest.json (static description of the feature set;
    # identical text to the first cell's since features.py is unchanged and
    # not seed-dependent) ---
    feature_manifest = {
        "regime_F0_E_arms": [
            {"name": "x_over_p", "computation": "x / p", "static_audit_verdict": "pass"},
            {"name": "y_over_p", "computation": "y / p", "static_audit_verdict": "pass"},
            {"name": "low4_x", "computation": "(x & 0xF) / 15", "static_audit_verdict": "pass"},
            {"name": "low4_y", "computation": "(y & 0xF) / 15", "static_audit_verdict": "pass"},
            {"name": "legendre_x", "computation": "pow(x, (p-1)//2, p) mapped to {-1,0,1}", "static_audit_verdict": "pass"},
            {"name": "legendre_x_plus_1", "computation": "legendre(x+1, p)", "static_audit_verdict": "pass"},
            {"name": "L4O_vector", "computation": "(1, x/p, y/p, x^2 mod p / p)", "static_audit_verdict": "pass"},
            {"name": "translate_x_plus_minus_Pi", "computation": "x(R+P_i)/p, x(R-P_i)/p for k=8 fixed points P_i chosen by base_seed", "count": 16, "static_audit_verdict": "pass"},
        ],
        "regime_F1_additional": [
            {"name": "base_x_histogram_16bin", "computation": "16-bin histogram of x(D) over [0,p), normalised", "static_audit_verdict": "pass"},
            {"name": "base_legendre_profile", "computation": "fraction of D with Legendre(x)=1,-1,0", "static_audit_verdict": "pass"},
        ],
        "regime_F0_ZN_arms": [
            {"name": "r_over_N", "computation": "r / N", "static_audit_verdict": "pass"},
            {"name": "low4_r", "computation": "(r & 0xF) / 15", "static_audit_verdict": "pass"},
            {"name": "legendre_r", "computation": "legendre(r, N)", "static_audit_verdict": "pass"},
            {"name": "legendre_r_plus_1", "computation": "legendre(r+1, N)", "static_audit_verdict": "pass"},
            {"name": "vector_1_r_r2", "computation": "(1, r/N, r^2 mod N / N)", "static_audit_verdict": "pass"},
            {"name": "translate_r_plus_minus_di", "computation": "(r+d_i) mod N / N, (r-d_i) mod N / N for k=8 fixed d_i by base_seed", "count": 16, "static_audit_verdict": "pass"},
        ],
        "static_audit_source": "experiments/EXP-RELN-82f487/source/leak_audit.py",
        "static_audit_scanned_files": ["features.py", "model_gnn.py", "model_trees.py", "graph_build.py"],
        "static_audit_overall_verdict": audit["overall_verdict"],
        "forbidden_modules_checked": ["enumerate_counts", "lookup_labels", "certificates"],
        "forbidden_identifier_substrings_checked": [
            "discrete_log", "dlog", "log_p", "logp", "scalar_k", "the_scalar",
            "enumeration_index", "node_order", "node_index", "positional_index",
        ],
    }
    with open(os.path.join(_RUN_DIR, "feature_manifest.json"), "w") as f:
        json.dump(feature_manifest, f, indent=2)

    # --- 7. per_arm/<arm>/16384/curve2_seed102/202/{metrics.json,
    #        selection_null.json, count_vector_source.json}
    # and model_cards/<arm>_<regime>_<cls>_rung16384_curve2_seed102_base202_train302.json
    per_arm_root = os.path.join(_RUN_DIR, "per_arm")
    model_cards_root = os.path.join(_RUN_DIR, "model_cards")
    for arm in ARMS:
        d = all_arms[arm]
        cell_dir = os.path.join(per_arm_root, arm, "16384", "curve2_seed102", "202")
        os.makedirs(cell_dir, exist_ok=True)

        metrics = {
            "arm": arm, "B": d["B"], "B_eff": d["B_eff"], "N": d["N"],
            "n_universe": d["n_universe"], "n_train": d["n_train"], "n_val": d["n_val"],
            "n_heldout": d["n_heldout"],
            "sigma_one_fixture": d["sigma_one_fixture"],
            "total_check": d["total_check"],
            "grammar_reproduction_fixture": d["grammar_reproduction_fixture"],
            "regimes": {},
        }
        selection_null = {}
        for regime in ["F0", "F1"]:
            r = d["regimes"][regime]
            metrics["regimes"][regime] = {
                "n_relations": r["n_relations"],
                "model_metrics": {cls: {"metrics": r["model_metrics"][cls]["metrics"],
                                         "bootstrap": r["model_metrics"][cls]["bootstrap"]}
                                   for cls in ["gnn", "trees"]},
                "excess": r["excess"],
                "gnn_minus_trees": r["gnn_minus_trees"],
                "label_permutation_null": r["label_permutation_null"],
                "null_agreement": r["null_agreement"],
            }
            selection_null[regime] = {
                "lambda_band": r["selection_null"]["lambda_band"],
                "rho_band": r["selection_null"]["rho_band"],
                "lambda_median": r["selection_null"]["lambda_median"],
                "rho_median": r["selection_null"]["rho_median"],
                "n_draws": r["selection_null"]["n_draws"],
            }
            for cls in ["gnn", "trees"]:
                card_name = f"{arm}_{regime}_{cls}_rung16384_curve2_seed102_base202_train302.json"
                with open(os.path.join(model_cards_root, card_name), "w") as f:
                    json.dump(r["model_metrics"][cls]["model_card"], f, indent=2)

        with open(os.path.join(cell_dir, "metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2)
        with open(os.path.join(cell_dir, "selection_null.json"), "w") as f:
            json.dump(selection_null, f, indent=2)

        count_vector_source = {
            "source": "in_run_enumeration_fallback",
            "reason": inputs["exhaustive_label_source_reason"],
            "enumerator": "experiments/EXP-RELN-82f487/source/enumerate_counts.py",
            "closed_form_total_check": d["total_check"],
            "base_meta": d["base_meta"],
        }
        with open(os.path.join(cell_dir, "count_vector_source.json"), "w") as f:
            json.dump(count_vector_source, f, indent=2)

    # --- 8. slope_fit.json (single rung, not fittable -- identical status text
    # style to the first cell, this cell's own numbers) ---
    ex = stage4["E_x_interval_excess"]
    slope_fit = {
        "status": "not_fittable",
        "reason": (
            "Only ONE rung (2^14) was run in this cell; a log-log slope needs "
            "at least two rungs. Identical situation to RUN-RELN-82f487-N14-"
            "sigma8-seed1."
        ),
        "rungs_computed": [16384],
        "rungs_not_run": [65536, 262144, 1048576, 16777216],
        "E_x_interval_excess_this_rung": ex,
    }
    with open(os.path.join(_RUN_DIR, "slope_fit.json"), "w") as f:
        json.dump(slope_fit, f, indent=2)

    # --- 9. determinism_rerun.json (not run, per handoff scope: "no expand
    # scope beyond this one cell") ---
    determinism = {
        "status": "not_run",
        "reason": (
            "Out of scope per TASK-20260907-8b29e0's explicit constraint "
            "(\"DO NOT expand scope beyond this one cell ... unless this cell "
            "finishes with substantial time remaining\"); the first cell "
            "(seed1) also did not run this. source/run_determinism.py is "
            "implemented and ready but not executed in this session."
        ),
        "script_ready_at": "experiments/EXP-RELN-82f487/source/run_determinism.py",
    }
    with open(os.path.join(_RUN_DIR, "determinism_rerun.json"), "w") as f:
        json.dump(determinism, f, indent=2)

    # --- 10. handoff/*.csv (documented not_run, matching seed1's convention:
    # this cell is being scored on the pipeline-fault-replication question,
    # not producing new consumer tables for EXP-RELN-141a86) ---
    handoff_dir = os.path.join(_RUN_DIR, "handoff")
    os.makedirs(handoff_dir, exist_ok=True)
    for name in ["slice_membership.csv", "permutation_importances.csv", "partial_dependence.csv"]:
        with open(os.path.join(handoff_dir, name), "w") as f:
            f.write(
                "# not_run: this run's scope (TASK-20260907-8b29e0) is the "
                "second-seed repeat-cell reproducibility check of "
                "EV-RELN-cc045d's E_random_vs_ZN_random pipeline-fault "
                "finding, not the EXP-RELN-141a86 handoff-table production "
                "step (which the first cell (seed1) also did not run, since "
                "that cell's own gates did not pass either).\n"
            )

    # --- 11. cost_instrumentation.json (measured, this machine, this
    # implementation, this curve/arm -- same protocol as the first cell:
    # E/x-interval arm, feature computation + a linear-probe inference proxy) ---
    curve = EllipticCurve(curve_rec["p"], curve_rec["a"], curve_rec["b"])
    B_eff = ec.b_eff_for_N(curve_rec["N"])
    pts = ec.all_curve_points(curve)
    points_by_x = {}
    for (x, y) in pts:
        points_by_x.setdefault(x, []).append((x, y))
    D, base_meta = ec.build_base_E_x_interval(curve, points_by_x, BASE_SEED, B_eff)
    translate_pts = feat.fixed_translate_points_E(curve, BASE_SEED, k=8)
    base_summary = feat.base_summary_E(curve, D)

    point_add_time = costi.measure_point_addition_time(curve, n_reps=20000)

    targets_sample = [pt for pt in pts if pt not in set(D)][:400]

    def feature_fn(sub):
        return feat.compute_features_E(curve, sub, translate_pts, "F0", base_summary)

    def model_predict_fn(feats_arr):
        return feats_arr.sum(axis=1)

    fi = costi.measure_feature_and_gnn_inference_time(feature_fn, model_predict_fn, targets_sample, n_sample=200)

    pairs, keys_sorted = lookup_labels.build_pair_sum_table_E(curve, D)

    def lookup_fn(tgt):
        return lookup_labels.lookup_decomposition_E(curve, D, pairs, keys_sorted, tgt)

    lookup_time = costi.measure_theta_b_lookup_time(lookup_fn, targets_sample, n_sample=50)

    report = costi.cost_ratio_report(point_add_time, fi["total_c_f_time_per_target"], lookup_time, len(D))
    report["feature_and_inference_breakdown"] = fi
    with open(os.path.join(_RUN_DIR, "cost_instrumentation.json"), "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps({"stage4_summary": {
        "pipeline_fault_detected": stage4["pipeline_fault_detected"],
        "E_random_vs_ZN_random": stage4["E_random_vs_ZN_random"],
        "fixtures_all_pass": stage4["fixtures_all_pass"],
        "label_permutation_leak_detected": stage4["label_permutation_leak_detected"],
        "canary_leak_detected": stage4["canary_leak_detected"],
    }}, indent=2))


if __name__ == "__main__":
    main()
