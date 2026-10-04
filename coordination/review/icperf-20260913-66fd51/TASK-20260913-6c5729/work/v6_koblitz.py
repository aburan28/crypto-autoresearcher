#!/usr/bin/env python3
"""V6 -- THE GENERIC BASELINE COLUMN.

(1) Weierstrass coefficients of the shipped curve, and whether they lie in F_2.
(2) #E(F_2) by hand-enumeration, t = q + 1 - #E(F_q), then the standard
    recursion s_n = t*s_{n-1} - q*s_{n-2} for #E(F_{2^n}), n = 15, 17, 19,
    with factorisation, largest prime factor r and cofactor h. Cross-checked
    against a brute-force count over every x in F_{2^n}.
(3) The generic baseline under three equivalence relations.
(5) Nearby-object control: a curve with a coefficient outside F_2, where the
    Frobenius argument must FAIL.

Integer arithmetic only; no solver, no compiler.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from valgf import GF2n  # my own V1 field arithmetic, written blind

HERE = pathlib.Path(__file__).resolve().parent

# ------------------------------------------------------------------ (1)
# find_points.sage line 8: E = EllipticCurve(K,[1,1,0,0,1])
# Sage's 5-coefficient form is [a1, a2, a3, a4, a6]:
#   y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6
A1, A2, A3, A4, A6 = 1, 1, 0, 0, 1

# ------------------------------------------------------------------ (2)
def count_E_over_F2():
    """#E(F_2) by hand: enumerate all (x, y) in F_2^2 and add the point at
    infinity. Arithmetic is in F_2, so this is a four-case table."""
    pts = []
    for x in (0, 1):
        for y in (0, 1):
            lhs = (y * y) ^ (A1 * x * y) ^ (A3 * y)
            rhs = (x * x * x) ^ (A2 * x * x) ^ (A4 * x) ^ A6
            if (lhs & 1) == (rhs & 1):
                pts.append((x, y))
    return len(pts) + 1, pts


nE2, affine_pts = count_E_over_F2()
t = 2 + 1 - nE2  # trace of Frobenius over F_2


def order_over_F2n(n):
    """#E(F_{2^n}) = 2^n + 1 - s_n with s_n = t*s_{n-1} - 2*s_{n-2},
    s_0 = 2, s_1 = t."""
    s0, s1 = 2, t
    if n == 0:
        return 2 ** 0 + 1 - s0, s0
    s = [s0, s1]
    for k in range(2, n + 1):
        s.append(t * s[k - 1] - 2 * s[k - 2])
    return 2 ** n + 1 - s[n], s[n]


def factor(m):
    f = {}
    d = 2
    while d * d <= m:
        while m % d == 0:
            f[d] = f.get(d, 0) + 1
            m //= d
        d += 1 if d == 2 else 2
    if m > 1:
        f[m] = f.get(m, 0) + 1
    return f


MODULI = {
    15: "x^15 + x^5 + x^4 + x^2 + 1",
    17: "x^17 + x^3 + 1",
    19: "x^19 + x^5 + x^2 + x + 1",
}
MOD_INT = {15: 32821, 17: 131081, 19: 524327}


def field(n):
    """valgf.GF2n takes the modulus as Sage's coefficients(sparse=False)
    string, i.e. constant term first."""
    bits = "".join("1" if (MOD_INT[n] >> i) & 1 else "0" for i in range(n + 1))
    return GF2n(n, bits)


def brute_force_count(n):
    """Independent count: for each x, y^2 + xy = x^3 + x^2 + 1 has 2 solutions
    when Tr((x^3+x^2+1)/x^2) = 0 and x != 0, 1 solution at x = 0, else 0."""
    F = field(n)
    total = 1  # point at infinity
    for xi in range(1 << n):
        if xi == 0:
            # y^2 = a6 = 1 -> exactly one y (squaring is a bijection)
            total += 1
            continue
        rhs = F.add(F.add(F.mul(F.mul(xi, xi), xi), F.mul(xi, xi)), 1)
        # y^2 + x*y = rhs  ->  z^2 + z = rhs/x^2 with z = y/x
        c = F.div(rhs, F.mul(xi, xi))
        if F.trace(c) == 0:
            total += 2
    return total


curves = {}
for n in (15, 17, 19):
    N, sn = order_over_F2n(n)
    f = factor(N)
    r = max(f)
    h = N // (r ** f[r]) * (r ** (f[r] - 1))
    bf = brute_force_count(n)
    curves[f"n{n}"] = {
        "n": n,
        "modulus": MODULI[n],
        "s_n": sn,
        "order_from_recursion": N,
        "order_from_brute_force_over_all_x": bf,
        "recursion_matches_brute_force": N == bf,
        "factorisation": {str(p): e for p, e in sorted(f.items())},
        "largest_prime_factor_r": r,
        "cofactor_h": N // r,
        "log2_r": round(math.log2(r), 3),
        "subgroup_is_large": r > N // 8,
    }

# ------------------------------------------------------------------ (3)
# Baseline, from KN-LIT-73f7e1 (read at source, provenance: retrieved):
#   VOW Section 5.1 eq. (5): T_rho = (sqrt(pi*p/2)/m + 1/theta)*t on a group of
#   prime order p. The paper's constant is sqrt(pi/2) = 1.2533 on sqrt(p), and
#   the record states plainly that the paper contains NO negation map and no
#   0.886 constant.
SQRT_PI_OVER_2 = math.sqrt(math.pi / 2.0)


def rho_ops(p, k):
    """Expected group operations for a rho/PCS walk on p/k equivalence classes.

    HEURISTIC (named, and it is a heuristic): the walk induced on the orbit
    space of an automorphism group of order k is itself a random walk on a set
    of size p/k. Under it the birthday constant is unchanged and the count
    scales as sqrt(p/k) = sqrt(p)/sqrt(k). This is the standard assumption; it
    is known to be imperfect for the negation map, where the induced walk has
    short fruitless cycles that must be detected and escaped, at a cost the
    heuristic does not model.
    """
    return SQRT_PI_OVER_2 * math.sqrt(p / k)


baseline = {}
for key, c in curves.items():
    n, r = c["n"], c["largest_prime_factor_r"]
    rows = {}
    for name, k in (("none", 1), ("negation_only", 2), ("tau_and_negation", 2 * n)):
        ops = rho_ops(r, k)
        rows[name] = {
            "k": k,
            "expected_group_operations": round(ops, 2),
            "log2": round(math.log2(ops), 3),
        }
    rows["speedup_tau_over_negation"] = round(
        rows["negation_only"]["expected_group_operations"]
        / rows["tau_and_negation"]["expected_group_operations"],
        4,
    )
    rows["speedup_tau_over_none"] = round(
        rows["none"]["expected_group_operations"]
        / rows["tau_and_negation"]["expected_group_operations"],
        4,
    )
    rows["sqrt_2n"] = round(math.sqrt(2 * n), 4)
    # what the whole-group (Pohlig-Hellman-blind) figure would be, for contrast
    rows["naive_whole_group_negation_only"] = {
        "group_order": c["order_from_recursion"],
        "expected_group_operations": round(rho_ops(c["order_from_recursion"], 2), 2),
        "log2": round(math.log2(rho_ops(c["order_from_recursion"], 2)), 3),
    }
    rows["pohlig_hellman_total_negation_only"] = round(
        sum(
            e * rho_ops(int(p), 2)
            for p, e in c["factorisation"].items()
        ),
        2,
    )
    baseline[key] = rows

# --------- does tau act with full order n on the prime-order subgroup?
# tau satisfies tau^2 - t*tau + 2 = 0, so on the subgroup of order r it acts as
# an integer lambda with lambda^2 - t*lambda + 2 = 0 (mod r). The <tau,-1>
# orbit of a generic point has size 2n only if lambda has multiplicative order
# exactly n mod r and -1 is not a power of lambda.
def tau_orbit_check(n, r):
    out = {"r": r, "n": n}
    # solve lambda^2 - t*lambda + 2 = 0 mod r by search (r is small here)
    lams = [x for x in range(r) if (x * x - t * x + 2) % r == 0]
    out["lambda_roots_mod_r"] = lams
    details = []
    for lam in lams:
        o = 1
        cur = lam % r
        while cur != 1 and o <= 4 * n + 4:
            cur = (cur * lam) % r
            o += 1
        order = o if cur == 1 else None
        powers = set()
        cur = 1
        for _ in range(order or 0):
            cur = (cur * lam) % r
            powers.add(cur)
        details.append(
            {
                "lambda": lam,
                "multiplicative_order_mod_r": order,
                "order_equals_n": order == n,
                "minus_one_is_a_power_of_lambda": (r - 1) % r in powers,
                "effective_orbit_size": (order or 0) * (1 if (r - 1) % r in powers else 2),
            }
        )
    out["roots"] = details
    return out


for key, c in curves.items():
    c["tau_action_on_prime_subgroup"] = tau_orbit_check(
        c["n"], c["largest_prime_factor_r"]
    )

# ------------------------------------------------------------------ (5)
# Nearby-object control. Take the SAME Weierstrass shape but with a6 outside
# F_2 -- a6 = the field generator `a` itself (x, as an integer 2). tau is an
# endomorphism of E only if E is defined over F_2, i.e. only if applying tau to
# the coefficients fixes them. tau(a6) = a6^2 != a6 whenever a6 is not in F_2.
def nearby_control(n):
    F = field(n)
    a6 = 2  # the generator `a`; a6^2 = a^2 != a for n > 1
    sq = F.mul(a6, a6)
    # count points on y^2 + xy = x^3 + x^2 + a6 by brute force
    total = 1
    for xi in range(1 << n):
        if xi == 0:
            total += 1
            continue
        rhs = F.add(F.add(F.mul(F.mul(xi, xi), xi), F.mul(xi, xi)), a6)
        c = F.div(rhs, F.mul(xi, xi))
        if F.trace(c) == 0:
            total += 2
    # what the F_2 recursion WOULD predict, if one wrongly applied it
    predicted, _ = order_over_F2n(n)
    return {
        "n": n,
        "a6": "a (the field generator), integer encoding 2",
        "a6_squared_equals_a6": sq == a6,
        "a6_in_F2": a6 in (0, 1),
        "tau_is_an_endomorphism": sq == a6,
        "actual_point_count": total,
        "count_the_F2_recursion_would_predict": predicted,
        "recursion_applies": total == predicted,
        "frobenius_speedup_available": sq == a6,
    }


control = {f"n{n}": nearby_control(n) for n in (15, 17, 19)}

out = {
    "coefficients": {
        "sage_literal": "EllipticCurve(K,[1,1,0,0,1])  # find_points.sage line 8",
        "a1": A1, "a2": A2, "a3": A3, "a4": A4, "a6": A6,
        "affine_equation": "y^2 + x*y = x^3 + x^2 + 1",
        "every_coefficient_in_F2": all(c in (0, 1) for c in (A1, A2, A3, A4, A6)),
        "reason": (
            "All five Weierstrass coefficients are the literals 0 and 1, which "
            "are the elements of the prime field F_2 and lie in F_{2^n} for "
            "every n. So E is the base change to F_{2^n} of a curve defined "
            "over F_2, and the 2-power Frobenius tau(x,y) = (x^2,y^2) maps "
            "E(F_{2^n}) to itself: it is an endomorphism. That is the "
            "definition of a Koblitz (anomalous binary) curve."
        ),
    },
    "E_over_F2": {
        "affine_points": affine_pts,
        "n_affine": len(affine_pts),
        "order_including_infinity": nE2,
        "trace_of_frobenius_t": t,
        "hand_count": (
            "x=0: y^2 = 1 has the single root y=1 (squaring is a bijection on "
            "F_2), giving (0,1). x=1: y^2 + y = 1+1+1 = 1, but y^2+y = 0 for "
            "both y in F_2, so no point. Total 1 affine + O = 2, hence "
            "t = 2 + 1 - 2 = 1."
        ),
    },
    "curves": curves,
    "baseline_group_operations": baseline,
    "baseline_provenance": (
        "VOW eq. (5) constant sqrt(pi/2) = 1.2533 on sqrt(p), from "
        "knowledge/literature/KN-LIT-73f7e1.md, which is provenance: retrieved "
        "(the coordinator read inputs/VOW-1996-PCS at source). That record "
        "states explicitly that the paper contains NO negation map and NO "
        "0.886 constant; 0.886 = sqrt(pi/4) is the negation-map constant and "
        "is attributed there to Wiener-Zuccherato 1998 / GLV 2000, both of "
        "which are provenance: recalled in this program and which I did not "
        "open. So the negation and <tau,-1> rows below rest on the sqrt(k) "
        "heuristic applied to VOW's own constant, not on a read source for "
        "either reduced constant."
    ),
    "nearby_object_control": control,
}
json.dump(out, open(HERE / "v6_koblitz.json", "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
