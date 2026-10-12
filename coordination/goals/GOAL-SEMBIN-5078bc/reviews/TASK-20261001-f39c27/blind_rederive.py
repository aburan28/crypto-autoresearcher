#!/usr/bin/env python3
"""Blind re-derivation for TASK-20261001-f39c27 (Validator, GOAL-SEMBIN-5078bc).

Written from the TASK STATEMENT and the cost_model block of
experiments/EXP-SEMBIN-04ec3c/specification.yaml (lines 89-138) ONLY. The
producer's code, runs, results, amendments, decisions, corrections, handoff
TASK-20261001-41f6b3 and every other review were not opened before this file,
its output, and blind_derivation.txt were hashed into pre_reveal_hashes.txt.

Quantity (as stated by the task):

    TOTAL(n) = min over m in 2..16, s in 0..floor(m/2), real d of
               log2( 2^PROBE + 2^FILL + 2^LA )

    PROBE = relations * trials_per_relation * oracle_time
            relations           = |F|                    = 2^d
            trials_per_relation = 1/p,  p = |F|^m / (m! * N)
            oracle_time         = |F|^(m-s)   (store |F|^s)
    FILL  = |F|^s        (one operation per table entry)
    LA    = |F|^2
    margin(n) = TOTAL(n) - log2(0.886 * sqrt(N))
        (positive margin = the index-calculus total costs MORE than the rho
         baseline; negative = less)

    N = ell (ECC2K-130 prime subgroup order) at n = 131, N = 2^n otherwise.

Every quantity is handled in log2 ("bits"). Unit: abstract operations exactly
as the statement charges them (one per oracle step, one per table entry, |F|^2
for linear algebra); no conversion to bit operations is made.

Exclusion conventions (the statement says: when
trials_per_relation * relations < 1, flag and exclude the cell):

  C1 (PRIMARY, pointwise): a cell is a point (m, s, d). Points with
     log2(total trials) = L - (m-1) d < 0, L = log2(m!) + log2(N), are
     excluded, i.e. d is restricted to [0, L/(m-1)]. An (m, s) pair is
     FLAGGED when its unconstrained minimiser lies in the excluded region
     (the constraint binds); its reported value is then the constrained
     minimum at the boundary.
  C2 (pairwise): an (m, s) pair whose unconstrained minimiser lies in the
     excluded region is dropped entirely.
  C0 (no exclusion): reported for transparency only, never as the answer.
  C3 (sensitivity, NOT in the statement): additionally require p <= 1,
     i.e. trials_per_relation >= 1, d <= L/m.
  C4 (sensitivity, NOT in the statement): C1 with d restricted to integers.

Lower bound d >= 0 (|F| >= 1) is imposed; the script reports whether it binds
at any global optimum.
"""

import json
import math
import platform
import sys

import mpmath as mp
import sympy

mp.mp.dps = 60

DEGREES = [97, 109, 131, 163, 191, 233, 239, 283, 409, 571]
M_VALUES = list(range(2, 17))
RHO_CONST = mp.mpf("0.886")
# inputs/BAILEY-2009-541-ECC2K130/paper_fulltext.md, Appendix A (line 1096),
# sha256 519f330a963a226ab875e055df499a08a08f799066178372867ef8d023b4d967.
ELL_ECC2K130 = 680564733841876926932320129493409985129
GOLDEN_ITERS = 300
BISECT_ITERS = 300


# ---------------------------------------------------------------- curve check
def koblitz_group_order(n, a):
    """#E_a(F_{2^n}) for E_a: y^2 + x y = x^3 + a x^2 + 1, via Frobenius trace."""
    count = 1  # point at infinity
    for x in (0, 1):
        for y in (0, 1):
            if (y * y + x * y - (x ** 3 + a * x * x + 1)) % 2 == 0:
                count += 1
    t = 2 + 1 - count
    v_prev, v_cur = 2, t  # V_0, V_1 of the Lucas sequence for X^2 - tX + 2
    for _ in range(n - 1):
        v_prev, v_cur = v_cur, t * v_cur - 2 * v_prev
    return 2 ** n + 1 - v_cur, t, count


