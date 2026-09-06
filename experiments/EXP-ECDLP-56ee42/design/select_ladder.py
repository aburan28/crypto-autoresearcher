"""
Parameter-ladder selector for EXP-ECDLP-56ee42 (design-time, deterministic).

Selects, for each target bit length T in TARGETS, the FIRST (p, a, b) in the
deterministic scan below such that E: y^2 = x^3 + x + b over F_p satisfies:
  - p prime, 2^T <= p < 2^(T+1)
  - nonsingular: 4a^3 + 27b^2 != 0 (mod p)
  - N = #E(F_p) prime  (=> the whole group is a prime-order subgroup, cofactor 1;
    trivially satisfies the smooth-order exclusion of KN-TECH-034 as stated in
    IDEA-20260901-863e36 and IDEA-20260901-b4e6eb)
  - N != p            (anomalous exclusion, same rule)
  - 2^T <= N < 2^(T+1) (ladder cell)
  - j(E) != 1728 (mod p)  (avoid the CM-by-i family; the measurement's
    character sums should not sit on a special family; with a = 1, c4 = 48 != 0,
    so j = 0 is impossible)
Scan: consecutive primes p from 2^T upward; for each p, b = 1, 2, 3, ...; a = 1
fixed (generic model). No randomness: the selection is a pure function of
TARGETS, so no seed is needed and the output is exactly reproducible.

Point counting is vectorised numpy (QR-table method; same method as
experiments/EXP-ISOU-2ac81f/implementation/base_curve_search.py::point_count_with_qr,
which uses the CM model a = -3, replaced here by the generic model a = 1).
The QR table is built once per p (it depends only on p, not on b).
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np
from sympy import isprime

TARGETS = [17, 19, 21, 23, 25, 27]
A = 1
MAX_B_PER_PRIME = 200
MAX_PRIME_STEPS = 64


def next_prime(n: int) -> int:
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not isprime(n):
        n += 2
    return n


def prime_setup(p: int, a: int):
    x0 = np.arange(p, dtype=np.uint64)
    x2m = (x0 * x0) % p
    qr = np.zeros(p, dtype=bool)
    qr[x2m] = True
    return x0, x2m, qr


def point_count(x0, x2m, qr, p: int, a: int, b: int) -> int:
    # f(x) = x^3 + a x + b, evaluated mod p; all products stay < p^2 < 2^64
    # for p < 2^32.
    f = ((x2m * x0) % p + a * x0 + b) % p
    # N = p + 1 + sum_{x: f(x) != 0} chi(f(x)), the ISOU identity, with
    # chi = 2*qr - 1 and the zero set (where chi contributes 0, but
    # 2*qr[0]-1 = +1) subtracted back out: N = 1 + 2*sum qr[f] - z.
    z = int((f == 0).sum())
    return int(1 + 2 * int(qr[f].sum()) - z)


def j_invariant(p: int, a: int, b: int):
    a3 = pow(a, 3, p)
    disc = (4 * a3 + 27 * pow(b, 2, p)) % p
    if disc == 0:
        return None  # singular
    c4 = 48 * a % p
    delta = (-16 * disc) % p
    return (pow(c4, 3, p) * pow(delta, p - 2, p)) % p


def select_for_target(T: int) -> dict:
    p = next_prime(1 << T)
    hi_p = 1 << (T + 1)
    steps = 0
    while p < hi_p and steps < MAX_PRIME_STEPS:
        x0, x2m, qr = prime_setup(p, A)
        for b in range(1, MAX_B_PER_PRIME + 1):
            j = j_invariant(p, A, b)
            if j is None or j == 1728 % p:
                continue
            N = point_count(x0, x2m, qr, p, A, b)
            if not isprime(N):
                continue
            if N == p:
                continue
            if not ((1 << T) <= N < (1 << (T + 1))):
                continue
            return {
                "target_T": T, "p": p, "a": A, "b": b, "N": N,
                "log2_N": round(math.log2(N), 6),
                "j": j, "t": p + 1 - N,
                "checks": {
                    "p_prime": isprime(p),
                    "nonsingular": j_invariant(p, A, b) is not None,
                    "N_prime": isprime(N),
                    "N_not_p": N != p,
                    "in_cell": (1 << T) <= N < (1 << (T + 1)),
                    "not_CM_j_1728": j != 1728 % p,
                    "smooth_N_excluded": "N prime, hence not smooth (KN-TECH-034 rule as stated in 863e36/b4e6eb)",
                },
            }
        del x0, x2m, qr
        p = next_prime(p + 1)
        steps += 1
    raise SystemExit(f"no curve found for target T={T}")


def main() -> None:
    out = []
    for T in TARGETS:
        t0 = time.time()
        row = select_for_target(T)
        row["selection_seconds"] = round(time.time() - t0, 1)
        out.append(row)
        print(f"T={T}: p={row['p']} b={row['b']} N={row['N']} (log2 {row['log2_N']}) "
              f"j={row['j']} t={row['t']}  [{row['selection_seconds']}s]", file=sys.stderr)
    nmin = min(r["N"] for r in out)
    nmax = max(r["N"] for r in out)
    table = {
        "selector": "select_ladder.py (deterministic; no seed; pure function of TARGETS)",
        "model": "y^2 = x^3 + x + b over F_p (a = 1, generic, non-CM)",
        "lift_convention": "canonical integer representative in [0, p)",
        "cell_rule": "first (p,b) in deterministic scan with N prime, N != p, 2^T <= N < 2^(T+1)",
        "span_nmax_over_nmin": round(nmax / nmin, 1),
        "span_ok": nmax / nmin >= 6,
        "curves": out,
    }
    print(json.dumps(table, indent=2))


if __name__ == "__main__":
    main()
