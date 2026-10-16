#!/usr/bin/env python3
"""Check EXP-ECDLP-422afc.

Recomputes the census and independently checks the planted S3 identity.
A fraction outside the prediction band is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PRIMES = [101, 211, 307]


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("decomp_run", path)
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
    if result.get("primes") != PRIMES or result.get("m") != 2 or result.get("beta") != 0.5:
        print("frozen inputs changed", file=sys.stderr)
        return 1
    module = load_run(Path(__file__).with_name("run.py"))
    if module.census() != result:
        print("recompute mismatch", file=sys.stderr)
        return 1
    for item in result["cells"]:
        planted = item.get("planted") or {}
        if not item.get("planted_s3_zero"):
            print(f"planted sum failed at {item.get('prime')}", file=sys.stderr)
            return 1
        value = module.summation_s3(planted["x1"], planted["x2"], planted["x_sum"], item["prime"])
        if value != 0:
            print(f"independent S3 failed at {item.get('prime')}", file=sys.stderr)
            return 1
        if item["decomposing_count"] > item["prime"] or item["factor_base_size"] < 2:
            print(f"count out of range at {item.get('prime')}", file=sys.stderr)
            return 1
    text = manifest_path.read_text(encoding="utf-8")
    if "attack_claimed: false" not in text or "experiment_id: EXP-ECDLP-422afc" not in text:
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
