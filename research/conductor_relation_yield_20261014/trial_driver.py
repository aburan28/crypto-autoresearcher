"""Adapt one sealed prepared arm to the repository trial supervisor.

The caller supplies an already admitted input and binaries. This adapter does
not issue seeds, choose an arm, or authorize a scientific trial.
"""
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


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input", "manifest", "admission", "collector", "count-verifier", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    output = args.out.resolve()
    if not output.is_dir():
        parser.error("the trial supervisor must create --out before launch")
    paths = {name: getattr(args, name.replace("-", "_")).resolve()
             for name in ("input", "manifest", "admission", "collector", "count-verifier")}
    prepared = json.loads(paths["manifest"].read_text())
    admission = json.loads(paths["admission"].read_text())
    if prepared.get("input_sha256") != digest(paths["input"]):
        parser.error("prepared input digest mismatch")
    for key, path in (("input_sha256", paths["input"]),
                      ("manifest_sha256", paths["manifest"]),
                      ("collector_sha256", paths["collector"]),
                      ("count_verify_sha256", paths["count-verifier"])):
        if admission.get(key) != digest(path):
            parser.error(f"admission {key} mismatch")
    command = [sys.executable, str(HERE / "execute_prepared.py"),
               "--input", str(paths["input"]), "--manifest", str(paths["manifest"]),
               "--admission", str(paths["admission"]),
               "--collector", str(paths["collector"]),
               "--count-verifier", str(paths["count-verifier"]),
               "--output", str(output / "attempt"),
               "--watchdog-seconds", "1800", "--memory-gib", "4"]
    if args.control:
        command.append("--control")
    process = subprocess.run(command, check=False)
    receipt_path = output / "attempt" / "receipt.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.is_file() else None
    verified_path = output / "attempt" / "verify.stdout"
    verified = json.loads(verified_path.read_text()) if verified_path.is_file() else None
    interval_path = output / "attempt" / "interval.stdout"
    interval = json.loads(interval_path.read_text()) if interval_path.is_file() else None
    result = {
        "schema": "arity3-trial-result/v1", "status": receipt.get("status") if receipt else "missing_receipt",
        "input_sha256": digest(paths["input"]), "manifest_sha256": digest(paths["manifest"]),
        "admission_sha256": digest(paths["admission"]),
        "collector_sha256": digest(paths["collector"]),
        "count_verify_sha256": digest(paths["count-verifier"]),
        "attempt_receipt_sha256": digest(receipt_path) if receipt else None,
        "verified": verified, "interval": interval,
    }
    manifest = {
        "schema": "arity3-trial-manifest/v1", "status": result["status"],
        "prepared_input": str(paths["input"]), "prepared_manifest": str(paths["manifest"]),
        "admission": str(paths["admission"]), "command": command,
        "subprocess_return_code": process.returncode,
        "raw_result_sha256": None,
        "attempt_receipt_sha256": result["attempt_receipt_sha256"],
    }
    write_json(output / "raw-result.json", result)
    manifest["raw_result_sha256"] = digest(output / "raw-result.json")
    write_json(output / "manifest.yaml", manifest)
    expected = "completed_control" if args.control else "completed_unreviewed"
    return 0 if process.returncode == 0 and result["status"] == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
