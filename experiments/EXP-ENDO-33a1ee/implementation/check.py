#!/usr/bin/env python3
"""Integrity check for EXP-ENDO-33a1ee (not an outcome gate): artifacts, digests, frozen parameters, correctness."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def main() -> int:
    run_dir = Path(sys.argv[1])
    import yaml
    man = yaml.safe_load((run_dir / "manifest.yaml").read_text())
    for name, digest in man["artifacts"].items():
        path = run_dir / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            print(f"{name} missing or digest mismatch", file=sys.stderr)
            return 1
    raw = json.loads((run_dir / "raw-result.json").read_text())
    for role in ("target", "control"):
        s = raw[role]
        if (s["points"], s["reps"]) != (64, 41):
            print(f"{role}: frozen parameters changed", file=sys.stderr)
            return 1
        if not s["correct"]:
            print(f"{role}: outputs disagree with the reference: {s['mismatches'][:5]}", file=sys.stderr)
            return 1
        t = json.loads((run_dir / role / "timings.json").read_text())
        if any(len(t[a]) != 41 for a in ("A0", "A1", "A2", "A3")):
            print(f"{role}: timing series incomplete", file=sys.stderr)
            return 1
    print("ok: both curves correct, 41 repetitions x 4 arms recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
