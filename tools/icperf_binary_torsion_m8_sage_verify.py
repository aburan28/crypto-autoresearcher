"""Independent Sage replay of the planted eight-summand torsion chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing
from sage.version import version as sage_version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chain", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    chain_bytes, base_bytes, fixture_bytes = (path.read_bytes() for path in
                                            (args.chain, args.base, args.fixture))
    rec, base, fixture = (json.loads(blob) for blob in
                          (chain_bytes, base_bytes, fixture_bytes))
    assert rec["base_sha256"] == hashlib.sha256(base_bytes).hexdigest()
    assert rec["fixture_sha256"] == hashlib.sha256(fixture_bytes).hexdigest()
    assert rec["coordinate_source_sha256"] == base["source_sha256"]
    ring = PolynomialRing(GF(2), "t")
    t = ring.gen()
    modulus = t**61 + t**5 + t**2 + t + 1
    assert modulus.is_irreducible()
    field = GF(2**61, name="z", modulus=modulus)
    z = field.gen()

    def elem(bits):
        return sum((z**i for i in range(61) if (int(bits) >> i) & 1), field.zero())

    def bits(value):
        return sum(int(c) << i for i, c in enumerate(value.polynomial().list()))

    b = elem(fixture["b_polynomial_bits"])
    curve = EllipticCurve(field, [1, 0, 0, 0, b])
    r = Integer(fixture["prime_order"])
    gamma = b**(2**59)
    assert r.is_prime(proof=True) and gamma**4 == b
    assert bits(gamma) == rec["gamma"]

    def point(coords):
        return curve(0) if coords is None else curve(elem(coords[0]), elem(coords[1]))

    def phi(point_value):
        assert point_value != curve(0) and point_value[0] != gamma
        return gamma / (point_value[0] + gamma)

    def pphi3(values):
        return ((values[0]**2+values[0]) * (values[1]**2+values[1]) *
                (values[2]**2+values[2]) + gamma*(values[0]+values[1]+values[2])**2)

    reps = rec["base_representatives"]
    selected = next(row for row in base["candidate_scans"]
                    if row["offset"] == base["selected_offset"])
    assert reps == selected["selected_representatives"][:8]
    points = [point(coords) for coords in rec["raw_points"]]
    assert len(points) == 8 and all(p != curve(0) for p in points)
    assert [bits(phi(p)) for p in points] == [row[0] for row in reps]
    assert [list(coords) for coords in rec["raw_points"]] == [row[1:] for row in reps]

    partials = []
    total = curve(0)
    for p in points:
        total += p
        partials.append(total)
    raw_sum = point(rec["raw_sum"])
    subgroup_target = point(rec["subgroup_target"])
    assert total == raw_sum and 4*raw_sum == subgroup_target
    assert r*subgroup_target == curve(0)
    assert partials[1:7] == [point(coords) for coords in rec["intermediate_points"]]
    us = [phi(p) for p in partials[1:7]]
    assert [bits(value) for value in us] == rec["intermediate_phi"]

    t4 = r*point(fixture["source_point"])
    assert t4 == point(rec["torsion_order_four"])
    assert 2*t4 != curve(0) and 4*t4 == curve(0)
    inv4 = Integer(rec["inverse_cofactor_mod_r"])
    assert (4*inv4) % r == 1
    root = inv4*subgroup_target
    channels = [root+j*t4 for j in range(4)]
    assert channels == [point(coords) for coords in rec["target_channels"]]
    assert len(set(channels)) == 4
    assert all(4*channel == subgroup_target and channel != curve(0) and
               channel[0] != gamma for channel in channels)
    assert channels.count(raw_sum) == 1
    selected_channel = channels.index(raw_sum)
    assert selected_channel == rec["selected_channel"]
    channel_ts = [phi(p) for p in channels]
    assert [bits(value) for value in channel_ts] == rec["target_channel_phi"]

    ts = [phi(p) for p in points]
    triples = [[ts[0], ts[1], us[0]]]
    for i in range(1, 6):
        triples.append([us[i-1], ts[i+1], us[i]])
    triples.append([us[-1], ts[-1], channel_ts[selected_channel]])
    assert len(triples) == 7
    assert [[bits(value) for value in triple] for triple in triples] == rec["chain_triples_phi"]
    assert all(pphi3(triple) == 0 for triple in triples)
    final_values = [pphi3([us[-1], ts[-1], value]) for value in channel_ts]
    assert [bits(value) for value in final_values] == rec["final_channel_values"]
    assert final_values[selected_channel] == 0

    t2 = curve(field.zero(), gamma**2)
    assert t2 == 2*t4 and 2*t2 == curve(0)
    masks = rec["torsion_duplicate_orbit"]["even_masks"]
    assert masks == [mask for mask in range(256) if mask.bit_count() % 2 == 0]
    transformed_ts = set()
    coefficient_rows = set()
    for mask in masks:
        transformed = [p+t2 if (mask >> i) & 1 else p for i, p in enumerate(points)]
        assert all(q != curve(0) and q[0] != gamma for q in transformed)
        assert sum(transformed, curve(0)) == raw_sum
        tuple_bits = tuple(bits(phi(p)) for p in transformed)
        assert tuple_bits == tuple(reps[i][0] ^ ((mask >> i) & 1) for i in range(8))
        transformed_ts.add(tuple_bits)
        coefficient_rows.add(tuple(sorted((bits((4*p)[0]), bits((4*p)[1]))
                                          for p in transformed)))
    assert len(transformed_ts) == 128 and len(coefficient_rows) == 1
    assert len({t for row in reps for t in (row[0], row[0]^1)}) == 16
    assert rec["torsion_duplicate_orbit"]["ordered_group_tuples_from_permutations_and_even_shifts"] == 128*math.factorial(8)
    shape = rec["chain_shape"]
    assert shape["summands"] == 8 and shape["three_point_equations"] == 7
    assert shape["full_field_intermediates"] == 6 and shape["base_bits_each"] == 10
    assert shape["boolean_variables_per_channel_before_lift"] == 446
    assert shape["boolean_equations_per_channel_before_lift"] == 427
    assert shape["target_channels"] == 4

    result = {"schema": "icperf-binary-torsion-m8-sage-replay-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "chain_sha256": hashlib.sha256(chain_bytes).hexdigest(),
              "base_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "sage_version": sage_version, "python_version": sys.version,
              "selected_channel": selected_channel,
              "zero_chained_equations": len(triples),
              "even_torsion_masks_replayed": len(masks),
              "unique_projected_coefficient_rows": len(coefficient_rows),
              "scope": "independent planted chain and duplicate-row replay; no unknown-target solve"}
    with args.out.open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "equations": len(triples),
                      "torsion_masks": len(masks)}, sort_keys=True))


if __name__ == "__main__":
    main()
