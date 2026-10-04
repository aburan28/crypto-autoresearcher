#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 9 C2 Berlekamp-Massey at p=16777213. Certificate kind none.

Sequence is k in increasing-v order. k-order 1,2,...,D is forbidden.
"""
from __future__ import annotations

import json
import math
import platform
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage9_c2_16777213.py"
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


def increasing_v_sequence(vs: list[int], ks: list[int], field: int) -> list[int]:
    if len(vs) != D or len(ks) != D:
        raise RuntimeError("sequence requires exactly D pairs")
    if len(set(v % field for v in vs)) != D:
        raise RuntimeError("V values are not distinct in the interpolation ring")
    if any(k < 1 or k > D for k in ks):
        raise RuntimeError("k values are not in 1..D")
    pairs = sorted(((int(v) % field, int(k)) for v, k in zip(vs, ks)), key=lambda t: t[0])
    seq = [k for _, k in pairs]
    if seq == list(range(1, D + 1)):
        raise RuntimeError("k-order 1,2,...,D is forbidden")
    return seq


def berlekamp_massey(seq: list[int], field: int) -> tuple[int, list[int]]:
    """Linear complexity L and connection polynomial C with C(0)=1.

    C is [1, c_1, ..., c_L] over the prime field. Massey's algorithm.
    """
    if field < 2:
        raise RuntimeError("field modulus must be at least 2")
    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1
    for n, s_n in enumerate(seq):
        d = s_n % field
        for i in range(1, min(L, len(C) - 1) + 1):
            d = (d + C[i] * (seq[n - i] % field)) % field
        if d == 0:
            m += 1
            continue
        T = C[:]
        scale = (d * pow(b, -1, field)) % field
        need = len(B) + m
        if len(C) < need:
            C = C + [0] * (need - len(C))
        for i, bi in enumerate(B):
            C[i + m] = (C[i + m] - scale * bi) % field
        if 2 * L <= n:
            L = n + 1 - L
            B = T
            b = d
            m = 1
        else:
            m += 1
    if C[0] % field != 1:
        raise RuntimeError("connection polynomial does not satisfy C(0)=1")
    if len(C) < L + 1:
        C = C + [0] * (L + 1 - len(C))
    C = [c % field for c in C[: L + 1]]
    return L, C


def bitlen_field(q: int) -> int:
    return math.ceil(math.log2(q))


def s_c(q: int, L: int) -> int:
    bits = bitlen_field(q)
    if L == 0:
        return HEADER_BITS + bits
    if L < 0:
        raise RuntimeError("negative linear complexity")
    return HEADER_BITS + 2 * L * bits


def gammas(s_bits: int, n: int) -> dict:
    denom_power = D * math.log2(n)
    denom_linear = D * math.log2(n / D)
    return {
        "S_C_bits": s_bits,
        "gamma_power": 1.0 - math.log(s_bits) / math.log(denom_power),
        "gamma_linear": 1.0 - s_bits / denom_linear,
    }


def c2_arm(vs: list[int], ks: list[int], field: int, n: int, label: str) -> dict:
    seq = increasing_v_sequence(vs, ks, field)
    L, C = berlekamp_massey(seq, field)
    sc = s_c(field, L)
    g = gammas(sc, n)
    return {
        "label": label,
        "field": field,
        "N": n,
        "increasing_v_k": seq,
        "L": L,
        "connection_polynomial": C,
        "C0": C[0],
        "S_C": sc,
        "bitlen_field": bitlen_field(field),
        "gamma_power": g["gamma_power"],
        "gamma_linear": g["gamma_linear"],
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
        "C2": c2_arm(vs, ks, cell["field"], cell["N"], "C2"),
    }


def _self_check_k_order_is_l2_and_forbidden() -> None:
    """Development control: k-order has L=2 and must be refused as a Stage 9 sequence."""
    ks = list(range(1, D + 1))
    L, C = berlekamp_massey(ks, T2["field"])
    if L != 2 or C != [1, (T2["field"] - 2) % T2["field"], 1]:
        raise RuntimeError(f"k-order BM self-check failed: L={L} C={C}")
    try:
        increasing_v_sequence(list(range(D)), ks, T2["field"])
    except RuntimeError as exc:
        if "forbidden" not in str(exc):
            raise
    else:
        raise RuntimeError("k-order increasing-v guard failed to refuse")


def main() -> int:
    t0 = time.perf_counter()
    _self_check_k_order_is_l2_and_forbidden()
    t2 = evaluate_cell(T2)
    t1 = evaluate_cell(T1)
    t1_vs = t1["V"]
    t1_ks = t1["k"]
    t1_null2_ks = null2_ks(t1_ks)
    t1_null2 = c2_arm(t1_vs, t1_null2_ks, T1["field"], T1["N"], "C2-NULL2")
    if t2["C2"]["increasing_v_k"] == list(range(1, D + 1)):
        raise RuntimeError("T2 sequence collapsed to k-order")
    if t1["C2"]["increasing_v_k"] == list(range(1, D + 1)):
        raise RuntimeError("T1 sequence collapsed to k-order")
    fixture_pass = True
    raw = {
        "run_id": "RUN-ECDLP-420e73-S9",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 9,
        "authorized_by": "DEC-20260908-4deaab",
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "T2_C2_high_L_is_not_failed_infrastructure": True,
        "C2_miss_is_not_H1_closure": True,
        "k_order_forbidden": True,
        "T2": t2,
        "T1": t1,
        "T1_NULL2": {
            "seed": NULL2_SEED,
            "algorithm": "random.Random(20260908).shuffle",
            "k_shuffled": t1_null2_ks,
            "C2": t1_null2,
        },
        "T2_C2_L": t2["C2"]["L"],
        "T1_C2_L": t1["C2"]["L"],
        "T1_NULL2_C2_L": t1_null2["L"],
        "T2_increasing_v_k": t2["C2"]["increasing_v_k"],
        "T1_increasing_v_k": t1["C2"]["increasing_v_k"],
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": (
            "Toy C2 Berlekamp-Massey on frozen Stage 7 cells at p=16777213. "
            "Sequence is k in increasing-v order. k-order is forbidden. "
            "T2 C2 high L is class inadequacy, not failed_infrastructure. "
            "A C2 miss is not H1 closure. Not H1. Not a W class. "
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
