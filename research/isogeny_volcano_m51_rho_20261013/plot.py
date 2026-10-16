#!/usr/bin/env python3
"""Plot the frozen m=51 volcano-level analysis outputs."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/m51-volcano-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/m51-volcano-xdg-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def short_label(contrast_id: str) -> str:
    return (
        contrast_id.replace("primary-", "")
        .replace("secondary-", "")
        .replace("diagnostic-", "")
        .replace("-vs-", " / ")
    )


def main() -> None:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--input-dir", type=Path, default=HERE)
    parser.add_argument("--output", type=Path, default=HERE / "volcano_level_contrasts.svg")
    args = parser.parse_args()

    contrast = rows(args.input_dir / "contrast_summary.csv")
    orbit = rows(args.input_dir / "orbit_summary.csv")
    orbit_arm = rows(args.input_dir / "orbit_arm_summary.csv")
    aa = rows(args.input_dir / "aa_summary.csv")
    analysis = json.loads((args.input_dir / "analysis.json").read_text())
    inference_available = analysis.get("status") == "VALID_FOR_SCOPED_INFERENCE"
    if not contrast or not orbit or not orbit_arm or not aa:
        raise ValueError("analysis tables are empty")
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")

    fig, axes = plt.subplots(3, 1, figsize=(11.0, 12.5), constrained_layout=True)

    ax = axes[0]
    labels = [short_label(row["contrast_id"]) for row in contrast]
    y = np.arange(len(contrast))
    points = np.asarray([float(row["observed_bits"]) for row in contrast])
    lows = np.asarray([float(row["family_ci_low"]) for row in contrast])
    highs = np.asarray([float(row["family_ci_high"]) for row in contrast])
    predicted = np.asarray([float(row["predicted_bits"]) for row in contrast])
    colors = [
        "#7b3294" if row["tier"] == "primary" else "#008837" if row["tier"] == "secondary" else "#666666"
        for row in contrast
    ]
    if inference_available:
        for point, low, high, yi, color in zip(points, lows, highs, y, colors):
            ax.errorbar(
                point,
                yi,
                xerr=np.asarray([[point - low], [high - point]]),
                fmt="none",
                ecolor=color,
                elinewidth=2.0,
                capsize=4,
                zorder=2,
            )
    ax.scatter(points, y, c=colors, s=45, label="measured")
    if inference_available:
        ax.scatter(predicted, y, marker="x", c="#d95f02", s=65, linewidths=2, label="random-map prediction")
    ax.axvline(0.0, color="black", linewidth=0.8)
    if inference_available:
        ax.axvspan(-0.1, 0.1, color="#7b3294", alpha=0.08, label="primary +/-0.10-bit band")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("log2 ratio of mean online walk group operations (bits)")
    ax.set_title(
        "m=51 crater/floor contrasts; 3,072 inferential paired blocks"
        if inference_available
        else "DESCRIPTIVE POINT ESTIMATES ONLY — A/A gate failed"
    )
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="best", fontsize=8)

    ax = axes[1]
    primary_id = "primary-floor-tau17-vs-crater-tau17"
    primary_orbits = [row for row in orbit if row["contrast_id"] == primary_id]
    primary_orbits.sort(key=lambda row: int(row["orbit_id"]))
    x = np.asarray([int(row["orbit_id"]) for row in primary_orbits])
    values = np.asarray([float(row["observed_bits"]) for row in primary_orbits])
    if inference_available:
        ax.axhspan(-0.1, 0.1, color="#7b3294", alpha=0.10)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.plot(x, values, marker="o", color="#7b3294", linewidth=1.4)
    ax.set_xticks(x)
    ax.set_xlabel("conductor-271 floor Frobenius orbit (exact representative)")
    ax.set_ylabel("floor-tau17 / crater-tau17 (bits)")
    ax.set_title(
        "Primary contrast by floor orbit; 192 blocks/orbit (descriptive/exploratory)"
    )
    ax.grid(alpha=0.25)

    ax = axes[2]
    aa_labels = [row["arm"] for row in aa]
    y = np.arange(len(aa))
    points = np.asarray([float(row["b_over_a_bits"]) for row in aa])
    lows = np.asarray([float(row["family_ci_low"]) for row in aa])
    highs = np.asarray([float(row["family_ci_high"]) for row in aa])
    passed = [row["pass"].lower() == "true" for row in aa]
    colors = ["#2166ac" if ok else "#b2182b" for ok in passed]
    for point, low, high, yi, color in zip(points, lows, highs, y, colors):
        ax.errorbar(
            point,
            yi,
            xerr=np.asarray([[point - low], [high - point]]),
            fmt="none",
            ecolor=color,
            elinewidth=2.0,
            capsize=4,
        )
    ax.scatter(points, y, c=colors, s=45)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.axvspan(-0.15, 0.15, color="#2166ac", alpha=0.10)
    ax.set_yticks(y, aa_labels)
    ax.invert_yaxis()
    ax.set_xlabel("independent-walk B/A log2 mean ratio (bits)")
    ax.set_title("A/A controls; 1,024 paired blocks, Bonferroni 99% intervals")
    ax.grid(axis="x", alpha=0.25)

    if inference_available:
        title = (
            "Same-action crater/floor model association and action-order diagnostics; m=51, r≈2^34\n"
            "Fixed sampled models/generator/hash implementation; not a causal conductor effect"
        )
        color = "black"
    else:
        title = (
            "A/A ALERT — inferential contrasts and prediction overlays withheld\n"
            "Raw descriptive point estimates shown only; inspect the A/A controls before interpretation"
        )
        color = "#b2182b"
    fig.suptitle(title, fontsize=13, color=color)
    fig.text(
        0.5,
        0.003,
        "Fixed-orbit bootstrap: primary/diagnostic 95%; four secondary contrasts 98.75%; "
        "A/A controls 99%. Orbit-resampling intervals are sensitivity analyses.",
        ha="center",
        va="bottom",
        fontsize=8,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, format="svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
