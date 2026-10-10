"""Independent integrity checks for the frozen SSIQ prefix-scan artifact."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def check(path: Path) -> None:
    data = json.loads((path / "raw-result.json").read_text(encoding="utf-8"))
    assert data["experiment_id"] == "EXP-SSIQ-975f7e"
    assert data["run_id"] == "RUN-SSIQ-be0b59"
    rows = data["rows"]
    assert [row["degree"] for row in rows] == sorted({row["degree"] for row in rows})
    expected_smooth = []
    for degree in range(31, 181):
        remainder = degree
        for prime in (2, 3, 5, 7):
            while remainder % prime == 0:
                remainder //= prime
        if remainder == 1:
            expected_smooth.append(degree)
    assert [row["degree"] for row in rows] == expected_smooth
    for row in rows:
        degree = row["degree"]
        factors = row["factors_ascending"]
        assert factors == sorted(factors)
        assert all(prime in (2, 3, 5, 7) for prime in factors)
        assert math.prod(factors) == degree
        for order, key in ((factors, "ascending"), (list(reversed(factors)), "descending")):
            candidates = [math.prod(order[:index]) for index in range(1, len(order) + 1)]
            expected = max(product for product in candidates if product <= 30)
            assert row[f"{key}_prefix"] == expected
            assert row[f"{key}_cofactor"] == degree // expected
        a, b = row["ascending_prefix"], row["descending_prefix"]
        ratio = max(a, b) >= 2 * min(a, b)
        sides = (row["ascending_cofactor"] > 30) != (row["descending_cofactor"] > 30)
        assert row["ratio_at_least_two"] == ratio
        assert row["opposite_cofactor_sides"] == sides
        assert row["meets_both"] == (ratio and sides)
    assert data["smooth_count"] == len(rows)
    assert data["match_count"] == sum(row["meets_both"] for row in rows)
    assert all(data["controls"].values())
    assert rows[0]["degree"] == 32
    assert rows[0]["ascending_prefix"] == rows[0]["descending_prefix"]


if __name__ == "__main__":
    check(Path(sys.argv[1]))
