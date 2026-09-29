#!/usr/bin/env python3
"""Joint V6 of REVIEW-ICPERF-20260913-66fd51 (TASK-20260913-6c5729): the generic
baseline column.  Validator's own arithmetic; reuses val_gf2n.py (written fresh
for V1).  No solver, no compiler; integer recursion + GF(2^n) arithmetic only.

Steps, following review-plan-addendum-V6.yaml:
 (1) coefficient statement from the generator (find_points.sage line 8) and the
     descent script (Weil_descent.sage line 171), not from any ledger record;
 (2) E(F_2) hand count -> trace t -> recursion for #E(F_{2^n}), n = 15, 17, 19,
     factorisation, r and h; cross-checked against a brute-force count with the
     validator's own field arithmetic, and the group order checked on random
     points ([#E]P = O);
 (2b) tau = 2-power Frobenius: endomorphism check, orbit size on the order-r
     subgroup, lambda with tau(P) = [lambda]P by BSGS, lambda^2 - t lambda + 2
     = 0 mod r, ord(lambda), -1 not in <lambda>  =>  <tau,-1> class size;
 (3) three-row baseline table from the VOW source (plain-walk constant) and the
     named sqrt(k) class heuristic (negation, <tau,-1>);
 (4) what the run reports as its baseline (grep of the run's deliverables);
 (5) nearby-object control: y^2 + xy = x^3 + x^2 + b with b outside F_2, where
     the argument must fail.
"""
import json
import math
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from val_gf2n import GF2n, BinaryCurve  # noqa: E402

ROOT = "/workspace"
GEN = f"{ROOT}/inputs/TRIMOSKA-ECICB-2024/upstream/find_points.sage"
WD = f"{ROOT}/inputs/TRIMOSKA-ECICB-2024/upstream/Weil_descent.sage"
BENCH = f"{ROOT}/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
RUN = f"{ROOT}/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
CELLS = {15: "INFOn15l5-1-S.dimacs", 17: "INFOn17l6-1-S.dimacs", 19: "INFOn19l6-1-S.dimacs"}

random.seed(20260915)
T0 = time.time()
out = {}

# ---------------------------------------------------------------- (1) coefficients
gen_lines = open(GEN).read().splitlines()
line8 = gen_lines[7]
m = re.search(r"EllipticCurve\(K,\[([^\]]*)\]\)", line8)
a1, a2, a3, a4, a6 = [c.strip() for c in m.group(1).split(",")]
wd_lines = open(WD).read().splitlines()
wd_curve_lines = [(i + 1, ln.strip()) for i, ln in enumerate(wd_lines) if "EllipticCurve" in ln]
root_test_line = gen_lines[24].strip()  # f=y^2+X*y-X^3-X^2-1
coeff_in_F2 = all(c in ("0", "1") for c in (a1, a2, a3, a4, a6))
out["step1_coefficients"] = {
    "find_points.sage_line_8": line8.strip(),
    "find_points.sage_line_25_root_test": root_test_line,
    "Weil_descent.sage_curve_lines": wd_curve_lines,
    "sage_convention": "EllipticCurve(K,[a1,a2,a3,a4,a6]): y^2 + a1 xy + a3 y = x^3 + a2 x^2 + a4 x + a6",
    "a1,a2,a3,a4,a6": [a1, a2, a3, a4, a6],
    "weierstrass_equation": "y^2 + xy = x^3 + x^2 + 1",
    "every_coefficient_in_F2": coeff_in_F2,
    "reason": "each of the five literals is 0 or 1; K(0) and K(1) are the prime-field elements of GF(2^n) for every n, "
              "so E is the base change to F_{2^n} of the curve E/F_2 with the same equation; the 2-power Frobenius "
              "(x,y) -> (x^2,y^2) fixes F_2 pointwise and therefore maps E(F_{2^n}) to itself (endomorphism tau). "
              "INFO*.dimacs headers carry n, l, modulus, x_R and the label only -- no curve coefficients -- so the "
              "generator and descent scripts are the only primary statements of the curve.",
}

# ---------------------------------------------------------------- (2) E(F_2) hand count and recursion
hand = []
for x in (0, 1):
    for y in (0, 1):
        lhs = (y * y + x * y) % 2
        rhs = (x ** 3 + x ** 2 + 1) % 2
        hand.append({"x": x, "y": y, "lhs_y2+xy": lhs, "rhs_x3+x2+1": rhs, "on_E": lhs == rhs})
