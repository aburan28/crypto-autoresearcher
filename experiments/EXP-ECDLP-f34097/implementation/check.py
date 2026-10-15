#!/usr/bin/env python3
"""Schema check for an EXP-ECDLP-f34097 stage-0 observation.

Exit 0 when the three artifacts exist and name this cell.
The scientific pass/fail is a field in the observation, not this exit code.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = (
    "p",
    "degree_bound",
    "planted_section",
    "planted_on_curve",
    "identity_at_planted",
    "oracle_recovered",
    "oracle_multiplier",
    "structured_contains_planted",
    "structured_solution_count",
    "random_contains_planted",
    "random_solution_count",
    "variable_count",
)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check.py RUN_DIR")
    run_dir = Path(sys.argv[1])
    for name in ("manifest.yaml", "raw-result.json", "RESULTS.md"):
        if not (run_dir / name).is_file():
            raise SystemExit(f"missing {name}")
    payload = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    if payload.get("schema") != "crypto.autoresearch.exp-ecdlp-f34097.stage0.v1":
        raise SystemExit("unexpected schema")
    if payload.get("experiment_id") != "EXP-ECDLP-f34097":
        raise SystemExit("unexpected experiment id")
    if payload.get("p") != 31 or payload.get("degree_bound") != 1:
        raise SystemExit("cell is not the preregistered (p, d) = (31, 1)")
    if payload.get("planted_section") != [2, 0, 3, 0]:
        raise SystemExit("planted section does not match the freeze")
    missing = [key for key in REQUIRED if key not in payload]
    if missing:
        raise SystemExit(f"missing fields: {', '.join(missing)}")
    manifest = (run_dir / "manifest.yaml").read_text(encoding="utf-8")
    if "RUN-ECDLP-62ec3d" not in manifest or "EXP-ECDLP-f34097" not in manifest:
        raise SystemExit("manifest does not name this run")
    text = (run_dir / "RESULTS.md").read_text(encoding="utf-8")
    if "section-cost" not in text:
        raise SystemExit("RESULTS.md is missing the claim-boundary sentence")


if __name__ == "__main__":
    main()
