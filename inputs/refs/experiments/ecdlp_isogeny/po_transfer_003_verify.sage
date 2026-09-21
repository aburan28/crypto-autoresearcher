#!/usr/bin/env sage
# Independent public replay verifier for PO-transfer-003 variants.

import hashlib
import json
import os
import sys
import time


def parse_arg(flag, default=None):
    args = list(sys.argv[1:])
    if flag in args:
        return args[args.index(flag) + 1]
    return default


def point_from_json(E, value):
    if value == ["O"] or value == ("O",):
        return E(0)
    return E(Integer(value[0]), Integer(value[1]))


def point_key(P):
    if P == P.curve()(0):
        return ("O",)
    return (int(P[0]), int(P[1]))


def canonical_y_point(E, u):
    rhs = u**3 + E.a4() * u + E.a6()
    if not rhs.is_square():
        return None
    y = rhs.sqrt()
    if int(y) > int(-y):
        y = -y
    return E(u, y)


def interpolate(R, X, constraints):
    field = R.base_ring()
    points = [(field(item["x"]), field(item["y"])) for item in constraints]
    if len(set(x for x, _y in points)) != len(points):
        raise ValueError("duplicate interpolation x-coordinate")
    value = R(0)
    for i, (xi, yi) in enumerate(points):
        numerator = R(1)
        denominator = field(1)
        for j, (xj, _yj) in enumerate(points):
            if i == j:
                continue
            numerator *= X - xj
            denominator *= xi - xj
        value += (yi / denominator) * numerator
    return value


def reconstruct_source(E, Fpoly, R, X, fb_points, Q, source, expect_large_prime):
    field = E.base_field()
    constraints = source["interpolation_constraints"]
    v = interpolate(R, X, constraints)
    H = v**2 - Fpoly
    if H.degree() != 6 or H.gcd(H.derivative()).degree() != 0:
        raise ValueError("source intersection is not squarefree degree six")
    residual_roots = [field(value) for value in source["residual_roots"]]
    if len(residual_roots) != 2 or any(H(root) != 0 for root in residual_roots):
        raise ValueError("invalid residual roots")

    by_u = {int(P[0]): i for i, P in enumerate(fb_points)}
    coeffs = [0] * len(fb_points)
    target_coeff = 0
    for item in constraints:
        if item["label"] == "fb":
            coeffs[int(item["label_value"])] += 1
        elif item["label"] == "target":
            target_coeff += int(item["label_value"])
        else:
            raise ValueError("unknown interpolation label")

    large_primes = []
    for root in residual_roots:
        P = E(root**2, v(root))
        idx = by_u.get(int(P[0]))
        if idx is not None:
            if P == fb_points[idx]:
                coeffs[idx] += 1
            elif P == -fb_points[idx]:
                coeffs[idx] -= 1
            else:
                raise ValueError("factor-base orientation mismatch")
            continue
        canonical = canonical_y_point(E, P[0])
        if P == canonical:
            sign = 1
        elif P == -canonical:
            sign = -1
        else:
            raise ValueError("large-prime orientation mismatch")
        large_primes.append((canonical, sign))

    expected_count = 1 if expect_large_prime else 0
    if len(large_primes) != expected_count:
        raise ValueError("unexpected large-prime count")
    public_sum = target_coeff * Q
    for coefficient, point in zip(coeffs, fb_points):
        public_sum += Integer(coefficient) * point
    if large_primes:
        public_sum += Integer(large_primes[0][1]) * large_primes[0][0]
    if public_sum != E(0):
        raise ValueError("source row does not replay")

    result = {
        "coefficients": tuple(coeffs),
        "target_coeff": int(target_coeff),
    }
    if large_primes:
        result["large_prime_key"] = point_key(large_primes[0][0])
        result["large_prime_sign"] = int(large_primes[0][1])
    return result


