#!/usr/bin/env python3
"""Independent bounded replay of frozen FROB C2 and C3 first-curve controls.

C2 has archived residue lists and can be rechecked exactly. C3 lacks archived
sample identities: this checks its cardinality/ratio identities against a
fresh valid seeded draw, but cannot bind that draw to the historical run.
The script imports the prior audit helpers and the archived checker's field and
curve primitives; it never imports the Sage experiment driver.
"""

import argparse
from copy import deepcopy
import hashlib
import itertools
import json
from math import isqrt, prod
from pathlib import Path
import random
import sys
import time

import recheck_core as core


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "c2-c3-control-replay.json"


def first_nonstable_standard(field, dim):
    n = field.n
    basis = [[int(i == j) for i in range(n)] for j in range(n)]
    for combo in itertools.combinations(range(n), dim):
        outside = [i for i in range(n) if i not in combo]
        for j in combo:
            if any(field.frobenius(basis[j])[i] for i in outside):
                return list(combo), tuple(basis[j])
    return None, None


def verify_c2_membership(record, residues):
    assert record["size_B_W"] == len(residues)
    assert record["_ks"] == residues


def validate_partition(part, bases, points, ec, order):
    assert part["status"] == "ok"
    assert part["block_sizes"] == [len(base) for base in bases]
    assert all(len(base) == len(set(base)) for base in bases)
    assert all(all((-k) % order in set(base) for k in base) for base in bases)
    targets = set()
    count = 0
    for tup in itertools.product(*bases):
        index = sum(tup) % order
        point_sum = None
        for k in tup:
            point_sum = ec.add(point_sum, points[k])
        assert point_sum == points[index]
        if index:
            targets.add(index)
        count += 1
    union_size = len(set().union(*(set(base) for base in bases)))
    assert part["prod_tuple_count"] == count == prod(len(base) for base in bases)
    assert part["distinct_targets"] == len(targets)
    assert part["B_union_size"] == union_size
    assert part["U_neg"] == [union_size, 2]
    assert part["p_m"] == [len(targets), order - 1]
    for extra in (0, 8, 32):
        assert part["cost_ratio_neg"][str(extra)] == {
            "denominator_zero": False,
            "value": core.ratio(union_size, len(targets), order, extra),
        }
    return count


