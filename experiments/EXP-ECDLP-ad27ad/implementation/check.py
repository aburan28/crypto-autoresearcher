#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-ad27ad run artifacts. Reads only; exit 0 iff no problem.

Shares no code with run.py or primeset.py. Carries its own primality test, elliptic-curve
arithmetic, rotation-minimum and the three membership rules, and REPLAYS every recorded closure
pair (P + Q recomputed, membership of P, Q and the sum re-decided) and decomposition triple
(R - P recomputed) per cell and kind, recomputes every ratio and standard error from the recorded
hit counts, recounts E(F_p) and D_rot exactly for every exhaustive cell, and rebuilds the summary
from the cells. A fabricated raw result whose samples were not produced by the stated computation
fails here.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

EXP = "EXP-ECDLP-ad27ad"


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


def on_curve(P, a, b, p):
    return P is None or (P[1] * P[1] - (P[0] ** 3 + a * P[0] + b)) % p == 0


def rotmin(x, c):
    mask = (1 << c) - 1
    x &= mask
    best = x
    for _ in range(c - 1):
        x = ((x << 1) | (x >> (c - 1))) & mask
        best = min(best, x)
    return best


def member(kind, x, c, m, p, key):
    if kind == "rot":
        return rotmin(x, c) < (1 << (c - m))
    if kind == "hash":
        h = hashlib.blake2b(f"{key}:{x}".encode(), digest_size=8).digest()
        return int.from_bytes(h, "big") < (1 << (64 - m))
    if kind == "size":
        return x < (p >> m)
    raise ValueError(kind)


def check_kind(rec, kind, key, problems, counts):
    tag = f"c={rec['c']} seed={rec['seed']} curve={rec['curve']} m={rec['m']} {kind}"
    block = rec["rot" if kind == "rot" else "hash" if kind == "hash" else "size_random_prime"]
    if kind == "size":
        p, a, b = rec["random_prime"], rec["random_prime_a"], rec["random_prime_b"]
    else:
        p, a, b = rec["p"], rec["a"], rec["b"]
    c, m = rec["c"], rec["m"]
    if (4 * a * a * a + 27 * b * b) % p == 0:
        problems.append(f"{tag}: singular curve")
        return
    for s in block.get("replay_closure_pairs", []):
        counts["closure_pairs"] += 1
        P, Q = tuple(s["P"]), tuple(s["Q"])
        S = None if s["S"] is None else tuple(s["S"])
        if not (on_curve(P, a, b, p) and on_curve(Q, a, b, p)):
            problems.append(f"{tag}: replay pair not on the curve")
        if not (member(kind, P[0], c, m, p, key) and member(kind, Q[0], c, m, p, key)):
            problems.append(f"{tag}: replay pair not in D")
        if ec_add(P, Q, a, p) != S:
            problems.append(f"{tag}: P + Q does not recompute")
        if s["in_D"] != (S is not None and member(kind, S[0], c, m, p, key)):
            problems.append(f"{tag}: closure membership flag wrong")
    for s in block.get("replay_decomposition", []):
        counts["decomposition_triples"] += 1
        R, P = tuple(s["R"]), tuple(s["P"])
        T = None if s["T"] is None else tuple(s["T"])
        if not (on_curve(R, a, b, p) and on_curve(P, a, b, p)) or not member(kind, P[0], c, m, p, key):
            problems.append(f"{tag}: decomposition replay inputs invalid")
        if ec_add(R, (P[0], (-P[1]) % p), a, p) != T:
            problems.append(f"{tag}: R - P does not recompute")
        if s["in_D"] != (T is not None and member(kind, T[0], c, m, p, key)):
            problems.append(f"{tag}: decomposition membership flag wrong")
    dens = block["density_hits"] / block["density_n"]
    cf = block["closure_hits"] / block["pairs"]
    df = block["decomposition_hits"] / block["decomposition_total"]
    if block["decomposition_total"] != block["targets"] * block["per_target"]:
        problems.append(f"{tag}: decomposition total != targets * per_target")
    se_c = math.sqrt(cf * (1 - cf) / block["pairs"]) if 0 < cf < 1 else 0.0
    se_d = math.sqrt(df * (1 - df) / block["decomposition_total"]) if 0 < df < 1 else 0.0
    for key_, val in (("density", dens), ("closure_fraction", cf), ("closure_ratio", cf / dens),
                      ("closure_ratio_se", se_c / dens), ("decomposition_fraction", df),
                      ("decomposition_ratio", df / dens), ("decomposition_ratio_se", se_d / dens)):
        if abs(block[key_] - val) > 1e-9 * max(1.0, abs(val)):
            problems.append(f"{tag}: {key_} does not recompute from the recorded counts")


