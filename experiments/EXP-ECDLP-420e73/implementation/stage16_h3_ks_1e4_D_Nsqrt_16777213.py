#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 16 H3 10^4-walk KS at D=round(N^{1/2}) per cell.

10000 independent_uniform r=16 adding walks per (cell x V-or-NULL3) arm.
T2 D=4096, T1 D=4095. KS versus Geometric(D/N) including T=0 is a
distance, not a test. Hard gate is fixture_pass. An H3 miss is a model
observation. Reuses the Stage 14 C walker. Stage 15 D=256 hitting times
are not nested. C1, C2, C3, Stage 10 x-mod-16, Stage 11 eight-walk
measurement, Stage 12 C4, Stage 13 fishing-1000, Stage 14 D=20 KS, and
Stage 15 D=256 KS are not re-run.

T2 NULL-3 x([k]P) has one freeze collision at stream indices 745 and
1623 (|unique V|=4095 at declared D=4096). That is not
failed_infrastructure. KS uses declared D/N.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import platform
import random
import resource
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage16_h3_ks_1e4_D_Nsqrt_16777213.py"
C_SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage14_walk.c"
REPO_ROOT = Path(__file__).resolve().parents[3]
IMPL_DIR = Path(__file__).resolve().parent
RUN_DIR = REPO_ROOT / "experiments/EXP-ECDLP-420e73/runs/RUN-ECDLP-420e73-S16"
REPORT_PATH = REPO_ROOT / "experiments/EXP-ECDLP-420e73/execution-report-s16.yaml"

P_FIELD = 16777213
R_ADDING = 16
N_WALKS = 10000
N_SPARES = 4096
SEED = 20260908
NMIN = 16770451
AUTHORIZED_BY = "DEC-20260908-04d446"
TASK_ID = "TASK-20260908-d7353d"

ADDENDS = [
    4083811, 14207148, 3197494, 5909533, 2112584, 3183261, 10497618, 7831654,
    5887209, 4196257, 199026, 3111920, 8124186, 1874953, 16389255, 8467452,
]
STARTS_REUSED = [
    16512131, 3548612, 6906991, 7276399, 14567537, 10110148, 14742596, 3279851,
    3740181, 16190719,
]
NULL3_K = None  # filled from Random(20260908) construction, not a YAML dump

