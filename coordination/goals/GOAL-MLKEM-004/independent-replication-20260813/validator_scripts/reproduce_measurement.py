#!/usr/bin/env python3
"""Rebuild the vector population in memory and compare it to archived raw data.

Run with the Coordinator-rebuilt /tmp/sagevenv. This validator script writes
no measurement artifacts: it independently reconstructs the seeded basis,
LLL and g6k population, verifies membership on the in-memory (x,y) vectors,
and compares all norms and phase arrays to raw_scores.json.
"""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
from fpylll import FPLLL, IntegerMatrix, LLL
from g6k import Siever, SieverParams


def center_mod(v, q):
    r = np.mod(v, q)
    return np.where(r > q // 2, r - q, r).astype(np.int64)


def to_integer_matrix(matrix):
    rows, cols = matrix.shape
    out = IntegerMatrix(rows, cols)
    for i in range(rows):
        for j in range(cols):
            out[i, j] = int(matrix[i, j])
    return out


def from_integer_matrix(matrix):
    return np.asarray(
        [
            [matrix[i, j] for j in range(matrix.ncols)]
            for i in range(matrix.nrows)
        ],
        dtype=np.int64,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_scores", type=Path)
    args = ap.parse_args()
    with args.raw_scores.open() as f:
        raw = json.load(f)

    started = time.time()
    p = raw["parameters"]
    m, n, d, q = int(p["m"]), int(p["n"]), int(p["d"]), int(p["q"])
    expected_n = int(p["n_sieve_vectors"])
    a = np.asarray(raw["A"], dtype=np.int64)

    basis = np.zeros((d, d), dtype=np.int64)
    basis[:m, :m] = np.eye(m, dtype=np.int64)
    basis[:m, m:] = a
    basis[m:, m:] = q * np.eye(n, dtype=np.int64)

    FPLLL.set_random_seed(int(p["fpylll_seed"]))
    reduced = LLL.reduction(to_integer_matrix(basis))
    siever = Siever(
        reduced,
        SieverParams(threads=1),
        seed=int(p["seeds"]["sieve"]),
    )
    siever.initialize_local(0, 0, d)
    sieve_started = time.time()
    siever.bgj1_sieve()
    sieve_seconds = time.time() - sieve_started

    coeffs = np.asarray([tuple(v) for v in siever.itervalues()], dtype=np.int64)
    used_basis = from_integer_matrix(siever.M.B)
    vectors = coeffs @ used_basis
    x = vectors[:, :m]
    y = vectors[:, m:]

    residue = (x @ a - y) % q
    membership_violating_entries = int(np.count_nonzero(residue))
    zero_vectors = int(np.count_nonzero(np.all(vectors == 0, axis=1)))

    archived_norms = {
        key: np.asarray(raw["per_vector"][key], dtype=np.int64)
        for key in ("norm2_v", "norm2_x", "norm2_y")
    }
    reconstructed_norms = {
        "norm2_v": np.sum(vectors * vectors, axis=1),
        "norm2_x": np.sum(x * x, axis=1),
        "norm2_y": np.sum(y * y, axis=1),
    }
    norm_mismatches = {
        key: int(np.count_nonzero(reconstructed_norms[key] != archived_norms[key]))
        if len(reconstructed_norms[key]) == len(archived_norms[key])
        else None
        for key in archived_norms
    }

    candidates = np.asarray(
        [c["vector"] for c in raw["candidates"]], dtype=np.int64
    )
    phase_arrays_checked = 0
    phase_value_mismatches = 0
    target_phase_mismatches = {}
    for target in raw["targets"]:
        b = np.asarray(target["b"], dtype=np.int64)
        items = target["per_candidate"]
        candidate_indices = [int(item["candidate_index"]) for item in items]
        subset = candidates[candidate_indices]
        reconstructed = center_mod(
            (x @ b)[:, None] - y @ subset.T,
            q,
        ).T
        archived = np.asarray([item["phases_t"] for item in items], dtype=np.int64)
        mismatches = (
            int(np.count_nonzero(reconstructed != archived))
            if reconstructed.shape == archived.shape
            else None
        )
        phase_arrays_checked += len(items)
        if mismatches is not None:
            phase_value_mismatches += mismatches
        target_phase_mismatches[target["name"]] = {
            "shape_reconstructed": list(reconstructed.shape),
            "shape_archived": list(archived.shape),
            "mismatches": mismatches,
        }

    main = next(t for t in raw["targets"] if t["name"] == "MAIN_lwe_sigma2")
    main_error = np.asarray(main["error_vector"], dtype=np.int64)
    reconstructed_x_dot_e = center_mod(x @ main_error, q)
    archived_x_dot_e = np.asarray(
        raw["per_vector"]["x_dot_e_main"], dtype=np.int64
    )
    x_dot_e_mismatches = (
        int(np.count_nonzero(reconstructed_x_dot_e != archived_x_dot_e))
        if reconstructed_x_dot_e.shape == archived_x_dot_e.shape
        else None
    )

    result = {
        "input": str(args.raw_scores),
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "fpylll": importlib.metadata.version("fpylll"),
            "g6k": importlib.metadata.version("g6k"),
            "passagemath_standard": importlib.metadata.version(
                "passagemath-standard"
            ),
        },
        "run": {
            "algorithm": "bgj1_sieve",
            "threads": 1,
            "fpylll_seed": int(p["fpylll_seed"]),
            "g6k_seed": int(p["seeds"]["sieve"]),
            "sieve_seconds_current_container": sieve_seconds,
            "total_seconds_current_container": time.time() - started,
        },
        "population": {
            "expected_N": expected_n,
            "reconstructed_N": int(len(vectors)),
            "vector_sha256_little_endian_int64": hashlib.sha256(
                vectors.astype("<i8", copy=False).tobytes()
            ).hexdigest(),
            "membership_violating_entries": membership_violating_entries,
            "zero_vectors": zero_vectors,
            "norm_mismatches": norm_mismatches,
        },
        "phase_comparison": {
            "phase_arrays_checked": phase_arrays_checked,
            "phase_value_mismatches": phase_value_mismatches,
            "per_target": target_phase_mismatches,
            "x_dot_e_main_mismatches": x_dot_e_mismatches,
        },
        "scientific_content_match": bool(
            len(vectors) == expected_n
            and membership_violating_entries == 0
            and zero_vectors == 0
            and all(v == 0 for v in norm_mismatches.values())
            and phase_value_mismatches == 0
            and x_dot_e_mismatches == 0
        ),
        "provenance_note": (
            "The /tmp/sagevenv rebuild was performed by the Coordinator "
            "session from KN-TECH-797223. This validator only verified that "
            "instrument functional and executed this independent in-memory "
            "reconstruction against the committed raw archive."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
