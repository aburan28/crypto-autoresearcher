#!/usr/bin/env python3
"""TASK-20260928-a1c7e5 -- review joint J1 (the cost-model algebra) of
REVIEW-SEMBIN-20260928-04ec3c.

Independent re-derivation of EXP-SEMBIN-04ec3c's cost model from the frozen
`cost_model` block of experiments/EXP-SEMBIN-04ec3c/specification.yaml ALONE.
This file does NOT import the producer driver. It reads the producer's
raw-result.json only to compare against it.

Sections (each prints a labelled block; `--json` writes everything):
  S0  the model as written, re-implemented; row-by-row agreement with the driver
  S1  closed form #1  relations x trials x oracle = m! * 2^(n + d(1-s))
  S2  closed form #2  store-free MITM = 2^(2n/(floor(m/2)+1))
  S3  closed form #3  min store = S/(S-1) * (n/2 + log2 m!)
  S4  weak point 1: is the excess-relation term O(1) in m?  (exact rank sim)
  S5  weak point 2: odd m  -- does any odd m beat both even neighbours?
  S6  the table-construction term the model omits, and what charging it does
  S7  cofactor sensitivity: the driver's N = 2^n at every n != 131

Standard library only; deterministic (S4 uses a fixed seed and says so).
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
RAW = REPO / "experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/raw-result.json"

# ---------------------------------------------------------------------------
# parameters taken from the contract (cost_model, procedure, baseline)
# ---------------------------------------------------------------------------
DEGREES = [97, 109, 131, 163, 191, 233, 239, 283, 409, 571]   # 11 listed, 163 twice
VOW_CONST = math.log2(0.886)            # cost_model.baseline: W = 0.886 * 2^(n/2)
PUBLISHED_131 = 60.8090                 # cost_model.baseline, second column
# ECC2K-130 prime subgroup order, as the driver states it (I did not re-derive
# this integer; I only check it is a 129-bit prime-sized number, see S7).
R131 = 680564733841876926932320129493409985129
BUDGETS = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]


def L(m: int) -> float:
    """log2 m!  (exact, via lgamma)."""
    return math.lgamma(m + 1) / math.log(2)


def lse(*xs: float) -> float:
    """log2(sum 2^x)."""
    mx = max(xs)
    return mx + math.log2(sum(2.0 ** (x - mx) for x in xs))


def logN(n: int, convention: str) -> float:
    """log2 of the group order the yield term divides by.

    'driver'  : r for n = 131, n elsewhere (what the producer did)
    'twon'    : n everywhere (the J1 closed forms as written)
    'h2','h4' : n - 1 / n - 2 at every n != 131, r at 131 (true cofactor range
                for an ordinary binary curve, which always has a 2-torsion point)
    """
    if convention == "twon":
        return float(n)
    if n == 131:
        return math.log2(R131)
    if convention == "driver":
        return float(n)
    if convention == "h2":
        return n - 1.0
    if convention == "h4":
        return n - 2.0
    raise ValueError(convention)


def cell(n, m, d, s, conv="driver", charge_build=False):
    """One cell of the model, re-derived from cost_model.

    relations  = |F| = 2^d
    trials/rel = 1/p = m! N / |F|^m
    oracle     = |F|^(m-s) time, |F|^s store       (MITM_CAPPED; s=0 is ENUM)
    linalg     = |F|^2 time
    """
    nn = logN(n, conv)
    stage1 = d + (L(m) + nn - m * d) + (m - s) * d          # = L + nn + d(1-s)
    la = 2.0 * d
    store = max(s * d, d + math.log2(m))
    terms = [stage1, la]
    if charge_build and s >= 1:
        # The MITM table holds |F|^s entries (the model's own store count); each
        # entry is a group element that must be computed before any probe can
        # hit it. Time >= entries written. Charged ONCE (target-independent).
        terms.append(s * d)
    total = lse(*terms)
    vow = nn / 2.0 + VOW_CONST
    return dict(n=n, m=m, d=d, s=s, stage1=stage1, la=la, store=store,
                total=total, vow=vow, margin_vow=total - vow,
                margin_pub=(total - PUBLISHED_131) if n == 131 else None)


def degenerate(n, m, d, conv="driver"):
    nn = logN(n, conv)
    return (nn / m < 2.0) or (m > n) or (d < 1.0)


def grid(n, step=0.25):
    d = 1.0
    while d <= n + 1e-9:
        yield d
        d += step


def s_capped(m, d, B):
    S = m // 2
    if B is None:
        return S
    return min(S, max(0, int(B // d)))


def best_over_d(n, m, B, conv="driver", charge_build=False, step=0.25):
    best = None
    for d in grid(n, step):
        c = cell(n, m, d, s_capped(m, d, B), conv, charge_build)
        if best is None or c["total"] < best["total"]:
            best = c
    return best


def min_store_first_cross(n, m, conv="driver", charge_build=False, step=0.05,
                          baseline="vow"):
    """Smallest-store sub-baseline cell under full MITM (s = floor(m/2)).
    Sweeps d upward; store = max(Sd, d+log2 m) is increasing in d, so the first
    crossing is the minimum store. Returns None if none."""
    S = m // 2
    d = 1.0
    while d <= n + 1e-9:
        c = cell(n, m, d, S, conv, charge_build)
        tgt = c["vow"] if baseline == "vow" else PUBLISHED_131
        if c["total"] < tgt and not degenerate(n, m, d, conv):
            return c
        d += step
    return None


# ---------------------------------------------------------------------------
def S0_agreement(raw):
    """Re-implement the model as written and compare every reported cell."""
    out = {"mitm_store_free": 0, "mitm_capped": 0, "min_store": 0,
           "max_abs_total_diff": 0.0, "max_abs_store_diff": 0.0,
           "max_abs_d_diff": 0.0, "mismatches": []}
    for c in raw["mitm_store_free"]:
        mine = best_over_d(c["n"], c["m"], None)
        dt = abs(round(mine["total"], 4) - c["log2_total"])
        dd = abs(mine["d"] - c["d"])
        out["max_abs_total_diff"] = max(out["max_abs_total_diff"], dt)
        out["max_abs_d_diff"] = max(out["max_abs_d_diff"], dd)
        out["mitm_store_free"] += 1
        if dt > 1e-3 or dd > 1e-9:
            out["mismatches"].append(("free", c["n"], c["m"], c["d"], mine["d"]))
    for c in raw["mitm_capped"]:
        mine = best_over_d(c["n"], c["m"], c["budget_log2_entries"])
        dt = abs(round(mine["total"], 4) - c["log2_total"])
        ds = abs(round(mine["store"], 4) - c["log2_store_entries"])
        out["max_abs_total_diff"] = max(out["max_abs_total_diff"], dt)
        out["max_abs_store_diff"] = max(out["max_abs_store_diff"], ds)
        out["mitm_capped"] += 1
        if dt > 1e-3 or ds > 1e-3:
            out["mismatches"].append(("capped", c["n"], c["m"],
                                      c["budget_log2_entries"]))
    for r in raw["min_store_for_subrho"]:
        mine = min_store_first_cross(r["n"], r["m"])
        out["min_store"] += 1
        if (mine is None) != (not r["reachable"]):
            out["mismatches"].append(("minstore-reach", r["n"], r["m"]))
        elif mine is not None:
            ds = abs(round(mine["store"], 4) - r["log2_store_entries"])
            out["max_abs_store_diff"] = max(out["max_abs_store_diff"], ds)
            if ds > 1e-3:
                out["mismatches"].append(("minstore", r["n"], r["m"],
                                          r["log2_store_entries"], mine["store"]))
    # sub-rho counts as the driver defines them
    charged = {(c["n"], c["m"], c["budget_log2_entries"]) for c in raw["mitm_capped"]
               if c["beats_vow"] and not c["degenerate"]}
    free = {(c["n"], c["m"]) for c in raw["mitm_store_free"]
            if c["beats_vow"] and not c["degenerate"]}
    out["subrho_capped_triples"] = len(charged)
    out["subrho_store_free_distinct_nm"] = len(free)
    out["subrho_store_free_as_driver_counts_it"] = len(free) * len(BUDGETS)
    return out


def S1_closed_form_1(raw):
    """relations x trials x oracle vs m! * 2^(n + d(1-s))."""
    diffs = {}
    for c in raw["mitm_capped"]:
        cf = L(c["m"]) + c["n"] + c["d"] * (1 - c["s_tabulated"])
        diffs.setdefault(c["n"], set()).add(round(c["log2_relation_phase"] - cf, 3))
    return {str(n): sorted(v) for n, v in diffs.items()}


def S2_closed_form_2(raw):
    """store-free MITM total vs 2^(2n/(floor(m/2)+1)).

    Balanced derivation (mine): stage1 = L + N + d(1-S), LA = 2d, equal at
    d* = (N + L)/(S+1); total = 2(N+L)/(S+1) + 1 (two equal terms summed).
    Valid while S >= 1 and d* is interior."""
    rows = []
    for c in raw["mitm_store_free"]:
        n, m = c["n"], c["m"]
        S = m // 2
        nn = logN(n, "driver")
        cf_plan = 2.0 * n / (S + 1)
        cf_mine = 2.0 * (nn + L(m)) / (S + 1) + 1.0
        rows.append(dict(n=n, m=m, driver_total=c["log2_total"],
                         plan_closed_form=round(cf_plan, 3),
                         my_closed_form=round(cf_mine, 3),
                         driver_minus_plan=round(c["log2_total"] - cf_plan, 3),
                         driver_minus_mine=round(c["log2_total"] - cf_mine, 3)))
    return rows


def S3_closed_form_3(raw):
    """min store vs S/(S-1)*(n/2 + log2 m!).

    Exact infimum (mine), from stage1 < vow and store = S d:
      d (S-1) > N/2 + L + |log2 0.886|  =>  store > S/(S-1)*(N/2 + L + 0.1747)
    (ignores the linear-algebra term, which the driver's log-sum includes and
    which is >= 20 bits below stage1 at every minimum-store cell here)."""
    rows = []
    for r in raw["min_store_for_subrho"]:
        n, m = r["n"], r["m"]
        S = m // 2
        if S < 2:
            continue
        nn = logN(n, "driver")
        plan = S / (S - 1) * (n / 2.0 + L(m))
        mine = S / (S - 1) * (nn / 2.0 - VOW_CONST + L(m))
        lin_ok = (mine / S) < (nn / 2.0 + VOW_CONST) / 2.0   # need 2d < vow
        rows.append(dict(n=n, m=m, reachable=r["reachable"],
                         driver_store=r.get("log2_store_entries"),
                         plan_cf=round(plan, 3), my_cf=round(mine, 3),
                         la_constraint_admits=lin_ok,
                         driver_minus_plan=(None if not r["reachable"] else
                                            round(r["log2_store_entries"] - plan, 3)),
                         driver_minus_mine=(None if not r["reachable"] else
                                            round(r["log2_store_entries"] - mine, 3))))
    return rows


# ---------------------------------------------------------------------------
# S4: excess relations. Exact rank computation over GF(q), q prime.
# ---------------------------------------------------------------------------
Q = 2_147_483_647   # 2^31 - 1, prime; stands in for Z/NZ (N prime)


def rows_until_dependency(nF: int, m: int, rng: random.Random, two_col_ab=True):
    """Add random relations until one is a linear combination of earlier ones
    (the first nontrivial left-kernel vector of the relation matrix).

    Each relation: m DISTINCT factor-base columns with random nonzero
    coefficients (the multiplicities of a decomposition are 1 generically;
    signs/coefficients are random here to avoid accidental structure).

    If two_col_ab: the DLP needs a kernel vector lambda with sum lambda_i b_i
    != 0, i.e. a dependency among FACTOR-BASE parts that is NOT also a
    dependency among the (b_i) -- equivalently, rank of [M | b] must be
    exceeded. We count rows until rank(M) < #rows AND the kernel vector has
    nonzero b-projection: implemented as rows until rank([M|b]) < #rows+... we
    simply track rank(M) and rank([M|b]) and stop at the first row count where
    a kernel vector of M exists that is not a kernel vector of [M|b], i.e.
    rows - rank(M) > rows - rank([M|b]).
    """
    basis = {}          # pivot col -> row (dict col->val), reduced
    basis_ab = {}
    rankM = 0
    rankMb = 0
    rows = 0
    ncols = nF

    def reduce_insert(vec, bas):
        v = dict(vec)
        while v:
            piv = min(v)
            if piv in bas:
                brow = bas[piv]
                f = v[piv]
                for col, val in brow.items():
                    nv = (v.get(col, 0) - f * val) % Q
                    if nv:
                        v[col] = nv
                    else:
                        v.pop(col, None)
            else:
                inv = pow(v[piv], Q - 2, Q)
                v = {c: (x * inv) % Q for c, x in v.items()}
                bas[piv] = v
                return True
        return False

    while True:
        cols = rng.sample(range(ncols), m)
        vec = {c: rng.randrange(1, Q) for c in cols}
        b = rng.randrange(1, Q)
        rows += 1
        if reduce_insert(vec, basis):
            rankM += 1
        vec_b = dict(vec)
        vec_b[ncols] = b                  # the b-column
        if reduce_insert(vec_b, basis_ab):
            rankMb += 1
        kerM = rows - rankM
        kerMb = rows - rankMb
        if kerM > kerMb:                  # a kernel vector with sum lambda b != 0
            return rows
        if rows > ncols + 10:
            return rows


def S4_excess(seed=20260930, nF_list=(32, 64, 96), trials=30,
              m_list=(2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16)):
    rng = random.Random(seed)
    out = []
    for nF in nF_list:
        for m in m_list:
            if m > nF:
                continue
            xs = [rows_until_dependency(nF, m, rng) for _ in range(trials)]
            # fixed point of x = 1 - exp(-m x): fraction of columns touched
            x = 1.0
            for _ in range(200):
                x = 1.0 - math.exp(-m * x)
            out.append(dict(nF=nF, m=m, trials=trials,
                            mean_rows=round(sum(xs) / len(xs), 2),
                            max_rows=max(xs), min_rows=min(xs),
                            max_excess_over_F=max(xs) - nF,
                            touched_fraction_prediction=round(x, 5)))
    return {"seed": seed, "q": Q, "rows": out,
            "deterministic_bound": "rows needed <= |F| + 2 for ANY m: |F|+1 "
            "vectors in a |F|-dim space are dependent; one more guarantees a "
            "dependency whose b-projection is nonzero unless b lies in the "
            "row space image (probability ~1/q)."}


# ---------------------------------------------------------------------------
def S5_odd_m(raw):
    by = {}
    for r in raw["min_store_for_subrho"]:
        by[(r["n"], r["m"])] = r.get("log2_store_entries") if r["reachable"] else None
    rows, violations = [], []
    for n in DEGREES:
        for m in range(3, 16, 2):
            lo, mid, hi = by.get((n, m - 1)), by.get((n, m)), by.get((n, m + 1))
            beats_lower = (mid is not None) and (lo is None or mid < lo)
            beats_both = beats_lower and (hi is None or mid < hi)
            rows.append(dict(n=n, m=m, store_m_minus_1=lo, store_m=mid,
                             store_m_plus_1=hi, beats_lower_even=beats_lower,
                             beats_both_even=beats_both))
            if beats_both:
                violations.append((n, m))
    # the same question under MITM_CAPPED at every budget: best total per (n,m,B)
    capped = {(c["n"], c["m"], c["budget_log2_entries"]): c["log2_total"]
              for c in raw["mitm_capped"]}
    odd_beats_lower_capped = []
    for (n, m, B), t in capped.items():
        if m % 2 == 1 and (n, m - 1, B) in capped and t < capped[(n, m - 1, B)] - 1e-9:
            odd_beats_lower_capped.append((n, m, B, t, capped[(n, m - 1, B)]))
    # analytic: store_min(2S+1) - store_min(2S) = S/(S-1) * log2(2S+1)
    analytic = [dict(m=2 * S + 1, S=S,
                     predicted_gap_bits=round(S / (S - 1) * math.log2(2 * S + 1), 3))
                for S in range(2, 8)]
    measured_gap = []
    for n in DEGREES:
        for S in range(2, 8):
            a, b = by.get((n, 2 * S)), by.get((n, 2 * S + 1))
            if a is not None and b is not None:
                measured_gap.append(dict(n=n, m=2 * S + 1, gap=round(b - a, 3),
                                         predicted=round(S / (S - 1) *
                                                         math.log2(2 * S + 1), 3)))
    return {"rows": rows, "odd_m_beating_both_even_neighbours": violations,
            "odd_m_beating_lower_even_under_capped": odd_beats_lower_capped,
            "analytic_gap": analytic, "measured_gap_vs_analytic": measured_gap}


def S5b_odd_m_if_s_uncapped():
    """Sensitivity, NOT the frozen model. The frozen model caps s at floor(m/2)
    ("time is the larger side, store is the smaller"). The only reason to cap
    s there is that tabulating MORE than half makes the table build dominate --
    a time term the frozen model never charges (S6). If the cap is lifted to
    s = ceil(m/2) at odd m, does an odd m then beat both even neighbours?"""
    out = []
    for n in DEGREES:
        nn = logN(n, "driver")
        T = nn / 2.0 - VOW_CONST

        def store(m, s):
            return s / (s - 1) * (T + L(m)) if s >= 2 else None
        for m in range(5, 16, 2):
            even_lo = store(m - 1, (m - 1) // 2)
            even_hi = store(m + 1, (m + 1) // 2)
            odd_capped = store(m, m // 2)
            odd_uncapped = store(m, (m + 1) // 2)
            out.append(dict(n=n, m=m, even_lo=round(even_lo, 2),
                            odd_frozen_cap=round(odd_capped, 2),
                            odd_s_ceil=round(odd_uncapped, 2),
                            even_hi=round(even_hi, 2),
                            odd_s_ceil_beats_both=odd_uncapped < min(even_lo, even_hi)))
    return out


# ---------------------------------------------------------------------------
def S6_build_term(raw):
    """What the model omits: the |F|^s table must be written before it is read."""
    out = {}
    # (a) in the producer's own reported cells
    sub = [c for c in raw["mitm_capped"] if c["beats_vow"] and not c["degenerate"]]
    free = [c for c in raw["mitm_store_free"] if c["beats_vow"] and not c["degenerate"]]
    ms = [r for r in raw["min_store_for_subrho"] if r["reachable"]]
    out["reported_subrho_capped_cells"] = len(sub)
    out["of_which_store_exceeds_total"] = sum(c["log2_store_entries"] > c["log2_total"]
                                             for c in sub)
    out["min_gap_store_minus_total_capped"] = round(min(
        c["log2_store_entries"] - c["log2_total"] for c in sub), 4)
    out["reported_subrho_store_free_cells_distinct"] = len(free)
    out["of_which_store_exceeds_total_free"] = sum(
        c["log2_store_entries"] > c["log2_total"] for c in free)
    out["min_store_rows_reachable"] = len(ms)
    out["of_which_store_exceeds_total_minstore"] = sum(
        r["log2_store_entries"] > r["log2_total"] for r in ms)
    # (b) re-run the whole sweep with the build term charged
    recount = {"capped": 0, "free": 0, "published_131": 0}
    closest = None
    for n in DEGREES:
        for m in range(2, 17):
            for B in BUDGETS + [None]:
                c = best_over_d(n, m, B, charge_build=True)
                if c["total"] < c["vow"] and not degenerate(n, m, c["d"]):
                    recount["capped" if B is not None else "free"] += 1
                if n == 131 and c["margin_pub"] is not None and c["margin_pub"] < 0:
                    recount["published_131"] += 1
                if closest is None or c["margin_vow"] < closest["margin_vow"]:
                    closest = c
    out["subrho_cells_with_build_charged"] = recount
    out["closest_cell_with_build_charged"] = {k: (round(v, 4) if isinstance(v, float)
                                                  else v) for k, v in closest.items()}
    # (c) per-degree corrected minimum total, and its analytic floor
    per = {}
    for n in DEGREES:
        best = None
        for m in range(2, 17):
            c = best_over_d(n, m, None, charge_build=True, step=0.05)
            # also allow s < floor(m/2) explicitly (store-free tradeoff)
            for s in range(0, m // 2 + 1):
                for d in grid(n, 0.25):
                    cc = cell(n, m, d, s, charge_build=True)
                    if cc["total"] < c["total"]:
                        c = cc
            if best is None or c["total"] < best["total"]:
                best = c
        nn = logN(n, "driver")
        per[n] = dict(best_m=best["m"], best_s=best["s"], best_d=best["d"],
                      corrected_min_total=round(best["total"], 3),
                      vow=round(best["vow"], 4),
                      margin_over_vow=round(best["total"] - best["vow"], 3),
                      analytic_floor=round(nn / 2.0, 3))
    out["corrected_min_total_by_degree"] = per
    # (d) P2 under the corrected model at n = 131
    p2 = []
    for m in range(2, 17):
        c = best_over_d(131, m, None, charge_build=True, step=0.05)
        p2.append(dict(m=m, corrected_total=round(c["total"], 3),
                       below_published=c["total"] < PUBLISHED_131,
                       d=round(c["d"], 2), s=c["s"]))
    out["P2_under_build_charged_model_n131"] = p2
    # (e) the named breaking cell
    c_model = cell(131, 8, 26.7, 4)
    c_true = cell(131, 8, 26.7, 4, charge_build=True)
    out["breaking_cell"] = dict(
        n=131, m=8, d=26.7, s=4,
        model_total=round(c_model["total"], 4),
        model_store=round(c_model["store"], 4),
        charged_total=round(c_true["total"], 4),
        vow=round(c_model["vow"], 4), published=PUBLISHED_131,
        difference_bits=round(c_true["total"] - c_model["total"], 4))
    return out


# ---------------------------------------------------------------------------
def S7_cofactor(raw):
    """The driver uses N = 2^n at every n != 131. An ordinary binary curve
    y^2 + xy = x^3 + a x^2 + b always has the 2-torsion point (0, sqrt b), so
    #E is even and the prime subgroup order is at most #E/2 ~ 2^(n-1)."""
    out = {"r131_bits": R131.bit_length(),
           "log2_r131": round(math.log2(R131), 6)}
    for conv in ("driver", "h2", "h4"):
        sub_le80 = 0
        sub_capped = 0
        minstore = {}
        for n in DEGREES:
            for m in range(2, 17):
                for B in BUDGETS:
                    c = best_over_d(n, m, B, conv=conv)
                    if c["total"] < c["vow"] and not degenerate(n, m, c["d"], conv):
                        sub_capped += 1
                        if B <= 80:
                            sub_le80 += 1
            best = None
            for m in range(2, 17):
                c = min_store_first_cross(n, m, conv=conv)
                if c is not None and (best is None or c["store"] < best["store"]):
                    best = c
            minstore[n] = None if best is None else dict(
                m=best["m"], store=round(best["store"], 2),
                excess=round(best["store"] - best["vow"], 2))
        out[conv] = dict(subrho_capped=sub_capped, subrho_budget_le_80=sub_le80,
                         min_store_by_degree=minstore)
    # the two baseline columns at n = 131 under each reading
    out["n131_columns"] = {
        "vow_as_contract_writes_it_0.886*2^(n/2)": round(131 / 2 + VOW_CONST, 4),
        "vow_as_driver_computes_it_0.886*sqrt(r)": round(math.log2(R131) / 2 + VOW_CONST, 4),
        "published": PUBLISHED_131,
        "gap_contract_reading": round(131 / 2 + VOW_CONST - PUBLISHED_131, 4),
        "gap_driver_reading": round(math.log2(R131) / 2 + VOW_CONST - PUBLISHED_131, 4),
        "sqrt_pi_r_over_4n": round(0.5 * math.log2(math.pi * R131 / (4 * 131)), 4),
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--skip-sim", action="store_true")
    a = ap.parse_args()
    raw = json.loads(RAW.read_text())
    res = {}
    res["S0_agreement_with_driver"] = S0_agreement(raw)
    res["S1_closed_form_1_offsets_by_degree"] = S1_closed_form_1(raw)
    res["S2_closed_form_2"] = S2_closed_form_2(raw)
    res["S3_closed_form_3"] = S3_closed_form_3(raw)
    res["S4_excess"] = None if a.skip_sim else S4_excess()
    res["S5_odd_m"] = S5_odd_m(raw)
    res["S5b_odd_m_if_s_uncapped"] = S5b_odd_m_if_s_uncapped()
    res["S6_build_term"] = S6_build_term(raw)
    res["S7_cofactor"] = S7_cofactor(raw)
    text = json.dumps(res, indent=1, default=str)
    if a.json:
        Path(a.json).write_text(text + "\n")
    # compact console summary
    s0 = res["S0_agreement_with_driver"]
    print("S0", {k: v for k, v in s0.items() if k != "mismatches"},
          "mismatches:", len(s0["mismatches"]), s0["mismatches"][:5])
    print("S1", res["S1_closed_form_1_offsets_by_degree"])
    for r in res["S2_closed_form_2"]:
        if r["n"] == 131:
            print("S2", r)
    for r in res["S3_closed_form_3"]:
        if r["n"] in (97, 131, 571) and r["m"] in (8, 9, 10, 12, 14):
            print("S3", r)
    if res["S4_excess"]:
        for r in res["S4_excess"]["rows"]:
            print("S4", r)
    s5 = res["S5_odd_m"]
    print("S5 violations:", s5["odd_m_beating_both_even_neighbours"],
          "capped odd<lower:", len(s5["odd_m_beating_lower_even_under_capped"]))
    for g in s5["measured_gap_vs_analytic"]:
        if g["n"] == 131:
            print("S5 gap", g)
    for r in res["S5b_odd_m_if_s_uncapped"]:
        if r["n"] in (97, 131):
            print("S5b", r)
    s6 = res["S6_build_term"]
    for k, v in s6.items():
        if k != "P2_under_build_charged_model_n131":
            print("S6", k, v)
    print("S6 P2@131", [(r["m"], r["corrected_total"], r["below_published"])
                        for r in s6["P2_under_build_charged_model_n131"]])
    s7 = res["S7_cofactor"]
    for k in ("driver", "h2", "h4"):
        print("S7", k, s7[k]["subrho_capped"], s7[k]["subrho_budget_le_80"],
              {n: v for n, v in s7[k]["min_store_by_degree"].items() if n in (97, 109, 131)})
    print("S7 n131", s7["n131_columns"], s7["r131_bits"], s7["log2_r131"])


if __name__ == "__main__":
    main()