EXTRA_START_PINS = {
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

# Stage 15 D=256 hitting times are not nested under D=round(N^{1/2}). first_j still matches.
STAGE7_V_PREFIX_T2 = [
    0, 14386069, 13311471, 510744, 13641516, 11286066, 16703438, 13064901,
    3436861, 9847978, 4422270, 2431989, 8626592, 2704728, 8015097, 11447766,
    8129445, 341717, 16207358, 12600408,
]
STAGE7_V_PREFIX_T1 = [
    6, 4288347, 2837810, 15061002, 7941042, 3891067, 6883471, 15571429,
    15172588, 6789969, 6889484, 865709, 4039235, 6596143, 14029655, 5242584,
    7908075, 2872040, 4197418, 1510565,
]
STAGE10_NULL3_K_PREFIX = [
    12664300, 6842134, 11844367, 6996586, 4488890, 6629474, 1373371, 715077,
    12256922, 7014070, 15143700, 12434262, 1263476, 13985324, 4621790, 8306822,
    2915849, 13925014, 13948079, 8437742,
]

PIN_K21 = {"S7-T2-P16777213": 919160, "S7-T1-P16777213": 11575537}
PIN_K256 = {"S7-T2-P16777213": 16283645, "S7-T1-P16777213": 8804309}
PIN_K_D = {"S7-T2-P16777213": 15023503, "S7-T1-P16777213": 2439767}
PIN_NULL3_K20 = 4442873
PIN_NULL3_K255 = 3925208
PIN_NULL3_K4094 = 5707805
PIN_NULL3_K4095 = 8435369
PIN_NULL3_V20 = {"S7-T2-P16777213": 4443814, "S7-T1-P16777213": 6296420}
PIN_NULL3_V255 = {"S7-T2-P16777213": 16523022, "S7-T1-P16777213": 11205200}
PIN_NULL3_V_END = {"S7-T2-P16777213": 8711474, "S7-T1-P16777213": 13739162}
NULL3_T2_COLLISION_INDICES = (745, 1623)


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


def draw_null3_k(n: int = 4096) -> list[int]:
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
    while len(k) < n:
        s = rng.randrange(1, NMIN)
        if s in forbidden:
            continue
        k.append(s)
        forbidden.add(s)
    if addends != ADDENDS or starts != STARTS_REUSED:
        raise RuntimeError("NULL-3 stream addends/starts mismatch")
    return k


def design_V(p: int, a: int, P, D: int) -> list[int]:
    R = None
    xs: list[int] = []
    for _k in range(1, D + 1):
        R = add(p, a, R, P)
        if R is None:
            raise RuntimeError(f"design V hit O at k={_k}")
        xs.append(R[0])
    return xs


def _load_cells():
    t2 = {
        "id": "S7-T2-P16777213", "p": P_FIELD, "a": 19, "b": 107, "N": 16777213,
        "P": (0, 1722727), "D": 4096, "cap_steps": 32768,
    }
    t1 = {
        "id": "S7-T1-P16777213", "p": P_FIELD, "a": 0, "b": 7, "N": 16770451,
        "P": (6, 7827705), "D": 4095, "cap_steps": 32768,
    }
    k = draw_null3_k(4096)
    t2["V"] = design_V(t2["p"], t2["a"], t2["P"], t2["D"])
    t1["V"] = design_V(t1["p"], t1["a"], t1["P"], t1["D"])
    t2["V_NULL3"] = []
    for kk in k:
        Q = mul(t2["p"], t2["a"], kk, t2["P"])
        if Q is None:
            raise RuntimeError(f"T2 NULL-3 hit O at k={kk}")
        t2["V_NULL3"].append(Q[0])
    t1["V_NULL3"] = []
    for kk in k[: t1["D"]]:
        Q = mul(t1["p"], t1["a"], kk, t1["P"])
        if Q is None:
            raise RuntimeError(f"T1 NULL-3 hit O at k={kk}")
        t1["V_NULL3"].append(Q[0])
    return t2, t1, k


T2, T1, NULL3_K = _load_cells()

_LIB = None


def cap_steps(n: int, D: int) -> int:
    return 8 * math.ceil(n / D)


def walk_rng(cell_id: str, start_index: int, arm: str) -> random.Random:
    material = f"{SEED}|{cell_id}|{start_index}|{arm}".encode("ascii")
    walk_rng_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return random.Random(walk_rng_seed)


def first_j_of(cell_id: str, start_index: int, arm: str) -> int:
    return walk_rng(cell_id, start_index, arm).randrange(R_ADDING)


def extra_starts() -> tuple[list[int], int]:
    nmin = 16770451
    forbidden = set(ADDENDS) | set(STARTS_REUSED)
    material = f"{SEED}|stage14_extra_starts".encode("ascii")
    rng_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    rng = random.Random(rng_seed)
    extra: list[int] = []
    skips = 0
    while len(extra) < 9990 + N_SPARES:
        s = rng.randrange(1, nmin)
        if s in forbidden or s in extra:
            skips += 1
            continue
        extra.append(s)
    return extra, skips


def all_start_scalars() -> tuple[list[int], dict]:
    extra, skips = extra_starts()
    starts = list(STARTS_REUSED) + extra
    expected = 10 + 9990 + N_SPARES
    if len(starts) != expected:
        raise RuntimeError(f"start list length {len(starts)} != {expected}")
    pins = {
        "material_sha256": hashlib.sha256(f"{SEED}|stage14_extra_starts".encode("ascii")).hexdigest(),
        "rng_seed": int.from_bytes(
            hashlib.sha256(f"{SEED}|stage14_extra_starts".encode("ascii")).digest()[:8], "big"
        ),
        "start_index_10": starts[10],
        "start_index_11": starts[11],
        "start_index_9999": starts[9999],
        "start_index_10000_first_spare": starts[10000],
        "start_index_10031": starts[10031],
        "start_index_10032_first_new_spare": starts[10032],
        "start_index_14095_last_spare": starts[14095],
        "n_collision_skips_in_this_draw": skips,
    }
    match = all(pins[k] == EXTRA_START_PINS[k] for k in EXTRA_START_PINS if k != "material_ascii")
    return starts, {"pins": pins, "match": match}


def compile_lib() -> Path:
    so_path = IMPL_DIR / "stage14_walk.so"
    c_path = IMPL_DIR / "stage14_walk.c"
    cmd = [
        "gcc", "-O3", "-march=native", "-shared", "-fPIC",
        "-o", str(so_path), str(c_path),
    ]
    subprocess.check_call(cmd)
    return so_path


def load_lib():
    global _LIB
    if _LIB is not None:
        return _LIB
    so_path = compile_lib()
    lib = ctypes.CDLL(str(so_path))
    lib.stage14_walk.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int64,
        ctypes.POINTER(ctypes.c_int64),
    ]
    lib.stage14_walk.restype = None
    _LIB = lib
    return lib


def mt_state(rng: random.Random):
    st = rng.getstate()
    mt = (ctypes.c_uint32 * 624)(*st[1][:624])
    index = int(st[1][624])
    return mt, index


def vbits_for(p: int, vset: set[int]):
    nwords = (p + 31) // 32
    bits = (ctypes.c_uint32 * nwords)()
    for v in vset:
        if v < 0 or v >= p:
            raise RuntimeError(f"V element {v} not in 0..{p-1}")
        bits[v >> 5] |= 1 << (v & 31)
    return bits


def c_walk(lib, rng, p, a, add_x, add_y, start_pt, vbits, cap):
    mt, index = mt_state(rng)
    out = (ctypes.c_int64 * 5)()
    if start_pt is None:
        sx = sy = 0
        start_inf = 1
    else:
        sx, sy = start_pt
        start_inf = 0
    lib.stage14_walk(
        mt, index, p, a, add_x, add_y,
        sx, sy, start_inf, vbits, cap, out,
    )
    status_code = int(out[0])
    status = {0: "hit", 1: "capped", 2: "identity", 3: "identity_at_start"}[status_code]
    return {
        "status": status,
        "steps": int(out[1]),
        "landing_x": None if int(out[2]) < 0 else int(out[2]),
        "first_j": int(out[3]),
        "first_j_used_as_step": bool(out[4]),
        "capped": status == "capped",
        "hit": status == "hit",
    }


def f_geo(t: int, p: float) -> float:
    return 1.0 - (1.0 - p) ** (t + 1)


def ks_distance(times: list[int], p: float):
    if not times:
        return None
    m = len(times)
    counts = Counter(times)
    seen = 0
    ks = 0.0
    for t in sorted(counts):
        seen += counts[t]
        fn = seen / m
        d = abs(fn - f_geo(t, p))
        if d > ks:
            ks = d
    return ks


def t_geo_99(p: float) -> int:
    # smallest integer t with F_geo(t) >= 0.99
    target = 0.99
    t = int(math.ceil(math.log(1.0 - target) / math.log(1.0 - p))) - 1
    if t < 0:
        t = 0
    while f_geo(t, p) < target:
        t += 1
    while t > 0 and f_geo(t - 1, p) >= target:
        t -= 1
    return t


