#!/usr/bin/env python3
"""Verify a completed EXP-DREG-001 checkpoint continuation and its lineage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

from verify_cancelled_run import verify as verify_cancelled
from verify_run import verify as verify_completed


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_manifest(run_dir: Path) -> dict:
    return yaml.safe_load((run_dir / "manifest.yaml").read_text())["run"]


def load_state(run_dir: Path, manifest: dict) -> dict:
    return json.loads(
        (run_dir / manifest["artifacts"]["checkpoints"] / "state.json").read_text()
    )


def verify(parent_dir: Path, successor_dir: Path, amendment_path: Path,
           null_a_dir: Path) -> dict[str, object]:
    parent_dir = parent_dir.resolve()
    successor_dir = successor_dir.resolve()
    amendment_path = amendment_path.resolve()
    null_a_dir = null_a_dir.resolve()

    parent_report = verify_cancelled(parent_dir)
    successor_report = verify_completed(successor_dir)
    null_a_report = verify_completed(null_a_dir)
    parent_manifest = load_manifest(parent_dir)
    successor_manifest = load_manifest(successor_dir)
    parent_state = load_state(parent_dir, parent_manifest)
    successor_state = load_state(successor_dir, successor_manifest)
    successor_raw = json.loads(
        (successor_dir / successor_manifest["artifacts"]["raw_result"]).read_text()
    )
    instrument_path = successor_dir / successor_manifest["artifacts"]["instrument_result"]
    instrument_raw = json.loads(instrument_path.read_text())
    null_a_manifest = load_manifest(null_a_dir)
    null_a_raw = json.loads(
        (null_a_dir / null_a_manifest["artifacts"]["raw_result"]).read_text()
    )
    amendment = yaml.safe_load(amendment_path.read_text())["protocol_amendment"]

    require(amendment["id"] == "AMD-20260718-003", "wrong amendment")
    require(amendment["confirmatory_status"] == "preserved",
            "confirmatory status was not preserved")
    require(successor_manifest["continues"] == parent_manifest["id"],
            "successor/parent lineage mismatch")
    require(successor_manifest["preregistration"].endswith(amendment_path.name),
            "successor does not cite the continuation amendment")
    require(sha256(instrument_path)
            == successor_manifest["artifacts"]["sha256"]["instrument_result"],
            "instrument-result manifest hash mismatch")
    require(sha256(instrument_path)
            == successor_raw["source_instrument_result"]["sha256"],
            "raw wrapper source hash mismatch")
    for key, value in instrument_raw.items():
        require(successor_raw.get(key) == value,
                f"raw wrapper changed instrument metric: {key}")
    require(successor_raw["certificate"]["kind"] == "none",
            "pure measurement raw result lacks certificate.kind=none")
    require(successor_manifest["result"]["certificate"]["kind"] == "none",
            "pure measurement manifest lacks certificate.kind=none")

    frozen = amendment["parent_checkpoint"]
    require(sha256(parent_dir / parent_manifest["artifacts"]["checkpoints"] / "state.json")
            == frozen["state_sha256"], "parent state no longer matches amendment")
    parent_adj = parent_dir / "work" / (
        "h012c_adj_null_n17_t3_i0_D5_s2026_5deee45d29ace465.pkl"
    )
    require(sha256(parent_adj) == frozen["adjacency_cache_sha256"],
            "parent adjacency cache mismatch")
    require(parent_state["next_col"] == frozen["next_col"],
            "parent checkpoint boundary mismatch")
    require(parent_state["ncols"] == frozen["ncols"],
            "parent total-column mismatch")

    parent_copy = successor_dir / successor_manifest["artifacts"]["parent_checkpoint_state"]
    require(sha256(parent_copy) == frozen["state_sha256"],
            "successor parent-state receipt mismatch")
    prelaunch = json.loads(
        (successor_dir / successor_manifest["artifacts"]["prelaunch_verification"]).read_text()
    )
    require(prelaunch["gate"] == "pass", "prelaunch gate did not pass")
    require(prelaunch["state_sha256"] == frozen["state_sha256"],
            "prelaunch state hash mismatch")
    require(prelaunch["adjacency_cache_sha256"] == frozen["adjacency_cache_sha256"],
            "prelaunch adjacency hash mismatch")
    successor_adj = successor_dir / successor_manifest["artifacts"]["adjacency_cache"]
    require(sha256(successor_adj) == frozen["adjacency_cache_sha256"],
            "successor adjacency cache mismatch")

    require(successor_state["done"] is True, "successor checkpoint is incomplete")
    require(successor_state["next_col"] == successor_state["ncols"] == frozen["ncols"],
            "successor did not reach the frozen terminal column")
    require(successor_state["system_hash"] == frozen["system_hash"],
            "successor system identity mismatch")
    require(successor_state["units"][:len(parent_state["units"])] == parent_state["units"],
            "successor did not preserve the parent unit prefix")
    require(successor_state["carries"][:len(parent_state["carries"])]
            == parent_state["carries"], "successor did not preserve parent carriers")

    added_units = successor_state["units"][len(parent_state["units"]):]
    require(len(added_units) > 0, "successor added no work units")
    cursor = frozen["next_col"]
    for unit in added_units:
        require(unit["j0"] == cursor, "continuation unit interval is not contiguous")
        require(unit["j1"] > unit["j0"], "empty continuation unit")
        require(unit["j1"] <= frozen["ncols"], "continuation exceeded frozen columns")
        cursor = unit["j1"]
    require(cursor == frozen["ncols"], "continuation interval is incomplete")

    equal_fields = (
        "system_hash", "n", "ti", "d", "nb", "nrows", "ncols",
        "pred", "rank", "deficit", "status",
    )
    equality = {name: successor_raw[name] == null_a_raw[name] for name in equal_fields}
    require(successor_raw["which"] == null_a_raw["which"] == "null",
            "comparison arms are not null")
    require(all(equality.values()), f"NULL-A/B mismatch: {equality}")

    return {
        "status": "continuation_and_null_partition_verified",
        "amendment": amendment["id"],
        "parent": parent_report,
        "successor": successor_report,
        "null_a": null_a_report,
        "added_column_interval": [frozen["next_col"], frozen["ncols"]],
        "added_units": len(added_units),
        "null_partition_equal_fields": equality,
        "timing_interpretation": "excluded_by_amendment",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parent", type=Path)
    parser.add_argument("successor", type=Path)
    parser.add_argument("amendment", type=Path)
    parser.add_argument("null_a", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(
        verify(args.parent, args.successor, args.amendment, args.null_a),
        indent=2,
        sort_keys=True,
    ) + "\n"
    if args.output is not None:
        args.output.write_text(report)
    print(report, end="")


if __name__ == "__main__":
    main()
