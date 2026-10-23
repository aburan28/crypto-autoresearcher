#!/usr/bin/env python3
"""Bounded independent geometry and aggregate recheck of frozen FROB C4.

Exact curve orders are certified from point orders and the Hasse interval.
Generated seeded null-arm samples are valid but cannot be bound to the
historical samples, whose residue lists were not retained. This imports the
archived checker's field/curve primitives and prior audit helpers, never the
Sage driver.
"""

import argparse
import hashlib
import itertools
import json
from math import isqrt, lcm
from pathlib import Path
import random
import re
import sys
import time

import recheck_core as core
from recheck_c2_c3 import validate_partition


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "c4-null-geometry-replay.json"


def prime_factorization(value):
    n = value
    factors = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def parse_sage_field(text, q):
    values = [0] * 5
    for raw_term in text.replace(" ", "").split("+"):
        match = re.fullmatch(r"(?:(\d+)\*)?z(?:\^(\d+))?", raw_term)
        if match:
            coefficient = int(match.group(1) or 1)
            exponent = int(match.group(2) or 1)
        else:
            assert raw_term.isdecimal(), raw_term
            coefficient, exponent = int(raw_term), 0
        assert 0 <= exponent < 5
        values[exponent] = (values[exponent] + coefficient) % q
    return values


def candidate_curve(field, a, b, checker):
    A = [a, 1, 0, 0, 0]
    B = [b, 1, 0, 0, 0]
    ec = checker.EC(field, A, B)
    A3 = field.power(A, 3)
    B2 = field.mul(B, B)
    denominator = field.add(field.scal(4, A3), field.scal(27, B2))
    assert not field.is_zero(denominator)
    j = field.mul(field.scal(1728 * 4, A3), field.inv(denominator))
    assert field.frobenius(j) != j  # degree five: the only proper subfield is F_q
    return ec, j


def first_points(ec, field, max_x_index=100):
    for x_index, vector in enumerate(itertools.product(range(field.q), repeat=5)):
        if x_index > max_x_index:
            break
        x = list(vector)
        rhs = field.add(field.add(field.power(x, 3), field.mul(ec.A, x)), ec.B)
        y = field.sqrt(rhs)
        if y is not None:
            point = (x, y)
            assert ec.on_curve(point)
            yield x_index, point


