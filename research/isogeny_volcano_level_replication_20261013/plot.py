#!/usr/bin/env python3
"""Render source-labelled per-level operation-count deltas from results.json."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


COLORS = {"m37": "#167c5a", "m41": "#5b4ab5"}


def fnum(value):
    return float(value) if value not in ("", None) else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path(__file__).with_name("results.json"))
    ap.add_argument("--contrasts", type=Path, default=Path(__file__).with_name("contrasts.csv"))
    ap.add_argument("--output-prefix", type=Path, default=Path(__file__).with_name("volcano-level-differences"))
    args = ap.parse_args()
    results = json.loads(args.results.read_text())
    with args.contrasts.open(newline="") as f:
        rows = list(csv.DictReader(f))
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.8), constrained_layout=False)
    fig.subplots_adjust(left=.14, right=.97, bottom=.16, top=.80, wspace=.32, hspace=.52)
    for row_i, study in enumerate(("m37", "m41")):
        cfg = results["studies"][study]
        levels = cfg["levels"]
        primary = [r for r in rows if r["study"] == study and r["kind"] == "primary_level_vs_crater_neg"]
        secondary = [r for r in rows if r["study"] == study and r["kind"] == "secondary_level_vs_crater_tau"]
        if len(primary) != 3 or len(secondary) != 4:
            raise ValueError(f"{study}: expected 3 primary and 4 secondary rows")
        for col_i, (subset, title, simultaneous) in enumerate(((primary, "Lower levels vs crater (negation only)", True),
                                                                (secondary, "Each level vs crater + native Frobenius", False))):
            ax = axes[row_i, col_i]
            ax.set_facecolor("#fcfcfb")
            ax.axvline(0, color="#77736e", lw=1)
            if simultaneous:
                ax.axvspan(math.log2(.97), math.log2(1.03), color="#eeeae3", zorder=0, label="±3% equivalence band")
            ys = list(range(len(subset)))
            for y, r in zip(ys, subset):
                value = float(r["log2_ratio"])
                lo = fnum(r["simultaneous95_bits_lo"] if simultaneous else r["pointwise95_bits_lo"])
                hi = fnum(r["simultaneous95_bits_hi"] if simultaneous else r["pointwise95_bits_hi"])
                ax.errorbar(value, y, xerr=[[value - lo], [hi - value]], fmt="o", color=COLORS[study],
                            ecolor=COLORS[study], capsize=3, lw=1.6, ms=6, zorder=3)
                level_key = r["numerator"]
                old_group = "vs_crater_neg" if simultaneous else "vs_crater_tau"
                old_key = "crater" if level_key == "crater_neg" else level_key
                old = results["archived_pilot_comparison"][study][old_group][old_key]["log2_ratio"]
                ax.plot(old, y, marker="D", mfc="none", mec="#44413e", ms=5, zorder=2)
            labels = [r["numerator"].replace("crater_neg", "crater") for r in subset]
            ax.set_yticks(ys, labels)
            ax.invert_yaxis()
            ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
            ax.set_xlabel("log₂ ratio of mean rho operations (bits)", fontsize=9)
            ax.grid(axis="x", color="#e5e2dd", lw=.8)
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.tick_params(axis="y", length=0)
            if simultaneous:
                ax.text(.99, .04, "filled: fresh + simultaneous 95% CI\nhollow diamond: archived pilot point (not pooled)",
                        transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#55514d")
            else:
                ax.text(.99, .04, "fresh pointwise 95% CI; archived pilot not pooled\nτ is a context arm, not a transported endpoint action",
                        transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#55514d")
        axes[row_i, 0].text(-.20, 1.10, f"GF(2^{cfg['m']})", transform=axes[row_i, 0].transAxes,
                            fontsize=12, fontweight="bold", color=COLORS[study])
    fig.suptitle("Measured differences at each isogeny-volcano level", x=.02, y=.965, ha="left",
                 fontsize=17, fontweight="bold")
    fig.text(.02, .915, "Fresh independent operation counts. Left: one Bonferroni family across all six lower-level contrasts. "
             "Right: native Frobenius-action context only.", fontsize=10, color="#514e4a")
    sources = "; ".join(f"{s} raw-tree {v['raw_tree_sha256'][:12]}…" for s, v in results["studies"].items())
    fig.text(.02, .075, "Interpretation: these measurements do not demonstrate an executable transfer, an end-to-end ECDLP speedup, or a weak curve.",
             fontsize=9, fontweight="bold", color="#7d3027")
    fig.text(.02, .035, f"Sources: {args.results.name}; {args.contrasts.name}; {sources}. Analysis seed "
             f"{results['analysis']['seed']}, B={results['analysis']['bootstrap_reps']:,}. SVG/PNG generated by {Path(__file__).name}.",
             fontsize=7.5, color="#66615c")
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    metadata = {"Title": "Measured differences at each isogeny-volcano level",
                "Description": results["interpretation_guardrail"]}
    fig.savefig(args.output_prefix.with_suffix(".svg"), facecolor="#fcfcfb", metadata=metadata)
    # PNG accepts a wider free-form metadata dictionary than SVG.
    fig.savefig(args.output_prefix.with_suffix(".png"), facecolor="#fcfcfb", dpi=180,
                metadata={"Title": metadata["Title"], "Description": metadata["Description"]})


if __name__ == "__main__":
    main()
