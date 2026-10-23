"""Exact Hasse ceilings for proper-subfield x bases on descended binary curves.

The lemma is conditional on E being defined over the listed subfield. This
integer screen does not assert a curve order or perform an ECDLP experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from math import isqrt
from pathlib import Path


def row(n: int) -> dict:
    lower_large_prime = 1 << (n - 1)
    cells = []
    for d in range(1, n):
        if n % d:
            continue
        q = 1 << d
        hasse_ceiling = q + 1 + isqrt(4 * q)
        cells.append({"subfield_degree": d, "q": q,
                      "hasse_ceiling": hasse_ceiling,
                      "below_half_field_order": hasse_ceiling < lower_large_prime})
    return {"field_degree": n, "large_prime_lower_bound": lower_large_prime,
            "proper_subfields": cells,
            "maximum_hasse_ceiling": max(c["hasse_ceiling"] for c in cells)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    record = {"schema": "icperf-binary-subfield-rank-gate-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "rows": [row(n) for n in (50, 53, 63)],
              "lemma": "For E/F_q and x(P) in F_q, Frobenius_q(P)=+/-P; if P has prime order r, then r divides q+1-/+t and r<=q+1+floor(2sqrt(q)), where |t|<=2sqrt(q).",
              "scope": "conditional subgroup-rank obstruction; no ordinary-binary non-descended curve claim and no cost claim"}
    assert all(all(c["below_half_field_order"] for c in row_["proper_subfields"])
               for row_ in record["rows"])
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "status": "written"}, sort_keys=True))


if __name__ == "__main__":
    main()
