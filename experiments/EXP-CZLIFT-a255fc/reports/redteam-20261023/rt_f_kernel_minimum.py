"""Red-team check F (TASK-20261023-326d39, joint R1): the arithmetic part of the excess.

Uses rt_e's verified Mordell-Weil data (basis, Gram in PARI's normalization
h^(P) = lim log H(x(nP)) / n^2, coordinates of every point of naive height <= 30000) and plain
Python. For each curve of recalled rank r >= 1 and each of the 16 primes where E(F_p) is cyclic:
  * a_i = discrete log of red_p(B_i) to a generator of E(F_p), so red_p(v) = <v, a> mod N_p
    (checked: the recorded `distinct` of every cell with H <= 30000 is reproduced from <v, a>);
  * lambda1^2(actual) = min canonical height of a non-zero K in ker(red_p), by Fincke-Pohst over
    the Gram matrix; every such K has p^2 | den X(K), so lambda1^2 >= 2 log p - c_E;
  * the same minimum for 100 random homomorphisms g with the SAME image index k_p
    (g uniform in (k_p Z / N_p)^r with gcd(g / k_p, N_p / k_p) = 1);
  * the percentile of the actual minimum in the random distribution, and the frozen-cell
    median recomputed under (i) the actual map and (ii) the random maps.
numpy default_rng(20261023). Non-cyclic E(F_p) is skipped and counted.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt_c_points_kernel_index as C  # noqa: E402
import rt_b_lattice_null as B  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
E_OUT = os.path.join(HERE, "rt_e_mw_coordinate_null_output_H30000.json")
OUT = os.path.join(HERE, "rt_f_kernel_minimum_output.json")


def ec_mul(P, k, A, p):
    R = None
    Q = P
    while k:
        if k & 1:
            R = C.ec_add(R, Q, A, p)
        Q = C.ec_add(Q, Q, A, p)
        k >>= 1
    return R


def find_generator(A, Bc, p, Np, rng):
    qs = list(sympy.factorint(Np).keys())
    for _ in range(200):
        x = int(rng.integers(0, p))
        g = (x ** 3 + A * x + Bc) % p
        if g == 0:
            continue
        y = sympy.sqrt_mod(g, p)
        if y is None:
            continue
        P = (x, int(y))
        if all(ec_mul(P, Np // q, A, p) is not None for q in qs):
            return P
    return None


def frozen(c):
    return c["n_points"] >= 30 and c["model_distinct"] <= 0.9 * c["N_p"]


def upper_median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def main():
    rng = np.random.default_rng(20261023)
    e = json.load(open(E_OUT))
    raw = json.load(open(os.path.join(ROOT, "experiments", "EXP-CZLIFT-a255fc", "runs", "RUN-CZLIFT-490b33", "raw-result.json")))
    curves = {cv["label"]: cv for cv in raw["raw"]["curves"]}
    out = {"normalization": "PARI ellheight, h^ = lim log H(x(nP))/n^2", "curves": {}, "pooled": {}}
    pooled_pct = []
    pooled_gap = []
    actual_ratios, random_medians = [], [[] for _ in range(100)]
    for lab, info in e["curves"].items():
        cv = curves[lab]
        r = cv["rank_recalled"]
        G = np.array(info["gram"])
        Vc = np.vstack([np.zeros((1, r), dtype=np.int64), np.array(info["coords"], dtype=np.int64)])
        A, Bc, b2 = C.short_model(cv["ainvs"])
        basis = [tuple(b) for b in info["basis_naive"]]
        rows = []
        skipped = []
        for p in cv["primes"]:
            Np = C.curve_order(A, Bc, p)
            gen = find_generator(A, Bc, p, Np, rng)
            if gen is None:
                skipped.append(p)
                continue
            table = {}
            P = None
            for k in range(Np):
                table[P] = k
                P = C.ec_add(P, gen, A, p)
            a = np.array([table[C.reduce_pt(b, p, b2)] for b in basis], dtype=np.int64)
            k_p = math.gcd(math.gcd(*[int(x) for x in a]) if r > 1 else int(a[0]), Np)
            # sanity: reproduce recorded distinct for H <= 30000
            img = (Vc @ a) % Np
            mism = 0
            for c in cv["coverage"]:
                if c["p"] == p and c["H"] <= 30000:
                    if len(np.unique(img[: c["n_points"]])) != c["distinct"]:
                        mism += 1
            # enumerate short vectors once, deep enough
            vol = math.pi ** (r / 2) / math.gamma(r / 2 + 1)
            q0 = (Np * math.sqrt(np.linalg.det(G)) / vol) ** (2 / r)
            Q = 2.5 * q0
            while True:
                W = B._enumerate(G, Q)
                qW = np.einsum("ij,jk,ik->i", W, G, W)
                order = np.argsort(qW)
                W, qW = W[order][1:], qW[order][1:]  # drop zero
                hit = np.nonzero(((W @ a) % Np) == 0)[0]
                if len(hit):
                    break
                Q *= 1.5
            lam_actual = float(qW[hit[0]])
            lam_rand = []
            m = Np // k_p
            for t in range(100):
                while True:
                    g = rng.integers(0, m, size=r)
                    if math.gcd(math.gcd(*[int(x) for x in g]) if r > 1 else int(g[0]), m) == 1:
                        break
                g = g * k_p
                h = np.nonzero(((W @ g) % Np) == 0)[0]
                lam_rand.append(float(qW[h[0]]) if len(h) else float("inf"))
                # frozen-cell ratios under this random map (cells with H <= 30000)
                imgr = (Vc @ g) % Np
                for c in cv["coverage"]:
                    if c["p"] == p and c["H"] <= 30000 and frozen(c):
                        random_medians[t].append(len(np.unique(imgr[: c["n_points"]])) / c["model_distinct"])
            for c in cv["coverage"]:
                if c["p"] == p and c["H"] <= 30000 and frozen(c):
                    actual_ratios.append(len(np.unique(img[: c["n_points"]])) / c["model_distinct"])
            pct = float(np.mean([x < lam_actual for x in lam_rand]) + 0.5 * np.mean([x == lam_actual for x in lam_rand]))
            gap = lam_actual - 2 * math.log(p)
            pooled_pct.append(pct)
            pooled_gap.append(gap)
            rows.append({"p": p, "N_p": Np, "k_p": k_p, "distinct_mismatches_H_le_3e4": mism,
                         "lambda1sq_actual": round(lam_actual, 3), "two_log_p": round(2 * math.log(p), 3),
                         "lambda1sq_minus_2logp": round(gap, 3),
                         "lambda1sq_random_median": round(float(np.median(lam_rand)), 3),
                         "lambda1sq_random_p10_p90": [round(float(np.percentile(lam_rand, 10)), 3),
                                                      round(float(np.percentile(lam_rand, 90)), 3)],
                         "percentile_of_actual_in_random": round(pct, 3)})
        out["curves"][lab] = {"rank": r, "skipped_noncyclic": skipped, "rows": rows,
                              "median_percentile": float(np.median([x["percentile_of_actual_in_random"] for x in rows])) if rows else None,
                              "min_lambda1sq_minus_2logp": min(x["lambda1sq_minus_2logp"] for x in rows) if rows else None}
        print(lab, "median pct", out["curves"][lab]["median_percentile"], "min gap", out["curves"][lab]["min_lambda1sq_minus_2logp"],
              "skipped", skipped, "mism", sum(x["distinct_mismatches_H_le_3e4"] for x in rows), flush=True)
    rm = [upper_median(x) for x in random_medians]
    out["pooled"] = {
        "pairs": len(pooled_pct),
        "mean_percentile_of_actual_lambda1": float(np.mean(pooled_pct)),
        "frac_actual_above_random_median": float(np.mean([x > 0.5 for x in pooled_pct])),
        "frozen_cells_H_le_3e4_cyclic_only": len(actual_ratios),
        "median_ratio_actual_map": upper_median(actual_ratios),
        "median_ratio_random_maps_same_index": {"median": float(np.median(rm)), "band_2p5_97p5": [float(np.percentile(rm, 2.5)), float(np.percentile(rm, 97.5))]},
        "min_lambda1sq_minus_2logp_over_all": min(pooled_gap),
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out["pooled"], indent=1))


if __name__ == "__main__":
    main()
