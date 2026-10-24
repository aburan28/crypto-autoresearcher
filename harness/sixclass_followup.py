"""Freeze a native six-class trial and allow one reviewer-selected follow-up.

This is a bounded diagnostic workflow. Official experiment admission, review,
and claim promotion continue through the repository's normal run/coordinate
contracts. Every stage is write-once and binds the frozen binary and target.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness import sixclass_isolated, sixclass_native

SCHEMA = "crypto.autoresearch.sixclass-followup.v1"
INPUT_KEYS = {"walkers", "num_branches", "dp_bits", "max_steps_per_walker", "seed"}
LIMITS = {
    "walkers": (1, 10000),
    "num_branches": (2, 2048),
    "dp_bits": (1, 24),
    "max_steps_per_walker": (1, 100000),
    "seed": (0, 2**64 - 1),
}


def _write(path: Path, document: dict) -> None:
    sixclass_isolated._write_new(path, document)


def validate_input(value: dict) -> dict:
    if not isinstance(value, dict) or set(value) != INPUT_KEYS:
        raise ValueError("input must contain exactly the frozen six-class fields")
    for key, (low, high) in LIMITS.items():
        number = value[key]
        if type(number) is not int or not low <= number <= high:
            raise ValueError(f"{key} is outside the frozen bounded schema")
    if value["num_branches"] & (value["num_branches"] - 1):
        raise ValueError("num_branches must be a power of two")
    return value


def derive_job(base: dict, selection: dict) -> dict:
    validate_input(selection)
    curve = dict(base["curve"])
    for key in INPUT_KEYS - {"walkers"}:
        curve[key] = selection[key]
    return {"curve": curve, "beta": base["beta"], "lambda": base["lambda"]}


def _source_pins() -> dict:
    return {"followup_sha256": sixclass_native.digest(Path(__file__)),
            "isolation_sha256": sixclass_native.digest(Path(sixclass_isolated.__file__)),
            "launcher_sha256": sixclass_native.digest(Path(sixclass_native.__file__))}


def freeze(binary: Path, base_job: Path, attempt: Path, initial: dict) -> dict:
    validate_input(initial)
    base = json.loads(base_job.read_text())
    derive_job(base, initial)
    manifest = {
        "schema": SCHEMA, "binary_sha256": sixclass_native.digest(binary),
        "base_job_sha256": sixclass_native.digest(base_job),
        "source_pins": _source_pins(), "initial_input": initial,
        "followup_schema": {key: {"minimum": a, "maximum": b}
                            for key, (a, b) in LIMITS.items()},
        "max_followups": 1, "isolation_image": sixclass_isolated.IMAGE,
        "scope": "bounded native diagnostic; no research-state transition",
    }
    attempt.mkdir(parents=True, exist_ok=False)
    _write(attempt / "manifest.json", manifest)
    return manifest


def _admit(attempt: Path, binary: Path, base_job: Path) -> dict:
    manifest = json.loads((attempt / "manifest.json").read_text())
    if (manifest["schema"] != SCHEMA or manifest["source_pins"] != _source_pins()
            or manifest["binary_sha256"] != sixclass_native.digest(binary)
            or manifest["base_job_sha256"] != sixclass_native.digest(base_job)
            or manifest["max_followups"] != 1
            or manifest["isolation_image"] != sixclass_isolated.IMAGE):
        raise ValueError("frozen binary, job, runner, or schema has changed")
    validate_input(manifest["initial_input"])
    return manifest


def _execute(attempt: Path, phase: str, binary: Path, base_job: Path,
             selection: dict, *, sudo: bool, timeout: int) -> dict:
    phase_dir = attempt / phase
    phase_dir.mkdir(exist_ok=False)
    _write(phase_dir / "input.json", selection)
    job = derive_job(json.loads(base_job.read_text()), selection)
    _write(phase_dir / "job.json", job)
    try:
        return sixclass_isolated.run(phase_dir / "job.json", binary,
                                     selection["walkers"], phase_dir / "receipt.json",
                                     sudo=sudo, timeout=timeout)
    except Exception as exc:
        _write(phase_dir / "failure.json", {"phase": phase,
               "error_type": type(exc).__name__, "error": str(exc)})
        raise


def initial(attempt: Path, binary: Path, base_job: Path,
            *, sudo: bool = False, timeout: int = 120) -> dict:
    manifest = _admit(attempt, binary, base_job)
    return _execute(attempt, "initial", binary, base_job,
                    manifest["initial_input"], sudo=sudo, timeout=timeout)


def followup(attempt: Path, binary: Path, base_job: Path, selection: dict,
             reviewer: str, reason: str, *, sudo: bool = False,
             timeout: int = 120) -> dict:
    manifest = _admit(attempt, binary, base_job)
    validate_input(selection)
    if not reviewer.strip() or not reason.strip():
        raise ValueError("reviewer and test reason are required")
    if selection == manifest["initial_input"]:
        raise ValueError("follow-up must change a frozen input")
    if (attempt / "final.json").exists():
        raise ValueError("finalized attempt cannot accept a follow-up")
    first = attempt / "initial/receipt.json"
    if not first.is_file():
        raise ValueError("an independently checked initial receipt is required")
    first_receipt = json.loads(first.read_text())
    first_job = attempt / "initial/job.json"
    if (json.loads((attempt / "initial/input.json").read_text()) != manifest["initial_input"]
            or first_receipt["job_sha256"] != sixclass_native.digest(first_job)
            or first_receipt["worker_sha256"] != manifest["binary_sha256"]
            or not sixclass_native.verify_first_dp(json.loads(first_job.read_text()),
                                                   first_receipt["result"])):
        raise ValueError("initial receipt chain failed verification")
    phase_dir = attempt / "followup"
    phase_dir.mkdir(exist_ok=False)
    _write(phase_dir / "selection.json", {"reviewer": reviewer,
            "reason": reason, "input": selection,
            "initial_receipt_sha256": sixclass_native.digest(first),
            "manifest_sha256": sixclass_native.digest(attempt / "manifest.json")})
    # The reviewer choice is written before the native run and cannot change.
    _write(phase_dir / "input.json", selection)
    job = derive_job(json.loads(base_job.read_text()), selection)
    _write(phase_dir / "job.json", job)
    try:
        return sixclass_isolated.run(phase_dir / "job.json", binary,
                                     selection["walkers"], phase_dir / "receipt.json",
                                     sudo=sudo, timeout=timeout)
    except Exception as exc:
        _write(phase_dir / "failure.json", {"phase": "followup",
               "error_type": type(exc).__name__, "error": str(exc)})
        raise


def finalize(attempt: Path, binary: Path, base_job: Path) -> dict:
    manifest = _admit(attempt, binary, base_job)
    phases = ["initial"] + (["followup"] if (attempt / "followup").exists() else [])
    chain = []
    for phase in phases:
        directory = attempt / phase
        job_path, receipt_path = directory / "job.json", directory / "receipt.json"
        if not receipt_path.is_file():
            raise ValueError(f"{phase} has no completed receipt")
        selection = json.loads((directory / "input.json").read_text())
        if phase == "initial" and selection != manifest["initial_input"]:
            raise ValueError("initial input differs from the frozen manifest")
        if json.loads(job_path.read_text()) != derive_job(json.loads(base_job.read_text()), selection):
            raise ValueError(f"{phase} job differs from frozen input derivation")
        receipt = json.loads(receipt_path.read_text())
        if (receipt["job_sha256"] != sixclass_native.digest(job_path)
                or receipt["worker_sha256"] != manifest["binary_sha256"]
                or not sixclass_native.verify_first_dp(json.loads(job_path.read_text()),
                                                       receipt["result"])):
            raise ValueError(f"{phase} receipt failed independent check")
        if receipt["result"]["log"] is not None and not sixclass_native.verify_log(
                json.loads(job_path.read_text()), receipt["result"]["log"]):
            raise ValueError(f"{phase} log failed independent check")
        chain.append({"phase": phase, "input_sha256": sixclass_native.digest(directory / "input.json"),
                      "job_sha256": receipt["job_sha256"],
                      "receipt_sha256": sixclass_native.digest(receipt_path),
                      "log_recovered": receipt["result"]["log"] is not None})
    if len(phases) == 2:
        selection_path = attempt / "followup/selection.json"
        selection = json.loads(selection_path.read_text())
        if (selection["input"] != json.loads((attempt / "followup/input.json").read_text())
                or selection["initial_receipt_sha256"] != chain[0]["receipt_sha256"]
                or selection["manifest_sha256"] != sixclass_native.digest(attempt / "manifest.json")
                or not selection["reviewer"].strip() or not selection["reason"].strip()
                or selection["input"] == manifest["initial_input"]):
            raise ValueError("follow-up selection chain is invalid")
        chain[1]["selection_sha256"] = sixclass_native.digest(selection_path)
    dossier = {"schema": SCHEMA, "manifest_sha256": sixclass_native.digest(attempt / "manifest.json"),
               "stages": chain, "status": "bounded_observations_only"}
    _write(attempt / "final.json", dossier)
    return dossier


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sudo", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("freeze", "initial", "followup", "finalize"):
        command = sub.add_parser(name)
        command.add_argument("--attempt", type=Path, required=True)
        command.add_argument("--binary", type=Path, required=True)
        command.add_argument("--job", type=Path, required=True)
        if name in ("freeze", "followup"):
            command.add_argument("--input", type=Path, required=True)
        if name == "followup":
            command.add_argument("--reviewer", required=True)
            command.add_argument("--reason", required=True)
        if name in ("initial", "followup"):
            command.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    if args.command == "freeze":
        result = freeze(args.binary, args.job, args.attempt,
                        json.loads(args.input.read_text()))
    elif args.command == "initial":
        result = initial(args.attempt, args.binary, args.job,
                         sudo=args.sudo, timeout=args.timeout)
    elif args.command == "followup":
        result = followup(args.attempt, args.binary, args.job,
                          json.loads(args.input.read_text()), args.reviewer,
                          args.reason, sudo=args.sudo, timeout=args.timeout)
    else:
        result = finalize(args.attempt, args.binary, args.job)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
