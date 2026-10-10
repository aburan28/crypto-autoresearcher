#!/usr/bin/env sage
"""Deterministic EXP-ICEX-153c34 frozen-L panel generator.

This file is intentionally a Sage script because the approved generation rule
uses Sage's exact elliptic-curve order and primality routines.  It writes only
JSON to stdout; the S0 driver captures that byte stream and independently
re-runs this file for G0-1.  No protocol-labelled draw is used by the S0
smoke runner.
"""

import argparse
import hashlib
import json
import sys

from sage.all import EllipticCurve, GF, Integer, is_prime, next_prime


NAMESPACE = "EXP-ICEX-153c34/v1"
P_WINDOWS = {
    16: (32769, 59049),
    18: (161052, 248832),
    20: (537825, 759375),
    22: (2476100, 3200000),
    24: (9765626, 11881376),
}
B_STARS = {16: 9, 18: 12, 20: 15, 22: 20, 24: 26}
L_STARS = {16: 5, 18: 6, 20: 8, 22: 10, 24: 13}


def digest(label):
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def admissible(p, a, b):
    if a % p in (0,):
        return None, "j in {0,1728}"
    if (4 * a**3 + 27 * b**2) % p == 0:
        return None, "singular"
    E = EllipticCurve(GF(p), [a, b])
    N = Integer(E.order())
    if not is_prime(N):
        return N, "order not prime"
    if N == p:
        return N, "anomalous"
    if N == p + 1:
        return N, "supersingular"
    for k in range(1, 21):
        if pow(p, k, N) == 1:
            return N, "embedding degree %d" % k
    return N, None


def liftable(p, a, b, x):
    r = (x**3 + a * x + b) % p
    return r != 0 and pow(r, (p - 1) // 2, p) == 1


def base_point(p, a, b):
    F = GF(p)
    for x in range(p):
        r = F(x) ** 3 + F(a) * F(x) + F(b)
        if r.is_square():
            y = int(r.sqrt())
            return [x, min(y, p - y)]
    raise RuntimeError("no affine base point")


def make_fixture(bits, seed):
    B = B_STARS[bits]
    L = L_STARS[bits]
    lo, hi = P_WINDOWS[bits]
    rejected = []
    for counter in range(1_000_000):
        x = digest("%s|curve|%d|%d|%d" % (NAMESPACE, bits, seed, counter))
        p = int(next_prime(Integer(2 ** (bits - 1) + (x % 2 ** (bits - 1)))))
        if p.bit_length() != bits:
            rejected.append({"counter": counter, "reason": "wrong bit length", "p": p})
            continue
        if not (lo <= p <= hi):
            rejected.append({"counter": counter, "reason": "outside p window", "p": p})
            continue
        a = (x >> 64) % p
        b = (x >> 128) % p
        N, why = admissible(p, a, b)
        if why is not None:
            rejected.append({"counter": counter, "reason": why, "p": p})
            continue
        actual_L = sum(1 for xx in range(B) if liftable(p, a, b, xx))
        if actual_L != L:
            rejected.append({"counter": counter, "reason": "L=%d (wanted %d)" % (actual_L, L), "p": p})
            continue
        return {
            "bits": bits, "seed": seed, "counter": counter, "p": p,
            "a": int(a), "b": int(b), "N": int(N), "B_star": B,
            "L_star": L, "G": base_point(p, a, b),
            "rejected_counters": rejected,
        }
    raise RuntimeError("panel fixture search exhausted for %s/%s" % (bits, seed))


def generate():
    return {
        "experiment_id": "EXP-ICEX-153c34",
        "namespace": NAMESPACE,
        "generation_rule": "specification.yaml panel_fixtures.generation_rule",
        "panel": [make_fixture(bits, seed) for bits in (16, 18, 20, 22, 24)
                   for seed in (1, 2, 3, 4)],
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="kept for explicit invocation")
    args = ap.parse_args()
    json.dump(generate(), sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")
