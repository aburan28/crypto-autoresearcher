"""
Parameter-ladder selector for EXP-ECDLP-df601f (design-time, deterministic).

Selects, for each target bit length T in TARGETS, the FIRST CURVES_PER_T
distinct (p, a, b) triples in the deterministic scan below such that
E: y^2 = x^3 + x + b over F_p satisfies:
  - p prime, 2^T <= p < 2^(T+1)
  - nonsingular: 4a^3 + 27b^2 != 0 (mod p)
  - N = #E(F_p) prime  (cofactor 1; KN-TECH-034 smooth-order exclusion)
  - N != p            (anomalous exclusion)
  - 2^T <= N < 2^(T+1)
  - j(E) != 0 and j(E) != 1728 (mod p)
  - distinct N across the four curves of one T-cell (no isogenous repeats)

Scan: consecutive primes p from 2^T upward; for each p, b = 1, 2, 3, ...;
a = 1 fixed. No randomness: a pure function of TARGETS and CURVES_PER_T.

Point counting is the QR-table method of
experiments/EXP-ECDLP-56ee42/design/select_ladder.py (same identity, same
a = 1 model). The first curve of each overlapping T in
{17, 19, 21, 23, 25, 27} is therefore the 56ee42 curve, which is a
deliberate baseline-embedding fixture, not a reuse of that experiment's
statistic.
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np
from sympy import isprime

TARGETS = [17, 18, 19, 21, 23, 24, 25, 27]
CURVES_PER_T = 4
A = 1
MAX_B_PER_PRIME = 400
MAX_PRIME_STEPS = 96


def next_prime(n: int) -> int:
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not isprime(n):
        n += 2
    return n


def prime_setup(p: int):
    x0 = np.arange(p, dtype=np.uint64)
    x2m = (x0 * x0) % p
    qr = np.zeros(p, dtype=bool)
    qr[x2m] = True
    return x0, x2m, qr


def point_count(x0, x2m, qr, p: int, a: int, b: int) -> int:
    f = ((x2m * x0) % p + a * x0 + b) % p
    z = int((f == 0).sum())
    return int(1 + 2 * int(qr[f].sum()) - z)


def j_invariant(p: int, a: int, b: int):
    a3 = pow(a, 3, p)
    disc = (4 * a3 + 27 * pow(b, 2, p)) % p
    if disc == 0:
        return None
    c4 = (48 * a) % p
    delta = (-16 * disc) % p
    return (pow(c4, 3, p) * pow(delta, p - 2, p)) % p


def select_for_target(T: int) -> list[dict]:
    p = next_prime(1 << T)
    hi_p = 1 << (T + 1)
    steps = 0
    found: list[dict] = []
    seen_N: set[int] = set()
    while p < hi_p and steps < MAX_PRIME_STEPS and len(found) < CURVES_PER_T:
        x0, x2m, qr = prime_setup(p)
        for b in range(1, MAX_B_PER_PRIME + 1):
            if len(found) >= CURVES_PER_T:
                break
            j = j_invariant(p, A, b)
            if j is None or j == (1728 % p) or j == 0:
                continue
            N = point_count(x0, x2m, qr, p, A, b)
            if N in seen_N:
                continue
            if not isprime(N):
                continue
            if N == p:
                continue
            if not ((1 << T) <= N < (1 << (T + 1))):
                continue
            seen_N.add(N)
            found.append(
                {
                    "target_T": T,
                    "curve_index": len(found),
                    "p": int(p),
                    "a": A,
                    "b": int(b),
                    "N": int(N),
                    "log2_N": round(math.log2(N), 6),
                    "j": int(j),
                    "t": int(p + 1 - N),
                    "checks": {
                        "p_prime": bool(isprime(p)),
                        "nonsingular": True,
                        "N_prime": True,
                        "N_not_p": True,
                        "in_cell": True,
                        "not_CM_j_0": True,
                        "not_CM_j_1728": True,
                        "smooth_N_excluded": (
                            "N prime, hence not smooth "
                            "(KN-TECH-034 rule as stated in 863e36/b4e6eb)"
                        ),
                        "distinct_N_in_cell": True,
                    },
                }
            )
        del x0, x2m, qr
        p = next_prime(p + 1)
        steps += 1
    if len(found) < CURVES_PER_T:
        raise SystemExit(
            f"only {len(found)}/{CURVES_PER_T} curves found for target T={T}"
        )
    return found


def main() -> None:
    out = []
    for T in TARGETS:
        t0 = time.time()
        rows = select_for_target(T)
        elapsed = round(time.time() - t0, 1)
        for row in rows:
            row["selection_seconds_cell"] = elapsed
            out.append(row)
            print(
                f"T={T}[{row['curve_index']}]: p={row['p']} b={row['b']} "
                f"N={row['N']} (log2 {row['log2_N']}) j={row['j']} t={row['t']}",
                file=sys.stderr,
            )
        print(f"T={T} cell done in {elapsed}s", file=sys.stderr)
    nmin = min(r["N"] for r in out)
    nmax = max(r["N"] for r in out)
    table = {
        "selector": (
            "select_ladder.py (deterministic; no seed; pure function of "
            "TARGETS and CURVES_PER_T)"
        ),
        "model": "y^2 = x^3 + x + b over F_p (a = 1, generic, non-CM)",
        "lift_convention": "canonical integer representative in [0, p)",
        "cell_rule": (
            f"first {CURVES_PER_T} (p,b) in deterministic scan with N prime, "
            "N != p, distinct N, 2^T <= N < 2^(T+1), j not in {0, 1728}"
        ),
        "targets": TARGETS,
        "curves_per_T": CURVES_PER_T,
        "span_nmax_over_nmin": round(nmax / nmin, 1),
        "span_ok": nmax / nmin >= 1000,
        "n_min": nmin,
        "n_max": nmax,
        "curves": out,
    }
    print(json.dumps(table, indent=2))


if __name__ == "__main__":
    main()
