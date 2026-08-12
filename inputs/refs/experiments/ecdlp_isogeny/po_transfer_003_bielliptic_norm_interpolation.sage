#!/usr/bin/env sage
# PO-transfer-003: bielliptic norm/interpolation transfer.
#
# This controlled toy experiment tests whether native principal divisors on
#
#   C: y^2 = x^6 + A*x^2 + B
#
# can produce useful relations on the elliptic quotient
#
#   E1: Y^2 = U^3 + A*U + B,  pi1(x,y) = (x^2,y)
#
# without materializing the sparse-divisor MITM table used by PO-transfer-002.
# A cubic v(x) is interpolated through either four factor-base lifts or one
# lift of -lambda*Q and three factor-base lifts.  The remaining quadratic
# factor of v(x)^2-F(x) is split and pushed through pi1.  Target and factor-base
# logs are never used during relation generation.

import hashlib
import itertools
import json
import math
import os
import random
import sys
import time


def json_clean(value):
    if isinstance(value, dict):
        return {str(k): json_clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_clean(v) for v in value]
    if value is None or isinstance(value, (bool, str, int, float)):
        return value
    try:
        if value in ZZ:
            return int(value)
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return str(value)


def parse_out(default_path):
    args = list(sys.argv[1:])
    if "--out" in args:
        i = args.index("--out")
        return args[i + 1]
    return default_path


def parse_int_arg(flag, default=None):
    args = list(sys.argv[1:])
    if flag in args:
        i = args.index(flag)
        return int(args[i + 1])
    return default


def source_path():
    path = os.path.abspath(sys.argv[0])
    if path.endswith(".sage.py") and os.path.exists(path[:-3]):
        path = path[:-3]
    return path


