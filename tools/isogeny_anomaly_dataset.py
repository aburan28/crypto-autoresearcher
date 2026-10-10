#!/usr/bin/env python3
"""Validate and assemble reproducible isogeny anomaly datasets (stdlib only)."""
import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = ("curve_id", "family", "field", "order", "features", "provenance")
FAMILIES = {"binary", "prime", "extension"}

def validate(record):
    missing = [k for k in REQUIRED if k not in record]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if record["family"] not in FAMILIES:
        raise ValueError("invalid family")
    if not isinstance(record["features"], dict):
        raise ValueError("features must be an object")
    if not isinstance(record["provenance"], dict):
        raise ValueError("provenance must be an object")
    for key in ("revision", "generator", "parameters"):
        if key not in record["provenance"]:
            raise ValueError(f"missing provenance.{key}")
    if not isinstance(record["curve_id"], str) or not record["curve_id"]:
        raise ValueError("invalid curve_id")
    return record

def load_jsonl(path):
    for line_number, line in enumerate(Path(path).read_text().splitlines(), 1):
        if line.strip():
            try:
                yield validate(json.loads(line))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc

def assemble(paths, output):
    records = {}
    for path in paths:
        for record in load_jsonl(path):
            identity = record["curve_id"]
            canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
            if identity in records and records[identity] != canonical:
                raise ValueError(f"conflicting curve_id: {identity}")
            records[identity] = canonical
    data = "".join(records[k] + "\n" for k in sorted(records))
    Path(output).write_text(data)
    return {"records": len(records), "sha256": hashlib.sha256(data.encode()).hexdigest()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(assemble(args.inputs, args.output), indent=2))

if __name__ == "__main__":
    main()
