"""Recompute the frozen cell and compare it to raw-result.json.

A mismatch, a missing artifact, or attack_claimed true fails the check.
norm_max_fanout is compared and then ignored when the reading row is checked.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from run import build_report


def main(argv=None) -> int:
    run_dir = Path(argv[0] if argv else sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    reading_path = run_dir / "reading.yaml"
    manifest_path = run_dir / "manifest.yaml"
    for path in (raw_path, reading_path, manifest_path):
        if not path.is_file() or path.stat().st_size == 0:
            print(f"missing or empty {path.name}", file=sys.stderr)
            return 1
    recorded = json.loads(raw_path.read_text(encoding="utf-8"))
    fresh = build_report()
    if recorded != fresh:
        print("raw-result.json does not match a fresh computation", file=sys.stderr)
        return 1
    reading = yaml.safe_load(reading_path.read_text(encoding="utf-8"))
    if reading.get("attack_claimed") is not False or recorded.get("attack_claimed") is not False:
        print("attack_claimed must be false", file=sys.stderr)
        return 1
    if reading.get("reading_row") != recorded["reading_row"]:
        print("reading.yaml row disagrees with raw-result.json", file=sys.stderr)
        return 1
    checks = recorded["checks"]
    row = recorded["reading_row"]
    norm = recorded["norm"]
    if not isinstance(checks, dict) or not checks:
        print("checks missing", file=sys.stderr)
        return 1
    passed = all(bool(v) for v in checks.values())
    if not passed and row != "instrument_failure":
        print("failed check must read instrument_failure", file=sys.stderr)
        return 1
    if passed and not norm["l_ge_2"] and row != "not_lossy":
        print("L < 2 must read not_lossy", file=sys.stderr)
        return 1
    if passed and norm["l_ge_2"] and norm["b_gt_4"] and row != "explanation_1":
        print("b > 4 with L >= 2 must read explanation_1", file=sys.stderr)
        return 1
    if passed and norm["l_ge_2"] and norm["b_le_4"] and row != "bounded_branching":
        print("b <= 4 with L >= 2 must read bounded_branching", file=sys.stderr)
        return 1
    if row not in ("instrument_failure", "not_lossy", "explanation_1", "bounded_branching"):
        print("unknown reading row", file=sys.stderr)
        return 1
    if recorded.get("max_fanout_does_not_choose_row") is not True:
        print("max fanout must not choose the row", file=sys.stderr)
        return 1
    if "secondary" not in recorded:
        print("secondary block missing", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
