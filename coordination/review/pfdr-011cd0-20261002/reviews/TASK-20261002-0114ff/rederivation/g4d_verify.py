#!/usr/bin/env python3
"""J1 G4-D: the validator's own discrete-log certificate verifier.

TASK-20261002-0114ff. Written from the specification text (certificate
statement {key, p, a, b, N, P, Q, k}; G4-D) without reading verify_solves.py.
Standard library only; shares no code with any producer script. Own prime
test, own affine Weierstrass arithmetic over F_p, own modular inverse
(extended Euclid).

Per record, all must hold:
  C1  p is prime (deterministic Miller-Rabin, bases 2..37, valid for n < 3.3e24)
  C2  4a^3 + 27b^2 != 0 mod p, 0 <= a, b < p
  C3  P and Q are affine points on y^2 = x^3 + a x + b
  C4  N is prime, N in the Hasse interval [p+1-2sqrt(p), p+1+2sqrt(p)], N != p
  C5  N * P = O and P != O (so ord P = N)
  C6  0 <= k < N and k * P = Q  (the certificate)
  C7  the key is an R14 instance: mode census, bits in {20, 26}, curve in 10..13,
      m in {3, 4, 5}, arm one of the 11 search-panel arms
  C8  (p, a, b, N, P) equal design.json's entry for (bits, curve)
Per file: no duplicate key; the set of keys equals the 264-instance universe;
Q and k are identical for all records of one (bits, curve) (target seed 0).
Usage: g4d_verify.py DESIGN_JSON OUT_JSON CERTFILE [CERTFILE ...]
"""
import gzip
import hashlib
import itertools
import json
import math
import sys

ARMS = ["subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
        "known_null_sub", "random_dick_r0", "random_dick_r1", "random_dick_r2", "known_null_dick"]


def is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def inv(x, p):
    a, b, u, v = x % p, p, 1, 0
    while a:
        q = b // a
        a, b, u, v = b - q * a, a, v - q * u, u
    if b != 1:
        raise ZeroDivisionError("not invertible")
    return v % p


def on_curve(Pt, a, b, p):
    if Pt is None:
        return True
    x, y = Pt
    return 0 <= x < p and 0 <= y < p and (y * y - (x * x * x + a * x + b)) % p == 0


def add(P1, P2, a, p):
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def mul(k, Pt, a, p):
    R, A = None, Pt
    if k < 0:
        k, A = -k, (None if Pt is None else (Pt[0], (-Pt[1]) % p))
    while k:
        if k & 1:
            R = add(R, A, a, p)
        A = add(A, A, a, p)
        k >>= 1
    return R


def main():
    design = json.load(open(sys.argv[1]))
    dcurve = {(c["bits"], c["curve"]): c for c in design["curves"]}
    out_path, files = sys.argv[2], sys.argv[3:]
    universe = {(b, c, m, arm, "census") for b in (20, 26) for c in range(10, 14)
                for m in (3, 4, 5) for arm in ARMS}
    report = {"verifier": "rederivation/g4d_verify.py", "files": {}}
    for fp in files:
        raw = open(fp, "rb").read()
        recs = [json.loads(l) for l in gzip.decompress(raw).decode().splitlines() if l.strip()]
        fails, keys, dup = [], [], 0
        per_curve = {}
        for i, r in enumerate(recs):
            kd = r["key"]
            key = (kd["bits"], kd["curve"], kd["m"], kd["arm"], kd["mode"])
            p, a, b, N, k = r["p"], r["a"], r["b"], r["N"], r["k"]
            P = tuple(r["P"]) if r["P"] is not None else None
            Q = tuple(r["Q"]) if r["Q"] is not None else None
            chk = {}
            chk["C1"] = is_prime(p)
            chk["C2"] = 0 <= a < p and 0 <= b < p and (4 * a ** 3 + 27 * b * b) % p != 0
            chk["C3"] = P is not None and Q is not None and on_curve(P, a, b, p) and on_curve(Q, a, b, p)
            s = math.isqrt(p)
            chk["C4"] = is_prime(N) and (p + 1 - 2 * s - 2) <= N <= (p + 1 + 2 * s + 2) and N != p
            chk["C5"] = chk["C3"] and mul(N, P, a, p) is None
            chk["C6"] = chk["C3"] and 0 <= k < N and mul(k, P, a, p) == Q
            chk["C7"] = key in universe
            dc = dcurve.get((key[0], key[1]))
            chk["C8"] = dc is not None and (dc["p"], dc["a"], dc["b"], dc["N"], tuple(dc["P"])) == (p, a, b, N, P)
            if key in keys:
                dup += 1
            keys.append(key)
            per_curve.setdefault((key[0], key[1]), set()).add((Q, k))
            bad = [c for c, v in chk.items() if not v]
            if bad:
                fails.append({"index": i, "key": list(key), "failed": bad})
        kset = set(keys)
        report["files"][fp] = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "records": len(recs),
            "records_passing_all_checks": len(recs) - len(fails),
            "failures": fails,
            "duplicate_keys": dup,
            "missing_universe_keys": sorted(map(list, universe - kset)),
            "keys_outside_universe": sorted(map(list, kset - universe)),
            "curves_with_inconsistent_target": sorted([list(c) for c, v in per_curve.items() if len(v) != 1]),
            "pass": (not fails and dup == 0 and kset == universe and len(recs) == len(universe)
                     and all(len(v) == 1 for v in per_curve.values())),
        }
    report["pass"] = all(f["pass"] for f in report["files"].values())
    json.dump(report, open(out_path, "w"), indent=1, sort_keys=True)
    print(json.dumps({fp: {k: v for k, v in f.items() if k in ("records", "records_passing_all_checks", "pass")}
                      for fp, f in report["files"].items()}))


if __name__ == "__main__":
    main()
