"""No-science output custody for the v2 canned supervisor fixture.

This module deliberately has no solver import.  It turns a sealed, synthetic
diagnostic receipt into the two top-level files required by the ordinary
supervisor, and can rederive them byte-for-byte for the checker.
"""
from __future__ import annotations

import hashlib
import json
import tarfile
from datetime import datetime
from pathlib import Path

SCHEMA = "icperf-prime63-m2-output-contract-v2"
DIAGNOSTIC_SCHEMA = "icperf-prime63-m2-diagnostic-raw-v2"
CELLS = ("monitor-null", "coset-m2", "random-m2", "small_x-m2")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

class ContractError(ValueError):
    pass

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def _json(path):
    if not path.is_file() or path.is_symlink():
        raise ContractError(f"missing or unsafe {path.name}")
    try:
        value = json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"invalid JSON {path.name}") from error
    if not isinstance(value, dict):
        raise ContractError(f"object required {path.name}")
    return value, path.read_bytes()

def _sha(value, name):
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ContractError(f"invalid {name} digest")

def verify_input_manifest():
    """Bind source and fixed historical inputs without recursively hashing this manifest."""
    manifest, _ = _json(HERE / "input_manifest.json")
    if manifest.get("schema") != "icperf-prime63-m2-output-contract-v2-input-v1" or manifest.get("self_hash_excluded") is not True:
        raise ContractError("input manifest schema")
    for relative, expected in manifest.get("fixed_input_sha256", {}).items():
        path = ROOT / relative
        if not path.is_file() or digest(path.read_bytes()) != expected: raise ContractError("fixed input hash mismatch")
    for name, expected in manifest.get("source_sha256", {}).items():
        path = HERE / name
        if not path.is_file() or digest(path.read_bytes()) != expected: raise ContractError("source hash mismatch")
    return manifest

