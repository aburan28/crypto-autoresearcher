#!/usr/bin/env python3
"""Check EXP-SCURVE-41f104.

Recomputes the j-invariant with integer arithmetic written out again.
A matrix miss is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from math import gcd
from pathlib import Path


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("rho_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def independent_j(coefficient_a: int):
    denominator = coefficient_a * coefficient_a - 4
    if denominator == 0:
        return None
    numerator = 256 * (coefficient_a * coefficient_a - 3) ** 3
    common = gcd(abs(numerator), abs(denominator))
    return numerator // common, denominator // common


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
    if result.get("experiment_id") != "EXP-SCURVE-41f104" or result.get("toy_order") != 10007:
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("attack_claimed") is not False:
        print("attack flag set", file=sys.stderr)
        return 1
    module = load_run(Path(__file__).with_name("run.py"))
    if module.census() != result:
        print("recompute mismatch", file=sys.stderr)
        return 1
    if not result.get("planted_ok"):
        print("j undefined", file=sys.stderr)
        return 1
    recomputed = independent_j(117050)
    main_row = result["main"]
    if recomputed != (main_row["j_numerator"], main_row["j_denominator"]):
        print("independent j mismatch", file=sys.stderr)
        return 1
    text = manifest_path.read_text(encoding="utf-8")
    required = (
        "attack_claimed: false",
        "experiment_id: EXP-SCURVE-41f104",
        "planted_ok: true",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
