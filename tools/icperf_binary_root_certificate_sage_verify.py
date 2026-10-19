"""Independently replay a binary m8 full-point certificate in Sage."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, PolynomialRing
from sage.version import version as sage_version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--chain", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    blobs = [p.read_bytes() for p in (args.certificate, args.base, args.chain)]
    cert, base, chain = [json.loads(blob) for blob in blobs]
    digests = [hashlib.sha256(blob).hexdigest() for blob in blobs]
    assert cert["input_sha256"]["base"] == digests[1]
    assert cert["input_sha256"]["chain"] == digests[2]
    assert cert["result"]["certified"]
    assert len(cert["result"]["full_point_certificates"]) == 1
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

    curve = EllipticCurve(field, [1, 0, 0, 0, elem(chain["curve"]["b_polynomial_bits"])])
    gamma = elem(chain["gamma"])
    assert gamma**4 == elem(chain["curve"]["b_polynomial_bits"])

    def point(coords):
        return curve(elem(coords[0]), elem(coords[1]))

    def phi(p):
        return gamma / (p[0] + gamma)

    def pphi3(a, b, c):
        return (a*a+a)*(b*b+b)*(c*c+c) + gamma*(a+b+c)**2

    result = cert["result"]
    selected = next(row for row in base["candidate_scans"]
                    if row["offset"] == base["selected_offset"])
    assert set(result["base_phi"]) <= set(selected["accepted_phi"])
    ts = [elem(value) for value in result["base_phi"]]
    us = [elem(value) for value in result["intermediate_phi"]]
    target = point(chain["target_channels"][result["target_channel"]])
    triples = [[ts[0], ts[1], us[0]]]
    triples += [[us[i-1], ts[i+1], us[i]] for i in range(1, 6)]
    triples += [[us[-1], ts[-1], elem(chain["target_channel_phi"][result["target_channel"]])]]
    assert len(triples) == 7 and all(pphi3(*row) == 0 for row in triples)
    witness = result["full_point_certificates"][0]
    points = [point(coords) for coords in witness["points"]]
    assert [bits(phi(p)) for p in points] == result["base_phi"]
    assert sum(points, curve(0)) == target
    subgroup_target = point(chain["subgroup_target"])
    assert 4*target == subgroup_target
    assert chain["curve"]["prime_order"]*subgroup_target == curve(0)
    reps = [point(row[1:]) for row in selected["selected_representatives"]]
    assert sum((coefficient * (4*reps[index]) for index, coefficient in
                witness["projected_row"]), curve(0)) == subgroup_target
    assert sum((4*p for p in points), curve(0)) == subgroup_target
    output = {"schema": "icperf-binary-root-certificate-sage-replay-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "certificate_sha256": digests[0], "base_sha256": digests[1],
              "chain_sha256": digests[2], "sage_version": sage_version,
              "python_version": sys.version, "field_equations_checked": 7,
              "full_point_certificates_checked": 1, "projected_rows_checked": 1,
              "scope": "independent planted root certificate replay; no solver search or speed claim"}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"equations": 7, "certificates": 1, "rows": 1}, sort_keys=True))


if __name__ == "__main__":
    main()
