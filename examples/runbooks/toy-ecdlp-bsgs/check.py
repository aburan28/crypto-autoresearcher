#!/usr/bin/env python3
"""Independent checker for one toy-ECDLP trial directory.

Written separately from solve.py and sharing no code with it: projective
(x:y:z) arithmetic instead of affine, Fermat inversion instead of pow(-1).
It re-derives the instance from the prescribed arguments, so an output that
solved a different instance, used different parameters, or counted
operations a prescribed BSGS could not have taken fails here.

    check.py <run_dir> <curve.json> <mode> <seed-or-k-or-none>

Exit 0 when every check holds; 1 with one line per failed check otherwise.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys


class Curve:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a, b

    def inv(self, x):
        return pow(x, self.p - 2, self.p)

    def to_affine(self, P):
        x, y, z = P
        if z % self.p == 0:
            return None
        zi = self.inv(z)
        return (x * zi % self.p, y * zi % self.p)

    def double(self, P):
        x, y, z = P
        p, a = self.p, self.a
        if z % p == 0 or y % p == 0:
            return (0, 1, 0)
        w = (a * z * z + 3 * x * x) % p
        s = y * z % p
        bb = x * y * s % p
        h = (w * w - 8 * bb) % p
        x3 = 2 * h * s % p
        y3 = (w * (4 * bb - h) - 8 * y * y * s * s) % p
        z3 = 8 * s * s * s % p
        return (x3, y3, z3)

    def add(self, P, Q):
        p = self.p
        if P[2] % p == 0:
            return Q
        if Q[2] % p == 0:
            return P
        x1, y1, z1 = P
        x2, y2, z2 = Q
        u1, u2 = y2 * z1 % p, y1 * z2 % p
        v1, v2 = x2 * z1 % p, x1 * z2 % p
        if v1 == v2:
            return self.double(P) if u1 == u2 else (0, 1, 0)
        u, v, w = (u1 - u2) % p, (v1 - v2) % p, z1 * z2 % p
        a = (u * u * w - v ** 3 - 2 * v * v * v2) % p
        return (v * a % p, (u * (v * v * v2 - a) - v ** 3 * u2) % p, v ** 3 * w % p)

    def scalar(self, k, P):
        R = (0, 1, 0)
        for bit in bin(k)[2:]:
            R = self.double(R)
            if bit == "1":
                R = self.add(R, P)
        return R

    def contains(self, xy):
        x, y = xy
        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0


def main(argv: list[str]) -> int:
    run_dir, curve_path, mode, value = Path(argv[1]), Path(argv[2]), argv[3], argv[4]
    curve = json.loads(curve_path.read_text())
    result = json.loads((run_dir / "raw-result.json").read_text())
    E = Curve(curve["p"], curve["a"], curve["b"])
    n, G = curve["n"], (curve["G"][0], curve["G"][1], 1)
    failures = []

    def need(condition, message):
        if not condition:
            failures.append(message)

    need(E.contains(curve["G"]), "G is not on the curve")
    need(E.scalar(n, G)[2] % E.p == 0, "n*G is not the identity")
    need(result.get("curve") == {k: curve[k] for k in ("p", "a", "b", "n", "G")}, "curve parameters differ")
    need(result.get("mode") == mode, f"mode is {result.get('mode')!r}, prescribed {mode!r}")
    if mode == "search":
        seed = int(value)
        need(result.get("seed") == seed, f"seed is {result.get('seed')!r}, prescribed {seed}")
        k = 1 + int(hashlib.sha256(f"toy-ecdlp-bsgs/k/{seed}".encode()).hexdigest()[:16], 16) % (n - 1)
        expected_q = E.to_affine(E.scalar(k, G))
    elif mode == "known-k":
        k = int(value)
        need(result.get("k_input") == k, f"k_input is {result.get('k_input')!r}, prescribed {k}")
        expected_q = E.to_affine(E.scalar(k, G))
    else:
        k, expected_q = None, (curve["G"][0], (curve["G"][1] + 1) % E.p)
    need(result.get("Q") == list(expected_q), "Q is not the prescribed instance")
    if mode == "off-curve":
        need(not E.contains(expected_q), "the off-curve control point is on the curve")
        need(result.get("status") == "rejected_input", "the off-curve instance was not rejected")
        need(result.get("k_found") is None and result.get("verified") is False,
             "a logarithm was reported for an off-curve point")
    else:
        m = math.isqrt(n - 1) + 1
        found = result.get("k_found")
        need(result.get("status") == "solved" and isinstance(found, int) and 0 <= found < n,
             "no logarithm in [0, n) was reported")
        if isinstance(found, int):
            need(E.to_affine(E.scalar(found, G)) == tuple(result["Q"]), "k_found * G != Q")
            need(found == k, "k_found is not the prescribed logarithm")
            # The prescribed algorithm's own count for this k: a solver that
            # reached the answer another way cannot match it by accident.
            need(result.get("m") == m and result.get("baby_steps") == m, "baby-step table size is not m")
            need(result.get("giant_steps") == found // m + 1, "giant steps differ from BSGS for this k")
        need(result.get("group_ops") == result.get("baby_steps", 0) + result.get("giant_steps", 0),
             "group_ops != baby_steps + giant_steps")
        need(result.get("verified") is True, "the solver did not verify its own answer")
    need((run_dir / "manifest.yaml").is_file(), "manifest.yaml is missing")
    for line in failures:
        print(f"CHECK FAILED: {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