def percentile_99(times: list[int]):
    if not times:
        return None
    m = len(times)
    k = math.ceil(0.99 * m)
    if k < 1:
        k = 1
    if k > m:
        k = m
    return sorted(times)[k - 1]


def precompute_cell(cell: dict, starts: list[int]):
    p, a, P = cell["p"], cell["a"], cell["P"]
    addend_pts = []
    for s in ADDENDS:
        Q = mul(p, a, s, P)
        if Q is None:
            raise RuntimeError(f"{cell['id']}: addend scalar produced O")
        addend_pts.append(Q)
    start_pts = []
    for s in starts:
        start_pts.append(mul(p, a, s, P))
    return addend_pts, start_pts


def run_arm(payload: dict) -> dict:
    lib = load_lib()
    cell = payload["cell"]
    arm = payload["arm"]
    vlist = payload["vlist"]
    starts = payload["starts"]
    addend_pts = payload["addend_pts"]
    start_pts = payload["start_pts"]
    p, a, n = cell["p"], cell["a"], cell["N"]
    D_cell = cell["D"]
    cap = cap_steps(n, D_cell)
    if cap != cell["cap_steps"]:
        raise RuntimeError(f"{cell['id']}: cap_steps {cap} != {cell['cap_steps']}")
    vset = set(vlist)
    if arm == "NULL-3" and cell["id"] == "S7-T2-P16777213":
        i_col, j_col = NULL3_T2_COLLISION_INDICES
        if len(vlist) != D_cell:
            raise RuntimeError(
                f"{cell['id']} {arm}: V length {len(vlist)} != declared D {D_cell}"
            )
        if len(vset) != D_cell - 1:
            raise RuntimeError(
                f"{cell['id']} {arm}: |unique V|={len(vset)} != {D_cell - 1} "
                "(T2 NULL-3 freeze collision)"
            )
        if vlist[i_col] != vlist[j_col]:
            raise RuntimeError(
                f"{cell['id']} {arm}: missing freeze x-collision at {i_col} and {j_col}"
            )
    else:
        if len(vlist) != D_cell or len(vset) != D_cell:
            raise RuntimeError(
                f"{cell['id']} {arm}: V not {D_cell} distinct "
                f"(len={len(vlist)} nunique={len(vset)})"
            )
    vbits = vbits_for(p, vset)
    add_x = (ctypes.c_int64 * R_ADDING)(*(Q[0] for Q in addend_pts))
    add_y = (ctypes.c_int64 * R_ADDING)(*(Q[1] for Q in addend_pts))

    hitting_times: list[int] = []
    capped_flags: list[int] = []
    landing_x: list[int] = []
    start_index_used: list[int] = []
    start_scalar_used: list[int] = []
    first_js: list[int] = []
    identity_events: list[dict] = []
    spare_next = N_WALKS
    t_arm = time.perf_counter()
    for i in range(N_WALKS):
        start_index = i
        while True:
            rng = walk_rng(cell["id"], start_index, arm)
            start_pt = start_pts[start_index]
            result = c_walk(lib, rng, p, a, add_x, add_y, start_pt, vbits, cap)
            result["start_index"] = start_index
            result["start_scalar"] = starts[start_index]
            if result["status"] in ("identity", "identity_at_start"):
                identity_events.append({
                    "start_index": start_index,
                    "start_scalar": starts[start_index],
                    "status": result["status"],
                    "steps": result["steps"],
                    "first_j": result["first_j"],
                    "official_walk": i,
                })
                if spare_next > 14095:
                    raise RuntimeError(
                        f"{cell['id']} {arm}: spare exhaustion below 10000 completed walks"
                    )
                start_index = spare_next
                spare_next += 1
                continue
            if result["hit"] and result["landing_x"] not in vset:
                raise RuntimeError(f"{cell['id']} {arm}: claimed hit not in V")
            hitting_times.append(result["steps"])
            capped_flags.append(1 if result["capped"] else 0)
            landing_x.append(-1 if result["landing_x"] is None else result["landing_x"])
            start_index_used.append(start_index)
            start_scalar_used.append(starts[start_index])
            first_js.append(result["first_j"])
            break
        if (i + 1) % 500 == 0:
            print(
                f"PROGRESS {cell['id']} {arm} {i+1}/{N_WALKS} "
                f"sec={time.perf_counter()-t_arm:.1f}",
                file=sys.stderr,
                flush=True,
            )

    n_capped = sum(capped_flags)
    uncensored = [t for t, c in zip(hitting_times, capped_flags) if c == 0]
    m = len(uncensored)
    p_geo = D_cell / n
    ks = ks_distance(uncensored, p_geo)
    mean = (sum(hitting_times) / len(hitting_times)) if hitting_times else None
    expected = n / D_cell
    ratio = (mean / expected) if mean is not None else None
    factor2 = None if ratio is None else (ratio < 0.5 or ratio > 2.0)
    fj0 = first_j_of(cell["id"], 0, arm)
    fj10 = first_j_of(cell["id"], 10, arm)
    return {
        "label": arm,
        "cell": cell["id"],
        "N": n,
        "D": D_cell,
        "nunique_V": len(vset),
        "cap_steps": cap,
        "expected_N_over_D": expected,
        "n_walks_requested": N_WALKS,
        "n_walks_completed": len(hitting_times),
        "completed": len(hitting_times) == N_WALKS,
        "hitting_times": hitting_times,
        "capped_flags": capped_flags,
        "landing_x": landing_x,
        "start_index_used": start_index_used,
        "start_scalar_used": start_scalar_used,
        "first_j": first_js,
        "identity_events": identity_events,
        "n_identity_events": len(identity_events),
        "n_capped": n_capped,
        "n_uncensored": m,
        "ks_distance": ks,
        "ks_within_0_10": (ks is not None and ks <= 0.10),
        "mean_hitting_time": mean,
        "mean_over_N_over_D": ratio,
        "factor2_departure": factor2,
        "percentile_99": percentile_99(uncensored),
        "t_geo_99": t_geo_99(p_geo),
        "first_j_idx0": fj0,
        "first_j_idx10": fj10,
        "first_j_idx0_match": fj0 == FIRST_J_IDX0[cell["id"]][arm],
        "first_j_idx10_match": fj10 == FIRST_J_IDX10[cell["id"]][arm],
        "p_geo": p_geo,
        "wall_clock_seconds": time.perf_counter() - t_arm,
        "claimed_hits_in_V": True,
    }


