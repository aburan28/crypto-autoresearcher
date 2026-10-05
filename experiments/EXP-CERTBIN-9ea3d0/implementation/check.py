#!/usr/bin/env python3
"""Independent checks for one EXP-CERTBIN-9ea3d0 run directory."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AMAZON_BEDROCK = "NOT SELECTED"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    args = ap.parse_args()
    d = Path(args.run_dir)
    raw_path = d / "raw-result.json"
    if not raw_path.exists():
        print("missing raw-result.json", file=sys.stderr)
        return 2
    raw = json.loads(raw_path.read_text())
    if raw.get("amazon_bedrock") and AMAZON_BEDROCK not in str(raw.get("amazon_bedrock")):
        print("bedrock marker missing", file=sys.stderr)
        return 2
    if not raw.get("ok", False):
        print("payload ok != true", file=sys.stderr)
        return 2
    for name in ("command.txt", "stdout.log", "stderr.log"):
        if not (d / name).exists():
            print(f"missing {name}", file=sys.stderr)
            return 2
    print(json.dumps({"check": "pass", "stage": raw.get("stage")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
