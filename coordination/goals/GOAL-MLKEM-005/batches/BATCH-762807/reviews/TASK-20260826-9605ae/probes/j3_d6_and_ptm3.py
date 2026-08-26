#!/usr/bin/env python3
"""J3(c) -- D6 re-derived from the DEFINITION, plus the PTM-3 known-false control.

NOT BLIND, and never described as blind: 57.242 and 54.8457 are published in
batch.yaml, DEC-20260824-5e222e and EV-MLKEM-59e4a4, all of which I read.
This file re-derives the identity independently of the producer's code -- it
imports nothing from rt_ctrl_1_matched_pair_v2.py -- and then tries to break the
check.
"""
import json

Q = 3329

# ---- the definition, written out by me from the standard definition ----
#   delta_0 = ( ||b_0|| / vol(L)^(1/d) ) ^ (1/d)
# For IntegerMatrix.random(d, "qary", k=d//2, q=Q) the basis is
#   [[ I_k , A ], [ 0 , q*I_{d-k} ]]  with k = d//2,
# so vol(L) = q^(d-k) = q^(d/2) and therefore vol^(1/d) = q^(1/2).
# The 1/d exponent applies to the RATIO.


def corrected(b0, q, d):
    return (b0 / q ** 0.5) ** (1.0 / d)


def defective_predecessor_line78(b0, q, d):
    """The pinned predecessor's line 78, verbatim: b0**(1/d) / (q**0.5)**(1/1)."""
    return b0 ** (1.0 / d) / (q ** 0.5) ** (1.0 / 1)


def closed_form(q, d):
    """corrected / defective = q^(-1/(2d)) * q^(1/2) = q^(1/2 - 1/(2d))."""
    return q ** (0.5 - 1.0 / (2.0 * d))


# ---- the third and fourth DELIBERATELY WRONG formulas PTM-3 requires ----
def wrong_A(b0, q, d):
    return b0 ** (1.0 / d) / q ** (1.0 / (2.0 * d))


def wrong_B(b0, q, d):
    return (b0 / q) ** (1.0 / d)


B0S = (1e2, 137.0, 130.15375522819156, 5e3, 2.5e4, 1e6, 1.234e9)

out = {"q": Q, "definition_note":
       "delta_0 = (b0 / vol^(1/d))^(1/d); vol^(1/d) = q^(1/2) for k=d//2 qary"}

# ---------- (1) the identity itself, my own arithmetic ----------
ident = {}
for d in (64, 80, 128, 512):
    ratios = [corrected(b, Q, d) / defective_predecessor_line78(b, Q, d)
              for b in B0S]
    cf = closed_form(Q, d)
    ident[d] = {"closed_form": cf,
                "max_rel_dev_over_b0": max(abs(r / cf - 1.0) for r in ratios),
                "b0_independent": max(ratios) - min(ratios)}
out["identity_by_d"] = ident

# ---------- (2) reproduce the two committed figures ----------
out["reproduce_committed"] = {
    "q3329_d512_recomputed": closed_form(Q, 512),
    "q3329_d512_committed_quoted": 57.242,
    "q3329_d512_rounds_to_committed": round(closed_form(Q, 512), 3) == 57.242,
    "q3329_d80_recomputed": closed_form(Q, 80),
    "q3329_d80_committed_quoted": 54.8457,
    "q3329_d80_rounds_to_committed": round(closed_form(Q, 80), 4) == 54.8457,
}

# ---------- PTM-3 (i): the identity must FAIL at other d ----------
neg512, neg80 = {}, {}
for d in (2, 8, 16, 32, 64, 80, 128, 256, 511, 512, 513, 1024):
    v = closed_form(Q, d)
    neg512[d] = {"value": v, "rounds_to_57.242": round(v, 3) == 57.242}
    neg80[d] = {"value": v, "rounds_to_54.8457": round(v, 4) == 54.8457}
out["PTM3_i_wrong_d"] = {
    "d_values_that_reproduce_57.242": [d for d, v in neg512.items()
                                       if v["rounds_to_57.242"]],
    "d_values_that_reproduce_54.8457": [d for d, v in neg80.items()
                                        if v["rounds_to_54.8457"]],
    "table": {d: {"closed_form": neg512[d]["value"]} for d in neg512},
}

# ---------- PTM-3 (ii): the check must REJECT a third wrong formula ----------
def check_pair(num, den, d):
    """MY CHECK: is (num/den) equal to q^(1/2 - 1/(2d)) for every b0, and is it
    b0-independent?  Both conditions, not just b0-independence."""
    ratios = [num(b, Q, d) / den(b, Q, d) for b in B0S]
    cf = closed_form(Q, d)
    b0_indep = (max(ratios) - min(ratios)) < 1e-9 * max(abs(r) for r in ratios)
    matches = max(abs(r / cf - 1.0) for r in ratios) < 1e-12
    return {"b0_independent": b0_indep, "matches_closed_form": matches,
            "ratio_at_first_b0": ratios[0], "closed_form": cf,
            "MY_CHECK_ACCEPTS": bool(b0_indep and matches)}


ptm = {}
for d in (64, 80, 512):
    ptm[d] = {
        "the_real_pair_corrected_over_predecessor_line78":
            check_pair(corrected, defective_predecessor_line78, d),
        "third_wrong_formula_b0**(1/d)/q**(1/(2d))":
            check_pair(corrected, wrong_A, d),
        "fourth_wrong_formula_(b0/q)**(1/d)":
            check_pair(corrected, wrong_B, d),
        "corrected_over_ITSELF_the_vacuous_case":
            check_pair(corrected, corrected, d),
    }
out["PTM3_ii_wrong_formula"] = ptm

# ---------- the empirical vol check, from the producer's OWN committed record --
# surrogate_results.jsonl records vol_root_from_gso_exp_logdet_over_2d.
out["vol_root_check"] = {
    "q_pow_half": Q ** 0.5,
    "producer_recorded_vol_root_from_gso": 57.697486947007526,
    "agree_to": abs(Q ** 0.5 - 57.697486947007526),
    "note": ("the producer's own d=64 record independently confirms "
             "vol^(1/d) == q^(1/2) on this construction, which is the premise "
             "the closed form rests on"),
}
print(json.dumps(out, indent=2))
