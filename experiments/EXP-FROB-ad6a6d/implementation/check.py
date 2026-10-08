"""Recompute the frozen cell and compare it to raw-result.json.

The secondary image I_rev, I_tan, and the empty-bin fraction are
compared for equality and then ignored when the reading row is checked.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run import build_report  # noqa: E402


def main(argv: list[str] | None = None) -> int:
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
    if reading.get("i_frob") != recorded["i_frob"] or reading.get("i_rand") != recorded["i_rand"]:
        print("reading.yaml counts disagree with raw-result.json", file=sys.stderr)
        return 1
    checks = recorded["checks"]
    if not isinstance(checks, dict) or not checks:
        print("checks missing", file=sys.stderr)
        return 1
    passed = all(bool(value) for value in checks.values())
    lossy = bool(recorded["l_at_least_one"])
    exceeds = recorded["i_frob"] > recorded["threshold"]
    row = recorded["reading_row"]
    if (not passed) and row != "instrument_failure":
        print("failed check must read instrument_failure", file=sys.stderr)
        return 1
    if passed and (not lossy) and row != "not_lossy":
        print("L < 1 must read not_lossy", file=sys.stderr)
        return 1
    if passed and lossy and exceeds and row != "image_exceeds_half":
        print("the inequality failure must read image_exceeds_half", file=sys.stderr)
        return 1
    if passed and lossy and (not exceeds) and row != "image_at_most_half":
        print("the prediction must read image_at_most_half", file=sys.stderr)
        return 1
    if row not in ("instrument_failure", "not_lossy", "image_exceeds_half", "image_at_most_half"):
        print("unknown reading row", file=sys.stderr)
        return 1
    if recorded.get("secondary_does_not_choose_row") is not True:
        print("secondary flag missing", file=sys.stderr)
        return 1
    if "i_tan" not in recorded or "i_rev" not in recorded:
        print("secondary counts missing", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
