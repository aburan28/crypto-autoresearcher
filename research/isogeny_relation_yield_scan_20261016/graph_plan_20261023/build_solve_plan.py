"""Compile analyzed confirmation finalists into solve-stage relation/solver trials.

This compiler emits candidate-only plans. It never makes or reveals a seed and
does not create the Coordinator approval record or an executable dispatch plan.
"""
from __future__ import annotations

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
SOLVE_PREPARER = STUDY / "preparation/prepare_graph_solve_input.py"
SOLVER = STUDY / "graph_solve_candidate_20261023/solve.py"
SOLVE_CHECKER = STUDY / "graph_solve_candidate_20261023/check.py"
RHO_DRIVER = STUDY / "graph_trial_adapter_20261023/matched_rho.py"
RHO_CHECKER = STUDY / "graph_trial_adapter_20261023/check_matched_rho.py"
RUN_ID = re.compile(r"^RUN-ECTD-[0-9a-f]{6}$")
ARMS = ("low_x", "mid_x", "random_x")
SOURCE_PATHS = (
    DRIVER, CHECKER, WRAPPER, MATERIALIZER, SOLVE_PREPARER,
    RHO_DRIVER, RHO_CHECKER,
    SOLVER, SOLVE_CHECKER,
    HERE / "study_admission.py", HERE / "build_confirmation_plan.py",
    HERE / "build_solve_plan.py", HERE / "finalist_solve_contract.yaml",
    STUDY / "preparation/prepare_graph_input.py",
    STUDY / "preparation/verify_prepared_graph.py",
    ROOT / "research/conductor_relation_yield_20261014/prepare_input.py",
    ROOT / "research/conductor_relation_yield_20261014/execute_prepared.py",
    ROOT / "research/conductor_relation_yield_20261014/collector.rs",
    ROOT / "research/conductor_relation_yield_20261014/count_verify.cpp",
    ROOT / "research/conductor_relation_yield_20261014/verify_collector.py",
    SCHEDULE_DIR / "discovery-arms.jsonl", SCHEDULE_DIR / "manifest.json",
    SCHEDULE_DIR / "verification.json", STUDY / "manifest-v2.json",
    STUDY / "walk-p29-2048-attempt2.jsonl", STUDY / "walk-p37-256.jsonl",
    STUDY / "graph_selection_candidate_20261023/discovery_select.py",
    STUDY / "graph_confirmation_candidate_20261023/confirm.py",
    ROOT / "experiments/EXP-ECTD-001/driver/rho_bsgs.py",
    ROOT / "experiments/EXP-ECTD-001/driver/curve.py",
    ROOT / "tools/experiment_execution.py", ROOT / "tools/allocate_id.py",
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


def finalist_rows(analysis: dict, selection: dict, selection_sha256: str,
                  schedule_path: Path = SCHEDULE_DIR / "discovery-arms.jsonl") -> list[dict]:
    if (analysis.get("schema") != "ectd.graph-confirmation-analysis-candidate/v1" or
            analysis.get("status") != "confirmed_receipts_analyzed" or
            analysis.get("selection_sha256") is None or
            analysis.get("schedule_sha256") != sha(schedule_path) or
            selection.get("schema") != "ectd.graph-discovery-selection-candidate/v1" or
            selection.get("status") != "selected_from_validated_discovery" or
            selection.get("discovery_arms_checked") != 8206 or
            selection.get("schedule_sha256") != sha(schedule_path) or
            analysis.get("selection_sha256") != selection_sha256):
        raise ValueError("validated confirmation analysis and exact selected-discovery receipt required")
    schedule = {json.loads(line)["arm_key"]: json.loads(line)
                for line in schedule_path.read_text().splitlines()}
    rows = []
    seen = set()
    for stratum in ("P29", "P37"):
        chosen = {item["index"]: item for item in
                  selection.get("strata", {}).get(stratum, {}).get("selected_vertices", [])}
        finalists = analysis.get("finalists", {}).get(stratum, [])
        if not 1 <= len(finalists) <= 6:
            raise ValueError(f"confirmation must nominate 1..6 finalists in {stratum}")
        for item in finalists:
            index = item.get("index")
            if index not in chosen or (stratum, index) in seen:
                raise ValueError(f"finalist is not a unique prespecified selected vertex: {stratum}:{index}")
            seen.add((stratum, index))
            for arm in ARMS:
                key = f"{stratum}-v{index:04d}-{arm}"
                row = schedule.get(key)
                if row is None or row.get("base_rule") != arm or row.get("model", {}).get("j") != item.get("j"):
                    raise ValueError(f"finalist schedule row differs: {key}")
                rows.append(row)
    if len(rows) > 36 or len({row["arm_key"] for row in rows}) != len(rows):
        raise ValueError("solve relation workload exceeds the frozen 36-arm cap")
    return rows


def read_run_ids(path: Path, count: int) -> list[str]:
    values = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if len(values) != count or len(set(values)) != count or any(not RUN_ID.fullmatch(x) for x in values):
        raise ValueError(f"run id file must contain {count} unique allocator-form ids")
    sys.path.insert(0, str(ROOT / "tools"))
    import allocate_id
    if allocate_id.check_run_id_file(path) != 0:
        raise ValueError("run ids fail allocator validation")
    return values


def make_trials(rows: list[dict], run_ids: list[str], *, experiment_id: str,
                root_files: dict, commitments: dict, admission_path: str,
                collector_path: str, count_verifier_path: str, sage_path: str) -> list[dict]:
    if not rows or len(rows) != len(run_ids) or len(rows) > 36:
        raise ValueError("solve-stage trials must cover 1..36 rows with unique RUN ids")
    for value in (*root_files.values(), *commitments.values(), collector_path,
                  count_verifier_path):
        repo_file(value)
    if not Path(sage_path).is_file():
        raise ValueError("Sage executable does not exist")
    if set(root_files) != {"base", "target", "verifier"} or set(commitments) != {"P29", "P37"}:
        raise ValueError("solve stage requires the three roots and one commitment per stratum")
    trials = []
    for row, run_id in zip(rows, run_ids):
        family = row["stratum"]
        args = [sys.executable, rel(DRIVER), "--arm-key", row["arm_key"],
                "--stage", "solve", "--collector", collector_path,
                "--count-verifier", count_verifier_path, "--out", "{output_dir}",
                "--admission", admission_path, "--sage", sage_path,
                "--base-root-file", root_files["base"],
                "--target-root-file", root_files["target"],
                "--verifier-root-file", root_files["verifier"],
                "--commitment", commitments[family], "--watchdog-seconds", "1830",
                "--memory-gib", "4" if family == "P29" else "8"]
        check_args = [sys.executable, rel(CHECKER), "--run-dir", "{output_dir}",
                      "--admission", admission_path,
                      "--collector", collector_path,
                      "--count-verifier", count_verifier_path]
        artifacts = ["manifest.yaml", "raw-result.json", "driver.stdout", "driver.stderr",
                     "materializer.stdout", "materializer.stderr", "prepared/prepared.txt",
                     "prepared/manifest.json", "prepared/binding.json", "attempt/events.jsonl",
                     "attempt/receipt.json", "attempt/input_verify.stdout",
                     "attempt/input_verify.stderr", "attempt/collector.stdout",
                     "attempt/collector.stderr", "attempt/count.stdout", "attempt/count.stderr",
                     "attempt/rank_verify.stdout", "attempt/rank_verify.stderr",
                     "solve/solve.json", "solve/solver.stdout", "solve/solver.stderr",
                     "solve/checker.stdout", "solve/checker.stderr"]
        trials.append({"id": row["arm_key"], "run_id": run_id, "argv": args,
                       "check_argv": check_args, "artifacts": artifacts,
                       "memory_mb": 4096 if family == "P29" else 8192,
                       "watchdog_seconds": 1830,
                       "parameters": {"stage": "solve", "stratum": family,
                                      "index": row["path_index"], "arm": row["base_rule"],
                                      "target_count": 32768},
                       "depends_on": []})
    return trials


def make_rho_trials(rows: list[dict], rho_run_ids: list[str],
                    relation_run_ids: dict[str, str], rho_seeds: list[int], *,
                    experiment_id: str) -> list[dict]:
    finalists = sorted({(row["stratum"], row["path_index"], row["model"]["j"])
                        for row in rows})
    if (not finalists or len(finalists) > 12 or len(rho_seeds) != 10 or
            len(set(rho_seeds)) != 10 or any(not isinstance(x, int) or x < 0 for x in rho_seeds) or
            len(rho_run_ids) != 10 * len(finalists)):
        raise ValueError("rho workload requires ten unique seeds for each of 1..12 finalists")
    trials = []
    cursor = 0
    for family, index, j_value in finalists:
        low_id = f"{family}-v{index:04d}-low_x"
        base = f"experiments/{experiment_id}/runs/{relation_run_ids[low_id]}/prepared"
        dependencies = [f"{family}-v{index:04d}-{arm}" for arm in ARMS]
        for repetition, seed in enumerate(rho_seeds):
            task_id = f"{family}-v{index:04d}-rho-{repetition:02d}"
            out = "{output_dir}/rho-result.json"
            argv = [sys.executable, rel(RHO_DRIVER), "--input", base + "/prepared.txt",
                    "--manifest", base + "/manifest.json", "--seed", str(seed),
                    "--max-steps", "60000000", "--out", out]
            check_argv = [sys.executable, rel(RHO_CHECKER), "--input", base + "/prepared.txt",
                          "--manifest", base + "/manifest.json", "--result", out]
            trials.append({
                "id": task_id, "run_id": rho_run_ids[cursor],
                "argv": argv, "check_argv": check_argv,
                "artifacts": ["rho-result.json"], "allow_empty_artifacts": [],
                "memory_mb": 2048, "watchdog_seconds": 1830,
                "watchdog_reason": "Plain-rho inner cap is fixed at 60,000,000 steps per repetition.",
                "parameters": {"stage": "solve", "baseline": "plain_rho",
                               "stratum": family, "index": index, "j": j_value,
                               "repetition": repetition, "seed": seed,
                               "max_steps": 60000000},
                "depends_on": dependencies,
            })
            cursor += 1
    return trials


def build_candidate(specification_path: Path, *, task_id: str, queue_path: str,
                    selection_path: Path, analysis_path: Path,
                    prior_confirmation_admission_path: Path, root_files: dict,
                    commitments: dict, collector_path: str,
                    count_verifier_path: str, sage_path: Path,
                    relation_run_ids_path: Path, rho_run_ids_path: Path,
                    rho_seeds_path: Path, output_path: Path,
                    source_commit: str | None = None) -> dict:
    from materialize import check_commitment, load_schedule
    from build_confirmation_plan import SOURCE_PATHS as confirmation_sources
    from execute_graph_prepared import check_frozen_sources, source_paths

    specification_path, selection_path, analysis_path, prior_confirmation_admission_path = map(
        Path.resolve, (specification_path, selection_path, analysis_path,
                      prior_confirmation_admission_path))
    output_path = output_path.resolve()
    spec_doc = yaml.safe_load(specification_path.read_text())
    spec = spec_doc.get("experiment", spec_doc)
    if (spec.get("status") != "review_required" or spec.get("frozen") is not True or
            spec.get("execution_authorized") is not False or spec.get("approved_by")):
        raise ValueError("solve candidate requires an unapproved frozen review_required specification")
    experiment_id = spec["id"]
    if (rel(specification_path) != f"experiments/{experiment_id}/specification.yaml" or
            not output_path.is_relative_to(ROOT / "experiments" / experiment_id)):
        raise ValueError("candidate specification/output must be in its canonical EXP directory")
    if (not task_id.strip() or not queue_path or Path(queue_path).is_absolute() or
            ".." in Path(queue_path).parts):
        raise ValueError("candidate requires a task and repository-relative queue binding")
    prior = json.loads(prior_confirmation_admission_path.read_text())
    if (prior.get("schema") != "ectd.graph-study-admission.v1" or
            prior.get("status") != "approved" or prior.get("approved_by") != "coordinator" or
            prior.get("execution_stage") != 1 or prior.get("experiment_id") != experiment_id):
        raise ValueError("approved stage-1 confirmation admission required")
    selection_doc = json.loads(selection_path.read_text())
    if (prior.get("selection_path") != rel(selection_path) or
            prior.get("selection_sha256") != sha(selection_path)):
        raise ValueError("selection differs from the approved confirmation admission")
    analysis = json.loads(analysis_path.read_text())
    if analysis.get("experiment_id") != experiment_id:
        raise ValueError("confirmation analysis belongs to a different experiment")
    selection_doc["_sha256"] = sha(selection_path)
    rows = finalist_rows(analysis, selection_doc, sha(selection_path))

    root_paths = {name: repo_file(value) for name, value in root_files.items()}
    if set(root_paths) != {"base", "target", "verifier"}:
        raise ValueError("solve admission requires exactly the three roots")
    prior_roots = {name: repo_file(value) for name, value in prior.get("root_files", {}).items()}
    if set(prior_roots) != {"base", "target", "verifier"}:
        raise ValueError("confirmation admission root set differs")
    discovery_path = repo_file(prior.get("prior_admission_path", ""))
    discovery = json.loads(discovery_path.read_text())
    discovery_roots = {name: repo_file(value) for name, value in discovery.get("root_files", {}).items()}
    if set(discovery_roots) != {"base", "target", "verifier"}:
        raise ValueError("discovery ancestry root set differs")
    if (root_paths["base"].read_bytes() != prior_roots["base"].read_bytes() or
            root_paths["verifier"].read_bytes() != prior_roots["verifier"].read_bytes() or
            root_paths["target"].read_bytes() in
            (prior_roots["target"].read_bytes(), discovery_roots["target"].read_bytes())):
        raise ValueError("solve target root must be fresh while base/verifier roots are reused")
    if set(commitments) != {"P29", "P37"}:
        raise ValueError("solve commitments must bind both strata")
    commitment_digests = {}
    for family in ("P29", "P37"):
        commitment = repo_file(commitments[family])
        _, row = load_schedule(f"{family}-v0000-low_x", "solve")
        actual_roots, _ = check_commitment(row, root_paths, commitment)
        prior_digest = prior.get("strata", {}).get(family, {}).get("commitment_sha256")
        if sha(commitment) == prior_digest:
            raise ValueError(f"solve reuses the confirmation commitment for {family}")
        commitment_digests[family] = {
            "path": commitments[family], "sha256": sha(commitment),
            "graph_sha256": sha(STUDY / ("walk-p29-2048-attempt2.jsonl" if family == "P29" else "walk-p37-256.jsonl")),
            **{name + "_root_sha256": hashlib.sha256(value).hexdigest()
               for name, value in actual_roots.items()},
        }
    if commitment_digests["P29"]["sha256"] == commitment_digests["P37"]["sha256"]:
        raise ValueError("P29 and P37 solve commitments must differ")

    sage_path = Path(sage_path).resolve()
    if not sage_path.is_file():
        raise ValueError("Sage executable is missing")
    collector = repo_file(collector_path)
    count_verifier = repo_file(count_verifier_path)
    relation_ids = read_run_ids(relation_run_ids_path, len(rows))
    rho_count = 10 * (len(rows) // 3)
    rho_ids = read_run_ids(rho_run_ids_path, rho_count)
    seed_values = [int(line.strip()) for line in rho_seeds_path.read_text().splitlines()
                   if line.strip()]
    if (len(seed_values) != 10 or len(set(seed_values)) != 10 or
            any(value < 0 for value in seed_values)):
        raise ValueError("rho seed file must contain ten unique nonnegative integers")
    if source_commit is None:
        source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                cwd=ROOT, text=True).strip()
    frozen_paths = list(dict.fromkeys([
        *source_paths().values(), *confirmation_sources, *SOURCE_PATHS,
        STUDY / "preparation/verify_prepared_graph.py",
    ]))
    check_frozen_sources(ROOT, frozen_paths, source_commit)
    sources = {rel(path): sha(path) for path in frozen_paths}
    relation_trials = make_trials(
        rows, relation_ids, experiment_id=experiment_id, root_files=root_files,
        commitments=commitments,
        admission_path=f"experiments/{experiment_id}/graph-study-admission-solve.json",
        collector_path=collector_path, count_verifier_path=count_verifier_path,
        sage_path=str(sage_path))
    relation_run_by_id = {row["arm_key"]: run_id
                          for row, run_id in zip(rows, relation_ids)}
    rho_trials = make_rho_trials(rows, rho_ids, relation_run_by_id, seed_values,
                                 experiment_id=experiment_id)
    body = {
        "schema": "crypto.autoresearch.trial_plan.v1",
        "experiment_id": experiment_id, "task_id": task_id,
        "candidate_only": True, "approval_required": True,
        "frozen": True, "stop_on_invalid_output": True,
        "specification": rel(specification_path),
        "specification_sha256": sha(specification_path), "queue": queue_path,
        "source_commit": source_commit, "source_sha256": sources,
        "stage": "solve", "execution_stage": 2,
        "schedule_sha256": sha(SCHEDULE_DIR / "discovery-arms.jsonl"),
        "selection": {"path": rel(selection_path), "sha256": sha(selection_path)},
        "finalist_analysis": {"path": rel(analysis_path), "sha256": sha(analysis_path)},
        "prior_confirmation_admission": {
            "path": rel(prior_confirmation_admission_path),
            "sha256": sha(prior_confirmation_admission_path)},
        "prior_discovery_admission": {"path": rel(discovery_path), "sha256": sha(discovery_path)},
        "root_files": {name: {"path": value, "sha256": sha(root_paths[name])}
                       for name, value in root_files.items()},
        "commitments": commitment_digests,
        "binaries": {"collector": {"path": collector_path, "sha256": sha(collector)},
                     "count_verifier": {"path": count_verifier_path, "sha256": sha(count_verifier)},
                     "sage": {"path": str(sage_path), "sha256": sha(sage_path)}},
        "rho_seed_file": {"path": rel(rho_seeds_path), "sha256": sha(rho_seeds_path)},
        "target_count_per_arm": 32768,
        "relation_trial_count": len(relation_trials),
        "rho_trial_count": len(rho_trials),
        "trials": relation_trials + rho_trials,
        "scope_note": "Candidate finalist relation/solver and matched-rho workload from fresh solve roots. Path-map transfer timing still requires the frozen path-transfer phase before this stage is complete.",
    }
    encoded = (json.dumps(body, indent=2, sort_keys=True) + "\n").encode()
    with output_path.open("xb") as stream:
        stream.write(encoded)
    return {"schema": "ectd.graph-solve-candidate-plan-build.v1",
            "status": "candidate_only", "relation_trials": len(relation_trials),
            "rho_trials": len(rho_trials), "candidate_plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "output": str(output_path)}
