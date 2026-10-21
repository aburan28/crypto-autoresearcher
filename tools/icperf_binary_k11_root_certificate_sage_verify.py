"""Independently replay the k11 synthetic full-point extraction controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing
from sage.version import version as sage_version


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    controls = json.loads(args.controls.read_bytes())
    root = Path(__file__).resolve().parents[1]
    chain_path = root / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
    chain = json.loads(chain_path.read_bytes())
    assert controls["chain_sha256"] == sha(chain_path)
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

    b = elem(chain["curve"]["b_polynomial_bits"])
    curve = EllipticCurve(field, [1, 0, 0, 0, b])
    gamma = elem(chain["gamma"])
    r = Integer(chain["curve"]["prime_order"])
    assert gamma**4 == b and r.is_prime(proof=True)

    def phi(point):
        return gamma / (point[0] + gamma)

    def phi3(a, c, d):
        return (a*a + a)*(c*c + c)*(d*d + d) + gamma*(a + c + d)**2

    def point(row):
        return curve(elem(row[0]), elem(row[1]))

    paths = {
        "weighted": root / "research/icperf_binary_torsion_k11_weighted_20261017/base.json",
        "local_random": root / "research/icperf_binary_torsion_k11_local_control_20261017/base.json",
    }
    checked = []
    for entry in controls["bases"]:
        label = entry["base_kind"]
        assert label in paths and entry["base_sha256"] == sha(paths[label])
        base = json.loads(paths[label].read_bytes())
        scan = next(row for row in base["candidate_scans"] if row["offset"] == 4096)
        assert entry["input_representatives"] == scan["selected_representatives"][:8]
        points = [point(row[1:]) for row in entry["input_representatives"]]
        ts = [elem(row[0]) for row in entry["input_representatives"]]
        assert all(phi(p) == t for p, t in zip(points, ts))
        partial = []
        total = curve(0)
        for p in points:
            total += p
            assert total != curve(0) and total[0] != gamma
            partial.append(total)
        us = [elem(value) for value in entry["intermediate_phi"]]
        assert us == [phi(p) for p in partial[1:7]]
        assert point(entry["synthetic_raw_target"]) == total
        assert [bits(c) for c in (4*total)[:2]] == entry["synthetic_projected_target"]
        assert r*(4*total) == curve(0)
        assert bits(phi(total)) == entry["synthetic_target_phi"]
        triples = [[ts[0], ts[1], us[0]]]
        triples += [[us[i-1], ts[i+1], us[i]] for i in range(1, 6)]
        triples += [[us[-1], ts[-1], phi(total)]]
        assert len(triples) == 7 and all(phi3(*row) == 0 for row in triples)
        flipped = list(ts)
        flipped[0] += elem(1)
        assert phi3(flipped[0], ts[1], us[0]) != 0
        sign_masks = []
        for mask in range(256):
            summed = curve(0)
            for i, p in enumerate(points):
                summed += -p if mask & (1 << i) else p
            if summed == total:
                sign_masks.append(mask)
        assert sign_masks == [0]
        assert all(row["certified"] and row["sign_certificates"] == 1 and
                   row["unique_projected_rows"] == 1 and not row["bit_flip_certified"]
                   for row in entry["channels"])
        checked.append({"base_kind": label, "seven_equations_checked": 7,
                        "full_point_signs_checked": 256,
                        "accepted_sign_masks": sign_masks, "channels_checked": 4})
    output = {"schema": "icperf-binary-k11-root-certificate-sage-replay-v1",
              "scope": "independent synthetic known-point and group replay; no archived-target solver result",
              "source_sha256": sha(Path(__file__)), "controls_sha256": sha(args.controls),
              "chain_sha256": sha(chain_path), "sage_version": sage_version,
              "python_version": sys.version, "bases": checked}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"bases": len(checked), "sign_masks_per_base": 256}, sort_keys=True))


if __name__ == "__main__":
    main()
