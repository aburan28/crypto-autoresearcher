"""Independent scalar replay and complete-order check for a packed tail file.

This checker deliberately does not import the producer or its group law.
Selections depend on the final byte length and a fixed SHA256 counter stream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

PAIR = struct.Struct("<QQ")
SEED = b"icperf-prime50-m8-20261017"
CHUNK_PAIRS = 1_000_000


def add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    u, v = Q
    if x == u:
        if (y + v) % p == 0:
            return None
        slope = ((3*x*x + a) * pow(2*y, -1, p)) % p
    else:
        slope = ((v-y) * pow(u-x, -1, p)) % p
    xx = (slope*slope-x-u) % p
    return xx, (slope*(x-xx)-y) % p


def positions(n, count=4096):
    out = set(range(min(256, n))) | set(range(max(0, n-256), n))
    counter = 0
    while len(out) < min(n, count + 512):
        digest = hashlib.sha256(SEED + counter.to_bytes(8, "big")).digest()
        out.add(int.from_bytes(digest[:8], "big") % n)
        counter += 1
    return out, counter


def check(table: Path, input_path: Path, validation: Path, samples: Path):
    header, *rows = input_path.read_text().splitlines()
    p, a, b, h, base = map(int, header.split())
    fb = [tuple(map(int, row.split())) for row in rows]
    assert base == 2 * len(fb)
    for x, y in fb:
        assert 0 <= x < p and 0 <= y < p and (y*y-x*x*x-a*x-b) % p == 0
    size = table.stat().st_size
    assert size % PAIR.size == 0
    n = size // PAIR.size
    wanted, counters = positions(n)
    selected = {}
    overall = hashlib.sha256()
    chunk_hashes = []
    previous = None
    bad_order = bad_bound = collisions = 0
    with table.open("rb") as stream:
        for start in range(0, n, CHUNK_PAIRS):
            block = stream.read(min(CHUNK_PAIRS, n-start) * PAIR.size)
            if len(block) != min(CHUNK_PAIRS, n-start) * PAIR.size:
                raise ValueError("short read")
            overall.update(block)
            chunk_hashes.append(hashlib.sha256(block).hexdigest())
            for offset, (x, code) in enumerate(PAIR.iter_unpack(block)):
                index = start + offset
                first = ((code >> 1) % base) >> 1
                order_key = (x, -first, code)
                if previous is not None and order_key < previous:
                    bad_order += 1
                if previous is not None and x == previous[0]:
                    collisions += 1
                previous = order_key
                if x >= p or code >= 2 * base**h:
                    bad_bound += 1
                if index in wanted:
                    selected[index] = (x, code)
    sample_rows = []
    bad_scalar = 0
    for index, (x, code) in sorted(selected.items()):
        digits = []
        v = code >> 1
        for _ in range(h):
            digits.append(v % base)
            v //= base
        valid = not v and digits[0] % 2 == 0
        valid &= all(digits[j]//2 <= digits[j+1]//2 for j in range(h-1))
        point = None
        for d in reversed(digits):
            F = fb[d//2]
            if d & 1:
                F = (F[0], (-F[1]) % p)
            point = add(F, point, p, a)
            if point is None:
                valid = False
                break
        valid &= point is not None and point[0] == x and int(point[1] > p//2) == (code & 1)
        bad_scalar += not valid
        sample_rows.append({"position": index, "x": x, "code": code,
                            "scalar_replay_ok": bool(valid)})
    result = {"status": "pass" if not (bad_order or bad_bound or bad_scalar) else "fail",
              "table_sha256": overall.hexdigest(), "entries": n,
              "payload_bytes": size, "chunk_pairs": CHUNK_PAIRS,
              "chunk_sha256": chunk_hashes, "sample_seed": SEED.decode(),
              "counter_draws": counters, "sample_count": len(selected),
              "bad_order": bad_order, "bad_bound": bad_bound,
              "bad_scalar": bad_scalar, "same_x_extra_entries": collisions,
              "distinct_x": n - collisions,
              "curve": {"p": p, "a": a, "b": b},
              "arity": h, "factor_base_size": len(fb)}
    validation.write_text(json.dumps(result, indent=2) + "\n")
    samples.write_text(json.dumps(sample_rows, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--samples", type=Path, required=True)
    args = parser.parse_args()
    outcome = check(args.table, args.input, args.validation, args.samples)
    print(json.dumps({k: v for k, v in outcome.items() if k != "chunk_sha256"}))
    raise SystemExit(0 if outcome["status"] == "pass" else 1)
