#!/usr/bin/env python3
"""Regenerate graph.svg for the DEC-20261023-2e7447 decision report (EXP-CZLIFT-1a3453).

Reads plot_data.json. Before plotting it cross-checks every copied value against the committed
sources and aborts on any mismatch:
  - experiments/EXP-CZLIFT-1a3453/runs/<run>/raw-result.json
    (raw.curves[index]: p, n, rows[r].coord/digit/max_power/threshold)
  - experiments/EXP-CZLIFT-1a3453/reports/redteam-20261023/rt_scope_output.json
    (records[*]: p, n, h, T, rho_min, blind)

Two panels, 72 records from RUN-CZLIFT-037e5f and RUN-CZLIFT-d37ca4:
  (A) For each record, the maximum statistic X over the 8 higher-digit rows (x1..x4, y1..y4) and over the
      2 digit-0 rows, plotted against n. Each record's frozen threshold T(p,n) = ln((p-1)n) + 12 is drawn
      as a tick, and the trivial bound X <= h = (n-1)/2 is a dashed line. The planted PTM-1 leak reaches
      X = 0.999h, which is on that line. Records with h <= T are blind.
  (B) The detection floor rho_min = sqrt(T/h) and the observed single-pair correlation
      tau_max = sqrt(X_max/h) of the higher digits, against n. rho = 1 is the blind boundary.
No fit and no extrapolation.

    python3 plot.py            # writes graph.svg next to this file
"""

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
EXP = HERE.parent.parent
RUN_COLOUR = {"RUN-CZLIFT-037e5f": "#2a78d6", "RUN-CZLIFT-d37ca4": "#eb6834"}
ARM_MARKER = {"cm_canonical": "o", "random_naive": "s"}
INK, MUTED, GRID, REF, SHADE = "#0b0b0b", "#52514e", "#e4e3df", "#8a8984", "#f1efe9"
HIGHER = [1, 2, 3, 4, 6, 7, 8, 9]
DIGIT0 = [0, 5]
TOL = 1e-12


def fail(msg: str) -> None:
    sys.exit(f"plot.py: cross-check failed: {msg}")


def cross_check(doc: dict) -> list:
    notes = []
    order = doc["row_order"]
    raws = {}
    for run in doc["run_ids"]:
        path = EXP / "runs" / run / "raw-result.json"
        if not path.exists():
            fail(f"missing {path}")
        raws[run] = json.loads(path.read_text())["raw"]["curves"]
    scope_path = EXP / "reports" / "redteam-20261023" / "rt_scope_output.json"
    if not scope_path.exists():
        fail(f"missing {scope_path}")
    scope = {(r["run"], r["index"]): r for r in json.loads(scope_path.read_text())["records"]}
    if len(doc["records"]) != 72:
        fail(f"expected 72 records, found {len(doc['records'])}")
    for rec in doc["records"]:
        key = (rec["run"], rec["index"])
        curve = raws[rec["run"]][rec["index"]]
        if (curve["p"], curve["n"]) != (rec["p"], rec["n"]):
            fail(f"{key}: p,n {rec['p']},{rec['n']} vs raw {curve['p']},{curve['n']}")
        if curve["arm"] != rec["arm"] or curve["label"] != rec["label"]:
            fail(f"{key}: arm/label differ from raw")
        rows = curve["rows"]
        if len(rows) != 10:
            fail(f"{key}: raw has {len(rows)} rows")
        for r, (tag, val) in enumerate(zip(order, rec["max_power"])):
            row = rows[r]
            if f"{row['coord']}{row['digit']}" != tag:
                fail(f"{key}: row {r} is {row['coord']}{row['digit']}, expected {tag}")
            if abs(row["max_power"] - val) > TOL * max(1.0, abs(val)):
                fail(f"{key} {tag}: max_power {val} vs raw {row['max_power']}")
            if abs(row["threshold"] - rec["T"]) > TOL * rec["T"]:
                fail(f"{key} {tag}: T {rec['T']} vs raw threshold {row['threshold']}")
        s = scope[key]
        for f in ("p", "n", "h", "blind"):
            if s[f] != rec[f]:
                fail(f"{key}: {f} {rec[f]} vs rt_scope {s[f]}")
        for f in ("T", "rho_min"):
            if abs(s[f] - rec[f]) > TOL * abs(s[f]):
                fail(f"{key}: {f} {rec[f]} vs rt_scope {s[f]}")
        if rec["blind"] != (rec["h"] <= rec["T"]):
            fail(f"{key}: blind flag inconsistent with h <= T")
    notes.append("cross-check passed: 720 max_power, 720 thresholds, 72 x (p, n, h, T, rho_min, blind)")
    return notes