def derive(run_dir):
    run_dir = Path(run_dir)
    input_manifest = verify_input_manifest()
    launch, launch_bytes = _json(run_dir / "launch.json")
    environment, _ = _json(run_dir / "environment.json")
    receipt, receipt_bytes = _json(run_dir / "diagnostic" / "receipt.json")
    command = (run_dir / "command.txt")
    if not command.is_file() or command.is_symlink() or not command.read_text().strip():
        raise ContractError("missing or empty command")
    authority = launch.get("authority")
    if not isinstance(authority, dict) or not isinstance(authority.get("owner"), str) or not authority["owner"].strip() or type(authority.get("epoch")) is not int or authority["epoch"] < 1:
        raise ContractError("invalid launch authority")
    if receipt.get("schema") != DIAGNOSTIC_SCHEMA:
        raise ContractError("diagnostic schema mismatch")
    for key in ("run_id", "trial_id", "plan_sha256"):
        if not isinstance(launch.get(key), str) or not launch[key].strip() or receipt.get(key) != launch[key]:
            raise ContractError(f"plan/claim binding mismatch: {key}")
    _sha(receipt.get("plan_sha256"), "plan")
    if receipt.get("launch_sha256") != digest(launch_bytes) or receipt.get("claim_owner") != authority["owner"] or receipt.get("claim_epoch") != authority["epoch"]:
        raise ContractError("plan/claim/source binding mismatch")
    sources = environment.get("source_sha256")
    if not isinstance(sources, dict) or not all(isinstance(k, str) and isinstance(v, str) and len(v) == 64 for k, v in sources.items()):
        raise ContractError("source binding missing")
    expected_sources = {str((HERE / name).relative_to(ROOT)): value
                        for name, value in input_manifest["source_sha256"].items()}
    if {key: sources.get(key) for key in expected_sources} != expected_sources:
        raise ContractError("source binding mismatch")
    tar_path = run_dir / "diagnostic" / "raw.tar.gz"
    if not tar_path.is_file() or tar_path.is_symlink() or receipt.get("raw_tar_sha256") != digest(tar_path.read_bytes()):
        raise ContractError("diagnostic archive mismatch")
    members = receipt.get("raw_members")
    if not isinstance(members, list) or not members:
        raise ContractError("raw member custody missing")
    try:
        with tarfile.open(tar_path, "r:gz") as archive:
            entries = archive.getmembers()
            names = [m.name for m in entries if m.isfile()]
            if len(names) != len(entries) or len(names) != len(set(names)):
                raise ContractError("non-file or duplicate raw member")
            declared = []
            for row in members:
                if not isinstance(row, dict): raise ContractError("raw member declaration invalid")
                name, expected, size = row.get("path"), row.get("sha256"), row.get("bytes")
                if not isinstance(name, str) or name.startswith("/") or ".." in Path(name).parts: raise ContractError("unlisted raw member")
                _sha(expected, "raw member")
                if type(size) is not int or size < 0: raise ContractError("raw member size invalid")
                handle = archive.extractfile(name)
                if handle is None: raise ContractError("missing raw member")
                data = handle.read()
                if len(data) != size or digest(data) != expected: raise ContractError("raw member digest mismatch")
                declared.append(name)
    except tarfile.TarError as error:
        raise ContractError("invalid diagnostic archive") from error
    if names != declared:
        raise ContractError("unlisted raw member")
    cells = receipt.get("cells")
    if not isinstance(cells, list) or [r.get("cell") for r in cells if isinstance(r, dict)] != list(CELLS):
        raise ContractError("fixed cell schedule mismatch")
    control, positives = cells[0], cells[1:]
    if control.get("kind") != "synthetic_null" or control.get("attempted") is not True or control.get("stop") != "infrastructure_monitor_error" or (control.get("fault") or {}).get("code") != "unreadable_live_root":
        raise ContractError("monitor null control mismatch")
    stops = {}
    for row in positives:
        if row.get("kind") != "positive" or type(row.get("attempted")) is not bool:
            raise ContractError("positive classification missing")
        if row["attempted"]:
            if row.get("stop") not in {"timeout_censored", "memory_censored", "scratch_censored", "exited"}:
                raise ContractError("positive terminal class missing")
            if row["stop"] == "exited" and row.get("response") != "canned_positive":
                raise ContractError("false successful response")
            stops[row["cell"]] = row["stop"]
        elif not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise ContractError("unattempted positive reason missing")
        else:
            stops[row["cell"]] = "unattempted"
    if not isinstance(environment.get("commit"), str) or not environment["commit"]:
        raise ContractError("execution commit missing")
    try:
        wall = (datetime.fromisoformat(receipt["ended_utc"]) - datetime.fromisoformat(receipt["started_utc"])).total_seconds()
    except (KeyError, TypeError, ValueError) as error:
        raise ContractError("invalid timestamps") from error
    if wall < 0: raise ContractError("negative wall time")
    raw = {"schema": SCHEMA, "experiment_id": receipt["experiment_id"], "run_id": receipt["run_id"], "trial_id": receipt["trial_id"], "plan_sha256": receipt["plan_sha256"], "diagnostic_receipt_sha256": digest(receipt_bytes), "diagnostic_raw_tar_sha256": receipt["raw_tar_sha256"], "cell_stops": stops, "verification_status": "pending_independent_checker", "attack_claimed": False, "scientific_interpretation": None}
    manifest = {"run": {"id": receipt["run_id"], "experiment_id": receipt["experiment_id"], "task_id": "TASK-20261020-f237a2", "status": "completed", "code": {"commit": environment["commit"], "command": command.read_text().strip()}, "environment": environment, "inputs": {"plan_sha256": receipt["plan_sha256"], "trial_id": receipt["trial_id"]}, "timing": {"wall_seconds": wall, "started_utc": receipt["started_utc"], "ended_utc": receipt["ended_utc"]}, "result": {"raw_result": "raw-result.json", "raw_result_sha256": digest(canonical(raw)), "certificate": {"kind": "none"}, "positive_censored": sum(v.endswith("_censored") for v in stops.values()), "verification_status": "pending_independent_checker"}, "attack_claimed": False}}
    return raw, manifest

def write_outputs(run_dir):
    raw, manifest = derive(run_dir)
    paths = (Path(run_dir) / "raw-result.json", Path(run_dir) / "manifest.yaml")
    if any(p.exists() or p.is_symlink() for p in paths): raise ContractError("top-level output already exists")
    for path, value in zip(paths, (raw, manifest)):
        path.write_bytes(canonical(value))
    return {p.name: digest(p.read_bytes()) for p in paths}

def verify_outputs(run_dir):
    raw, manifest = derive(run_dir)
    for name, expected in (("raw-result.json", raw), ("manifest.yaml", manifest)):
        path = Path(run_dir) / name
        if not path.is_file() or path.is_symlink() or path.read_bytes() != canonical(expected):
            raise ContractError(f"{name} missing or differs")
