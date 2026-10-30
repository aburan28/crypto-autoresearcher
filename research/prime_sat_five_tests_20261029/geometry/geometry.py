"""Exact finite instruments; execution belongs to the root's frozen protocol.

All integer polynomial arrays are in increasing degree. No import performs a
scientific calculation. SymPy is imported only by the symbolic run arm.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import time
from collections import Counter
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def prime(n):
    return n >= 2 and all(n % q for q in range(2, math.isqrt(n) + 1))


def trim(a, p):
    a = [int(c) % p for c in a]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a or [0]


def padd(a, b, p):
    return trim([(a[i] if i < len(a) else 0) +
                 (b[i] if i < len(b) else 0) for i in range(max(len(a), len(b)))], p)


def pscale(a, c, p):
    return trim([c*x for x in a], p)


def pmul(a, b, p):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = (out[i+j] + x*y) % p
    return trim(out, p)


def pdiv(a, b, p):
    r, b = trim(a, p), trim(b, p)
    if b == [0]:
        raise ZeroDivisionError("zero polynomial")
    q = [0] * max(1, len(r)-len(b)+1)
    inv = pow(b[-1], -1, p)
    while r != [0] and len(r) >= len(b):
        i = len(r)-len(b)
        c = r[-1]*inv % p
        q[i] = c
        for j, bj in enumerate(b):
            r[i+j] = (r[i+j]-c*bj) % p
        r = trim(r, p)
    return trim(q, p), r


def peval(a, x, p):
    ans = 0
    for c in reversed(a):
        ans = (ans*x+c) % p
    return ans


def pgcd(a, b, p):
    while b != [0]:
        a, b = b, pdiv(a, b, p)[1]
    return pscale(a, pow(a[-1], -1, p), p)


def root_poly(roots, p):
    ans = [1]
    for x in roots:
        ans = pmul(ans, [-x, 1], p)
    return ans


def graeffe(u, p):
    """Monic odd-degree root-squaring transform T*O(T)^2-E(T)^2."""
    even, odd = u[::2], u[1::2]
    return padd([0] + pmul(odd, odd, p), pscale(pmul(even, even, p), -1, p), p)


def membership(u, d, c, p):
    g = u[:]
    layers = []
    for _ in range(d.bit_length()-1):
        g = graeffe(g, p)
        layers.append(g)
    expected = root_poly([c]*5, p)
    r = [0, 1]
    quotient_layers = []
    for _ in range(d.bit_length()-1):
        q, r = pdiv(pmul(r, r, p), u, p)
        quotient_layers.append({"q": q, "r": r})
    return g == expected, trim(r, p) == [c], layers, quotient_layers


def on_curve(P, p, a, b):
    return P is None or (P[1]*P[1]-P[0]**3-a*P[0]-b) % p == 0


def affine_add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    u, v = Q
    if x == u:
        if (y+v) % p == 0:
            return None
        slope = (3*x*x+a)*pow(2*y, -1, p) % p
    else:
        slope = (v-y)*pow(u-x, -1, p) % p
    z = (slope*slope-x-u) % p
    return z, (slope*(x-z)-y) % p


def projective_add(P, Q, p, a):
    """Independent Jacobian reference; never calls the affine implementation."""
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    if Z1 == 0:
        return Q
    if Z2 == 0:
        return P
    U1 = X1*Z2**2 % p
    U2 = X2*Z1**2 % p
    S1 = Y1*Z2**3 % p
    S2 = Y2*Z1**3 % p
    if U1 == U2:
        if S1 != S2 or Y1 == 0:
            return 0, 1, 0
        M = (3*X1*X1+a*pow(Z1, 4, p)) % p
        S = 4*X1*Y1*Y1 % p
        X3 = (M*M-2*S) % p
        return X3, (M*(S-X3)-8*pow(Y1, 4, p)) % p, 2*Y1*Z1 % p
    H = (U2-U1) % p
    R = (S2-S1) % p
    H3 = pow(H, 3, p)
    U1H2 = U1*H*H % p
    X3 = (R*R-H3-2*U1H2) % p
    return X3, (R*(U1H2-X3)-S1*H3) % p, H*Z1*Z2 % p


def projective_sum(points, p, a):
    ans = (0, 1, 0)
    for P in points:
        Q = (0, 1, 0) if P is None else (P[0], P[1], 1)
        ans = projective_add(ans, Q, p, a)
    if ans[2] == 0:
        return None
    z = pow(ans[2], -1, p)
    return ans[0]*z*z % p, ans[1]*z*z*z % p


def affine_points(p, a, b):
    sq = {}
    for y in range(p):
        sq.setdefault(y*y % p, []).append(y)
    return [(x, y) for x in range(p) for y in sq.get((x**3+a*x+b) % p, [])]


def select_curve(p, cap):
    count = 0
    for a in range(1, p):
        for b in range(1, p):
            count += 1
            if count > cap:
                return {"status": "selector_cap", "tested_curve_candidates": count-1}
            if (4*a**3+27*b*b) % p == 0:
                continue
            pts = affine_points(p, a, b)
            n = len(pts)+1
            if prime(n) and n != p:
                return {"status": "selected", "p": p, "a": a, "b": b,
                        "order": n, "cofactor": 1, "points": pts,
                        "tested_curve_candidates": count}
    return {"status": "no_curve", "tested_curve_candidates": count}


def select_coset(curve, d, require_five=True):
    p = curve["p"]
    if (p-1) % d or d & (d-1):
        return {"status": "unsupported_divisor"}
    by_x = {}
    for P in curve["points"]:
        by_x.setdefault(P[0], []).append(P)
    sizes = []
    for c in sorted({pow(t, d, p) for t in range(1, p)}):
        roots = [x for x in range(p) if pow(x, d, p) == c]
        usable = [x for x in roots if x in by_x]
        sizes.append({"c": c, "usable_x": len(usable)})
        if not require_five or len(usable) >= 5:
            return {"status": "selected", "d": d, "c": c, "roots": roots,
                    "usable_x": usable, "points_by_x": {x: by_x[x] for x in usable},
                    "tested_cosets": sizes}
    return {"status": "ineligible_no_five_usable_x", "tested_cosets": sizes}


def solve_linear(rows, rhs, p):
    m = [list(row)+[v] for row, v in zip(rows, rhs)]
    pivots = []
    i = 0
    for j in range(5):
        k = next((k for k in range(i, len(m)) if m[k][j] % p), None)
        if k is None:
            continue
        m[i], m[k] = m[k], m[i]
        inv = pow(m[i][j], -1, p)
        m[i] = [v*inv % p for v in m[i]]
        for k in range(len(m)):
            if k != i and m[k][j]:
                c = m[k][j]
                m[k] = [(v-c*w) % p for v, w in zip(m[k], m[i])]
        pivots.append(j)
        i += 1
    if any(not any(row[:5]) and row[5] for row in m):
        return "inconsistent", None
    if len(pivots) != 5:
        return "rank_deficient", None
    out = [0]*5
    for i, j in enumerate(pivots):
        out[j] = m[i][5]
    return "unique", out


def interpolate_norm(points, R, p, a, b):
    """Hermite equations for A+B*y, with monic cubic A; y!=0 chart."""
    mult = Counter(points + [(R[0], -R[1] % p)])
    rows, rhs = [], []
    for (x, y), multiplicity in mult.items():
        if y == 0:
            return "y_zero_local_parameter", None, None
        yc = [y]
        fc = [(x**3+a*x+b) % p, (3*x*x+a) % p, 3*x % p, 1]
        for n in range(1, multiplicity):
            middle = sum(yc[i]*yc[n-i] for i in range(1, n))
            yc.append(((fc[n] if n < len(fc) else 0)-middle)*pow(2*y, -1, p) % p)
        for n in range(multiplicity):
            def xp(k):
                return math.comb(k, n)*pow(x, k-n, p) % p if n <= k else 0
            rows.append([xp(0), xp(1), xp(2), yc[n],
                         (x*yc[n]+(yc[n-1] if n else 0)) % p])
            rhs.append(-xp(3) % p)
    status, v = solve_linear(rows, rhs, p)
    if status != "unique":
        return status, None, None
    return status, [v[0], v[1], v[2], 1], trim([v[3], v[4]], p)


def norm_poly(A, B, p, a, b):
    return padd(pmul(A, A, p), pscale(pmul(pmul(B, B, p), [b, a, 0, 1], p), -1, p), p)


def relation_key(points):
    return canonical(sorted(points))


def norm_check(points, R, curve, coset):
    p, a, b = (curve[k] for k in ("p", "a", "b"))
    if R is None:
        return {"status": "excluded_target_identity"}
    if R[1] == 0:
        return {"status": "excluded_target_y_zero"}
    if any(P[0] == R[0] for P in points):
        return {"status": "excluded_target_x_overlap"}
    if any(len({P[1] for P in points if P[0] == x}) > 1 for x in {P[0] for P in points}):
        return {"status": "excluded_opposite_sign_same_x"}
    status, A, B = interpolate_norm(list(points), R, p, a, b)
    if status != "unique":
        return {"status": "excluded_interpolation_"+status}
    u = root_poly([P[0] for P in points], p)
    if pgcd(B, u, p) != [1]:
        return {"status": "excluded_recovery_denominator_zero"}
    expected_norm = pmul([-R[0], 1], u, p)
    same_norm = norm_poly(A, B, p, a, b) == expected_norm
    gp, qp, layers, qlayers = membership(u, coset["d"], coset["c"], p)
    squarefree = len({P[0] for P in points}) == 5
    recovered = sorted((P[0], -peval(A, P[0], p)*pow(peval(B, P[0], p), -1, p) % p) for P in points)
    same_points = recovered == sorted(points)
    root_towers = []
    for point in points:
        tower = [point[0]]
        for _ in range(coset["d"].bit_length()-1):
            tower.append(tower[-1]*tower[-1] % p)
        root_towers.append(tower)
    per_root_accepts = all(tower[-1] == coset["c"] for tower in root_towers)
    corrupted_A = A[:]
    corrupted_A[0] = (corrupted_A[0]+1) % p
    corrupted_norm_rejected = norm_poly(corrupted_A, B, p, a, b) != expected_norm
    valid = same_norm and gp and (qp == squarefree) and same_points and per_root_accepts and corrupted_norm_rejected
    return {"status": "accepted" if valid else "mismatch", "A": A, "B": B,
            "U": u, "graeffe_layers": layers, "quotient_layers": qlayers,
            "norm_identity": same_norm, "graeffe_accepts": gp, "quotient_accepts": qp,
            "squarefree": squarefree, "recovered_points_equal": same_points,
            "per_root_towers": root_towers, "per_root_accepts": per_root_accepts,
            "corrupted_norm_rejected": corrupted_norm_rejected}


def forward_census(curve, coset, targets, repeated=False):
    p, a = curve["p"], curve["a"]
    target_set = set(targets)
    counts, statuses = Counter(), Counter()
    selected = {canonical(R): [] for R in targets}
    certs, mismatches = [], []
    trace = hashlib.sha256()
    if repeated:
        base = sorted(P for ps in coset["points_by_x"].values() for P in ps)
        iterator = itertools.combinations_with_replacement(base, 5)
    else:
        iterator = (ps for xs in itertools.combinations(coset["usable_x"], 5)
                    for ps in itertools.product(*(coset["points_by_x"][x] for x in xs)))
    for points in iterator:
        counts["point_multisets_enumerated"] += 1
        counts["projective_group_add_calls"] += 5
        R = projective_sum(points, p, a)
        trace.update((canonical([points, R])+"\n").encode())
        if R not in target_set:
            continue
        counts["oracle_target_relations"] += 1
        check = norm_check(points, R, curve, coset)
        statuses[check["status"]] += 1
        if "A" in check:
            counts["hermite_interpolations_unique"] += 1
        if check["status"] == "accepted":
            selected[canonical(R)].append(relation_key(points))
            certs.append({"points": points, "target": R, **check})
        elif check["status"] == "mismatch":
            mismatches.append({"points": points, "target": R, **check})
    return {"counts": dict(counts), "chart_status_counts": dict(statuses),
            "selected_relations": {k: sorted(v) for k, v in selected.items()},
            "certificates": certs, "mismatches": mismatches,
            "complete_enumeration_sha256": trace.hexdigest(),
            "repeated_point_arm": repeated,
            "scope": "forward_correspondence_census_not_inverse_solver"}


def inverse_coefficients(curve, coset, R):
    p, a, b = (curve[k] for k in ("p", "a", "b"))
    r, s = R
    counts, exclusions = Counter(), Counter()
    relations = {"graeffe": set(), "quotient": set()}
    certs, bad = [], []
    trace = hashlib.sha256()
    for a2, a1, b1, b0 in itertools.product(range(p), repeat=4):
        counts["coefficient_assignments"] += 1
        a0 = (s*(b1*r+b0)-r**3-a2*r*r-a1*r) % p
        A, B = [a0, a1, a2, 1], trim([b0, b1], p)
        u, rem = pdiv(norm_poly(A, B, p, a, b), [-r, 1], p)
        if rem != [0] or len(u) != 6 or u[-1] != 1:
            raise AssertionError("target norm divisibility")
        # Both predicates are evaluated on every coefficient assignment, before
        # recovery or root enumeration. This keeps their domains identical.
        gp, qp, layers, qlayers = membership(u, coset["d"], coset["c"], p)
        counts["graeffe_layers_evaluated"] += len(layers)
        counts["quotient_layers_evaluated"] += len(qlayers)
        trace.update(bytes([a2, a1, b1, b0, int(gp), int(qp)]))
        if not (gp or qp):
            continue
        counts["membership_accepts_any"] += 1
        if peval(u, r, p) == 0:
            exclusions["target_x_overlap"] += 1
            continue
        if pgcd(B, u, p) != [1]:
            exclusions["recovery_denominator_zero"] += 1
            continue
        roots, rest = [], u[:]
        for x in range(p):
            while len(rest) > 1 and peval(rest, x, p) == 0:
                roots.append(x)
                rest, rr = pdiv(rest, [-x, 1], p)
                if rr != [0]:
                    raise AssertionError("root division")
        points = [(x, -peval(A, x, p)*pow(peval(B, x, p), -1, p) % p) for x in roots]
        good = len(roots) == 5 and all(on_curve(P, p, a, b) for P in points)
        good = good and projective_sum(points, p, a) == R
        squarefree = len(set(roots)) == 5
        good = good and qp == (gp and squarefree)
        row = {"A": A, "B": B, "U": u, "points": points, "target": R,
               "graeffe_accepts": gp, "quotient_accepts": qp, "squarefree": squarefree,
               "graeffe_layers": layers, "quotient_layers": qlayers}
        if not good:
            bad.append(row)
        else:
            key = relation_key(points)
            if gp:
                relations["graeffe"].add(key)
            if qp:
                relations["quotient"].add(key)
            certs.append(row)
    return {"counts": dict(counts), "exclusion_counts": dict(exclusions),
            "relations": {k: sorted(v) for k, v in relations.items()},
            "certificates": certs, "mismatches": bad,
            "complete_assignment_sha256": trace.hexdigest(),
            "scope": "exhaustive_coefficient_search_no_speed_claim"}


def run_graeffe(config):
    result, curves = [], {}
    def prepare(cell, require_five=True):
        p = cell["p"]
        if p not in curves:
            curves[p] = select_curve(p, config["maximum_curve_candidates"])
        curve = curves[p]
        if curve["status"] != "selected":
            return curve, {"status": "curve_unavailable"}
        return curve, select_coset(curve, cell["d"], require_five)
    for kind, cells in (("forward", config["forward_cells"]),
                        ("empty_squarefree_control", config["negative_cells"]),
                        ("inverse", config["inverse_cells"])):
        for cell in cells:
            started = time.perf_counter()
            curve, coset = prepare(cell, kind != "empty_squarefree_control")
            row = {"kind": kind, "input": cell, "curve": curve, "coset": coset}
            if coset["status"] == "selected":
                targets = [None] + curve["points"][:3]
                if kind == "inverse":
                    targets = curve["points"][:1]
                forward = forward_census(curve, coset, targets)
                row["forward"] = forward
                if kind == "inverse":
                    repeated = forward_census(curve, coset, targets, repeated=True)
                    inv = inverse_coefficients(curve, coset, targets[0])
                    row["repeated_forward"] = repeated
                    row["inverse"] = inv
                    expected_q = set(forward["selected_relations"][canonical(targets[0])])
                    expected_g = set(repeated["selected_relations"][canonical(targets[0])])
                    row["inverse_oracle_agreement"] = {
                        "quotient": set(inv["relations"]["quotient"]) == expected_q,
                        "graeffe": set(inv["relations"]["graeffe"]) == expected_g}
                if kind == "empty_squarefree_control":
                    row["negative_control_pass"] = forward["counts"].get("point_multisets_enumerated", 0) == 0
                row["status"] = "complete"
            else:
                row["status"] = "ineligible_retained"
            row["unisolated_wall_seconds"] = time.perf_counter()-started
            result.append(row)
    return {"cells": result, "degree_of_regularity": None, "solving_degree": None,
            "coefficient_search_larger_than_p17": "not_performed",
            "complete_field_operation_count": None,
            "cost_scope": "explicit_enumeration_and_layer_event_counts_only"}


def chart_add(P, Q, p, a):
    """Disjoint complete addition charts, independently compared to Jacobians."""
    if P is None:
        return "left_identity", Q
    if Q is None:
        return "right_identity", P
    x, y = P
    u, v = Q
    if x != u:
        slope = (v-y)*pow(u-x, -1, p) % p
        chart = "generic"
    elif (y+v) % p == 0:
        return "inverse_or_two_torsion", None
    else:
        slope = (3*x*x+a)*pow(2*y, -1, p) % p
        chart = "doubling"
    outx = (slope*slope-x-u) % p
    return chart, (outx, (slope*(x-outx)-y) % p)


def addition_census(p, a, b, pts):
    counts, mismatch, rows = Counter(), [], []
    for P, Q in itertools.product([None]+pts, repeat=2):
        chart, got = chart_add(P, Q, p, a)
        reference = projective_sum([P, Q], p, a)
        counts[chart] += 1
        row = {"P": P, "Q": Q, "chart": chart, "result": got, "reference": reference}
        rows.append(row)
        if got != reference or not on_curve(got, p, a, b):
            mismatch.append(row)
    return {"counts": dict(counts), "models": rows, "mismatches": mismatch,
            "omitted_exception_mutant_missing": len(rows)-counts["generic"]}


def symbolic_saturation(p, a, b, P, order, method):
    import sympy as sp
    x, y, l, z = sp.symbols("x y l z")
    u, v = P
    h = x-u
    f1 = y*y-x**3-a*x-b
    f2 = h*l-y+v
    fields = [x**p-x, y**p-y, l**p-l]
    g = l*(y+v)-(x*x+u*x+u*u+a)
    q = 1-h**(p-1)
    # Independently expand the certificate coefficients over F_p.
    def zero(expr, variables=(l, y, x)):
        return sp.Poly(sp.expand(expr), *variables, modulus=p).is_zero
    certificate_checks = {
        "localized_curve_consequence": zero(h*g-f1-(y+v)*f2),
        "nonzero_indicator": zero(h*q+fields[0]),
        "corrupted_certificate_rejected": not zero(h*(g+1)-f1-(y+v)*f2)}
    I, J = [f1, f2]+fields, [f1, f2]+fields+[g, q]
    arms = {}
    bases = {}
    for name, equations, variables in (
            ("unsaturated", I, (l, y, x)),
            ("certified_finite_field_saturation", J, (l, y, x)),
            ("rabinowitsch", I+[1-z*h], (z, l, y, x))):
        start = time.perf_counter()
        gb = sp.groebner(equations, *variables, modulus=p, order=order, method=method)
        elapsed = time.perf_counter()-start
        polys = list(gb.polys)
        projected = [f.as_expr() for f in polys if not f.as_expr().has(z)]
        bases[name] = projected
        arms[name] = {
            "basis": [str(f.as_expr()) for f in polys],
            "projected_basis": [str(f) for f in projected],
            "input_polynomial_count": len(equations),
            "input_max_total_degree": max(sp.Poly(f, *variables).total_degree() for f in equations),
            "output_polynomial_count": len(polys),
            "output_max_total_degree": max((f.total_degree() for f in polys), default=0),
            "output_term_count": sum(len(f.terms()) for f in polys),
            "unisolated_wall_seconds": elapsed,
            "solving_degree": None, "degree_of_regularity": None,
            "field_operation_count": None, "macaulay_matrix_trace": None}
    # Independent finite enumeration uses original arithmetic predicates, then
    # evaluates every output basis to check that elimination preserved models.
    models, checked = {}, {}
    counts = Counter()
    for name, basis in bases.items():
        evaluators = [sp.Poly(f, l, y, x, modulus=p).terms() for f in basis]
        got = []
        for ll, yy, xx in itertools.product(range(p), repeat=3):
            counts["basis_assignments_checked"] += 1
            if all(sum(int(c)*pow(ll, m[0], p)*pow(yy, m[1], p)*pow(xx, m[2], p)
                       for m, c in terms) % p == 0 for terms in evaluators):
                got.append((ll, yy, xx))
        models[name] = got
    raw = [(ll, yy, xx) for ll, yy, xx in itertools.product(range(p), repeat=3)
           if (yy*yy-xx**3-a*xx-b) % p == 0 and ((xx-u)*ll-yy+v) % p == 0]
    generic = [row for row in raw if row[2] != u]
    checked["unsaturated_exact"] = models["unsaturated"] == raw
    checked["certified_generic_exact"] = models["certified_finite_field_saturation"] == generic
    checked["inverse_variable_generic_exact"] = models["rabinowitsch"] == generic
    # The exceptional model is deliberately not called a genuine point sum:
    # at Q=P the cleared slope equation admits arbitrary l, including spurious
    # and off-curve outputs. Complete chart union above supplies actual doubling.
    exceptional = []
    for ll, yy, xx in raw:
        if xx != u:
            continue
        outx = (ll*ll-u-xx) % p
        got = outx, (ll*(u-outx)-v) % p
        correct = projective_sum([P, (xx, yy)], p, a)
        exceptional.append({"l": ll, "Q": (xx, yy), "cleared_output": got,
                            "on_curve": on_curve(got, p, a, b),
                            "actual_sum": correct, "equals_actual_sum": got == correct})
    return {"P": P, "arms": arms, "checks": checked,
            "certificates": {"variables": ["l", "y", "x"], "h": str(h),
                "generators": [str(f) for f in I],
                "g": str(g), "q": str(q), "exponent": 1,
                "g_multipliers": ["1", str(y+v), "0", "0", "0"],
                "q_multipliers": ["0", "0", "-1", "0", "0"],
                "checks": certificate_checks},
            "models": models, "generic_model_count": len(generic),
            "unsaturated_model_count": len(raw), "exceptional_models": exceptional,
            "enumeration_counts": dict(counts)}


def run_saturation(config):
    cells = []
    for cell in config["cells"]:
        p, a, b = (cell[k] for k in ("p", "a", "b"))
        if (4*a**3+27*b*b) % p == 0:
            cells.append({"input": cell, "status": "singular_ineligible"})
            continue
        pts = affine_points(p, a, b)
        symbolic_points = pts if p == 7 else pts[:3]
        cells.append({"input": cell, "status": "complete", "curve_order": len(pts)+1,
                      "prime_order": prime(len(pts)+1),
                      "addition_census": addition_census(p, a, b, pts),
                      "symbolic_cells": [symbolic_saturation(p, a, b, P,
                          config["groebner_order"], config["groebner_method"])
                          for P in symbolic_points]})
    return {"cells": cells, "scope": "complete_finite_chart_union_and_symbolic_ideal_equivalence",
            "predecessor_reused": False,
            "predecessor_status": "specification_only_in_current_git_tree_no_run_history_found",
            "solving_degree": None, "degree_of_regularity": None,
            "complete_field_operation_count": None}


def run(config):
    if config.get("schema") != "prime-sat-geometry-config/v1":
        raise ValueError("unsupported geometry config")
    return {"schema": "prime-sat-geometry-result/v1", "config": config,
            "config_sha256": digest(config),
            "graeffe": run_graeffe(config["graeffe"]),
            "saturation": run_saturation(config["saturation"]),
            "scope": "finite_observations_no_attack_or_performance_claim"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite an existing result")
    config = json.loads(args.config.read_text())
    result = run(config)
    with args.output.open("x") as f:
        json.dump(result, f, sort_keys=True, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
