"""Compile the frozen held-out confirmation schedule into supervisor trials.

Candidate mode binds a selected discovery result and fresh, committed roots but
remains non-executable. Approved mode copies that exact workload only after a
Coordinator decision and stage-1 admission bind its inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import yaml

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
HERE = Path(__file__).resolve().parent
SCHEDULE_DIR = STUDY / "graph_schedule_20261023"
DRIVER = STUDY / "graph_trial_adapter_20261023/trial_driver.py"
CHECKER = STUDY / "graph_trial_adapter_20261023/trial_check.py"
WRAPPER = STUDY / "preparation/execute_graph_prepared.py"
MATERIALIZER = STUDY / "graph_input_schedule_20261023/materialize.py"
RUN_ID = re.compile(r"^RUN-ECTD-[0-9a-f]{6}$")
ARMS = {"low_x", "mid_x", "random_x"}
ARTIFACTS = [
    "manifest.yaml", "raw-result.json", "driver.stdout", "driver.stderr",
    "materializer.stdout", "materializer.stderr", "prepared/prepared.txt",
    "prepared/manifest.json", "prepared/binding.json", "attempt/events.jsonl",
    "attempt/receipt.json", "attempt/input_verify.stdout",
    "attempt/input_verify.stderr", "attempt/collector.stdout",
    "attempt/collector.stderr", "attempt/count.stdout", "attempt/count.stderr",
    "attempt/rank_verify.stdout", "attempt/rank_verify.stderr",
]
ALLOW_EMPTY = [
    "driver.stderr", "materializer.stderr", "attempt/input_verify.stderr",
    "attempt/collector.stderr", "attempt/count.stderr", "attempt/rank_verify.stderr",
]
SOURCE_PATHS = (
    DRIVER, CHECKER, WRAPPER, MATERIALIZER,
    HERE / "study_admission.py", HERE / "build_confirmation_plan.py",
    HERE / "build_discovery_plan.py", HERE / "test_build_confirmation_plan.py",
    STUDY / "preparation/prepare_graph_input.py",
    STUDY / "preparation/verify_prepared_graph.py",
    ROOT / "research/conductor_relation_yield_20261014/prepare_input.py",
    ROOT / "research/conductor_relation_yield_20261014/execute_prepared.py",
    ROOT / "research/conductor_relation_yield_20261014/collector.rs",
    ROOT / "research/conductor_relation_yield_20261014/count_verify.cpp",
    ROOT / "research/conductor_relation_yield_20261014/verify_collector.py",
    ROOT / "research/conductor_relation_yield_20261014/exact_interval.py",
    ROOT / "harness/toycurve.py",
    SCHEDULE_DIR / "discovery-arms.jsonl",
    SCHEDULE_DIR / "manifest.json",
    SCHEDULE_DIR / "verification.json",
    STUDY / "manifest-v2.json",
    STUDY / "walk-p29-2048-attempt2.jsonl",
    STUDY / "walk-p37-256.jsonl",
    STUDY / "graph_selection_candidate_20261023/discovery_select.py",
    STUDY / "graph_confirmation_candidate_20261023/confirm.py",
    ROOT / "tools/experiment_execution.py",
    ROOT / "tools/allocate_id.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def repo_file(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"path must be repository-relative: {value!r}")
    resolved = (ROOT / path).resolve()
    if ROOT.resolve() not in resolved.parents or not resolved.is_file():
        raise ValueError(f"required repository file is missing: {value}")
    return resolved


def read_run_ids(path: Path, count: int) -> list[str]:
    values = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if (len(values) != count or len(set(values)) != count or
            any(not RUN_ID.fullmatch(value) for value in values)):
        raise ValueError(f"run ID file must contain {count} unique allocator-form RUN-ECTD IDs")
    sys.path.insert(0, str(ROOT / "tools"))
    import allocate_id
    if allocate_id.check_run_id_file(path) != 0:
        raise ValueError("RUN-ID list failed the repository-wide allocator check")
    return values


def selected_rows(selection: dict, schedule_path: Path) -> list[dict]:
    if (selection.get("schema") != "ectd.graph-discovery-selection-candidate/v1" or
            selection.get("status") != "selected_from_validated_discovery" or
            selection.get("discovery_arms_checked") != 8206 or
            selection.get("schedule_sha256") != sha(schedule_path)):
        raise ValueError("complete validated discovery selection and exact schedule required")
    schedule = {json.loads(line)["arm_key"]: json.loads(line)
                for line in schedule_path.read_text().splitlines()}
    keys = []
    for stratum in ("P29", "P37"):
        entry = selection.get("strata", {}).get(stratum, {})
        vertices = entry.get("selected_vertices", [])
        expected = [f"{stratum}-v{item['index']:04d}-{arm}"
                    for item in vertices for arm in ("low_x", "mid_x", "random_x")]
        if entry.get("confirmation_arm_keys") != expected:
            raise ValueError(f"confirmation arms are not the exact selected three-arm set: {stratum}")
        if not vertices or len({item["index"] for item in vertices}) != len(vertices):
            raise ValueError(f"selected confirmation vertices are empty or duplicated: {stratum}")
        keys.extend(expected)
    if not keys or len(keys) > 294 or len(set(keys)) != len(keys):
        raise ValueError("confirmation workload must contain 1..294 unique selected arms")
    rows = []
    for key in keys:
        row = schedule.get(key)
        if row is None or row.get("base_rule") not in ARMS:
            raise ValueError(f"selected confirmation arm is absent or unsupported: {key}")
        rows.append(row)
    return rows


def make_trials(rows: list[dict], run_ids: list[str], *, experiment_id: str,
                root_files: dict, commitments: dict, admission_path: str,
                collector: str, count_verifier: str) -> list[dict]:
    if not rows or len(rows) != len(run_ids) or len(rows) > 294:
        raise ValueError("one unique RUN ID is required for each of at most 294 confirmation arms")
    trials = []
    for row, run_id in zip(rows, run_ids):
        family, arm = row["stratum"], row["base_rule"]
        argv = ["python3", rel(DRIVER), "--arm-key", row["arm_key"],
                "--stage", "confirmation", "--base-root-file", root_files["base"],
                "--target-root-file", root_files["target"],
                "--verifier-root-file", root_files["verifier"],
                "--commitment", commitments[family], "--admission", admission_path,
                "--collector", collector, "--count-verifier", count_verifier,
                "--out", "{run_dir}", "--watchdog-seconds", "1800", "--memory-gib",
                "4" if family == "P29" else "8"]
        check_argv = ["python3", rel(CHECKER), "--run-dir", "{run_dir}",
                      "--admission", admission_path]
        trials.append({
            "id": row["arm_key"], "run_id": run_id, "argv": argv,
            "check_argv": check_argv, "artifacts": ARTIFACTS.copy(),
            "allow_empty_artifacts": ALLOW_EMPTY.copy(),
            "memory_mb": 4096 if family == "P29" else 8192,
            "watchdog_seconds": 1830,
            "watchdog_reason": "Supervisor ceiling allows the arm's 1800-second inner watchdog to seal a censored receipt.",
            "parameters": {"stage": "confirmation", "stratum": family,
                           "index": row["path_index"], "arm": arm,
                           "target_count": 32768},
            "depends_on": [],
        })
    return trials


def validate_roots(root_files: dict, commitments: dict, prior_admission: dict) -> tuple[dict, dict]:
    from materialize import check_commitment, load_schedule
    roots_paths = {name: repo_file(path) for name, path in root_files.items()}
    if set(roots_paths) != {"base", "target", "verifier"}:
        raise ValueError("confirmation must bind exactly base, target and verifier roots")
    prior_paths = {name: repo_file(path)
                   for name, path in prior_admission.get("root_files", {}).items()}
    if set(prior_paths) != {"base", "target", "verifier"}:
        raise ValueError("prior discovery admission root set differs")
    if (roots_paths["base"].read_bytes() != prior_paths["base"].read_bytes() or
            roots_paths["verifier"].read_bytes() != prior_paths["verifier"].read_bytes() or
            roots_paths["target"].read_bytes() == prior_paths["target"].read_bytes()):
        raise ValueError("confirmation must reuse base/verifier roots and use a fresh target root")
    if set(commitments) != {"P29", "P37"}:
        raise ValueError("confirmation requires distinct P29/P37 commitments")
    digests = {}
    for family in ("P29", "P37"):
        commitment = repo_file(commitments[family])
        _, row = load_schedule(f"{family}-v0000-low_x", "confirmation")
        actual_roots, _ = check_commitment(row, roots_paths, commitment)
        digests[family] = {"path": commitments[family], "sha256": sha(commitment),
                           "graph_sha256": sha(STUDY / ("walk-p29-2048-attempt2.jsonl" if family == "P29" else "walk-p37-256.jsonl")),
                           **{name + "_root_sha256": hashlib.sha256(value).hexdigest()
                              for name, value in actual_roots.items()}}
        if digests[family]["sha256"] == prior_admission.get("strata", {}).get(family, {}).get("commitment_sha256"):
            raise ValueError(f"confirmation reuses the discovery graph commitment: {family}")
    if digests["P29"]["sha256"] == digests["P37"]["sha256"]:
        raise ValueError("P29 and P37 confirmation commitments must differ")
    return roots_paths, digests


def build_candidate(specification_path: Path, *, task_id: str, queue_path: str,
                    selection_path: Path, prior_admission_path: Path,
                    root_files: dict, commitments: dict, collector_path: str,
                    count_verifier_path: str, run_ids_path: Path,
                    output_path: Path, source_commit: str | None = None) -> dict:
    sys.path.insert(0, str(STUDY / "preparation"))
    from execute_graph_prepared import check_frozen_sources, source_paths
    specification_path, selection_path, prior_admission_path = map(
        Path.resolve, (specification_path, selection_path, prior_admission_path))
    output_path = output_path.resolve()
    spec_doc = yaml.safe_load(specification_path.read_text())
    spec = spec_doc.get("experiment", spec_doc)
    if (spec.get("status") != "review_required" or spec.get("frozen") is not True or
            spec.get("execution_authorized") is not False or spec.get("approved_by")):
        raise ValueError("candidate requires an unapproved frozen review_required specification")
    experiment_id = spec["id"]
    if (rel(specification_path) != f"experiments/{experiment_id}/specification.yaml" or
            not output_path.is_relative_to(ROOT / "experiments" / experiment_id)):
        raise ValueError("candidate specification/output must be inside its canonical experiment directory")
    if not task_id.strip() or not queue_path or Path(queue_path).is_absolute() or ".." in Path(queue_path).parts:
        raise ValueError("candidate requires repository-relative task and queue bindings")
    selection = json.loads(selection_path.read_text())
    prior = json.loads(prior_admission_path.read_text())
    if (prior.get("schema") != "ectd.graph-study-admission.v1" or
            prior.get("status") != "approved" or prior.get("execution_stage") != 0):
        raise ValueError("approved discovery admission required before confirmation planning")
    if prior.get("experiment_id") != experiment_id:
        raise ValueError("confirmation and discovery must belong to one experiment")
    root_paths, commitment_digests = validate_roots(root_files, commitments, prior)
    collector = repo_file(collector_path)
    count_verifier = repo_file(count_verifier_path)
    rows = selected_rows(selection, SCHEDULE_DIR / "discovery-arms.jsonl")
    run_ids = read_run_ids(run_ids_path, len(rows))
    if source_commit is None:
        source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    check_frozen_sources(ROOT, [*source_paths().values(), *SOURCE_PATHS], source_commit)
    sources = {rel(path): sha(path) for path in SOURCE_PATHS}
    admission_path = f"experiments/{experiment_id}/graph-study-admission-confirmation.json"
    trials = make_trials(rows, run_ids, experiment_id=experiment_id, root_files=root_files,
                         commitments=commitments, admission_path=admission_path,
                         collector=collector_path, count_verifier=count_verifier_path)
    body = {
        "schema": "crypto.autoresearch.trial_plan.v1", "experiment_id": experiment_id,
        "task_id": task_id, "candidate_only": True, "approval_required": True,
        "frozen": True, "stop_on_invalid_output": True,
        "specification": rel(specification_path), "specification_sha256": sha(specification_path),
        "queue": queue_path, "source_commit": source_commit, "source_sha256": sources,
        "schedule_sha256": sha(SCHEDULE_DIR / "discovery-arms.jsonl"),
        "selection": {"path": rel(selection_path), "sha256": sha(selection_path)},
        "prior_discovery_admission": {"path": rel(prior_admission_path), "sha256": sha(prior_admission_path)},
        "root_files": {name: {"path": value, "sha256": sha(root_paths[name])}
                       for name, value in root_files.items()},
        "commitments": commitment_digests,
        "binaries": {"collector": {"path": collector_path, "sha256": sha(collector)},
                     "count_verifier": {"path": count_verifier_path, "sha256": sha(count_verifier)}},
        "stage": "confirmation", "target_count_per_arm": 32768,
        "trials": trials,
        "scope_note": "Candidate held-out confirmation plan for exactly the selected low_x/mid_x/random_x arms. No seed is generated or revealed by the compiler; candidate plans are refused by the execution loader.",
    }
    encoded = (json.dumps(body, indent=2, sort_keys=True) + "\n").encode()
    with output_path.open("xb") as stream:
        stream.write(encoded)
    return {"schema": "ectd.graph-confirmation-candidate-plan-build.v1",
            "status": "candidate_only", "trial_count": len(trials),
            "candidate_plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "output": str(output_path)}


def build_approved(candidate_path: Path, admission_path: Path,
                   decision_path: Path, specification_path: Path,
                   output_path: Path) -> dict:
    from study_admission import validate_approval_fields
    candidate_path, admission_path, decision_path, specification_path = map(
        Path.resolve, (candidate_path, admission_path, decision_path, specification_path))
    candidate = json.loads(candidate_path.read_text())
    admission = json.loads(admission_path.read_text())
    decision_doc = yaml.safe_load(decision_path.read_text())
    specification_doc = yaml.safe_load(specification_path.read_text())
    if (candidate.get("schema") != "crypto.autoresearch.trial_plan.v1" or
            candidate.get("candidate_only") is not True or
            candidate.get("approval_required") is not True or
            candidate.get("approved_by") not in (None, "") or
            admission.get("schema") != "ectd.graph-study-admission.v1" or
            admission.get("status") != "approved" or
            admission.get("approved_by") != "coordinator" or
            admission.get("execution_stage") != 1):
        raise ValueError("confirmation candidate and Coordinator stage-1 admission required")
    decision, spec, stage = validate_approval_fields(admission, decision_doc, specification_doc)
    if (stage != 1 or decision.get("id") != admission.get("decision_id") or
            admission.get("experiment_id") != candidate.get("experiment_id") or
            admission.get("specification_path") != rel(specification_path) or
            admission.get("decision_path") != rel(decision_path) or
            admission.get("specification_sha256") != sha(specification_path) or
            admission.get("decision_sha256") != sha(decision_path) or
            candidate.get("specification") != rel(specification_path) or
            admission.get("task_id") != candidate.get("task_id") or
            admission.get("source_commit") != candidate.get("source_commit") or
            admission.get("source_sha256") != candidate.get("source_sha256") or
            candidate.get("schedule_sha256") != sha(SCHEDULE_DIR / "discovery-arms.jsonl") or
            admission.get("output_prefix") != f"experiments/{candidate['experiment_id']}/runs"):
        raise ValueError("stage-1 admission does not bind this confirmation candidate")
    selection = candidate.get("selection", {})
    prior = candidate.get("prior_discovery_admission", {})
    if (admission.get("selection_path") != selection.get("path") or
            admission.get("selection_sha256") != selection.get("sha256") or
            admission.get("prior_admission_path") != prior.get("path") or
            admission.get("prior_admission_sha256") != prior.get("sha256")):
        raise ValueError("admission selection or prior discovery receipt differs from candidate")
    if (sha(repo_file(selection["path"])) != selection["sha256"] or
            sha(repo_file(prior["path"])) != prior["sha256"]):
        raise ValueError("confirmation selection or prior discovery receipt changed")
    selection_doc = json.loads(repo_file(selection["path"]).read_text())
    rows = selected_rows(selection_doc, SCHEDULE_DIR / "discovery-arms.jsonl")
    run_ids = [trial.get("run_id") for trial in candidate.get("trials", [])]
    expected_trials = make_trials(
        rows, run_ids, experiment_id=candidate["experiment_id"],
        root_files={name: item["path"] for name, item in candidate["root_files"].items()},
        commitments={family: item["path"] for family, item in candidate["commitments"].items()},
        admission_path=f"experiments/{candidate['experiment_id']}/graph-study-admission-confirmation.json",
        collector=candidate["binaries"]["collector"]["path"],
        count_verifier=candidate["binaries"]["count_verifier"]["path"])
    if candidate.get("trials") != expected_trials:
        raise ValueError("confirmation candidate trials differ from the frozen selection workload")
    for source, digest in candidate.get("source_sha256", {}).items():
        if sha(repo_file(source)) != digest:
            raise ValueError(f"confirmation frozen source changed: {source}")
    for name, item in candidate["root_files"].items():
        if sha(repo_file(item["path"])) != item["sha256"]:
            raise ValueError(f"confirmation root file changed: {name}")
    if admission.get("root_files") != {name: value["path"]
                                       for name, value in candidate["root_files"].items()}:
        raise ValueError("confirmation root paths differ from candidate")
    if (admission.get("binaries", {}).get("collector_path") != candidate["binaries"]["collector"]["path"] or
            admission.get("binaries", {}).get("collector_sha256") != candidate["binaries"]["collector"]["sha256"] or
            admission.get("binaries", {}).get("count_verifier_path") != candidate["binaries"]["count_verifier"]["path"] or
            admission.get("binaries", {}).get("count_verifier_sha256") != candidate["binaries"]["count_verifier"]["sha256"]):
        raise ValueError("confirmation binaries differ from candidate")
    for family in ("P29", "P37"):
        identity = admission.get("strata", {}).get(family, {})
        planned = candidate["commitments"][family]
        if sha(repo_file(planned["path"])) != planned["sha256"]:
            raise ValueError(f"confirmation {family} commitment file changed")
        if (identity.get("commitment_path") != planned["path"] or
                identity.get("commitment_sha256") != planned["sha256"] or
                identity.get("graph_sha256") != planned["graph_sha256"] or
                any(identity.get(name + "_root_sha256") != planned[name + "_root_sha256"]
                    for name in ("base", "target", "verifier"))):
            raise ValueError(f"confirmation {family} commitment differs from candidate")
    body = dict(candidate)
    body.pop("candidate_only")
    body.pop("approval_required")
    body["approved_by"] = decision["id"]
    body["specification_sha256"] = sha(specification_path)
    body["stage_admission"] = {"path": rel(admission_path), "sha256": sha(admission_path),
                               "decision_path": rel(decision_path), "decision_sha256": sha(decision_path)}
    body["scope_note"] = "Coordinator-approved held-out confirmation plan for the exact selected low_x/mid_x/random_x arms. Supervisor halts on any invalid receipt; complete ECDLP costs remain a separate stage."
    output_path = output_path.resolve()
    if not output_path.is_relative_to(ROOT / "experiments" / candidate["experiment_id"]):
        raise ValueError("approved confirmation plan output must stay inside the experiment directory")
    encoded = (json.dumps(body, indent=2, sort_keys=True) + "\n").encode()
    with output_path.open("xb") as stream:
        stream.write(encoded)
    return {"schema": "ectd.graph-confirmation-trial-plan-build.v1",
            "status": "built", "experiment_id": candidate["experiment_id"],
            "approved_by": decision["id"], "trial_count": len(body["trials"]),
            "trial_plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "output": str(output_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-candidate", type=Path)
    parser.add_argument("--admission")
    parser.add_argument("--decision")
    parser.add_argument("--approved-specification")
    parser.add_argument("--approved-output", type=Path)
    parser.add_argument("--specification", type=Path)
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--prior-admission", type=Path)
    parser.add_argument("--run-ids", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--task-id")
    parser.add_argument("--queue")
    parser.add_argument("--base-root-file")
    parser.add_argument("--target-root-file")
    parser.add_argument("--verifier-root-file")
    parser.add_argument("--commitment-p29")
    parser.add_argument("--commitment-p37")
    parser.add_argument("--collector")
    parser.add_argument("--count-verifier")
    parser.add_argument("--source-commit")
    args = parser.parse_args()
    if args.approved_candidate is not None:
        if any(value is None for value in
               (args.admission, args.decision, args.approved_specification, args.approved_output)):
            parser.error("approved mode requires candidate, admission, decision, specification and output")
        result = build_approved(args.approved_candidate, Path(args.admission),
                                Path(args.decision), Path(args.approved_specification),
                                args.approved_output)
        print(json.dumps(result, sort_keys=True))
        return
    candidate_required = (args.specification, args.selection, args.prior_admission,
                          args.run_ids, args.output, args.task_id, args.queue,
                          args.base_root_file, args.target_root_file,
                          args.verifier_root_file, args.commitment_p29,
                          args.commitment_p37, args.collector, args.count_verifier)
    if any(value is None for value in candidate_required):
        parser.error("candidate mode requires specification, selection, prior admission, run IDs, output, task/queue, roots, commitments and binaries")
    result = build_candidate(
        args.specification, task_id=args.task_id, queue_path=args.queue,
        selection_path=args.selection, prior_admission_path=args.prior_admission,
        root_files={"base": args.base_root_file, "target": args.target_root_file,
                    "verifier": args.verifier_root_file},
        commitments={"P29": args.commitment_p29, "P37": args.commitment_p37},
        collector_path=args.collector, count_verifier_path=args.count_verifier,
        run_ids_path=args.run_ids, output_path=args.output,
        source_commit=args.source_commit)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
