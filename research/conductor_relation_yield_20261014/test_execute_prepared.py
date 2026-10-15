"""Write-once small-group control of the bounded execution component."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from test_collector import G, R, encode_input, first_signed_base, mul

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--collector", type=Path, required=True)
    parser.add_argument("--count-verifier", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=False)
    q = mul(7, G)
    targets = [(index, (scalar - 7) % R, 1, mul(scalar, G)) for index, scalar in enumerate(range(1, R))]
    prepared = encode_input(first_signed_base(3), targets).encode()
    input_path = root / "input.txt"
    input_path.write_bytes(prepared)
    manifest_path = root / "input.manifest.json"
    manifest_path.write_text(json.dumps({
        "schema": "arity3-prepared-input-control/v1", "endpoint": "F17-control", "arm": "native",
        "p": 17, "r": R, "target_count": len(targets),
        "protocol_conformant_target_count": False,
        "generator": G, "Q": q,
        "input_sha256": hashlib.sha256(prepared).hexdigest(),
    }, indent=2, sort_keys=True) + "\n")
    command = [sys.executable, str(HERE / "execute_prepared.py"), "--control",
               "--input", str(input_path), "--manifest", str(manifest_path),
               "--collector", str(args.collector.resolve()),
               "--count-verifier", str(args.count_verifier.resolve()),
               "--output", str(root / "attempt"), "--watchdog-seconds", "60",
               "--memory-gib", "1"]
    process = subprocess.run(command, capture_output=True, text=True)
    (root / "wrapper.stdout").write_text(process.stdout)
    (root / "wrapper.stderr").write_text(process.stderr)
    (root / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    assert process.returncode == 0, process.stderr
    receipt = json.loads((root / "attempt" / "receipt.json").read_text())
    assert receipt["status"] == "completed_control"
    assert receipt["execute_sha256"] == hashlib.sha256((HERE / "execute_prepared.py").read_bytes()).hexdigest()
    assert [phase["phase"] for phase in receipt["phases"]] == ["collector", "count", "verify"]
    assert all(phase["status"] == "completed" for phase in receipt["phases"])
    checked = json.loads((root / "attempt" / "verify.stdout").read_text())
    assert checked["independent_ordered_count_match"] is True
    assert checked["targets"] == R - 1
    print("bounded execution control: 18 targets, collector/count/verifier, immutable attempt PASS")


if __name__ == "__main__":
    main()
