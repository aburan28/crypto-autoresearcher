#!/usr/bin/env python3
"""One supervisor trial around the Modal controller; never retries science.

The checker establishes local transport/archive integrity only. Native public
witness verification, the frozen analysis and scientific review remain separate
recorded stages, and no successful transport is labeled a mathematical result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controller


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    with Path(path).open("x") as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False) + "\n")


def seal_controller_tree(directory):
    directory = Path(directory)
    entries = []
    for path in sorted((directory / "modal").rglob("*")):
        if path.is_symlink():
            raise ValueError("controller evidence symlink forbidden")
        if path.is_file():
            entries.append({"path": path.relative_to(directory).as_posix(),
                            "bytes": path.stat().st_size, "sha256": sha_file(path)})
    manifest = {"schema": "classical.ecdlp.endpoint-reuse.modal-trial-evidence/v1", "files": entries}
    write_json(directory / "modal-evidence-manifest.json", manifest)
    archive = directory / "modal-evidence.tar.gz"
    with archive.open("xb") as target:
        with tarfile.open(fileobj=target, mode="w:gz", dereference=False) as bundle:
            for entry in entries:
                bundle.add(directory / entry["path"], arcname=entry["path"], recursive=False)
    return {"path": archive.name, "bytes": archive.stat().st_size, "sha256": sha_file(archive),
            "member_manifest": "modal-evidence-manifest.json",
            "member_manifest_sha256": sha_file(directory / "modal-evidence-manifest.json")}


def operational_status(record, error):
    record = record if isinstance(record, dict) else {}
    collection = record.get("collection", {})
    return {"controller_success": record.get("success") is True,
            "engine_command_returncode": record.get("engine_command_returncode"),
            "collected_engine_returncode": collection.get("engine_returncode"),
            "transport_complete": collection.get("complete") is True,
            "status": "completed" if (error is None and not record.get("error")
                        and record.get("success") is True and record.get("engine_command_returncode") == 0
                        and collection.get("complete") is True and collection.get("engine_returncode") == 0) else "failed"}


def run(args):
    out = args.out
    if not out.is_dir() or any((out / name).exists() for name in ("modal", "manifest.yaml", "raw-result.json", "modal-evidence.tar.gz")):
        raise ValueError("supervisor's fresh run directory required")
    record = None
    error = None
    try:
        record = controller.run(args.image_receipt, args.protocol, args.public_bundle,
                                args.inputs_manifest_sha256, out / "modal")
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    evidence = seal_controller_tree(out)
    collection = record.get("collection", {}) if isinstance(record, dict) else {}
    operation = operational_status(record, error)
    raw = {"schema": "classical.ecdlp.endpoint-reuse.modal-trial/v1", "attack_claimed": False,
           "experiment_id": "EXP-ECDLP-2b4ff1", "run_id": args.run_id,
           "controller_receipt": "modal/controller-receipt.json", "controller": record,
           "driver_error": error, "evidence": evidence,
           "protocol_file_sha256": sha_file(args.protocol),
           "public_bundle_sha256": sha_file(args.public_bundle),
           "inputs_manifest_sha256": args.inputs_manifest_sha256,
           "transport_complete": collection.get("complete") is True,
           "operational_status": operation,
           "scientific_validity": "not_assessed", "independent_public_verification": False,
           "analysis_executed": False, "all_clocks_wall_valid": False,
           "automatic_retry": False, "maximum_scientific_attempts": 1}
    write_json(out / "raw-result.json", raw)
    # JSON is valid YAML; the official supervisor fills only its own missing
    # run-envelope facts and retains these original driver bytes separately.
    write_json(out / "manifest.yaml", {"run": {
        "id": args.run_id, "experiment_id": "EXP-ECDLP-2b4ff1", "attack_claimed": False,
        "status": operation["status"],
        "status_note": "Observed controller/engine operation only; public witness checking and scientific validity remain not_assessed.",
        "metrics": {"transport_complete": raw["transport_complete"], "scientific_validity": "not_assessed",
                    "all_clocks_wall_valid": False},
        "result": {"certificate": {"kind": "none", "verified": None,
                                    "note": "Transport-only record; public witness checking and scientific interpretation are separate."}},
    }})
    print(json.dumps({"transport_complete": raw["transport_complete"], "evidence": evidence,
                      "scientific_validity": "not_assessed", "automatic_retry": False}))
    return 0 if operation["status"] == "completed" else 1


def check(out):
    out = Path(out)
    raw = json.loads((out / "raw-result.json").read_bytes())
    if (raw.get("schema") != "classical.ecdlp.endpoint-reuse.modal-trial/v1"
            or raw.get("attack_claimed") is not False or raw.get("automatic_retry") is not False
            or raw.get("all_clocks_wall_valid") is not False):
        raise ValueError("trial observation/clock/retry contract differs")
    evidence = raw["evidence"]
    archive = out / evidence["path"]
    member_file = out / evidence["member_manifest"]
    if (evidence["path"] != "modal-evidence.tar.gz" or evidence["member_manifest"] != "modal-evidence-manifest.json"
            or archive.stat().st_size != evidence["bytes"] or sha_file(archive) != evidence["sha256"]
            or sha_file(member_file) != evidence["member_manifest_sha256"]):
        raise ValueError("controller evidence archive or member manifest differs")
    manifest = json.loads(member_file.read_bytes())
    expected = {entry["path"]: entry for entry in manifest["files"]}
    if (manifest.get("schema") != "classical.ecdlp.endpoint-reuse.modal-trial-evidence/v1"
            or len(expected) != len(manifest["files"])):
        raise ValueError("wrong evidence schema or duplicate members")
    seen = set()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            name = member.name
            rel = Path(name)
            if (name in seen or name not in expected or not member.isfile()
                    or rel.is_absolute() or ".." in rel.parts or rel.parts[0] != "modal"):
                raise ValueError("unsafe or undeclared controller evidence member")
            seen.add(name)
            digest = hashlib.sha256()
            source = bundle.extractfile(member)
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
            entry = expected[name]
            local = out / name
            if (member.size != entry["bytes"] or digest.hexdigest() != entry["sha256"]
                    or not local.is_file() or local.is_symlink() or sha_file(local) != entry["sha256"]):
                raise ValueError("controller evidence bytes differ: " + name)
    if seen != set(expected):
        raise ValueError("incomplete evidence archive")
    receipt_path = out / "modal/controller-receipt.json"
    if receipt_path.is_file():
        controller_record = json.loads(receipt_path.read_bytes())
        if raw["controller"] != controller_record:
            raise ValueError("raw controller duplicate differs from archived actual controller receipt")
        if raw["transport_complete"] is not (controller_record.get("collection", {}).get("complete") is True):
            raise ValueError("transport_complete differs from archived actual collection result")
    elif raw["controller"] is not None:
        raise ValueError("raw controller has no archived actual receipt")
    operation = operational_status(raw["controller"], raw["driver_error"])
    if raw.get("operational_status") != operation:
        raise ValueError("operational status differs from actual controller/engine outcome")
    print(json.dumps({"transport_evidence_integrity": True, "transport_complete": raw["transport_complete"],
                      "scientific_validity": "not_assessed", "independent_public_verification": False}))
    return 0 if operation["status"] == "completed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    launch = sub.add_parser("run")
    for name in ("image-receipt", "protocol", "public-bundle", "out"):
        launch.add_argument("--" + name, type=Path, required=True)
    launch.add_argument("--inputs-manifest-sha256", required=True)
    launch.add_argument("--run-id", required=True)
    verify = sub.add_parser("check")
    verify.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    return run(args) if args.action == "run" else check(args.out)


if __name__ == "__main__":
    raise SystemExit(main())
