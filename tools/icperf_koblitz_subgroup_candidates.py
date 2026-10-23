"""Find and certify bounded Koblitz prime-subgroup candidates at n=64..80.

The search uses factorint(limit=100000) only to discover candidates. A listed
candidate is certified independently by exact divisibility into the Frobenius
group order and deterministic Miller–Rabin below 2^64. Missing candidates in
a search row are not a factorization or mathematical exclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sympy import __version__ as sympy_version
from sympy import factorint

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_koblitz_size_screen import count_over_f2, prime64  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for a in (0, 1):
        t1 = 3 - count_over_f2(a)
        tm2, tm1 = 2, t1
        for n in range(2, 81):
            tm2, tm1 = tm1, t1 * tm1 - 2 * tm2
            if n < 64:
                continue
            order = (1 << n) + 1 - tm1
            attempted = factorint(order, limit=100_000)
            candidates = []
            for factor in attempted:
                r = int(factor)
                if (1 << 50) <= r <= (1 << 63) and prime64(r):
                    assert order % r == 0
                    candidates.append({"prime_order": r, "prime_bits": r.bit_length(),
                                       "cofactor": order // r,
                                       "certificate": "r prime by deterministic MR64; r divides exact Frobenius group order"})
            rows.append({"a": a, "field_degree": n, "trace": tm1,
                         "group_order": order,
                         "bounded_factor_search": [[int(p), int(e)] for p, e in sorted(attempted.items())],
                         "certified_candidates": sorted(candidates, key=lambda x: x["prime_order"]),
                         "empty_means_no_candidate_found_only": not candidates})
    expected = {(0, 71): 5513228015079457,
                (0, 73): 86020738150056119,
                (1, 73): 5384682420498870703}
    for (a, n), r in expected.items():
        cell = next(row for row in rows if row["a"] == a and row["field_degree"] == n)
        assert any(c["prime_order"] == r for c in cell["certified_candidates"])
    record = {"schema": "icperf-koblitz-subgroup-candidates-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "size_screen_source_sha256": hashlib.sha256((Path(__file__).parent / "icperf_koblitz_size_screen.py").read_bytes()).hexdigest(),
              "sympy_version": sympy_version, "search_limit": 100_000,
              "ambient_field_degree_range": [64, 80],
              "target_prime_order_interval": [1 << 50, 1 << 63],
              "rows": rows,
              "scope": "bounded candidate discovery; listed prime divisors certified, empty search rows inconclusive"}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "status": "written",
                      "certified_candidates": sum(len(x["certified_candidates"]) for x in rows)},
                     sort_keys=True))


if __name__ == "__main__":
    main()
