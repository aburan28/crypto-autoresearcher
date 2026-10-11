"""J7 mechanical checks and small computations (no randomness unless stated).

(b) matched-random construction: A_fix equal across every arm of a job; target_label census on
    every row; random-arm seeds distinct; |F| of structured vs matched randoms (mismatches).
(d) censoring by arm (structured vs random), Fisher's exact test (two-sided, own code).
(e) the structured arms' own residual variance against the random arms' V, pooled per (class, m)
    over resolved cells (ALT-e1 definitions of attacks/choices.yaml).
(f) TT and TB pair counts identical between census and on modes on every instance (table-only).
(g) relation-level index of dispersion of the random arms (distinct relations per instance,
    within-curve triples, complete instances; 02_bundles.jsonl), pooled per (class, m).
(h) the PTM-1 statistic (arm vs two randoms, SD = sqrt(1.5 V)) applied to the STRUCTURED arms
    (each of the three random pairs of its triple), for an apples-to-apples rate with PTM-1.
(i) TT-SS coupling on shared instances: correlation of within-triple residuals, random arms.
Output: attacks/out/10_j7_checks.json
"""
import json
import math
import os
import statistics
import sys
from collections import Counter, defaultdict
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import (OUT, P, RANDOMS, RANDOM_ARMS, RUNGS, STRUCT, build_index, canonical_rows,  # noqa: E402
                   censored, m_of, usable)


def fisher_two_sided(a, b, c, d):
    """2x2 table [[a, b], [c, d]]; two-sided p by summing tables no more probable."""
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def lp(x):
        return (math.lgamma(r1 + 1) + math.lgamma(n - r1 + 1) + math.lgamma(c1 + 1) + math.lgamma(n - c1 + 1)
                - math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(r1 - x + 1) - math.lgamma(c1 - x + 1)
                - math.lgamma(n - r1 - c1 + x + 1))
    lo, hi = max(0, r1 + c1 - n), min(r1, c1)
    p0 = lp(a)
    return min(1.0, sum(math.exp(lp(x)) for x in range(lo, hi + 1) if lp(x) <= p0 + 1e-9))