def miller_rabin(n, bases):
    if n < 2:
        return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def curve_checks():
    order, trace, pts_f2 = koblitz_group_order(131, 0)
    small_primes = list(sympy.primerange(2, 400))
    return {
        "curve": "y^2 + x*y = x^3 + 1 over F_2^131 (Koblitz, a = 0)",
        "points_over_F2": pts_f2,
        "frobenius_trace_over_F2": trace,
        "group_order_F2_131": str(order),
        "group_order_equals_4_ell": order == 4 * ELL_ECC2K130,
        "ell": str(ELL_ECC2K130),
        "ell_bits": ELL_ECC2K130.bit_length(),
        "ell_is_prime_sympy": bool(sympy.isprime(ELL_ECC2K130)),
        "ell_is_prime_miller_rabin_78_bases": miller_rabin(ELL_ECC2K130, small_primes),
        "log2_ell": mp.nstr(mp.log(ELL_ECC2K130, 2), 25),
    }


# ------------------------------------------------------------- cost algebra
def log2N(n):
    return mp.log(ELL_ECC2K130, 2) if n == 131 else mp.mpf(n)


def log2_factorial(m):
    return mp.log(math.factorial(m), 2)


def components(n, m, s, d):
    """All terms in log2, built from their definitions (not the simplified form)."""
    lN = log2N(n)
    lfact = log2_factorial(m)
    log_relations = d                       # |F| = 2^d
    log_p = m * d - (lfact + lN)            # p = |F|^m / (m! N)
    log_trials_per_rel = -log_p             # 1/p
    log_oracle = (m - s) * d                # |F|^(m-s)
    log_store = s * d                       # |F|^s
    probe = log_relations + log_trials_per_rel + log_oracle
    fill = log_store                        # one op per table entry
    la = 2 * d                              # |F|^2
    return {
        "probe": probe,
        "fill": fill,
        "la": la,
        "log2_total_trials": log_relations + log_trials_per_rel,
        "log2_trials_per_relation": log_trials_per_rel,
        "log2_p": log_p,
        "log2_store": log_store,
    }


def lse2(xs):
    mx = max(xs)
    return mx + mp.log(sum(mp.power(2, x - mx) for x in xs), 2)


def total(n, m, s, d):
    c = components(n, m, s, d)
    return lse2([c["probe"], c["fill"], c["la"]])


def simplified_probe(n, m, s, d):
    """Closed form: PROBE = log2(m!) + log2(N) + (1 - s) d."""
    return log2_factorial(m) + log2N(n) + (1 - s) * d


def L_of(n, m):
    return log2_factorial(m) + log2N(n)


# -------------------------------------------------------------- minimisers
def golden_min(f, lo, hi, iters=GOLDEN_ITERS):
    """Golden-section search; valid because f is convex in d (log-sum-exp of affine)."""
    g = (mp.sqrt(5) - 1) / 2
    a, b = mp.mpf(lo), mp.mpf(hi)
    c = b - g * (b - a)
    e = a + g * (b - a)
    fc, fe = f(c), f(e)
    for _ in range(iters):
        if fc <= fe:
            b, e, fe = e, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, e, fe
            e = a + g * (b - a)
            fe = f(e)
    x = (a + b) / 2
    cands = [(f(lo), mp.mpf(lo)), (f(hi), mp.mpf(hi)), (f(x), x)]
    return min(cands, key=lambda t: t[0])


def derivative_root(n, m, s, lo, hi):
    """Independent method: sign of dTOTAL/dd = sign(sum slope_i 2^{x_i}).

    Slopes: PROBE (1 - s), FILL s, LA 2. f is convex so the sign changes at
    most once; bisect for it and clamp to [lo, hi].
    """
    slopes = (1 - s, s, 2)

    def h(d):
        c = components(n, m, s, d)
        xs = (c["probe"], c["fill"], c["la"])
        mx = max(xs)
        return sum(k * mp.power(2, x - mx) for k, x in zip(slopes, xs))

    a, b = mp.mpf(lo), mp.mpf(hi)
    if h(a) >= 0:
        return a
    if h(b) <= 0:
        return b
    for _ in range(BISECT_ITERS):
        mid = (a + b) / 2
        if h(mid) < 0:
            a = mid
        else:
            b = mid
    return (a + b) / 2


