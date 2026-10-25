"""Run canned fixtures through the real supervisor after source-tree binding."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import experiment_execution  # noqa: E402

SOURCE_FILES = ("execute.py", "check.py", "output_contract.py", "fixture_supervisor.py",
                "test_output_contract.py", "input_manifest.json", "output-contract.json", "README.md")

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_hashes():
    return {name: sha(HERE / name) for name in SOURCE_FILES}

def verify_source_commit(commit: str, hashes: dict[str, str]) -> None:
    """Require a reachable commit whose tree contains exactly our current bytes."""
    if subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, "HEAD"], check=False).returncode:
        raise ValueError("source commit is not reachable from HEAD")
    for name, expected in hashes.items():
        path = (HERE / name).relative_to(ROOT).as_posix()
        shown = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"], capture_output=True, check=False)
        if shown.returncode or hashlib.sha256(shown.stdout).hexdigest() != expected:
            raise ValueError(f"source commit does not contain exact {name}")

def _fixture(root: Path, mode: str, source_commit: str, source: dict[str, str]):
    spec = root / "experiments/EXP-ICPERF-fixture"
    spec.mkdir(parents=True)
    specification = spec / "specification.yaml"
    specification.write_text("fixture: true\nno_science: true\n", encoding="utf-8")
    trial = {"id": "fixture-" + mode, "run_id": "RUN-ICPERF-abcdef",
             "argv": [sys.executable, str(HERE / "execute.py"), "--run-dir", "{run_dir}", "--mode", mode],
             "check_argv": [sys.executable, str(HERE / "check.py"), "--run-dir", "{run_dir}"],
             "artifacts": ["manifest.yaml", "raw-result.json"], "allow_empty_artifacts": [],
             "memory_mb": 64, "watchdog_seconds": 20, "watchdog_reason": "fixture process bound"}
    plan = {"schema": "crypto.autoresearch.trial_plan.v1", "experiment_id": "EXP-ICPERF-fixture",
            "task_id": "TASK-20261020-f237a2", "specification": "experiments/EXP-ICPERF-fixture/specification.yaml",
            "specification_sha256": sha(specification),
            "source_sha256": {str((HERE / name).relative_to(ROOT)): digest for name, digest in source.items()},
            "trials": [trial]}
    plan_path = root / "fixture-plan.json"
    plan_path.write_text(json.dumps(plan, sort_keys=True) + "\n", encoding="utf-8")
    authority = {"owner": "fixture-authority", "epoch": 1, "commit": source_commit,
                 "expires_at": "2999-01-01T00:00:00+00:00"}
    status = experiment_execution.execute_trial(root, plan_path, plan, trial, authority, os.open("/dev/null", os.O_RDONLY))
    directory = experiment_execution.run_root(root, plan, trial)
    receipt = json.loads((directory / "execution-receipt.json").read_text())
    manifest = json.loads((directory / "manifest.yaml").read_text())
    if manifest["run"]["code"]["commit"] != source_commit or manifest["run"]["inputs"]["plan_sha256"] != sha(plan_path):
        raise ValueError("fixture manifest failed source/plan binding")
    return directory, {"mode": mode, "status": status, "receipt_status": receipt["status"],
                       "artifact_sha256": receipt["artifact_sha256"], "raw_member_sha256": raw_members(directory),
                       "manifest_sha256": sha(directory / "manifest.yaml"), "raw_result_sha256": sha(directory / "raw-result.json")}

def raw_members(directory: Path) -> dict[str, str]:
    receipt = json.loads((directory / "diagnostic" / "receipt.json").read_text())
    return {row["path"]: row["sha256"] for row in receipt["raw_members"]}

def run(mode: str, source_commit: str, capture: Path | None = None):
    source = source_hashes(); verify_source_commit(source_commit, source)
    with tempfile.TemporaryDirectory(prefix="icperf-v2-fixture-") as temporary:
        directory, report = _fixture(Path(temporary), mode, source_commit, source)
        if capture is not None: shutil.copytree(directory, capture / mode)
        return report

def build(out: Path, source_commit: str):
    out.mkdir(parents=True, exist_ok=True)
    source = source_hashes(); verify_source_commit(source_commit, source)
    with tempfile.TemporaryDirectory(prefix="icperf-v2-custody-") as temporary:
        capture = Path(temporary) / "raw"; capture.mkdir()
        results = [run(mode, source_commit, capture) for mode in ("bounded-censor", "canned-positive")]
        tar = out / "fixture-custody.tar.gz"
        with tarfile.open(tar, "w:gz") as archive: archive.add(capture, arcname="raw")
        report = {"schema": "icperf-prime63-m2-output-contract-v2-fixture-report-v2",
                  "task_id": "TASK-20261020-f237a2", "fixture_only": True, "scientific_execution": False,
                  "source_commit": source_commit, "source_sha256": source,
                  "commands": ["fixture_supervisor.run(bounded-censor)", "fixture_supervisor.run(canned-positive)"],
                  "supervisor_results": results, "custody_tar_sha256": sha(tar),
                  "limits": "Fixture authority is not production admission; no solver or scientific trial was invoked."}
        (out / "fixture-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--out", type=Path, required=True); parser.add_argument("--source-commit", required=True)
    args = parser.parse_args(); print(json.dumps(build(args.out, args.source_commit), sort_keys=True))
