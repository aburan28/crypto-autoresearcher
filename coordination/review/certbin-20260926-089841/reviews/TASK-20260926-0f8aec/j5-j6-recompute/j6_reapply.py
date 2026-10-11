#!/usr/bin/env python3
"""TASK-20260926-0f8aec, joint J6: re-apply NC-DR-1..NC-DR-9 literally, from
the specification text, to MY J5 values (j5-recompute.json), and compare
with decision-rules.json. Also re-read PN-1..PN-5 and the pre-data prior
(a)-(g) against my values. Imports nothing from impl/. Written after J5."""
from __future__ import annotations

import gzip
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

WT = Path(sys.argv[1])
OUTDIR = Path(__file__).resolve().parent
RUN = WT / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
me = json.load(open(OUTDIR / "j5-recompute.json"))
dr = json.load(open(RUN / "decision-rules.json"))
A = me["arms"]


def iv(c):
    return (c["lower"], c["upper"]) if c.get("defined") else None


def level(x, n):
    t, l = math.ceil(Fraction(9, 10) * n), math.floor(Fraction(1, 10) * n)
    return "TENSOR" if x >= t else "LINEAR" if x <= l else "MIXED"


out = {}
cmp = []


def rec(rule, item, mine, recorded):
    cmp.append({"rule": rule, "item": item, "reapplied": mine, "recorded": recorded, "equal": mine == recorded})


# NC-DR-1
L1, L2 = me["MN1"]["L1"], me["MN1"]["L2"]
lab1, lab2 = level(L1["w"], L1["n_C"]), level(L2["w"], L2["n_C"])
if L1["n_C"] < 120:
    v1 = "NOT EVALUABLE (sample)"
elif lab1 != lab2:
    v1 = "UNDETERMINED (certification)"
else:
    v1 = lab1
rec("NC-DR-1", "L1 label", lab1, dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["label"])
rec("NC-DR-1", "L2 label", lab2, dr["NC-DR-1"]["L2_uncertified_excluded"]["label"])
rec("NC-DR-1", "E-TENSOR falsified (w <= floor(n_C/2))", L1["w"] <= L1["n_C"] // 2,
    dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["E_TENSOR_falsified"])
rec("NC-DR-1", "E-LINEAR falsified (w > floor(n_C/2))", L1["w"] > L1["n_C"] // 2,
    dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["E_LINEAR_falsified"])
rec("NC-DR-1", "verdict", v1, dr["NC-DR-1"]["verdict"])


# NC-DR-2
def overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


nconv = iv(L1["cp95"])
s386 = iv(me["refs"]["S3_386_of_386"])
s82 = iv(A["S_3 (82)"]["W4_cp95"])
rec("NC-DR-2", "vs 386/386", "AT S_3's RATE" if overlap(nconv, s386) else "BELOW S_3", dr["NC-DR-2"]["label"])
rec("NC-DR-2", "vs in-run S_3 (82)", "AT S_3's RATE" if overlap(nconv, s82) else "BELOW S_3", dr["NC-DR-2"]["in_run_S3_82"]["label"])
# NC-DR-3
ARMS3 = ["N-CONV", "N-CONVL", "N-CONV17", "N-ELL144", "NULL-F262", "NULL-AFF62", "S_3 (82)"]


def nm(a):
    return a + " [one affine draw]" if a == "NULL-AFF62" else a


above = {}
for X in ARMS3:
    for Y in ARMS3:
        if X == Y:
            continue
        ix, iy = iv(A[X]["W4_cp95"]), iv(A[Y]["W4_cp95"])
        lab = f"{nm(X)} ABOVE {nm(Y)}" if ix[0] > iy[1] else "NOT DISTINGUISHED"
        above[(X, Y)] = ix[0] > iy[1]
        rec("NC-DR-3", f"{nm(X)} vs {nm(Y)}", lab, dr["NC-DR-3"]["pairs"].get(f"{nm(X)} vs {nm(Y)}"))
# NC-DR-4 (order of cases)
case1 = v1 == "TENSOR" and above[("N-CONV", "N-ELL144")] and above[("N-CONV", "NULL-F262")]
lvlL = level(A["N-CONVL"]["W4_verified_wdag"], A["N-CONVL"]["n"])
lvl17 = level(A["N-CONV17"]["W4_verified_wdag"], A["N-CONV17"]["n"])
if case1:
    v4, sub = "CONVOLUTION TENSOR", None
