#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 11 H3 nearby-object walks at p=16777213. Certificate kind none.

Eight re-randomized r=16 adding walks per (cell x V-or-NULL3) arm.
j is drawn uniformly from {0,...,15} by a per-walk sha256 RNG.
Hard gate is fixture_pass. An H3 factor-2 miss is a model observation.
The Stage 10 deterministic x-mod-16 walk is not re-run.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import random
import sys
import time
from pathlib import Path

SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage11_h3_rerandom_16777213.py"
P_FIELD = 16777213
D = 20
R_ADDING = 16
N_WALKS = 8
SEED = 20260908

ADDENDS = [4083811, 14207148, 3197494, 5909533, 2112584, 3183261, 10497618, 7831654, 5887209, 4196257, 199026, 3111920, 8124186, 1874953, 16389255, 8467452]
STARTS = [16512131, 3548612, 6906991, 7276399, 14567537, 10110148, 14742596, 3279851]
SPARES = [3740181, 16190719]
NULL3_K = [12664300, 6842134, 11844367, 6996586, 4488890, 6629474, 1373371, 715077, 12256922, 7014070, 15143700, 12434262, 1263476, 13985324, 4621790, 8306822, 2915849, 13925014, 13948079, 8437742]

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
    first_j = rng.randrange(R_ADDING)
    R = start_pt
    if R is None:
        return {
            "status": "identity_at_start",
            "steps": 0,
            "capped": False,
            "hit": False,
            "landing_x": None,
            "first_j": first_j,
            "first_j_used_as_step": False,
        }
    if R[0] in vset:
        return {
            "status": "hit",
            "steps": 0,
            "capped": False,
            "hit": True,
            "landing_x": R[0],
            "first_j": first_j,
            "first_j_used_as_step": False,
        }
    j = first_j
    R = add(p, a, R, addend_pts[j])
    if R is None:
        return {
            "status": "identity",
            "steps": 1,
            "capped": False,
            "hit": False,
            "landing_x": None,
            "first_j": first_j,
            "first_j_used_as_step": True,
        }
    if R[0] in vset:
        return {
            "status": "hit",
            "steps": 1,
            "capped": False,
            "hit": True,
            "landing_x": R[0],
            "first_j": first_j,
            "first_j_used_as_step": True,
        }
    for step in range(2, cap + 1):
        j = rng.randrange(R_ADDING)
        R = add(p, a, R, addend_pts[j])
        if R is None:
            return {
                "status": "identity",
                "steps": step,
                "capped": False,
                "hit": False,
                "landing_x": None,
                "first_j": first_j,
                "first_j_used_as_step": True,
            }
        if R[0] in vset:
            return {
                "status": "hit",
                "steps": step,
                "capped": False,
                "hit": True,
                "landing_x": R[0],
                "first_j": first_j,
                "first_j_used_as_step": True,
            }
    return {
        "status": "capped",
        "steps": cap,
        "capped": True,
        "hit": False,
        "landing_x": R[0] if R is not None else None,
        "first_j": first_j,
        "first_j_used_as_step": True,
    }


def run_arm(cell: dict, vset: set[int], arm: str) -> dict:
    p, a, n = cell["p"], cell["a"], cell["N"]
    P = cell["P"]
    cap = cap_steps(n)
    addend_pts = []
    for s in ADDENDS:
        Q = mul(p, a, s, P)
        if Q is None:
            raise RuntimeError(f"{cell['id']} {arm}: addend scalar produced O")
        addend_pts.append(Q)
    start_pool = [(i, s, False) for i, s in enumerate(STARTS)]
    start_pool.extend((8 + i, s, True) for i, s in enumerate(SPARES))
    walks = []
    identity_events = []
    pool_i = 0
    while len(walks) < N_WALKS:
        if pool_i >= len(start_pool):
            break
        start_index, s, spare = start_pool[pool_i]
        pool_i += 1
        rng = walk_rng(cell["id"], start_index, arm)
        start_pt = mul(p, a, s, P)
        print(f"START {cell['id']} {arm} start_index={start_index} scalar={s}", file=sys.stderr, flush=True)
        t_walk = time.perf_counter()
        result = walk_once(p, a, addend_pts, start_pt, vset, cap, rng)
        result["start_scalar"] = s
        result["start_index"] = start_index
        result["spare"] = spare
        result["arm"] = arm
        result["wall_clock_seconds"] = time.perf_counter() - t_walk
        pinned = FIRST_J[cell["id"]][arm][start_index]
        result["first_j_pin"] = pinned
        result["first_j_matches_pin"] = result["first_j"] == pinned
        if result["first_j"] != pinned:
            raise RuntimeError(
                f"{cell['id']} {arm} start_index={start_index}: first_j "
                f"{result['first_j']} != pin {pinned}"
            )
        print(
            f"DONE  {cell['id']} {arm} start_index={start_index} "
            f"status={result['status']} steps={result['steps']} "
            f"first_j={result['first_j']} sec={result['wall_clock_seconds']:.3f}",
            file=sys.stderr,
            flush=True,
        )
        if result["status"] in ("identity", "identity_at_start"):
            identity_events.append(result)
            continue
        if result["hit"] and result["landing_x"] not in vset:
            raise RuntimeError(f"{cell['id']} {arm}: claimed hit not in V")
        walks.append(result)
    completed = len(walks) == N_WALKS
    times = [w["steps"] for w in walks]
    mean = (sum(times) / len(times)) if times else None
    expected = n / D
    ratio = (mean / expected) if mean is not None else None
    factor2 = None if ratio is None else (ratio < 0.5 or ratio > 2.0)
    return {
        "label": arm,
        "cell": cell["id"],
        "N": n,
        "D": D,
        "cap_steps": cap,
        "expected_N_over_D": expected,
        "n_walks_requested": N_WALKS,
        "n_walks_completed": len(walks),
        "completed": completed,
        "walks": walks,
        "identity_events": identity_events,
        "mean_hitting_time": mean,
        "mean_over_N_over_D": ratio,
        "factor2_departure": factor2,
        "first_j_pins_all_match": all(w["first_j_matches_pin"] for w in walks),
    }


