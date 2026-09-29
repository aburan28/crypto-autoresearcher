#!/usr/bin/env python3
"""EJ4 computations for TASK-20260928-e2cfcf (REVIEW-AUXIN-20260928-8456b6).

Review computation only; no protocol run. Builds the C-PLANT-M and C-PLANT-P
construction integers from their recipe text (typed controls, as transcluded),
builds BND-1, BND-2, BND-3 and one reviewer-declared BOUND state from their
declared parts, evaluates the D3 BOUND rules and narrow corrective.bin_by_status
with the validator's own evaluator, and then runs a mutation truth table over
the C-BOUND gates (as composed with G-GATE1), stopping_rules item 10, the N4
condition as F-N4 reads it, and gate_evaluation_mode.

OUTCOME DISCIPLINE: no control integer, witness integer or depth is written to
any output. Integers are committed by sha256 of canonical JSON; witnesses are
reported by symbolic label; depths only as the bin predicate outcomes.
Primality: validator-written Baillie-PSW screen (strong base-2 + strong Lucas,
Selfridge method A) as definitions.prime defines the screen; no certificate is
produced, which the evaluator logic under test does not need.

Usage (repository root): python3 ej4_states.py <out.json>
"""
import hashlib
import itertools
import json
import math
import sys
from math import isqrt

import mpmath as mp

mp.mp.dps = 170
TAU = mp.mpf(10) ** -45
TOL2 = mp.mpf(10) ** -50
TIE = mp.mpf(10) ** -100
SMALL = [p for p in range(3, 2000) if all(p % q for q in range(2, isqrt(p) + 1))]


# ---------------- primality screen (definitions.prime) -----------------------
def strong_prp2(n):
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = pow(2, d, n)
    if x in (1, n - 1):
        return True
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return True
    return False


def jacobi(a, n):
    a %= n
    r = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                r = -r
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            r = -r
        a %= n
    return r if n == 1 else 0


def strong_lucas(n):
    if isqrt(n) ** 2 == n:
        return False
    D = 5
    while True:
        j = jacobi(D, n)
        if j == -1:
            break
        if j == 0 and abs(D) != n:
            return False
        D = -D - 2 if D > 0 else -D + 2
    P, Q = 1, (1 - D) // 4
    d, s = n + 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    U, V, Qk = 0, 2, 1          # U_0, V_0, Q^0
    inv2 = pow(2, -1, n)
    for bit in bin(d)[2:]:
        U, V = U * V % n, (V * V - 2 * Qk) % n
        Qk = Qk * Qk % n
        if bit == "1":
            U, V = (P * U + V) * inv2 % n, (D * U + P * V) * inv2 % n
            Qk = Qk * Q % n
    if U == 0 or V == 0:
        return True
    for _ in range(s - 1):
        V = (V * V - 2 * Qk) % n
        Qk = Qk * Qk % n
        if V == 0:
            return True
    return False


def is_prime(n):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for p in SMALL:
        if n == p:
            return True
        if n % p == 0:
            return False
    return strong_prp2(n) and strong_lucas(n)


def nextprime_ge(x):
    while not is_prime(x):
        x += 1
    return x


