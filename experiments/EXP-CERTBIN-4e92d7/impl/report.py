"""Phase 8 writer: every declared artifact of the run package.

raw-result.json is recomputed from the written targets-*.jsonl.gz and
pivot-hazards.json files by code separate from analysis.py, and compared with
cell-summary.json on every primary metric.
"""
import datetime
import gzip
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from collections import Counter

import numpy as np
import yaml

import analysis
from analysis import FAMS, GRANS, DS

SCOPE_STATEMENT = None  # filled from the specification text at run time


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write_new(path, text, mode="w"):
    if os.path.exists(path):
        raise RuntimeError(f"{path} exists; refusing to overwrite")
    tmp = path + ".tmp"
    with open(tmp, mode) as f:
        f.write(text)
    os.replace(tmp, path)


def jdump(obj):
    return json.dumps(obj, indent=1, default=_jd)


def _jd(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


# ---------------------------------------------------------------------------
def independent_primary(out_dir):
    """Re-derive the primary metrics from the written per-target files."""
    res = {}
    for fam in FAMS:
        recs = []
        with gzip.open(os.path.join(out_dir, f"targets-{fam}.jsonl.gz"), "rt") as f:
            for line in f:
                recs.append(json.loads(line))
        res[fam] = {}
        for D in DS:
            rd = [r for r in recs if r["D"] == D and r["stratum"] != "degenerate"]
            keys = set()
            for r in rd:
                keys |= set(r["refs"])
            m1 = {}
            for g in GRANS:
                m1[g] = {}
                for k in sorted(keys):
                    sub = [r for r in rd if r["stratum"] == "unsat" and k in r["refs"]]
                    m1[g][k] = [sum(1 for r in sub if r["refs"][k]["match"][g]), len(sub)]
            ent = {}
            for g in GRANS:
                c = Counter(r["h_" + g] for r in rd)
                n = sum(c.values())
                ent[g] = -sum(v / n * math.log2(v / n) for v in c.values()) if n else None
            res[fam][f"D{D}"] = {"unsat_retention_counts": m1, "entropy_bits": ent,
                                 "arm_sizes": {"unsat": sum(r["stratum"] == "unsat" for r in rd),
                                               "sat": sum(r["stratum"] == "sat" for r in rd)}}
    hz = json.load(open(os.path.join(out_dir, "pivot-hazards.json")))
    t = hz["families"]["F-S3"]["D4"]
    hs = []
    for k in ("U1", "U2", "U3", "S1", "S2"):
        if k not in t or t[k] is None:
            continue
        for dep, S, z in zip(t[k]["sampled_dependent"], t[k]["S_k"], t[k]["zeros_k"]):
            if dep and S >= 200:
                hs.append(z / S)
    hs.sort()
    n = len(hs)
    med = (hs[n // 2] if n % 2 else (hs[n // 2 - 1] + hs[n // 2]) / 2) if n else None
    res["M2_F-S3_D4"] = {"n": n, "median_h": med, "frac_in_band": (sum(1 for h in hs if 0.4 <= h <= 0.6) / n) if n else None}
    return res


def agreement(cell, indep):
    diffs = []
    checked = 0
    for fam in FAMS:
        for D in DS:
            c = cell["families"][fam][f"D{D}"]
            i = indep[fam][f"D{D}"]
            if c["arm_sizes"] != i["arm_sizes"]:
                diffs.append({"family": fam, "D": D, "metric": "arm_sizes"})
            checked += 1
            for g in GRANS:
                for k, v in c["retention"][g].items():
                    checked += 1
                    iv = i["unsat_retention_counts"][g].get(k, [0, 0])
                    if [v["unsat"]["x"], v["unsat"]["n"]] != iv:
                        diffs.append({"family": fam, "D": D, "g": g, "ref": k, "cell": [v["unsat"]["x"], v["unsat"]["n"]], "raw": iv})
                checked += 1
                a, b = c["M4_entropy"][g]["H_bits"], i["entropy_bits"][g]
                if not ((a is None and b is None) or (a is not None and b is not None and abs(a - b) < 1e-9)):
                    diffs.append({"family": fam, "D": D, "g": g, "metric": "H_bits", "cell": a, "raw": b})
    m2c = cell["M2"]
    m2i = indep["M2_F-S3_D4"]
    checked += 1
    if m2c.get("n", 0) != m2i["n"] or (m2i["n"] and (abs(m2c["median_h"] - m2i["median_h"]) > 1e-9 or abs(m2c["frac_in_[0.4,0.6]"] - m2i["frac_in_band"]) > 1e-9)):
        diffs.append({"metric": "M2", "cell": {k: m2c.get(k) for k in ("n", "median_h", "frac_in_[0.4,0.6]")}, "raw": m2i})
    # M3 numerator / denominators from raw counts
    def rf_raw(fam):
        cnts = indep[fam]["D4"]["unsat_retention_counts"]["strict"]
        keys = analysis.m1_keys(fam, {"refs": [{"label": k} for k in cnts]}) if fam != "F-PLANT" else []
        vals = [(cnts[k][0] / cnts[k][1]) for k in keys if k in cnts and cnts[k][1]]
        return max(vals) if vals else None
    checked += 1
    if cell["M3"]["numerator"]["retention_family"] != rf_raw("F-S3"):
        diffs.append({"metric": "M3 numerator", "cell": cell["M3"]["numerator"]["retention_family"], "raw": rf_raw("F-S3")})
    for d, den in zip((1, 2, 3), cell["M3"]["denominators"]):
        checked += 1
        if den["retention_family"] != rf_raw(f"F-AFF-{d}"):
            diffs.append({"metric": f"M3 denominator F-AFF-{d}", "cell": den["retention_family"], "raw": rf_raw(f"F-AFF-{d}")})
    return {"checked_items": checked, "disagreements": diffs, "agree": not diffs}


# ---------------------------------------------------------------------------
def fmt(x, nd=4):
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return f"{x:.{nd}g}"
    return str(x)


def predictions_table(cell, checks, dr, sizing):
    c4 = cell["families"]["F-S3"]["D4"]
    fr = c4["retention_family_unsat"]["strict"]
    rows = []
    rfv = fr["retention_family"]
    if rfv is None:
        p1 = ("not evaluable", "no unsatisfiable-arm retention")
    elif rfv <= 0.01:
        p1 = ("E1 band held (<= 0.01)", f"retention_family = {fmt(rfv)} ({fr['count']}/{fr['n']}, ref {fr['maximizing_reference']})")
    elif rfv >= 0.5:
        p1 = ("E2 band held (>= 0.5)", f"retention_family = {fmt(rfv)}")
    else:
        p1 = ("between the E1 and E2 bands", f"retention_family = {fmt(rfv)}")
    rows.append(("P1", "T_strict retention, unsat arm, F-S3, D = 4", *p1))
    m2 = cell["M2"]
    if not m2.get("evaluable"):
        rows.append(("P2", "per-pivot hazard (P2 set)", "not evaluable", "P2 set empty"))
    else:
        held = "failed (median < 0.2)" if m2["median_h"] < 0.2 else ("held (>= 90% in [0.4, 0.6])" if m2["frac_in_[0.4,0.6]"] >= 0.9 else "neither (median >= 0.2, < 90% in band)")
        rows.append(("P2", "per-pivot hazard (P2 set)", held,
                     f"n = {m2['n']}, median h = {fmt(m2['median_h'])}, fraction in band = {fmt(m2['frac_in_[0.4,0.6]'])}"))
    ks = {k: v["K_sampled"] for k, v in c4["K_and_replay"].items() if k in ("U1", "U2", "U3", "S1", "S2", "modal")}
    kr = {k: v["K_over_rank"] for k, v in c4["K_and_replay"].items() if k in ks}
    rows.append(("P3", "K / rank per reference (no directional prediction; E2 needs K <= 1)",
                 "E2 condition K <= 1 " + ("met by some reference" if any(v <= 1 for v in ks.values()) else "not met by any reference"),
                 "K = " + ", ".join(f"{k}:{v}" for k, v in ks.items()) + "; K/rank = " + ", ".join(f"{k}:{fmt(v, 3)}" for k, v in kr.items())))
    ps2 = checks["C-PROPS"]["PS2"]
    vac = {k: v for k, v in checks["PS2_vacuous"].items() if k.startswith("F-S3/")}
    rows.append(("P4", "Prop. S T_set matches (sat vs unsat ref with 1 in R_D)",
                 "held (0 matches)" if ps2["failed"] == 0 else f"FAILED ({ps2['failed']} matches; instrument)",
                 "F-S3 PS2 vacuous at: " + (", ".join(k for k, v in vac.items() if v) or "none")))
    fd = c4["f_div"]
    meds = {k: (fd[k]["unsat"]["median_f_div"], fd[k]["sat"]["median_f_div"]) for k in fd}
    e1ok = all((u is None or u <= 0.1) and (s is None or s <= 0.1) for u, s in meds.values())
    rows.append(("P5", "median f_div per arm (E1: <= 0.1 both arms, no arm difference)",
                 "E1 condition on medians " + ("held" if e1ok else "failed"),
                 "; ".join(f"{k}: unsat {fmt(u, 3)}, sat {fmt(s, 3)}, MW p = {fmt((fd[k]['mann_whitney_unsat_vs_sat'] or {}).get('p_value'), 3)}" for k, (u, s) in meds.items())))
    m3 = cell["M3"]
    if m3["kind"] == "not_estimable":
        p6 = "not estimable (E1 [0.5, 2] clause not evaluable)"
    elif m3["kind"] == "zero":
        p6 = "ratio 0 (E2 >= 10x not met; outside E1 [0.5, 2])"
    elif m3["kind"] == "lower_bound":
        p6 = f"lower bound {fmt(m3['value'])}" + (" (>= 10: E2 condition met)" if m3["value"] >= 10 else "")
    else:
        v = m3["value"]
        p6 = f"{fmt(v)}" + (" (>= 10: E2 condition)" if v >= 10 else (" (in E1 band [0.5, 2])" if 0.5 <= v <= 2 else " (outside both bands)"))
    rows.append(("P6", "retention ratio F-S3 / F-AFF (M3, D = 4, T_strict)", p6, json.dumps({k: m3.get(k) for k in ("kind", "value")})))
    m4 = c4["M4_entropy"]
    hst = m4["strict"]["H_bits"]
    rows.append(("P7", "H(T_strict), D = 4 (E1 >= 8.97; P-GPU needs <= h(P_sat) + 0.1)",
                 ("E1 threshold met" if hst is not None and hst >= 8.97 else "E1 threshold not met") + "; " +
                 ("P-GPU entropy condition met" if hst is not None and hst <= m4["h_P_sat"] + 0.1 else "P-GPU entropy condition not met"),
                 f"H = {fmt(hst)} bits, distinct = {m4['strict']['distinct']}, N = {m4['strict']['N']}, h(P_sat) = {fmt(m4['h_P_sat'])}"))
    sv = sizing["per_reference"]["F-S3"]["D4"]
    sst = {k: v["saving"]["saving_strict"] for k, v in sv.items()}
    sse = {k: v["saving"]["saving_set"] for k, v in sv.items()}
    le10 = all(x is not None and x <= 10 for x in list(sst.values()) + list(sse.values()))
    rows.append(("P8", "saving ratio (<= 10 predicted; < 1.5 closes)",
                 ("held (all <= 10)" if le10 else "failed (some > 10)") + "; DR-7: strict " + dr["DR-7"].get("strict_replay", "n/a") + ", T_set " + dr["DR-7"].get("T_set_replay", "n/a"),
                 "saving_strict " + ", ".join(f"{k}:{fmt(v, 4)}" for k, v in sst.items()) + "; saving_set " + ", ".join(f"{k}:{fmt(v, 4)}" for k, v in sse.items())))
    full_ok = [k for k, v in sv.items() if v["sizes"]["full"]["dense_bytes"] <= 233472]
    rows.append(("P9", "pruned D = 4 sizes vs 32 B / 228 KB (predicted: no full dense D = 4 matrix meets either)",
                 ("full dense prediction held" if not full_ok else "full dense prediction failed") + "; DR-6: one-per-SM " + dr["DR-6"].get("one_system_per_SM", "n/a") + ", thousands-per-warp " + dr["DR-6"].get("thousands_per_warp", "n/a"),
                 "pruned dense bytes " + ", ".join(f"{k}:{fmt(v['sizes']['pruned']['dense_bytes'], 7)}" for k, v in sv.items())))
    return rows


def prior_table(cell, checks, dr, sizing):
    c4 = cell["families"]["F-S3"]["D4"]
    rows = []
    fr = c4["retention_family_unsat"]["strict"]
    per = fr["per_reference"]
    vals = [v["value"] for v in per.values()]
    H = c4["M4_entropy"]["strict"]["H_bits"]
    if any(v is not None and v > 0.01 for v in vals) or (H is not None and H < 8.97):
        a_st = "OVERTURNED"
    elif any(v is None for v in vals) or H is None:
        a_st = "not evaluable for some reference (empty arm)"
    else:
        a_st = "not overturned"
    rows.append(("(a)", "M1 <= 0.01 for every reference at D = 4 and H(T_strict) >= 8.97",
                 a_st,
                 "M1: " + ", ".join(f"{k}={fmt(v['value'])}" for k, v in per.items()) + f"; H = {fmt(H)}"))
    kk = {k: (v["K_sampled"], v["K_rank"]) for k, v in c4["K_and_replay"].items() if k in ("U1", "U2", "U3", "S1", "S2", "modal")}
    b_ok = all(kr is not None and kr <= 17 and ks > kr for ks, kr in kk.values())
    rows.append(("(b)", "K_rank <= 17 and K >> K_rank at D = 4",
                 "not overturned" if b_ok else "OVERTURNED (at least one reference has K <= K_rank)",
                 ", ".join(f"{k}: K={a}, K_rank={b}" for k, (a, b) in kk.items())))
    m2 = cell["M2"]
    if m2.get("evaluable"):
        c_txt = f"median h = {fmt(m2['median_h'])}, fraction in band = {fmt(m2['frac_in_[0.4,0.6]'])}, set size {m2['n']}"
        near = 0.4 <= m2["median_h"] <= 0.6
        c_st = "not overturned" if near else "OVERTURNED (median outside the contract's [0.4, 0.6] hazard band)"
    else:
        c_txt = "P2 set empty"
        c_st = "not evaluable"
    rows.append(("(c)", "P2 set small; medians near 0.5; the 90%-in-band clause could fail", c_st, c_txt))
    rr = c4["retention"]["rank"]
    rank_hi = {k: (rr[k]["unsat"]["value"], rr[k]["sat"]["value"]) for k in rr}
    rset = c4["retention_family_unsat"]["set"]["retention_family"]
    rstr = fr["retention_family"]
    rrank = c4["retention_family_unsat"]["rank"]["retention_family"]
    d1 = all((u is None or u >= 0.9) and (s is None or s >= 0.9) for u, s in rank_hi.values())
    d2 = (rset is not None and rstr is not None and rrank is not None and rstr <= rset <= rrank)
    rows.append(("(d)", "T_rank retention within an arm >= 0.9, and T_set between T_rank and T_strict",
                 "not overturned" if (d1 and d2) else "OVERTURNED" + (" (T_rank < 0.9 for some reference/arm)" if not d1 else "") + (" (T_set not between)" if not d2 else ""),
                 "T_rank retention (unsat, sat): " + ", ".join(f"{k}=({fmt(u, 3)}, {fmt(s, 3)})" for k, (u, s) in rank_hi.items()) +
                 f"; family max unsat: T_rank {fmt(rrank)}, T_set {fmt(rset)}, T_strict {fmt(rstr)}"))
    ds = cell["families"]["F-S3"]["D_star_distribution"]["unsat"]
    nun = sum(ds.values())
    notr = ds.get("not reached at D <= 4", 0)
    vac4 = checks["PS2_vacuous"].get("F-S3/D4")
    e_ok = nun > 0 and notr / nun > 0.5
    rows.append(("(e)", "most unsat instances do NOT reach 1 in R_4; PS2 possibly vacuous; D* mostly not reached",
                 "not overturned" if e_ok else "OVERTURNED",
                 f"unsat arm D* distribution {dict(ds)}; PS2 vacuous at D = 4: {vac4}; 1-in-R_4 rate unsat = {fmt(c4['one_in_R_rate']['unsat'])}"))
    sv = sizing["per_reference"]["F-S3"]["D4"]
    sse = {k: v["saving"]["saving_set"] for k, v in sv.items()}
    sst = {k: v["saving"]["saving_strict"] for k, v in sv.items()}
    f1 = all(x is not None and x >= 1.38 for x in sse.values())
    f2 = all(x is not None and 2 <= x <= 10 for x in sst.values())
    f3 = all(x is not None and x >= 1.5 for x in sse.values())
    rows.append(("(f)", "saving_set >= 1.38 (identity) and just above the 1.5 closure threshold at D = 4; saving_strict between 2 and 10",
                 "not overturned" if (f1 and f2 and f3) else "OVERTURNED" + ("" if f1 else " (saving_set < 1.38)") + ("" if f3 else " (saving_set < 1.5 for some reference)") + ("" if f2 else " (saving_strict outside [2, 10])"),
                 "saving_set " + ", ".join(f"{k}:{fmt(v, 4)}" for k, v in sse.items()) + "; saving_strict " + ", ".join(f"{k}:{fmt(v, 4)}" for k, v in sst.items()) +
                 "; how close counts as 'just above' is not operationalised here: the values are reported for the reviewer"))
    m3 = cell["M3"]
    g_ok = m3["kind"] == "not_estimable" or (m3["kind"] == "point" and 0.5 <= m3["value"] <= 2)
    rows.append(("(g)", "M3 not estimable or in [0.5, 2]", "not overturned" if g_ok else "OVERTURNED",
                 json.dumps({k: m3.get(k) for k in ("kind", "value")})))
    return rows


def run_report(spec, cell, checks, dr, sizing, agree, manifest_status):
    sc = spec["experiment"]["claim_tier_and_scope"]
    L = []
    L.append("# Run report: RUN-CERTBIN-3b7e05 (EXP-CERTBIN-4e92d7, specification version 1)\n")
    L.append("Generated mechanically by phase 8 of `experiments/EXP-CERTBIN-4e92d7/impl/driver.py`. "
             "Every line below is an observation or the mechanical application of a frozen rule. "
             "It declares no hypothesis or heuristic supported, refuted, or closed. That judgement belongs to "
             "the Reviewer and the Coordinator.\n")
    L.append(f"**Run validity status:** `{manifest_status}`.\n")
    inv = checks["invalidation"]
    L.append(f"Invalidation rules triggered: {', '.join(k for k, v in inv['triggered'].items() if v) or 'none'}. "
             f"Voided metrics: {'; '.join(inv['voided_metrics']) or 'none'}.\n")
    L.append("## Claim tier and scope (verbatim from the specification)\n")
    L.append(f"- claim_tier: **{sc['claim_tier']}**")
    L.append(f"- statement: {sc['statement']}")
    L.append(f"- sota_delta: {sc['sota_delta']}")
    L.append(f"- dominated_by: {sc['dominated_by']}")
    L.append(f"- certificate_kind: {sc['certificate_kind']}")
    L.append(f"- affected_vs_safe: {sc['affected_vs_safe']}\n")
    L.append("Tested parameters: n = 17 (F_2[t]/(t^17 + t^3 + 1)), m = 2, l = 9 (V = {deg < 9}), D in {3, 4}, one random "
             "ordinary curve (curve.json), the declared row order, degrevlex column order (constant last), and pivot rule. "
             "No transfer beyond this cell is claimed. Any statement about n = 131 would be extrapolation resting on the "
             "untested HEUR-CERTBIN-TS3.\n")
    L.append("## Arm sizes (non-degenerate test targets) and UNDERPOWERED flags (SR-3)\n")
    L.append("| family | D | unsat | sat | degenerate | underpowered |")
    L.append("|---|---|---|---|---|---|")
    for fam in FAMS:
        for D in DS:
            c = cell["families"][fam][f"D{D}"]
            up = [a for a, v in c["underpowered"].items() if v]
            L.append(f"| {fam} | {D} | {c['arm_sizes']['unsat']} | {c['arm_sizes']['sat']} | {c['N_degenerate']} | {', '.join('UNDERPOWERED ' + a for a in up) or 'no'} |")
    L.append("")
    L.append("## Primary cell: M1-M5 at D = 4 (F-S3 and null counterparts)\n")
    L.append("| family | retention_family T_strict (count/n, ref) | T_set | T_rank | H(T_strict) bits (distinct/N) | h(P_sat) |")
    L.append("|---|---|---|---|---|---|")
    for fam in FAMS:
        c = cell["families"][fam]["D4"]
        f = c["retention_family_unsat"]
        s = f["strict"]
        m4 = c["M4_entropy"]
        L.append(f"| {fam} | {fmt(s['retention_family'])} ({s['count']}/{s['n']}, {s['maximizing_reference']}) | "
                 f"{fmt(f['set']['retention_family'])} | {fmt(f['rank']['retention_family'])} | "
                 f"{fmt(m4['strict']['H_bits'])} ({m4['strict']['distinct']}/{m4['strict']['N']}) | {fmt(m4['h_P_sat'])} |")
    L.append("")
    m2 = cell["M2"]
    L.append(f"M2 (P2 set, F-S3, D = 4, 5 declared references): {json.dumps({k: m2.get(k) for k in ('n', 'evaluable', 'median_h', 'frac_in_[0.4,0.6]', 'min_h', 'max_h')})}\n")
    L.append(f"M3 (D = 4, T_strict): {json.dumps({k: cell['M3'].get(k) for k in ('kind', 'value', 'bootstrap95', 'per_draw_ratios')})}\n")
    L.append("M5 (instrument checks): " + ", ".join(f"{k}: {'pass' if v['pass'] else 'FAIL'}" for k, v in checks["M5_summary"].items()) + "\n")
    L.append("## Decision rules (mechanical; each names its granularity and D)\n")
    for k in ("DR-1", "DR-2", "DR-3", "DR-4", "DR-5"):
        d = dr[k]
        v = d.get("verdict", d.get("reading"))
        L.append(f"- **{k}** [{d.get('granularity')}, D = {d.get('D')}]: {v}" + (f" ({d['reason']})" if d.get("reason") else ""))
    d6 = dr["DR-6"]
    L.append(f"- **DR-6** [{d6.get('granularity')}, D = 4]: one system per SM {d6.get('one_system_per_SM', d6.get('verdict'))}; "
             f"thousands per warp {d6.get('thousands_per_warp', 'n/a')} (pruned dense bytes of maximizing reference = {fmt(d6.get('inputs', {}).get('pruned_dense_bytes'), 7)})")
    d7 = dr["DR-7"]
    L.append(f"- **DR-7** [{d7.get('granularity')}, D = 4]: strict replay {d7.get('strict_replay', d7.get('verdict'))}; T_set replay {d7.get('T_set_replay', 'n/a')}")
    L.append(f"- **DR-8**: primary cell {dr['DR-8']['primary_cell']}. Every D = 3 and every T_set/T_rank/T_ops reading is SECONDARY.")
    L.append(f"\nMaximizing-reference rule used: {dr['maximizing_reference_rule']}.\n")
    L.append("## Predictions P1-P9 (frozen thresholds, mechanical comparison)\n")
    L.append("| id | quantity | outcome | values |")
    L.append("|---|---|---|---|")
    for r in predictions_table(cell, checks, dr, sizing):
        L.append("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
    L.append("")
    L.append("## Proposition S: PS2 vacuity\n")
    for k, v in checks["PS2_vacuous"].items():
        L.append(f"- {k}: {'VACUOUS' if v else 'not vacuous'}")
    L.append("")
    L.append("## Coordinator prior (a)-(g) against the data\n")
    L.append("The prior is qualitative in places. The operational readings used are: (a) as written; (b) 'K >> K_rank' read as "
             "K > K_rank for every reference; (c) 'medians near 0.5' read as the median inside the contract's [0.4, 0.6] hazard band; "
             "(d) as written, over every reference and both arms for T_rank, and the family maxima for the T_set ordering; "
             "(e) 'most' read as more than half of the non-degenerate unsatisfiable arm with D* not reached; (f) saving_set >= 1.5 "
             "and saving_strict in [2, 10], with closeness to 1.5 left to the reviewer; (g) as written. The values are "
             "given so a reviewer can apply a different reading.\n")
    L.append("| part | prior statement (paraphrase) | status | observed |")
    L.append("|---|---|---|---|")
    for r in prior_table(cell, checks, dr, sizing):
        L.append("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
    L.append("")
    L.append("## Raw-result and cell-summary agreement\n")
    L.append(f"raw-result.json was recomputed from the written targets-*.jsonl.gz and pivot-hazards.json files and compared "
             f"with cell-summary.json on {agree['checked_items']} primary-metric items: "
             f"{'all agree' if agree['agree'] else str(len(agree['disagreements'])) + ' DISAGREEMENTS (see raw-result.json)'}.\n")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
def phase8(run, plan, spec, spec_text, ctx):
    import shutil
    final = run.out
    out = os.path.join(run.ck, "p8-staging")
    if os.path.exists(out):
        shutil.rmtree(out)  # transient staging from an interrupted phase 8
    os.makedirs(out)
    U = {}
    for (ph, fam) in ((2, "F-S3"), (2, "F-PLANT"), (3, "F-RANDX"), (4, "F-AFF-1"), (4, "F-AFF-2"), (4, "F-AFF-3"),
                      (5, "F-NULLF2"), (6, "F-S3-REV")):
        for D in DS:
            U[(fam, D)] = run.ck_load(f"p{ph}-{fam}-D{D}")
    P1 = ctx["phase1"]
    det = run.ck_load("p7-determinism")
    st = json.load(open(os.path.join(final, "selftest.json")))
    actx = {"phase1": P1, "units": U, "phase7": det, "selftest": st, "plan": plan}
    cell, hazards, sizing, checks, dr = analysis.analyse(actx)
    dr = analysis.decision_rules_sizing(dr, cell, sizing)

    # ---- orders, curve, references
    for D in DS:
        S = ctx["shapes"][D]
        write_new(os.path.join(out, f"column-order-D{D}.json"),
                  json.dumps({"D": D, "C_D": S.C, "order": "descending degrevlex, v_0 > ... > v_17, constant last",
                              "columns": [{"col": i, "monomial": list(m), "degree": len(m)} for i, m in enumerate(S.cols)]}))
        write_new(os.path.join(out, f"row-order-D{D}.json"),
                  json.dumps({"D": D, "R_D": S.R, "rule": "row = (index of mu) * 17 + k; mu by (degree asc, sorted index tuple lex)",
                              "rows": S.row_order()}))
    cv = dict(P1["curve"])
    cv["factor_base_size_F_V"] = P1["F-PLANT"]["factor_base_size"]
    cv["field"] = "F_2[t]/(t^17 + t^3 + 1); element <-> 17-bit integer, bit j = coefficient of t^j"
    cv["equation"] = "Y^2 + XY = X^3 + A X^2 + B"
    write_new(os.path.join(out, "curve.json"), jdump(cv))

    refs_out = {}
    d_star = {}
    for fam in FAMS:
        src = "F-S3" if fam in ("F-S3", "F-S3-REV") else fam
        fr = {"source_instances": src, "shortfall": P1.get(src, {}).get("ref_shortfall"), "references": {}}
        if fam == "F-PLANT":
            fr["note"] = "F-PLANT is scored against the F-S3 references (and its own modal reference)"
        for D in DS:
            unit = U[(fam, D)]
            for r in unit["refs"]:
                e = fr["references"].setdefault(r["label"], {})
                if r["label"] == "modal":
                    e.setdefault("modal_per_D", {})[f"D{D}"] = r["modal_info"]
                    e.setdefault("instance_idx_per_D", {})[f"D{D}"] = r.get("instance_idx")
                e[f"D{D}"] = {"rank": r["rank"], "one_in_R": r["one_in_R"], "h_rank": r["h_rank"], "h_set": r["h_set"],
                              "h_strict": r["h_strict"], "h_ops": r["h_ops"], "len_strict": r["len_strict"],
                              "Z_size": r["Z_size"], "K_exact": r.get("K_exact"), "K_rank": r.get("K_rank"),
                              "T_strict": r["T_strict"]}
        for inst in P1.get(src, {}).get("refs", []):
            e = fr["references"].setdefault(inst["selected_as"], {})
            e.update({"arm": "sat" if inst["s"] >= 1 else "unsat", "s": inst["s"], "stream_draw": inst["draw"],
                      "x_R": inst.get("x_R"), "a": inst.get("a"), "b": inst.get("b"), "E_hex": inst.get("E_hex")})
            o3 = e.get("D3", {}).get("one_in_R")
            o4 = e.get("D4", {}).get("one_in_R")
            e["D_star"] = 3 if o3 else (4 if o4 else "not reached at D <= 4")
        refs_out[fam] = fr
    write_new(os.path.join(out, "references.json"), jdump(refs_out))

    # ---- per-target files
    for fam in FAMS:
        d3 = {r["idx"]: r for r in U[(fam, 3)]["records"]}
        d4 = {r["idx"]: r for r in U[(fam, 4)]["records"]}
        p = os.path.join(out, f"targets-{fam}.jsonl.gz")
        if os.path.exists(p):
            raise RuntimeError(f"{p} exists")
        tmp = p + ".tmp"
        with gzip.open(tmp, "wt") as f:
            for idx in sorted(d3):
                ds = 3 if d3[idx]["one_in_R"] else (4 if d4[idx]["one_in_R"] else "not reached at D <= 4")
                for r in (d3[idx], d4[idx]):
                    rr = dict(r)
                    rr["D_star"] = ds
                    f.write(json.dumps(rr, separators=(",", ":"), default=_jd) + "\n")
        os.replace(tmp, p)

    # ---- hazards, cell summary, checks, decisions, sizing
    write_new(os.path.join(out, "pivot-hazards.json"),
              json.dumps({"layout": "families -> D -> reference key -> per-pivot columnar arrays (index k = pivot step)",
                          "families": hazards}, separators=(",", ":"), default=_jd))
    rej = P1["rejections"]
    cell["rejections_per_stream"] = rej
    cell["F-AFF_reference_x_collisions_with_F-S3_test_targets"] = {f"F-AFF-{d}": P1[f"F-AFF-{d}"]["ref_x_collides_with_F-S3_test_x"] for d in (1, 2, 3)}
    cell["primary_unit"] = "GF(2) full-row XOR operations"
    write_new(os.path.join(out, "cell-summary.json"), jdump(cell))
    write_new(os.path.join(out, "instrument-checks.json"), jdump(checks))
    write_new(os.path.join(out, "decision-rules.json"), jdump(dr))
    sizing["saving_set_identity_check"] = {
        f"{fam}/D{D}/{lab}": v["saving"]["saving_set_identity_exact"] and v["saving"]["ops_set_equals_rank_sq"]
        for fam, dd in sizing["per_reference"].items() for D, refs in dd.items() for lab, v in refs.items()}
    sizing["saving_set_identity_all_pass"] = all(sizing["saving_set_identity_check"].values())
    sizing["labels"] = "all sizes and op counts are MEASURED from the actual matrices and op logs; nothing is modeled"
    write_new(os.path.join(out, "sizing.json"), jdump(sizing))

    # ---- raw result (independent recompute) + agreement
    indep = independent_primary(out)
    agree = agreement(cell, indep)
    status = "invalid_measurement" if checks["invalidation"]["run_void"] else "completed_valid"
    raw = {"run_id": run.args.run_id, "experiment_id": "EXP-CERTBIN-4e92d7", "validity_status": status,
           "derivation": "recomputed by report.independent_primary from targets-*.jsonl.gz and pivot-hazards.json",
           "primary": indep, "M3": cell["M3"], "decision_rules_verdicts": {k: (v.get("verdict") or v.get("reading") or {kk: v.get(kk) for kk in ("one_system_per_SM", "thousands_per_warp", "strict_replay", "T_set_replay")}) for k, v in dr.items() if k.startswith("DR-") and k != "DR-8"},
           "agreement_with_cell_summary": agree}
    write_new(os.path.join(out, "raw-result.json"), jdump(raw))
    write_new(os.path.join(out, "run-report.md"), run_report(spec, cell, checks, dr, sizing, agree, status))
    write_manifest_and_env(run, plan, spec, spec_text, status, checks, cell, dr, agree, out)
    for f in sorted(os.listdir(out)):
        dst = os.path.join(final, f)
        if os.path.exists(dst):
            raise RuntimeError(f"{dst} exists; refusing to overwrite")
    for f in sorted(os.listdir(out)):
        os.replace(os.path.join(out, f), os.path.join(final, f))
    os.rmdir(out)


def write_manifest_and_env(run, plan, spec, spec_text, status, checks, cell, dr, agree, out):
    final = run.out
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    invs = [json.loads(l) for l in open(os.path.join(final, "checkpoint", "invocations.jsonl"))]
    st = json.load(open(os.path.join(final, "selftest.json")))
    plan_path = os.path.abspath(run.args.plan)
    try:
        res_json = subprocess.run([sys.executable, "-m", "orchestration.adapter", "resolve", "--role", "executor", "--json"],
                                  capture_output=True, text=True, cwd=repo).stdout
        resol = json.loads(res_json)
    except Exception as e:
        resol = {"error": repr(e)}
    session_model = os.environ.get("AUTORESEARCH_SESSION_MODEL")
    inference = {
        "requested_policy": "executor-implementation",
        "canonical_policy": resol.get("policy"),
        "backend": resol.get("backend"),
        "provider": resol.get("provider"),
        "adapter_resolved_model_id": resol.get("resolved_model_id"),
        "resolved_model_id": session_model,
        "model_provenance": "operator-supplied (executor session model as reported by the Claude Code runtime)",
        "model_verified": False,
        "requested_reasoning_effort": resol.get("requested_reasoning_effort"),
        "reasoning_effort": None,
        "fallback_used": bool(session_model and session_model != resol.get("resolved_model_id")),
        "fallback_reason": (f"Claude Code subagent runs with model: inherit; the session model ({session_model}) differs from "
                            f"the adapter binding ({resol.get('resolved_model_id')}) for executor-implementation. The handoff "
                            f"sets fallback_allowed: false; recorded here, not silently substituted.")
        if session_model and session_model != resol.get("resolved_model_id") else None,
        "degraded_requirements": [],
        "independent_session": False,
        "adapter_version": resol.get("adapter_version"),
        "config_digest": resol.get("config_digest"),
        "note": "The model wrote the implementation. Every number in this run comes from deterministic code; no model was in the computational loop.",
    }
    fe = run.ck_load("first-elimination")
    phases = {}
    for name in sorted(os.listdir(run.ck)):
        if not name.endswith(".json.gz") or name.startswith("first-") or name.startswith("p8"):
            continue
        d = run.ck_load(name[:-8])
        m = d.get("_meta", d)
        phases[name[:-8]] = {k: m.get(k) for k in ("started_at", "finished_at", "wall_seconds", "peak_rss_bytes", "pid")}
    peak = max([i.get("peak_rss_bytes") or 0 for i in invs] + [p.get("peak_rss_bytes") or 0 for p in phases.values()])
    env = {
        "python_version": sys.version, "python_executable": sys.executable,
        "numpy_version": np.__version__, "numpy_location": np.__file__, "pyyaml_version": yaml.__version__,
        "numpy_install_note": "numpy 2.4.6 installed by the executor with `pip install --user numpy` (system python3 had none) before any run; recorded as an environment setup step",
        "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "mem_total_kB": next((l.split()[1] for l in open("/proc/meminfo") if l.startswith("MemTotal")), None),
        "sage": "not used",
        "env": {k: os.environ.get(k) for k in ("PYTHONDONTWRITEBYTECODE", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "AUTORESEARCH_SESSION_MODEL")},
        "rlimit_as_bytes": 4 * 1024 ** 3,
        "compiled_helpers": "none (pure Python + numpy)",
    }
    write_new(os.path.join(out, "environment.json"), jdump(env))
    impl_dir = os.path.dirname(os.path.abspath(__file__))
    impl_hashes = {f: sha256_file(os.path.join(impl_dir, f)) for f in sorted(os.listdir(impl_dir))
                   if os.path.isfile(os.path.join(impl_dir, f))}
    artifacts = {}
    for d in (final, out):
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if os.path.isfile(p) and f not in ("manifest.yaml", "stdout.log", "stderr.log", "command.txt"):
                artifacts[f] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
    ckbytes = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(run.ck) for f in fs
                  if not dp.startswith(out))
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(final) for f in fs)
    c4 = cell["families"]["F-S3"]["D4"]
    manifest = {"run": {
        "id": run.args.run_id, "experiment_id": "EXP-CERTBIN-4e92d7", "task_id": "TASK-20260923-6f1ad4",
        "status": status,
        "claim_tier": "toy",
        "code": {"commit": invs[0]["git"].get("commit"), "dirty": invs[0]["git"].get("dirty"),
                 "dirty_paths_at_first_invocation": invs[0]["git"].get("status_porcelain"),
                 "impl_sha256": impl_hashes,
                 "commands": {"selftest": st.get("argv"), "driver_invocations": [i["argv"] for i in invs if i.get("event") == "start"]},
                 "command_file": "command.txt"},
        "inference": inference,
        "environment": {"see": "environment.json", "python_version": platform.python_version(), "numpy_version": np.__version__,
                        "operating_system": platform.platform(), "architecture": platform.machine(), "sage_version": None},
        "inputs": {"specification": "experiments/EXP-CERTBIN-4e92d7/specification.yaml",
                   "specification_sha256": hashlib.sha256(spec_text).hexdigest(),
                   "trial_plan": "experiments/EXP-CERTBIN-4e92d7/trial-plan-v1.json",
                   "trial_plan_sha256": sha256_file(plan_path),
                   "trial_plan_mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(plan_path), datetime.timezone.utc).isoformat(),
                   "first_elimination_at": fe["at"],
                   "seeds": plan["seeds"], "generator": "numpy.random.Generator(numpy.random.PCG64(seed)), one generator per stream",
                   "curve": {k: cell_curve for k, cell_curve in run.ck_load("p1-instances")["curve"].items() if k in ("A", "B", "order", "h", "q", "k_Q", "P", "Q")},
                   "parameters": {"n": 17, "m": 2, "l": 9, "D": [3, 4], "modulus": "t^17 + t^3 + 1"}},
        "timing": {"invocations": [{k: i.get(k) for k in ("event", "pid", "started_at", "at", "wall_seconds", "argv", "rc")} for i in invs],
                   "selftest": {"started_at": st.get("started_at"), "finished_at": st.get("finished_at"), "wall_seconds": st.get("wall_seconds")},
                   "phases": phases},
        "resources": {"peak_rss_bytes": peak, "per_invocation_peak_rss_bytes": [i.get("peak_rss_bytes") for i in invs if i.get("event") == "end"],
                      "cpu_seconds_per_invocation": [i.get("cpu_seconds") for i in invs if i.get("event") == "end"],
                      "memory_cap": "RLIMIT_AS 4 GiB set in-process", "watchdog_seconds": 86400,
                      "workers": 1, "sharding_demonstration": "not performed; the run used a single worker"},
        "result": {
            "valid": status == "completed_valid", "invalid_reason": None if status == "completed_valid" else checks["invalidation"],
            "voided_metrics": checks["invalidation"]["voided_metrics"],
            "metrics": {"F-S3_D4_T_strict_retention_family_unsat": c4["retention_family_unsat"]["strict"]["retention_family"],
                        "F-S3_D4_H_T_strict_bits": c4["M4_entropy"]["strict"]["H_bits"],
                        "M3": {k: cell["M3"].get(k) for k in ("kind", "value")},
                        "M2": {k: cell["M2"].get(k) for k in ("n", "median_h", "frac_in_[0.4,0.6]")},
                        "instrument_checks": {k: v["pass"] for k, v in checks["M5_summary"].items()}},
            "decision_rules": "decision-rules.json",
            "raw_result_agrees_with_cell_summary": agree["agree"],
            "certificate": {"kind": "none", "verified": None, "verifier": None,
                            "note": "no solve or relation is claimed; Boolean solutions are re-verified as instrument checks (C-WIT)"}},
        "protocol_interpretations_and_deviations": plan.get("interpretations"),
        "artifacts": artifacts,
        "package_bytes_before_logs_and_manifest": total,
        "checkpoint_bytes": ckbytes,
    }}
    class NoAlias(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True
    write_new(os.path.join(out, "manifest.yaml"), yaml.dump(manifest, Dumper=NoAlias, sort_keys=False, width=120))
