"""Custodian-only preparation of rootless graph worker inputs and catalog.

This command reads the approved private admission and seed roots, materializes
all arms before dispatch, and writes a separate worker-visible directory with
only prepared inputs, prepared manifests, public bindings, and rootless approval.
It never launches a relation collector.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import subprocess
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
MATERIALIZER = STUDY / "graph_input_schedule_20261023/materialize.py"
STAGE_NUMBER = {"discovery": 0, "confirmation": 1, "solve": 2}

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(STUDY / "graph_input_schedule_20261023"))

from prepared_worker import (  # noqa: E402
    assert_rootless, load_worker_catalog, public_binding, sha,
    write_worker_admission,
)
from study_admission import repo_path  # noqa: E402


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def rows_for(admission: dict, stage: str) -> list[dict]:
    if stage == "discovery":
        from build_discovery_plan import load_rows
        return load_rows()
    if stage == "confirmation":
        from build_confirmation_plan import selected_rows
        selection_path = repo_path(admission["selection_path"])
        selection = json.loads(selection_path.read_text())
        schedule = STUDY / "graph_schedule_20261023/discovery-arms.jsonl"
        return selected_rows(selection, schedule)
    from build_solve_plan import finalist_rows
    analysis_path = repo_path(admission["finalist_analysis_path"])
    selection_path = repo_path(admission["selection_path"])
    analysis = json.loads(analysis_path.read_text())
    selection = json.loads(selection_path.read_text())
    selection["_sha256"] = sha(selection_path)
    return finalist_rows(analysis, selection, sha(selection_path))


def copy_new(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, destination.open("xb") as dst:
        shutil.copyfileobj(src, dst)


def prepare(admission_path: Path, private_dir: Path, output_dir: Path,
            stage: str) -> dict:
    admission_path = admission_path.resolve()
    private_dir = private_dir.resolve()
    output_dir = output_dir.resolve()
    admission = json.loads(admission_path.read_text())
    expected_stage = STAGE_NUMBER[stage]
    if (admission.get("schema") != "ectd.graph-study-admission.v1" or
            admission.get("status") != "approved" or
            admission.get("approved_by") != "coordinator" or
            admission.get("execution_stage") != expected_stage):
        raise ValueError("matching Coordinator-approved stage admission required")
    if not output_dir.is_relative_to(ROOT / "experiments" / admission["experiment_id"]):
        raise ValueError("worker catalog output must be inside the experiment directory")
    if (output_dir.exists() and any(output_dir.iterdir())):
        raise ValueError("worker catalog output directory must be absent or empty")
    if private_dir == output_dir or private_dir in output_dir.parents or output_dir in private_dir.parents:
        raise ValueError("private materializer output and worker catalog must be separate trees")
    output_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)
    rows = rows_for(admission, stage)
    if not rows or len({row["arm_key"] for row in rows}) != len(rows):
        raise ValueError("frozen stage schedule must contain unique arm keys")
    roots = admission.get("root_files", {})
    if set(roots) != {"base", "target", "verifier"}:
        raise ValueError("private admission must bind exactly three roots")
    root_paths = {name: repo_path(value) for name, value in roots.items()}
    worker_admission_path = output_dir / "worker-admission.json"
    arms = {}
    private_admission_verified = False
    for row in rows:
        key = row["arm_key"]
        family = row["stratum"]
        commitment = repo_path(admission["strata"][family]["commitment_path"])
        materialized_dir = private_dir / key
        prepared_dir = output_dir / "arms" / key
        command = [sys.executable, str(MATERIALIZER), "prepare", "--arm-key", key,
                   "--stage", stage,
                   "--base-root-file", str(root_paths["base"]),
                   "--target-root-file", str(root_paths["target"]),
                   "--verifier-root-file", str(root_paths["verifier"]),
                   "--commitment", str(commitment), "--output-dir", str(materialized_dir)]
        subprocess.run(command, stdin=subprocess.DEVNULL, check=True)
        if not private_admission_verified:
            from execute_graph_prepared import check_frozen_sources, source_paths
            from study_admission import verify_study_admission
            private_manifest = materialized_dir / "manifest.json"
            private_binding = materialized_dir / "binding.json"
            binaries = admission["binaries"]
            check_args = SimpleNamespace(
                manifest=private_manifest,
                collector=repo_path(binaries["collector_path"]),
                count_verifier=repo_path(binaries["count_verifier_path"]),
                output=ROOT / admission["output_prefix"] / ".prepared-catalog-preflight")
            source_commit, _ = verify_study_admission(
                admission_path, private_binding, check_args,
                json.loads(private_manifest.read_text()), source_paths(), check_frozen_sources)
            if source_commit != admission.get("source_commit"):
                raise ValueError("prepared catalog admission source commit differs")
            write_worker_admission(admission_path, worker_admission_path)
            private_admission_verified = True
        if (prepared_dir.exists() and any(prepared_dir.iterdir())):
            raise ValueError(f"worker arm output already exists: {key}")
        prepared_dir.mkdir(parents=True, exist_ok=True)
        public_binding_path = prepared_dir / "binding.json"
        copy_new(materialized_dir / "prepared.txt", prepared_dir / "prepared.txt")
        copy_new(materialized_dir / "manifest.json", prepared_dir / "manifest.json")
        public_binding_doc = public_binding(json.loads(
            (materialized_dir / "binding.json").read_text()))
        with public_binding_path.open("x", encoding="utf-8") as stream:
            json.dump(public_binding_doc, stream, indent=2, sort_keys=True)
            stream.write("\n")
        input_path = prepared_dir / "prepared.txt"
        manifest_path = prepared_dir / "manifest.json"
        arms[key] = {
            "input_path": rel(input_path), "input_sha256": sha(input_path),
            "manifest_path": rel(manifest_path), "manifest_sha256": sha(manifest_path),
            "binding_path": rel(public_binding_path), "binding_sha256": sha(public_binding_path),
        }
    if not private_admission_verified:
        raise ValueError("no arm was available to validate the approved admission")
    catalog = {
        "schema": "ectd.graph-prepared-worker-catalog.v1",
        "experiment_id": admission["experiment_id"],
        "execution_stage": expected_stage,
        "schedule_sha256": admission["schedule"]["arms_sha256"],
        "worker_admission_path": rel(worker_admission_path),
        "worker_admission_sha256": sha(worker_admission_path),
        "arms": arms,
    }
    assert_rootless(catalog, "prepared catalog")
    catalog_path = output_dir / "catalog.json"
    with catalog_path.open("x", encoding="utf-8") as stream:
        json.dump(catalog, stream, indent=2, sort_keys=True)
        stream.write("\n")
    load_worker_catalog(catalog_path, rows, admission["experiment_id"], expected_stage)
    return {"schema": "ectd.graph-prepared-worker-catalog-build.v1",
            "status": "prepared_only", "experiment_id": admission["experiment_id"],
            "execution_stage": expected_stage, "arm_count": len(rows),
            "catalog_sha256": sha(catalog_path), "worker_admission_sha256": sha(worker_admission_path),
            "catalog_path": rel(catalog_path), "collector_launches": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission", type=Path, required=True,
                        help="private, Coordinator-approved study admission")
    parser.add_argument("--stage", choices=tuple(STAGE_NUMBER), required=True)
    parser.add_argument("--private-dir", type=Path, required=True,
                        help="custodian-only scratch directory for private materializer bindings")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="repository directory containing worker-visible prepared artifacts")
    args = parser.parse_args()
    print(json.dumps(prepare(args.admission, args.private_dir, args.output_dir, args.stage),
                     sort_keys=True))


if __name__ == "__main__":
    main()
