"""J9 (a), (b)-check, (c), (e) and J10 O1-O3 readings from ARCHIVED records only
(TASK-20260926-c58e87; RT-4). Own aggregation code; imports nothing from impl/ or verifier/.
Reads: RUN-CERTBIN-6ebb0e closures.jsonl.gz, instances.jsonl.gz, support.json;
RC-1 instance-sets.json. Uses j10-ptm/rtlib.py for field arithmetic (N-CONVL target type)
and the E_hex decoder (support-class check).
Usage: python3 j9_analysis.py <worktree> <out.json>
"""
import collections
import gzip
import json
import sys
from fractions import Fraction
from math import comb

sys.path.insert(0, __file__.rsplit("/", 2)[0] + "/j10-ptm")
import rtlib as R  # noqa: E402

wt, out = sys.argv[1], sys.argv[2]
run = f"{wt}/experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
CL = [json.loads(l) for l in gzip.open(f"{run}/closures.jsonl.gz", "rt")]
INS = [json.loads(l) for l in gzip.open(f"{run}/instances.jsonl.gz", "rt")]
ins = {r["key"]: r for r in INS}
by = collections.defaultdict(dict)
for r in CL:
    by[r["key"]][r["closure"]] = r


def tail_ge(k, n, p):
    return sum(Fraction(comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def cp95(x, n):
    """exact Clopper-Pearson 95% by bisection on exact rational tails (60 iterations)."""
    if n == 0:
        return None
    def bis(f, lo, hi):
        lo, hi = Fraction(lo), Fraction(hi)
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid):
                hi = mid
            else:
                lo = mid
        return float((lo + hi) / 2)
    a = Fraction(1, 40)
    lower = 0.0 if x == 0 else bis(lambda p: tail_ge(x, n, p) >= a, 0, 1)
    upper = 1.0 if x == n else bis(lambda p: (1 - tail_ge(x + 1, n, p)) <= a, 0, 1)
    return [round(lower, 6), round(upper, 6)]


res = {}
arms = sorted({r["arm"] for r in INS})
# ---------------- per-arm M_4 / W_4 tables ------------------------------------------
table = {}
for arm in arms:
    for role in ("unsat", "sat"):
        keys = [r["key"] for r in INS if r["arm"] == arm and r["role"] == role]
        if not keys:
            continue
        m4 = [by[k]["M_4"] for k in keys]
        w4 = [by[k]["W_4"] for k in keys]
        s = [ins[k]["s"] for k in keys]
        t = {"n": len(keys),
             "M4_one": sum(1 for x in m4 if x["one"]),
             "W4_one": sum(1 for x in w4 if x["one"]),
             "W4_one_first_iteration": dict(collections.Counter(str(x["one_first_iteration"]) for x in w4)),
             "P_values": dict(collections.Counter(x["P"] for x in m4)),
             "fallen_hist": dict(sorted(collections.Counter(x["fallen"] for x in m4).items())),
             "rank_range": [min(x["rank"] for x in m4), max(x["rank"] for x in m4)],
             "linear_forms_hist": dict(sorted(collections.Counter(x["linear_forms"] for x in m4).items())),
             "M4_profiles_top": [[list(p), c] for p, c in collections.Counter(tuple(x["dims_by_deg"]) for x in m4).most_common(4)]}
        if role == "unsat":
            t["fallen_eq_988"] = sum(1 for x in m4 if x["fallen"] == 988)
            t["M4_one_and_fallen_988"] = sum(1 for x in m4 if x["one"] and x["fallen"] == 988)
            t["M4_one_with_fallen_lt_988"] = sum(1 for x in m4 if x["one"] and x["fallen"] < 988)
            t["M4_cp95"] = cp95(t["M4_one"], t["n"])
            t["codim_B3_hist"] = dict(sorted(collections.Counter(988 - x["fallen"] for x in m4).items()))
        else:
            t["s_hist"] = dict(sorted(collections.Counter(s).items()))
            t["fallen_eq_988_minus_s"] = sum(1 for x, ss in zip(m4, s) if ss <= 15 and x["fallen"] == 988 - ss)
            t["s_le_15"] = sum(1 for ss in s if ss <= 15)
            t["fallen_minus_(988-s)_hist"] = dict(sorted(collections.Counter(x["fallen"] - (988 - ss) for x, ss in zip(m4, s)).items()))
            t["M4_refuted"] = t["M4_one"]
            t["W4_refuted"] = t["W4_one"]
            codims = [4048 - x["final_dim"] for x in w4]
            t["codim_W4_ge_s"] = sum(1 for c, ss in zip(codims, s) if c >= ss)
            t["codim_W4_eq_s"] = sum(1 for c, ss in zip(codims, s) if c == ss)
            t["codim_W4_minus_s_hist"] = dict(sorted(collections.Counter(c - ss for c, ss in zip(codims, s)).items()))
        table[f"{arm}|{role}"] = t
res["arm_tables"] = table

# ---------------- J9 (b) declared-rule check -------------------------------------------
def rule_eval(arm):
    u = table.get(f"{arm}|unsat")
    sat = table.get(f"{arm}|sat")
    frac_u = u["M4_one_and_fallen_988"] / u["n"]
    frac_s = (sat["fallen_eq_988_minus_s"] / sat["s_le_15"]) if sat and sat["s_le_15"] else None
    holds = frac_u >= 0.9 and (frac_s is None or frac_s >= 0.9)
    fails = u["M4_one"] <= 0.5 * u["n"]
    return {"unsat_M4_one_and_fallen_988": [u["M4_one_and_fallen_988"], u["n"]],
            "unsat_M4_one": [u["M4_one"], u["n"]],
            "sat_fallen_eq_988_minus_s": [sat["fallen_eq_988_minus_s"], sat["s_le_15"]] if sat else None,
            "label": "HOLDS" if holds else ("FAILS" if fails else "PARTIAL")}
res["J9b_rule_check"] = {"N-CONV": rule_eval("N-CONV"), "N-CONV17": rule_eval("N-CONV17"),
                         "N-CONVL_HEX": {
                             "unsat_fallen_lt_988": [sum(1 for k in ins if ins[k]["arm"] == "N-CONVL" and by[k]["M_4"]["fallen"] < 988 and ins[k]["role"] == "unsat"), 144],
                             "all_fallen_lt_988": [sum(1 for k in ins if ins[k]["arm"] == "N-CONVL" and by[k]["M_4"]["fallen"] < 988), 288],
                             "unsat_fallen_eq_988": sum(1 for k in ins if ins[k]["arm"] == "N-CONVL" and ins[k]["role"] == "unsat" and by[k]["M_4"]["fallen"] == 988),
                             "M4_rate": [table["N-CONVL|unsat"]["M4_one"], 144]}}

# ---------------- stratification by source set ----------------------------------------
strat = {}
for arm in ("N-CONV", "N-CONVL"):
    for src in ("U62", "S62", "C20"):
        keys = [r["key"] for r in INS if r["arm"] == arm and r["role"] == "unsat" and r["source_set"] == src]
        x = sum(1 for k in keys if by[k]["M_4"]["one"])
        strat[f"{arm}|{src}"] = {"M4": [x, len(keys)], "cp95": cp95(x, len(keys)),
                                 "W4_iter1": sum(1 for k in keys if by[k]["W_4"]["one_first_iteration"] == 1),
                                 "fallen_hist": dict(sorted(collections.Counter(by[k]["M_4"]["fallen"] for k in keys).items()))}
res["stratification_by_source_set"] = strat

# ---------------- J9 (a) selection -----------------------------------------------------
res["J9a"] = {
    "S3_stage1_unconditional_M4": {"x": 324, "n": 386, "cp95_own": cp95(324, 386), "source": "KN-OPEN-3c8f51 / EXP-CERTBIN-ddfe75 preregistered_prediction source (quoted, Stage-1 flags)"},
    "S3_in_run_82": {"M4": [table["S3-U62|unsat"]["M4_one"] + table["S3-C20|unsat"]["M4_one"], 82]},
    "NCONV_M4_all": [table["N-CONV|unsat"]["M4_one"], 144, cp95(table["N-CONV|unsat"]["M4_one"], 144)],
    "NCONVL_M4_all": [table["N-CONVL|unsat"]["M4_one"], 144, cp95(table["N-CONVL|unsat"]["M4_one"], 144)],
    "NCONV17_M4_all": [table["N-CONV17|unsat"]["M4_one"], 144, cp95(table["N-CONV17|unsat"]["M4_one"], 144)],
}

# ---------------- N-CONVL target type (x(2E) of the drawn curve vs twist) ---------------
# x_R is on E_{A,b'} iff Tr(x_R + A + b'/x_R^2) = 0; for the archived curve Tr(x_R + A + B/x_R^2) = 0 and
# Tr(x_R) = Tr(A) on all 144 (checked below), so with the halving criterion (verified separately in
# j9-null/halving_check.json) x_R is an x(2E) target of E_{A,b'} iff Tr(b'/x_R^2) = Tr(B/x_R^2).
ttype = collections.Counter()
tt_rows = []
trA = R.gtr(R.A_CURVE)
chk = {"Tr_xR_eq_Tr_A": 0, "on_archived_curve": 0, "n": 0}
for k, r in ins.items():
    if r["arm"] != "N-CONVL":
        continue
    xr = r["x_R"]
    E = R.hex_to_E(r["E_hex"])
    bp = sum(int(E[kk, 0]) << kk for kk in range(17))  # b' read off the constant column (own decode)
    chk["bprime_field_matches_E"] = chk.get("bprime_field_matches_E", 0) + int(bp == r.get("bprime"))
    inv2 = R.ginv(R.gsq(xr))
    on_orig = R.gtr(xr ^ R.A_CURVE ^ R.gmul(R.B_CURVE, inv2)) == 0
    chk["n"] += 1
    chk["on_archived_curve"] += int(on_orig)
    chk["Tr_xR_eq_Tr_A"] += int(R.gtr(xr) == trA)
    on_new = R.gtr(xr ^ R.A_CURVE ^ R.gmul(bp, inv2)) == 0
    typ = "x(2E) of E_{A,b'}" if (on_new and R.gtr(xr) == trA) else ("x(E) minus x(2E)" if on_new else "twist")
    m4 = by[k]["M_4"]["one"]
    ttype[(r["role"], typ, m4)] += 1
    tt_rows.append({"key": k, "role": r["role"], "type": typ, "M4": m4, "fallen": by[k]["M_4"]["fallen"]})
res["NCONVL_target_type"] = {"checks": chk,
                             "counts_role_type_M4": {f"{a}|{b}|{c}": v for (a, b, c), v in sorted(ttype.items())}}
for typ in ("x(2E) of E_{A,b'}", "twist", "x(E) minus x(2E)"):
    rows = [x for x in tt_rows if x["role"] == "unsat" and x["type"] == typ]
    if rows:
        xx = sum(1 for x in rows if x["M4"])
        res["NCONVL_target_type"][f"unsat|{typ}"] = {"M4": [xx, len(rows)], "cp95": cp95(xx, len(rows)),
                                                    "fallen_hist": dict(sorted(collections.Counter(x["fallen"] for x in rows).items()))}

# ---------------- J9 (e) nulls: profiles and support class -------------------------------
sup = json.load(open(f"{run}/support.json"))
U = R.union_support(R.poly_basis())
nulls = {}
for arm in ("NULL-F262", "NULL-AFF62", "N-ELL144", "NELL-A20"):
    keys = [r["key"] for r in INS if r["arm"] == arm]
    prof = collections.Counter(tuple(by[k]["M_4"]["dims_by_deg"]) for k in keys if ins[k]["role"] == "unsat")
    sub = collections.Counter(tuple(by[k]["R'_4"]["dims_by_deg"]) for k in keys if "R'_4" in by[k] and ins[k]["role"] == "unsat")
    t5 = sum(1 for k in keys if by[k]["rc_b"].get("T5_applicable") and ins[k]["role"] == "unsat")
    inside = 0
    quad_rank = collections.Counter()
    for k in keys:
        E = R.hex_to_E(ins[k]["E_hex"])
        rows_ok = True
        for kk in range(17):
            for c in R.np.flatnonzero(E[kk]):
                if not U[kk, c] and not (arm in ("N-ELL144", "NELL-A20") and kk == 16):
                    rows_ok = False
        inside += int(rows_ok)
        kd, _ = R.left_kernel_dim_quadratic(E)
        quad_rank[17 - kd] += 1
    nulls[arm] = {"n": len(keys), "unsat_M4_profiles": [[list(p), c] for p, c in prof.most_common(3)],
                  "unsat_subst_profiles": [[list(p), c] for p, c in sub.most_common(3)],
                  "T5_applicable_unsat": t5,
                  "systems_inside_U_rows_0_15_or_all": inside, "quadratic_rank_hist": dict(quad_rank),
                  "W4_refuted": sum(1 for k in keys if by[k]["W_4"]["one"])}
res["J9e_nulls"] = nulls

# ---------------- O3 in-run S_3 records -------------------------------------------------
o3 = {}
for arm in ("S3-U62", "S3-C20", "S3-S62"):
    keys = [r["key"] for r in INS if r["arm"] == arm]
    m4 = [by[k]["M_4"] for k in keys]
    o3[arm] = {"n": len(keys), "M4_one": sum(1 for x in m4 if x["one"]),
               "P": dict(collections.Counter(x["P"] for x in m4)),
               "fallen_range": [min(x["fallen"] for x in m4), max(x["fallen"] for x in m4)],
               "codim_B3_range": [988 - max(x["fallen"] for x in m4), 988 - min(x["fallen"] for x in m4)],
               "rule_R-ED_applied_unchanged_predicts_M4_one": len(keys) if arm != "S3-S62" else 0}
res["O3_in_run"] = o3
json.dump(res, open(out, "w"), indent=1)
print(json.dumps(res["J9b_rule_check"], indent=1))
print(json.dumps(res["stratification_by_source_set"], indent=1))
print(json.dumps(res["J9a"], indent=1))
print(json.dumps(res["NCONVL_target_type"], indent=1))
print(json.dumps(res["J9e_nulls"], indent=1))
print(json.dumps(res["O3_in_run"], indent=1))
for k, v in table.items():
    print(k, json.dumps(v))
