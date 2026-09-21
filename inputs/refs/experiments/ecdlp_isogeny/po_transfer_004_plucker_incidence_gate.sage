#!/usr/bin/env sage
# PO-transfer-004: Plucker incidence compression gate for BNIT.
#
# Controlled toy research only.  This script consumes public PO-transfer-003c
# data, reconstructs the bielliptic factor-base lifts, and tests whether the
# target-plus-four-point co-cubic condition has non-random finite-geometric
# structure.  Brute pair-pair incidence work and an ideal-oracle floor are
# reported separately; orthogonality is never charged as an equality hash.

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


def parse_arg(flag, default=None):
    args = list(sys.argv[1:])
    if flag in args:
        return args[args.index(flag) + 1]
    return default


def source_hash(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def point_key(P):
    if P == P.curve()(0):
        return ("O",)
    return (int(P[0]), int(P[1]))


def point_from_json(E, value):
    if value == ["O"] or value == ("O",):
        return E(0)
    return E(Integer(value[0]), Integer(value[1]))


def canonical_sqrt(value):
    if not value.is_square():
        return None
    root = value.sqrt()
    return root if int(root) <= int(-root) else -root


def canonical_y_point(E, u):
    rhs = u**3 + E.a4() * u + E.a6()
    y = canonical_sqrt(rhs)
    if y is None:
        return None
    return E(u, y)


def rho_ops(order):
    return 0.886 * math.sqrt(int(order))


def interpolate_polynomial(R, X, points):
    if len(set(x for x, _y in points)) != len(points):
        return None
    value = R(0)
    for i, (xi, yi) in enumerate(points):
        numerator = R(1)
        denominator = xi.parent()(1)
        for j, (xj, _yj) in enumerate(points):
            if i == j:
                continue
            numerator *= X - xj
            denominator *= xi - xj
        value += (yi / denominator) * numerator
    return value


def find_curve(p, seed):
    field = GF(Integer(p))
    R = PolynomialRing(field, "x")
    X = R.gen()
    rng = random.Random(int(seed))
    for attempt in range(1, 10001):
        A = field(rng.randrange(1, int(p)))
        B = field(rng.randrange(1, int(p)))
        E = EllipticCurve(field, [0, 0, 0, A, B])
        order = Integer(E.order())
        if not order.is_prime(proof=False):
            continue
        Fpoly = X**6 + A * X**2 + B
        if Fpoly.gcd(Fpoly.derivative()).degree() != 0:
            continue
        if HyperellipticCurve(Fpoly).genus() != 2:
            continue
        return {
            "field": field,
            "R": R,
            "X": X,
            "A": A,
            "B": B,
            "E": E,
            "order": order,
            "Fpoly": Fpoly,
            "curve_search_attempts": attempt,
        }
    raise RuntimeError("no fresh prime-order bielliptic cell found")


def make_curve(p, A, B):
    field = GF(Integer(p))
    R = PolynomialRing(field, "x")
    X = R.gen()
    A = field(A)
    B = field(B)
    E = EllipticCurve(field, [0, 0, 0, A, B])
    Fpoly = X**6 + A * X**2 + B
    if Fpoly.gcd(Fpoly.derivative()).degree() != 0:
        raise ValueError("frozen cover is not smooth")
    return {
        "field": field,
        "R": R,
        "X": X,
        "A": A,
        "B": B,
        "E": E,
        "order": Integer(E.order()),
        "Fpoly": Fpoly,
        "curve_search_attempts": 0,
    }


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
        candidate_count += 1
        score = (
            (int(P[0]) * 1103515245 + int(P[1]) * 12345 + int(seed) * 2654435761)
            % int(field.order()),
            int(P[0]),
            int(P[1]),
        )
        selected.append((score, P, x))
        selected.sort(key=lambda item: item[0])
        if len(selected) > requested_size:
            selected.pop()
    if candidate_count < requested_size:
        raise RuntimeError("insufficient liftable factor-base points")
    points = [item[1] for item in selected]
    lifts = []
    for index, (_score, P, x) in enumerate(selected):
        xs = [x] if x == 0 else [x, -x]
        for sign_index, lift_x in enumerate(xs):
            lifts.append(
                {
                    "lift_id": 2 * index + sign_index,
                    "fb_index": index,
                    "x": lift_x,
                    "y": P[1],
                }
            )
    return points, lifts, candidate_count


def select_blind_public_target(E, fb_points, seed):
    field = E.base_field()
    excluded = {point_key(P) for P in fb_points}
    start = (int(seed) * 2246822519 + 3266489917) % int(field.order())
    for offset in range(int(field.order())):
        u = field((start + offset) % int(field.order()))
        Q = canonical_y_point(E, u)
        if Q is not None and Q != E(0) and point_key(Q) not in excluded:
            return Q
    raise RuntimeError("no blind public target outside the factor base")


def quotient_vector(lift, target_lift):
    x = lift["x"]
    tx = target_lift["x"]
    return vector(
        x.parent(),
        [x - tx, x**2 - tx**2, x**3 - tx**3, lift["y"] - target_lift["y"]],
    )


def bivector(a, b):
    return vector(
        a.base_ring(),
        [
            a[0] * b[1] - a[1] * b[0],
            a[0] * b[2] - a[2] * b[0],
            a[0] * b[3] - a[3] * b[0],
            a[1] * b[2] - a[2] * b[1],
            a[1] * b[3] - a[3] * b[1],
            a[2] * b[3] - a[3] * b[2],
        ],
    )


def normalize_projective(value):
    for coordinate in value:
        if coordinate != 0:
            normalized = value / coordinate
            return tuple(int(x) for x in normalized)
    return None


def klein_value(z):
    return z[0] * z[5] - z[1] * z[4] + z[2] * z[3]


def wedge_pair(z, w):
    return (
        z[0] * w[5]
        - z[1] * w[4]
        + z[2] * w[3]
        + z[3] * w[2]
        - z[4] * w[1]
        + z[5] * w[0]
    )


def build_pair_records(lifts, target_lift, random_vectors=None):
    vectors = {}
    for lift in lifts:
        if random_vectors is None:
            vectors[lift["lift_id"]] = quotient_vector(lift, target_lift)
        else:
            vectors[lift["lift_id"]] = random_vectors[lift["lift_id"]]
    records = []
    degenerate = 0
    for first, second in itertools.combinations(lifts, 2):
        if first["fb_index"] == second["fb_index"]:
            continue
        z = bivector(vectors[first["lift_id"]], vectors[second["lift_id"]])
        normalized = normalize_projective(z)
        if normalized is None:
            degenerate += 1
            continue
        if klein_value(z) != 0:
            raise AssertionError("non-decomposable pair bivector")
        records.append(
            {
                "lift_ids": (first["lift_id"], second["lift_id"]),
                "fb_indices": (first["fb_index"], second["fb_index"]),
                "z": z,
                "normalized": normalized,
            }
        )
    unique_planes = len(set(record["normalized"] for record in records))
    return records, degenerate, unique_planes


def enumerate_incidences(pair_records):
    pair_pair_iterations = 0
    disjoint_wedge_tests = 0
    raw_hits = 0
    unique = {}
    for first_index in range(len(pair_records)):
        first = pair_records[first_index]
        first_fb = set(first["fb_indices"])
        for second_index in range(first_index + 1, len(pair_records)):
            pair_pair_iterations += 1
            second = pair_records[second_index]
            if first_fb.intersection(second["fb_indices"]):
                continue
            disjoint_wedge_tests += 1
            if wedge_pair(first["z"], second["z"]) != 0:
                continue
            raw_hits += 1
            lift_ids = tuple(sorted(first["lift_ids"] + second["lift_ids"]))
            unique.setdefault(
                lift_ids,
                {
                    "first_pair": first["lift_ids"],
                    "second_pair": second["lift_ids"],
                    "fb_indices": tuple(sorted(first["fb_indices"] + second["fb_indices"])),
                },
            )
    return {
        "pair_pair_iterations": pair_pair_iterations,
        "disjoint_wedge_tests": disjoint_wedge_tests,
        "raw_hits": raw_hits,
        "unique_hits": list(unique.values()),
    }


def random_quotient_vectors(field, lifts, seed):
    rng = random.Random(int(seed))
    result = {}
    for lift in lifts:
        while True:
            value = vector(field, [field(rng.randrange(int(field.order()))) for _ in range(4)])
            if value != 0:
                result[lift["lift_id"]] = value
                break
    return result


def relation_from_incidence(cell, target_lift, lift_by_id, fb_points, hit):
    R = cell["R"]
    X = cell["X"]
    E = cell["E"]
    Fpoly = cell["Fpoly"]
    selected_lifts = [lift_by_id[lift_id] for lift_id in sorted(set(hit["first_pair"] + hit["second_pair"]))]
    if len(selected_lifts) != 4:
        return None, "duplicate_lift"
    selected_x = [target_lift["x"]] + [lift["x"] for lift in selected_lifts]
    if len(set(selected_x)) != 5:
        return None, "repeated_x"
    points = [(target_lift["x"], target_lift["y"])] + [
        (lift["x"], lift["y"]) for lift in selected_lifts[:3]
    ]
    v = interpolate_polynomial(R, X, points)
    if v is None or v.degree() > 3:
        return None, "interpolation_failure"
    fourth = selected_lifts[3]
    if v(fourth["x"]) != fourth["y"]:
        return None, "false_incidence"
    H = v**2 - Fpoly
    if H.degree() != 6 or H.gcd(H.derivative()).degree() != 0:
        return None, "degenerate_intersection"
    selected_poly = X - target_lift["x"]
    for lift in selected_lifts:
        selected_poly *= X - lift["x"]
    residual, remainder = H.quo_rem(selected_poly)
    if remainder != 0 or residual.degree() != 1:
        return None, "residual_degree"
    residual_root = -residual[0] / residual[1]
    residual_point = E(residual_root**2, v(residual_root))
    coefficients = [0] * len(fb_points)
    for lift in selected_lifts:
        coefficients[lift["fb_index"]] += 1
    target_coeff = int(target_lift["target_coeff"])
    by_u = {int(P[0]): i for i, P in enumerate(fb_points)}
    fb_index = by_u.get(int(residual_point[0]))
    relation = {
        "coefficients": tuple(coefficients),
        "target_coeff": target_coeff,
        "target_lambda": int(target_lift["lambda"]),
        "target_x": int(target_lift["x"]),
        "selected_lift_ids": tuple(lift["lift_id"] for lift in selected_lifts),
        "selected_fb_indices": tuple(lift["fb_index"] for lift in selected_lifts),
        "v_coefficients": tuple(int(c) for c in v.list()),
        "residual_root": int(residual_root),
    }
    if fb_index is not None:
        canonical = fb_points[fb_index]
        if residual_point == canonical:
            coefficients[fb_index] += 1
        elif residual_point == -canonical:
            coefficients[fb_index] -= 1
        else:
            return None, "orientation_failure"
        relation["coefficients"] = tuple(coefficients)
        relation["kind"] = "direct"
    else:
        canonical = canonical_y_point(E, residual_point[0])
        if residual_point == canonical:
            sign = 1
        elif residual_point == -canonical:
            sign = -1
        else:
            return None, "orientation_failure"
        relation["kind"] = "single_large_prime"
        relation["large_prime_key"] = point_key(canonical)
        relation["large_prime_sign"] = sign

    public_sum = target_coeff * target_lift["Q"]
    for coefficient, point in zip(relation["coefficients"], fb_points):
        public_sum += Integer(coefficient) * point
    if relation["kind"] == "single_large_prime":
        public_sum += Integer(relation["large_prime_sign"]) * point_from_json(
            E, relation["large_prime_key"]
        )
    if public_sum != E(0):
        return None, "public_verification_failure"
    relation["nonzero"] = sum(1 for c in relation["coefficients"] if c) + 1
    if relation["kind"] == "single_large_prime":
        relation["nonzero"] += 1
    return relation, relation["kind"]


def eliminate_large_primes(E, Q, fb_points, direct_relations, partial_relations):
    final_relations = list(direct_relations)
    anchors = {}
    collisions = 0
    public_failures = 0
    for relation in partial_relations:
        key = tuple(relation["large_prime_key"])
        anchor = anchors.get(key)
        if anchor is None:
            anchors[key] = relation
            continue
        collisions += 1
        anchor_sign = int(anchor["large_prime_sign"])
        relation_sign = int(relation["large_prime_sign"])
        coefficients = tuple(
            relation_sign * a - anchor_sign * b
            for a, b in zip(anchor["coefficients"], relation["coefficients"])
        )
        target_coeff = (
            relation_sign * int(anchor["target_coeff"])
            - anchor_sign * int(relation["target_coeff"])
        )
        if not any(coefficients) and target_coeff % int(E.order()) == 0:
            continue
        public_sum = target_coeff * Q
        for coefficient, point in zip(coefficients, fb_points):
            public_sum += Integer(coefficient) * point
        if public_sum != E(0):
            public_failures += 1
            continue
        final_relations.append(
            {
                "kind": "large_prime_eliminated",
                "coefficients": coefficients,
                "target_coeff": target_coeff,
                "large_prime_key": key,
                "large_prime_signs": (anchor_sign, relation_sign),
                "source_rows": (anchor, relation),
                "nonzero": sum(1 for c in coefficients if c) + (1 if target_coeff else 0),
            }
        )

    unique = []
    seen = set()
    for relation in final_relations:
        key = (tuple(relation["coefficients"]), int(relation["target_coeff"]) % int(E.order()))
        if key in seen:
            continue
        seen.add(key)
        unique.append(relation)
    return unique, len(anchors), collisions, public_failures


def solve_relation_system(order, fb_points, Q, relations):
    K = GF(Integer(order))
    variables = len(fb_points)
    if not relations:
        return {
            "variables": variables,
            "relations": 0,
            "rank": 0,
            "augmented_rank": 0,
            "target_recovered": False,
            "recovered_scalar": None,
        }
    rows = []
    rhs = []
    for relation in relations:
        coefficients = relation["coefficients"]
        rows.append([K(c) for c in coefficients[1:]] + [K(relation["target_coeff"])])
        rhs.append(K(-coefficients[0]))
    A = matrix(K, rows)
    b = vector(K, rhs)
    rank = int(A.rank())
    augmented_rank = int(A.augment(b).rank())
    recovered_scalar = None
    target_recovered = False
    if rank == variables and rank == augmented_rank:
        recovered_scalar = int(Integer(A.solve_right(b)[-1]) % Integer(order))
        target_recovered = recovered_scalar * fb_points[0] == Q
    return {
        "variables": variables,
        "relations": len(relations),
        "rank": rank,
        "augmented_rank": augmented_rank,
        "target_recovered": bool(target_recovered),
        "recovered_scalar": recovered_scalar,
    }


def target_lifts(E, Q, lambda_max, fb_points):
    field = E.base_field()
    fb_u = {int(P[0]) for P in fb_points}
    result = []
    target_point = -Q
    for lam in range(1, min(int(lambda_max), int(E.order()) - 1) + 1):
        if lam > 1:
            target_point -= Q
        if target_point == E(0) or int(target_point[0]) in fb_u:
            continue
        x = canonical_sqrt(field(target_point[0]))
        if x is None:
            continue
        for target_x in ([x] if x == 0 else [x, -x]):
            result.append(
                {
                    "lambda": lam,
                    "target_coeff": -lam,
                    "x": target_x,
                    "y": target_point[1],
                    "Q": Q,
                }
            )
    return result


def planted_control(cell, lifts, fb_points):
    R = cell["R"]
    X = cell["X"]
    Fpoly = cell["Fpoly"]
    field = cell["field"]
    E = cell["E"]
    lift_by_id = {lift["lift_id"]: lift for lift in lifts}
    for selected in itertools.combinations(lifts, 4):
        if len({lift["fb_index"] for lift in selected}) != 4:
            continue
        points = [(lift["x"], lift["y"]) for lift in selected]
        v = interpolate_polynomial(R, X, points)
        if v is None or v.degree() > 3:
            continue
        H = v**2 - Fpoly
        if H.degree() != 6 or H.gcd(H.derivative()).degree() != 0:
            continue
        selected_poly = R(1)
        for lift in selected:
            selected_poly *= X - lift["x"]
        residual, remainder = H.quo_rem(selected_poly)
        if remainder != 0 or residual.degree() != 2:
            continue
        roots = residual.roots(multiplicities=False)
        if len(roots) != 2:
            continue
        target_x = roots[0]
        residual_x = roots[1]
        target_Q = E(target_x**2, v(target_x))
        target_lift = {
            "lambda": -1,
            "target_coeff": 1,
            "x": target_x,
            "y": v(target_x),
            "Q": target_Q,
        }
        vectors = [quotient_vector(lift, target_lift) for lift in selected]
        z1 = bivector(vectors[0], vectors[1])
        z2 = bivector(vectors[2], vectors[3])
        wedge_zero = wedge_pair(z1, z2) == 0
        scrambled = vector(field, list(vectors[3]))
        scrambled[3] += field(1)
        wrong_nonzero = wedge_pair(z1, bivector(vectors[2], scrambled)) != 0
        image_points = [target_Q] + [E(lift["x"]**2, lift["y"]) for lift in selected]
        image_points.append(E(residual_x**2, v(residual_x)))
        replay_valid = sum(image_points, E(0)) == E(0)
        hit = {
            "first_pair": tuple(lift["lift_id"] for lift in selected[:2]),
            "second_pair": tuple(lift["lift_id"] for lift in selected[2:]),
        }
        replay_relation, replay_status = relation_from_incidence(
            cell, target_lift, lift_by_id, fb_points, hit
        )
        return {
            "found": True,
            "wedge_zero": bool(wedge_zero),
            "scrambled_wedge_nonzero": bool(wrong_nonzero),
            "principal_divisor_replay_valid": bool(replay_valid),
            "production_replay_valid": replay_relation is not None,
            "production_replay_status": replay_status,
            "target_xy": [int(target_lift["x"]), int(target_lift["y"])],
            "selected_xy": [
                [int(lift["x"]), int(lift["y"])] for lift in selected
            ],
            "selected_fb_indices": [int(lift["fb_index"]) for lift in selected],
            "residual_xy": [int(residual_x), int(v(residual_x))],
            "v_coefficients": [int(c) for c in v.list()],
        }
    return {
        "found": False,
        "wedge_zero": False,
        "scrambled_wedge_nonzero": False,
        "principal_divisor_replay_valid": False,
        "production_replay_valid": False,
    }


def analyze_configuration(cell, public, fb_size, random_seed, bnit_reference):
    t0 = time.time()
    E = cell["E"]
    field = cell["field"]
    order = cell["order"]
    fb_points_all, lifts_all, liftable_count = build_factor_base(
        cell, public["max_fb_size"], public["seed"]
    )
    fb_points = fb_points_all[:fb_size]
    lifts = [lift for lift in lifts_all if lift["fb_index"] < fb_size]
    G = fb_points[0]
    Q = public["Q"]
    if public.get("expected_G") is not None and point_key(G) != public["expected_G"]:
        raise ValueError("factor-base regeneration changed frozen generator")
    expected_factor_base = public.get("expected_factor_base")
    if expected_factor_base is not None:
        regenerated = [point_key(P) for P in fb_points_all[: len(expected_factor_base)]]
        if regenerated != expected_factor_base:
            raise ValueError("factor-base regeneration changed frozen prefix")
    targets = target_lifts(E, Q, public["lambda_max"], fb_points)
    lift_by_id = {lift["lift_id"]: lift for lift in lifts}

    totals = {
        "pair_records": 0,
        "degenerate_pairs": 0,
        "unique_planes_sum": 0,
        "pair_pair_iterations": 0,
        "disjoint_wedge_tests": 0,
        "raw_hits": 0,
        "unique_hits": 0,
        "replay_failures": 0,
    }
    replay_status = {}
    direct_relations = []
    partial_relations = []
    target_summaries = []

    for target_index, target_lift in enumerate(targets):
        pairs, degenerate, unique_planes = build_pair_records(lifts, target_lift)
        incidence = enumerate_incidences(pairs)
        totals["pair_records"] += len(pairs)
        totals["degenerate_pairs"] += degenerate
        totals["unique_planes_sum"] += unique_planes
        for key in ["pair_pair_iterations", "disjoint_wedge_tests", "raw_hits"]:
            totals[key] += incidence[key]
        totals["unique_hits"] += len(incidence["unique_hits"])
        accepted = 0
        for hit in incidence["unique_hits"]:
            relation, status = relation_from_incidence(
                cell, target_lift, lift_by_id, fb_points, hit
            )
            replay_status[status] = replay_status.get(status, 0) + 1
            if relation is None:
                totals["replay_failures"] += 1
                continue
            accepted += 1
            if relation["kind"] == "direct":
                direct_relations.append(relation)
            else:
                partial_relations.append(relation)
        target_summaries.append(
            {
                "target_index": target_index,
                "lambda": int(target_lift["lambda"]),
                "target_x": int(target_lift["x"]),
                "pairs": len(pairs),
                "disjoint_wedge_tests": incidence["disjoint_wedge_tests"],
                "unique_hits": len(incidence["unique_hits"]),
                "accepted_relations": accepted,
            }
        )

    final_relations, lp_anchors, lp_collisions, lp_public_failures = eliminate_large_primes(
        E, Q, fb_points, direct_relations, partial_relations
    )
    solve = solve_relation_system(order, fb_points, Q, final_relations)
    public_rows_valid = all(
        sum(
            (Integer(c) * P for c, P in zip(relation["coefficients"], fb_points)),
            E(0),
        )
        + Integer(relation["target_coeff"]) * Q
        == E(0)
        for relation in final_relations
    )

    control = None
    random_control = None
    if targets:
        control = planted_control(cell, lifts, fb_points)
        random_replicates = []
        for target_index, target_lift in enumerate(targets):
            replicate_count = 8 if fb_size == public["base_fb_size"] and target_index == 0 else 1
            for replicate in range(replicate_count):
                replicate_seed = (
                    random_seed + 10000019 * target_index + 104729 * replicate
                )
                random_vectors = random_quotient_vectors(field, lifts, replicate_seed)
                random_pairs, random_degenerate, random_unique_planes = build_pair_records(
                    lifts, target_lift, random_vectors=random_vectors
                )
                random_incidence = enumerate_incidences(random_pairs)
                random_replicates.append(
                    {
                        "target_index": target_index,
                        "target_lambda": int(target_lift["lambda"]),
                        "target_x": int(target_lift["x"]),
                        "seed": int(replicate_seed),
                        "pair_records": len(random_pairs),
                        "degenerate_pairs": random_degenerate,
                        "unique_planes": random_unique_planes,
                        "pair_pair_iterations": random_incidence["pair_pair_iterations"],
                        "disjoint_wedge_tests": random_incidence["disjoint_wedge_tests"],
                        "raw_hits": random_incidence["raw_hits"],
                        "unique_hits": len(random_incidence["unique_hits"]),
                    }
                )
        random_tests = sum(row["disjoint_wedge_tests"] for row in random_replicates)
        random_raw_hits = sum(row["raw_hits"] for row in random_replicates)
        random_unique_hits = sum(row["unique_hits"] for row in random_replicates)
        random_control = {
            "replicate_count": len(random_replicates),
            "replicates": random_replicates,
            "disjoint_wedge_tests": random_tests,
            "raw_hits": random_raw_hits,
            "unique_hits": random_unique_hits,
            "raw_incidence_rate": float(random_raw_hits / max(1, random_tests)),
            "deduplicated_incidence_rate": float(
                random_unique_hits / max(1, random_tests)
            ),
        }

    raw_incidence_rate = float(
        totals["raw_hits"] / max(1, totals["disjoint_wedge_tests"])
    )
    deduplicated_incidence_rate = float(
        totals["unique_hits"] / max(1, totals["disjoint_wedge_tests"])
    )
    q = Integer(field.order())
    expected_random_rate = float(
        (q**3 + 2 * q**2 + q + 1) / ((q**2 + 1) * (q**2 + q + 1))
    )
    control_rate = (
        random_control["raw_incidence_rate"]
        if random_control is not None
        else expected_random_rate
    )
    pair_table_peak = max((summary["pairs"] for summary in target_summaries), default=0)
    matrix_entries = sum(relation["nonzero"] for relation in final_relations)
    charged_actual = (
        int(field.order())
        + totals["pair_records"]
        + totals["pair_pair_iterations"]
        + totals["disjoint_wedge_tests"]
        + totals["unique_hits"]
        + matrix_entries
    )
    ideal_oracle_ops = (
        int(field.order())
        + totals["pair_records"]
        + totals["unique_hits"]
        + matrix_entries
    )
    memory_entries = pair_table_peak * 8 + lp_anchors * 8 + matrix_entries + 3 * len(final_relations)
    rho = rho_ops(order)
    if not targets:
        classification = "no_target_lifts"
    elif solve["rank"] < solve["variables"]:
        classification = "rank_deficient"
    elif not solve["target_recovered"]:
        classification = "target_descent_deficient"
    elif charged_actual > rho:
        classification = "baseline_lost"
    else:
        classification = "candidate"

    return {
        "label": public["label"],
        "source_kind": public["source_kind"],
        "p": int(field.order()),
        "A": int(cell["A"]),
        "B": int(cell["B"]),
        "order": int(order),
        "seed": int(public["seed"]),
        "random_control_seed": int(random_seed),
        "curve_search_attempts": int(cell["curve_search_attempts"]),
        "fb_size": int(fb_size),
        "liftable_points": int(liftable_count),
        "lift_count": len(lifts),
        "generator": list(point_key(G)),
        "target": list(point_key(Q)),
        "target_lifts": len(targets),
        "totals": totals,
        "replay_status": replay_status,
        "direct_relations": len(direct_relations),
        "partial_relations": len(partial_relations),
        "large_prime_anchors": lp_anchors,
        "large_prime_collisions": lp_collisions,
        "large_prime_public_failures": lp_public_failures,
        "final_relations": len(final_relations),
        "target_relations": sum(r["target_coeff"] != 0 for r in final_relations),
        "rank": solve["rank"],
        "variables": solve["variables"],
        "augmented_rank": solve["augmented_rank"],
        "target_recovered": solve["target_recovered"],
        "recovered_scalar": solve["recovered_scalar"],
        "public_rows_valid": bool(public_rows_valid),
        "raw_incidence_rate": raw_incidence_rate,
        "deduplicated_incidence_rate": deduplicated_incidence_rate,
        "expected_random_rate": expected_random_rate,
        "incidence_excess_vs_expected": float(raw_incidence_rate / expected_random_rate),
        "incidence_excess_vs_control": float(
            raw_incidence_rate / control_rate if control_rate > 0 else float("inf")
        ),
        "planted_control": control,
        "random_control": random_control,
        "pair_table_peak_records": pair_table_peak,
        "charged_actual_ops": int(charged_actual),
        "ideal_oracle_ops": int(ideal_oracle_ops),
        "rho_ops": float(rho),
        "charged_actual_over_rho": float(charged_actual / rho),
        "ideal_oracle_over_rho": float(ideal_oracle_ops / rho),
        "bnit_003c_kernel_attempts": (
            int(bnit_reference) if bnit_reference is not None else None
        ),
        "actual_ops_over_bnit_kernels": (
            float(charged_actual / bnit_reference) if bnit_reference else None
        ),
        "ideal_oracle_over_bnit_kernels": (
            float(ideal_oracle_ops / bnit_reference) if bnit_reference else None
        ),
        "memory_entries": int(memory_entries),
        "memory_over_sqrt_n": float(memory_entries / math.sqrt(int(order))),
        "classification": classification,
        "target_summaries": target_summaries,
        "relation_rows": final_relations,
        "wall_seconds": float(time.time() - t0),
    }


def fit_exponent(rows, metric):
    usable = [row for row in rows if row[metric] > 0]
    if len(usable) < 3:
        return {"available": False, "metric": metric}
    xs = [math.log(float(row["order"])) for row in usable]
    ys = [math.log(float(row[metric])) for row in usable]
    xm = sum(xs) / len(xs)
    ym = sum(ys) / len(ys)
    denominator = sum((x - xm) ** 2 for x in xs)
    slope = sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / denominator
    return {
        "available": True,
        "metric": metric,
        "cells": len(usable),
        "slope": float(slope),
        "warning": "toy empirical fit; not an asymptotic claim",
    }


def load_public_cells(source_path, bnit_path):
    with open(source_path, "r") as handle:
        source = json.load(handle)
    with open(bnit_path, "r") as handle:
        bnit = json.load(handle)
    bnit_by_p = {int(row["p"]): int(row["kernel_attempts"]) for row in bnit["rows"]}
    cells = []
    for row in source["rows"]:
        p = int(row["p"])
        base_fb = int(row["fb_size"])
        cell = make_curve(p, row["A"], row["B"])
        cells.append(
            (
                cell,
                {
                    "label": "frozen_p%s" % p,
                    "source_kind": "frozen",
                    "seed": int(row["seed"]),
                    "base_fb_size": base_fb,
                    "max_fb_size": base_fb + 2,
                    "lambda_max": int(row["lambda_max"]),
                    "Q": point_from_json(cell["E"], row["target"]),
                    "expected_G": tuple(row["generator"]),
                    "expected_factor_base": [
                        tuple(point) for point in row["factor_base_points"]
                    ],
                    "fb_sizes": [max(4, base_fb - 2), base_fb, base_fb + 2],
                },
                bnit_by_p[p],
            )
        )

    fresh_configs = [
        {"p": 103, "seed": 20260720, "fb": 8, "lambda_max": 16},
        {"p": 223, "seed": 20260721, "fb": 10, "lambda_max": 20},
        {"p": 439, "seed": 20260722, "fb": 12, "lambda_max": 24},
        {"p": 4127, "seed": 20260723, "fb": 16, "lambda_max": 32},
    ]
    for config in fresh_configs:
        cell = find_curve(config["p"], config["seed"])
        max_fb = config["fb"] + 2
        points, _lifts, _count = build_factor_base(cell, max_fb, config["seed"])
        Q = select_blind_public_target(cell["E"], points, config["seed"])
        cells.append(
            (
                cell,
                {
                    "label": "fresh_p%s" % config["p"],
                    "source_kind": "fresh",
                    "seed": config["seed"],
                    "base_fb_size": config["fb"],
                    "max_fb_size": max_fb,
                    "lambda_max": config["lambda_max"],
                    "Q": Q,
                    "expected_G": point_key(points[0]),
                    "expected_factor_base": [point_key(P) for P in points],
                    "fb_sizes": [max(4, config["fb"] - 2), config["fb"], max_fb],
                },
                None,
            )
        )
    return source, bnit, cells


def main():
    default_source = "experiments/ecdlp_isogeny/po_transfer_003d_result.json"
    default_bnit = "experiments/ecdlp_isogeny/po_transfer_003c_result.json"
    source_path = parse_arg("--source", default_source)
    bnit_path = parse_arg("--bnit", default_bnit)
    out_path = parse_arg("--out", "experiments/ecdlp_isogeny/po_transfer_004_result.json")
    script_path = os.path.abspath(sys.argv[0])
    if script_path.endswith(".sage.py") and os.path.exists(script_path[:-3]):
        script_path = script_path[:-3]

    source, bnit, cells = load_public_cells(source_path, bnit_path)
    rows = []
    for cell_index, (cell, public, bnit_reference) in enumerate(cells):
        for fb_size in public["fb_sizes"]:
            row = analyze_configuration(
                cell,
                public,
                fb_size,
                public["seed"] + 1000003 * (cell_index + 1) + fb_size,
                bnit_reference,
            )
            rows.append(row)
            print(
                "%s fb=%s targets=%s pairs=%s tests=%s hits=%s rank=%s/%s recovered=%s actual/rho=%.2f oracle/rho=%.2f class=%s"
                % (
                    row["label"],
                    fb_size,
                    row["target_lifts"],
                    row["pair_table_peak_records"],
                    row["totals"]["disjoint_wedge_tests"],
                    row["totals"]["unique_hits"],
                    row["rank"],
                    row["variables"],
                    row["target_recovered"],
                    row["charged_actual_over_rho"],
                    row["ideal_oracle_over_rho"],
                    row["classification"],
                )
            )

    base_rows = [
        row
        for row in rows
        if row["fb_size"]
        == next(
            public["base_fb_size"]
            for _cell, public, _reference in cells
            if public["label"] == row["label"]
        )
    ]
    planted_production_all_configs = all(
        row["planted_control"]
        and row["planted_control"]["found"]
        and row["planted_control"]["wedge_zero"]
        and row["planted_control"]["scrambled_wedge_nonzero"]
        and row["planted_control"]["principal_divisor_replay_valid"]
        and row["planted_control"]["production_replay_valid"]
        for row in rows
    )
    random_control_all_targets_all_configs = all(
        row["random_control"] is not None
        and set(
            int(replicate["target_index"])
            for replicate in row["random_control"]["replicates"]
        )
        == set(range(row["target_lifts"]))
        for row in rows
    )
    controls_pass = bool(
        planted_production_all_configs and random_control_all_targets_all_configs
    )
    any_candidate = any(row["classification"] == "candidate" for row in rows)
    full_rank_cells = sorted(
        set(row["label"] for row in rows if row["target_recovered"])
    )
    fits = {
        "charged_actual_ops": fit_exponent(base_rows, "charged_actual_ops"),
        "ideal_oracle_ops": fit_exponent(base_rows, "ideal_oracle_ops"),
        "memory_entries": fit_exponent(base_rows, "memory_entries"),
    }
    frozen_base_rows = [row for row in base_rows if row["source_kind"] == "frozen"]
    shared_anchor = max(frozen_base_rows, key=lambda row: row["p"])
    fresh_base_rows = [row for row in base_rows if row["source_kind"] == "fresh"]
    structural_criteria = {
        "controls_and_public_replay": bool(
            controls_pass
            and all(row["public_rows_valid"] for row in rows)
            and all(row["large_prime_public_failures"] == 0 for row in rows)
        ),
        "target_recovery_at_least_three_sizes": len(full_rank_cells) >= 3,
        "concrete_sub_pair_pair_query_structure": False,
        "sixteen_x_fewer_than_bnit_shared_anchor": bool(
            shared_anchor["actual_ops_over_bnit_kernels"] is not None
            and shared_anchor["actual_ops_over_bnit_kernels"] <= 1.0 / 16.0
        ),
        "memory_below_four_sqrt_n": all(
            row["memory_over_sqrt_n"] < 4.0 for row in base_rows
        ),
        "persistent_fresh_incidence_excess": all(
            row["incidence_excess_vs_control"] > 1.0 for row in fresh_base_rows
        ),
    }
    structural_success = all(structural_criteria.values())
    charged_fit = fits["charged_actual_ops"]
    algorithmic_criteria = {
        "structural_success": structural_success,
        "charged_below_rho_on_one_configuration": any_candidate,
        "charged_toy_fit_at_most_one_half": bool(
            charged_fit["available"] and charged_fit["slope"] <= 0.5
        ),
    }
    algorithmic_success = all(algorithmic_criteria.values())
    result = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claim_or_task": "PO-transfer-004 Plucker incidence compression gate",
        "status": "NEGATIVE RESULT",
        "scope": ["TOY-EVIDENCE", "MODEL-BOUND", "CONTROLLED-INSTANCES"],
        "command": "HOME=/private/tmp/codex-sage-home sage %s --source %s --bnit %s --out %s"
        % (script_path, source_path, bnit_path, out_path),
        "source_sha256": source_hash(script_path),
        "input_source": os.path.abspath(source_path),
        "input_source_sha256": source_hash(source_path),
        "bnit_source": os.path.abspath(bnit_path),
        "bnit_source_sha256": source_hash(bnit_path),
        "formal_predicate": (
            "For quotient vectors w_i in F_p^5/<m(T)>, target plus four cover points "
            "lie on a cubic iff (w1 wedge w2) wedge (w3 wedge w4)=0."
        ),
        "accounting_warning": (
            "Brute pair-pair incidence work is charged. ideal_oracle_ops omits orthogonality "
            "query cost and is a diagnostic floor, not an algorithm."
        ),
        "fresh_pre_registered": [
            {"p": 103, "seed": 20260720},
            {"p": 223, "seed": 20260721},
            {"p": 439, "seed": 20260722},
            {"p": 4127, "seed": 20260723},
        ],
        "fresh_target_rule": (
            "Deterministic first canonical public curve point outside the factor-base prefix; "
            "no fixture discrete logarithm is constructed or consumed."
        ),
        "controls_pass": bool(controls_pass),
        "control_coverage": {
            "planted_production_all_configs": bool(planted_production_all_configs),
            "random_control_all_targets_all_configs": bool(
                random_control_all_targets_all_configs
            ),
        },
        "rows": rows,
        "fits": fits,
        "gate": {
            "controls_pass": bool(controls_pass),
            "planted_production_all_configs": bool(planted_production_all_configs),
            "random_control_all_targets_all_configs": bool(
                random_control_all_targets_all_configs
            ),
            "full_rank_target_recovery_cells": full_rank_cells,
            "full_rank_target_recovery_cell_count": len(full_rank_cells),
            "any_below_rho_candidate": bool(any_candidate),
            "shared_bnit_anchor": {
                "label": shared_anchor["label"],
                "fb_size": shared_anchor["fb_size"],
                "actual_ops_over_bnit_kernels": shared_anchor[
                    "actual_ops_over_bnit_kernels"
                ],
            },
            "structural_criteria": structural_criteria,
            "structural_success": bool(structural_success),
            "algorithmic_criteria": algorithmic_criteria,
            "algorithmic_success": bool(algorithmic_success),
            "success": bool(algorithmic_success),
        },
    }
    with open(out_path, "w") as handle:
        json.dump(json_clean(result), handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("wrote %s" % out_path)


main()
