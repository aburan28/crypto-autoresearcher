#!/usr/bin/env python3
"""Check EXP-PAIR-f4584a.

Recomputes the slot census with a second copy of the arithmetic.
A gap that misses the pre-registered pattern is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("pair_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def trial_smooth(value: int) -> bool:
    magnitude = abs(value)
    if magnitude == 0:
        return False
    for prime in (2, 3, 5, 7):
        while magnitude % prime == 0:
            magnitude //= prime
    return magnitude == 1


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
    if result.get("experiment_id") != "EXP-PAIR-f4584a" or result.get("bound") != 7:
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
        print("controls failed", file=sys.stderr)
        return 1
    for cell in result["named_points"]:
        if not cell["agreed"]:
            print("expansions disagree", file=sys.stderr)
            return 1
        value_f = cell["values"]["f"][0]
        value_g = cell["values"]["g"][0]
        if trial_smooth(value_f) != module.smooth(value_f) or trial_smooth(value_g) != module.smooth(value_g):
            print("independent smoothness mismatch", file=sys.stderr)
            return 1
    text = manifest_path.read_text(encoding="utf-8")
    required = (
        "attack_claimed: false",
        "experiment_id: EXP-PAIR-f4584a",
        "planted_ok: true",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
