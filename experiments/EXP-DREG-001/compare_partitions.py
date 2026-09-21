#!/usr/bin/env python3
"""Verify and compare two sealed EXP-DREG-001 column partitions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from verify_run import verify


def load_run(run_dir: Path) -> tuple[dict, dict, dict]:
    manifest = yaml.safe_load((run_dir / "manifest.yaml").read_text())["run"]
    raw = json.loads((run_dir / manifest["artifacts"]["raw_result"]).read_text())
    state = json.loads(
        (run_dir / manifest["artifacts"]["checkpoints"] / "state.json").read_text()
    )
    return manifest, raw, state


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def compare(left_dir: Path, right_dir: Path) -> dict[str, object]:
    left_dir = left_dir.resolve()
    right_dir = right_dir.resolve()
    left_verified = verify(left_dir)
    right_verified = verify(right_dir)
    left_manifest, left_raw, left_state = load_run(left_dir)
    right_manifest, right_raw, right_state = load_run(right_dir)

    require(left_manifest["inputs"]["partition"] == "A", "left run is not partition A")
    require(right_manifest["inputs"]["partition"] == "B", "right run is not partition B")
    require(
        left_manifest["inputs"]["chunk_force"]
        != right_manifest["inputs"]["chunk_force"],
        "partitions do not use different chunk widths",
    )
    require(left_raw["which"] == right_raw["which"] == "sem", "arms are not both sem")

    equal_fields = (
        "system_hash",
        "n",
        "ti",
        "d",
        "nb",
        "nrows",
        "ncols",
        "pred",
        "rank",
        "deficit",
        "status",
    )
    equality = {name: left_raw[name] == right_raw[name] for name in equal_fields}
    require(all(equality.values()), f"partition result mismatch: {equality}")
    require(left_state["done"] is True and right_state["done"] is True,
            "at least one checkpoint is non-terminal")
    require(left_state["next_col"] == left_raw["ncols"],
            "partition A did not process every column")
    require(right_state["next_col"] == right_raw["ncols"],
            "partition B did not process every column")

    code_fields = ("commit", "instrument_sha256", "dependency_sha256")
    code_equality = {
        name: left_manifest["code"][name] == right_manifest["code"][name]
        for name in code_fields
    }
    require(all(code_equality.values()), f"partition code mismatch: {code_equality}")

    return {
        "status": "partition_replication_verified",
        "experiment_id": left_manifest["experiment_id"],
        "preregistration": left_manifest["preregistration"],
        "arm": "sem",
        "partitioning_independent": True,
        "equal_result_fields": equality,
        "equal_code_fields": code_equality,
        "terminal_metrics": {
            "system_hash": left_raw["system_hash"],
            "nrows": left_raw["nrows"],
            "ncols": left_raw["ncols"],
            "rank": left_raw["rank"],
            "semiregular_prediction": left_raw["pred"],
            "deficit": left_raw["deficit"],
        },
        "partitions": [
            {
                "run_id": left_manifest["id"],
                "partition": "A",
                "chunk_force": left_manifest["inputs"]["chunk_force"],
                "units": left_raw["n_units"],
                "raw_result_sha256": left_manifest["artifacts"]["sha256"]["raw_result"],
                "checkpoint_state_sha256": left_manifest["artifacts"]["sha256"]["checkpoint_state"],
                "verification": left_verified["status"],
            },
            {
                "run_id": right_manifest["id"],
                "partition": "B",
                "chunk_force": right_manifest["inputs"]["chunk_force"],
                "units": right_raw["n_units"],
                "raw_result_sha256": right_manifest["artifacts"]["sha256"]["raw_result"],
                "checkpoint_state_sha256": right_manifest["artifacts"]["sha256"]["checkpoint_state"],
                "verification": right_verified["status"],
            },
        ],
        "interpretation_status": "withheld_pending_null_A_and_B",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(compare(args.left, args.right), indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(report)
    print(report, end="")


if __name__ == "__main__":
    main()
