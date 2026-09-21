#!/usr/bin/env python3
"""Self-checks for every instrument this run uses, run BEFORE any measurement.

The vendored field arithmetic is checked first and hardest, because every count
in arm D flows through it; then the Boolean-descent builder is checked by
EVALUATION (the descended coordinate equations are evaluated at random Boolean
assignments and compared against S_3 computed directly in F_{2^n}), which is
the check that catches a wrong descent rather than a wrong count; then the
symbolic expansion is cross-checked against the descent; then the cost model's
vectorised path is cross-checked against its scalar path.

A failure here is an `implementation_error` and must stop the run.
"""
from __future__ import annotations

import math

import numpy as np

import cost_model as cm
import families as fam
import image_enum as ie
import symbolic_s3 as ss
from binary_field import GF2m, BinaryCurve, INFINITY, _is_irreducible, modulus_for
from f2poly import FieldPoly, S3, S3_via_general_squaring, build_chain


def check(label: str, cond: bool, detail: str = "") -> dict:
    if not cond:
        raise AssertionError(f"SELFTEST FAILED: {label} {detail}")
    return {"check": label, "passed": True, "detail": detail}


def field_checks(ns=(12, 15, 17)) -> list[dict]:
    out = []
    rng = np.random.default_rng(4242)
    for n in ns:
        f = GF2m(n)
        out.append(check(f"modulus_irreducible_n{n}",
                         _is_irreducible(n, modulus_for(n)),
                         f"modulus=0x{modulus_for(n):x}"))
        for _ in range(200):
            a = int(rng.integers(1, 1 << n))
            b = int(rng.integers(1, 1 << n))
            if f.mul(a, f.inv(a)) != 1:
                raise AssertionError("inverse is wrong")
            if f.sqr(a) != f.mul(a, a):
                raise AssertionError("sqr disagrees with mul")
            if f.sqrt(f.sqr(a)) != a:
                raise AssertionError("sqrt is not the inverse of sqr")
            if f.mul(a, b) != f.mul(b, a):
                raise AssertionError("mul is not commutative")
            c = f.add(f.sqr(a), a)
            if f.trace(c) != 0:
                raise AssertionError("Tr(a^2+a) must vanish")
            z = f.solve_quadratic(c)
            if z is None or f.add(f.sqr(z), z) != c:
                raise AssertionError("solve_quadratic failed on a solvable c")
        out.append(check(f"field_arithmetic_n{n}", True, "200 random triples"))
        E = BinaryCurve(f, 0, 1)
        pts = E.affine_points()
        order = len(pts) + 1
        hasse = 2 * math.isqrt(1 << n) + 2
        out.append(check(f"hasse_interval_n{n}",
                         abs(order - (1 << n) - 1) <= hasse,
                         f"order={order}, q={1 << n}"))
        for p in pts[:50]:
            if not E.is_on_curve(p):
                raise AssertionError("affine_points returned an off-curve point")
            if E.add(p, E.negate(p)) is not INFINITY:
                raise AssertionError("P + (-P) != O")
        for _ in range(100):
            p = pts[int(rng.integers(0, len(pts)))]
            q = pts[int(rng.integers(0, len(pts)))]
            r = pts[int(rng.integers(0, len(pts)))]
            try:
                lhs = E.add(E.add(p, q), r)
                rhs = E.add(p, E.add(q, r))
            except ArithmeticError:
                continue
            if lhs != rhs:
                raise AssertionError("group law is not associative")
        out.append(check(f"group_law_n{n}", True, "100 random associativity "
                                                  "and 50 negation checks"))
    return out


