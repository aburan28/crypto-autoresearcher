#!/usr/bin/env python3
"""Replay the frozen FROB checker without editing its run directory."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from math import isqrt, prod
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN_REL = Path("experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2")
RUN = ROOT / RUN_REL
SOURCE_COMMIT = "e83bb2f14414c9669360816aeee5876dfcfd4384"
OUTPUT = HERE / "audit.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_prime_by_trial_division(n: int) -> bool:
    if n < 2:
        return False
    return all(n % d for d in range(2, isqrt(n) + 1))


def rational_partition_valid(partition: dict, n_order: int) -> bool:
    """Independently recompute stored arithmetic from aggregate counts only."""
    if partition["status"] != "ok" or n_order < 2:
        return False
    distinct = partition["distinct_targets"]
    union_size = partition["B_union_size"]
    block_sizes = partition["block_sizes"]
    if (
        distinct < 0 or distinct > n_order - 1
        or union_size < 0 or union_size > n_order - 1
        or any(size < 0 or size % 2 for size in block_sizes)
        or partition["p_m"] != [distinct, n_order - 1]
        or partition["U_neg"] != [union_size, 2]
        or partition["prod_tuple_count"] != prod(block_sizes)
    ):
        return False
    for extra in (0, 8, 32):
        recorded = partition["cost_ratio_neg"][str(extra)]
        if distinct == 0:
            if recorded != {"denominator_zero": True, "numerator": [union_size, 2]}:
                return False
        else:
            value = (Fraction(union_size, 2) + 1 + extra) / Fraction(
                distinct, n_order - 1
            )
            if recorded != {
                "denominator_zero": False,
                "value": [value.numerator, value.denominator],
            }:
                return False
    return True


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=check, capture_output=True
    )


def audit() -> dict:
    manifest_path = RUN / "manifest.yaml"
    manifest_bytes = manifest_path.read_bytes()
    run = yaml.safe_load(manifest_bytes)["run"]
    assert run["id"] == "RUN-FROB-91ee9c-7119f2"
    assert git("show", f"{SOURCE_COMMIT}:{RUN_REL}/manifest.yaml").stdout == manifest_bytes

    artifacts = []
    for name, record in sorted(run["artifacts"].items()):
        artifact_path = (ROOT / record["path"]).resolve()
        assert artifact_path.is_relative_to(RUN.resolve()), name
        contents = artifact_path.read_bytes()
        artifacts.append(
            {
                "name": name,
                "path": record["path"],
                "bytes": len(contents),
                "sha256": digest(contents),
                "bytes_match": len(contents) == record["bytes"],
                "sha256_match": digest(contents) == record["sha256"],
            }
        )

    code = run["code"]
    recorded_head = code["head_commit"]
    assert git("cat-file", "-t", recorded_head).stdout.strip() == b"commit"
    driver_at_head = git(
        "cat-file", "-e", f"{recorded_head}:{code['driver_path']}", check=False
    ).returncode == 0

    with tempfile.TemporaryDirectory(prefix="frob-checker-replay-") as scratch:
        copied = Path(scratch) / "run"
        shutil.copytree(RUN, copied)
        checker = subprocess.run(
            [sys.executable, str(copied / "checker.py"), str(copied)],
            check=True,
            capture_output=True,
            text=True,
        )
        replay_bytes = (copied / "work/checker-report.json").read_bytes()
        assert json.loads(checker.stdout) == json.loads(replay_bytes)

    archived_bytes = (RUN / "work/checker-report.json").read_bytes()
    checker_report = json.loads(replay_bytes)
    tuples = checker_report["tuple_sum_reverifications"]
    tuple_statuses = Counter(item["status"] for item in tuples)
    confirmed_tuples = [item for item in tuples if item["status"] == "ok"]
    raw_result = json.loads((RUN / "raw-result.json").read_text())
    raw_cells = [json.loads(line) for line in (RUN / "raw.jsonl").read_text().splitlines()]
    curve_inventory = []
    for record in raw_cells:
        cell = record["data"]
        curve_inventory.append({
            "cell": record["cell"],
            "status": cell.get("cell_status"),
            "curves": [{
                "N": curve["N"],
                "object_partition_count": len(curve.get("object_arm_partitions", [])),
                "C2_partition_count": len(curve.get("C2_arm_partitions", [])),
                "C3_seed_count": len(curve.get("C3_arm_by_seed", {})),
                "object_partition_residue_lists_stored": any(
                    "_ks" in partition
                    for partition in curve.get("object_arm_partitions", [])
                ),
            } for curve in cell.get("curves", [])],
        })
    rational_arms = {arm: [] for arm in ("object", "C2", "C3", "C4")}
    for record in raw_cells:
        cell = record["data"]
        for curve in cell.get("curves", []):
            n_order = curve["N"]
            rational_arms["object"].extend(
                (partition, n_order) for partition in curve.get("object_arm_partitions", [])
                if partition["status"] == "ok"
            )
            rational_arms["C2"].extend(
                (partition, n_order) for partition in curve.get("C2_arm_partitions", [])
                if partition["status"] == "ok"
            )
            for partitions in curve.get("C3_arm_by_seed", {}).values():
                rational_arms["C3"].extend(
                    (partition, n_order) for partition in partitions
                    if partition["status"] == "ok"
                )
        c4 = cell.get("C4", {})
        for partitions in c4.get("partitions_by_seed", {}).values():
            rational_arms["C4"].extend(
                (partition, c4["N"]) for partition in partitions
                if partition["status"] == "ok"
            )
    rational_counts = {arm: len(rows) for arm, rows in rational_arms.items()}
    rational_all_match = all(
        rational_partition_valid(partition, n_order)
        for rows in rational_arms.values() for partition, n_order in rows
    )
    sample, sample_order = rational_arms["object"][0]
    mutant = deepcopy(sample)
    mutant["cost_ratio_neg"]["0"]["value"][0] += 1
    rational_mutant_rejected = not rational_partition_valid(mutant, sample_order)

    result = {
        "schema": "frob-historical-provenance-audit/v1",
        "source_commit": SOURCE_COMMIT,
        "run_id": run["id"],
        "manifest_sha256": digest(manifest_bytes),
        "artifacts": artifacts,
        "artifact_summary": {
            "count": len(artifacts),
            "stored_bytes": sum(item["bytes"] for item in artifacts),
            "all_bytes_match": all(item["bytes_match"] for item in artifacts),
            "all_sha256_match": all(item["sha256_match"] for item in artifacts),
            "stored_bytes_match_manifest": sum(item["bytes"] for item in artifacts)
            == run["artifact_stored_bytes_excluding_manifest"],
        },
        "checker_replay": {
            "checker_sha256": digest((RUN / "checker.py").read_bytes()),
            "archived_report_sha256": digest(archived_bytes),
            "replay_report_sha256": digest(replay_bytes),
            "byte_identical": replay_bytes == archived_bytes,
            "trace_kernel_dimension_checks": len(checker_report["field_and_c5_checks"]),
            "trace_kernel_dimensions_all_match": all(
                item["dim_ker_T_matches"] for item in checker_report["field_and_c5_checks"]
            ),
            "orbit_divisibility_checks": len(checker_report["orbit_divisibility_checks"]),
            "orbit_divisibility_all_true": all(
                item["divisible"] for item in checker_report["orbit_divisibility_checks"]
            ),
            "tuple_status_counts": dict(sorted(tuple_statuses.items())),
            "curve_witness_checks": len(confirmed_tuples),
            "curve_witness_order_probable_prime_frobenius_all_true": all(
                item["independent_order_N_confirmed"]
                and item["independent_N_prime"]
                and item["independent_frobenius_eigenvalue_confirmed"]
                for item in confirmed_tuples
            ),
            "curve_witness_N_prime_by_trial_division_all_true": all(
                is_prime_by_trial_division(item["N"]) for item in confirmed_tuples
            ),
            "tuple_sumsets_recomputed": 0,
            "control_arms_recomputed": 0,
        },
        "historical_cell_statuses": {
            cell: item["status"] for cell, item in sorted(raw_result["cells"].items())
        },
        "raw_curve_inventory": curve_inventory,
        "aggregate_rational_recheck": {
            "partition_counts": rational_counts,
            "all_stored_identities_match": rational_all_match,
            "mutated_ratio_rejected": rational_mutant_rejected,
            "scope": "aggregate arithmetic only; no tuple sumsets or slot membership reconstructed",
        },
        "execution_provenance": {
            "recorded_head_commit": recorded_head,
            "recorded_driver_path": code["driver_path"],
            "driver_present_in_recorded_head": driver_at_head,
            "run_directory_recorded_untracked_at_execution_start":
                "untracked" in code["dirty_note"],
            "schema_code_commit_present": bool(code.get("commit")),
            "schema_code_command_present": bool(code.get("command")),
            "schema_environment_present": bool(run.get("environment")),
            "separate_command_and_environment_artifacts_present":
                (RUN / "command.txt").is_file() and (RUN / "environment.json").is_file(),
            "generator_execution_source_bound": False,
        },
        "scope_note": (
            "This replays the archived pure-Python checker and hash pins. The "
            "checker's tuple_sum_reverifications entries check curve witnesses, "
            "not tuple sumsets or control arms. It does not rerun the Sage "
            "generator or bind the original untracked driver to the pre-run HEAD."
        ),
    }
    assert result["artifact_summary"] == {
        "count": 14,
        "stored_bytes": 566042,
        "all_bytes_match": True,
        "all_sha256_match": True,
        "stored_bytes_match_manifest": True,
    }
    assert result["checker_replay"]["byte_identical"]
    assert result["checker_replay"]["trace_kernel_dimension_checks"] == 3
    assert result["checker_replay"]["trace_kernel_dimensions_all_match"]
    assert result["checker_replay"]["orbit_divisibility_checks"] == 6
    assert result["checker_replay"]["orbit_divisibility_all_true"]
    assert result["checker_replay"]["curve_witness_checks"] == 3
    assert result["checker_replay"]["curve_witness_order_probable_prime_frobenius_all_true"]
    assert result["checker_replay"]["curve_witness_N_prime_by_trial_division_all_true"]
    assert result["historical_cell_statuses"] == {
        "FROB-SPLIT-q11n5": "completed",
        "FROB-NOLATTICE-q13n5": "completed",
        "FROB-EQDEG-q19n5": "completed",
        "FROB-EXT-q13n7": "not_run_resource",
    }
    assert len(curve_inventory) == 4
    assert rational_counts == {"object": 8, "C2": 3, "C3": 6, "C4": 6}
    assert rational_all_match and rational_mutant_rejected
    assert [len(row["curves"]) for row in curve_inventory] == [2, 2, 2, 0]
    assert all(
        not curve["object_partition_residue_lists_stored"]
        for row in curve_inventory for curve in row["curves"]
    )
    assert result["checker_replay"]["tuple_status_counts"] == {
        "ok": 3,
        "skipped_too_large_for_pure_python_full_reenumeration_this_session": 3,
    }
    assert not driver_at_head
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    serialized = json.dumps(audit(), indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
    elif OUTPUT.read_text() != serialized:
        print("audit.json is stale", file=sys.stderr)
        return 1
    else:
        print("FROB audit is byte-exact and current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
