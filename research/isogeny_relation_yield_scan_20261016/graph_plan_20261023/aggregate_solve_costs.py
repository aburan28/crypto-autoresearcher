"""Validate and aggregate complete finalist solve and matched-rho receipts.

This is post-run accounting only. It accepts a candidate solve plan and a
run-root catalog keyed by that plan's run IDs; it never selects finalists,
changes admission, or treats censored cells as zero-cost solves.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REQUIRED_SOLVE_TIMES = (
    "input_and_relation_replay", "matrix_row_build", "linear_algebra",
    "individual_log_recovery", "scalar_verification",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def bound_path(root: Path, manifest: dict, key: str) -> Path:
    raw = manifest.get("paths", {}).get(key)
    if not isinstance(raw, str):
        raise ValueError(f"trial manifest lacks the {key} path")
    candidate = Path(raw)
    choices = ([candidate] if candidate.is_absolute() else
               [root / candidate, ROOT / candidate])
    for path in choices:
        resolved = path.resolve()
        if resolved.is_file():
            return resolved
    raise ValueError(f"bound trial artifact is missing: {key}")


def positive_number(value, label: str, *, allow_zero: bool = True) -> float:
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or
            not math.isfinite(value) or value < 0 or (not allow_zero and value == 0)):
        raise ValueError(f"invalid nonnegative duration for {label}")
    return float(value)


def validate_run_receipt(trial: dict, root: Path, plan_sha256: str,
                         artifacts: tuple[str, ...]) -> dict:
    receipt = read(root / "execution-receipt.json")
    if (receipt.get("plan_sha256") != plan_sha256 or
            receipt.get("trial_id") != trial.get("id") or
            receipt.get("run_id") != trial.get("run_id") or
            receipt.get("status") != "output_validated" or
            receipt.get("check_returncode") != 0):
        raise ValueError(f"executor receipt does not validate the planned run: {trial['run_id']}")
    digests = receipt.get("artifact_sha256", {})
    if not isinstance(digests, dict):
        raise ValueError(f"executor receipt lacks an artifact digest map: {trial['run_id']}")
    for name in artifacts:
        digest = digests.get(name)
        artifact = root / name
        if (not isinstance(digest, str) or len(digest) != 64 or
                not artifact.is_file() or sha(artifact) != digest):
            raise ValueError(f"executor artifact digest or content differs: {trial['run_id']}:{name}")
    return receipt


def read_catalog(path: Path, plan: dict, plan_sha256: str) -> dict[str, Path]:
    catalog = read(path)
    if (catalog.get("schema") != "ectd.graph-solve-run-catalog/v1" or
            catalog.get("candidate_plan_sha256") != plan_sha256):
        raise ValueError("unexpected solve run catalog schema")
    trials = plan.get("trials")
    if not isinstance(trials, list):
        raise ValueError("candidate plan lacks trials")
    expected = {trial.get("run_id") for trial in trials}
    roots = catalog.get("runs")
    if (not all(isinstance(key, str) for key in expected) or
            not isinstance(roots, dict) or set(roots) != expected):
        raise ValueError("run catalog must bind every planned run exactly once")
    output = {}
    for run_id, value in roots.items():
        if not isinstance(value, str) or Path(value).is_absolute() or ".." in Path(value).parts:
            raise ValueError("run roots must be safe paths relative to the catalog")
        root = (path.parent / value).resolve()
        if not root.is_dir():
            raise ValueError(f"missing run directory for {run_id}")
        output[run_id] = root
    return output


def validate_relation(trial: dict, root: Path, plan_sha256: str) -> dict:
    validate_run_receipt(trial, root, plan_sha256,
                         ("raw-result.json", "solve/solve.json", "solve/checker.stdout"))
    raw_path = root / "raw-result.json"
    manifest_path = root / "manifest.yaml"
    receipt_path = root / "attempt/receipt.json"
    raw, manifest = read(raw_path), read(manifest_path)
    prepared_path = bound_path(root, manifest, "prepared-manifest")
    input_path = bound_path(root, manifest, "input")
    solve_path = root / "solve/solve.json"
    check_path = root / "solve/checker.stdout"
    receipt, prepared, solved = map(read, (receipt_path, prepared_path, solve_path))
    if (manifest.get("raw_result_sha256") != sha(raw_path) or
            raw.get("schema") != "ectd.graph-trial-result.v1" or
            raw.get("status") not in ("completed_unreviewed", "completed_control") or
            raw.get("prepared", {}).get("stage") != "solve" or
            raw.get("prepared", {}).get("arm") != trial["parameters"].get("arm") or
            raw.get("prepared", {}).get("stratum") != trial["parameters"].get("stratum") or
            raw.get("prepared", {}).get("index") != trial["parameters"].get("index") or
            sha(input_path) != raw.get("digests", {}).get("input_sha256") or
            raw.get("complete_solve", {}).get("status") not in
                ("valid_censored", "valid_verified_scalar") or
            solved.get("schema") != "ectd.graph-complete-solve-candidate.v1" or
            solved.get("status") not in ("verified_scalar", "censored_insufficient_rank") or
            solved.get("input_sha256") != raw.get("digests", {}).get("input_sha256") or
            raw.get("digests", {}).get("prepared-manifest_sha256") != sha(prepared_path) or
            solved.get("scalar") is None or
            not check_path.is_file()):
        raise ValueError(f"relation/solve receipt is incomplete or invalid: {trial['run_id']}")
    checker = json.loads(check_path.read_text())
    if checker.get("status") not in ("valid_verified_scalar", "valid_censored"):
        raise ValueError(f"independent solve checker did not pass: {trial['run_id']}")
    if ((solved["status"] == "verified_scalar") !=
            (checker.get("status") == "valid_verified_scalar")):
        raise ValueError(f"solve terminal status differs from independent checker: {trial['run_id']}")
    measurement = prepared.get("preparation_measurement", {})
    if (measurement.get("schema") != "ectd.graph-solve-preparation-measurement/v1" or
            measurement.get("target_count") != 32768 or
            measurement.get("base_point_count") != len(
                input_path.read_text().splitlines()[1:]) - 32768):
        raise ValueError(f"solve preparation timing or identity is missing: {trial['run_id']}")
    phases = {item.get("phase"): item for item in receipt.get("phases", [])}
    collector = phases.get("collector")
    if (receipt.get("status") != "completed_unreviewed" or not collector or
            collector.get("status") != "completed" or collector.get("return_code") != 0):
        raise ValueError(f"relation collector receipt is incomplete: {trial['run_id']}")
    timings = solved.get("timings_seconds")
    required_times = REQUIRED_SOLVE_TIMES if solved["status"] == "verified_scalar" else (
        "input_and_relation_replay", "matrix_row_build", "linear_algebra", "scalar_verification")
    if not isinstance(timings, dict) or any(key not in timings for key in required_times):
        raise ValueError(f"solve phase timing is incomplete: {trial['run_id']}")
    durations = {key: positive_number(value, key) for key, value in timings.items()}
    prep_wall = positive_number(measurement.get("wall_seconds"), "preparation wall")
    collector_wall = positive_number(collector.get("elapsed_seconds"), "collector wall")
    complete_solve = raw["complete_solve"]
    solver_resources = complete_solve.get("solver_resources")
    if not isinstance(solver_resources, dict):
        raise ValueError(f"solver process resource receipt is missing: {trial['run_id']}")
    if solver_resources is not None:
        for field in ("wall_seconds", "peak_sampled_rss_bytes", "child_process_cpu_seconds"):
            positive_number(solver_resources.get(field), "solver " + field)
    return {
        "trial": trial, "raw": raw, "solved": solved, "prepared": prepared,
        "raw_sha256": sha(raw_path), "manifest_sha256": sha(manifest_path),
        "receipt_sha256": sha(receipt_path), "solve_sha256": sha(solve_path),
        "prepared_manifest_sha256": sha(prepared_path),
        "preparation_wall_seconds": prep_wall,
        "preparation_process_cpu_seconds": positive_number(
            measurement.get("process_cpu_seconds"), "preparation CPU"),
        "preparation_peak_rss_platform_units": positive_number(
            measurement.get("peak_rss_platform_units"), "preparation peak RSS"),
        "preparation_breakdown_seconds": {
            key: positive_number(measurement.get(key), key) for key in (
                "target_stream_and_source_pair_seconds", "base_generation_seconds",
                "target_point_construction_seconds", "serialization_seconds")},
        "collector_wall_seconds": collector_wall,
        "collector_peak_sampled_rss_bytes": positive_number(
            collector.get("peak_sampled_rss_bytes"), "collector peak RSS"),
        "solver_resources": solver_resources,
        "checker_resources": complete_solve.get("checker_resources"),
        "solve_timings_seconds": durations,
        "cold_start_wall_seconds": (prep_wall + collector_wall + sum(durations.values())
                                     if solved["status"] == "verified_scalar" else None),
        "observed_before_censor_wall_seconds": prep_wall + collector_wall + sum(durations.values()),
        "target_count": 32768,
    }


def validate_transfer(trial: dict, root: Path, plan_sha256: str) -> dict:
    validate_run_receipt(trial, root, plan_sha256, ("transfer.json", "transfer-check.json"))
    result_path, check_path = root / "transfer.json", root / "transfer-check.json"
    result, checked = read(result_path), read(check_path)
    params = trial["parameters"]
    if (result.get("schema") != "ectd.graph-path-transfer-result/v1" or
            result.get("status") != "output_validated" or
            checked.get("schema") != "ectd.graph-path-transfer-check/v1" or
            checked.get("status") != "pass" or
            (result.get("stratum"), result.get("index"), result.get("edge_count")) !=
            (params.get("stratum"), params.get("index"), params.get("edge_count"))):
        raise ValueError(f"path transfer receipt is incomplete or invalid: {trial['run_id']}")
    setup = positive_number(result.get("path_setup_seconds"), "path setup")
    point_map = positive_number(result.get("path_point_map_seconds"), "path point map")
    return {"trial": trial, "result": result,
            "result_sha256": sha(result_path), "check_sha256": sha(check_path),
            "path_setup_seconds": setup, "path_point_map_seconds": point_map,
            "cold_transfer_seconds": setup + point_map}


def validate_rho(trial: dict, root: Path, expected: dict, plan_sha256: str) -> dict:
    validate_run_receipt(trial, root, plan_sha256, ("rho-result.json",))
    result_path, check_path = root / "rho-result.json", root / "check.stdout.log"
    result, checked = read(result_path), read(check_path)
    params = trial["parameters"]
    if (result.get("schema") != "ectd.graph-matched-rho-result/v1" or
            result.get("seed") != params.get("seed") or
            result.get("max_steps") != 60000000 or
            any(result.get(key) != expected.get(key) for key in
                ("p", "a", "b", "r", "generator", "Q")) or
            checked.get("status") not in ("valid_verified_scalar", "valid_censored")):
        raise ValueError(f"matched-rho receipt differs from the relation cell: {trial['run_id']}")
    if result.get("status") == "verified_scalar":
        if checked.get("status") != "valid_verified_scalar" or result.get("verified") is not True:
            raise ValueError(f"rho scalar lacks independent validation: {trial['run_id']}")
    elif result.get("status") != "censored_step_cap" or checked.get("status") != "valid_censored":
        raise ValueError(f"rho terminal state is invalid: {trial['run_id']}")
    return {"trial": trial, "status": result["status"], "seed": result["seed"],
            "steps": result.get("steps"), "group_ops": result.get("group_ops"),
            "wall_seconds": positive_number(result.get("wall_seconds"), "rho wall"),
            "process_cpu_seconds": positive_number(result.get("process_cpu_seconds"), "rho cpu"),
            "peak_rss_platform_units": positive_number(
                result.get("peak_rss_platform_units"), "rho peak RSS"),
            "result_sha256": sha(result_path), "check_sha256": sha(check_path)}


def aggregate(plan_path: Path, catalog_path: Path) -> dict:
    plan = read(plan_path)
    if (plan.get("schema") != "crypto.autoresearch.trial_plan.v1" or
            plan.get("stage") != "solve" or plan.get("candidate_only") is not True):
        raise ValueError("candidate solve-stage plan required")
    plan_digest = sha(plan_path)
    roots = read_catalog(catalog_path, plan, plan_digest)
    trials = plan["trials"]
    by_id = {trial["id"]: trial for trial in trials}
    relation_trials = [trial for trial in trials if trial.get("parameters", {}).get("arm")]
    transfer_trials = [trial for trial in trials if trial.get("parameters", {}).get("phase") == "path_transfer"]
    rho_trials = [trial for trial in trials if trial.get("parameters", {}).get("baseline") == "plain_rho"]
    if (len(relation_trials) % 3 or len(transfer_trials) != len(relation_trials) // 3 or
            len(rho_trials) != 10 * len(transfer_trials)):
        raise ValueError("candidate plan does not contain three treatments, one transfer, and ten rho runs per finalist")
    relation = {trial["id"]: validate_relation(trial, roots[trial["run_id"]], plan_digest)
                for trial in relation_trials}
    transfer = {trial["parameters"]["stratum"] + ":" + str(trial["parameters"]["index"]):
                validate_transfer(trial, roots[trial["run_id"]], plan_digest) for trial in transfer_trials}
    cells = {}
    for trial_id, row in relation.items():
        trial = row["trial"]
        params = trial["parameters"]
        key = (params["stratum"], params["index"])
        cell = cells.setdefault(key, {"stratum": key[0], "index": key[1], "treatments": {}})
        if params["arm"] in cell["treatments"]:
            raise ValueError("duplicate finalist treatment")
        cell["treatments"][params["arm"]] = row
    output_cells = []
    for key, cell in sorted(cells.items()):
        if set(cell["treatments"]) != {"low_x", "mid_x", "random_x"}:
            raise ValueError(f"finalist treatment set is incomplete: {key}")
        low = cell["treatments"]["low_x"]
        transfer_row = transfer.get(f"{key[0]}:{key[1]}")
        if transfer_row is None:
            raise ValueError(f"finalist transfer is missing: {key}")
        if transfer_row["result"].get("source_points_sha256") != low["prepared"].get("source_points_sha256"):
            raise ValueError(f"transfer and finalist source point pair differ: {key}")
        rho_rows = []
        for trial in rho_trials:
            params = trial["parameters"]
            if (params.get("stratum"), params.get("index")) == key:
                rho_rows.append(validate_rho(trial, roots[trial["run_id"]], low["solved"], plan_digest))
        if len(rho_rows) != 10 or {item["trial"]["parameters"]["repetition"] for item in rho_rows} != set(range(10)):
            raise ValueError(f"finalist must have ten uniquely identified rho repetitions: {key}")
        for row in cell["treatments"].values():
            if (any(row["solved"].get(field) != low["solved"].get(field)
                    for field in ("p", "a", "b", "r", "generator", "Q")) or
                    row["prepared"].get("source_points_sha256") != low["prepared"].get("source_points_sha256") or
                    row["prepared"].get("target_vector_sha256") != low["prepared"].get("target_vector_sha256")):
                raise ValueError(f"factor-base treatments do not share the exact G,Q and target stream: {key}")
        if (transfer_row["result"].get("endpoint_generator") != low["solved"].get("generator") or
                transfer_row["result"].get("endpoint_Q") != low["solved"].get("Q")):
            raise ValueError(f"transported pair differs from prepared finalist pair: {key}")
        treatment_rows = []
        for arm, row in sorted(cell["treatments"].items()):
            transfer_seconds = transfer_row["cold_transfer_seconds"]
            treatment_rows.append({"stratum": key[0], "index": key[1], "arm": arm,
                "run_id": row["trial"]["run_id"],
                "status": row["solved"]["status"], "rank": row["solved"]["rank"],
                "unknown_columns": row["solved"]["unknown_columns"],
                "relation_yield": {field: row["raw"]["rank_check"].get(field) for field in (
                    "targets", "useful_targets", "useful_triples", "raw_unordered_triples",
                    "unique_canonical_coefficient_rows", "rank_increments", "rank_prefix")},
                "preparation_wall_seconds": row["preparation_wall_seconds"],
                "preparation_process_cpu_seconds": row["preparation_process_cpu_seconds"],
                "preparation_peak_rss_platform_units": row["preparation_peak_rss_platform_units"],
                "preparation_breakdown_seconds": row["preparation_breakdown_seconds"],
                "collector_wall_seconds": row["collector_wall_seconds"],
                "collector_peak_sampled_rss_bytes": row["collector_peak_sampled_rss_bytes"],
                "solver_resources": row["solver_resources"],
                "checker_resources": row["checker_resources"],
                "solve_timings_seconds": row["solve_timings_seconds"],
                "path_transfer_seconds": transfer_seconds,
                "cold_start_wall_seconds": (transfer_seconds + row["cold_start_wall_seconds"]
                                             if row["cold_start_wall_seconds"] is not None else None),
                "observed_before_censor_wall_seconds": transfer_seconds + row["observed_before_censor_wall_seconds"],
                "amortization_target_count": row["target_count"],
                "amortized_seconds_per_target": (transfer_seconds + row["cold_start_wall_seconds"]) / row["target_count"],
                "rho_repetitions": [{k: v for k, v in rho.items() if k != "trial"} for rho in rho_rows],
                "rho_censored_count": sum(rho["status"] != "verified_scalar" for rho in rho_rows),
                "rho_wall_seconds_min_median_max": {
                    "min": min(rho["wall_seconds"] for rho in rho_rows),
                    "median": statistics.median(rho["wall_seconds"] for rho in rho_rows),
                    "max": max(rho["wall_seconds"] for rho in rho_rows)},
                "interpretation_limit": "Per-run measurements on this exact finalist and fixed workload; no cross-curve or cryptographic-scale claim."})
        output_cells.append({"stratum": key[0], "index": key[1],
                             "transfer_run_id": transfer_row["trial"]["run_id"],
                             "treatments": treatment_rows})
    all_values = [item for cell in output_cells for item in cell["treatments"]]
    complete_values = [item for item in all_values
                       if item["status"] == "verified_scalar" and item["cold_start_wall_seconds"] is not None]
    def summary(rows: list[dict]) -> dict:
        values = [row["cold_start_wall_seconds"] for row in rows
                  if row["status"] == "verified_scalar" and row["cold_start_wall_seconds"] is not None]
        return {"complete_count": len(values), "censored_count": len(rows) - len(values),
                "min_median_max_seconds": ({"min": min(values), "median": statistics.median(values),
                                             "max": max(values)} if values else None)}
    extremes = None
    if complete_values:
        minimum = min(complete_values, key=lambda item: (item["cold_start_wall_seconds"], item["stratum"], item["index"], item["arm"]))
        maximum = max(complete_values, key=lambda item: (item["cold_start_wall_seconds"], item["stratum"], item["index"], item["arm"]))
        extremes = {"minimum": {"stratum": minimum["stratum"], "index": minimum["index"],
                                 "arm": minimum["arm"], "seconds": minimum["cold_start_wall_seconds"]},
                    "maximum": {"stratum": maximum["stratum"], "index": maximum["index"],
                                 "arm": maximum["arm"], "seconds": maximum["cold_start_wall_seconds"]}}
    return {"schema": "ectd.graph-finalist-cost-table/v1", "status": "complete" if len(complete_values) == len(all_values) else "contains_censored_cells",
            "candidate_plan_sha256": plan_digest, "run_catalog_sha256": sha(catalog_path),
            "finalist_count": len(output_cells), "relation_cell_count": len(all_values),
            "extremes_selection": "minimum_and_maximum_over_verified_complete_cold_start_cells_only; all cells remain listed",
            "cold_start_wall_seconds_min_median_max": ({"min": min(x["cold_start_wall_seconds"] for x in complete_values),
                "median": statistics.median(x["cold_start_wall_seconds"] for x in complete_values),
                "max": max(x["cold_start_wall_seconds"] for x in complete_values)} if complete_values else None),
            "extremes": extremes,
            "per_treatment_summary": {arm: summary([item for item in all_values if item["arm"] == arm])
                                      for arm in ("low_x", "mid_x", "random_x")},
            "cells": output_cells,
            "limits": ["Preparation is timed in the prepared manifest; relation collection is timed by its supervised phase receipt; solve phases are timed inside the solver.",
                       "Independent checker replay time is retained in raw receipts and excluded from attack cost; in-solver equation verification is included.",
                       "No complete comparison is available until every planned run has an immutable receipt and passing independent checker."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-catalog", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = aggregate(args.plan, args.run_catalog)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in
                      ("schema", "status", "finalist_count", "relation_cell_count")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
