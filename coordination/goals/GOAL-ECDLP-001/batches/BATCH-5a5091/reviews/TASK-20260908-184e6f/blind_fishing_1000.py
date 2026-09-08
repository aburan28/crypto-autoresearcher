#!/usr/bin/env python3
"""Blind re-derivation of Stage 13 fishing-1000 from v1_stage13_protocol only.

Does not import the producer. Does not read RUN-ECDLP-420e73-S13.
Workspace root is parents[7] from this path.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
_ = ROOT  # convention: workspace root from the Stage 10/11/12/13 review path

P_FIELD = 16777213
D = 20
N_DESIGNS = 1000
SEED = 20260908
ZLIB_LEVEL = 9
RETRY_CAP = 32
FORBIDDEN_K_INC = list(range(1, D + 1))

DESIGN0_PINS = {
    "S7-T2-P16777213": {
        "k": [12298913, 8467048, 14076747, 10936910, 7569783, 10645121, 2505911, 4502224, 1012183, 12777962, 16054694, 3388688, 13887009, 16099079, 14892208, 10680189, 7540820, 4260711, 16417450, 11779753],
        "k_inc": [10936910, 16417450, 12298913, 8467048, 16054694, 14076747, 2505911, 4502224, 14892208, 12777962, 10645121, 3388688, 4260711, 1012183, 16099079, 7569783, 11779753, 10680189, 7540820, 13887009],
        "retry": 0,
    },
    "S7-T1-P16777213": {
        "k": [975148, 12294012, 7424872, 3457847, 15464397, 13949641, 15331771, 11788257, 1985447, 4061519, 15702412, 4284282, 15100540, 10472768, 9061857, 10419827, 9562457, 12432150, 6334657, 11755702],
        "k_inc": [10419827, 11788257, 13949641, 4284282, 15464397, 11755702, 975148, 15331771, 7424872, 12294012, 10472768, 6334657, 4061519, 1985447, 9061857, 3457847, 15702412, 15100540, 9562457, 12432150],
        "retry": 0,
    },
}

T2 = {
    "id": "S7-T2-P16777213",
    "p": P_FIELD,
    "a": 19,
    "b": 107,
    "N": 16777213,
    "P": (0, 1722727),
}
T1 = {
    "id": "S7-T1-P16777213",
    "p": P_FIELD,
    "a": 0,
    "b": 7,
    "N": 16770451,
    "P": (6, 7827705),
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


def mul(p: int, a: int, k: int, P):
    if k < 1:
        return None
    R = None
    Q = P
    kk = k
    while kk:
        if kk & 1:
            R = add(p, a, R, Q)
        Q = add(p, a, Q, Q)
        kk >>= 1
    return R


def sample_k(cell_id: str, n: int, design_index: int, retry: int) -> list[int]:
    if retry == 0:
        material = f"{SEED}|{cell_id}|{design_index}".encode("ascii")
    else:
        material = f"{SEED}|{cell_id}|{design_index}|retry{retry}".encode("ascii")
    rng_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    rng = random.Random(rng_seed)
    return rng.sample(range(1, n), D)


def c4_of_k_inc(k_inc: list[int], n: int) -> dict:
    payload = b"".join(int(k).to_bytes(4, "big") for k in k_inc)
    if len(payload) != 80:
        raise RuntimeError(f"payload length {len(payload)} != 80")
    compressed = zlib.compress(payload, ZLIB_LEVEL)
    s_bits = 8 * len(compressed)
    denom_power = D * math.log2(n)
    denom_linear = D * math.log2(n / D)
    return {
        "payload_len_bytes": len(payload),
        "S_C_bits": s_bits,
        "gamma_power": 1.0 - math.log(s_bits) / math.log(denom_power),
        "gamma_linear": 1.0 - s_bits / denom_linear,
    }


def one_design(cell: dict, design_index: int) -> dict:
    p, a, n, P = cell["p"], cell["a"], cell["N"], cell["P"]
    for retry in range(0, RETRY_CAP + 1):
        ks = sample_k(cell["id"], n, design_index, retry)
        xs = []
        invalid = False
        for k in ks:
            R = mul(p, a, k, P)
            if R is None:
                invalid = True
                break
            xs.append(R[0])
        if invalid or len(set(xs)) != D:
            continue
        k_inc = [k for _, k in sorted(zip(xs, ks), key=lambda t: t[0])]
        if k_inc == FORBIDDEN_K_INC:
            continue
        return {
            "design_index": design_index,
            "retry": retry,
            "k": ks,
            "k_inc": k_inc,
            "C4": c4_of_k_inc(k_inc, n),
        }
    raise RuntimeError(f"{cell['id']} design {design_index}: retry exhaustion")


def cell_fishing(cell: dict) -> dict:
    designs = [one_design(cell, i) for i in range(N_DESIGNS)]
    pin = DESIGN0_PINS[cell["id"]]
    d0 = designs[0]
    gammas_p = [d["C4"]["gamma_power"] for d in designs]
    min_p = min(gammas_p)
    return {
        "id": cell["id"],
        "n_designs": len(designs),
        "n_retries": sum(d["retry"] for d in designs),
        "payload_len_bytes_all_80": all(d["C4"]["payload_len_bytes"] == 80 for d in designs),
        "design0_k_match": d0["k"] == pin["k"],
        "design0_k_inc_match": d0["k_inc"] == pin["k_inc"],
        "design0_retry_match": d0["retry"] == pin["retry"],
        "min_gamma_power": min_p,
        "min_gamma_power_design_index": gammas_p.index(min_p),
        "min_gamma_linear": min(d["C4"]["gamma_linear"] for d in designs),
        "mean_gamma_power": statistics.fmean(gammas_p),
        "mean_differs_from_min": statistics.fmean(gammas_p) != min_p,
        "k_order_used": any(d["k_inc"] == FORBIDDEN_K_INC for d in designs),
    }


def main() -> int:
    t2 = cell_fishing(T2)
    t1 = cell_fishing(T1)
    design0_pins_all_match = all(
        [
            t2["design0_k_match"],
            t2["design0_k_inc_match"],
            t2["design0_retry_match"],
            t1["design0_k_match"],
            t1["design0_k_inc_match"],
            t1["design0_retry_match"],
        ]
    )
    raw = {
        "task_id": "TASK-20260908-184e6f",
        "producer_imported": False,
        "stage13_run_read": False,
        "k_order_used": t2["k_order_used"] or t1["k_order_used"],
        "design0_pins_all_match": design0_pins_all_match,
        "payload_len_bytes_all_80": t2["payload_len_bytes_all_80"] and t1["payload_len_bytes_all_80"],
        "n_retries_total": t2["n_retries"] + t1["n_retries"],
        "T2": t2,
        "T1": t1,
        "certificate_kind": "none",
        "C4_is_non_admissible_indicator": True,
        "fishing_1000_is_not_H1_support": True,
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if design0_pins_all_match else 2


if __name__ == "__main__":
    raise SystemExit(main())
