# Draws ratios.svg/png from summary.json (recorded medians). Run from experiments/EXP-ECDLP-502ae2.
import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = "reports/review-DEC-20261015-ab6f23"
by = {(s["L"], s["arm"]): s for s in json.load(open(f"{D}/summary.json"))}
Ls = [3, 4, 5]
solve = [by[(L, "A")]["median_solve_ms"] / by[(L, "B")]["median_solve_ms"] if "median_solve_ms" in by[(L, "A")] else None for L in Ls]
gb = [by[(L, "A")]["median_gb_ms"] / by[(L, "B")]["median_gb_ms"] if "median_gb_ms" in by[(L, "A")] else 600000 / by[(L, "B")]["median_gb_ms"] for L in Ls]
fig, ax = plt.subplots(figsize=(7.5, 3.4))
x = range(len(Ls))
ax.bar([i - 0.2 for i in x], [v or 0 for v in solve], 0.38, color="#c0392b", label="full solve (-P 1)")
ax.bar([i + 0.2 for i in x], gb, 0.38, color="#7d3c98", label="basis only (-g 2)")
ax.text(2 + 0.2, gb[2] * 1.15, "lower bound:\nA timed out (600 s)", ha="center", fontsize=7)
ax.text(2 - 0.2, 1.3, "A timed out", ha="center", fontsize=7, rotation=90)
ax.axhline(1, color="black", lw=1)
ax.set_xticks(list(x)); ax.set_xticklabels([f"L={L}" for L in Ls])
ax.set_yscale("log"); ax.set_ylabel("median time A / median time B")
ax.set_title("EXP-ECDLP-502ae2 (msolve, m = 3): chain (A) vs dense same set (B), n = 6 per cell", fontsize=8.5)
ax.legend(fontsize=7, loc="upper left"); ax.grid(axis="y", alpha=.3); fig.tight_layout()
for e in ("svg", "png"): fig.savefig(f"{D}/ratios.{e}", dpi=150)
print([round(v, 1) if v else None for v in solve], [round(v, 1) for v in gb])