n_affine = sum(1 for h in hand if h["on_E"])
E_F2 = n_affine + 1  # + point at infinity
t = 2 + 1 - E_F2
V = {0: 2, 1: t}
for k in range(2, 40):
    V[k] = t * V[k - 1] - 2 * V[k - 2]


def order_E(k):
    return 2 ** k + 1 - V[k]


def order_twist(k):
    return 2 ** k + 1 + V[k]


def factor(N):
    f = []
    d = 2
    while d * d <= N:
        while N % d == 0:
            f.append(d)
            N //= d
        d += 1 if d == 2 else 2
    if N > 1:
        f.append(N)
    return f


def is_prime(N):
    return N > 1 and factor(N) == [N]


out["step2_hand_count_E_F2"] = {
    "candidates": hand,
    "affine_points": n_affine,
    "plus_point_at_infinity": 1,
    "#E(F_2)": E_F2,
    "trace_t = 2 + 1 - #E(F_2)": t,
    "frobenius_char_poly": f"T^2 - ({t})T + 2",
    "recursion": "V_0 = 2, V_1 = t, V_k = t V_{k-1} - 2 V_{k-2};  #E(F_{2^k}) = 2^k + 1 - V_k;  #E'(F_{2^k}) = 2^k + 1 + V_k",
    "V_k_for_k_1_to_19": {k: V[k] for k in range(1, 20)},
    "#E(F_{2^k})_for_k_1_to_19": {k: order_E(k) for k in range(1, 20)},
}

