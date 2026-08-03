#!/usr/bin/env python3
"""Recompute CTRL-NULL-IT-PLANT detection from a raw edge ledger.

Independent of the Executor driver: given an edge ledger and C_search,
recompute C_path and evaluate the plant-detection predicate used by EXP-IT-001.

Usage:
  python3 recompute_null_plant_from_ledger.py \
    --ledger path/to/ctrl_null_it_plant_edge_ledger.jsonl \
    --c-search INT \
    --c-path-reported INT

Ledger formats accepted:
  * JSONL rows with fields {ell, c_iso?} (and optional from_j/to_j)
  * JSON list of the same objects
  * JSON object with key "edge_ledger"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def c_iso(ell: int) -> int:
    """Match experiments/EXP-IT-001/implementation/it001_pure.c_iso."""
    return 4 * int(ell)


def load_ledger(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text()
    if path.suffix == ".jsonl" or "\n" in raw.strip() and raw.lstrip().startswith("{"):
        rows = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        # Heuristic: if first parse was a single JSON list dumped as one line, handle below
        if len(rows) == 1 and isinstance(rows[0], list):
            return rows[0]
        if len(rows) == 1 and isinstance(rows[0], dict) and "edge_ledger" in rows[0]:
            return list(rows[0]["edge_ledger"])
        return rows
    data = json.loads(raw)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "edge_ledger" in data:
        return list(data["edge_ledger"])
    raise ValueError(f"unrecognized ledger shape in {path}")


def recompute(edge_ledger: list[dict[str, Any]], c_search: int) -> dict[str, Any]:
    charged = []
    for e in edge_ledger:
        ell = int(e.get("ell", 0))
        cis = int(e["c_iso"]) if "c_iso" in e else c_iso(ell)
        charged.append({**e, "ell": ell, "c_iso": cis})
    c_eval = sum(int(e["c_iso"]) for e in charged)
    c_path = int(c_search) + int(c_eval)
    return {
        "edge_count": len(charged),
        "C_search": int(c_search),
        "C_eval": int(c_eval),
        "C_path_recomputed": int(c_path),
        "edge_ledger": charged,
    }


def plant_detected(c_path_reported: int, c_path_recomputed: int, eps: int = 0) -> bool:
    # Mirror run_bounded_toy / it001_driver plant predicate:
    # reported is a packaged undercount of recomputed honest path.
    return (
        c_path_reported <= (c_path_recomputed // 4) + eps
        and c_path_reported < c_path_recomputed
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", required=True, type=Path)
    p.add_argument("--c-search", required=True, type=int)
    p.add_argument("--c-path-reported", required=True, type=int)
    p.add_argument("--eps", type=int, default=0)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    ledger = load_ledger(args.ledger)
    recomputed = recompute(ledger, args.c_search)
    detected = plant_detected(args.c_path_reported, recomputed["C_path_recomputed"], args.eps)
    out = {
        "plant_detection_id": "CTRL-NULL-IT-PLANT-v3",
        "C_path_reported": int(args.c_path_reported),
        "plant_detected": bool(detected),
        "plant_detection_eps": int(args.eps),
        **recomputed,
    }
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.write_text(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
