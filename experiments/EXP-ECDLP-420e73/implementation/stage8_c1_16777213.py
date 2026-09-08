#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 8 C1 interpolant at p=16777213. Certificate kind none."""
from __future__ import annotations

import json
import math
import platform
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage8_c1_16777213.py"
P_FIELD = 16777213
D = 20
HEADER_BITS = 64
NULL2_SEED = 20260908

T2 = {
    "id": "S7-T2-P16777213",
    "p": P_FIELD,
    "a": 19,
    "b": 107,
    "N": 16777213,
    "field": 16777213,
    "P": (0, 1722727),
    "V": [0, 14386069, 13311471, 510744, 13641516, 11286066, 16703438, 13064901, 3436861, 9847978, 4422270, 2431989, 8626592, 2704728, 8015097, 11447766, 8129445, 341717, 16207358, 12600408],
}
T1 = {
    "id": "S7-T1-P16777213",
    "p": P_FIELD,
    "a": 0,
    "b": 7,
    "N": 16770451,
    "field": 16770451,
    "P": (6, 7827705),
    "V": [6, 4288347, 2837810, 15061002, 7941042, 3891067, 6883471, 15571429, 15172588, 6789969, 6889484, 865709, 4039235, 6596143, 14029655, 5242584, 7908075, 2872040, 4197418, 1510565],
}


