"""Stage 3 curve search run for EXP-ECDLP-612fb1.

p = largest prime below 2^24 with p = 3 mod 4; (a, b) drawn from the
curve-search stream (seed 1000) in [1, 1000] until #E is prime.  The point
count is by Euler's criterion over every x (curve.count_points); the record
is then verified INDEPENDENTLY by verify_certificate.verify_curve_record
([N]R = O on the generator and 20 random points, Hasse, primality).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curve as C  # noqa: E402
import verify_certificate as V  # noqa: E402

CURVE_SEARCH_SEED = 1000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    t0 = time.time()
    p = (1 << 24) - 1
    while not (p % 4 == 3 and C.is_probable_prime(p)):
        p -= 1
    print(f"[search] p = {p} (largest prime = 3 mod 4 below 2^24)", flush=True)
    rng = np.random.default_rng(CURVE_SEARCH_SEED)
    tried = []
    found = None
    while found is None:
        a = int(rng.integers(1, 1001))
        b = int(rng.integers(1, 1001))
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            tried.append({"a": a, "b": b, "N": None, "note": "singular"})
            continue
        ts = time.time()
        N = C.count_points(p, a, b)
        prime = C.is_probable_prime(N)
        tried.append({"a": a, "b": b, "N": N, "N_prime": prime, "seconds": round(time.time() - ts, 2)})
        print(f"[candidate] a={a} b={b} #E={N} prime={prime} ({time.time() - ts:.1f}s)", flush=True)
        if prime:
            found = (a, b, N)
    a, b, N = found
    # generator: smallest x with a point (any point has order N since N is prime)
    x = 0
    while True:
        rhs = (x * x * x + a * x + b) % p
        if rhs != 0 and pow(rhs, (p - 1) // 2, p) == 1:
            y = pow(rhs, (p + 1) // 4, p)
            break
        x += 1
    G = (x, y)
    curve_id = "TOY-P24-" + hashlib.sha256(f"{p},{a},{b},{N},{G[0]},{G[1]}".encode()).hexdigest()[:12]
    rec = {"curve_id": curve_id, "p": p, "a": a, "b": b, "N": N, "P": [G[0], G[1]],
           "field_bits": p.bit_length(), "equation": "y^2 = x^3 + a x + b over F_p",
           "search_seed": CURVE_SEARCH_SEED, "candidates_tried": len(tried),
           "point_counting_method": "Euler criterion over every x in F_p (curve.count_points), vectorised"}
    ver = V.verify_curve_record(rec)
    rec["verification"] = ver
    print(f"[curve] {json.dumps(rec)}", flush=True)
    with open(os.path.join(args.outdir, "curve_record.json"), "w") as fh:
        json.dump(rec, fh, indent=1)
    with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
        json.dump({"p": p, "candidates": tried, "curve": rec}, fh, indent=1)
    with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
        json.dump({"params": {"kind": "curve-search", "seeds": {"curve_search_seed": CURVE_SEARCH_SEED},
                              "p": p, "field_bits": p.bit_length()},
                   "curve": rec, "verified": ver["verified"], "certificate": {"kind": "none"},
                   "headline_metrics": {"N": N, "candidates_tried": len(tried)},
                   "elapsed_seconds": time.time() - t0}, fh, indent=1)
    print(f"[done] verified={ver['verified']} {time.time() - t0:.1f}s")
    return 0 if ver["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
