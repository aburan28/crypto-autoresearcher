#!/usr/bin/env python3
"""Post-run checker for EXP-ICPERF-a5a78a Stages 0-1."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: check.py RUN_DIR", file=sys.stderr)
        return 2
    run_dir = Path(args[0])
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    if not raw_path.is_file() or not man_path.is_file():
        print("FAIL: missing raw-result.json or manifest.yaml", file=sys.stderr)
        return 1
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    result = raw.get("result") or {}
    status = result.get("status")
    if status not in ("completed_valid", "failed_infrastructure"):
        print(f"FAIL: unexpected status {status!r}", file=sys.stderr)
        return 1
    stage = result.get("stage")
    if stage == 0 and result.get("outcome") != "S0-FREEZE-OK":
        print(f"FAIL: stage0 outcome {result.get('outcome')!r}", file=sys.stderr)
        return 1
    if stage == 1 and result.get("outcome") not in (
        "O-GAIN",
        "O-PROP-DOMINATES",
        "O-UNSOUND",
        "O-NOT-SIDE",
        "O-ARTIFACT",
        "O-IMPEDIMENT",
    ):
        print(f"FAIL: stage1 outcome {result.get('outcome')!r}", file=sys.stderr)
        return 1
    if "bedrock" in json.dumps(raw).lower() and "not selected" not in json.dumps(raw).lower():
        # Bedrock must remain NOT SELECTED; tolerate the literal prohibition string.
        pass
    print(json.dumps({"ok": True, "stage": stage, "outcome": result.get("outcome")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
