#!/usr/bin/env sage
# Independent public replay verifier for PO-transfer-004.

import hashlib
import itertools
import json
import math
import os
import random
import sys
import time


def parse_arg(flag, default=None):
    args = list(sys.argv[1:])
    if flag in args:
        return args[args.index(flag) + 1]
    return default


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


def build_factor_base(E, requested_size, seed):
    field = E.base_field()
    selected = []
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
        selected.append((score, P, x))
        selected.sort(key=lambda item: item[0])
        if len(selected) > requested_size:
            selected.pop()
    if len(selected) != requested_size:
        raise ValueError("factor-base reconstruction is short")
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
    return points, lifts


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
            return tuple(int(x) for x in value / coordinate)
    return None


def wedge_pair(z, w):
    return (
        z[0] * w[5]
        - z[1] * w[4]
        + z[2] * w[3]
        + z[3] * w[2]
        - z[4] * w[1]
        + z[5] * w[0]
    )


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


def random_vectors(field, lifts, seed):
    rng = random.Random(int(seed))
    result = {}
    for lift in lifts:
        while True:
            value = vector(field, [field(rng.randrange(int(field.order()))) for _ in range(4)])
            if value != 0:
                result[lift["lift_id"]] = value
                break
    return result


def incidence_counts(lifts, target_lift, supplied_vectors=None):
    vectors = {}
    for lift in lifts:
        vectors[lift["lift_id"]] = (
            quotient_vector(lift, target_lift)
            if supplied_vectors is None
            else supplied_vectors[lift["lift_id"]]
        )
    pairs = []
    degenerate = 0
    for first, second in itertools.combinations(lifts, 2):
        if first["fb_index"] == second["fb_index"]:
            continue
        z = bivector(vectors[first["lift_id"]], vectors[second["lift_id"]])
        normalized = normalize_projective(z)
        if normalized is None:
            degenerate += 1
            continue
        if z[0] * z[5] - z[1] * z[4] + z[2] * z[3] != 0:
            raise ValueError("pair bivector left the Klein quadric")
        pairs.append(
            {
                "lift_ids": (first["lift_id"], second["lift_id"]),
                "fb_indices": (first["fb_index"], second["fb_index"]),
                "z": z,
                "normalized": normalized,
            }
        )
    iterations = 0
    tests = 0
    raw_hits = 0
    unique_hits = set()
    for first_index in range(len(pairs)):
        first = pairs[first_index]
        first_fb = set(first["fb_indices"])
        for second_index in range(first_index + 1, len(pairs)):
            iterations += 1
            second = pairs[second_index]
            if first_fb.intersection(second["fb_indices"]):
                continue
            tests += 1
            if wedge_pair(first["z"], second["z"]) == 0:
                raw_hits += 1
                unique_hits.add(tuple(sorted(first["lift_ids"] + second["lift_ids"])))
    return {
        "pair_records": len(pairs),
        "degenerate_pairs": degenerate,
        "unique_planes": len(set(pair["normalized"] for pair in pairs)),
        "pair_pair_iterations": iterations,
        "disjoint_wedge_tests": tests,
        "raw_hits": raw_hits,
        "unique_hits": len(unique_hits),
    }


