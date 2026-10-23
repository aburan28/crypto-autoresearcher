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
MATERIALIZER = STUDY / "graph_input_schedule_20261023/materialize.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--arm-key")
    parser.add_argument("--prepared-manifest", type=Path)
    for name in ("collector", "count-verifier", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--base-root-file", type=Path)
    parser.add_argument("--target-root-file", type=Path)
    parser.add_argument("--verifier-root-file", type=Path)
    parser.add_argument("--commitment", type=Path)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--watchdog-seconds", type=int, default=1800)
    parser.add_argument("--memory-gib", type=int, default=4)
    args = parser.parse_args()
    if args.control == (args.admission is not None):
        parser.error("use --control alone or provide --admission for scientific mode")
    if args.control and args.binding is not None:
        parser.error("control mode does not accept a materializer binding")
    if args.control and args.arm_key is not None:
        parser.error("control mode accepts only an existing bounded prepared input")
    if args.input is not None:
        if args.prepared_manifest is None or any(value is not None for value in
                (args.base_root_file, args.target_root_file, args.verifier_root_file, args.commitment)):
            parser.error("prepared-input mode requires --prepared-manifest and no materialization roots")
    else:
        if (args.prepared_manifest is not None or args.binding is not None or
                any(value is None for value in
                    (args.base_root_file, args.target_root_file, args.verifier_root_file, args.commitment))):
            parser.error("scheduled-arm mode requires three roots and a commitment, without a supplied binding")
    if args.watchdog_seconds < 1 or args.memory_gib < 1:
        parser.error("resource guards must be positive")
    out = args.out.resolve()
    if not out.is_dir() or any(out.iterdir()):
        parser.error("trial supervisor must provide an empty, existing --out directory")
    paths = {name: getattr(args, name.replace("-", "_")).resolve() for name in
             ("collector", "count-verifier")}
    materializer_receipt = None
    if args.arm_key is not None:
        paths.update({name: getattr(args, name.replace("-", "_")).resolve() for name in
                      ("base-root-file", "target-root-file", "verifier-root-file", "commitment")})
        prepared_dir = out / "prepared"
        command = [sys.executable, str(MATERIALIZER), "prepare", "--arm-key", args.arm_key,
                   "--base-root-file", str(paths["base-root-file"]),
                   "--target-root-file", str(paths["target-root-file"]),
                   "--verifier-root-file", str(paths["verifier-root-file"]),
                   "--commitment", str(paths["commitment"]), "--output-dir", str(prepared_dir)]
        with (out / "materializer.stdout").open("xb") as stdout, (out / "materializer.stderr").open("xb") as stderr:
            process = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout,
                                     stderr=stderr, check=False)
        if process.returncode != 0:
            raise RuntimeError(f"scheduled arm materialization failed with exit {process.returncode}")
        paths["input"] = prepared_dir / "prepared.txt"
        paths["prepared-manifest"] = prepared_dir / "manifest.json"
        paths["binding"] = prepared_dir / "binding.json"
        materializer_receipt = {
            "command": command, "return_code": process.returncode,
            "stdout_sha256": sha(out / "materializer.stdout"),
            "stderr_sha256": sha(out / "materializer.stderr"),
            "binding_sha256": sha(paths["binding"]),
        }
    else:
        paths["input"] = args.input.resolve()
        paths["prepared-manifest"] = args.prepared_manifest.resolve()
    if args.admission is not None:
        paths["admission"] = args.admission.resolve()
        admission_doc = json.loads(paths["admission"].read_text())
        if args.arm_key is not None and admission_doc.get("schema") != "ectd.graph-study-admission.v1":
            parser.error("scheduled-arm materialization requires study-level admission")
        if admission_doc.get("schema") == "ectd.graph-study-admission.v1":
            if "binding" not in paths and args.binding is None:
                parser.error("study admission requires the materializer --binding")
            if "binding" not in paths:
                paths["binding"] = args.binding.resolve()
        elif args.binding is not None:
            parser.error("per-arm admission does not accept a materializer binding")
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
    if args.control:
        command.append("--control")
    else:
        command += ["--admission", str(paths["admission"])]
        if "binding" in paths:
            command += ["--binding", str(paths["binding"])]
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
    if materializer_receipt is not None:
        result["materializer"] = materializer_receipt
    write_once(out / "raw-result.json", result)
    write_once(out / "manifest.yaml", {
        "schema": "ectd.graph-trial-manifest.v1", "status": result["status"],
        "paths": {name: str(path) for name, path in paths.items()},
        "command": command, "subprocess_return_code": process.returncode,
        "raw_result_sha256": sha(out / "raw-result.json"),
        "attempt_receipt_sha256": result["attempt_receipt_sha256"],
        "driver_stdout_sha256": sha(out / "driver.stdout"),
        "driver_stderr_sha256": sha(out / "driver.stderr"),
        "materializer": materializer_receipt,
    })
    expected = "completed_control" if args.control else "completed_unreviewed"
    return 0 if process.returncode == 0 and result["status"] == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
