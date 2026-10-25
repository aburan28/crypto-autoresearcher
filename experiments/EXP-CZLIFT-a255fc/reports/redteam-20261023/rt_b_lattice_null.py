"""Red-team check B (TASK-20261023-326d39, joint R1): the structural null.

Question: is the observed coverage-ratio median (1.033) what one gets from ANY lattice ball pushed
through ANY group homomorphism, with no arithmetic of the specific curve?

Model per curve of recalled rank r >= 1 (11a1 has no frozen cells): a random positive-definite Gram
matrix G = M^T M with M = I + 0.2 * Gaussian (a near-orthogonal stand-in for a reduced Mordell-Weil
lattice); the point set at grid height H is the zero vector plus the (n(H) - 1)/2 shortest +-pairs
of Z^r under G, with n(H) the run's recorded count; reduction mod p is replaced by a uniformly
random homomorphism v -> <v, g> mod N_p, g uniform in (Z/N_p)^r (cyclic model of E(F_p)). The
frozen cells (n >= 30, model <= 0.9 N_p) and the producer's ratio and upper median are reused.

What is NOT modelled: the naive-height ball is only approximately a quadratic-form ball; E(F_p)
is not always cyclic; the actual Mordell-Weil Gram matrix is not used.
20 Gram draws x 10 homomorphism draws = 200 replicates per run; numpy default_rng(20261023).
Reads only raw-result.json (counts, N_p, frozen cells, observed medians); imports no producer code.
"""
from __future__ import annotations

import json
import os
import statistics

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RUNS = {"main": "RUN-CZLIFT-74f172", "replication": "RUN-CZLIFT-490b33"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rt_b_lattice_null_output.json")


def frozen(c):
    return c["n_points"] >= 30 and c["model_distinct"] <= 0.9 * c["N_p"]


def upper_median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]


def _enumerate(G, qmax):
    """All integer vectors v with v^T G v <= qmax (Fincke-Pohst)."""
    r = G.shape[0]
    # q(v) = sum_i Q[i,i] (v_i + sum_{j>i} Q[i,j] v_j)^2
    Q = G.astype(float).copy()
    for i in range(r):
        for j in range(i + 1, r):
            Q[j, i] = Q[i, j]
            Q[i, j] = Q[i, j] / Q[i, i]
        for k in range(i + 1, r):
            for l in range(k, r):
                Q[k, l] -= Q[k, i] * Q[i, l]
    out = []
    v = [0] * r

    def rec(i, rem):
        c = -sum(Q[i, j] * v[j] for j in range(i + 1, r))
        span = (rem / Q[i, i]) ** 0.5
        lo, hi = int(np.ceil(c - span - 1e-12)), int(np.floor(c + span + 1e-12))
        for x in range(lo, hi + 1):
            t = Q[i, i] * (x - c) ** 2
            if t > rem + 1e-12:
                continue
            v[i] = x
            if i == 0:
                out.append(list(v))
            else:
                rec(i - 1, rem - t)
        v[i] = 0

    rec(r - 1, qmax)
    return np.array(out, dtype=np.int64)


def shortest_vectors(G, n_needed, rng):
    r = G.shape[0]
    vol_unit = np.pi ** (r / 2) / __import__("math").gamma(r / 2 + 1)
    qmax = (1.2 * n_needed * np.sqrt(np.linalg.det(G)) / vol_unit) ** (2 / r)
    while True:
        V = _enumerate(G, qmax)
        if len(V) >= n_needed + 2:
            q = np.einsum("ij,jk,ik->i", V, G, V)
            order = np.argsort(q, kind="stable")
            # zero vector first, then +-pairs with equal keys; n_needed is odd
            return V[order[:n_needed]], qmax
        qmax *= 1.3


def run_one(curves, rng, n_gram=20, n_hom=10):
    meds = []
    per_curve = {cv["label"]: [] for cv in curves if cv["rank_recalled"] >= 1}
    for _ in range(n_gram):
        sets = {}
        for cv in curves:
            r = cv["rank_recalled"]
            if r < 1:
                continue
            nmax = max(cv["counts"].values())
            M = np.eye(r) + 0.2 * rng.standard_normal((r, r))
            G = M.T @ M
            V, _ = shortest_vectors(G, nmax, rng)
            sets[cv["label"]] = V
        for _ in range(n_hom):
            ratios = []
            cur = {lab: [] for lab in per_curve}
            for cv in curves:
                if cv["rank_recalled"] < 1:
                    continue
                V = sets[cv["label"]]
                for p in cv["primes"]:
                    rows = [c for c in cv["coverage"] if c["p"] == p and frozen(c)]
                    if not rows:
                        continue
                    Np = rows[0]["N_p"]
                    g = rng.integers(0, Np, size=V.shape[1])
                    img = (V @ g) % Np
                    for c in rows:
                        d = len(np.unique(img[: c["n_points"]]))
                        rr = d / c["model_distinct"]
                        ratios.append(rr)
                        cur[cv["label"]].append(rr)
            meds.append(upper_median(ratios))
            for lab, xs in cur.items():
                if xs:
                    per_curve[lab].append(upper_median(xs))
    return meds, per_curve


def main():
    rng = np.random.default_rng(20261023)
    out = {"seed": 20261023, "model": "random Gram (I + 0.2 N(0,1)), random homomorphism to Z/N_p", "runs": {}}
    for tag, run in RUNS.items():
        raw = json.load(open(os.path.join(ROOT, "experiments", "EXP-CZLIFT-a255fc", "runs", run, "raw-result.json")))
        curves = raw["raw"]["curves"]
        observed = raw["metrics"]["coverage_ratio_median"]
        obs_pc = {}
        for cv in curves:
            xs = [c["ratio_to_model"] for c in cv["coverage"] if frozen(c)]
            if xs:
                obs_pc[cv["label"]] = upper_median(xs)
        meds, pc = run_one(curves, rng)
        out["runs"][run] = {
            "observed_median": observed,
            "lattice_null_median_of_medians": float(np.median(meds)),
            "lattice_null_band_2p5_97p5": [float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))],
            "lattice_null_reps_ge_observed": int(sum(m >= observed for m in meds)),
            "reps": len(meds),
            "per_curve": {lab: {"observed_median": obs_pc.get(lab),
                                "lattice_null_median": float(np.median(v)),
                                "lattice_null_band_2p5_97p5": [float(np.percentile(v, 2.5)),
                                                               float(np.percentile(v, 97.5))]}
                          for lab, v in pc.items() if v},
        }
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
