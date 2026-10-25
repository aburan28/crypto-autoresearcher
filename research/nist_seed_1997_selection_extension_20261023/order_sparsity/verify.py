#!/usr/bin/env python3
"""Independent signed-digit DP and exact pair replay for analysis.json."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "analysis.json").read_text())


def min_signed_weight(value: int) -> int:
    """Minimum weight over digits {-1,0,1}, via bit/carry dynamic programming."""
    states = {0: 0}
    for bit_index in range(value.bit_length() + 3):
        bit = (value >> bit_index) & 1
        next_states = {}
        for carry, cost in states.items():
            for digit in (-1, 0, 1):
                if (bit + carry - digit) & 1:
                    continue
                new_carry = (bit + carry - digit) // 2
                if abs(new_carry) > 1:
                    continue
                next_cost = cost + abs(digit)
                next_states[new_carry] = min(next_cost, next_states.get(new_carry, 10**9))
        states = next_states
    assert 0 in states
    return states[0]


rows = {r["curve_uid"]: r for r in data["rows"]}
assert len(rows) == 21
for row in rows.values():
    n = int(row["n_hex"], 16)
    gap = int(row["gap_hex"], 16)
    assert gap == (1 << n.bit_length()) - n
    assert row["n_binary_weight"] == bin(n).count("1")
    assert row["gap_binary_weight"] == bin(gap).count("1")
    assert row["n_naf_weight"] == min_signed_weight(n)
    assert row["gap_naf_weight"] == min_signed_weight(gap)
assert len(data["pairs"]) == 25
assert sum(p["earlier_omission"] for p in data["pairs"]) == 16
for pair in data["pairs"]:
    omitted = rows[pair["omitted_uid"]]
    published = rows[pair["published_uid"]]
    assert omitted["field_hex"] == published["field_hex"]
    assert omitted["timestamp"] == published["timestamp"]
    assert pair["earlier_omission"] == (omitted["ordinal"] < published["ordinal"])
    for metric in ("n_binary_weight", "n_naf_weight", "gap_binary_weight", "gap_naf_weight"):
        assert pair[metric] == {"omitted": omitted[metric], "published": published[metric],
                                "published_better": published[metric] < omitted[metric],
                                "tie": published[metric] == omitted[metric]}
print("verified 21 minimum signed-digit weights and 25 exact UID-bound pairs")
