#!/usr/bin/env python3
# xstat.py -- TASK-20260901-579808 (BATCH-ace664, GOAL-AES-003)
#
# Arm analysis under the inherited repaired X statistic of
# IDEA-20260901-026d6a with the f8294e additions: realized-composition cutoff
# c = smallest integer with exact-DP tail P(S >= c) <= 0.05, c > null-mean
# re-verification, hit-log integrity gate (hit_log_overflow == 0,
# hit_log_cap == 256, detail record count == receipt hit count), and the
# mandatory overdispersion audit at n_hits >= 50. Written FRESH for this task
# on the dpcore.py exact integer-polynomial DP (see PREREGISTRATION.md §3/§6).
#
# usage: python3 src/xstat.py <receipt.json> <out.json> [--label L]
# Exit codes: 0 analysis completed (verdict fields inside JSON);
# 9 = input/field error (invalid_measurement, never a reading about e).
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model
# under inference amendment DEC-20260831-0d1eeb); fallback_used true;
# model_verified false; degraded_requirements [];
# amendment DEC-20260831-0d1eeb;
# standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
import json, sys, datetime
from fractions import Fraction
import dpcore

sys.set_int_max_str_digits(1000000)  # exact-rational report strings (~9e3 digits at n=53)

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
}
ALPHA = Fraction(1, 20)


def frac_obj(q):
    return {"exact": f"{q.numerator}/{q.denominator}", "float": float(q)}


def test_rows(rows, rates):
    null = dpcore.exact_null(rows, rates)
    res = {
        "n_hits": null["n_hits"],
        "S_obs": null["S_obs"],
        "total_nonforced_bytes": null["total_bytes_B"],
        "p_extra": frac_obj(null["p_extra"]),
        "p_deficit": frac_obj(null["p_deficit"]),
        "null_mean": frac_obj(null["null_mean"]),
        "null_variance": frac_obj(null["null_variance"]),
        "S_obs_above_null_mean": null["S_obs_above_null_mean"],
        "cutoff_c": null["cutoff_c"],
        "size_at_cutoff": frac_obj(null["size_at_cutoff"]) if null["size_at_cutoff"] is not None else None,
        "tail_at_cutoff_minus_1": frac_obj(null["tail_at_cutoff_minus_1"]) if null["tail_at_cutoff_minus_1"] is not None else None,
        "cutoff_gt_null_mean": null["cutoff_gt_null_mean"],
        "cutoff_rule": ("smallest integer c with exact-DP tail P(S >= c | realized "
                        "mask multiset, run-internal rates) <= 0.05; c > null mean "
                        "re-verified (degeneracy clause (c) if violated)"),
    }
    nh = null["n_hits"]
    if nh >= 50:
        xs = [r["X"] for r in rows]
        emp_mean = Fraction(sum(xs), len(xs))
        emp_var = sum((Fraction(x) - emp_mean) ** 2 for x in xs) / len(xs)
        res["overdispersion_audit"] = {
            "triggered": True,
            "empirical_mean_X": frac_obj(emp_mean),
            "empirical_var_X": frac_obj(emp_var),
            "null_mean_X_per_hit": frac_obj(null["null_mean"] / nh),
            "null_var_X_per_hit": frac_obj(null["null_variance"] / nh),
        }
    else:
        res["overdispersion_audit"] = {
            "triggered": False,
            "note": ("n_hits < 50: audit not run; small-n variance-calibration "
                     "limit disclosed with the reading, never smoothed"),
        }
    return res, null


def analyze(receipt, label):
    rows, checks = dpcore.build_rows(receipt)
    rates = dpcore.class_rates(receipt)
    n_hit = rates["n_hit"]
    out = {
        "arm": receipt.get("arm"),
        "label": label,
        "seat": {k: receipt.get(k) for k in
                 ("sbox", "amask", "smask", "log2N", "seed", "arm_id", "threads")},
        "null_mode": "run_internal_empirical",
        "n_hits_receipt": n_hit,
        "n_miss": rates["n_miss"],
        "hit_log_integrity": {
            "hit_log_cap_receipt": receipt.get("hit_log_cap"),
            "hit_log_overflow_receipt": receipt.get("hit_log_overflow"),
            "hit_e_detail_records": len(receipt.get("hit_e_detail", [])),
            "cap_is_256": receipt.get("hit_log_cap") == 256,
            "overflow_is_zero": receipt.get("hit_log_overflow") == 0,
            "detail_count_equals_receipt_hits": len(receipt.get("hit_e_detail", [])) == n_hit,
            "gate": (receipt.get("hit_log_cap") == 256
                     and receipt.get("hit_log_overflow") == 0
                     and len(receipt.get("hit_e_detail", [])) == n_hit),
        },
        "p_diag": frac_obj(rates["p_diag"]),
        "p_off": frac_obj(rates["p_off"]),
        "p_diag_float_vs_naive": float(rates["p_diag"] / Fraction(1, 256)),
        "p_off_float_vs_naive": float(rates["p_off"] / Fraction(1, 256)),
        "ezdiag_miss": receipt["ezdiag_miss"],
        "ezoff_miss": receipt["ezoff_miss"],
        "ezdiag_all": receipt["ezdiag_all"],
        "ezoff_all": receipt["ezoff_all"],
        "ezdiag_hit": receipt["ezdiag_hit"],
        "ezoff_hit": receipt["ezoff_hit"],
        "consistency_checks": checks,
        "per_hit": rows,
    }
    allres, _null_all = test_rows(rows, rates)
    out["S_obs"] = allres["S_obs"]
    out["test_all_hits"] = allres
    inact = [r for r in rows if r["subclass"] == "inactive"]
    act = [r for r in rows if r["subclass"] == "active"]
    multi = [r for r in rows if r["subclass"] == "multi_word"]
    out["test_inactive_subclass"], _ = test_rows(inact, rates)
    out["test_active_subclass"], _ = test_rows(act, rates)
    if multi:
        out["test_multiword_subclass"], _ = test_rows(multi, rates)
    out["mask_composition"] = {
        "active_word_hits": len(act),
        "inactive_word_hits": len(inact),
        "multi_word_hits": len(multi),
        "masks": sorted({r["mask"] for r in rows}),
    }
    return out


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("usage: xstat.py <receipt.json> <out.json> [--label L]\n")
        return 9
    receipt_path, out_path = sys.argv[1], sys.argv[2]
    label = ""
    if "--label" in sys.argv:
        label = sys.argv[sys.argv.index("--label") + 1]
    receipt = dpcore.load_receipt(receipt_path)
    if receipt["W_ge1_nontrivial"] > dpcore.SUBSAMPLE_CAP:
        sys.stderr.write("n_hits above frozen exact-DP cap 2000: not handled at "
                         "t=1; report as invalid_measurement\n")
        return 9
    out = {
        "schema": "crypto.autoresearch.xstat_arm.v2",
        "task_id": "TASK-20260901-579808",
        "idea_record": "IDEA-20260901-f8294e",
        "receipt": receipt_path,
        "analysis": analyze(receipt, label),
        "analyzed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with "
                              "python3 json.load before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    a = out["analysis"]["test_all_hits"]
    print(json.dumps({"arm": out["analysis"]["arm"], "n_hits": a["n_hits"],
                      "S_obs": a["S_obs"], "p_extra": a["p_extra"]["float"],
                      "p_deficit": a["p_deficit"]["float"],
                      "null_mean": a["null_mean"]["float"],
                      "cutoff_c": a["cutoff_c"],
                      "hit_log_gate": out["analysis"]["hit_log_integrity"]["gate"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
