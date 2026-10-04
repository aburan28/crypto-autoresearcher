#!/usr/bin/env python3
"""Blind Stage 11 H3 re-derivation from v1_stage11_protocol cells only.

Does not import or read the Stage 11 producer or its raw result.
Independent r-adding walk, r=16, partition independent_uniform_0_15.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
_ = ROOT  # workspace root; cells are hardcoded, no producer import

P = 16777213
D = 20
WALK_R = 16
SEED = 20260908
N_WALKS = 8
T2 = {
    "id": "S7-T2-P16777213",
    "a": 19,
    "b": 107,
    "N": 16777213,
    "P": (0, 1722727),
    "V": [
        0, 14386069, 13311471, 510744, 13641516, 11286066, 16703438,
        13064901, 3436861, 9847978, 4422270, 2431989, 8626592, 2704728,
        8015097, 11447766, 8129445, 341717, 16207358, 12600408,
    ],
}
T1 = {
    "id": "S7-T1-P16777213",
    "a": 0,
    "b": 7,
    "N": 16770451,
    "P": (6, 7827705),
    "V": [
        6, 4288347, 2837810, 15061002, 7941042, 3891067, 6883471,
        15571429, 15172588, 6789969, 6889484, 865709, 4039235, 6596143,
        14029655, 5242584, 7908075, 2872040, 4197418, 1510565,
    ],
}
ADDENDS = [
    4083811, 14207148, 3197494, 5909533, 2112584, 3183261, 10497618,
    7831654, 5887209, 4196257, 199026, 3111920, 8124186, 1874953,
    16389255, 8467452,
]
STARTS = [
    16512131, 3548612, 6906991, 7276399, 14567537, 10110148, 14742596,
    3279851, 3740181, 16190719,
]
NULL3_K = [
    12664300, 6842134, 11844367, 6996586, 4488890, 6629474, 1373371,
    715077, 12256922, 7014070, 15143700, 12434262, 1263476, 13985324,
    4621790, 8306822, 2915849, 13925014, 13948079, 8437742,
]
NULL3_V_T2 = [
    5008632, 16059306, 6768596, 10311345, 12881503, 11670341, 2237608,
    14433701, 3919924, 12118938, 1323836, 6448954, 12258498, 10503013,
    6500704, 2551759, 11438792, 11003594, 6078716, 9225734,
]
NULL3_V_T1 = [
    4232246, 12647966, 14113284, 15639226, 7796176, 11842120, 15492402,
    3294931, 3074382, 11697033, 16598714, 2029482, 11658992, 11059053,
    4883322, 369323, 1834504, 1634034, 12304223, 5575639,
]
FIRST_J = {
    "S7-T2-P16777213": {
        "design": [6, 7, 14, 4, 4, 2, 5, 1, 8, 5],
        "NULL-3": [5, 10, 11, 5, 13, 7, 5, 3, 1, 15],
    },
    "S7-T1-P16777213": {
        "design": [4, 7, 2, 8, 15, 3, 6, 9, 6, 4],
        "NULL-3": [4, 15, 0, 1, 5, 7, 12, 7, 1, 15],
    },
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


def mul(p: int, a: int, k: int, Pt):
    R = None
    Q = Pt
    kk = k
    while kk:
        if kk & 1:
            R = add(p, a, R, Q)
        Q = add(p, a, Q, Q)
        kk >>= 1
    return R


def walk_rng(cell_id: str, start_index: int, arm: str) -> random.Random:
    material = f"{SEED}|{cell_id}|{start_index}|{arm}".encode("ascii")
    walk_rng_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return random.Random(walk_rng_seed)


def first_j_of(cell_id: str, start_index: int, arm: str) -> int:
    return walk_rng(cell_id, start_index, arm).randrange(16)


def confirm_first_j_pins() -> dict:
    out = {}
    all_match = True
    for cell_id, arms in FIRST_J.items():
        out[cell_id] = {}
        for arm, pins in arms.items():
            reconstructed = [first_j_of(cell_id, i, arm) for i in range(len(pins))]
            match = reconstructed == pins
            all_match = all_match and match
            out[cell_id][arm] = {"expected": pins, "reconstructed": reconstructed, "match": match}
    example_material = b"20260908|S7-T2-P16777213|0|design"
    example_digest = hashlib.sha256(example_material).hexdigest()
    example_seed = int.from_bytes(hashlib.sha256(example_material).digest()[:8], "big")
    return {
        "all_match": all_match,
        "arms": out,
        "example": {
            "digest": example_digest,
            "walk_rng_seed": example_seed,
            "expected_digest": "021e3eda4148360d504a6aaff68a4c9c5b52f4c4794935763bdc4e023a949d88",
            "expected_seed": 152628544496219661,
            "digest_match": example_digest
            == "021e3eda4148360d504a6aaff68a4c9c5b52f4c4794935763bdc4e023a949d88",
            "seed_match": example_seed == 152628544496219661,
        },
    }


def confirm_design_V(cell: dict) -> None:
    R = None
    for k in range(1, D + 1):
        R = add(P, cell["a"], R, cell["P"])
        if R is None or R[0] != cell["V"][k - 1]:
            raise RuntimeError(f"{cell['id']} design V mismatch at k={k}")


def confirm_null3_V(cell: dict, expected: list[int]) -> list[int]:
    vs = []
    for k in NULL3_K:
        R = mul(P, cell["a"], k, cell["P"])
        if R is None:
            raise RuntimeError(f"{cell['id']} NULL-3 hit O at k={k}")
        vs.append(R[0])
    if vs != expected:
        raise RuntimeError(f"{cell['id']} NULL-3 V mismatch")
    if len(set(vs)) != D:
        raise RuntimeError(f"{cell['id']} NULL-3 V not distinct")
    return vs


def walk_once(cell: dict, addend_pts: list, start_index: int, arm: str, V: set[int], cap: int) -> dict:
    rng = walk_rng(cell["id"], start_index, arm)
    start_scalar = STARTS[start_index]
    R = mul(P, cell["a"], start_scalar, cell["P"])
    if R is None:
        first_j = rng.randrange(16)
        return {
            "status": "identity_at_start",
            "steps": 0,
            "start_index": start_index,
            "first_j": first_j,
            "first_j_expected": FIRST_J[cell["id"]][arm][start_index],
        }
    if R[0] in V:
        first_j = rng.randrange(16)
        return {
            "status": "hit",
            "steps": 0,
            "hit_x": R[0],
            "start_index": start_index,
            "first_j": first_j,
            "first_j_expected": FIRST_J[cell["id"]][arm][start_index],
        }
    first_j = None
    step = 0
    while step < cap:
        j = rng.randrange(16)
        if first_j is None:
            first_j = j
        R = add(P, cell["a"], R, addend_pts[j])
        step += 1
        if R is None:
            return {
                "status": "identity",
                "steps": step,
                "start_index": start_index,
                "first_j": first_j,
                "first_j_expected": FIRST_J[cell["id"]][arm][start_index],
            }
        if R[0] in V:
            return {
                "status": "hit",
                "steps": step,
                "hit_x": R[0],
                "start_index": start_index,
                "first_j": first_j,
                "first_j_expected": FIRST_J[cell["id"]][arm][start_index],
            }
    return {
        "status": "capped",
        "steps": cap,
        "start_index": start_index,
        "first_j": first_j,
        "first_j_expected": FIRST_J[cell["id"]][arm][start_index],
    }


def arm_summary(walks: list[dict], n_over_d: float) -> dict:
    means = [w["steps"] for w in walks]
    mean = sum(means) / len(means)
    ratio = mean / n_over_d
    first_j_ok = all(w["first_j"] == w["first_j_expected"] for w in walks)
    return {
        "n": len(walks),
        "mean": mean,
        "ratio_vs_N_over_D": ratio,
        "factor2_departure": not (0.5 <= ratio <= 2.0),
        "hits": sum(1 for w in walks if w["status"] == "hit"),
        "identities": sum(1 for w in walks if w["status"].startswith("identity")),
        "capped": sum(1 for w in walks if w["status"] == "capped"),
        "first_j_pins_match": first_j_ok,
        "start_indices": [w["start_index"] for w in walks],
        "walks": walks,
    }


def run_arm(cell: dict, V: list[int], addend_pts: list, arm: str) -> dict:
    cap = 8 * math.ceil(cell["N"] / D)
    n_over_d = cell["N"] / D
    Vset = set(V)
    walks = []
    spare = 8
    for start_index in range(N_WALKS):
        w = walk_once(cell, addend_pts, start_index, arm, Vset, cap)
        if w["status"].startswith("identity"):
            if spare > 9:
                raise RuntimeError(f"{cell['id']} {arm} spare exhaustion after identity at {start_index}")
            walks.append(w)  # record the identity event
            replacement = walk_once(cell, addend_pts, spare, arm, Vset, cap)
            spare += 1
            if replacement["status"].startswith("identity"):
                raise RuntimeError(f"{cell['id']} {arm} spare {replacement['start_index']} also identity")
            walks.append(replacement)
        else:
            walks.append(w)
    completed = [w for w in walks if w["status"] in ("hit", "capped")]
    if len(completed) != N_WALKS:
        raise RuntimeError(f"{cell['id']} {arm} completed {len(completed)} != 8")
    out = arm_summary(completed, n_over_d)
    out["cap"] = cap
    out["N_over_D"] = n_over_d
    out["identity_events"] = [w for w in walks if w["status"].startswith("identity")]
    return out


def main() -> None:
    pins = confirm_first_j_pins()
    if not pins["all_match"] or not pins["example"]["digest_match"] or not pins["example"]["seed_match"]:
        raise RuntimeError(f"first_j pin mismatch: {pins}")
    confirm_design_V(T2)
    confirm_design_V(T1)
    confirm_null3_V(T2, NULL3_V_T2)
    confirm_null3_V(T1, NULL3_V_T1)

    t2_add = [mul(P, T2["a"], s, T2["P"]) for s in ADDENDS]
    t1_add = [mul(P, T1["a"], s, T1["P"]) for s in ADDENDS]
    if any(Q is None for Q in t2_add + t1_add):
        raise RuntimeError("addend point is O")

    result = {
        "first_j_pins": {
            "all_match": True,
            "example_digest_match": True,
            "example_seed_match": True,
        },
        "T2_design": run_arm(T2, T2["V"], t2_add, "design"),
        "T2_null3": run_arm(T2, NULL3_V_T2, t2_add, "NULL-3"),
        "T1_design": run_arm(T1, T1["V"], t1_add, "design"),
        "T1_null3": run_arm(T1, NULL3_V_T1, t1_add, "NULL-3"),
        "producer_imported": False,
        "c1_c2_c3_rerun": False,
        "deterministic_x_mod_16_rerun": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
