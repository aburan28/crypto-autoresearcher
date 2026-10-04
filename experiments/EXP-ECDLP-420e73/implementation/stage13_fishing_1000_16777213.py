#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 13 fishing-1000 at p=16777213. Certificate kind none.

1000 independent random designs of size D=20 per frozen Stage 7 cell.
S_C is 8 * len(zlib.compress(payload, 9)) on increasing-v k_inc.
k-order 1,2,...,D is forbidden and resampled.
C4 is a non-admissible indicator. Fishing min-gamma never supports H1.
C1, C2, C3, Stage 10/11 walks, and the Stage 12 three-arm C4 are not re-run.
Stage 12 gammas are read from RUN-ECDLP-420e73-S12, not recomputed.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import random
import resource
import statistics
import sys
import time
import zlib
from pathlib import Path

SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage13_fishing_1000_16777213.py"
REPO_ROOT = Path(__file__).resolve().parents[3]
STAGE12_RAW = REPO_ROOT / "experiments/EXP-ECDLP-420e73/runs/RUN-ECDLP-420e73-S12/raw-result.json"

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


def encode_payload(seq: list[int]) -> bytes:
    return b"".join(int(k).to_bytes(4, "big") for k in seq)


def c4_of_k_inc(k_inc: list[int], n: int) -> dict:
    payload = encode_payload(k_inc)
    if len(payload) != 80:
        raise RuntimeError(f"payload length {len(payload)} != 80")
    compressed = zlib.compress(payload, ZLIB_LEVEL)
    s_bits = 8 * len(compressed)
    denom_power = D * math.log2(n)
    denom_linear = D * math.log2(n / D)
    return {
        "payload_len_bytes": len(payload),
        "zlib_level": ZLIB_LEVEL,
        "zlib_len_bytes": len(compressed),
        "S_C_bits": s_bits,
        "gamma_power": 1.0 - math.log(s_bits) / math.log(denom_power),
        "gamma_linear": 1.0 - s_bits / denom_linear,
    }


def one_design(cell: dict, design_index: int) -> dict:
    p, a, n, P = cell["p"], cell["a"], cell["N"], cell["P"]
    for retry in range(0, RETRY_CAP + 1):
        ks = sample_k(cell["id"], n, design_index, retry)
        points = []
        xs = []
        invalid = False
        for k in ks:
            R = mul(p, a, k, P)
            if R is None:
                invalid = True
                break
            xs.append(R[0])
            points.append(R)
        if invalid:
            continue
        if len(set(xs)) != D:
            continue
        k_inc = [k for _, k in sorted(zip(xs, ks), key=lambda t: t[0])]
        if k_inc == FORBIDDEN_K_INC:
            continue
        for k, R in zip(ks, points):
            R2 = mul(p, a, k, P)
            if R2 != R:
                raise RuntimeError(f"{cell['id']} design {design_index}: landing reconstruction mismatch")
        c4 = c4_of_k_inc(k_inc, n)
        return {
            "design_index": design_index,
            "retry": retry,
            "k": ks,
            "V": xs,
            "k_inc": k_inc,
            "C4": c4,
        }
    raise RuntimeError(
        f"{cell['id']} design {design_index}: retry exhaustion at cap {RETRY_CAP}"
    )


def cell_fishing(cell: dict) -> dict:
    designs = []
    n_retries = 0
    for i in range(N_DESIGNS):
        d = one_design(cell, i)
        n_retries += d["retry"]
        designs.append(d)
    pin = DESIGN0_PINS[cell["id"]]
    d0 = designs[0]
    design0_k_match = d0["k"] == pin["k"]
    design0_k_inc_match = d0["k_inc"] == pin["k_inc"]
    design0_retry_match = d0["retry"] == pin["retry"]
    if not (design0_k_match and design0_k_inc_match and design0_retry_match):
        raise RuntimeError(
            f"{cell['id']} design0 pin mismatch k={d0['k']} k_inc={d0['k_inc']} retry={d0['retry']}"
        )
    payload_all_80 = all(d["C4"]["payload_len_bytes"] == 80 for d in designs)
    gammas_p = [d["C4"]["gamma_power"] for d in designs]
    gammas_l = [d["C4"]["gamma_linear"] for d in designs]
    min_p = min(gammas_p)
    min_l = min(gammas_l)
    min_p_idx = gammas_p.index(min_p)
    min_l_idx = gammas_l.index(min_l)
    min_p_design = designs[min_p_idx]
    min_l_design = designs[min_l_idx]
    return {
        "id": cell["id"],
        "p": cell["p"],
        "a": cell["a"],
        "b": cell["b"],
        "N": cell["N"],
        "generator_P": list(cell["P"]),
        "n_designs": N_DESIGNS,
        "n_retries": n_retries,
        "payload_len_bytes_all_80": payload_all_80,
        "design0": {
            "k": d0["k"],
            "k_inc": d0["k_inc"],
            "retry": d0["retry"],
            "k_pin_match": design0_k_match,
            "k_inc_pin_match": design0_k_inc_match,
            "retry_pin_match": design0_retry_match,
            "C4": d0["C4"],
        },
        "min_gamma_power": min_p,
        "min_gamma_power_design_index": min_p_idx,
        "min_gamma_linear": min_l,
        "min_gamma_linear_design_index": min_l_idx,
        "minimizing_power_C4": min_p_design["C4"],
        "minimizing_linear_C4": min_l_design["C4"],
        "mean_gamma_power": statistics.fmean(gammas_p),
        "median_gamma_power": statistics.median(gammas_p),
        "mean_gamma_linear": statistics.fmean(gammas_l),
        "median_gamma_linear": statistics.median(gammas_l),
    }