def icbrt(n):
    if n < 8:
        return 1 if n else 0
    x = 1 << (n.bit_length() // 3 + 1)
    while True:
        y = (2 * x + n // (x * x)) // 3
        if y >= x:
            break
        x = y
    while x ** 3 > n:
        x -= 1
    while (x + 1) ** 3 <= n:
        x += 1
    return x


def ceildiv(a, b):
    return -(-a // b)


# ---------------- construction recipes (typed controls) -----------------------
B = 256
M0 = 3 * 2 ** (B - 2)


def plant_m():
    S = isqrt(M0)
    d1 = nextprime_ge(isqrt(S))
    d2 = nextprime_ge(d1 + 1)
    D = d1 * d2
    u0 = ceildiv(M0, 2 * D)
    u = u0
    while True:
        if u != d1 and u != d2 and is_prime(u):
            r = 2 * D * u + 1
            if (r + 1) % 12 == 0 and is_prime(r) and is_prime((r + 1) // 12):
                break
        u += 1
        if u - u0 >= 2 ** 48:
            raise SystemExit("C-PLANT-M left its window")
    assert isqrt(S) <= d1 < isqrt(S) + 2 ** 24 and d1 < d2 < d1 + 2 ** 24 and r.bit_length() == B
    return {"r": r, "d1": d1, "d2": d2, "D": D, "u": u, "steps": u - u0}


def plant_p():
    d0 = icbrt(M0 // 4)
    d = nextprime_ge(d0)
    w0 = ceildiv(M0, 12 * d)
    w = w0
    while True:
        if w != d and is_prime(w):
            r = 12 * d * w - 1
            if is_prime(r) and is_prime((r - 1) // 2):
                break
        w += 1
        if w - w0 >= 2 ** 48:
            raise SystemExit("C-PLANT-P left its window")
    assert d0 <= d < d0 + 2 ** 24 and r.bit_length() == B
    return {"r": r, "d": d, "w": w, "steps": w - w0}


# ---------------- typed costs, floors, bins ------------------------------------
def T(branch, m, d):
    return mp.sqrt(mp.mpf(m) / d) + (mp.sqrt(d) if branch == "minus" else mp.mpf(d))


def e_of(branch, r, m, d):
    return mp.log(T(branch, m, d), 2) / mp.log(r, 2)


def F_of(branch, r):
    L = mp.log(r, 2)
    if branch == "minus":
        return (1 + mp.log(r - 1, 2) / 4) / L
    return (mp.log(3, 2) - mp.mpf(2) / 3 + mp.log(r + 1, 2) / 3) / L


def C_of(branch, r, m):
    return mp.log(mp.sqrt(m) + 1, 2) / mp.log(r, 2)


def exact_bins(s):
    flag = abs(s - mp.mpf(1) / 4) <= TAU or abs(s - mp.mpf(3) / 4) <= TAU
    if s >= mp.mpf(3) / 4 + TAU:
        b = "NEAR_FLOOR"
    elif s <= mp.mpf(1) / 4 - TAU:
        b = "NEAR_CEILING"
    elif abs(s - mp.mpf(1) / 4) <= TAU:
        b = "NEAR_CEILING"
    else:
        b = "INTERMEDIATE"
    return b, flag


def bound_bins(s):
    """narrow corrective.bin_by_status, BOUND clause."""
    b_exact, flag = exact_bins(s)
    if not flag and s >= mp.mpf(3) / 4 + TAU:
        return {"bin": "NEAR_FLOOR", "bin_at_least": "NEAR_FLOOR", "boundary_flag": False}
    return {"bin": "UNDETERMINED", "bin_at_least": b_exact, "boundary_flag": bool(flag)}


def divisors_from(pp):
    ds = [1]
    for p, k in pp:
        ds = [x * p ** i for x in ds for i in range(k + 1)]
    return sorted(set(ds))


def is_perfect_power(n):
    for k in range(2, n.bit_length() + 1):
        x = int(round(mp.mpf(n) ** (mp.mpf(1) / k)))
        for y in (x - 1, x, x + 1):
            if y > 1 and y ** k == n:
                return True
    return False


def evaluate_bound(branch, r, F_pp, parts):
    """D3 BOUND rules: W, witness (minimiser_and_ties), bounds, depth, bins."""
    m = r - 1 if branch == "minus" else r + 1
    Fb = math.prod(p ** k for p, k in F_pp)
    assert Fb * math.prod(parts) == m, "declared parts do not multiply to m_b"
    well_formed = all(is_prime(p) for p, _ in F_pp) and all(
        p > 1 and not is_prime(p) and not is_perfect_power(p) for p in parts)
    W = sorted({e * math.prod(S) for e in divisors_from(F_pp)
                for k in range(len(parts) + 1) for S in itertools.combinations(parts, k)})
    ev = {d: e_of(branch, r, m, d) for d in W}
    estar = min(ev.values())
    tied = sorted(d for d in W if ev[d] - estar <= TIE * estar)
    wit = tied[0]
    ub, lb = ev[wit], F_of(branch, r)
    C, Fl = C_of(branch, r, m), F_of(branch, r)
    s = (C - ub) / (C - Fl)
    out = {"status": "BOUND" if well_formed else "NOT_WELL_FORMED", "W": W, "witness": wit,
           "tied": tied, "upper": ub, "lower": lb, "depth_predicates": {
               "s_ge_3/4+tau": bool(s >= mp.mpf(3) / 4 + TAU), "s_le_1/4-tau": bool(s <= mp.mpf(1) / 4 - TAU),
               "s_below_1/100": bool(s < mp.mpf(1) / 100), "s_above_0.99": bool(s > mp.mpf("0.99"))}}
    out.update(bound_bins(s))
    out["floor_ok"] = bool(ub >= Fl - TAU) and bool(lb >= Fl - TAU)
    return out, m


def exact_min(branch, r, pp):
    m = r - 1 if branch == "minus" else r + 1
    ds = divisors_from(pp)
    assert ds[-1] == m
    ev = {d: e_of(branch, r, m, d) for d in ds}
    return min(ev.values())


def commit(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# ---------------- gates, stop 10, N4 as F-N4 reads it ---------------------------
CAT = ["status", "W", "witness", "bin", "bin_at_least", "boundary_flag"]


def gate_verdicts(ret, exp, is_bnd1, plant_m_exact):
    """ret: evaluator return on one path. Gate 1 (composed with G-GATE1): exact
    equality of the six categorical fields. Gate 2: both bounds within 1e-50 of
    the expected closed forms and floor invariant. Gate 3: BND-1 CONSISTENCY."""
    g1 = all(ret.get(k) == exp[k] for k in CAT)
    ub, lb = ret.get("upper"), ret.get("lower")
    g2 = (ub is not None and lb is not None and abs(ub - exp["upper"]) <= TOL2 and abs(lb - exp["lower"]) <= TOL2
          and ub >= exp["lower"] - TAU and lb >= exp["lower"] - TAU)
    g3 = True
    if is_bnd1:
        g3 = ub is not None and abs(ub - plant_m_exact) <= TOL2
    return {"g1": g1, "g2": g2, "g3": g3}


def decide(retA, retB, exp, is_bnd1, plant_m_exact):
    vA = gate_verdicts(retA, exp, is_bnd1, plant_m_exact)
    vB = gate_verdicts(retB, exp, is_bnd1, plant_m_exact)
    gate_holds = {g: vA[g] and vB[g] for g in vA}
    paths_disagree = any(vA[g] != vB[g] for g in vA)
    stop10 = not all(gate_holds.values())
    # N4 condition read as F-N4 states it
    def field_other(ret):
        cat = any(ret.get(k) != exp[k] for k in CAT)
        ub, lb = ret.get("upper"), ret.get("lower")
        bnd = (ub is None or lb is None or abs(ub - exp["upper"]) > TOL2 or abs(lb - exp["lower"]) > TOL2
               or ub < exp["lower"] - TAU or lb < exp["lower"] - TAU)
        cons = is_bnd1 and (ub is None or abs(ub - plant_m_exact) > TOL2)
        return cat or bnd or cons
    n4_fn4 = field_other(retA) or field_other(retB)
    # contrast reading: exact equality of each real-valued bound (not F-N4)
    def exact_other(ret):
        return any(ret.get(k) != exp[k] for k in CAT + ["upper", "lower"])
    n4_exact = exact_other(retA) or exact_other(retB)
    return {"stop10_fires": stop10, "paths_disagree_on_a_gate": paths_disagree, "N4_met_F-N4": n4_fn4,
            "agree_F-N4": stop10 == n4_fn4, "N4_met_exact_equality_contrast": n4_exact,
            "agree_exact_contrast": stop10 == n4_exact}


def mutations(exp, alt):
    """alt: wrong-but-plausible value per categorical field."""
    ms = [("baseline (every field as expected on both paths)", {}, {})]
    for k in CAT:
        ms += [(f"{k} wrong on path A only", {k: alt[k]}, {}),
               (f"{k} wrong on path B only", {}, {k: alt[k]}),
               (f"{k} wrong on both paths", {k: alt[k]}, {k: alt[k]}),
               (f"{k} absent on path A", {k: None}, {})]
    for b in ("upper", "lower"):
        ms += [(f"{b} off by 0.5e-50 on A (inside gate-2 tolerance)", {b: exp[b] + TOL2 / 2}, {}),
               (f"{b} off by 2e-50 on A (outside tolerance)", {b: exp[b] + 2 * TOL2}, {}),
               (f"{b} off by -2e-50 on B (outside tolerance)", {}, {b: exp[b] - 2 * TOL2}),
               (f"{b} +0.9e-50 on A and -0.9e-50 on B (paths differ by 1.8e-50, each inside tolerance)",
                {b: exp[b] + TOL2 * mp.mpf("0.9")}, {b: exp[b] - TOL2 * mp.mpf("0.9")}),
               (f"{b} absent on A", {b: None}, {})]
    ms += [("lower below floor by 2e-45 on A (floor invariant fails)", {"lower": exp["lower"] - 2 * TAU}, {})]
    return ms


def run_table(name, exp, alt, is_bnd1, plant_m_exact):
    rows = []
    for label, ma, mb in mutations(exp, alt):
        A = dict(exp); A.update(ma)
        Bp = dict(exp); Bp.update(mb)
        A = {k: v for k, v in A.items() if v is not None}
        Bp = {k: v for k, v in Bp.items() if v is not None}
        rows.append(dict(state=name, mutation=label, **decide(A, Bp, exp, is_bnd1, plant_m_exact)))
    return rows


def main(out):
    pm, pp = plant_m(), plant_p()
    rM, rP = pm["r"], pp["r"]
    d1, d2, D, u = pm["d1"], pm["d2"], pm["D"], pm["u"]
    d, w = pp["d"], pp["w"]
    pmx = exact_min("minus", rM, [(2, 1), (d1, 1), (d2, 1), (u, 1)])

    # reviewer-declared state, recorded with its expected values BEFORE evaluation
    declared = {
        "id": "BND-V1 (validator-declared, reviewer-evaluation mode only)",
        "row_and_branch": "C-PLANT-M, minus (m = r_M - 1)",
        "declared_state": "F = d1 * u with certified prime powers d1^1 and u^1; parts [2 * d2].",
        "expected_before_evaluation": {
            "status": "BOUND",
            "W": "{e * prod(S) : e | d1*u, S subset of {2*d2}} = {1, d1, u, d1*u, 2*d2, 2*D, 2*d2*u, m}",
            "witness": "u (tied exactly with 2*D, because u * 2D = m and T_minus(x) = T_minus(m/x); the smaller is u)",
            "upper_bound": "e_minus(u)", "lower_bound": "F_minus(r_M)",
            "bin_fields_from_bin_by_status": "bin NEAR_FLOOR, bin_at_least NEAR_FLOOR, boundary_flag false",
            "why": ("T_minus(u) = T_minus(2D) = sqrt(2D) + sqrt(u), and 2u lies within a factor 1 + 2^-37 of D, "
                    "so T_minus(u) is about (sqrt 2 + 1/sqrt 2) sqrt(D) = 2.1213 sqrt(D) against the real minimum "
                    "2 m^(1/4) of about 2 sqrt(D); e - F is about log2(1.0607)/log2(r_M) < 0.09/255, while "
                    "C - F exceeds 62/log2(r_M); so the witnessed depth exceeds 0.99 > 3/4 + tau and is not "
                    "within tau of 1/4 or 3/4. Every other member of W is at distance at least 2^60 from sqrt(m) "
                    "in ratio."),
        },
    }
    declared_commit = commit(declared)

    states = {
        "BND-1": ("minus", rM, [(2, 1), (u, 1)], [D]),
        "BND-2": ("minus", rM, [(2, 1)], [d1 * d2 * u]),
        "BND-3": ("plus", rP, [(2, 1)], [2 * d, 3 * w]),
        "BND-V1": ("minus", rM, [(d1, 1), (u, 1)], [2 * d2]),
    }
    mM, mP = rM - 1, rP + 1
    symbolic = {  # expected witness sets / witnesses as the draft's expected blocks state them
        "BND-1": ({e * f for e in divisors_from([(2, 1), (u, 1)]) for f in (1, D)}, min(D, 2 * u)),
        "BND-2": ({1, 2, mM // 2, mM}, 2),
        "BND-3": ({1, 2, 2 * d, 4 * d, 3 * w, 6 * w, 6 * d * w, 12 * d * w}, 2 * d),
        "BND-V1": ({1, d1, u, d1 * u, 2 * d2, 2 * D, 2 * d2 * u, mM}, u),
    }
    exp_bins = {"BND-1": ("NEAR_FLOOR", "NEAR_FLOOR", False), "BND-2": ("UNDETERMINED", "NEAR_CEILING", False),
                "BND-3": ("NEAR_FLOOR", "NEAR_FLOOR", False), "BND-V1": ("NEAR_FLOOR", "NEAR_FLOOR", False)}
    label = {min(D, 2 * u): "min(D, 2u)", 2: "2", 2 * d: "2d", u: "u"}
    res = {"construction_commitments": {
               "C-PLANT-M": commit({k: v for k, v in pm.items() if k != "steps"}),
               "C-PLANT-P": commit({k: v for k, v in pp.items() if k != "steps"}),
               "C-PLANT-M_bits_r": rM.bit_length(), "C-PLANT-P_bits_r": rP.bit_length(),
               "recipe_windows_respected": True},
           "declared_state_commitment_before_evaluation": declared_commit,
           "declared_state": declared, "states": {}, "truth_table": []}
    for name, (br, r, Fpp, parts) in states.items():
        ev, m = evaluate_bound(br, r, Fpp, parts)
        Wexp, wexp = symbolic[name]
        b, bal, fl = exp_bins[name]
        chk = {"status_BOUND": ev["status"] == "BOUND",
               "W_equals_expected_block": set(ev["W"]) == Wexp,
               "witness_equals_expected_block": ev["witness"] == wexp,
               "witness_label": label.get(ev["witness"], "other"),
               "tie_set_size": len(ev["tied"]),
               "bin": ev["bin"], "bin_at_least": ev["bin_at_least"], "boundary_flag": ev["boundary_flag"],
               "bins_equal_expected_block": (ev["bin"], ev["bin_at_least"], ev["boundary_flag"]) == (b, bal, fl),
               "depth_predicates": ev["depth_predicates"], "floor_invariant_holds": ev["floor_ok"],
               "upper_equals_closed_form": bool(abs(ev["upper"] - e_of(br, r, m, wexp)) <= TOL2),
               "lower_equals_F": bool(abs(ev["lower"] - F_of(br, r)) <= TOL2),
               "parts_commitment": commit({"F": Fpp, "parts": parts})}
        if name == "BND-1":
            chk["CONSISTENCY_holds"] = bool(abs(ev["upper"] - pmx) <= TOL2)
        res["states"][name] = chk
        exp = {"status": "BOUND", "W": ev["W"], "witness": ev["witness"], "bin": ev["bin"],
               "bin_at_least": ev["bin_at_least"], "boundary_flag": ev["boundary_flag"],
               "upper": ev["upper"], "lower": ev["lower"]}
        alt = {"status": "EXACT", "W": ev["W"][:-1], "witness": 1,
               "bin": "INTERMEDIATE" if ev["bin"] != "INTERMEDIATE" else "NEAR_FLOOR",
               "bin_at_least": "INTERMEDIATE", "boundary_flag": not ev["boundary_flag"]}
        res["truth_table"] += run_table(name, exp, alt, name == "BND-1", pmx)
    # BND-1 CONSISTENCY failure driven by the C-PLANT-M exponent, bounds exact
    ev1, _ = evaluate_bound(*states["BND-1"])
    exp1 = {"status": "BOUND", "W": ev1["W"], "witness": ev1["witness"], "bin": ev1["bin"],
            "bin_at_least": ev1["bin_at_least"], "boundary_flag": ev1["boundary_flag"],
            "upper": ev1["upper"], "lower": ev1["lower"]}
    r_ = decide(exp1, exp1, exp1, True, pmx + 2 * TOL2)
    res["truth_table"].append(dict(state="BND-1", mutation="C-PLANT-M EXACT exponent off by 2e-50; BND-1 fields exact (CONSISTENCY fails)", **r_))
    tt = res["truth_table"]
    res["truth_table_summary"] = {
        "cases": len(tt),
        "stop10_vs_N4_F-N4_disagreements": [f"{x['state']}: {x['mutation']}" for x in tt if not x["agree_F-N4"]],
        "stop10_vs_exact_equality_contrast_disagreements": len([x for x in tt if not x["agree_exact_contrast"]]),
        "cases_where_stop10_does_not_fire_but_paths_differ_on_a_bound": [
            f"{x['state']}: {x['mutation']}" for x in tt if "paths differ" in x["mutation"] and not x["stop10_fires"]],
    }
    json.dump(res, open(out, "w"), indent=1, default=str)
    print(json.dumps({"construction_commitments": res["construction_commitments"],
                      "declared_state_commitment_before_evaluation": declared_commit,
                      "states": res["states"], "truth_table_summary": res["truth_table_summary"]}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
