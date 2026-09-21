#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 1 anomalous T2 / NULL-1 instrument. Certificate kind none."""
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

P_FIELD = 523
D = 20
HEADER_BITS = 64
SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage1_anomalous_affine.py"

T2 = {
    "id": "S1-T2-P523",
    "p": P_FIELD,
    "a": 2,
    "b": 6,
    "N": 523,
    "P": (0, 23),
    "V": [0, 436, 365, 181, 65, 502, 497, 417, 473, 485, 5, 500, 158, 362, 185, 419, 237, 340, 29, 42],
}
NULL1 = {
    "id": "S1-NULL1-P523",
    "p": P_FIELD,
    "a": 3,
    "b": 3,
    "N": 503,
    "P": (1, 141),
    "V": [1, 74, 512, 87, 98, 95, 425, 377, 392, 240, 85, 171, 219, 346, 361, 278, 197, 374, 262, 239],
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
    null1 = evaluate_cell(NULL1)
    t2_formal = t2["linearized_formal_log"]["recovers_exact_affine"] is True
    null1_id = null1["identity"]["recovers_exact_affine"] is False
    fixture_pass = t2_formal and null1_id
    raw = {
        "run_id": "RUN-ECDLP-420e73-S1",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 1,
        "authorized_by": "DEC-20260908-c2303f",
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "T2": t2,
        "NULL1": null1,
        "T2_formal_log_recovers_exact_affine": t2_formal,
        "T2_formal_log_a_hat": t2["linearized_formal_log"]["a_hat"],
        "T2_formal_log_b_hat": t2["linearized_formal_log"]["b_hat"],
        "NULL1_identity_recovers_exact_affine": not null1_id,
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": (
            "Toy anomalous T2 plus same-prime NULL-1 C3 instrument only. "
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
