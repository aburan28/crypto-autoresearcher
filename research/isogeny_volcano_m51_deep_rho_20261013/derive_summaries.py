#!/usr/bin/env python3
"""Derive the additive CSV views from a sealed four-level rho run.

This script uses only the Python standard library.  Run it with ``-I -S -B``;
it never imports the frozen analyzer and never writes into the sealed run.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ARMS = ("C", "A", "P", "B")
EXPECTED = {
    "C": ("f1", 1),
    "A": ("f271", 271),
    "P": ("f120871", 120871),
    "B": ("f32756041", 32756041),
}
CONTRASTS = ("A-C", "P-C", "B-C", "P-A", "B-A", "B-P", "M271", "M120871", "I")


def fmt(value: object) -> object:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite value: {value!r}")
        return repr(value)
    return value


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            if set(row) != set(fieldnames):
                raise ValueError(f"wrong columns for {path.name}: {sorted(row)}")
            writer.writerow({key: fmt(row[key]) for key in fieldnames})


def load_records(path: Path) -> tuple[Counter[tuple[str, str]], dict[str, set[str]], dict[str, set[int]]]:
    counts: Counter[tuple[str, str]] = Counter()
    curves: dict[str, set[str]] = defaultdict(set)
    conductors: dict[str, set[int]] = defaultdict(set)
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            arm = row["arm"]
            if arm not in ARMS:
                raise ValueError(f"unknown arm {arm!r}")
            if row["ok"] != "1":
                raise ValueError(f"unsuccessful record {row['record_id']}")
            counts[(row["subset"], arm)] += 1
            if row["subset"] == "inference":
                curves[arm].add(row["curve_id"])
            conductors[arm].add(int(row["f_E"]))
    if sum(counts.values()) != 20480:
        raise ValueError(f"expected 20480 records, got {sum(counts.values())}")
    for arm in ARMS:
        if counts[("inference", arm)] != 3072 or counts[("aa", arm)] != 2048:
            raise ValueError(f"wrong subset counts for {arm}: {counts}")
        expected_conductor = EXPECTED[arm][1]
        if conductors[arm] != {expected_conductor}:
            raise ValueError(f"wrong conductor for {arm}: {conductors[arm]}")
    return counts, curves, conductors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    if analysis["status"] != "aa_alert_labels_withheld":
        raise ValueError(f"unexpected analysis status: {analysis['status']}")
    if analysis["sealed_run_status"] != "complete":
        raise ValueError(f"sealed run is not complete: {analysis['sealed_run_status']}")
    if analysis["aa_gate"]["pass"] is not False:
        raise ValueError("A/A gate unexpectedly passed")
    if analysis["counts"] != {
        "aa_solves": 8192,
        "inference_solves": 12288,
        "pair_clusters": 32,
        "records": 20480,
    }:
        raise ValueError(f"unexpected analysis counts: {analysis['counts']}")

    counts, curves, _conductors = load_records(args.records)
    selected = analysis["selected_32_estimand"]
    setup = analysis["setup_and_process_costs"]["native_setup_by_arm"]
    baseline = selected["arm_calibrated_arithmetic_mean_walk_ops"]["C"]
    baseline_bits = selected["arm_log2_means"]["C"]
    levels = []
    for arm in ARMS:
        level, conductor = EXPECTED[arm]
        mean = selected["arm_calibrated_arithmetic_mean_walk_ops"][arm]
        bits = selected["arm_log2_means"][arm]
        levels.append(
            {
                "arm": arm,
                "level": level,
                "f_E": conductor,
                "inference_records": counts[("inference", arm)],
                "aa_records": counts[("aa", arm)],
                "distinct_inference_curve_ids": len(curves[arm]),
                "calibrated_mean_walk_ops": mean,
                "log2_calibrated_mean_walk_ops": bits,
                "ratio_to_C": mean / baseline,
                "delta_bits_vs_C": bits - baseline_bits,
                "native_setup_invocations": setup[arm]["invocations"],
                "native_setup_distinct_models": setup[arm]["distinct_models"],
                "native_setup_mean_sec": setup[arm]["setup_sec"]["mean"],
            }
        )
    level_fields = [
        "arm",
        "level",
        "f_E",
        "inference_records",
        "aa_records",
        "distinct_inference_curve_ids",
        "calibrated_mean_walk_ops",
        "log2_calibrated_mean_walk_ops",
        "ratio_to_C",
        "delta_bits_vs_C",
        "native_setup_invocations",
        "native_setup_distinct_models",
        "native_setup_mean_sec",
    ]
    write_csv(args.output_dir / "level-summary.csv", level_fields, levels)

    by_id = {row["id"]: row for row in analysis["contrasts"]}
    if tuple(row["id"] for row in analysis["contrasts"]) != CONTRASTS:
        raise ValueError("unexpected primary contrast ordering")
    contrast_rows = []
    for contrast_id in CONTRASTS:
        row = by_id[contrast_id]
        if row["decision_label"] != "WITHHELD_AA_ALERT":
            raise ValueError(f"label was not withheld for {contrast_id}")
        contrast_rows.append(
            {
                "contrast_id": contrast_id,
                "estimate_bits": row["bits"],
                "work_ratio": row["work_ratio"],
                "diagnostic_se_bits": row["modeled_population_se_bits"],
                "diagnostic_simultaneous_lower_bits": row["modeled_population_lower_bits"],
                "diagnostic_simultaneous_upper_bits": row["modeled_population_upper_bits"],
                "diagnostic_adjusted_p": row["maxT_adjusted_p"],
                "included_in_nine_contrast_family": True,
                "exact_calibrated_weight_pairing": contrast_id == "B-P",
                "decision_label": row["decision_label"],
                "causal": row["causal"],
                "scope": row["scope"],
            }
        )
    did = analysis["ordinary_difference_in_differences"]
    if did["decision_label"] != "WITHHELD_AA_ALERT" or did["id"] != "2I":
        raise ValueError("ordinary difference-in-differences label was not withheld")
    contrast_rows.append(
        {
            "contrast_id": "2I",
            "estimate_bits": did["bits"],
            "work_ratio": did["work_ratio"],
            "diagnostic_se_bits": did["modeled_population_se_bits"],
            "diagnostic_simultaneous_lower_bits": did["modeled_population_lower_bits"],
            "diagnostic_simultaneous_upper_bits": did["modeled_population_upper_bits"],
            "diagnostic_adjusted_p": did["maxT_adjusted_p"],
            "included_in_nine_contrast_family": False,
            "exact_calibrated_weight_pairing": False,
            "decision_label": did["decision_label"],
            "causal": did["causal"],
            "scope": did["scope"],
        }
    )
    contrast_fields = [
        "contrast_id",
        "estimate_bits",
        "work_ratio",
        "diagnostic_se_bits",
        "diagnostic_simultaneous_lower_bits",
        "diagnostic_simultaneous_upper_bits",
        "diagnostic_adjusted_p",
        "included_in_nine_contrast_family",
        "exact_calibrated_weight_pairing",
        "decision_label",
        "causal",
        "scope",
    ]
    write_csv(args.output_dir / "contrast-summary.csv", contrast_fields, contrast_rows)

    gate = analysis["aa_gate"]
    aa_rows = []
    for index, arm in enumerate(gate["ids"]):
        lower = gate["lower"][index]
        upper = gate["upper"][index]
        margin = gate["margin_bits"]
        aa_rows.append(
            {
                "arm": arm,
                "estimate_bits": gate["estimate"][index],
                "diagnostic_se_bits": gate["se"][index],
                "diagnostic_simultaneous_lower_bits": lower,
                "diagnostic_simultaneous_upper_bits": upper,
                "margin_bits": margin,
                "within_equivalence_margin": lower > -margin and upper < margin,
                "diagnostic_adjusted_p": gate["adjusted_p"][index],
                "max_cluster_squared_influence_share": gate["max_cluster_squared_influence_share"][index],
                "gate_status": gate["gate_status"],
            }
        )
    aa_fields = [
        "arm",
        "estimate_bits",
        "diagnostic_se_bits",
        "diagnostic_simultaneous_lower_bits",
        "diagnostic_simultaneous_upper_bits",
        "margin_bits",
        "within_equivalence_margin",
        "diagnostic_adjusted_p",
        "max_cluster_squared_influence_share",
        "gate_status",
    ]
    write_csv(args.output_dir / "aa-summary.csv", aa_fields, aa_rows)

    pair_rows = []
    pair_data = analysis["descriptive_heterogeneity"]["per_pair_equal_row_weight"]
    if [row["pair_id"] for row in pair_data] != list(range(32)):
        raise ValueError("unexpected pair ids")
    for row in pair_data:
        output: dict[str, object] = {
            "pair_id": row["pair_id"],
            "records_per_arm": row["records_per_arm"],
        }
        output.update({f"mean_walk_ops_{arm}": row["arm_equal_row_weight_means"][arm] for arm in ARMS})
        output.update({f"bits_{contrast}": row["contrasts_bits"][contrast] for contrast in CONTRASTS})
        pair_rows.append(output)
    pair_fields = ["pair_id", "records_per_arm"]
    pair_fields += [f"mean_walk_ops_{arm}" for arm in ARMS]
    pair_fields += [f"bits_{contrast}" for contrast in CONTRASTS]
    write_csv(args.output_dir / "pair-summary.csv", pair_fields, pair_rows)


if __name__ == "__main__":
    main()