def add(p: int, a: int, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def multiples(cell: dict) -> list[tuple[int, tuple[int, int]]]:
    p, a = cell["p"], cell["a"]
    R = None
    rows = []
    for k in range(1, D + 1):
        R = add(p, a, R, cell["P"])
        if R is None:
            raise RuntimeError(f"{cell['id']}: [k]P hit O at k={k}")
        if R[0] != cell["V"][k - 1]:
            raise RuntimeError(f"{cell['id']}: V mismatch at k={k}")
        rows.append((k, R))
    return rows


def poly_mul_linear(coeffs: list[int], neg_root: int, field: int) -> list[int]:
    out = [0] * (len(coeffs) + 1)
    for i, c in enumerate(coeffs):
        out[i] = (out[i] + c * neg_root) % field
        out[i + 1] = (out[i + 1] + c) % field
    return out


def interpolate(xs: list[int], ys: list[int], field: int) -> list[int]:
    n = len(xs)
    if n != D or len(ys) != D:
        raise RuntimeError("interpolant requires exactly D distinct pairs")
    if len(set(x % field for x in xs)) != n:
        raise RuntimeError("abscissae are not distinct in the field")
    coeffs = [0] * n
    for i in range(n):
        numer = [1]
        denom = 1
        xi = xs[i] % field
        for j in range(n):
            if i == j:
                continue
            xj = xs[j] % field
            numer = poly_mul_linear(numer, (-xj) % field, field)
            denom = denom * ((xi - xj) % field) % field
        scale = (ys[i] % field) * pow(denom, -1, field) % field
        for k, c in enumerate(numer):
            coeffs[k] = (coeffs[k] + c * scale) % field
    for i, x in enumerate(xs):
        acc = 0
        xp = 1
        xv = x % field
        for c in coeffs:
            acc = (acc + c * xp) % field
            xp = xp * xv % field
        if acc != ys[i] % field:
            raise RuntimeError(f"interpolant failed to recover y at i={i}")
    return coeffs


def degree_nnz(coeffs: list[int]) -> tuple[int, int]:
    nnz = sum(1 for c in coeffs if c != 0)
    deg = -1
    for i, c in enumerate(coeffs):
        if c != 0:
            deg = i
    return deg, nnz


def bitlen_field(q: int) -> int:
    return math.ceil(math.log2(q))


def s_c_dense(q: int) -> int:
    return HEADER_BITS + D * bitlen_field(q)


def s_c_sparse(q: int, nnz: int) -> int:
    return HEADER_BITS + nnz * (math.ceil(math.log2(D)) + bitlen_field(q))


def gammas(s_bits: int, n: int) -> dict:
    denom_power = D * math.log2(n)
    denom_linear = D * math.log2(n / D)
    return {
        "S_C_bits": s_bits,
        "gamma_power": 1.0 - math.log(s_bits) / math.log(denom_power),
        "gamma_linear": 1.0 - s_bits / denom_linear,
    }


def c1_arm(xs: list[int], ks: list[int], field: int, n: int, label: str) -> dict:
    coeffs = interpolate(xs, ks, field)
    deg, nnz = degree_nnz(coeffs)
    sparse_terms = [[j, c] for j, c in enumerate(coeffs) if c != 0]
    dense = gammas(s_c_dense(field), n)
    sparse = gammas(s_c_sparse(field, nnz), n)
    return {
        "label": label,
        "field": field,
        "N": n,
        "degree": deg,
        "nnz": nnz,
        "coefficients": coeffs,
        "sparse_terms": sparse_terms,
        "S_C_dense": dense["S_C_bits"],
        "S_C_sparse": sparse["S_C_bits"],
        "gamma_power_dense": dense["gamma_power"],
        "gamma_linear_dense": dense["gamma_linear"],
        "gamma_power_sparse": sparse["gamma_power"],
        "gamma_linear_sparse": sparse["gamma_linear"],
    }


def null2_ks(ks: list[int]) -> list[int]:
    shuffled = list(ks)
    random.Random(NULL2_SEED).shuffle(shuffled)
    return shuffled


def evaluate_cell(cell: dict) -> dict:
    rows = multiples(cell)
    vs = [R[0] for _, R in rows]
    ks = [k for k, _ in rows]
    return {
        "id": cell["id"],
        "p": cell["p"],
        "a": cell["a"],
        "b": cell["b"],
        "N": cell["N"],
        "field": cell["field"],
        "generator_P": list(cell["P"]),
        "V": cell["V"],
        "k": ks,
        "C1": c1_arm(vs, ks, cell["field"], cell["N"], "C1"),
    }


def main() -> int:
    t0 = time.perf_counter()
    t2 = evaluate_cell(T2)
    t1 = evaluate_cell(T1)
    t1_vs = t1["V"]
    t1_ks = t1["k"]
    t1_null2_ks = null2_ks(t1_ks)
    t1_null2 = c1_arm(t1_vs, t1_null2_ks, T1["field"], T1["N"], "C1-NULL2")
    fixture_pass = True
    raw = {
        "run_id": "RUN-ECDLP-420e73-S8",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 8,
        "authorized_by": "DEC-20260908-7fea98",
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "T2_C1_high_degree_is_not_failed_infrastructure": True,
        "C1_miss_is_not_H1_closure": True,
        "T2": t2,
        "T1": t1,
        "T1_NULL2": {
            "seed": NULL2_SEED,
            "algorithm": "random.Random(20260908).shuffle",
            "k_shuffled": t1_null2_ks,
            "C1": t1_null2,
        },
        "T2_C1_degree": t2["C1"]["degree"],
        "T2_C1_nnz": t2["C1"]["nnz"],
        "T1_C1_degree": t1["C1"]["degree"],
        "T1_C1_nnz": t1["C1"]["nnz"],
        "T1_NULL2_C1_degree": t1_null2["degree"],
        "T1_NULL2_C1_nnz": t1_null2["nnz"],
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": (
            "Toy C1 interpolant on frozen Stage 7 cells at p=16777213. "
            "T2 C1 high degree is class inadequacy, not failed_infrastructure. "
            "A C1 miss is not H1 closure. Not H1. Not a W class. "
            "No a98ea9 Stage 5. Gammas are observations."
        ),
        "wall_clock_seconds": time.perf_counter() - t0,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source": SOURCE,
        "null2_seed": NULL2_SEED,
        "workspace_root_unused": str(ROOT),
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if fixture_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
