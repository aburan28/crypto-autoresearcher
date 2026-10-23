#!/usr/bin/env python3
"""Disjoint numeric shards of all 2^46 strict 20-draw candidate-start states."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
import time

import scan

HERE = Path(__file__).resolve().parent
ORBIT_SIZE = 1 << 46


def seed_from_state(state: int) -> bytes:
    assert 0 <= state <= scan.MASK48 and state % 4 == 1
    seed = bytearray()
    for _ in range(20):
        seed.append(state >> 40)
        state = (scan.MULT48 * state + 0xb) & scan.MASK48
    return bytes(seed)


def state_from_timestamp(timestamp: int, ordinal: int) -> int:
    state = ((timestamp & 0xffffffff) << 16) | 0x330e
    for _ in range(20 * (ordinal - 1) + 1):
        state = (scan.MULT48 * state + 0xb) & scan.MASK48
    assert state % 4 == 1
    return state


def run(out: Path) -> dict:
    started_at = datetime.now(timezone.utc).isoformat()
    wall_start = time.monotonic()
    protocol_path = HERE / "orbit_protocol.json"
    protocol = json.loads(protocol_path.read_text())
    first, count = protocol["first_state_index"], protocol["state_count"]
    assert 0 <= first < ORBIT_SIZE and 0 < count <= ORBIT_SIZE - first
    traits_path = scan.ROOT / "research/nist_seed_skipped_curves_20261016/traits.json"
    traits = json.loads(traits_path.read_text())
    controls = []
    for name, published in traits["published_controls"].items():
        x = state_from_timestamp(published["timestamp"], published["seed_ordinal_one_based"])
        assert seed_from_state(x).hex() == published["seed_hex"].removeprefix("0x")
        controls.append({"name": name, "state_index": (x - 1) // 4, "ok": True})
    assert len(controls) == 10
    p = int(traits["published_controls"][protocol["field_control"]]["p_hex"], 16)
    out.mkdir(parents=True, exist_ok=False)
    path = out / "root_admitting_candidates.jsonl"
    counters = {"forbidden": 0, "no_root": 0, "root_exists": 0}
    with path.open("w") as stream:
        for i in range(first, first + count):
            x = 4 * i + 1
            seed = seed_from_state(x)
            c = scan.ansi_c(seed, p.bit_length())
            if c == 0 or (4 * c + 27) % p == 0:
                counters["forbidden"] += 1
                continue
            b2 = (-27 * pow(c, -1, p)) % p
            if pow(b2, (p - 1) // 2, p) != 1:
                counters["no_root"] += 1
                continue
            b = pow(b2, (p + 1) // 4, p)
            assert b * b % p == b2
            stream.write(json.dumps({"state_index": i, "first_state": hex(x), "seed": seed.hex(), "c": hex(c), "b": hex(b)}) + "\n")
            counters["root_exists"] += 1
    assert sum(counters.values()) == count
    manifest = {"protocol_sha256": scan.digest(protocol_path), "scanner_sha256": scan.digest(Path(__file__)), "traits_sha256": scan.digest(traits_path), "first_state_index": first, "state_count": count, "fraction_of_strict_orbit": "1/1073741824", "field": protocol["field_control"], "p": hex(p), "counters": counters, "candidate_file_sha256": scan.digest(path), "published_controls": controls, "python": sys.version, "platform": platform.platform(), "started_at_utc": started_at, "finished_at_utc": datetime.now(timezone.utc).isoformat(), "wall_seconds": time.monotonic() - wall_start}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: orbit_scan.py OUTPUT_DIRECTORY")
    print(json.dumps(run(Path(sys.argv[1])), indent=2))
