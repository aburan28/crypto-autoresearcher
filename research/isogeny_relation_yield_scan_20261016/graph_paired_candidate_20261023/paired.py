"""Candidate paired targetwise confirmation summaries from validated arms.

The selected vertices are fixed by discovery. This reports descriptive paired
occupancy differences only; it does not approve or interpret an experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

STUDY = Path(__file__).resolve().parents[1]
CONFIRM_SOURCE = STUDY / "graph_confirmation_candidate_20261023/confirm.py"
sys.path.insert(0, str(CONFIRM_SOURCE.parent))
import confirm

ARMS = ("low_x", "mid_x", "random_x")
PAIRS = (("low_x", "mid_x"), ("low_x", "random_x"), ("mid_x", "random_x"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def occupancy(path: Path, expected: dict, expected_coefficient_sha: str,
              expected_stdout_sha: str) -> list[bool]:
    """Read target indicators; independent rank replay already checked triples."""
    require(sha(path) == expected_stdout_sha, f"collector phase digest differs: {path}")
    indicators = []
    coefficient_hash = hashlib.sha256()
    with path.open() as stream:
        header = next(stream).rstrip("\n").split("\t")
        require(header == ["collector-v1", str(expected["p"]), str(expected["r"]),
                           str(2 * expected["base_x_orbits"]),
                           str(expected["target_count"])],
                f"collector header differs: {path}")
        for line in stream:
            fields = line.rstrip("\n").split("\t")
            if fields[0] == "triple":
                require(len(fields) == 5, f"collector triple line differs: {path}")
                continue
            require(len(fields) == 7 and fields[0] == "target" and
                    fields[1] == str(len(indicators)),
                    f"collector target order differs: {path}")
            alpha, beta, unordered, ordered, useful = map(int, fields[2:])
            require(0 <= alpha < expected["r"] and 1 <= beta < expected["r"] and
                    0 <= useful <= unordered <= ordered,
                    f"collector target counts differ: {path}")
            coefficient_hash.update(f"{alpha},{beta}\n".encode())
            indicators.append(useful > 0)
    require(len(indicators) == expected["target_count"] and
            coefficient_hash.hexdigest() == expected_coefficient_sha,
            f"collector extent or paired coefficients differ: {path}")
    return indicators


def paired_counts(left: list[bool], right: list[bool]) -> dict:
    require(len(left) == len(right) and len(left) > 0, "paired target extent differs")
    both = sum(a and b for a, b in zip(left, right))
    left_only = sum(a and not b for a, b in zip(left, right))
    right_only = sum(not a and b for a, b in zip(left, right))
    neither = len(left) - both - left_only - right_only
    return {"targets": len(left), "both": both, "left_only": left_only,
            "right_only": right_only, "neither": neither,
            "paired_difference": {"numerator": left_only - right_only,
                                  "denominator": len(left)},
            "discordant_targets": left_only + right_only}


def analyze(repo: Path, analysis_path: Path, selection_path: Path,
            schedule_path: Path, plan_path: Path) -> dict:
    repo = repo.resolve()
    analysis, selection, plan = read(analysis_path), read(selection_path), read(plan_path)
    require(analysis.get("schema") == "ectd.graph-confirmation-analysis-candidate/v1" and
            analysis.get("status") == "confirmed_receipts_analyzed" and
            analysis.get("plan_sha256") == sha(plan_path) and
            analysis.get("selection_sha256") == sha(selection_path) and
            analysis.get("schedule_sha256") == sha(schedule_path) and
            plan.get("frozen") is True and plan.get("approved_by"),
            "validated confirmation analysis and frozen plan required")
    for source in (Path(__file__), CONFIRM_SOURCE):
        relative = source.resolve().relative_to(repo).as_posix()
        require(plan.get("source_sha256", {}).get(relative) == sha(source),
                f"paired analysis source not frozen: {relative}")
    schedule = {row["arm_key"]: row for row in
                (json.loads(line) for line in schedule_path.read_text().splitlines())}
    trials = {trial["id"]: trial for trial in plan["trials"]}
    summaries = {row["arm_key"]: row for row in analysis["confirmation_summary"]}
    expected_keys = [key for stratum in ("P29", "P37")
                     for key in selection["strata"][stratum]["confirmation_arm_keys"]]
    require(len(summaries) == len(expected_keys) == len(trials) and
            set(summaries) == set(expected_keys) == set(trials),
            "paired confirmation extent differs")
    streams = {}
    for key in expected_keys:
        row = schedule[key]
        verified = confirm.read_validated_arm(repo, plan, sha(plan_path), row, trials[key])
        require(summaries[key] == verified, f"confirmation summary differs from receipt: {key}")
        run_dir = repo / Path(plan["specification"]).parent / "runs" / trials[key]["run_id"]
        attempt = read(run_dir / "attempt/receipt.json")
        phases = [phase for phase in attempt["phases"] if phase["phase"] == "collector"]
        require(len(phases) == 1 and phases[0]["status"] == "completed" and
                phases[0]["return_code"] == 0,
                f"collector phase differs: {key}")
        streams[key] = occupancy(run_dir / "attempt/collector.stdout",
                                 {**row, "target_count": 32768},
                                 verified["coefficient_sha256"], phases[0]["stdout_sha256"])
        require(sum(streams[key]) == verified["useful_targets"],
                f"collector useful-target count differs: {key}")
    strata = {}
    for stratum in ("P29", "P37"):
        vertices = []
        for selected in selection["strata"][stratum]["selected_vertices"]:
            index = selected["index"]
            keys = {arm: f"{stratum}-v{index:04d}-{arm}" for arm in ARMS}
            require(all(key in streams for key in keys.values()),
                    f"paired vertex coverage differs: {stratum} {index}")
            pairs = {f"{left}_minus_{right}": paired_counts(
                         streams[keys[left]], streams[keys[right]])
                     for left, right in PAIRS}
            vertices.append({"index": index, "j": schedule[keys["low_x"]]["model"]["j"],
                             "arm_keys": keys,
                             "useful_targets": {arm: summaries[keys[arm]]["useful_targets"]
                                                for arm in ARMS},
                             "pairs": pairs})
        strata[stratum] = {"selected_vertex_count": len(vertices), "vertices": vertices}
    return {"schema": "ectd.graph-paired-confirmation-candidate/v1",
            "status": "paired_descriptive_summary", "analysis_sha256": sha(analysis_path),
            "selection_sha256": sha(selection_path), "schedule_sha256": sha(schedule_path),
            "plan_sha256": sha(plan_path), "strata": strata,
            "scope": "selected-vertex paired targetwise occupancy only; no causal or ECDLP cost inference"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "analysis", "selection", "schedule", "plan", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.repo, args.analysis, args.selection, args.schedule, args.plan)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": result["status"],
                      "selected_vertices": {key: value["selected_vertex_count"]
                                            for key, value in result["strata"].items()},
                      "output_sha256": sha(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
