"""One-trial adapter for the frozen prime63 panel and standard supervisor.

The supervisor owns launch.json, command/environment/logs, and receipt. This
driver owns only the three declared panel artifacts after in-flight admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import execute


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def run(plan: Path, owner: str, epoch: int, trial_id: str, run_dir: Path,
        *, root: Path = execute.ROOT) -> dict:
    # Every additional output follows a fresh repository authorization and
    # exact supervisor launch check. create_panel repeats this before Sage.
    authority = execute.admit(plan, owner, epoch, root=root,
                              run_dir=run_dir, trial_id=trial_id)
    if any((run_dir / name).exists() for name in
           ("panel", "raw-result.json", "manifest.yaml", "raw.tar.gz")):
        raise execute.execution.ExecutionError("second panel attempt or partial output exists")
    panel = execute.create_panel(plan, owner, epoch, run_dir, trial_id)
    archive = run_dir / "panel/raw.tar.gz"
    with (run_dir / "raw.tar.gz").open("xb") as stream:
        stream.write(archive.read_bytes())
    raw = {"schema": "icperf-prime63-one-trial-v1",
           "experiment_id": authority["plan"]["experiment_id"],
           "trial_id": trial_id, "run_id": authority["run_id"],
           "plan_sha256": authority["plan_sha256"],
           "launch_sha256": authority["launch_sha256"],
           "panel_receipt_sha256": digest(run_dir / "panel/receipt.json"),
           "raw_archive_sha256": digest(run_dir / "raw.tar.gz"),
           "attempted": panel["attempted"], "unattempted": panel["unattempted"],
           "cells": panel["cells"], "scientific_conclusion": None}
    write_once(run_dir / "raw-result.json", raw)
    manifest = {"run": {
        "id": authority["run_id"], "experiment_id": authority["plan"]["experiment_id"],
        "status": "completed", "code": {
            "commit": authority["authorization"]["commit"],
            "command": " ".join(authority["plan"]["trials"][0]["argv"])},
        "environment": {"supervisor": "tools/experiment_execution.py",
                        "source_sha256": authority["plan"]["source_sha256"]},
        "inputs": {"trial_id": trial_id, "plan_sha256": authority["plan_sha256"],
                   "parameters": {"cells": 27}},
        "timing": {"wall_seconds": panel["wall_seconds"]},
        "result": {"raw_result": "raw-result.json",
                   "certificate": {"kind": "none"},
                   "attempted": panel["attempted"], "unattempted": panel["unattempted"]}}}
    write_once(run_dir / "manifest.yaml", manifest)  # canonical JSON is YAML
    return raw


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--owner", required=True)
    p.add_argument("--epoch", required=True, type=int)
    p.add_argument("--trial-id", required=True)
    p.add_argument("--run-dir", required=True, type=Path)
    a = p.parse_args()
    result = run(a.plan, a.owner, a.epoch, a.trial_id, a.run_dir)
    print(json.dumps({"status": "recorded", "attempted": result["attempted"],
                      "unattempted": result["unattempted"]}, sort_keys=True))


if __name__ == "__main__":
    main()
