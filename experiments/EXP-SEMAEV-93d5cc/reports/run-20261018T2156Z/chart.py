"""Draw the EXP-SEMAEV-93d5cc run-report graphs from recorded values only.

    python3 chart.py   (run from this directory)

Reads each run's raw-result.json and arms.tar.gz (and the archived runs they
compare with), writes plot-data.json, and draws figure-icinv.svg and
figure-fib.svg. No value is computed beyond counts,
medians and ratios of recorded numbers.
"""
from __future__ import annotations

import json
import tarfile
from pathlib import Path

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RUNS = REPO / "experiments/EXP-SEMAEV-93d5cc/runs"
SUCC = REPO / "experiments/EXP-SEMAEV-88c46c/runs"
FIB = REPO / "experiments/EXP-FIB-001/runs"
INK, MUTED, GRID, SURF = "#1a1a19", "#6b6a63", "#e4e3dd", "#fcfcfb"
COL = {"archived": "#8a8984", "legacy": "#2a78d6", "repaired": "#eb6834"}
CELLS = [("icinv-m4", RUNS / "RUN-SEMAEV-9cab7b"), ("fib-004", RUNS / "RUN-SEMAEV-3e69b6"),
         ("fib-005", RUNS / "RUN-SEMAEV-4be606"), ("fib-decision", RUNS / "RUN-SEMAEV-894e27"),
         ("mtic-007", RUNS / "RUN-SEMAEV-2a8498"), ("mtic-008", RUNS / "RUN-SEMAEV-fcd67c"),
         ("mtic-010b", SUCC / "RUN-SEMAEV-980e8c")]
plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "svg.fonttype": "none"})


def member(run: Path, name: str):
    with tarfile.open(run / "arms.tar.gz") as t:
        return json.load(t.extractfile(name))


raw = {c: json.loads((r / "raw-result.json").read_text()) for c, r in CELLS if (r / "raw-result.json").exists()}
data = {"source_runs": {c: str(r.relative_to(REPO)) for c, r in CELLS}, "cells": {}}
for c, d in raw.items():
    cmp_ = d["comparison"]
    data["cells"][c] = {"ctrl_legacy_repro_pass": cmp_["ctrl_legacy_repro"]["pass"],
                        "conclusion_fields": cmp_["conclusion_fields"],
                        "changed_repaired_vs_archived": cmp_["conclusion_changed_repaired_vs_archived"],
                        "changed_repaired_vs_legacy": cmp_["conclusion_changed_repaired_vs_legacy"]}
# per-target FIB C16-1 Groebner seconds (recorded cost_seconds)
fib = {"archived": json.loads((FIB / "RUN-FIB-004/raw.json").read_text())}
for arm in ("legacy", "repaired"):
    fib[arm] = member(RUNS / "RUN-SEMAEV-3e69b6", f"arms/{arm}/runs/RUN-FIB-004/raw.json")
c16 = {k: [m["cost_seconds"] for m in v["per_curve"]["C16-1"]["measurements"]] for k, v in fib.items()}
c16_2 = {k: v["per_curve"]["C16-2"]["n_measured"] for k, v in fib.items()}
data["fib_c16_1_cost_seconds"] = c16
data["fib_c16_2_n_measured"] = c16_2
rho = {k: v["per_curve_correlation"]["C16-1"]["rho_s"] for k, v in
       ((s, raw["fib-decision"]["comparison"][s]) for s in ("archived", "legacy", "repaired"))}
data["fib_c16_1_rho_s"] = rho
icinv = {s: raw["icinv-m4"]["comparison"][s] for s in ("archived", "legacy", "repaired")}
data["icinv"] = icinv
(HERE / "plot-data.json").write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")

