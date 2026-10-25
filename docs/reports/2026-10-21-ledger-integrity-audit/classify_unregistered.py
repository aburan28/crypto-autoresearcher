#!/usr/bin/env python3
"""Source-bind the fifteen malformed originals without schema replacements."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml


def main(repo: Path, classification: Path) -> dict:
    sys.path.insert(0, str(repo.resolve()))
    from tools import validate_ledger

    sources = json.loads(classification.read_text())["uncovered"]
    if len(sources) != 15 or len(sources) != len(set(sources)):
        raise ValueError("unexpected uncovered archive inventory")
    rows = []
    for source in sources:
        raw = (repo / source).read_bytes()
        try:
            yaml.safe_load(raw.decode("utf-8"))
        except yaml.YAMLError as error:
            mark = getattr(error, "problem_mark", None)
            rows.append({
                "source": source,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "parser_error": type(error).__name__,
                "line": mark.line + 1 if mark else None,
                "column": mark.column + 1 if mark else None,
                "problem": str(getattr(error, "problem", error)).splitlines()[0],
                "current_registry_kind":
                    validate_ledger._schema_supersession_kind_for_path(source),
            })
        else:
            raise ValueError(f"uncovered source now parses: {source}")
    if any(row["current_registry_kind"] is not None for row in rows):
        raise ValueError("an uncovered path now has a schema registry route")
    return {"status": "pass", "pyyaml_version": yaml.__version__,
            "unregistered_unparseable": len(rows),
            "current_schema_registry_routes": 0,
            "records": rows}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: classify_unregistered.py REPO CLASSIFICATION")
    print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2])), indent=2))
