#!/usr/bin/env python3
"""Check EXP-OAKLEY-7f73ef.

Recomputes the subfield hit count and checks the planted point with
schoolbook arithmetic. A count outside the 3-sd band is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

DEGREE = 25
MASK = (1 << DEGREE) - 1
REDUCTION = (1 << 3) | 1
B_COEFFICIENT = 2


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("yield_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def schoolbook_multiply(left: int, right: int) -> int:
    product = 0
    while right:
        if right & 1:
            product ^= left
        right >>= 1
        left <<= 1
        if left & (1 << DEGREE):
            left = (left & MASK) ^ REDUCTION
    return product


def curve_holds(x_coord: int, y_coord: int) -> bool:
    left = schoolbook_multiply(y_coord, y_coord) ^ schoolbook_multiply(x_coord, y_coord)
    cube = schoolbook_multiply(schoolbook_multiply(x_coord, x_coord), x_coord)
    return left == (cube ^ B_COEFFICIENT)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py RUN_DIR", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    manifest_path = run_dir / "manifest.yaml"
    if not raw_path.is_file() or not manifest_path.is_file():
        print("missing outputs", file=sys.stderr)
        return 1
    result = json.loads(raw_path.read_text(encoding="utf-8"))
    if result.get("experiment_id") != "EXP-OAKLEY-7f73ef" or result.get("population") != 32:
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("predicted_probability") != "1/120" or result.get("attack_claimed") is not False:
        print("prediction changed", file=sys.stderr)
        return 1
    module = load_run(Path(__file__).with_name("run.py"))
    if module.census() != result:
        print("recompute mismatch", file=sys.stderr)
        return 1
    planted = result.get("planted") or {}
    if not planted.get("planted_ok"):
        print("planted identities failed", file=sys.stderr)
        return 1
    point = planted.get("planted_point") or {}
    if not curve_holds(point.get("x"), point.get("y")) or not curve_holds(
        point.get("double_x"), point.get("double_y")
    ):
        print("planted point is off the curve", file=sys.stderr)
        return 1
    count = result.get("hit_count")
    if not isinstance(count, int) or count < 0 or count > 32:
        print("hit count out of range", file=sys.stderr)
        return 1
    text = manifest_path.read_text(encoding="utf-8")
    required = (
        "attack_claimed: false",
        "experiment_id: EXP-OAKLEY-7f73ef",
        "planted_ok: true",
        f"hit_count: {count}",
        "population: 32",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
