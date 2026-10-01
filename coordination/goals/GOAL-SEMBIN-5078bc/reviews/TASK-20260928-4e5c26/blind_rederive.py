#!/usr/bin/env python3
"""Blind re-derivation for TASK-20260928-4e5c26 (GOAL-SEMBIN-5078bc).

Written WITHOUT reading EXP-SEMBIN-04ec3c's code, RESULTS.md, runs/, the
experiment specification, DEC-20260928-7c3d91, TASK-20260928-e4f7b2,
H-SEMBIN-8e7ae3, or any earlier SEMBIN review/rederivation artifact.

Quantity (as stated in the dispatch prompt): index calculus on E(F_{2^n}),
n prime; factor base F with |F| = 2^d; m summands; a decomposition oracle
with TIME |F|^(m-s) and STORE |F|^s, integer 0 <= s <= floor(m/2).
Find the minimum store (log2 entries) such that some d gives a total cost
strictly below rho = 0.886 * sqrt(N), N = r (n = 131) or 2^n otherwise.

All costs are in log2 of "elementary operations", where one elementary
operation is one group operation, one table probe, or one mod-r multiply-add
(an optimistic unit for index calculus; see blind_derivation.md).

Model PRIMARY ("E", the stated term list, first-principles conventions):
  F           = {P in E : x(P) in V}, dim_F2 V = d, closed under negation,
                |F| = 2^d points.
  K           = |F|/2 unknowns (log(-P) = -log(P)); relations needed = K.
  lambda      = |F|^m / (m! N)  expected # unordered m-multisets of F summing
                to a uniformly random target (random-sum heuristic).
  trials/rel  = 1/lambda  (expected-yield reading: the oracle returns every
                decomposition of the target; NOT capped at one per call).
  oracle      = |F|^(m-s) per trial, store |F|^s (build NOT charged, because
                the oracle is specified by its TIME/STORE pair).
  RC          = K * max(trials/rel * |F|^(m-s), 1)
              = K * max(m! N / |F|^s, 1)     (floor: >= 1 op per relation)
  LA          = m * K^2   (sparse Lanczos/Wiedemann: ~K matvecs, each m*K)
  total       = RC + LA
Variants (each changes exactly one thing vs PRIMARY):
  V1_K_eq_F        K = |F| (textbook count, no negation halving).
  V2_prob_capped   trials/rel = 1/P, P = 1 - exp(-lambda) (true probability,
                   at most one relation per oracle call).
  V3_build_charged total += |F|^s (cost of building the store).
  V4_truncated     RC = K * max(s! N / |F|^s, 1): truncated MITM enumeration
                   counting distinct hits (a probe hits a distinct s-sum key
                   w.p. |F|^s / (s! N)); the m! -> s! duplicate saving.
  V5_fullgroup131  n=131 decomposition probability uses #E = 4r (baseline
                   still uses r).
  V6_LA3           LA = 3 * m * K^2 (Wiedemann: 3K matvecs).
  V7_K_eq_F_LA3    V1 and V6 together (most IC-pessimistic constants).
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, asdict, replace

import mpmath as mp

mp.mp.dps = 60

R131 = 680564733841876926932320129493409985129
NS = [97, 109, 131, 163, 191, 233, 239, 283, 409, 571]
MS = list(range(2, 17))
RHO_CONST = mp.mpf("0.886")
FROB_THRESHOLD_131 = mp.mpf("60.8090")
EPS_WARN = mp.mpf("1e-9")


def log2(x) -> mp.mpf:
    return mp.log(mp.mpf(x), 2)


def lse2(*xs) -> mp.mpf:
    """log2(sum 2^x) for the given log2 values."""
    xs = [mp.mpf(x) for x in xs if x is not None]
    mx = max(xs)
    return mx + log2(mp.fsum(mp.power(2, x - mx) for x in xs))


LOG2_FACT = {k: log2(math.factorial(k)) for k in range(0, 40)}


@dataclass(frozen=True)
class Model:
    name: str
    neg_half: bool = True          # K = |F|/2
    rc: str = "expected"           # expected | capped | truncated
    la_const: int = 1
    build_charged: bool = False
    fullgroup131: bool = False


PRIMARY = Model("PRIMARY")
VARIANTS = [
    PRIMARY,
    replace(PRIMARY, name="V1_K_eq_F", neg_half=False),
    replace(PRIMARY, name="V2_prob_capped", rc="capped"),
    replace(PRIMARY, name="V3_build_charged", build_charged=True),
    replace(PRIMARY, name="V4_truncated", rc="truncated"),
    replace(PRIMARY, name="V5_fullgroup131", fullgroup131=True),
    replace(PRIMARY, name="V6_LA3", la_const=3),
    replace(PRIMARY, name="V7_K_eq_F_LA3", neg_half=False, la_const=3),
]


def group_bits(n: int) -> mp.mpf:
    """log2 N used for the rho baseline (as directed)."""
    return log2(R131) if n == 131 else mp.mpf(n)


def decomp_bits(n: int, model: Model) -> mp.mpf:
    """log2 of the group size a random m-sum is spread over (lambda)."""
    if n == 131 and model.fullgroup131:
        return log2(4 * R131)
    return group_bits(n)


def baseline_bits(n: int) -> mp.mpf:
    return log2(RHO_CONST) + group_bits(n) / 2


def cell(n: int, m: int, d: int, s: int, model: Model) -> dict:
    LN = decomp_bits(n, model)
    lf = LOG2_FACT[m]
    K = mp.mpf(d - 1) if model.neg_half else mp.mpf(d)
    lam = d * m - lf - LN                      # log2 lambda
    if model.rc == "expected":
        per_rel = lf + LN - d * s              # log2(m! N / |F|^s)
        rc = K + max(per_rel, mp.mpf(0))
    elif model.rc == "truncated":
        per_rel = LOG2_FACT[s] + LN - d * s
        rc = K + max(per_rel, mp.mpf(0))
    elif model.rc == "capped":
        lam_lin = mp.power(2, lam)
        P = -mp.expm1(-lam_lin)                # 1 - exp(-lambda)
        trials = -log2(P)
        rc = K + trials + d * (m - s)
    else:
        raise ValueError(model.rc)
    la = log2(model.la_const * m) + 2 * K
    build = mp.mpf(d * s) if model.build_charged else None
    total = lse2(rc, la, build)
    calls = K - lam                            # log2(# full oracle calls)
    return {
        "n": n, "m": m, "d": d, "s": s,
        "store_bits": d * s,
        "oracle_time_bits": d * (m - s),
        "log2_lambda": float(lam),
        "log2_full_oracle_calls": float(calls),
        "rc_bits": float(rc), "la_bits": float(la),
        "build_bits": None if build is None else float(build),
        "total_bits": total,
        "store_exceeds_group": d * s > float(group_bits(n)),
    }


def scan(n: int, m: int, model: Model):
    B = baseline_bits(n)
    best_store = None
    best_cells = []
    unconstrained = None
    for s in range(0, m // 2 + 1):
        for d in range(1, n):
            c = cell(n, m, d, s, model)
            if unconstrained is None or c["total_bits"] < unconstrained["total_bits"]:
                unconstrained = c
            if c["total_bits"] < B:
                st = c["store_bits"]
                if best_store is None or st < best_store:
                    best_store, best_cells = st, [c]
                elif st == best_store:
                    best_cells.append(c)
    best_cells.sort(key=lambda c: c["total_bits"])
    return B, best_store, best_cells, unconstrained


def fmt(c: dict | None, B) -> dict | None:
    if c is None:
        return None
    out = dict(c)
    out["total_bits"] = float(c["total_bits"])
    out["margin_below_baseline_bits"] = float(B - c["total_bits"])
    out["store_excess_over_baseline_bits"] = float(c["store_bits"] - B)
    out["near_tie_warning"] = bool(abs(B - c["total_bits"]) < EPS_WARN)
    return out


def run_model(model: Model) -> dict:
    res = {"model": asdict(model), "per_n": {}}
    for n in NS:
        B = baseline_bits(n)
        rows = []
        for m in MS:
            _, st, cells, unc = scan(n, m, model)
            rows.append({
                "m": m,
                "min_store_bits": st,
                "cell": fmt(cells[0], B) if cells else None,
                "tied_cells": [(c["d"], c["s"], float(c["total_bits"])) for c in cells],
                "unconstrained_min_total": fmt(unc, B),
            })
        feas = [r for r in rows if r["min_store_bits"] is not None]
        if feas:
            ms = min(r["min_store_bits"] for r in feas)
            argm = [r["m"] for r in feas if r["min_store_bits"] == ms]
            # among tied m, the reported cell is the one with the lowest total
            best_row = min((r for r in feas if r["min_store_bits"] == ms),
                           key=lambda r: r["cell"]["total_bits"])
            summary = {
                "minimising_m": argm,
                "min_store_bits": ms,
                "cell_at_min": best_row["cell"],
                "store_excess_over_baseline_bits": float(ms - B),
            }
        else:
            summary = {"minimising_m": [], "min_store_bits": None,
                       "cell_at_min": None,
                       "store_excess_over_baseline_bits": None}
        res["per_n"][str(n)] = {
            "baseline_bits": float(B),
            "N_bits_baseline": float(group_bits(n)),
            "N_bits_decomposition": float(decomp_bits(n, model)),
            "summary": summary,
            "rows": rows,
        }
    # n = 131 unconstrained-store question
    rows131 = res["per_n"]["131"]["rows"]
    below = [r["m"] for r in rows131
             if r["unconstrained_min_total"]["total_bits"] < float(FROB_THRESHOLD_131)]
    res["n131_unconstrained"] = {
        "threshold_bits": float(FROB_THRESHOLD_131),
        "smallest_m_strictly_below": min(below) if below else None,
        "all_m_below": below,
        "min_total_by_m": {r["m"]: {
            "total_bits": r["unconstrained_min_total"]["total_bits"],
            "d": r["unconstrained_min_total"]["d"],
            "s": r["unconstrained_min_total"]["s"],
            "store_bits": r["unconstrained_min_total"]["store_bits"],
            "store_exceeds_group": r["unconstrained_min_total"]["store_exceeds_group"],
        } for r in rows131},
    }
    # m = 3 total as a function of d at n = 131 (best s for each d, and s = 1)
    m3 = []
    for d in range(1, 131):
        cs = [cell(131, 3, d, s, model) for s in (0, 1)]
        best = min(cs, key=lambda c: c["total_bits"])
        m3.append({"d": d,
                   "total_s0": float(cs[0]["total_bits"]),
                   "total_s1": float(cs[1]["total_bits"]),
                   "best_s": best["s"], "best_total": float(best["total_bits"])})
    res["n131_m3_total_vs_d"] = m3
    return res


def continuous_min_store(n: int, m: int, model: Model):
    """Real-valued d relaxation: infimum of s*d over s and real d in [1, n-1]
    with total(d) < B.  total(d) = RC(d) + LA(d) with RC non-increasing and LA
    increasing in d, so the feasible set for each s is an interval; its left
    end is found by bisection after locating the minimiser by golden search."""
    B = baseline_bits(n)

    def tot(d, s):
        LN = decomp_bits(n, model)
        lf = LOG2_FACT[m]
        K = d - 1 if model.neg_half else d
        if model.rc == "expected":
            rc = K + max(lf + LN - d * s, mp.mpf(0))
        elif model.rc == "truncated":
            rc = K + max(LOG2_FACT[s] + LN - d * s, mp.mpf(0))
        else:
            raise ValueError("continuous relaxation only for uncapped models")
        la = log2(model.la_const * m) + 2 * K
        return lse2(rc, la)

    best = None
    for s in range(2, m // 2 + 1):
        lo, hi = mp.mpf(1), mp.mpf(n - 1)
        a, b = lo, hi
        gr = (mp.sqrt(5) - 1) / 2
        for _ in range(200):
            c1 = b - gr * (b - a)
            c2 = a + gr * (b - a)
            if tot(c1, s) < tot(c2, s):
                b = c2
            else:
                a = c1
        dstar = (a + b) / 2
        if not tot(dstar, s) < B:
            continue
        L, R = lo, dstar
        if tot(L, s) < B:
            dcross = L
        else:
            for _ in range(200):
                mid = (L + R) / 2
                if tot(mid, s) < B:
                    R = mid
                else:
                    L = mid
            dcross = R
        st = s * dcross
        if best is None or st < best[0]:
            best = (st, s, dcross)
    if best is None:
        return None
    return {"store_bits": float(best[0]), "s": best[1], "d": float(best[2]),
            "excess_bits": float(best[0] - B)}


def frob_check():
    """Identify the 60.8090-bit figure: sqrt(pi r / 4) / sqrt(131)."""
    exact = log2(mp.sqrt(mp.pi * R131 / 4) / mp.sqrt(131))
    with886 = log2(RHO_CONST * mp.sqrt(R131) / mp.sqrt(131))
    return {"log2_sqrt(pi*r/4)/sqrt(131)": float(exact),
            "log2_0.886*sqrt(r)/sqrt(131)": float(with886)}


def main(out_path: str):
    out = {
        "task": "TASK-20260928-4e5c26",
        "note": "blind re-derivation; see blind_derivation.md for the model",
        "log2_r131": float(log2(R131)),
        "log2_0.886": float(log2(RHO_CONST)),
        "frobenius_threshold_identification": frob_check(),
        "models": {},
    }
    for model in VARIANTS:
        out["models"][model.name] = run_model(model)
    # continuous-d relaxation (PRIMARY and V1 only)
    out["continuous_relaxation"] = {}
    for model in (PRIMARY, VARIANTS[1]):
        tab = {}
        for n in NS:
            rows = {m: continuous_min_store(n, m, model) for m in MS}
            feas = {m: v for m, v in rows.items() if v is not None}
            mbest = min(feas, key=lambda k: feas[k]["store_bits"]) if feas else None
            tab[str(n)] = {"by_m": rows, "argmin_m": mbest,
                           "min": feas.get(mbest) if mbest else None}
        out["continuous_relaxation"][model.name] = tab
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    # flat CSV of PRIMARY per-(n, m) minimum-store cells
    csv_path = out_path.rsplit(".", 1)[0] + "_primary_cells.csv"
    with open(csv_path, "w") as fh:
        fh.write("n,m,baseline_bits,min_store_bits,d,s,total_bits,rc_bits,la_bits,"
                 "margin_bits,store_excess_bits,log2_lambda,log2_full_oracle_calls,"
                 "oracle_time_bits,tied_cells\n")
        for n in NS:
            p = out["models"]["PRIMARY"]["per_n"][str(n)]
            for r in p["rows"]:
                c = r["cell"]
                if c is None:
                    fh.write(f"{n},{r['m']},{p['baseline_bits']:.6f},,,,,,,,,,,,\n")
                    continue
                ties = ";".join(f"d{t[0]}s{t[1]}" for t in r["tied_cells"])
                fh.write(f"{n},{r['m']},{p['baseline_bits']:.6f},{c['store_bits']},{c['d']},"
                         f"{c['s']},{c['total_bits']:.6f},{c['rc_bits']:.6f},"
                         f"{c['la_bits']:.6f},{c['margin_below_baseline_bits']:.6f},"
                         f"{c['store_excess_over_baseline_bits']:.6f},{c['log2_lambda']:.4f},"
                         f"{c['log2_full_oracle_calls']:.4f},{c['oracle_time_bits']},{ties}\n")
    for name, tab in out["continuous_relaxation"].items():
        print(f"== continuous-d relaxation {name}")
        for n in NS:
            t = tab[str(n)]
            mn = t["min"]
            print(f"  n={n:3d} argmin_m={t['argmin_m']} "
                  + (f"store={mn['store_bits']:.4f} s={mn['s']} d={mn['d']:.4f} "
                     f"excess={mn['excess_bits']:.4f}" if mn else "none"))
    # compact console summary
    for name, res in out["models"].items():
        print(f"== {name}")
        for n in NS:
            p = res["per_n"][str(n)]
            sm = p["summary"]
            if sm["min_store_bits"] is None:
                print(f"  n={n:3d} B={p['baseline_bits']:.4f}  NO feasible cell")
                continue
            c = sm["cell_at_min"]
            print(f"  n={n:3d} B={p['baseline_bits']:.4f} m*={sm['minimising_m']} "
                  f"store={sm['min_store_bits']} (m={c['m']},d={c['d']},s={c['s']}) "
                  f"total={c['total_bits']:.4f} rc={c['rc_bits']:.4f} "
                  f"la={c['la_bits']:.4f} excess={sm['store_excess_over_baseline_bits']:.4f}")
        u = res["n131_unconstrained"]
        print(f"  n=131 unconstrained: smallest m < {u['threshold_bits']}: "
              f"{u['smallest_m_strictly_below']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "blind_rederived.json")
