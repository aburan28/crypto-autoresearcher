#!/usr/bin/env python3
"""Independent check for EXP-BINSTD-6a150a run directories.

Recomputes modular residues for decidable rows and refuses fabricated TRUE.
Does not invent parameters. Amazon Bedrock not used.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from kdiv import route_a, route_b  # noqa: E402

EXP_ROOT = Path(__file__).resolve().parents[1]


def check_run_dir(run_dir: Path) -> int:
    raw = run_dir / "raw-result.json"
    man = run_dir / "manifest.yaml"
    if not raw.is_file() or not man.is_file():
        print(f"FAIL: missing raw-result.json or manifest.yaml in {run_dir}", file=sys.stderr)
        return 2
    data = json.loads(raw.read_text(encoding="utf-8"))
    stage = data.get("stage")
    if stage == 0:
        freeze = EXP_ROOT / "stage0" / "retrieval-protocol-freeze.json"
        preds = EXP_ROOT / "stage0" / "preregistered-predictions.json"
        if not freeze.is_file() or not preds.is_file():
            print("FAIL: stage0 freeze artifacts missing", file=sys.stderr)
            return 2
        print("OK stage0 freeze present")
        return 0
    if stage == 1:
        receipt = EXP_ROOT / "stage1" / "admission_receipt.json"
        if not receipt.is_file():
            print("FAIL: admission_receipt missing", file=sys.stderr)
            return 2
        print("OK stage1 admission_receipt present")
        return 0
    if stage == 2:
        part1_path = EXP_ROOT / "stage2" / "part1_rows.json"
        results = EXP_ROOT / "RESULTS.md"
        if not part1_path.is_file() or not results.is_file():
            print("FAIL: stage2 artifacts missing", file=sys.stderr)
            return 2
        part1 = json.loads(part1_path.read_text(encoding="utf-8"))
        fabricated = 0
        for row in part1.get("rows", []):
            if row.get("verdict") == "TRUE":
                if not row.get("primary_sourced") or row.get("tier") != "TIER-P":
                    fabricated += 1
                    continue
                k = int(row["k"])
                r = int(row["r"])
                if route_a(k, r) is not True or route_b(k, r) is not True:
                    print(f"FAIL: TRUE row {row['row']} fails twin recompute", file=sys.stderr)
                    return 2
            if row.get("verdict") == "FALSE":
                k = int(row["k"])
                r = int(row["r"])
                if route_a(k, r) is not False or route_b(k, r) is not False:
                    print(f"FAIL: FALSE row {row['row']} fails twin recompute", file=sys.stderr)
                    return 2
        if fabricated:
            print(f"FAIL: fabricated_true_count={fabricated}", file=sys.stderr)
            return 2
        label = part1.get("outcome_label")
        if f"Outcome label: **{label}**" not in results.read_text(encoding="utf-8"):
            # soft: RESULTS must mention the label
            if label not in results.read_text(encoding="utf-8"):
                print("FAIL: RESULTS.md missing outcome label", file=sys.stderr)
                return 2
        print(f"OK stage2 label={label} fabricated=0")
        return 0
    print(f"FAIL: unknown stage {stage}", file=sys.stderr)
    return 2


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir")
    args = p.parse_args(argv)
    return check_run_dir(Path(args.run_dir))


if __name__ == "__main__":
    raise SystemExit(main())