def derived(rec: dict) -> dict:
    mp = rec["max_power"]
    hi = max(mp[i] for i in HIGHER)
    d0 = max(mp[i] for i in DIGIT0)
    return {"hi": hi, "d0": d0, "tau_hi": math.sqrt(hi / rec["h"])}


def main() -> None:
    doc = json.loads((HERE / "plot_data.json").read_text())
    for line in cross_check(doc):
        print(line)
    recs = doc["records"]
    for rec in recs:
        rec.update(derived(rec))
    power = [r for r in recs if not r["blind"]]
    blind = [r for r in recs if r["blind"]]
    excess = max(r["hi"] - r["T"] for r in recs)
    print(f"records {len(recs)}; power-bearing {len(power)}; blind {len(blind)}; "
          f"max higher-digit excess over T {excess:.3f}")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": "DEC-20261023-2e7447"})
    fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(8.4, 10.2), gridspec_kw={"hspace": 0.38})
    n_max_blind = max(r["n"] for r in blind)
    n_min_power = min(r["n"] for r in power)
    edge = 0.5 * (n_max_blind + n_min_power)

    # Panel A: statistic against n.
    ax_a.axvspan(9, edge, color=SHADE, zorder=0)
    ns = [10 + i for i in range(0, 620)]
    ax_a.plot(ns, [(n - 1) / 2 for n in ns], color=REF, linestyle="--", linewidth=1.1, zorder=1)
    for r in recs:
        col = RUN_COLOUR[r["run"]]
        mk = ARM_MARKER[r["arm"]]
        ax_a.plot([r["n"]], [r["T"]], marker="_", markersize=9, markeredgewidth=1.6, color=INK, zorder=2)
        face = col if not r["blind"] else "none"
        ax_a.plot([r["n"]], [r["hi"]], marker=mk, markersize=5.2, markerfacecolor=face, markeredgecolor=col,
                  linestyle="none", zorder=3)
        ax_a.plot([r["n"]], [r["d0"]], marker="x", markersize=4, color=MUTED, linestyle="none", zorder=2)
    ax_a.set_xscale("log")
    ax_a.set_yscale("log")
    ax_a.set_xlim(9, 700)
    ax_a.set_ylim(3, 400)
    ax_a.set_xlabel("prime subgroup order n (log scale)", color=INK)
    ax_a.set_ylabel("per-record maximum of X = |S|^2 / h (log scale)", color=INK)
    ax_a.set_title("(A) Maximum statistic per record vs threshold T(p,n) and trivial bound h = (n-1)/2",
                   loc="left", fontsize=9.5, color=INK)
    ax_a.text(10, 300, f"blind zone: h <= T on {len(blind)} records (n <= {n_max_blind})", fontsize=7.5,
              color=MUTED)
    ax_a.text(110, 32, "X <= h for every digit sequence;\nplanted PTM-1 floor(pk/n) reaches X = 0.999h\n"
              "(VAL-20261022-55676f: spikes 42/42 power-bearing, 0/30 blind)", fontsize=7, color=MUTED,
              va="bottom")
    handles = [
        plt.Line2D([], [], marker="o", color=RUN_COLOUR["RUN-CZLIFT-037e5f"], linestyle="none",
                   label="RUN-CZLIFT-037e5f (seed 20261009)"),
        plt.Line2D([], [], marker="o", color=RUN_COLOUR["RUN-CZLIFT-d37ca4"], linestyle="none",
                   label="RUN-CZLIFT-d37ca4 (seed 20261010)"),
        plt.Line2D([], [], marker="o", markerfacecolor="none", markeredgecolor=MUTED, linestyle="none",
                   label="circle CM-canonical, square random-naive; hollow = blind record"),
        plt.Line2D([], [], marker="x", color=MUTED, linestyle="none",
                   label="digit 0 (x0, y0): determines k up to sign, still white"),
        plt.Line2D([], [], marker="_", markersize=9, markeredgewidth=1.6, color=INK, linestyle="none",
                   label="threshold T = ln((p-1)n) + 12 for that record"),
        plt.Line2D([], [], color=REF, linestyle="--", label="trivial bound h = (n-1)/2"),
    ]
    ax_a.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 0.93), fontsize=7, frameon=False)

    # Panel B: detection floor rho_min and observed tau_max against n.
    ax_b.axvspan(9, edge, color=SHADE, zorder=0)
    ax_b.axhline(1.0, color=REF, linestyle="--", linewidth=1.1)
    for r in recs:
        col = RUN_COLOUR[r["run"]]
        mk = ARM_MARKER[r["arm"]]
        face = col if not r["blind"] else "none"
        ax_b.plot([r["n"]], [r["rho_min"]], marker=mk, markersize=5.2, markerfacecolor=face,
                  markeredgecolor=col, linestyle="none", zorder=3)
        ax_b.plot([r["n"]], [r["tau_hi"]], marker="v", markersize=3.6, color=MUTED, linestyle="none", zorder=2)
    med = doc["constants"]["rho_min_power_bearing"]["median"]
    lo = doc["constants"]["rho_min_power_bearing"]["min"]
    ax_b.set_xscale("log")
    ax_b.set_xlim(9, 700)
    ax_b.set_ylim(0, 2.1)
    ax_b.set_xlabel("prime subgroup order n (log scale)", color=INK)
    ax_b.set_ylabel("normalised single-pair correlation tau", color=INK)
    ax_b.set_title("(B) Detection floor rho_min = sqrt(T/h) per record, and observed tau_max = sqrt(X_max/h)",
                   loc="left", fontsize=9.5, color=INK)
    ax_b.text(52, 1.04, "rho_min >= 1 (h <= T): no correlation of any size can register", fontsize=7.5,
              color=MUTED)
    ax_b.text(120, 1.25, f"power-bearing records: {len(power)}; rho_min {lo:.2f}-"
              f"{max(r['rho_min'] for r in power):.2f}, median {med:.2f}\n"
              "covariant even x-digit leaks at n < 109: floor about 1.44 rho_min (RT-20261023-dcb217)",
              fontsize=7, color=MUTED)
    hb = [
        plt.Line2D([], [], marker="o", color=MUTED, linestyle="none",
                   label="rho_min (filled: power-bearing; hollow: blind); colour = run, shape = arm"),
        plt.Line2D([], [], marker="v", color=MUTED, linestyle="none",
                   label="observed tau_max, higher digits (below rho_min on every record)"),
        plt.Line2D([], [], color=REF, linestyle="--", label="rho = 1"),
    ]
    ax_b.legend(handles=hb, loc="upper right", fontsize=7, frameon=False)

    for ax in (ax_a, ax_b):
        ax.grid(which="major", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(MUTED)
        ax.tick_params(colors=MUTED)
    fig.suptitle("EXP-CZLIFT-1a3453: torsion-section digit spectrum, 72 records (2 runs x 36), "
                 "DEC-20261023-2e7447", x=0.02, ha="left", fontsize=10.5, color=INK)
    fig.text(0.02, 0.955, "Recorded values: max_power and threshold from raw-result.json; h, rho_min and blind from "
             "rt_scope_output.json. Toy tier: p <= 571, n <= 613, precision 5.", fontsize=7.5, color=MUTED,
             ha="left")
    fig.subplots_adjust(left=0.09, right=0.98, top=0.93, bottom=0.05)
    fig.savefig(HERE / "graph.svg", format="svg", metadata={"Date": None})
    print(f"wrote {HERE / 'graph.svg'}")


if __name__ == "__main__":
    main()
