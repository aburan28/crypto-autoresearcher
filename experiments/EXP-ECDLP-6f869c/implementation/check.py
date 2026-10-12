#!/usr/bin/env python3
"""Check EXP-ECDLP-6f869c.

Recomputes the step-ratio worksheet. A matrix miss is not a checker failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_run(path: Path):
    spec = importlib.util.spec_from_file_location("walk_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lower_median(values: list[int]) -> int:
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]


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
    if result.get("experiment_id") != "EXP-ECDLP-6f869c" or result.get("prime") != 503:
        print("frozen inputs changed", file=sys.stderr)
        return 1
    if result.get("attack_claimed") is not False or result.get("generator") != 1:
        print("attack flag set", file=sys.stderr)
        return 1
    if result.get("seed_label") != "IDEA-20261006-6374b1":
        print("seed label changed", file=sys.stderr)
        return 1
    if (result.get("threshold_numerator"), result.get("threshold_denominator")) != (7, 5):
        print("ratio threshold changed", file=sys.stderr)
        return 1
    if result.get("cap") != 2000 or result.get("minimum_finished") != 12 or result.get("seeds") != 16:
        print("budget changed", file=sys.stderr)
        return 1
    identity = result.get("identity") or {}
    joint_steps = identity.get("joint_steps")
    separate_steps = identity.get("separate_steps")
    if not isinstance(joint_steps, list) or joint_steps != identity.get("joint_steps"):
        print("identity record missing", file=sys.stderr)
        return 1
    if isinstance(joint_steps, list) and len(joint_steps) >= 12:
        if identity.get("joint_median") != lower_median(joint_steps):
            print("joint median drifted", file=sys.stderr)
            return 1
        if identity.get("separate_median") != lower_median(separate_steps):
            print("separate median drifted", file=sys.stderr)
            return 1
        joint = identity["joint_median"]
        separate = identity["separate_median"]
        if identity.get("at_least_7_5") is not (5 * separate >= 7 * joint):
            print("ratio comparison drifted", file=sys.stderr)
            return 1
    module = load_run(Path(__file__).with_name("run.py"))
    if module.census() != result:
        print("recompute mismatch", file=sys.stderr)
        return 1
    if result.get("scanner_ok") is not True or result.get("implementations_agree") is not True:
        print("scanner disagreed", file=sys.stderr)
        return 1
    if result.get("scored") is True and result.get("planted_ok") is not True:
        print("scored census is not planted", file=sys.stderr)
        return 1
    if result.get("scored") is not True and (result.get("matrix_holds") or result.get("beyond_matrix")):
        print("unscored census produced a matrix reading", file=sys.stderr)
        return 1
    text = manifest_path.read_text(encoding="utf-8")
    required = (
        "attack_claimed: false",
        "experiment_id: EXP-ECDLP-6f869c",
        "scanner_ok: true",
    )
    if any(line not in text for line in required):
        print("manifest missing required fields", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
