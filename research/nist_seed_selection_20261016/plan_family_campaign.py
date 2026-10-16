#!/usr/bin/env python3
"""Freeze the exhaustive cofactor-one prime-stream shard plan."""

import hashlib
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STREAMS = (
    ("P-521", 1136, 80, 1024),
    ("P-384", 2688, 150, 512),
    ("P-224", 7026, 500, 512),
    ("P-256", 1842, 300, 512),
    ("prime239v3", 3048, 300, 512),
    ("prime192v2", 6013, 500, 512),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / "raw" / "family_campaign" / "plan.json"
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    per_stream = []
    for name, end, width, stack in STREAMS:
        per_stream.append([{"target": name, "start": start, "end": min(start + width - 1, end),
                            "stack_mib": stack} for start in range(1, end + 1, width)])
    shards = []
    for offset in range(max(len(stream) for stream in per_stream)):
        shards.extend(stream[offset] for stream in per_stream if offset < len(stream))
    plan = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "max_workers": 8, "per_shard_watchdog_seconds": 7200,
            "candidate_sha256": digest(ROOT / "raw" / "candidates.jsonl"),
            "torsion_screen_sha256": digest(ROOT / "raw" / "prime_3torsion_screen.jsonl"),
            "evaluator_sha256": digest(ROOT / "evaluate_family_fast.py"),
            "fast_controls_sha256": digest(ROOT / "raw" / "fast_evaluator_controls.json"),
            "shards": shards}
    output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"shards": len(shards), "max_workers": 8,
                      "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
