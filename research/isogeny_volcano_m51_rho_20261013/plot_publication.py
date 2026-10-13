#!/usr/bin/env python3
"""Render the publication figure from the frozen m=51 analysis tables.

This is a presentation-only companion to the frozen ``plot.py``.  It does
not perform inference or change any recorded result.  The explicit layout
reserves a separate footer band so the bottom x-axis label and provenance
note cannot overlap.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/m51-volcano-publication-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/m51-volcano-publication-xdg-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
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
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=HERE / "volcano_level_contrasts",
        help="path without a suffix; .svg and .png are written",
    )
    args = parser.parse_args()

    contrast = read_rows(args.input_dir / "contrast_summary.csv")
    orbit = read_rows(args.input_dir / "orbit_summary.csv")
    aa = read_rows(args.input_dir / "aa_summary.csv")
    analysis = json.loads((args.input_dir / "analysis.json").read_text(encoding="utf-8"))
    if not contrast or not orbit or not aa:
        raise ValueError("analysis tables are empty")
    if analysis.get("status") != "VALID_FOR_SCOPED_INFERENCE":
        raise ValueError("publication figure requires VALID_FOR_SCOPED_INFERENCE")

    svg_path = args.output_prefix.with_suffix(".svg")
    png_path = args.output_prefix.with_suffix(".png")
    for output in (svg_path, png_path):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9.5,
            "legend.fontsize": 8,
            "svg.hashsalt": "isogeny-volcano-m51-rho-20261013",
        }
    )
    fig, axes = plt.subplots(3, 1, figsize=(11.0, 13.2))
    # Keep a dedicated bottom band for the provenance note.  In particular,
    # do not use constrained_layout, which placed the frozen plot's footer on
    # top of the bottom panel's x-axis label in some renderers.
    fig.subplots_adjust(left=0.245, right=0.975, top=0.895, bottom=0.095, hspace=0.62)

    ax = axes[0]
    labels = [short_label(row["contrast_id"]) for row in contrast]
    y = np.arange(len(contrast))
    points = np.asarray([float(row["observed_bits"]) for row in contrast])
    lows = np.asarray([float(row["family_ci_low"]) for row in contrast])
    highs = np.asarray([float(row["family_ci_high"]) for row in contrast])
    predicted = np.asarray([float(row["predicted_bits"]) for row in contrast])
    colors = [
        "#7b3294"
        if row["tier"] == "primary"
        else "#008837"
        if row["tier"] == "secondary"
        else "#555555"
        for row in contrast
    ]
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
    ax.scatter(points, y, c=colors, s=48, label="measured", zorder=3)
    ax.scatter(
        predicted,
        y,
        marker="x",
        c="#d95f02",
        s=68,
        linewidths=2,
        label="random-map prediction",
        zorder=4,
    )
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.axvspan(-0.1, 0.1, color="#7b3294", alpha=0.08, label="primary +/-0.10-bit band")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("log2 ratio of arithmetic mean online walk group operations (bits)")
    ax.set_title("A. Exact sampled-model contrasts; 3,072 paired inferential blocks")
    ax.grid(axis="x", alpha=0.25)
    # The lower-right quadrant is empty for the bottom three contrasts; keep
    # the legend there so it cannot cover the primary point or its interval.
    ax.legend(loc="lower right", ncol=1, frameon=False)

    ax = axes[1]
    primary_id = "primary-floor-tau17-vs-crater-tau17"
    primary_orbits = [row for row in orbit if row["contrast_id"] == primary_id]
    primary_orbits.sort(key=lambda row: int(row["orbit_id"]))
    x = np.asarray([int(row["orbit_id"]) for row in primary_orbits])
    values = np.asarray([float(row["observed_bits"]) for row in primary_orbits])
    ax.axhspan(-0.1, 0.1, color="#7b3294", alpha=0.10)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.plot(x, values, marker="o", color="#7b3294", linewidth=1.4)
    ax.set_xticks(x)
    ax.set_xlabel("conductor-271 floor Frobenius orbit (one fixed representative)")
    ax.set_ylabel("floor-tau17 / crater-tau17 (bits)")
    ax.set_title("B. Primary contrast by orbit; 192 blocks/orbit, descriptive only")
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
            zorder=2,
        )
    ax.scatter(points, y, c=colors, s=48, zorder=3)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.axvspan(-0.15, 0.15, color="#2166ac", alpha=0.10)
    ax.set_yticks(y, aa_labels)
    ax.invert_yaxis()
    ax.set_xlabel("independent-walk B/A log2 ratio of arithmetic means (bits)")
    ax.set_title("C. Held-out A/A controls; 1,024 paired blocks, Bonferroni 99% intervals")
    ax.grid(axis="x", alpha=0.25)

    fig.suptitle(
        "m=51 conductor-271 crater/floor collision-walk record\n"
        "Same-action association and action-order controls; not a causal conductor effect",
        fontsize=14,
    )
    fig.text(
        0.5,
        0.027,
        "Panel A: primary/diagnostic 95%; four secondary contrasts Bonferroni 98.75%. "
        "Panel B has no intervals. Panel C: Bonferroni 99%.",
        ha="center",
        va="bottom",
        fontsize=8,
    )
    fig.text(
        0.5,
        0.011,
        "Study isogeny-volcano-m51-rho-20261013 | raw records SHA-256 0f3099774d453053... | "
        "hierarchical orbit-resampling intervals are sensitivity analyses",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="#444444",
    )

    fig.savefig(svg_path, format="svg", metadata={"Date": None})
    # Matplotlib terminates many SVG path-data lines with a literal space.
    # Normalize those generated lines so the checked-in vector artifact also
    # passes repository whitespace validation; this is presentation-only.
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    fig.savefig(
        png_path,
        format="png",
        dpi=180,
        metadata={"Software": "matplotlib; source plot_publication.py"},
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
