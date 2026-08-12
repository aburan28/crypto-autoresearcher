#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import math
import os
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
STREAM_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-TARGET-STREAM-001" / "src" / "streaming_projective_shared_sign_locator.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STREAM = load("compressed_projective_stream_base", STREAM_SOURCE)
ORBIT = STREAM.ORBIT
PREFIX_FRACTION = 0.5
SELECTOR = os.environ.get("PREFIX_SELECTOR", "source-derived-diagonal-prefix")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_prefixes(a_size: int, b_size: int) -> list[tuple[int, int, int]]:
    """Select a source-only prefix subset; target values never enter this order."""
    full = ORBIT.ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    count = max(1, math.ceil(PREFIX_FRACTION * len(full)))
    if SELECTOR == "source-derived-diagonal-prefix":
        return full[:count]
    if SELECTOR == "interleaved-diagonal-prefix":
        return full[::2][:count]
    if SELECTOR == "parity-balanced-prefix":
        balanced = [prefix for prefix in full if sum(prefix) % 2 == 0]
        return balanced[:count]
    if SELECTOR == "source-hash-ranked-prefix":
        ranked = sorted(full, key=lambda prefix: hashlib.sha256(("prefix:" + ",".join(str(value) for value in prefix)).encode("ascii")).digest())
        return ranked[:count]
    raise ValueError(f"unknown source-only prefix selector: {SELECTOR}")


def locate(predicates: Any, target_index: int, skeleton: dict[str, Any], a_size: int, b_size: int, classes: list[dict[str, Any]], columns: list[int]) -> dict[str, Any]:
    rank = skeleton["rank"]
    if rank == 0 or not skeleton["inverse"]:
        return {"hits": [], "sampled_entries": 0, "predicted_mismatches": 0, "lift_queries": 0, "lift_false_quotient_zeros": 0, "reconstruction_ops": ORBIT.zero_ops(), "selected_prefix_count": 0, "full_prefix_count": a_size**3}
    prefixes = selected_prefixes(a_size, b_size)
    pivot_columns = skeleton["pivot_columns"]
    inverse = skeleton["inverse"]
    basis = skeleton["basis_rows"]
    reconstruction_ops = ORBIT.zero_ops()
    hits = []
    predicted_mismatches = 0
    sampled_entries = 0
    lift_queries = 0
    false_quotient_zeros = 0
    for prefix in prefixes:
        sampled = [predicates.value(target_index, prefix, column) for column in pivot_columns]
        coefficients = ORBIT.ADAPTIVE.SOURCE_AWARE.row_times_matrix(sampled, inverse, predicates.p)
        reconstruction_ops["field_multiplications"] += rank * rank
        reconstruction_ops["field_additions"] += rank * max(0, rank - 1)
        for column in columns:
            predicted = sum(coefficients[index] * basis[index][column] for index in range(rank)) % predicates.p
            actual = predicates.value(target_index, prefix, column)
            predicted_mismatches += int(predicted != actual)
            sampled_entries += 1
            reconstruction_ops["field_multiplications"] += rank
            reconstruction_ops["field_additions"] += max(0, rank - 1)
            if predicted != 0:
                continue
            members = [tuple(item) for item in classes[column]["members"]]
            for suffix in members:
                indices = prefix + suffix
                value = predicates.original_value(target_index, indices)
                lift_queries += 1
                if value == 0:
                    hits.append({"indices": list(indices), "a_index": indices[0], "suffix_class": column})
                else:
                    false_quotient_zeros += 1
    return {"hits": hits, "sampled_entries": sampled_entries, "predicted_mismatches": predicted_mismatches, "lift_queries": lift_queries, "lift_false_quotient_zeros": false_quotient_zeros, "reconstruction_ops": reconstruction_ops, "selected_prefix_count": len(prefixes), "full_prefix_count": a_size**3}


ORBIT.locate = locate
ORBIT.BASE.locate = locate


def run(relation_inputs: list[Path], fixture_path: Path, families: list[str], budget_labels: list[str]) -> dict[str, Any]:
    result = ORBIT.run(relation_inputs, fixture_path, families, budget_labels)
    for row in result.get("rows", []):
        for budget in row.get("budgets", []):
            dimensions = budget.get("dimensions", [])
            a_size = int(dimensions[0]) if dimensions else 0
            selected = max(1, math.ceil(PREFIX_FRACTION * a_size**3)) if a_size else 0
            budget["selected_prefix_count"] = selected
            budget["full_prefix_count"] = a_size**3
            budget["prefix_fraction"] = PREFIX_FRACTION
            for target in budget.get("target_records", []):
                target["selected_prefix_count"] = selected
                target["full_prefix_count"] = a_size**3
    result["protocol"] = "EXP-ECDLP-TT-PROJECTIVE-COMPRESSED-LOCATOR-001-locator-v1"
    result["source"]["producer_sha256"] = sha256_file(SCRIPT_PATH)
    result["source"]["stream_source_sha256"] = sha256_file(STREAM_SOURCE)
    result["config"].update({"selector": SELECTOR, "prefix_fraction": PREFIX_FRACTION, "target_dependent_selection": False, "target_cache_mode": "streaming-one-target-at-a-time"})
    result["summary"]["boundary"] = "Source-only half-prefix projective locator with exact full-prefix oracle comparison; no generic ECDLP or exponent claim."
    return result


for name in dir(STREAM):
    if not name.startswith("_") and name not in {"run"}:
        globals()[name] = getattr(STREAM, name)
