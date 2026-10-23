"""One fixed public P29 check-vertex control for the phased graph runner."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from prepare_graph_input import prepare

STUDY = Path(__file__).resolve().parents[1]
BASE_ROOT = b"B" * 32
TARGET_ROOT = b"T" * 32


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collector", type=Path, required=True)
    parser.add_argument("--count-verifier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-count", type=int, choices=(8, 128), default=8)
    parser.add_argument("--index", type=int, choices=(0, 8), default=8)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    arm = "low_x" if args.index == 0 else "graph_transport"
    payload, meta = prepare(STUDY / "walk-p29-2048-attempt2.jsonl", args.index,
                            arm, "discovery", BASE_ROOT, TARGET_ROOT, args.target_count)
    prepared = root / "prepared.txt"
    manifest = root / "manifest.json"
    prepared.write_bytes(payload)
    manifest.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    command = [sys.executable, str(STUDY / "preparation/execute_graph_prepared.py"),
               "--input", str(prepared), "--manifest", str(manifest),
               "--collector", str(args.collector), "--count-verifier", str(args.count_verifier),
               "--output", str(root / "attempt"), "--control", "--watchdog-seconds", "120",
               "--memory-gib", "2"]
    result = subprocess.run(command, capture_output=True, text=True)
    (root / "wrapper.stdout").write_text(result.stdout)
    (root / "wrapper.stderr").write_text(result.stderr)
    (root / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    if result.returncode:
        raise RuntimeError(f"graph control runner failed: {result.returncode}; see saved outputs")
    receipt = json.loads((root / "attempt/receipt.json").read_text())
    rank = json.loads((root / "attempt/rank_verify.stdout").read_text())
    checked = json.loads((root / "attempt/input_verify.stdout").read_text())
    if (receipt["status"] != "completed_control" or checked["status"] != "pass" or
            rank["status"] != "valid" or not rank["independent_ordered_count_match"] or
            rank["targets"] != args.target_count):
        raise AssertionError("fixed graph collector control did not verify")
    print(json.dumps({"status": "pass", "mode": receipt["mode"], "stratum": "P29",
                      "index": args.index, "arm": arm, "targets": rank["targets"],
                      "useful_targets": rank["useful_targets"],
                      "ordered_count_match": rank["independent_ordered_count_match"],
                      "input_sha256": hashlib.sha256(payload).hexdigest(),
                      "collector_sha256": receipt["bindings"]["collector_binary_sha256"],
                      "count_sha256": receipt["bindings"]["count_binary_sha256"],
                      "receipt_sha256": hashlib.sha256((root / "attempt/receipt.json").read_bytes()).hexdigest(),
                      "limit": "fixed public implementation control; outside discovery inference"}, sort_keys=True))


if __name__ == "__main__":
    main()
