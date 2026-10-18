"""Approved-only six-call U/S/U planted-positive driver.

This file is a prospective launcher. It refuses every scientific call until
the Coordinator freezes and approves the protocol, binds a trial plan, and
the supervisor supplies an admitted launch. Static preparation uses
``encode_sorted.py`` and ``verify_inputs.py`` instead.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parents[1]
SPEC = HERE / "specification.yaml"
PLAN = HERE / "trial-plan.json"
MANIFEST = HERE / "inputs/sorted_positive_manifest.json"
POSITIVE = ROOT / "experiments/EXP-ICPERF-018b0c/inputs/positive_manifest.json"
BASES = {
    "weighted": ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json",
    "local_random": ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json",
}
SEED, WALL, RSS, MODELS = 20261018, 1200, 8 * (1 << 30), 64
ORDER = ("weighted_unsorted_first", "weighted_sorted", "weighted_unsorted_repeat",
         "local_random_unsorted_first", "local_random_sorted", "local_random_unsorted_repeat")


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def write(path: Path, record: dict) -> None:
    with path.open("x") as stream:
        json.dump(record, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def admitted(run_dir: Path) -> tuple[dict, dict, dict, dict]:
    """Fail closed until a frozen approved specification and admitted launch exist."""
    import yaml
    if not run_dir.is_dir() or run_dir.parent != HERE / "runs":
        raise ValueError("an existing supervisor-created run directory is required")
    spec = yaml.safe_load(SPEC.read_text())["experiment"]
    if (spec["id"] != "EXP-ICPERF-554db4" or spec["status"] not in ("approved", "running")
            or spec["frozen"] is not True or spec["execution_authorized"] is not True
            or not spec["approved_by"]):
        raise ValueError("experiment lacks a frozen approval decision")
    plan_blob = PLAN.read_bytes()
    plan = json.loads(plan_blob)
    launch, environment = read(run_dir / "launch.json"), read(run_dir / "environment.json")
    if (plan["approved_by"] != spec["approved_by"] or plan["experiment_id"] != spec["id"]
            or plan["specification_sha256"] != sha(SPEC.read_bytes())
            or launch["plan_sha256"] != sha(plan_blob)
            or launch["run_id"] != run_dir.name or launch["trial_id"] != "positive_panel"
            or launch["authority"]["commit"] != environment["commit"]):
        raise ValueError("supervisor launch or plan binding mismatch")
    trial, = [item for item in plan["trials"] if item["id"] == "positive_panel"]
    if trial["run_id"] != run_dir.name or str(Path(__file__).relative_to(ROOT)) not in trial["argv"]:
        raise ValueError("trial plan does not bind this driver")
    for group in ("source_sha256", "input_sha256"):
        for path, digest in plan[group].items():
            bound = Path(path)
            if not bound.is_absolute():
                bound = ROOT / bound
            if sha(bound.read_bytes()) != digest:
                raise ValueError(f"{group} changed: {path}")
    # The independently sealed schedule is a separate gate, never inferred
    # from producer data or this implementation's positive controls.
    blind = plan.get("blind_schedule_receipt")
    if not isinstance(blind, dict) or not blind.get("sealed_before_predecessor_read"):
        raise ValueError("independent sealed gamma schedule is missing")
    bound = ROOT / blind["path"]
    if sha(bound.read_bytes()) != blind["sha256"]:
        raise ValueError("independent sealed gamma schedule digest mismatch")
    return launch, environment, spec, plan


def bundle_calls(run_dir: Path) -> dict:
    calls = run_dir / "calls"
    paths = sorted(path for path in calls.rglob("*") if path.is_file())
    if any(path.is_symlink() for path in calls.rglob("*")):
        raise ValueError("call tree contains symlink")
    rows = []
    target = run_dir / "calls.tar.gz"
    with target.open("xb") as sink:
        with gzip.GzipFile(fileobj=sink, mode="wb", filename="", mtime=0) as packed:
            with tarfile.open(fileobj=packed, mode="w|") as archive:
                for path in paths:
                    name = path.relative_to(run_dir).as_posix()
                    blob = path.read_bytes()
                    entry = tarfile.TarInfo(name)
                    entry.size, entry.mtime, entry.mode = len(blob), 0, 0o644
                    with path.open("rb") as source:
                        archive.addfile(entry, source)
                    rows.append({"path": name, "size_bytes": len(blob), "sha256": sha(blob)})
    result = {"schema": "icperf-binary-m8-call-tree-v1", "files": rows,
              "bundle_path": target.name, "bundle_size_bytes": target.stat().st_size,
              "bundle_sha256": sha(target.read_bytes())}
    write(run_dir / "calls-manifest.json", result)
    return result


def run_panel(run_dir: Path) -> dict:
    launch, environment, spec, plan = admitted(run_dir)
    # Importing the solver interface here ensures static preparation cannot
    # accidentally start or require a scientific solver dependency.
    import psutil
    from tools.icperf_binary_k11_solver import collect
    from tools.icperf_binary_root_certificate import certificate
    from verify_inputs import verify
    if sys.flags.optimize:
        raise ValueError("optimized Python disables scientific assertions")
    input_check = verify()
    if set(input_check["controls"]) != set(BASES):
        raise ValueError("both independent positive controls required")
    manifest = read(MANIFEST)
    positive = read(POSITIVE)
    solver = Path(spec["input_bindings"]["original_solver_binary"]["path"])
    if sha(solver.read_bytes()) != spec["input_bindings"]["original_solver_binary"]["sha256"]:
        raise ValueError("solver binary digest mismatch")
    calls = run_dir / "calls"
    calls.mkdir(exist_ok=False)
    started = now()
    begin = time.monotonic()
    records = []
    for name in ORDER:
        label = "local_random" if name.startswith("local_random") else "weighted"
        sorted_arm = name.endswith("sorted") and not name.endswith("unsorted")
        source = positive["controls"][label]
        row = manifest["arms"][label]
        chosen_path = ROOT / (row["formula_path"] if sorted_arm else source["formula_path"])
        packed = chosen_path.read_bytes()
        expected = row["formula_gzip_sha256"] if sorted_arm else source["formula_gzip_sha256"]
        if sha(packed) != expected:
            raise ValueError(f"{name}: input formula digest mismatch")
        decompressed_at = time.monotonic()
        raw = gzip.decompress(packed)
        decompression_wall = time.monotonic() - decompressed_at
        if sha(raw) != (row["raw_xcnf_sha256"] if sorted_arm else source["formula_raw_sha256"]):
            raise ValueError(f"{name}: raw formula digest mismatch")
        base = read(BASES[label])
        arm = {"kind": "torsion_phi", "base_dimension": 11, "offset": 4096,
               "primary_variables": 454, "cnf_variables": row["cnf_variables"] if sorted_arm
               else source["source_row"]["input_counts"]["cnf_variables"],
               "target_coordinate": row["target_coordinate"]}
        chain = {"gamma": manifest["gamma"],
                 "curve": {"b_polynomial_bits": 31, "prime_order": 576460752557211763},
                 "selected_channel": 0,
                 "target_channels": [row["raw_target"]] * 4,
                 "subgroup_target": row["projected_target"]}
        available = psutil.virtual_memory().available
        reserve = MODELS * (len(raw) + max(1 << 20, arm["cnf_variables"] * 12)) + 10 * (1 << 20)
        host = {"available_memory_bytes": available,
                "free_disk_bytes": shutil.disk_usage(calls).free,
                "declared_raw_reserve_bytes": reserve,
                "load_average": list(psutil.getloadavg()), "checked_at": now()}
        if available < 10 * (1 << 30) or host["free_disk_bytes"] < reserve:
            records.append({"name": name, "status": "host_admission_stop", "host": host,
                            "decompression_wall_seconds": decompression_wall})
            continue
        call_dir = calls / name
        checked_wall = checked_cpu = 0.0

        def certify(bits: int) -> dict:
            nonlocal checked_wall, checked_cpu
            wall_start, cpu_start = time.monotonic(), time.process_time()
            try:
                result = certificate(bits, base, chain, arm)
                return {"schema": "icperf-binary-m8-point-check-v1", "result": result,
                        "base_kind": label, "encoding": "sorted" if sorted_arm else "unsorted",
                        "assignment_hex": hex(bits)}
            finally:
                checked_wall += time.monotonic() - wall_start
                checked_cpu += time.process_time() - cpu_start

        try:
            observation = collect(raw, 454, solver, WALL, RSS, MODELS, SEED, call_dir, certify)
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            records.append({"name": name, "status": "infrastructure_or_input_failure",
                            "error_type": type(error).__name__, "error": str(error),
                            "call_directory_exists": call_dir.exists(), "host": host,
                            "decompression_wall_seconds": decompression_wall})
            continue
        observation["host"] = host
        observation["name"] = name
        observation["encoding"] = "sorted" if sorted_arm else "unsorted"
        observation["decompression_wall_seconds"] = decompression_wall
        observation["point_filter_wall_seconds"] = checked_wall
        observation["point_filter_cpu_seconds"] = checked_cpu
        write(call_dir / "summary.json", observation)
        records.append({"name": name, "status": observation["status"], "host": host,
                        "attempts": len(observation["attempts"]),
                        "summary_sha256": sha((call_dir / "summary.json").read_bytes()),
                        "decompression_wall_seconds": decompression_wall})
    bundle = bundle_calls(run_dir)
    result = {"schema": "icperf-binary-m8-sorted-panel-v1",
              "experiment_id": "EXP-ICPERF-554db4", "scope": "six planted calls; zero natural calls",
              "plan_sha256": launch["plan_sha256"], "source_commit": environment["commit"],
              "started_at": started, "finished_at": now(),
              "total_wall_seconds": time.monotonic() - begin, "calls": records,
              "input_check": input_check,
              "calls_bundle_sha256": bundle["bundle_sha256"],
              "calls_manifest_sha256": sha((run_dir / "calls-manifest.json").read_bytes())}
    write(run_dir / "raw-result.json", result)
    import yaml
    manifest_run = {"run": {"id": run_dir.name, "experiment_id": result["experiment_id"],
                            "status": "completed", "code": {"commit": environment["commit"],
                            "command": launch["argv"]},
                            "environment": {"python": sys.version, "platform": platform.platform(),
                                            "solver_sha256": sha(solver.read_bytes()),
                                            "one_solver_process_at_a_time": True},
                            "inputs": {"plan_sha256": launch["plan_sha256"],
                                       "positive_manifest_sha256": sha(POSITIVE.read_bytes()),
                                       "sorted_manifest_sha256": sha(MANIFEST.read_bytes())},
                            "timing": {"started_at": started, "finished_at": now(),
                                       "wall_seconds": result["total_wall_seconds"]},
                            "result": {"raw_result": "raw-result.json",
                                       "certificate": {"kind": "none", "verified": False},
                                       "scope": result["scope"]}}}
    with (run_dir / "manifest.yaml").open("x") as stream:
        yaml.safe_dump(manifest_run, stream, sort_keys=False)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run_panel(args.run_dir.resolve())
    print(json.dumps({"calls": len(result["calls"]), "scope": result["scope"]}, sort_keys=True))


if __name__ == "__main__":
    main()
