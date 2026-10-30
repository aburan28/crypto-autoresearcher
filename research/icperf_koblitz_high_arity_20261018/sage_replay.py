"""Independent Sage replay of planted Koblitz m=2..8 high-arity inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing


def bits_of(value) -> int:
    return sum(int(c) << i for i, c in enumerate(value.polynomial()))


def replay(record: dict, base: dict, fixture: dict) -> dict:
    n = fixture["field_degree"]
    assert (fixture["a"], n, fixture["prime_order"]) == (
        1, 73, 5384682420498870703)
    bit_ring = PolynomialRing(GF(2), "t")
    t = bit_ring.gen()
    modulus = t**n + t**fixture["field_polynomial_exponents"][1] + 1
    assert modulus.is_irreducible()
    field = GF(2**n, name="z", modulus=modulus)
    z = field.gen()
    def field_of(bits: int):
        return sum((z**i for i in range(n) if (int(bits) >> i) & 1), field.zero())
    curve = EllipticCurve(field, [1, fixture["a"], 0, 0, 1])
    zero = curve(0)
    r = Integer(fixture["prime_order"])
    assert r.is_prime(proof=True)
    generator = curve(field_of(fixture["generator"][0]),
                      field_of(fixture["generator"][1]))
    assert r * generator == zero
    indices = [0, 73, 146, 219, 292, 365, 1, 74]
    assert record["point_indices"] == indices
    points = []
    for index, archived in zip(indices, record["base_points"]):
        assert archived == base["base_points"][index]["point"]
        point = curve(field_of(archived[0]), field_of(archived[1]))
        assert r * point == zero
        points.append(point)
    membership_bits = int(base["membership"]["polynomial_hex"], 16)
    membership = sum((t**i for i in range(membership_bits.bit_length())
                      if (membership_bits >> i) & 1), bit_ring.zero())
    assert all(membership(point[0]) == 0 for point in points)

    ring = PolynomialRing(field, "T")
    T = ring.gen()
    def semaev3(x, y, target):
        e2 = x*y + x*target + y*target
        return e2**2 + x*y*target + 1
    prefix = zero
    prefixes = []
    for point in points:
        prefix += point
        assert prefix != zero
        prefixes.append(prefix)
    summaries = []
    prior_roots = None
    for m, row in enumerate(record["rows"], start=2):
        assert row["m"] == m and row["direct_label"] == f"S{m+1}_point_specialized"
        assert row["chain_label"] == "chained_S3"
        target = prefixes[m - 1]
        assert [bits_of(target[0]), bits_of(target[1])] == row["target"]
        triples = []
        for j in range(2, m + 1):
            if j == 2:
                triple = (points[0][0], points[1][0], prefixes[1][0])
            else:
                triple = (prefixes[j - 2][0], points[j - 1][0], prefixes[j - 1][0])
            assert semaev3(*triple) == 0
            triples.append([bits_of(value) for value in triple])
        assert triples == row["chain_triples"]
        assert len(triples) == row["chain_equations"] == m - 1

        roots = set()
        for mask in range(1 << m):
            signed_sum = zero
            for index, point in enumerate(points[:m]):
                signed_sum += -point if (mask >> index) & 1 else point
            assert signed_sum != zero
            roots.add(bits_of(signed_sum[0]))
        assert sorted(roots) == row["root_x"]
        assert len(roots) == row["distinct_target_x_roots"] == 1 << (m - 1)
        assert row["signed_assignments"] == 1 << m

        direct = ring.one()
        for root in sorted(roots):
            direct *= T + field_of(root)
        coefficients = [bits_of(direct[i]) for i in range(direct.degree() + 1)]
        assert coefficients == row["direct_polynomial_coefficients"]
        assert direct.degree() == row["direct_polynomial_degree"]
        assert sum(c != 0 for c in coefficients) == row["direct_polynomial_nonzero_terms"]
        assert direct(target[0]) == 0

        probe = row["negative_control"]
        probe_point = Integer(probe["scalar"]) * generator
        assert [bits_of(probe_point[0]), bits_of(probe_point[1])] == probe["point"]
        assert bits_of(direct(probe_point[0])) == probe["evaluation"] != 0

        if m == 2:
            x, y = points[0][0], points[1][0]
            s3 = (x+y)**2*T**2 + x*y*T + (x*y)**2 + 1
            assert s3.degree() == 2
            assert s3.monic() == direct
        else:
            new_x = points[m - 1][0]
            resultant_factors = ring.one()
            for root in prior_roots:
                u = field_of(root)
                # S3(u, new_x, T), one factor per root of prior S_m.
                factor = (u+new_x)**2*T**2 + u*new_x*T + (u*new_x)**2 + 1
                resultant_factors *= factor
            assert resultant_factors.degree() == direct.degree()
            assert resultant_factors.monic() == direct
        prior_roots = sorted(roots)
        summaries.append({"m": m, "direct_label": row["direct_label"],
                          "degree": int(direct.degree()),
                          "nonzero_terms": row["direct_polynomial_nonzero_terms"],
                          "chain_equations": len(triples),
                          "recursive_factorized_resultant": "PASS"})
    return {"base_points": len(points), "arity_rows": len(summaries),
            "s3_chain_and_specialized_direct_checks": "PASS",
            "rows": summaries}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    input_bytes, base_bytes, fixture_bytes = (
        args.inputs.read_bytes(), args.base.read_bytes(), args.fixture.read_bytes())
    record, base = json.loads(input_bytes), json.loads(base_bytes)
    assert record["base_sha256"] == hashlib.sha256(base_bytes).hexdigest()
    assert record["fixture_sha256"] == hashlib.sha256(fixture_bytes).hexdigest()
    fixture = next(row for row in json.loads(fixture_bytes)["fixtures"]
                   if (row["a"], row["field_degree"]) == (1, 73))
    result = {"schema": "icperf-koblitz-high-arity-sage-replay-v1",
              "inputs_sha256": hashlib.sha256(input_bytes).hexdigest(),
              "base_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python_version": sys.version,
              "method": "independent Sage curve and field replay plus factorized specialized resultants",
              "result": replay(record, base, fixture)}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arity_rows": result["result"]["arity_rows"],
                      "checks": result["result"]["s3_chain_and_specialized_direct_checks"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
