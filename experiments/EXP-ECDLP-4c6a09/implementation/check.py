#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-4c6a09 run artifacts. Reads only; exit 0 iff no problem.

Shares no code with the Rust runner. Carries its own exact arithmetic in Q[t]/(f) (Fractions),
finite-field elliptic-curve arithmetic, Legendre point count and primality test, and REPLAYS from
the recorded inputs: CTRL-SHAPE against this file's own NIST constants, every toy prime p = f(2^k)
re-evaluated and re-tested for primality, every recorded sample point re-verified on the curve
exactly with its residue at (t - 2^k, p) recomputed, every non-torsion witness re-checked by
reduction, the torsion bound T checked against #E(F_q) on a seeded sample of cells, and every rung
statistic, gamma fit, per-shape summary and regression slope rebuilt from the recorded cells. A
fabricated raw result fails here.
"""
from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

EXP = "EXP-ECDLP-4c6a09"
TORSION_SAMPLE_CELLS = 24
NIST = {  # public constants, FIPS 186-4 D.1.2; shape evaluated at the deployed k must equal them
    "P-192": (64, 2 ** 192 - 2 ** 64 - 1),
    "P-224": (32, 2 ** 224 - 2 ** 96 + 1),
    "P-256": (32, 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1),
    "P-384": (32, 2 ** 384 - 2 ** 128 - 2 ** 96 + 2 ** 32 - 1),
}


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


def poly_eval(g, x):
    v = 0
    for c in reversed(g):
        v = v * x + c
    return v


def poly_mul_mod(a, b, g):
    d = len(g) - 1
    if d == 1:
        return [a[0] * b[0]]
    res = [Fraction(0)] * (2 * d - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    res[i + j] += ai * bj
    for i in range(2 * d - 2, d - 1, -1):
        c = res[i]
        if c:
            for j in range(d + 1):
                res[i - d + j] -= c * g[j]
    return res[:d]


def rhs(x, A, B, g):
    d = len(g) - 1
    x3 = poly_mul_mod(poly_mul_mod(x, x, g), x, g)
    out = [x3[i] + A * x[i] for i in range(d)]
    out[0] += B
    return out


def embed(a, p, root):
    v, pw = 0, 1
    for c in a:
        if c:
            if c.denominator % p == 0:
                return None
            v = (v + c.numerator * pow(c.denominator, -1, p) * pw) % p
        pw = pw * root % p
    return v


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


def count_points(p, a, b):
    n = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v == 0:
            continue
        n += 1 if pow(v, (p - 1) // 2, p) == 1 else -1
    return n


def gamma_fit(rungs):
    pts = [(math.log(r["work"]), math.log(r["distinct_residues"])) for r in rungs if r["distinct_residues"] > 0][-3:]
    if len(pts) < 2:
        return None
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in pts) / sxx


def slope(pairs):
    n = len(pairs)
    mx = sum(x for x, _ in pairs) / n
    my = sum(y for _, y in pairs) / n
    sxx = sum((x - mx) ** 2 for x, _ in pairs)
    return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in pairs) / sxx


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def main(run_dir: str) -> int:
    problems: list[str] = []
    raw = json.loads(Path(run_dir, "raw-result.json").read_text())
    if raw.get("experiment_id") != EXP:
        problems.append("experiment_id mismatch")
    if raw.get("ctrl_shape") is not True:
        problems.append("ctrl_shape not recorded true")
    rng = random.Random("check-4c6a09")
    counts = {"cells": 0, "sample_points": 0, "witnesses": 0, "torsion_bound_cells": 0, "shapes_checked": 0}
    cells = raw.get("cells", [])
    torsion_cells = set(id(c) for c in (cells if len(cells) <= TORSION_SAMPLE_CELLS else rng.sample(cells, TORSION_SAMPLE_CELLS)))
    shape_polys = {}
    for cell in cells:
        counts["cells"] += 1
        fld = cell["field"]
        g = [int(x) for x in fld["g"]]
        d = len(g) - 1
        p = int(fld["p"])
        k = fld["k"]
        tag = f"seed={cell['seed']} {fld['kind']} {fld['shape']} k={k} curve={cell['curve_index']}"
        if fld["kind"] == "solinas":
            shape_polys.setdefault(fld["shape"], g)
            if shape_polys[fld["shape"]] != g:
                problems.append(f"{tag}: two different polynomials recorded for one shape")
        if g[-1] != 1 or fld["d"] != d or fld["weight"] != sum(1 for c in g if c):
            problems.append(f"{tag}: g not monic, or degree/weight mismatch")
            continue
        if not is_prime(p) or p.bit_length() != fld["p_bits"]:
            problems.append(f"{tag}: p not prime or p_bits wrong")
        if d > 1 and poly_eval(g, 2 ** k) != p:
            problems.append(f"{tag}: p != g(2^k)")
        root = int(cell["root_mod_p"])
        if (d > 1 and root != pow(2, k, p)) or (d == 1 and root != 0):
            problems.append(f"{tag}: root_mod_p is not 2^k mod p")
        A, B = int(cell["curve"]["A"]), int(cell["curve"]["B"])
        if (4 * A ** 3 + 27 * B ** 2) % p == 0 or 4 * A ** 3 + 27 * B ** 2 == 0:
            problems.append(f"{tag}: curve singular or bad reduction at p")
        T = cell["torsion_bound_T"]
        for s in cell.get("sample_points", []):
            counts["sample_points"] += 1
            x = [Fraction(v) for v in s["x"]]
            y = [Fraction(v) for v in s["y"]]
            if len(x) != d or poly_mul_mod(y, y, g) != rhs(x, Fraction(A), Fraction(B), g):
                problems.append(f"{tag}: sample point is not on the curve")
                continue
            if s["rational"] != all(v == 0 for v in x[1:] + y[1:]):
                problems.append(f"{tag}: rational flag wrong")
            ex, ey = embed(x, p, root), embed(y, p, root)
            want = None if ex is None or ey is None else [str(ex), str(ey)]
            if s["residue"] != want:
                problems.append(f"{tag}: residue at (t - 2^k, p) does not recompute")
            w = s.get("nontorsion_witness")
            if w is not None:
                counts["witnesses"] += 1
                q, r = w["q"], w["root"]
                if not is_prime(q) or poly_eval(g, r) % q != 0:
                    problems.append(f"{tag}: witness (q, root) is not a degree-one prime of K")
                    continue
                qx, qy = embed(x, q, r), embed(y, q, r)
                if qx is None or qy is None or ec_mul(T, (qx, qy), A % q, q) is None:
                    problems.append(f"{tag}: non-torsion witness fails at q={q}")
        if id(cell) in torsion_cells and cell.get("torsion_bound_primes"):
            q = cell["torsion_bound_primes"][0]
            counts["torsion_bound_cells"] += 1
            if count_points(q, A % q, B % q) % T != 0:
                problems.append(f"{tag}: torsion bound T={T} does not divide #E(F_{q})")
        rungs = cell["rungs"]
        prev_w, prev_d, prev_n = -1, -1, -1
        for r in rungs:
            if r["work"] < prev_w or r["distinct_residues"] < prev_d or r["new_nontorsion_points_cumulative"] < prev_n:
                problems.append(f"{tag}: rungs not monotone")
            prev_w, prev_d, prev_n = r["work"], r["distinct_residues"], r["new_nontorsion_points_cumulative"]
        if not close(cell["gamma"], gamma_fit(rungs)):
            problems.append(f"{tag}: gamma does not recompute from the rungs")
        if cell["new_nontorsion_points"] != rungs[-1]["new_nontorsion_points_cumulative"]:
            problems.append(f"{tag}: new_nontorsion_points != last rung")
    for shape, g in shape_polys.items():
        counts["shapes_checked"] += 1
        if shape not in NIST or poly_eval(g, 2 ** NIST[shape][0]) != NIST[shape][1]:
            problems.append(f"CTRL-SHAPE: {shape} polynomial does not evaluate to the public NIST prime")
    # summary
    per_shape = {}
    for cell in cells:
        per_shape.setdefault(cell["field"]["shape"], {"solinas": [], "random_g": [], "tdc": [], "Q": []})[cell["field"]["kind"]].append(cell["gamma"])
    def mean(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else None
    got_ps = raw.get("summary", {}).get("per_shape", {})
    for shape, arms in per_shape.items():
        got = got_ps.get(shape)
        if got is None:
            problems.append(f"summary: missing shape {shape}")
            continue
        for arm, vals in arms.items():
            if [None if v is None else v for v in got.get(arm, [])] != vals:
                problems.append(f"summary {shape}: {arm} gamma list does not match the cells")
        ms, mr = mean(arms["solinas"]), mean(arms["random_g"])
        diff = (ms - mr) if (ms is not None and mr is not None) else None
        if not close(got.get("gamma_solinas_minus_random_g"), diff):
            problems.append(f"summary {shape}: gamma_solinas_minus_random_g does not recompute")
    pairs = []
    for cell in cells:
        if cell["field"]["d"] > 1 and cell["gamma"] is not None:
            rd = cell["field"].get("root_discriminant_field") or cell["field"]["root_discriminant"]
            pairs.append((math.log(rd), cell["gamma"]))
    reg = raw.get("summary", {}).get("regression_gamma_vs_log_root_discriminant")
    if len(pairs) >= 3:
        if reg is None or reg.get("n") != len(pairs) or not close(reg.get("slope"), slope(pairs)):
            problems.append("summary: regression slope or n does not recompute from the cells")
        elif reg.get("ci99") and not (reg["ci99"][0] - 1e-9 <= reg["slope"] <= reg["ci99"][1] + 1e-9):
            problems.append("summary: regression interval does not bracket the slope")
    elif reg is not None:
        problems.append("summary: regression reported with fewer than three pairs")
    report = {"experiment_id": EXP, "checked": counts, "problems": problems, "ok": not problems}
    print(json.dumps(report, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