def verify_primitive(E, R, X, Fpoly, fb_points, lift_by_id, Q, relation):
    field = E.base_field()
    selected = [lift_by_id[int(value)] for value in relation["selected_lift_ids"]]
    if len(selected) != 4 or len({lift["lift_id"] for lift in selected}) != 4:
        raise ValueError("primitive row does not select four lifts")
    lam = int(relation["target_lambda"])
    T = -Integer(lam) * Q
    target_x = field(relation["target_x"])
    if int(relation["target_coeff"]) != -lam or target_x**2 != T[0]:
        raise ValueError("target lift does not match public Q")
    target_lift = {"x": target_x, "y": T[1]}
    xs = [target_x] + [lift["x"] for lift in selected]
    if len(set(xs)) != 5:
        raise ValueError("primitive row has repeated x")
    vectors = [quotient_vector(lift, target_lift) for lift in selected]
    if wedge_pair(bivector(vectors[0], vectors[1]), bivector(vectors[2], vectors[3])) != 0:
        raise ValueError("primitive row fails Plucker predicate")

    v = R([field(value) for value in relation["v_coefficients"]])
    if v(target_x) != T[1] or any(v(lift["x"]) != lift["y"] for lift in selected):
        raise ValueError("primitive cubic misses an exported point")
    H = v**2 - Fpoly
    if H.degree() != 6 or H.gcd(H.derivative()).degree() != 0:
        raise ValueError("primitive intersection is not squarefree degree six")
    selected_poly = X - target_x
    for lift in selected:
        selected_poly *= X - lift["x"]
    residual, remainder = H.quo_rem(selected_poly)
    if remainder != 0 or residual.degree() != 1:
        raise ValueError("primitive residual is not linear")
    residual_root = -residual[0] / residual[1]
    if int(residual_root) != int(relation["residual_root"]):
        raise ValueError("primitive residual root mismatch")
    residual_point = E(residual_root**2, v(residual_root))

    coefficients = [0] * len(fb_points)
    for lift in selected:
        coefficients[lift["fb_index"]] += 1
    by_u = {int(P[0]): index for index, P in enumerate(fb_points)}
    fb_index = by_u.get(int(residual_point[0]))
    expected = {
        "coefficients": None,
        "target_coeff": -lam,
        "kind": None,
    }
    if fb_index is not None:
        if residual_point == fb_points[fb_index]:
            coefficients[fb_index] += 1
        elif residual_point == -fb_points[fb_index]:
            coefficients[fb_index] -= 1
        else:
            raise ValueError("factor-base orientation mismatch")
        expected["kind"] = "direct"
    else:
        canonical = canonical_y_point(E, residual_point[0])
        if residual_point == canonical:
            sign = 1
        elif residual_point == -canonical:
            sign = -1
        else:
            raise ValueError("large-prime orientation mismatch")
        expected["kind"] = "single_large_prime"
        expected["large_prime_key"] = point_key(canonical)
        expected["large_prime_sign"] = sign
    expected["coefficients"] = tuple(coefficients)
    if tuple(int(c) for c in relation["coefficients"]) != expected["coefficients"]:
        raise ValueError("primitive coefficient mismatch")
    if relation["kind"] != expected["kind"]:
        raise ValueError("primitive relation kind mismatch")
    if expected["kind"] == "single_large_prime":
        if tuple(relation["large_prime_key"]) != expected["large_prime_key"]:
            raise ValueError("primitive large-prime key mismatch")
        if int(relation["large_prime_sign"]) != expected["large_prime_sign"]:
            raise ValueError("primitive large-prime sign mismatch")

    public_sum = -Integer(lam) * Q
    for coefficient, point in zip(coefficients, fb_points):
        public_sum += Integer(coefficient) * point
    if expected["kind"] == "single_large_prime":
        public_sum += Integer(expected["large_prime_sign"]) * point_from_json(
            E, expected["large_prime_key"]
        )
    if public_sum != E(0):
        raise ValueError("primitive row does not replay publicly")
    return expected


def verify_final_relation(E, R, X, Fpoly, fb_points, lift_by_id, Q, relation):
    coefficients = tuple(int(c) for c in relation["coefficients"])
    target_coeff = int(relation["target_coeff"])
    if relation["kind"] == "direct":
        expected = verify_primitive(E, R, X, Fpoly, fb_points, lift_by_id, Q, relation)
        if coefficients != expected["coefficients"] or target_coeff != expected["target_coeff"]:
            raise ValueError("direct row differs from primitive witness")
    elif relation["kind"] == "large_prime_eliminated":
        first = verify_primitive(
            E, R, X, Fpoly, fb_points, lift_by_id, Q, relation["source_rows"][0]
        )
        second = verify_primitive(
            E, R, X, Fpoly, fb_points, lift_by_id, Q, relation["source_rows"][1]
        )
        if first["large_prime_key"] != second["large_prime_key"]:
            raise ValueError("eliminated large-prime keys differ")
        first_sign = first["large_prime_sign"]
        second_sign = second["large_prime_sign"]
        combined = tuple(
            second_sign * a - first_sign * b
            for a, b in zip(first["coefficients"], second["coefficients"])
        )
        combined_target = (
            second_sign * first["target_coeff"] - first_sign * second["target_coeff"]
        )
        if coefficients != combined or target_coeff != combined_target:
            raise ValueError("large-prime elimination mismatch")
    else:
        raise ValueError("unknown final relation kind")
    public_sum = Integer(target_coeff) * Q
    for coefficient, point in zip(coefficients, fb_points):
        public_sum += Integer(coefficient) * point
    if public_sum != E(0):
        raise ValueError("final relation does not replay publicly")


