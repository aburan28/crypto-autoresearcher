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
TRANSFER_DRIVER = STUDY / "graph_trial_adapter_20261023/path_transfer.py"
TRANSFER_CHECKER = STUDY / "graph_trial_adapter_20261023/check_path_transfer.py"
RUN_ID = re.compile(r"^RUN-ECTD-[0-9a-f]{6}$")
ARMS = ("low_x", "mid_x", "random_x")
SOURCE_PATHS = (
    DRIVER, CHECKER, WRAPPER, MATERIALIZER, SOLVE_PREPARER,
    RHO_DRIVER, RHO_CHECKER, TRANSFER_DRIVER, TRANSFER_CHECKER,
    SOLVER, SOLVE_CHECKER,
    HERE / "study_admission.py", HERE / "prepared_worker.py",
    HERE / "prepare_worker_catalog.py", HERE / "build_confirmation_plan.py",
    HERE / "build_solve_plan.py", HERE / "finalist_solve_contract.yaml",
    HERE / "aggregate_solve_costs.py",
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
                collector_path: str, count_verifier_path: str, sage_path: str,
                prepared_catalog: Path | None = None) -> list[dict]:
    prepared_admission = None
    prepared_arms = None
    if prepared_catalog is not None:
        sys.path.insert(0, str(HERE))
        from prepared_worker import load_worker_catalog
        prepared_admission, prepared_arms = load_worker_catalog(
            prepared_catalog, rows, experiment_id, 2)
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
        if prepared_arms is None:
            args = [sys.executable, rel(DRIVER), "--arm-key", row["arm_key"],
                    "--stage", "solve", "--collector", collector_path,
                    "--count-verifier", count_verifier_path, "--out", "{output_dir}",
                    "--admission", admission_path, "--sage", sage_path,
                    "--base-root-file", root_files["base"],
                    "--target-root-file", root_files["target"],
                    "--verifier-root-file", root_files["verifier"],
                    "--commitment", commitments[family]]
            trial_artifacts = ["manifest.yaml", "raw-result.json", "driver.stdout", "driver.stderr",
                     "materializer.stdout", "materializer.stderr", "prepared/prepared.txt",
                     "prepared/manifest.json", "prepared/binding.json", "attempt/events.jsonl",
                     "attempt/receipt.json", "attempt/input_verify.stdout",
                     "attempt/input_verify.stderr", "attempt/collector.stdout",
                     "attempt/collector.stderr", "attempt/count.stdout", "attempt/count.stderr",
                     "attempt/rank_verify.stdout", "attempt/rank_verify.stderr",
                     "solve/solve.json", "solve/solver.stdout", "solve/solver.stderr",
                     "solve/checker.stdout", "solve/checker.stderr"]
        else:
            prepared = prepared_arms[row["arm_key"]]
            args = [sys.executable, rel(DRIVER), "--input", rel(prepared["input"]),
                    "--prepared-manifest", rel(prepared["manifest"]),
                    "--prepared-worker-admission", rel(prepared_admission),
                    "--binding", rel(prepared["binding"]), "--stage", "solve",
                    "--collector", collector_path, "--count-verifier", count_verifier_path,
                    "--out", "{output_dir}", "--sage", sage_path]
            trial_artifacts = [item for item in ("manifest.yaml", "raw-result.json", "driver.stdout", "driver.stderr",
                     "attempt/events.jsonl", "attempt/receipt.json", "attempt/input_verify.stdout",
                     "attempt/input_verify.stderr", "attempt/collector.stdout", "attempt/collector.stderr",
                     "attempt/count.stdout", "attempt/count.stderr", "attempt/rank_verify.stdout",
                     "attempt/rank_verify.stderr", "solve/solve.json", "solve/solver.stdout",
                     "solve/solver.stderr", "solve/checker.stdout", "solve/checker.stderr")]
        args += ["--watchdog-seconds", "1830", "--memory-gib",
                 "4" if family == "P29" else "8"]
        check_admission = rel(prepared_admission) if prepared_admission else admission_path
        check_args = [sys.executable, rel(CHECKER), "--run-dir", "{output_dir}",
                      "--admission", check_admission,
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
                       "check_argv": check_args, "artifacts": trial_artifacts,
                       "memory_mb": 4096 if family == "P29" else 8192,
                       "watchdog_seconds": 1830,
                       "parameters": {"stage": "solve", "stratum": family,
                                      "index": row["path_index"], "arm": row["base_rule"],
                                      "target_count": 32768},
                       "depends_on": []})
    return trials


