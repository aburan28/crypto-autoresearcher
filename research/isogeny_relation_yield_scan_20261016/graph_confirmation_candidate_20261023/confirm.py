"""Candidate held-out confirmation and finalist analysis for the fixed graph.

Run only after a Coordinator-approved confirmation plan and all validated
fresh-target receipts exist. Exact interval cells are write-once and reusable
after interruption. This module issues no approval or scientific verdict.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
LEGACY_INTERVAL = ROOT / "research/conductor_relation_yield_20261014/exact_interval.py"
sys.path.insert(0, str(LEGACY_INTERVAL.parent))
from exact_interval import interval, upper_tail_at_least

ORDINARY_ARMS = ("low_x", "mid_x", "random_x")
CONFIRM_TARGETS = 32768


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def hash_coefficient_stream(input_path: Path, base_points: int, targets: int) -> str:
    digest = hashlib.sha256()
    target_rows = 0
    with input_path.open() as stream:
        next(stream)
        for _ in range(base_points):
            next(stream)
        for index, line in enumerate(stream):
            fields = line.split()
            require(len(fields) == 6 and fields[:2] == ["target", str(index)],
                    f"prepared target order differs: {input_path}")
            digest.update((fields[2] + "," + fields[3] + "\n").encode())
            target_rows += 1
            if target_rows > targets:
                raise ValueError("too many prepared targets")
    require(target_rows == targets, f"prepared target count differs: {input_path}")
    return digest.hexdigest()


def read_validated_arm(repo: Path, plan: dict, plan_hash: str,
                       row: dict, trial: dict) -> dict:
    key = row["arm_key"]
    run_dir = repo / Path(plan["specification"]).parent / "runs" / trial["run_id"]
    receipt = read(run_dir / "execution-receipt.json")
    require(receipt.get("status") == "output_validated" and
            receipt.get("returncode") == receipt.get("check_returncode") == 0 and
            receipt.get("plan_sha256") == plan_hash and
            receipt.get("trial_id") == key and receipt.get("run_id") == trial["run_id"],
            f"confirmation supervisor receipt differs: {key}")
    artifacts = receipt.get("artifact_sha256", {})
    for name in ("raw-result.json", "manifest.yaml", "check.stdout.log", "check.stderr.log"):
        require(artifacts.get(name) == sha(run_dir / name),
                f"confirmation artifact digest differs: {key} {name}")
    raw = read(run_dir / "raw-result.json")
    manifest = read(run_dir / "manifest.yaml")
    attempt_path = run_dir / "attempt/receipt.json"
    attempt = read(attempt_path)
    require(raw.get("schema") == "ectd.graph-trial-result.v1" and
            manifest.get("schema") == "ectd.graph-trial-manifest.v1" and
            attempt.get("schema") == "ectd.graph-arm-execution-attempt.v1" and
            raw.get("status") == manifest.get("status") == attempt.get("status") ==
            "completed_unreviewed" and raw.get("mode") == attempt.get("mode") ==
            "scientific_trial" and manifest.get("subprocess_return_code") == 0 and
            raw.get("attempt_receipt_sha256") == manifest.get("attempt_receipt_sha256") ==
            sha(attempt_path) and manifest.get("raw_result_sha256") == sha(run_dir / "raw-result.json") and
            attempt.get("admission_sha256") == raw.get("digests", {}).get("admission_sha256") and
            isinstance(attempt.get("admission_sha256"), str) and
            len(attempt["admission_sha256"]) == 64,
            f"confirmation graph attempt differs: {key}")
    expected = {"stratum": row["stratum"], "index": row["path_index"],
                "arm": row["base_rule"], "stage": "confirmation",
                "target_count": CONFIRM_TARGETS}
    require(raw.get("prepared") == expected and
            all(attempt.get("bindings", {}).get(k) == v for k, v in expected.items()),
            f"confirmation arm identity differs: {key}")
    prepared_path = Path(manifest["paths"]["prepared-manifest"])
    input_path = Path(manifest["paths"]["input"])
    prepared = read(prepared_path)
    require(raw["digests"].get("prepared-manifest_sha256") == sha(prepared_path) and
            raw["digests"].get("input_sha256") == sha(input_path) and
            prepared.get("input_sha256") == sha(input_path) and
            prepared.get("seed_mode") == "independent_verifier_root" and
            prepared.get("schedule_conformant") is True and
            all(prepared.get(k) == v for k, v in expected.items()) and
            prepared.get("j") == row["model"]["j"] and
            prepared.get("generator") == row["generator"],
            f"confirmation prepared input differs: {key}")
    with input_path.open() as stream:
        header = next(stream).split()
    require(header == ["curve", str(row["p"]), str(row["model"]["a"]),
                       str(row["model"]["b"]), str(row["r"]),
                       str(2 * row["base_x_orbits"]), str(CONFIRM_TARGETS)],
            f"confirmation curve differs: {key}")
    coefficient_hash = hash_coefficient_stream(input_path, 2 * row["base_x_orbits"], CONFIRM_TARGETS)
    rank = raw.get("rank_check", {})
    checked = read(run_dir / "check.stdout.log")
    require(rank.get("status") == "valid" and rank.get("targets") == CONFIRM_TARGETS and
            rank.get("independent_ordered_count_match") is True and
            isinstance(rank.get("useful_targets"), int) and
            0 <= rank["useful_targets"] <= CONFIRM_TARGETS and
            all(str(n) in rank.get("rank_prefix", {}) for n in (512, 2048, 8192, 32768)) and
            checked.get("status") == "valid" and checked.get("targets") == CONFIRM_TARGETS and
            checked.get("useful_targets") == rank["useful_targets"] and
            checked.get("rank_increments") == rank["rank_increments"],
            f"confirmation count or rank replay differs: {key}")
    return {"arm_key": key, "stratum": row["stratum"], "index": row["path_index"],
            "j": row["model"]["j"], "arm": row["base_rule"], "r": row["r"],
            "targets": CONFIRM_TARGETS, "useful_targets": rank["useful_targets"],
            "rank_increments": rank["rank_increments"], "rank_prefix": rank["rank_prefix"],
            "coefficient_sha256": coefficient_hash,
            "base_root_sha256": prepared["base_root_sha256"],
            "target_root_sha256": prepared["target_root_sha256"],
            "verifier_root_sha256": prepared["verifier_root_sha256"],
            "commitment_sha256": prepared["commitment_sha256"],
            "run_id": trial["run_id"],
            "execution_receipt_sha256": sha(run_dir / "execution-receipt.json"),
            "raw_result_sha256": sha(run_dir / "raw-result.json")}


def verify_interval_endpoints(record: dict) -> None:
    """Four exact boundary predicates validate a resumed cached interval."""
    value = record["interval"]
    N, n, x = record["population"], record["draws"], record["observed"]
    D = record["tail_denominator"]
    lo, hi = value["lower_successes"], value["upper_successes"]
    require(value["population"] == N and value["draws"] == n and
            value["observed"] == x and value["tail_numerator"] == 1 and
            value["tail_denominator"] == D and 0 <= lo <= hi <= N,
            "cached exact interval parameters differ")
    if x == 0:
        require(lo == 0, "zero-hit lower endpoint differs")
    else:
        require(upper_tail_at_least(N, lo, n, x, 1, D) and
                (lo == 0 or not upper_tail_at_least(N, lo - 1, n, x, 1, D)),
                "cached exact lower endpoint differs")
    if x == n:
        require(hi == N, "all-hit upper endpoint differs")
    else:
        upper_predicate = lambda K: upper_tail_at_least(N, N - K, n, n - x, 1, D)
        require(upper_predicate(hi) and (hi == N or not upper_predicate(hi + 1)),
                "cached exact upper endpoint differs")


def interval_cell(cache_dir: Path, row: dict, family_count: int) -> tuple[dict, str]:
    D = 200 * family_count
    key = row["arm_key"]
    path = cache_dir / f"{key}.json"
    expected = {"schema": "ectd.graph-confirmation-interval-cell.v1", "arm_key": key,
                "population": row["r"] - 1, "draws": row["targets"],
                "observed": row["useful_targets"], "tail_denominator": D,
                "execution_receipt_sha256": row["execution_receipt_sha256"],
                "analyzer_source_sha256": sha(Path(__file__)),
                "exact_interval_source_sha256": sha(LEGACY_INTERVAL)}
    if path.exists():
        stored = read(path)
        require(all(stored.get(k) == v for k, v in expected.items()),
                f"cached interval identity differs: {key}")
    else:
        result = interval(expected["population"], expected["draws"], expected["observed"], 1, D)
        stored = {**expected, "interval": result}
        with path.open("x") as stream:
            json.dump(stored, stream, indent=2, sort_keys=True)
            stream.write("\n")
    verify_interval_endpoints(stored)
    return stored["interval"], sha(path)


def fraction_json(value: Fraction | None) -> dict | None:
    return None if value is None else {"numerator": value.numerator, "denominator": value.denominator}


def ratio_record(left: dict, right: dict, left_ci: dict, right_ci: dict) -> dict:
    """Conservative ratio from simultaneous marginal count intervals."""
    if right["useful_targets"] == 0:
        point = None  # positive infinity
    else:
        point = Fraction(left["useful_targets"], right["useful_targets"])
    left_low, left_high = left_ci["lower_successes"], left_ci["upper_successes"]
    right_low, right_high = right_ci["lower_successes"], right_ci["upper_successes"]
    lower = None if right_high == 0 else Fraction(left_low, right_high)
    upper = None if right_low == 0 else Fraction(left_high, right_low)
    undefined = left["useful_targets"] == right["useful_targets"] == 0
    lead = (not undefined and point is not None and lower is not None and
            ((lower > 1 and point >= Fraction(6, 5)) or
             (upper is not None and upper < 1 and point <= Fraction(4, 5))))
    return {"point_ratio": fraction_json(point) if not undefined else None,
            "point_ratio_unbounded": point is None and not undefined,
            "point_ratio_undefined": undefined,
            "interval_lower": fraction_json(lower), "interval_upper": fraction_json(upper),
            "interval_upper_unbounded": upper is None and right_high > 0,
            "interval_undefined": right_high == 0,
            "prespecified_20_percent_lead": lead}


def finalist_selection(selection: dict, rows: list[dict], intervals: dict[str, dict]) -> tuple[dict, dict]:
    by_key = {row["arm_key"]: row for row in rows}
    ratios, finalists = {}, {}
    for stratum, selected in selection["strata"].items():
        indices = [entry["index"] for entry in selected["selected_vertices"]]
        require(indices and len(indices) == len(set(indices)), f"selected vertex identity differs: {stratum}")
        low = [by_key[f"{stratum}-v{index:04d}-low_x"] for index in indices]
        high_order = sorted(low, key=lambda item: (-item["useful_targets"], item["j"]))
        low_order = sorted(low, key=lambda item: (item["useful_targets"], item["j"]))
        ratio_items = []
        for index in indices:
            first = by_key[f"{stratum}-v{index:04d}-low_x"]
            other = by_key[f"{stratum}-v{index:04d}-random_x"]
            ratio = ratio_record(first, other, intervals[first["arm_key"]], intervals[other["arm_key"]])
            ratios[f"{stratum}-v{index:04d}"] = ratio
            point = ratio["point_ratio"]
            if not ratio["point_ratio_undefined"]:
                value = None if point is None else Fraction(point["numerator"], point["denominator"])
                ratio_items.append((index, first["j"], value))
        best_ratio = min(ratio_items, key=lambda item:
                         (0, 0, item[1]) if item[2] is None else (1, -item[2], item[1])) if ratio_items else None
        worst_ratio = min(ratio_items, key=lambda item:
                          (1, 0, item[1]) if item[2] is None else (0, item[2], item[1])) if ratio_items else None
        median = low_order[(len(low_order) - 1) // 2]
        nominated = [(0, "source"), (high_order[0]["index"], "best_low_x"),
                     (low_order[0]["index"], "worst_low_x"),
                     (median["index"], "lower_median_low_x")]
        if best_ratio is not None:
            nominated.extend([(best_ratio[0], "best_low_x_over_random_x"),
                              (worst_ratio[0], "worst_low_x_over_random_x")])
        entries: dict[int, dict] = {}
        for index, reason in nominated:
            item = by_key[f"{stratum}-v{index:04d}-low_x"]
            entries.setdefault(item["j"], {"index": index, "j": item["j"], "reasons": []})["reasons"].append(reason)
        finalists[stratum] = list(entries.values())
        require(len(finalists[stratum]) <= 6, "finalist cap exceeded")
    return ratios, finalists


def check_stage_roots(rows: list[dict], discovery: list[dict], selection: dict) -> None:
    """Roots are shared across strata; graph-specific commitments are not."""
    require(rows and discovery, "empty discovery or confirmation stage")
    for field in ("base_root_sha256", "target_root_sha256", "verifier_root_sha256"):
        require(len({row[field] for row in rows}) == 1,
                f"confirmation {field} differs between arms")
    for field in ("base_root_sha256", "verifier_root_sha256"):
        require(len({row[field] for row in discovery}) == 1 and
                rows[0][field] == discovery[0][field],
                f"confirmation {field} differs from discovery")
    require(len({row["target_root_sha256"] for row in discovery}) == 1 and
            rows[0]["target_root_sha256"] != discovery[0]["target_root_sha256"],
            "confirmation reuses or disagrees with discovery target root")
    confirmation_commitments = {}
    for stratum in ("P29", "P37"):
        current = {row["commitment_sha256"] for row in rows
                   if row["stratum"] == stratum}
        previous = {row["commitment_sha256"] for row in discovery
                    if row["stratum"] == stratum}
        require(len(current) == len(previous) == 1 and
                next(iter(previous)) == selection["strata"][stratum]["commitment_sha256"] and
                current != previous,
                f"confirmation graph commitment or fresh stage differs: {stratum}")
        confirmation_commitments[stratum] = next(iter(current))
    require(confirmation_commitments["P29"] != confirmation_commitments["P37"],
            "distinct confirmation graph strata reuse one commitment digest")


def analyze(repo: Path, selection_path: Path, schedule_path: Path,
            plan_path: Path, cache_dir: Path) -> dict:
    repo = repo.resolve()
    selection = read(selection_path)
    require(selection.get("schema") == "ectd.graph-discovery-selection-candidate/v1" and
            selection.get("status") == "selected_from_validated_discovery" and
            selection.get("discovery_arms_checked") == 8206,
            "complete validated discovery selection required")
    schedule_manifest = read(schedule_path.parent / "manifest.json")
    require(selection.get("schedule_sha256") == sha(schedule_path) ==
            schedule_manifest.get("schedule_sha256"), "schedule binding differs")
    schedule = {row["arm_key"]: row for row in
                (json.loads(line) for line in schedule_path.read_text().splitlines())}
    keys = [key for stratum in ("P29", "P37")
            for key in selection["strata"][stratum]["confirmation_arm_keys"]]
    require(keys and len(keys) == len(set(keys)) and len(keys) <= 294 and
            all(key in schedule and schedule[key]["base_rule"] in ORDINARY_ARMS for key in keys),
            "selected confirmation arms differ")
    plan = read(plan_path)
    trials = {trial["id"]: trial for trial in plan.get("trials", [])}
    require(plan.get("schema") == "crypto.autoresearch.trial_plan.v1" and
            plan.get("frozen") is True and plan.get("approved_by") and
            len(trials) == len(plan["trials"]) == len(keys) and set(trials) == set(keys) and
            len({trial["run_id"] for trial in plan["trials"]}) == len(keys),
            "approved confirmation plan extent differs")
    for path in (Path(__file__), LEGACY_INTERVAL, selection_path, schedule_path):
        try:
            relative = path.resolve().relative_to(repo).as_posix()
        except ValueError as error:
            raise ValueError(f"confirmation source outside repository: {path}") from error
        require(plan.get("source_sha256", {}).get(relative) == sha(path),
                f"confirmation plan did not freeze {relative}")
    plan_hash = sha(plan_path)
    rows = [read_validated_arm(repo, plan, plan_hash, schedule[key], trials[key]) for key in keys]
    discovery = selection["discovery_summary"]
    require(len(discovery) == 8206, "discovery summary extent differs")
    check_stage_roots(rows, discovery, selection)
    for stratum in ("P29", "P37"):
        hashes = {row["coefficient_sha256"] for row in rows if row["stratum"] == stratum}
        require(len(hashes) == 1 and next(iter(hashes)) != selection["strata"][stratum]["coefficient_sha256"],
                f"confirmation target coefficients are not fresh and paired: {stratum}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    intervals, cache_hashes = {}, {}
    for row in rows:
        intervals[row["arm_key"]], cache_hashes[row["arm_key"]] = interval_cell(cache_dir, row, len(rows))
    ratios, finalists = finalist_selection(selection, rows, intervals)
    return {"schema": "ectd.graph-confirmation-analysis-candidate/v1",
            "status": "confirmed_receipts_analyzed", "experiment_id": plan["experiment_id"],
            "approval": plan["approved_by"], "selection_sha256": sha(selection_path),
            "schedule_sha256": sha(schedule_path), "plan_sha256": plan_hash,
            "family_count": len(rows), "simultaneous_coverage_at_least": "99/100",
            "tail_numerator": 1, "tail_denominator": 200 * len(rows),
            "confirmation_summary": rows, "intervals": intervals,
            "interval_cache_sha256": cache_hashes,
            "low_x_over_random_x": ratios, "finalists": finalists,
            "scope": "held-out confirmation and finalist nomination only; complete ECDLP costs remain unmeasured"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "selection", "schedule", "plan", "cache-dir", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.repo, args.selection, args.schedule, args.plan, args.cache_dir)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "family_count": result["family_count"],
                      "finalist_counts": {key: len(value) for key, value in result["finalists"].items()},
                      "output_sha256": sha(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
