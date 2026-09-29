#!/usr/bin/env python3
"""Local, write-once delivery telemetry. No solver or scientific validation."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def read_bounded(path):
    if path.stat().st_size > 1048576:
        raise ValueError("Input exceeds frozen per-file cap")
    return path.read_bytes()

def emit(path, data):
    raw = (json.dumps(data, indent=2) + "\n").encode()
    if len(raw) > 8192:
        raise ValueError("Output exceeds frozen cap")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    readback = path.read_bytes()
    if readback != raw:
        raise ValueError("Output readback mismatch")
    print(json.dumps({"path": str(path), "sha256": digest(raw),
                      "bytes": len(raw), "readback_verified_at": now()}))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["begin", "finish"])
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--first-tool-started-at")
    a = parser.parse_args()
    invocation_at = now()
    batch = Path(__file__).resolve().parent
    root = batch.parents[4]
    contract_path = batch / "contracts" / "delivery.json"
    contract_raw = read_bounded(contract_path)
    contract = json.loads(contract_raw)
    output_root = Path(a.output_root).resolve()
    if str(output_root) != contract["output_transport_root"]:
        raise ValueError("Output root differs from frozen transport")
    task_dir = output_root / contract["task_directory"]
    first = task_dir / "start.json"
    final = task_dir / "report.json"
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   text=True, timeout=5).strip()
    transport_head = subprocess.check_output(["git", "-C", str(output_root), "rev-parse", "HEAD"],
                                             text=True, timeout=5).strip()
    if a.stage == "begin":
        if not a.first_tool_started_at:
            raise ValueError("Actual first-tool timestamp required")
        stamp = dt.datetime.fromisoformat(a.first_tool_started_at.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("Timestamp must include timezone")
        if stamp > dt.datetime.now(dt.timezone.utc):
            raise ValueError("First-tool timestamp cannot be future")
        sources = {}
        total = len(contract_raw)
        for name in ["AGENTS.md", "agents/validator.md"]:
            raw = read_bounded(root / name)
            total += len(raw)
            sources[name] = {"bytes": len(raw), "sha256": digest(raw)}
        if total > contract["budget"]["maximum_total_input_bytes"]:
            raise ValueError("Input aggregate exceeds cap")
        emit(first, {
            "record_kind": "agent_invoked_delivery_telemetry",
            "task_id": contract["task_id"], "stage": "start",
            "diagnostic_only": True, "nonce": contract["nonce"],
            "first_tool_started_at_reported": stamp.isoformat(),
            "probe_invocation_at": invocation_at, "emitted_at": now(),
            "git_head": head, "output_transport_git_head": transport_head, "contract_sha256": digest(contract_raw),
            "mandatory_source_hashes": sources,
            "first_tool_provenance": "Timestamp returned by the worker's first read-only shell call; parent observation recorded separately",
            "scientific_conclusion": None
        })
    else:
        raw = read_bounded(first)
        start = json.loads(raw)
        if start["task_id"] != contract["task_id"] or start["nonce"] != contract["nonce"]:
            raise ValueError("Task or nonce mismatch")
        if start["contract_sha256"] != digest(contract_raw):
            raise ValueError("Contract binding mismatch")
        emit(final, {
            "record_kind": "agent_invoked_delivery_telemetry",
            "task_id": contract["task_id"], "stage": "completion",
            "diagnostic_only": True, "outcome": "roundtrip_observed",
            "nonce": start["nonce"], "start_sha256": digest(raw),
            "contract_sha256": digest(contract_raw),
            "start_emitted_at": start["emitted_at"],
            "probe_invocation_at": invocation_at, "emitted_at": now(),
            "git_head": head, "output_transport_git_head": transport_head,
            "requested_policy": "review-adversarial",
            "requested_reasoning_effort": "xhigh",
            "resolved_model_id": None, "model_verified": False,
            "claim_scope": "This invocation read the start file and reproduced its nonce and SHA-256",
            "limitations": ["No independent evidence review was performed",
                            "Parent dispatch timing and deadline disposition are separate",
                            "Native model memory is unmeasured"],
            "scientific_conclusion": None
        })

if __name__ == "__main__":
    main()
