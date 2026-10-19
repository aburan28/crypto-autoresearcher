"""Prospective, no-solver bridge from prime63 diagnostic custody to run artifacts.

This module does not authorize a scientific call or change RUN-ICPERF-eb0d88.
A fresh-ID approved launcher may call ``write_outputs`` after its diagnostic
receipt is sealed and before the standard supervisor runs its checker.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "icperf-prime63-m2-output-contract-v1"
DIAGNOSTIC_SCHEMA = "icperf-prime63-m2-diagnostic-raw-v1"
CELL_ORDER = ("monitor-null", "coset-m2", "random-m2", "small_x-m2")
TERMINAL_STOPS = {
    "exited", "timeout_censored", "memory_censored", "scratch_censored",
    "infrastructure_monitor_error",
}


class ContractError(ValueError):
    """The prospective run artifacts cannot be bound to one diagnostic."""


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> tuple[dict, bytes]:
    if not path.is_file() or path.is_symlink():
        raise ContractError(f"missing or unsafe file: {path.name}")
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"expected object: {path.name}")
    return value, raw


def _time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ContractError("diagnostic time missing")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("diagnostic time invalid") from exc
    if stamp.tzinfo is None:
        raise ContractError("diagnostic time lacks timezone")
    return stamp


def derive(run_dir: Path) -> tuple[dict, dict]:
    """Compute exact top-level bytes from one already-written diagnostic.

    The caller still owes an independent mathematical/raw checker. This helper
    checks only the bridge identity and the minimal schedule/receipt contract.
    """
    run_dir = Path(run_dir)
    launch, launch_bytes = read_json(run_dir / "launch.json")
    environment, _ = read_json(run_dir / "environment.json")
    receipt, receipt_bytes = read_json(run_dir / "diagnostic/receipt.json")
    command_path = run_dir / "command.txt"
    if not command_path.is_file() or command_path.is_symlink():
        raise ContractError("missing or unsafe command.txt")
    command = command_path.read_text().strip()
    if not command:
        raise ContractError("empty command.txt")
    authority = launch.get("authority")
    if not isinstance(authority, dict):
        raise ContractError("missing launch authority")
    if receipt.get("schema") != DIAGNOSTIC_SCHEMA:
        raise ContractError("diagnostic schema mismatch")
    for field in ("run_id", "trial_id", "plan_sha256"):
        if not isinstance(launch.get(field), str) or receipt.get(field) != launch[field]:
            raise ContractError(f"diagnostic/launch {field} mismatch")
    if (receipt.get("launch_sha256") != digest(launch_bytes)
            or receipt.get("claim_owner") != authority.get("owner")
            or receipt.get("claim_epoch") != authority.get("epoch")):
        raise ContractError("diagnostic authority mismatch")
    if not isinstance(receipt.get("experiment_id"), str) or not receipt["experiment_id"]:
        raise ContractError("experiment id missing")
    cells = receipt.get("cells")
    if not isinstance(cells, list) or tuple(row.get("cell") for row in cells
                                            if isinstance(row, dict)) != CELL_ORDER:
        raise ContractError("fixed four-cell schedule mismatch")
    control = cells[0]
    if (control.get("kind") != "synthetic_null" or control.get("attempted") is not True
            or control.get("stop") != "infrastructure_monitor_error"
            or (control.get("fault") or {}).get("code") != "unreadable_live_root"):
        raise ContractError("monitor-null control mismatch")
    positives = cells[1:]
    for row in positives:
        if row.get("kind") != "positive" or type(row.get("attempted")) is not bool:
            raise ContractError("positive cell classification missing")
        if row["attempted"] and (not isinstance(row.get("stop"), str)
                                 or row["stop"] not in TERMINAL_STOPS):
            raise ContractError("positive terminal stop missing")
        if (row["attempted"] and row["stop"] == "exited"
                and type(row.get("exit_code")) is not int):
            raise ContractError("exited cell lacks integer exit code")
        if not row["attempted"] and not isinstance(row.get("reason"), str):
            raise ContractError("unattempted positive reason missing")
    raw_tar = run_dir / "diagnostic/raw.tar.gz"
    if not raw_tar.is_file() or raw_tar.is_symlink() or \
            digest(raw_tar.read_bytes()) != receipt.get("raw_tar_sha256"):
        raise ContractError("raw diagnostic archive mismatch")
    started, ended = _time(receipt.get("started_utc")), _time(receipt.get("ended_utc"))
    wall = (ended - started).total_seconds()
    if wall < 0 or not isinstance(environment.get("commit"), str) or not environment["commit"]:
        raise ContractError("invalid timing or execution commit")
    statuses = [row.get("stop") if row["attempted"] else "unattempted"
                for row in positives]
    infrastructure_stop = any(
        row["attempted"] and (row["stop"] == "infrastructure_monitor_error"
                              or (row["stop"] == "exited" and row["exit_code"] != 0))
        for row in positives)
    raw_result = {
        "schema": SCHEMA,
        "experiment_id": receipt["experiment_id"],
        "run_id": receipt["run_id"],
        "trial_id": receipt["trial_id"],
        "plan_sha256": receipt["plan_sha256"],
        "diagnostic_receipt_sha256": digest(receipt_bytes),
        "diagnostic_receipt": receipt,
        "cell_stops": dict(zip(CELL_ORDER[1:], statuses)),
        "verification_status": "pending_independent_checker",
        "scientific_interpretation": None,
    }
    manifest = {
        "run": {
            "id": receipt["run_id"],
            "experiment_id": receipt["experiment_id"],
            "status": "failed_infrastructure" if infrastructure_stop else "completed",
            "code": {"commit": environment["commit"], "command": command},
            "environment": environment,
            "inputs": {"plan_sha256": receipt["plan_sha256"],
                       "trial_id": receipt["trial_id"],
                       "parameters": {"fixed_cells": list(CELL_ORDER[1:]),
                                      "arity_m": 2}},
            "timing": {"wall_seconds": wall,
                       "started_utc": receipt["started_utc"],
                       "ended_utc": receipt["ended_utc"],
                       "scope": "diagnostic_launcher_only"},
            "result": {"raw_result": "raw-result.json",
                       "raw_result_sha256": digest(canonical(raw_result)),
                       "certificate": {"kind": "none"},
                       "positive_attempted": sum(row["attempted"] is True for row in positives),
                       "positive_censored": sum(stop.endswith("_censored") for stop in statuses),
                       "positive_unattempted": sum(stop == "unattempted" for stop in statuses),
                       "verification_status": "pending_independent_checker"},
        }
    }
    return raw_result, manifest


def write_outputs(run_dir: Path) -> tuple[str, str]:
    """Create both required files once; never repair or overwrite a prior run."""
    run_dir = Path(run_dir)
    raw_result, manifest = derive(run_dir)
    paths = (run_dir / "raw-result.json", run_dir / "manifest.yaml")
    if any(path.exists() or path.is_symlink() for path in paths):
        raise ContractError("top-level output already exists")
    payloads = (canonical(raw_result), canonical(manifest))
    for path, payload in zip(paths, payloads):
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
    return tuple(digest(payload) for payload in payloads)


def verify_outputs(run_dir: Path) -> None:
    """Reject missing, changed, or mutually inconsistent top-level outputs."""
    run_dir = Path(run_dir)
    raw_result, manifest = derive(run_dir)
    for name, expected in (("raw-result.json", raw_result),
                           ("manifest.yaml", manifest)):
        path = run_dir / name
        if not path.is_file() or path.is_symlink() or path.read_bytes() != canonical(expected):
            raise ContractError(f"{name} missing or differs from diagnostic custody")