elif v1 == "LINEAR":
    v4 = "LOWER-DEGREE PART REQUIRED"
    sub = {"TENSOR": "SEMAEV LINEAR PART SUFFICES (curve constant not required)",
           "LINEAR": "CURVE CONSTANT REQUIRED (with the confound that the drawn curves' targets are not x(2E))"}.get(lvlL, "MIXED")
else:
    v4, sub = "MIXED", None
if lvl17 == "TENSOR":
    app = "CONVOLUTION FORMS SUFFICE WITHOUT THE COKERNEL FALL"
elif lvl17 == "LINEAR" and case1:
    app = "THE RANK-16 COKERNEL IS NEEDED"
else:
    app = "descriptive"
rec("NC-DR-4", "verdict", v4, dr["NC-DR-4"]["verdict"])
rec("NC-DR-4", "sub_label (only in case (2))", sub, dr["NC-DR-4"]["sub_label"])
rec("NC-DR-4", "appended N-CONV17 reading", app, dr["NC-DR-4"]["appended_N-CONV17_reading"])
rec("NC-DR-4", "N-CONVL level (recorded, informational in case (1))", lvlL + "-level", dr["NC-DR-4"]["N-CONVL_level"])
rec("NC-DR-4", "N-CONV17 level", lvl17 + "-level", dr["NC-DR-4"]["N-CONV17_level"])
# NC-DR-5 (unsat population per dev 10 / R5; S3-S62 on all). Also: does the label change with the population?
pop_sensitivity = {}
for key, p in me["NC-DR-5_profiles"].items():
    a, pop = key.split("|")
    pop_sensitivity.setdefault(a, {})[pop] = p["label"]
    r = dr["NC-DR-5"]["per_arm"].get(a, {}).get(pop)
    if r is not None:
        rec("NC-DR-5", f"{a} ({pop})", p["label"], r["label"])
out["NC-DR-5_label_by_population"] = pop_sensitivity
out["NC-DR-5_population_changes_any_label"] = any(len(set(v.values())) > 1 for v in pop_sensitivity.values())
# NC-DR-6
m4 = iv(A["N-CONV"]["M4_cp95"])
lab6 = "N-CONV M_4 AT STAGE-1 RATE" if overlap(m4, (0.799, 0.875)) else "N-CONV M_4 NOT AT STAGE-1 RATE"
rec("NC-DR-6", "N-CONV label", lab6, dr["NC-DR-6"]["N-CONV_label"])
cond = A["N-CONV"]["W4_given_not_M4"]
out["NC-DR-6_conditional"] = {"x": cond["x"], "n": cond["n"], "defined": cond.get("defined"),
                              "consumed_by_any_rule": False,
                              "note": "NC-DR-6 text: 'Also the conditional W_4 rate ... Descriptive.' No NC-DR label reads it."}
# NC-DR-7
rec7 = {"CONVOLUTION TENSOR": "the n = 19 cell quotes S_3-specificity against an N-CONV-type arm (same-support nulls insufficient)",
        "LOWER-DEGREE PART REQUIRED": "N-ELL-type and same-support nulls carry the contrast, and an N-CONVL-type arm discriminates",
        "MIXED": "both arms"}[v4]
rec("NC-DR-7", "recommendation", rec7, dr["NC-DR-7"]["recommendation"])
# NC-DR-8 (from J4: every control holds; re-derived counts in J5 found no voiding event)
rec("NC-DR-8", "all_pass / run_void / INV-6 / INV-7", [True, False, False, False],
    [dr["NC-DR-8"]["all_pass"], dr["NC-DR-8"]["run_void"], dr["NC-DR-8"]["counts_void_INV6"], dr["NC-DR-8"]["arm_metrics_void_INV7"]])
# NC-DR-9
rec("NC-DR-9", "primary", {"NC-DR-1": v1, "NC-DR-4": v4}, dr["NC-DR-9"]["primary"])
rec("NC-DR-9", "secondary", ["NC-DR-2", "NC-DR-3", "NC-DR-5", "NC-DR-6", "NC-DR-7"], dr["NC-DR-9"]["secondary"])

# PN-1..PN-5 and prior (a)-(g) on my values (and the closures records the texts name)
cl = {}
for l in gzip.open(RUN / "closures.jsonl.gz", "rt"):
    r = json.loads(l)
    cl[(r["key"], r["closure"])] = r
