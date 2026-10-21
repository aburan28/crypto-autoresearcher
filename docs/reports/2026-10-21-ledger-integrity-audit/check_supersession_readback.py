#!/usr/bin/env python3
"""Check generated detail payloads for the nine archived parse failures."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo: Path, site: Path, classification: Path) -> dict:
    classified = json.loads(classification.read_text())
    covered = classified["covered"]
    require(len(covered) == 9, "unexpected registered parse-failure count")
    checked = []
    for row in covered:
        source_path = row["source"]
        replacement_path = row["replacement"]
        record_id = Path(source_path).stem
        detail = json.loads((site / "data/records" / f"{record_id}.json").read_text())
        original = json.loads((site / "data/sources" / f"{record_id}.json").read_text())
        copy = detail.get("supersession")
        require(detail["summary"]["path"] == source_path,
                f"canonical path changed: {record_id}")
        require(detail["verified"] is False and bool(detail["parse_error"])
                and detail["body"] is None, f"original parse warning hidden: {record_id}")
        require(original["path"] == source_path and
                original["raw"] == (repo / source_path).read_text(encoding="utf-8", errors="replace"),
                f"original source changed in payload: {record_id}")
        require(isinstance(copy, dict) and copy["path"] == replacement_path,
                f"registered copy missing: {record_id}")
        require(copy["source_sha256"] == digest(repo / source_path) and
                copy["replacement_sha256"] == digest(repo / replacement_path),
                f"readback digest mismatch: {record_id}")
        body = copy["body"]
        require(isinstance(body, dict) and any(
            isinstance(value, dict) and value.get("id") == record_id
            for value in body.values()), f"replacement record ID mismatch: {record_id}")
        checked.append({"id": record_id, "source": source_path,
                        "replacement": replacement_path})
    return {"status": "pass", "registered_copies_shown": len(checked),
            "original_parse_warnings_preserved": len(checked),
            "source_payloads_exact": len(checked), "records": checked}


if __name__ == "__main__":
    require(len(sys.argv) == 4, "usage: check_supersession_readback.py REPO SITE CLASSIFICATION")
    print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])), indent=2))
