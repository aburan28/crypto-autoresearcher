#!/usr/bin/env python3
"""Check EXP-ECDLP-bfbe6f.

Recomputes the twelve-residue worksheet. A matrix miss is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


P = 41
A = 1
B = 2
POINTS = ((0, 17), (1, 2), (3, 14), (5, 3))
PAIRS = ((0, 1), (0, 3), (0, 5), (1, 3), (1, 5), (3, 5))
EXPECTED_AT_SEVEN = [13, 33, 35, 11, 28, 38]
THIRD = 7


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("ecdlp_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def s3(x1: int, x2: int, x3: int) -> int:
    leading = (x1 - x2) ** 2 % P
    linear = 2 * ((x1 + x2) * (x1 * x2 + A) + 2 * B) % P
    constant = ((x1 * x2 - A) ** 2 - 4 * B * (x1 + x2)) % P
    return (leading * x3 * x3 - linear * x3 + constant) % P


def inv(value: int) -> int:
    return pow(value % P, P - 2, P)


def ec_add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int] | None:
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    slope = ((y2 - y1) % P * inv((x2 - x1) % P)) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)


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
    if result.get("experiment_id") != "EXP-ECDLP-bfbe6f" or result.get("prime") != P:
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("attack_claimed") is not False:
        print("attack flag set", file=sys.stderr)
        return 1
    if result.get("expected_at_seven") != EXPECTED_AT_SEVEN:
        print("pre-registered residues changed", file=sys.stderr)
        return 1
    if result.get("success_consults_diagonal") is not False:
        print("diagonal entered the success test", file=sys.stderr)
        return 1
    if result.get("pairs") != [list(pair) for pair in PAIRS]:
        print("pair order changed", file=sys.stderr)
        return 1
    for x_value, y_value in POINTS:
        rhs = (x_value * x_value * x_value + A * x_value + B) % P
        if (y_value * y_value) % P != rhs:
            print("point off the curve", file=sys.stderr)
            return 1
    if (4 * A * A * A + 27 * B * B) % P == 0:
        print("singular curve", file=sys.stderr)
        return 1
    by_x = {x_value: (x_value, y_value) for x_value, y_value in POINTS}
    fresh_sum = []
    fresh_true = []
    fresh_seven = []
    for x1, x2 in PAIRS:
        total = ec_add(by_x[x1], by_x[x2])
        if total is None:
            print("sum left the affine plane", file=sys.stderr)
            return 1
        fresh_sum.append(total[0])
        fresh_true.append(s3(x1, x2, total[0]))
        fresh_seven.append(s3(x1, x2, THIRD))
    if fresh_sum != result.get("sum_x") or fresh_true != result.get("true_values"):
        print("true-sum worksheet mismatch", file=sys.stderr)
        return 1
    if fresh_seven != result.get("seven_values"):
        print("fixed-seven worksheet mismatch", file=sys.stderr)
        return 1
    module = load_run(Path(__file__).with_name("run.py"))
    if module.census() != result:
        print("recompute mismatch", file=sys.stderr)
        return 1
    if not result.get("planted_ok"):
        print("planted controls failed", file=sys.stderr)
        return 1
    text = manifest_path.read_text(encoding="utf-8")
    required = (
        "attack_claimed: false",
        "experiment_id: EXP-ECDLP-bfbe6f",
        "planted_ok: true",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
