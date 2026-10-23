"""Independently replay the torsion-coordinate base in Sage arithmetic."""

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
    modulus = t**61 + t**5 + t**2 + t + 1
    assert n == 61 and modulus.is_irreducible()
    field = GF(2**n, name="z", modulus=modulus)
    z = field.gen()

    def elem(bits: int):
        return sum((z**i for i in range(n) if (int(bits) >> i) & 1), field.zero())

    def bits(value) -> int:
        return sum(int(c) << i for i, c in enumerate(value.polynomial().list()))

    b = elem(rec["curve"]["b_polynomial_bits"])
    curve = EllipticCurve(field, [1, 0, 0, 0, b])
    r = Integer(rec["curve"]["prime_order"])
    assert r.is_prime(proof=True) and fixture["prime_order"] == r
    gamma = b**(2**(n-2))
    assert gamma**4 == b and bits(gamma) == rec["coordinate"]["gamma"]
    t2_point = curve(field.zero(), gamma**2)
    assert bits(gamma**2) == rec["coordinate"]["gamma_squared"]
    assert 2*t2_point == curve(0)

    def point(coords):
        return curve(elem(coords[0]), elem(coords[1]))

    def canonical_lift(x):
        assert x != 0
        beta = x + b / x**2
        if beta.trace() != 0:
            return None
        half_trace = sum((beta**(2**(2*i)) for i in range((n+1)//2)), field.zero())
        assert half_trace**2 + half_trace == beta
        return curve(x, x * half_trace)

    def phi_x(x):
        assert x != gamma
        return gamma / (x + gamma)

    def x_phi(value):
        assert value != 0
        return gamma * (1 + 1/value)

    coeffs = [elem(c) for c in rec["linearized_membership_coefficients"]]
    k = rec["predeclared_selection"]["subspace_dimension"]
    assert k == 10 and coeffs[-1] == 1 and len(coeffs) == k + 1

    def linearized(value):
        result = field.zero()
        power = value
        for coeff in coeffs:
            result += coeff * power
            power = power**2
        return result

    assert {bits(v) for v in (elem(i) for i in range(1 << k))} == set(range(1 << k))
    assert all(linearized(elem(i)) == 0 for i in range(1 << k))
    scans = []
    for row in rec["candidate_scans"]:
        c = row["offset"]
        constant = linearized(elem(c))
        assert constant == elem(row["affine_membership_constant"]) and constant != 0
        accepted = []
        for i in range(1 << k):
            value = elem(c ^ i)
            assert linearized(value) == constant
            x = x_phi(value)
            if x == 0 or x == gamma:
                continue
            assert phi_x(x) == value
            try:
                curve.lift_x(x)
            except ValueError:
                continue
            accepted.append(c ^ i)
        accepted.sort()
        assert accepted == row["accepted_phi"]
        assert len(accepted) == row["raw_representatives"]
        assert len(accepted) == 2 * row["projected_columns"]
        assert all((v ^ 1) in accepted for v in accepted)
        scans.append({"offset": c, "accepted": len(accepted),
                      "unique_projected_columns": row["projected_columns"]})

    target = rec["predeclared_selection"]["target_columns"]
    winner = min(rec["candidate_scans"],
                 key=lambda row: (abs(row["projected_columns"] - target), row["offset"]))
    assert winner["offset"] == rec["selected_offset"]
    reps = winner["selected_representatives"]
    assert len(reps) == len(winner["projected_points"]) == len(winner["pair_signs"])
    seen_projected_x = set()
    for rep, coords, sign in zip(reps, winner["projected_points"], winner["pair_signs"]):
        value, x_bits, y_bits = rep
        assert value % 2 == 0 and x_phi(elem(value)) == elem(x_bits)
        p = canonical_lift(elem(x_bits))
        assert p == point([x_bits, y_bits]) and phi_x(p[0]) == elem(value)
        paired_x = x_phi(elem(value ^ 1))
        paired = canonical_lift(paired_x)
        assert paired is not None and paired in (p + t2_point, -(p + t2_point))
        image, paired_image = 4*p, 4*paired
        assert image == point(coords) and r*image == curve(0) and image != curve(0)
        assert paired_image == (image if sign == 1 else -image)
        assert bits(image[0]) not in seen_projected_x
        seen_projected_x.add(bits(image[0]))

    control = rec["paired_random_control"]
    seed, domain = control["seed"], control["domain"].encode()
    counts = {"zero": 0, "exceptional": 0, "nonliftable": 0, "duplicate": 0,
              "projected_duplicate": 0, "accepted": 0}
    seen_x, seen_projected_x = set(), set()
    rows = []
    signs = []
    for counter in range(control["draws"]):
        h = hashlib.sha256(domain + seed.to_bytes(8, "big") +
                           counter.to_bytes(8, "big")).digest()
        x_bits = int.from_bytes(h[:8], "big") & ((1 << n) - 1)
        x = elem(x_bits)
        if x == 0:
            counts["zero"] += 1
            continue
        if x == gamma:
            counts["exceptional"] += 1
            continue
        if x_bits in seen_x:
            counts["duplicate"] += 1
            continue
        p = canonical_lift(x)
        if p is None:
            counts["nonliftable"] += 1
            continue
        image = 4*p
        if bits(image[0]) in seen_projected_x:
            counts["projected_duplicate"] += 1
            continue
        paired = canonical_lift((p+t2_point)[0])
        assert paired is not None
        paired_image = 4*paired
        sign = 1 if paired_image == image else -1
        assert paired_image == (image if sign == 1 else -image)
        seen_x.update((x_bits, bits(paired[0])))
        seen_projected_x.add(bits(image[0]))
        rows.append([x_bits, bits(p[1]), bits(paired[0]), bits(paired[1]),
                     bits(image[0]), bits(image[1])])
        signs.append(sign)
        counts["accepted"] += 1
    assert counts == control["counts"]
    assert rows == control["paired_representatives"] and signs == control["pair_signs"]
    assert len(rows) == winner["projected_columns"]

    def pphi3(values):
        e1 = sum(values, field.zero())
        s3 = (values[0]**2 + values[0]) * (values[1]**2 + values[1]) * (values[2]**2 + values[2])
        return s3 + gamma * e1**2

    def s3(xs):
        e2 = xs[0]*xs[1] + xs[0]*xs[2] + xs[1]*xs[2]
        return e2**2 + xs[0]*xs[1]*xs[2] + b

    true_controls = rec["three_point_controls"]["true"]
    false_controls = rec["three_point_controls"]["false"]
    assert len(true_controls) == len(false_controls) == 32
    for i, (a, c, third_phi, third_x) in enumerate(true_controls):
        assert [a,c] == [reps[i][0], reps[i+32][0]]
        p, q = point(reps[i][1:]), point(reps[i+32][1:])
        third = p+q
        assert bits(third[0]) == third_x and bits(phi_x(third[0])) == third_phi
        values = [elem(a), elem(c), elem(third_phi)]
        xs = [p[0], q[0], third[0]]
        assert pphi3(values) == 0 and s3(xs) == 0
        assert s3(xs) * (values[0]*values[1]*values[2])**2 == gamma**3 * pphi3(values)
    for i, (a, c, third_phi) in enumerate(false_controls):
        assert [a,c,third_phi] == [reps[i][0], reps[i+32][0], reps[i+64][0]]
        values = [elem(a), elem(c), elem(third_phi)]
        xs = [x_phi(v) for v in values]
        assert pphi3(values) != 0 and s3(xs) != 0
        assert s3(xs) * (values[0]*values[1]*values[2])**2 == gamma**3 * pphi3(values)

    result = {"schema": "icperf-binary-torsion-sage-replay-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "base_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "sage_version": sage_version, "python_version": sys.version,
              "candidate_scans": scans, "selected_offset": winner["offset"],
              "pair_signs_replayed": True, "paired_random_control_replayed": True,
              "true_three_point_controls": len(true_controls),
              "false_three_point_controls": len(false_controls),
              "coordinate_identity_and_rational_formula_checked": True,
              "scope": "independent finite-input and identity replay; no solver performance result"}
    with args.out.open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "selected_columns": len(reps),
                      "checked_three_point_triples": len(true_controls)+len(false_controls)}, sort_keys=True))


if __name__ == "__main__":
    main()
