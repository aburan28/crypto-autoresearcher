"""Independently replay the same-width k11 torsion-base control in Sage."""

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
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rec, parent, fixture = [json.loads(p.read_bytes()) for p in
                            (args.base, args.parent, args.fixture)]
    assert rec["parent_base_sha256"] == sha(args.parent)
    assert rec["fixture_sha256"] == sha(args.fixture)
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

    b = elem(fixture["b_polynomial_bits"])
    curve = EllipticCurve(field, [1, 0, 0, 0, b])
    r = Integer(fixture["prime_order"])
    assert r.is_prime(proof=True) and rec["curve"]["prime_order"] == r
    gamma = elem(rec["coordinate"]["gamma"])
    assert gamma**4 == b
    two_torsion = curve(field.zero(), gamma**2)
    assert [bits(two_torsion[0]), bits(two_torsion[1])] == rec["coordinate"]["two_torsion"]
    assert 2*two_torsion == curve(0)

    def canonical_lift(x):
        if x == 0:
            return None
        beta = x + b/x**2
        if beta.trace() != 0:
            return None
        half = sum((beta**(2**(2*i)) for i in range(31)), field.zero())
        assert half**2 + half == beta
        return curve(x, x*half)

    def x_phi(value):
        return gamma * (1 + 1/value)

    offset = rec["selected_offset"]
    selection = rec["selection"]
    assert offset == parent["selected_offset"] == 4096
    assert selection["width"] == 11 and selection["target_columns"] == 316
    assert selection["selection_uses_target"] is False
    full, counts = {}, {"pairs_attempted": 0, "exceptional_pairs": 0,
                        "nonliftable_pairs": 0}
    for v in range(0, 1 << 11, 2):
        counts["pairs_attempted"] += 1
        even = offset ^ v
        x, xp = x_phi(elem(even)), x_phi(elem(even ^ 1))
        if x in (0, gamma) or xp in (0, gamma):
            counts["exceptional_pairs"] += 1
            continue
        p, pp = canonical_lift(x), canonical_lift(xp)
        assert (p is None) == (pp is None)
        if p is None:
            counts["nonliftable_pairs"] += 1
            continue
        assert pp in (p + two_torsion, -(p + two_torsion))
        full[even] = (p, pp)
    assert counts == {key: rec["full_block"][key] for key in counts}
    assert sorted(full) == rec["full_block"]["liftable_even_phi"]
    assert len(full) == rec["full_block"]["liftable_pairs"] == 511

    domain, seed = selection["domain"].encode(), selection["seed"]
    def rank(even):
        return hashlib.sha256(domain + seed.to_bytes(8, "big") + even.to_bytes(8, "big")).digest()
    chosen = sorted(sorted(full, key=lambda even: (rank(even), even))[:316])
    scan = rec["candidate_scans"][0]
    assert scan["offset"] == offset and scan["projected_columns"] == 316
    assert chosen == [row[0] for row in scan["selected_representatives"]]
    assert sorted(even for t in chosen for even in (t, t ^ 1)) == scan["accepted_phi"]
    for row, coords, sign in zip(scan["selected_representatives"],
                                 scan["projected_points"], scan["pair_signs"]):
        even, xb, yb = row
        p, pp = full[even]
        assert [bits(p[0]), bits(p[1])] == [xb, yb]
        image, pair_image = 4*p, 4*pp
        assert [bits(image[0]), bits(image[1])] == coords
        assert r*image == curve(0)
        assert pair_image == (image if sign == 1 else -image)
    candidate = next(row for row in parent["candidate_scans"] if row["offset"] == offset)
    parent_even = {row[0] for row in candidate["selected_representatives"]}
    overlap = len(parent_even & set(chosen))
    assert overlap == 194
    output = {"schema": "icperf-binary-torsion-k11-local-control-sage-replay-v1",
              "scope": "independent same-width control replay; no relation or speed measurement",
              "source_sha256": sha(Path(__file__)), "base_sha256": sha(args.base),
              "parent_base_sha256": sha(args.parent), "fixture_sha256": sha(args.fixture),
              "sage_version": sage_version, "python_version": sys.version,
              "full_liftable_pairs_checked": len(full), "selected_columns_checked": len(chosen),
              "overlap_with_weighted_base": overlap, "pair_signs_checked": len(chosen)}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"full_liftable_pairs": len(full), "selected_columns": len(chosen),
                      "weighted_overlap": overlap}, sort_keys=True))


if __name__ == "__main__":
    main()
