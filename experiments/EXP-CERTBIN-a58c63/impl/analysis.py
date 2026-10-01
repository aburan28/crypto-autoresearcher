"""Phase 8 statistics for EXP-CERTBIN-a58c63: MB1-MB5, MA1, MA2, M3, M5 and the
secondary metrics; instrument checks and invalidation rules; DB-1..DB-12;
tail checks. Exact arithmetic for every interval and tail (statsx)."""
from collections import Counter
from fractions import Fraction

import numpy as np

from statsx import (clopper_pearson, poisson_interval, poisson_ratio_interval, binom_tail_exact, frac_log10,
                    binom_band, median, entropy_bits)

GR = ("rank", "set", "strict", "ops")


def arm_of(rec):
    return rec["stratum"]


def scored(records, key):
    out = []
    for r in records:
        if r["degenerate"] or key not in r["refs"]:
            continue
        out.append(r)
    return out


def retention(records, key, arm, gran="strict"):
    rs = [r for r in scored(records, key) if arm_of(r) == arm]
    x = sum(1 for r in rs if r["refs"][key]["match"][gran])
    return x, len(rs)


def ret_block(records, key, arm, gran="strict", ci=True):
    x, n = retention(records, key, arm, gran)
    d = {"ref": key, "arm": arm, "granularity": gran, "matched": x, "n": n,
         "retention": (x / n if n else None)}
    if ci and n:
        cp = clopper_pearson(x, n)
        d["CP95"] = [cp["lo"], cp["hi"]]
        d["CP95_str"] = [cp["lo_str"], cp["hi_str"]]
    return d


def fam_retention(records, keys, arm="unsat", gran="strict", ci=True):
    per = [ret_block(records, k, arm, gran, ci) for k in keys]
    vals = [(p["retention"], i) for i, p in enumerate(per) if p["retention"] is not None]
    if not vals:
        return {"per_ref": per, "retention_family": None, "min": None, "maximizing_ref": None}
    mx = max(vals, key=lambda v: (v[0], -v[1]))
    mn = min(v[0] for v in vals)
    return {"per_ref": per, "retention_family": mx[0], "maximizing_ref": per[mx[1]]["ref"], "min": mn,
            "maximizing_count": [per[mx[1]]["matched"], per[mx[1]]["n"]]}


def stab_class(v):
    if v is None:
        return "not evaluable"
    if v >= 0.9:
        return "STABLE"
    if v < 0.5:
        return "UNSTABLE"
    return "PARTIAL"


def ref_keys(unit, prefix=""):
    labs = [r["label"] for r in unit["refs"]]
    return labs


def unsat_keys(unit, prefix=""):
    """keys of unsat own references + the modal (always included, per Stage-1 M1)."""
    out = []
    for r in unit["refs"]:
        if r["label"] == "modal" or (r["s"] == 0 and r["label"].startswith("U")):
            out.append(prefix + r["label"])
    return out


def type_counts(records, key, arm):
    c = Counter()
    for r in scored(records, key):
        if arm_of(r) != arm:
            continue
        d = r["refs"][key]
        c[d.get("type") or "MATCH"] += 1
        if d.get("prefix_flag"):
            c["prefix_flag"] += 1
    return dict(c)


def fdiv_median(records, key, arm):
    v = [r["refs"][key]["f_div"] for r in scored(records, key) if arm_of(r) == arm and r["refs"][key]["f_div"] is not None]
    return median(v), len(v)


def m3_ratio(num_fr, den_fr, num_records, den_records, num_keys, den_keys, seed, nres):
    """F-J3-1 precedence (first matching rule applies)."""
    ncount = num_fr["maximizing_count"][0] if num_fr["maximizing_count"] else 0
    dcounts = [p["matched"] for p in den_fr["per_ref"]]
    dmax_count = den_fr["maximizing_count"][0] if den_fr["maximizing_count"] else 0
    out = {"numerator_retention_family": num_fr["retention_family"],
           "denominator_retention_family": den_fr["retention_family"],
           "numerator_count": ncount, "denominator_count": dmax_count}
    if num_fr["retention_family"] is None or den_fr["retention_family"] is None:
        out.update({"rule": "not evaluable", "value": None})
        return out
    if ncount == 0 and dmax_count == 0:
        out.update({"rule": "(1) both counts 0", "value": "not estimable"})
    elif ncount == 0:
        out.update({"rule": "(2) numerator 0", "value": 0.0})
    elif dmax_count == 0:
        # CP95 upper bound of the denominator's maximizing reference
        p = den_fr["per_ref"][[q["ref"] for q in den_fr["per_ref"]].index(den_fr["maximizing_ref"])]
        ub = p["CP95"][1]
        out.update({"rule": "(3) denominator 0: lower bound", "value": num_fr["retention_family"] / ub,
                    "denominator_CP95_upper": ub})
    else:
        pt = num_fr["retention_family"] / den_fr["retention_family"]
        g = np.random.Generator(np.random.PCG64(seed))
        nu = [r for r in num_records if not r["degenerate"] and r["stratum"] == "unsat"]
        de = [r for r in den_records if not r["degenerate"] and r["stratum"] == "unsat"]
        ratios = []

        def rf(recs, keys):
            best = None
            for k in keys:
                sc = [r for r in recs if k in r["refs"]]
                if not sc:
                    continue
                v = sum(r["refs"][k]["match"]["strict"] for r in sc) / len(sc)
                best = v if best is None else max(best, v)
            return best
        for _ in range(nres):
            a = [nu[i] for i in g.integers(0, len(nu), size=len(nu))]
            b = [de[i] for i in g.integers(0, len(de), size=len(de))]
            x, y = rf(a, num_keys), rf(b, den_keys)
            ratios.append(x / y if (x is not None and y) else float("inf"))
        ratios.sort()
        out.update({"rule": "(4) point estimate with bootstrap 95% interval", "value": pt,
                    "bootstrap95": [ratios[int(0.025 * nres)], ratios[int(0.975 * nres) - 1]],
                    "bootstrap": {"resamples": nres, "seed": seed, "percentile": True}})
    return out


