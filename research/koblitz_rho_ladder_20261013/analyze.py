#!/usr/bin/env python3
"""Validate and analyse the frozen paired ecbench Koblitz ladder."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import bootstrap


EXPECTED_ARMS = {
    "rho-frob": (
        "rho.signed_frobenius",
        "ic_boundary::signed_frobenius_rho_tuned",
    ),
    "rho-neg": (
        "rho.negation",
        "ic_boundary::rho_walk_with(NegationClasses, RhoWalk::negation())",
    ),
    "rho-plain": (
        "rho.plain",
        "ic_boundary::rho_walk_with(PointClasses, RhoWalk::plain())",
    ),
}
BOOTSTRAP_SEED = 2026101303
BOOTSTRAP_RESAMPLES = 50_000
EXPECTED_SPEC_FILE_SHA256 = "751769ef2eeb6c9946f9822c14956c9c2617335859e46752ad7f1e510586c950"
EXPECTED_SPEC_ID = "ECS1h37e1cc41d056"
EXPECTED_SPEC_SHA256 = "37e1cc41d0563266c2841d6fbeb2dd9665caa15e5228dab91a6883852c72a8a2"
EXPECTED_BINARY_SHA256 = "f2164ce16c6ae17c408777dc2448e8f226a42ca8c4d3da1d00aeff7419ec1f88"
EXPECTED_PRODUCER_COMMIT = "0dc6b7f4a03253e7c7641f99700f7f423f8d07e0"
EXPECTED_ROLES = {
    "rho-frob": "reference",
    "rho-neg": "baseline",
    "rho-plain": "control",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes(path: Path) -> bytes:
    if path.suffix == ".zst":
        proc = subprocess.run(
            ["zstd", "-q", "-d", "-c", "--", str(path)],
            check=True,
            stdout=subprocess.PIPE,
        )
        return proc.stdout
    return path.read_bytes()


def ratio_of_means(numerator: np.ndarray, denominator: np.ndarray, axis: int = -1):
    return np.mean(numerator, axis=axis) / np.mean(denominator, axis=axis)


def bca_ratio(
    numerator: np.ndarray,
    denominator: np.ndarray,
    *,
    cell_m: int,
    cell_a: int,
    metric_tag: int,
) -> dict[str, float | int | str]:
    point = float(ratio_of_means(numerator, denominator))
    seed = np.random.SeedSequence(
        [BOOTSTRAP_SEED, cell_m, cell_a, metric_tag]
    )
    result = bootstrap(
        (numerator, denominator),
        ratio_of_means,
        paired=True,
        vectorized=True,
        axis=0,
        confidence_level=0.95,
        n_resamples=BOOTSTRAP_RESAMPLES,
        batch=1_000,
        method="BCa",
        rng=np.random.default_rng(seed),
    )
    low = float(result.confidence_interval.low)
    high = float(result.confidence_interval.high)
    if not (
        math.isfinite(point)
        and math.isfinite(low)
        and math.isfinite(high)
        and 0.0 < low <= high
    ):
        raise ValueError(f"invalid BCa interval [{low}, {high}] for {point}")
    return {
        "estimand": "ratio_of_arithmetic_means",
        "ratio": point,
        "ci95_low": low,
        "ci95_high": high,
        "bits": math.log2(point),
        "bits_ci95_low": math.log2(low),
        "bits_ci95_high": math.log2(high),
        "method": "paired target-level BCa bootstrap",
        "resamples": BOOTSTRAP_RESAMPLES,
        "root_seed": BOOTSTRAP_SEED,
    }


def nested_number(record: dict, *keys: str) -> float:
    value = record
    for key in keys:
        value = value[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{'.'.join(keys)} is not numeric")
    return float(value)


def counter(record: dict, name: str) -> float:
    return nested_number(record, "counters", name)


def validate_record(record: dict) -> None:
    arm = record.get("arm")
    if arm not in EXPECTED_ARMS:
        raise ValueError(f"unexpected arm {arm!r}")
    expected_id, expected_entry = EXPECTED_ARMS[arm]
    if record["method"]["id"] != expected_id:
        raise ValueError(f"arm/method mismatch for {record.get('record_id')}")
    if record["method"]["entry"] != expected_entry:
        raise ValueError(f"method entry mismatch for {record.get('record_id')}")
    if record["method"]["params"] != {"cap_multiple": "64"}:
        raise ValueError(f"method parameters changed in {record.get('record_id')}")
    if record["role"] != EXPECTED_ROLES[arm]:
        raise ValueError(f"arm/role mismatch for {record.get('record_id')}")
    if record["schema"] != "ecbench.record/v1":
        raise ValueError(f"record schema changed in {record.get('record_id')}")
    if record.get("warmup"):
        raise ValueError("unexpected warm-up record")
    if record["outcome"]["status"] != "verified":
        raise ValueError(f"non-verified record {record.get('record_id')}")
    if record["outcome"].get("matches_target") is not True:
        raise ValueError(f"target mismatch in {record.get('record_id')}")
    if record["outcome"].get("matches_planted") is not True:
        raise ValueError(f"planted-key mismatch in {record.get('record_id')}")
    if int(record["outcome"]["recovered"]) != int(record["workload"]["planted"]):
        raise ValueError(f"recovered scalar mismatch in {record.get('record_id')}")

    walks = counter(record, "walks")
    starts = counter(record, "start_additions")
    if starts + 1 != walks:
        raise ValueError(f"walk/start identity failed in {record.get('record_id')}")
    walk = counter(record, "walk_operations")
    walk_parts = (
        counter(record, "steps")
        + counter(record, "look_ahead_additions")
        + counter(record, "cycle_escape_doublings")
    )
    if walk != walk_parts:
        raise ValueError(f"walk-operation identity failed in {record.get('record_id')}")
    total_parts = (
        counter(record, "setup_additions")
        + counter(record, "setup_doublings")
        + starts
        + walk
        + counter(record, "verification_operations")
    )
    total = nested_number(record, "cost", "total_gae")
    if total != total_parts:
        raise ValueError(f"counted-GAE identity failed in {record.get('record_id')}")
    phase_total = sum(float(phase["gae"]) for phase in record["phases"])
    if not math.isclose(total, phase_total, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(f"phase/GAE identity failed in {record.get('record_id')}")


def mean(records: list[dict], extractor) -> float:
    return float(np.mean([extractor(record) for record in records]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    args = parser.parse_args()

    spec_bytes = args.spec.read_bytes()
    session_bytes = args.session.read_bytes()
    audit_bytes = args.audit.read_bytes()
    records_bytes = read_bytes(args.records)
    spec = json.loads(spec_bytes)
    session = json.loads(session_bytes)
    audit = json.loads(audit_bytes)
    records = [json.loads(line) for line in records_bytes.splitlines() if line.strip()]

    expected_cells = [(int(c["a"]), int(c["n"])) for c in spec["workloads"]["curves"]]
    expected_targets = int(spec["workloads"]["targets_per_curve"])
    expected_rounds = int(spec["measurement"]["rounds"])
    expected_count = len(expected_cells) * expected_targets * expected_rounds * len(EXPECTED_ARMS)
    if sha256(spec_bytes) != EXPECTED_SPEC_FILE_SHA256:
        raise ValueError("frozen spec file digest changed")
    if session["spec_id"] != EXPECTED_SPEC_ID or session["spec_sha256"] != EXPECTED_SPEC_SHA256:
        raise ValueError("session spec ID does not match the frozen spec")
    if session["binary_sha256"] != EXPECTED_BINARY_SHA256:
        raise ValueError("producer binary digest changed")
    if session["git_commit"] not in (None, EXPECTED_PRODUCER_COMMIT):
        raise ValueError("session embeds an unexpected producer revision")
    if session["git_dirty"] not in (None, False):
        raise ValueError("session reports a dirty producer revision")
    if len(set(expected_cells)) != len(expected_cells):
        raise ValueError("duplicate cell in frozen spec")
    if session["status"] != "complete":
        raise ValueError(f"session status is {session['status']!r}, not complete")
    if len(records) != expected_count:
        raise ValueError(f"found {len(records)} records, expected {expected_count}")
    if session["records_written"] != expected_count:
        raise ValueError("session record count does not match frozen plan")
    if session["executions_planned"] != expected_count:
        raise ValueError("session execution count does not match frozen plan")
    if session["records_sha256"] != sha256(records_bytes):
        raise ValueError("records SHA-256 does not match session seal")
    if audit.get("schema") != "ecbench.audit/v1" or audit.get("ok") is not True:
        raise ValueError("ecbench audit does not pass")
    if audit.get("problems") != [] or not all(audit.get("checks", {}).values()):
        raise ValueError("ecbench audit contains a failed check")
    if audit.get("session_id") != session["session_id"]:
        raise ValueError("ecbench audit/session mismatch")
    if audit.get("records") != expected_count or audit.get("verified_records") != expected_count:
        raise ValueError("ecbench audit record counts do not match")
    if not audit.get("replays") or not all(item.get("reproduced") for item in audit["replays"]):
        raise ValueError("ecbench audit lacks successful deterministic replays")

    pairs: dict[tuple[int, int, str, int], dict[str, dict]] = defaultdict(dict)
    record_ids: set[str] = set()
    session_ids: set[str] = set()
    binaries: set[str] = set()
    sequences: set[int] = set()
    for record in records:
        validate_record(record)
        record_id = record["record_id"]
        if record_id in record_ids:
            raise ValueError(f"duplicate record ID {record_id}")
        record_ids.add(record_id)
        session_ids.add(record["session_id"])
        binaries.add(record["binary_sha256"])
        seq = int(record["seq"])
        if seq in sequences:
            raise ValueError(f"duplicate execution sequence {seq}")
        sequences.add(seq)
        curve_spec = record["workload"]["curve_spec"]
        cell = (int(curve_spec["a"]), int(curve_spec["n"]))
        key = (*cell, record["workload"]["workload_id"], int(record["round"]))
        arm = record["arm"]
        if arm in pairs[key]:
            raise ValueError(f"duplicate arm {arm} in pair {key}")
        pairs[key][arm] = record

    if session_ids != {session["session_id"]}:
        raise ValueError("record/session IDs do not match")
    if binaries != {session["binary_sha256"]}:
        raise ValueError("record/session binary digests do not match")
    if sequences != set(range(expected_count)):
        raise ValueError("execution sequences are not exactly the frozen plan")

    by_cell: dict[tuple[int, int], list[dict[str, dict]]] = defaultdict(list)
    for key, arms in pairs.items():
        if set(arms) != set(EXPECTED_ARMS):
            raise ValueError(f"incomplete pair {key}: {sorted(arms)}")
        seeds = {str(record["algorithm_seed"]) for record in arms.values()}
        workloads = {
            json.dumps(record["workload"], sort_keys=True) for record in arms.values()
        }
        if len(seeds) != 1 or len(workloads) != 1:
            raise ValueError(f"broken seed/workload pairing in {key}")
        for name in (
            "jumps",
            "jump_coefficient_bits",
            "distinguished_point_bits",
            "setup_additions",
            "setup_doublings",
        ):
            if len({counter(record, name) for record in arms.values()}) != 1:
                raise ValueError(f"counter {name} differs within pair {key}")
        expected_actions = {"rho-frob": 2 * key[1], "rho-neg": 2, "rho-plain": 1}
        for arm, expected_action in expected_actions.items():
            if arms[arm]["boundaries"]["automorphisms_used"] != expected_action:
                raise ValueError(f"wrong action order for {arm} in pair {key}")
        by_cell[key[:2]].append(arms)

    actual_cells = set(by_cell)
    if actual_cells != set(expected_cells):
        raise ValueError(f"cell mismatch: {sorted(actual_cells)}")

    cells = []
    for a, m in expected_cells:
        paired = sorted(
            by_cell[(a, m)],
            key=lambda arms: (
                arms["rho-frob"]["workload"]["target_index"],
                arms["rho-frob"]["round"],
            ),
        )
        if len(paired) != expected_targets * expected_rounds:
            raise ValueError(f"cell a={a},m={m} has {len(paired)} pairs")
        target_indices = [
            arms["rho-frob"]["workload"]["target_index"] for arms in paired
        ]
        if target_indices != list(range(expected_targets)):
            raise ValueError(f"target indices are not exactly 0..{expected_targets - 1}")

        def array(arm: str, extractor) -> np.ndarray:
            return np.asarray([extractor(arms[arm]) for arms in paired], dtype=np.float64)

        walk = {
            arm: array(arm, lambda record: counter(record, "walk_operations"))
            for arm in EXPECTED_ARMS
        }
        gae = {
            arm: array(arm, lambda record: nested_number(record, "cost", "total_gae"))
            for arm in EXPECTED_ARMS
        }
        wall = {
            arm: array(arm, lambda record: nested_number(record, "time", "solve_wall_ns"))
            for arm in EXPECTED_ARMS
        }

        walk_neg_frob = bca_ratio(
            walk["rho-neg"], walk["rho-frob"], cell_m=m, cell_a=a, metric_tag=1
        )
        gae_neg_frob = bca_ratio(
            gae["rho-neg"], gae["rho-frob"], cell_m=m, cell_a=a, metric_tag=2
        )
        walk_plain_neg = bca_ratio(
            walk["rho-plain"], walk["rho-neg"], cell_m=m, cell_a=a, metric_tag=3
        )
        wall_neg_frob = bca_ratio(
            wall["rho-neg"], wall["rho-frob"], cell_m=m, cell_a=a, metric_tag=4
        )
        walk_plain_frob = bca_ratio(
            walk["rho-plain"], walk["rho-frob"], cell_m=m, cell_a=a, metric_tag=5
        )
        model_ratio = math.sqrt(m)
        model_bits = 0.5 * math.log2(m)
        first = paired[0]["rho-frob"]

        arm_summary = {}
        for arm in EXPECTED_ARMS:
            arm_records = [arms[arm] for arms in paired]
            lower_bound_values = {record["cost"]["lower_bound"] for record in arm_records}
            if len(lower_bound_values) != 1:
                raise ValueError(f"inconsistent cost-bound label for a={a},m={m},{arm}")
            walk_model = {
                "rho-frob": math.sqrt(math.pi) / (2.0 * math.sqrt(m)),
                "rho-neg": math.sqrt(math.pi) / 2.0,
                "rho-plain": math.sqrt(math.pi / 2.0),
            }[arm]
            diagnostic_names = (
                "look_ahead_additions",
                "cycle_escape_doublings",
                "cycles_length_2",
                "cycles_length_4",
                "cycles_other_length",
                "walks_abandoned_in_a_cycle",
                "walks_capped",
                "useless_collisions",
                "distinguished_points",
            )
            arm_summary[arm] = {
                "mean_walk_operations": float(np.mean(walk[arm])),
                "walk_operations_sd": float(np.std(walk[arm], ddof=1)),
                "mean_walk_over_sqrt_r": float(
                    np.mean(walk[arm]) / math.sqrt(first["workload"]["curve"]["r"])
                ),
                "random_map_model_walk_over_sqrt_r": walk_model,
                "mean_total_counted_gae": float(np.mean(gae[arm])),
                "counted_gae_is_lower_bound": lower_bound_values.pop(),
                "mean_setup_operations": mean(
                    arm_records,
                    lambda record: counter(record, "setup_additions")
                    + counter(record, "setup_doublings"),
                ),
                "mean_start_additions": mean(
                    arm_records, lambda record: counter(record, "start_additions")
                ),
                "mean_verification_operations": mean(
                    arm_records,
                    lambda record: counter(record, "verification_operations"),
                ),
                "mean_canonicalisations_unpriced": mean(
                    arm_records,
                    lambda record: counter(record, "canonicalisations_uncharged"),
                ),
                "mean_solve_wall_ns_descriptive": float(np.mean(wall[arm])),
                "local_walks_restarted_at_cap": int(
                    sum(counter(record, "walks_capped") for record in arm_records)
                ),
                "diagnostic_counter_totals": {
                    name: int(sum(counter(record, name) for record in arm_records))
                    for name in diagnostic_names
                },
            }

        cells.append(
            {
                "a": a,
                "m": m,
                "mu": 1 if a == 1 else -1,
                "curve_slug": first["workload"]["curve"]["slug"],
                "r": first["workload"]["curve"]["r"],
                "log2_r": math.log2(first["workload"]["curve"]["r"]),
                "cofactor": first["workload"]["curve"]["cofactor"],
                "automorphisms_available": first["workload"]["curve"][
                    "automorphisms_available"
                ],
                "pairs": len(paired),
                "verified_records": len(paired) * len(EXPECTED_ARMS),
                "status": "VALID_EXPLORATORY_OBSERVATION",
                "model": {"sqrt_m": model_ratio, "rho_bits": model_bits},
                "walk_neg_over_frob": walk_neg_frob,
                "walk_residual_bits": walk_neg_frob["bits"] - model_bits,
                "walk_point_within_0_15_bit_marker": abs(
                    walk_neg_frob["bits"] - model_bits
                )
                <= 0.15,
                "counted_gae_neg_over_frob": gae_neg_frob,
                "walk_plain_over_neg": walk_plain_neg,
                "plain_neg_residual_from_sqrt2_bits": walk_plain_neg["bits"] - 0.5,
                "walk_plain_over_frob_supplementary": walk_plain_frob,
                "plain_frob_model_bits": 0.5 * math.log2(2 * m),
                "plain_frob_residual_bits": walk_plain_frob["bits"]
                - 0.5 * math.log2(2 * m),
                "solve_wall_neg_over_frob_descriptive": wall_neg_frob,
                "arms": arm_summary,
            }
        )

    output = {
        "schema": "koblitz-rho-ladder-analysis/v1",
        "status": "EXPLORATORY_NOT_LEDGER_EVIDENCE",
        "claim_boundary": (
            "word-sized counter calibration only; not a measured bound, "
            "runtime speedup, isogeny-transfer result, or weak-curve verdict"
        ),
        "inputs": {
            "spec_path": str(args.spec),
            "spec_file_sha256": sha256(spec_bytes),
            "session_path": str(args.session),
            "session_file_sha256": sha256(session_bytes),
            "audit_path": str(args.audit),
            "audit_file_sha256": sha256(audit_bytes),
            "records_path": str(args.records),
            "records_uncompressed_sha256": sha256(records_bytes),
            "session_id": session["session_id"],
            "spec_id": session["spec_id"],
            "binary_sha256": session["binary_sha256"],
            "producer_git_commit_embedded_by_session": session["git_commit"],
            "producer_git_dirty_embedded_by_session": session["git_dirty"],
            "producer_git_commit_observed_before_build": EXPECTED_PRODUCER_COMMIT,
            "producer_revision_binding": (
                "external build provenance plus binary SHA-256; this producer build "
                "did not embed Git metadata in the session"
            ),
        },
        "validation": {
            "planned_records": expected_count,
            "records_read": len(records),
            "outcome_counts": {"verified": len(records)},
            "all_records_verified": True,
            "all_pairs_complete": True,
            "all_pair_seeds_and_targets_equal": True,
            "all_counter_identities_pass": True,
            "ecbench_seals_and_session_audit_pass": True,
            "deterministic_replays": len(audit["replays"]),
            "all_overall_solves_completed_without_timeout_or_exhaustion": True,
            "local_walk_cap_restarts_retained": int(
                sum(
                    counter(record, "walks_capped")
                    for record in records
                )
            ),
            "cells": len(cells),
            "pairs_per_cell": expected_targets * expected_rounds,
        },
        "inference": {
            "primary_counter": "counters.walk_operations",
            "primary_estimand": "log2(mean(rho-neg) / mean(rho-frob))",
            "bootstrap": "paired target-level BCa",
            "resamples": BOOTSTRAP_RESAMPLES,
            "root_seed": BOOTSTRAP_SEED,
            "simultaneous_intervals": False,
            "cells_pooled": False,
            "counted_gae_ratio_warning": (
                "ratio of two differently incomplete counts; omitted canonicalisation "
                "cost means it is not itself a one-sided bound"
            ),
            "wall_interval_warning": (
                "BCa sampling interval is descriptive only; L0 virtual-host timing"
            ),
        },
        "cells": cells,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")

    columns = [
        "a",
        "m",
        "mu",
        "r",
        "log2_r",
        "cofactor",
        "pairs",
        "walk_ratio",
        "walk_ci95_low",
        "walk_ci95_high",
        "walk_bits",
        "walk_bits_ci95_low",
        "walk_bits_ci95_high",
        "model_bits",
        "residual_bits",
        "counted_gae_ratio",
        "plain_neg_walk_ratio",
        "plain_frob_walk_ratio",
        "plain_frob_walk_bits",
        "wall_ratio_descriptive",
    ]
    with args.csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for cell in cells:
            writer.writerow(
                {
                    "a": cell["a"],
                    "m": cell["m"],
                    "mu": cell["mu"],
                    "r": cell["r"],
                    "log2_r": f"{cell['log2_r']:.9f}",
                    "cofactor": cell["cofactor"],
                    "pairs": cell["pairs"],
                    "walk_ratio": f"{cell['walk_neg_over_frob']['ratio']:.9f}",
                    "walk_ci95_low": f"{cell['walk_neg_over_frob']['ci95_low']:.9f}",
                    "walk_ci95_high": f"{cell['walk_neg_over_frob']['ci95_high']:.9f}",
                    "walk_bits": f"{cell['walk_neg_over_frob']['bits']:.9f}",
                    "walk_bits_ci95_low": f"{cell['walk_neg_over_frob']['bits_ci95_low']:.9f}",
                    "walk_bits_ci95_high": f"{cell['walk_neg_over_frob']['bits_ci95_high']:.9f}",
                    "model_bits": f"{cell['model']['rho_bits']:.9f}",
                    "residual_bits": f"{cell['walk_residual_bits']:.9f}",
                    "counted_gae_ratio": f"{cell['counted_gae_neg_over_frob']['ratio']:.9f}",
                    "plain_neg_walk_ratio": f"{cell['walk_plain_over_neg']['ratio']:.9f}",
                    "plain_frob_walk_ratio": f"{cell['walk_plain_over_frob_supplementary']['ratio']:.9f}",
                    "plain_frob_walk_bits": f"{cell['walk_plain_over_frob_supplementary']['bits']:.9f}",
                    "wall_ratio_descriptive": f"{cell['solve_wall_neg_over_frob_descriptive']['ratio']:.9f}",
                }
            )


if __name__ == "__main__":
    main()
