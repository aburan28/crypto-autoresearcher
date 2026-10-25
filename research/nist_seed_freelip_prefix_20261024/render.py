#!/usr/bin/env sage -python
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

here=Path(__file__).resolve().parent
run=here/"runs/prefix-v2"
data=json.loads((run/"results.json").read_text())
checked=json.loads((run/"verification.json").read_text())
assert checked["status"]=="passed" and checked["results_sha256"]==hashlib.sha256((run/"results.json").read_bytes()).hexdigest()
names=["prime192v1","prime239v1","prime239v2","prime239v3","prime192v2","prime192v3"]
routes=[(26,"direct",7),(26,"prob-p",7),(26,"prob-n",7),(26,"prime-p",8),(26,"prime-n",8),(26,"direct",0),(26,"direct",6),(26,"direct",8),(30,"direct",7)]
labels=["Discard\n7","ProbPrime\np, 7","ProbPrime\nn, 7","Prime\np, 8","Prime\nn, 8","Discard\n0","Discard\n6","Discard\n8","30-bit\ndiscard 7"]
cases={(c["name"],c["nbits"],c["mode"],c["rounds"]):c for c in data["cases"] if c["kind"]=="point"}
matrix=[[int(cases[(name,)+route]["gx_matches"]) for route in routes] for name in names]
fig,ax=plt.subplots(figsize=(10,4.6))
ax.imshow(matrix,cmap=ListedColormap(["#edf0f3","#2871a5"]),vmin=0,vmax=1,aspect="auto")
ax.set_xticks(range(9),labels,fontsize=9)
ax.set_yticks(range(6),names,fontsize=10)
for y,row in enumerate(matrix):
    for x,value in enumerate(row):ax.text(x,y,str(value),ha="center",va="center",color="white" if value else "#778391",fontsize=11)
ax.set_xticks([x-.5 for x in range(10)],minor=True);ax.set_yticks([y-.5 for y in range(7)],minor=True)
ax.grid(which="minor",color="white",linewidth=2);ax.tick_params(which="both",length=0)
ax.spines[:].set_visible(False)
fig.suptitle("Routine primality calls reproduce the seven-output prefix",fontsize=13,fontweight="bold",y=.98)
ax.set_title("Configured FreeLIP 1.0; 26-bit limbs unless marked. Cells compare the first point's x-coordinate with published Gx.",fontsize=9,pad=14)
fig.legend(handles=[Patch(facecolor="#2871a5",label="Published Gx matches"),Patch(facecolor="#edf0f3",label="No match")],loc="lower center",ncol=2,frameon=False,fontsize=9)
fig.subplots_adjust(left=.17,right=.99,top=.82,bottom=.22)
path=here/"point_matches.svg";fig.savefig(path)
path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
plt.close(fig)
