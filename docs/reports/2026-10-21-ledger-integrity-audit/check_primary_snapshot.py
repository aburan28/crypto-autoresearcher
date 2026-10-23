"""Compare the pinned nine-row UI snapshot with an archived primary JSONL.

Pass the JSONL extracted from the cryptanalysis commit named in the snapshot.
This checks source bytes and selected directly copied identity/measurement
fields; it does not replay any historical benchmark or scalar certificate.
"""

import argparse
import hashlib
import json
from pathlib import Path


RAW_SHA256 = "3886d486bf05ba476c00a67c9d7b20ed07250862273019a3b59195a22d60b973"
SNAPSHOT_SHA256 = "4cc3b31ab805b34d9f2d1103e574f8130a6902d09703d49337c467257568ae5e"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_jsonl", type=Path)
    args = parser.parse_args()
    snapshot = Path(__file__).resolve().parents[3] / "ui/benchmarks/cryptanalysis-primary.json"
    require(sha256(args.source_jsonl) == RAW_SHA256, "source JSONL hash differs from pin")
    require(sha256(snapshot) == SNAPSHOT_SHA256, "UI snapshot hash differs from pin")
    raw = [json.loads(line) for line in args.source_jsonl.read_text().splitlines()
           if line.strip()]
    source = json.loads(snapshot.read_text())
    rows = source["rows"]
    require(len(raw) == len(rows) == 9, "expected exactly nine source and UI rows")
    comparisons = 0
    for row, display in zip(raw, rows):
        fields = (
            (row["run_id"], display["run_id"]),
            (row["candidate_id"], display["candidate_id"]),
            (row["total_operations"], display["total_operations"]),
            (row["wall_ns"], display["wall_ns"]),
            (row["online"]["ic_online_ns"], display["ic_online_ns"]),
            (row["counts"]["targets_verified"], display["targets_verified"]),
        )
        for original, shown in fields:
            require(original == shown, "archived field differs from UI snapshot")
            comparisons += 1
    print(json.dumps({
        "source_sha256": sha256(args.source_jsonl),
        "snapshot_sha256": sha256(snapshot),
        "source_commit": source["source_commit"],
        "rows": len(rows),
        "field_comparisons": comparisons,
        "mismatches": 0,
        "scope": "archived bytes and direct fields only; no fresh performance replay",
    }, indent=2))


if __name__ == "__main__":
    main()