def exact_point_order(ec, point, candidate_order, factors):
    assert ec.scalar_mul(candidate_order, point) is None
    order = candidate_order
    for p in factors:
        while order % p == 0 and ec.scalar_mul(order // p, point) is None:
            order //= p
    assert ec.scalar_mul(order, point) is None
    assert all(ec.scalar_mul(order // p, point) is not None
               for p in factors if order % p == 0)
    return order


def certify_curve_order(ec, field, claimed_order):
    q_size = field.q ** 5
    hasse_radius = isqrt(4 * q_size)
    low = q_size + 1 - hasse_radius
    high = q_size + 1 + hasse_radius
    factors = prime_factorization(claimed_order)
    accumulated = 1
    witnesses = []
    for x_index, point in first_points(ec, field):
        order = exact_point_order(ec, point, claimed_order, factors)
        accumulated = lcm(accumulated, order)
        witnesses.append({"x_index": x_index, "point_order": order})
        possible = [k * accumulated for k in range((low + accumulated - 1) // accumulated,
                                                      high // accumulated + 1)]
        if possible == [claimed_order]:
            return {"order": claimed_order, "Hasse_interval": [low, high],
                    "point_order_lcm": accumulated, "possible_multiples": possible,
                    "witnesses": witnesses, "factorization": {str(p): e for p, e in factors.items()}}
    raise AssertionError("first 101 x coordinates did not yield a unique Hasse multiple")


def find_prime_generator(ec, field, prime_order, cofactor):
    assert prime_factorization(prime_order) == {prime_order: 1}
    for x_index, point in first_points(ec, field):
        generator = ec.scalar_mul(cofactor, point)
        if generator is not None and ec.scalar_mul(prime_order, generator) is None:
            assert ec.on_curve(generator)
            return x_index, generator
    raise AssertionError("first 101 x coordinates did not yield a prime-order witness")


def generated_c4_bases(seed, partition, sizes, order):
    pairs = list(range(1, (order - 1) // 2 + 1))
    derived = int(seed) + 7919 * len(pairs) + hash(tuple(tuple(b) for b in partition)) % 100000
    rng = random.Random(derived)
    used = set()
    result = []
    for size in sizes:
        assert size % 2 == 0
        available = [k for k in pairs if k not in used]
        chosen = rng.sample(available, size // 2)
        used.update(chosen)
        result.append([k for r in chosen for k in (r, order - r)])
    return result


def replay_cell(cell_name, raw, q, checker):
    assert raw["cell_status"] == "completed"
    field = checker.FQN(q, 5, checker.find_first_irreducible(q, 5))
    object_curve = raw["curves"][0]
    object_order = object_curve["N"]
    null = raw["C4"]
    assert null["status"] == "ok"
    assert null["N"] > 1 and null["cofactor"] > 0
    assert object_order // 2 <= null["N"] <= 2 * object_order

    rejected = raw["C4_rejected"]
    examined = []
    preceding = [(a, b) for a in range(q) for b in range(q)
                 if (a, b) < (null["a"], null["b"])]
    assert len(preceding) == len(rejected)
    for (a, b), record in zip(preceding, rejected):
        assert record["a"] == a and record["b"] == b
        assert record["reason"] == "no_matching_N"
        ec, _j = candidate_curve(field, a, b, checker)
        proof = certify_curve_order(ec, field, record["order"])
        eligible = [p for p, exponent in prime_factorization(record["order"]).items()
                    if exponent == 1 and object_order // 2 <= p <= 2 * object_order]
        assert eligible == []
        examined.append({"a": a, "b": b, "reason": record["reason"], "order_certificate": proof})

    ec, j = candidate_curve(field, null["a"], null["b"], checker)
    assert null["A"] == ("z" if null["a"] == 0 else f"z + {null['a']}")
    assert null["B"] == ("z" if null["b"] == 0 else f"z + {null['b']}")
    assert j == parse_sage_field(null["j_invariant"], q)
    claimed_order = null["N"] * null["cofactor"]
    order_proof = certify_curve_order(ec, field, claimed_order)
    try:
        certify_curve_order(ec, field, claimed_order + 1)
    except AssertionError:
        wrong_order_rejected = True
    else:
        wrong_order_rejected = False
    assert wrong_order_rejected
    eligible = [p for p, exponent in prime_factorization(claimed_order).items()
                if exponent == 1 and object_order // 2 <= p <= 2 * object_order]
    assert null["N"] == max(eligible)
    x_index, generator = find_prime_generator(ec, field, null["N"], null["cofactor"])

    points = [None] * null["N"]
    point = generator
    for k in range(1, null["N"]):
        points[k] = point
        point = ec.add(point, generator)
    assert point is None

    object_parts = {str(p["partition_blocks"]): p for p in object_curve["object_arm_partitions"]}
    aggregate_rows = 0
    generated_tuples = 0
    for seed, parts in sorted(null["partitions_by_seed"].items()):
        for part in parts:
            obj = object_parts[str(part["partition_blocks"])]
            if part["status"] != "ok":
                assert part["status"] == obj["status"] == "empty_base"
                continue
            assert obj["status"] == "ok"
            assert len(part["partition_blocks"]) == 1
            bases = generated_c4_bases(seed, part["partition_blocks"], obj["block_sizes"], null["N"])
            generated_tuples += validate_partition(part, bases, points, ec, null["N"])
            aggregate_rows += 1
    assert aggregate_rows == 2
    return {"cell": cell_name, "q": q, "accepted_curve": {"a": null["a"], "b": null["b"],
            "N": null["N"], "cofactor": null["cofactor"], "j_coefficients": j,
            "order_certificate": order_proof, "generator_x_index": x_index,
            "wrong_order_rejected": wrong_order_rejected},
            "rejected_candidates": examined, "null_subgroup_points_enumerated": null["N"] - 1,
            "aggregate_rows": aggregate_rows, "generated_sample_tuples": generated_tuples}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    started = time.time()
    split = core.load_split()
    checker = split.load_checker()
    raw_by_cell = {record["cell"]: record["data"] for record in
                   (json.loads(line) for line in (core.RUN / "raw.jsonl").read_text().splitlines())}
    cells = [replay_cell(name, raw_by_cell[name], q, checker)
             for name, (q, _factors, _modulus, _factor_strings) in core.CONFIG.items()]
    totals = {"accepted_null_curves": len(cells),
              "rejected_candidates_order_certified": sum(len(c["rejected_candidates"]) for c in cells),
              "wrong_order_mutants_rejected": sum(c["accepted_curve"]["wrong_order_rejected"] for c in cells),
              "null_subgroup_points_enumerated": sum(c["null_subgroup_points_enumerated"] for c in cells),
              "aggregate_rows": sum(c["aggregate_rows"] for c in cells),
              "generated_sample_tuples": sum(c["generated_sample_tuples"] for c in cells)}
    assert totals == {"accepted_null_curves": 3, "rejected_candidates_order_certified": 2,
                      "wrong_order_mutants_rejected": 3,
                      "null_subgroup_points_enumerated": 143568, "aggregate_rows": 6,
                      "generated_sample_tuples": 26620}
    result = {"schema": "frob-c8-c4-null-geometry-replay/v1",
              "source_run": "RUN-FROB-91ee9c-7119f2",
              "checker_sha256": hashlib.sha256((core.RUN / "checker.py").read_bytes()).hexdigest(),
              "raw_jsonl_sha256": hashlib.sha256((core.RUN / "raw.jsonl").read_bytes()).hexdigest(),
              "cells": cells, "totals": totals,
              "limit": "Exact curve orders use the Hasse bound and verified point orders; C4 sampled residue lists were not retained, so generated samples do not bind historical tuple identities; original execution source custody remains open"}
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        print(f"wrote {OUTPUT.relative_to(core.ROOT)}")
    elif OUTPUT.read_text() != serialized:
        print("c4-null-geometry-replay.json is stale", file=sys.stderr)
        return 1
    else:
        print("FROB C4 null geometry replay is byte-exact and current")
    print(f"elapsed_seconds={time.time() - started:.3f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
