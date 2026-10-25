import json, math, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
sys.path.insert(0, ".")
from estimate import ncols
cal = json.load(open("calib.json"))
xs = [p["ncols"] for p in cal]
def fit(key):
    lx = [math.log(x) for x in xs]; ly = [math.log(p[key]) for p in cal]; n = len(lx)
    mx, my = sum(lx)/n, sum(ly)/n
    b = sum((a-mx)*(c-my) for a, c in zip(lx, ly))/sum((a-mx)**2 for a in lx)
    return b, math.exp(my-b*mx)
bt, at = fit("wall_s"); br, ar = fit("maxrss_mb")
grid = [5e4*1.15**i for i in range(0, 45)]
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for a, key, b, c, lab, f in [(ax[0], "wall_s", bt, at, "wall time (s, 1 core)", 1), (ax[1], "maxrss_mb", br, ar, "peak RSS (MB)", 1)]:
    a.loglog(xs, [p[key] for p in cal], "ko", label="measured (N=24,26,28; D=5)")
    a.loglog(grid, [c*g**b for g in grid], "b--", label=f"fit ~ ncols^{b:.2f} (derived)")
    for nm, N in [("C19 N=40", 40), ("C21 N=42", 42)]:
        a.axvline(ncols(N, 5), color="r", ls=":"); a.text(ncols(N, 5), c*ncols(N,5)**b*0.2, nm, rotation=90, fontsize=7)
    a.set_xlabel("columns, sum_{d<=5} C(N,d)"); a.set_ylabel(lab); a.legend(fontsize=7); a.grid(True, which="both", alpha=.3)
fig.suptitle("lfdclose2 degree-5 closure cost (saturating m=3 instances); extrapolation to C19 is 6x beyond data", fontsize=9)
fig.tight_layout(); fig.savefig("calibration.svg"); fig.savefig("calibration.png", dpi=150)