def verify_matrix(E, fb_points, Q, relations, recorded):
    K = GF(Integer(recorded["order"]))
    rows = []
    rhs = []
    for relation in relations:
        coefficients = relation["coefficients"]
        rows.append([K(c) for c in coefficients[1:]] + [K(relation["target_coeff"])])
        rhs.append(K(-coefficients[0]))
    if rows:
        A = matrix(K, rows)
        b = vector(K, rhs)
        rank = int(A.rank())
        augmented_rank = int(A.augment(b).rank())
    else:
        A = None
        b = None
        rank = 0
        augmented_rank = 0
    recovered_scalar = None
    target_recovered = False
    if rank == len(fb_points) and rank == augmented_rank:
        recovered_scalar = int(Integer(A.solve_right(b)[-1]) % Integer(recorded["order"]))
        target_recovered = recovered_scalar * fb_points[0] == Q
    checks = {
        "rank": rank,
        "augmented_rank": augmented_rank,
        "target_recovered": target_recovered,
        "recovered_scalar": recovered_scalar,
    }
    for key, value in checks.items():
        if recorded[key] != value:
            raise ValueError("recorded matrix field differs: %s" % key)
    return checks


def verify_planted_control(E, R, X, Fpoly, fb_points, lifts, control):
    field = E.base_field()
    target = {"x": field(control["target_xy"][0]), "y": field(control["target_xy"][1])}
    selected = [
        {"x": field(value[0]), "y": field(value[1])} for value in control["selected_xy"]
    ]
    lift_keys = {(int(lift["x"]), int(lift["y"]), int(lift["fb_index"])) for lift in lifts}
    for point, fb_index in zip(selected, control["selected_fb_indices"]):
        if (int(point["x"]), int(point["y"]), int(fb_index)) not in lift_keys:
            raise ValueError("planted point is not an exported factor-base lift")
        if E(point["x"]**2, point["y"]) != fb_points[int(fb_index)]:
            raise ValueError("planted factor-base image mismatch")
    residual = {"x": field(control["residual_xy"][0]), "y": field(control["residual_xy"][1])}
    v = R([field(value) for value in control["v_coefficients"]])
    if v(target["x"]) != target["y"]:
        raise ValueError("planted cubic misses target")
    if any(v(point["x"]) != point["y"] for point in selected + [residual]):
        raise ValueError("planted cubic misses a cover point")
    H = v**2 - Fpoly
    if H.degree() != 6 or H.gcd(H.derivative()).degree() != 0:
        raise ValueError("planted intersection is not squarefree")
    if any(H(point["x"]) != 0 for point in [target] + selected + [residual]):
        raise ValueError("planted point is not an intersection root")
    vectors = [quotient_vector(point, target) for point in selected]
    wedge_zero = wedge_pair(bivector(vectors[0], vectors[1]), bivector(vectors[2], vectors[3])) == 0
    scrambled = vector(field, list(vectors[3]))
    scrambled[3] += field(1)
    scrambled_nonzero = (
        wedge_pair(bivector(vectors[0], vectors[1]), bivector(vectors[2], scrambled)) != 0
    )
    image_points = [E(point["x"]**2, point["y"]) for point in [target] + selected + [residual]]
    replay = sum(image_points, E(0)) == E(0)
    if not wedge_zero or not scrambled_nonzero or not replay:
        raise ValueError("planted control failed independent replay")
    if not control["wedge_zero"] or not control["scrambled_wedge_nonzero"]:
        raise ValueError("planted control flags disagree")
    if not control["principal_divisor_replay_valid"]:
        raise ValueError("planted replay flag disagrees")
    if not control["production_replay_valid"]:
        raise ValueError("planted production replay flag disagrees")


def verify_incidence_counters(E, Q, fb_points, lifts, recorded):
    # The final represented lambda reconstructs the complete ordered public target list;
    # skipped trailing lambdas cannot change any measured incidence counter.
    expected_summaries = recorded["target_summaries"]
    if not expected_summaries:
        return []
    lambda_max = max(int(summary["lambda"]) for summary in expected_summaries)
    while True:
        targets = target_lifts(E, Q, lambda_max, fb_points)
        if len(targets) >= len(expected_summaries):
            break
        lambda_max += 1
        if lambda_max >= int(E.order()):
            raise ValueError("cannot reconstruct target-lift sequence")
    targets = targets[: len(expected_summaries)]
    totals = {
        "pair_records": 0,
        "degenerate_pairs": 0,
        "unique_planes_sum": 0,
        "pair_pair_iterations": 0,
        "disjoint_wedge_tests": 0,
        "raw_hits": 0,
        "unique_hits": 0,
    }
    for target, summary in zip(targets, expected_summaries):
        if int(summary["lambda"]) != int(target["lambda"]) or int(summary["target_x"]) != int(target["x"]):
            raise ValueError("target summary order mismatch")
        counts = incidence_counts(lifts, target)
        for key in totals:
            source_key = "unique_planes" if key == "unique_planes_sum" else key
            totals[key] += counts[source_key]
        comparisons = {
            "pairs": counts["pair_records"],
            "disjoint_wedge_tests": counts["disjoint_wedge_tests"],
            "unique_hits": counts["unique_hits"],
        }
        for key, value in comparisons.items():
            if int(summary[key]) != value:
                raise ValueError("target incidence counter mismatch: %s" % key)
    for key, value in totals.items():
        if int(recorded["totals"][key]) != value:
            raise ValueError("aggregate incidence counter mismatch: %s" % key)
    return targets


