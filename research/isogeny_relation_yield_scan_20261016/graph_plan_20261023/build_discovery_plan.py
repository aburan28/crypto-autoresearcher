"""Compile the complete fixed graph schedule into supervisor trial records.

This is a plan compiler only. It writes no admission or observations. Its
inputs are the frozen experiment/decision, study admission, committed roots,
schedule, binaries, and an allocator-produced one-to-one RUN-ID list.
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

SOURCE_PATHS = (
    DRIVER, CHECKER, WRAPPER, MATERIALIZER,
    HERE / "study_admission.py", HERE / "build_discovery_plan.py",
    HERE / "test_build_discovery_plan.py",
    STUDY / "preparation/prepare_graph_input.py",
    STUDY / "preparation/verify_prepared_graph.py",
    ROOT / "research/conductor_relation_yield_20261014/prepare_input.py",
    ROOT / "research/conductor_relation_yield_20261014/execute_prepared.py",
    ROOT / "research/conductor_relation_yield_20261014/collector.rs",
    ROOT / "research/conductor_relation_yield_20261014/count_verify.cpp",
    ROOT / "research/conductor_relation_yield_20261014/verify_collector.py",
    ROOT / "harness/toycurve.py",
    SCHEDULE_DIR / "discovery-arms.jsonl",
    SCHEDULE_DIR / "manifest.json",
    SCHEDULE_DIR / "verification.json",
    SCHEDULE_DIR / "plan.py",
    SCHEDULE_DIR / "verify.py",
    STUDY / "manifest-v2.json",
    STUDY / "walk-p29-2048-attempt2.jsonl",
    STUDY / "walk-p37-256.jsonl",
    STUDY / "graph_selection_candidate_20261023/discovery_select.py",
    STUDY / "graph_confirmation_candidate_20261023/confirm.py",
    STUDY / "graph_confirmation_candidate_20261023/benchmark_interval.py",
    STUDY / "graph_solve_candidate_20261023/solve.py",
    STUDY / "graph_solve_candidate_20261023/check.py",
    ROOT / "tools/experiment_execution.py",
    ROOT / "tools/runbook.py",
    ROOT / "tools/research_dispatch.py",
    ROOT / "tools/allocate_id.py",
)

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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def repo_file(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"path must be repository-relative: {value!r}")
    resolved = (ROOT / path).resolve()
    if ROOT.resolve() not in resolved.parents:
        raise ValueError(f"path escapes repository: {value!r}")
    if not resolved.is_file():
        raise ValueError(f"required file is missing: {value}")
    return resolved


def load_rows() -> list[dict]:
    manifest = json.loads((SCHEDULE_DIR / "manifest.json").read_text())
    receipt = json.loads((SCHEDULE_DIR / "verification.json").read_text())
    rows = [json.loads(line) for line in (SCHEDULE_DIR / "discovery-arms.jsonl").read_text().splitlines()]
    if (manifest.get("schema") != "ectd-graph-discovery-schedule/v1" or
            manifest.get("status") != "candidate_unapproved" or
            manifest.get("arms") != 8206 or manifest.get("target_probes") != 60889088 or
            manifest.get("schedule_sha256") != sha(SCHEDULE_DIR / "discovery-arms.jsonl") or
            receipt.get("status") != "pass" or receipt.get("arms_checked") != 8206 or
            receipt.get("target_probes") != 60889088 or
            receipt.get("schedule_sha256") != manifest["schedule_sha256"] or len(rows) != 8206 or
            len({row.get("arm_key") for row in rows}) != 8206):
        raise ValueError("complete independently verified discovery schedule required")
    for row in rows:
        expected_quota = 8192 if row.get("stratum") == "P29" else 2048
        if (row.get("discovery_targets") != expected_quota or
                row.get("stage") not in (None, "discovery") or
                row.get("base_rule") not in ("low_x", "mid_x", "random_x", "power_x",
                                               "graph_transport", "u2_native", "u2_transport")):
            raise ValueError(f"invalid fixed schedule row {row.get('arm_key')}")
    return rows


def read_run_ids(path: Path, count: int) -> list[str]:
    values = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if len(values) != count or len(set(values)) != count or any(not RUN_ID.fullmatch(v) for v in values):
        raise ValueError(f"run ID file must contain {count} unique allocator-form RUN-ECTD IDs")
    return values


def make_trials(rows: list[dict], run_ids: list[str], *, experiment_id: str,
                root_files: dict, commitments: dict, admission_path: str,
                collector: str, count_verifier: str) -> list[dict]:
    if len(rows) != 8206 or len(run_ids) != len(rows):
        raise ValueError("the plan must bind exactly one run ID to every fixed arm")
    run_by_arm = {row["arm_key"]: run_id for row, run_id in zip(rows, run_ids)}
    if len(run_by_arm) != len(rows):
        raise ValueError("duplicate scheduled arm")
    trials = []
    for row, run_id in zip(rows, run_ids):
        arm_key, family = row["arm_key"], row["stratum"]
        commitment = commitments[family]
        argv = ["python3", rel(DRIVER), "--arm-key", arm_key,
                "--base-root-file", root_files["base"],
                "--target-root-file", root_files["target"],
                "--verifier-root-file", root_files["verifier"],
                "--commitment", commitment, "--admission", admission_path,
                "--collector", collector, "--count-verifier", count_verifier,
                "--out", "{run_dir}"]
        check_argv = ["python3", rel(CHECKER), "--run-dir", "{run_dir}",
                      "--admission", admission_path]
        dependency = row.get("control_reference")
        if dependency:
            if dependency not in run_by_arm:
                raise ValueError(f"control reference is not scheduled: {dependency}")
            check_argv += ["--reference-run-dir",
                           f"experiments/{experiment_id}/runs/{run_by_arm[dependency]}"]
        memory = 4096 if family == "P29" else 8192
        watchdog = 1830
        trials.append({
            "id": arm_key, "run_id": run_id,
            "argv": argv, "check_argv": check_argv,
            "artifacts": ARTIFACTS.copy(), "allow_empty_artifacts": ALLOW_EMPTY.copy(),
            "memory_mb": memory, "watchdog_seconds": watchdog,
            "watchdog_reason": "Supervisor ceiling allows the arm's 1800-second inner watchdog to seal a censored receipt.",
            "note": f"Fixed {family} {row['base_rule']} discovery arm at vertex {row['path_index']} with {row['discovery_targets']} targets.",
            "depends_on": [dependency] if dependency else [],
        })
    return trials


def build_candidate(specification_path: Path, *, task_id: str, queue_path: str,
                    root_files: dict, commitments: dict, collector_path: str,
                    count_verifier_path: str, source_commit: str | None,
                    run_ids_path: Path, output_path: Path) -> dict:
    """Write a non-executable candidate plan so readiness can precede approval.

    Candidate plans live at candidate-trial-plan.json and are explicitly refused
    by the execution loader. After Coordinator approval, build() writes the
    approved trial-plan.json and dispatcher-bound queue as separate artifacts.
    """
    specification_path = specification_path.resolve()
    output_path = output_path.resolve()
    spec_doc = yaml.safe_load(specification_path.read_text())
    spec = spec_doc.get("experiment", spec_doc)
    if (not isinstance(spec, dict) or not isinstance(spec.get("id"), str) or
            spec.get("status") != "review_required" or spec.get("frozen") is not True or
            spec.get("execution_authorized") is not False or spec.get("approved_by")):
        raise ValueError("candidate plan requires an unapproved frozen review_required specification")
    experiment_id = spec["id"]
    if rel(specification_path) != f"experiments/{experiment_id}/specification.yaml":
        raise ValueError("candidate specification must be the experiment's canonical specification")
    if rel(output_path) != f"experiments/{experiment_id}/candidate-trial-plan.json":
        raise ValueError("candidate output must use candidate-trial-plan.json")
    if not task_id.strip() or not queue_path or queue_path.startswith("/") or ".." in Path(queue_path).parts:
        raise ValueError("candidate plan requires a task ID and repository-relative reserved queue path")
    if Path(queue_path).as_posix() != queue_path or "\\" in queue_path:
        raise ValueError("candidate queue path must be canonical POSIX repository-relative")
    if set(root_files) != {"base", "target", "verifier"}:
        raise ValueError("candidate plan must bind base, discovery-target and verifier roots")
    if set(commitments) != {"P29", "P37"}:
        raise ValueError("candidate plan must bind both stratum commitments")
    root_paths = {name: repo_file(path) for name, path in root_files.items()}
    commitment_paths = {family: repo_file(path) for family, path in commitments.items()}
    collector = repo_file(collector_path)
    count_verifier = repo_file(count_verifier_path)
    sys.path.insert(0, str(STUDY / "graph_input_schedule_20261023"))
    from materialize import check_commitment, load_schedule
    for family in ("P29", "P37"):
        _, row = load_schedule(f"{family}-v0000-graph_transport")
        check_commitment(row, root_paths, commitment_paths[family])

    run_ids = read_run_ids(run_ids_path, 8206)
    sys.path.insert(0, str(ROOT / "tools"))
    import allocate_id
    if allocate_id.check_run_id_file(run_ids_path) != 0:
        raise ValueError("RUN-ID list failed the repository-wide allocator check")

    sys.path.insert(0, str(STUDY / "preparation"))
    from execute_graph_prepared import check_frozen_sources, source_paths
    if source_commit is None:
        source_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    check_frozen_sources(ROOT, [*source_paths().values(), *SOURCE_PATHS], source_commit)
    sources = {rel(path): sha(path) for path in SOURCE_PATHS}
    rows = load_rows()
    trials = make_trials(
        rows, run_ids, experiment_id=experiment_id, root_files=root_files,
        commitments=commitments,
        admission_path=f"experiments/{experiment_id}/graph-study-admission.json",
        collector=collector_path, count_verifier=count_verifier_path)
    schedule_path = SCHEDULE_DIR / "discovery-arms.jsonl"
    candidate = {
        "schema": "crypto.autoresearch.trial_plan.v1",
        "experiment_id": experiment_id, "task_id": task_id,
        "candidate_only": True, "approval_required": True,
        "frozen": True,
        "specification": rel(specification_path),
        "specification_sha256": sha(specification_path),
        "queue": queue_path,
        "source_commit": source_commit,
        "source_sha256": sources,
        "schedule_sha256": sha(schedule_path),
        "schedule_arms": len(rows),
        "schedule_target_probes": 60889088,
        "root_files": {name: {"path": path, "sha256": sha(root_paths[name])}
                        for name, path in root_files.items()},
        "commitments": {family: {"path": path, "sha256": sha(commitment_paths[family])}
                         for family, path in commitments.items()},
        "binaries": {"collector": {"path": collector_path, "sha256": sha(collector)},
                     "count_verifier": {"path": count_verifier_path,
                                        "sha256": sha(count_verifier)}},
        "trials": trials,
        "scope_note": "Candidate-only 8,206-arm discovery plan. This artifact establishes pre-approval plan readiness and is rejected by the execution loader; Coordinator approval requires a separately built approved trial-plan.json and dispatch queue.",
    }
    encoded = (json.dumps(candidate, indent=2, sort_keys=True) + "\n").encode()
    with output_path.open("xb") as stream:
        stream.write(encoded)
    return {"schema": "ectd.graph-discovery-candidate-plan-build.v1",
            "status": "candidate_only", "approval_required": True,
            "experiment_id": experiment_id, "trial_count": len(trials),
            "schedule_sha256": sha(schedule_path),
            "candidate_plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "output": str(output_path)}


def build(specification_path: Path, admission_path: Path, decision_path: Path,
          queue_path: Path, run_ids_path: Path, output_path: Path) -> dict:
    specification_path, admission_path, decision_path, queue_path = (
        path.resolve() for path in (specification_path, admission_path, decision_path, queue_path))
    spec_doc = yaml.safe_load(specification_path.read_text())
    spec = spec_doc.get("experiment", spec_doc)
    admission = json.loads(admission_path.read_text())
    decision_doc = yaml.safe_load(decision_path.read_text())
    if (admission.get("schema") != "ectd.graph-study-admission.v1" or
            admission.get("status") != "approved" or admission.get("approved_by") != "coordinator" or
            admission.get("specification_path") != rel(specification_path) or
            admission.get("decision_path") != rel(decision_path) or
            admission.get("specification_sha256") != sha(specification_path) or
            admission.get("decision_sha256") != sha(decision_path) or
            spec.get("execution_authorized") is not True or spec.get("frozen") is not True):
        raise ValueError("frozen approved specification and matching study admission required")
    from study_admission import validate_approval_fields
    decision, _checked_spec, stage = validate_approval_fields(admission, decision_doc, spec_doc)
    if (stage not in spec.get("execution_authorized_stages", []) or
            admission.get("experiment_id") != spec.get("id") or
            decision.get("id") != spec.get("approved_by") or
            not queue_path.is_file() or
            admission.get("output_prefix") != f"experiments/{spec['id']}/runs" or
            not str(admission.get("task_id", "")).startswith("TASK-")):
        raise ValueError("approved stage, experiment identity, decision or queue differs")
    schedule_path = SCHEDULE_DIR / "discovery-arms.jsonl"
    schedule_manifest_path = SCHEDULE_DIR / "manifest.json"
    schedule_verification_path = SCHEDULE_DIR / "verification.json"
    expected_schedule = {
        "arms_sha256": sha(schedule_path),
        "manifest_sha256": sha(schedule_manifest_path),
        "verification_sha256": sha(schedule_verification_path),
        "graph_manifest_sha256": sha(STUDY / "manifest-v2.json"),
        "arm_count": 8206, "target_probes": 60889088,
    }
    if (admission.get("schedule") != expected_schedule or
            set(admission.get("strata", {})) != {"P29", "P37"}):
        raise ValueError("admission does not bind the exact full graph schedule")
    family_commitments = {family: admission["strata"][family]["commitment_path"]
                          for family in ("P29", "P37")}
    root_files = admission["root_files"]
    if set(root_files) != {"base", "target", "verifier"}:
        raise ValueError("study admission must bind the base, target and verifier roots")
    if set(admission.get("binaries", {})) != {
            "collector_path", "collector_sha256", "count_verifier_path", "count_verifier_sha256"}:
        raise ValueError("study admission binary binding is incomplete")
    for value in [*root_files.values(), *family_commitments.values(),
                  admission["binaries"]["collector_path"],
                  admission["binaries"]["count_verifier_path"]]:
        repo_file(value)
    run_ids = read_run_ids(run_ids_path, 8206)
    sys.path.insert(0, str(ROOT / "tools"))
    import allocate_id
    if allocate_id.check_run_id_file(run_ids_path) != 0:
        raise ValueError("RUN-ID list failed the repository-wide allocator check")
    sys.path.insert(0, str(STUDY / "preparation"))
    from execute_graph_prepared import check_frozen_sources, source_paths
    source_commit = admission.get("source_commit")
    check_frozen_sources(ROOT, [*source_paths().values(), *SOURCE_PATHS], source_commit)
    expected_admission_sources = {rel(path): sha(path) for path in source_paths().values()}
    if admission.get("source_sha256") != expected_admission_sources:
        raise ValueError("admission source hashes do not match current frozen sources")
    binaries = admission["binaries"]
    if (sha(repo_file(binaries["collector_path"])) != binaries["collector_sha256"] or
            sha(repo_file(binaries["count_verifier_path"])) != binaries["count_verifier_sha256"]):
        raise ValueError("collector binary digest differs from admission")
    sys.path.insert(0, str(STUDY / "graph_input_schedule_20261023"))
    from materialize import check_commitment, load_schedule
    root_paths = {name: repo_file(path) for name, path in root_files.items()}
    for family in ("P29", "P37"):
        commitment_path = repo_file(family_commitments[family])
        _, row = load_schedule(f"{family}-v0000-graph_transport")
        check_commitment(row, root_paths, commitment_path)
    collector = admission["binaries"]["collector_path"]
    count_verifier = admission["binaries"]["count_verifier_path"]
    rows = load_rows()
    trials = make_trials(rows, run_ids, experiment_id=spec["id"], root_files=root_files,
                         commitments=family_commitments, admission_path=rel(admission_path),
                         collector=collector, count_verifier=count_verifier)
    sources = {rel(path): sha(path) for path in SOURCE_PATHS}
    plan = {
        "schema": "crypto.autoresearch.trial_plan.v1", "experiment_id": spec["id"],
        "task_id": admission["task_id"], "approved_by": decision["id"],
        "specification": rel(specification_path), "specification_sha256": sha(specification_path),
        "queue": rel(queue_path), "frozen": True,
        "source_sha256": sources, "trials": trials,
        "scope_note": "Fixed 8,206-arm discovery schedule: 7,175 P29 arms and 1,031 P37 arms; all four full-quota check arms are retained at every scheduled check vertex. Every scheduled arm has one allocated RUN ID and a write-once receipt.",
    }
    encoded = (json.dumps(plan, indent=2, sort_keys=True) + "\n").encode()
    with output_path.open("xb") as stream:
        stream.write(encoded)
    return {"schema": "ectd.graph-discovery-trial-plan-build.v1", "status": "built",
            "experiment_id": spec["id"], "trial_count": len(trials),
            "schedule_sha256": sha(SCHEDULE_DIR / "discovery-arms.jsonl"),
            "trial_plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "run_id_count": len(set(run_ids)), "output": str(output_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="store_true",
                        help="build a pre-approval candidate that the execution loader refuses")
    parser.add_argument("--specification", type=Path, required=True)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--decision", type=Path)
    parser.add_argument("--queue")
    parser.add_argument("--run-ids", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--task-id")
    parser.add_argument("--base-root-file")
    parser.add_argument("--target-root-file")
    parser.add_argument("--verifier-root-file")
    parser.add_argument("--commitment-p29")
    parser.add_argument("--commitment-p37")
    parser.add_argument("--collector")
    parser.add_argument("--count-verifier")
    parser.add_argument("--source-commit")
    args = parser.parse_args()
    if args.candidate:
        required = (args.queue, args.task_id, args.base_root_file, args.target_root_file,
                    args.verifier_root_file, args.commitment_p29, args.commitment_p37,
                    args.collector, args.count_verifier)
        if any(value is None for value in required):
            parser.error("--candidate requires queue/task, three root files, two commitments and both binaries")
        result = build_candidate(
            args.specification, task_id=args.task_id, queue_path=args.queue,
            root_files={"base": args.base_root_file, "target": args.target_root_file,
                        "verifier": args.verifier_root_file},
            commitments={"P29": args.commitment_p29, "P37": args.commitment_p37},
            collector_path=args.collector, count_verifier_path=args.count_verifier,
            source_commit=args.source_commit, run_ids_path=args.run_ids,
            output_path=args.output)
    else:
        if not args.admission or not args.decision or not args.queue:
            parser.error("approved plan build requires --admission, --decision and --queue")
        result = build(args.specification, args.admission, args.decision,
                       Path(args.queue), args.run_ids, args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
