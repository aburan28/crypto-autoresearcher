"""Prespecified field-cluster intervals; no point-row pseudoreplication."""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import t as student


def interval(difference, standard_error, degrees, alpha):
    radius = float(student.ppf(1 - alpha / 2, degrees)) * standard_error
    return [difference - radius, difference + radius]


def primary_comparisons(fields, config):
    out = []
    for case in config["primary_cases"]:
        selected = [f for f in fields if f["case"] == case]
        for metric in config["primary_metrics"]:
            for arm in config["primary_control_arms"]:
                if case.startswith("toy"):
                    blocks = {}
                    for field in selected:
                        values = [row[metric] for row in field["curves"]]
                        if any(value is None for value in values):
                            raise ValueError("missing primary metric")
                        blocks.setdefault(field["block"], {}).setdefault(field["arm"], []).append(float(np.mean(values)))
                    if len(blocks) != config["blocks_per_stratum"]:
                        raise ValueError("incomplete toy blocks")
                    expected = {"S": 1, "R": config["random_controls_per_block"], "C": config["residue_controls_per_block"]}
                    if any({key: len(value) for key, value in block.items()} != expected for block in blocks.values()):
                        raise ValueError("incomplete matching")
                    s = np.array([np.mean(blocks[k]["S"]) for k in sorted(blocks)])
                    c = np.array([np.mean(blocks[k][arm]) for k in sorted(blocks)])
                    differences = s - c
                    variance = float(differences.var(ddof=1))
                    se, df = math.sqrt(variance / len(differences)), len(differences) - 1
                    unit = "paired distinct-prime blocks (all curves within fields)"
                    details = {"paired_difference_variance": variance}
                else:
                    s = np.array([row[metric] for f in selected if f["arm"] == "S" for row in f["curves"]], dtype=float)
                    c = np.array([np.mean([row[metric] for row in f["curves"]]) for f in selected if f["arm"] == arm])
                    if len(s) != 512 or len(c) != 144 or not np.all(np.isfinite(s)) or not np.all(np.isfinite(c)):
                        raise ValueError("incomplete or missing NIST metrics")
                    vs, vc = float(s.var(ddof=1)), float(c.var(ddof=1))
                    ss, sc = vs / len(s), vc / len(c)
                    se = math.sqrt(ss + sc)
                    df = (ss + sc) ** 2 / (ss * ss / (len(s) - 1) + sc * sc / (len(c) - 1))
                    unit = "S curve draws at fixed prime versus control-field means"
                    details = {"structured_variance": vs, "control_field_variance": vc}
                difference = float(s.mean() - c.mean())
                out.append({"case": case, "metric": metric, "control": arm, "structured_mean": float(s.mean()),
                            "control_mean": float(c.mean()), "difference": difference, "standard_error": se,
                            "degrees_of_freedom": df, "structured_units": len(s), "control_units": len(c),
                            "unit": unit, "nominal_99_percent_interval": interval(difference, se, df, 0.01),
                            "simultaneous_interval": interval(difference, se, df, config["familywise_alpha"] / config["primary_comparisons"]),
                            **details})
    if len(out) != config["primary_comparisons"]:
        raise ValueError("multiplicity mismatch")
    return out


def analyze(run):
    inputs = json.loads((run / "inputs.json").read_text())
    receipt = json.loads((run / "receipt.json").read_text())
    if receipt["status"] != "complete" or len(receipt["fields"]) != inputs["fields"]:
        raise ValueError("measurement incomplete")
    fields = [json.loads((run / "fields" / (row["field_id"] + ".json")).read_text()) for row in receipt["fields"]]
    comparisons = primary_comparisons(fields, inputs["config"])
    summaries = []
    for case in inputs["config"]["primary_cases"]:
        for arm in ["S", "R", "C"]:
            subset = [f for f in fields if f["case"] == case and f["arm"] == arm]
            curves = [row for f in subset for row in f["curves"]]
            row = {"case": case, "arm": arm, "fields": len(subset), "curves": len(curves),
                   "uniform_probes": sum(sum(r["uniform"]["proposal_counts"]) for r in curves),
                   "mean_probe_coverage": float(np.mean([r["uniform"]["coverage"] for r in curves])),
                   "mean_window_lag_1": float(np.mean([r["window_lag_1"] for r in curves])),
                   "mean_shuffled_window_lag_1": float(np.mean([r["shuffled_window"]["lag_correlations"]["1"] for r in curves])),
                   "mean_trace_square": float(np.mean([r["trace_square"] for r in curves])),
                   "mean_probe_bin_dispersion": float(np.mean([r["probe_bin_dispersion"] for r in curves]))}
            if "census" in curves[0]:
                row.update({"mean_exact_coverage": float(np.mean([r["census"]["coverage"] for r in curves])),
                            "mean_max_empty_run": float(np.mean([r["census"]["max_empty_run"] for r in curves])),
                            "total_affine_points": sum(r["N"] - 1 for r in curves)})
            companions = [f["isomorphic_companion"] for f in subset]
            row["mean_absolute_companion_lag_change"] = float(np.mean([abs(f["isomorphic_companion"]["window_lag_1"] - f["curves"][0]["window_lag_1"]) for f in subset]))
            row["companion_count"] = len(companions)
            summaries.append(row)
    result = {"schema": 1, "status": "measured_observations", "primary_comparisons": comparisons,
              "summaries": summaries, "interval_note": "Approximate paired Student/Welch intervals with a prespecified Bonferroni correction; nominal 99.9% simultaneous coverage across 24 comparisons. No exact coverage or power guarantee.",
              "simultaneous_intervals_excluding_zero": [dict(case=r["case"], metric=r["metric"], control=r["control"]) for r in comparisons if r["simultaneous_interval"][0] > 0 or r["simultaneous_interval"][1] < 0],
              "whole_curve_counts": inputs["curves"], "fields": inputs["fields"],
              "total_raw_bytes": sum(r["raw_bytes"] for r in receipt["fields"]),
              "total_worker_cpu_seconds": receipt["total_worker_cpu_seconds"],
              "wall_seconds_this_launch": receipt["wall_seconds_this_launch"]}
    with (run / "analysis.json").open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    result = analyze(args.run)
    print(json.dumps({key: result[key] for key in ("whole_curve_counts", "fields", "simultaneous_intervals_excluding_zero", "total_raw_bytes", "wall_seconds_this_launch")}, indent=2))
