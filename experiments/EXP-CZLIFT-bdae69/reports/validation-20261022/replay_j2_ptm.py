#!/usr/bin/env python3
"""Phase-2 replays for TASK-20261022-2d255e (J2, J3 follow-up, PTM-1).

A. Independent row replay: shares only the RNG-call protocol of run.py (needed
   to regenerate the recorded random draws: prime sample, d, x, y and the five
   Hensel eps draws per row); every section value, the functional, valuations
   and the ratio rule use the validator's own arithmetic (blind/fq_blind.py and
   below). Compares all five per-row fields for all sections on all 3200 rows.
B. Producer determinism replay in memory: driver.build(seed, ...) compared with
   the archived raw-result.json (no run record is written; nothing is written
   outside this folder).
C. Exact expectations: naive hom count (P(xy < p)) and naive success count
   conditional on the drawn primes (exact success sets over uniform d), with a
   Monte Carlo tail probability for the observed count.
D. PTM-1: the producer's success test on the Teichmuller section over all 288
   primes in (50,2000) with fresh seeds, and on precision-floor perturbations of
   it (functional nonzero only in digit j), against the 1/p random rate.

Usage: PYTHONDONTWRITEBYTECODE=1 python3 replay_j2_ptm.py <repo_root> <out_json>
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import random
import sys

ROOT = sys.argv[1]
OUT = sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(ROOT, "experiments/EXP-CZLIFT-bdae69")
RUNS = {"RUN-CZLIFT-0cefcd": 20261009, "RUN-CZLIFT-a5c1da": 20261010}
K = 4

_s = importlib.util.spec_from_file_location("fq_blind", os.path.join(HERE, "blind", "fq_blind.py"))
fqb = importlib.util.module_from_spec(_s)
_s.loader.exec_module(fqb)


def my_vp(x, p, k):
    x %= p ** k
    if x == 0:
        return k
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v


def my_teich(x, p, k=K):
    return pow(x, p ** (k - 1), p ** k)


def my_L(s, p, k=K):
    return fqb.padic_log_unit(pow(s, p - 1, p ** k), p, k)


def my_ratio_fields(s_g, s_gd, d, p, k=K):
    """Ratio L(s_gd)/L(s_g) in Q_p, read mod p when integral; undefined if L(s_g)=0
    mod p^k or the quotient is non-integral."""
    fg, fgd = my_L(s_g, p, k), my_L(s_gd, p, k)
    vg, vgd = my_vp(fg, p, k), my_vp(fgd, p, k)
    if vg >= k or vgd < vg:
        return fg, vg, False, False
    if vgd > vg:
        r = 0
    else:
        r = ((fgd // p ** vg) % p) * pow((fg // p ** vg) % p, -1, p) % p
    return fg, vg, True, r == d % p


def replay_rows(seed):
    P = fqb.primes_in(50, 2000)
    primes = sorted(random.Random(seed).sample(P, 40))
    out = []
    for p in primes:
        rng = random.Random(seed * 65_537 + p)
        M = p ** K
        g = fqb.smallest_primitive_root(p)
        rows = []
        for _ in range(40):
            d = rng.randrange(2, p - 2)
            x = pow(g, rng.randrange(1, p - 1), p)
            y = pow(g, rng.randrange(1, p - 1), p)
            gd = pow(g, d, p)
            secs = {}
            for kind in ("teichmuller", "naive", "hensel"):
                if kind == "teichmuller":
                    lift = lambda a: my_teich(a, p)  # noqa: E731
                    s_g, s_gd, s_x, s_y, s_xy = (lift(a) for a in (g, gd, x, y, x * y % p))
                elif kind == "naive":
                    s_g, s_gd, s_x, s_y, s_xy = g, gd, x, y, x * y % p
                else:
                    vals = []
                    for a in (g, gd, x, y, x * y % p):
                        vals.append((a + p * rng.randrange(M // p)) % M)
                    s_g, s_gd, s_x, s_y, s_xy = vals
                fg, vg, dfn, suc = my_ratio_fields(s_g, s_gd, d, p)
                secs[kind] = {"hom": s_xy == (s_x * s_y) % M, "functional_vanishes": fg % M == 0,
                              "v_functional": vg, "ratio_defined": dfn, "success": suc}
            rows.append({"d": d, "sections": secs})
        out.append({"p": p, "generator": g, "precision": K, "rows": rows})
    return primes, out


def part_a():
    res = {}
    for run_id, seed in RUNS.items():
        raw = json.load(open(os.path.join(EXP, "runs", run_id, "raw-result.json")))
        primes, mine = replay_rows(seed)
        rec = raw["raw"]["primes"]
        field_mismatch = {}
        rows_cmp = 0
        mism = []
        for a, b in zip(mine, rec):
            assert a["p"] == b["p"]
            for ra, rb in zip(a["rows"], b["rows"]):
                rows_cmp += 1
                if ra["d"] != rb["d"]:
                    mism.append([a["p"], "d", ra["d"], rb["d"]])
                for kind in ra["sections"]:
                    for f, v in ra["sections"][kind].items():
                        if rb["sections"][kind][f] != v:
                            key = f"{kind}.{f}"
                            field_mismatch[key] = field_mismatch.get(key, 0) + 1
                            if len(mism) < 20:
                                mism.append([a["p"], a["generator"], ra["d"], key, v, rb["sections"][kind][f]])
        res[run_id] = {"prime_list_equal": primes == raw["metrics"]["prime_list"],
                       "generators_equal": [x["generator"] for x in mine] == [x["generator"] for x in rec],
                       "rows_compared": rows_cmp, "field_mismatch_counts": field_mismatch,
                       "first_mismatches": mism, "independent_rows_identical": mine == rec}
    return res


def part_b():
    sys.path.insert(0, os.path.join(EXP, "implementation"))
    sys.path.insert(0, ROOT)
    import run as driver  # producer driver, imported read-only, no record written
    res = {}
    for run_id, seed in RUNS.items():
        raw = json.load(open(os.path.join(EXP, "runs", run_id, "raw-result.json")))
        m, r = driver.build(seed, 50, 2000, 40, 40)
        rt = json.loads(json.dumps({"metrics": m, "certificate": {"kind": "none"}, "raw": r},
                                   indent=1, sort_keys=True, default=str))
        res[run_id] = {"replay_equal_archived_raw_result": rt == raw,
                       "metrics_equal": rt["metrics"] == raw["metrics"],
                       "raw_equal": rt["raw"] == raw["raw"]}
    return res, driver


def part_c():
    res = {}
    P = fqb.primes_in(50, 2000)
    table = {p: None for p in P}
    for run_id, seed in RUNS.items():
        raw = json.load(open(os.path.join(EXP, "runs", run_id, "raw-result.json")))
        prs = raw["raw"]["primes"]
        # naive hom: x, y uniform on F_p^* \ {1} (exponent in [1, p-2]); hom iff x*y < p
        e_hom = 0.0
        for b in prs:
            p = b["p"]
            cnt = sum(max(0, min(p - 1, (p - 1) // xx) - 1) for xx in range(2, p))
            e_hom += 40 * cnt / (p - 2) ** 2
        # exact naive success sets per drawn prime
        exact_sets = {}
        e_exact = 0.0
        e_model = 0.0
        for b in prs:
            p, g = b["p"], b["generator"]
            succ = [d for d in range(2, p - 2) if pow(g, d, p * p) < p]
            small = [d for d in range(2, p - 2) if fqb.small_power(g, d, p)]
            exact_sets[p] = succ
            e_exact += 40 * len(succ) / (p - 4)
            e_model += 40 * (len(small) + (p - 4 - len(small)) / p) / (p - 4)
        obs = sum(1 for b in prs for r in b["rows"] if r["sections"]["naive"]["success"])
        import numpy as np
        nrng = np.random.default_rng(0x5EED ^ seed)
        sims = 200000
        tot = np.zeros(sims, dtype=np.int64)
        for b in prs:
            p = b["p"]
            tot += nrng.binomial(40, len(exact_sets[p]) / (p - 4), size=sims)
        ge = int((tot >= obs).sum())
        dups = 0
        for b in prs:
            ds = [r["d"] for r in b["rows"]]
            dups += len(ds) - len(set(ds))
        # dedup sensitivity: distinct (p, d) rows only
        seen = set()
        dd_rows = []
        for b in prs:
            for r in b["rows"]:
                key = (b["p"], r["d"])
                if key in seen:
                    continue
                seen.add(key)
                dd_rows.append((b["p"], r["sections"]["naive"]["success"]))
        n_dd = len(dd_rows)
        S_dd = sum(1 for _, s in dd_rows if s)
        ref_dd = sum(1 / p for p, _ in dd_rows) / n_dd
        z_dd = (S_dd - n_dd * ref_dd) / math.sqrt(n_dd * ref_dd * (1 - ref_dd))
        res[run_id] = {"naive_hom_expected_count_P_xy_lt_p": e_hom,
                       "naive_hom_recorded_count": sum(1 for b in prs for r in b["rows"] if r["sections"]["naive"]["hom"]),
                       "naive_hom_expected_under_1_over_p": sum(40 / b["p"] for b in prs),
                       "naive_success_observed": obs,
                       "E_success_given_primes_exact_uniform_d": e_exact,
                       "E_success_given_primes_model_gd_lt_p_plus_inv_p": e_model,
                       "mc_P_S_ge_observed_given_primes_exact": ge / sims, "mc_sims": sims,
                       "duplicate_d_rows": dups,
                       "dedup_distinct_rows": n_dd, "dedup_success": S_dd, "dedup_z": z_dd}
    return res


def part_d(driver):
    """PTM-1 with the producer's own functional and val_p and the run.py ratio rule."""
    from harness.czlift import teichmuller as prod_teich, val_p as prod_val
    P = fqb.primes_in(50, 2000)
    out = {}

    def ratio_rule(fg, fgd, p, k):
        vg, vgd = prod_val(fg, p, k), prod_val(fgd, p, k)
        if vg >= k or vgd < vg:
            return None
        if vgd > vg:
            return 0
        return (fgd // p ** vgd) * pow((fg // p ** vg) % p, -1, p) % p

    for label, seed in (("ptm_seed_A", 7), ("ptm_seed_B", 11)):
        rng = random.Random(seed)
        n = 0
        succ = {"teich": 0, "teich_floor_j3": 0, "teich_floor_j2": 0, "teich_floor_j1": 0}
        dfn = {kk: 0 for kk in succ}
        null = 0.0
        for p in P:
            M = p ** K
            g = fqb.smallest_primitive_root(p)
            for _ in range(40):
                d = rng.randrange(2, p - 2)
                n += 1
                null += 1 / p
                tg, tgd = prod_teich(g, p, K), prod_teich(pow(g, d, p), p, K)
                r = ratio_rule(driver.functional(tg, p, K), driver.functional(tgd, p, K), p, K)
                dfn["teich"] += r is not None
                succ["teich"] += (r is not None and r == d % p)
                for j in (3, 2, 1):
                    ug = (1 + p ** j * rng.randrange(1, p)) % M
                    ugd = (1 + p ** j * rng.randrange(1, p)) % M
                    sg, sgd = tg * ug % M, tgd * ugd % M
                    rr = ratio_rule(driver.functional(sg, p, K), driver.functional(sgd, p, K), p, K)
                    key = f"teich_floor_j{j}"
                    dfn[key] += rr is not None
                    succ[key] += (rr is not None and rr == d % p)
        sd = math.sqrt(sum((1 / p) * (1 - 1 / p) for p in P) * 40)
        out[label] = {"rows": n, "primes": len(P), "random_rate_expected_successes": null, "null_sd": sd,
                      "successes": succ, "ratio_defined": dfn,
                      "z": {kk: (v - null) / sd for kk, v in succ.items()}}
    return out


def main():
    res = {"A_independent_row_replay": part_a()}
    b, driver = part_b()
    res["B_producer_determinism_replay"] = b
    res["C_exact_expectations"] = part_c()
    res["D_PTM1"] = part_d(driver)
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps(res, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