def descent_checks() -> list[dict]:
    """Evaluate the descended Boolean system against direct field arithmetic."""
    out = []
    rng = np.random.default_rng(20260913)
    for (n, t, k) in [(12, 2, 6), (12, 3, 4), (15, 3, 5), (17, 2, 9)]:
        f = GF2m(n)
        vb = ie.low_degree_basis(k)
        B = 1
        RX = int(rng.integers(1, 1 << n))
        reps = [int(rng.integers(0, 1 << n)) for _ in range(t)]
        for typed in (False, True):
            sysd = build_chain(f, n, t, k, vb, B, RX,
                               reps=reps if typed else None)
            out.append(check(
                f"equation_count_n{n}_t{t}_typed{int(typed)}",
                sysd["actual_boolean_equation_count"]
                == sysd["declared_equation_count_n_times_t_minus_1"]))
            out.append(check(
                f"variable_count_n{n}_t{t}_typed{int(typed)}",
                sysd["actual_variable_slots_allocated"]
                == sysd["declared_variable_count_n_t_minus_2_plus_kt"]))
            nvars = sysd["actual_variable_slots_allocated"]
            for _ in range(25):
                assign = int(rng.integers(0, 1 << nvars))
                # direct field evaluation of the chain
                xs = []
                for i in range(t):
                    val = reps[i] if typed else 0
                    for j, b in enumerate(vb):
                        if (assign >> (i * k + j)) & 1:
                            val ^= b
                    xs.append(val)
                us = []
                off = k * t
                for j in range(t - 2):
                    val = 0
                    for i in range(n):
                        if (assign >> (off + j * n + i)) & 1:
                            val ^= 1 << i
                    us.append(val)

                def s3(a, b_, c):
                    inner = f.add(f.add(f.mul(a, b_), f.mul(a, c)), f.mul(b_, c))
                    return f.add(f.add(f.sqr(inner), f.mul(f.mul(a, b_), c)), B)

                direct = []
                if t == 2:
                    direct.append(s3(xs[0], xs[1], RX))
                else:
                    direct.append(s3(us[0], xs[0], xs[1]))
                    for i in range(1, t - 2):
                        direct.append(s3(us[i - 1], us[i], xs[i + 1]))
                    direct.append(s3(us[t - 3], xs[t - 1], RX))
                # evaluation through the Boolean coordinate equations
                got = []
                for e in sysd["field_polys"]:
                    acc = 0
                    for mask, coeff in e.terms.items():
                        if (assign & mask) == mask:
                            acc ^= coeff
                    got.append(acc)
                if got != direct:
                    raise AssertionError(
                        f"descended system disagrees with direct field "
                        f"evaluation at n={n} t={t} typed={typed}")
            out.append(check(f"descent_evaluation_n{n}_t{t}_typed{int(typed)}",
                             True, "25 random Boolean assignments"))
        # the characteristic-2 squaring shortcut against general multiplication
        x1 = FieldPoly.linear_form(f, vb, list(range(k)))
        x2 = FieldPoly.linear_form(f, vb, list(range(k, 2 * k)), constant=reps[0])
        x3 = FieldPoly.constant(f, RX)
        a = S3(x1, x2, x3, B)
        b = S3_via_general_squaring(x1, x2, x3, B)
        out.append(check(f"square_shortcut_matches_general_mul_n{n}",
                         a.terms == b.terms))
    return out


def symbolic_checks() -> list[dict]:
    """The symbolic degree bound against exact Boolean degrees by descent."""
    out = []
    rep = ss.expansion_report()
    out.append(check("symbolic_S3_typed_bound_is_3",
                     rep["S3_typed_u_v1_plus_y1_v2_plus_y2"]
                     ["f2_degree_bound_from_exponent_weights"] == 3))
    out.append(check("symbolic_y1S3_typed_bound_is_3",
                     rep["y1_S3_typed"]
                     ["f2_degree_bound_from_exponent_weights"] == 3))
    out.append(check("naive_product_bound_is_4",
                     rep["naive_product_bound_for_y1_S3"] == 4))
    return out


def cost_model_checks() -> list[dict]:
    out = []
    for m in [1, 2, 5, 12, 100, 500]:
        a = cm.log2_factorial(m)
        b = cm.log2_factorial_exact(m)
        if abs(a - b) > 1e-9:
            raise AssertionError(f"log2_factorial drifts at m={m}: {a} vs {b}")
    out.append(check("log2_factorial_matches_exact_integers", True,
                     "m in {1,2,5,12,100,500}"))
    for n in [100, 301, 571]:
        for reading in cm.K_READINGS:
            for typed in (False, True):
                scalar = cm.surface_row(n, reading, 3.0, 2.0, typed)
                vec = cm.surface_summary_vectorised(n, reading, 3.0, 2.0, typed)
                if scalar["argmin_m"] != vec["total"]["argmin_m"]:
                    raise AssertionError(
                        f"vectorised argmin disagrees with scalar at n={n} "
                        f"{reading} typed={typed}: {scalar['argmin_m']} vs "
                        f"{vec['total']['argmin_m']}")
                if abs(scalar["value_at_m_n"] - vec["total"]["value_at_m_n"]) > 1e-9:
                    raise AssertionError("vectorised boundary value disagrees")
    out.append(check("vectorised_surface_matches_scalar_surface", True,
                     "n in {100,301,571} x both readings x typed/untyped"))
    d = cm.solve_cprime()
    out.append(check("cprime_bisection_matches_sqrt_2ln2",
                     abs(float(d["cprime_bisection_minus_exact"])) < 1e-40,
                     d["cprime_bisection_minus_exact"]))
    return out


