"""Candidate deterministic discovery selector; no scientific data are bundled.

The Coordinator must freeze this source, control-root commitment, and trial
plan before discovery. A missing or invalid arm prevents any selection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MAIN = ("low_x", "mid_x", "random_x")
EXPECTED = {"P29": {"vertices": 2049, "quota": 8192, "extreme_count": 8,
                    "control_count": 16},
            "P37": {"vertices": 257, "quota": 2048, "extreme_count": 4,
                    "control_count": 8}}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def hex_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value)


def draw_controls(root: bytes, stratum: str, vertices: int, count: int) -> list[int]:
    """Draw distinct uniform indices by 256-bit rejection, before yields exist."""
    require(len(root) == 32 and 0 < count <= vertices, "invalid control draw inputs")
    accepted: list[int] = []
    seen: set[int] = set()
    ceiling = (1 << 256) // vertices * vertices
    counter = 0
    while len(accepted) < count:
        domain = json.dumps(["ectd.graph-control-index/v1", stratum, counter],
                            separators=(",", ":")).encode()
        value = int.from_bytes(hashlib.sha256(root + b"\0" + domain).digest(), "big")
        counter += 1
        if value >= ceiling:
            continue
        index = value % vertices
        if index not in seen:
            seen.add(index)
            accepted.append(index)
    return accepted


def discover_one(root: Path, plan: dict, plan_sha: str, row: dict, trial: dict) -> dict:
    """Read one supervisor-validated result; never turn failure into zero yield."""
    run_dir = root / Path(plan["specification"]).parent / "runs" / trial["run_id"]
    receipt = read(run_dir / "execution-receipt.json")
    require(receipt.get("status") == "output_validated" and
            receipt.get("returncode") == receipt.get("check_returncode") == 0 and
            receipt.get("plan_sha256") == plan_sha and
            receipt.get("trial_id") == row["arm_key"] and
            receipt.get("run_id") == trial["run_id"],
            f"unvalidated supervisor run: {row['arm_key']}")
    artifacts = receipt.get("artifact_sha256", {})
    for name in ("raw-result.json", "manifest.yaml", "check.stdout.log", "check.stderr.log"):
        require(artifacts.get(name) == sha(run_dir / name),
                f"supervisor artifact digest differs: {row['arm_key']} {name}")
    result = read(run_dir / "raw-result.json")
    manifest = read(run_dir / "manifest.yaml")
    attempt_path = run_dir / "attempt" / "receipt.json"
    attempt = read(attempt_path)
    require(result.get("schema") == "ectd.graph-trial-result.v1" and
            manifest.get("schema") == "ectd.graph-trial-manifest.v1" and
            attempt.get("schema") == "ectd.graph-arm-execution-attempt.v1" and
            result.get("status") == manifest.get("status") == attempt.get("status") ==
            "completed_unreviewed" and result.get("mode") == attempt.get("mode") ==
            "scientific_trial" and manifest.get("subprocess_return_code") == 0,
            f"graph attempt incomplete: {row['arm_key']}")
    require(hex_digest(attempt.get("admission_sha256")) and
            result.get("attempt_receipt_sha256") == manifest.get("attempt_receipt_sha256") ==
            sha(attempt_path) and manifest.get("raw_result_sha256") == sha(run_dir / "raw-result.json") and
            attempt.get("admission_sha256") == result.get("digests", {}).get("admission_sha256"),
            f"graph attempt binding differs: {row['arm_key']}")
    prepared_path = Path(manifest["paths"]["prepared-manifest"])
    input_path = Path(manifest["paths"]["input"])
    prepared = read(prepared_path)
    endpoint = bool(row.get("endpoint_id"))
    require(result["digests"].get("prepared-manifest_sha256") == sha(prepared_path) and
            result["digests"].get("input_sha256") == sha(input_path) and
            prepared.get("input_sha256") == sha(input_path) and
            prepared.get("seed_mode") == "independent_verifier_root" and
            prepared.get("schedule_conformant") is True and
            all(hex_digest(prepared.get(key)) for key in
                ("base_root_sha256", "target_root_sha256", "verifier_root_sha256",
                 "commitment_sha256")) and
            prepared.get("j") == row["model"]["j"] and
            prepared.get("stratum") == row["stratum"] and
            prepared.get("index") == (None if endpoint else row["path_index"]) and
            prepared.get("endpoint_id") == row.get("endpoint_id") and
            prepared.get("arm") == row["base_rule"] and
            prepared.get("target_count") == row["discovery_targets"],
            f"prepared input or seed identity differs: {row['arm_key']}")
    expected_model = row.get("output_model", row["model"])
    expected_generator = row.get("output_generator", row["generator"])
    with input_path.open() as stream:
        header = next(stream).split()
    require(header == ["curve", str(row["p"]), str(expected_model["a"]),
                       str(expected_model["b"]), str(row["r"]),
                       str(2 * row["base_x_orbits"]), str(row["discovery_targets"])] and
            prepared.get("generator") == expected_generator,
            f"prepared curve or generator differs: {row['arm_key']}")
    coefficients = hashlib.sha256()
    target_rows = 0
    with input_path.open() as stream:
        next(stream)
        for _ in range(2 * row["base_x_orbits"]):
            next(stream)
        for line in stream:
            parts = line.split()
            require(len(parts) == 6 and parts[:2] == ["target", str(target_rows)],
                    f"target row order differs: {row['arm_key']}")
            coefficients.update((parts[2] + "," + parts[3] + "\n").encode())
            target_rows += 1
    require(target_rows == row["discovery_targets"], f"target extent differs: {row['arm_key']}")
    expected_prepared = {"stratum": row["stratum"], "index": None if endpoint else row["path_index"],
                         "arm": row["base_rule"], "stage": "discovery",
                         "target_count": row["discovery_targets"]}
    require(result.get("prepared") == expected_prepared and
            attempt.get("bindings", {}).get("stratum") == row["stratum"] and
            attempt["bindings"].get("index") == expected_prepared["index"] and
            attempt["bindings"].get("arm") == row["base_rule"] and
            attempt["bindings"].get("target_count") == row["discovery_targets"],
            f"prepared arm identity differs: {row['arm_key']}")
    rank = result.get("rank_check", {})
    required_prefixes = {min(row["discovery_targets"], n) for n in
                         (512, 2048, 8192, 32768)}
    require(rank.get("status") == "valid" and rank.get("targets") == row["discovery_targets"] and
            rank.get("independent_ordered_count_match") is True and
            isinstance(rank.get("useful_targets"), int) and
            0 <= rank["useful_targets"] <= row["discovery_targets"] and
            all(str(n) in rank.get("rank_prefix", {}) for n in required_prefixes),
            f"rank or quota differs: {row['arm_key']}")
    checked = read(run_dir / "check.stdout.log")
    require(checked.get("status") == "valid" and
            checked.get("targets") == rank["targets"] and
            checked.get("useful_targets") == rank["useful_targets"] and
            checked.get("rank_increments") == rank["rank_increments"],
            f"independent checker summary differs: {row['arm_key']}")
    if row["base_rule"] in ("graph_transport", "u2_transport"):
        require(row.get("control_reference") in trial.get("depends_on", []) and
                checked.get("transport_pair_checked") is True,
                f"transport oracle or dependency missing: {row['arm_key']}")
    return {"arm_key": row["arm_key"], "stratum": row["stratum"],
            "index": None if endpoint else row["path_index"],
            **({"endpoint_id": row["endpoint_id"]} if endpoint else {}),
            "j": row["model"]["j"],
            "arm": row["base_rule"], "target_count": rank["targets"],
            "useful_targets": rank["useful_targets"],
            "rank_increments": rank["rank_increments"],
            "rank_prefix": rank["rank_prefix"],
            "coefficient_sha256": coefficients.hexdigest(),
            "base_root_sha256": prepared["base_root_sha256"],
            "target_root_sha256": prepared["target_root_sha256"],
            "verifier_root_sha256": prepared["verifier_root_sha256"],
            "commitment_sha256": prepared["commitment_sha256"],
            "run_id": trial["run_id"], "execution_receipt_sha256": sha(run_dir / "execution-receipt.json"),
            "raw_result_sha256": sha(run_dir / "raw-result.json")}


def nominate(schedule: list[dict], results: list[dict], control_root: bytes) -> dict:
    require(len(schedule) == len(results), "discovery coverage incomplete")
    expected_keys = {row["arm_key"] for row in schedule}
    require(len(expected_keys) == len(schedule) and
            {row["arm_key"] for row in results} == expected_keys and
            len({row["arm_key"] for row in results}) == len(results),
            "discovery arm identities differ")
    by_key = {row["arm_key"]: row for row in results}
    for field in ("base_root_sha256", "target_root_sha256", "verifier_root_sha256"):
        require(len({row[field] for row in results}) == 1, f"{field} differs across discovery arms")
    strata = {}
    for stratum, config in EXPECTED.items():
        commitments = {row["commitment_sha256"] for row in results
                       if row["stratum"] == stratum}
        require(len(commitments) == 1, f"graph commitment differs within discovery stratum: {stratum}")
        require(len({row["coefficient_sha256"] for row in results if row["stratum"] == stratum}) == 1,
                f"paired target coefficient stream differs: {stratum}")
        native = {arm: [] for arm in MAIN}
        for row in schedule:
            if row["stratum"] != stratum or row["base_rule"] not in MAIN:
                continue
            result = by_key[row["arm_key"]]
            require(result["target_count"] == config["quota"] and
                    result["index"] == row["path_index"] and
                    result["j"] == row["model"]["j"] and
                    result["arm"] == row["base_rule"],
                    f"native result identity differs: {row['arm_key']}")
            native[row["base_rule"]].append(result)
        require(all(len(native[arm]) == config["vertices"] for arm in MAIN),
                f"native vertex coverage differs: {stratum}")
        reasons: dict[int, list[str]] = {}
        extremes = {}
        for arm in MAIN:
            ranked_high = sorted(native[arm], key=lambda row:
                                 (-row["useful_targets"], row["j"], row["index"]))
            ranked_low = sorted(native[arm], key=lambda row:
                                (row["useful_targets"], row["j"], row["index"]))
            top = ranked_high[:config["extreme_count"]]
            bottom = ranked_low[:config["extreme_count"]]
            extremes[arm] = {"top": [row["index"] for row in top],
                             "bottom": [row["index"] for row in bottom],
                             "discovery_min_useful": ranked_low[0]["useful_targets"],
                             "discovery_max_useful": ranked_high[0]["useful_targets"]}
            for label, group in (("top", top), ("bottom", bottom)):
                for row in group:
                    reasons.setdefault(row["index"], []).append(f"{arm}:{label}")
        reasons.setdefault(0, []).append("source")
        controls = draw_controls(control_root, stratum, config["vertices"], config["control_count"])
        for index in controls:
            reasons.setdefault(index, []).append("independent_control")
        selected = sorted(reasons)
        limit = 65 if stratum == "P29" else 33
        require(len(selected) <= limit, "confirmation vertex cap exceeded")
        strata[stratum] = {"commitment_sha256": next(iter(commitments)),
                           "coefficient_sha256": next(row["coefficient_sha256"] for row in results
                                                        if row["stratum"] == stratum),
                           "extremes": extremes, "control_indices_draw_order": controls,
                           "selected_vertices": [{"index": index, "reasons": reasons[index]}
                                                 for index in selected],
                           "confirmation_arm_keys": [f"{stratum}-v{index:04d}-{arm}"
                                                     for index in selected for arm in MAIN]}
    require(strata["P29"]["commitment_sha256"] != strata["P37"]["commitment_sha256"],
            "distinct graph strata reuse one commitment digest")
    return strata


def select(repo: Path, schedule_path: Path, plan_path: Path,
           commitment_path: Path, control_root_path: Path) -> dict:
    repo = repo.resolve()
    schedule_manifest = read(schedule_path.parent / "manifest.json")
    schedule_verification = read(schedule_path.parent / "verification.json")
    require(schedule_manifest.get("schema") == "ectd-graph-discovery-schedule/v1" and
            schedule_manifest.get("schedule_sha256") == sha(schedule_path) and
            schedule_verification.get("status") == "pass" and
            schedule_verification.get("schedule_sha256") == sha(schedule_path),
            "candidate schedule binding differs")
    schedule = [json.loads(line) for line in schedule_path.read_text().splitlines()]
    require(len(schedule) == 8206 and len({row["arm_key"] for row in schedule}) == 8206,
            "complete candidate discovery schedule required")
    plan = read(plan_path)
    require(plan.get("schema") == "crypto.autoresearch.trial_plan.v1" and
            plan.get("frozen") is True and plan.get("approved_by") and
            plan.get("experiment_id") and isinstance(plan.get("trials"), list),
            "frozen approved discovery trial plan required")
    for path in (Path(__file__), schedule_path, commitment_path):
        try:
            relative = path.resolve().relative_to(repo).as_posix()
        except ValueError as error:
            raise ValueError(f"analysis input outside repository: {path}") from error
        require(plan.get("source_sha256", {}).get(relative) == sha(path),
                f"approved plan does not freeze {relative}")
    secondary_path = schedule_path.parent / "p29-secondary-floor-arms.jsonl"
    secondary_manifest_path = schedule_path.parent / "p29-secondary-floor-manifest.json"
    secondary_verification_path = schedule_path.parent / "p29-secondary-floor-verification.json"
    secondary_source_spec = repo / "experiments/EXP-ECTD-0cf008/specification.yaml"
    for path in (secondary_path, secondary_manifest_path, secondary_verification_path,
                 secondary_source_spec):
        relative = path.resolve().relative_to(repo).as_posix()
        require(plan.get("source_sha256", {}).get(relative) == sha(path),
                f"approved plan does not freeze {relative}")
    trials = {trial["id"]: trial for trial in plan["trials"]}
    secondary = [json.loads(line) for line in secondary_path.read_text().splitlines()]
    secondary_manifest = read(secondary_manifest_path)
    secondary_verification = read(secondary_verification_path)
    require(len(secondary) == 4 and
            {row.get("arm_key") for row in secondary} == {
                "P29-E2-low_x", "P29-E2-random_x", "P29-E3-low_x", "P29-E3-random_x"} and
            all(row.get("discovery_targets") == 8192 and
                row.get("finalist_selection_eligible") is False for row in secondary) and
            secondary_manifest.get("schedule_sha256") == sha(secondary_path) and
            secondary_manifest.get("primary_graph_schedule_sha256") == sha(schedule_path) and
            secondary_manifest.get("finalist_selection_eligible") is False and
            secondary_manifest.get("source_specification_sha256") == sha(secondary_source_spec) and
            secondary_verification.get("status") == "pass" and
            secondary_verification.get("schedule_sha256") == sha(secondary_path),
            "verified secondary same-conductor schedule required")
    all_rows = schedule + secondary
    require(len(trials) == len(plan["trials"]) == 8210 and
            set(trials) == {row["arm_key"] for row in all_rows} and
            len({trial["run_id"] for trial in plan["trials"]}) == 8210,
            "trial plan does not enumerate every graph and control arm exactly once")
    commitment = read(commitment_path)
    root = bytes.fromhex(control_root_path.read_text().strip())
    require(commitment.get("schema") == "ectd.graph-control-index-commitment/v1" and
            commitment.get("schedule_sha256") == sha(schedule_path) and
            commitment.get("control_root_sha256") == hashlib.sha256(root).hexdigest(),
            "precommitted control draw differs")
    plan_hash = sha(plan_path)
    results = [discover_one(repo, plan, plan_hash, row, trials[row["arm_key"]])
               for row in schedule]
    secondary_results = [discover_one(repo, plan, plan_hash, row, trials[row["arm_key"]])
                         for row in secondary]
    p29_streams = {row["coefficient_sha256"] for row in results if row["stratum"] == "P29"}
    require(len(p29_streams) == 1 and all(
        row["coefficient_sha256"] in p29_streams for row in secondary_results),
        "secondary endpoints do not share the P29 target coefficient stream")
    strata = nominate(schedule, results, root)
    return {"schema": "ectd.graph-discovery-selection-candidate/v1",
            "status": "selected_from_validated_discovery",
            "experiment_id": plan["experiment_id"], "approval": plan["approved_by"],
            "schedule_sha256": sha(schedule_path), "plan_sha256": plan_hash,
            "control_commitment_sha256": sha(commitment_path),
            "control_root_sha256": hashlib.sha256(root).hexdigest(),
            "discovery_arms_checked": len(results), "strata": strata,
            "discovery_summary": results,
            "same_conductor_controls_checked": len(secondary_results),
            "same_conductor_controls": secondary_results,
            "scope": "nomination only; confirmation, exact intervals, and ECDLP costs require fresh runs"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--control-commitment", type=Path, required=True)
    parser.add_argument("--control-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = select(args.repo, args.schedule, args.plan,
                    args.control_commitment, args.control_root)
    payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    with args.out.open("xb") as stream:
        stream.write(payload)
    print(json.dumps({"status": result["status"], "discovery_arms_checked": result["discovery_arms_checked"],
                      "selected_vertices": {key: len(value["selected_vertices"])
                                            for key, value in result["strata"].items()},
                      "output_sha256": hashlib.sha256(payload).hexdigest()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
