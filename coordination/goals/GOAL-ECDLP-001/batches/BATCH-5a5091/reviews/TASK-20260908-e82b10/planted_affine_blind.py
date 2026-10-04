#!/usr/bin/env python3
"""Blind re-derivation of Stage 0 planted affine and shuffle.

Uses only the frozen fixture numbers named in
review_plan_s0.yaml: N=8191, D=20, V={0..19},
k_v=(3*v+7) mod 8191, lambda=identity, shuffle
seed 20260908. Must not import or read the
Stage 0 producer or its run artifacts.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

N = 8191
D = 20
V = list(range(D))
PLANTED_A = 3
PLANTED_B = 7
SHUFFLE_SEED = 20260908
THETAS = (1.0 / 3.0, 0.5, 1.0)
REL_TOL = 1e-12
FORBIDDEN = [
    Path("experiments/EXP-ECDLP-420e73/implementation/stage0_planted_affine.py"),
    Path("experiments/EXP-ECDLP-420e73/runs/RUN-ECDLP-420e73-S0/raw-result.json"),
    Path("experiments/EXP-ECDLP-420e73/execution-report-s0.yaml"),
]


def recover_exact_affine(vs: list[int], ks: list[int]) -> tuple[bool, int | None, int | None]:
    """Unique (a,b) in 0..N-1 with k = a*v+b mod N for every v."""
    hits: set[tuple[int, int]] = set()
    for i in range(len(vs)):
        for j in range(i + 1, len(vs)):
            dv = (vs[i] - vs[j]) % N
            if dv == 0:
                continue
            dk = (ks[i] - ks[j]) % N
            a = (dk * pow(dv, -1, N)) % N
            b = (ks[i] - a * vs[i]) % N
            if all((a * v + b) % N == k for v, k in zip(vs, ks)):
                hits.add((a, b))
    if len(hits) == 1:
        a, b = next(iter(hits))
        return True, a, b
    return False, None, None


def identity_rows() -> list[dict]:
    rows = []
    for theta in THETAS:
        s = float(N) ** theta
        t = float(N) ** (1.0 - theta)
        predicted = 2.0 - theta
        realized = math.log(s * t * t) / math.log(N)
        rel = abs(realized - predicted) / abs(predicted)
        rows.append(
            {
                "theta": theta,
                "predicted_logN_ST2": predicted,
                "realized_logN_ST2": realized,
                "relative_error": rel,
            }
        )
    return rows


def main() -> int:
    for path in FORBIDDEN:
        # Existence is allowed; opening is not.
        _ = path
    planted_k = [(PLANTED_A * v + PLANTED_B) % N for v in V]
    planted_ok, planted_a, planted_b = recover_exact_affine(V, planted_k)
    shuffled_k = np.random.default_rng(SHUFFLE_SEED).permutation(planted_k).tolist()
    shuffle_ok, shuffle_a, shuffle_b = recover_exact_affine(V, shuffled_k)
    id_rows = identity_rows()
    identity_pass = all(row["relative_error"] <= REL_TOL for row in id_rows)
    out = {
        "fixture": {
            "N": N,
            "D": D,
            "V": V,
            "planted_a": PLANTED_A,
            "planted_b": PLANTED_B,
            "shuffle_seed": SHUFFLE_SEED,
            "units": "N-unit S=N^theta from idea (B)",
        },
        "identity": {
            "identity_pass": identity_pass,
            "rows": id_rows,
        },
        "planted": {
            "recovers_exact_affine": planted_ok,
            "a_hat": planted_a,
            "b_hat": planted_b,
        },
        "shuffle": {
            "recovers_exact_affine": shuffle_ok,
            "a_hat": shuffle_a,
            "b_hat": shuffle_b,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "not_an_H1_claim": True,
    }
    dest = Path(__file__).with_name("blind_raw.json")
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
