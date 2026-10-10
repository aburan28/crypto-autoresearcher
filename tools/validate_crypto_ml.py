#!/usr/bin/env python3
"""Validate crypto-ml-v1 JSON experiments without external dependencies."""
import json
import sys
from pathlib import Path

FAMILIES = {"block_cipher", "stream_cipher", "hash", "kem", "signature", "elliptic_curve", "other"}
TASKS = {"binary_distinguisher", "multiclass_distinguisher", "regression", "anomaly_detection"}
REQUIRED = ("experiment", "primitive", "sampling", "features", "labels", "splits", "evaluation", "provenance")

def validate(doc):
    errors = []
    if not isinstance(doc, dict):
        return ["root must be an object"]
    if doc.get("schema_version") != "crypto-ml-v1":
        errors.append("unsupported schema_version")
    for name in REQUIRED:
        if name not in doc:
            errors.append(f"missing {name}")
    if errors:
        return errors
    exp, prim, sample, splits = (doc[k] for k in ("experiment", "primitive", "sampling", "splits"))
    if not all(isinstance(x, dict) for x in (exp, prim, sample, splits)):
        return ["experiment, primitive, sampling and splits must be objects"]
    if exp.get("task") not in TASKS: errors.append("invalid task")
    if prim.get("family") not in FAMILIES: errors.append("invalid primitive family")
    if not isinstance(doc["features"], list) or not doc["features"] or not all(isinstance(f, str) and f for f in doc["features"]):
        errors.append("features must be a nonempty string array")
    if len(doc["features"]) != len(set(map(str, doc["features"]))): errors.append("duplicate features")
    if not isinstance(sample.get("independent_units"), int) or sample["independent_units"] < 2:
        errors.append("independent_units must be >=2")
    if not isinstance(sample.get("samples_per_unit"), int) or sample["samples_per_unit"] < 1:
        errors.append("samples_per_unit must be >=1")
    try:
        ratios = [splits[k] for k in ("train", "validation", "test")]
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and 0 < x < 1 for x in ratios) or abs(sum(ratios) - 1) > 1e-9:
            errors.append("splits must be positive and sum to 1")
    except KeyError:
        errors.append("missing split ratio")
    if not splits.get("grouping"): errors.append("split grouping is required")
    for key, fields in {"provenance": ("implementation_commit", "generator_version", "seed_manifest"), "labels": ("target",), "evaluation": ("metrics", "controls")}.items():
        if not isinstance(doc[key], dict) or any(not doc[key].get(f) for f in fields):
            errors.append(f"incomplete {key}")
    return errors

def main():
    if len(sys.argv) != 2:
        print("usage: python3 tools/validate_crypto_ml.py EXPERIMENT.json", file=sys.stderr)
        return 2
    try:
        errors = validate(json.loads(Path(sys.argv[1]).read_text()))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for error in errors: print(error, file=sys.stderr)
    if not errors: print("crypto-ml-v1: valid")
    return bool(errors)

if __name__ == "__main__":
    sys.exit(main())
