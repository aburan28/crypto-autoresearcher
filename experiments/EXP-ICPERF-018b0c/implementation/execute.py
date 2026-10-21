"""Bounded k11 positive and natural solver stages for an admitted trial plan.

The public entry point is ``tools/experiment_execution.py`` through the
approved ``run`` workflow. This driver refuses a direct or unapproved launch.
It records observations and never decides a factor-base or ECDLP claim.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import psutil
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_k11_solver import collect  # noqa: E402
from tools.icperf_binary_root_certificate import certificate  # noqa: E402

EXPERIMENT = "EXP-ICPERF-018b0c"
HERE = ROOT / "experiments" / EXPERIMENT
SPEC = HERE / "specification.yaml"
INPUTS = HERE / "inputs"
POSITIVE_PATH = INPUTS / "positive_manifest.json"
TARGET_PATH = INPUTS / "target_manifest.json"
FORMULA_PATH = INPUTS / "formula_manifest.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
BASES = {
    "weighted": ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json",
    "local_random": ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json",
}
MIN_AVAILABLE_MEMORY = 10 * (1 << 30)
CALL_WALL = 300
CALL_RSS = 8 * (1 << 30)
CALL_MODELS = 64
PANEL_WALL = 25200
SEED = 20261017


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def write(path: Path, record: dict) -> None:
    with path.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def bundle_calls(run_dir: Path) -> dict:
    """Bind every retained call file to two fixed-name archive artifacts."""
    calls = run_dir / "calls"
    paths = sorted(path for path in calls.rglob("*") if path.is_file())
    if any(path.is_symlink() for path in calls.rglob("*")):
        raise ValueError("call tree contains a symlink")
    files = []
    bundle_path = run_dir / "calls.tar.gz"
    with bundle_path.open("xb") as sink:
        with gzip.GzipFile(fileobj=sink, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|") as archive:
                for path in paths:
                    relative = path.relative_to(run_dir).as_posix()
                    size = path.stat().st_size
                    digest = sha_file(path)
                    entry = tarfile.TarInfo(relative)
                    entry.size = size
                    entry.mtime = 0
                    entry.mode = 0o644
                    with path.open("rb") as source:
                        archive.addfile(entry, source)
                    files.append({"path": relative, "size_bytes": size,
                                  "sha256": digest})
    record = {"schema": "icperf-k11-call-tree-v1", "files": files,
              "bundle_path": bundle_path.name,
              "bundle_size_bytes": bundle_path.stat().st_size,
              "bundle_sha256": sha_file(bundle_path)}
    write(run_dir / "calls-manifest.json", record)
    return record


def approved_launch(run_dir: Path, step: str) -> tuple[dict, dict, dict, dict]:
    """Require the adapter's admitted launch, exact plan, approved spec and hashes."""
    if not run_dir.is_dir() or run_dir.parent.name != "runs":
        raise ValueError("run directory must be an existing adapter-created runs/<RUN-ID> directory")
    launch = read(run_dir / "launch.json")
    environment = read(run_dir / "environment.json")
    spec = yaml.safe_load(SPEC.read_text())["experiment"]
    if (spec["id"] != EXPERIMENT or spec["status"] not in ("approved", "running")
            or spec["frozen"] is not True or spec["execution_authorized"] is not True
            or not spec["approved_by"]):
        raise ValueError("experiment is not frozen and authorized")
    plan_path = ROOT / spec["input_bindings"]["trial_plan"]
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    if (sha(plan_bytes) != launch["plan_sha256"] or plan["experiment_id"] != EXPERIMENT
            or plan["approved_by"] != spec["approved_by"]
            or plan["specification_sha256"] != sha(SPEC.read_bytes())
            or launch["trial_id"] != step or launch["run_id"] != run_dir.name
            or launch["authority"]["commit"] != environment["commit"]):
        raise ValueError("admitted launch/plan/specification binding mismatch")
    trial = next((row for row in plan["trials"] if row["id"] == step), None)
    if trial is None or str(Path(__file__).relative_to(ROOT)) not in trial["argv"]:
        raise ValueError("trial plan does not bind this driver")
    for name, binding in spec["input_bindings"].items():
        if not isinstance(binding, dict) or "path" not in binding:
            continue
        path = Path(binding["path"])
        if not path.is_absolute():
            path = ROOT / path
        if sha(path.read_bytes()) != binding["sha256"]:
            raise ValueError(f"input binding mismatch: {name}")
    if sha(Path(__file__).read_bytes()) != plan["source_sha256"][str(Path(__file__).relative_to(ROOT))]:
        raise ValueError("driver source differs from frozen plan")
    return launch, environment, spec, plan


