#!/usr/bin/env python3
# jointlr.py -- TASK-20260901-579808 (BATCH-ace664, GOAL-AES-003)
#
# ZERO-COST JOINT ANALYSIS (PR-P4, 0 runs): joint likelihood-ratio table of
# the new 2^32 arm + the committed G5 reading (seed 531002, n = 19, S_obs = 0;
# exact null pmf recomputed from the committed G5 receipt under its own
# run-internal rates) against the rho grid {0.02, 0.05, 0.08, 0.096, 0.10,
# 0.15, 0.214} under E-rho. Seeds are independent, so
#   LR_joint(rho) = LR_new(rho) * LR_G5(rho),
#   LR_arm(rho)   = P(S_arm | E-rho) / P(S_arm | null),
#   P(S | E-rho)  = sum_k C(n,k) rho^k (1-rho)^(n-k) P_null(S - k).
# For G5 (S_obs = 0) this reduces EXACTLY to LR_G5(rho) = (1-rho)^19.
# Sanity envelope (design-time calibration of f8294e): at S_new = 0 the joint
# BF reproduces (1-rho)^-(n_new + 19) within DP tolerance.
#
# usage: python3 src/jointlr.py <new_receipt.json> <g5_receipt.json> <out.json>
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model
# under inference amendment DEC-20260831-0d1eeb); fallback_used true;
# model_verified false; degraded_requirements [];
# amendment DEC-20260831-0d1eeb;
# standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
import json, sys, datetime
import dpcore
from power import binom_weights, p_obs_at

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
GRID = [0.02, 0.05, 0.08, 0.096, 0.10, 0.15, 0.214]


def null_of(receipt):
    rows, _ = dpcore.build_rows(receipt)
    rates = dpcore.class_rates(receipt)
    return dpcore.exact_null(rows, rates), rows


def lr_arm(null, rho):
    s_obs = null["S_obs"]
    p_null = dpcore.pmf_floats_at(null, [s_obs])[s_obs]
    p_rho = p_obs_at(null, s_obs, rho)
    return (p_rho / p_null) if p_null > 0 else None


def main():
    new_path, g5_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    new_receipt = dpcore.load_receipt(new_path)
    g5_receipt = dpcore.load_receipt(g5_path)
    null_new, _ = null_of(new_receipt)
    null_g5, _ = null_of(g5_receipt)

    n_new, s_new = null_new["n_hits"], null_new["S_obs"]
    n_g5, s_g5 = null_g5["n_hits"], null_g5["S_obs"]

    table = {}
    for rho in GRID:
        lr_n = lr_arm(null_new, rho)
        lr_g = lr_arm(null_g5, rho)
        closed_g5 = (1.0 - rho) ** n_g5
        joint = lr_n * lr_g
        row = {
            "LR_new_arm": lr_n,
            "LR_G5": lr_g,
            "LR_G5_closed_form_1mrho_pow_n": closed_g5,
            "LR_G5_matches_closed_form_rel_1e_9":
                abs(lr_g - closed_g5) <= 1e-9 * max(1.0, closed_g5),
            "LR_joint": joint,
            "BF_null_vs_E_rho_joint": (1.0 / joint) if joint else None,
        }
        if s_new == 0:
            closed_joint = (1.0 - rho) ** (n_new + n_g5)
            row["sanity_envelope_joint_BF_closed_form"] = closed_joint
            row["sanity_envelope_rel_err"] = (
                abs((1.0 / joint) - closed_joint) / closed_joint if joint else None)
        table[str(rho)] = row

    out = {
        "schema": "crypto.autoresearch.joint_lr.v1",
        "task_id": "TASK-20260901-579808",
        "idea_record": "IDEA-20260901-f8294e",
        "new_receipt": new_path,
        "g5_receipt_committed": g5_path,
        "new_arm": {"arm": new_receipt.get("arm"), "seed": new_receipt.get("seed"),
                    "n_hits": n_new, "S_obs": s_new},
        "g5_committed_reading": {"arm": g5_receipt.get("arm"), "seed": g5_receipt.get("seed"),
                                 "n_hits": n_g5, "S_obs": s_g5,
                                 "note": "exact null recomputed from the committed receipt (0 runs)"},
        "effect_model": "E-rho (per hit +1 extra zero with probability rho)",
        "grid": GRID,
        "table": table,
        "interpretation_note": ("LR_joint > 1 favors E-rho over the pure null; "
                                "BF_null_vs_E_rho_joint is the evidence for the null. "
                                "Descriptive only; no status interpretation."),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with "
                              "python3 json.load before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"n_new": n_new, "S_new": s_new, "n_g5": n_g5, "S_g5": s_g5,
                      "joint_BF_0.05": table["0.05"]["BF_null_vs_E_rho_joint"],
                      "joint_BF_0.096": table["0.096"]["BF_null_vs_E_rho_joint"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
