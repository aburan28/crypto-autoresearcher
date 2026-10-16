#!/usr/bin/env python3
"""Summarize the complete deterministic seed and coefficient screening stage."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    target_rows = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    source = ROOT / "raw" / "candidates.jsonl"
    counts = defaultdict(Counter)
    first_eligible = defaultdict(list)
    anchors = {}
    rows = 0
    with source.open() as stream:
        for line in stream:
            row = json.loads(line)
            name = row["target"]
            target = target_rows[name]
            rows += 1
            counts[name]["rows"] += 1
            if row["index"] < target["candidate_index"]:
                counts[name]["earlier"] += 1
            else:
                anchors[name] = row["seed"] == target["published_seed"]
            if row["kind"] == "prime":
                for method, variant in row["variants"].items():
                    counts[name][f"{method}:{variant['reason']}"] += 1
                primary = row["variants"]["nist_fips_186_2"]
                strict = row["variants"]["ansi_x9_62_1998"]
                counts[name]["strict_x9_same_c" if strict["c"] == primary["c"] else "strict_x9_different_c"] += 1
                if row["index"] == target["candidate_index"]:
                    anchors[name] = anchors[name] and int(target["published_b"]) in [int(x, 16) for x in primary["b_roots"]]
                    anchors[name + ":strict_x9_matches_coefficient"] = int(target["published_b"]) in [int(x, 16) for x in strict["b_roots"]]
            else:
                counts[name][row["reason"]] += 1
                if row["index"] == target["candidate_index"]:
                    anchors[name] = anchors[name] and int(row["b"], 16) == int(target["published_b"])
                    anchors[name + ":normal_basis"] = row["b_normal"]
    if rows != 31945 or len([k for k in anchors if ":" not in k]) != 14 or not all(
        value for key, value in anchors.items() if ":" not in key
    ):
        raise ArithmeticError("enumeration or published coefficient anchor failed")
    result = {
        "candidate_jsonl_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "total_target_candidate_pairs": rows,
        "total_earlier_target_candidate_pairs": sum(c["earlier"] for c in counts.values()),
        "counts_by_target": {name: dict(counts[name]) for name in target_rows},
        "anchors": anchors,
        "status": "seed_and_coefficient_screen_only; point-order acceptance requires exact counts",
    }
    output = ROOT / "raw" / "screening_summary.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"rows": rows, "output": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
