#!/usr/bin/env python3
"""Export every prime-stream candidate slot with both public-rule decisions."""

import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREVIOUS = REPO / "research/nist_seed_selection_20261016"
STREAMS = ("prime239v3", "prime192v2", "P-224", "P-256", "P-384", "P-521")
EXPECTED_POSITIONS = 21753


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", default="modalfull2")
    args = parser.parse_args()
    campaign = HERE / "raw" / f"modal_campaign_{args.attempt}"
    source_path = campaign / "x9_summary.json"
    output = campaign / "candidate_acceptance.csv"
    manifest_path = campaign / "candidate_acceptance_manifest.json"
    if output.exists() or manifest_path.exists():
        raise FileExistsError("candidate export already exists")
    summary = json.loads(source_path.read_text())
    if (summary["scope"] != "complete exact near-prime X9 public-reference count for six distinct prime streams"
            or summary["candidate_positions"] != EXPECTED_POSITIONS):
        raise AssertionError("summary is not a complete six-stream count")

    by_stream = defaultdict(dict)
    candidate_path = PREVIOUS / "raw/candidates.jsonl"
    with candidate_path.open() as source:
        for line in source:
            row = json.loads(line)
            if row["target"] in STREAMS:
                key = row["index"]
                if key in by_stream[row["target"]]:
                    raise AssertionError("duplicate source candidate")
                by_stream[row["target"]][key] = row["seed"]
    anchors = defaultdict(lambda: defaultdict(list))
    for name, target in summary["named_targets"].items():
        anchors[target["representative"]][target["published_index"]].append(name)
    accepted = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for stream, mappings in summary["accepted_roots_by_stream"].items():
        for mapping, roots in mappings.items():
            for root in roots:
                accepted[stream][mapping][root["index"]].append(root["side"])
    skipped = {stream: {int(index) for index in entries}
               for stream, entries in summary["known_skips"].items()}

    rows_written = 0
    fieldnames = ("stream", "index", "seed", "published_anchor_names",
                  "reported_skipped_seed", "unmasked_eligible_roots",
                  "strict_x9_eligible_roots")
    with output.open("x", newline="") as sink:
        writer = csv.DictWriter(sink, fieldnames=fieldnames)
        writer.writeheader()
        for stream in STREAMS:
            indices = by_stream[stream]
            endpoint = max(anchors[stream])
            if set(indices) != set(range(1, endpoint + 1)):
                raise AssertionError(f"source stream has gaps: {stream}")
            for index in sorted(indices):
                names = anchors[stream].get(index, [])
                writer.writerow({
                    "stream": stream, "index": index, "seed": indices[index],
                    "published_anchor_names": ";".join(sorted(names)),
                    "reported_skipped_seed": int(index in skipped.get(stream, set())),
                    "unmasked_eligible_roots": ";".join(
                        sorted(accepted[stream]["unmasked"].get(index, []))),
                    "strict_x9_eligible_roots": ";".join(
                        sorted(accepted[stream]["strict_x9"].get(index, []))),
                })
                rows_written += 1
    if rows_written != EXPECTED_POSITIONS:
        raise AssertionError("export did not cover the full grid")
    for stream in STREAMS:
        if any(index not in by_stream[stream]
               for mapping in ("unmasked", "strict_x9")
               for index in accepted[stream][mapping]):
            raise AssertionError("accepted root outside export grid")
    manifest = {"status": "complete_derived_export", "command": sys.argv,
                "python": platform.python_version(), "rows": rows_written,
                "interpretation": "empty eligible-root cells mean failure of the declared public reference screen, not a known historical rejection",
                "script_sha256": digest(Path(__file__)),
                "summary_sha256": digest(source_path),
                "candidate_source_sha256": digest(candidate_path),
                "csv_sha256": digest(output), "csv_path": str(output.relative_to(REPO))}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "rows": rows_written,
                      "sha256": manifest["csv_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