def enumeration_checks() -> list[dict]:
    """Convolution against a direct product enumeration with curve arithmetic."""
    out = []
    gm = ie.GroupModel.build(12, 0, 1)
    out.append(check("group_coordinatisation_verified",
                     gm.verification["bijectivity_checked_exhaustively"],
                     gm.verification["structure"]))
    vb = ie.low_degree_basis(3)
    V = set(ie.span(vb))
    rng = np.random.default_rng(31337)
    reps, _ = fam.draw_additive_cosets(rng, 12, 3, V)
    bases = [gm.factor_base(s)
             for s in fam.typed_xsets("additive_cosets", vb, reps, gm.field)]
    conv = ie.typed_multiplicities(gm, bases)
    brute = ie.brute_force_image(gm, bases)
    if int(np.count_nonzero(conv)) != brute["image_size"]:
        raise AssertionError("convolution and brute force disagree on the image")
    if ie._histogram_of_counts(conv[conv > 0].tolist()) != brute["fibre_histogram"]:
        raise AssertionError("convolution and brute force disagree on fibres")
    out.append(check("typed_convolution_matches_brute_force", True,
                     f"image={brute['image_size']}"))
    F = gm.factor_base(sorted(V))
    mu = ie.untyped_multiset_multiplicities(gm, F, 3)
    bu = ie.brute_force_untyped_multiset_image(gm, F, 3)
    if int(np.count_nonzero(mu)) != bu["image_size"]:
        raise AssertionError("untyped multiset DP disagrees with brute force")
    if ie._histogram_of_counts(mu[mu > 0].tolist()) != bu["fibre_histogram"]:
        raise AssertionError("untyped fibre multisets disagree")
    out.append(check("untyped_multiset_dp_matches_brute_force", True,
                     f"image={bu['image_size']}"))
    return out


def invalid_input_checks() -> list[dict]:
    """The four inputs the contract requires be REJECTED rather than scored."""
    results = []
    rng = np.random.default_rng(99)
    f = GF2m(12)
    vb = ie.low_degree_basis(3)
    V = set(ie.span(vb))

    cases = []
    # (a) representatives not in pairwise distinct cosets of V
    def a():
        fam.validate_typed_draw([5, 5 ^ 3, 1024], V)
    cases.append(("coset_representatives_not_pairwise_distinct_mod_V", a))

    # (b) m > n, and k < 1
    def b1():
        fam.validate_parameters(n=12, m=13, k=1)
    cases.append(("m_greater_than_n", b1))

    def b2():
        fam.validate_parameters(n=12, m=3, k=0)
    cases.append(("k_below_one", b2))

    # (c) t = 1
    def c():
        fam.validate_parameters(n=12, m=3, k=4, t=1)
    cases.append(("t_equals_one", c))

    # (d) V that is not an F_2-subspace
    def d():
        fam.validate_subspace(fam.random_nonsubspace(rng, 12, 3), 3)
    cases.append(("V_not_an_F2_subspace", d))

    for name, fn in cases:
        try:
            fn()
        except fam.InvalidInput as exc:
            results.append({"invalid_input": name, "rejected": True,
                            "kind": exc.kind, "reason": exc.detail,
                            "scored": False})
            continue
        raise AssertionError(f"invalid input {name} was NOT rejected")
    # and the guard must ACCEPT a legitimate draw, or it rejects everything
    reps, _ = fam.draw_additive_cosets(rng, 12, 3, V)
    fam.validate_typed_draw(reps, V)
    fam.validate_parameters(n=12, m=3, k=4, t=3)
    fam.validate_subspace(ie.span(vb), 3)
    results.append({"invalid_input": "positive_control_valid_draw_accepted",
                    "rejected": False, "kind": None,
                    "reason": "a legitimate draw, m <= n, k >= 1, t >= 2 and a "
                              "genuine subspace all pass the same guards",
                    "scored": True})
    return results


def run_all() -> dict:
    out = {
        "vendored_field_arithmetic": field_checks(),
        "weil_descent_builder": descent_checks(),
        "symbolic_expansion": symbolic_checks(),
        "cost_model": cost_model_checks(),
        "exact_enumeration": enumeration_checks(),
        "invalid_input_rejection": invalid_input_checks(),
    }
    out["all_passed"] = True
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(run_all(), indent=1))
