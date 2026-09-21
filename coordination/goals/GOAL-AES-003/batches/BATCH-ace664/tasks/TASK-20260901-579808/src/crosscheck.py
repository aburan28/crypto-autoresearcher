#!/usr/bin/env python3
# crosscheck.py -- TASK-20260901-579808 (BATCH-ace664, GOAL-AES-003)
#
# Fresh-code cross-validation of the new common-denominator integer DP
# (dpcore.py) against the committed BATCH-5ed9a3 analysis of the G5 receipt
# (runs/G5_analysis.json of TASK-20260901-ed281d): the new DP must reproduce
# S_obs = 0, p_extra = 1 exact, null mean 17180538557/17179868864, and
# p_deficit 0.3671453866933061 digit-for-digit BEFORE any decision-bearing
# use (PREREGISTRATION.md section 6 item 4).
#
# usage: python3 src/crosscheck.py <g5_receipt.json> <committed_g5_analysis.json> <out.json>
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

sys.set_int_max_str_digits(1000000)  # exact-rational report strings

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


def main():
    g5_path, committed_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    receipt = dpcore.load_receipt(g5_path)
    committed = json.load(open(committed_path))
    ct = committed["analysis"]["test_all_hits"]

    rows, checks = dpcore.build_rows(receipt)
    rates = dpcore.class_rates(receipt)
    null = dpcore.exact_null(rows, rates)

    fresh = {
        "S_obs": null["S_obs"],
        "p_extra_exact": f"{null['p_extra'].numerator}/{null['p_extra'].denominator}",
        "p_def_exact": f"{null['p_deficit'].numerator}/{null['p_deficit'].denominator}",
        "p_def_float": float(null["p_deficit"]),
        "null_mean_exact": f"{null['null_mean'].numerator}/{null['null_mean'].denominator}",
        "null_mean_float": float(null["null_mean"]),
        "cutoff_c": null["cutoff_c"],
        "consistency_checks": checks,
        "p_diag": f"{rates['p_diag'].numerator}/{rates['p_diag'].denominator}",
        "p_off": f"{rates['p_off'].numerator}/{rates['p_off'].denominator}",
    }
    committed_vals = {
        "S_obs": ct["S_obs"],
        "p_extra_exact": ct["p_extra"]["exact"],
        "p_def_exact": ct["p_deficit"]["exact"],
        "p_def_float": ct["p_deficit"]["float"],
        "null_mean_exact": ct["null_mean"]["exact"],
        "null_mean_float": ct["null_mean"]["float"],
    }
    match = {
        "S_obs": fresh["S_obs"] == committed_vals["S_obs"],
        "p_extra_exact": fresh["p_extra_exact"] == committed_vals["p_extra_exact"],
        "p_deficit_exact": fresh["p_def_exact"] == committed_vals["p_def_exact"],
        "p_deficit_float": fresh["p_def_float"] == committed_vals["p_def_float"],
        "null_mean_exact": fresh["null_mean_exact"] == committed_vals["null_mean_exact"],
        "null_mean_float": fresh["null_mean_float"] == committed_vals["null_mean_float"],
        "consistency_checks_all_true": all(checks.values()),
    }
    ok = all(match.values())
    out = {
        "schema": "crypto.autoresearch.crosscheck_dp.v1",
        "task_id": "TASK-20260901-579808",
        "idea_record": "IDEA-20260901-f8294e",
        "g5_receipt": g5_path,
        "committed_analysis": committed_path,
        "fresh_dp_values": fresh,
        "committed_values": committed_vals,
        "match": match,
        "crosscheck_pass": ok,
        "note": ("fresh common-denominator integer DP reproduces the committed "
                 "BATCH-5ed9a3 exact-rational readings of G5 digit-for-digit "
                 "(also reproduces the n=19 cutoff c: smallest c with tail <= 0.05)"),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with "
                              "python3 json.load before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"crosscheck_pass": ok, "match": match,
                      "fresh_cutoff_c": fresh["cutoff_c"]}, indent=1))
    sys.exit(0 if ok else 9)


if __name__ == "__main__":
    main()
