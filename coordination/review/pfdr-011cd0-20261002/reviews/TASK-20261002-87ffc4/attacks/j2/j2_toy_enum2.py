"""J2 follow-up enumeration (declared after reading toy_enum.json; reason: Part A's
engine-rule count under U used a U-extension that drops tails through a
zero base log, which is not L1's null event, and Part C2 at N = 13, s = 6 is
degenerate -- the base exhausts all six +-classes, so every admissible L gives
the same count).

  A2  h = 2, s = 4, N = 31, every L in (Z/31)^4: engine count with IDENTITY-ONLY
      drops (a stored vector u is absent iff u.L == 0; base elements absent iff
      L_b == 0). Checks R_engine == R* and nP_engine == nP* exactly outside L1's
      null event (two distinct elements both the identity), and P(null event)
      against L1's bound |V|/N.
  C3  h = 3 under the engine's admissible law (L_i != 0, L_i != +-L_j), Monte
      Carlo: (s, N) in {(6, 61), (8, 1009)}, 20000 draws each, seed
      SeedSequence([0x87ffc4, 2, s, N]). Stored set by the validated tail_rule
      with its L-dependent drops; reports how often it differs from the formal
      set, whether R_engine == R* on every draw, and E, Var of R against L1.
  G   h = 2 admissible law, scale series (s, N) in {(10, 10007), (20, 10007),
      (30, 10007), (30, 100003), (60, 100003)}, 20000 draws each, seed
      SeedSequence([0x87ffc4, 3, s, N]): E[R], D_R of the engine count against
      L1's |RR|/N and 1 - 1/N, as s^2/N falls.
  E2  PTM-L early-return selection at N = 1009, s = 8 (h = 2), admissible law,
      20000 draws, seed SeedSequence([0x87ffc4, 4]): elements taken in stored
      order, collection ends at the first x-coincidence (counted); moments
      against L1.
Command: nice -n 19 $PY attacks/j2/j2_toy_enum2.py --out attacks/j2/out/toy_enum2.json
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j2lib  # noqa: E402
from j2_toy_enum import all_L, dot, moments, f  # noqa: E402


def part_A2(N=31, s=4, h=2):
    Ls = all_L(N, s)
    tails0 = j2lib.tail_rule(s, h)
    tt_el, _deg, _seen = j2lib.harvester_elements(tails0, s)
    base = []
    for b in range(s):
        e = [0] * s
        e[b] = 1
        base.append(tuple(e))
    vals = {v: dot(Ls, v, N).astype(np.int32) for v in tt_el + base}
    # null event: two distinct elements of the relevant element set both identity
    out = {}
    for cname, elems, pairs in (
            ("TT", tt_el, list(itertools.combinations(tt_el, 2))),
            ("TB", tt_el + base, [(b, u) for b in base for u in tt_el])):
        zeros = np.zeros(len(Ls), dtype=np.int64)
        for v in elems:
            zeros += (vals[v] == 0)
        null = zeros >= 2
        classes, _ = j2lib.signed_pair_classes(pairs, N)
        Rstar = np.zeros(len(Ls), dtype=np.int64)
        Reng = np.zeros(len(Ls), dtype=np.int64)
        nPstar = np.zeros(len(Ls), dtype=np.int64)
        nPeng = np.zeros(len(Ls), dtype=np.int64)
        for key, members in classes.items():
            I = dot(Ls, key, N) == 0
            Rstar += I
            nPstar += len(members) * I
            hit = np.zeros(len(Ls), dtype=bool)
            for idx, sg in members:
                u, w = pairs[idx]
                co = (vals[u] != 0) & (vals[w] != 0) & ((vals[u] - sg * vals[w]) % N == 0)
                hit |= co
                nPeng += co
            Reng += hit
        out[cname] = {
            "P_null_event": float(null.mean()),
            "L1_bound_V_over_N": len(elems) / N,
            "R_engine_eq_Rstar_outside_null": bool(np.all(Reng[~null] == Rstar[~null])),
            "nP_engine_eq_nPstar_outside_null": bool(np.all(nPeng[~null] == nPstar[~null])),
            "P_R_ne_on_null": float(np.mean(Reng[null] != Rstar[null])) if null.any() else None,
            "E_R_engine": float(Reng.mean()), "E_Rstar": float(Rstar.mean()),
            "rel_dev_E_R_engine_vs_formula": float(Reng.mean() / Rstar.mean() - 1),
            "rel_dev_Var_R_engine_vs_formula": float(Reng.var() / Rstar.var() - 1),
        }
    return out


def sample_admissible(rng, N, s):
    # s distinct +-classes among 1..(N-1)/2, random sign each
    cls = rng.choice(np.arange(1, (N - 1) // 2 + 1), size=s, replace=False)
    sg = rng.choice(np.array([1, -1]), size=s)
    return [int((c * g) % N) for c, g in zip(cls, sg)]


def engine_count(L, N, s, h, tt_only=True):
    """Engine-rule TT count for one L: stored set by tail_rule with drops,
    formal dedup up to sign, +-e_b removed; coincident pairs and distinct
    relation classes (monic over F_N)."""
    tails = j2lib.tail_rule(s, h, L, N)
    tt_el, _deg, _seen = j2lib.harvester_elements(tails, s)
    groups = {}
    for v in tt_el:
        val = sum(c * l for c, l in zip(v, L)) % N
        if val == 0:
            continue
        key = min(val, N - val)
        groups.setdefault(key, []).append((v, val))
    nP = 0
    rels = set()
    for g in groups.values():
        for (u, uv), (w, wv) in itertools.combinations(g, 2):
            sg = 1 if uv == wv else -1
            r = tuple(a - sg * b for a, b in zip(u, w))
            k = j2lib.monic_mod(r, N)
            if k is None:
                continue
            nP += 1
            rels.add(k)
    return len(tails), nP, len(rels), rels


def class_table(s, h, N):
    tails0 = j2lib.tail_rule(s, h)
    tt_el, _deg, _seen = j2lib.harvester_elements(tails0, s)
    pairs = list(itertools.combinations(tt_el, 2))
    classes, excl = j2lib.signed_pair_classes(pairs, N)
    keys = list(classes)
    K = np.array(keys, dtype=np.int32)
    M = np.array([len(classes[k]) for k in keys], dtype=np.int64)
    return len(tails0), keys, K, M, excl


def part_C3_G(configs, h, seed_tag, draws=20000):
    res = []
    for s, N in configs:
        t0 = time.time()
        n_formal, keys, K, M, excl = class_table(s, h, N)
        RR = len(keys)
        rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, seed_tag, s, N]))
        Rs, Rst, nPs, nPst = [], [], [], []
        differ_set = 0
        mismatch = 0
        for _ in range(draws):
            L = sample_admissible(rng, N, s)
            n_st, nP, R, rels = engine_count(L, N, s, h)
            Larr = np.array(L, dtype=np.int64)
            I = (K @ Larr) % N == 0
            Rstar = int(I.sum())
            nPstar = int(M[I].sum())
            if n_st != n_formal:
                differ_set += 1
            if R != Rstar or nP != nPstar:
                mismatch += 1
            Rs.append(R)
            Rst.append(Rstar)
            nPs.append(nP)
            nPst.append(nPstar)
        Rs = np.array(Rs, dtype=float)
        nPs = np.array(nPs, dtype=float)
        ER_f = RR / N
        VR_f = RR / N * (1 - 1 / N)
        se_mean = Rs.std(ddof=1) / np.sqrt(draws)
        res.append({
            "s": s, "N": N, "h": h, "draws": draws, "s2_over_N": s * s / N,
            "formal_stored": n_formal, "RR": RR, "excluded_signed_pairs": excl,
            "draws_with_stored_set_ne_formal": differ_set,
            "draws_R_or_nP_engine_ne_representation": mismatch,
            "E_R": float(Rs.mean()), "E_R_formula": ER_f,
            "E_R_ratio": float(Rs.mean() / ER_f), "E_R_ratio_mc_se": float(se_mean / ER_f),
            "Var_R": float(Rs.var(ddof=1)), "Var_R_formula": VR_f,
            "D_R": float(Rs.var(ddof=1) / Rs.mean()) if Rs.mean() else None,
            "D_R_formula": 1 - 1 / N,
            "E_nP": float(nPs.mean()), "E_nP_formula": float(M.sum() / N),
            "D_P": float(nPs.var(ddof=1) / nPs.mean()) if nPs.mean() else None,
            "D_P_formula": float((1 - 1 / N) * (M * M).sum() / M.sum()),
            "seconds": time.time() - t0})
        print(res[-1], flush=True)
    return res


def part_E2(N=1009, s=8, h=2, draws=20000):
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 4]))
    tails0 = j2lib.tail_rule(s, h)
    tt_el, _deg, _seen = j2lib.harvester_elements(tails0, s)
    _n, keys, K, M, _ = class_table(s, h, N)
    counts = []
    for _ in range(draws):
        L = sample_admissible(rng, N, s)
        seen = {}
        c = 0
        for v in tt_el:
            val = sum(a * b for a, b in zip(v, L)) % N
            key = min(val, N - val)
            if key in seen:
                c = 1
                break
            seen[key] = v
        counts.append(c)
    counts = np.array(counts, dtype=float)
    return {"N": N, "s": s, "h": h, "draws": draws,
            "E_nP_early_return": float(counts.mean()), "Var_nP_early_return": float(counts.var(ddof=1)),
            "E_nP_formula_fixed_set": float(M.sum() / N),
            "Var_nP_formula_fixed_set": float((M * M).sum() / N * (1 - 1 / N))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    res = {"task": "TASK-20261002-87ffc4", "joint": "J2", "parts": {}}
    res["parts"]["A2_identity_only_U"] = part_A2()
    print(res["parts"]["A2_identity_only_U"], flush=True)
    res["parts"]["C3_h3_admissible_mc"] = part_C3_G([(6, 61), (8, 1009)], 3, 2)
    res["parts"]["G_h2_admissible_scale"] = part_C3_G(
        [(10, 10007), (20, 10007), (30, 10007), (30, 100003)], 2, 3)
    res["parts"]["E2_early_return_mc"] = part_E2()
    res["seconds"] = time.time() - t0
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res["parts"]["E2_early_return_mc"]))


if __name__ == "__main__":
    main()
