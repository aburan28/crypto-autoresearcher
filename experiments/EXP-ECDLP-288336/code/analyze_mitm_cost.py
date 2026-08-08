#!/usr/bin/env python3
"""Recompute charged MITM-cost metrics from a frozen source run.

This is deliberately a pure reanalysis: it never reruns the source experiment,
never edits source artifacts, and treats any provenance/control mismatch as an
invalid run rather than as mathematical evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SPEC = ROOT / "experiments/EXP-ECDLP-288336/specification.yaml"
SOURCE = {
    ROOT / "experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py":
        "64d682e56e28472987ebd319f6250a09620c566ab7a881701d53acce3300a540",
    ROOT / "experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/raw-results.json":
        "6e2d126166b0a6f6ee25c462e121c247b66f571e6e6ffc107e751602ee5ed978",
    ROOT / "experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/analysis.yaml":
        "1f51fd95f5bdf87e3c4972ed612786ae9164f358aaebe5d5cb0d33b704083211",
    ROOT / "experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/manifest.yaml":
        "20f758233b5381c3ce8497a6231eb923dd637787d64a0c715c55a2d6ec7f32d8",
}
RAW = ROOT / "experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/raw-results.json"
OUT = Path(os.environ.get("ECDLP_COST_OUT", ROOT / "experiments/EXP-ECDLP-288336/runs/RUN-ECDLP-288336-001/raw-result.json"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def finite(x):
    return x is not None and math.isfinite(float(x))


def main() -> int:
    t0 = time.perf_counter()
    validity_errors = []
    source_hashes = {}
    for path, expected in SOURCE.items():
        actual = sha256(path) if path.exists() else None
        source_hashes[str(path.relative_to(ROOT))] = {"expected": expected, "actual": actual, "match": actual == expected}
        if actual != expected:
            validity_errors.append(f"source hash mismatch: {path}")

    if not RAW.exists():
        validity_errors.append(f"missing source raw result: {RAW}")
        raw = {}
    else:
        raw = json.loads(RAW.read_text())

    cells = raw.get("cells", [])
    if len(cells) != 40:
        validity_errors.append(f"expected 40 cells, found {len(cells)}")

    rows = []
    seen = set()
    for cell in cells:
        cell_id = cell.get("cell_id")
        if cell_id in seen:
            validity_errors.append(f"duplicate cell: {cell_id}")
        seen.add(cell_id)
        arms = cell.get("arms", {})
        if set(arms) != {"A", "B", "C"}:
            validity_errors.append(f"arm set mismatch in {cell_id}: {sorted(arms)}")
            continue
        if not cell.get("all_controls_pass", False):
            validity_errors.append(f"source controls failed in {cell_id}")
        a, b, c = arms["A"], arms["B"], arms["C"]
        fsize = int(cell["factor_base_size"])
        expected_a = 2 * fsize ** 3
        expected_b = fsize ** 2 + 2 * int(b["candidates_verified"])
        expected_c = fsize ** 2 + 2 * int(c["candidates_verified"])
        if int(a["field_operations"]) != expected_a:
            validity_errors.append(f"Arm A arithmetic mismatch in {cell_id}")
        if int(b["field_operations"]) != expected_b:
            validity_errors.append(f"Arm B arithmetic mismatch in {cell_id}")
        if int(c["field_operations"]) != expected_c:
            validity_errors.append(f"Arm C arithmetic mismatch in {cell_id}")
        for arm_name, arm in (("A", a), ("B", b), ("C", c)):
            if int(arm.get("relations_found", -1)) < 0:
                validity_errors.append(f"negative relation count in {cell_id}/{arm_name}")
        if a["relations_found"] != b["relations_found"]:
            validity_errors.append(f"A/B relation mismatch in {cell_id}")
        right_pairs = int(b["right_half_pairs"])
        if right_pairs != fsize ** 2 or int(c["right_half_pairs"]) != right_pairs:
            validity_errors.append(f"right-half cardinality mismatch in {cell_id}")
        if not c.get("prng_collision_free", False):
            validity_errors.append(f"random-query collision control failed in {cell_id}")

        a_ops, b_ops, c_ops = map(lambda z: float(z["field_operations"]), (a, b, c))
        b_candidates = float(b["candidates_verified"])
        c_candidates = float(c["candidates_verified"])
        rows.append({
            "cell_id": cell_id,
            "p": int(cell["p"]),
            "b": float(cell["b"]),
            "seed": int(cell["seed"]),
            "factor_base_size": fsize,
            "relations_A": int(a["relations_found"]),
            "relations_B": int(b["relations_found"]),
            "relations_C": int(c["relations_found"]),
            "field_operations_A": int(a_ops),
            "field_operations_B": int(b_ops),
            "field_operations_C": int(c_ops),
            "field_operations_B_over_A": b_ops / a_ops,
            "field_operations_C_over_A": c_ops / a_ops,
            "candidates_B": int(b_candidates),
            "candidates_C": int(c_candidates),
            "candidates_B_over_C": (b_candidates / c_candidates) if c_candidates else None,
            "candidates_B_over_right_pairs": b_candidates / right_pairs,
            "candidates_C_over_right_pairs": c_candidates / right_pairs,
            "cost_per_relation_A": (a_ops / a["relations_found"]) if a["relations_found"] else None,
            "cost_per_relation_B": (b_ops / b["relations_found"]) if b["relations_found"] else None,
            "cost_per_relation_C": (c_ops / c["relations_found"]) if c["relations_found"] else None,
            "relation_count_A_minus_B": int(a["relations_found"]) - int(b["relations_found"]),
            "source_controls_pass": bool(cell.get("all_controls_pass", False)),
        })

    by_group = defaultdict(list)
    for row in rows:
        by_group[(row["p"], row["b"])].append(row)

    group_summary = []
    for (p, b), group in sorted(by_group.items()):
        ratios = [r["field_operations_B_over_A"] for r in group]
        c_ratios = [r["field_operations_C_over_A"] for r in group]
        bc = [r["candidates_B_over_C"] for r in group if finite(r["candidates_B_over_C"])]
        group_summary.append({
            "p": p,
            "b": b,
            "n_seeds": len(group),
            "mean_B_over_A": mean(ratios),
            "min_B_over_A": min(ratios),
            "max_B_over_A": max(ratios),
            "mean_C_over_A": mean(c_ratios),
            "mean_B_over_C_candidates_nonzero_C": mean(bc),
            "all_AB_relation_differences": [r["relation_count_A_minus_B"] for r in group],
        })

    valid = not validity_errors and len(rows) == 40
    b_over_a = [r["field_operations_B_over_A"] for r in rows]
    c_over_a = [r["field_operations_C_over_A"] for r in rows]
    bc_candidates = [r["candidates_B_over_C"] for r in rows if finite(r["candidates_B_over_C"])]
    result = {
        "experiment_id": "EXP-ECDLP-288336",
        "run_id": "RUN-ECDLP-288336-001",
        "source_experiment_id": "EXP-SEMAEV-f48dd1",
        "source_run_id": "RUN-SEMAEV-f48dd1-grid",
        "valid": valid,
        "validity_errors": validity_errors,
        "source_hashes": source_hashes,
        "cell_count": len(rows),
        "arm_record_count": len(rows) * 3,
        "control_pass_count": sum(1 for r in rows if r["source_controls_pass"]),
        "summary": {
            "all_source_hashes_match": all(v["match"] for v in source_hashes.values()),
            "all_controls_pass": all(r["source_controls_pass"] for r in rows),
            "all_arithmetic_identities_pass": not any("arithmetic mismatch" in e for e in validity_errors),
            "all_A_B_relation_counts_equal": all(r["relation_count_A_minus_B"] == 0 for r in rows),
            "mean_field_operations_B_over_A": mean(b_over_a),
            "min_field_operations_B_over_A": min(b_over_a) if b_over_a else None,
            "max_field_operations_B_over_A": max(b_over_a) if b_over_a else None,
            "mean_field_operations_C_over_A": mean(c_over_a),
            "mean_candidates_B_over_C_nonzero_C": mean(bc_candidates),
            "oracle_candidate_ratio_nonzero_count": len(bc_candidates),
            "oracle_candidate_ratio_direction": "higher_than_random" if bc_candidates and mean(bc_candidates) > 1 else "not_higher_or_undefined",
            "statistical_test": "not_applicable_deterministic_cost_identity",
            "claim_ceiling": "toy scoped implementation cost only",
        },
        "groups": group_summary,
        "cells": rows,
        "wall_clock_seconds": round(time.perf_counter() - t0, 6),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "valid": valid,
        "cell_count": len(rows),
        "mean_B_over_A": result["summary"]["mean_field_operations_B_over_A"],
        "mean_C_over_A": result["summary"]["mean_field_operations_C_over_A"],
        "mean_B_over_C_candidates_nonzero_C": result["summary"]["mean_candidates_B_over_C_nonzero_C"],
        "all_A_B_relation_counts_equal": result["summary"]["all_A_B_relation_counts_equal"],
        "errors": validity_errors,
    }, sort_keys=True))
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
