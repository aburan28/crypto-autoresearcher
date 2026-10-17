"""Independent Sage replay of affine-subspace and random-control base inputs."""

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
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_bytes = args.base.read_bytes()
    rec = json.loads(base_bytes)
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
    coeffs = [field_element(c) for c in rec["linearized_membership_coefficients"]]
    k = rec["predeclared_selection"]["subspace_dimension"]
    assert k == 11 and len(coeffs) == k + 1 and coeffs[-1] == 1

    def linearized(value):
        result = field.zero()
        power = value
        for c in coeffs:
            result += c * power
            power = power**2
        return result

    for v in range(1 << k):
        assert linearized(field_element(v)) == 0

    def classify(x_bits: int):
        try:
            point = curve.lift_x(field_element(x_bits))
        except ValueError:
            return "nonliftable"
        return "accepted" if r * point == curve(0) else "outside_subgroup"

    scans = []
    for scan in rec["candidate_scans"]:
        offset = scan["offset"]
        constant = linearized(field_element(offset))
        assert constant != 0 and constant == field_element(scan["affine_membership_constant"])
        counts = {"nonliftable": 0, "outside_subgroup": 0, "accepted": 0}
        accepted_x = []
        for v in range(1 << k):
            x_bits = offset ^ v
            assert linearized(field_element(x_bits)) == constant
            status = classify(x_bits)
            counts[status] += 1
            if status == "accepted":
                accepted_x.append(x_bits)
        assert counts == scan["counts"]
        assert accepted_x == [point[0] for point in scan["points"]]
        scans.append({"offset": offset, "counts": counts, "point_x_list_equal": True})

    target_size = rec["predeclared_selection"]["target_size"]
    winner = min(rec["candidate_scans"],
                 key=lambda row: (abs(row["realized_size"] - target_size), row["offset"]))
    assert winner["offset"] == rec["selected_offset"]
    control = rec["random_control"]
    seed = control["seed"]
    domain = control["domain"].encode()
    counts = {"zero": 0, "duplicate": 0, "nonliftable": 0,
              "outside_subgroup": 0, "accepted": 0}
    seen = set()
    accepted_x = []
    for counter in range(control["draws"]):
        digest = hashlib.sha256(domain + seed.to_bytes(8, "big") +
                                counter.to_bytes(8, "big")).digest()
        x_bits = int.from_bytes(digest[:8], "big") & ((1 << n) - 1)
        if x_bits == 0:
            status = "zero"
        elif x_bits in seen:
            status = "duplicate"
        else:
            seen.add(x_bits)
            status = classify(x_bits)
        counts[status] += 1
        if status == "accepted":
            accepted_x.append(x_bits)
    assert counts == control["counts"]
    assert accepted_x == [point[0] for point in control["points"]]
    assert len(accepted_x) == winner["realized_size"]
    for arm in (*rec["candidate_scans"], control):
        for x_bits, y_bits in arm["points"]:
            point = curve(field_element(x_bits), field_element(y_bits))
            assert r * point == curve(0)
    result = {"schema": "icperf-binary-subspace-sage-replay-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "base_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "python_version": sys.version, "sage_version": sage_version,
              "field_polynomial_irreducible": True,
              "subspace_polynomial_exact_kernel": True,
              "selected_offset": winner["offset"],
              "candidate_scans": scans,
              "control_counts": counts,
              "control_x_list_equal": True,
              "stored_points_on_curve_and_in_subgroup": True,
              "scope": "independent input-construction replay; no solver or ECDLP comparison"}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "verified_offsets": len(scans),
                      "selected_size": winner["realized_size"]}, sort_keys=True))


if __name__ == "__main__":
    main()