def solve_pair(n, m, s, hi_rule):
    L = L_of(n, m)
    if hi_rule == "none":
        hi = log2N(n) + 200
    elif hi_rule == "total_trials_ge_1":
        hi = L / (m - 1)
    elif hi_rule == "p_le_1":
        hi = L / m
    else:
        raise ValueError(hi_rule)
    lo = mp.mpf(0)
    f = lambda d: total(n, m, s, d)
    val_g, d_g = golden_min(f, lo, hi)
    d_r = derivative_root(n, m, s, lo, hi)
    val_r = f(d_r)
    agree = abs(val_g - val_r) < mp.mpf("1e-25")
    return {"d": d_r, "total": val_r, "golden_total": val_g, "golden_d": d_g,
            "methods_agree": bool(agree), "hi": hi, "lo": lo,
            "at_upper_bound": bool(abs(d_r - hi) < mp.mpf("1e-30")),
            "at_lower_bound": bool(abs(d_r - lo) < mp.mpf("1e-30"))}


def solve_pair_integer(n, m, s):
    L = L_of(n, m)
    hi = int(mp.floor(L / (m - 1)))
    best = None
    for d in range(0, hi + 1):
        v = total(n, m, s, mp.mpf(d))
        if best is None or v < best[0]:
            best = (v, d)
    return {"d": best[1], "total": best[0]}


def describe(n, m, s, d, val):
    c = components(n, m, s, d)
    rho = mp.log(RHO_CONST, 2) + log2N(n) / 2
    dominant = max(("probe", "fill", "la"), key=lambda k: c[k])
    return {
        "m": m, "s": s,
        "d": mp.nstr(d, 15),
        "TOTAL_bits": mp.nstr(val, 15),
        "PROBE_bits": mp.nstr(c["probe"], 15),
        "FILL_bits": mp.nstr(c["fill"], 15),
        "LA_bits": mp.nstr(c["la"], 15),
        "store_bits": mp.nstr(c["log2_store"], 15),
        "log2_total_trials": mp.nstr(c["log2_total_trials"], 15),
        "log2_trials_per_relation": mp.nstr(c["log2_trials_per_relation"], 15),
        "log2_p": mp.nstr(c["log2_p"], 15),
        "p_gt_1": bool(c["log2_p"] > 0),
        "dominant_term": dominant,
        "rho_bits": mp.nstr(rho, 15),
        "margin_bits": mp.nstr(val - rho, 15),
    }


