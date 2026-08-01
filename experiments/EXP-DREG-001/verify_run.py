#!/usr/bin/env python3
"""Verify one completed EXP-DREG-001 run package without changing it."""

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
    manifest = yaml.safe_load((run_dir / "manifest.yaml").read_text())["run"]
    require(
        manifest["status"] in {
            "completed_valid",
            "completed_valid_pending_partition_replication",
        },
        "run does not have a verifiable completed status",
    )
    require(manifest["result"]["valid"] is True, "manifest result is not valid")
    require((run_dir / "command.txt").read_text().strip() != "", "empty command")
    json.loads((run_dir / "environment.json").read_text())

    artifacts = manifest["artifacts"]
    hashes = artifacts["sha256"]
    code_dir = run_dir / artifacts["code_snapshot"]
    require(
        sha256(code_dir / "h012c_block_m4ri.py") == manifest["code"]["instrument_sha256"],
        "instrument snapshot hash mismatch",
    )
    for name, expected_hash in manifest["code"]["dependency_sha256"].items():
        require(sha256(code_dir / name) == expected_hash,
                f"dependency snapshot hash mismatch: {name}")
    raw_path = run_dir / artifacts["raw_result"]
    stdout_path = run_dir / artifacts["stdout"]
    stderr_path = run_dir / artifacts["stderr"]
    require(sha256(raw_path) == hashes["raw_result"], "raw-result hash mismatch")
    require(sha256(stdout_path) == hashes["stdout"], "stdout hash mismatch")
    require(sha256(stderr_path) == hashes["stderr"], "stderr hash mismatch")

    raw = json.loads(raw_path.read_text())
    expected = manifest["expected"]
    metrics = manifest["result"]["metrics"]
    triples = {
        "raw": (raw["rank"], raw["pred"], raw["deficit"]),
        "manifest": (
            metrics["rank"],
            metrics["semiregular_prediction"],
            metrics["deficit"],
        ),
    }
    require(len(set(triples.values())) == 1, f"metric mismatch: {triples}")
    require(
        raw["pred"] == expected["semiregular_prediction"],
        "semi-regular prediction differs from preregistration",
    )
    if expected.get("rank") is not None:
        require(raw["rank"] == expected["rank"], "rank differs from frozen anchor")
        require(raw["deficit"] == expected["deficit"],
                "deficit differs from frozen anchor")
    require(raw["status"] == "completed_valid", "raw status is not completed_valid")

    checkpoint_dir = run_dir / artifacts["checkpoints"]
    state_path = checkpoint_dir / "state.json"
    require(sha256(state_path) == hashes["checkpoint_state"], "state hash mismatch")
    state = json.loads(state_path.read_text())
    require(state["done"] is True, "checkpoint is not terminal")
    require(state["next_col"] == state["ncols"], "checkpoint did not process all columns")
    require(state["rank_acc"] == raw["rank"], "checkpoint/raw rank mismatch")
    require(state["system_hash"] == raw["system_hash"], "system identity mismatch")
    input_names = {"d": "degree", "which": "arm"}
    for key in ("n", "d", "seed", "which"):
        require(state[key] == manifest["inputs"][input_names.get(key, key)],
                f"manifest/checkpoint mismatch for {key}")

    carry_rank = 0
    seen: set[str] = set()
    for entry in state["carries"]:
        name = entry["file"]
        require(name not in seen, f"duplicate carrier name: {name}")
        seen.add(name)
        carry_path = checkpoint_dir / name
        require(sha256(carry_path) == entry["sha256"], f"carrier hash mismatch: {name}")
        carry_rank += int(entry["npiv"])
    require(carry_rank == raw["rank"], "carrier dimensions do not sum to rank")

    return {
        "run_id": manifest["id"],
        "status": "verified",
        "rank": raw["rank"],
        "prediction": raw["pred"],
        "deficit": raw["deficit"],
        "processed_columns": state["next_col"],
        "carrier_files": len(state["carries"]),
        "system_hash": raw["system_hash"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    reports = [verify(path.resolve()) for path in args.run_dirs]
    print(json.dumps(reports, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