def generated_c3_bases(seed, partition, sizes, order):
    """A valid frozen-seed construction; sample identities were not archived."""
    derived_seed = int(seed) + hash(tuple(tuple(b) for b in partition)) % 100000
    rng = random.Random(derived_seed)
    pairs = list(range(1, (order - 1) // 2 + 1))
    result = []
    for size in sizes:
        assert size % 2 == 0
        chosen = rng.sample(pairs, size // 2)
        result.append([k for r in chosen for k in (r, order - r)])
    return result


def replay_cell(cell_name, raw, q, factors, split, checker):
    assert raw["cell_status"] == "completed"
    first = raw["curves"][0]
    order = first["N"]
    curve = first["curve"]
    field = checker.FQN(q, 5, checker.find_first_irreducible(q, 5))
    cinv, dims = core.coordinates(field, factors, split)
    ec = checker.EC(field, [curve["A"]] + [0] * 4, [curve["B"]] + [0] * 4)
    encoded = curve["G_enc"]
    generator = (split.decode(encoded[0], q, 5), split.decode(encoded[1], q, 5))
    assert ec.on_curve(generator) and order > 1
    assert all(order % d for d in range(2, isqrt(order) + 1))
    assert ec.scalar_mul(order, generator) is None
    mu = curve["mu"]
    assert pow(mu, 5, order) == 1 and all(pow(mu, j, order) != 1 for j in range(1, 5))
    assert (field.frobenius(generator[0]), field.frobenius(generator[1])) == ec.scalar_mul(mu, generator)

    points = [None] * order
    point = generator
    for k in range(1, order):
        points[k] = point
        point = ec.add(point, generator)
    assert point is None

    c2_sets = {}
    for dim_s, record in first["C2_raw"].items():
        dim = int(dim_s)
        assert record["found"] is True
        combo, witness = first_nonstable_standard(field, dim)
        assert combo == record["basis_indices"]
        assert str(witness) == record["witness_not_stable"]
        outside = [i for i in range(5) if i not in combo]
        residues = [k for k in range(1, order)
                    if all(points[k][0][i] == 0 for i in outside)]
        verify_c2_membership(record, residues)
        c2_sets[dim] = residues

    object_parts = {str(p["partition_blocks"]): p for p in first["object_arm_partitions"]}
    c2_ok = 0
    c2_tuple_checks = 0
    for part in first["C2_arm_partitions"]:
        obj = object_parts[str(part["partition_blocks"])]
        if part["status"] != "ok":
            assert part["status"] == obj["status"] == "empty_base"
            continue
        assert obj["status"] == "ok"
        bases = [c2_sets[dim] for dim in part["slot_dims"]]
        c2_tuple_checks += validate_partition(part, bases, points, ec, order)
        assert part["U_frob"] is None and part["U_frob_reason"] == "slot set not pi-stable"
        c2_ok += 1

    c3_ok = 0
    c3_generated_tuples = 0
    for seed, parts in sorted(first["C3_arm_by_seed"].items()):
        for part in parts:
            obj = object_parts[str(part["partition_blocks"])]
            if part["status"] != "ok":
                assert part["status"] == obj["status"] == "empty_base"
                continue
            assert obj["status"] == "ok"
            # All historically populated C3 partitions are singleton slots.
            # Their aggregates depend on cardinality, not the sampled residues.
            assert len(part["partition_blocks"]) == 1
            bases = generated_c3_bases(seed, part["partition_blocks"], obj["block_sizes"], order)
            c3_generated_tuples += validate_partition(part, bases, points, ec, order)
            c3_ok += 1

    # Mutation controls distinguish exact C2 membership from aggregate-only C3.
    dim = min(c2_sets)
    bad = deepcopy(first["C2_raw"][str(dim)])
    bad["_ks"][0] = 0
    try:
        verify_c2_membership(bad, c2_sets[dim])
    except AssertionError:
        c2_mutant_rejected = True
    else:
        c2_mutant_rejected = False
    assert c2_mutant_rejected
    return {
        "cell": cell_name, "q": q, "N": order,
        "points_classified": order - 1,
        "C2_exact_membership_sizes": {str(d): len(v) for d, v in sorted(c2_sets.items())},
        "C2_ok_partitions": c2_ok, "C2_archived_tuple_identities": c2_tuple_checks,
        "C3_aggregate_partitions": c3_ok,
        "C3_generated_sample_tuples": c3_generated_tuples,
        "C2_mutated_residue_rejected": c2_mutant_rejected,
    }


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
    cells = []
    for name, (q, factors, _modulus, _factor_strings) in core.CONFIG.items():
        cells.append(replay_cell(name, raw_by_cell[name], q, factors, split, checker))
    totals = {
        "points_classified": sum(c["points_classified"] for c in cells),
        "C2_ok_partitions": sum(c["C2_ok_partitions"] for c in cells),
        "C2_archived_tuple_identities": sum(c["C2_archived_tuple_identities"] for c in cells),
        "C3_aggregate_partitions": sum(c["C3_aggregate_partitions"] for c in cells),
        "C3_generated_sample_tuples": sum(c["C3_generated_sample_tuples"] for c in cells),
    }
    assert totals == {
        "points_classified": 238350, "C2_ok_partitions": 3,
        "C2_archived_tuple_identities": 13242,
        "C3_aggregate_partitions": 6,
        "C3_generated_sample_tuples": 26620,
    }
    result = {
        "schema": "frob-c8-c2-c3-first-curve-replay/v1",
        "source_run": "RUN-FROB-91ee9c-7119f2",
        "checker_sha256": hashlib.sha256((core.RUN / "checker.py").read_bytes()).hexdigest(),
        "raw_jsonl_sha256": hashlib.sha256((core.RUN / "raw.jsonl").read_bytes()).hexdigest(),
        "cells": cells, "totals": totals,
        "limit": "C2 archived lists checked exactly; C3 sampled lists absent, so generated samples do not bind the historical samples; C4 and original source custody remain open",
    }
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        print(f"wrote {OUTPUT.relative_to(core.ROOT)}")
    elif OUTPUT.read_text() != serialized:
        print("c2-c3-control-replay.json is stale", file=sys.stderr)
        return 1
    else:
        print("FROB C2 exact and C3 aggregate replay is byte-exact and current")
    print(f"elapsed_seconds={time.time() - started:.3f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
