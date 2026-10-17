"""Independent Sage replay of a cofactor-projected affine binary base."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing
from sage.version import version as sage_version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_bytes, fixture_bytes = args.base.read_bytes(), args.fixture.read_bytes()
    rec, fixture = json.loads(base_bytes), json.loads(fixture_bytes)
    assert rec["fixture_sha256"] == hashlib.sha256(fixture_bytes).hexdigest()
    n = rec["curve"]["field_degree"]
    ring = PolynomialRing(GF(2), "t")
    t = ring.gen()
    polynomial = t**61 + t**5 + t**2 + t + 1
    assert polynomial.is_irreducible()
    field = GF(2**n, name="z", modulus=polynomial)
    z = field.gen()

    def field_element(bits: int):
        return sum((z**i for i in range(n) if (int(bits) >> i) & 1), field.zero())

    curve = EllipticCurve(field, [1, 0, 0, 0, field_element(rec["curve"]["b_polynomial_bits"])])
    r = Integer(rec["curve"]["prime_order"])
    assert r.is_prime(proof=True)

    def point(coords):
        if coords is None:
            return curve(0)
        return curve(field_element(coords[0]), field_element(coords[1]))

    coeffs = [field_element(c) for c in rec["linearized_membership_coefficients"]]
    k = rec["predeclared_selection"]["subspace_dimension"]
    assert k == 9 and len(coeffs) == k + 1 and coeffs[-1] == 1

    def linearized(value):
        result = field.zero()
        power = value
        for c in coeffs:
            result += c * power
            power = power**2
        return result

    for v in range(1 << k):
        assert linearized(field_element(v)) == 0

    scans = []
    for scan in rec["candidate_scans"]:
        offset = scan["offset"]
        constant = linearized(field_element(offset))
        assert constant != 0 and constant == field_element(scan["affine_membership_constant"])
        accepted_x = []
        for v in range(1 << k):
            x_bits = offset ^ v
            assert linearized(field_element(x_bits)) == constant
            try:
                curve.lift_x(field_element(x_bits))
            except ValueError:
                continue
            accepted_x.append(x_bits)
        assert accepted_x == [coords[0] for coords in scan["raw_points"]]
        assert len(accepted_x) == scan["realized_size"]
        for coords in scan["raw_points"]:
            point(coords)
        scans.append({"offset": offset, "accepted": len(accepted_x),
                      "raw_x_list_equal": True})

    target_size = rec["predeclared_selection"]["target_size"]
    winner = min(rec["candidate_scans"],
                 key=lambda row: (abs(row["realized_size"] - target_size), row["offset"]))
    assert winner["offset"] == rec["selected_offset"]
    projected = rec["selected_projected_points"]
    assert len(projected) == winner["realized_size"]
    for raw, coords in zip(winner["raw_points"], projected):
        image = point(coords)
        assert 4 * point(raw) == image and r * image == curve(0) and image != curve(0)
    assert len({coords[0] for coords in projected}) == len(projected)

    control = rec["random_control"]
    seed = control["seed"]
    domain = control["domain"].encode()
    counts = {"zero": 0, "duplicate": 0, "nonliftable": 0, "accepted": 0}
    seen = set()
    accepted_x = []
    for counter in range(control["draws"]):
        digest = hashlib.sha256(domain + seed.to_bytes(8, "big") +
                                counter.to_bytes(8, "big")).digest()
        x_bits = int.from_bytes(digest[:8], "big") & ((1 << n) - 1)
        if x_bits == 0:
            counts["zero"] += 1
        elif x_bits in seen:
            counts["duplicate"] += 1
        else:
            seen.add(x_bits)
            try:
                curve.lift_x(field_element(x_bits))
            except ValueError:
                counts["nonliftable"] += 1
            else:
                counts["accepted"] += 1
                accepted_x.append(x_bits)
    assert counts == control["counts"]
    assert accepted_x == [coords[0] for coords in control["raw_points"]]
    assert len(accepted_x) == winner["realized_size"]
    for raw, coords in zip(control["raw_points"], control["projected_points"]):
        image = point(coords)
        assert 4 * point(raw) == image and r * image == curve(0) and image != curve(0)
    assert len({coords[0] for coords in control["projected_points"]}) == len(accepted_x)

    torsion = rec["torsion"]
    torsion_points = [point(coords) for coords in torsion["points"]]
    assert len(set(torsion_points)) == 4
    assert torsion_points[1] == r * point(fixture["source_point"])
    assert [j * torsion_points[1] for j in range(4)] == torsion_points
    assert 4 * torsion_points[1] == curve(0)
    inv4 = Integer(torsion["inverse_cofactor_mod_r"])
    assert (4 * inv4) % r == 1
    channels = rec["channel_controls"]
    generator = point(fixture["generator"])
    q_public = Integer(channels["known_scalar"]) * generator
    target = Integer(channels["a"]) * generator + Integer(channels["b"]) * q_public
    assert q_public == point(channels["public_q"]) and target == point(channels["target"])
    root = inv4 * target
    assert root == point(channels["root"])
    assert [root + t for t in torsion_points] == [point(coords) for coords in channels["channels"]]
    assert len(set(point(coords) for coords in channels["channels"])) == 4
    assert all(4 * point(coords) == target for coords in channels["channels"])
    planted_raw = sum((point(coords) for coords in winner["raw_points"][:3]), curve(0))
    planted_projected = sum((point(coords) for coords in projected[:3]), curve(0))
    assert planted_raw == point(channels["planted_raw_sum"])
    assert planted_projected == point(channels["planted_projected_sum"])
    assert 4 * planted_raw == planted_projected
    planted_root = inv4 * planted_projected
    planted_channels = [planted_root + t for t in torsion_points]
    assert planted_channels.count(planted_raw) == 1
    assert planted_channels.index(planted_raw) == channels["planted_channel_index"]

    result = {"schema": "icperf-binary-projected-sage-replay-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "base_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "python_version": sys.version, "sage_version": sage_version,
              "subspace_polynomial_exact_kernel": True,
              "candidate_scans": scans, "selected_offset": winner["offset"],
              "control_counts": counts, "control_x_list_equal": True,
              "projected_points_valid": True,
              "torsion_order_four": True, "all_four_target_channels_valid": True,
              "planted_relation_channel_valid": True,
              "scope": "independent input and group-channel replay; no ECDLP cost comparison"}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "verified_offsets": len(scans),
                      "selected_size": winner["realized_size"]}, sort_keys=True))


if __name__ == "__main__":
    main()