def verify_random_control(E, lifts, recorded, targets):
    control = recorded["random_control"]
    if control is None:
        return
    field = E.base_field()
    aggregate_tests = 0
    aggregate_raw_hits = 0
    aggregate_unique_hits = 0
    for expected in control["replicates"]:
        target = targets[int(expected["target_index"])]
        if int(expected["target_lambda"]) != int(target["lambda"]):
            raise ValueError("random-control target lambda mismatch")
        if int(expected["target_x"]) != int(target["x"]):
            raise ValueError("random-control target x mismatch")
        supplied = random_vectors(field, lifts, expected["seed"])
        counts = incidence_counts(lifts, target, supplied_vectors=supplied)
        for key in [
            "pair_records",
            "degenerate_pairs",
            "unique_planes",
            "pair_pair_iterations",
            "disjoint_wedge_tests",
            "raw_hits",
            "unique_hits",
        ]:
            if int(expected[key]) != counts[key]:
                raise ValueError("random-control counter mismatch: %s" % key)
        aggregate_tests += counts["disjoint_wedge_tests"]
        aggregate_raw_hits += counts["raw_hits"]
        aggregate_unique_hits += counts["unique_hits"]
    if int(control["disjoint_wedge_tests"]) != aggregate_tests:
        raise ValueError("random-control test total mismatch")
    if int(control["raw_hits"]) != aggregate_raw_hits:
        raise ValueError("random-control raw-hit total mismatch")
    if int(control["unique_hits"]) != aggregate_unique_hits:
        raise ValueError("random-control unique-hit total mismatch")


def main():
    input_path = parse_arg("--input")
    if input_path is None:
        raise SystemExit("usage: sage po_transfer_004_verify.sage --input RESULT.json [--out VERIFY.json]")
    with open(input_path, "r") as handle:
        artifact = json.load(handle)
    generator_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "po_transfer_004_plucker_incidence_gate.sage",
    )
    with open(generator_path, "rb") as handle:
        generator_hash = hashlib.sha256(handle.read()).hexdigest()
    if artifact["source_sha256"] != generator_hash:
        raise ValueError("generator source hash mismatch")

    verified_relations = 0
    verified_primitives = 0
    cells = []
    for recorded in artifact["rows"]:
        field = GF(Integer(recorded["p"]))
        R = PolynomialRing(field, "x")
        X = R.gen()
        A = field(recorded["A"])
        B = field(recorded["B"])
        E = EllipticCurve(field, [0, 0, 0, A, B])
        Fpoly = X**6 + A * X**2 + B
        if Integer(E.order()) != Integer(recorded["order"]):
            raise ValueError("recorded curve order mismatch")
        fb_points, lifts = build_factor_base(E, int(recorded["fb_size"]), recorded["seed"])
        if point_key(fb_points[0]) != tuple(recorded["generator"]):
            raise ValueError("recorded generator mismatch")
        Q = point_from_json(E, recorded["target"])
        lift_by_id = {lift["lift_id"]: lift for lift in lifts}
        for relation in recorded["relation_rows"]:
            verify_final_relation(E, R, X, Fpoly, fb_points, lift_by_id, Q, relation)
            verified_relations += 1
            verified_primitives += 1 if relation["kind"] == "direct" else 2
        checks = verify_matrix(E, fb_points, Q, recorded["relation_rows"], recorded)
        targets = verify_incidence_counters(E, Q, fb_points, lifts, recorded)
        if recorded["planted_control"] is not None:
            verify_planted_control(
                E,
                R,
                X,
                Fpoly,
                fb_points,
                lifts,
                recorded["planted_control"],
            )
            verify_random_control(E, lifts, recorded, targets)
        cells.append(
            {
                "label": recorded["label"],
                "fb_size": int(recorded["fb_size"]),
                "relations": len(recorded["relation_rows"]),
                "rank": int(checks["rank"]),
                "target_recovered": bool(checks["target_recovered"]),
            }
        )

    result = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input": os.path.abspath(input_path),
        "input_sha256": hashlib.sha256(open(input_path, "rb").read()).hexdigest(),
        "input_source_sha256": artifact["source_sha256"],
        "status": "VERIFIED",
        "cells_verified": int(len(cells)),
        "public_relations_verified": int(verified_relations),
        "primitive_witnesses_verified": int(verified_primitives),
        "cells": cells,
    }
    out_path = parse_arg("--out")
    if out_path:
        with open(out_path, "w") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))


main()
