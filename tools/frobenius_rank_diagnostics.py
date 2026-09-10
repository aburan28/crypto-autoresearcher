#!/usr/bin/env python3
"""Read-only diagnostics for EXP-FROB-b8cf21's stored metrics, not a rank verifier.

Assumes the source's verified homogeneous rows over a prime-order subgroup,
with one column per nonidentity representative and no target-log column.
For U > 0 the nonzero logarithm vector gives rank <= U-1. This is an ambient
upper bound, not a claim that the chosen relation family attains it.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
from typing import Any


def natural(record: dict[str, Any], key: str) -> int:
    value = record.get(key)
    if type(value) is not int or value < 0:
        raise ValueError(f"{key} must be a nonnegative integer")
    return value


def ratio(numerator: int, denominator: int) -> dict[str, int] | None:
    if denominator == 0:
        return None
    value = Fraction(numerator, denominator)
    return {"numerator": value.numerator, "denominator": value.denominator}


def audit_metrics(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("metrics must be an object")
    cells, covers = data.get("cells"), data.get("covers")
    if not isinstance(cells, list) or not cells or not isinstance(covers, list):
        raise ValueError("nonempty cells and a covers list are required")
    cell_map: dict[str, dict[str, Any]] = {}
    for cell in cells:
        if not isinstance(cell, dict) or not isinstance(cell.get("id"), str):
            raise ValueError("invalid cell")
        if not cell["id"] or cell["id"] in cell_map:
            raise ValueError("empty or duplicate cell id")
        if not isinstance(cell.get("status"), str) or not cell["status"]:
            raise ValueError("cell status is required")
        if cell["status"] == "completed":
            natural(cell, "cover_count")
            if natural(cell, "N") < 2:
                raise ValueError("completed cell requires subgroup order N >= 2")
        cell_map[cell["id"]] = cell
    counts: Counter[str] = Counter()
    seen: set[tuple[str, str]] = set()
    rows: list[dict[str, Any]] = []
    for cover in covers:
        if not isinstance(cover, dict):
            raise ValueError("cover must be an object")
        cell_id, cover_id = cover.get("cell"), cover.get("cover")
        if not isinstance(cell_id, str) or not isinstance(cover_id, str) or not cover_id:
            raise ValueError("cover requires cell and cover identifiers")
        cell = cell_map.get(cell_id)
        if cell is None or cell["status"] != "completed":
            raise ValueError("cover refers to unknown or incomplete cell")
        key = (cell_id, cover_id)
        if key in seen:
            raise ValueError("duplicate cover")
        seen.add(key)
        counts[cell_id] += 1
        t = natural(cover, "t")
        attempted = natural(cover, "ordered_pairs")
        baseline = natural(cover, "unique_single_base_pairs")
        accepted = natural(cover, "accepted_pairs")
        mixed = natural(cover, "mixed_accepted_pairs")
        same_pairs = natural(cover, "same_base_accepted_pairs")
        if t < 1 or baseline > attempted or accepted > attempted or accepted != mixed + same_pairs:
            raise ValueError("inconsistent cover or pair counts")
        if t == 1 and mixed:
            raise ValueError("single-base control contains mixed pairs")
        presentations = cover.get("presentations")
        if not isinstance(presentations, dict) or not presentations:
            raise ValueError("presentations are required")
        for name, metrics in presentations.items():
            if name not in {"negation", "frobenius_negation"} or not isinstance(metrics, dict):
                raise ValueError("unsupported presentation")
            u = natural(metrics, "U")
            same = natural(metrics, "same_rank")
            all_rank = natural(metrics, "all_rank")
            delta = natural(metrics, "Delta_rank")
            ceiling = max(0, u - 1)
            if not (same <= all_rank <= ceiling) or delta != all_rank - same:
                raise ValueError("rank violates homogeneous prime-order presentation or Delta_rank")
            if natural(metrics, "rank_deficit") != u - all_rank:
                raise ValueError("rank_deficit disagrees with U-all_rank")
            if (not accepted and all_rank) or (not same_pairs and same) or (not mixed and delta):
                raise ValueError("positive rank without supporting accepted pairs")
            if t == 1 and delta:
                raise ValueError("single-base control adds rank")
            headroom = ceiling - same
            if not u:
                diagnosis = "empty_presentation"
            elif t == 1:
                diagnosis = "single_base_control"
            elif not headroom:
                diagnosis = "ambient_rank_saturated"
            elif not accepted:
                diagnosis = "no_relations"
            elif not mixed:
                diagnosis = "no_mixed_relations"
            elif not delta:
                diagnosis = "mixed_rows_add_no_rank"
            else:
                diagnosis = "mixed_span_gain"
            rows.append({
                "cell": cell_id, "cover": cover_id, "presentation": name,
                "t": t, "U": u, "same_rank": same, "all_rank": all_rank,
                "Delta_rank": delta, "ambient_rank_ceiling": ceiling,
                "ambient_headroom_before_mixing": headroom,
                "ambient_headroom_after_mixing": ceiling - all_rank,
                "diagnosis": diagnosis, "no_relations": accepted == 0,
                "no_mixed_relations": mixed == 0, "ambient_saturated": headroom == 0,
                "all_pairs_per_added_dimension": ratio(attempted, delta),
                "extra_pairs_per_added_dimension": ratio(attempted - baseline, delta),
            })
    for cell_id, cell in cell_map.items():
        if cell["status"] == "completed" and counts[cell_id] != cell["cover_count"]:
            raise ValueError(f"cover coverage mismatch for {cell_id}")
    return {
        "schema": "frobenius-stored-metrics-diagnostic-v1",
        "evidence_kind": "derived_from_stored_metrics_not_independent_verification",
        "claim_boundary": "No new experiment, rank recomputation, speedup, closure or status transition.",
        "assumptions": "Verified homogeneous rows, prime-order subgroup, nonidentity columns, no target-log column; U-1 is only an ambient ceiling.",
        "panel": {"planned_cells": len(cells), "completed_cells": sum(c["status"] == "completed" for c in cells),
                  "incomplete_cells": [dict(c) for c in cells if c["status"] != "completed"]},
        "presentation_count": len(rows),
        "diagnosis_counts": dict(sorted(Counter(r["diagnosis"] for r in rows).items())),
        "presentations": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if re.fullmatch(r"[0-9a-fA-F]{64}", args.expected_sha256) is None:
            raise ValueError("expected SHA-256 must contain 64 hex digits")
        raw = args.metrics.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != args.expected_sha256.lower():
            raise ValueError("source metrics SHA-256 mismatch")
        report = audit_metrics(json.loads(raw))
        report["source"] = {"path": str(args.metrics), "sha256": digest}
        encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
