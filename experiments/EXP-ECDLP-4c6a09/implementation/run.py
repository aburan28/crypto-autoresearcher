#!/usr/bin/env python3
"""EXP-ECDLP-4c6a09 (H-ECDLP-4da36f, SNFS-G3): Solinas number fields.

For the four NIST low-weight shapes f and toy primes p = f(2^k), lift seeded curves E/Q to
K_f = Q[t]/(f) and enumerate K_f-points in a work ladder; reduce at the degree-one prime
P_1 = (t - 2^k, p); record distinct residues D(W), the covering exponent gamma, non-torsion
new points and their minimal naive height; repeat for seeded random monic g of the same
degree and weight (coefficients in {-1, 0, 1}) with g(2^k') prime, for t^d - c fields (the
EXP-ECDLP-3e8403 form) and for Q itself; regress gamma on log root discriminant. The rank
arm (2-descent over K_f) is skipped and reported as skipped: no descent tool over number
fields is available. Pure Python 3 standard library; PARI/GP, when present, supplies field
discriminants. Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ecnf  # noqa: E402
import gptool  # noqa: E402
import nfield  # noqa: E402

EXP = "EXP-ECDLP-4c6a09"
HYP = "H-ECDLP-4da36f"

NIST_SHAPES = {  # low -> high coefficients; p = f(2^k) is the NIST prime at the listed k
    "P-192": [-1, -1, 0, 1],                                 # t^3 - t - 1,                  k = 64
    "P-224": [1, 0, 0, -1, 0, 0, 0, 1],                      # t^7 - t^3 + 1,                k = 32
    "P-256": [-1, 0, 0, 1, 0, 0, 1, -1, 1],                  # t^8 - t^7 + t^6 + t^3 - 1,    k = 32
    "P-384": [-1, 1, 0, -1, -1, 0, 0, 0, 0, 0, 0, 0, 1],     # t^12 - t^4 - t^3 + t - 1,     k = 32
}


# CTRL-SHAPE: each shape evaluated at its deployed k must give the public NIST prime (FIPS 186-4,
# D.1.2); these are public parameters, used only to pin the polynomial shapes. Toy primes f(2^k) at
# small k are what the cells use.
NIST_PRIMES = {
    "P-192": (64, 2 ** 192 - 2 ** 64 - 1),
    "P-224": (32, 2 ** 224 - 2 ** 96 + 1),
    "P-256": (32, 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1),
    "P-384": (32, 2 ** 384 - 2 ** 128 - 2 ** 96 + 2 ** 32 - 1),
}


def check_shapes():
    for name, (k, prime) in NIST_PRIMES.items():
        assert poly_eval(NIST_SHAPES[name], 2 ** k) == prime, f"CTRL-SHAPE failed for {name}"
    return True


def poly_text(g):
    terms = []
    for i in range(len(g) - 1, -1, -1):
        c = g[i]
        if not c:
            continue
        mono = "1" if i == 0 else ("t" if i == 1 else f"t^{i}")
        if abs(c) == 1 and i > 0:
            terms.append(("-" if c < 0 else "+") + mono)
        else:
            terms.append(("-" if c < 0 else "+") + f"{abs(c)}" + ("" if i == 0 else "*" + mono))
    s = " ".join(terms)
    return s[1:] if s.startswith("+") else "-" + s[1:]


def poly_eval(g, x):
    v = 0
    for c in reversed(g):
        v = v * x + c
    return v


def weight(g):
    return sum(1 for c in g if c)


def toy_primes_for(g, kmin, kmax, min_bits):
    out = []
    for k in range(kmin, kmax + 1):
        p = poly_eval(g, 2 ** k)
        if p >= 2 ** min_bits and nfield._is_prime(p):
            out.append((k, p))
    return out


def random_shape(d, w, rng):
    while True:
        g = [0] * d + [1]
        g[0] = rng.choice([-1, 1])
        idx = rng.sample(range(1, d), w - 2) if w > 2 else []
        for i in idx:
            g[i] = rng.choice([-1, 1])
        if nfield.NumberField(g).discriminant() != 0 and nfield.is_irreducible_over_Q(g) is True:
            return g


def seeded_curves(n, p, rng):
    out = []
    while len(out) < n:
        A, B = rng.randint(-20, 20), rng.randint(-20, 20)
        if 4 * A ** 3 + 27 * B ** 2 == 0 or (4 * A ** 3 + 27 * B ** 2) % p == 0:
            continue
        out.append((Fraction(A), Fraction(B)))
    return out


def fit_gamma(rungs):
    pts = [(math.log(r["work"]), math.log(r["distinct_residues"])) for r in rungs if r["distinct_residues"] > 0][-3:]
    if len(pts) < 2:
        return None
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in pts) / sxx


def run_cell(K, A, B, p, root, ladder, aux, split_for_T, T, seed=0):
    """One enumeration up to max(ladder) candidates; each rung is a snapshot of the cumulative
    state when `tried` first reaches that rung's work budget."""
    E = ecnf.CurveNF(K, A, B)
    ladder = sorted(set(ladder))
    rungs = []
    seen = {}
    residues = set()
    cum = {"new_nontorsion": 0, "rational": 0, "no_residue": 0}
    min_height = None
    rung_i = 0
    last_tried, last_shells = 0, 0

    def snapshot(tried, shells):
        rungs.append({"work": tried, "shells_completed": shells, "points_found_cumulative": len(seen),
                      "distinct_residues": len(residues), "new_nontorsion_points_cumulative": cum["new_nontorsion"],
                      "rational_points_seen": cum["rational"], "points_without_residue": cum["no_residue"]})

    for kind, tried, shells, P in E.iter_search(aux, ladder[-1], checkpoints=ladder, seed=seed):
        last_tried, last_shells = tried, shells
        if kind == "checkpoint":
            while rung_i < len(ladder) and tried >= ladder[rung_i]:
                snapshot(tried, shells)
                rung_i += 1
            continue
        if kind != "point":
            continue
        if (P[0], P[1]) in seen:
            continue
        seen[(P[0], P[1])] = True
        R = E.reduce_point(P, p, root)
        if R is None:
            cum["no_residue"] += 1
            continue
        residues.add(R)
        if K.is_rational(P[0]) and K.is_rational(P[1]):
            cum["rational"] += 1
            continue
        if not ecnf.is_torsion_candidate(E, P, split_for_T, T):
            cum["new_nontorsion"] += 1
            h = K.height(P[0])
            min_height = h if min_height is None else min(min_height, h)
    while rung_i < len(ladder):
        snapshot(last_tried, last_shells)
        rung_i += 1
    return {"rungs": rungs, "gamma": fit_gamma(rungs), "new_nontorsion_points": cum["new_nontorsion"],
            "min_new_point_log_height_over_log_p": (min_height / math.log(p)) if min_height is not None else None,
            "rank_arm": "skipped: no 2-descent over number fields available; new non-torsion point count is a lower bound on rank gain only if the points are independent, which is not certified"}


