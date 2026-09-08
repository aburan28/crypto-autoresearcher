#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 12 C4 first-slice at p=16777213. Certificate kind none.

S_C is 8 * len(zlib.compress(payload, 9)) on increasing-v k_inc.
k-order 1,2,...,D is forbidden. C4 is a non-admissible indicator.
C1, C2, C3, and the Stage 10/11 walks are not re-run.
"""
from __future__ import annotations

import json
import math
import platform
import random
import sys
import time
import zlib
from pathlib import Path

SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage12_c4_16777213.py"
P_FIELD = 16777213
D = 20
NULL2_SEED = 20260908
ZLIB_LEVEL = 9

K_INC_PINS = {
    "T2_design": [1, 18, 4, 12, 14, 9, 11, 15, 17, 13, 10, 6, 16, 20, 8, 3, 5, 2, 19, 7],
    "T1_design": [1, 12, 20, 3, 18, 6, 13, 19, 2, 16, 14, 10, 7, 11, 17, 5, 15, 4, 9, 8],
    "T1_NULL2": [13, 17, 8, 10, 12, 9, 6, 7, 15, 19, 20, 3, 18, 1, 5, 4, 11, 16, 14, 2],
}
NULL2_SHUFFLE_PIN = [13, 15, 10, 16, 4, 9, 18, 2, 14, 3, 1, 17, 6, 20, 11, 19, 5, 12, 7, 8]

T2 = {
    "id": "S7-T2-P16777213",
    "p": P_FIELD,
    "a": 19,
    "b": 107,
    "N": 16777213,
    "P": (0, 1722727),
    "V": [0, 14386069, 13311471, 510744, 13641516, 11286066, 16703438, 13064901, 3436861, 9847978, 4422270, 2431989, 8626592, 2704728, 8015097, 11447766, 8129445, 341717, 16207358, 12600408],
}
T1 = {
    "id": "S7-T1-P16777213",
    "p": P_FIELD,
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


def reconstruct_landings(cell: dict) -> list[int]:
    p, a = cell["p"], cell["a"]
    R = None
    xs = []
    for k in range(1, D + 1):
        R = add(p, a, R, cell["P"])
        if R is None:
            raise RuntimeError(f"{cell['id']}: [k]P hit O at k={k}")
        if R[0] != cell["V"][k - 1]:
            raise RuntimeError(f"{cell['id']}: V mismatch at k={k}")
        xs.append(R[0])
    return xs


def k_inc(vs: list[int], ks: list[int]) -> list[int]:
    if len(vs) != D or len(ks) != D:
        raise RuntimeError("k_inc requires exactly D pairs")
    if len(set(vs)) != D:
        raise RuntimeError("V values are not distinct")
    if any(k < 1 or k > D for k in ks):
        raise RuntimeError("k values are not in 1..D")
    seq = [k for _, k in sorted(zip(vs, ks), key=lambda t: t[0])]
    if seq == list(range(1, D + 1)):
        raise RuntimeError("k-order 1,2,...,D is forbidden")
    return seq


def encode_payload(seq: list[int]) -> bytes:
    return b"".join(int(k).to_bytes(4, "big") for k in seq)


def c4_arm(vs: list[int], ks: list[int], n: int, label: str, pin: list[int]) -> dict:
    seq = k_inc(vs, ks)
    if seq != pin:
        raise RuntimeError(f"{label} k_inc pin mismatch: {seq} != {pin}")
    payload = encode_payload(seq)
    if len(payload) != 80:
        raise RuntimeError(f"{label} payload length {len(payload)} != 80")
    compressed = zlib.compress(payload, ZLIB_LEVEL)
    zlib_len = len(compressed)
    s_bits = 8 * zlib_len
    denom_power = D * math.log2(n)
    denom_linear = D * math.log2(n / D)
    return {
        "label": label,
        "N": n,
        "k_inc": seq,
        "k_inc_pin_match": True,
        "payload_len_bytes": len(payload),
        "zlib_level": ZLIB_LEVEL,
        "zlib_len_bytes": zlib_len,
        "S_C_bits": s_bits,
        "gamma_power": 1.0 - math.log(s_bits) / math.log(denom_power),
        "gamma_linear": 1.0 - s_bits / denom_linear,
    }


def null2_ks() -> list[int]:
    shuffled = list(range(1, D + 1))
    random.Random(NULL2_SEED).shuffle(shuffled)
    if shuffled != NULL2_SHUFFLE_PIN:
        raise RuntimeError(f"NULL-2 shuffle pin mismatch: {shuffled}")
    return shuffled


def main() -> int:
    t0 = time.perf_counter()
    t2_xs = reconstruct_landings(T2)
    t1_xs = reconstruct_landings(T1)
    t2_ks = list(range(1, D + 1))
    t1_ks = list(range(1, D + 1))
    t2 = c4_arm(t2_xs, t2_ks, T2["N"], "T2_design", K_INC_PINS["T2_design"])
    t1 = c4_arm(t1_xs, t1_ks, T1["N"], "T1_design", K_INC_PINS["T1_design"])
    t1_null2_ks = null2_ks()
    t1_null2 = c4_arm(t1_xs, t1_null2_ks, T1["N"], "T1_NULL2", K_INC_PINS["T1_NULL2"])
    arms = [t2, t1, t1_null2]
    fixture_pass = all(
        arm["k_inc_pin_match"] and arm["payload_len_bytes"] == 80 and arm["S_C_bits"] > 0
        for arm in arms
    )
    raw = {
        "run_id": "RUN-ECDLP-420e73-S12",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 12,
        "authorized_by": "DEC-20260908-9abf6f",
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "C4_is_non_admissible_indicator": True,
        "C4_floor_is_not_failed_infrastructure": True,
        "C4_reading_is_not_H1_closure": True,
        "fishing_1000_is_not_this_slice": True,
        "c1_c2_c3_not_rerun": True,
        "h3_walks_not_rerun": True,
        "k_order_forbidden": True,
        "seed": NULL2_SEED,
        "zlib_level": ZLIB_LEVEL,
        "T2": {
            "id": T2["id"],
            "p": T2["p"],
            "a": T2["a"],
            "b": T2["b"],
            "N": T2["N"],
            "generator_P": list(T2["P"]),
            "V": T2["V"],
            "k": t2_ks,
            "landing_V_match": t2_xs == T2["V"],
            "C4": t2,
        },
        "T1": {
            "id": T1["id"],
            "p": T1["p"],
            "a": T1["a"],
            "b": T1["b"],
            "N": T1["N"],
            "generator_P": list(T1["P"]),
            "V": T1["V"],
            "k": t1_ks,
            "landing_V_match": t1_xs == T1["V"],
            "C4": t1,
        },
        "T1_NULL2": {
            "seed": NULL2_SEED,
            "algorithm": "random.Random(20260908).shuffle",
            "k_shuffled": t1_null2_ks,
            "C4": t1_null2,
        },
        "T2_C4_S_C_bits": t2["S_C_bits"],
        "T1_C4_S_C_bits": t1["S_C_bits"],
        "T1_NULL2_C4_S_C_bits": t1_null2["S_C_bits"],
        "T2_zlib_len_bytes": t2["zlib_len_bytes"],
        "T1_zlib_len_bytes": t1["zlib_len_bytes"],
        "T1_NULL2_zlib_len_bytes": t1_null2["zlib_len_bytes"],
        "k_inc_pins_all_match": all(arm["k_inc_pin_match"] for arm in arms),
        "payload_len_bytes_all_80": all(arm["payload_len_bytes"] == 80 for arm in arms),
        "landing_reconstruction_all_match": t2_xs == T2["V"] and t1_xs == T1["V"],
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": (
            "Toy C4 first-slice zlib encoding length on frozen Stage 7 "
            "cells at p=16777213. Increasing-v k_inc, 80-byte big-endian "
            "payload, zlib.compress level 9. C4 is a non-admissible "
            "indicator. A C4 floor is a width-padding observation, not "
            "failed_infrastructure. A C4 reading is not H1 closure. "
            "Fishing-1000 is not this slice. C1, C2, C3, and the Stage "
            "10/11 walks are not re-run. Not H1. Not a W class. No "
            "a98ea9 Stage 5. Gammas are observations."
        ),
        "wall_clock_seconds": time.perf_counter() - t0,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source": SOURCE,
        "workspace_root_unused": str(Path(__file__).resolve().parents[3]),
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if fixture_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
