#!/usr/bin/env python3
# power.py -- TASK-20260901-579808 (BATCH-ace664, GOAL-AES-003)
#
# Power under the preregistered effect model E-rho (each hit independently
# gains EXACTLY ONE extra zero with probability rho: X_eff = X_null +
# Bernoulli(rho)) at the REALIZED hit count and composition of an arm.
#
#   power(rho) = P(S_null + Binom(n, rho) >= c)
#              = sum_k C(n,k) rho^k (1-rho)^(n-k) * P_null(S >= c - k)
#
# The null tails P_null(S >= j) are EXACT rationals from the dpcore integer
# DP, converted to correctly-rounded float64 for the rho-scan (declared
# approximation error << 1e-6; double rounding ~1e-16 relative). rho_50 and
# rho_80 are located by bisection to 1e-6 (power is strictly increasing in
# rho). Bayes-factor calibration at the realized S_obs (null vs E-rho):
# BF = P(S_obs | null) / P(S_obs | rho), P(S_obs | rho) =
# sum_k C(n,k) rho^k (1-rho)^(n-k) P_null(S_obs - k); at S_obs = 0 this
# reduces exactly to (1-rho)^-n.
#
# usage: python3 src/power.py <receipt.json> <out.json> [--label L]
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
GRID = [0.02, 0.05, 0.08, 0.096, 0.10, 0.12, 0.139, 0.15, 0.214, 0.30]
BF_GRID = [0.02, 0.05, 0.08, 0.096, 0.10, 0.15, 0.214]


def binom_weights(n, rho):
    """float64 Binom(n, rho) weights w[k] by stable recurrence."""
    w = [0.0] * (n + 1)
    w[0] = (1.0 - rho) ** n
    for k in range(n):
        w[k + 1] = w[k] * (n - k) / (k + 1) * rho / (1.0 - rho)
    return w


def power_at(null, c, rho):
    n = null["n_hits"]
    if c is None:
        return None
    tails = dpcore.tail_floats(null, c - n, c)
    w = binom_weights(n, rho)
    return sum(w[k] * tails[c - k] for k in range(n + 1))


def p_obs_at(null, s_obs, rho):
    n = null["n_hits"]
    pts = dpcore.pmf_floats_at(null, [s_obs - k for k in range(n + 1)])
    w = binom_weights(n, rho)
    return sum(w[k] * pts[s_obs - k] for k in range(n + 1))


def solve_rho(null, c, target):
    lo, hi = 0.0, 0.999999
    plo = power_at(null, c, lo)
    if plo >= target:
        return 0.0
    if power_at(null, c, hi) < target:
        return None  # unreachable target at stated n/c
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if power_at(null, c, mid) >= target:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def main():
    receipt_path, out_path = sys.argv[1], sys.argv[2]
    label = ""
    if "--label" in sys.argv:
        label = sys.argv[sys.argv.index("--label") + 1]
    receipt = dpcore.load_receipt(receipt_path)
    rows, _checks = dpcore.build_rows(receipt)
    rates = dpcore.class_rates(receipt)
    null = dpcore.exact_null(rows, rates)
    n = null["n_hits"]
    c = null["cutoff_c"]
    s_obs = null["S_obs"]
    p_null_sobs = dpcore.pmf_floats_at(null, [s_obs])[s_obs]

    power_table = {str(rho): power_at(null, c, rho) for rho in GRID}
    rho_50 = solve_rho(null, c, 0.5)
    rho_80 = solve_rho(null, c, 0.8)
    bf_table = {}
    for rho in BF_GRID:
        p_rho = p_obs_at(null, s_obs, rho)
        bf_table[str(rho)] = {
            "P_S_obs_given_null": p_null_sobs,
            "P_S_obs_given_E_rho": p_rho,
            "BF_null_vs_E_rho": (p_null_sobs / p_rho) if p_rho > 0 else None,
            "BF_closed_form_if_S0": None if s_obs != 0 else (1.0 - rho) ** (-n),
        }
    out = {
        "schema": "crypto.autoresearch.power_erho.v1",
        "task_id": "TASK-20260901-579808",
        "idea_record": "IDEA-20260901-f8294e",
        "label": label,
        "receipt": receipt_path,
        "effect_model": ("E-rho: each hit independently gains EXACTLY ONE extra "
                         "zero with probability rho (X_eff = X_null + Bernoulli(rho)); "
                         "per-byte-rate alternative agrees to first order in the "
                         "per-hit mean shift (disclosed confounder)"),
        "n_hits_realized": n,
        "S_obs": s_obs,
        "cutoff_c_realized": c,
        "mask_composition": {"active": sum(1 for r in rows if r["subclass"] == "active"),
                             "inactive": sum(1 for r in rows if r["subclass"] == "inactive"),
                             "multi_word": sum(1 for r in rows if r["subclass"] == "multi_word")},
        "approximation_note": ("null tails exact rationals from the integer DP, "
                               "correctly rounded to float64; binomial weights in "
                               "float64; declared approximation error << 1e-6"),
        "power_grid": power_table,
        "rho_50": rho_50,
        "rho_80": rho_80,
        "bf_calibration_at_S_obs": bf_table,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with "
                              "python3 json.load before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"n": n, "c": c, "S_obs": s_obs, "rho_50": rho_50,
                      "rho_80": rho_80,
                      "power_0.096": power_table.get("0.096"),
                      "power_0.214": power_table.get("0.214")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