def self_test(starts: list[int]) -> None:
    lib = load_lib()
    rng = random.Random(12345)
    py = [rng.randrange(16) for _ in range(64)]
    rng = random.Random(12345)
    mt, index = mt_state(rng)
    # draw 64 j via a dummy walk would also consume add; instead copy MT loop in Python.
    # Direct: after copying state, C walk draws inside walk. Check first_j pins instead.
    for cell_id, arms in FIRST_J_IDX0.items():
        for arm, expect in arms.items():
            got = first_j_of(cell_id, 0, arm)
            if got != expect:
                raise RuntimeError(f"first_j idx0 {cell_id} {arm}: {got} != {expect}")
    for cell_id, arms in FIRST_J_IDX10.items():
        for arm, expect in arms.items():
            got = first_j_of(cell_id, 10, arm)
            if got != expect:
                raise RuntimeError(f"first_j idx10 {cell_id} {arm}: {got} != {expect}")
    example = hashlib.sha256(b"20260908|S7-T2-P16777213|10|design").hexdigest()[:16]
    if example != "d7f48ffdde092e0f":
        raise RuntimeError(f"example prefix {example}")

    # Compare 64 randrange(16) from copied MT against Python.
    class _Tmp:
        pass

    # C first_j must match Python first_j. Do not compare hitting times to Stage 14.
    for cell, arm_key, vkey in (
        (T1, "design", "V"),
        (T1, "NULL-3", "V_NULL3"),
        (T2, "design", "V"),
        (T2, "NULL-3", "V_NULL3"),
    ):
        p, a, P = cell["p"], cell["a"], cell["P"]
        addend_pts = [mul(p, a, s, P) for s in ADDENDS]
        add_x = (ctypes.c_int64 * R_ADDING)(*(Q[0] for Q in addend_pts))
        add_y = (ctypes.c_int64 * R_ADDING)(*(Q[1] for Q in addend_pts))
        vbits = vbits_for(p, set(cell[vkey]))
        cap = cap_steps(cell["N"], cell["D"])
        start_pt = mul(p, a, starts[0], P)
        rng = walk_rng(cell["id"], 0, arm_key)
        result = c_walk(lib, rng, p, a, add_x, add_y, start_pt, vbits, cap)
        expect_j = FIRST_J_IDX0[cell["id"]][arm_key]
        if result["first_j"] != expect_j:
            raise RuntimeError(
                f"C first_j {cell['id']} {arm_key} {result['first_j']} != {expect_j}"
            )
        print(
            f"SELFTEST {cell['id']} {arm_key} walk0 status={result['status']} "
            f"first_j={result['first_j']} OK (hitting time not compared to Stage 15)",
            file=sys.stderr,
            flush=True,
        )
    if T2["V"][:20] != STAGE7_V_PREFIX_T2:
        raise RuntimeError("T2 design V prefix does not match Stage 7")
    if T1["V"][:20] != STAGE7_V_PREFIX_T1:
        raise RuntimeError("T1 design V prefix does not match Stage 7")
    if NULL3_K[:20] != STAGE10_NULL3_K_PREFIX:
        raise RuntimeError("NULL-3 k prefix does not match Stage 10")
    if T2["V"][20] != PIN_K21["S7-T2-P16777213"] or T2["V"][255] != PIN_K256["S7-T2-P16777213"]:
        raise RuntimeError("T2 k=21/k=256 pins failed")
    if T1["V"][20] != PIN_K21["S7-T1-P16777213"] or T1["V"][255] != PIN_K256["S7-T1-P16777213"]:
        raise RuntimeError("T1 k=21/k=256 pins failed")
    if T2["V"][-1] != PIN_K_D["S7-T2-P16777213"] or T1["V"][-1] != PIN_K_D["S7-T1-P16777213"]:
        raise RuntimeError("design V k=D pins failed")
    if NULL3_K[20] != PIN_NULL3_K20 or NULL3_K[255] != PIN_NULL3_K255:
        raise RuntimeError("NULL-3 k index 20/255 pins failed")
    if NULL3_K[4094] != PIN_NULL3_K4094 or NULL3_K[4095] != PIN_NULL3_K4095:
        raise RuntimeError("NULL-3 k index 4094/4095 pins failed")
    if T2["V_NULL3"][20] != PIN_NULL3_V20["S7-T2-P16777213"] or T2["V_NULL3"][255] != PIN_NULL3_V255["S7-T2-P16777213"]:
        raise RuntimeError("T2 NULL-3 V index 20/255 pins failed")
    if T1["V_NULL3"][20] != PIN_NULL3_V20["S7-T1-P16777213"] or T1["V_NULL3"][255] != PIN_NULL3_V255["S7-T1-P16777213"]:
        raise RuntimeError("T1 NULL-3 V index 20/255 pins failed")
    if T2["V_NULL3"][-1] != PIN_NULL3_V_END["S7-T2-P16777213"]:
        raise RuntimeError("T2 NULL-3 V D-end pin failed")
    if T1["V_NULL3"][-1] != PIN_NULL3_V_END["S7-T1-P16777213"]:
        raise RuntimeError("T1 NULL-3 V D-end pin failed")
    if cap_steps(T2["N"], T2["D"]) != T2["cap_steps"] or cap_steps(T1["N"], T1["D"]) != T1["cap_steps"]:
        raise RuntimeError("cap_steps mismatch")
    if len(T2["V"]) != 4096 or len(T1["V"]) != 4095 or len(NULL3_K) != 4096:
        raise RuntimeError("per-cell D length mismatch")
    if len(T1["V_NULL3"]) != 4095 or len(T2["V_NULL3"]) != 4096:
        raise RuntimeError("NULL-3 V length mismatch")
    if len(set(T2["V"])) != 4096 or len(set(T1["V"])) != 4095:
        raise RuntimeError("design V is not D-distinct")
    if len(set(T1["V_NULL3"])) != 4095:
        raise RuntimeError("T1 NULL-3 V is not 4095-distinct")
    i_col, j_col = NULL3_T2_COLLISION_INDICES
    if T2["V_NULL3"][i_col] != T2["V_NULL3"][j_col]:
        raise RuntimeError("T2 NULL-3 freeze collision missing")
    if len(set(T2["V_NULL3"])) != 4095:
        raise RuntimeError("T2 NULL-3 |unique V| is not 4095")
    for cell, prefix in ((T2, STAGE7_V_PREFIX_T2), (T1, STAGE7_V_PREFIX_T1)):
        p, a, P = cell["p"], cell["a"], cell["P"]
        live = []
        for k in range(1, cell["D"] + 1):
            Q = mul(p, a, k, P)
            if Q is None:
                raise RuntimeError(f"{cell['id']} [k]P identity at k={k}")
            live.append(Q[0])
        if live != cell["V"]:
            raise RuntimeError(f"{cell['id']} live design V != reconstructed V")
        if live[:20] != prefix:
            raise RuntimeError(f"{cell['id']} live prefix != Stage 7")
        if live[20] != PIN_K21[cell["id"]] or live[255] != PIN_K256[cell["id"]]:
            raise RuntimeError(f"{cell['id']} live k=21/256 pins failed")
        if live[-1] != PIN_K_D[cell["id"]]:
            raise RuntimeError(f"{cell['id']} live k=D pin failed")
        null_k = NULL3_K if cell["id"] == "S7-T2-P16777213" else NULL3_K[: cell["D"]]
        null_v = []
        for k in null_k:
            Q = mul(p, a, k, P)
            if Q is None:
                raise RuntimeError(f"{cell['id']} NULL-3 [k]P identity at k={k}")
            null_v.append(Q[0])
        if null_v != cell["V_NULL3"]:
            raise RuntimeError(f"{cell['id']} live NULL-3 V != reconstructed V")
        if null_v[20] != PIN_NULL3_V20[cell["id"]] or null_v[255] != PIN_NULL3_V255[cell["id"]]:
            raise RuntimeError(f"{cell['id']} live NULL-3 V index 20/255 pins failed")
        if null_v[-1] != PIN_NULL3_V_END[cell["id"]]:
            raise RuntimeError(f"{cell['id']} live NULL-3 V D-end pin failed")
    print("SELFTEST live design V and NULL-3 V reconstruct OK", file=sys.stderr, flush=True)
    # Silence unused.
    del py, _Tmp


