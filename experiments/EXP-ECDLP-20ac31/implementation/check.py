#!/usr/bin/env python3
"""Check EXP-ECDLP-20ac31.

Recomputes the square-bias worksheet. A matrix miss is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("bias_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    if result.get("experiment_id") != "EXP-ECDLP-20ac31":
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("attack_claimed") is not False:
        print("attack flag set", file=sys.stderr)
        return 1
    if result.get("seed_label") != "IDEA-20261006-30b5f6" or result.get("rank") != 285:
        print("percentile rule changed", file=sys.stderr)
        return 1
    if result.get("shuffles") != 300 or result.get("success_consults_side") is not False:
        print("null model changed", file=sys.stderr)
        return 1
    prime = result.get("prime")
    if not isinstance(prime, int) or prime < 23 or prime > 120:
        print("prime outside the scan", file=sys.stderr)
        return 1
    shuffle_abs = result.get("shuffle_abs")
    if not isinstance(shuffle_abs, list) or len(shuffle_abs) != 300:
        print("shuffle record is short", file=sys.stderr)
        return 1
    ordered = sorted(shuffle_abs)
    if result.get("cutoff") != ordered[284]:
        print("cutoff is not rank 285", file=sys.stderr)
        return 1
    numerator = result.get("abs_numerator")
    if not isinstance(numerator, int) or result.get("exceeds") is not (numerator > ordered[284]):
        print("comparison drifted", file=sys.stderr)
        return 1
    public = result.get("public_point")
    if not isinstance(public, list) or len(public) != 2:
        print("missing public point", file=sys.stderr)
        return 1
    x_value, y_value = public
    rhs = (x_value * x_value * x_value + 6 * x_value + 2) % prime
    if (y_value * y_value - rhs) % prime != 0:
        print("public point off the curve", file=sys.stderr)
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
        "experiment_id: EXP-ECDLP-20ac31",
        "planted_ok: true",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
