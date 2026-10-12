#!/usr/bin/env python3
"""Check EXP-ECDLP-3c166b.

Recomputes the half-count. A matrix miss is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


P = 29


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("half_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def multiplicity(x_value: int, curve_a: int, curve_b: int) -> int:
    target = (x_value * x_value * x_value + curve_a * x_value + curve_b) % P
    return sum(1 for y_value in range(P) if (y_value * y_value) % P == target)


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
    if result.get("experiment_id") != "EXP-ECDLP-3c166b" or result.get("prime") != P:
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("attack_claimed") is not False:
        print("attack flag set", file=sys.stderr)
        return 1
    if result.get("low_end") != 14 or result.get("expected_gap") != 3:
        print("cut or gap changed", file=sys.stderr)
        return 1
    curves = result.get("curves")
    if not isinstance(curves, list) or len(curves) != 2:
        print("curve record changed", file=sys.stderr)
        return 1
    expected = {
        "E1": (20, 16, 37, 23, 1),
        "E2": (10, 9, 20, 4, 0),
    }
    fresh = {}
    for name, curve_a, curve_b in (("E1", -1, 1), ("E2", 1, 0)):
        low = high = 0
        for x_value in range(P):
            count = multiplicity(x_value, curve_a, curve_b)
            if x_value <= 14:
                low += count
            else:
                high += count
        fresh[name] = (low, high)
    for row in curves:
        name = row.get("name")
        if name not in expected:
            print("unexpected curve", file=sys.stderr)
            return 1
        low, high, projective, disc, constant = expected[name]
        if (row.get("expected_low"), row.get("expected_high"), row.get("expected_projective")) != (low, high, projective):
            print("pre-registered counts changed", file=sys.stderr)
            return 1
        if row.get("discriminant") != disc:
            print("discriminant changed", file=sys.stderr)
            return 1
        if fresh[name] != (row.get("low"), row.get("high")):
            print("half-count mismatch", file=sys.stderr)
            return 1
        if constant != row.get("b"):
            print("curve equation changed", file=sys.stderr)
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
        "experiment_id: EXP-ECDLP-3c166b",
        "planted_ok: true",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
