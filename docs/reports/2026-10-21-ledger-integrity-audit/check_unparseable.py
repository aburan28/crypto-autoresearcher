#!/usr/bin/env python3
"""Classify dashboard parse failures against frozen schema supersessions."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo: Path, integrity_file: Path) -> dict:
    integrity = json.loads(integrity_file.read_text())
    require(integrity.get("unparseable_state") == "complete",
            "dashboard deep scan is incomplete")
    failures = integrity.get("unparseable")
    require(isinstance(failures, list), "unparseable list is absent")
    paths = [row["path"] for row in failures]
    require(len(paths) == len(set(paths)), "duplicate unparseable path")

    registry_file = repo / "tools/schema_supersession_registry.yaml"
    registry = yaml.safe_load(registry_file.read_text())
    require(registry.get("schema") == "schema-supersession-registry-v1",
            "unexpected supersession schema")
    replacements = {row["superseded_path"]: row
                    for row in registry["records"]}
    covered, uncovered = [], []
    for path in sorted(paths):
        record = replacements.get(path)
        if record is None:
            uncovered.append(path)
            continue
        source = repo / path
        target = repo / record["superseding_path"]
        require(source.is_file() and target.is_file(), f"missing source/replacement: {path}")
        require(sha256(source) == record["superseded_sha256"],
                f"source digest mismatch: {path}")
        require(sha256(target) == record["superseding_sha256"],
                f"replacement digest mismatch: {path}")
        require(isinstance(yaml.safe_load(target.read_text()), dict),
                f"replacement is not a YAML mapping: {target}")
        covered.append({"source": path, "replacement": record["superseding_path"]})
    require(len(covered) + len(uncovered) == len(paths), "classification missed a path")
    return {"integrity_sha256": sha256(integrity_file),
            "registry_sha256": sha256(registry_file),
            "unparseable_total": len(paths),
            "hash_verified_replacements": len(covered),
            "without_registered_replacement": len(uncovered),
            "covered": covered, "uncovered": uncovered}


if __name__ == "__main__":
    require(len(sys.argv) == 3, "usage: check_unparseable.py REPO INTEGRITY_JSON")
    print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2])), indent=2))