def regress(xs, ys, rng, boots=1000):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None

    def slope(pr):
        n = len(pr)
        mx = sum(x for x, _ in pr) / n
        my = sum(y for _, y in pr) / n
        sxx = sum((x - mx) ** 2 for x, _ in pr)
        return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in pr) / sxx
    s0 = slope(pairs)
    bs = []
    for _ in range(boots):
        sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        s = slope(sample)
        if s is not None:
            bs.append(s)
    bs.sort()
    return {"slope": s0, "n": len(pairs), "ci99": [bs[int(0.005 * len(bs))], bs[int(0.995 * len(bs)) - 1]] if bs else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kmin", type=int, default=4)
    ap.add_argument("--kmax", type=int, default=12)
    ap.add_argument("--min-bits", type=int, default=12)
    ap.add_argument("--max-primes-per-shape", type=int, default=3)
    ap.add_argument("--random-g", type=int, default=20)
    ap.add_argument("--curves", type=int, default=5)
    ap.add_argument("--ladder", type=int, nargs="+", default=[300, 1000, 3000, 10000, 30000, 100000])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--aux-primes", type=int, default=8)
    ap.add_argument("--shapes", nargs="+", default=list(NIST_SHAPES))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()
    cell_seconds = []
    raw = {"experiment_id": EXP, "hypothesis_id": HYP, "gp_version": gptool.gp_version(),
           "ctrl_shape": check_shapes(), "cells": []}
    for seed in args.seeds:
        rng = random.Random(f"{EXP}:{seed}")
        fields = []
        for name in args.shapes:
            f = NIST_SHAPES[name]
            for k, p in toy_primes_for(f, args.kmin, args.kmax, args.min_bits)[: args.max_primes_per_shape]:
                fields.append({"kind": "solinas", "shape": name, "g": f, "k": k, "p": p, "d": len(f) - 1, "weight": weight(f)})
            d, w = len(f) - 1, weight(f)
            made = 0
            attempts = 0
            while made < args.random_g and attempts < 50 * args.random_g:
                attempts += 1
                g = random_shape(d, w, rng)
                ps = toy_primes_for(g, args.kmin, args.kmax, args.min_bits)
                if not ps:
                    continue
                k, p = ps[0]
                fields.append({"kind": "random_g", "shape": name, "g": g, "k": k, "p": p, "d": d, "weight": w})
                made += 1
            # t^d - c control (EXP-ECDLP-3e8403 form) at the same degree
            for cc in (3, 5, 7, 11, 13):
                g = [-cc] + [0] * (d - 1) + [1]
                ps = toy_primes_for(g, args.kmin, args.kmax, args.min_bits)
                if ps:
                    fields.append({"kind": "tdc", "shape": name, "g": g, "k": ps[0][0], "p": ps[0][1], "d": d, "weight": 2})
                    break
            # Q itself (d = 1) at the shape's first prime
            ps = toy_primes_for(f, args.kmin, args.kmax, args.min_bits)
            if ps:
                fields.append({"kind": "Q", "shape": name, "g": [0, 1], "k": ps[0][0], "p": ps[0][1], "d": 1, "weight": 1})
        for fld in fields:
            fld["g_text"] = poly_text(fld["g"])
            K = nfield.NumberField(fld["g"])
            p = fld["p"]
            root = (2 ** fld["k"]) % p if K.d > 1 else 0
            assert poly_eval(fld["g"], 2 ** fld["k"]) % p == 0 or K.d == 1
            aux = K.degree_one_primes(args.aux_primes, avoid=(p,))
            split_for_T = aux[:6]
            rngo = random.Random(f"{EXP}:order:{seed}:{p}")
            disc = K.discriminant()
            field_rec = dict(fld, disc=disc, root_discriminant=K.root_discriminant(),
                             nfdisc_pari=(gptool.nfdisc(fld["g"]) if K.d > 1 else 1))
            if field_rec["nfdisc_pari"]:
                field_rec["root_discriminant_field"] = abs(field_rec["nfdisc_pari"]) ** (1.0 / K.d)
            for ci, (A, B) in enumerate(seeded_curves(args.curves, p, random.Random(f"{EXP}:curves:{seed}:{fld['shape']}:{fld['k']}"))):
                T = ecnf.torsion_bound(ecnf.CurveNF(K, A, B), split_for_T, lambda q, a, b: ecnf.fp_order_bsgs(q, a, b, rngo))
                t0 = time.time()
                cell = run_cell(K, A, B, p, root, args.ladder, aux, split_for_T, T, seed)
                cell.update({"seed": seed, "field": field_rec, "curve": {"A": str(A), "B": str(B)}, "curve_index": ci,
                             "torsion_bound_T": T})
                raw["cells"].append(cell)
                cell_seconds.append(round(time.time() - t0, 3))
                print(f"seed={seed} {fld['kind']} {fld['shape']} k={fld['k']} curve={ci}: D={cell['rungs'][-1]['distinct_residues']} "
                      f"gamma={cell['gamma']} N={cell['new_nontorsion_points']}", file=sys.stderr, flush=True)
    # summary: per shape, gamma solinas minus random_g, and the regression
    summ = {}
    for cell in raw["cells"]:
        s = summ.setdefault(cell["field"]["shape"], {"solinas": [], "random_g": [], "tdc": [], "Q": []})
        s[cell["field"]["kind"]].append(cell["gamma"])

    def mean(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else None
    for shape, s in summ.items():
        s["gamma_solinas_minus_random_g"] = ((mean(s["solinas"]) or 0) - (mean(s["random_g"]) or 0)
                                            if s["solinas"] and s["random_g"] else None)
    rngb = random.Random(f"{EXP}:boot")
    xs = [math.log(c["field"].get("root_discriminant_field") or c["field"]["root_discriminant"]) for c in raw["cells"] if c["field"]["d"] > 1]
    ys = [c["gamma"] for c in raw["cells"] if c["field"]["d"] > 1]
    raw["summary"] = {"per_shape": summ, "regression_gamma_vs_log_root_discriminant": regress(xs, ys, rngb)}
    raw_path = os.path.join(args.out, "raw-result.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True, default=str)
    here = os.path.dirname(os.path.abspath(__file__))
    manifest = {"experiment_id": EXP, "command": " ".join(sys.argv), "python": platform.python_version(),
                "platform": platform.platform(), "gp_version": raw["gp_version"],
                "source_sha256": {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()
                                  for f in ("run.py", "nfield.py", "ecnf.py", "gptool.py")},
                "raw_result_sha256": hashlib.sha256(open(raw_path, "rb").read()).hexdigest(),
                "started_unix": started, "finished_unix": time.time(),
                "wall_clock_seconds": round(time.time() - started, 3), "cell_seconds": cell_seconds,
                "raw_result_is_replay_deterministic": "raw-result.json carries no timing; CTRL-REPLAY compares it byte for byte",
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
