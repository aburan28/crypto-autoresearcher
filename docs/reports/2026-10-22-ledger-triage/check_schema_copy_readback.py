"""Check the generated reader's three hash-bound, parseable schema copies."""

import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
TARGETS = {
    "experiments/EXP-ECDLP-daee4d/specification.yaml": "EXP-ECDLP-daee4d",
    "ledger/evidence/EV-QSP-2c78d3.yaml": "EV-QSP-2c78d3",
    "ledger/proposals/IDEA-20260920-b9f0c5.yaml": "IDEA-20260920-b9f0c5",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo, site):
    pairs = json.loads((HERE / "evidence/source-check.json").read_text())["pairs"]
    require({row["source"] for row in pairs} == TARGETS.keys(), "unexpected source pairs")
    rows = []
    for pair in pairs:
        source = pair["source"]
        record_id = TARGETS[source]
        detail = json.loads((site / "data/records" / f"{record_id}.json").read_text())
        original = json.loads((site / "data/sources" / f"{record_id}.json").read_text())
        copy = detail.get("supersession")
        require(detail["summary"]["path"] == source, f"canonical path changed: {record_id}")
        require(detail["verified"] is True and detail["parse_error"] is None,
                f"parseable original lost its validation state: {record_id}")
        require(original["path"] == source and
                original["raw"] == (repo / source).read_text(encoding="utf-8", errors="replace"),
                f"source payload differs from original: {record_id}")
        require(isinstance(copy, dict) and copy["path"] == pair["replacement"],
                f"registered copy absent: {record_id}")
        require(copy["source_sha256"] == pair["source_sha256"] == digest(repo / source)
                and copy["replacement_sha256"] == pair["replacement_sha256"]
                == digest(repo / pair["replacement"]),
                f"copy hash differs: {record_id}")
        require(any(isinstance(body, dict) and body.get("id") == record_id
                    for body in copy["body"].values()), f"copy ID differs: {record_id}")
        rows.append({"record_id": record_id, "original": source,
                     "replacement": pair["replacement"]})
    return {"status": "pass", "parseable_originals_preserved": len(rows),
            "hash_matched_schema_copies_visible": len(rows), "records": rows}


if __name__ == "__main__":
    require(len(sys.argv) == 3, "usage: check_schema_copy_readback.py REPO SITE")
    print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2])), indent=2))