# ---------------------------------------------------------------------------
def analyze_cell_B(cell, units, p4, P1, n, l, seed, nres):
    s3 = units["F-S3"]
    recs = s3["records"]
    ukeys = unsat_keys(s3)
    ukeys_U = [k for k in ukeys if k != "modal"]
    skeys = [r["label"] for r in s3["refs"] if r["label"].startswith("S")]
    out = {}
    # MB1
    fr = fam_retention(recs, ukeys)
    out["MB1"] = fr
    out["MB1_other_granularities"] = {g: fam_retention(recs, ukeys, gran=g, ci=False) for g in ("rank", "set", "ops")}
    out["sat_arm_vs_sat_refs"] = {g: [ret_block(recs, k, "sat", g, ci=(g == "strict")) for k in skeys] for g in GR}
    arms = {a: [r for r in recs if not r["degenerate"] and r["stratum"] == a] for a in ("unsat", "sat")}
    out["arm_sizes"] = {a: len(v) for a, v in arms.items()}
    out["arm_sizes"]["degenerate"] = sum(r["degenerate"] for r in recs)
    out["underpowered"] = {a: len(v) < 100 for a, v in arms.items()}
    # MB2
    mb2 = {}
    for k in ukeys + skeys:
        mb2[k] = {a: {"median_f_div": fdiv_median(recs, k, a)[0], "n": fdiv_median(recs, k, a)[1],
                      "types": type_counts(recs, k, a)} for a in ("unsat", "sat")}
    out["MB2"] = mb2
    # MB3
    N_unsat = len(arms["unsat"])
    mb3 = {"N_unsat": N_unsat, "per_ref": {}, "two_to_n": 1 << n}
    pooled = set()
    outside = 0
    for k in ukeys_U:
        kb = p4["per_ref"].get(k, {}).get("K_B")
        brk = [r for r in arms["unsat"] if r["refs"][k].get("type") == "ZERO-PIVOT"]
        for r in brk:
            pooled.add(r["idx"])
        row_order = sum(1 for r in arms["unsat"] if r["refs"][k].get("type") == "ROW-ORDER")
        d = {"K_B": kb, "X": len(brk), "breaking_x_R": [r["x_R"] for r in brk],
             "row_order_first_divergences": row_order,
             "row_order_rate": row_order / N_unsat if N_unsat else None,
             "reference_non_generic": (row_order > 0.01 * N_unsat) if N_unsat else None}
        if kb is not None:
            mu = Fraction(N_unsat * kb, 1 << n)
            pi = poisson_interval(mu)
            d["poisson999"] = pi
            d["inside"] = pi["lo"] <= len(brk) <= pi["hi"]
            outside += (not d["inside"])
        else:
            d["poisson999"] = None
            d["inside"] = None
        mb3["per_ref"][k] = d
    mb3["pooled_distinct_breaking_targets"] = len(pooled)
    mb3["pooled_rate"] = len(pooled) / N_unsat if N_unsat else None
    if N_unsat:
        cp = clopper_pearson(len(pooled), N_unsat)
        mb3["pooled_rate_CP95"] = [cp["lo"], cp["hi"]]
    mb3["n_refs_outside_interval"] = outside
    tail = binom_tail_exact(3, Fraction(1, 1000), outside)
    mb3["tail_break_set_extremes"] = {"outside": outside, "P_Bin_3_0.001_ge_outside": str(tail),
                                     "log10": frac_log10(tail) if tail else None}
    # F-RANDX breaks against the F-S3 unsat refs
    rx = units["F-RANDX"]["records"]
    rx_unsat = [r for r in rx if not r["degenerate"] and r["stratum"] == "unsat"]
    rxp = set()
    per = {}
    for k in ukeys_U:
        kk = f"F-S3:{k}"
        b = [r for r in rx_unsat if r["refs"].get(kk, {}).get("type") == "ZERO-PIVOT"]
        per[k] = {"X": len(b), "breaking_x_R": [r["x_R"] for r in b]}
        rxp.update(r["idx"] for r in b)
    mb3["F-RANDX"] = {"N_unsat": len(rx_unsat), "per_ref": per, "pooled_distinct": len(rxp),
                      "pooled_rate": len(rxp) / len(rx_unsat) if rx_unsat else None}
    if rx_unsat:
        cp = clopper_pearson(len(rxp), len(rx_unsat))
        mb3["F-RANDX"]["pooled_rate_CP95"] = [cp["lo"], cp["hi"]]
    split = {}
    for cls in ("x2E", "xE_not_x2E", "twist"):
        sub = [r for r in rx_unsat if r.get("x2E_class") == cls]
        b = [r for r in sub if r["idx"] in rxp]
        rt = {}
        for k in ukeys_U:
            kk = f"F-S3:{k}"
            rt[k] = (sum(r["refs"][kk]["match"]["strict"] for r in sub) / len(sub)) if sub else None
        split[cls] = {"n_unsat": len(sub), "breaking": len(b), "rate": len(b) / len(sub) if sub else None,
                      "strict_retention_vs_F-S3_refs": rt}
    ctr = P1["C-TR"]
    if not ctr.get("point_test_equals_doubling_image", True):
        split = {"VOID": "point test and doubling image disagree (AMD C-18)", "computed": split}
    mb3["F-RANDX"]["x2E_split"] = split
    out["MB3"] = mb3
    # MB4
    mb4 = {}
    curve_fams = ("F-S3", "F-SAT", "F-PLANT", "F-RANDX")
    for fam in curve_fams + ("F-NULLB", "F-AFFB"):
        u = units[fam]
        rr = [r for r in u["records"] if not r["degenerate"]]
        d = {}
        for a in ("unsat", "sat"):
            ra = [r for r in rr if r["stratum"] == a]
            ones = sum(r["one_in_R"] for r in ra)
            d[a] = {"n": len(ra), "one_in_R66": ones, "fraction": ones / len(ra) if ra else None,
                    "rank_distribution": dict(Counter(r["rank"] for r in ra))}
            if ra:
                cp = clopper_pearson(ones, len(ra))
                d[a]["fraction_CP95"] = [cp["lo"], cp["hi"]]
        un = [r for r in rr if r["stratum"] == "unsat"]
        d["delta_distribution_unsat"] = dict(Counter(r.get("delta") for r in un))
        d["C-DELTA_fail"] = [r["idx"] for r in u["records"] if r.get("C-DELTA_ok") is False]
        d["C-RANKB_fail"] = [r["idx"] for r in u["records"] if r.get("C-RANKB_ok") is False]
        d["C-DELTA_checked"] = sum(1 for r in u["records"] if r.get("C-DELTA_ok") is not None)
        d["C-RANKB_checked"] = sum(1 for r in u["records"] if r.get("C-RANKB_ok") is not None)
        mb4[fam] = d
    thr = (1 << (l + 1)) - 2
    un = arms["unsat"]
    deltas = [r["delta"] for r in un if r.get("delta") is not None]
    mb4["tail_delta_extremes"] = {"min_delta_unsat_F-S3": min(deltas) if deltas else None,
                                  "threshold_2^(l+1)-2": thr,
                                  "n_below": sum(1 for d in deltas if d < thr), "n": len(deltas),
                                  "fraction_below": (sum(1 for d in deltas if d < thr) / len(deltas)) if deltas else None,
                                  "TS2G_falsified_(>1%)": (sum(1 for d in deltas if d < thr) > 0.01 * len(deltas)) if deltas else None}
    out["MB4"] = mb4
    # MB5 (E3): AMD-20260924-3a9f06 C-2 / C-9
    mb5 = {}
    sat_recs = {fam: [r for r in units[fam]["records"] if not r["degenerate"] and r["stratum"] == "sat"]
                for fam in ("F-SAT", "F-PLANT")}
    union = {}
    for fam in ("F-SAT", "F-PLANT"):
        for r in sat_recs[fam]:
            union.setdefault(r["x_R"], (fam, r))
    any_unsat_ref_one = any(r["one_in_R"] for r in s3["refs"] if r["label"].startswith("U"))
    evaluable = (l == 5) or any_unsat_ref_one
    for k in ukeys_U:
        kk = f"F-S3:{k}"
        d = {}
        for fam, rs in sat_recs.items():
            x = sum(1 for r in rs if r["refs"][kk].get("E3_success"))
            alt = sum(1 for r in rs if r["refs"][kk].get("E3_prefix_first_sensitivity"))
            tc = Counter((r["refs"][kk].get("type") or "MATCH") + ("+prefix_flag" if r["refs"][kk].get("prefix_flag") else "") for r in rs)
            d[fam] = {"n": len(rs), "E3_count": x, "fraction": x / len(rs) if rs else None,
                      "E3_prefix_first_sensitivity_count": alt, "types": dict(tc)}
        ur = [r for _, r in union.values()]
        x = sum(1 for r in ur if r["refs"][kk].get("E3_success"))
        alt = sum(1 for r in ur if r["refs"][kk].get("E3_prefix_first_sensitivity"))
        tc = Counter((r["refs"][kk].get("type") or "MATCH") + ("+prefix_flag" if r["refs"][kk].get("prefix_flag") else "") for r in ur)
        d["pooled"] = {"definition": "union by x_R of the non-degenerate satisfiable F-SAT and F-PLANT targets (AMD C-9)",
                       "n": len(ur), "n_in_both_arms": sum(len(sat_recs[f]) for f in sat_recs) - len(ur),
                       "E3_count": x, "fraction": x / len(ur) if ur else None,
                       "E3_prefix_first_sensitivity": (alt / len(ur)) if ur else None,
                       "E3_prefix_first_sensitivity_count": alt, "types": dict(tc),
                       "underpowered_(<100)": len(ur) < 100,
                       "note_sensitivity": "REPORTING ONLY (AMD ruling_1 rejected_reading_reported); feeds no rule"}
        if ur:
            cp = clopper_pearson(x, len(ur))
            d["pooled"]["CP95"] = [cp["lo"], cp["hi"]]
        mb5[k] = d
    out["MB5"] = {"evaluable": evaluable, "per_ref": mb5,
                  "not_evaluable_reason": None if evaluable else "l = 6 and no unsat reference has 1 in R_66"}
    # modal, entropy
    out["modal"] = s3["modal_info"]
    ent = {}
    nd = [r for r in recs if not r["degenerate"]]
    for g in GR:
        h, nd_, N, mx = entropy_bits([r[f"h_{g}"] for r in nd])
        ent[g] = {"H_bits": h, "distinct": nd_, "N": N, "largest_class": mx}
    out["H_T"] = ent
    return out