def git_state() -> dict:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    porcelain = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
    )
    return {
        "commit": commit,
        "dirty": bool(porcelain.strip()),
        "dirty_summary": porcelain.strip()[:2000] if porcelain.strip() else "",
    }


def _yaml_dump(obj) -> str:
    try:
        import yaml  # type: ignore

        return yaml.safe_dump(obj, sort_keys=False)
    except Exception:
        return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def write_artifacts(raw: dict, stdout_text: str, stderr_text: str, cmd: str) -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    (RUN_DIR / "stdout.log").write_text(stdout_text)
    (RUN_DIR / "stderr.log").write_text(stderr_text)
    (RUN_DIR / "command.txt").write_text(cmd + "\n")
    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
        "nproc": os.cpu_count(),
    }
    (RUN_DIR / "environment.json").write_text(json.dumps(env, indent=2, sort_keys=True) + "\n")
    git = git_state()
    recorded = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = {
        "run": {
            "id": "RUN-ECDLP-420e73-S16",
            "experiment_id": "EXP-ECDLP-420e73",
            "hypothesis_id": "H-ECDLP-77caa5",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": TASK_ID,
            "stage": 16,
            "status": "completed_valid" if raw["fixture_pass"] else "failed_infrastructure",
            "recorded_at": recorded,
            "authorized_by": AUTHORIZED_BY,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_summary": (
                    "Untracked Stage 16 implementation and RUN-ECDLP-420e73-S16 "
                    "artifacts at run time."
                    if git["dirty"]
                    else ""
                ),
                "command": cmd,
                "source_path": SOURCE,
                "c_source_path": C_SOURCE,
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": "cursor-grok-4.6-cloud-agent",
                "model_provenance": "cursor cloud agent session acting as executor",
                "model_verified": False,
                "reasoning_effort": "medium",
                "fallback_used": False,
                "degraded_requirements": None,
            },
            "environment": {
                "python": env["python"],
                "platform": env["platform"],
                "machine": env["machine"],
            },
            "inputs": {
                "parameters": {
                    "T2": {"p": 16777213, "a": 19, "b": 107, "N": 16777213, "P": [0, 1722727], "D": 4096},
                    "T1": {"p": 16777213, "a": 0, "b": 7, "N": 16770451, "P": [6, 7827705], "D": 4095},
                    "D_rule": "round(N**(1/2)) per cell",
                    "r": 16,
                    "n_walks": 10000,
                    "seed": SEED,
                    "partition": "independent_uniform_0_15",
                    "authorized_by": AUTHORIZED_BY,
                },
                "seeds": {"declared": [SEED]},
            },
            "timing": {"wall_clock_seconds": raw["wall_clock_seconds"]},
            "resources": {
                "wall_clock_seconds": raw["wall_clock_seconds"],
                "peak_rss_bytes": raw["peak_rss_bytes"],
            },
            "result": {
                "validity_status": raw["validity_status"],
                "valid": raw["fixture_pass"],
                "validity_reason": (
                    "Stage 16 H3 10^4-walk KS fixture_pass. Walks completed. "
                    "KS distance and a factor-2 miss are not hard gates. "
                    "T2 NULL-3 freeze collision is not failed_infrastructure."
                    if raw["fixture_pass"]
                    else "Stage 16 fixture_pass failed."
                ),
                "certificate": {"kind": "none", "verified": True},
                "metrics": {
                    "fixture_pass": raw["fixture_pass"],
                    "extra_start_pins_match": raw["extra_start_pins_match"],
                    "first_j_idx0_all_match": raw["first_j_idx0_all_match"],
                    "first_j_idx10_all_match": raw["first_j_idx10_all_match"],
                    "stage15_d256_hitting_times_not_nested": True,
                    "H3_factor2_miss_is_not_failed_infrastructure": True,
                    "H3_miss_is_not_H1_closure": True,
                    "ks_is_not_a_gate": True,
                    "ks_is_not_H1_support": True,
                    "t2_null3_collision_is_not_failed_infrastructure": True,
                    "stage11_eight_walks_not_the_measurement": True,
                    "deterministic_x_mod_16_not_rerun": True,
                    "c1_c2_c3_not_rerun": True,
                    "c4_first_slice_not_rerun": True,
                    "fishing_1000_not_rerun": True,
                    "stage14_d20_ks_not_rerun": True,
                    "stage15_d256_ks_not_rerun": True,
                    "not_an_H1_claim": True,
                    "SMALL_W_or_LARGE_W": False,
                },
                "scientific_boundary": raw["scientific_boundary"],
            },
            "artifacts": {
                "raw_result": "raw-result.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "environment": "environment.json",
                "command": "command.txt",
            },
        }
    }
    (RUN_DIR / "manifest.yaml").write_text(_yaml_dump(manifest))


