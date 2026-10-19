#!/usr/bin/env python3
"""Integrity check for EXP-ENDO-7494e7 (not an outcome gate)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXPECTED = {"control+ascent: 11-descendant of a j = 0 curve (256-bit)", "mnt/mnt5/1", "other/Tom-384",
            "mnt/mnt5/2", "mnt/mnt5/3", "other/BADA55-VPR-224", "mnt/mnt3/1", "mnt/mnt3/3", "GOST 2001 test curve"}


def main() -> int:
    run_dir = Path(sys.argv[1])
    import yaml
    for name in ("manifest.yaml", "raw-result.json", "rows.jsonl"):
        if not (run_dir / name).is_file():
            print(f"missing {name}", file=sys.stderr)
            return 1
    man = yaml.safe_load((run_dir / "manifest.yaml").read_text())
    for name, digest in man["artifacts"].items():
        if hashlib.sha256((run_dir / name).read_bytes()).hexdigest() != digest:
            print(f"{name} digest mismatch", file=sys.stderr)
            return 1
    raw = json.loads((run_dir / "raw-result.json").read_text())
    names = {r["name"] for r in raw["rows"]}
    if names != EXPECTED:
        print(f"row set differs: missing {sorted(EXPECTED - names)} extra {sorted(names - EXPECTED)}", file=sys.stderr)
        return 1
    lines = [json.loads(l)["name"] for l in (run_dir / "rows.jsonl").read_text().splitlines() if l.strip()]
    if lines != [r["name"] for r in raw["rows"]]:
        print("rows.jsonl and raw-result.json disagree", file=sys.stderr)
        return 1
    a = raw["provenance"]["args"]
    if (a["build_limit"], a["max_candidates"], a["verify_scalars"], a["seed"], a["disc_bound"]) != (3, 12, 8, 20261016, 2000000):
        print("frozen parameters changed", file=sys.stderr)
        return 1
    print(f"ok: {len(raw['rows'])} rows, {sum(1 for r in raw['rows'] if 'error' in r)} with recorded errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