inst = [json.loads(l) for l in gzip.open(RUN / "instances.jsonl.gz", "rt")]
nell = [r["key"] for r in inst if r["arm"] == "N-ELL144" and r["role"] == "unsat"]
nell_t5_ref = [k for k in nell if cl[(k, "rc_b")]["T5_applicable"] and cl[(k, "R'_4")]["dims_by_deg"] == [0, 0, 16, 288, 2328]]
nell_ref_engine = [k for k in nell_t5_ref if cl[(k, "W_4")]["one"]]
nell_t5_pred_refute = [k for k in nell_t5_ref if cl[(k, "rc_b")]["T5_prediction"]["W4_refuted"]]
pn = {
    "PN-1": {"w": L1["w"], "n_C": L1["n_C"], "reading": "E-TENSOR threshold met (w >= 130)" if L1["w"] >= 130 else "not met"},
    "PN-2": "see J4 C-TOP recheck: 0 violations on 864; N-CONV17 one P (1695) -> held",
    "PN-3": "see J3 glue: T4 0 violations on 1028; T5 0 violations on 308 -> held",
    "PN-4": {"refuted_satisfiable_controls": sum(v.get("M4_refuted_engine", 0) + v.get("W4_refuted_engine", 0)
                                                 for v in me["satisfiable_controls"].values()), "reading": "held if 0"},
    "PN-5": {"N-ELL144_unsat": len(nell), "with_T5_and_semi_regular_substituted_profile": len(nell_t5_ref),
             "engine_W4_refutations_there": len(nell_ref_engine), "T5_predicts_refutation_there": len(nell_t5_pred_refute),
             "reading": "held (0 refutations where T5 applies with the reference profile; T5 predicts none)"},
}
out["PN_readings"] = pn
prior = {
    "(a) TENSOR modal": {"observed": v1, "held": v1 == "TENSOR"},
    "(b) N-CONV M_4 rate >= Stage-1 rate 324/386": {"observed": f'{A["N-CONV"]["M4_verified_flat_mu_le2"]}/{A["N-CONV"]["n"]}',
                                                    "held": Fraction(A["N-CONV"]["M4_verified_flat_mu_le2"], A["N-CONV"]["n"]) >= Fraction(324, 386)},
    "(c) N-CONV substituted profiles non-semi-regular on >= 90%": {
        "observed_non_reference": f'{me["NC-DR-5_profiles"]["N-CONV|unsat"]["n"] - me["NC-DR-5_profiles"]["N-CONV|unsat"]["reference_profile"]}/{me["NC-DR-5_profiles"]["N-CONV|unsat"]["n"]} (unsat); '
                                  f'{me["NC-DR-5_profiles"]["N-CONV|all"]["n"] - me["NC-DR-5_profiles"]["N-CONV|all"]["reference_profile"]}/{me["NC-DR-5_profiles"]["N-CONV|all"]["n"]} (all)',
        "held": me["NC-DR-5_profiles"]["N-CONV|all"]["reference_profile"] * 10 <= me["NC-DR-5_profiles"]["N-CONV|all"]["n"]},
    "(d) N-CONVL TENSOR-level": {"observed": lvlL, "held": lvlL == "TENSOR"},
    "(e) N-CONV17 no confident prior": {"observed": lvl17, "held": "n/a (no confident prior)"},
    "(f) N-ELL144 refuted 0 times": {"observed_engine_W4": A["N-ELL144"]["W4_engine"], "observed_verified": A["N-ELL144"]["W4_verified_wdag"],
                                     "held": A["N-ELL144"]["W4_engine"] == 0},
    "(g) every W_4 refutation gets a verified wdag-v1": {"uncertified_all_arms": len(me["uncertified_all_arms"]),
                                                         "held": len(me["uncertified_all_arms"]) == 0},
}
out["prior_a_g"] = prior
out["comparisons"] = cmp
out["mismatches"] = [c for c in cmp if not c["equal"]]
json.dump(out, open(OUTDIR / "j6-reapply.json", "w"), indent=1, default=str)
print("comparisons", len(cmp), "mismatches", len(out["mismatches"]))
for c in out["mismatches"]:
    print(json.dumps(c, default=str))
print("NC-DR-5 population changes any label:", out["NC-DR-5_population_changes_any_label"])
print(json.dumps(pn, indent=0, default=str))
print(json.dumps(prior, indent=0, default=str))
