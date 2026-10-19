#!/usr/bin/env python3
"""Freeze exact X9-reference work after the family campaign is validated."""

import hashlib
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STREAMS = (
    ("P-521", 1136, 10, 1024),
    ("P-384", 2688, 50, 512),
    ("P-224", 7026, 200, 512),
    ("P-256", 1842, 100, 512),
    ("prime239v3", 3048, 100, 512),
    ("prime192v2", 6013, 200, 512),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / "raw" / "x9_campaign" / "plan.json"
    if output.exists():
        raise FileExistsError(output)
    family_path = ROOT / "raw" / "family_campaign" / "family_summary.json"
    family = json.loads(family_path.read_text())
    if family["scope"] != "complete published cofactor-one family profile on all ten named prime targets":
        raise ArithmeticError("family campaign not complete")
    controls_path = ROOT / "raw" / "x9_evaluator_controls_v2.json"
    controls = json.loads(controls_path.read_text())
    if not controls["all_passed"] or controls["evaluator_sha256"] != digest(ROOT / "evaluate_x9_remaining.py"):
        raise ArithmeticError("X9 evaluator controls not passed on frozen script")
    per_stream = [[{"target": name, "start": start, "end": min(start + width - 1, end),
                    "stack_mib": stack} for start in range(1, end + 1, width)]
                  for name, end, width, stack in STREAMS]
    shards = []
    for offset in range(max(len(stream) for stream in per_stream)):
        shards.extend(stream[offset] for stream in per_stream if offset < len(stream))
    plan = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "max_workers": 1, "per_shard_watchdog_seconds": 7200,
            "candidate_sha256": digest(ROOT / "raw" / "candidates.jsonl"),
            "family_plan_sha256": digest(ROOT / "raw" / "family_campaign" / "plan.json"),
            "family_summary_sha256": digest(family_path),
            "evaluator_sha256": digest(ROOT / "evaluate_x9_remaining.py"),
            "evaluator_controls_sha256": digest(controls_path),
            "shards": shards}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"shards": len(shards), "max_workers": 1,
                      "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
