#!/usr/bin/env python3
"""EXP-ECDLP-3e8403: SNFS-field lift covering.

For each cell, lift E/F_p into the SNFS field K_d = Q[x]/(x^d - c) (arm snfs),
into the monic base-m field of a matched random prime (arm null_base_m), and
into Q (arm q_lift); enumerate x with coefficient vector in the box
[-X, X]^d; declare a K-point when x^3 + A x + B is a square in K (Legendre
tests at 48 degree-one primes, re-verified at 48 more); reduce to E(F_p) and
count distinct residues per rung. Pure Python 3 standard library.
Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import random
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import primeset  # noqa: E402


# ----------------------------------------------------------------------------
# Z[x]/(f) arithmetic for monic f, coefficients low-to-high
# ----------------------------------------------------------------------------

class Ring:
    def __init__(self, f: list[int]):
        assert f[-1] == 1
        self.f = f
        self.d = len(f) - 1
        self.tail = [-c for c in f[:-1]]  # x^d = sum tail_i x^i

    def mul(self, u: list[int], v: list[int]) -> list[int]:
        d = self.d
        prod = [0] * (2 * d - 1)
        for i, ui in enumerate(u):
            if ui == 0:
                continue
            for j, vj in enumerate(v):
                prod[i + j] += ui * vj
        for k in range(2 * d - 2, d - 1, -1):
            ck = prod[k]
            if ck == 0:
                continue
            prod[k] = 0
            for i, t in enumerate(self.tail):
                if t:
                    prod[k - d + i] += ck * t
        return prod[:d]

    def add(self, u, v):
        return [a + b for a, b in zip(u, v)]

    def eval_int(self, u: list[int], m: int) -> int:
        v = 0
        for c in reversed(u):
            v = v * m + c
        return v


def poly_roots_mod(f: list[int], q: int) -> list[int]:
    roots = []
    for r in range(q):
        v = 0
        for c in reversed(f):
            v = (v * r + c) % q
        if v == 0:
            roots.append(r)
    return roots


def degree_one_primes(f: list[int], count: int, start: int, skip: set[int]) -> list[tuple[int, int]]:
    """(q, r) pairs with f(r) = 0 mod q, q prime >= start, q not in skip."""
    pairs = []
    q = start
    while len(pairs) < count:
        if primeset.is_prime(q) and q not in skip:
            for r in poly_roots_mod(f, q):
                pairs.append((q, r))
                if len(pairs) >= count:
                    break
        q += 1
    return pairs


def is_square_in_K(ring: Ring, elem: list[int], pairs: list[tuple[int, int]], need: int) -> tuple[bool, int]:
    """Probabilistic squareness test; returns (declared_square, decisive_tests)."""
    decisive = 0
    for q, r in pairs:
        v = 0
        for c in reversed(elem):
            v = (v * r + c) % q
        if v == 0:
            continue
        if pow(v, (q - 1) // 2, q) != 1:
            return False, decisive + 1
        decisive += 1
        if decisive >= need:
            return True, decisive
    return (decisive > 0), decisive


def irreducible_degree_pattern(f: list[int], primes: list[int]) -> bool:
    """Necessary-condition test: for some prime q, f mod q is irreducible
    (checked by distinct-degree factorisation); sufficient for irreducibility over Q."""
    d = len(f) - 1
    for q in primes:
        if f[-1] % q == 0:
            continue
        # x^(q^i) mod f over F_q, i = 1..d/2; f irreducible iff gcd(x^(q^i) - x, f) = 1 for all i <= d/2
        if _irreducible_mod_q(f, q):
            return True
    return False


def _pmul(a, b, f, q):
    d = len(f) - 1
    prod = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            prod[i + j] = (prod[i + j] + ai * bj) % q
    inv = pow(f[-1], -1, q)
    for k in range(len(prod) - 1, d - 1, -1):
        c = prod[k] * inv % q
        if c:
            for i in range(d + 1):
                prod[k - d + i] = (prod[k - d + i] - c * f[i]) % q
    return (prod[:d] + [0] * d)[:d]


def _pgcd(a, b, q):
    a = [x % q for x in a]
    b = [x % q for x in b]
    def trim(v):
        while v and v[-1] == 0:
            v.pop()
        return v
    a, b = trim(a), trim(b)
    while b:
        # a mod b
        a = a[:]
        inv = pow(b[-1], -1, q)
        while len(a) >= len(b):
            c = a[-1] * inv % q
            shift = len(a) - len(b)
            for i, bi in enumerate(b):
                a[shift + i] = (a[shift + i] - c * bi) % q
            a = trim(a)
            if not a:
                break
        a, b = b, a
    return a


def _irreducible_mod_q(f, q):
    d = len(f) - 1
    x = [0, 1] + [0] * (d - 2) if d >= 2 else [0, 1]
    x = (x + [0] * d)[:d]
    cur = x[:]
    for i in range(1, d // 2 + 1):
        # cur = cur^q mod f
        res = [1] + [0] * (d - 1)
        base = cur[:]
        e = q
        while e:
            if e & 1:
                res = _pmul(res, base, f, q)
            base = _pmul(base, base, f, q)
            e >>= 1
        cur = res
        diff = [(a - b) % q for a, b in zip(cur, x)]
        g = _pgcd(f, diff, q)
        if len(g) > 1:
            return False
    return True


# ----------------------------------------------------------------------------
# cells
# ----------------------------------------------------------------------------

def balanced_residue(v: int, p: int) -> int:
    v %= p
    return v - p if v > p // 2 else v


def build_field(arm: str, d: int, p: int, m: int, c: int | None, seed: int) -> dict:
    if arm == "snfs":
        f = [-c] + [0] * (d - 1) + [1]
    elif arm == "null_base_m":
        f = primeset.monic_base_m_poly(p, m, d)
        if f is None:
            raise SystemExit("null polynomial does not fit")
        if not irreducible_degree_pattern(f, [q for q in range(1009, 1200) if primeset.is_prime(q)][:8]):
            raise SystemExit("CTRL-IRREDUCIBLE: regenerate with another seed")
    else:
        f = [-m, 1]  # d = 1, alpha = m: Q-lift
    ring = Ring(f)
    skip = set()
    pairs = degree_one_primes(f, 48, 1009, skip)
    used = {q for q, _ in pairs}
    pairs2 = degree_one_primes(f, 48, max(used) + 1, used)
    assert ring.eval_int(f, m) % p == 0
    return {"arm": arm, "d": len(f) - 1, "f": f, "m": m, "p": p, "ring": ring, "pairs": pairs, "pairs2": pairs2}


def lift_coeff(v: int, field: dict) -> list[int]:
    d, m, p = field["d"], field["m"], field["p"]
    if d == 1:
        return [balanced_residue(v, p)]
    digits = primeset.balanced_digits(balanced_residue(v, p) % p, m, d)
    if digits is None:
        # least-absolute residue may need d digits with a carry; fall back to the
        # plain residue in [0, p) which always fits since p <= m^d + |c|
        digits = primeset.balanced_digits(v % p, m, d)
    if digits is None:
        digits = primeset.balanced_digits(v % p, m, d + 1)
        assert digits is not None
        # fold the top digit into the lowest via alpha^d = -tail (exact for snfs: m^d = p + c)
        top = digits.pop()
        ring = field["ring"]
        extra = [top * t for t in ring.tail]
        digits = [a + b for a, b in zip(digits, extra)]
    return digits


def enumerate_box(field: dict, A: list[int], B: list[int], X: int, p: int, a: int, b: int,
                  W_target: int | None = None) -> dict:
    ring = field["ring"]
    d = field["d"]
    m = field["m"]
    hits = []  # (rung, residue)
    tests_hist = {}
    if d == 1:
        half = (W_target - 1) // 2 if W_target else X
        candidates = ((x,) for x in range(-half, half + 1))
        rung_of = lambda vec: abs(vec[0])  # noqa: E731
    else:
        candidates = itertools.product(range(-X, X + 1), repeat=d)
        rung_of = lambda vec: max(abs(t) for t in vec)  # noqa: E731
    count = 0
    reverify_fail = 0
    membership_fail = 0
    for vec in candidates:
        count += 1
        x = list(vec)
        x2 = ring.mul(x, x)
        x3 = ring.mul(x2, x)
        rhs = ring.add(ring.add(x3, ring.mul(A, x)), B)
        ok, dec = is_square_in_K(ring, rhs, field["pairs"], 40)
        tests_hist[dec] = tests_hist.get(dec, 0) + 1
        if not ok:
            continue
        ok2, _ = is_square_in_K(ring, rhs, field["pairs2"], 40)
        if not ok2:
            reverify_fail += 1
            continue
        rho = ring.eval_int(x, m) % p
        v = (rho ** 3 + a * rho + b) % p
        if v != 0 and pow(v, (p - 1) // 2, p) != 1:
            membership_fail += 1
            continue
        hits.append((rung_of(vec), rho))
    rungs = sorted(set(r for r, _ in hits))
    return {"candidates": count, "hits": hits, "reverify_fail": reverify_fail,
            "membership_fail": membership_fail, "decisive_tests_hist": tests_hist}


def ladder_stats(hits: list, d: int, X_list: list[int], W_of) -> list[dict]:
    rows = []
    for X in X_list:
        W = W_of(X)
        H = sum(1 for r, _ in hits if r <= X)
        D = len({rho for r, rho in hits if r <= X})
        rows.append({"X": X, "W": W, "H": H, "D": D, "yield_index": D / math.sqrt(W) if W else None})
    fit = [(math.log(r["W"]), math.log(r["D"])) for r in rows if r["D"] >= 2]
    gamma = None
    if len(fit) >= 3:
        xs, ys = zip(*fit)
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        gamma = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else None
    return {"rungs": rows, "gamma": gamma, "fitted_rungs": len(fit),
            "Y_max": max((r["yield_index"] for r in rows if r["yield_index"] is not None), default=None)}


def run_cell(d: int, bits: int, seed: int, X_list: list[int], curves: int) -> dict:
    sp = primeset.special_primes(d, bits, 1)
    if not sp:
        raise SystemExit(f"no special prime d={d} bits={bits}")
    sp = sp[0]
    p, m, c = sp["p"], sp["m"], sp["c"]
    rp = primeset.matched_random_prime(bits, seed, f"d{d}")
    pp = rp["p"]
    mp = int(round(pp ** (1.0 / d)))
    while mp ** d > pp:
        mp -= 1
    fields = {"snfs": build_field("snfs", d, p, m, c, seed),
              "null_base_m": build_field("null_base_m", d, pp, mp, None, seed),
              "q_lift": build_field("q_lift", 1, p, p, None, seed)}
    fields["q_lift"]["m"] = 0  # x evaluates to itself; residue = x mod p
    rng = random.Random(f"EXP-ECDLP-3e8403:{seed}:{d}:{bits}")
    out = {"d": d, "bits": bits, "seed": seed, "special": sp, "random": {"p": pp, "m": mp},
           "fields": {k: {"f": v["f"], "m": v["m"], "p": v["p"]} for k, v in fields.items()},
           "curves": []}
    X_max = max(X_list)
    for ci in range(curves):
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a * a * a + 27 * b * b) % p == 0:
            continue
        ap_, bp_ = rng.randrange(pp), rng.randrange(pp)
        if (4 * ap_ ** 3 + 27 * bp_ ** 2) % pp == 0:
            continue
        crow = {"a": a, "b": b, "a_random_arm": ap_, "b_random_arm": bp_, "arms": {}}
        for arm, field in fields.items():
            aa, bb = (ap_, bp_) if arm == "null_base_m" else (a, b)
            P = field["p"]
            A = lift_coeff(aa, field) if arm != "q_lift" else [balanced_residue(aa, P)]
            B = lift_coeff(bb, field) if arm != "q_lift" else [balanced_residue(bb, P)]
            # CTRL: lifts reduce correctly
            if arm != "q_lift":
                assert field["ring"].eval_int(A, field["m"]) % P == aa % P
                assert field["ring"].eval_int(B, field["m"]) % P == bb % P
            t0 = time.time()
            W_of = (lambda X, dd=field["d"]: (2 * X + 1) ** dd) if arm != "q_lift" else (lambda X, dd=d: (2 * X + 1) ** dd)
            if arm == "q_lift":
                field_run = dict(field)
                field_run["m"] = 0
                res = enumerate_box(field_run, A, B, X_max, P, aa, bb, W_target=W_of(X_max))
                # rung for q_lift: map |x| to the X whose W contains it
                remapped = []
                for r, rho in res["hits"]:
                    Xr = next(X for X in sorted(X_list) if abs(r) <= (W_of(X) - 1) // 2)
                    remapped.append((Xr, rho))
                res["hits"] = remapped
            else:
                res = enumerate_box(field, A, B, X_max, P, aa, bb)
            stats = ladder_stats(res["hits"], field["d"], sorted(X_list), W_of)
            crow["arms"][arm] = {"A": A, "B": B, "candidates": res["candidates"],
                                 "reverify_fail": res["reverify_fail"],
                                 "membership_fail": res["membership_fail"],
                                 "decisive_tests_hist": res["decisive_tests_hist"],
                                 "ladder": stats, "wall_clock_seconds": time.time() - t0,
                                 "mean_log2_model_coeff": _mean_log2(A + B)}
        out["curves"].append(crow)
    # CTRL-KNOWN-POINT on the snfs arm: plant x0 with coefficient 1 at rung 1
    field = fields["snfs"]
    x0 = [1] + [0] * (d - 1)
    y0 = [2] + [0] * (d - 1)
    A = lift_coeff(rng.randrange(p), field)
    rr = field["ring"]
    Bp = rr.add(rr.mul(y0, y0), [-t for t in rr.add(rr.mul(rr.mul(x0, x0), x0), rr.mul(A, x0))])
    a_pl = rr.eval_int(A, m) % p
    b_pl = rr.eval_int(Bp, m) % p
    res = enumerate_box(field, A, Bp, 1, p, a_pl, b_pl)
    out["ctrl_known_point"] = {"found": any(rho == (rr.eval_int(x0, m) % p) for _, rho in res["hits"]),
                               "hits_at_rung_1": len(res["hits"])}
    return out


def _mean_log2(vals):
    nz = [abs(v) for v in vals if v]
    return sum(math.log2(v) for v in nz) / len(nz) if nz else 0.0


def degree_ladder(seed: int, X_list: list[int], curves: int, W_cap: int) -> dict:
    """One prime p = 8^12 - c, lifted into K_d for d | 12 with m_d = 8^(12/d)."""
    base = 8
    p = None
    for c in primeset.C_LIST:
        if primeset.is_prime(base ** 12 - c):
            p, cc = base ** 12 - c, c
            break
    rng = random.Random(f"EXP-ECDLP-3e8403:ladder:{seed}")
    out = {"p": p, "c": cc, "cells": []}
    for d in [2, 3, 4, 6, 12]:
        m = base ** (12 // d)
        field = build_field("snfs", d, p, m, cc, seed)
        Xs = [X for X in X_list if (2 * X + 1) ** d <= W_cap] or [1]
        cell = {"d": d, "m": m, "X_list": Xs, "curves": []}
        crng = random.Random(f"EXP-ECDLP-3e8403:ladder:{seed}:curves")
        for _ in range(curves):
            a, b = crng.randrange(p), crng.randrange(p)
            if (4 * a ** 3 + 27 * b ** 2) % p == 0:
                continue
            A, B = lift_coeff(a, field), lift_coeff(b, field)
            res = enumerate_box(field, A, B, max(Xs), p, a, b)
            stats = ladder_stats(res["hits"], d, Xs, lambda X, dd=d: (2 * X + 1) ** dd)
            cell["curves"].append({"a": a, "b": b, "candidates": res["candidates"], "ladder": stats,
                                   "reverify_fail": res["reverify_fail"], "membership_fail": res["membership_fail"]})
        out["cells"].append(cell)
        print(f"degree ladder d={d} done", file=sys.stderr, flush=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", type=int, nargs="+", default=[2, 3, 4, 5])
    ap.add_argument("--bits", type=int, nargs="+", default=[24, 32])
    ap.add_argument("--X", type=int, nargs="+", default=[1, 2, 3, 4, 6, 8])
    ap.add_argument("--curves", type=int, default=4)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--degree-ladder", action="store_true")
    ap.add_argument("--ladder-w-cap", type=int, default=10 ** 6)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()
    cells = []
    for d in args.d:
        for bits in args.bits:
            for seed in args.seeds:
                cells.append(run_cell(d, bits, seed, args.X, args.curves))
                print(f"cell d={d} bits={bits} seed={seed} done", file=sys.stderr, flush=True)
    raw = {"experiment_id": "EXP-ECDLP-3e8403", "hypothesis_id": "H-ECDLP-bd1572", "argv": sys.argv,
           "cells": cells}
    if args.degree_ladder:
        raw["degree_ladder"] = degree_ladder(args.seeds[0], args.X, args.curves, args.ladder_w_cap)
    raw["wall_clock_seconds"] = time.time() - started
    raw_path = os.path.join(args.out, "raw-result.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True, default=str)
    src = os.path.abspath(__file__)
    manifest = {"experiment_id": "EXP-ECDLP-3e8403", "command": " ".join(sys.argv),
                "python": platform.python_version(), "platform": platform.platform(),
                "source_sha256": {"run.py": hashlib.sha256(open(src, "rb").read()).hexdigest(),
                                  "primeset.py": hashlib.sha256(open(os.path.join(os.path.dirname(src), "primeset.py"), "rb").read()).hexdigest()},
                "raw_result_sha256": hashlib.sha256(open(raw_path, "rb").read()).hexdigest(),
                "started_unix": started, "finished_unix": time.time(),
                "asserts_nothing_about": "the hypothesis; observations only"}
    try:
        manifest["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        manifest["git_commit"] = None
    with open(os.path.join(args.out, "manifest.yaml"), "w", encoding="utf-8") as fh:
        for k, v in manifest.items():
            fh.write(f"{k}: {json.dumps(v)}\n")


if __name__ == "__main__":
    main()
