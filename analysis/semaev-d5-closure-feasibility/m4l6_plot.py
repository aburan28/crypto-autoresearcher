import textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
rows = [tuple(map(int, l.split())) for l in open("raw-20261026/c4.rss")]
t0 = rows[0][0]
t = [(r[0] - t0) / 60 for r in rows]; g = [r[1] / 1e6 for r in rows]
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.plot(t, g, "k.-", ms=3, label="resident memory, sampled every 20 s (recorded)")
ax.axhline(14.5, color="r", ls="--", label="address-space cap 14.5 GB (set by prlimit)")
ax.axhline(13.04, color="b", ls=":", label="triangular storage, full rank: columns^2/16 = 13.0 GB (derived)")
ax.axvline(1973 / 60, color="gray", ls="-.", label="allocation failure, 1,973 s (exit 134)")
ax.set_xlabel("minutes since first sample"); ax.set_ylabel("RSS (GB)"); ax.grid(alpha=.3); ax.legend(fontsize=7, loc="lower right")
ax.set_title("m=4, l=6, n=17 (N=58, 456,838 degree-4 columns), hky_par degree-4 closure, 4 threads", fontsize=8)
fig.tight_layout(); fig.savefig("m4l6-rss.svg"); fig.savefig("m4l6-rss.png", dpi=150)
txt = open("m4-l6-search-20261026.md").read()
with PdfPages("report-20261026.pdf") as pdf:
    lines = [w for l in txt.splitlines() for w in (textwrap.wrap(l, 118) or [""])]
    for s in range(0, len(lines), 62):
        f = plt.figure(figsize=(8.5, 11)); y = 0.97
        for w in lines[s:s + 62]:
            f.text(0.05, y, w, fontsize=6.6, family="monospace", va="top"); y -= 0.0153
        pdf.savefig(f); plt.close(f)
    f = plt.figure(figsize=(8.5, 5)); a = f.add_axes([0, 0, 1, 1]); a.axis("off"); a.imshow(mpimg.imread("m4l6-rss.png")); pdf.savefig(f); plt.close(f)
