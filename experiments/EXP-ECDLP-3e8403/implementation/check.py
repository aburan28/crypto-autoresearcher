#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-3e8403 run artifacts. Reads only.

Shares no code with run.py. With its own ring arithmetic modulo the recorded
defining polynomial and its own Legendre tests at its own degree-one primes,
it (a) re-verifies EVERY recorded hit: the lifted model reduces to (a, b) at
the recorded base, x^3 + A x + B evaluates to a square at 40 decisive
degree-one primes, and the residue is a valid x-coordinate of E(F_p); (b)
draws a seeded sample of 40 box candidates per arm that are NOT recorded hits
and confirms each is a non-square (a runner that silently dropped points or
invented them fails here); (c) recomputes H, D, the yield index and the
matched candidate counts from the recorded hits. Exit 0 iff no problem.
"""
from __future__ import annotations

import itertools
import json
import math
import random
import sys
from pathlib import Path

EXP = "EXP-ECDLP-3e8403"
NON_HIT_SAMPLE = 40


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
    for a_ in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a_, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def ring_mul(u, v, f):
    d = len(f) - 1
    prod = [0] * (2 * d - 1) if d > 1 else [0]
    for i, ui in enumerate(u):
        for j, vj in enumerate(v):
            prod[i + j] += ui * vj
    for k in range(len(prod) - 1, d - 1, -1):
        c = prod[k]
        if c:
            prod[k] = 0
            for i in range(d):
                prod[k - d + i] -= c * f[i]
    return prod[:d]


def evaluate(u, x, mod):
    v = 0
    for c in reversed(u):
        v = (v * x + c) % mod
    return v


def degree_one_primes(f, count, start):
    pairs, q = [], start
    while len(pairs) < count:
        if is_prime(q):
            for r in range(q):
                if evaluate(f, r, q) == 0:
                    pairs.append((q, r))
        q += 1
    return pairs


def is_square(elem, pairs, need=40):
    decisive = 0
    for q, r in pairs:
        v = evaluate(elem, r, q)
        if v == 0:
            continue
        if pow(v, (q - 1) // 2, q) != 1:
            return False
        decisive += 1
        if decisive >= need:
            return True
    return decisive > 0


def rhs(x, A, B, f):
    x2 = ring_mul(x, x, f)
    x3 = ring_mul(x2, x, f)
    Ax = ring_mul(A, x, f)
    return [p_ + q_ + r_ for p_, q_, r_ in zip(x3, Ax, B)]


def check_arm(tag, arm, res, a, b, errs, rng):
    f, m, p = res["field_f"], res["field_m"], res["field_p"]
    d = len(f) - 1
    A, B = res["A"], res["B"]
    X = res["X_max"]
    if evaluate(f, m, p) != 0:
        errs.append(f"{tag} {arm}: base is not a root of the defining polynomial mod p")
    if evaluate(A, m, p) != a % p or evaluate(B, m, p) != b % p:
        errs.append(f"{tag} {arm}: lifted model does not reduce to (a, b)")
    pairs = degree_one_primes(f, 60, 7919)  # disjoint from the runner's 1009.. range by construction
    hits, vectors = res.get("hits") or [], res.get("hit_vectors") or []
    if len(hits) != len(vectors):
        errs.append(f"{tag} {arm}: hits and hit_vectors differ in length")
    hit_set = set()
    for (rung, rho), vec in zip(hits, vectors):
        hit_set.add(tuple(vec))
        if max(abs(t) for t in vec) != rung or len(vec) != d:
            errs.append(f"{tag} {arm}: hit vector {vec} does not match its rung {rung}")
        if evaluate(vec, m, p) != rho:
            errs.append(f"{tag} {arm}: residue of {vec} is not {rho}")
        v = (rho ** 3 + a * rho + b) % p
        if v and pow(v, (p - 1) // 2, p) != 1:
            errs.append(f"{tag} {arm}: residue {rho} is not an x-coordinate of E")
        if not is_square(rhs(vec, A, B, f), pairs):
            errs.append(f"{tag} {arm}: recorded hit {vec} is NOT a square in K")
    expected_candidates = (2 * X + 1) ** d if d > 1 else res["candidates"]
    if res["candidates"] != expected_candidates:
        errs.append(f"{tag} {arm}: candidate count {res['candidates']} != {expected_candidates}")
    # non-hit sample: a dropped point shows up here
    for _ in range(NON_HIT_SAMPLE):
        if d > 1:
            vec = tuple(rng.randint(-X, X) for _ in range(d))
        else:
            half = (res["candidates"] - 1) // 2
            vec = (rng.randint(-half, half),)
        if vec in hit_set:
            continue
        if is_square(rhs(list(vec), A, B, f), pairs):
            errs.append(f"{tag} {arm}: candidate {list(vec)} is a square in K but was not recorded as a hit")
    # ladder recomputation
    for row in (res.get("ladder") or {}).get("rungs") or []:
        H = sum(1 for r_, _ in hits if r_ <= row["X"])
        D = len({rho for r_, rho in hits if r_ <= row["X"]})
        if row["H"] != H or row["D"] != D:
            errs.append(f"{tag} {arm}: ladder row X={row['X']} H/D {row['H']}/{row['D']} != recomputed {H}/{D}")
        if abs((row.get("yield_index") or 0) - D / math.sqrt(row["W"])) > 1e-12:
            errs.append(f"{tag} {arm}: yield index mismatch at X={row['X']}")


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
    rng = random.Random("EXP-ECDLP-3e8403:check")
    cells = raw.get("cells") or []
    if not cells:
        errs.append("no cells")
    arms_checked = 0
    for cell in cells:
        tag = f"d={cell.get('d')} bits={cell.get('bits')} seed={cell.get('seed')}"
        if not (cell.get("ctrl_known_point") or {}).get("found"):
            errs.append(f"{tag}: CTRL-KNOWN-POINT not found")
        for curve in cell.get("curves") or []:
            cands = set()
            for arm, res in (curve.get("arms") or {}).items():
                if res.get("reverify_fail") or res.get("membership_fail"):
                    errs.append(f"{tag} {arm}: reverify/membership failure recorded")
                cands.add(res.get("candidates"))
                ab = (curve["a_random_arm"], curve["b_random_arm"]) if arm == "null_base_m" else (curve["a"], curve["b"])
                check_arm(tag, arm, res, ab[0], ab[1], errs, rng)
                arms_checked += 1
            if len(cands) != 1:
                errs.append(f"{tag}: arms enumerated different candidate counts {sorted(cands)}")
    ladder = raw.get("degree_ladder")
    if ladder:
        p, c = ladder["p"], ladder["c"]
        for cell in ladder.get("cells") or []:
            d, m = cell["d"], cell["m"]
            for curve in cell.get("curves") or []:
                res = {"field_f": [-c] + [0] * (d - 1) + [1], "field_m": m, "field_p": p, "A": curve["A"],
                       "B": curve["B"], "X_max": max(cell["X_list"]), "hits": curve["hits"],
                       "hit_vectors": curve["hit_vectors"], "candidates": curve["candidates"],
                       "ladder": curve["ladder"]}
                check_arm(f"ladder d={d}", "snfs", res, curve["a"], curve["b"], errs, rng)
                arms_checked += 1
    for e in errs:
        print("FAIL:", e, file=sys.stderr)
    print(f"{EXP} check: {len(cells)} cell(s), {arms_checked} arm(s) re-verified with independent arithmetic, {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
