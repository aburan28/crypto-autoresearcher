"""Derive exact signed-multiset representation ceilings at m=2..8.

The count C(2B+m-1,m) is an upper bound on distinct subgroup sums: it
counts unordered m-multisets of the B columns and their negatives before
group collisions, cancellations, or solver restrictions. No sampling occurs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "subgroup_affine": ROOT / "research/icperf_binary_subspace_base_20261017/base.json",
    "raw_x_projected": ROOT / "research/icperf_binary_projected_base_20261017/base.json",
    "torsion_phi_projected": ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json",
}
FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture, chain = json.loads(FIXTURE.read_bytes()), json.loads(CHAIN.read_bytes())
    r = fixture["prime_order"]
    assert r == chain["curve"]["prime_order"] and fixture["cofactor"] == 4
    assert len(chain["target_channels"]) == 4
    getcontext().prec = 40
    bases = {}
    for name, path in INPUTS.items():
        base = json.loads(path.read_bytes())
        scan = next(row for row in base["candidate_scans"]
                    if row["offset"] == base["selected_offset"])
        if name == "subgroup_affine":
            size = scan["realized_size"]
            assert size == len(scan["points"])
        elif name == "raw_x_projected":
            size = scan["realized_size"]
            assert size == len(base["selected_projected_points"])
        else:
            size = scan["projected_columns"]
            assert size == len(scan["projected_points"])
        assert base["curve"]["prime_order"] == r
        rows = []
        for m in range(2, 9):
            count = math.comb(2 * size + m - 1, m)
            rows.append({"m": m, "signed_multiset_count": count,
                         "maximum_distinct_target_fraction_decimal": str(Decimal(count) / Decimal(r)),
                         "fraction_numerator": min(count, r),
                         "fraction_denominator": r})
        bases[name] = {"base_path": str(path.relative_to(ROOT)), "base_sha256": sha(path),
                       "projected_columns": size, "rows": rows}
    # A hypothetical target size from the prime-engine default formula is a
    # reference count only; there is no constructed 287-column base here.
    reference_size = 287
    reference = [{"m": m, "signed_multiset_count": math.comb(2 * reference_size + m - 1, m),
                  "maximum_distinct_target_fraction_decimal":
                      str(Decimal(math.comb(2 * reference_size + m - 1, m)) / Decimal(r))}
                 for m in range(2, 9)]
    output = {"schema": "icperf-binary-coverage-bound-v1",
              "scope": "derived upper bound on representable subgroup targets; no observed relation yield or solver measurement",
              "source_sha256": sha(Path(__file__)), "fixture_sha256": sha(FIXTURE),
              "chain_sha256": sha(CHAIN), "prime_subgroup_order": r,
              "raw_target_channels": len(chain["target_channels"]),
              "formula": "number of unordered signed m-multisets from B sign-folded columns = binomial(2B+m-1,m); distinct subgroup sums are at most this count and at most r",
              "channel_accounting": "four raw target channels share one projected subgroup target; do not multiply the signed-multiset bound by four",
              "bases": bases,
              "hypothetical_default_size": {"projected_columns": reference_size,
                                            "scope": "size reference only; no constructed base", "rows": reference}}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({name: {"B": row["projected_columns"],
                             "m8_max_fraction": row["rows"][-1]["maximum_distinct_target_fraction_decimal"]}
                      for name, row in bases.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
