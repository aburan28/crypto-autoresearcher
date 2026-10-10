#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-2535ec run artifacts. Reads only.

Shares no code with run.py. With its own primality test, its own sieve and
its own trial division it (a) re-verifies every cell's primes and the root
condition f_arm(m_arm) = p for all three arms; (b) REPLAYS the smallest
scored box of one seeded-chosen cell in full, recounting the doubly smooth
pairs of all three arms from the recorded polynomials, bases and bounds, and
requires exact agreement with the recorded counts; (c) recomputes every yield
ratio and category-sum identity. A raw result whose counts were not produced
by the stated enumeration fails (b). Exit 0 iff no problem.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

EXP = "EXP-ECDLP-2535ec"
ARMS = ("special", "null_same_prime", "null_random_prime")


def is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41):
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


def primes_upto(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(n + 1) if sieve[i]]


def smooth(n, primes, bound):
    n = abs(n)
    if n == 0:
        return False
    for q in primes:
        while n % q == 0:
            n //= q
        if n == 1:
            return True
        if q * q > n:
            return n <= bound
    return n == 1


def horner(coeffs, x):
    v = 0
    for c in reversed(coeffs):
        v = v * x + c
    return v


def norm(coeffs, a, b):
    d = len(coeffs) - 1
    return sum(f * a ** i * b ** (d - i) for i, f in enumerate(coeffs))


def replay_box(arms, A, Bs):
    primes = primes_upto(Bs)
    counts = {k: 0 for k in ARMS}
    pairs = 0
    for b in range(1, A + 1):
        for a in range(-A, A + 1):
            if math.gcd(a, b) != 1:
                continue
            pairs += 1
            for k in ARMS:
                arm = arms[k]
                rat, alg = a + b * arm["m"], norm(arm["f"], a, b)
                if rat and alg and smooth(rat, primes, Bs) and smooth(alg, primes, Bs):
                    counts[k] += 1
    return pairs, counts


def main(argv):
    if len(argv) != 1:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(argv[0])
    errs = []
    try:
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        manifest = (run_dir / "manifest.yaml").read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"unreadable artifacts: {error}", file=sys.stderr)
        return 1
    if raw.get("experiment_id") != EXP or EXP not in manifest:
        errs.append("wrong experiment id")
    cells = raw.get("cells") or []
    if not cells:
        errs.append("no cells")
    for cell in cells:
        tag = f"d={cell.get('d')} bits={cell.get('bits')} seed={cell.get('seed')}"
        arms = cell.get("arms") or {}
        for k in ARMS:
            arm = arms.get(k) or {}
            if not is_prime(arm.get("p", 0)):
                errs.append(f"{tag} {k}: p is not prime")
            if horner(arm.get("f", []), arm.get("m", 0)) != arm.get("p"):
                errs.append(f"{tag} {k}: f(m) != p")
            if len(arm.get("f", [])) - 1 != cell.get("d") or arm["f"][-1] != 1:
                errs.append(f"{tag} {k}: polynomial degree or leading coefficient wrong")
        if arms.get("special", {}).get("f", [None])[0] != -cell.get("c"):
            errs.append(f"{tag}: special polynomial constant term != -c")
        for res in cell.get("results") or []:
            if res.get("ctrl_same_box") is not True:
                errs.append(f"{tag}: CTRL-SAME-BOX not true")
            counts = res.get("counted_doubly_smooth_pairs") or {}
            for key, other in (("special_vs_null_same_prime", "null_same_prime"),
                               ("special_vs_null_random_prime", "null_random_prime")):
                r = (res.get("yield_ratio") or {}).get(key) or {}
                u = counts.get(other)
                expected = None if not u else counts.get("special", 0) / u
                if r.get("ratio") != expected:
                    errs.append(f"{tag} {key}: ratio {r.get('ratio')} != {expected}")
                cats = r.get("categories") or {}
                if cats and sum(cats.values()) != res.get("coprime_pairs"):
                    errs.append(f"{tag} {key}: category counts do not sum to the coprime pair count")
                if cats and cats.get("both", 0) + cats.get("special_only", 0) != counts.get("special"):
                    errs.append(f"{tag} {key}: categories disagree with the special count")
    # full replay of the smallest box of one seeded cell
    replayed = None
    if cells:
        rng = random.Random("EXP-ECDLP-2535ec:check")
        cell = rng.choice(cells)
        res = min(cell["results"], key=lambda r: (r["A"], r["B_s"]))
        pairs, counts = replay_box(cell["arms"], res["A"], res["B_s"])
        replayed = f"d={cell['d']} bits={cell['bits']} seed={cell['seed']} A={res['A']} B_s={res['B_s']}"
        if pairs != res["coprime_pairs"]:
            errs.append(f"replay {replayed}: coprime pair count {pairs} != recorded {res['coprime_pairs']}")
        if counts != res["counted_doubly_smooth_pairs"]:
            errs.append(f"replay {replayed}: recounted {counts} != recorded {res['counted_doubly_smooth_pairs']}")
    for e in errs:
        print("FAIL:", e, file=sys.stderr)
    print(f"{EXP} check: {len(cells)} cell(s), replayed box [{replayed}], {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
