#!/usr/bin/env python3
"""Verify an immutable budget-cancelled EXP-DREG-001 checkpoint package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(run_dir: Path) -> dict[str, object]:
    run_dir = run_dir.resolve()
    manifest = yaml.safe_load((run_dir / "manifest.yaml").read_text())["run"]
    require(manifest["status"] == "cancelled_by_budget", "wrong terminal status")
    require(manifest["result"]["valid"] is False, "incomplete result marked valid")
    require(manifest["result"]["checkpoint_valid"] is True,
            "checkpoint was not marked valid")
    require(manifest["result"]["process_exit_code"] == 0, "process did not exit cleanly")

    artifacts = manifest["artifacts"]
    hashes = artifacts["sha256"]
    code_dir = run_dir / artifacts["code_snapshot"]
    require(sha256(code_dir / "h012c_block_m4ri.py")
            == manifest["code"]["instrument_sha256"], "instrument hash mismatch")
    for name, expected_hash in manifest["code"]["dependency_sha256"].items():
        require(sha256(code_dir / name) == expected_hash,
                f"dependency hash mismatch: {name}")

    for key in ("raw_result", "stdout", "stderr"):
        require(sha256(run_dir / artifacts[key]) == hashes[key],
                f"artifact hash mismatch: {key}")

    raw = json.loads((run_dir / artifacts["raw_result"]).read_text())
    require(raw["status"] == "cancelled_by_budget", "raw terminal status mismatch")
    require(raw["measurement_complete"] is False, "raw result claims completeness")
    require(raw["evidence_admissible"] is False, "raw result claims admissibility")
    require(raw["process_exit_code"] == 0, "raw exit code mismatch")

    checkpoint_dir = run_dir / artifacts["checkpoints"]
    state_path = checkpoint_dir / "state.json"
    require(sha256(state_path) == hashes["checkpoint_state"],
            "checkpoint state hash mismatch")
    state = json.loads(state_path.read_text())
    require(state["done"] is False, "cancelled checkpoint is terminal-complete")
    require(0 < state["next_col"] < state["ncols"], "invalid checkpoint boundary")
    require(state["next_col"] == raw["checkpoint_telemetry"]["processed_columns"],
            "processed-column mismatch")
    require(state["ncols"] == raw["checkpoint_telemetry"]["ncols"],
            "column-count mismatch")
    require(state["rank_acc"] == raw["checkpoint_telemetry"]["rank_acc"],
            "checkpoint-rank mismatch")
    require(state["system_hash"] == raw["checkpoint_telemetry"]["system_hash"],
            "system identity mismatch")
    require(raw["checkpoint_telemetry"]["remaining_columns"]
            == state["ncols"] - state["next_col"], "remaining-column mismatch")

    carrier_rank = 0
    seen: set[str] = set()
    for entry in state["carries"]:
        name = entry["file"]
        require(name not in seen, f"duplicate carrier name: {name}")
        seen.add(name)
        require(sha256(checkpoint_dir / name) == entry["sha256"],
                f"carrier hash mismatch: {name}")
        carrier_rank += int(entry["npiv"])
    require(carrier_rank == state["rank_acc"], "carrier dimensions do not sum to rank")
    require(carrier_rank == raw["checkpoint_telemetry"]["carrier_rank_sum"],
            "raw carrier-rank mismatch")

    metrics = manifest["result"]["metrics_observed_but_excluded"]
    require(metrics["processed_columns"] == state["next_col"],
            "manifest processed-column mismatch")
    require(metrics["total_columns"] == state["ncols"],
            "manifest total-column mismatch")
    require(metrics["checkpoint_rank"] == state["rank_acc"],
            "manifest checkpoint-rank mismatch")

    return {
        "run_id": manifest["id"],
        "status": "verified_cancelled_checkpoint",
        "evidence_admissible": False,
        "processed_columns": state["next_col"],
        "total_columns": state["ncols"],
        "remaining_columns": state["ncols"] - state["next_col"],
        "checkpoint_rank": state["rank_acc"],
        "carrier_files": len(state["carries"]),
        "system_hash": state["system_hash"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.run_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