def float_grid_check(n, step=0.01):
    """Third, crude method in plain floats: global grid min under C1."""
    lN = float(log2N(n))
    best = None
    for m in M_VALUES:
        lf = math.log2(math.factorial(m))
        L = lf + lN
        hi = L / (m - 1)
        for s in range(0, m // 2 + 1):
            k = 0
            while True:
                d = k * step
                if d > hi:
                    break
                xs = (L + (1 - s) * d, s * d, 2 * d)
                mx = max(xs)
                v = mx + math.log2(sum(2.0 ** (x - mx) for x in xs))
                if best is None or v < best[0]:
                    best = (v, m, s, d)
                k += 1
    return {"TOTAL_bits": best[0], "m": best[1], "s": best[2], "d": best[3],
            "step": step}


# -------------------------------------------------------------------- main
def main():
    out = {
        "task_id": "TASK-20261001-f39c27",
        "environment": {
            "python": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "mpmath": mp.__version__,
            "mpmath_dps": mp.mp.dps,
            "sympy": sympy.__version__,
        },
        "curve_checks": curve_checks(),
        "sign_convention": "margin = TOTAL - log2(0.886*sqrt(N)); positive => IC costs more than rho",
        "degrees": {},
    }

    # ECC2K-130 published-rho cross-check of ell (informational only):
    # sqrt(pi*ell/(2*2*131)) is the cost_model's second baseline column.
    out["ecc2k130_published_rho_log2"] = mp.nstr(
        mp.log(mp.sqrt(mp.pi * ELL_ECC2K130 / (2 * 2 * 131)), 2), 10)

    identity_max_err = mp.mpf(0)
    for n in DEGREES:
        rec = {"log2N": mp.nstr(log2N(n), 25),
               "rho_bits": mp.nstr(mp.log(RHO_CONST, 2) + log2N(n) / 2, 15),
               "pairs": []}
        best = {"C0": None, "C1": None, "C2": None, "C3": None, "C4": None}
        all_agree = True
        lower_bound_binds_at_best = {}
        for m in M_VALUES:
            for s in range(0, m // 2 + 1):
                # identity check: PROBE components == closed form, at 3 probe points
                for d in (mp.mpf(1), mp.mpf("7.3"), mp.mpf("41.9")):
                    err = abs(components(n, m, s, d)["probe"] - simplified_probe(n, m, s, d))
                    identity_max_err = max(identity_max_err, err)
                r0 = solve_pair(n, m, s, "none")
                r1 = solve_pair(n, m, s, "total_trials_ge_1")
                r3 = solve_pair(n, m, s, "p_le_1")
                r4 = solve_pair_integer(n, m, s)
                all_agree &= r0["methods_agree"] and r1["methods_agree"] and r3["methods_agree"]
                L = L_of(n, m)
                uncon_tt = L - (m - 1) * r0["d"]  # log2 total trials at C0 minimiser
                flagged = bool(uncon_tt < 0)
                pair = {
                    "m": m, "s": s,
                    "flagged_total_trials_lt_1_at_unconstrained_min": flagged,
                    "C0_total": mp.nstr(r0["total"], 12), "C0_d": mp.nstr(r0["d"], 12),
                    "C1_total": mp.nstr(r1["total"], 12), "C1_d": mp.nstr(r1["d"], 12),
                    "C1_at_exclusion_boundary": r1["at_upper_bound"],
                    "C3_total": mp.nstr(r3["total"], 12), "C3_d": mp.nstr(r3["d"], 12),
                    "C4_total": mp.nstr(r4["total"], 12), "C4_d": r4["d"],
                }
                rec["pairs"].append(pair)
                cand = {
                    "C0": (r0["total"], m, s, r0["d"], r0),
                    "C1": (r1["total"], m, s, r1["d"], r1),
                    "C3": (r3["total"], m, s, r3["d"], r3),
                    "C4": (r4["total"], m, s, mp.mpf(r4["d"]), None),
                }
                if not flagged:
                    cand["C2"] = (r0["total"], m, s, r0["d"], r0)
                for k, v in cand.items():
                    if best[k] is None or v[0] < best[k][0]:
                        best[k] = v
        rec["minimiser_methods_agree_all_pairs"] = bool(all_agree)
        rec["flagged_pairs"] = [(p["m"], p["s"]) for p in rec["pairs"]
                                if p["flagged_total_trials_lt_1_at_unconstrained_min"]]
        rec["optimum"] = {}
        for k, v in best.items():
            val, m, s, d, r = v
            desc = describe(n, m, s, d, val)
            if r is not None:
                desc["at_upper_bound_of_d"] = r["at_upper_bound"]
                desc["at_lower_bound_d_eq_0"] = r["at_lower_bound"]
            rec["optimum"][k] = desc
        # runner-up under C1 among different m, to show how sharp the optimum is
        c1_by_m = {}
        for p in rec["pairs"]:
            v = mp.mpf(p["C1_total"])
            if p["m"] not in c1_by_m or v < c1_by_m[p["m"]][0]:
                c1_by_m[p["m"]] = (v, p["s"])
        rec["C1_best_per_m"] = {m: {"s": s, "TOTAL_bits": mp.nstr(v, 10)}
                                for m, (v, s) in sorted(c1_by_m.items())}
        rec["float_grid_check_C1"] = float_grid_check(n)
        out["degrees"][str(n)] = rec

    out["probe_identity_max_abs_err"] = mp.nstr(identity_max_err, 5)
    json.dump(out, sys.stdout, indent=1, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
