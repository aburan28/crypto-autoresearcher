#!/usr/bin/env python3
"""TASK-20260926-0f8aec J5: compare j5-recompute.json with the recorded
decision-rules.json, cell-summary.json and trial-plan-v1.json power table.
Every interval is compared at the recorded 6-decimal precision and, where
recorded, at 20 significant digits. Writes j5-compare.json (a table of
recomputed vs recorded) and prints mismatches."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import mpmath

mpmath.mp.dps = 60
WT = Path(sys.argv[1])
OUTDIR = Path(__file__).resolve().parent
RUN = WT / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
me = json.load(open(OUTDIR / "j5-recompute.json"))
dr = json.load(open(RUN / "decision-rules.json"))
cs = json.load(open(RUN / "cell-summary.json"))
tp = json.load(open(WT / "experiments/EXP-CERTBIN-ddfe75/trial-plan-v1.json"))
rows, bad = [], []


def iv(c):
    if not c.get("defined", True):
        return None
    return [c["lower_6"], c["upper_6"]]


def cmp(name, mine, rec, x=None, n=None, pos=None):
    ok = mine == rec
    rows.append({"item": name, "x": x, "n": n, "recomputed": mine, "recorded": rec, "equal": ok, "position": pos})
    if not ok:
        bad.append(name)


def cmp_cp(name, c, rec_cp, rec20=None):
    if not c.get("defined", True):
        rows.append({"item": name, "x": c["x"], "n": c["n"], "recomputed": "UNDEFINED (0/0)", "recorded": rec_cp,
                     "equal": None, "position": "zero denominator"})
        return
    cmp(name + " cp95[6dp]", iv(c), rec_cp, c["x"], c["n"], c["position"])
    if rec20 is not None:
        mine20 = [c["lower_20sig"] if c["x"] > 0 else "0.0", c["upper_20sig"] if c["x"] < c["n"] else "1.0"]
        eq = all(mpmath.mpf(a) == mpmath.mpf(b) for a, b in zip(mine20, rec20))
        rows.append({"item": name + " cp95[20sig]", "x": c["x"], "n": c["n"], "recomputed": mine20, "recorded": rec20,
                     "equal": eq, "position": c["position"]})
        if not eq:
            bad.append(name + " 20sig")


# MN1 / NC-DR-1
for L, key in (("L1", "L1_uncertified_as_not_refuted"), ("L2", "L2_uncertified_excluded")):
    m, r = me["MN1"][L], dr["NC-DR-1"][key]
    cmp(f"NC-DR-1 {L} w", m["w"], r["w"], m["w"], m["n_C"], "ceiling" if m["w"] == m["n_C"] else "interior")
    cmp(f"NC-DR-1 {L} n_C", m["n_C"], r["n_C"])
    cmp_cp(f"NC-DR-1 {L}", m["cp95"], r["cp95"])
    cmp(f"NC-DR-1 {L} label", m["label"], r["label"])
    cmp(f"NC-DR-1 {L} E_TENSOR_falsified", m["E_TENSOR_falsified"], r["E_TENSOR_falsified"])
    cmp(f"NC-DR-1 {L} E_LINEAR_falsified", m["E_LINEAR_falsified"], r["E_LINEAR_falsified"])
cmp("NC-DR-1 thresholds", me["MN1"]["L1"]["thresholds"], dr["NC-DR-1"]["thresholds_at_n_C"])
cmp("NC-DR-1 uncertified", me["MN1"]["uncertified"], dr["NC-DR-1"]["uncertified"])
cmp("MN1 cell-summary w/n_C/uncertified", [me["MN1"]["L1"]["w"], me["MN1"]["L1"]["n_C"], me["MN1"]["uncertified"]],
    [cs["MN1_w4_refuted_NCONV"]["w"], cs["MN1_w4_refuted_NCONV"]["n_C"], cs["MN1_w4_refuted_NCONV"]["uncertified"]])
cmp_cp("MN1 cell-summary", me["MN1"]["L1"]["cp95"], cs["MN1_w4_refuted_NCONV"]["cp95"])
# MN2 and secondaries per arm
sec = cs["secondary"]["arms"]
for a, m in me["arms"].items():
    r2 = cs["MN2_w4_refuted_by_arm"][a]
    cmp(f"MN2 {a} x/n", [m["W4_verified_wdag"], m["n"]], [r2["x"], r2["n"]])
    cmp_cp(f"MN2 {a}", m["W4_cp95"], r2["cp95"], sec[a]["W4_cp95"].get("cp95_exact_20dig"))
    cmp(f"{a} W4 wdag-only == wdag-or-flat(|mu|<=2)", m["W4_verified_wdag"], m["W4_verified_wdag_or_flat_mu_le2"])
    cmp(f"{a} W4_engine/uncertified", [m["W4_engine"], m["W4_uncertified"]], [sec[a]["W4_engine"], sec[a]["W4_uncertified"]])
    cmp(f"{a} M4 verified/engine", [m["M4_verified_flat_mu_le2"], m["M4_engine"]], [sec[a]["M4_verified"], sec[a]["M4_engine"]])
    cmp_cp(f"{a} M4", m["M4_cp95"], sec[a]["M4_cp95"]["cp95"], sec[a]["M4_cp95"].get("cp95_exact_20dig"))
    g, rg = m["W4_given_not_M4"], sec[a]["W4_given_not_M4"]
    cmp(f"{a} W4|not M4 x/n", [g["x"], g["n"]], [rg["x"], rg["n"]])
    cmp_cp(f"{a} W4|not M4", g, rg["cp95"])
    if a in dr["NC-DR-6"]["per_arm_M4"]:
        rr = dr["NC-DR-6"]["per_arm_M4"][a]
        cmp(f"NC-DR-6 {a} M4 x/n", [m["M4_verified_flat_mu_le2"], m["n"]], [rr["x"], rr["n"]])
        cmp_cp(f"NC-DR-6 {a} M4", m["M4_cp95"], rr["cp95"])
g = me["arms"]["N-CONV"]["W4_given_not_M4"]
rows.append({"item": "NC-DR-6 N-CONV_W4_given_M4_unrefuted", "x": g["x"], "n": g["n"],
             "recomputed": "UNDEFINED (0/0)", "recorded": dr["NC-DR-6"]["N-CONV_W4_given_M4_unrefuted"],
             "equal": None, "position": "zero denominator"})
# NC-DR-2
cmp_cp("NC-DR-2 N-CONV", me["MN1"]["L1"]["cp95"], dr["NC-DR-2"]["N-CONV_cp95"])
cmp_cp("NC-DR-2 S3 386/386", me["refs"]["S3_386_of_386"], dr["NC-DR-2"]["S3_386_cp95"])
cmp_cp("NC-DR-2 in-run S3 82", me["arms"]["S_3 (82)"]["W4_cp95"], dr["NC-DR-2"]["in_run_S3_82"]["cp95"])
# NC-DR-3 intervals
name_map = {"S_3 (82)": "S_3 (82)"}
for a, r in dr["NC-DR-3"]["intervals"].items():
    m = me["arms"][a]
    cmp(f"NC-DR-3 {a} x/n", [m["W4_verified_wdag"], m["n"]], [r["x"], r["n"]])
    cmp_cp(f"NC-DR-3 {a}", m["W4_cp95"], r["cp95"])
# stage-1 frozen constant
s1 = me["refs"]["stage1_324_of_386"]
rows.append({"item": "frozen constant: Stage-1 CP95 of 324/386 (specification quotes [0.799, 0.875])", "x": 324, "n": 386,
             "recomputed": [s1["lower_6"], s1["upper_6"]], "recorded": dr["NC-DR-6"]["stage1_interval"],
             "equal": [round(s1["lower_6"], 3), round(s1["upper_6"], 3)] == dr["NC-DR-6"]["stage1_interval"],
             "position": "interior"})
# by source, paired table
for s, c in me["N-CONV_by_source"].items():
    r = cs["secondary"]["N-CONV_by_source"][s]
    cmp(f"N-CONV by source {s} w/n", [c["x"], c["n"]], [r["w"], r["n"]])
    cmp_cp(f"N-CONV by source {s}", c, r["cp95"])
cmp("paired S3 vs N-CONV 2x2", me["paired_S3_vs_NCONV_W4"], cs["secondary"]["paired_S3_vs_NCONV_W4"])
# certificates, satisfiable controls
cmp("MN3 certificates per kind", me["certificates_per_kind"], cs["MN3_soundness_and_certificates"]["certificates"])
for a, c in me["satisfiable_controls"].items():
    r = cs["MN3_soundness_and_certificates"]["satisfiable_controls"][a]
    cmp(f"MN3 satisfiable {a}", {k: c.get(k, 0) for k in ("n", "M4_refuted_engine", "W4_refuted_engine", "certificates_verified",
                                                        "s_le_31", "codim_ge_s", "codim_eq_s")},
        {k: r[k] for k in ("n", "M4_refuted_engine", "W4_refuted_engine", "certificates_verified", "s_le_31", "codim_ge_s", "codim_eq_s")})
# NC-DR-5
for key, m in me["NC-DR-5_profiles"].items():
    a, pop = key.split("|")
    r = dr["NC-DR-5"]["per_arm"].get(a, {}).get(pop)
    if r is None:
        continue
    cmp(f"NC-DR-5 {a} {pop}", [m["n"], m["reference_profile"], m["substituted"], m["T5_applicable"], m["label"]],
        [r["n"], r["reference_profile"], r["substituted"], r["T5_applicable"], r["label"]])
# draw statistics
for a, m in me["draw_statistics"].items():
    r = cs["secondary"]["draw_statistics"][a]
    u, e = m["unsat_among_evaluated"].split("/")
    cmp(f"draws {a}", [m["attempts"], m["evaluated"], m["rejections"], m["attempts_per_slot_max"]],
        [r["attempts"], r["evaluated"], r["rejections"], r["attempts_per_slot_max"]])
    cmp(f"draws {a} unsat fraction", float(int(u) / int(e)), r["unsat_fraction_among_evaluated"])
# power table
ptm = {r["p"]: r for r in me["power_table_exact"]["rows"]}
cmp("power table thresholds", me["power_table_exact"]["thresholds"],
    {"tensor": tp["power_table"]["thresholds"]["tensor_ceil_0.9n"], "linear": tp["power_table"]["thresholds"]["linear_floor_0.1n"],
     "half": tp["power_table"]["thresholds"]["half_floor_n/2"]})
for r in tp["power_table"]["rows"]:
    m = ptm[r["p"]]
    for col in ("P(w >= 130)", "P(w <= 14)", "P(w <= 72)"):
        a, b = m[col]["value_20sig"], r[col]["value"]
        eqv = mpmath.almosteq(mpmath.mpf(a), mpmath.mpf(b), rel_eps=mpmath.mpf(10) ** -19) or a == b
        la, lb = m[col]["log10"], r[col]["log10"]
        eql = abs(mpmath.mpf(la) - mpmath.mpf(lb)) <= mpmath.mpf(10) ** -12 * max(1, abs(mpmath.mpf(lb)))
        rows.append({"item": f"power p={r['p']} {col}", "recomputed": [a, la, m[col]["one_minus_value_20sig"]],
                     "recorded": [b, lb], "equal": bool(eqv and eql), "position": "exact tail"})
        if not (eqv and eql):
            bad.append(f"power p={r['p']} {col}")
out = {"rows": rows, "mismatches": bad, "n_rows": len(rows)}
json.dump(out, open(OUTDIR / "j5-compare.json", "w"), indent=1, default=str)
print("rows", len(rows), "mismatches", bad)
for r in rows:
    if r["equal"] is not True:
        print(json.dumps(r, default=str)[:400])
