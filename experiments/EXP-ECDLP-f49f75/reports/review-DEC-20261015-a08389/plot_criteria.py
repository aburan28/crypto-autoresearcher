# Draws criteria-ratio.svg/png from criteria.json (written by plot_source_analyze.py). Run from the experiment dir.
import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D='reports/review-DEC-20261015-a08389'
c=json.load(open(f'{D}/criteria.json'))
fig,ax=plt.subplots(figsize=(8,3.6))
for solver,col,off in (("std","#c0392b",-0.18),("slimgb","#7d3c98",0.18)):
    r=c["jointly_completed"][solver]["ratio_A_over_B"]
    ks=list(r); ax.bar([i+off for i in range(len(ks))],[r[k] for k in ks],0.36,color=col,label=f"{solver}")
ax.axhline(1,color="black",lw=1); ax.text(len(ks)-0.5,1.15,"A = B (criterion threshold)",ha="right",fontsize=7)
ax.set_xticks(range(len(ks))); ax.set_xticklabels([k.replace("m","m=").replace("L",", L=") for k in ks],fontsize=7)
ax.set_yscale("log"); ax.set_ylabel("median time A / median time B\n(chain / dense same set)")
ax.set_title("EXP-ECDLP-f49f75: arm A faster than B in 0/8 cells (std) and 0/8 (slimgb)\n"
             "m=3: A retired at L=5; B and C completed L=5 (n=6 per cell; RUN-01/02/03)",fontsize=8)
ax.legend(fontsize=7); ax.grid(axis="y",alpha=.3); fig.tight_layout()
for e in ("svg","png"): fig.savefig(f"{D}/criteria-ratio.{e}",dpi=150)
