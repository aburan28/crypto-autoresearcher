#!/usr/bin/env python3
"""Read-only Cairn replay of the EXP-ECDLP-5cad48 Stage 1 CS audit.

The original producer writes a run directory and timing fields. This adapter
checks the same frozen cells using decimal values parsed from the committed
input, and emits only the exact boolean and integer fields the objective pins.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INPUT = Path("experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S1/raw-result.json")
CELLS = {"S1-P523": (5, 8, 12), "S1-P1033": (6, 10, 16)}
ARMS = ("floor(Mx/p)", "x mod M", "sha", "shuffle", "P2")


def replay(repo: Path, expected_sha256: str) -> dict[str, bool | int]:
    raw_bytes = (repo / INPUT).read_bytes()
    actual = hashlib.sha256(raw_bytes).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"input hash {actual} differs from pinned {expected_sha256}")
    raw = json.loads(raw_bytes, parse_float=Decimal)
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S1":
        raise ValueError("unexpected input run_id")
    cells = {cell["id"]: cell for cell in raw["cells"]}
    all_holds = True
    rows = 0
    for cell_id, sizes in CELLS.items():
        measures = {int(item["M"]): item for item in cells[cell_id]["Ms"]}
        for size in sizes:
            arms = measures[size]["arms"]
            for arm in ARMS:
                item = arms[arm]
                g = Decimal(str(item["G_exact"]))
                delta = Decimal(str(item["M_delta_exact"]))
                cs = Decimal(str(item["cs_bound_exact"]))
                if delta <= 0:
                    raise ValueError(f"{cell_id} M={size} {arm}: nonpositive M_delta_exact")
                all_holds = all_holds and g <= cs * delta
                rows += 1
    return {
        "all_cells_aligned_holds": all_holds,
        "cs_bound_official_supported": False,
        "n_exact_rows": rows,
        "not_a_W_decay_claim": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--wrapper-sha256", required=True)
    args = parser.parse_args(argv)
    own = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if own != args.wrapper_sha256:
        parser.error(f"wrapper hash {own} differs from pinned {args.wrapper_sha256}")
    try:
        result = replay(REPO, args.input_sha256)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
