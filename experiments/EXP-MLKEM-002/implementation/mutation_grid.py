#!/usr/bin/env python3
"""Mutation-grid helpers and coverage aggregation for EXP-MLKEM-002."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_grid(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def silent_sets(grid: dict[str, Any]) -> dict[str, list[int]]:
    out = {}
    for row in grid.get("parameter_results", []):
        out[row["parameter_set"]] = list(row.get("silent_byte_set", []))
    return out


def disagreements(
    scalar: dict[str, list[int]], optimized: dict[str, list[int]]
) -> dict[str, Any]:
    result = {}
    for ps in sorted(set(scalar) | set(optimized)):
        s = set(scalar.get(ps, []))
        o = set(optimized.get(ps, []))
        result[ps] = {
            "scalar_silent": sorted(s),
            "optimized_silent": sorted(o),
            "only_optimized": sorted(o - s),
            "only_scalar": sorted(s - o),
            "disagreement_count": len(s.symmetric_difference(o)),
        }
    return result


def format_silent_csv(sets: dict[str, list[int]]) -> str:
    parts = []
    for ps, idxs in sets.items():
        if idxs:
            parts.append(ps + ":" + ",".join(str(i) for i in idxs))
    return ";".join(parts)


def aggregate_coverage(paths: dict[str, Path]) -> dict[str, Any]:
    maps = {}
    for build_id, path in paths.items():
        if not path.exists():
            maps[build_id] = {"status": "missing", "path": str(path)}
            continue
        grid = load_grid(path)
        maps[build_id] = {
            "backend": grid.get("backend"),
            "resolved_commit": grid.get("resolved_commit"),
            "silent_sets": silent_sets(grid),
            "parameter_results": grid.get("parameter_results", []),
        }
    return maps