def source_hash():
    path = source_path()
    try:
        with open(path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except Exception:
        return None


def rho_ops(order):
    return 0.886 * math.sqrt(int(order))


def point_key(P):
    if P == P.curve()(0):
        return ("O",)
    return (int(P[0]), int(P[1]))


def canonical_sqrt(a):
    if not a.is_square():
        return None
    r = a.sqrt()
    return r if int(r) <= int(-r) else -r


def canonical_y_point(E, u):
    rhs = u**3 + E.a4() * u + E.a6()
    y = canonical_sqrt(rhs)
    if y is None:
        return None
    return E(u, y)


def interpolate_polynomial(R, X, constraints):
    xs = [item[0] for item in constraints]
    if len(set(xs)) != len(xs):
        return None
    value = R(0)
    for i, (xi, yi) in enumerate(constraints):
        numerator = R(1)
        denominator = xi.parent()(1)
        for j, (xj, _yj) in enumerate(constraints):
            if i == j:
                continue
            numerator *= X - xj
            denominator *= xi - xj
        value += (yi / denominator) * numerator
    return value


def find_curve(p, seed, fixed=None):
    field = GF(Integer(p))
    R = PolynomialRing(field, "x")
    X = R.gen()
    rng = random.Random(int(seed))
    candidates = []
    if fixed is not None:
        candidates.append((Integer(fixed[0]) % p, Integer(fixed[1]) % p))
    for _ in range(10000):
        candidates.append((Integer(rng.randrange(1, int(p))), Integer(rng.randrange(1, int(p)))))

    for attempt, (a_int, b_int) in enumerate(candidates, start=1):
        A = field(a_int)
        B = field(b_int)
        E = EllipticCurve(field, [0, 0, 0, A, B])
        N = Integer(E.order())
        if not N.is_prime(proof=False):
            continue
        Fpoly = X**6 + A * X**2 + B
        if Fpoly.gcd(Fpoly.derivative()).degree() != 0:
            continue
        C = HyperellipticCurve(Fpoly)
        if C.genus() != 2:
            continue
        Eaux = EllipticCurve(field, [0, A, 0, 0, B**2])
        return {
            "field": field,
            "ring": R,
            "X": X,
            "A": A,
            "B": B,
            "E": E,
            "Eaux": Eaux,
            "N": N,
            "Fpoly": Fpoly,
            "C": C,
            "attempts": attempt,
        }
    raise RuntimeError("no prime-order smooth bielliptic cell found for p=%s" % p)


def build_factor_base(cell, requested_size, seed):
    field = cell["field"]
    E = cell["E"]
    selected = []
    candidate_count = 0
    for u_int in range(int(field.order())):
        u = field(u_int)
        x = canonical_sqrt(u)
        if x is None:
            continue
        P = canonical_y_point(E, u)
        if P is None or P == E(0):
            continue
        score = (
            (int(P[0]) * 1103515245 + int(P[1]) * 12345 + int(seed) * 2654435761)
            % int(field.order()),
            int(P[0]),
            int(P[1]),
        )
        candidate_count += 1
        selected.append((score, P, x))
        selected.sort(key=lambda item: item[0])
        if len(selected) > requested_size:
            selected.pop()
    if candidate_count < requested_size:
        raise RuntimeError("factor base request exceeds liftable canonical points")

    points = [item[1] for item in selected]
    lifts = []
    for _score, P, x in selected:
        if x == 0:
            lifts.append([x])
        else:
            lifts.append([x, -x])
    by_u = {int(P[0]): i for i, P in enumerate(points)}
    return points, lifts, by_u, candidate_count


def pi1_point(cell, x, y):
    return cell["E"](x**2, y)


def pi2_point(cell, x, y):
    if x == 0:
        return None
    B = cell["B"]
    return cell["Eaux"](B / x**2, B * y / x**3)


def split_identity_control(cell, seed, max_attempts=12000):
    rng = random.Random(int(seed) + int(99173))
    field = cell["field"]
    R = cell["ring"]
    X = cell["X"]
    E = cell["E"]
    Eaux = cell["Eaux"]
    Fpoly = cell["Fpoly"]
    for attempt in range(1, max_attempts + 1):
        coeffs = [field(rng.randrange(0, int(field.order()))) for _ in range(4)]
        v = sum((coeffs[i] * X**i for i in range(4)), R(0))
        H = v**2 - Fpoly
        if H.degree() != 6 or H.gcd(H.derivative()).degree() != 0:
            continue
        roots = H.roots(multiplicities=False)
        if len(roots) != 6 or any(r == 0 for r in roots):
            continue
        e_points = [pi1_point(cell, r, v(r)) for r in roots]
        a_points = [pi2_point(cell, r, v(r)) for r in roots]
        sum_e = sum(e_points, E(0))
        sum_a = sum(a_points, Eaux(0))
        flipped = -e_points[0] + sum(e_points[1:], E(0))
        return {
            "found": True,
            "attempts": attempt,
            "v_coefficients": [int(c) for c in coeffs],
            "roots": [int(r) for r in roots],
            "pi1_sum_zero": bool(sum_e == E(0)),
            "pi2_sum_zero": bool(sum_a == Eaux(0)),
            "negative_control_nonzero": bool(flipped != E(0)),
            "individual_aux_nonzero": bool(any(P != Eaux(0) for P in a_points)),
        }
    return {
        "found": False,
        "attempts": max_attempts,
        "pi1_sum_zero": False,
        "pi2_sum_zero": False,
        "negative_control_nonzero": False,
        "individual_aux_nonzero": False,
    }


def quotient_witness(cell):
    field = cell["field"]
    Fpoly = cell["Fpoly"]
    E = cell["E"]
    Eaux = cell["Eaux"]
    for x_int in range(1, int(field.order())):
        x = field(x_int)
        y = canonical_sqrt(Fpoly(x))
        if y is None:
            continue
        p1 = pi1_point(cell, x, y)
        p1_sigma = pi1_point(cell, -x, y)
        p2 = pi2_point(cell, x, y)
        p2_sigma = pi2_point(cell, -x, y)
        return {
            "sample_x": int(x),
            "pi1_sigma_fixed": bool(p1_sigma == p1),
            "pi2_sigma_negated": bool(p2_sigma == -p2),
            "pi1_nonzero": bool(p1 != E(0)),
            "pi2_nonzero": bool(p2 != Eaux(0)),
            "target_aux_order_gcd": int(gcd(Integer(E.order()), Integer(Eaux.order()))),
        }
    raise RuntimeError("could not find quotient witness")


def residual_relation(
    cell, constraints, labels, fb_points, fb_by_u, Q, allow_large_prime=False
):
    R = cell["ring"]
    X = cell["X"]
    E = cell["E"]
    Fpoly = cell["Fpoly"]
    v = interpolate_polynomial(R, X, constraints)
    if v is None or v.degree() != 3:
        return None, "degenerate_interpolation"
    H = v**2 - Fpoly
    if H.degree() != 6 or H.gcd(H.derivative()).degree() != 0:
        return None, "degenerate_intersection"
    selected_poly = R(1)
    for x, _y in constraints:
        selected_poly *= X - x
    residual, remainder = H.quo_rem(selected_poly)
    if remainder != 0 or residual.degree() != 2:
        return None, "residual_degree"
    residual_roots = residual.roots(multiplicities=False)
    if len(residual_roots) != 2:
        return None, "residual_nonsplit"

    coeffs = [0] * len(fb_points)
    target_coeff = 0
    for label in labels:
        if label[0] == "fb":
            coeffs[label[1]] += 1
        elif label[0] == "target":
            target_coeff += int(label[1])
        else:
            raise ValueError("unknown constraint label")

    large_primes = []
    for root in residual_roots:
        y = v(root)
        P = pi1_point(cell, root, y)
        idx = fb_by_u.get(int(P[0]))
        if idx is None:
            if not allow_large_prime:
                return None, "residual_outside_factor_base"
            canonical = canonical_y_point(E, P[0])
            if canonical is None:
                return None, "orientation_failure"
            if P == canonical:
                sign = 1
            elif P == -canonical:
                sign = -1
            else:
                return None, "orientation_failure"
            large_primes.append((canonical, sign))
            continue
        canonical = fb_points[idx]
        if P == canonical:
            coeffs[idx] += 1
        elif P == -canonical:
            coeffs[idx] -= 1
        else:
            return None, "orientation_failure"

    if len(large_primes) > 1:
        return None, "double_large_prime"

    public_sum = target_coeff * Q
    for c, P in zip(coeffs, fb_points):
        if c:
            public_sum += c * P
    if large_primes:
        public_sum += large_primes[0][1] * large_primes[0][0]
    if public_sum != E(0):
        return None, "public_verification_failure"

    nonzero = (
        sum(1 for c in coeffs if c != 0)
        + (1 if target_coeff else 0)
        + len(large_primes)
    )
    relation = {
        "coefficients": tuple(coeffs),
        "target_coeff": int(target_coeff),
        "nonzero": int(nonzero),
        "residual_roots": tuple(int(r) for r in residual_roots),
        "interpolation_constraints": tuple(
            {
                "x": int(x),
                "y": int(y),
                "label": str(label[0]),
                "label_value": int(label[1]),
            }
            for (x, y), label in zip(constraints, labels)
        ),
    }
    if large_primes:
        relation["kind"] = "single_large_prime"
        relation["large_prime_key"] = point_key(large_primes[0][0])
        relation["large_prime_sign"] = int(large_primes[0][1])
        return relation, "single_large_prime"
    relation["kind"] = "direct"
    return relation, "accepted"


def solve_relation_system(order, fb_size, relations, G, Q):
    K = GF(Integer(order))
    variables = fb_size
    if not relations:
        return {
            "variables": variables,
            "relations": 0,
            "rank": 0,
            "augmented_rank": 0,
            "consistent": True,
            "target_recovered": False,
            "recovered_secret": None,
        }
    rows = []
    rhs = []
    for relation in relations:
        coeffs = relation["coefficients"]
        rows.append([K(c) for c in coeffs[1:]] + [K(relation["target_coeff"])])
        rhs.append(K(-coeffs[0]))
    A = matrix(K, rows)
    b = vector(K, rhs)
    rank = A.rank()
    augmented_rank = A.augment(b).rank()
    consistent = rank == augmented_rank
    recovered_secret = None
    target_recovered = False
    if consistent and rank == variables:
        solution = A.solve_right(b)
        recovered_secret = Integer(solution[-1]) % Integer(order)
        target_recovered = recovered_secret * G == Q
    return {
        "variables": int(variables),
        "relations": int(len(relations)),
        "rank": int(rank),
        "augmented_rank": int(augmented_rank),
        "consistent": bool(consistent),
        "target_recovered": bool(target_recovered),
        "recovered_secret": int(recovered_secret) if recovered_secret is not None else None,
    }


def collect_relations(
    cell,
    factor_base,
    Q,
    lambda_max,
    allow_large_prime=False,
    stream_rank=False,
    anchor_cap=None,
):
    E = cell["E"]
    order = cell["N"]
    fb_points, fb_lifts, fb_by_u, liftable_count = factor_base
    fb_size = len(fb_points)
    G = fb_points[0]
    relations = []
    seen = set()
    large_prime_anchors = {}
    large_prime_anchor_peak_entries = 0
    collection_complete = False
    current_rank = 0
    counters = {
        "zero_attempts": 0,
        "target_attempts": 0,
        "degenerate_interpolation": 0,
        "degenerate_intersection": 0,
        "residual_degree": 0,
        "residual_nonsplit": 0,
        "residual_outside_factor_base": 0,
        "single_large_prime": 0,
        "double_large_prime": 0,
        "large_prime_eliminated": 0,
        "large_prime_trivial": 0,
        "large_prime_public_failure": 0,
        "large_prime_wrong_sign_tested": False,
        "large_prime_wrong_sign_nonzero": False,
        "large_prime_anchor_evictions": 0,
        "online_rank_tests": 0,
        "online_rank_rejected": 0,
        "orientation_failure": 0,
        "public_verification_failure": 0,
        "accepted": 0,
        "duplicates": 0,
    }
    verification_group_ops = 0

    def retain_final(relation):
        nonlocal collection_complete, current_rank
        key = (relation["coefficients"], relation["target_coeff"] % int(order))
        if key in seen:
            counters["duplicates"] += 1
            return
        seen.add(key)
        if stream_rank:
            counters["online_rank_tests"] += 1
            trial = solve_relation_system(order, fb_size, relations + [relation], G, Q)
            if trial["rank"] <= current_rank:
                counters["online_rank_rejected"] += 1
                return
            current_rank = trial["rank"]
        relations.append(relation)
        if stream_rank and current_rank == fb_size:
            solved = solve_relation_system(order, fb_size, relations, G, Q)
            collection_complete = bool(solved["target_recovered"])

    def retain(relation, status):
        nonlocal verification_group_ops, large_prime_anchor_peak_entries
        counters[status] = counters.get(status, 0) + 1
        if relation is None:
            return
        verification_group_ops += relation["nonzero"]
        if status != "single_large_prime":
            retain_final(relation)
            return

        lp_key = tuple(relation["large_prime_key"])
        anchor = large_prime_anchors.get(lp_key)
        if anchor is None:
            if anchor_cap is not None and len(large_prime_anchors) >= int(anchor_cap):
                oldest_key = next(iter(large_prime_anchors))
                del large_prime_anchors[oldest_key]
                counters["large_prime_anchor_evictions"] += 1
            large_prime_anchors[lp_key] = relation
            current_anchor_entries = sum(
                item["nonzero"] + 2 for item in large_prime_anchors.values()
            )
            large_prime_anchor_peak_entries = max(
                large_prime_anchor_peak_entries, current_anchor_entries
            )
            return

        anchor_sign = int(anchor["large_prime_sign"])
        relation_sign = int(relation["large_prime_sign"])
        if not counters["large_prime_wrong_sign_tested"]:
            wrong_coeffs = tuple(
                relation_sign * a + anchor_sign * b
                for a, b in zip(anchor["coefficients"], relation["coefficients"])
            )
            wrong_target = (
                relation_sign * int(anchor["target_coeff"])
                + anchor_sign * int(relation["target_coeff"])
            )
            wrong_sum = wrong_target * Q
            for c, P in zip(wrong_coeffs, fb_points):
                if c:
                    wrong_sum += c * P
            counters["large_prime_wrong_sign_tested"] = True
            counters["large_prime_wrong_sign_nonzero"] = bool(wrong_sum != E(0))
        coeffs = tuple(
            relation_sign * a - anchor_sign * b
            for a, b in zip(anchor["coefficients"], relation["coefficients"])
        )
        target_coeff = (
            relation_sign * int(anchor["target_coeff"])
            - anchor_sign * int(relation["target_coeff"])
        )
        if not any(coeffs) and target_coeff % int(order) == 0:
            counters["large_prime_trivial"] += 1
            return
        public_sum = target_coeff * Q
        for c, P in zip(coeffs, fb_points):
            if c:
                public_sum += c * P
        if public_sum != E(0):
            counters["large_prime_public_failure"] += 1
            return
        combined = {
            "kind": "large_prime_eliminated",
            "coefficients": coeffs,
            "target_coeff": int(target_coeff),
            "nonzero": int(sum(1 for c in coeffs if c) + (1 if target_coeff else 0)),
            "large_prime_key": lp_key,
            "large_prime_signs": (anchor_sign, relation_sign),
            "source_rows": (
                {
                    "interpolation_constraints": anchor["interpolation_constraints"],
                    "residual_roots": anchor["residual_roots"],
                    "coefficients": anchor["coefficients"],
                    "target_coeff": anchor["target_coeff"],
                    "large_prime_key": anchor["large_prime_key"],
                    "large_prime_sign": anchor["large_prime_sign"],
                },
                {
                    "interpolation_constraints": relation["interpolation_constraints"],
                    "residual_roots": relation["residual_roots"],
                    "coefficients": relation["coefficients"],
                    "target_coeff": relation["target_coeff"],
                    "large_prime_key": relation["large_prime_key"],
                    "large_prime_sign": relation["large_prime_sign"],
                },
            ),
        }
        counters["large_prime_eliminated"] += 1
        verification_group_ops += combined["nonzero"]
        if stream_rank:
            del large_prime_anchors[lp_key]
        retain_final(combined)

    target_stats = {
        "considered": 0,
        "liftable": 0,
        "group_ops": 0,
    }

    def collect_zero_phase():
        # Four factor-base lifts determine a cubic and leave a residual
        # quadratic to split.
        for indices in itertools.combinations(range(fb_size), 4):
            if collection_complete:
                break
            for xs in itertools.product(*(fb_lifts[i] for i in indices)):
                if collection_complete:
                    break
                counters["zero_attempts"] += 1
                constraints = [(x, fb_points[i][1]) for i, x in zip(indices, xs)]
                labels = [("fb", i) for i in indices]
                relation, status = residual_relation(
                    cell,
                    constraints,
                    labels,
                    fb_points,
                    fb_by_u,
                    Q,
                    allow_large_prime=allow_large_prime,
                )
                retain(relation, status)

    def collect_target_phase():
        # A rational lift exists when the U-coordinate of -lambda*Q is a square.
        target_point = -Q
        for lam in range(1, min(int(lambda_max), int(order) - 1) + 1):
            if collection_complete:
                break
            if lam > 1:
                target_point -= Q
                target_stats["group_ops"] += 1
            target_stats["considered"] += 1
            if target_point == E(0):
                continue
            tx = canonical_sqrt(target_point[0])
            if tx is None:
                continue
            if int(target_point[0]) in fb_by_u:
                continue
            target_stats["liftable"] += 1
            target_xs = [tx] if tx == 0 else [tx, -tx]
            for target_x in target_xs:
                if collection_complete:
                    break
                for indices in itertools.combinations(range(fb_size), 3):
                    if collection_complete:
                        break
                    for xs in itertools.product(*(fb_lifts[i] for i in indices)):
                        if collection_complete:
                            break
                        counters["target_attempts"] += 1
                        constraints = [(target_x, target_point[1])] + [
                            (x, fb_points[i][1]) for i, x in zip(indices, xs)
                        ]
                        labels = [("target", -lam)] + [
                            ("fb", i) for i in indices
                        ]
                        relation, status = residual_relation(
                            cell,
                            constraints,
                            labels,
                            fb_points,
                            fb_by_u,
                            Q,
                            allow_large_prime=allow_large_prime,
                        )
                        retain(relation, status)

    if stream_rank:
        collect_target_phase()
        if not collection_complete:
            collect_zero_phase()
    else:
        collect_zero_phase()
        collect_target_phase()

    target_multiples_considered = target_stats["considered"]
    target_multiples_liftable = target_stats["liftable"]
    target_multiple_group_ops = target_stats["group_ops"]

    target_relations = [r for r in relations if r["target_coeff"] != 0]
    zero_relations = [r for r in relations if r["target_coeff"] == 0]
    solve = solve_relation_system(order, fb_size, relations, G, Q)
    public_rows_valid = all(
        sum((Integer(c) * P for c, P in zip(r["coefficients"], fb_points)), E(0))
        + Integer(r["target_coeff"]) * Q
        == E(0)
        for r in relations
    )

    kernel_attempts = counters["zero_attempts"] + counters["target_attempts"]
    factor_base_scan_attempts = int(cell["field"].order())
    matrix_nonzero_entries = sum(r["nonzero"] for r in relations)
    large_prime_anchor_entries = sum(
        relation["nonzero"] + 2 for relation in large_prime_anchors.values()
    )
    if not stream_rank:
        large_prime_anchor_peak_entries = max(
            large_prime_anchor_peak_entries, large_prime_anchor_entries
        )
    charged_lower_bound_ops = (
        kernel_attempts
        + factor_base_scan_attempts
        + verification_group_ops
        + target_multiple_group_ops
        + matrix_nonzero_entries
        + large_prime_anchor_entries
        + counters["online_rank_tests"]
    )
    field_ops_proxy = (
        kernel_attempts * 160
        + factor_base_scan_attempts * 8
        + matrix_nonzero_entries
        + counters["online_rank_tests"] * fb_size**2
    )
    memory_entries = (
        fb_size
        + sum(len(items) for items in fb_lifts)
        + matrix_nonzero_entries
        + 2 * len(relations)
        + large_prime_anchor_peak_entries
    )
    rho = rho_ops(order)
    if not target_relations:
        classification = "native_relation_only" if zero_relations else "no_relations"
    elif solve["rank"] < solve["variables"]:
        classification = "rank_deficient"
    elif not solve["target_recovered"]:
        classification = "target_descent_deficient"
    elif charged_lower_bound_ops > rho:
        classification = "baseline_lost"
    else:
        classification = "candidate"

    return {
        "order": int(order),
        "fb_size": int(fb_size),
        "liftable_canonical_points": int(liftable_count),
        "generator": list(point_key(G)),
        "target": list(point_key(Q)),
        "large_prime_enabled": bool(allow_large_prime),
        "stream_rank_enabled": bool(stream_rank),
        "large_prime_anchor_cap": int(anchor_cap) if anchor_cap is not None else None,
        "collection_early_stopped": bool(collection_complete),
        "lambda_max": int(lambda_max),
        "target_multiples_considered": int(target_multiples_considered),
        "target_multiples_liftable": int(target_multiples_liftable),
        "target_multiple_group_ops": int(target_multiple_group_ops),
        "kernel_attempts": int(kernel_attempts),
        "factor_base_scan_attempts": int(factor_base_scan_attempts),
        "zero_attempts": int(counters["zero_attempts"]),
        "target_attempts": int(counters["target_attempts"]),
        "attempt_status": counters,
        "relations": int(len(relations)),
        "zero_relations": int(len(zero_relations)),
        "target_relations": int(len(target_relations)),
        "direct_relations": int(sum(r["kind"] == "direct" for r in relations)),
        "large_prime_relations": int(
            sum(r["kind"] == "large_prime_eliminated" for r in relations)
        ),
        "large_prime_buckets": int(len(large_prime_anchors)),
        "large_prime_anchor_entries": int(large_prime_anchor_entries),
        "large_prime_anchor_peak_entries": int(large_prime_anchor_peak_entries),
        "matrix_nonzero_entries": int(matrix_nonzero_entries),
        "rank": int(solve["rank"]),
        "variables": int(solve["variables"]),
        "augmented_rank": int(solve["augmented_rank"]),
        "consistent": bool(solve["consistent"]),
        "target_recovered": bool(solve["target_recovered"]),
        "recovered_secret": solve["recovered_secret"],
        "public_rows_valid": bool(public_rows_valid),
        "verification_group_ops": int(verification_group_ops),
        "field_ops_proxy": int(field_ops_proxy),
        "charged_lower_bound_ops": int(charged_lower_bound_ops),
        "rho_ops": float(rho),
        "charged_ops_over_rho": float(charged_lower_bound_ops / rho),
        "memory_entries": int(memory_entries),
        "memory_over_sqrt_n": float(memory_entries / math.sqrt(int(order))),
        "rank_per_1000_attempts": float(1000.0 * solve["rank"] / max(1, kernel_attempts)),
        "target_relation_rate": float(len(target_relations) / max(1, counters["target_attempts"])),
        "classification": classification,
        "factor_base_points": [list(point_key(P)) for P in fb_points],
        "relation_rows": relations,
    }


def fit_attempt_rank_exponent(rows):
    usable = [r for r in rows if r["rank"] > 0 and r["kernel_attempts"] > 0]
    if len(usable) < 3:
        return {
            "available": False,
            "reason": "fewer than three nonzero-rank cells",
        }
    xs = [math.log(float(r["order"])) for r in usable]
    ys = [math.log(float(r["kernel_attempts"]) / float(r["rank"])) for r in usable]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0:
        return {"available": False, "reason": "zero order variance"}
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator
    intercept = y_mean - slope * x_mean
    return {
        "available": True,
        "cells": len(usable),
        "slope": float(slope),
        "intercept": float(intercept),
        "metric": "kernel_attempts_per_rank",
        "warning": "toy empirical fit; not an asymptotic claim",
    }


def run_suite(
    allow_large_prime=False, stream_rank=False, anchor_cap=None, only_p=None
):
    configs = [
        {"p": 101, "seed": 20260713, "fb_size": 8, "secret": 17, "lambda_max": 16},
        {"p": 211, "seed": 20260714, "fb_size": 10, "secret": 29, "lambda_max": 20},
        {"p": 431, "seed": 20260715, "fb_size": 12, "secret": 37, "lambda_max": 24},
        {
            "p": 4099,
            "seed": 20260716,
            "fb_size": 16,
            "secret": 137,
            "lambda_max": 32,
            "fixed": (4041, 4067),
        },
    ]
    rows = []
    controls = []
    cells = []
    for config in configs:
        if only_p is not None and int(config["p"]) != int(only_p):
            continue
        t0 = time.time()
        cell = find_curve(config["p"], config["seed"], config.get("fixed"))
        control = split_identity_control(cell, config["seed"])
        witness = quotient_witness(cell)
        factor_base = build_factor_base(cell, config["fb_size"], config["seed"])
        G = factor_base[0][0]
        Q = Integer(config["secret"]) * G
        row = collect_relations(
            cell,
            factor_base,
            Q,
            config["lambda_max"],
            allow_large_prime=allow_large_prime,
            stream_rank=stream_rank,
            anchor_cap=anchor_cap,
        )
        row["p"] = int(config["p"])
        row["seed"] = int(config["seed"])
        row["A"] = int(cell["A"])
        row["B"] = int(cell["B"])
        row["curve_search_attempts"] = int(cell["attempts"])
        row["auxiliary_order"] = int(cell["Eaux"].order())
        row["auxiliary_order_factorization"] = str(factor(Integer(cell["Eaux"].order())))
        row["wall_seconds"] = float(time.time() - t0)
        rows.append(row)
        controls.append({"p": int(config["p"]), **control})
        cells.append(
            {
                "p": int(config["p"]),
                "curve": "Y^2 = U^3 + %s*U + %s" % (int(cell["A"]), int(cell["B"])),
                "cover": "y^2 = x^6 + %s*x^2 + %s" % (int(cell["A"]), int(cell["B"])),
                "auxiliary": "V^2 = W^3 + %s*W^2 + %s"
                % (int(cell["A"]), int(cell["B"]**2)),
                "quotient_witness": witness,
            }
        )
        print(
            "p=%s n=%s fb=%s rel=%s target=%s rank=%s/%s recovered=%s ops/rho=%.2f class=%s"
            % (
                config["p"],
                row["order"],
                row["fb_size"],
                row["relations"],
                row["target_relations"],
                row["rank"],
                row["variables"],
                row["target_recovered"],
                row["charged_ops_over_rho"],
                row["classification"],
            )
        )

    control_pass = all(
        item["found"]
        and item["pi1_sum_zero"]
        and item["pi2_sum_zero"]
        and item["negative_control_nonzero"]
        for item in controls
    )
    any_recovery = any(row["target_recovered"] for row in rows)
    any_candidate = any(row["classification"] == "candidate" for row in rows)
    result = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": "HOME=/private/tmp/codex-sage-home sage %s%s --out %s"
        % (
            source_path(),
            "".join(
                [
                    " --stream-rank" if stream_rank else (" --large-prime" if allow_large_prime else ""),
                    " --anchor-cap %s" % anchor_cap if anchor_cap is not None else "",
                    " --only-p %s" % only_p if only_p is not None else "",
                ]
            ),
            parse_out(
                "experiments/ecdlp_isogeny/po_transfer_003c_result.json"
                if stream_rank
                else (
                    "experiments/ecdlp_isogeny/po_transfer_003b_result.json"
                    if allow_large_prime
                    else "experiments/ecdlp_isogeny/po_transfer_003_result.json"
                )
            ),
        ),
        "source_sha256": source_hash(),
        "claim_or_task": (
            "PO-transfer-003d bounded-anchor streaming transfer"
            if anchor_cap is not None
            else (
                "PO-transfer-003c streaming rank-basis transfer"
                if stream_rank
                else (
                    "PO-transfer-003b bielliptic one-large-prime elimination"
                    if allow_large_prime
                    else "PO-transfer-003 bielliptic norm-interpolation transfer"
                )
            )
        ),
        "status": "OBSERVATION",
        "scope": ["TOY-EVIDENCE", "MODEL-BOUND", "CONTROLLED-INSTANCES"],
        "candidate": (
            "Push principal divisors div(y-v(x)) from a split genus-2 cover to the original "
            "elliptic quotient, coupling v to known multiples of the public target before "
            "factoring the residual quadratic."
        ),
        "assumptions": [
            "Prime-order toy E1/F_p only.",
            "A fixture scalar generates the public Q outside the collector; the collector receives only public G and Q.",
            "No factor-base discrete logarithms are computed or consumed.",
            "Each interpolation/residual test is charged as at least one group-operation equivalent.",
            "The field-operation proxy is reported separately and is not an exact cycle model.",
            "A toy fit is not an asymptotic or deployment claim.",
        ],
        "relation_identity": (
            "If v(x)^2-(x^6+A*x^2+B) splits, pushforward of div(y-v(x)) gives "
            "sum_i (x_i^2,v(x_i)) = O on E1."
        ),
        "controls_pass": bool(control_pass),
        "controls": controls,
        "correspondence_cells": cells,
        "rows": rows,
        "attempt_rank_fit": fit_attempt_rank_exponent(rows),
        "gate": {
            "large_prime_enabled": bool(allow_large_prime),
            "stream_rank_enabled": bool(stream_rank),
            "large_prime_anchor_cap": int(anchor_cap) if anchor_cap is not None else None,
            "only_p": int(only_p) if only_p is not None else None,
            "any_target_recovery": bool(any_recovery),
            "any_below_rho_candidate": bool(any_candidate),
            "success": bool(control_pass and any_candidate),
            "po_transfer_002_recovering_reference_ops_over_rho": 178.04488864776442,
        },
    }
    return result


def main():
    stream_rank = "--stream-rank" in sys.argv[1:]
    allow_large_prime = "--large-prime" in sys.argv[1:] or stream_rank
    anchor_cap = parse_int_arg("--anchor-cap")
    only_p = parse_int_arg("--only-p")
    out_path = parse_out(
        "experiments/ecdlp_isogeny/po_transfer_003c_result.json"
        if stream_rank
        else (
            "experiments/ecdlp_isogeny/po_transfer_003b_result.json"
            if allow_large_prime
            else "experiments/ecdlp_isogeny/po_transfer_003_result.json"
        )
    )
    result = run_suite(
        allow_large_prime=allow_large_prime,
        stream_rank=stream_rank,
        anchor_cap=anchor_cap,
        only_p=only_p,
    )
    with open(out_path, "w") as handle:
        json.dump(json_clean(result), handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("wrote %s" % out_path)


main()