# brute-force cross-check with the validator's own field arithmetic (running-product trick,
# also proves a is a generator of the multiplicative group)
fields, curves = {}, {}
bf = {}
for n, info in CELLS.items():
    mod_s = open(f"{BENCH}/{info}").read().splitlines()[1].strip()
    F = GF2n.from_info_modulus(n, mod_s)
    E = BinaryCurve(F, 1, 1)
    fields[n], curves[n] = F, E
    a = 2  # the class of x
    ainv2 = F.inv(F.sq(a))
    x, xi2 = 1, 1
    cnt = 0
    steps = 0
    while True:
        # x != 0: two points iff Tr(x + 1 + 1/x^2) == 0
        if F.trace(x ^ 1 ^ xi2) == 0:
            cnt += 2
        x = F.mul(x, a)
        xi2 = F.mul(xi2, ainv2)
        steps += 1
        if x == 1:
            break
    a_generates = steps == (1 << n) - 1
    N_bf = cnt + 1 + 1  # + (0, 1) + O
    bf[n] = {"modulus": F.modulus_str(), "a_is_generator_of_F*": a_generates, "steps": steps,
             "#E_bruteforce": N_bf, "#E_recursion": order_E(n), "agree": N_bf == order_E(n),
             "#twist_bruteforce": (steps - cnt // 2) * 2 + 1 + 1, "#twist_recursion": order_twist(n),
             "twist_agree": (steps - cnt // 2) * 2 + 2 == order_twist(n)}


def smul(E, k, P):
    R = None
    Q = P
    while k:
        if k & 1:
            R = E.add(R, Q)
        Q = E.add(Q, Q)
        k >>= 1
    return R


def random_point(E):
    F = E.F
    while True:
        x = random.randrange(1, 1 << F.n)
        ys = E.ys(x)
        if ys:
            return (x, random.choice(ys))


def frob(F, P):
    if P is None:
        return None
    return (F.sq(P[0]), F.sq(P[1]))


def bsgs(E, P, Q, r):
    """lambda in [0, r) with [lambda]P = Q, P of prime order r."""
    mm = math.isqrt(r) + 1
    table = {}
    R = None
    for j in range(mm):
        table[R] = j
        R = E.add(R, P)
    mP = smul(E, mm, P)
    neg_mP = E.neg(mP)
    G = Q
    for i in range(mm + 1):
        if G in table:
            lam = (i * mm + table[G]) % r
            assert smul(E, lam, P) == Q
            return lam
        G = E.add(G, neg_mP)
    raise RuntimeError("bsgs failed")


step2 = {}
for n in (15, 17, 19):
    N = order_E(n)
    fac = factor(N)
    r = max(fac)
    h = N // r
    F, E = fields[n], curves[n]
    # group order check on random points
    order_checks = all(smul(E, N, random_point(E)) is None for _ in range(5))
    # Frobenius is an endomorphism: tau(P) on E for random P
    tau_on_E = all(E.on_curve(frob(F, random_point(E))) for _ in range(50))
    # a point of order r
    while True:
        P = smul(E, h, random_point(E))
        if P is not None:
            break
    assert smul(E, r, P) is None
    # tau-orbit of P
    orbit = [P]
    Q = frob(F, P)
    while Q != P:
        orbit.append(Q)
        Q = frob(F, Q)
        assert len(orbit) <= 2 * n
    negP = E.neg(P)
    neg_in_orbit = negP in orbit
    lam = bsgs(E, P, frob(F, P), r)
    char_poly_zero = (lam * lam - t * lam + 2) % r == 0
    # multiplicative order of lambda mod r
    o, z = 1, lam % r
    while z != 1:
        z = (z * lam) % r
        o += 1
        assert o <= r
    minus_one_power = any(pow(lam, j, r) == r - 1 for j in range(1, o + 1))
    step2[n] = {
        "#E(F_2^n)": N, "factorisation": fac, "r_largest_prime": r, "r_is_prime": is_prime(r), "h_cofactor": h,
        "twist_order": order_twist(n), "twist_factorisation": factor(order_twist(n)),
        "bruteforce_crosscheck": bf[n], "[#E]P=O_on_5_random_points": order_checks,
        "tau(P)_on_E_for_50_random_P": tau_on_E,
        "tau_orbit_size_of_order_r_point": len(orbit), "minus_P_in_tau_orbit": neg_in_orbit,
        "<tau,-1>_class_size": (1 if neg_in_orbit else 2) * len(orbit),
        "lambda_with_tau(P)=[lambda]P": lam, "lambda^2 - t*lambda + 2 == 0 mod r": char_poly_zero,
        "ord_r(lambda)": o, "-1_in_<lambda>": minus_one_power,
        "n_is_prime": is_prime(n),
        "subfield_subgroups_if_n_composite": ({f"#E(F_2^{d})": order_E(d) for d in range(1, n) if n % d == 0 and d > 1}
                                              if not is_prime(n) else None),
    }
out["step2_orders"] = step2

# ---------------------------------------------------------------- (3) baseline table
# Sources, with provenance:
#   plain walk: van Oorschot-Wiener, inputs/VOW-1996-PCS/paper_fulltext.md Appendix A Lemma 1
#     (E(X) ~ sqrt(pi n / 2)) and Section 5.1 eq. (5) T_rho = (sqrt(pi p / 2)/m + 1/theta) t for a group of
#     prime order p, Pohlig-Hellman reducing to the largest prime p | #G (lines 449-459)  -- provenance: retrieved
#     (read at source by this validator; KN-LIT-73f7e1 records the same reading).
#   class heuristic (HEUR-CLASS-WALK, named here as a heuristic): an iteration function well defined on the
#     classes of an equivalence relation whose classes have size k (here the orbits of a group of efficiently
#     computable group automorphisms with known action on logs) behaves as a random mapping on N/k classes, so
#     the expected steps to a collision are sqrt(pi N / (2k)), i.e. a factor sqrt(k) below the plain walk;
#     fruitless short cycles and the cost of canonicalising a class are ignored (leading term only).
#     Literature source for k = 2 (negation) and k = 2n (Koblitz <tau,-1>): Wiener-Zuccherato 1998 and
#     Gallant-Lambert-Vanstone 2000 -- provenance: recalled (not opened in this program; KN-LIT-73f7e1 says so).
#     The 0.886 = sqrt(pi/4) constant is this heuristic at k = 2; it is NOT in the VOW paper (KN-LIT-73f7e1).
table = {}
for n in (15, 17, 19):
    r = step2[n]["r_largest_prime"]
    k_tau = step2[n]["<tau,-1>_class_size"]
    plain = math.sqrt(math.pi * r / 2)
    neg = math.sqrt(math.pi * r / 4)
    tau = math.sqrt(math.pi * r / (2 * k_tau))
    N = step2[n]["#E(F_2^n)"]
    ph_full = sum(math.sqrt(math.pi * p / 2) for p in step2[n]["factorisation"])
    table[n] = {
        "r": r, "class_size_<tau,-1>": k_tau,
        "rows_expected_group_operations_leading_term": {
            "none (plain walk, VOW eq.5 / Lemma 1, sqrt(pi r/2), constant 1.2533)": round(plain, 1),
            "negation only (k=2, sqrt(pi r/4), constant 0.8862)": round(neg, 1),
            "<tau,-1> (k=2n, sqrt(pi r/(4n)))": round(tau, 1),
        },
        "factors": {
            "none -> negation": round(plain / neg, 3), "none -> <tau,-1> = sqrt(2n)": round(plain / tau, 3),
            "negation -> <tau,-1> = sqrt(n)": round(neg / tau, 3),
            "sqrt(2n)": round(math.sqrt(2 * n), 3), "sqrt(n)": round(math.sqrt(n), 3),
        },
        "log2": {"plain": round(math.log2(plain), 2), "negation": round(math.log2(neg), 2), "<tau,-1>": round(math.log2(tau), 2)},
        "full_group_pohlig_hellman_plain_sum_over_prime_factors": round(ph_full, 1),
        "note": ("r-subgroup cost; the run's instances are not restricted to the order-r subgroup (S targets are sums of "
                 "three random E(F_2^n) points with x in V, U targets are uniform field elements), and Pohlig-Hellman "
                 "makes the full-group ECDLP cost the sum over prime factors shown"),
    }
out["step3_baseline_table"] = table

# ---------------------------------------------------------------- (4) what the run reports
pat = re.compile(r"rho|baseline|generic|pollard|sqrt|0\.886|negation|koblitz|frobenius|\btau\b", re.I)
hits = {}
for fn in ("manifest.yaml", "manifest_v2.yaml", "task-report.md", "summary.json", "plan.json", "environment.json"):
    p = f"{RUN}/{fn}"
    if os.path.exists(p):
        h = [(i + 1, ln.strip()[:120]) for i, ln in enumerate(open(p, errors="replace").read().splitlines()) if pat.search(ln)]
        hits[fn] = h
spec = open(f"{ROOT}/experiments/EXP-ICPERF-66fd51/specification.yaml").read().splitlines()
hyp = open(f"{ROOT}/ledger/hypotheses/H-ICPERF-cc4847.yaml").read().splitlines()
out["step4_run_baseline"] = {
    "grep_pattern": pat.pattern,
    "hits_in_run_deliverables": hits,
    "contract_interpretation_limit": [ln.strip() for ln in spec if "rho column" in ln],
    "hypothesis_interpretation_limit": [ln.strip() for ln in hyp if "rho comparison" in ln],
    "hypothesis_in_repo_baseline": [ln.strip() for ln in hyp if "in-repo baseline" in ln],
}

# ---------------------------------------------------------------- (5) nearby-object control
control = {}
for n in (15, 17, 19):
    F = fields[n]
    a = 2  # generator class of x, outside F_2
    for b_name, b in (("b = a", a), ("b = a^3 + a + 1", F.pow(a, 3) ^ a ^ 1)):
        Eb = BinaryCurve(F, 1, b)
        Eb2 = BinaryCurve(F, 1, F.sq(b))
        b_in_F2 = b in (0, 1)
        b_fixed_by_squaring = F.sq(b) == b
        # tau on E_b
        pts = [random_point(Eb) for _ in range(200)]
        tau_pts = [frob(F, P) for P in pts]
        on_Eb = sum(Eb.on_curve(P) for P in tau_pts)
        on_Eb2 = sum(Eb2.on_curve(P) for P in tau_pts)
        # brute-force #E_b(F_2^n): x=0 -> one point y = sqrt(b); x != 0 -> two points iff Tr(x + 1 + b/x^2) = 0
        ainv2 = F.inv(F.sq(a))
        x, xi2, cnt = 1, 1, 0
        while True:
            if F.trace(x ^ 1 ^ F.mul(b, xi2)) == 0:
                cnt += 2
            x = F.mul(x, a)
            xi2 = F.mul(xi2, ainv2)
            if x == 1:
                break
        N_b = cnt + 2
        order_ok = all(smul(Eb, N_b, random_point(Eb)) is None for _ in range(3))
        control[f"n={n}, {b_name}"] = {
            "b_hex": hex(b), "b_in_F2": b_in_F2, "b^2 == b (fixed by Frobenius)": b_fixed_by_squaring,
            "E(F_2)_hand_count_possible": False if not b_in_F2 else True,
            "why_recursion_step_fails": "E_b is not defined over F_2 (b is not fixed by squaring), so there is no E_b(F_2) to "
                                        "count and no F_2-Frobenius trace t; the recursion of step (2) has no base case",
            "tau(P)_on_E_b_of_200": on_Eb, "tau(P)_on_E_{b^2}_of_200": on_Eb2,
            "algebraic_reason": "(y^2)^2 + x^2 y^2 = (y^2 + xy)^2 = (x^3 + x^2 + b)^2 = x^6 + x^4 + b^2, so tau maps E_b onto "
                                "E_{b^2}, which equals E_b iff b^2 = b iff b in F_2",
            "#E_b(F_2^n)_bruteforce": N_b, "#E_b_factorisation": factor(N_b),
            "[#E_b]P=O_on_3_random_points": order_ok,
            "koblitz_recursion_value_for_comparison": order_E(n), "equals_koblitz_value": N_b == order_E(n),
            "consequence_for_the_baseline": "no order-n group automorphism of E_b(F_2^n) is supplied by Frobenius; the "
                                            "only efficiently computable automorphism is negation (|Aut(E_b)| = 2 for j = 1/b != 0 "
                                            "in characteristic 2, recalled textbook fact), so the class size stays 2 and the "
                                            "<tau,-1> row does not exist for E_b: the sqrt(2n) argument FAILS here, as it must",
        }
out["step5_nearby_object_control"] = control

out["seconds"] = round(time.time() - T0, 2)
json.dump(out, open(f"{HERE}/v6_koblitz_baseline.json", "w"), indent=1, default=str)

# ---------------------------------------------------------------- console summary
print("STEP 1:", line8.strip(), "| all coefficients in F_2:", coeff_in_F2, "| Weil_descent.sage:", wd_curve_lines)
print(f"STEP 2: #E(F_2) = {E_F2} (affine {n_affine} + O), t = {t}, char poly T^2 - {t}T + 2")
print("        V_k:", [V[k] for k in range(0, 20)])
for n in (15, 17, 19):
    s = step2[n]
    print(f"  n={n}: #E = {s['#E(F_2^n)']} = {'*'.join(map(str, s['factorisation']))}  r = {s['r_largest_prime']} "
          f"(prime {s['r_is_prime']}) h = {s['h_cofactor']} | bruteforce agree {s['bruteforce_crosscheck']['agree']} "
          f"twist {s['twist_order']} agree {s['bruteforce_crosscheck']['twist_agree']} | tau endo {s['tau(P)_on_E_for_50_random_P']} "
          f"orbit {s['tau_orbit_size_of_order_r_point']} -P in orbit {s['minus_P_in_tau_orbit']} class {s['<tau,-1>_class_size']} "
          f"| lambda {s['lambda_with_tau(P)=[lambda]P']} charpoly0 {s['lambda^2 - t*lambda + 2 == 0 mod r']} ord {s['ord_r(lambda)']} "
          f"-1 in <lambda> {s['-1_in_<lambda>']} | n prime {s['n_is_prime']} subfields {s['subfield_subgroups_if_n_composite']}")
print("STEP 3:")
for n in (15, 17, 19):
    tb = table[n]
    print(f"  n={n} r={tb['r']}:", tb["rows_expected_group_operations_leading_term"], tb["factors"],
          "PH full group:", tb["full_group_pohlig_hellman_plain_sum_over_prime_factors"])
print("STEP 4: hits in run deliverables:", {k: v for k, v in hits.items()})
print("        contract:", out["step4_run_baseline"]["contract_interpretation_limit"])
print("        hypothesis:", out["step4_run_baseline"]["hypothesis_interpretation_limit"])
print("STEP 5:")
for k, v in control.items():
    print(f"  {k}: b in F_2 {v['b_in_F2']}, tau(P) on E_b {v['tau(P)_on_E_b_of_200']}/200, on E_b^2 {v['tau(P)_on_E_{b^2}_of_200']}/200, "
          f"#E_b {v['#E_b(F_2^n)_bruteforce']} (= {'*'.join(map(str, v['#E_b_factorisation']))}) order ok {v['[#E_b]P=O_on_3_random_points']}, "
          f"koblitz value {v['koblitz_recursion_value_for_comparison']} equal {v['equals_koblitz_value']}")
print("seconds:", out["seconds"])