def prepare_call(raw_path: Path, raw_sha: str, packed_sha: str) -> bytes:
    packed = raw_path.read_bytes()
    if sha(packed) != packed_sha:
        raise ValueError("compressed formula hash mismatch")
    raw = gzip.decompress(packed)
    if sha(raw) != raw_sha:
        raise ValueError("raw formula hash mismatch")
    return raw


def certify(assignment: int, label: str, base: dict, chain: dict,
            arm: dict, target_index: int | None, channel: int) -> dict:
    checked = certificate(assignment, base, chain, arm)
    return {"schema": "icperf-k11-full-point-check-v1",
            "scope": "one exact signed-point and subgroup-row filter; no rank or ECDLP claim",
            "experiment_id": EXPERIMENT, "base_kind": label,
            "target_index": target_index, "channel": channel,
            "assignment_hex": hex(assignment), "result": checked}


def call(raw: bytes, arm: dict, label: str, base: dict, chain: dict,
         target_index: int | None, channel: int, solver: Path, call_dir: Path,
         remaining_panel_wall: float) -> dict:
    available = psutil.virtual_memory().available
    disk = shutil.disk_usage(call_dir.parent).free
    wall = min(CALL_WALL, remaining_panel_wall)
    reserve = CALL_MODELS * (len(raw) + max(1 << 20, arm["cnf_variables"] * 12)) + 10 * (1 << 20)
    host = {"available_memory_before_bytes": available, "free_disk_before_bytes": disk,
            "estimated_raw_output_reserve_bytes": reserve,
            "load_average_before": list(psutil.getloadavg()), "checked_at": now()}
    if available < MIN_AVAILABLE_MEMORY or disk < reserve:
        return {"status": "host_admission_stop", "host": host,
                "reason": "less than 10 GiB available memory or declared raw-output reserve"}
    if wall <= 0:
        return {"status": "panel_wall_censored", "host": host}
    wrapper_started = time.monotonic()
    point_filter_wall = point_filter_cpu = 0.0

    def timed_certify(assignment: int) -> dict:
        nonlocal point_filter_wall, point_filter_cpu
        wall_start, cpu_start = time.monotonic(), time.process_time()
        try:
            return certify(assignment, label, base, chain, arm, target_index, channel)
        finally:
            point_filter_wall += time.monotonic() - wall_start
            point_filter_cpu += time.process_time() - cpu_start

    try:
        result = collect(raw, arm["primary_variables"], solver, wall, CALL_RSS,
                         CALL_MODELS, SEED, call_dir, timed_certify)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return {"status": "infrastructure_or_input_failure", "host": host,
                "error_type": type(exc).__name__, "error": str(exc),
                "attempt_directory_exists": call_dir.exists()}
    result["host"] = host
    result["point_filter_wall_seconds"] = point_filter_wall
    result["point_filter_cpu_seconds"] = point_filter_cpu
    result["call_wrapper_wall_seconds"] = time.monotonic() - wrapper_started
    result["base_kind"] = label
    result["target_index"] = target_index
    result["channel"] = channel
    write(call_dir / "summary.json", result)
    return {"status": result["status"], "host": host,
            "summary_sha256": sha((call_dir / "summary.json").read_bytes()),
            "attempts": len(result["attempts"]),
            "total_wall_seconds": result["total_wall_seconds"],
            "call_dir": str(call_dir.relative_to(call_dir.parents[1]))}


def positive_stage(calls: Path, positive: dict, bases: dict, chain: dict,
                   solver: Path, begin: float) -> list[dict]:
    records = []
    for label in ("weighted", "local_random"):
        source = positive["controls"][label]["source_row"]
        synthetic = source["synthetic_control"]
        arm = {"kind": "torsion_phi", "base_dimension": 11, "offset": 4096,
               "primary_variables": 454,
               "cnf_variables": source["input_counts"]["cnf_variables"],
               "target_coordinate": synthetic["synthetic_target_phi"]}
        bound = dict(chain, selected_channel=0,
                     target_channels=[synthetic["synthetic_raw_target"]] * 4,
                     subgroup_target=synthetic["synthetic_projected_target"])
        control = positive["controls"][label]
        preparation_started = time.monotonic()
        raw = prepare_call(ROOT / control["formula_path"], control["formula_raw_sha256"],
                           control["formula_gzip_sha256"])
        decompression_wall = time.monotonic() - preparation_started
        outcome = call(raw, arm, label, bases[label], bound, None, 0,
                       solver, calls / f"positive_{label}", PANEL_WALL - (time.monotonic() - begin))
        records.append({"base_kind": label,
                        "input_decompression_wall_seconds": decompression_wall, **outcome})
        # Preserve both planted outcomes even when one cannot be admitted.
    return records