def exhaustive(rec, problems):
    p, a, b, c, m = rec["p"], rec["a"], rec["b"], rec["c"], rec["m"]
    ex = rec["exhaustive"]
    table = bytearray(p)
    for y in range(p):
        table[y * y % p] = 1
    n_pts, n_d = 0, 0
    thr = 1 << (c - m)
    for x in range(p):
        v = (x ** 3 + a * x + b) % p
        k = 1 if v == 0 else (2 if table[v] else 0)
        n_pts += k
        if k and rotmin(x, c) < thr:
            n_d += k
    tag = f"exhaustive c={c} m={m}"
    if ex["n_points"] != n_pts or ex["n_D"] != n_d or abs(ex["exact_density"] - n_d / n_pts) > 1e-12:
        problems.append(f"{tag}: exact point / D counts do not recompute")
    if abs(ex["exact_decomposition_ratio"] - ex["exact_decomposition_fraction_mean"] / ex["exact_density"]) > 1e-9:
        problems.append(f"{tag}: exact decomposition ratio inconsistent")


def main(run_dir: str) -> int:
    problems: list[str] = []
    raw = json.loads(Path(run_dir, "raw-result.json").read_text())
    if raw.get("experiment_id") != EXP:
        problems.append("experiment_id mismatch")
    counts = {"cells": 0, "closure_pairs": 0, "decomposition_triples": 0, "exhaustive": 0}
    for rec in raw.get("cells", []):
        counts["cells"] += 1
        c, p = rec["c"], rec["p"]
        if p != 2 ** c - 1 or not is_prime(p):
            problems.append(f"c={c}: p is not the Mersenne prime")
        if not is_prime(rec["random_prime"]) or rec["random_prime"].bit_length() != c:
            problems.append(f"c={c}: matched random prime not prime or wrong size")
        check_kind(rec, "rot", None, problems, counts)
        check_kind(rec, "hash", rec.get("hash_key"), problems, counts)
        check_kind(rec, "size", None, problems, counts)
        if "exhaustive" in rec:
            counts["exhaustive"] += 1
            exhaustive(rec, problems)
    cells = raw.get("cells", [])
    summ = raw.get("summary", {})
    if cells:
        for kind in ("rot", "hash", "size_random_prime"):
            want = {"max_abs_closure_dev": max(abs(x[kind]["closure_ratio"] - 1) for x in cells),
                    "max_abs_decomposition_dev": max(abs(x[kind]["decomposition_ratio"] - 1) for x in cells),
                    "cells_outside_closure_band": sum(1 for x in cells if abs(x[kind]["closure_ratio"] - 1) > max(0.03, 3 * x[kind]["closure_ratio_se"])),
                    "cells_outside_decomposition_band": sum(1 for x in cells if abs(x[kind]["decomposition_ratio"] - 1) > max(0.05, 3 * x[kind]["decomposition_ratio_se"]))}
            got = summ.get(kind, {})
            for k_, v in want.items():
                if got.get(k_) is None or abs(got[k_] - v) > 1e-9:
                    problems.append(f"summary {kind}.{k_} does not recompute from the cells")
        diffs = [(x["rot"]["closure_ratio"] - x["hash"]["closure_ratio"]) / (math.hypot(x["rot"]["closure_ratio_se"], x["hash"]["closure_ratio_se"]) or 1e-9) for x in cells]
        z = summ.get("rot_minus_hash_closure_z", {})
        if abs(z.get("max_abs", -1) - max(abs(d) for d in diffs)) > 1e-9 or z.get("cells_beyond_3se") != sum(1 for d in diffs if abs(d) > 3):
            problems.append("summary rot_minus_hash_closure_z does not recompute")
    report = {"experiment_id": EXP, "checked": counts, "problems": problems, "ok": not problems}
    print(json.dumps(report, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