def write_report(raw: dict) -> None:
    arms = raw["arms_summary"]
    obs = [
        "10000 walks completed or hit cap on every declared arm. fixture_pass is "
        + ("true" if raw["fixture_pass"] else "false")
        + ". Certificate kind none.",
        "Extra-start pins at indices 10, 11, 9999, 10000, and 10031 matched.",
        "first_j at start_index 0 matched Stage 11 on every arm. first_j at start_index 10 matched the protocol pins.",
        "Stage 15 D=256 hitting times are not nested under D=round(N^{1/2}). Stage 11's eight walks are not the measurement.",
        "T2 NULL-3 freeze x-collision at indices 745 and 1623 is recorded. KS uses declared D/N. Not failed_infrastructure.",
    ]
    for row in arms:
        obs.append(
            f"{row['cell']} {row['label']}: n_uncensored={row['n_uncensored']} "
            f"n_capped={row['n_capped']} n_identity={row['n_identity_events']} "
            f"factor2_departure={row['factor2_departure']} "
            f"ks_within_0_10={row['ks_within_0_10']}."
        )
    report = {
        "execution_report": {
            "id": "ER-ECDLP-420e73-S16",
            "experiment_id": "EXP-ECDLP-420e73",
            "run_id": "RUN-ECDLP-420e73-S16",
            "task_id": TASK_ID,
            "recorded_at": "2026-09-08",
            "stage": 16,
            "authorized_by": AUTHORIZED_BY,
            "validity_status": raw["validity_status"],
            "fixture_pass": raw["fixture_pass"],
            "certificate": {"kind": "none", "verified": True},
            "SMALL_W_or_LARGE_W": False,
            "fit_of_a": False,
            "exp_a98ea9_stage5_authorized": False,
            "not_an_H1_claim": True,
            "h3_ks_is_not_H1_support": True,
            "H3_factor2_miss_is_not_failed_infrastructure": True,
            "H3_miss_is_not_H1_closure": True,
            "ks_is_not_a_gate": True,
            "ks_distance_is_not_a_p_value": True,
            "stage11_eight_walks_not_the_measurement": True,
            "deterministic_x_mod_16_not_rerun": True,
            "c1_c2_c3_not_rerun": True,
            "c4_first_slice_not_rerun": True,
            "fishing_1000_not_rerun": True,
            "stage14_d20_ks_not_rerun": True,
            "stage15_d256_ks_not_rerun": True,
            "extra_start_pins_match": raw["extra_start_pins_match"],
            "first_j_idx0_all_match": raw["first_j_idx0_all_match"],
            "first_j_idx10_all_match": raw["first_j_idx10_all_match"],
            "stage15_d256_hitting_times_not_nested": True,
            "t2_null3_collision_is_not_failed_infrastructure": True,
            "observations": obs,
            "unexpected_observations": [
                "KS values, means, factor-2 flags, n_capped, and 99th percentiles "
                "are H3 observations at these cells, this partition, "
                "D=round(N^{1/2}), and 10000 walks. They are not H1 and not "
                "failed_infrastructure. T2 NULL-3 freeze collision is not "
                "failed_infrastructure. Unofficial floats are in raw-result.json, "
                "not in commit messages."
            ],
            "scientific_boundary": raw["scientific_boundary"],
        }
    }
    REPORT_PATH.write_text(_yaml_dump(report))