def natural_stage(calls: Path, formulas: dict, targets: dict, bases: dict,
                  chain: dict, solver: Path, begin: float,
                  previous: dict) -> list[dict]:
    positive = previous.get("calls", [])
    if len(positive) != 2 or any(row["status"] != "point_relation_certified" for row in positive):
        return [{"status": "gated_by_positive_controls", "reason": "both positive calls must certify"}]
    records = []
    by_key = {(arm["target_index"], arm["base_kind"], arm["channel"]): arm
              for arm in formulas["arms"]}
    assert len(by_key) == 64
    remaining = PANEL_WALL - float(previous["total_wall_seconds"])
    for index, target in enumerate(targets["admitted"]):
        order = ("weighted", "local_random") if index % 2 == 0 else ("local_random", "weighted")
        for label in order:
            for channel in range(4):
                arm = by_key[index, label, channel]
                preparation_started = time.monotonic()
                raw = prepare_call(ROOT / arm["gzip_path"], arm["raw_xcnf_sha256"],
                                   arm["gzip_sha256"])
                decompression_wall = time.monotonic() - preparation_started
                bound = dict(chain, selected_channel=channel,
                             target_channels=target["raw_channels"],
                             subgroup_target=target["subgroup_point"])
                spent = time.monotonic() - begin
                outcome = call(raw, arm, label, bases[label], bound, index, channel,
                               solver, calls / f"natural_{index:02d}_{label}_channel_{channel}",
                               remaining - spent)
                records.append({"base_kind": label, "target_index": index,
                                "channel": channel,
                                "input_decompression_wall_seconds": decompression_wall,
                                **outcome})
                if outcome["status"] in ("host_admission_stop", "panel_wall_censored",
                                         "infrastructure_or_input_failure", "invalid_model_or_certificate",
                                         "solver_launch_failure", "solver_failure_or_unclassified"):
                    return records
    return records


def manifest(run_dir: Path, launch: dict, environment: dict, result: dict,
             solver: Path, started_at: str, wall: float) -> dict:
    status = ("failed_infrastructure" if result["status"] in
              ("host_admission_stop", "infrastructure_or_input_failure") else "completed")
    return {"run": {"id": launch["run_id"], "experiment_id": EXPERIMENT,
                    "status": status,
                    "code": {"commit": environment["commit"],
                             "command": launch["argv"],
                             "source_sha256": environment["source_sha256"]},
                    "environment": {"python": sys.version,
                                    "platform": platform.platform(),
                                    "psutil_version": psutil.__version__,
                                    "solver_path": str(solver),
                                    "solver_sha256": sha(solver.read_bytes()),
                                    "solver_version": subprocess.run([str(solver), "--version"],
                                                                      capture_output=True, text=True,
                                                                      timeout=10).stdout.strip(),
                                    "one_solver_process_at_a_time": True},
                    "inputs": {"parameters": {"field_bits": 61, "subgroup_order": 576460752557211763,
                                               "summands": 8, "factor_base_columns": 316,
                                               "target_count": 8, "channels_per_target": 4,
                                               "solver_seed": SEED, "call_wall_seconds": CALL_WALL,
                                               "sampled_rss_bytes": CALL_RSS,
                                               "max_primary_models": CALL_MODELS},
                               "target_manifest_sha256": sha(TARGET_PATH.read_bytes()),
                               "positive_manifest_sha256": sha(POSITIVE_PATH.read_bytes()),
                               "formula_manifest_sha256": sha(FORMULA_PATH.read_bytes())},
                    "timing": {"started_at": started_at, "finished_at": now(),
                               "wall_seconds": wall},
                    "result": {"raw_result": "raw-result.json", "outcome": result["status"],
                               "certificate": {"kind": "none", "verified": False},
                               "scope": "bounded solver and full-point observations, no complete ECDLP cost claim"}}}