def analyze_cell_A(cell, unitsA, D):
    s3 = unitsA[("F-S3", D)]
    recs = s3["records"]
    ukeys = unsat_keys(s3)
    out = {"MA1": {}}
    fr = fam_retention(recs, ukeys)
    out["MA1"]["strict_unsat"] = fr
    out["MA1"]["other_granularities"] = {g: fam_retention(recs, ukeys, gran=g, ci=False) for g in ("rank", "set", "ops")}
    out["MA1"]["median_f_div"] = {k: {a: fdiv_median(recs, k, a)[0] for a in ("unsat", "sat")} for k in ukeys}
    hull = s3.get("hull") or {}
    out["MA1"]["hull"] = {k: {x: v.get(x) for x in ("K", "K_exact", "K_rank", "K_rank_hull", "dimW", "zero_in_H")}
                          | {"dim_Sigma_H": v["Sigma_H"]["dim"], "Sigma_H_consistent": v["Sigma_H"]["consistent"],
                             "dim_Sigma": v["Sigma"]["dim"]}
                          for k, v in (hull.get("refs") or {}).items()}
    out["MA2_TS1R"] = {fam: (unitsA[(fam, D)].get("hull") or {}).get("TS1R") for fam in
                       ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-AFF") if (fam, D) in unitsA}
    for t in out["MA2_TS1R"].values():
        if t:
            t.pop("measurements_full", None)
    ones = {}
    for fam in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-AFF", "F-NULLF2"):
        if (fam, D) not in unitsA:
            continue
        rr = [r for r in unitsA[(fam, D)]["records"] if not r["degenerate"]]
        ones[fam] = {a: {"n": sum(1 for r in rr if r["stratum"] == a),
                         "one_in_R": sum(1 for r in rr if r["stratum"] == a and r["one_in_R"])} for a in ("unsat", "sat")}
    out["one_in_R_rates"] = ones
    rx = [r for r in unitsA[("F-RANDX", D)]["records"] if not r["degenerate"] and r["stratum"] == "unsat"]
    out["F-RANDX_x2E_split_one_in_R"] = {c: {"n": sum(1 for r in rx if r.get("x2E_class") == c),
                                            "one_in_R": sum(1 for r in rx if r.get("x2E_class") == c and r["one_in_R"])}
                                        for c in ("x2E", "xE_not_x2E", "twist")}
    nd = [r for r in recs if not r["degenerate"]]
    out["H_T"] = {g: dict(zip(("H_bits", "distinct", "N", "largest_class"), entropy_bits([r[f"h_{g}"] for r in nd])))
                  for g in GR}
    out["modal"] = s3["modal_info"]
    return out


# ---------------------------------------------------------------------------
# instrument checks (M5)
def nesting_violations(records):
    bad = []
    for r in records:
        for k, d in r["refs"].items():
            m = d["match"]
            if (m["ops"] and not m["strict"]) or (m["strict"] and not m["set"]) or (m["set"] and not m["rank"]):
                bad.append({"idx": r["idx"], "ref": k, "match": m})
    return bad


def instrument_checks_cell(lab, n, l, P1, unitsA, unitsB, revA, revB, p4, cprov_pass, E0, Ej, Ushape_info):
    ck = {}
    curve_fams = ("F-S3", "F-SAT", "F-PLANT", "F-RANDX")
    # C-ORACLE
    bad = []
    for fam in curve_fams:
        for t in P1[fam].get("refs", []) + P1[fam]["targets"]:
            if not t.get("oracle_agree"):
                bad.append({"family": fam, "idx": t.get("idx"), "label": t.get("selected_as"), "x_R": t["x_R"],
                            "s_A": t.get("s_A"), "s_B": t.get("s_B"), "s_C": t.get("s_C")})
    xc = P1["F-SAT"].get("E_SAT_cross_check", {})
    if xc and not xc.get("equal"):
        bad.append({"item": "E_SAT cross-check (AMD C-17)", **xc})
    ck["C-ORACLE"] = {"pass": not bad, "violations": bad,
                      "checked": sum(len(P1[f].get("refs", [])) + len(P1[f]["targets"]) for f in curve_fams),
                      "E_SAT_cross_check_equal": xc.get("equal")}
    # C-WIT
    bad = []
    for fam in curve_fams + ("F-AFF", "F-NULLF2", "F-NULLB", "F-AFFB"):
        for t in P1[fam].get("refs", []) + P1[fam]["targets"]:
            if t.get("wit_fail"):
                bad.append({"family": fam, "idx": t.get("idx"), "label": t.get("selected_as"), "fail": t["wit_fail"]})
    for fam in ("F-PLANT", "F-SAT"):
        for t in P1[fam]["targets"]:
            if t["s"] < 1:
                bad.append({"family": fam, "idx": t["idx"], "issue": "s < 1"})
    for t in P1["F-PLANT"]["targets"]:
        if not t.get("planted_witness_found"):
            bad.append({"family": "F-PLANT", "idx": t["idx"], "issue": "planted witness not among the solutions"})
    ck["C-WIT"] = {"pass": not bad, "violations": bad}
    # C-DELTA / C-RANKB (control scope: curve-algebra families, references included)
    for cname, fld in (("C-DELTA", "C-DELTA_ok"), ("C-RANKB", "C-RANKB_ok")):
        bad, checked, data_nulls = [], 0, {}
        for fam in curve_fams:
            u = unitsB[fam]
            for r in u["refs"]:
                v = r["checks"].get(fld)
                if v is not None:
                    checked += 1
                    if v is False:
                        bad.append({"family": fam, "ref": r["label"], "x_R": r["x_R"], "s": r["s"], "rank": r["rank"],
                                    "one_in_R": r["one_in_R"], "delta": r["checks"].get("delta"),
                                    "rank_pred": r["checks"].get("rank_pred")})
            for r in u["records"]:
                v = r.get(fld)
                if v is not None:
                    checked += 1
                    if v is False:
                        bad.append({"family": fam, "idx": r["idx"], "x_R": r["x_R"], "s": r["s"], "rank": r["rank"],
                                    "one_in_R": r["one_in_R"], "delta": r.get("delta"), "top_identity_ok": r.get("top_identity_ok"),
                                    "rank_pred": r.get("rank_pred")})
        for fam in ("F-NULLB", "F-AFFB"):
            u = unitsB[fam]
            vals = [r.get(fld) for r in u["records"]] + [r["checks"].get(fld) for r in u["refs"]]
            data_nulls[fam] = {"checked": sum(v is not None for v in vals), "mismatches": sum(v is False for v in vals)}
        ck[cname] = {"pass": not bad, "violations": bad, "checked": checked,
                     "null_families_as_data": data_nulls}
    # C-BREAK, C-REPLAYB
    cb = p4["C-BREAK"]
    ck["C-BREAK"] = {"pass": cb["pass"], "n_zero_pivot_checks": len(cb["checks"]),
                     "n_matched_full_minor": len(cb["matched_full_minor"]),
                     "violations": [c for c in cb["checks"] if not c["pass"]] + [c for c in cb["matched_full_minor"] if not c["pass"]]}
    rb = p4["C-REPLAYB"]
    ck["C-REPLAYB"] = {"version": 2, "pass": all(v["pass"] for v in rb.values()),
                       "per_ref": {k: {"pass": v["pass"], "failures": v["failures"],
                                       "n_matched_checked": v["n_matched_checked"],
                                       "n_matched_available": v.get("n_matched_available"),
                                       "n_schedule_valid_DATA": v["n_schedule_valid"],
                                       "k_star_distribution_DATA": v["k_star_distribution"],
                                       "attributed_zeros_total": v["attributed_zeros_total"],
                                       "attributed_zeros_checked": v["attributed_zeros_checked"],
                                       "label_DATA": v["label"]} for k, v in rb.items()},
                       "note": "AMD-20260924-3a9f06 C-4: fails only on (a) guided != own, (b) replay != proposition-R prediction, (c) an attributed zero not verified; predicted and verified schedule invalidity is DATA"}
    # C-CLASS (AMD C-3)
    cc = {}
    for fam, u in unitsB.items():
        bad = []
        unsat_keys_f = set()
        for r in u["refs"]:
            if r["s"] == 0 and r["label"].startswith("U"):
                unsat_keys_f.add(r["label"])
        if fam in ("F-SAT", "F-PLANT", "F-RANDX"):
            unsat_keys_f |= {f"F-S3:U{i}" for i in (1, 2, 3)}
        for rec in u["records"]:
            for key, d in rec["refs"].items():
                t = d.get("type")
                if t == "UNCLASSIFIED":
                    bad.append({"idx": rec["idx"], "ref": key, "item": "i", "type": t})
                if d.get("prefix_flag") and t != "COLUMN":
                    bad.append({"idx": rec["idx"], "ref": key, "item": "iii", "type": t})
                if l == 5 and key in unsat_keys_f:
                    if t in ("PREFIX", "EXTRA-PIVOT"):
                        bad.append({"idx": rec["idx"], "ref": key, "item": "ii", "type": t})
                    if t == "COLUMN":
                        if rec["s"] < 1 or d.get("c_ref") != rec.get("first_nonpivot_col"):
                            bad.append({"idx": rec["idx"], "ref": key, "item": "ii", "type": t, "s": rec["s"],
                                        "c_ref": d.get("c_ref"), "first_nonpivot_col": rec.get("first_nonpivot_col")})
        cc[fam] = {"pass": not bad, "violations": bad[:50], "n_violations": len(bad)}
    ck["C-CLASS"] = {"pass": all(v["pass"] for v in cc.values()), "per_family": cc,
                     "curve_algebra_pass": all(cc[f]["pass"] for f in curve_fams),
                     "nulls_pass": {f: cc[f]["pass"] for f in ("F-NULLB", "F-AFFB")}}
    # C-12: C-DELTA / C-RANKB computed on the null families (their own failure route)
    c12 = {}
    for fam in ("F-NULLB", "F-AFFB"):
        u = unitsB[fam]
        bad = []
        for fld in ("C-DELTA_ok", "C-RANKB_ok"):
            for r in u["records"]:
                if r.get(fld) is False:
                    bad.append({"idx": r["idx"], "check": fld, "s": r["s"], "rank": r["rank"], "one_in_R": r["one_in_R"],
                                "delta": r.get("delta"), "rank_pred": r.get("rank_pred")})
            for r in u["refs"]:
                if r["checks"].get(fld) is False:
                    bad.append({"ref": r["label"], "check": fld})
        c12[fam] = {"pass": not bad, "violations": bad[:50], "n_violations": len(bad)}
    ck["C-12_nulls_Lemma_B-S"] = {"pass": all(v["pass"] for v in c12.values()), "per_family": c12,
                                  "consequence": "a mismatch marks that null family's regime-B metrics INVALID pending adjudication and voids DB-8 and M3 for the cell"}
    # regime A controls
    if unitsA:
        bad = []
        for fam in curve_fams:
            for t in P1[fam].get("refs", []) + P1[fam]["targets"]:
                if not t.get("aff_ok", True):
                    bad.append({"family": fam, "idx": t.get("idx"), "issue": "E(r) != affine combination"})
        for t in P1["F-AFF"].get("refs", []) + P1["F-AFF"]["targets"]:
            if not t.get("aff_ok", True):
                bad.append({"family": "F-AFF", "idx": t.get("idx"), "issue": "affine identity (two code paths)"})
        for (fam, D), u in unitsA.items():
            c = u.get("caff_direct")
            if c and c["mismatch_pairs"]:
                bad.append({"family": fam, "D": D, "direct_replay_mismatches": c["mismatches"][:20],
                            "n": c["mismatch_pairs"]})
        ck["C-AFF"] = {"pass": not bad, "violations": bad,
                       "direct_replay_pairs_checked": sum((u.get("caff_direct") or {}).get("checked_pairs", 0) for u in unitsA.values())}
        bad, pairs = [], 0
        for (fam, D), u in unitsA.items():
            c = u.get("caff_direct") or {}
            if c.get("first_zero_mismatch"):
                bad.append({"family": fam, "D": D, "path": "direct replay vs forms", "first": c["first_zero_mismatch"][:10]})
            cf = u.get("cforms_matmul")
            if cf:
                pairs += cf["pairs_checked"]
                if cf["mismatches"]:
                    bad.append({"family": fam, "D": D, "path": "matmul forms vs bitwise forms", "detail": cf["mismatches"]})
        ck["C-FORMS"] = {"pass": not bad, "violations": bad, "pairs_checked_matmul": pairs}
        bad, badh = [], []
        for (fam, D), u in unitsA.items():
            h = u.get("hull")
            if not h:
                continue
            for k, v in h["refs"].items():
                if not v["C-SURV"]["pass"]:
                    bad.append({"family": fam, "D": D, "ref": k, **v["C-SURV"]})
                if not v["C-HZERO"]["pass"]:
                    badh.append({"family": fam, "D": D, "ref": k, "pivots": v["C-HZERO"]["violations"][:20],
                                 "r_ref_in_hull": v.get("r_ref_in_hull"), "dimW": v.get("dimW")})
        ck["C-SURV"] = {"pass": not bad, "violations": bad}
        ck["C-HZERO"] = {"pass": not badh, "violations": badh}
    else:
        for c in ("C-AFF", "C-FORMS", "C-SURV", "C-HZERO"):
            ck[c] = {"pass": None, "note": "regime-A arm void (C-PROV failed; INV-2)"}
    # C-TR
    ck["C-TR"] = {"pass": P1["C-TR"]["pass"], **{k: v for k, v in P1["C-TR"].items() if k != "pass"},
                  "consequence": "recorded as data; the measured hull is used anyway; no invalidation"}
    # C-PASS
    bad = []
    for reg, units in (("A", unitsA), ("B", unitsB)):
        for key, u in units.items():
            for r in u["refs"]:
                if r.get("cpass") is not True:
                    bad.append({"regime": reg, "unit": str(key), "ref": r["label"]})
            for r in u["records"]:
                if r.get("cpass") is not True:
                    bad.append({"regime": reg, "unit": str(key), "idx": r["idx"]})
    for reg, units in (("A", revA), ("B", revB)):
        for key, u in units.items():
            for r in u["records"]:
                if r.get("cpass") is not True:
                    bad.append({"regime": reg, "unit": f"REV {key}", "idx": r["idx"]})
    ck["C-PASS"] = {"pass": not bad, "violations": bad[:50], "n_violations": len(bad)}
    # C-REV
    bad = []
    rev_ret = {}
    for reg, units, rev in (("A", unitsA, revA), ("B", unitsB, revB)):
        for key, ru in rev.items():
            base = units[("F-S3", key)] if reg == "A" else units["F-S3"]
            bm = {r["idx"]: r for r in base["records"]}
            for r in ru["records"]:
                b = bm[r["idx"]]
                for f in ("rank", "pivcols_hash", "one_in_R"):
                    if r[f] != b[f]:
                        bad.append({"regime": reg, "D": key, "idx": r["idx"], "field": f, "reversed": r[f], "original": b[f]})
            brm = {x["label"]: x for x in base["refs"]}
            for x in ru["refs"]:
                b = brm[x["label"]]
                for f in ("rank", "one_in_R"):
                    if x[f] != b[f]:
                        bad.append({"regime": reg, "D": key, "ref": x["label"], "field": f})
            ukeys = [x["label"] for x in ru["refs"] if x["label"].startswith("U")]
            rev_ret[f"{reg}-D{key}"] = {k: {a: retention(ru["records"], k, a) for a in ("unsat", "sat")} for k in ukeys}
    ck["C-REV"] = {"pass": not bad, "violations": bad, "T_strict_retention_under_reversal_DATA": rev_ret}
    # C-PROPS: PS0, PS1 (PS0' added by the caller); PS2/PS3 implied
    bad0, bad1 = [], []
    for reg, units in (("A", unitsA), ("B", unitsB)):
        for key, u in units.items():
            for r in u["records"]:
                if r.get("PS0_fail"):
                    bad0.append({"regime": reg, "unit": str(key), "idx": r["idx"], "fail": r["PS0_fail"]})
                if r.get("PS1_fail"):
                    bad1.append({"regime": reg, "unit": str(key), "idx": r["idx"]})
            for r in u["refs"]:
                c = r.get("checks", {})
                if c.get("PS0_fail"):
                    bad0.append({"regime": reg, "unit": str(key), "ref": r["label"]})
                if c.get("PS1_fail"):
                    bad1.append({"regime": reg, "unit": str(key), "ref": r["label"]})
    ps2 = {}
    for reg, units in (("A", unitsA), ("B", unitsB)):
        for key, u in units.items():
            fam = key[0] if isinstance(key, tuple) else key
            if fam != "F-S3":
                continue
            for r in u["refs"]:
                if r["s"] == 0 and r["one_in_R"]:
                    col = 0
                    for f2 in ("F-S3", "F-SAT", "F-PLANT"):
                        k2 = (f2, key[1]) if isinstance(key, tuple) else f2
                        if k2 not in units:
                            continue
                        rk = r["label"] if f2 == "F-S3" else f"F-S3:{r['label']}"
                        col += sum(1 for t in units[k2]["records"] if t["s"] >= 1 and t["refs"].get(rk, {}).get("match", {}).get("set"))
                    ps2[f"{reg}-{key}-{r['label']}"] = {"sat_instances_with_equal_T_set": col, "pass": col == 0}
    ps3 = sum(1 for u in unitsA.values() for r in u["records"] if r.get("PS3_fail"))
    ck["C-PROPS"] = {"PS0_violations": bad0, "PS1_violations": bad1, "PS0_pass": not bad0, "PS1_pass": not bad1,
                     "PS2_implied": ps2 if ps2 else "VACUOUS (no unsat F-S3 reference has 1 in R_D)",
                     "PS3_implied_violations_regimeA": ps3}
    # nesting
    nv = []
    for reg, units in (("A", unitsA), ("B", unitsB)):
        for key, u in units.items():
            for v in nesting_violations(u["records"]):
                nv.append({"regime": reg, "unit": str(key), **v})
    ck["nesting"] = {"pass": not nv, "violations": nv[:50], "n": len(nv)}
    # hash/content anomalies
    an = []
    for reg, units in (("A", unitsA), ("B", unitsB)):
        for key, u in units.items():
            an += [{"regime": reg, "unit": str(key), **a} for a in u.get("hash_anomalies", [])]
    ck["trace_hash_content_anomalies"] = {"n": len(an), "items": an[:50]}
    return ck


def nulls_check(P1, n, E0, Ej, module_hashes):
    out = {}
    # F-NULLB: nonzero coefficients; 16 equal bins of the integer encoding, exact 99.9% bands
    coeffs = [c for t in P1["F-NULLB"]["refs"] + P1["F-NULLB"]["targets"] for c in t["coeffs"]]
    nz = all(c != 0 for c in coeffs)
    N = len(coeffs)
    width = 1 << (n - 4)
    q1 = (1 << n) - 1
    bins = Counter(c // width for c in coeffs)
    rows = []
    ok = nz
    for b in range(16):
        p = Fraction(width - 1 if b == 0 else width, q1)
        lo, hi = binom_band(N, p) if N <= 3000 else (None, None)
        x = bins.get(b, 0)
        inb = lo is not None and lo <= x <= hi
        ok &= inb
        rows.append({"bin": b, "count": x, "p": str(p), "band999": [lo, hi], "in_band": inb})
    out["F-NULLB"] = {"n_coefficients": N, "all_nonzero": nz, "bins": rows, "pass": ok}
    al = P1["F-AFFB"]["alpha"]
    out["F-AFFB"] = {"alpha": al, "all_nonzero": all(a != 0 for a in al), "pass": all(a != 0 for a in al)}
    return out


def nulls_check_A(P1, desc, E0, Ej):
    from families import E_from_hex
    from statsx import binom_band_mp
    ncols = len(desc.eq_mons)
    A0 = E_from_hex(P1["F-AFF"]["A0_hex"], ncols)
    Aj = [E_from_hex(x, ncols) for x in P1["F-AFF"]["Aj_hex"]]
    contained = bool(np.all(A0 <= E0)) and all(bool(np.all(a <= e)) for a, e in zip(Aj, Ej))
    supp = int(E0.sum() + sum(e.sum() for e in Ej))
    ones = int(A0.sum() + sum(a.sum() for a in Aj))
    lo, hi = binom_band_mp(supp, Fraction(1, 2))
    aff = {"support_contained": contained, "support_positions": supp, "ones": ones, "band999": [lo, hi],
           "in_band": lo <= ones <= hi, "pass": contained and lo <= ones <= hi}
    U = E0.astype(bool).copy()
    for x in Ej:
        U |= x.astype(bool)
    tot = ones2 = 0
    cont = True
    for t in P1["F-NULLF2"]["refs"] + P1["F-NULLF2"]["targets"]:
        E = E_from_hex(t["E_hex"], ncols).astype(bool)
        cont &= bool(np.all(~E | U))
        tot += int(U.sum())
        ones2 += int(E.sum())
    lo2, hi2 = binom_band_mp(tot, Fraction(1, 2))
    nf2 = {"support_contained": cont, "positions_pooled": tot, "ones": ones2, "band999": [lo2, hi2],
           "in_band": lo2 <= ones2 <= hi2, "pass": cont and lo2 <= ones2 <= hi2}
    return {"F-AFF": aff, "F-NULLF2": nf2}


# ---------------------------------------------------------------------------
# decision rules
def db_cell(lab, n, l, cs, ck, e3_field="fraction"):
    """DB-1, DB-2, DB-3, DB-5, DB-6, DB-7, DB-8, DB-9, DB-10, DB-11 for one cell,
    under protocol version 2 (specification v1 + AMD-20260924-3a9f06)."""
    out = {}
    B = cs["regime_B"]
    rf = B["MB1"]["retention_family"]
    inv3 = not (ck["C-ORACLE"]["pass"] and ck["C-WIT"]["pass"])
    inv4 = not (ck["C-DELTA"]["pass"] and ck["C-RANKB"]["pass"])
    inv5 = not (ck["C-BREAK"]["pass"] and ck["C-REPLAYB"]["pass"])
    inv10 = not ck["C-CLASS"]["curve_algebra_pass"]

    def void_tag(*flags):
        names = [nm for nm, f in zip(("INV-3", "INV-4", "INV-5", "INV-10"), (inv3, inv4, inv5, inv10)) if f and nm in flags]
        return names
    # DB-1
    c1 = stab_class(rf)
    v1 = void_tag("INV-3", "INV-4")
    out["DB-1"] = {"cell": lab, "regime": "B", "granularity": "T_strict", "D": 66, "arm": "unsat",
                   "inputs": {"retention_family": rf, "maximizing_ref": B["MB1"]["maximizing_ref"], "min": B["MB1"]["min"]},
                   "verdict": c1 if not v1 else f"VOID/INVALID pending adjudication ({', '.join(v1)}); computed: {c1}",
                   "void": bool(v1),
                   "TS2B_falsified_here_by_DB-1": (rf is not None and rf < 0.9) if not v1 else None}
    # DB-2
    un = B["MB4"]["F-S3"]["unsat"]
    frac = un["fraction"]
    sat_ranks = []
    for fam in ("F-SAT", "F-PLANT"):
        sat_ranks += [int(k) for k in B["MB4"][fam]["sat"]["rank_distribution"].keys()]
    all_sat_below = all(r < 2278 for r in sat_ranks)
    if frac is None:
        v2 = "not evaluable"
    elif frac >= 0.95 and all_sat_below:
        v2 = "DECIDES"
    elif frac <= 0.05:
        v2 = "DOES NOT DECIDE AT THIS D"
    else:
        v2 = "PARTIAL"
    vv2 = void_tag("INV-3", "INV-4")
    out["DB-2"] = {"cell": lab, "regime": "B", "D": 66,
                   "inputs": {"unsat_fraction_one_in_R66": frac, "n_unsat": un["n"],
                              "every_sat_target_rank_below_2278": all_sat_below, "sat_rank_values": sorted(set(sat_ranks))},
                   "verdict": v2 if not vv2 else f"VOID/INVALID pending adjudication ({', '.join(vv2)}); computed: {v2}",
                   "void": bool(vv2)}
    # DB-3
    mb3 = B["MB3"]
    per = mb3["per_ref"]
    inside = sum(1 for d in per.values() if d.get("inside"))
    evaluable = all(d.get("inside") is not None for d in per.values()) and len(per) == 3
    v3 = ("CONSISTENT" if inside >= 2 else "FALSIFIED") if evaluable else "not evaluable (missing K_B or reference shortfall)"
    vv3 = void_tag("INV-3", "INV-4", "INV-5", "INV-10")
    out["DB-3"] = {"cell": lab, "regime": "B", "D": 66,
                   "inputs": {k: {"X": d["X"], "K_B": d["K_B"],
                                  "interval": [d["poisson999"]["lo"], d["poisson999"]["hi"]] if d["poisson999"] else None,
                                  "mu": d["poisson999"]["mu"] if d["poisson999"] else None,
                                  "inside": d["inside"], "row_order_rate": d["row_order_rate"]} for k, d in per.items()},
                   "refs_inside": inside,
                   "reference_non_generic": {k: d["reference_non_generic"] for k, d in per.items()},
                   "verdict": v3 if not vv3 else f"VOID ({', '.join(vv3)}); computed: {v3}", "void": bool(vv3)}
    # DB-5
    mb5 = B["MB5"]
    underpowered = False
    f5 = {}
    if not mb5["evaluable"]:
        v5 = "NOT EVALUABLE"
    else:
        f5 = {k: d["pooled"].get(e3_field) for k, d in mb5["per_ref"].items()}
        ns = {k: d["pooled"]["n"] for k, d in mb5["per_ref"].items()}
        underpowered = any(v < 100 for v in ns.values()) if ns else True
        if not f5 or any(v is None for v in f5.values()):
            v5 = "not evaluable (no satisfiable targets)"
        elif all(v >= 0.95 for v in f5.values()):
            v5 = "E3 HOLDS"
        else:
            v5 = "E3 FALSIFIED"
        if underpowered:
            v5 = f"UNDERPOWERED (E3 arm < 100); value reading: {v5}"
    vv5 = void_tag("INV-3", "INV-4", "INV-10")
    out["DB-5"] = {"cell": lab, "regime": "B", "D": 66,
                   "inputs": {"E3_fraction_per_unsat_ref": f5, "field": e3_field,
                              "E3_arm_n": {k: d["pooled"]["n"] for k, d in mb5["per_ref"].items()}},
                   "underpowered": underpowered,
                   "verdict": v5 if not vv5 else f"VOID ({', '.join(vv5)}); computed: {v5}", "void": bool(vv5)}
    # DB-6
    A = cs.get("regime_A")
    ra = A["D4"]["MA1"]["strict_unsat"]["retention_family"] if A else None
    if ra is None or rf is None:
        v6 = "not evaluable"
    elif ra < 0.5 and rf >= 0.9:
        v6 = "CONTRAST CONFIRMED"
    elif ra < 0.5 and rf < 0.5:
        v6 = "BOTH UNSTABLE"
    elif ra >= 0.9 and rf >= 0.9:
        v6 = "BOTH STABLE"
    else:
        v6 = "PARTIAL"
    vv6 = void_tag("INV-3", "INV-4")
    out["DB-6"] = {"cell": lab, "inputs": {"regime_A_retention_family_D4_T_strict": ra, "regime_B_retention_family": rf},
                   "verdict": v6 if not vv6 else f"VOID/INVALID ({', '.join(vv6)}); computed: {v6}", "void": bool(vv6)}
    # DB-7 (AMD C-9 (iii)-(iv): a void or underpowered conjunct is never a failing conjunct)
    reasons = []
    if out["DB-1"]["void"]:
        reasons.append("DB-1 void")
    if out["DB-2"]["void"]:
        reasons.append("DB-2 void")
    if out["DB-5"]["void"]:
        reasons.append("DB-5 void")
    if l == 5 and underpowered and not out["DB-5"]["void"]:
        reasons.append("E3 arm underpowered")
    if reasons:
        v7 = "NOT EVALUABLE (" + "; ".join(reasons) + ")"
        fails = []
    else:
        fails = []
        if v2 != "DECIDES":
            fails.append(f"DB-2 = {v2}")
        if c1 != "STABLE":
            fails.append(f"DB-1 = {c1}")
        if v5 != "E3 HOLDS":
            fails.append(f"DB-5 = {v5}")
        v7 = "P-GPU (STRICT REPLAY) SURVIVES IN REGIME B AT THIS CELL" if not fails else "P-GPU NOT SUPPORTED AT THIS CELL"
    out["DB-7"] = {"cell": lab, "failing_conjuncts": fails, "verdict": v7,
                   "note": "A survival verdict is still dominated per attempt by oracle A and carries sota_delta zero." +
                           (" At l = 6, D = 66 a STABLE regime-B verdict is not a P-GPU result (Lemma B-S (d))." if l == 6 else "")}
    # DB-8
    fam_rf = {"F-S3": rf, "F-NULLB": B["nulls"]["F-NULLB"]["retention_family"], "F-AFFB": B["nulls"]["F-AFFB"]["retention_family"]}
    cl = {k: stab_class(v) for k, v in fam_rf.items()}
    if any(v is None for v in fam_rf.values()):
        v8 = "not evaluable"
    elif all(c == "STABLE" for c in cl.values()):
        v8 = "GENERIC STABILITY"
    elif fam_rf["F-S3"] < 0.9 and fam_rf["F-NULLB"] >= 0.9 and fam_rf["F-AFFB"] >= 0.9:
        v8 = "S_3-SPECIFIC INSTABILITY"
    elif fam_rf["F-S3"] >= 0.9 and fam_rf["F-NULLB"] < 0.9 and fam_rf["F-AFFB"] < 0.9:
        v8 = "S_3-SPECIFIC STABILITY"
    else:
        v8 = "MIXED"
    null_void = []
    if not ck["C-NULLS"]["pass"]:
        null_void.append("C-NULLS")
    if not ck["C-12_nulls_Lemma_B-S"]["pass"]:
        null_void.append("C-12 (null Lemma B-S mismatch: INVALID pending adjudication)")
    if not all(ck["C-CLASS"]["nulls_pass"].values()):
        null_void.append("INV-10 (null C-CLASS)")
    out["DB-8"] = {"cell": lab, "inputs": fam_rf, "classes": cl, "M3": B["M3"] if not null_void else {"VOID": null_void, "computed": B["M3"]},
                   "verdict": v8 if not null_void else f"VOID ({'; '.join(null_void)}); computed: {v8}"}
    # DB-9
    d9 = {}
    for reg, blk in (("B", B), ("A", A["D4"] if A else None)):
        if blk is None:
            continue
        sz = blk["sizing_maximizing_ref"]
        if sz is None:
            d9[reg] = {"verdict": "not evaluable"}
            continue
        pb = sz["pruned_dense_bytes"]
        d9[reg] = {"maximizing_ref": sz["ref"], "pruned_dense_bytes": pb, "saving_strict": sz["saving_strict"],
                   "one_system_per_SM": "SURVIVES" if pb <= 233472 else "FAILS",
                   "thousands_per_warp": "FAILS" if pb > 32 else "SURVIVES",
                   "strict_replay_closed_(saving_strict<1.5)": (sz["saving_strict"] is not None and sz["saving_strict"] < 1.5),
                   "D": 66 if reg == "B" else 4}
    out["DB-9"] = {"cell": lab, "per_regime": d9}
    # DB-10
    if A:
        hull = A["D4"]["MA1"]["hull"]
        full = all(v["K_rank_hull"] == v["dimW"] for v in hull.values()) if hull else None
        ts = A["D4"]["MA2_TS1R"].get("F-S3")
        pc3 = A["D4"]["MA1"]["strict_unsat"]["retention_family"]
        a_void = not all(ck[c]["pass"] for c in ("C-AFF", "C-FORMS", "C-SURV", "C-HZERO"))
        out["DB-10"] = {"cell": lab, "regime": "A", "D": 4,
                        "KR1_RR2": ("HULL RANK FULL" if full else ("REVISIT TRIGGER FIRES" if full is False else "not evaluable")),
                        "KR1_inputs": {k: [v["K_rank_hull"], v["dimW"], v["dim_Sigma_H"]] for k, v in hull.items()},
                        "TS1R_RR4": ts["verdict_RR4"] if ts else "not evaluable",
                        "TS1R_inputs": {"m": ts["m"], "o": ts["o"], "P": ts["P_Bin_m_0.001_ge_o"]} if ts else None,
                        "P-C3": ("HOLDS" if pc3 < 0.5 else "FAILS") if pc3 is not None else "not evaluable",
                        "P-C3_input": pc3,
                        "INV-6_affected_family_void": a_void,
                        "INV-6_note": "a C-AFF/C-FORMS/C-SURV/C-HZERO failure voids MA1 hull quantities and MA2 for the AFFECTED family (see instrument-checks)"}
    else:
        out["DB-10"] = {"cell": lab, "verdict": "VOID (regime-A arm void, INV-2)"}
    # DB-11
    r1 = mb3.get("pooled_rate_CP95")
    r2 = mb3["F-RANDX"].get("pooled_rate_CP95")
    if r1 is None or r2 is None:
        v11 = "not evaluable"
    else:
        v11 = "INDEPENDENT" if (r1[0] <= r2[1] and r2[0] <= r1[1]) else "DEPENDENT"
    vv11 = void_tag("INV-3", "INV-4", "INV-5", "INV-10")
    out["DB-11"] = {"cell": lab, "inputs": {"F-S3_pooled_rate": mb3["pooled_rate"], "F-S3_CP95": r1,
                                            "F-RANDX_pooled_rate": mb3["F-RANDX"]["pooled_rate"], "F-RANDX_CP95": r2},
                    "verdict": v11 if not vv11 else f"VOID ({', '.join(vv11)}); computed: {v11}"}
    return out


def db4(cells_summary, ck_all):
    out = {}
    for l in (6, 5):
        a, b = f"n17-l{l}", f"n19-l{l}"
        if a not in cells_summary or b not in cells_summary:
            out[f"l{l}"] = {"verdict": "not evaluable (cell missing)"}
            continue
        m17 = cells_summary[a]["regime_B"]["MB3"]
        m19 = cells_summary[b]["regime_B"]["MB3"]
        iv = poisson_ratio_interval(m19["pooled_distinct_breaking_targets"], m19["N_unsat"],
                                    m17["pooled_distinct_breaking_targets"], m17["N_unsat"])
        if iv["hi"] < 1:
            v = "DECAYS"
        elif iv["lo"] >= 1:
            v = "NON-DECAYING (artifact tell)"
        else:
            v = "UNRESOLVED"
        def kbs(m):
            v = [d["K_B"] for d in m["per_ref"].values()]
            return None if (not v or any(x is None for x in v)) else sum(v)
        k17, k19 = kbs(m17), kbs(m19)
        pred = (k19 / k17 / 4) if (k17 and k19 is not None) else None
        void = any(not (ck_all[c]["C-BREAK"]["pass"] and ck_all[c]["C-REPLAYB"]["pass"]
                        and ck_all[c]["C-CLASS"]["curve_algebra_pass"] and ck_all[c]["C-DELTA"]["pass"]
                        and ck_all[c]["C-RANKB"]["pass"] and ck_all[c]["C-ORACLE"]["pass"] and ck_all[c]["C-WIT"]["pass"])
                   for c in (a, b))
        out[f"l{l}"] = {"inputs": {"x19": m19["pooled_distinct_breaking_targets"], "N19": m19["N_unsat"],
                                   "x17": m17["pooled_distinct_breaking_targets"], "N17": m17["N_unsat"],
                                   "K_B_sum_19": k19, "K_B_sum_17": k17,
                                   "K_B_definition": "sum over the cell's unsat references (AMD C-7); None if any is not estimable"},
                        "ratio_interval_95": iv, "predicted_(K_B19/K_B17)/4": pred,
                        "consistent_with_prediction": ((iv["lo"] <= pred <= iv["hi"]) if pred is not None else "not evaluable (K_B not estimable)"),
                        "verdict": v if not void else f"VOID (INV-5 at a contributing cell); computed: {v}"}
    return out


DB12 = {"primary": ["DB-1, DB-2, DB-5, DB-6, DB-7 at (17, 6) and (17, 5)", "DB-3 at every cell", "DB-4 per l"],
        "secondary": ["every n = 19 verdict other than DB-3/DB-4", "every T_set, T_rank, T_ops, D = 3, null or cross-family reading"]}
