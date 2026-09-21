#!/usr/bin/env python3
"""Standalone blind re-derivation of COMPARATOR_x_bucket q_maj on S1-a.

Implements affine Weierstrass addition and an exact (k, ell) pair count.
Does not import any producer module.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

# Frozen parameters from the review-plan quantity statement.
P = 47237
A = 31367
B = 41141
N_ORDER = 47057
S_X, S_Y = 2, 97
S_IMAGE = 2
IDENTITY_LABEL = 0
INSTANCE_ID = "S1-a"


def _inv(x: int, modulus: int) -> int:
    return pow(x, -1, modulus)


def on_curve(x: int, y: int) -> bool:
    return (y * y) % P == (pow(x, 3, P) + (A * x) % P + B) % P


def add_affine(pt_p, pt_q):
    """Affine Weierstrass addition. Identity is None."""
    if pt_p is None:
        return pt_q
    if pt_q is None:
        return pt_p
    x1, y1 = pt_p
    x2, y2 = pt_q
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None
        lam = ((3 * x1 * x1 + A) * _inv((2 * y1) % P, P)) % P
    else:
        lam = ((y2 - y1) * _inv((x2 - x1) % P, P)) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def bucket_label(x: int) -> int:
    return min((x * S_IMAGE) // P, S_IMAGE - 1)


def walk_labels():
    """Walk P_k = [k]S for k=0..n-1. Identity (k=0) gets IDENTITY_LABEL."""
    if not on_curve(S_X, S_Y):
        raise RuntimeError("generator S is off-curve")

    labels = np.empty(N_ORDER, dtype=np.int64)
    xs = np.full(N_ORDER, -1, dtype=np.int64)
    identity_indices = []
    off_curve = 0

    pt = None  # [0]S
    for k in range(N_ORDER):
        if pt is None:
            identity_indices.append(k)
            labels[k] = IDENTITY_LABEL
            xs[k] = -1
        else:
            x, y = pt
            if not on_curve(x, y):
                off_curve += 1
            labels[k] = bucket_label(x)
            xs[k] = x
        pt = add_affine(pt, (S_X, S_Y))

    walk_closed = pt is None
    first_identity_only_at_zero = identity_indices == [0]
    return {
        "labels": labels,
        "xs": xs,
        "walk_closed": walk_closed,
        "identity_indices": identity_indices,
        "first_identity_only_at_zero": first_identity_only_at_zero,
        "off_curve_affine": off_curve,
        "terminal_is_identity": walk_closed,
    }


def fiber_sizes(labels: np.ndarray) -> list[int]:
    return [int(np.sum(labels == a)) for a in range(S_IMAGE)]


def count_N_exact(labels: np.ndarray, batch: int = 256) -> np.ndarray:
    """Exact N[a,b,c] by batched integer pairwise sums.

    For each (a,b), for k in A_a: increment N[a,b, v((k+ell) mod n)] over ell in A_b.
    Batched to keep the temporary (batch x |A_b|) table well under memory.
    """
    n = int(labels.shape[0])
    cells = np.zeros((S_IMAGE, S_IMAGE, S_IMAGE), dtype=np.int64)
    members = [np.flatnonzero(labels == a).astype(np.int64) for a in range(S_IMAGE)]
    for a in range(S_IMAGE):
        ka = members[a]
        for b in range(S_IMAGE):
            kb = members[b]
            if ka.size == 0 or kb.size == 0:
                continue
            acc = np.zeros(S_IMAGE, dtype=np.int64)
            for start in range(0, ka.size, batch):
                chunk = ka[start : start + batch]
                sums = (chunk[:, None] + kb[None, :]) % n
                labs = labels[sums]
                for c in range(S_IMAGE):
                    acc[c] += int(np.count_nonzero(labs == c))
            cells[a, b, :] = acc
    return cells


def count_N_fft(labels: np.ndarray):
    """Circular-convolution cross-check via numpy.fft of exact length n.

    Recovers integer bins by rounding and records residuals. Allowed because
    n^2 < 2^53 so integer pair counts fit in the float64 mantissa.
    """
    n = int(labels.shape[0])
    indicators = [ (labels == a).astype(np.float64) for a in range(S_IMAGE) ]
    ffts = [np.fft.fft(ind) for ind in indicators]
    cells = np.zeros((S_IMAGE, S_IMAGE, S_IMAGE), dtype=np.int64)
    conv_residuals = []
    n_residuals = []
    for a in range(S_IMAGE):
        for b in range(S_IMAGE):
            conv = np.fft.ifft(ffts[a] * ffts[b]).real
            conv_int = np.rint(conv)
            conv_res = conv - conv_int
            conv_residuals.append(
                {
                    "a": a,
                    "b": b,
                    "max_abs_residual": float(np.max(np.abs(conv_res))),
                    "rms_residual": float(np.sqrt(np.mean(conv_res * conv_res))),
                }
            )
            conv_int = conv_int.astype(np.int64)
            for c in range(S_IMAGE):
                raw = float(np.dot(indicators[c], conv))
                rounded = int(round(raw))
                from_int_conv = int(np.dot(indicators[c].astype(np.int64), conv_int))
                n_residuals.append(
                    {
                        "a": a,
                        "b": b,
                        "c": c,
                        "float_dot": raw,
                        "rounded": rounded,
                        "from_int_conv": from_int_conv,
                        "round_residual": raw - rounded,
                    }
                )
                cells[a, b, c] = from_int_conv
    return cells, conv_residuals, n_residuals


def checksums(labels: np.ndarray, cells: np.ndarray, fibers: list[int]) -> dict:
    n = int(labels.shape[0])
    n2 = n * n
    cell_sum = int(cells.sum())
    row_sums = {}
    row_ok = True
    for a in range(S_IMAGE):
        for b in range(S_IMAGE):
            expected = fibers[a] * fibers[b]
            got = int(cells[a, b, :].sum())
            row_sums[f"{a},{b}"] = {"got": got, "expected": expected}
            if got != expected:
                row_ok = False
    return {
        "n": n,
        "n_squared": n2,
        "N_cells_sum": cell_sum,
        "N_cells_sum_equals_n2": cell_sum == n2,
        "fiber_sum": int(sum(fibers)),
        "fiber_sum_equals_n": int(sum(fibers)) == n,
        "each_ab_row_sums_to_fiber_product": row_ok,
        "ab_row_sums": row_sums,
    }


def main() -> int:
    out_dir = Path(__file__).resolve().parent
    raw_path = out_dir / "blind_raw.json"

    walk = walk_labels()
    labels = walk["labels"]
    fibers = fiber_sizes(labels)

    cells = count_N_exact(labels)
    fft_cells, conv_residuals, n_residuals = count_N_fft(labels)
    fft_agrees = bool(np.array_equal(cells, fft_cells))

    checks = checksums(labels, cells, fibers)
    max_c_per_ab = {}
    pair_count = 0
    for a in range(S_IMAGE):
        for b in range(S_IMAGE):
            row = [int(cells[a, b, c]) for c in range(S_IMAGE)]
            mx = max(row)
            argmax = int(np.argmax(cells[a, b, :]))
            max_c_per_ab[f"{a},{b}"] = {
                "N": row,
                "max_c": mx,
                "argmax_c": argmax,
            }
            pair_count += mx

    n2 = N_ORDER * N_ORDER
    g = math.gcd(pair_count, n2)
    num = pair_count // g
    den = n2 // g
    q_maj = f"{num}/{den}"

    payload = {
        "task_id": "TASK-20260907-f5f3ec",
        "batch_id": "BATCH-8357ae",
        "quantity": "q_maj of COMPARATOR_x_bucket on S1-a at s=2",
        "parameters": {
            "instance_id": INSTANCE_ID,
            "p": P,
            "A": A,
            "B": B,
            "n": N_ORDER,
            "S": [S_X, S_Y],
            "r": 1,
            "s": S_IMAGE,
            "statistic": "COMPARATOR_x_bucket",
            "identity_label": IDENTITY_LABEL,
        },
        "walk": {
            "walk_closed": walk["walk_closed"],
            "first_identity_only_at_zero": walk["first_identity_only_at_zero"],
            "identity_indices": walk["identity_indices"],
            "off_curve_affine": walk["off_curve_affine"],
            "generator_on_curve": True,
        },
        "fiber_sizes": fibers,
        "N_abc": [
            [
                [int(cells[a, b, c]) for c in range(S_IMAGE)]
                for b in range(S_IMAGE)
            ]
            for a in range(S_IMAGE)
        ],
        "max_c_per_ab": max_c_per_ab,
        "pair_count": pair_count,
        "q_maj": {
            "numerator": num,
            "denominator": den,
            "rational": q_maj,
            "pair_count": pair_count,
            "n_squared": n2,
            "gcd": g,
        },
        "checksums": checks,
        "fft_crosscheck": {
            "agrees_with_exact": fft_agrees,
            "conv_residuals": conv_residuals,
            "n_residuals": n_residuals,
        },
        "enumeration_complete": bool(
            walk["walk_closed"]
            and walk["first_identity_only_at_zero"]
            and walk["off_curve_affine"] == 0
            and checks["N_cells_sum_equals_n2"]
            and checks["fiber_sum_equals_n"]
            and checks["each_ab_row_sums_to_fiber_product"]
            and fft_agrees
        ),
    }

    raw_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "raw_output": str(raw_path),
        "q_maj": q_maj,
        "pair_count": pair_count,
        "fiber_sizes": fibers,
        "walk_closed": walk["walk_closed"],
        "N_sum": checks["N_cells_sum"],
        "enumeration_complete": payload["enumeration_complete"],
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
