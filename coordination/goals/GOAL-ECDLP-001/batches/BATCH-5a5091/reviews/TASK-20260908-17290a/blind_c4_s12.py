#!/usr/bin/env python3
"""Blind re-derivation of Stage 12 C4 S_C from v1_stage12_protocol only.

Does not import the producer. Workspace root is parents[7] from this path.
"""
from __future__ import annotations

import json
import math
import random
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
D = 20
NULL2_SEED = 20260908
ZLIB_LEVEL = 9

K_INC_PINS = {
    "T2_design": [1, 18, 4, 12, 14, 9, 11, 15, 17, 13, 10, 6, 16, 20, 8, 3, 5, 2, 19, 7],
    "T1_design": [1, 12, 20, 3, 18, 6, 13, 19, 2, 16, 14, 10, 7, 11, 17, 5, 15, 4, 9, 8],
    "T1_NULL2": [13, 17, 8, 10, 12, 9, 6, 7, 15, 19, 20, 3, 18, 1, 5, 4, 11, 16, 14, 2],
}

T2 = {
    "id": "S7-T2-P16777213",
    "p": 16777213,
    "a": 19,
    "b": 107,
    "N": 16777213,
    "P": (0, 1722727),
    "V": [0, 14386069, 13311471, 510744, 13641516, 11286066, 16703438, 13064901, 3436861, 9847978, 4422270, 2431989, 8626592, 2704728, 8015097, 11447766, 8129445, 341717, 16207358, 12600408],
}
T1 = {
    "id": "S7-T1-P16777213",
    "p": 16777213,
    "a": 0,
    "b": 7,
    "N": 16770451,
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


def reconstruct_V(cell: dict) -> list[int]:
    p, a = cell["p"], cell["a"]
    R = None
    xs = []
    for k in range(1, D + 1):
        R = add(p, a, R, cell["P"])
        if R is None:
            raise RuntimeError(f"{cell['id']}: identity at k={k}")
        if R[0] != cell["V"][k - 1]:
            raise RuntimeError(f"{cell['id']}: V mismatch at k={k}")
        xs.append(R[0])
    return xs


def k_inc(vs: list[int], ks: list[int]) -> list[int]:
    seq = [k for _, k in sorted(zip(vs, ks), key=lambda t: t[0])]
    if seq == list(range(1, D + 1)):
        raise RuntimeError("k-order 1,2,...,D is forbidden")
    return seq


def c4(vs: list[int], ks: list[int], n: int, pin: list[int], label: str) -> dict:
    seq = k_inc(vs, ks)
    if seq != pin:
        raise RuntimeError(f"{label} k_inc pin mismatch")
    payload = b"".join(int(k).to_bytes(4, "big") for k in seq)
    if len(payload) != 80:
        raise RuntimeError(f"{label} payload {len(payload)} != 80")
    compressed = zlib.compress(payload, ZLIB_LEVEL)
    s_bits = 8 * len(compressed)
    denom_power = D * math.log2(n)
    denom_linear = D * math.log2(n / D)
    return {
        "label": label,
        "k_inc": seq,
        "k_inc_pin_match": True,
        "payload_len_bytes": 80,
        "zlib_len_bytes": len(compressed),
        "S_C_bits": s_bits,
        "gamma_power": 1.0 - math.log(s_bits) / math.log(denom_power),
        "gamma_linear": 1.0 - s_bits / denom_linear,
    }


def main() -> None:
    t2_xs = reconstruct_V(T2)
    t1_xs = reconstruct_V(T1)
    ks = list(range(1, D + 1))
    null2 = list(ks)
    random.Random(NULL2_SEED).shuffle(null2)
    t2 = c4(t2_xs, ks, T2["N"], K_INC_PINS["T2_design"], "T2_design")
    t1 = c4(t1_xs, ks, T1["N"], K_INC_PINS["T1_design"], "T1_design")
    n2 = c4(t1_xs, null2, T1["N"], K_INC_PINS["T1_NULL2"], "T1_NULL2")
    raw = {
        "task_id": "TASK-20260908-17290a",
        "workspace_root": str(ROOT),
        "producer_imported": False,
        "k_order_used": False,
        "T2_V_match": t2_xs == T2["V"],
        "T1_V_match": t1_xs == T1["V"],
        "null2_shuffle": null2,
        "T2_design": t2,
        "T1_design": t1,
        "T1_NULL2": n2,
        "same_S_C_all_arms": t2["S_C_bits"] == t1["S_C_bits"] == n2["S_C_bits"],
        "k_inc_pins_all_match": True,
        "payload_len_bytes_all_80": True,
    }
    out = Path(__file__).with_name("blind_raw.json")
    out.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"wrote": str(out), "same_S_C": raw["same_S_C_all_arms"]}, sort_keys=True))


if __name__ == "__main__":
    main()
