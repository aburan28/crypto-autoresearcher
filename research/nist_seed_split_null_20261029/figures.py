"""Draws fig_null.svg and fig_sweep.svg from runs/*.json only (no new computation beyond the
exact null pmf, which is re-evaluated from analysis_lib for display)."""
import json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis_lib import primes, probs, load_rows
plt.rcParams.update({"font.size": 9, "svg.fonttype": "none", "font.family": "DejaVu Sans"})
RAW = sys.argv[1]
res = json.load(open("runs/results.json")); le = json.load(open("runs/lookelsewhere.json")); pm = json.load(open("runs/permute.json"))
rows = load_rows(RAW); ells = primes(3, 691)
OM, PU = "#d95f02", "#1b6ca8"
fig, axs = plt.subplots(2, 2, figsize=(7.2, 4.6), sharex=True)
names = {"192": "192-bit (prime192)", "224": "224-bit (P-224)", "239": "239-bit (prime239)", "256": "256-bit (P-256)"}
for ax, bits in zip(axs.flat, ["192", "224", "239", "256"]):
    p = next(r["p"] for r in rows if str(r["bits"]) == bits)
    f = [1.0]
    for l in ells:
        q = probs(p, l)[0]; g = [0.0] * (len(f) + 1)
        for k, v in enumerate(f): g[k] += v * (1 - q); g[k + 1] += v * q
        f = g
    ks = range(35, 86); ax.bar(ks, [f[k] for k in ks], color="#bbbbbb", width=0.9, label="prime-order null")
    cs = [(c["split"], c["label"], n) for n, c in res["curves"].items() if str(c["bits"]) == bits]
    for j, (k, lab, n) in enumerate(sorted(cs)):
        ax.plot([k], [f[k] + 0.006 + 0.007 * (sum(1 for kk, _, _ in cs if kk == k and _ <= n) - 1)], "v" if lab == "omitted" else "o",
                color=OM if lab == "omitted" else PU, ms=6)
        if n == "prime239v1": ax.annotate("prime239v1\n42 splits", (k, f[k] + 0.01), xytext=(k + 3, 0.05), fontsize=7, arrowprops=dict(arrowstyle="-", lw=0.6))
    m = res["fields"][bits]["prime_order"]; ax.set_title(f"{names[bits]}: null mean {m['mean']:.1f}, sd {m['sd']:.2f}", fontsize=8.5)
    ax.set_ylim(0, 0.085); ax.grid(axis="y", lw=0.3)
for ax in axs[1]: ax.set_xlabel("split primes 3 ≤ ℓ ≤ 691 (124 odd primes)")
for ax in axs[:, 0]: ax.set_ylabel("null probability")
axs[0, 0].plot([], [], "v", color=OM, label="omitted (11)"); axs[0, 0].plot([], [], "o", color=PU, label="published (8)")
axs[0, 0].legend(fontsize=7, loc="upper left", frameon=False)
fig.tight_layout(); fig.savefig("fig_null.svg")

g = le["grid"]; fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=True)
a1.step(g, [x / 25 for x in pm["observed"]], where="post", color="k", lw=1, label="all 25 pairs")
a1.step(g, [x / 20 for x in pm["leave_one_out"]["prime239v1"]], where="post", color="#7b3294", lw=0.9, ls="--", label="20 pairs without prime239v1")
for q, v in le["null_max_score_quantiles"].items():
    a1.axhline(v / 25, color="#999", lw=0.6, ls=":"); a1.text(52, v / 25 + 0.008, f"null max-over-grid {float(q):.2f} quantile (25 pairs)", fontsize=6.5)
a1.axvline(691, color="#c00", lw=0.6); a1.set_ylabel("fraction of pairs with\nomitted > published"); a1.set_ylim(0.5, 1.03)
a1.legend(fontsize=7, frameon=False, loc="lower left"); a1.set_xscale("log")
a1.set_title(f"Within-field pair score vs cutoff B (max 25 at B ∈ {le['argmax_B']}; look-elsewhere MC p = {le['p_max_over_grid_ge_obs_max']:.4f}, n={le['nrep']})", fontsize=8)
for i, (n, lab) in enumerate(zip(le["names"], le["labels"])):
    if lab != "published": continue
    a2.plot(g, le["mid_pct"][i], lw=1.4 if n == "prime239v1" else 0.8, color="#c00" if n == "prime239v1" else PU, alpha=1 if n == "prime239v1" else 0.6,
            label=n if n in ("prime239v1", "secp224r1") else None, ls="-" if n != "secp224r1" else "--")
a2.set_yscale("log"); a2.set_ylim(0.001, 100); a2.axvline(691, color="#c00", lw=0.6)
a2.set_ylabel("published curve mid-percentile (%)\nunder prime-order null"); a2.set_xlabel("cutoff B (odd primes 3 ≤ ℓ ≤ B), log scale")
a2.legend(fontsize=7, frameon=False); a2.grid(lw=0.3)
fig.tight_layout(); fig.savefig("fig_sweep.svg")

# Figure 3: frozen held-out test (runs/heldout.json)
ho = json.load(open("runs/heldout.json"))
fig, ax = plt.subplots(figsize=(7.2, 3.3))
fields = [192, 224, 239, 256, 384]; HO = "#7a7a7a"
for i, f in enumerate(fields):
    groups = [("held-out unpublished", [x for x in ho["heldout"] if x["bits"] == f and x["label"] == "heldout"], HO, "s", -0.22),
              ("named omitted", [x for x in ho["named19"] if x["bits"] == f and x["label"] == "omitted"], OM, "v", 0.0),
              ("published", [x for x in ho["named19"] if x["bits"] == f and x["label"] == "published"]
                            + [x for x in ho["heldout"] if x["bits"] == f and x["label"] == "published"], PU, "o", 0.22)]
    for lab, xs, c, m, dx in groups:
        ax.scatter([i + dx] * len(xs), [x["split"] for x in xs], c=c, marker=m, s=18, alpha=0.85, label=lab if i == 0 else None, zorder=3)
ax.set_xticks(range(len(fields))); ax.set_xticklabels([f"{f}-bit" for f in fields])
ax.set_ylabel("split primes 3 ≤ ℓ ≤ 691"); ax.grid(axis="y", lw=0.3)
pr = ho["primary"]
ax.set_title(f"Frozen held-out test: held-out > published in {pr['observed']:.3f} of {pr['pairs']} within-field pairs "
             f"(permutation p = {pr['perm_p_one_sided']:.2f}; does not replicate)", fontsize=8)
ax.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3); ax.set_ylim(40, 73)
fig.tight_layout(); fig.savefig("fig_heldout.svg")

# Typst renders SVG text with its own fonts; name the serif it already embeds so a
# report PDF does not carry a second font (keeps report.pdf under the 64 KiB data limit).
import pathlib
for name in ("fig_null.svg", "fig_sweep.svg", "fig_heldout.svg"):
    p = pathlib.Path(name); p.write_text(p.read_text().replace("font-family: 'DejaVu Sans'", "font-family: 'Libertinus Serif', 'DejaVu Sans'"))