# ---- figure 1: ICINV m4 (two panels, one axis each)
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.6))
for ax, key, title in ((axes[0], "s4_support_counts", "S4 support (terms mod p)"),
                       (axes[1], "singular_locus_dim_degree_counts", "singular locus dim/degree")):
    vals = sorted({v for s in icinv.values() for st in ("control", "class") for v in s[f"{st}_{key}"]}, key=str)
    x = range(len(vals))
    w = 0.26
    for i, s in enumerate(("archived", "legacy", "repaired")):
        cnt = [icinv[s][f"control_{key}"].get(v, 0) + icinv[s][f"class_{key}"].get(v, 0) for v in vals]
        ax.bar([xi + (i - 1) * w for xi in x], cnt, w * 0.92, color=COL[s], label=s)
        for xi, n in zip(x, cnt):
            if n:
                ax.text(xi + (i - 1) * w, n + 8, str(n), ha="center", va="bottom", fontsize=6.5, color=INK,
                        rotation=90)
    ax.set_xticks(list(x), vals)
    ax.set_title(title, fontsize=9, color=INK, loc="left")
    ax.set_ylabel("records (of 552)")
    ax.set_ylim(0, 680)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
axes[0].legend(frameon=False, fontsize=7.5, loc="upper left")
fig.suptitle("RUN-SEMAEV-9cab7b vs RUN-ICINV-e0cd8f-m3class: m4 invariants, 276 curves x (base, gauge)",
             fontsize=8.5, color=MUTED, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(HERE / "figure-icinv.svg")
plt.close(fig)

# ---- figure 2: FIB C16-1 per-target cost (log) and rho_s against frozen bands
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={"width_ratios": [1.6, 1]})
ax = axes[0]
for i, s in enumerate(("archived", "legacy", "repaired")):
    ys = sorted(c16[s])
    ax.scatter([i + ((j * 37) % len(ys) / len(ys) - 0.5) * 0.5 for j in range(len(ys))], ys, s=10,
               color=COL[s], alpha=0.75, linewidths=0)
    med = ys[len(ys) // 2]
    ax.plot([i - 0.32, i + 0.32], [med, med], color=INK, linewidth=1.2)
    ax.text(i + 0.34, med, f"median {med:.3g} s", va="center", fontsize=7, color=INK)
ax.set_yscale("log")
ax.set_xticks([0, 1, 2], ["archived", "legacy rerun", "repaired rerun"])
ax.set_xlim(-0.5, 2.9)
ax.set_ylabel("Groebner seconds per target (log)")
ax.set_title("C16-1, n = 200 targets per arm, 20 s cap (none capped)", fontsize=9, color=INK, loc="left")
ax.grid(axis="y", color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
ax = axes[1]
for lo, hi, lab in ((-0.2, 0.2, "|rho| < 0.2 falsification band"), (-0.4, -0.2, "inconclusive band")):
    ax.axhspan(lo, hi, color=GRID, alpha=0.6 if lab.startswith("|") else 0.3, linewidth=0)
ax.axhline(-0.4, color=MUTED, linewidth=0.8, linestyle="--")
ax.text(2.45, -0.41, "gate -0.4", fontsize=7, color=MUTED, va="top", ha="right")
ax.axhline(0, color=MUTED, linewidth=0.5)
for i, s in enumerate(("archived", "legacy", "repaired")):
    ax.scatter([i], [rho[s]], s=36, color=COL[s], edgecolors=SURF, linewidths=1)
    ax.text(i, rho[s] + 0.03, f"{rho[s]:+.3f}", ha="center", fontsize=7, color=INK)
ax.set_xticks([0, 1, 2], ["archived", "legacy", "repaired"])
ax.set_ylim(-0.5, 0.25)
ax.set_xlim(-0.5, 2.5)
ax.set_ylabel("Spearman rho_s (n_R, cost)")
ax.set_title("C16-1 rho_s vs frozen bands", fontsize=9, color=INK, loc="left")
fig.suptitle("RUN-SEMAEV-3e69b6 / -894e27 vs RUN-FIB-004 / -006C", fontsize=8.5, color=MUTED, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(HERE / "figure-fib.svg")
plt.close(fig)
print(json.dumps({"rho": rho, "c16_2_n_measured": c16_2}, indent=1))
