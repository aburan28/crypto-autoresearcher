"""Independently replay a sealed arm for the repository trial supervisor."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--prepared-manifest", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    prepared = json.loads(args.prepared_manifest.read_text())
    admission = json.loads(args.admission.read_text())
    result = json.loads((run_dir / "raw-result.json").read_text())
    manifest = json.loads((run_dir / "manifest.yaml").read_text())
    receipt = json.loads((run_dir / "attempt" / "receipt.json").read_text())
    expected = "completed_control" if args.control else "completed_unreviewed"
    if (result["status"] != expected or receipt["status"] != result["status"]
            or manifest["status"] != result["status"]):
        raise ValueError("trial did not complete")
    bound = {"input_sha256": digest(args.input),
             "manifest_sha256": digest(args.prepared_manifest),
             "admission_sha256": digest(args.admission)}
    if any(result.get(key) != value for key, value in bound.items()):
        raise ValueError("trial result digest mismatch")
    if prepared["input_sha256"] != bound["input_sha256"]:
        raise ValueError("prepared input digest mismatch")
    if admission.get("input_sha256") != bound["input_sha256"] or admission.get("manifest_sha256") != bound["manifest_sha256"]:
        raise ValueError("admission input digest mismatch")
    if (manifest["raw_result_sha256"] != digest(run_dir / "raw-result.json")
            or result["attempt_receipt_sha256"] != digest(run_dir / "attempt" / "receipt.json")):
        raise ValueError("trial artifact digest mismatch")
    command = [sys.executable, str(HERE / "verify_collector.py"), str(args.input),
               str(run_dir / "attempt" / "collector.stdout"),
               "--gx", str(prepared["generator"][0]), "--gy", str(prepared["generator"][1]),
               "--qx", str(prepared["Q"][0]), "--qy", str(prepared["Q"][1]),
               "--count-output", str(run_dir / "attempt" / "count.stdout")]
    replay = subprocess.run(command, check=True, capture_output=True, text=True)
    independent = json.loads(replay.stdout)
    if independent != result["verified"] or independent.get("status") != "valid":
        raise ValueError("independent point/row replay disagrees")
    if not args.control:
        interval = subprocess.run([sys.executable, str(HERE / "exact_interval.py"),
                                   "--population", str(prepared["r"] - 1),
                                   "--draws", str(prepared["target_count"]),
                                   "--observed", str(independent["useful_targets"])],
                                  check=True, capture_output=True, text=True)
        if json.loads(interval.stdout) != result["interval"]:
            raise ValueError("exact interval replay disagrees")
    elif result["interval"] is not None:
        raise ValueError("control unexpectedly has scientific interval")
    print(json.dumps({"status": "valid", "useful_targets": independent["useful_targets"],
                      "rank_increments": independent["rank_increments"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
