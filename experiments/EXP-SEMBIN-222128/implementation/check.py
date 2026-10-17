#!/usr/bin/env python3
"""Admissibility check for the stage-0 HKYY closure. No scientific prediction."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = (
    "schema", "experiment_id", "hypothesis_id", "trial_id", "stage",
    "nvars", "d_max", "d_ref", "d_pin", "d_pin_second", "sat_contains_one", "pins_agree",
)


def main() -> None:
    run_dir = Path(sys.argv[1])
    raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    missing = [name for name in REQUIRED if name not in raw]
    if missing:
        raise SystemExit(f"missing {missing}")
    if raw["schema"] != "crypto.autoresearch.exp-sembin-222128.stage0.v1":
        raise SystemExit("schema")
    if raw["experiment_id"] != "EXP-SEMBIN-222128":
        raise SystemExit("experiment")
    if raw["trial_id"] != "hkyy-toy-closure":
        raise SystemExit("trial")
    if raw["stage"] != 0 or raw["nvars"] != 2 or raw["d_max"] != 4:
        raise SystemExit("parameters")
    if not isinstance(raw["d_ref"], int) or not isinstance(raw["d_pin"], int):
        raise SystemExit("degrees")
    if not isinstance(raw["sat_contains_one"], bool) or not isinstance(raw["pins_agree"], bool):
        raise SystemExit("flags")
    manifest = (run_dir / "manifest.yaml").read_text(encoding="utf-8")
    if "EXP-SEMBIN-222128" not in manifest:
        raise SystemExit("manifest")
    results = (run_dir / "RESULTS.md").read_text(encoding="utf-8")
    if "slope" not in results:
        raise SystemExit("results")
    print("check ok")


if __name__ == "__main__":
    main()
