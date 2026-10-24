#!/usr/bin/env python3
"""Independent bit-string replay of the two dated X9.62 formulas."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "analysis.json").read_text())


def sha_bits(seed: int) -> str:
    digest = hashlib.sha1(seed.to_bytes(20, "big")).digest()
    return "".join(f"{byte:08b}" for byte in digest)


def dated_bits(seed: int, p_bits: int, is_1997: bool) -> int:
    t = p_bits if is_1997 else p_bits - 1
    s = (t - 1) // 160
    h = t - 160 * s
    first = sha_bits(seed)[-h:]
    pieces = ["0" + first[1:]]
    pieces += [sha_bits((seed + i) % (1 << 160)) for i in range(1, s + 1)]
    combined = "".join(pieces)
    assert len(combined) == t
    return int(combined, 2)


assert len(data["rows"]) == 21
for row in data["rows"]:
    seed = int(row["seed_hex"], 16)
    m = row["p_bits"]
    r97 = dated_bits(seed, m, True)
    r98 = dated_bits(seed, m, False)
    assert r97 == int(row["r1997_hex"], 16)
    assert r98 == int(row["r1998_hex"], 16)
    assert r98 == (r97 & ~(1 << (m - 2)))
assert sum(r["in_1997_draft_sample_table"] for r in data["rows"]) == 7
assert sum(r["r1998_matches_archived_c"] for r in data["rows"] if r["label"] == "published") == 4
assert sum(r["r1998_matches_archived_c"] for r in data["rows"] if r["label"] == "omitted") == 4
print("verified 21 pairs of dated SHA-1 bit strings and the one-bit identity")
