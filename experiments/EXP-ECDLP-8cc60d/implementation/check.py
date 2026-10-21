#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-8cc60d run artifacts. Reads only; exit 0 iff no problem.

Shares no code with run.py or primeset.py. Carries its own primality test, trial division,
elliptic-curve arithmetic, exact point count and multiplicative-order routine, and REPLAYS from
recorded inputs: a seeded sample of census rows per cell (group order recounted exactly below 2^20,
Hasse plus a random point killed by the order above; l the largest prime factor; k = ord_l(p);
the four exact conditions recomputed from (k, l, c)), every supersingular control, every deployed-
curve row against this file's own public constants ([l]G = O recomputed), every part-B census
count, and every recorded norm-box replay sample. A fabricated raw result whose rows were not
produced by the stated computation fails here.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

EXP = "EXP-ECDLP-8cc60d"
ROWS_PER_CELL = 6


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
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


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R


def sqrt_mod(n, p):
    n %= p
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


def random_point(p, a, b, rng):
    while True:
        x = rng.randrange(p)
        v = (x * x * x + a * x + b) % p
        if v == 0:
            return (x, 0)
        if pow(v, (p - 1) // 2, p) == 1:
            return (x, sqrt_mod(v, p))


def count_exact(p, a, b):
    table = bytearray(p)
    for y in range(p):
        table[y * y % p] = 1
    n = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v == 0:
            continue
        n += 1 if table[v] else -1
    return n


def factor(n):
    out = {}
    d = 2
    while d * d <= n and d < 2_000_000:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def mult_order(g, l):
    """Order of g in (Z/l)^*, l prime, by factoring l - 1."""
    g %= l
    order = l - 1
    for q in factor(l - 1):
        while order % q == 0 and pow(g, order // q, l) == 1:
            order //= q
    return order


def exact_conditions(k, l, c, o2):
    return {"k1_iff_ord2_divides_c_minus_1": (k == 1) == ((c - 1) % o2 == 0),
            "k_never_2": k != 2,
            "k3_iff_ord_2c_is_6": (k == 3) == (mult_order(pow(2, c, l), l) == 6),
            "k4_iff_l_divides_aurifeuillean": (k == 4) == ((pow(2, 2 * c - 1, l) - pow(2, c, l) + 1) % l == 0)}


# Public NIST constants (FIPS 186-4, D.1.2), typed here independently of run.py; a transcription
# error fails the on-curve / [l]G = O checks below rather than passing silently.
DEPLOYED = {
    "P-521": dict(c=521, p=2 ** 521 - 1, a=-3,
                  b=0x051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00,
                  G=(0xc6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66,
                     0x11839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650),
                  l=0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409),
    "P-256": dict(c=None, p=2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1, a=-3,
                  b=0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
                  G=(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
                     0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5),
                  l=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551),
    "P-224": dict(c=None, p=2 ** 224 - 2 ** 96 + 1, a=-3,
                  b=0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4,
                  G=(0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21,
                     0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34),
                  l=0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d),
    "P-192": dict(c=None, p=2 ** 192 - 2 ** 64 - 1, a=-3,
                  b=0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1,
                  G=(0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012,
                     0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811),
                  l=0xffffffffffffffffffffffff99def836146bc9b1b4d22831),
}


def main(run_dir: str) -> int:
    problems: list[str] = []
    raw = json.loads(Path(run_dir, "raw-result.json").read_text())
    if raw.get("experiment_id") != EXP:
        problems.append("experiment_id mismatch")
    rng = random.Random("check-8cc60d")
    checked = {"rows": 0, "cells": 0, "part_c_rows": 0, "part_d_samples": 0, "part_b_cells": 0}
    # ---- part A ---------------------------------------------------------------------------
    for cell in raw.get("part_a", {}).get("cells", []):
        cen = cell["census"]
        p, arm, c = cen["p"], cen["arm"], cen.get("c")
        tag = f"part_a p={p} seed={cell.get('seed')}"
        checked["cells"] += 1
        if not is_prime(p):
            problems.append(f"{tag}: p not prime")
        if arm == "mersenne" and p != 2 ** c - 1:
            problems.append(f"{tag}: mersenne arm but p != 2^c - 1")
        rows = cen["rows"]
        sample = rows if len(rows) <= ROWS_PER_CELL else rng.sample(rows, ROWS_PER_CELL)
        for row in sample:
            checked["rows"] += 1
            a, b, n, l, k = row["a"], row["b"], row["order"], row["l"], row["k"]
            if (4 * a * a * a + 27 * b * b) % p == 0:
                problems.append(f"{tag}: singular curve recorded")
                continue
            if p < 1 << 20:
                if count_exact(p, a, b) != n:
                    problems.append(f"{tag}: order {n} does not match exact recount for (a,b)=({a},{b})")
            else:
                if abs(n - p - 1) > 2 * math.isqrt(p) + 1:
                    problems.append(f"{tag}: order outside Hasse interval")
                if ec_mul(n, random_point(p, a, b, rng), a, p) is not None:
                    problems.append(f"{tag}: random point not killed by recorded order {n}")
            if not is_prime(l) or n % l != 0 or max(factor(n)) != l:
                problems.append(f"{tag}: l={l} is not the largest prime factor of {n}")
                continue
            if mult_order(p, l) != k:
                problems.append(f"{tag}: k={k} != ord_l(p)")
            if row.get("t") != (l - 1) // k:
                problems.append(f"{tag}: t != (l-1)/k")
            if arm == "mersenne":
                o2 = mult_order(2, l)
                if row.get("ord_l_2") != o2:
                    problems.append(f"{tag}: ord_l(2) mismatch")
                ex = exact_conditions(k, l, c, o2)
                if row.get("exact_conditions") != ex:
                    problems.append(f"{tag}: exact_conditions mismatch for l={l}")
                if row.get("identity_ok") != all(ex.values()):
                    problems.append(f"{tag}: identity_ok inconsistent")
                if row.get("small_ord_l_2") != (o2 <= 10 ** 4):
                    problems.append(f"{tag}: small_ord_l_2 inconsistent")
        ss = cen.get("supersingular_control")
        if p % 4 == 3 and (ss is None or ss.get("order") != p + 1):
            problems.append(f"{tag}: supersingular control missing or order != p + 1")
        if ss:
            fac = factor(p + 1)
            if {int(q): e for q, e in ss["factorisation"].items()} != fac or ss.get("l") != max(fac):
                problems.append(f"{tag}: supersingular factorisation mismatch")
    # ---- part B ---------------------------------------------------------------------------
    for cell in raw.get("part_b", {}).get("cells", []):
        checked["part_b_cells"] += 1
        tag = f"part_b p={cell.get('p')} seed={cell.get('seed')}"
        src = [x for x in raw["part_a"]["cells"] if x["census"]["p"] == cell["p"] and x["seed"] == cell["seed"]]
        if not src:
            problems.append(f"{tag}: no matching census cell")
            continue
        rows = src[0]["census"]["rows"]
        if cell.get("n_rows") != len(rows):
            problems.append(f"{tag}: n_rows != census rows")
        obs = sum(1 for r in rows if r.get("small_ord_l_2"))
        if cell.get("observed") != obs:
            problems.append(f"{tag}: observed small-ord count {cell.get('observed')} != {obs}")
        if cell.get("within") != (cell.get("observed", 0) <= cell.get("poisson_999_quantile", -1)):
            problems.append(f"{tag}: within flag inconsistent")
    # ---- part C ---------------------------------------------------------------------------
    for row in raw.get("part_c", {}).get("rows", []):
        checked["part_c_rows"] += 1
        name = row.get("name")
        cv = DEPLOYED.get(name)
        if cv is None:
            problems.append(f"part_c: unknown curve {name}")
            continue
        p, l, (gx, gy) = cv["p"], cv["l"], cv["G"]
        a = cv["a"] % p
        on = (gy * gy - (gx ** 3 + a * gx + cv["b"])) % p == 0
        killed = on and ec_mul(l, (gx, gy), a, p) is None
        expect = {"p_prime": is_prime(p), "l_prime": is_prime(l), "base_point_on_curve": on,
                  "order_check_lG_is_O": killed, "bits_p": p.bit_length(), "bits_l": l.bit_length()}
        for key, val in expect.items():
            if row.get(key) != val:
                problems.append(f"part_c {name}: {key} recorded {row.get(key)} but recomputed {val}")
        if not (on and killed):
            problems.append(f"part_c {name}: this file's own constants fail on-curve/[l]G = O (checker constants or curve wrong)")
        if cv["c"]:
            c = cv["c"]
            flags = {"k_is_1": pow(2, c - 1, l) == 1, "k_is_2": False,
                     "k_is_3": (pow(2, 2 * c, l) - pow(2, c, l) + 1) % l == 0,
                     "k_is_4": (pow(2, 2 * c - 1, l) - pow(2, c, l) + 1) % l == 0,
                     "p_plus_1_is_power_of_2": (p + 1) & p == 0}
            for key, val in flags.items():
                if row.get(key) != val:
                    problems.append(f"part_c {name}: {key} mismatch")
            if row.get("k_in_1_to_4") != (flags["k_is_1"] or flags["k_is_3"] or flags["k_is_4"]):
                problems.append(f"part_c {name}: k_in_1_to_4 inconsistent")
    # ---- part D ---------------------------------------------------------------------------
    for box in raw.get("part_d", {}).get("boxes", []):
        lb = box["log2_B"]
        tag = f"part_d log2_B={lb}"
        for s in box.get("replay_sample", []):
            checked["part_d_samples"] += 1
            a, b = s["a"], s["b"]
            fs = abs(a ** 5 - 16 * b ** 5)
            fb = abs(2 ** 101 * a ** 4 - b ** 4)
            if abs(b) > 1 << lb or abs(a) > 1 << lb or math.gcd(a, b) != 1 or fs == 0 or fb == 0:
                problems.append(f"{tag}: replay sample outside the stated box or not coprime")
            if abs(math.log2(fs) - s["log2_special"]) > 1e-9 or abs(math.log2(fb) - s["log2_basem"]) > 1e-9:
                problems.append(f"{tag}: replay sample norms do not recompute")
        n = box["n"]
        if n <= 0:
            problems.append(f"{tag}: empty box")
            continue
        if abs(box["sum_log2_special"] / n - box["mean_log2_norm_special"]) > 1e-6 or abs(box["sum_log2_basem"] / n - box["mean_log2_norm_basem"]) > 1e-6:
            problems.append(f"{tag}: means do not match recorded sums")
        gap = box["mean_log2_norm_special"] - box["mean_log2_norm_basem"]
        if abs(gap - box["gap_bits_special_minus_basem"]) > 1e-6 or box["derived_prediction"] != -(97 - lb) or box["within_3_bits"] != (abs(gap + (97 - lb)) <= 3):
            problems.append(f"{tag}: gap, prediction or within_3_bits inconsistent")
    report = {"experiment_id": EXP, "checked": checked, "problems": problems, "ok": not problems}
    print(json.dumps(report, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
