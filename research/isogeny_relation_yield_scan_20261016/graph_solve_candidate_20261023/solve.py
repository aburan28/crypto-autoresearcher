"""Candidate complete modular relation solve for one prepared graph arm.

Run with ``sage -python``. The planted Q scalar is never an input. A rank
shortfall is a censored outcome, not a zero-cost solve or a mathematical
obstruction. Scientific use requires a frozen Coordinator-approved contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

from sage.all import EllipticCurve, GF, Matrix, vector
from sage.version import version as sage_version

ROOT = Path(__file__).resolve().parents[3]
LEGACY = ROOT / "research/conductor_relation_yield_20261014"
sys.path.insert(0, str(LEGACY))
from verify_collector import (canonical_row, column_layout, parse_input,
                              row_for, verify)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_useful_rows(input_path: Path, collector_path: Path, generator: tuple[int, int],
                      q: tuple[int, int]):
    curve, base, targets = parse_input(input_path)
    layout = column_layout(base, generator, q, curve)
    width = len(layout[4]) + (layout[5] is not None)
    rows: dict[tuple[int, ...], int] = {}
    current = None
    for line in collector_path.read_text().splitlines()[1:]:
        fields = line.split("\t")
        if fields[0] == "target":
            current = int(fields[1])
            continue
        if fields[0] != "triple" or current is None:
            raise ValueError("collector order differs")
        index, i, j, k = map(int, fields[1:])
        if index != current:
            raise ValueError("collector target index differs")
        if i == j or j == k or len({i // 2, j // 2, k // 2}) != 3:
            continue
        alpha, beta, _ = targets[index]
        coefficients, rhs = row_for((i, j, k), alpha, beta, base, curve, layout)
        if not any(coefficients):
            continue
        canonical, value = canonical_row(coefficients, rhs, curve.r)
        previous = rows.setdefault(canonical, value)
        if previous != value:
            raise ValueError("same coefficient row has inconsistent right side")
    return curve, base, targets, layout, width, rows


def solve(input_path: Path, collector_path: Path, count_path: Path,
          generator: tuple[int, int], q: tuple[int, int]) -> dict:
    started = time.monotonic()
    verification = verify(input_path, collector_path, generator, q,
                          {512, 2048, 8192, 32768}, count_path)
    replay_seconds = time.monotonic() - started
    started = time.monotonic()
    curve, base, targets, layout, width, rows = parse_useful_rows(
        input_path, collector_path, generator, q)
    if len(rows) != verification["unique_canonical_coefficient_rows"] or width != verification["unknown_columns"]:
        raise ValueError("matrix rows or unknown columns differ from independent rank replay")
    ordered_rows = sorted(rows.items())
    digest = hashlib.sha256()
    for coefficients, rhs in ordered_rows:
        digest.update((json.dumps([coefficients, rhs], separators=(",", ":")) + "\n").encode())
    row_seconds = time.monotonic() - started
    started = time.monotonic()
    F = GF(curve.r)
    matrix = Matrix(F, [list(coefficients) for coefficients, _ in ordered_rows],
                    ncols=width, sparse=True)
    rhs_vector = vector(F, [rhs for _, rhs in ordered_rows])
    rank = int(matrix.rank())
    if rank != verification["rank_increments"]:
        raise ValueError("Sage matrix rank differs from independent replay")
    result = {
        "schema": "ectd.graph-complete-solve-candidate.v1",
        "status": "censored_insufficient_rank" if rank < width else "solving",
        "input_sha256": sha(input_path), "collector_sha256": sha(collector_path),
        "count_sha256": sha(count_path), "p": curve.p, "a": curve.a, "b": curve.b,
        "r": curve.r, "generator": list(generator), "Q": list(q),
        "targets": len(targets), "unknown_columns": width,
        "unique_coefficient_rows": len(rows), "rank": rank,
        "matrix_rows_sha256": digest.hexdigest(),
        "sage_version": sage_version,
        "timings_seconds": {"input_and_relation_replay": replay_seconds,
                            "matrix_row_build": row_seconds},
        "scalar": None, "base_logs": None, "solution": None,
    }
    if rank < width:
        result["timings_seconds"]["linear_algebra"] = time.monotonic() - started
        result["timings_seconds"]["scalar_verification"] = 0.0
        return result
    solution = [int(value) for value in matrix.solve_right(rhs_vector)]
    if any(sum(c * x for c, x in zip(coefficients, solution)) % curve.r != rhs
           for coefficients, rhs in ordered_rows):
        raise ValueError("modular matrix solution fails an equation")
    result["timings_seconds"]["linear_algebra"] = time.monotonic() - started
    started = time.monotonic()
    g_orbit, g_log, q_orbit, q_sign, columns, q_column = layout
    base_logs = [g_log if orbit == g_orbit else solution[columns[orbit]]
                 for orbit in range(len(base) // 2)]
    if q_orbit is None:
        scalar = solution[q_column]
    else:
        scalar = q_sign * base_logs[q_orbit] % curve.r
    E = EllipticCurve(GF(curve.p), [curve.a, curve.b])
    sage_g = E(generator)
    if scalar * sage_g != E(q):
        raise ValueError("solved scalar fails independent Sage point equation")
    for orbit, value in enumerate(base_logs):
        if value * sage_g != E(base[2 * orbit]):
            raise ValueError(f"factor-base log fails independent point equation at orbit {orbit}")
    result.update({"status": "verified_scalar", "scalar": scalar,
                   "base_logs": base_logs, "solution": solution})
    result["timings_seconds"]["scalar_verification"] = time.monotonic() - started
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("input", "collector", "count", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("gx", "gy", "qx", "qy"):
        parser.add_argument("--" + name, type=int, required=True)
    args = parser.parse_args()
    result = solve(args.input, args.collector, args.count,
                   (args.gx, args.gy), (args.qx, args.qy))
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "rank": result["rank"],
                      "unknown_columns": result["unknown_columns"],
                      "output_sha256": sha(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
