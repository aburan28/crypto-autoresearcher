"""Supervised adapter for one already prepared graph arm.

The repository trial supervisor owns admission and the run directory. This
adapter never selects an arm, issues a seed, or approves an experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
WRAPPER = STUDY / "preparation/execute_graph_prepared.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("input", "prepared-manifest", "collector", "count-verifier", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--watchdog-seconds", type=int, default=1800)
    parser.add_argument("--memory-gib", type=int, default=4)
    args = parser.parse_args()
    if args.control == (args.admission is not None):
        parser.error("use --control alone or provide --admission for scientific mode")
    if args.watchdog_seconds < 1 or args.memory_gib < 1:
        parser.error("resource guards must be positive")
    out = args.out.resolve()
    if not out.is_dir() or any(out.iterdir()):
        parser.error("trial supervisor must provide an empty, existing --out directory")
    paths = {name: getattr(args, name.replace("-", "_")).resolve() for name in
             ("input", "prepared-manifest", "collector", "count-verifier")}
    if args.admission is not None:
        paths["admission"] = args.admission.resolve()
    prepared = json.loads(paths["prepared-manifest"].read_text())
    if prepared.get("input_sha256") != sha(paths["input"]):
        parser.error("prepared input digest differs")
    command = [sys.executable, str(WRAPPER), "--input", str(paths["input"]),
               "--manifest", str(paths["prepared-manifest"]),
               "--collector", str(paths["collector"]),
               "--count-verifier", str(paths["count-verifier"]),
               "--output", str(out / "attempt"),
               "--watchdog-seconds", str(args.watchdog_seconds),
               "--memory-gib", str(args.memory_gib)]
    command += ["--control"] if args.control else ["--admission", str(paths["admission"])]
    with (out / "driver.stdout").open("xb") as stdout, (out / "driver.stderr").open("xb") as stderr:
        process = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                 check=False)
    attempt = out / "attempt"
    receipt_path = attempt / "receipt.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.is_file() else None
    def phase_json(name: str) -> object | None:
        path = attempt / f"{name}.stdout"
        if not path.is_file() or not path.stat().st_size:
            return None
        try:
            return json.loads(path.read_text())
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
    result = {
        "schema": "ectd.graph-trial-result.v1",
        "status": receipt.get("status") if receipt else "missing_receipt",
        "mode": "implementation_control" if args.control else "scientific_trial",
        "prepared": {key: prepared[key] for key in ("stratum", "index", "arm", "stage", "target_count")},
        "digests": {name + "_sha256": sha(path) for name, path in paths.items()},
        "wrapper_sha256": sha(WRAPPER),
        "attempt_receipt_sha256": sha(receipt_path) if receipt else None,
        "input_check": phase_json("input_verify"),
        "rank_check": phase_json("rank_verify"),
    }
    write_once(out / "raw-result.json", result)
    write_once(out / "manifest.yaml", {
        "schema": "ectd.graph-trial-manifest.v1", "status": result["status"],
        "paths": {name: str(path) for name, path in paths.items()},
        "command": command, "subprocess_return_code": process.returncode,
        "raw_result_sha256": sha(out / "raw-result.json"),
        "attempt_receipt_sha256": result["attempt_receipt_sha256"],
        "driver_stdout_sha256": sha(out / "driver.stdout"),
        "driver_stderr_sha256": sha(out / "driver.stderr"),
    })
    expected = "completed_control" if args.control else "completed_unreviewed"
    return 0 if process.returncode == 0 and result["status"] == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