def evaluate_cell(cell: dict) -> dict:
    v_design = set(cell["V"])
    v_null3 = set(cell["V_NULL3"])
    if len(v_design) != D or len(v_null3) != D:
        raise RuntimeError(f"{cell['id']}: V not 20 distinct")
    return {
        "id": cell["id"],
        "p": cell["p"],
        "a": cell["a"],
        "b": cell["b"],
        "N": cell["N"],
        "generator_P": list(cell["P"]),
        "V": cell["V"],
        "V_NULL3": cell["V_NULL3"],
        "design": run_arm(cell, v_design, "design"),
        "null3": run_arm(cell, v_null3, "NULL-3"),
    }


def main() -> int:
    t0 = time.perf_counter()
    if len(ADDENDS) != R_ADDING:
        raise RuntimeError("addend count != r")
    for cell_id, arms in FIRST_J.items():
        for arm, js in arms.items():
            got = [walk_rng(cell_id, i, arm).randrange(R_ADDING) for i in range(10)]
            if got != js:
                raise RuntimeError(f"first_j pin failed {cell_id} {arm}: {got} != {js}")
    t2 = evaluate_cell(T2)
    t1 = evaluate_cell(T1)
    arms = [t2["design"], t2["null3"], t1["design"], t1["null3"]]
    fixture_pass = all(arm["completed"] for arm in arms)
    raw = {
        "run_id": "RUN-ECDLP-420e73-S11",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 11,
        "authorized_by": "DEC-20260908-53266e",
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "H3_factor2_miss_is_not_failed_infrastructure": True,
        "H3_miss_is_not_H1_closure": True,
        "eight_walks_is_not_1e4_KS": True,
        "c1_c2_c3_not_rerun": True,
        "deterministic_x_mod_16_not_rerun": True,
        "partition": "independent_uniform_0_15",
        "seed": SEED,
        "r": R_ADDING,
        "n_walks": N_WALKS,
        "addend_scalars": ADDENDS,
        "start_scalars": STARTS,
        "start_scalars_spare": SPARES,
        "null3_k": NULL3_K,
        "T2": t2,
        "T1": t1,
        "T2_design_mean": t2["design"]["mean_hitting_time"],
        "T2_design_mean_over_N_over_D": t2["design"]["mean_over_N_over_D"],
        "T2_design_factor2_departure": t2["design"]["factor2_departure"],
        "T2_null3_mean": t2["null3"]["mean_hitting_time"],
        "T2_null3_mean_over_N_over_D": t2["null3"]["mean_over_N_over_D"],
        "T2_null3_factor2_departure": t2["null3"]["factor2_departure"],
        "T1_design_mean": t1["design"]["mean_hitting_time"],
        "T1_design_mean_over_N_over_D": t1["design"]["mean_over_N_over_D"],
        "T1_design_factor2_departure": t1["design"]["factor2_departure"],
        "T1_null3_mean": t1["null3"]["mean_hitting_time"],
        "T1_null3_mean_over_N_over_D": t1["null3"]["mean_over_N_over_D"],
        "T1_null3_factor2_departure": t1["null3"]["factor2_departure"],
        "first_j_pins_all_match": all(arm["first_j_pins_all_match"] for arm in arms),
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": (
            "Toy H3 nearby-object re-randomized r-adding walks on frozen "
            "Stage 7 cells at p=16777213. Eight walks per arm, r=16, "
            "independent_uniform_0_15, cap 8*ceil(N/D). Not the idea's "
            "10^4-walk KS plan. The Stage 10 deterministic walk is not "
            "re-run. An H3 factor-2 miss is a model observation, not "
            "failed_infrastructure. An H3 miss is not H1 closure. Not H1. "
            "Not a W class. No a98ea9 Stage 5. C1, C2, and C3 are not "
            "re-run. C4 and fishing-1000 are Stage 12+."
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