def make_rho_trials(rows: list[dict], rho_run_ids: list[str],
                    relation_run_ids: dict[str, str], rho_seeds: list[int], *,
                    experiment_id: str,
                    prepared_arms: dict[str, dict] | None = None) -> list[dict]:
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
        if prepared_arms is None:
            base = f"experiments/{experiment_id}/runs/{relation_run_ids[low_id]}/prepared"
            input_path = base + "/prepared.txt"
            manifest_path = base + "/manifest.json"
            dependencies = [f"{family}-v{index:04d}-{arm}" for arm in ARMS]
            input_digest = None
        else:
            prepared = prepared_arms[low_id]
            input_path = rel(prepared["input"])
            manifest_path = rel(prepared["manifest"])
            dependencies = []
            input_digest = sha(prepared["input"])
        for repetition, seed in enumerate(rho_seeds):
            task_id = f"{family}-v{index:04d}-rho-{repetition:02d}"
            out = "{output_dir}/rho-result.json"
            argv = [sys.executable, rel(RHO_DRIVER), "--input", input_path,
                    "--manifest", manifest_path, "--seed", str(seed),
                    "--max-steps", "60000000", "--out", out]
            check_argv = [sys.executable, rel(RHO_CHECKER), "--input", input_path,
                          "--manifest", manifest_path, "--result", out]
            parameters = {"stage": "solve", "baseline": "plain_rho",
                          "stratum": family, "index": index, "j": j_value,
                          "repetition": repetition, "seed": seed,
                          "max_steps": 60000000}
            if input_digest is not None:
                parameters["prepared_input_sha256"] = input_digest
            trials.append({
                "id": task_id, "run_id": rho_run_ids[cursor],
                "argv": argv, "check_argv": check_argv,
                "artifacts": ["rho-result.json"], "allow_empty_artifacts": [],
                "memory_mb": 2048, "watchdog_seconds": 1830,
                "watchdog_reason": "Plain-rho inner cap is fixed at 60,000,000 steps per repetition.",
                "parameters": parameters,
                "depends_on": dependencies,
            })
            cursor += 1
    return trials


