"""Recreate one solve-stage control input and invoke its independent verifier."""
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
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STUDY = HERE.parents[1]
PREPARER = STUDY / "preparation/prepare_graph_solve_input.py"
VERIFIER = STUDY / "preparation/verify_prepared_graph.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    started = datetime.now(timezone.utc)
    timer = time.monotonic()
    roots = [hashlib.sha256(label.encode()).digest()
             for label in ("base-control", "target-control", "verifier-control")]
    spec = importlib.util.spec_from_file_location("prepare_graph_solve_input", PREPARER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    payload, metadata = module.prepare(STUDY / "walk-p37-256.jsonl", 0,
                                      "low_x", *roots)
    command = None
    with TemporaryDirectory(prefix="ectd-solve-verify-") as temp:
        directory = Path(temp)
        prepared = directory / "prepared.txt"
        manifest = directory / "manifest.json"
        prepared.write_bytes(payload)
        manifest.write_text(json.dumps(metadata, sort_keys=True))
        root_paths = []
        for label, value in zip(("base", "target", "verifier"), roots):
            path = directory / (label + ".hex")
            path.write_text(value.hex() + "\n")
            root_paths.append(path)
        command = [sys.executable, str(VERIFIER), "--prepared", str(prepared),
                   "--manifest", str(manifest), "--base-root", str(root_paths[0]),
                   "--target-root", str(root_paths[1]), "--verifier-root", str(root_paths[2])]
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        verifier = json.loads(process.stdout)
    if (metadata["stage"] != "solve" or metadata["target_count"] != 32768 or
            verifier.get("status") != "pass" or
            verifier.get("targets_checked") != metadata["target_count"] or
            verifier.get("deterministic_seed_replay") is not True):
        raise AssertionError("independent solve-stage preparation replay failed")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT,
                                    text=True).splitlines()
    result = {
        "schema": "ectd.graph-solve-preparation-replay-control/v1",
        "mode": "local_deterministic_control",
        "started_utc": started.isoformat(),
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "wall_seconds": time.monotonic() - timer,
        "process_cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime +
                               resource.getrusage(resource.RUSAGE_SELF).ru_stime,
        "command": "python3 research/isogeny_relation_yield_scan_20261016/graph_plan_20261023/solve_preparation_control/verify_control.py",
        "git_head": head, "git_dirty_paths_at_receipt": dirty,
        "platform": platform.platform(), "python": sys.version,
        "preparer_sha256": sha(PREPARER), "verifier_sha256": sha(VERIFIER),
        "input_sha256": metadata["input_sha256"],
        "root_sha256": {name: metadata[name + "_root_sha256"]
                        for name in ("base", "target", "verifier")},
        "verifier_result": verifier,
        "limits": "input identity/group replay only; no relation collection, rank solve, ECDLP or rho",
    }
    with (HERE / "verify-result.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
