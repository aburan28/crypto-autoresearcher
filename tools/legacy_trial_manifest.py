#!/usr/bin/env python3
"""Run a bound legacy worksheet unchanged and add a native run envelope.

The new plan's ``legacy_trial`` mapping names an old trial plan, its SHA256,
trial/experiment/run IDs, ``input_seed`` (which may honestly be null),
``input_seed_semantics`` and ``curve_id``. Both old and new source closures
must match their frozen bytes. The legacy raw result and manifest are copied
byte for byte; only a new outer manifest carries the new experiment/run IDs.

Admission and ownership remain the native supervisor's responsibility. This
tool requires its launch.json/environment.json/command.txt and never makes
model attestations, mathematical certificates or scientific status changes.
The minimum native manifest permits seed:null; the separate JSON schema's
integer-only seed declaration is not changed by this adapter.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ("manifest.yaml", "raw-result.json", "legacy-manifest.yaml", "legacy-execution.json")
PROVENANCE = ("launch.json", "environment.json", "command.txt")
SELF = "tools/legacy_trial_manifest.py"


class LegacyTrialError(ValueError):
    pass


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LegacyTrialError(f"expected JSON object: {path}")
    return value


def inside(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise LegacyTrialError(f"expected repository-relative path: {name!r}")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise LegacyTrialError(f"path leaves checkout: {name}")
    return path


def checked_hash(path: Path, expected: Any) -> None:
    if (not isinstance(expected, str) or len(expected) != 64
            or any(c not in "0123456789abcdef" for c in expected)
            or not path.is_file() or sha(path) != expected):
        raise LegacyTrialError(f"bound file changed/missing: {path}")


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LegacyTrialError(f"expected YAML mapping: {path}")
    return value


def expand(argv: Any, directory: Path) -> list[str]:
    if (not isinstance(argv, list) or not argv
            or any(not isinstance(a, str) or not a or "\x00" in a for a in argv)):
        raise LegacyTrialError("command must be an argv array")
    return [a.replace("{run_dir}", str(directory)) for a in argv]


@dataclass
class Context:
    root: Path
    path: Path
    directory: Path
    plan: dict[str, Any]
    trial: dict[str, Any]
    block: dict[str, Any]
    old_path: Path
    old_plan: dict[str, Any]
    old_trial: dict[str, Any]
    old_spec: dict[str, Any]
    launch: dict[str, Any]
    environment: dict[str, Any]
    provenance_sha256: dict[str, str]


def context(root: Path, plan_path: Path, directory: Path) -> Context:
    root, plan_path, directory = root.resolve(), plan_path.resolve(), directory.resolve()
    if not plan_path.is_relative_to(root) or not directory.is_relative_to(root):
        raise LegacyTrialError("plan and run directory must be inside the checkout")
    plan = read_json(plan_path)
    block = plan.get("legacy_trial")
    if (plan.get("schema") != "crypto.autoresearch.trial_plan.v1"
            or plan.get("frozen") is not True or not isinstance(block, dict)):
        raise LegacyTrialError("requires a frozen native plan and legacy_trial mapping")
    for field in ("trial_plan", "trial_plan_sha256", "trial_id", "experiment_id", "run_id",
                  "input_seed", "input_seed_semantics", "curve_id"):
        if field not in block:
            raise LegacyTrialError(f"legacy_trial missing {field}")
    if block["input_seed"] is not None and type(block["input_seed"]) is not int:
        raise LegacyTrialError("input_seed must be an integer or null, never invented")
    if not isinstance(block["input_seed_semantics"], str) or not block["input_seed_semantics"].strip():
        raise LegacyTrialError("input_seed_semantics is required")
    if block["curve_id"] is not None and not isinstance(block["curve_id"], str):
        raise LegacyTrialError("curve_id must be an exact ID or null")
    old_path = inside(root, block["trial_plan"])
    checked_hash(old_path, block["trial_plan_sha256"])
    old_plan = read_json(old_path)
    if old_plan.get("frozen") is not True or old_plan.get("experiment_id") != block["experiment_id"]:
        raise LegacyTrialError("old frozen plan identity mismatch")
    old_trials = [t for t in old_plan.get("trials", []) if t.get("id") == block["trial_id"]]
    if len(old_trials) != 1 or old_trials[0].get("run_id") != block["run_id"]:
        raise LegacyTrialError("old trial/run identity mismatch")
    old_trial = old_trials[0]
    if set(old_trial.get("artifacts", [])) != {"manifest.yaml", "raw-result.json"}:
        raise LegacyTrialError("adapter only supports the two-artifact legacy worksheet contract")
    old_spec_path = inside(root, old_plan["specification"])
    checked_hash(old_spec_path, old_plan["specification_sha256"])
    old_spec = load_yaml(old_spec_path).get("experiment")
    if not isinstance(old_spec, dict) or old_spec.get("id") != block["experiment_id"]:
        raise LegacyTrialError("old specification identity mismatch")
    sources = plan.get("source_sha256")
    old_sources = old_plan.get("source_sha256")
    if not isinstance(sources, dict) or not isinstance(old_sources, dict) or not old_sources:
        raise LegacyTrialError("both plans must bind their complete source closure")
    required = {**old_sources, block["trial_plan"]: block["trial_plan_sha256"],
                old_plan["specification"]: old_plan["specification_sha256"]}
    if SELF not in sources:
        raise LegacyTrialError("new source closure must bind this adapter")
    for name, expected in required.items():
        if sources.get(name) != expected:
            raise LegacyTrialError(f"new closure does not bind old dependency: {name}")
    for name, expected in sources.items():
        checked_hash(inside(root, name), expected)
    checked_hash(inside(root, plan["specification"]), plan["specification_sha256"])
    launch = read_json(directory / "launch.json")
    environment = read_json(directory / "environment.json")
    trials = [t for t in plan.get("trials", []) if t.get("id") == launch.get("trial_id")]
    if len(trials) != 1:
        raise LegacyTrialError("supervisor launch does not select exactly one new trial")
    trial = trials[0]
    expected_dir = root / "experiments" / plan["experiment_id"] / "runs" / trial["run_id"]
    if directory != expected_dir or trial["run_id"] != launch.get("run_id"):
        raise LegacyTrialError("new run path/identity does not match supervisor")
    if trial["run_id"] == block["run_id"] or plan["experiment_id"] == block["experiment_id"]:
        raise LegacyTrialError("successor must use new outer EXP and RUN identities")
    if (launch.get("plan_sha256") != sha(plan_path)
            or launch.get("argv") != expand(trial.get("argv"), directory)
            or launch.get("check_argv") != expand(trial.get("check_argv"), directory)):
        raise LegacyTrialError("supervisor command/plan provenance mismatch")
    command = json.loads((directory / "command.txt").read_text(encoding="utf-8"))
    if command != launch["argv"]:
        raise LegacyTrialError("command.txt does not match supervisor argv")
    if (environment.get("source_sha256") != sources
            or environment.get("specification_sha256") != plan["specification_sha256"]
            or environment.get("commit") != launch.get("authority", {}).get("commit")):
        raise LegacyTrialError("supervisor environment/source provenance mismatch")
    commit = environment.get("commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise LegacyTrialError("supervisor has no execution commit")
    if set(trial.get("artifacts", [])) != set(OUTPUTS):
        raise LegacyTrialError("successor must declare exactly the four adapter artifacts")
    return Context(root, plan_path, directory, plan, trial, block, old_path, old_plan,
                   old_trial, old_spec, launch, environment,
                   {n: sha(directory / n) for n in PROVENANCE})


def write_once(path: Path, value: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(value)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def run_child(argv: list[str], root: Path) -> dict[str, Any]:
    if not hasattr(os, "wait4"):
        raise LegacyTrialError("accurate per-child resource receipt requires POSIX wait4")
    started = datetime.now(timezone.utc).isoformat()
    before = time.monotonic()
    child_env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    child = subprocess.Popen(argv, cwd=root, stdin=subprocess.DEVNULL, env=child_env)
    try:
        _, status, usage = os.wait4(child.pid, 0)
        child.returncode = os.waitstatus_to_exitcode(status)
    except BaseException:
        child.terminate()
        child.wait()
        raise
    return {"argv": argv, "environment_overrides": {"PYTHONDONTWRITEBYTECODE": "1"}, "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "wall_seconds": time.monotonic() - before,
            "returncode": child.returncode,
            "cpu_seconds": usage.ru_utime + usage.ru_stime,
            "peak_rss_bytes": int(usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024))}


def validate_legacy_outputs(c: Context) -> tuple[dict[str, Any], dict[str, Any]]:
    old_manifest = load_yaml(c.directory / "legacy-manifest.yaml")
    old_run = old_manifest.get("run")
    raw = read_json(c.directory / "raw-result.json")
    if (not isinstance(old_run, dict) or old_run.get("experiment_id") != c.block["experiment_id"]
            or old_run.get("run_id") != c.block["run_id"]
            or raw.get("experiment_id") != c.block["experiment_id"]
            or raw.get("run_id") != c.block["run_id"]):
        raise LegacyTrialError("preserved raw/manifest identities are not the original trial")
    if old_run.get("attack_claimed") is not False or raw.get("attack_claimed") is not False:
        raise LegacyTrialError("metadata adapter cannot promote an attack claim")
    if not isinstance(old_run.get("metrics"), dict):
        raise LegacyTrialError("old manifest has no original metric mapping")
    return old_run, raw


def canonical_manifest(c: Context, receipt: dict[str, Any], old_run: dict[str, Any]) -> dict[str, Any]:
    parameters = {"legacy_inputs": c.old_spec.get("inputs"),
                  "legacy_experiment_id": c.block["experiment_id"],
                  "legacy_run_id": c.block["run_id"],
                  "legacy_trial_plan": c.block["trial_plan"],
                  "legacy_trial_plan_sha256": c.block["trial_plan_sha256"],
                  "input_seed_semantics": c.block["input_seed_semantics"],
                  "attack_claimed": False,
                  "prediction_scope": "original frozen predictions; calibration/reproduction only"}
    return {"run": {
        "id": c.trial["run_id"], "experiment_id": c.plan["experiment_id"],
        "status": "completed_valid",
        "code": {"commit": c.environment["commit"], "dirty": receipt["dirty"],
                 "command": (c.directory / "command.txt").read_text(encoding="utf-8").strip()},
        "environment": {"supervisor": c.environment,
                        "supervisor_launch_sha256": receipt["supervisor_sha256"]["launch.json"],
                        "working_directory": str(c.root),
                        "timing_boundary": "adapter interval from before scratch-directory creation through legacy driver, original checker, output copying and pre-envelope validation/provenance checks; excludes canonical envelope emission and native supervisor checker phase",
                        "resource_boundary": "driver plus pre-envelope checker per-child CPU; maximum of their per-process RSS peaks, not process-group peak",
                        "metadata_adapter": SELF,
                        "adapter_runtime": receipt["runtime"],
                        "inference": "no inference performed or attested by this adapter"},
        "inputs": {"curve_id": c.block["curve_id"], "seed": c.block["input_seed"],
                   "parameters": parameters},
        "timing": receipt["timing"],
        "resources": {"peak_rss_bytes": max(p["peak_rss_bytes"] for p in receipt["phases"]),
                      "cpu_seconds": sum(p["cpu_seconds"] for p in receipt["phases"])},
        "result": {"metrics": old_run["metrics"], "valid": True, "invalid_reason": None,
                   "certificate": {"kind": "none", "verified": None, "verifier": None}},
        "artifacts": {n: {"sha256": sha(c.directory / n)} for n in
                      ("raw-result.json", "legacy-manifest.yaml", "legacy-execution.json")}
    }}


def execute(plan_path: Path, directory: Path, *, root: Path = ROOT) -> None:
    c = context(root, plan_path, directory)
    if any((directory / n).exists() for n in OUTPUTS):
        raise LegacyTrialError("adapter outputs already exist; preserve attempt and allocate a new run")
    status = subprocess.run(["git", "-C", str(c.root), "status", "--porcelain", "--untracked-files=normal"],
                            capture_output=True, text=True, check=True)
    receipt: dict[str, Any] = {"schema": "crypto.autoresearch.legacy_execution.v1",
        "new_experiment_id": c.plan["experiment_id"], "new_run_id": c.trial["run_id"],
        "new_plan_sha256": sha(c.path), "legacy_trial": c.block,
        "source_sha256": c.plan["source_sha256"], "supervisor_sha256": c.provenance_sha256,
        "runtime": {"python": sys.version, "pyyaml": yaml.__version__},
        "dirty": bool(status.stdout), "dirty_scope": "whole worktree at adapter start, including supervisor-created run artifacts",
        "phases": [], "output_sha256": {}, "status": "started"}
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    failure: BaseException | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="legacy-trial-", dir=c.directory) as temporary:
            scratch = Path(temporary)
            receipt["legacy_scratch_directory"] = str(scratch)
            try:
                driver = run_child(expand(c.old_trial["argv"], scratch), c.root)
                receipt["phases"].append({"kind": "original_driver", **driver})
                if driver["returncode"] != 0:
                    raise LegacyTrialError(f"original driver failed: {driver['returncode']}")
                checker = run_child(expand(c.old_trial["check_argv"], scratch), c.root)
                receipt["phases"].append({"kind": "original_checker", **checker})
                if checker["returncode"] != 0:
                    raise LegacyTrialError(f"original checker failed: {checker['returncode']}")
            finally:
                # Even failed outputs survive; never relabel or rewrite their bytes.
                for old_name, new_name in (("manifest.yaml", "legacy-manifest.yaml"),
                                           ("raw-result.json", "raw-result.json")):
                    file = scratch / old_name
                    if file.is_file():
                        data = file.read_bytes()
                        write_once(c.directory / new_name, data)
                        receipt["output_sha256"][new_name] = hashlib.sha256(data).hexdigest()
        old_run, _ = validate_legacy_outputs(c)
        refreshed = context(root, plan_path, directory)
        if refreshed.provenance_sha256 != c.provenance_sha256:
            raise LegacyTrialError("supervisor provenance changed during legacy computation")
        receipt["status"] = "original_outputs_checked"
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        failure = exc
        receipt["status"] = "failed"
        receipt["failure"] = str(exc)
    finally:
        receipt["timing"] = {"started_at": started,
                             "finished_at": datetime.now(timezone.utc).isoformat(),
                             "wall_seconds": time.monotonic() - begin}
        write_once(c.directory / "legacy-execution.json", json_bytes(receipt))
    if failure is not None:
        raise LegacyTrialError(str(failure))
    manifest = canonical_manifest(c, receipt, old_run)
    write_once(c.directory / "manifest.yaml", yaml.safe_dump(manifest, sort_keys=False).encode())


def check(plan_path: Path, directory: Path, *, root: Path = ROOT) -> None:
    c = context(root, plan_path, directory)
    receipt = read_json(directory / "legacy-execution.json")
    expected = {"schema": "crypto.autoresearch.legacy_execution.v1",
                "new_experiment_id": c.plan["experiment_id"], "new_run_id": c.trial["run_id"],
                "new_plan_sha256": sha(c.path), "legacy_trial": c.block,
                "source_sha256": c.plan["source_sha256"], "supervisor_sha256": c.provenance_sha256,
                "status": "original_outputs_checked"}
    if any(receipt.get(k) != v for k, v in expected.items()):
        raise LegacyTrialError("legacy execution receipt binding mismatch")
    for name in ("legacy-manifest.yaml", "raw-result.json"):
        checked_hash(directory / name, receipt.get("output_sha256", {}).get(name))
    phases = receipt.get("phases")
    if (not isinstance(phases, list) or [p.get("kind") for p in phases] != ["original_driver", "original_checker"]
            or any(p.get("returncode") != 0 for p in phases)):
        raise LegacyTrialError("original driver/checker did not both finish successfully")
    scratch = Path(receipt.get("legacy_scratch_directory", "")).resolve()
    if scratch.parent != c.directory or not scratch.name.startswith("legacy-trial-"):
        raise LegacyTrialError("legacy execution scratch directory is outside this attempt")
    for phase, command in zip(phases, (c.old_trial["argv"], c.old_trial["check_argv"])):
        if (phase.get("argv") != expand(command, scratch)
                or phase.get("environment_overrides") != {"PYTHONDONTWRITEBYTECODE": "1"}):
            raise LegacyTrialError("legacy phase command/provenance changed")
        for name in ("wall_seconds", "cpu_seconds", "peak_rss_bytes"):
            value = phase.get(name)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise LegacyTrialError(f"invalid measured legacy phase resource: {name}")
    if type(receipt.get("dirty")) is not bool:
        raise LegacyTrialError("legacy execution must record actual dirty state")
    timing = receipt.get("timing", {})
    for name in ("started_at", "finished_at"):
        stamp = datetime.fromisoformat(timing.get(name, ""))
        if stamp.tzinfo is None:
            raise LegacyTrialError("legacy timing requires timezone-aware timestamps")
    old_run, _ = validate_legacy_outputs(c)
    actual = load_yaml(directory / "manifest.yaml")
    if actual != canonical_manifest(c, receipt, old_run):
        raise LegacyTrialError("canonical envelope differs from bound original outputs/provenance")
    with tempfile.TemporaryDirectory(prefix="legacy-check-") as temporary:
        scratch = Path(temporary)
        write_once(scratch / "manifest.yaml", (directory / "legacy-manifest.yaml").read_bytes())
        write_once(scratch / "raw-result.json", (directory / "raw-result.json").read_bytes())
        completed = subprocess.run(expand(c.old_trial["check_argv"], scratch), cwd=c.root,
                                   stdin=subprocess.DEVNULL, check=False,
                                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if completed.returncode != 0:
            raise LegacyTrialError(f"original checker rejected preserved bytes: {completed.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "check"))
    parser.add_argument("--trial-plan", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        (execute if args.action == "run" else check)(args.trial_plan, args.run_dir)
    except (OSError, ValueError, subprocess.SubprocessError, yaml.YAMLError) as exc:
        print(f"legacy trial adapter refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
