#!/usr/bin/env python3
"""Derive exact CM class-group 2-ranks from archived fundamental discriminants.

For an imaginary quadratic fundamental discriminant D with t distinct prime
divisors, genus theory gives the class group's 2-rank as t - 1.  This script
does not compute the class number or a curve's actual endomorphism ring.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCES = (
    ROOT / "research/nist_seed_exact_conductor_census_20261023/runs/census-20261023T1733Z/results.json",
    ROOT / "research/nist_seed_exact_conductor_20261023/runs/first-stage-20261023T1720Z/results.json",
)
EXPECTED_SOURCE_SHA256 = (
    "178864fce2e529ea5828008bd9887a6789099a9c928104376c7055ff5c59139d",
    "e96adac781a997209151c4bd005cd4a1ba8430bc4af59d978d07ee5a4e5c88a8",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    # Synthetic genus-count controls: the fields of D=-3 and D=-15 have
    # respectively one and two distinct ramified rational primes.
    assert _rank_from_fundamental(-3, [3]) == 0
    assert _rank_from_fundamental(-15, [3, 5]) == 1
    rows = []
    seen = set()
    sources = []
    for path, expected_digest in zip(SOURCES, EXPECTED_SOURCE_SHA256, strict=True):
        digest = sha256(path)
        assert digest == expected_digest, path
        sources.append({"path": str(path.relative_to(ROOT)), "sha256": digest})
        for record in json.loads(path.read_text()):
            name = record["name"]
            if name.startswith("control_"):
                continue
            assert name not in seen, name
            seen.add(name)
            value = record["value"]
            delta = int(value["delta"])
            fundamental = int(value["D_K"])
            conductor = int(value["f_pi"])
            assert delta == conductor * conductor * fundamental
            assert fundamental < 0 and fundamental % 4 == 1
            product = 1
            distinct = []
            for prime_text, exponent in value["factors"]:
                prime = int(prime_text)
                product *= prime**exponent
                if fundamental % prime == 0:
                    distinct.append(prime)
            assert product == abs(delta)
            assert len(distinct) == len(set(distinct))
            rank = _rank_from_fundamental(fundamental, distinct)
            label = "omitted" if name.startswith("omitted_") else "published"
            rows.append({
                "name": name,
                "label": label,
                "curve_uid": record["curve_uid"],
                "fundamental_discriminant": str(fundamental),
                "distinct_prime_divisor_count": len(distinct),
                "cm_class_group_2_rank": rank,
            })
    rows.sort(key=lambda row: (row["label"], row["name"]))
    assert len(rows) == 19
    assert Counter(row["label"] for row in rows) == {"omitted": 11, "published": 8}
    counts = {
        label: dict(sorted(Counter(row["cm_class_group_2_rank"] for row in rows if row["label"] == label).items()))
        for label in ("omitted", "published")
    }
    ranks = {label: {row["cm_class_group_2_rank"] for row in rows if row["label"] == label} for label in counts}
    assert ranks["omitted"] & ranks["published"]
    output = {
        "schema": "nist-seed-cm-genus-rank/v1",
        "sources": sources,
        "theorem": "For negative fundamental discriminant D with t distinct prime divisors, class-group 2-rank=t-1.",
        "result": {
            "omitted_count": 11,
            "published_same_field_count": 8,
            "rank_counts": counts,
            "overlapping_ranks": sorted(ranks["omitted"] & ranks["published"]),
            "exact_rank_separates_labels": False,
        },
        "rows": rows,
    }
    (HERE / "analysis.json").write_text(json.dumps(output, indent=2) + "\n")


def _product(values: list[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


def _rank_from_fundamental(discriminant: int, primes: list[int]) -> int:
    assert discriminant < 0 and discriminant % 4 == 1
    assert primes and len(primes) == len(set(primes))
    assert abs(discriminant) == _product(primes)
    return len(primes) - 1


if __name__ == "__main__":
    main()
