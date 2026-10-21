"""Independent Sage group replay of the new k11 public target schedule."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing
from sage.version import version as sage_version

ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "experiments/EXP-ICPERF-018b0c/inputs/target_manifest.json"
FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
DOMAIN = b"ICPERF-k11-natural-v1\0"


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    target_blob, fixture_blob = TARGET.read_bytes(), FIXTURE.read_bytes()
    target, fixture = json.loads(target_blob), json.loads(fixture_blob)
    fixture_sha = sha(fixture_blob)
    assert target["fixture_sha256"] == fixture_sha
    assert bytes.fromhex(target["domain_hex"]) == DOMAIN
    ring = PolynomialRing(GF(2), "t")
    t = ring.gen()
    modulus = t**61 + t**5 + t**2 + t + 1
    assert modulus.is_irreducible()
    field = GF(2**61, name="z", modulus=modulus)
    z = field.gen()

    def elem(value):
        return sum((z**i for i in range(61) if (int(value) >> i) & 1), field.zero())

    def bits(value):
        return sum(int(c) << i for i, c in enumerate(value.polynomial().list()))

    curve = EllipticCurve(field, [1, 0, 0, 0, elem(fixture["b_polynomial_bits"])])
    r = Integer(fixture["prime_order"])
    assert r.is_prime(proof=True) and fixture["cofactor"] == 4
    assert Integer(fixture["field_polynomial"]) == (1 << 61) | (1 << 5) | (1 << 2) | (1 << 1) | 1

    def point(coords):
        return curve(0) if coords is None else curve(elem(coords[0]), elem(coords[1]))

    gamma = elem(fixture["b_polynomial_bits"])**(2**59)
    assert gamma**4 == elem(fixture["b_polynomial_bits"])
    assert bits(gamma) == target["gamma"]
    generator = point(fixture["generator"])
    torsion = r * point(fixture["source_point"])
    assert r * generator == curve(0) and generator != curve(0)
    assert torsion != curve(0) and 4 * torsion == curve(0)
    assert point(target["torsion_order_four"]) == torsion
    inverse4 = Integer(target["inverse_cofactor_mod_r"])
    assert (4 * inverse4) % r == 1
    admitted = []
    seen = set()
    for counter, row in enumerate(target["candidates"]):
        assert row["counter"] == counter
        digest = hashlib.sha256(DOMAIN + bytes.fromhex(fixture_sha)
                                + counter.to_bytes(4, "big")).digest()
        scalar = Integer(1 + int.from_bytes(digest, "big") % (int(r) - 1))
        subgroup = scalar * generator
        assert row["scalar"] == int(scalar)
        assert subgroup == point(row["subgroup_point"])
        if subgroup in seen:
            assert row["rejection"] == "duplicate_subgroup_point"
            continue
        root = inverse4 * subgroup
        channels = [root + c * torsion for c in range(4)]
        if curve(0) in channels:
            assert row["rejection"] == "non_affine_raw_channel"
        elif any(p[0] in (field.zero(), gamma) for p in channels):
            assert row["rejection"] == "zero_or_pole_raw_x"
        else:
            assert row["target_index"] == len(admitted)
            assert [point(coords) for coords in row["raw_channels"]] == channels
            assert [bits(gamma / (p[0] + gamma)) for p in channels] == row["channel_phi"]
            assert all(4 * p == subgroup for p in channels)
            admitted.append(row)
            seen.add(subgroup)
        if len(admitted) == 8:
            assert counter == len(target["candidates"]) - 1
            break
    assert len(admitted) == 8 and admitted == target["admitted"]
    result = {"schema": "icperf-k11-target-sage-replay-v1",
              "scope": "independent finite-field and point replay; no solver trial",
              "source_sha256": sha(Path(__file__).read_bytes()),
              "target_manifest_sha256": sha(target_blob),
              "fixture_sha256": fixture_sha,
              "sage_version": sage_version, "python_version": sys.version,
              "prime_order_proved": True, "field_irreducible": True,
              "targets_checked": len(admitted), "raw_channels_checked": 4 * len(admitted),
              "first_eight_admissible_and_distinct": True}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"targets_checked": len(admitted),
                      "raw_channels_checked": 4 * len(admitted)}, sort_keys=True))


if __name__ == "__main__":
    main()
