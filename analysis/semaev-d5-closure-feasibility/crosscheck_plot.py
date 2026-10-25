import json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
a=json.load(open("calib.json")); b=json.load(open("calib_hky.json"))
x=[p["ncols"] for p in a]
fig,ax=plt.subplots(1,2,figsize=(10,4))
for i,(k,lab) in enumerate((("wall_s","wall time (s)"),("maxrss_mb","peak RSS (MB)"))):
    ax[i].loglog(x,[p[k] for p in a],"ko-",label="lfdclose2 (1 thread)")
    ax[i].loglog(x,[p[k] for p in b],"bs-",label="hky_par (4 threads)")
    ax[i].set_xlabel("columns, sum_{d<=5} C(N,d)  (N=24,26,28)"); ax[i].set_ylabel(lab); ax[i].grid(True,which="both",alpha=.3); ax[i].legend(fontsize=8)
fig.suptitle("Degree-5 closure, same satisfiable m=3 systems: recorded values only (calib.json, calib_hky.json)",fontsize=9)
fig.tight_layout(); fig.savefig("crosscheck.svg"); fig.savefig("crosscheck.png",dpi=150)
import textwrap, matplotlib.image as mpimg
txt=open("crosscheck-hky-par-20261020.md").read()
with PdfPages("report-20261020.pdf") as pdf:
    lines=[w for l in txt.splitlines() for w in (textwrap.wrap(l,118) or [""])]
    per=62
    for s in range(0,len(lines),per):
        f=plt.figure(figsize=(8.5,11)); y=0.97
        for w in lines[s:s+per]: f.text(0.05,y,w,fontsize=6.6,family="monospace",va="top"); y-=0.0153
        pdf.savefig(f); plt.close(f)
    f=plt.figure(figsize=(8.5,5)); a2=f.add_axes([0,0,1,1]); a2.axis("off"); a2.imshow(mpimg.imread("crosscheck.png")); pdf.savefig(f); plt.close(f)
