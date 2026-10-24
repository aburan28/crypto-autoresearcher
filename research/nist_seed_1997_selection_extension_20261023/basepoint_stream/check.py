#!/usr/bin/env python3
"""Bounded exact-byte search under the frozen direct-stream protocol."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "research/nist_seed_skipped_curves_20261016/traits.json"
EXPECTED = "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67"
OUT = Path(__file__).with_name("results.json")


def offsets(haystack: bytes, needle: bytes) -> list[int]:
    found = []
    pos = 0
    while (pos := haystack.find(needle, pos)) >= 0:
        found.append(pos)
        pos += 1
    return found


def main() -> None:
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    records = json.loads(raw)["published_controls"]
    assert len(records) == 10
    output = []
    for name, row in sorted(records.items()):
        p = int(row["p_hex"], 16)
        width = (p.bit_length() + 7) // 8
        gx = row["identity"]["curve"]["generator"][0].to_bytes(width, "big")
        seed = bytes.fromhex(row["seed_hex"])
        ordinal = row["seed_ordinal_one_based"]
        limit = 20 * ordinal + 100000
        count = limit + max(width, len(seed))
        state = (row["timestamp"] << 16) | 0x330e
        stream = bytearray(count)
        for i in range(count):
            state = (0x5deece66d * state + 0xb) & ((1 << 48) - 1)
            stream[i] = state >> 40
        direct_hits = [i for i in offsets(stream, gx) if i <= limit]
        seed_hits = [i for i in offsets(stream, seed) if i <= limit]
        synthetic_hits = offsets(stream, bytes(stream[:width]))
        expected_seed = 20 * (ordinal - 1)
        assert expected_seed in seed_hits, name
        assert 0 in synthetic_hits, name
        output.append({
            "name": name,
            "curve_uid": row["identity"]["curve_uid"],
            "timestamp": row["timestamp"],
            "seed_ordinal_one_based": ordinal,
            "gx_hex": gx.hex(),
            "gx_width_bytes": width,
            "last_match_start_offset": limit,
            "published_seed_expected_offset": expected_seed,
            "published_seed_hits": seed_hits,
            "direct_gx_hits": direct_hits,
            "synthetic_gx_hits": synthetic_hits,
        })
    OUT.write_text(json.dumps({"source_sha256": EXPECTED, "rule": "srand48 timestamp, lrand48 high byte, contiguous big-endian Gx", "records": output}, indent=2) + "\n")
    hits = sum(len(r["direct_gx_hits"]) for r in output)
    print(f"checked {len(output)} published Gx values; direct hits: {hits}; seed and synthetic controls: pass")


if __name__ == "__main__":
    main()