def main():
    rows = canonical_rows("census-m3") + canonical_rows("census-m4") + canonical_rows("census-m5")
    ix = build_index(rows)
    out = {}
    # (b)
    afix_bad, label_bad, seed_dup, size_mm = [], [], [], []
    jobs = defaultdict(list)
    for r in rows:
        if r.get("panel") == "main" and r.get("arm"):
            jobs[(m_of(r), r["bits"], r["curve"])].append(r)
    for k, rs in jobs.items():
        af = {r["harvest"]["attempt_budget_A_fix"] for r in rs if r.get("harvest") and r["arm"] != "known_log"}
        if len(af) > 1:
            afix_bad.append([*k, sorted(af)])
        for r in rs:
            if r.get("target_label") != "census":
                label_bad.append([*k, r["arm"], r["mode"], r.get("target_label")])
        seeds = {}
        for r in rs:
            if r["arm"] in RANDOM_ARMS and r["mode"] == "census":
                seeds[r["arm"]] = (r.get("fb_size"), json.dumps(r.get("fb_params"), sort_keys=True))
        # fb_params carries no seed (_census_instance strips it), so seed distinctness is read
        # from __main__._census_job (seeds c, c+1000, ..., c+5000), not from the rows; here only
        # the fb_size of each random family is checked to be constant within the family
        if len({seeds[a][0] for a in seeds if a in RANDOMS["subgroup"]}) > 1 or len({seeds[a][0] for a in seeds if a in RANDOMS["dickson"]}) > 1:
            seed_dup.append(list(k))
        for A in STRUCT:
            a = ix.get(("main", k[0], k[1], k[2], A, "census"))
            r0 = ix.get(("main", k[0], k[1], k[2], RANDOMS[A][0], "census"))
            if a and r0 and a["fb_size"] != r0["fb_size"]:
                size_mm.append([*k, A, a["fb_size"], r0["fb_size"]])
        sfb = {r["harvest"]["attempt_budget_A_fix"] for r in rs if r.get("harvest")}
    out["b_matched_random"] = {"jobs": len(jobs), "A_fix_unequal_jobs": afix_bad, "target_label_not_census": label_bad,
                               "random_family_size_not_constant_in_a_job": seed_dup,
                               "seed_distinctness": "from code: __main__._census_job builders use seeds c, c+1000, c+2000 (random_sub) and c+3000, c+4000, c+5000 (random_dick); the rows carry fb_params without the seed",
                               "structured_vs_random_size_mismatch": size_mm,
                               "random_draw_rule": ("factor_base.py FactorBase.random: rejection sampling of uniform x in "
                                                    "[0, p) without repetition, kept when lift_x gives a point with y != 0; "
                                                    "i.e. uniform among x-coordinates of curve points (read, not computed)")}
    # (d)
    cs = Counter()
    for r in rows:
        if r.get("panel") == "main" and r.get("mode") == "census" and (r.get("arm") in STRUCT or r.get("arm") in RANDOM_ARMS) and usable(r):
            grp = "structured" if r["arm"] in STRUCT else "random"
            cs[(grp, censored(r))] += 1
    a, b = cs[("structured", True)], cs[("structured", False)]
    c, d = cs[("random", True)], cs[("random", False)]
    out["d_censoring_by_arm"] = {"structured_censored": a, "structured_not": b, "random_censored": c, "random_not": d,
                                 "rate_structured": a / (a + b), "rate_random": c / (c + d),
                                 "fisher_two_sided_p": fisher_two_sided(a, b, c, d),
                                 "censored_instances": sorted([[m_of(r), r["bits"], r["curve"], r["arm"]] for r in rows
                                                               if r.get("mode") == "census" and usable(r) and r.get("panel") == "main"
                                                               and (r["arm"] in STRUCT or r["arm"] in RANDOM_ARMS) and censored(r)])}
    # (e)
    from rtlib import RUNS
    kc = [json.loads(l) for l in open(os.path.join(RUNS, P + "analysis", "kappa-cells.jsonl"))]
    pool = defaultdict(lambda: [0.0, 0.0, 0])
    for cc in kc:
        if not cc["resolved"] or cc["class"] == "TB" or not cc["counts_A"]:
            continue
        nA, nR = cc["counts_A"], cc["counts_R"]
        C_A, C_R = sum(nA), sum(sum(v) for v in nR) / 3
        kh = C_A / C_R
        s2 = sum(statistics.variance(v) for v in nR)
        e2 = sum((x - kh * statistics.mean(v)) ** 2 for x, v in zip(nA, nR))
        J = len(nA)
        V_A = max(0.0, (J / max(1, J - 1)) * e2 - kh * kh * s2 / 3)
        V_R = max(s2, C_R)
        p = pool[f"{cc['class']}|{cc['m']}"]
        p[0] += V_A
        p[1] += V_R
        p[2] += 1
    out["e_structured_vs_random_variance"] = {k: {"cells": v[2], "sum_V_A": v[0], "sum_V_R": v[1], "ratio_V_A_over_V_R": v[0] / v[1]}
                                              for k, v in sorted(pool.items())}
    # (f)
    mism = []
    for r in rows:
        if r.get("panel") == "main" and r.get("mode") == "census" and usable(r):
            o = ix.get(("main", m_of(r), r["bits"], r["curve"], r["arm"], "on"))
            if o is None or not usable(o):
                continue
            for c_ in ("TT", "TB"):
                for kk in ("pairs_raw", "pairs_nonformal", "dup_formal", "rows_emitted", "informative_rank"):
                    if r["harvest"][c_]["at_stop"][kk] != o["harvest"][c_]["at_stop"][kk]:
                        mism.append([m_of(r), r["bits"], r["curve"], r["arm"], c_, kk])
    out["f_TT_TB_census_vs_on"] = {"mismatches": mism[:50], "mismatch_count": len(mism)}
    # (g)
    bund = {}
    for line in open(os.path.join(OUT, "out", "02_bundles.jsonl")):
        x = json.loads(line)
        if x["mode"] != "census" or x["file"].startswith(P + "stage-r"):
            continue
        if x["scope"] != ("A_fix" if x["class"] == "SS" else "stop"):
            continue
        bund[(x["m"], x["bits"], x["curve"], x["arm"], x["class"])] = x
    drel = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    for m in (3, 4, 5):
        for bb in RUNGS:
            for cc_ in range(5):
                for fam in (RANDOMS["subgroup"], RANDOMS["dickson"]):
                    for cl in ("TT", "SS"):
                        recs = [bund.get((m, bb, cc_, a, cl)) for a in fam]
                        if not all(x is not None and x["complete"] for x in recs):
                            continue
                        rel = [x["relations"] for x in recs]
                        prs = [x["pairs_from_rows"] for x in recs]
                        d_ = drel[f"{cl}|{m}"]
                        d_[0] += statistics.variance(rel)
                        d_[1] += statistics.mean(rel)
                        d_[2] += statistics.variance(prs)
                        d_[3] += statistics.mean(prs)
    out["g_dispersion_relations_vs_pairs"] = {k: {"D_relations": v[0] / v[1] if v[1] else None,
                                                  "D_pairs_same_instances": v[2] / v[3] if v[3] else None}
                                              for k, v in sorted(drel.items())}
    # (h)
    exc, res = 0, 0
    lst = []
    for cc in kc:
        if cc["class"] == "TB" or not cc["counts_A"]:
            continue
        for pair in combinations(range(3), 2):
            nA = cc["counts_A"]
            nR = [[v[i] for i in pair] for v in cc["counts_R"]]
            C_R = sum(sum(v) / 2 for v in nR)
            if C_R < 10:
                continue
            s2 = sum(statistics.variance(v) for v in nR)
            SD = math.sqrt(1.5 * max(s2, C_R))
            z = (sum(nA) - C_R) / SD
            res += 1
            if abs(z) > 3:
                exc += 1
                lst.append([cc["arm"], cc["class"], cc["m"], cc["bits"], list(pair), round(z, 3)])
    out["h_structured_under_PTM1_statistic"] = {"resolved_pseudo_cells": res, "excursions": exc, "rate": exc / res,
                                                "list": lst}
    # (i)
    corr = {}
    for m in (3, 4, 5):
        xs, ys = [], []
        for bb in RUNGS:
            for cc_ in range(5):
                for fam in (RANDOMS["subgroup"], RANDOMS["dickson"]):
                    rs = [ix.get(("main", m, bb, cc_, a, "census")) for a in fam]
                    if not all(usable(r) for r in rs):
                        continue
                    tt = [r["harvest"]["TT"]["at_stop"]["pairs_nonformal"] for r in rs]
                    ss = [r["harvest"]["SS"]["at_A_fix"]["pairs_nonformal"] for r in rs]
                    mt, ms = statistics.mean(tt), statistics.mean(ss)
                    st, sss = statistics.pstdev(tt) or 1.0, statistics.pstdev(ss) or 1.0
                    for a_, b_ in zip(tt, ss):
                        xs.append((a_ - mt) / st)
                        ys.append((b_ - ms) / sss)
        corr[str(m)] = {"n": len(xs), "pearson_within_triple_residuals": statistics.correlation(xs, ys) if len(xs) > 2 else None}
    out["i_TT_SS_coupling"] = corr
    with open(os.path.join(OUT, "out", "10_j7_checks.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({k: (v if k != "d_censoring_by_arm" else {kk: vv for kk, vv in v.items() if kk != "censored_instances"})
                      for k, v in out.items() if k not in ("h_structured_under_PTM1_statistic",)}, indent=1)[:6000])
    print("h:", {k: v for k, v in out["h_structured_under_PTM1_statistic"].items() if k != "list"})


if __name__ == "__main__":
    main()
