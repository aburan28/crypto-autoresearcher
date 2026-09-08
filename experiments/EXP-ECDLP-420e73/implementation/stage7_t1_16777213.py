#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 7 T2 / T1 C3 instrument at p=16777213. Certificate kind none."""
from __future__ import annotations

import json
import math
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "EXP-ECDLP-bbb42f"))
from driver.sssa import formal_log_of_pP  # noqa: E402

P_FIELD = 16777213
D = 20
HEADER_BITS = 64
SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage7_t1_16777213.py"

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


def multiples(cell: dict) -> list[tuple[int, tuple[int, int]]]:
    p, a = cell["p"], cell["a"]
    R = None
    rows = []
    for k in range(1, D + 1):
        R = add(p, a, R, cell["P"])
        if R is None:
            raise RuntimeError(f"{cell['id']}: [k]P hit O at k={k}")
        if R[0] != cell["V"][k - 1]:
            raise RuntimeError(f"{cell['id']}: V mismatch at k={k}")
        rows.append((k, R))
    return rows


def recover_affine(xs: list[int], ks: list[int], n: int) -> tuple[int | None, int | None, bool]:
    if len(xs) < 2:
        return None, None, False
    x0, x1 = xs[0], xs[1]
    k0, k1 = ks[0], ks[1]
    dx = (x1 - x0) % n
    if dx == 0:
        return None, None, False
    a = ((k1 - k0) * pow(dx, -1, n)) % n
    b = (k0 - a * x0) % n
    exact = all((a * x + b) % n == k for x, k in zip(xs, ks))
    return a, b, exact


def s_c_bits(n: int) -> int:
    return 2 * math.ceil(math.log2(n)) + HEADER_BITS


def gammas(s_bits: int, n: int) -> dict:
    denom_power = D * math.log2(n)
    denom_linear = D * math.log2(n / D)
    return {
        "S_C_bits": s_bits,
        "gamma_power": 1.0 - math.log(s_bits) / math.log(denom_power),
        "gamma_linear": 1.0 - s_bits / denom_linear,
    }


def identity_arm(cell: dict, rows: list[tuple[int, tuple[int, int]]]) -> dict:
    vs = [R[0] for _, R in rows]
    ks = [k for k, _ in rows]
    a_hat, b_hat, exact = recover_affine(vs, ks, cell["N"])
    return {
        "lambda": "identity",
        "applicable_rows": D,
        "inapplicable": False,
        "recovers_exact_affine": exact,
        "a_hat": a_hat,
        "b_hat": b_hat,
        **gammas(s_c_bits(cell["N"]), cell["N"]),
    }


def formal_log_arm(cell: dict, rows: list[tuple[int, tuple[int, int]]]) -> dict:
    ss: list[int] = []
    ks: list[int] = []
    applicable = 0
    notes = []
    for k, (x, y) in rows:
        try:
            _t, s = formal_log_of_pP(x, y, cell["a"], cell["b"], cell["p"])
            ss.append(s)
            ks.append(k)
            applicable += 1
        except (RuntimeError, ValueError) as exc:
            notes.append({"k": k, "reason": str(exc)})
    inapplicable = applicable != D
    if inapplicable:
        a_hat, b_hat, exact = None, None, False
    else:
        a_hat, b_hat, exact = recover_affine(ss, ks, cell["N"])
    return {
        "lambda": "linearized_formal_log",
        "applicable_rows": applicable,
        "inapplicable": inapplicable,
        "inapplicable_notes": notes,
        "lambda_values": ss if not inapplicable else None,
        "recovers_exact_affine": exact,
        "a_hat": a_hat,
        "b_hat": b_hat,
        **gammas(s_c_bits(cell["N"]), cell["N"]),
    }


def evaluate_cell(cell: dict) -> dict:
    rows = multiples(cell)
    return {
        "id": cell["id"],
        "p": cell["p"],
        "a": cell["a"],
        "b": cell["b"],
        "N": cell["N"],
        "generator_P": list(cell["P"]),
        "V": cell["V"],
        "identity": identity_arm(cell, rows),
        "linearized_formal_log": formal_log_arm(cell, rows),
    }


def main() -> int:
    t0 = time.perf_counter()
    t2 = evaluate_cell(T2)
    t1 = evaluate_cell(T1)
    t2_formal = t2["linearized_formal_log"]["recovers_exact_affine"] is True
    t1_id_exact = t1["identity"]["recovers_exact_affine"] is True
    # T1 identity exact affine is an observation, not a hard gate.
    fixture_pass = t2_formal
    raw = {
        "run_id": "RUN-ECDLP-420e73-S7",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 7,
        "authorized_by": "DEC-20260908-4ea074",
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "T2": t2,
        "T1": t1,
        "T2_formal_log_recovers_exact_affine": t2_formal,
        "T2_formal_log_a_hat": t2["linearized_formal_log"]["a_hat"],
        "T2_formal_log_b_hat": t2["linearized_formal_log"]["b_hat"],
        "T1_identity_recovers_exact_affine": t1_id_exact,
        "T1_identity_is_not_a_hard_gate": True,
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": (
            "Toy T2 at p=16777213 plus last named ordinary T1 C3 instrument only. "
            "T1 exact affine is an observation, not a hard gate. "
            "Not H1. Not a W class. No a98ea9 Stage 5. Gammas are observations."
        ),
        "wall_clock_seconds": time.perf_counter() - t0,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source": SOURCE,
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if fixture_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
