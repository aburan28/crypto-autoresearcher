#!/usr/bin/env python3
"""Check EXP-ECDLP-5f4f14.

Recomputes the chord-slope worksheet. A matrix miss is not a checker failure.
An unscored census is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("slope_run", path)
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
    if result.get("experiment_id") != "EXP-ECDLP-5f4f14" or result.get("prime") != 53:
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("attack_claimed") is not False:
        print("attack flag set", file=sys.stderr)
        return 1
    if result.get("seed_label") != "IDEA-20261006-76e571":
        print("seed label changed", file=sys.stderr)
        return 1
    if (result.get("loss_numerator"), result.get("split_numerator")) != (5, 2):
        print("separators changed", file=sys.stderr)
        return 1
    if result.get("minimum_prime_factor") != 17 or result.get("null_draws") != 500:
        print("eligibility rule changed", file=sys.stderr)
        return 1
    if result.get("scanner_ok") is not True:
        print("scanner failed", file=sys.stderr)
        return 1
    if result.get("scored") is not True and (result.get("matrix_holds") or result.get("beyond_matrix")):
        print("unscored census produced a matrix reading", file=sys.stderr)
        return 1
    if result.get("scored") is True:
        domain = result.get("domain_size")
        image = result.get("image_size")
        if not isinstance(domain, int) or not isinstance(image, int):
            print("sizes missing", file=sys.stderr)
            return 1
        if result.get("loss_ok") is not (5 * (domain - image) >= domain):
            print("loss test drifted", file=sys.stderr)
            return 1
    module = load_run(Path(__file__).with_name("run.py"))
    if module.census() != result:
        print("recompute mismatch", file=sys.stderr)
        return 1
    text = manifest_path.read_text(encoding="utf-8")
    required = (
        "attack_claimed: false",
        "experiment_id: EXP-ECDLP-5f4f14",
        "scanner_ok: true",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
