#!/usr/bin/env python3
"""Executable successor to EXP-XOR-62b256 with an internal replay control.

The predecessor implementation is executed twice inside one authorized top-level
command.  Scientific payloads are compared after removing wall-clock observations,
which are provenance rather than deterministic algorithm output.  Only the first
pass is retained as the run result.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
PREDECESSOR = ROOT / "experiments/EXP-XOR-62b256/implementation/arm_d_cost.py"
EXPECTED_PREDECESSOR_SHA256 = (
    "c8c8e7df68f9d761a5caed663e8d3448765a1ea2cc779e76a626adc0a7a6caf7"
)
EXPERIMENT_ID = "EXP-XOR-019343"


def load_predecessor():
    observed = hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest()
    if observed != EXPECTED_PREDECESSOR_SHA256:
        raise RuntimeError(
            f"predecessor hash mismatch: {observed} != {EXPECTED_PREDECESSOR_SHA256}"
        )
    spec = importlib.util.spec_from_file_location("arm_d_cost_predecessor", PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module, observed


def scientific_payload(value):
    """Remove only explicitly nondeterministic timing observations."""
    if isinstance(value, dict):
        return {
            key: scientific_payload(item)
            for key, item in value.items()
            if key != "wall_clock_seconds"
        }
    if isinstance(value, list):
        return [scientific_payload(item) for item in value]
    return value


def canonical_bytes(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def run(output: Path) -> None:
    module, predecessor_sha256 = load_predecessor()
    with tempfile.TemporaryDirectory(prefix="exp-xor-019343-") as temporary:
        temporary_root = Path(temporary)
        first_dir = temporary_root / "first"
        replay_dir = temporary_root / "replay"
        module.run(first_dir)
        module.run(replay_dir)

        first_raw = json.loads((first_dir / "raw-result.json").read_text())
        replay_raw = json.loads((replay_dir / "raw-result.json").read_text())
        first_scientific = scientific_payload(first_raw)
        replay_scientific = scientific_payload(replay_raw)
        first_bytes = canonical_bytes(first_scientific)
        replay_bytes = canonical_bytes(replay_scientific)
        deterministic_match = first_bytes == replay_bytes
        if not deterministic_match:
            raise RuntimeError("scientific payload differs across internal replay")

        analysis = yaml.safe_load((first_dir / "analysis.yaml").read_text())
        environment = json.loads((first_dir / "environment.json").read_text())

    implementation_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    raw = copy.deepcopy(first_raw)
    raw.update(
        {
            "schema": "exp-xor-019343-raw-v1",
            "experiment_id": EXPERIMENT_ID,
            "protocol_predecessor": "EXP-XOR-62b256",
            "predecessor_implementation_sha256": predecessor_sha256,
            "implementation_sha256": implementation_sha256,
            "determinism_control": {
                "method": "two complete evaluations inside one top-level invocation",
                "excluded_fields": ["wall_clock_seconds"],
                "scientific_payload_match": deterministic_match,
                "scientific_payload_sha256": hashlib.sha256(first_bytes).hexdigest(),
                "replay_scientific_payload_sha256": hashlib.sha256(replay_bytes).hexdigest(),
            },
        }
    )
    analysis = copy.deepcopy(analysis)
    analysis.update(
        {
            "schema": "exp-xor-019343-analysis-v1",
            "experiment_id": EXPERIMENT_ID,
            "protocol_predecessor": "EXP-XOR-62b256",
        }
    )
    analysis.setdefault("controls", {})["scientific_payload_replay_match"] = (
        deterministic_match
    )
    analysis["determinism_control"] = raw["determinism_control"]
    environment.update(
        {
            "experiment_id": EXPERIMENT_ID,
            "implementation_sha256": implementation_sha256,
            "predecessor_implementation_sha256": predecessor_sha256,
        }
    )

    output.mkdir(parents=True, exist_ok=True)
    (output / "raw-result.json").write_text(
        json.dumps(raw, indent=2, default=str) + "\n", encoding="utf-8"
    )
    (output / "analysis.yaml").write_text(
        yaml.safe_dump(analysis, sort_keys=False), encoding="utf-8"
    )
    (output / "environment.json").write_text(
        json.dumps(environment, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