def arm_summary(arm: dict) -> dict:
    return {
        "cell": arm["cell"],
        "label": arm["label"],
        "D": arm["D"],
        "nunique_V": arm["nunique_V"],
        "n_walks_completed": arm["n_walks_completed"],
        "n_capped": arm["n_capped"],
        "n_uncensored": arm["n_uncensored"],
        "n_identity_events": arm["n_identity_events"],
        "ks_distance": arm["ks_distance"],
        "ks_within_0_10": arm["ks_within_0_10"],
        "mean_hitting_time": arm["mean_hitting_time"],
        "mean_over_N_over_D": arm["mean_over_N_over_D"],
        "factor2_departure": arm["factor2_departure"],
        "percentile_99": arm["percentile_99"],
        "t_geo_99": arm["t_geo_99"],
        "first_j_idx0": arm["first_j_idx0"],
        "first_j_idx10": arm["first_j_idx10"],
        "first_j_idx0_match": arm["first_j_idx0_match"],
        "first_j_idx10_match": arm["first_j_idx10_match"],
        "claimed_hits_in_V": arm["claimed_hits_in_V"],
        "completed": arm["completed"],
        "wall_clock_seconds": arm["wall_clock_seconds"],
        "cap_steps": arm["cap_steps"],
        "expected_N_over_D": arm["expected_N_over_D"],
        "identity_events": arm["identity_events"],
    }


