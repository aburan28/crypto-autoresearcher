#!/usr/bin/env python3
"""Independent verifier for RT-CTRL-1 telemetry files; imports no writer code."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def digest_json(value: dict) -> str:
    copy = dict(value)
    copy.pop("sha256", None)
    return hashlib.sha256(json.dumps(copy, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--expect-cause", choices=["controlled_sigterm", "hard_cap", "completed", "sigterm_grace_expired"], required=True)
    args = parser.parse_args()
    manifest_path = args.out / "target_manifest.json"
    receipt_path = args.out / "terminal_receipt.json"
    events_path = args.out / "events.jsonl"
    if not all(p.is_file() for p in (manifest_path, receipt_path, events_path)):
        return fail("manifest, event stream, or terminal receipt missing")
    manifest = json.loads(manifest_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    expected_manifest = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if receipt.get("target_manifest_sha256") != expected_manifest:
        return fail("manifest digest mismatch")
    if receipt.get("terminal_cause") != args.expect_cause:
        return fail("unexpected terminal cause")
    lines = [json.loads(line) for line in events_path.read_text().splitlines() if line]
    if not lines:
        return fail("empty event stream")
    previous = expected_manifest
    for event in lines:
        if event.get("previous_sha256") != previous:
            return fail("broken event chain")
        if event.get("sha256") != digest_json(event):
            return fail("event digest mismatch")
        previous = event["sha256"]
    # The receipt intentionally snapshots the chain before the receipt-written event.
    if receipt.get("last_event_sha256") not in {previous, lines[-2].get("sha256") if len(lines) > 1 else None}:
        return fail("receipt not connected to event chain")
    print("PASS: telemetry receipt, manifest, and hash chain verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
