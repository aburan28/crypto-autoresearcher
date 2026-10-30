"""Decision-report graph for DEC-20261018-3b4a32: per cell, the legacy
reproduction control and whether the repaired arm changed any S4-dependent
recorded output (vs the legacy rerun) and any frozen conclusion field (vs the
archive). Reads the seven validated runs' raw-result.json only.

    python3 chart.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RUNS = [("icinv-m4", "EXP-SEMAEV-93d5cc", "RUN-SEMAEV-9cab7b"), ("fib-004", "EXP-SEMAEV-93d5cc", "RUN-SEMAEV-3e69b6"),
        ("fib-005", "EXP-SEMAEV-93d5cc", "RUN-SEMAEV-4be606"), ("fib-decision", "EXP-SEMAEV-93d5cc", "RUN-SEMAEV-894e27"),
        ("mtic-007", "EXP-SEMAEV-93d5cc", "RUN-SEMAEV-2a8498"), ("mtic-008", "EXP-SEMAEV-93d5cc", "RUN-SEMAEV-fcd67c"),
        ("mtic-010b", "EXP-SEMAEV-6e9dcf", "RUN-SEMAEV-0e5876")]
INK, MUTED, SURF = "#1a1a19", "#6b6a63", "#fcfcfb"
YES, NO = "#eb6834", "#d9d8d2"


def strip(cell, s):
    """S4-dependent outputs per arm: timing medians excluded; for fib-decision the
    timing-derived rho_s and cost ratios are compared (A/A spread in the report)."""
    if cell in ("fib-004", "fib-005"):
        return {c: {k: v for k, v in d.items() if k not in ("median_cost_seconds",)} for c, d in s.items()}
    if cell == "fib-decision":
        return {"rho": {c: v.get("rho_s") for c, v in (s.get("per_curve_correlation") or {}).items()},
                "ratio": s.get("predictor_cost_ratios")}
    return s


rows, data = [], {}
for cell, exp, rid in RUNS:
    c = json.loads((REPO / f"experiments/{exp}/runs/{rid}/raw-result.json").read_text())["comparison"]
    out_changed = strip(cell, c["repaired"]) != strip(cell, c["legacy"])
    concl_changed = any(c["conclusion_changed_repaired_vs_archived"].values())
    data[cell] = {"run": rid, "ctrl_legacy_repro": c["ctrl_legacy_repro"]["pass"],
                  "s4_outputs_changed_vs_legacy": out_changed, "frozen_conclusion_field_changed_vs_archive": concl_changed}
    rows.append((cell, rid, c["ctrl_legacy_repro"]["pass"], out_changed, concl_changed))
(HERE / "plot-data.json").write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")

cols = ["legacy rerun = archive\n(CTRL-LEGACY-REPRO)", "S4-dependent outputs\nrepaired ≠ legacy", "frozen conclusion field\nrepaired ≠ archive"]
fig, ax = plt.subplots(figsize=(7.2, 3.3))
fig.patch.set_facecolor(SURF)
ax.set_facecolor(SURF)
for i, (cell, rid, a, b, c) in enumerate(rows):
    y = len(rows) - 1 - i
    for j, v in enumerate((a, b, c)):
        good = (j == 0)
        color = ("#2a78d6" if v else "#b23b3b") if good else (YES if v else NO)
        ax.add_patch(plt.Rectangle((j + 0.04, y + 0.08), 0.92, 0.84, color=color, linewidth=0))
        label = ("pass" if v else "FAIL") if good else ("yes" if v else "no")
        ax.text(j + 0.5, y + 0.5, label, ha="center", va="center", fontsize=8.5,
                color="white" if (good or v) else INK)
    ax.text(-0.08, y + 0.5, f"{cell}  {rid}", ha="right", va="center", fontsize=8, color=INK)
for j, t in enumerate(cols):
    ax.text(j + 0.5, len(rows) + 0.15, t, ha="center", va="bottom", fontsize=7.5, color=MUTED)
ax.set_xlim(-2.3, 3)
ax.set_ylim(0, len(rows) + 1.0)
ax.axis("off")
fig.tight_layout()
fig.savefig(HERE / "figure-cells.svg")
print(json.dumps(data, indent=1))