def main() -> int:
    t0 = time.perf_counter()
    stderr_chunks: list[str] = []

    def log(msg: str) -> None:
        print(msg, file=sys.stderr, flush=True)
        stderr_chunks.append(msg + "\n")

    starts, extra_info = all_start_scalars()
    if not extra_info["match"]:
        raise RuntimeError(f"extra-start pins failed: {extra_info}")
    log("extra-start pins OK")
    compile_lib()
    log("compiled stage14_walk.so (reused Stage 14 C walker)")
    self_test(starts)
    log("self-test first_j / V pins OK (Stage 15 hitting times not nested)")
    if "--self-test" in sys.argv:
        print(json.dumps({"self_test": "ok", "extra_start_pins_match": True}, indent=2))
        return 0

    log("precomputing addend and start points")
    t_pre = time.perf_counter()
    t2_add, t2_starts = precompute_cell(T2, starts)
    t1_add, t1_starts = precompute_cell(T1, starts)
    log(f"precompute sec={time.perf_counter()-t_pre:.3f}")

    jobs = [
        {"cell": T2, "arm": "design", "vlist": T2["V"], "starts": starts,
         "addend_pts": t2_add, "start_pts": t2_starts},
        {"cell": T2, "arm": "NULL-3", "vlist": T2["V_NULL3"], "starts": starts,
         "addend_pts": t2_add, "start_pts": t2_starts},
        {"cell": T1, "arm": "design", "vlist": T1["V"], "starts": starts,
         "addend_pts": t1_add, "start_pts": t1_starts},
        {"cell": T1, "arm": "NULL-3", "vlist": T1["V_NULL3"], "starts": starts,
         "addend_pts": t1_add, "start_pts": t1_starts},
    ]
    results = {}
    with ProcessPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_arm, job): (job["cell"]["id"], job["arm"]) for job in jobs}
        for fut in as_completed(futs):
            key = futs[fut]
            arm = fut.result()
            results[key] = arm
            log(
                f"DONE {arm['cell']} {arm['label']} completed={arm['completed']} "
                f"n_capped={arm['n_capped']} n_identity={arm['n_identity_events']} "
                f"sec={arm['wall_clock_seconds']:.1f}"
            )

    t2d = results[("S7-T2-P16777213", "design")]
    t2n = results[("S7-T2-P16777213", "NULL-3")]
    t1d = results[("S7-T1-P16777213", "design")]
    t1n = results[("S7-T1-P16777213", "NULL-3")]
    arms = [t2d, t2n, t1d, t1n]
    extra_match = extra_info["match"]
    fj0 = all(a["first_j_idx0_match"] for a in arms)
    fj10 = all(a["first_j_idx10_match"] for a in arms)
    hits_in_v = all(a["claimed_hits_in_V"] for a in arms)
    completed = all(a["completed"] for a in arms)
    v_prefix = T2["V"][:20] == STAGE7_V_PREFIX_T2 and T1["V"][:20] == STAGE7_V_PREFIX_T1
    null3_prefix = NULL3_K[:20] == STAGE10_NULL3_K_PREFIX
    v_pins = (
        T2["V"][20] == PIN_K21["S7-T2-P16777213"]
        and T2["V"][255] == PIN_K256["S7-T2-P16777213"]
        and T2["V"][-1] == PIN_K_D["S7-T2-P16777213"]
        and T1["V"][20] == PIN_K21["S7-T1-P16777213"]
        and T1["V"][255] == PIN_K256["S7-T1-P16777213"]
        and T1["V"][-1] == PIN_K_D["S7-T1-P16777213"]
        and NULL3_K[20] == PIN_NULL3_K20
        and NULL3_K[255] == PIN_NULL3_K255
        and NULL3_K[4094] == PIN_NULL3_K4094
        and NULL3_K[4095] == PIN_NULL3_K4095
        and T2["V_NULL3"][20] == PIN_NULL3_V20["S7-T2-P16777213"]
        and T1["V_NULL3"][20] == PIN_NULL3_V20["S7-T1-P16777213"]
        and T2["V_NULL3"][255] == PIN_NULL3_V255["S7-T2-P16777213"]
        and T1["V_NULL3"][255] == PIN_NULL3_V255["S7-T1-P16777213"]
        and T2["V_NULL3"][-1] == PIN_NULL3_V_END["S7-T2-P16777213"]
        and T1["V_NULL3"][-1] == PIN_NULL3_V_END["S7-T1-P16777213"]
    )
    i_col, j_col = NULL3_T2_COLLISION_INDICES
    t2_null3_collision = (
        T2["V_NULL3"][i_col] == T2["V_NULL3"][j_col]
        and len(set(T2["V_NULL3"])) == 4095
        and len(set(T1["V_NULL3"])) == 4095
        and len(set(T2["V"])) == 4096
        and len(set(T1["V"])) == 4095
    )
    fixture_pass = (
        extra_match and fj0 and fj10 and completed and hits_in_v
        and v_prefix and null3_prefix and v_pins and t2_null3_collision
    )
    scientific_boundary = (
        "Toy H3 10^4-walk Kolmogorov-Smirnov on frozen Stage 7 cells at "
        "p=16777213, D=round(N^{1/2}) per cell (T2 4096, T1 4095). 10000 "
        "independent_uniform r=16 walks per arm, cap 8*ceil(N/D), "
        "Geometric(D/N) including T=0. KS is a distance, not a test and "
        "not a gate. An H3 miss is a model observation, not "
        "failed_infrastructure and not H1 closure. T2 NULL-3 freeze "
        "x-collision at indices 745 and 1623 is not failed_infrastructure; "
        "KS uses declared D/N. Stage 15 D=256 hitting times are not nested. "
        "Stage 11's eight walks are not the measurement. The Stage 10 "
        "deterministic x-mod-16 walk is not re-run. C1, C2, C3, the Stage 12 "
        "three-arm C4, Stage 13 fishing-1000, the Stage 14 D=20 KS, and the "
        "Stage 15 D=256 KS are not re-run. Not H1. Not a W class. No a98ea9 "
        "Stage 5. Stage 17 is not authorized."
    )
    raw = {
        "run_id": "RUN-ECDLP-420e73-S16",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 16,
        "authorized_by": AUTHORIZED_BY,
        "task_id": TASK_ID,
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "h3_ks_is_not_H1_support": True,
        "H3_factor2_miss_is_not_failed_infrastructure": True,
        "H3_miss_is_not_H1_closure": True,
        "ks_is_not_a_gate": True,
        "ks_distance_is_not_a_p_value": True,
        "stage11_eight_walks_not_the_measurement": True,
        "deterministic_x_mod_16_not_rerun": True,
        "c1_c2_c3_not_rerun": True,
        "c4_first_slice_not_rerun": True,
        "fishing_1000_not_rerun": True,
        "stage14_d20_ks_not_rerun": True,
        "stage15_d256_ks_not_rerun": True,
        "stage15_d256_hitting_times_not_nested": True,
        "t2_null3_collision_indices": list(NULL3_T2_COLLISION_INDICES),
        "t2_null3_nunique": len(set(T2["V_NULL3"])),
        "t2_null3_collision_is_not_failed_infrastructure": True,
        "stage17_authorized": False,
        "partition": "independent_uniform_0_15",
        "seed": SEED,
        "r": R_ADDING,
        "n_walks": N_WALKS,
        "addend_scalars": ADDENDS,
        "start_scalars_reused_from_stage10": STARTS_REUSED,
        "null3_k": NULL3_K,
        "extra_start_pins": extra_info["pins"],
        "extra_start_pins_match": extra_match,
        "T2": {"id": T2["id"], "p": T2["p"], "a": T2["a"], "b": T2["b"], "N": T2["N"],
               "D": T2["D"], "generator_P": list(T2["P"]), "V": T2["V"], "V_NULL3": T2["V_NULL3"],
               "design": t2d, "null3": t2n},
        "T1": {"id": T1["id"], "p": T1["p"], "a": T1["a"], "b": T1["b"], "N": T1["N"],
               "D": T1["D"], "generator_P": list(T1["P"]), "V": T1["V"], "V_NULL3": T1["V_NULL3"],
               "design": t1d, "null3": t1n},
        "arms_summary": [arm_summary(a) for a in arms],
        "first_j_idx0_all_match": fj0,
        "first_j_idx10_all_match": fj10,
        "design_V_prefix_match": v_prefix,
        "null3_k_prefix_match": null3_prefix,
        "v_pins_match": v_pins,
        "t2_null3_collision_match": t2_null3_collision,
        "stage15_d256_hitting_times_not_nested": True,
        "stage14_d20_ks_not_rerun": True,
        "stage15_d256_ks_not_rerun": True,
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": scientific_boundary,
        "wall_clock_seconds": time.perf_counter() - t0,
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source": SOURCE,
        "c_source": C_SOURCE,
        "walker": "C affine add with Python random.Random MT19937 state copy",
    }
    summary = {
        "run_id": raw["run_id"],
        "fixture_pass": fixture_pass,
        "extra_start_pins_match": extra_match,
        "first_j_idx0_all_match": fj0,
        "first_j_idx10_all_match": fj10,
        "design_V_prefix_match": v_prefix,
        "null3_k_prefix_match": null3_prefix,
        "v_pins_match": v_pins,
        "t2_null3_collision_match": t2_null3_collision,
        "stage15_d256_hitting_times_not_nested": True,
        "certificate": raw["certificate"],
        "arms_summary": raw["arms_summary"],
        "wall_clock_seconds": raw["wall_clock_seconds"],
        "not_an_H1_claim": True,
        "ks_is_not_a_gate": True,
    }
    stdout_text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    print(stdout_text, end="")
    cmd = "python3 experiments/EXP-ECDLP-420e73/implementation/stage16_h3_ks_1e4_D_Nsqrt_16777213.py"
    write_artifacts(raw, stdout_text, "".join(stderr_chunks), cmd)
    write_report(raw)
    return 0 if fixture_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
