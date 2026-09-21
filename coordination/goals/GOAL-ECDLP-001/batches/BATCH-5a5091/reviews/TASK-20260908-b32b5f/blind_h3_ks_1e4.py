#!/usr/bin/env python3
"""Blind re-derivation of Stage 14 extra-start pins, first_j, nested walk 0.

Does not import the Stage 14 producer. Does not read RUN-ECDLP-420e73-S14.
Workspace root is parents[7] from this path.
A full 10000-walk KS re-run is not this joint.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
_ = ROOT  # convention: workspace root from the Stage 10/11/12/13/14 review path

P_FIELD = 16777213
D = 20
R_ADDING = 16
SEED = 20260908
NMIN = 16770451
N_SPARE = 4096

ADDENDS = [4083811, 14207148, 3197494, 5909533, 2112584, 3183261, 10497618, 7831654, 5887209, 4196257, 199026, 3111920, 8124186, 1874953, 16389255, 8467452]
STARTS_REUSED = [16512131, 3548612, 6906991, 7276399, 14567537, 10110148, 14742596, 3279851, 3740181, 16190719]
NULL3_K = [12664300, 6842134, 11844367, 6996586, 4488890, 6629474, 1373371, 715077, 12256922, 7014070, 15143700, 12434262, 1263476, 13985324, 4621790, 8306822, 2915849, 13925014, 13948079, 8437742]

PROTOCOL_PINS = {
    "material_ascii": "20260908|stage14_extra_starts",
    "material_sha256": "7c0af2d4d79d7de7863574728d7089b5ae46db12be67b1817e2700c7b9dd875a",
    "rng_seed": 8938223406434581991,
    "start_index_10": 2321726,
    "start_index_11": 1202185,
    "start_index_9999": 12097902,
    "start_index_10000_first_spare": 3391,
    "start_index_10031": 4108081,
    "start_index_10032_first_new_spare": 7307652,
    "start_index_14095_last_spare": 13224198,
    "n_collision_skips_in_this_draw": 8,
}

FIRST_J_IDX0 = {
    "S7-T2-P16777213": {"design": 6, "NULL-3": 5},
    "S7-T1-P16777213": {"design": 4, "NULL-3": 4},
}
FIRST_J_IDX10 = {
    "S7-T2-P16777213": {"design": 6, "NULL-3": 8},
    "S7-T1-P16777213": {"design": 8, "NULL-3": 6},
}

T2 = {
    "id": "S7-T2-P16777213",
    "p": P_FIELD,
    "a": 19,
    "b": 107,
    "N": 16777213,
    "P": (0, 1722727),
    "V": [0, 14386069, 13311471, 510744, 13641516, 11286066, 16703438, 13064901, 3436861, 9847978, 4422270, 2431989, 8626592, 2704728, 8015097, 11447766, 8129445, 341717, 16207358, 12600408],
    "V_NULL3": [5008632, 16059306, 6768596, 10311345, 12881503, 11670341, 2237608, 14433701, 3919924, 12118938, 1323836, 6448954, 12258498, 10503013, 6500704, 2551759, 11438792, 11003594, 6078716, 9225734],
}
T1 = {
    "id": "S7-T1-P16777213",
    "p": P_FIELD,
    "a": 0,
    "b": 7,
    "N": 16770451,
    "P": (6, 7827705),
    "V": [6, 4288347, 2837810, 15061002, 7941042, 3891067, 6883471, 15571429, 15172588, 6789969, 6889484, 865709, 4039235, 6596143, 14029655, 5242584, 7908075, 2872040, 4197418, 1510565],
    "V_NULL3": [4232246, 12647966, 14113284, 15639226, 7796176, 11842120, 15492402, 3294931, 3074382, 11697033, 16598714, 2029482, 11658992, 11059053, 4883322, 369323, 1834504, 1634034, 12304223, 5575639],
}


def walk_rng(cell_id: str, start_index: int, arm: str) -> random.Random:
    material = f"{SEED}|{cell_id}|{start_index}|{arm}".encode("ascii")
    walk_rng_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return random.Random(walk_rng_seed)


def first_j(cell_id: str, start_index: int, arm: str) -> int:
    return walk_rng(cell_id, start_index, arm).randrange(R_ADDING)


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
    R = None
    Q = P
    kk = k
    while kk:
        if kk & 1:
            R = add(p, a, R, Q)
        Q = add(p, a, Q, Q)
        kk >>= 1
    return R


def cap_steps(n: int) -> int:
    return 8 * math.ceil(n / D)


def walk_once(p: int, a: int, addend_pts, start_pt, vset: set[int], cap: int, rng: random.Random) -> dict:
    fj = rng.randrange(R_ADDING)
    R = start_pt
    if R is None:
        return {"status": "identity_at_start", "steps": 0, "capped": False, "hit": False, "landing_x": None, "first_j": fj}
    if R[0] in vset:
        return {"status": "hit", "steps": 0, "capped": False, "hit": True, "landing_x": R[0], "first_j": fj}
    j = fj
    R = add(p, a, R, addend_pts[j])
    if R is None:
        return {"status": "identity", "steps": 1, "capped": False, "hit": False, "landing_x": None, "first_j": fj}
    if R[0] in vset:
        return {"status": "hit", "steps": 1, "capped": False, "hit": True, "landing_x": R[0], "first_j": fj}
    for step in range(2, cap + 1):
        j = rng.randrange(R_ADDING)
        R = add(p, a, R, addend_pts[j])
        if R is None:
            return {"status": "identity", "steps": step, "capped": False, "hit": False, "landing_x": None, "first_j": fj}
        if R[0] in vset:
            return {"status": "hit", "steps": step, "capped": False, "hit": True, "landing_x": R[0], "first_j": fj}
    return {"status": "capped", "steps": cap, "capped": True, "hit": False, "landing_x": R[0] if R is not None else None, "first_j": fj}


def extra_start_draw() -> dict:
    material = f"{SEED}|stage14_extra_starts".encode("ascii")
    material_sha256 = hashlib.sha256(material).hexdigest()
    rng_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    rng = random.Random(rng_seed)
    forbidden = set(ADDENDS) | set(STARTS_REUSED)
    extra: list[int] = []
    seen = set()
    n_skips = 0
    need = 9990 + N_SPARE
    while len(extra) < need:
        s = rng.randrange(1, NMIN)
        if s in forbidden or s in seen:
            n_skips += 1
            continue
        extra.append(s)
        seen.add(s)
    computed = {
        "material_ascii": material.decode("ascii"),
        "material_sha256": material_sha256,
        "rng_seed": rng_seed,
        "start_index_10": extra[0],
        "start_index_11": extra[1],
        "start_index_9999": extra[9989],
        "start_index_10000_first_spare": extra[9990],
        "start_index_10031": extra[10021],
        "start_index_10032_first_new_spare": extra[10022],
        "start_index_14095_last_spare": extra[14085],
        "n_collision_skips_in_this_draw": n_skips,
    }
    match = all(computed[k] == PROTOCOL_PINS[k] for k in PROTOCOL_PINS)
    return {"computed": computed, "protocol": PROTOCOL_PINS, "match": match, "n_extra": len(extra)}


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    pins = extra_start_draw()
    first_j_idx0 = {}
    first_j_idx10 = {}
    first_j_idx0_match = True
    first_j_idx10_match = True
    for cell in (T2, T1):
        first_j_idx0[cell["id"]] = {}
        first_j_idx10[cell["id"]] = {}
        for arm in ("design", "NULL-3"):
            j0 = first_j(cell["id"], 0, arm)
            j10 = first_j(cell["id"], 10, arm)
            first_j_idx0[cell["id"]][arm] = j0
            first_j_idx10[cell["id"]][arm] = j10
            if j0 != FIRST_J_IDX0[cell["id"]][arm]:
                first_j_idx0_match = False
            if j10 != FIRST_J_IDX10[cell["id"]][arm]:
                first_j_idx10_match = False

    nested = []
    for cell in (T2, T1):
        addend_pts = [mul(cell["p"], cell["a"], s, cell["P"]) for s in ADDENDS]
        start_pt = mul(cell["p"], cell["a"], STARTS_REUSED[0], cell["P"])
        cap = cap_steps(cell["N"])
        for arm, vkey in (("design", "V"), ("NULL-3", "V_NULL3")):
            rng = walk_rng(cell["id"], 0, arm)
            result = walk_once(cell["p"], cell["a"], addend_pts, start_pt, set(cell[vkey]), cap, rng)
            nested.append({
                "cell": cell["id"],
                "arm": arm,
                "start_index": 0,
                "start_scalar": STARTS_REUSED[0],
                "status": result["status"],
                "steps": result["steps"],
                "capped": result["capped"],
                "hit": result["hit"],
                "landing_x": result["landing_x"],
                "first_j": result["first_j"],
                "first_j_matches_protocol_idx0": result["first_j"] == FIRST_J_IDX0[cell["id"]][arm],
            })

    payload = {
        "task_id": "TASK-20260908-b32b5f",
        "quantity": "Stage 14 extra-start pins, first_j at 0 and 10, nested walk 0",
        "producer_imported": False,
        "stage14_run_read": False,
        "full_1e4_ks_rerun": False,
        "k_order_1_to_D_used": False,
        "stage10_x_mod_16_rerun": False,
        "stage11_eight_walks_treated_as_measurement": False,
        "extra_start_pins": pins,
        "first_j_idx0": first_j_idx0,
        "first_j_idx10": first_j_idx10,
        "first_j_idx0_match": first_j_idx0_match,
        "first_j_idx10_match": first_j_idx10_match,
        "nested_stage11_walk0": nested,
        "nested_walk0_all_hit": all(w["hit"] and not w["capped"] for w in nested),
        "nested_walk0_first_j_all_match": all(w["first_j_matches_protocol_idx0"] for w in nested),
    }
    (out_dir / "blind_raw.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "extra_start_pins_match": pins["match"],
        "first_j_idx0_match": first_j_idx0_match,
        "first_j_idx10_match": first_j_idx10_match,
        "nested_walk0_all_hit": payload["nested_walk0_all_hit"],
        "nested": [{k: w[k] for k in ("cell", "arm", "status", "steps", "landing_x", "first_j")} for w in nested],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
