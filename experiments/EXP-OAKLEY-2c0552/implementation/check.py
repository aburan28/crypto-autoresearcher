#!/usr/bin/env python3
"""Check EXP-OAKLEY-2c0552.

Recomputes the quadruple census and checks the planted S3 identity
with the same polynomial written out again. A positive disagreement
count is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PRIME = 17
A = 1
B = 1


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("chain_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summation_s3(x1: int, x2: int, x3: int) -> int:
    difference = (x1 - x2) % PRIME
    first = difference * difference % PRIME * (x3 * x3 % PRIME) % PRIME
    middle = ((x1 + x2) * ((x1 * x2 + A) % PRIME) + 2 * B) % PRIME
    second = 2 * middle % PRIME * x3 % PRIME
    third = pow((x1 * x2 - A) % PRIME, 2, PRIME)
    fourth = 4 * B % PRIME * ((x1 + x2) % PRIME) % PRIME
    return (first - second + third - fourth) % PRIME


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
    if result.get("prime") != PRIME or result.get("experiment_id") != "EXP-OAKLEY-2c0552":
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("ordered_quadruples") != PRIME ** 4 or result.get("attack_claimed") is not False:
        print("census domain changed", file=sys.stderr)
        return 1
    module = load_run(Path(__file__).with_name("run.py"))
    if module.census() != result:
        print("recompute mismatch", file=sys.stderr)
        return 1
    if not result.get("planted_ok"):
        print("planted sum failed", file=sys.stderr)
        return 1
    planted = result.get("planted") or {}
    if summation_s3(planted["x1"], planted["x2"], planted["x_sum"]) != 0:
        print("independent S3 failed", file=sys.stderr)
        return 1
    count = result.get("disagreement_count")
    if not isinstance(count, int) or count < 0 or count > PRIME ** 4:
        print("disagreement count out of range", file=sys.stderr)
        return 1
    text = manifest_path.read_text(encoding="utf-8")
    required = (
        "attack_claimed: false",
        "experiment_id: EXP-OAKLEY-2c0552",
        "planted_ok: true",
        f"disagreement_count: {count}",
        f"ordered_quadruples: {PRIME ** 4}",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
