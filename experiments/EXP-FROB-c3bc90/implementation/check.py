"""Recompute the frozen cell and compare it to raw-result.json.

The second-shift counts and the half-sample flag are compared for
equality and then ignored when the reading row is checked.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run import build_report, gap_ge, gap_le, reading_row  # noqa: E402


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
    for key in ("g_obj_num", "g_obj_den", "g_null_num", "g_null_den"):
        if reading.get(key) != recorded[key]:
            print(f"reading.yaml {key} disagrees with raw-result.json", file=sys.stderr)
            return 1
    checks = recorded["checks"]
    if not isinstance(checks, dict) or not checks:
        print("checks missing", file=sys.stderr)
        return 1
    n_obj = int(recorded["n_obj"])
    n_null = int(recorded["n_null"])
    lossy = bool(recorded["l_at_least_one"])
    meets = gap_ge(int(recorded["object_zeros_rel"]), int(recorded["object_zeros_shift"]), n_obj) and gap_le(
        int(recorded["null_zeros_rel"]), int(recorded["null_zeros_shift"]), n_null
    )
    expected = reading_row(checks, n_obj >= 100 and n_null >= 100, lossy, meets and n_obj > 0 and n_null > 0)
    if recorded["reading_row"] != expected:
        print("reading row does not match the frozen rule", file=sys.stderr)
        return 1
    if recorded["reading_row"] not in (
        "instrument_failure",
        "sample_under_100",
        "not_lossy",
        "gap_misses_claim",
        "gap_meets_claim",
    ):
        print("unknown reading row", file=sys.stderr)
        return 1
    if recorded.get("secondary_does_not_choose_row") is not True:
        print("secondary flag missing", file=sys.stderr)
        return 1
    for key in ("t2_n", "t2_zeros_rel", "t2_zeros_shift", "halves_close", "object_y0"):
        if key not in recorded:
            print(f"secondary field {key} missing", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