def verify_relation(E, Fpoly, R, X, fb_points, Q, relation):
    coefficients = tuple(int(c) for c in relation["coefficients"])
    target_coeff = int(relation["target_coeff"])
    public_sum = target_coeff * Q
    for coefficient, point in zip(coefficients, fb_points):
        public_sum += Integer(coefficient) * point
    if public_sum != E(0):
        raise ValueError("final row does not replay")

    if relation["kind"] == "direct":
        source = reconstruct_source(E, Fpoly, R, X, fb_points, Q, relation, False)
        if source["coefficients"] != coefficients or source["target_coeff"] != target_coeff:
            raise ValueError("direct row differs from interpolation witness")
        return
    if relation["kind"] != "large_prime_eliminated":
        raise ValueError("unknown relation kind")

    first = reconstruct_source(
        E, Fpoly, R, X, fb_points, Q, relation["source_rows"][0], True
    )
    second = reconstruct_source(
        E, Fpoly, R, X, fb_points, Q, relation["source_rows"][1], True
    )
    if first["large_prime_key"] != second["large_prime_key"]:
        raise ValueError("large-prime keys do not match")
    first_sign = first["large_prime_sign"]
    second_sign = second["large_prime_sign"]
    combined_coefficients = tuple(
        second_sign * a - first_sign * b
        for a, b in zip(first["coefficients"], second["coefficients"])
    )
    combined_target = (
        second_sign * first["target_coeff"] - first_sign * second["target_coeff"]
    )
    if combined_coefficients != coefficients or combined_target != target_coeff:
        raise ValueError("large-prime elimination coefficients do not replay")


def verify_matrix(E, order, fb_points, Q, relations, recorded):
    K = GF(Integer(order))
    rows = []
    rhs = []
    for relation in relations:
        coefficients = relation["coefficients"]
        rows.append([K(c) for c in coefficients[1:]] + [K(relation["target_coeff"])])
        rhs.append(K(-coefficients[0]))
    if not rows:
        rank = 0
        augmented_rank = 0
        recovered = None
        target_recovered = False
    else:
        A = matrix(K, rows)
        b = vector(K, rhs)
        rank = int(A.rank())
        augmented_rank = int(A.augment(b).rank())
        recovered = None
        target_recovered = False
        if rank == int(recorded["variables"]) and rank == augmented_rank:
            recovered = int(Integer(A.solve_right(b)[-1]) % Integer(order))
            target_recovered = recovered * fb_points[0] == Q
    if rank != int(recorded["rank"]):
        raise ValueError("recorded rank mismatch")
    if augmented_rank != int(recorded["augmented_rank"]):
        raise ValueError("recorded augmented rank mismatch")
    if target_recovered != bool(recorded["target_recovered"]):
        raise ValueError("recorded target-recovery mismatch")
    if recovered != recorded["recovered_secret"]:
        raise ValueError("recorded recovered scalar mismatch")
    return rank, target_recovered, recovered


def main():
    input_path = parse_arg("--input")
    if input_path is None:
        raise SystemExit("usage: sage po_transfer_003_verify.sage --input RESULT.json [--out VERIFY.json]")
    with open(input_path, "r") as handle:
        artifact = json.load(handle)

    generator = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "po_transfer_003_bielliptic_norm_interpolation.sage",
    )
    with open(generator, "rb") as handle:
        generator_hash = hashlib.sha256(handle.read()).hexdigest()
    if artifact["source_sha256"] != generator_hash:
        raise ValueError("generator source hash mismatch")

    verified_rows = 0
    cells = []
    for recorded in artifact["rows"]:
        field = GF(Integer(recorded["p"]))
        R = PolynomialRing(field, "x")
        X = R.gen()
        A = field(recorded["A"])
        B = field(recorded["B"])
        E = EllipticCurve(field, [0, 0, 0, A, B])
        Fpoly = X**6 + A * X**2 + B
        fb_points = [point_from_json(E, value) for value in recorded["factor_base_points"]]
        G = point_from_json(E, recorded["generator"])
        Q = point_from_json(E, recorded["target"])
        if G != fb_points[0] or Integer(E.order()) != Integer(recorded["order"]):
            raise ValueError("public instance mismatch")
        relations = recorded["relation_rows"]
        for relation in relations:
            verify_relation(E, Fpoly, R, X, fb_points, Q, relation)
            verified_rows += 1
        rank, recovered, scalar = verify_matrix(
            E, recorded["order"], fb_points, Q, relations, recorded
        )
        cells.append(
            {
                "p": int(recorded["p"]),
                "relations": len(relations),
                "rank": rank,
                "target_recovered": recovered,
                "recovered_scalar": scalar,
            }
        )

    result = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input": os.path.abspath(input_path),
        "input_source_sha256": artifact["source_sha256"],
        "status": "VERIFIED",
        "public_rows_verified": int(verified_rows),
        "cells": cells,
    }
    out_path = parse_arg("--out")
    if out_path:
        with open(out_path, "w") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))


main()
