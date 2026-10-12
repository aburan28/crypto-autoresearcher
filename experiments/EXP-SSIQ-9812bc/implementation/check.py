"""Recompute the fiber gap and compare it to the written artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run import build_report, reading_row  # noqa: E402


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: check.py RUN_DIR", file=sys.stderr)
        return 1
    run_dir = Path(args[0])
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
    if not isinstance(reading, dict):
        print("reading.yaml is not a mapping", file=sys.stderr)
        return 1
    if reading.get("attack_claimed") is not False or recorded.get("attack_claimed") is not False:
        print("attack_claimed must be false", file=sys.stderr)
        return 1
    for key in ("reading_row", "gap", "m_a", "m_n", "n_a", "n_n", "checks_pass"):
        if reading.get(key) != recorded[key]:
            print(f"reading.yaml {key} disagrees with raw-result.json", file=sys.stderr)
            return 1
    expected = reading_row(
        bool(recorded["checks_pass"]),
        int(recorded["gap"]),
        int(recorded["n_a"]),
        int(recorded["n_n"]),
    )
    if recorded["reading_row"] != expected:
        print("reading row does not match the frozen rule", file=sys.stderr)
        return 1
    if recorded["reading_row"] not in (
        "instrument_failure",
        "negative_gap",
        "sample_size_explains_gap",
        "gap_meets_claim",
    ):
        print("unknown reading row", file=sys.stderr)
        return 1
    if recorded["source_idea"] != "IDEA-20261006-592877":
        print("source idea mismatch", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
