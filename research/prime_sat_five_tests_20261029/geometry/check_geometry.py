"""Independent raw-result verifier. Does not import the producer implementation."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path


def add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    X, Y = P
    U, V = Q
    if X == U and (Y+V) % p == 0:
        return None
    numerator, denominator = ((3*X*X+a, 2*Y) if X == U else (V-Y, U-X))
    slope = numerator*pow(denominator % p, p-2, p) % p
    Z = (slope*slope-X-U) % p
    return [Z, (slope*(X-Z)-Y) % p]


def point_sum(points, p, a):
    out = None
    for point in points:
        out = add(out, point, p, a)
    return out


def is_prime(n):
    return n >= 2 and all(n % q for q in range(2, math.isqrt(n)+1))


def expected_curve(p, cap):
    tested = 0
    for a in range(1, p):
        for b in range(1, p):
            tested += 1
            if tested > cap:
                return {"status": "selector_cap", "tested_curve_candidates": cap}
            if (4*a**3+27*b*b) % p == 0:
                continue
            points = [[x, y] for x, y in itertools.product(range(p), repeat=2)
                      if (y*y-x**3-a*x-b) % p == 0]
            order = len(points)+1
            if order != p and is_prime(order):
                return {"status": "selected", "p": p, "a": a, "b": b,
                        "order": order, "cofactor": 1, "points": points,
                        "tested_curve_candidates": tested}
    return {"status": "no_curve", "tested_curve_candidates": tested}


def expected_coset(curve, d, require_five):
    p = curve["p"]
    if (p-1) % d or d & (d-1):
        return {"status": "unsupported_divisor"}
    xs = {point[0] for point in curve["points"]}
    tested = []
    for c in sorted({pow(t, d, p) for t in range(1, p)}):
        roots = [x for x in range(p) if pow(x, d, p) == c]
        usable = [x for x in roots if x in xs]
        tested.append({"c": c, "usable_x": len(usable)})
        if not require_five or len(usable) >= 5:
            return {"status": "selected", "c": c, "roots": roots,
                    "usable_x": usable, "tested_cosets": tested}
    return {"status": "ineligible_no_five_usable_x", "tested_cosets": tested}


def check(result):
    import sympy as sp
    result = json.loads(json.dumps(result))
    failures, counts = [], {"norm_certificates": 0, "addition_rows": 0, "saturation_cells": 0}
    X = sp.Symbol("X")

    def require(ok, context):
        if not ok:
            failures.append(context)

    def poly(coeffs):
        return sum(int(c)*X**i for i, c in enumerate(coeffs))

    cfg = result["config"]["graeffe"]
    for row in result["graeffe"]["cells"]:
        expected = expected_curve(row["input"]["p"], cfg["maximum_curve_candidates"])
        require(row["curve"].get("status") == expected["status"], ["curve_eligibility", row["input"]])
        for key, value in expected.items():
            require(row["curve"].get(key) == value, ["curve_selection", row["input"], key])
        if expected["status"] == "selected":
            negative = row["kind"] == "empty_squarefree_control"
            coset = expected_coset(expected, row["input"]["d"], not negative)
        else:
            coset = {"status": "curve_unavailable"}
        status = "complete" if coset["status"] == "selected" else "ineligible_retained"
        require(row["status"] == status, ["graeffe_eligibility", row["input"]])
        require(row["coset"].get("status") == coset["status"], ["coset_eligibility", row["input"]])
        for key in ("c", "roots", "usable_x", "tested_cosets"):
            if key in coset:
                require(row["coset"].get(key) == coset[key], ["coset_selection", row["input"], key])
        if row["status"] != status or status != "complete":
            continue
        curve = row["curve"]
        p, a, b = (curve[k] for k in ("p", "a", "b"))
        c, d = row["coset"]["c"], row["coset"]["d"]
        pointset = [[x, y] for x, y in itertools.product(range(p), repeat=2)
                    if (y*y-x**3-a*x-b) % p == 0]
        require(pointset == curve["points"], ["curve_point_set", row["input"]])
        require(len(pointset)+1 == curve["order"] and curve["order"] != p,
                ["curve_identity", row["input"]])
        require(all(curve["order"] % q for q in range(2, math.isqrt(curve["order"])+1)),
                ["curve_prime_order", row["input"]])
        for arm in ["forward", "repeated_forward", "inverse"]:
            if arm not in row:
                continue
            require(not row[arm]["mismatches"], ["producer_mismatch", row["input"], arm])
            for cert in row[arm]["certificates"]:
                counts["norm_certificates"] += 1
                P, R = cert["points"], cert["target"]
                A, B, U = (poly(cert[k]) for k in ("A", "B", "U"))
                norm = A*A-B*B*(X**3+a*X+b)
                ctx = [row["input"], arm, cert["A"], cert["B"]]
                require(sp.Poly(norm-(X-R[0])*U, X, modulus=p).is_zero, ["norm_identity", ctx])
                target_product = sp.prod(X-xy[0] for xy in P)
                require(sp.Poly(U-target_product, X, modulus=p).is_zero, ["U_roots", ctx])
                require(point_sum(P, p, a) == R, ["group_relation", ctx])
                require(all((xy[1]**2-xy[0]**3-a*xy[0]-b) % p == 0 for xy in P), ["point_curve", ctx])
                require(all(pow(xy[0], d, p) == c for xy in P), ["membership", ctx])
                require(all((int(A.subs(X, xy[0]))+int(B.subs(X, xy[0]))*xy[1]) % p == 0 for xy in P), ["recovery", ctx])
                require(all(int(B.subs(X, xy[0])) % p != 0 and xy[0] != R[0] for xy in P), ["selected_chart", ctx])
                up = sp.Poly(U, X, modulus=p)
                squarefree = sp.gcd(up, up.diff()).degree() == 0
                qp = sp.rem(sp.Poly(X**d-c, X, modulus=p), up).is_zero
                require(qp == cert["quotient_accepts"] and qp == squarefree, ["quotient_predicate", ctx])
                previous = U
                for layer in cert["graeffe_layers"]:
                    previous_poly = sp.Poly(previous, X, modulus=p)
                    even = sum(int(previous_poly.nth(2*i))*X**i for i in range(3))
                    odd = sum(int(previous_poly.nth(2*i+1))*X**i for i in range(3))
                    transformed = X*odd**2-even**2
                    require(sp.Poly(transformed-poly(layer), X, modulus=p).is_zero, ["graeffe_layer", ctx])
                    previous = poly(layer)
                require(sp.Poly(previous-(X-c)**5, X, modulus=p).is_zero, ["graeffe_terminal", ctx])
        if "inverse" in row:
            target_key = json.dumps(row["inverse"]["certificates"][0]["target"], separators=(",", ":")) if row["inverse"]["certificates"] else json.dumps(curve["points"][0], separators=(",", ":"))
            require(set(row["inverse"]["relations"]["quotient"]) == set(row["forward"]["selected_relations"][target_key]), ["inverse_squarefree_completeness", row["input"]])
            require(set(row["inverse"]["relations"]["graeffe"]) == set(row["repeated_forward"]["selected_relations"][target_key]), ["inverse_repeated_completeness", row["input"]])
            require(row["inverse"]["counts"]["coefficient_assignments"] == p**4, ["inverse_exhaustive_count", row["input"]])

    for row in result["saturation"]["cells"]:
        p, a, b = (row["input"][k] for k in ("p", "a", "b"))
        singular = (4*a**3+27*b*b) % p == 0
        expected_status = "singular_ineligible" if singular else "complete"
        require(row["status"] == expected_status,
                ["saturation_eligibility", row["input"]])
        if singular or row["status"] != expected_status:
            continue
        census = row["addition_census"]
        expected_points = [None]+[[x, y] for x, y in itertools.product(range(p), repeat=2)
                                 if (y*y-x**3-a*x-b) % p == 0]
        expected_pairs = {(json.dumps(P), json.dumps(Q)) for P, Q in itertools.product(expected_points, repeat=2)}
        got_pairs = set()
        for model in census["models"]:
            counts["addition_rows"] += 1
            P, Q = model["P"], model["Q"]
            got_pairs.add((json.dumps(P), json.dumps(Q)))
            require(add(P, Q, p, a) == model["result"], ["addition_chart", row["input"], P, Q])
        require(got_pairs == expected_pairs and len(got_pairs) == len(census["models"]), ["addition_complete", row["input"]])
        l, y, x = sp.symbols("l y x")
        for cell in row["symbolic_cells"]:
            counts["saturation_cells"] += 1
            u, v = cell["P"]
            h = x-u
            f1, f2 = y*y-x**3-a*x-b, h*l-y+v
            intended = [f1, f2, x**p-x, y**p-y, l**p-l]
            certificate = cell["certificates"]
            parsed = [sp.sympify(s, locals={"l": l, "y": y, "x": x}) for s in certificate["generators"]]
            for got, want in zip(parsed, intended):
                require(sp.Poly(got-want, l, y, x, modulus=p).is_zero, ["certificate_intended_generator", row["input"], cell["P"]])
            for key in ["g", "q"]:
                target = sp.sympify(certificate[key], locals={"l": l, "y": y, "x": x})
                mult = [sp.sympify(s, locals={"l": l, "y": y, "x": x}) for s in certificate[key+"_multipliers"]]
                residual = h**certificate["exponent"]*target-sum(m*f for m, f in zip(mult, intended))
                require(sp.Poly(residual, l, y, x, modulus=p).is_zero, ["saturation_certificate", key, row["input"], cell["P"]])
            expected_raw = [[ll, yy, xx] for ll, yy, xx in itertools.product(range(p), repeat=3)
                            if (yy*yy-xx**3-a*xx-b) % p == 0 and ((xx-u)*ll-yy+v) % p == 0]
            expected_generic = [point for point in expected_raw if point[2] != u]
            for name, models in cell["models"].items():
                expected = expected_raw if name == "unsaturated" else expected_generic
                require(models == expected, ["saturation_models", name, row["input"], cell["P"]])
                terms = [sp.Poly(sp.sympify(f, locals={"l": l, "y": y, "x": x}),
                                 l, y, x, modulus=p).terms()
                         for f in cell["arms"][name]["projected_basis"]]
                recomputed = []
                for ll, yy, xx in itertools.product(range(p), repeat=3):
                    zeros = [sum(int(c)*ll**m[0]*yy**m[1]*xx**m[2] for m, c in polyterms) % p == 0
                             for polyterms in terms]
                    if all(zeros):
                        recomputed.append([ll, yy, xx])
                require(recomputed == expected, ["independent_basis_model_check", name, row["input"], cell["P"]])
    return {"schema": "prime-sat-geometry-check/v1", "valid": not failures,
            "counts": counts, "failures": failures,
            "scope": "independently_recomputed_certificate_and_model_checks_not_performance_validation"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite checker result")
    raw = args.input.read_bytes()
    result = json.loads(raw)
    out = check(result)
    out["input_sha256"] = hashlib.sha256(raw).hexdigest()
    with args.output.open("x") as f:
        json.dump(out, f, sort_keys=True, indent=2)
        f.write("\n")
    if not out["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
