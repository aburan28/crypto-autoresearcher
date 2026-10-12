"""Create exact n-1 primality and two-isogeny descent certificates.

Generation uses deterministic seeded factor searches and probable-prime routing.
Acceptance uses only the recursive Lucas n-1 criterion and exact identities.
"""

import collections
import json
import math
import platform
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 20261007
RNG = random.Random(SEED)
DEADLINE = time.monotonic() + 300
FACTORIZATION_LOG = []
NODES = {}
BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)


def probable_prime(n):
    if n < 2:
        return False
    for a in BASES:
        if n == a:
            return True
        if n % a == 0:
            return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def check_budget():
    if time.monotonic() > DEADLINE:
        raise TimeoutError("300 second generation budget exhausted")


def rho(n):
    if n % 2 == 0:
        return 2
    for attempt in range(100):
        check_budget()
        y, c = RNG.randrange(1, n), RNG.randrange(1, n)
        start_y, start_c = y, c
        batch, g, r, steps = 128, 1, 1, 0
        while g == 1:
            check_budget()
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                product = 1
                for _ in range(min(batch, r - k)):
                    y = (y * y + c) % n
                    product = product * abs(x - y) % n
                    steps += 1
                g = math.gcd(product, n)
                k += batch
            r *= 2
        if g == n:
            g = 1
            while g == 1:
                check_budget()
                ys = (ys * ys + c) % n
                g = math.gcd(abs(x - ys), n)
                steps += 1
        FACTORIZATION_LOG.append({"n": n, "attempt": attempt,
                                  "start_y": start_y, "c": start_c,
                                  "steps": steps, "gcd": g})
        if 1 < g < n:
            return g
    raise RuntimeError("rho retry budget exhausted")


def factor(n):
    parts = []
    for p in range(2, 1000):
        while n % p == 0:
            parts.append(p)
            n //= p
    def split(k):
        check_budget()
        if k == 1:
            return
        if probable_prime(k):
            parts.append(k)
            return
        d = rho(k)
        split(d)
        split(k // d)
    split(n)
    return collections.Counter(parts)


def certify(n):
    key = str(n)
    if key in NODES:
        return
    if n == 2:
        NODES[key] = {"n": 2, "method": "base_case"}
        return
    if n < 2 or not probable_prime(n):
        raise ValueError(f"not a probable prime: {n}")
    factors = factor(n - 1)
    witnesses = {}
    for q in sorted(factors):
        certify(q)
        for a in range(2, 10000):
            if pow(a, n - 1, n) == 1 and math.gcd(pow(a, (n - 1) // q, n) - 1, n) == 1:
                witnesses[str(q)] = a
                break
        else:
            raise ValueError(f"no Lucas witness for n={n}, q={q}")
    NODES[key] = {"n": n, "method": "lucas_full_n_minus_1",
                  "factors": {str(q): e for q, e in sorted(factors.items())},
                  "witnesses": witnesses}


def main():
    started = time.monotonic()
    data = json.loads((ROOT / "cheon_example_audit.json").read_text())
    out = {"python": platform.python_version(), "seed": SEED,
           "generation_budget_seconds": 300, "candidates": [], "failures": []}
    try:
        for d in data["passes"]:
            a, b = d["a"], d["b"]
            r, f1, f2 = abs(b), d["factors"][1], d["factors"][2]
            for value in (r, f1, f2):
                certify(value)
            s, t = 703, 439
            yp, yq = d["point_y"]
            D = a * a - 4 * b
            u = a + 2 * s * s - 2 * yp // s
            v = -2 * s * u
            out["candidates"].append({
                "n": d["n"], "a": a, "b": b, "D": D,
                "prime_roots": [r, f1, f2],
                "P": [s * s, yp], "Q": [-t * t, yq],
                "T": [0, 0], "Eprime_a": -2 * a, "Eprime_b": D,
                "R": [u, v], "Tprime": [0, 0],
                "alpha_generators": [-1, b],
                "alpha_prime_generators": [u, D],
                "claimed_rank": 2,
                "claimed_P_Q_independent": True,
            })
    except Exception as exc:
        out["failures"].append({"type": type(exc).__name__, "message": str(exc)})
    out["prime_nodes"] = NODES
    out["factorization_log"] = FACTORIZATION_LOG
    out["generation_elapsed_seconds"] = time.monotonic() - started
    (ROOT / "candidate_certificates.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"candidate_count": len(out["candidates"]),
                      "prime_node_count": len(NODES), "failures": out["failures"],
                      "elapsed_seconds": out["generation_elapsed_seconds"]}, indent=2))
    if out["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