def make_transfer_trials(rows: list[dict], transfer_run_ids: list[str], *,
                         experiment_id: str,
                         relation_run_ids: dict[str, str],
                         prepared_arms: dict[str, dict] | None = None,
                         sage_path: str | None = None) -> list[dict]:
    """Map the same public source G,Q pair to each finalist and retain path costs."""
    finalists = sorted({(row["stratum"], row["path_index"], row["model"]["j"])
                        for row in rows})
    if not finalists or len(transfer_run_ids) != len(finalists):
        raise ValueError("one transfer trial id is required for each finalist")
    if sage_path is None or not Path(sage_path).is_file():
        raise ValueError("Sage executable is required for path transfer")
    trials = []
    source_points_by_stratum: dict[str, str] = {}
    target_vectors_by_stratum: dict[str, str] = {}
    for (family, index, _), run_id in zip(finalists, transfer_run_ids):
        low_id = f"{family}-v{index:04d}-low_x"
        if prepared_arms is None:
            manifest = (f"experiments/{experiment_id}/runs/"
                        f"{relation_run_ids[low_id]}/prepared/manifest.json")
            dependencies = [low_id]
        else:
            low_manifest_path = Path(prepared_arms[low_id]["manifest"])
            low_manifest = json.loads(low_manifest_path.read_text())
            manifest = rel(low_manifest_path)
            dependencies = []
            source_digest = low_manifest.get("source_points_sha256")
            if not isinstance(source_digest, str) or len(source_digest) != 64:
                raise ValueError("prepared solve manifest lacks public source G,Q points")
            if family in source_points_by_stratum and source_points_by_stratum[family] != source_digest:
                raise ValueError("solve finalists do not share the stratum source G,Q pair")
            source_points_by_stratum[family] = source_digest
            target_digest = low_manifest.get("target_vector_sha256")
            if not isinstance(target_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", target_digest):
                raise ValueError("prepared solve manifest lacks a valid target-vector digest")
            if family in target_vectors_by_stratum and target_vectors_by_stratum[family] != target_digest:
                raise ValueError("solve finalists do not share the stratum target vector")
            target_vectors_by_stratum[family] = target_digest
            for arm in ARMS:
                arm_manifest = json.loads(Path(prepared_arms[
                    f"{family}-v{index:04d}-{arm}"]["manifest"]).read_text())
                for key in ("source_points_sha256", "source_generator", "source_Q",
                            "generator", "Q", "target_vector_sha256"):
                    if arm_manifest.get(key) != low_manifest.get(key):
                        raise ValueError("finalist treatments do not share exact G,Q and targets")
        transfer = f"{family}-v{index:04d}-path-transfer"
        output = "{output_dir}/transfer.json"
        argv = [sage_path, "-python", rel(TRANSFER_DRIVER), "--stratum", family,
                "--index", str(index), "--source-manifest", manifest,
                "--endpoint-manifest", manifest, "--out", output]
        check_argv = [sage_path, "-python", rel(TRANSFER_CHECKER), "--stratum", family,
                      "--index", str(index), "--source-manifest", manifest,
                      "--endpoint-manifest", manifest, "--result", output,
                      "--out", "{output_dir}/transfer-check.json"]
        trials.append({
            "id": transfer, "run_id": run_id,
            "argv": argv, "check_argv": check_argv,
            "artifacts": ["transfer.json", "transfer-check.json"],
            "allow_empty_artifacts": [],
            "memory_mb": 4096 if family == "P29" else 8192,
            "watchdog_seconds": 1830,
            "watchdog_reason": "Saved-path transfer covers the finalist's exact source-to-endpoint edge prefix.",
            "parameters": {"stage": "solve", "phase": "path_transfer",
                           "stratum": family, "index": index,
                           "edge_count": index,
                           "source_arm": "low_x",
                           "same_public_G_Q_as_all_treatments": True,
                           "scalar_or_seed_in_worker_argv": False},
            "depends_on": dependencies,
        })
    return trials


def build_candidate(specification_path: Path, *, task_id: str, queue_path: str,
                    selection_path: Path, analysis_path: Path,
                    prior_confirmation_admission_path: Path, root_files: dict,
                    commitments: dict, collector_path: str,
                    count_verifier_path: str, sage_path: Path,
                    relation_run_ids_path: Path, transfer_run_ids_path: Path,
                    rho_run_ids_path: Path,
                    rho_seeds_path: Path, output_path: Path,
                    source_commit: str | None = None,
                    prepared_catalog: Path | None = None) -> dict:
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
    transfer_ids = read_run_ids(transfer_run_ids_path, len(rows) // 3)
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
        sage_path=str(sage_path), prepared_catalog=prepared_catalog)
    prepared_admission = None
    prepared_arms = None
    if prepared_catalog is not None:
        from prepared_worker import load_worker_catalog
        prepared_admission, prepared_arms = load_worker_catalog(
            prepared_catalog, rows, experiment_id, 2)
    relation_run_by_id = {row["arm_key"]: run_id
                          for row, run_id in zip(rows, relation_ids)}
    rho_trials = make_rho_trials(rows, rho_ids, relation_run_by_id, seed_values,
                                 experiment_id=experiment_id,
                                 prepared_arms=prepared_arms)
    transfer_trials = make_transfer_trials(
        rows, transfer_ids, experiment_id=experiment_id,
        relation_run_ids=relation_run_by_id, prepared_arms=prepared_arms,
        sage_path=str(sage_path))
    body = {
        "schema": "crypto.autoresearch.trial_plan.v1",
        "experiment_id": experiment_id, "task_id": task_id,
        "candidate_only": True, "approval_required": True,
        "frozen": True, "stop_on_invalid_output": True,
        "specification": rel(specification_path),
        "specification_sha256": sha(specification_path), "queue": queue_path,
        "source_commit": source_commit, "source_sha256": sources,
        "stage": "solve", "execution_stage": 2,
        "cost_aggregator": {"path": rel(HERE / "aggregate_solve_costs.py"),
                            "sha256": sha(HERE / "aggregate_solve_costs.py")},
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
        **({"prepared_catalog": {"path": rel(prepared_catalog.resolve()),
                                  "sha256": sha(prepared_catalog.resolve())},
            "prepared_worker_admission": {"path": rel(prepared_admission),
                                          "sha256": sha(prepared_admission)}}
           if prepared_catalog is not None else {}),
        "target_count_per_arm": 32768,
        "relation_trial_count": len(relation_trials),
        "transfer_trial_count": len(transfer_trials),
        "rho_trial_count": len(rho_trials),
        "trials": relation_trials + transfer_trials + rho_trials,
        "scope_note": "Candidate finalist relation/solver, public-point path transfer, and matched-rho workload from fresh solve roots. Path transfer never receives a scalar or verifier root.",
    }
    encoded = (json.dumps(body, indent=2, sort_keys=True) + "\n").encode()
    with output_path.open("xb") as stream:
        stream.write(encoded)
    return {"schema": "ectd.graph-solve-candidate-plan-build.v1",
            "status": "candidate_only", "relation_trials": len(relation_trials),
            "transfer_trials": len(transfer_trials), "rho_trials": len(rho_trials),
            "candidate_plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "output": str(output_path)}


def build_approved(candidate_path: Path, admission_path: Path,
                   decision_path: Path, specification_path: Path,
                   output_path: Path, prepared_catalog: Path) -> dict:
    """Compile the approved solve candidate into a rootless executor plan."""
    from study_admission import validate_approval_fields
    from prepared_worker import load_worker_catalog

    candidate_path, admission_path, decision_path, specification_path, prepared_catalog = map(
        Path.resolve, (candidate_path, admission_path, decision_path,
                      specification_path, prepared_catalog))
    candidate = json.loads(candidate_path.read_text())
    admission = json.loads(admission_path.read_text())
    decision_doc = yaml.safe_load(decision_path.read_text())
    specification_doc = yaml.safe_load(specification_path.read_text())
    if (candidate.get("schema") != "crypto.autoresearch.trial_plan.v1" or
            candidate.get("candidate_only") is not True or
            candidate.get("approval_required") is not True or
            admission.get("schema") != "ectd.graph-study-admission.v1" or
            admission.get("status") != "approved" or
            admission.get("approved_by") != "coordinator" or
            admission.get("execution_stage") != 2):
        raise ValueError("solve candidate and Coordinator stage-2 admission required")
    decision, specification, stage = validate_approval_fields(
        admission, decision_doc, specification_doc)
    experiment_id = candidate.get("experiment_id")
    if (stage != 2 or decision.get("id") != admission.get("decision_id") or
            experiment_id != admission.get("experiment_id") or
            admission.get("specification_path") != rel(specification_path) or
            admission.get("specification_sha256") != sha(specification_path) or
            candidate.get("specification") != rel(specification_path) or
            candidate.get("specification_sha256") != sha(specification_path) or
            admission.get("task_id") != candidate.get("task_id") or
            admission.get("source_commit") != candidate.get("source_commit") or
            admission.get("source_sha256") != candidate.get("source_sha256") or
            candidate.get("schedule_sha256") != sha(SCHEDULE_DIR / "discovery-arms.jsonl") or
            admission.get("output_prefix") != f"experiments/{experiment_id}/runs"):
        raise ValueError("stage-2 admission does not bind this solve candidate")
    expected_schedule = {
        "arms_sha256": sha(SCHEDULE_DIR / "discovery-arms.jsonl"),
        "manifest_sha256": sha(SCHEDULE_DIR / "manifest.json"),
        "verification_sha256": sha(SCHEDULE_DIR / "verification.json"),
        "graph_manifest_sha256": sha(STUDY / "manifest-v2.json"),
        "arm_count": 8206, "target_probes": 60889088,
        "secondary_controls": {
            "arms_sha256": sha(SCHEDULE_DIR / "p29-secondary-floor-arms.jsonl"),
            "manifest_sha256": sha(SCHEDULE_DIR / "p29-secondary-floor-manifest.json"),
            "verification_sha256": sha(SCHEDULE_DIR / "p29-secondary-floor-verification.json"),
            "arm_count": 4, "target_probes": 32768}}
    if admission.get("schedule") != expected_schedule:
        raise ValueError("stage-2 admission schedule differs from the frozen graph study")
    analysis_ref = candidate.get("finalist_analysis", {})
    selection_ref = candidate.get("selection", {})
    prior_ref = candidate.get("prior_confirmation_admission", {})
    if (admission.get("finalist_analysis_path") != analysis_ref.get("path") or
            admission.get("finalist_analysis_sha256") != analysis_ref.get("sha256") or
            admission.get("selection_path") != selection_ref.get("path") or
            admission.get("selection_sha256") != selection_ref.get("sha256") or
            admission.get("prior_admission_path") != prior_ref.get("path") or
            admission.get("prior_admission_sha256") != prior_ref.get("sha256")):
        raise ValueError("solve admission finalist, selection, or confirmation ancestry differs")
    analysis_path = repo_file(analysis_ref.get("path", ""))
    selection_path = repo_file(selection_ref.get("path", ""))
    prior_path = repo_file(prior_ref.get("path", ""))
    if (sha(analysis_path) != analysis_ref.get("sha256") or
            sha(selection_path) != selection_ref.get("sha256") or
            sha(prior_path) != prior_ref.get("sha256")):
        raise ValueError("solve finalist, selection, or prior admission digest differs")
    prior = json.loads(prior_path.read_text())
    if (prior.get("schema") != "ectd.graph-study-admission.v1" or
            prior.get("status") != "approved" or prior.get("approved_by") != "coordinator" or
            prior.get("execution_stage") != 1 or prior.get("experiment_id") != experiment_id):
        raise ValueError("approved stage-1 confirmation admission required")
    if prior.get("selection_path") != rel(selection_path) or prior.get("selection_sha256") != sha(selection_path):
        raise ValueError("solve selection differs from the approved confirmation admission")
    prior_discovery_path = repo_file(prior.get("prior_admission_path", ""))
    if sha(prior_discovery_path) != prior.get("prior_admission_sha256"):
        raise ValueError("confirmation admission discovery ancestry digest differs")
    discovery = json.loads(prior_discovery_path.read_text())
    if (discovery.get("schema") != "ectd.graph-study-admission.v1" or
            discovery.get("status") != "approved" or discovery.get("execution_stage") != 0 or
            discovery.get("experiment_id") != experiment_id):
        raise ValueError("approved discovery admission ancestry required")

    root_entries = candidate.get("root_files", {})
    if (set(root_entries) != {"base", "target", "verifier"} or
            admission.get("root_files") != {name: value.get("path")
                                             for name, value in root_entries.items()}):
        raise ValueError("solve root files differ from the approved admission")
    roots = {name: repo_file(item.get("path", "")) for name, item in root_entries.items()}
    for name, item in root_entries.items():
        if sha(roots[name]) != item.get("sha256"):
            raise ValueError(f"solve {name} root digest differs")
    old_confirmation = {name: repo_file(path) for name, path in prior.get("root_files", {}).items()}
    old_discovery = {name: repo_file(path) for name, path in discovery.get("root_files", {}).items()}
    if (set(old_confirmation) != {"base", "target", "verifier"} or
            set(old_discovery) != {"base", "target", "verifier"} or
            roots["base"].read_bytes() != old_confirmation["base"].read_bytes() or
            roots["verifier"].read_bytes() != old_confirmation["verifier"].read_bytes() or
            roots["target"].read_bytes() in (old_confirmation["target"].read_bytes(),
                                              old_discovery["target"].read_bytes())):
        raise ValueError("solve roots must reuse base/verifier and use a fresh target")
    if admission.get("binaries") != {
            "collector_path": candidate["binaries"]["collector"]["path"],
            "collector_sha256": candidate["binaries"]["collector"]["sha256"],
            "count_verifier_path": candidate["binaries"]["count_verifier"]["path"],
            "count_verifier_sha256": candidate["binaries"]["count_verifier"]["sha256"],
            "sage_path": candidate["binaries"]["sage"]["path"],
            "sage_sha256": candidate["binaries"]["sage"]["sha256"]}:
        raise ValueError("solve binaries differ from the approved admission")
    for family in ("P29", "P37"):
        planned = candidate.get("commitments", {}).get(family, {})
        identity = admission.get("strata", {}).get(family, {})
        commitment = repo_file(planned.get("path", ""))
        if (sha(commitment) != planned.get("sha256") or
                identity.get("commitment_path") != planned.get("path") or
                identity.get("commitment_sha256") != planned.get("sha256") or
                identity.get("graph_sha256") != planned.get("graph_sha256") or
                any(identity.get(name + "_root_sha256") != planned.get(name + "_root_sha256")
                    for name in ("base", "target", "verifier"))):
            raise ValueError(f"solve {family} commitment differs from the approved admission")
    seed_ref = candidate.get("rho_seed_file", {})
    seed_path = repo_file(seed_ref.get("path", ""))
    if sha(seed_path) != seed_ref.get("sha256"):
        raise ValueError("matched-rho seed file digest differs")
    seeds = [int(line.strip()) for line in seed_path.read_text().splitlines() if line.strip()]
    if len(seeds) != 10 or len(set(seeds)) != 10 or any(seed < 0 for seed in seeds):
        raise ValueError("matched-rho seed file must contain ten unique nonnegative seeds")

    selection = json.loads(selection_path.read_text())
    analysis = json.loads(analysis_path.read_text())
    rows = finalist_rows(analysis, selection, sha(selection_path))
    worker_admission, prepared_arms = load_worker_catalog(
        prepared_catalog, rows, experiment_id, 2)
    if (sha(prepared_catalog) != candidate.get("prepared_catalog", {}).get("sha256")
            and candidate.get("prepared_catalog") is not None):
        raise ValueError("candidate prepared catalog digest differs")
    if candidate.get("prepared_worker_admission", {}).get("sha256") not in (
            None, sha(worker_admission)):
        raise ValueError("candidate worker admission digest differs")

    original_trials = candidate.get("trials", [])
    relation_count = candidate.get("relation_trial_count")
    transfer_count = candidate.get("transfer_trial_count")
    rho_count = candidate.get("rho_trial_count")
    if (not isinstance(relation_count, int) or not isinstance(transfer_count, int) or
            not isinstance(rho_count, int) or relation_count != len(rows) or
            transfer_count != len(rows) // 3 or rho_count != 10 * (len(rows) // 3) or
            len(original_trials) != relation_count + transfer_count + rho_count):
        raise ValueError("solve candidate trial counts differ from the frozen finalist workload")
    relation_source = original_trials[:relation_count]
    transfer_source = original_trials[relation_count:relation_count + transfer_count]
    rho_source = original_trials[relation_count + transfer_count:]
    relation_ids = [trial.get("run_id") for trial in relation_source]
    transfer_ids = [trial.get("run_id") for trial in transfer_source]
    rho_ids = [trial.get("run_id") for trial in rho_source]
    relation_by_arm = {row["arm_key"]: run_id for row, run_id in zip(rows, relation_ids)}
    if ([trial.get("id") for trial in relation_source] != [row["arm_key"] for row in rows] or
            any(not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id)
                for run_id in (*relation_ids, *transfer_ids, *rho_ids))):
        raise ValueError("solve candidate run IDs or finalist order differ")
    if len(set((*relation_ids, *transfer_ids, *rho_ids))) != len(
            relation_ids + transfer_ids + rho_ids):
        raise ValueError("solve candidate run ids must be unique across every phase")
    if ([trial.get("parameters", {}).get("phase") for trial in transfer_source] !=
            ["path_transfer"] * transfer_count or
            [trial.get("id") for trial in transfer_source] != [
                f"{row['stratum']}-v{row['path_index']:04d}-path-transfer"
                for row in rows[::3]]):
        raise ValueError("solve candidate path-transfer rows differ from finalist identities")
    repetitions = sorted({trial.get("parameters", {}).get("repetition") for trial in rho_source})
    if repetitions != list(range(10)):
        raise ValueError("solve candidate matched-rho repetitions differ")
    candidate_seeds = [next(trial["parameters"]["seed"] for trial in rho_source
                            if trial.get("parameters", {}).get("repetition") == repetition)
                       for repetition in repetitions]
    if candidate_seeds != seeds:
        raise ValueError("solve candidate matched-rho seeds differ from the frozen seed file")
    expected_relations = make_trials(
        rows, relation_ids, experiment_id=experiment_id,
        root_files={name: item["path"] for name, item in root_entries.items()},
        commitments={family: item["path"] for family, item in candidate["commitments"].items()},
        admission_path=f"experiments/{experiment_id}/graph-study-admission-solve.json",
        collector_path=candidate["binaries"]["collector"]["path"],
        count_verifier_path=candidate["binaries"]["count_verifier"]["path"],
        sage_path=candidate["binaries"]["sage"]["path"],
        prepared_catalog=prepared_catalog)
    expected_transfer = make_transfer_trials(
        rows, transfer_ids, experiment_id=experiment_id,
        relation_run_ids=relation_by_arm, prepared_arms=prepared_arms,
        sage_path=candidate["binaries"]["sage"]["path"])
    expected_rho = make_rho_trials(
        rows, rho_ids, relation_by_arm, seeds, experiment_id=experiment_id,
        prepared_arms=prepared_arms)
    expected_trials = expected_relations + expected_transfer + expected_rho
    if (len(expected_trials) != len(original_trials) or
            original_trials != expected_trials):
        raise ValueError("solve candidate trial identities or resource guards differ")
    from build_confirmation_plan import SOURCE_PATHS as confirmation_sources
    from execute_graph_prepared import check_frozen_sources, source_paths
    frozen_paths = list(dict.fromkeys([
        *source_paths().values(), *confirmation_sources, *SOURCE_PATHS,
        STUDY / "preparation/verify_prepared_graph.py",
    ]))
    check_frozen_sources(ROOT, frozen_paths, candidate["source_commit"])
    expected_sources = {rel(path): sha(path) for path in frozen_paths}
    if (candidate.get("source_sha256") != expected_sources or
            admission.get("source_sha256") != expected_sources):
        raise ValueError("solve candidate or admission frozen source map differs")

    body = dict(candidate)
    body["trials"] = expected_trials
    for private_field in ("candidate_only", "approval_required", "root_files", "commitments",
                          "selection", "prior_confirmation_admission", "prior_discovery_admission",
                          "rho_seed_file"):
        body.pop(private_field, None)
    body["approved_by"] = decision["id"]
    body["specification_sha256"] = sha(specification_path)
    body["prepared_catalog_sha256"] = sha(prepared_catalog)
    body["prepared_worker_admission_sha256"] = sha(worker_admission)
    body["rho_seed_file_sha256"] = seed_ref["sha256"]
    body["stage_admission"] = {"sha256": sha(admission_path),
                               "decision_sha256": sha(decision_path)}
    body["scope_note"] = (
        "Coordinator-approved finalist relation/solver trials, source-to-finalist transfer "
        "trials on public G,Q points, and ten matched plain-rho trials per finalist on the "
        "same prepared target input. Worker argv contains only custodian-prepared points, "
        "public bindings, and rootless admission documents.")
    output_path = output_path.resolve()
    if not output_path.is_relative_to(ROOT / "experiments" / experiment_id):
        raise ValueError("approved solve plan output must stay inside the experiment directory")
    encoded = (json.dumps(body, indent=2, sort_keys=True) + "\n").encode()
    with output_path.open("xb") as stream:
        stream.write(encoded)
    return {"schema": "ectd.graph-solve-trial-plan-build.v1",
            "status": "built", "experiment_id": experiment_id,
            "approved_by": decision["id"], "trial_count": len(expected_trials),
            "trial_plan_sha256": hashlib.sha256(encoded).hexdigest(),
            "output": str(output_path)}
