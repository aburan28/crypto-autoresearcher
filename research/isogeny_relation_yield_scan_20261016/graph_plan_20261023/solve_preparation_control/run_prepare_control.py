#!/usr/bin/env python3
"""Run the deterministic local control for finalist solve-stage preparation."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREPARER = HERE.parents[1] / "preparation/prepare_graph_solve_input.py"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    started = datetime.now(timezone.utc)
    t0 = time.monotonic()
    spec = importlib.util.spec_from_file_location("prepare_graph_solve_input", PREPARER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    roots = [hashlib.sha256(label.encode()).digest()
             for label in ("base-control", "target-control", "verifier-control")]
    arms = []
    for arm in ("low_x", "mid_x", "random_x"):
        payload, metadata = module.prepare(
            module.STUDY / "walk-p37-256.jsonl", 0, arm, *roots)
        if len(payload.splitlines()) != 1 + 2 * metadata["base_abscissae"] + 32768:
            raise AssertionError("prepared row count differs")
        arms.append({"arm": arm, "Q": metadata["Q"],
                     "base_sha256": metadata["base_sha256"],
                     "target_vector_sha256": metadata["target_vector_sha256"],
                     "input_sha256": metadata["input_sha256"],
                     "target_count": metadata["target_count"],
                     "base_x_orbits": metadata["base_abscissae"],
                     "payload_bytes": len(payload)})
    if len({tuple(row["Q"]) for row in arms}) != 1:
        raise AssertionError("the paired arms do not use the same Q")
    if len({row["target_vector_sha256"] for row in arms}) != 1:
        raise AssertionError("the paired arms do not use the same target vector")
    if len({row["base_sha256"] for row in arms}) != 3:
        raise AssertionError("factor-base treatments are not distinct")
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT,
                                    text=True).splitlines()
    result = {
        "schema": "ectd.graph-solve-preparation-control/v1",
        "mode": "local_implementation_control",
        "started_utc": started.isoformat(),
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "wall_seconds": time.monotonic() - t0,
        "process_cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime +
                               resource.getrusage(resource.RUSAGE_SELF).ru_stime,
        "peak_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "platform": platform.platform(), "python": sys.version,
        "command": "python3 research/isogeny_relation_yield_scan_20261016/graph_plan_20261023/solve_preparation_control/run_prepare_control.py",
        "git_head": git_head, "git_dirty_paths_at_start": dirty,
        "walk": "research/isogeny_relation_yield_scan_20261016/walk-p37-256.jsonl",
        "vertex_index": 0, "stage": "solve", "target_count_per_arm": 32768,
        "root_sha256": {label: sha(value) for label, value in
                         zip(("base", "target", "verifier"), roots)},
        "paired_same_Q": True, "paired_same_target_vector": True,
        "distinct_factor_bases": True, "arms": arms,
        "limits": "preparation only; no relation collector, rank solver, DLP solve, or rho run",
    }
    out = HERE / "result.json"
    with out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
