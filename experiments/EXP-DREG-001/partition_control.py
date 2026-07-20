#!/usr/bin/env sage -python
"""Deterministic positive control for the block-carrier rank invariant."""

from __future__ import annotations

import hashlib
import json
import random
import sys
from array import array
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sage.all import GF, matrix

from h012c_block_m4ri import process_subchunk


F2 = GF(2)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_matrix(
    nrows: int, ncols: int, density: float, seed: int, dependent_rows: bool
):
    rng = random.Random(seed)
    value = matrix(F2, nrows, ncols)
    for col in range(ncols):
        for row in range(nrows):
            if rng.random() < density:
                value[row, col] = 1
    # Add deliberate duplicates and zero columns when the shape permits them.
    if ncols >= 8:
        value.set_column(ncols - 1, value.column(0))
        value.set_column(ncols - 2, value.column(1))
        value.set_column(ncols - 3, [0] * nrows)
    if dependent_rows and nrows >= 3:
        value.set_row(nrows - 1, value.row(0))
        value.set_row(nrows - 2, [0] * ncols)
    return value


def adjacency(value):
    nrows, ncols = value.dimensions()
    return [array("I", value.column(col).nonzero_positions()) for col in range(ncols)]


def split_carrier(pivots, carrier):
    if len(pivots) < 2:
        return [(pivots, carrier)]
    middle = len(pivots) // 2
    return [
        (pivots[:middle], carrier.matrix_from_columns(list(range(middle)))),
        (
            pivots[middle:],
            carrier.matrix_from_columns(list(range(middle, len(pivots)))),
        ),
    ]


def block_rank(value, width: int, split: bool) -> tuple[int, list[int]]:
    nrows, ncols = value.dimensions()
    col_rows = adjacency(value)
    carries = []
    rank = 0
    increments = []
    for start in range(0, ncols, width):
        stop = min(ncols, start + width)
        added, pivots, carrier, _ = process_subchunk(
            col_rows, start, stop, nrows, carries, {}
        )
        increments.append(added)
        rank += added
        if added:
            carries.extend(split_carrier(pivots, carrier) if split else [(pivots, carrier)])
    return rank, increments


def main() -> None:
    cases = []
    for case_id, (nrows, ncols, density, seed, dependent_rows) in enumerate(
        [
            (17, 41, 0.08, 11, False),
            (37, 89, 0.25, 12, True),
            (64, 137, 0.50, 13, False),
            (23, 47, 0.00, 14, False),
        ]
    ):
        value = make_matrix(nrows, ncols, density, seed, dependent_rows)
        expected = int(value.rank())
        partitions = []
        for width in (7, 13, 29):
            for split in (False, True):
                observed, increments = block_rank(value, width, split)
                if observed != expected:
                    raise AssertionError(
                        f"case {case_id}, width {width}, split {split}: "
                        f"{observed} != {expected}"
                    )
                partitions.append(
                    {
                        "width": width,
                        "split_carriers": split,
                        "rank": observed,
                        "increments": increments,
                    }
                )
        cases.append(
            {
                "case": case_id,
                "nrows": nrows,
                "ncols": ncols,
                "density": density,
                "seed": seed,
                "dependent_rows": dependent_rows,
                "monolithic_rank": expected,
                "partitions": partitions,
            }
        )

    instrument = ROOT / "src" / "h012c_block_m4ri.py"
    print(
        json.dumps(
            {
                "status": "completed_valid",
                "control_version": 2,
                "control": "deterministic synthetic partition equivalence",
                "instrument_sha256": file_hash(instrument),
                "cases": cases,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