def main() -> None:
    if sys.flags.optimize:
        raise ValueError("optimized Python disables scientific validation assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True, choices=("positive", "natural"))
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--positive-run-dir", type=Path)
    args = parser.parse_args()
    if (args.step == "positive") == (args.positive_run_dir is not None):
        parser.error("--positive-run-dir is required exactly for natural")
    run_dir = args.run_dir.resolve()
    launch, environment, spec, plan = approved_launch(run_dir, args.step)
    solver = Path(spec["input_bindings"]["solver_binary"]["path"])
    started_at, begin = now(), time.monotonic()
    bases = {label: read(path) for label, path in BASES.items()}
    chain = read(CHAIN)
    calls = run_dir / "calls"
    calls.mkdir(exist_ok=False)
    if args.step == "positive":
        observations = positive_stage(calls, read(POSITIVE_PATH), bases, chain, solver, begin)
    else:
        positive_trial = next((trial for trial in plan["trials"] if trial["id"] == "positive"), None)
        natural_trial = next((trial for trial in plan["trials"] if trial["id"] == "natural"), None)
        if (positive_trial is None or natural_trial is None
                or "positive" not in natural_trial.get("depends_on", [])
                or args.positive_run_dir.resolve() != run_dir.parent / positive_trial["run_id"]):
            raise ValueError("natural stage is not bound to the planned positive dependency")
        prior_receipt = read(args.positive_run_dir / "execution-receipt.json")
        if (prior_receipt.get("status") != "output_validated"
                or prior_receipt.get("plan_sha256") != launch["plan_sha256"]
                or prior_receipt.get("run_id") != positive_trial["run_id"]
                or prior_receipt.get("artifact_sha256", {}).get("raw-result.json")
                != sha((args.positive_run_dir / "raw-result.json").read_bytes())):
            raise ValueError("positive dependency receipt or raw-result binding mismatch")
        previous = read(args.positive_run_dir / "raw-result.json")
        if (previous["step"] != "positive" or previous["experiment_id"] != EXPERIMENT
                or previous["plan_sha256"] != launch["plan_sha256"]):
            raise ValueError("wrong positive dependency")
        observations = natural_stage(calls, read(FORMULA_PATH), read(TARGET_PATH),
                                     bases, chain, solver, begin, previous)
    stopping = next((row["status"] for row in observations if row["status"] in
                     ("host_admission_stop", "panel_wall_censored", "infrastructure_or_input_failure",
                      "invalid_model_or_certificate", "solver_launch_failure",
                      "solver_failure_or_unclassified", "gated_by_positive_controls")), None)
    bundle_started_wall, bundle_started_cpu = time.monotonic(), time.process_time()
    bundle = bundle_calls(run_dir)
    bundle_wall = time.monotonic() - bundle_started_wall
    bundle_cpu = time.process_time() - bundle_started_cpu
    elapsed = time.monotonic() - begin
    result = {"schema": "icperf-k11-bounded-solver-stage-v1",
              "experiment_id": EXPERIMENT, "step": args.step,
              "status": stopping or "completed_bounded_observation",
              "scope": "bounded solver and point-certificate observations only",
              "plan_sha256": launch["plan_sha256"],
              "source_commit": environment["commit"],
              "started_at": started_at, "finished_at": now(),
              "total_wall_seconds": elapsed, "calls": observations,
              "calls_bundle": {"wall_seconds": bundle_wall, "cpu_seconds": bundle_cpu,
                               "tar_bytes": bundle["bundle_size_bytes"],
                               "manifest_bytes": (run_dir / "calls-manifest.json").stat().st_size,
                               "raw_file_count": len(bundle["files"])}}
    result["calls_bundle_sha256"] = bundle["bundle_sha256"]
    result["calls_manifest_sha256"] = sha((run_dir / "calls-manifest.json").read_bytes())
    write(run_dir / "raw-result.json", result)
    with (run_dir / "manifest.yaml").open("x") as stream:
        yaml.safe_dump(manifest(run_dir, launch, environment, result, solver,
                                started_at, elapsed), stream, sort_keys=False)
    print(json.dumps({"step": args.step, "status": result["status"],
                      "calls": len(observations)}, sort_keys=True))


if __name__ == "__main__":
    main()
