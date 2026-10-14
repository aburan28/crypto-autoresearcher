#!/usr/bin/env python3
"""Check EXP-SEMBIN-22a1a2.

Recomputes the labelled falls and checks the planted field arithmetic.
A matrix miss is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("fall_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def binomial(n: int, k: int) -> int:
    value = 1
    for i in range(k):
        value = value * (n - i) // (i + 1)
    return value


def square_cancels() -> bool:
    exponents = tuple(1 if i == 0 else 0 for i in range(9))
    doubled = tuple(2 if i == 0 else 0 for i in range(9))
    reduced = tuple(1 if exponent else 0 for exponent in doubled)
    return reduced == exponents and sum(doubled) == 2


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
    if result.get("experiment_id") != "EXP-SEMBIN-22a1a2":
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("n_field") != 3 or result.get("degree_cap") != 4 or result.get("bound") != 4:
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("attack_claimed") is not False:
        print("attack flag set", file=sys.stderr)
        return 1
    if binomial(13, 4) != 715 or result.get("column_count") != 715:
        print("monomial count mismatch", file=sys.stderr)
        return 1
    if not square_cancels():
        print("boolean reduction mismatch", file=sys.stderr)
        return 1
    # z^3 + z + 1 has no root in F_2.
    if (1) == 0 or (1 ^ 1 ^ 1) == 0:
        print("modulus is not irreducible", file=sys.stderr)
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
        "experiment_id: EXP-SEMBIN-22a1a2",
        "planted_ok: true",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
