#!/usr/bin/env python3
"""Independent, label-free F-2/P-5 re-derivation for TASK-20261001-8615ec.

The implementation deliberately contains no protocol draw machinery.  It
derives the F-2 curve fixtures from the frozen SHA-256 rule, obtains #E(F_p)
with PARI/GP, and computes the label-free P-5 scan counts for F-1 and F-2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


F1 = [
    {"id": "b16-s11", "bits": 16, "seed": 11, "p": 62417, "a": 31838, "b": 5672, "N": 61979, "G": [0, 27690]},
    {"id": "b16-s12", "bits": 16, "seed": 12, "p": 49391, "a": 17959, "b": 16189, "N": 49367, "G": [6, 24294]},
    {"id": "b16-s13", "bits": 16, "seed": 13, "p": 39607, "a": 28493, "b": 1765, "N": 39581, "G": [0, 15550]},
    {"id": "b20-s11", "bits": 20, "seed": 11, "p": 855727, "a": 220250, "b": 149669, "N": 856153, "G": [3, 354997]},
    {"id": "b20-s12", "bits": 20, "seed": 12, "p": 855641, "a": 287740, "b": 209027, "N": 854363, "G": [0, 248685]},
    {"id": "b20-s13", "bits": 20, "seed": 13, "p": 911707, "a": 786752, "b": 903968, "N": 911033, "G": [2, 189920]},
    {"id": "b24-s11", "bits": 24, "seed": 11, "p": 9769087, "a": 1694034, "b": 548449, "N": 9773123, "G": [0, 3916788]},
    {"id": "b24-s12", "bits": 24, "seed": 12, "p": 15738469, "a": 11997084, "b": 5182456, "N": 15735007, "G": [4, 7793897]},
    {"id": "b24-s13", "bits": 24, "seed": 13, "p": 10589077, "a": 4368383, "b": 1627642, "N": 10593239, "G": [1, 4615285]},
]

F1_EXPECTED = {
    "b16-s11": [10, 83, 10, 6, 38, 88, 72, 904, 2750, 166, 331, 662, 1324],
    "b16-s12": [9, 76, 9, 2, 33, 70, 8, 264, 2106, 178, 355, 709, 1417],
    "b16-s13": [9, 70, 9, 6, 29, 70, 72, 694, 1618, 129, 257, 514, 1028],
    "b20-s11": [16, 237, 16, 6, 103, 218, 72, 2464, 20860, 955, 1909, 3818, 7636],
    "b20-s12": [16, 237, 16, 7, 106, 226, 98, 2964, 22148, 911, 1821, 3641, 7281],
    "b20-s13": [16, 243, 16, 10, 115, 250, 200, 4580, 26008, 864, 1728, 3455, 6910],
    "b24-s11": [26, 626, 26, 14, 320, 668, 392, 17904, 202432, 3560, 7120, 14239, 28477],
    "b24-s12": [28, 757, 28, 12, 348, 720, 288, 16684, 240076, 5347, 10694, 21388, 42776],
    "b24-s13": [26, 646, 26, 10, 337, 694, 200, 13472, 224422, 3763, 7526, 15051, 30102],
}

KAPPAS = (("1/4", Fraction(1, 4)), ("1/2", Fraction(1, 2)), ("1", Fraction(1)), ("2", Fraction(2)))


def ceil_root(n: int, degree: int) -> int:
    lo, hi = 0, 1
    while hi**degree < n:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**degree >= n:
            hi = mid
        else:
            lo = mid
    return hi


def sha256_int(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest(), "big")


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def pari_card(p: int, a: int, b: int) -> int:
    if shutil.which("gp") is None:
        raise RuntimeError("PARI/GP executable gp was not found")
    expr = f"ellcard(ellinit([{a},{b}],{p}))"
    proc = subprocess.run(["gp", "-q"], input=expr + "\n", text=True, capture_output=True, check=True)
    values = []
    clean = re.sub(r"\x1b\[[0-9;]*m", "", proc.stdout)
    for line in clean.splitlines():
        token = line.strip()
        if token.isdigit():
            values.append(int(token))
    if not values:
        raise RuntimeError(f"could not parse PARI output for p={p}, a={a}, b={b}: {proc.stdout!r}")
    return values[-1]


def derive_f2(seed: int) -> dict:
    for c in range(1_000_000):
        x = sha256_int(f"EXP-RELN-dc761f/v1|curve|28|{seed}|{c}")
        p = next_prime(2**27 + (x % 2**27))
        if p.bit_length() != 28:
            continue
        a = (x >> 64) % p
        b = (x >> 128) % p
        if a == 0 or b == 0 or (4 * a**3 + 27 * b**2) % p == 0:
            continue
        N = pari_card(p, a, b)
        if not is_prime(N) or N in (p, p + 1):
            continue
        if any(pow(p, k, N) == 1 for k in range(1, 21)):
            continue
        x0, y0 = first_point(p, a, b)
        return {"id": f"b28-s{seed}", "bits": 28, "seed": seed, "counter": c, "p": p, "a": a, "b": b, "N": N, "G": [x0, min(y0, p - y0)]}
    raise RuntimeError(f"no admissible F-2 fixture found for seed {seed}")


def next_prime(n: int) -> int:
    if n <= 2:
        return 2
    candidate = n if n % 2 else n + 1
    while not is_prime(candidate):
        candidate += 2
    return candidate


def legendre(n: int, p: int) -> int:
    return pow(n % p, (p - 1) // 2, p)


def tonelli_shanks(n: int, p: int) -> int:
    n %= p
    if n == 0:
        return 0
    if p == 2:
        return n
    if legendre(n, p) != 1:
        raise ValueError("non-residue passed to Tonelli-Shanks")
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        s += 1
        q //= 2
    z = 2
    while legendre(z, p) != p - 1:
        z += 1
    c = pow(z, q, p)
    r = pow(n, (q + 1) // 2, p)
    t = pow(n, q, p)
    m = s
    while t != 1:
        i, tt = 1, (t * t) % p
        while tt != 1:
            tt = (tt * tt) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        r = (r * b) % p
        t = (t * b * b) % p
        c = (b * b) % p
        m = i
    return r


def first_point(p: int, a: int, b: int) -> tuple[int, int]:
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            return x, 0
        if legendre(rhs, p) == 1:
            return x, tonelli_shanks(rhs, p)
    raise RuntimeError("no affine point found")


def add(P: tuple[int, int] | None, Q: tuple[int, int] | None, p: int, a: int) -> tuple[int, int] | None:
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 % p == 0:
            return None
        slope = ((3 * x1 * x1 + a) * pow(2 * y1, -1, p)) % p
    else:
        slope = ((y2 - y1) * pow((x2 - x1) % p, -1, p)) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def scan_points(p: int, a: int, B2: int) -> list[tuple[int, int]]:
    points = []
    for x in range(B2):
        rhs = (x * x * x + a * x + CURRENT_B) % p
        if rhs == 0:
            points.append((x, 0))
        elif legendre(rhs, p) == 1:
            y = tonelli_shanks(rhs, p)
            points.append((x, y))
            if y != p - y:
                points.append((x, p - y))
    points.sort()
    return points


def p5_values(curve: dict) -> dict:
    global CURRENT_B
    p, a, b, q = curve["p"], curve["a"], curve["b"], curve["N"]
    B = ceil_root(p, 5)
    B2 = ceil_root(p * p, 5)
    L = ceil_root(q, 5)
    CURRENT_B = b
    S = scan_points(p, a, B2)
    lp_classes = {x for x, _ in S if B <= x < B2}
    first_class: dict[tuple[int, int], int] = {}
    R_full = R_lp1 = R_lp2 = 0
    for i, P in enumerate(S):
        for k in range(i, len(S)):
            R = add(P, S[k], p, a)
            if R is None or R in first_class:
                continue
            nlp = int(P[0] >= B) + int(S[k][0] >= B)
            first_class[R] = nlp
            if nlp == 0:
                R_full += 1
            elif nlp == 1:
                R_lp1 += 1
            else:
                R_lp2 += 1
    n_lp = len(lp_classes)
    n_edge = R_lp1 + R_lp2
    budgets = {label: (frac * (n_lp + 1) * q + n_edge - 1) // n_edge for label, frac in KAPPAS}
    values = [B, B2, L, len({x for x, _ in S if x < B}), n_lp, len(S), R_full, R_lp1, R_lp2,
              budgets["1/4"], budgets["1/2"], budgets["1"], budgets["2"]]
    frozen = F1_EXPECTED.get(curve["id"])
    return {
        "id": curve["id"], "bits": curve["bits"], "seed": curve["seed"], "counter": curve.get("counter"),
        "p": p, "a": a, "b": b, "N": q, "G": curve["G"],
        "columns": ["B", "B2", "L", "L_fb", "n_lp", "scan_size", "R_full", "R_lp1", "R_lp2", "A_1/4", "A_1/2", "A_1", "A_2"],
        "values": values, "n_edge": n_edge,
        "matches_frozen_f1": None if frozen is None else frozen == values,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if len(F1_EXPECTED) != 9:
        raise AssertionError("F-1 control table is incomplete")
    f2 = [derive_f2(seed) for seed in (11, 12, 13)]
    curves = F1 + f2
    rows = [p5_values(curve) for curve in curves]
    controls = [{"id": row["id"], "expected": F1_EXPECTED[row["id"]], "actual": row["values"], "pass": row["matches_frozen_f1"]}
                for row in rows if row["id"] in F1_EXPECTED]
    payload = {
        "task_id": "TASK-20261001-8615ec",
        "experiment_id": "EXP-RELN-dc761f",
        "computation": "label-free F-1 P-5 control plus F-2 seeds 11/12/13 fixture and P-5 re-derivation",
        "algorithm": {
            "fixture": "SHA-256 UTF-8 namespace rule from specification; PARI/GP ellcard; deterministic admissibility tests; Tonelli-Shanks for the least-x generator",
            "p5": "exact B/B2/L integer fifth roots; sorted affine scan; first unordered pair decomposition; unique non-infinity group-element class counts; exact Fraction budgets",
            "protocol_draws": False,
            "scientific_run": False,
        },
        "f2": f2,
        "p5": rows,
        "f1_controls": controls,
        "f1_controls_pass": all(x["pass"] for x in controls),
    }
    Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"f1_controls_pass": payload["f1_controls_pass"], "f2_ids": [x["id"] for x in f2], "rows": len(rows)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"validator error: {exc}", file=sys.stderr)
        raise
