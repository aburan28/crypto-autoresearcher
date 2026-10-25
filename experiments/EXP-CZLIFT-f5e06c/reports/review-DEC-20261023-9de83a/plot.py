#!/usr/bin/env python3
"""Decision-report graph for DEC-20261023-9de83a (EXP-CZLIFT-f5e06c, EV-CZLIFT-e9a7cf).

Reads plot_data.json from this directory and writes graph.svg to it.

Panel A: one-sided 95% Clopper-Pearson upper bounds on the per-row success
rate of non-canonical recovery, with 0 successes observed (RUN-CZLIFT-032a92,
RUN-CZLIFT-6447f0). Each bound is shown against the recorded mean 1/p and
against the p^-1/2 band of the tested primes.
Panel B: operating characteristic of the frozen "|z| <= 4 around 1/p" clause,
computed by the red team (RT-20261023-fbf42f).

Checks: the script recomputes mean 1/p from the recorded p lists and compares
it with the recorded reference, and recomputes 1 - 0.05^(1/n) and compares it
with the recorded bound. It exits non-zero on any mismatch, which catches a
transcription error. Mean p^-1/2 is reviewer-computed here, not a run output.

Run: python3 -I plot.py  (stdlib + matplotlib)
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REL_TOL = 1e-9
ARM_COLOR = {"anomalous": "#1f77b4", "torsion": "#2ca02c"}
SQRT_COLOR = "#d62728"


def load():
    with open(os.path.join(HERE, "plot_data.json"), encoding="utf-8") as fh:
        return json.load(fh)


def check(name, got, want):
    if abs(got - want) > REL_TOL * abs(want):
        sys.exit(f"CHECK FAILED {name}: computed {got!r} != recorded {want!r}")


def derive(data):
    out = []
    for cell in data["cells"]:
        ps = []
        for rid in cell["run_ids"]:
            ps.extend(data["p_values"][cell["arm"]][rid])
        mean_inv_p = sum(1.0 / p for p in ps) / len(ps)
        inv_sqrt = [p ** -0.5 for p in ps]
        recorded = cell["mean_inv_p_recorded"]
        if recorded is None:
            seeds = [c for c in data["cells"]
                     if c["arm"] == cell["arm"] and len(c["run_ids"]) == 1]
            recorded = sum(c["mean_inv_p_recorded"] for c in seeds) / len(seeds)
        check(cell["id"] + " mean 1/p", mean_inv_p, recorded)
        if cell["observed_successes"] != 0:
            sys.exit(f"{cell['id']}: bound formula assumes 0 successes")
        n = cell["n_rows"]
        check(cell["id"] + " cp95", 1.0 - 0.05 ** (1.0 / n), cell["cp95_upper"])
        out.append({
            "cell": cell,
            "n": n,
            "cp": cell["cp95_upper"],
            "mean_inv_p": mean_inv_p,
            "mean_inv_sqrt": sum(inv_sqrt) / len(inv_sqrt),
            "min_inv_sqrt": min(inv_sqrt),
            "max_inv_sqrt": max(inv_sqrt),
            "p_min": min(ps),
            "p_max": max(ps),
        })
    return out


def panel_a(ax, rows):
    base = 1e-5
    for x, r in enumerate(rows):
        color = ARM_COLOR[r["cell"]["arm"]]
        xb = x - 0.13
        ax.vlines(xb, base, r["cp"], color=color, lw=9, alpha=0.30)
        ax.plot([xb], [r["cp"]], marker="v", color=color, ms=9, ls="none")
        ax.annotate(f"{r['cp']:.2e}\nn = {r['n']}", (xb, r["cp"]),
                    textcoords="offset points", xytext=(0, 7),
                    ha="center", va="bottom", fontsize=7)
        ax.plot([xb], [r["mean_inv_p"]], marker="_", color="black", ms=20,
                mew=2.2, ls="none")
        xs = x + 0.15
        ax.vlines(xs, r["min_inv_sqrt"], r["max_inv_sqrt"], color=SQRT_COLOR, lw=2.2)
        ax.plot([xs], [r["mean_inv_sqrt"]], marker="o", color=SQRT_COLOR, ms=5,
                ls="none")
    ax.set_yscale("log")
    ax.set_ylim(base, 3e-1)
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_xticks(list(range(len(rows))))
    ax.set_xticklabels([r["cell"]["label"] for r in rows], fontsize=7.5)
    ax.set_ylabel("success probability per row (exact hit d)")
    ax.set_title("A. Non-canonical recovery: 0 successes; 95% upper bounds "
                 "vs 1/p and $p^{-1/2}$", fontsize=9.5)
    ax.grid(axis="y", which="major", alpha=0.3)
    handles = [
        Patch(color=ARM_COLOR["anomalous"], alpha=0.45,
              label="anomalous arm: 95% upper bound (rate lies below)"),
        Patch(color=ARM_COLOR["torsion"], alpha=0.45,
              label="torsion arm, each section: 95% upper bound"),
        Line2D([], [], color="black", marker="_", ms=14, mew=2, ls="none",
               label="mean 1/p over rows (recorded; the prediction)"),
        Line2D([], [], color=SQRT_COLOR, marker="o", ms=5, lw=2,
               label="$p^{-1/2}$ over tested primes (bar: range; dot: row mean)"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=7, framealpha=0.92)


def panel_b(ax, oc):
    labels = oc["rates"]
    xs = list(range(len(labels)))
    ax.axvspan(-0.4, 1.4, color="#999999", alpha=0.12, lw=0)
    ax.plot(xs, oc["P_success_criterion_met_both_seeds"], "o-", color="#1f77b4",
            label="frozen criterion met on both seeds")
    ax.plot(xs, oc["P_falsification_fires_both_seeds"], "s-", color="#d62728",
            label="falsification fires on both seeds")
    ax.plot(xs, oc["torsion_only_P_falsification_both_seeds"], "^--",
            color="#2ca02c", label="falsification from the torsion arm alone")
    ax.annotate("rate 0 and rate 1/p:\nthe clause passes with\nP = 1.000 and 0.900",
                (0.5, 0.93), textcoords="data", ha="center", va="top", fontsize=7)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7.5)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("true per-row success rate")
    ax.set_ylabel("probability (exact Poisson-binomial, red team)")
    ax.set_title("B. Power of the frozen |z| \u2264 4 clause (no power below ~20/p)",
                 fontsize=9.5)
    ax.grid(alpha=0.3)
    ax.legend(loc="center right", fontsize=7, framealpha=0.92)


def main():
    data = load()
    rows = derive(data)
    print("cell, n, cp95_upper, mean_1/p, cp/mean_1/p, p^-1/2 [min, row-mean, max], cp < min p^-1/2")
    for r in rows:
        print(f"{r['cell']['id']}, {r['n']}, {r['cp']:.4e}, {r['mean_inv_p']:.4e}, "
              f"{r['cp'] / r['mean_inv_p']:.1f}x, "
              f"[{r['min_inv_sqrt']:.4e}, {r['mean_inv_sqrt']:.4e}, {r['max_inv_sqrt']:.4e}], "
              f"{r['cp'] < r['min_inv_sqrt']}")
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(13.5, 5.6), gridspec_kw={"width_ratios": [1.45, 1.0]})
    panel_a(ax_a, rows)
    panel_b(ax_b, data["operating_characteristic"])
    fig.text(
        0.01, 0.01,
        "EXP-CZLIFT-f5e06c; runs RUN-CZLIFT-032a92 (seed 20261009) and RUN-CZLIFT-6447f0 "
        "(seed 20261010); EV-CZLIFT-e9a7cf; DEC-20261023-9de83a. Toy tier (p \u2264 97813 < 2^17). "
        "A: one-sided Clopper-Pearson 95% bounds, 0 successes, rows = (curve lift, section, (P, d)); "
        "torsion bounds are per section (sections share (P, d) draws). "
        "B: from reports/redteam-20261023/rt_power_and_design.json.",
        fontsize=6.8, ha="left", va="bottom", wrap=True)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    out = os.path.join(HERE, "graph.svg")
    fig.savefig(out, format="svg")
    print("wrote", out)


if __name__ == "__main__":
    main()
