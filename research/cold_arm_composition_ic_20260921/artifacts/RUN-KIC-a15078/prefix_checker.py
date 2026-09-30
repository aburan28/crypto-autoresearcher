#!/usr/bin/env python3
"""Relation-generation prefix checker for RUN-KIC-56c897."""

from __future__ import annotations

import hashlib
import json
from typing import Any


class PrefixError(RuntimeError): pass


def relation_rows(data: bytes) -> list[dict[str, Any]]:
    rows = []
    for line in data.decode().splitlines():
        if not line.strip(): continue
        value = json.loads(line)
        if value.get("kind") == "relation_rank_receipt": rows.append(value)
    return sorted(rows, key=lambda row: row["accepted_relation"])


def canonical(row: dict[str, Any]) -> dict[str, Any]:
    keys = ("accepted_relation", "trial", "coefficient_a", "coefficient_b", "target_point_key",
            "factor_point_indices", "orbit_labels", "sparse_row", "relation_hash", "verified_group_identity")
    missing = [key for key in keys if key not in row]
    if missing: raise PrefixError(f"relation receipt missing mandatory prefix fields: {missing}")
    return {key: row[key] for key in keys}


def check(baseline_data: bytes, candidate_data: bytes) -> dict[str, Any]:
    baseline, candidate = relation_rows(baseline_data), relation_rows(candidate_data)
    if not candidate: raise PrefixError("candidate relation prefix is empty")
    if len(baseline) < len(candidate): raise PrefixError("baseline is shorter than candidate prefix")
    left, right = [canonical(row) for row in baseline[:len(candidate)]], [canonical(row) for row in candidate]
    if left != right:
        mismatch = next(index for index, pair in enumerate(zip(left, right), 1) if pair[0] != pair[1])
        raise PrefixError(f"relation prefix mismatch at accepted relation {mismatch}")
    encoded = json.dumps(right, sort_keys=True, separators=(",", ":")).encode()
    return {"valid": True, "candidate_prefix_rows": len(candidate), "baseline_rows": len(baseline),
            "prefix_sha256": hashlib.sha256(encoded).hexdigest()}


if __name__ == "__main__": raise SystemExit("library module")