def load_stage12_comparison() -> dict:
    raw = json.loads(STAGE12_RAW.read_text())
    if raw.get("run_id") != "RUN-ECDLP-420e73-S12":
        raise RuntimeError("Stage 12 raw-result run_id mismatch")
    return {
        "source_run": "RUN-ECDLP-420e73-S12",
        "recomputed": False,
        "T2_gamma_power": raw["T2"]["C4"]["gamma_power"],
        "T2_gamma_linear": raw["T2"]["C4"]["gamma_linear"],
        "T1_gamma_power": raw["T1"]["C4"]["gamma_power"],
        "T1_gamma_linear": raw["T1"]["C4"]["gamma_linear"],
        "note": "Comparison only. Stage 12 three-arm C4 was not re-run.",
    }


def main() -> int:
    t0 = time.perf_counter()
    stage12 = load_stage12_comparison()
    t2 = cell_fishing(T2)
    t1 = cell_fishing(T1)
    design0_pins_all_match = (
        t2["design0"]["k_pin_match"]
        and t2["design0"]["k_inc_pin_match"]
        and t2["design0"]["retry_pin_match"]
        and t1["design0"]["k_pin_match"]
        and t1["design0"]["k_inc_pin_match"]
        and t1["design0"]["retry_pin_match"]
    )
    payload_len_bytes_all_80 = t2["payload_len_bytes_all_80"] and t1["payload_len_bytes_all_80"]
    n_retries_total = t2["n_retries"] + t1["n_retries"]
    fixture_pass = (
        design0_pins_all_match
        and payload_len_bytes_all_80
        and t2["n_designs"] == N_DESIGNS
        and t1["n_designs"] == N_DESIGNS
    )
    raw = {
        "run_id": "RUN-ECDLP-420e73-S13",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 13,
        "authorized_by": "DEC-20260908-42579b",
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "C4_is_non_admissible_indicator": True,
        "fishing_1000_is_not_H1_support": True,
        "C4_floor_is_not_failed_infrastructure": True,
        "fishing_floor_is_not_failed_infrastructure": True,
        "C4_reading_is_not_H1_closure": True,
        "fishing_reading_is_not_H1_closure": True,
        "ks_1e4_walks_not_this_slice": True,
        "c1_c2_c3_not_rerun": True,
        "h3_walks_not_rerun": True,
        "stage12_three_arm_c4_not_rerun": True,
        "k_order_forbidden": True,
        "seed": SEED,
        "n_designs": N_DESIGNS,
        "D": D,
        "zlib_level": ZLIB_LEVEL,
        "retry_cap": RETRY_CAP,
        "T2": t2,
        "T1": t1,
        "stage12_comparison_not_rerun": stage12,
        "design0_pins_all_match": design0_pins_all_match,
        "payload_len_bytes_all_80": payload_len_bytes_all_80,
        "n_retries_total": n_retries_total,
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": (
            "Toy fishing-1000 C4 on frozen Stage 7 cells at p=16777213. "
            "1000 independent random designs of size D=20 per cell. "
            "Increasing-v k_inc, 80-byte big-endian payload, zlib.compress "
            "level 9. C4 is a non-admissible indicator. Fishing min-gamma "
            "never supports H1. A fishing floor is a C4 observation, not "
            "failed_infrastructure. A fishing reading is not H1 closure. "
            "10^4-walk KS is not this slice. C1, C2, C3, the Stage 10/11 "
            "walks, and the Stage 12 three-arm C4 are not re-run. Not H1. "
            "Not a W class. No a98ea9 Stage 5. Gammas are observations."
        ),
        "wall_clock_seconds": time.perf_counter() - t0,
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source": SOURCE,
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if fixture_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
