#!/usr/bin/env python3
"""J2 recomputation for TASK-20261022-2d255e, written before check.py/run.py were read.

Reads raw-result.json of both runs (by key), recomputes every frozen metric from
the per-row booleans, recomputes the naive and Teichmuller rows independently from
(p, g, d) with the validator's own arithmetic, probes borderline rows, and
applies the sealed blind evaluator (blind/fq_blind.py, unchanged) to the actual
tuples for the J3 comparison.

Usage: python3 -I recompute_j2.py <repo_root> <out_json>
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
from collections import Counter

ROOT = sys.argv[1]
OUT = sys.argv[2]
EXP = os.path.join(ROOT, "experiments/EXP-CZLIFT-bdae69")
HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = {"RUN-CZLIFT-0cefcd": 20261009, "RUN-CZLIFT-a5c1da": 20261010}
SECTIONS = ("teichmuller", "naive", "hensel")

spec = importlib.util.spec_from_file_location("fq_blind", os.path.join(HERE, "blind", "fq_blind.py"))
fqb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fqb)


def is_prime(n):
    if n < 2:
        return False
    f = 2
    while f * f <= n:
        if n % f == 0:
            return False
        f += 1
    return True


def vp(x, p, cap):
    if x == 0:
        return cap
    v = 0
    while x % p == 0 and v < cap:
        x //= p
        v += 1
    return v


def L(a, p, prec=4):
    """own functional log_p(a^(p-1)) mod p^prec (integer a coprime to p)."""
    N = p ** prec
    return fqb.padic_log_unit(pow(a, p - 1, N), p, prec)


def teich(x, p, prec=4):
    """Teichmuller representative of x mod p, mod p^prec: x^(p^(prec-1)) mod p^prec."""
    N = p ** prec
    return pow(x, p ** (prec - 1), N)


def zvariants(S, rows_p, defined_mask):
    n = len(rows_p)
    ref = sum(1.0 / p for p in rows_p) / n
    zA = (S - n * ref) / math.sqrt(n * ref * (1 - ref))
    mu = sum(1.0 / p for p in rows_p)
    var = sum((1.0 / p) * (1 - 1.0 / p) for p in rows_p)
    zB = (S - mu) / math.sqrt(var)
    pd = [p for p, m in zip(rows_p, defined_mask) if m]
    if pd:
        nd = len(pd)
        refd = sum(1.0 / p for p in pd) / nd
        zC = (S - nd * refd) / math.sqrt(nd * refd * (1 - refd))
    else:
        zC = None
    return {"reference_inv_p": ref, "z_binomial_mean_ref": zA,
            "z_poisson_binomial": zB, "z_over_defined_rows": zC}


def run_one(run_id, seed):
    rd = os.path.join(EXP, "runs", run_id)
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    rec = {"run_id": run_id, "seed": seed}
    m = raw["metrics"]
    primes = raw["raw"]["primes"]
    # --- coverage / structure
    plist = [b["p"] for b in primes]
    cov = {
        "n_prime_blocks": len(primes),
        "prime_list_matches_metrics": plist == m["prime_list"],
        "all_prime": all(is_prime(p) for p in plist),
        "all_in_open_50_2000": all(50 < p < 2000 for p in plist),
        "distinct_primes": len(set(plist)) == len(plist),
        "sorted": plist == sorted(plist),
        "rows_per_prime": sorted(Counter(len(b["rows"]) for b in primes).items()),
        "precision_values": sorted({b["precision"] for b in primes}),
        "metrics_seed": m["seed"],
    }
    gen_ok, gen_smallest, d_out_of_range, d_pm1, dup_d = 0, 0, [], [], 0
    sec_missing = 0
    for b in primes:
        p, g = b["p"], b["generator"]
        if fqb.is_primitive_root(g, p):
            gen_ok += 1
        if g == fqb.smallest_primitive_root(p):
            gen_smallest += 1
        ds = [r["d"] for r in b["rows"]]
        dup_d += len(ds) - len(set(ds))
        for d in ds:
            if not (2 <= d <= p - 3):
                d_out_of_range.append([p, d])
            if d in (1, p - 2, p - 1, 0):
                d_pm1.append([p, d])
        for r in b["rows"]:
            if set(r["sections"]) != set(SECTIONS):
                sec_missing += 1
    cov.update({"generator_is_primitive_root": gen_ok, "generator_is_smallest_primitive_root": gen_smallest,
                "d_out_of_range": d_out_of_range, "d_equal_pm1_rows": d_pm1,
                "duplicate_d_within_prime": dup_d, "rows_missing_a_section": sec_missing})
    rec["coverage"] = cov
    # --- aggregate metrics from raw booleans
    rows = [(b["p"], b["generator"], r) for b in primes for r in b["rows"]]
    rows_p = [p for p, _, _ in rows]
    agg = {}
    for s in SECTIONS:
        hom = sum(1 for _, _, r in rows if r["sections"][s]["hom"])
        van = sum(1 for _, _, r in rows if r["sections"][s]["functional_vanishes"])
        dfn = [bool(r["sections"][s]["ratio_defined"]) for _, _, r in rows]
        suc = sum(1 for _, _, r in rows if r["sections"][s]["success"])
        n = len(rows)
        a = {"n": n, "hom_count": hom, "vanish_count": van, "defined_count": sum(dfn), "success_count": suc,
             "homomorphism_rate": hom / n, "functional_vanishing_rate": van / n,
             "ratio_defined_rate": sum(dfn) / n, "success_rate": suc / n,
             "success_without_defined": sum(1 for (_, _, r), dd in zip(rows, dfn)
                                            if r["sections"][s]["success"] and not dd),
             "vanish_vs_vfunctional_inconsistent": sum(
                 1 for _, _, r in rows
                 if bool(r["sections"][s]["functional_vanishes"]) != (r["sections"][s]["v_functional"] >= 4)),
             "v_functional_hist": sorted(Counter(r["sections"][s]["v_functional"] for _, _, r in rows).items())}
        a.update(zvariants(suc, rows_p, dfn))
        agg[s] = a
    rec["recomputed"] = agg
    # --- compare with recorded metrics (raw metrics block, manifest via text, stdout)
    stdout = json.loads(open(os.path.join(rd, "stdout.log")).read())
    cmp = {}
    for s in SECTIONS:
        recd = m["sections"][s]
        so = stdout[s]
        mine = {"n": agg[s]["n"], "homomorphism_rate": agg[s]["homomorphism_rate"],
                "functional_vanishing_rate": agg[s]["functional_vanishing_rate"],
                "ratio_defined_rate": agg[s]["ratio_defined_rate"], "success_rate": agg[s]["success_rate"],
                "reference_inv_p": agg[s]["reference_inv_p"], "z_score": agg[s]["z_binomial_mean_ref"]}
        cmp[s] = {k: {"recorded": recd[k], "stdout": so[k], "mine": mine[k],
                      "abs_diff": abs(recd[k] - mine[k]), "stdout_equal": so[k] == recd[k]}
                  for k in mine}
    rec["comparison"] = cmp
    # --- independent per-row recomputation (naive, teichmuller) from (p, g, d)
    nv = Counter()
    tm = Counter()
    nv_mismatch_rows = []
    hom_cands = Counter()
    hens_undefined = []
    for p, g, r in rows:
        d = r["d"]
        N = p ** 4
        rd_ = pow(g, d, p)
        # naive
        Lg = L(g, p)
        Lr = L(rd_, p)
        defined = Lg % (p * p) != 0
        succ_fq = fqb.naive_success_exact(p, g, d)
        succ_fq = bool(succ_fq) if succ_fq is not None else False
        R = fqb.naive_ratio_padic(p, g, d)
        succ_log = R is not None and R % p == d % p
        succ_full = R is not None and R == d % (p ** 3)
        v_r = vp(Lr, p, 4)
        v_g = vp(Lg, p, 4)
        cand_a = pow(g, d, N) == rd_
        cand_b = (g * pow(g, d - 1, p)) == rd_
        cand_c = pow(g, d, p * p) == rd_
        hom_cands["a_sg_pow_d_eq_s_gd_mod_p4"] += cand_a
        hom_cands["b_sg_times_s_gdm1_eq_s_gd"] += cand_b
        hom_cands["c_mod_p2"] += cand_c
        hom_cands["g_pow_d_lt_p"] += fqb.small_power(g, d, p)
        recn = r["sections"]["naive"]
        nv["rows"] += 1
        nv["success_match_fq"] += (recn["success"] == succ_fq)
        nv["success_match_padic_log"] += (recn["success"] == succ_log)
        nv["success_full_precision_count"] += succ_full
        nv["defined_match"] += (recn["ratio_defined"] == defined)
        nv["vfunc_match_v_L_gd"] += (recn["v_functional"] == v_r)
        nv["vfunc_match_v_L_g"] += (recn["v_functional"] == v_g)
        nv["vanish_match"] += (recn["functional_vanishes"] == (Lr == 0))
        nv["hom_match_cand_a"] += (recn["hom"] == cand_a)
        nv["hom_match_cand_b"] += (recn["hom"] == cand_b)
        if recn["success"] != succ_fq:
            nv_mismatch_rows.append([p, g, d, recn["success"], succ_fq])
        # teichmuller
        tg = teich(g, p)
        tgd = teich(rd_, p)
        hom_t = pow(tg, d, N) == tgd
        Lt = fqb.padic_log_unit(pow(tgd, p - 1, N), p, 4)
        rect = r["sections"]["teichmuller"]
        tm["rows"] += 1
        tm["own_hom_true"] += hom_t
        tm["own_vanish_true"] += (Lt == 0)
        tm["hom_match"] += (rect["hom"] == hom_t)
        tm["vanish_match"] += (rect["functional_vanishes"] == (Lt == 0))
        tm["defined_false"] += (not rect["ratio_defined"])
        tm["success_false"] += (not rect["success"])
        if not r["sections"]["hensel"]["ratio_defined"]:
            hens_undefined.append([p, g, d, r["sections"]["hensel"]])
    rec["naive_row_recompute"] = dict(nv)
    rec["naive_success_mismatch_rows"] = nv_mismatch_rows
    rec["naive_hom_candidate_counts"] = dict(hom_cands)
    rec["teichmuller_row_recompute"] = dict(tm)
    rec["hensel_undefined_rows"] = hens_undefined
    # --- borderline listing: naive successes split by g^d < p
    succ_rows = [[p, g, r["d"], fqb.small_power(g, r["d"], p), pow(g, r["d"], p * p) // p]
                 for p, g, r in rows if r["sections"]["naive"]["success"]]
    rec["naive_success_rows_p_g_d_smallpow_floorquot"] = succ_rows
    rec["naive_success_from_g_pow_d_lt_p"] = sum(1 for x in succ_rows if x[3])
    rec["naive_success_from_rest"] = sum(1 for x in succ_rows if not x[3])
    # per-prime breakdown of rest successes (clumping probe)
    rest_by_p = Counter(x[0] for x in succ_rows if not x[3])
    rec["naive_rest_success_by_prime"] = sorted(rest_by_p.items())
    hens_s = [[p, g, r["d"]] for p, g, r in rows if r["sections"]["hensel"]["success"]]
    rec["hensel_success_rows"] = hens_s
    # --- J3: sealed blind evaluator on actual tuples
    tuples = [(p, g, r["d"]) for p, g, r in rows]
    rec["J3_blind_evaluator_on_actual_tuples"] = fqb.expected_count(tuples)
    # --- frozen criteria
    rec["criteria"] = {
        "teich_hom_rate_eq_1": agg["teichmuller"]["homomorphism_rate"] == 1.0,
        "teich_vanish_rate_eq_1": agg["teichmuller"]["functional_vanishing_rate"] == 1.0,
        "naive_abs_z_le_4": abs(agg["naive"]["z_binomial_mean_ref"]) <= 4,
        "hensel_abs_z_le_4": abs(agg["hensel"]["z_binomial_mean_ref"]) <= 4,
        "naive_z_gt_4": agg["naive"]["z_binomial_mean_ref"] > 4,
        "hensel_z_gt_4": agg["hensel"]["z_binomial_mean_ref"] > 4,
        "naive_z_gt_4_all_variants": all(
            (agg["naive"][k] or 0) > 4 for k in ("z_binomial_mean_ref", "z_poisson_binomial", "z_over_defined_rows")),
        "hensel_abs_z_le_4_all_variants": all(
            abs(agg["hensel"][k] or 0) <= 4 for k in ("z_binomial_mean_ref", "z_poisson_binomial", "z_over_defined_rows")),
    }
    return rec


def main():
    out = {"runs": [run_one(r, s) for r, s in RUNS.items()]}
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    for rec in out["runs"]:
        slim = {k: v for k, v in rec.items() if k not in ("hensel_undefined_rows",)}
        print(json.dumps(slim, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
