#!/usr/bin/env python3
"""Independent group-law check of a candidate whose order GP reported prime."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def root(a: int, p: int) -> int | None:
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    c, x, t, m = pow(z, q, p), pow(a, (q + 1) // 2, p), pow(a, q, p), s
    while t != 1:
        i, v = 1, t * t % p
        while v != 1:
            v = v * v % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        x, t, c, m = x * b % p, t * b * b % p, b * b % p, i
    assert x * x % p == a
    return x


def add(P: tuple[int, int] | None, Q: tuple[int, int] | None, p: int, a: int = -3):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = ((3 * x1 * x1 + a) * pow(2 * y1, -1, p)) % p
    else:
        lam = ((y2 - y1) * pow((x2 - x1) % p, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    return x3, (lam * (x1 - x3) - y1) % p


def mul(k: int, P: tuple[int, int], p: int):
    R = None
    while k:
        if k & 1:
            R = add(R, P, p)
        P = add(P, P, p)
        k >>= 1
    return R


def verify(run: Path, timestamp: int, ordinal: int) -> dict:
    manifest = json.loads((run / "prepare_manifest.json").read_text())
    row = next(s for s in manifest["streams"] if s["timestamp"] == timestamp)
    p = int(row["p"], 16)
    meta = next(json.loads(line) for line in (run / f"metadata_{timestamp}.jsonl").read_text().splitlines() if json.loads(line)["ordinal"] == ordinal)
    nline = next(line for line in (run / f"orders_{timestamp}.txt").read_text().splitlines() if line.startswith(f"{ordinal} "))
    _, n, nt = map(int, nline.split())
    assert n > 0 and nt == 2 * p + 2 - n
    b2 = int(meta["b2"], 16)
    b = int(meta["b0"], 16) or root(b2, p)
    assert b is not None and b * b % p == b2
    assert (int(meta["c"], 16) * b * b + 27) % p == 0
    assert (4 * (-3) ** 3 + 27 * b * b) % p != 0
    primality = subprocess.run(["gp", "-q", "-f"], input=f"print(isprime({n}));\nquit;\n", text=True, capture_output=True, check=True)
    assert primality.stdout.strip() == "1"
    x = 0
    while True:
        y = root((x * x * x - 3 * x + b) % p, p)
        if y is not None:
            break
        x += 1
    P = (x, y)
    assert y * y % p == (x * x * x - 3 * x + b) % p
    assert mul(n, P, p) is None
    bound = 2 * __import__("math").isqrt(p) + 2
    assert abs(n - (p + 1)) <= bound
    assert n > 2 * bound
    return {"timestamp": timestamp, "ordinal": ordinal, "seed": meta["seed"], "p": hex(p), "a": "-3", "b": hex(b), "n": hex(n), "twist_n": hex(nt), "trace": p + 1 - n, "deterministic_point": [hex(x), hex(y)], "n_times_point_is_identity": True, "n_is_prime_gp": True, "hasse_uniqueness": True, "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "orders_sha256": hashlib.sha256((run / f"orders_{timestamp}.txt").read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("timestamp", type=int)
    parser.add_argument("ordinal", type=int)
    args = parser.parse_args()
    result = verify(args.run, args.timestamp, args.ordinal)
    out = args.run / f"verify_{args.timestamp}_{args.ordinal}.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
