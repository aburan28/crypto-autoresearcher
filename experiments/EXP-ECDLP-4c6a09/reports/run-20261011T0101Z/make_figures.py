#!/usr/bin/env python3
"""Derived views of recorded G3 outputs; no new experiment or inference."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

SHAPES = ["P-192", "P-224", "P-256", "P-384"]
KINDS = ["solinas", "random_g", "tdc", "Q"]
NAMES = {"solinas": "Solinas", "random_g": "Random g", "tdc": r"$t^d-c$", "Q": r"$\mathbb{Q}$"}
COLORS = {"solinas": "#176b87", "random_g": "#db7c26", "tdc": "#8064a2", "Q": "#5d8a55"}

def identity(c):
    return {"seed": c["seed"], "field": c["field"], "curve": c["curve"], "curve_index": c["curve_index"]}

def draw_construction(out):
    fig, ax = plt.subplots(figsize=(10.2,4.1))
    ax.set(xlim=(0,10), ylim=(0,4))
    ax.axis("off")
    boxes = [(0.1,2.3,2.7,1.15,"Prime presentation\n$ p=f(m),\\quad m=2^k $", "#e8f2f6"),
             (3.4,2.3,2.9,1.15,"Number field\n$ K=\\mathbb{Q}(\\alpha),\\ f(\\alpha)=0 $", "#e8f2f6"),
             (6.9,2.3,2.9,1.15,"Exact points\n$ y^2=x^3+Ax+B $ in $K$", "#e8f2f6"),
             (6.9,.25,2.9,1.2,"Finite-field residues\n$ E(\\mathbb{F}_p) $\nCount distinct points $D(W)$", "#eaf3e6"),
             (0.1,.25,6.2,1.2,"Experiment: small x search → exact square test → reduction\nCompare Solinas / random g / t^d−c / rational points\nUnknown: efficient lifts of arbitrary targets\nand useful ECDLP relations", "#faf2df")]
    for x,y,w,h,t,c in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.025", facecolor=c, edgecolor="#58717b", linewidth=1))
        ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=12)
    for x1,y1,x2,y2 in [(2.85,2.87,3.34,2.87),(6.35,2.87,6.84,2.87),(8.35,2.25,8.35,1.53)]:
        ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=14,color="#456775"))
    ax.text(7.1,1.85,"α ↦ m mod p\n(good reduction)",ha="center",va="center",fontsize=12)
    ax.set_title("Derived algebraic construction and measured search; no ECDLP solver is asserted",fontsize=12,pad=8)
    fig.tight_layout()
    fig.savefig(out / "construction.svg")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    data = json.loads(a.raw.read_text())
    cells = data["cells"]
    a.out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "svg.fonttype": "none", "figure.dpi": 160})
    groups = {(s, k): [c for c in cells if c["field"]["shape"] == s and c["field"]["kind"] == k]
              for s in SHAPES for k in KINDS}
    stats = []
    for (s, k), group in groups.items():
        gs = [c["gamma"] for c in group if c["gamma"] is not None]
        ds = [c["rungs"][-1]["distinct_residues"] for c in group]
        ns = [c["new_nontorsion_points"] for c in group]
        hs = [c["min_new_point_log_height_over_log_p"] for c in group if c["min_new_point_log_height_over_log_p"] is not None]
        stats.append({"shape": s, "kind": k, "cells": len(group), "gamma_finite_n": len(gs),
                      "gamma_missing_n": len(group)-len(gs), "gamma_mean": float(np.mean(gs)) if gs else None,
                      "final_D_mean": float(np.mean(ds)) if ds else None, "final_D_range": [min(ds), max(ds)] if ds else None,
                      "reported_nontorsion_mean": float(np.mean(ns)) if ns else None,
                      "height_finite_n": len(hs), "height_mean": float(np.mean(hs)) if hs else None,
                      "final_shells_completed_histogram": dict(Counter(c["rungs"][-1]["shells_completed"] for c in group)),
                      "distinct_polynomials": len({tuple(c["field"]["g"]) for c in group}),
                      "distinct_finite_curves": len({(c["field"]["p"], c["curve"]["A"], c["curve"]["B"]) for c in group})})
    gammas = [c for c in cells if c["gamma"] is not None]
    nonq = [c for c in cells if c["field"]["d"] > 1]
    largest = max(gammas, key=lambda c: c["gamma"])
    smallest_rd = min(nonq, key=lambda c: c["field"].get("root_discriminant_field", c["field"]["root_discriminant"]))
    audit = {"arithmetic_on_recorded_data_only": True, "run_id": a.raw.parent.name,
             "raw_sha256": hashlib.sha256(a.raw.read_bytes()).hexdigest(), "cells": len(cells),
             "counts_by_seed": dict(Counter(c["seed"] for c in cells)), "groups": stats,
             "gamma_missing_total": sum(c["gamma"] is None for c in cells),
             "all_cells_reached_100000": all(c["rungs"][-1]["work"] == 100000 for c in cells),
             "all_cells_have_six_rungs": all(len(c["rungs"]) == 6 for c in cells),
             "rank_arm_labels": dict(Counter(c["rank_arm"] for c in cells)),
             "nonq_cells_without_pari_nfdisc": sum(c["field"]["nfdisc_pari"] is None for c in nonq),
             "regression_note": "Recorded pooled cell regression has no degree or shared-field adjustment; no causal interpretation is made.",
             "solinas_instances": sorted({(c["field"]["shape"], c["field"]["k"], c["field"]["p"], c["field"]["p_bits"]) for c in cells if c["field"]["kind"] == "solinas"}),
             "largest_gamma_cell": {**identity(largest), "gamma": largest["gamma"], "final_D": largest["rungs"][-1]["distinct_residues"]},
             "smallest_nonq_root_discriminant_cell": identity(smallest_rd),
             "recorded_summary": data["summary"]}
    (a.out / "derived-summary.json").write_text(json.dumps(audit, indent=2)+"\n")
    with (a.out / "cells.csv").open("w", newline="") as f:
        keys = ["seed", "kind", "shape", "g", "k", "p", "p_bits", "A", "B", "curve_index", "gamma", "final_D", "new_nontorsion_points", "height_over_log_p", "field_root_discriminant"]
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for c in cells:
            fld = c["field"]
            w.writerow({"seed": c["seed"], "kind": fld["kind"], "shape": fld["shape"], "g": json.dumps(fld["g"]),
                        "k": fld["k"], "p": fld["p"], "p_bits": fld["p_bits"], **c["curve"], "curve_index": c["curve_index"],
                        "gamma": c["gamma"], "final_D": c["rungs"][-1]["distinct_residues"], "new_nontorsion_points": c["new_nontorsion_points"],
                        "height_over_log_p": c["min_new_point_log_height_over_log_p"], "field_root_discriminant": fld.get("root_discriminant_field")})

    fig, axes = plt.subplots(2, 2, figsize=(8.4, 6.4), sharex=True)
    for ax, s in zip(axes.flat, SHAPES):
        for k in KINDS:
            group = groups[s, k]
            if not group:
                continue
            works = [r["work"] for r in group[0]["rungs"]]
            ys = np.array([[r["distinct_residues"] for r in c["rungs"]] for c in group], dtype=float)
            ax.plot(works, ys.mean(axis=0), color=COLORS[k], marker="o", markersize=3,
                    label=f"{NAMES[k]} (n={len(group)})")
            ax.fill_between(works, ys.min(axis=0), ys.max(axis=0), color=COLORS[k], alpha=.08)
        ax.set_title(s)
        ax.set_xscale("log")
        ax.set_yscale("symlog", linthresh=1)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Distinct residues D(W), points")
        ax.grid(alpha=.15)
        ax.legend(fontsize=9.5, loc="upper left")
    for ax in axes[1]:
        ax.set_xlabel("Candidate x attempts W")
    fig.suptitle("Observed coverage: mean across cells, including zero-point cells", fontsize=12)
    fig.text(.5, .015, f"Bands: observed min–max; no confidence interval. Source: {a.raw.parent.name}.\nCells share fields and curves.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0,.04,1,.96))
    fig.savefig(a.out / "coverage.svg")
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(8.4, 6.0), sharey=True)
    for ax, s in zip(axes.flat, SHAPES):
        labels = []
        for ix, k in enumerate(KINDS):
            group = groups[s, k]
            ys = np.array([c["gamma"] for c in group if c["gamma"] is not None])
            if len(ys):
                jitter = ((np.arange(len(ys))*0.61803398875)%1-.5)*.48
                ax.scatter(ix+jitter, ys, s=11, color=COLORS[k], alpha=.45, linewidths=0)
                ax.scatter([ix], [ys.mean()], s=95, color=COLORS[k], edgecolors="#222222", marker="D", zorder=4)
            labels.append(f"{NAMES[k]}\n{len(ys)}/{len(group)} fitted")
        ax.set_xticks(range(4), labels, fontsize=9.5)
        ax.set_title(s)
        ax.set_ylabel("γ (dimensionless)")
        ax.axhline(0, color="#777777", linewidth=.5)
        ax.grid(axis="y", alpha=.15)
    fig.suptitle("Recorded γ: individual cells and arithmetic mean (diamonds)", fontsize=12)
    fig.text(.5,.015, f"Missing slopes excluded from means and counted in labels; dots are not independent samples.\n{a.raw.parent.name}", ha="center", fontsize=8)
    fig.tight_layout(rect=(0,.04,1,.96))
    fig.savefig(a.out / "gamma.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4,4.5))
    for k in KINDS[:3]:
        cs = [c for c in nonq if c["field"]["kind"] == k and c["gamma"] is not None]
        xs = [c["field"].get("root_discriminant_field", c["field"]["root_discriminant"]) for c in cs]
        ys = [c["gamma"] for c in cs]
        ax.scatter(xs, ys, color=COLORS[k], s=17, alpha=.25, label=f"{NAMES[k]} (n={len(cs)})", linewidths=0)
    reg = data["summary"]["regression_gamma_vs_log_root_discriminant"]
    if reg:
        ax.set_title(f"Recorded regression slope: {reg['slope']:.4f}; 99% bootstrap interval [{reg['ci99'][0]:.4f}, {reg['ci99'][1]:.4f}]")
    ax.set_xscale("log")
    ax.set_xlabel("Field root discriminant |disc(K)|^(1/degree), dimensionless (log axis)")
    ax.set_ylabel("Recorded finite-search γ, dimensionless")
    ax.legend()
    ax.grid(alpha=.15)
    fig.text(.5,.015, "Interval copied from runner; its cell bootstrap does not account for shared fields/curves.\nNo new interval estimated.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1))
    fig.savefig(a.out / "discriminant.svg")
    plt.close(fig)

    draw_construction(a.out)
    print(json.dumps({"cells":len(cells), "raw_sha256":audit["raw_sha256"], "out":str(a.out)}))

if __name__ == "__main__":
    main()
