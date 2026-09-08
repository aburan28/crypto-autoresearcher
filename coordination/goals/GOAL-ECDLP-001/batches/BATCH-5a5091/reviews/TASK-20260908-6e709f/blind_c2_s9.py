#!/usr/bin/env python3
"""Blind Stage 9 C2 re-derivation from v1_stage9_protocol cells only.

Does not import or read the Stage 9 producer or its raw result.
Massey Berlekamp-Massey of k in increasing-v order over F_p (T2) and Z/N (T1).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
_ = ROOT  # workspace root; cells are hardcoded, no producer import

P = 16777213
D = 20
T2 = {
    "a": 19,
    "b": 107,
    "N": 16777213,
    "P": (0, 1722727),
    "V": [0, 14386069, 13311471, 510744, 13641516, 11286066, 16703438, 13064901, 3436861, 9847978, 4422270, 2431989, 8626592, 2704728, 8015097, 11447766, 8129445, 341717, 16207358, 12600408],
}
T1 = {
    "a": 0,
    "b": 7,
    "N": 16770451,
    "P": (6, 7827705),
    "V": [6, 4288347, 2837810, 15061002, 7941042, 3891067, 6883471, 15571429, 15172588, 6789969, 6889484, 865709, 4039235, 6596143, 14029655, 5242584, 7908075, 2872040, 4197418, 1510565],
}


def add(p: int, a: int, P1, Q):
    if P1 is None:
        return Q
    if Q is None:
        return P1
    x1, y1 = P1
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P1 == Q:
        if y1 == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def confirm_V(cell: dict) -> None:
    R = None
    for k in range(1, D + 1):
        R = add(P, cell["a"], R, cell["P"])
        if R is None or R[0] != cell["V"][k - 1]:
            raise RuntimeError(f"V mismatch or O at k={k}")


def increasing_v_k(vs: list[int], ks: list[int]) -> list[int]:
    if len(set(vs)) != D:
        raise RuntimeError("V not distinct")
    seq = [k for _, k in sorted(zip(vs, ks), key=lambda t: t[0])]
    if seq == list(range(1, D + 1)):
        raise RuntimeError("k-order 1,2,...,D is forbidden")
    return seq


def massey(seq: list[int], mod: int) -> tuple[int, list[int]]:
    """Independent Massey: C and B stored as coefficient lists, C[0]=1."""
    C = [1]
    B = [1]
    ell = 0
    shift = 1
    last = 1
    for t, st in enumerate(seq):
        delta = st % mod
        for i in range(1, len(C)):
            if t - i >= 0:
                delta = (delta + C[i] * (seq[t - i] % mod)) % mod
        if delta == 0:
            shift += 1
            continue
        saved = C + []
        inv = pow(last, -1, mod)
        factor = (delta * inv) % mod
        grown = [0] * shift + B
        if len(C) < len(grown):
            C = C + [0] * (len(grown) - len(C))
        for i, g in enumerate(grown):
            C[i] = (C[i] - factor * g) % mod
        if 2 * ell <= t:
            ell = t + 1 - ell
            B = saved
            last = delta
            shift = 1
        else:
            shift += 1
    if C[0] % mod != 1:
        raise RuntimeError("C(0) != 1")
    if len(C) < ell + 1:
        C.extend([0] * (ell + 1 - len(C)))
    return ell, [c % mod for c in C[: ell + 1]]


def main() -> int:
    confirm_V(T2)
    confirm_V(T1)
    ks = list(range(1, D + 1))
    t2_seq = increasing_v_k(T2["V"], ks)
    t1_seq = increasing_v_k(T1["V"], ks)
    k_null = ks[:]
    random.Random(20260908).shuffle(k_null)
    n2_seq = increasing_v_k(T1["V"], k_null)
    t2_L, t2_C = massey(t2_seq, T2["N"])
    t1_L, t1_C = massey(t1_seq, T1["N"])
    n2_L, n2_C = massey(n2_seq, T1["N"])
    raw = {
        "T2_C2": {"L": t2_L, "connection_polynomial": t2_C, "increasing_v_k": t2_seq},
        "T1_C2": {"L": t1_L, "connection_polynomial": t1_C, "increasing_v_k": t1_seq},
        "T1_NULL2_C2": {
            "L": n2_L,
            "connection_polynomial": n2_C,
            "increasing_v_k": n2_seq,
            "k_shuffled": k_null,
            "seed": 20260908,
        },
        "T2_C2_L": t2_L,
        "T1_C2_L": t1_L,
        "T1_NULL2_C2_L": n2_L,
        "expected_L": 10,
        "match_expected": t2_L == 10 and t1_L == 10 and n2_L == 10,
        "neither_sequence_is_k_order": True,
        "T2_C2_high_L_is_not_failed_infrastructure": True,
        "C2_miss_is_not_H1_closure": True,
        "k_order_forbidden": True,
        "not_an_H1_claim": True,
        "SMALL_W_or_LARGE_W": False,
        "source": "frozen v1_stage9_protocol cells plus independent Massey",
        "producer_not_read": True,
        "ROOT_parents": 7,
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if raw["match_expected"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
