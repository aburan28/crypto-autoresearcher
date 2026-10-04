#!/usr/bin/env python3
"""Blind re-derivation of Stage 16 extra-start pins, first_j, design V pins, NULL-3 pins.

Does not import the Stage 16 producer. Does not read RUN-ECDLP-420e73-S16.
Does not read stage14_walk.c. Workspace root is parents[7] from this path.
A full 10000-walk KS re-run is not this joint.
Stage 15 D=256 hitting times are not nested.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
_ = ROOT

P_FIELD = 16777213
R_ADDING = 16
SEED = 20260908
NMIN = 16770451
N_SPARE = 4096
T2_D = 4096
T1_D = 4095

ADDENDS = [4083811, 14207148, 3197494, 5909533, 2112584, 3183261, 10497618, 7831654, 5887209, 4196257, 199026, 3111920, 8124186, 1874953, 16389255, 8467452]
STARTS_REUSED = [16512131, 3548612, 6906991, 7276399, 14567537, 10110148, 14742596, 3279851, 3740181, 16190719]

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

DESIGN_V_PINS = {
    "S7-T2-P16777213": {"k21": 919160, "k256": 16283645, "kD": 15023503, "D": T2_D},
    "S7-T1-P16777213": {"k21": 11575537, "k256": 8804309, "kD": 2439767, "D": T1_D},
}

NULL3_PINS = {
    "k_index_20": 4442873,
    "k_index_255": 3925208,
    "k_index_4094": 5707805,
    "k_index_4095": 8435369,
    "V_T2_index_20": 4443814,
    "V_T1_index_20": 6296420,
    "V_T2_index_255": 16523022,
    "V_T1_index_255": 11205200,
    "V_T2_index_4095": 8711474,
    "V_T1_index_4094": 13739162,
}
NULL3_T2_COLLISION_INDICES = (745, 1623)

T2 = {
    "id": "S7-T2-P16777213",
    "p": P_FIELD,
    "a": 19,
    "b": 107,
    "N": 16777213,
    "P": (0, 1722727),
    "D": T2_D,
}
T1 = {
    "id": "S7-T1-P16777213",
    "p": P_FIELD,
    "a": 0,
    "b": 7,
    "N": 16770451,
    "P": (6, 7827705),
    "D": T1_D,
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


def draw_null3_k() -> dict:
    rng = random.Random(SEED)
    forbidden: set[int] = set()
    addends: list[int] = []
    while len(addends) < 16:
        s = rng.randrange(1, NMIN)
        if s in forbidden:
            continue
        addends.append(s)
        forbidden.add(s)
    starts: list[int] = []
    while len(starts) < 10:
        s = rng.randrange(1, NMIN)
        if s in forbidden:
            continue
        starts.append(s)
        forbidden.add(s)
    k: list[int] = []
    while len(k) < T2_D:
        s = rng.randrange(1, NMIN)
        if s in forbidden:
            continue
        k.append(s)
        forbidden.add(s)
    return {
        "addends_match": addends == ADDENDS,
        "starts_match": starts == STARTS_REUSED,
        "k": k,
        "k_index_20": k[20],
        "k_index_255": k[255],
        "k_index_4094": k[4094],
        "k_index_4095": k[4095],
        "k_index_20_match": k[20] == NULL3_PINS["k_index_20"],
        "k_index_255_match": k[255] == NULL3_PINS["k_index_255"],
        "k_index_4094_match": k[4094] == NULL3_PINS["k_index_4094"],
        "k_index_4095_match": k[4095] == NULL3_PINS["k_index_4095"],
    }


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

    design_v = {}
    design_v_match = True
    for cell in (T2, T1):
        expected = DESIGN_V_PINS[cell["id"]]
        pt21 = mul(cell["p"], cell["a"], 21, cell["P"])
        pt256 = mul(cell["p"], cell["a"], 256, cell["P"])
        ptD = mul(cell["p"], cell["a"], expected["D"], cell["P"])
        xs = []
        R = None
        for _k in range(1, expected["D"] + 1):
            R = add(cell["p"], cell["a"], R, cell["P"])
            if R is None:
                raise RuntimeError(f"{cell['id']} design V hit O")
            xs.append(R[0])
        row = {
            "k21_x": None if pt21 is None else pt21[0],
            "k256_x": None if pt256 is None else pt256[0],
            "kD_x": None if ptD is None else ptD[0],
            "k21_match": (None if pt21 is None else pt21[0]) == expected["k21"],
            "k256_match": (None if pt256 is None else pt256[0]) == expected["k256"],
            "kD_match": (None if ptD is None else ptD[0]) == expected["kD"],
            "nunique": len(set(xs)),
            "D": expected["D"],
            "D_distinct": len(set(xs)) == expected["D"],
        }
        design_v[cell["id"]] = row
        if not (row["k21_match"] and row["k256_match"] and row["kD_match"] and row["D_distinct"]):
            design_v_match = False

    null3 = draw_null3_k()
    null3_v = {}
    t2_xs = []
    for kk in null3["k"]:
        Q = mul(T2["p"], T2["a"], kk, T2["P"])
        if Q is None:
            raise RuntimeError("T2 NULL-3 hit O")
        t2_xs.append(Q[0])
    t1_xs = []
    for kk in null3["k"][: T1_D]:
        Q = mul(T1["p"], T1["a"], kk, T1["P"])
        if Q is None:
            raise RuntimeError("T1 NULL-3 hit O")
        t1_xs.append(Q[0])
    i_col, j_col = NULL3_T2_COLLISION_INDICES
    t2_collision = t2_xs[i_col] == t2_xs[j_col] and len(set(t2_xs)) == T2_D - 1
    t1_distinct = len(set(t1_xs)) == T1_D
    null3_v["S7-T2-P16777213"] = {
        "V_index_20": t2_xs[20],
        "V_index_255": t2_xs[255],
        "V_index_end": t2_xs[4095],
        "V_index_20_match": t2_xs[20] == NULL3_PINS["V_T2_index_20"],
        "V_index_255_match": t2_xs[255] == NULL3_PINS["V_T2_index_255"],
        "V_index_end_match": t2_xs[4095] == NULL3_PINS["V_T2_index_4095"],
        "nunique": len(set(t2_xs)),
        "collision_indices": [i_col, j_col],
        "collision_match": t2_collision,
    }
    null3_v["S7-T1-P16777213"] = {
        "V_index_20": t1_xs[20],
        "V_index_255": t1_xs[255],
        "V_index_end": t1_xs[4094],
        "V_index_20_match": t1_xs[20] == NULL3_PINS["V_T1_index_20"],
        "V_index_255_match": t1_xs[255] == NULL3_PINS["V_T1_index_255"],
        "V_index_end_match": t1_xs[4094] == NULL3_PINS["V_T1_index_4094"],
        "nunique": len(set(t1_xs)),
        "D_distinct": t1_distinct,
    }
    null3_v_match = all(
        null3_v["S7-T2-P16777213"][k]
        for k in ("V_index_20_match", "V_index_255_match", "V_index_end_match", "collision_match")
    ) and all(
        null3_v["S7-T1-P16777213"][k]
        for k in ("V_index_20_match", "V_index_255_match", "V_index_end_match", "D_distinct")
    )

    payload = {
        "task_id": "TASK-20260908-53e074",
        "quantity": "Stage 16 extra-start pins, first_j at 0 and 10, design V k=21/k=256/k=D, NULL-3 k/V pins and T2 freeze collision",
        "producer_imported": False,
        "stage16_run_read": False,
        "stage14_walk_c_read": False,
        "full_1e4_ks_rerun": False,
        "k_order_1_to_D_used": False,
        "stage10_x_mod_16_rerun": False,
        "stage11_eight_walks_treated_as_measurement": False,
        "stage15_d256_hitting_times_nested": False,
        "T2_D": T2_D,
        "T1_D": T1_D,
        "extra_start_pins": pins,
        "first_j_idx0": first_j_idx0,
        "first_j_idx10": first_j_idx10,
        "first_j_idx0_match": first_j_idx0_match,
        "first_j_idx10_match": first_j_idx10_match,
        "design_v_pins": design_v,
        "design_v_pins_match": design_v_match,
        "null3_k": {
            "addends_match": null3["addends_match"],
            "starts_match": null3["starts_match"],
            "k_index_20": null3["k_index_20"],
            "k_index_255": null3["k_index_255"],
            "k_index_4094": null3["k_index_4094"],
            "k_index_4095": null3["k_index_4095"],
            "k_index_20_match": null3["k_index_20_match"],
            "k_index_255_match": null3["k_index_255_match"],
            "k_index_4094_match": null3["k_index_4094_match"],
            "k_index_4095_match": null3["k_index_4095_match"],
        },
        "null3_v": null3_v,
        "null3_v_match": null3_v_match,
        "t2_null3_collision_is_not_failed_infrastructure": True,
    }
    payload["null3_k_and_v_match"] = (
        null3["addends_match"]
        and null3["starts_match"]
        and null3["k_index_20_match"]
        and null3["k_index_255_match"]
        and null3["k_index_4094_match"]
        and null3["k_index_4095_match"]
        and null3_v_match
    )
    match = (
        pins["match"]
        and first_j_idx0_match
        and first_j_idx10_match
        and design_v_match
        and payload["null3_k_and_v_match"]
    )
    payload["match"] = match
    (out_dir / "blind_raw.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "extra_start_pins_match": pins["match"],
        "first_j_idx0_match": first_j_idx0_match,
        "first_j_idx10_match": first_j_idx10_match,
        "design_v_pins_match": design_v_match,
        "null3_k_and_v_match": payload["null3_k_and_v_match"],
        "match": match,
        "design_v": {cid: {k: v for k, v in row.items()} for cid, row in design_v.items()},
        "null3_k": payload["null3_k"],
        "null3_v": null3_v,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
