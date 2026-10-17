"""Independent Sage replay of the target-blind weighted k11 torsion base."""

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
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_blob, fixture_blob = args.base.read_bytes(), args.fixture.read_bytes()
    rec, fixture = json.loads(base_blob), json.loads(fixture_blob)
    assert rec["fixture_sha256"] == hashlib.sha256(fixture_blob).hexdigest()
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
    assert r.is_prime(proof=True) and rec["curve"]["prime_order"] == r
    gamma = b**(2**59)
    assert gamma**4 == b and bits(gamma) == rec["coordinate"]["gamma"]
    t2 = curve(field.zero(), gamma**2)
    assert [bits(t2[0]), bits(t2[1])] == rec["coordinate"]["two_torsion"]
    assert 2*t2 == curve(0)

    def point(coords):
        return curve(elem(coords[0]), elem(coords[1]))

    def x_phi(value):
        return gamma * (1 + 1/value)

    def phi_x(x):
        return gamma / (x + gamma)

    def canonical_lift(x):
        if x == 0:
            return None
        beta = x + b / x**2
        if beta.trace() != 0:
            return None
        half = sum((beta**(2**(2*i)) for i in range(31)), field.zero())
        assert half**2 + half == beta
        return curve(x, x * half)

    coeffs = [elem(c) for c in rec["linearized_membership_coefficients"]]
    rule = rec["predeclared_selection"]
    assert rule["subspace_dimension"] == 11 and rule["weight_limit"] == 5
    assert len(coeffs) == 12 and coeffs[-1] == 1

    def linearized(value):
        result, power = field.zero(), value
        for coeff in coeffs:
            result += coeff * power
            power = power**2
        return result

    assert all(linearized(elem(v)) == 0 for v in range(1 << 11))
    assert rule["target_columns"] == next(B for B in range(1, 1000)
                                          if math.comb(2 * B + 7, 8) >= r) == 311
    assert rule["offsets"] == [2048, 4096, 6144, 8192]
    scans = []
    for scan in rec["candidate_scans"]:
        offset = scan["offset"]
        constant = linearized(elem(offset))
        assert constant == elem(scan["affine_membership_constant"])
        accepted = []
        exceptional = nonliftable = 0
        for v in range(1 << 11):
            if (v >> 1).bit_count() > 5:
                continue
            value = elem(offset ^ v)
            assert linearized(value) == constant
            x = x_phi(value)
            if x == 0 or x == gamma:
                exceptional += 1
                continue
            if canonical_lift(x) is None:
                nonliftable += 1
            else:
                accepted.append(offset ^ v)
        accepted.sort()
        assert accepted == scan["accepted_phi"]
        assert len(accepted) == scan["raw_representatives"] == 2*scan["projected_columns"]
        assert nonliftable == scan["nonliftable"] and exceptional == scan["exceptional"]
        assert all((v ^ 1) in accepted for v in accepted)
        scans.append({"offset": offset, "accepted": len(accepted),
                      "projected_columns": scan["projected_columns"]})
    selected = min(rec["candidate_scans"],
                   key=lambda row: (abs(row["projected_columns"] - 311), row["offset"]))
    assert selected["offset"] == rec["selected_offset"]
    reps = selected["selected_representatives"]
    assert len(reps) == len(selected["projected_points"]) == len(selected["pair_signs"])
    for rep, image_coords, sign in zip(reps, selected["projected_points"], selected["pair_signs"]):
        value, xb, yb = rep
        assert value % 2 == 0 and (value ^ 1) in selected["accepted_phi"]
        p = canonical_lift(elem(xb))
        assert p == point([xb, yb]) and bits(phi_x(p[0])) == value
        pair = canonical_lift(x_phi(elem(value ^ 1)))
        assert pair is not None and pair in (p+t2, -(p+t2))
        image = 4*p
        assert image == point(image_coords) and r*image == curve(0)
        assert 4*pair == (image if sign == 1 else -image)

    control = rec["paired_random_control"]
    counts = {"zero": 0, "exceptional": 0, "nonliftable": 0, "duplicate": 0,
              "projected_duplicate": 0, "accepted": 0}
    seen_x, seen_projected_x, rows, signs = set(), set(), [], []
    domain, seed = control["domain"].encode(), control["seed"]
    for counter in range(control["draws"]):
        h = hashlib.sha256(domain + seed.to_bytes(8, "big") + counter.to_bytes(8, "big")).digest()
        xb = int.from_bytes(h[:8], "big") & ((1 << 61) - 1)
        x = elem(xb)
        if x == 0:
            counts["zero"] += 1; continue
        if x == gamma:
            counts["exceptional"] += 1; continue
        if xb in seen_x:
            counts["duplicate"] += 1; continue
        p = canonical_lift(x)
        if p is None:
            counts["nonliftable"] += 1; continue
        image = 4*p
        if bits(image[0]) in seen_projected_x:
            counts["projected_duplicate"] += 1; continue
        pair = canonical_lift((p+t2)[0])
        assert pair is not None
        paired_image = 4*pair
        sign = 1 if paired_image == image else -1
        assert paired_image == (image if sign == 1 else -image)
        seen_x.update((xb, bits(pair[0])))
        seen_projected_x.add(bits(image[0]))
        rows.append([xb, bits(p[1]), bits(pair[0]), bits(pair[1]), bits(image[0]), bits(image[1])])
        signs.append(sign)
        counts["accepted"] += 1
    assert counts == control["counts"]
    assert rows == control["paired_representatives"] and signs == control["pair_signs"]
    assert len(rows) == selected["projected_columns"]

    def pphi3(a, b, c):
        return (a*a+a)*(b*b+b)*(c*c+c) + gamma*(a+b+c)**2

    for a, c, third_phi, third_x in rec["three_point_controls"]["true"]:
        assert pphi3(elem(a), elem(c), elem(third_phi)) == 0
        assert bits(phi_x((point(reps[[v[0] for v in reps].index(a)][1:]) +
                           point(reps[[v[0] for v in reps].index(c)][1:]))[0])) == third_phi
        assert x_phi(elem(third_phi)) == elem(third_x)
    for a, c, third_phi in rec["three_point_controls"]["false"]:
        assert pphi3(elem(a), elem(c), elem(third_phi)) != 0
    output = {"schema": "icperf-binary-torsion-k11-weighted-sage-replay-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "base_sha256": hashlib.sha256(base_blob).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_blob).hexdigest(),
              "sage_version": sage_version, "python_version": sys.version,
              "candidate_scans": scans, "selected_offset": selected["offset"],
              "selected_columns_checked": len(reps),
              "paired_random_control_checked": len(rows),
              "true_false_formula_controls_checked": 64,
              "scope": "independent target-blind base and formula replay; no solver or ECDLP speed result"}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"selected_offset": selected["offset"],
                      "projected_columns": len(reps), "control_rows": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
