import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
x=json.loads((p/"summary.json").read_text());d=x["depths"];depth=[r["depth"]for r in d]
fig,axes=plt.subplots(1,2,figsize=(9.4,3.4),layout="constrained")
axes[0].plot(depth,[r["geometric_degree"]for r in d],"o--",label="geometric degree (specified)")
axes[0].plot(depth,[r["rational_kernel"]for r in d],"x-",label="rational kernel (recorded)")
axes[0].set(xlabel="auxiliary chain depth d",ylabel="points / degree",xticks=depth,title="Kernel admission")
axes[0].legend(fontsize=8)
axes[1].bar(depth,[r["empty_bases"]for r in d],label="empty target base",color="#a5acb8")
axes[1].bar(depth,[r["nonempty_bases"]for r in d],bottom=[r["empty_bases"]for r in d],label="nonempty target base",color="#2f789c")
axes[1].set(xlabel="auxiliary chain depth d",ylabel="finite fibers (derived record counts)",xticks=depth,title="Complete rational-fiber census")
axes[1].legend(fontsize=8)
fig.suptitle("RUN-IC-ffda66; one deterministic census; no sampling uncertainty recorded",fontsize=10)
fig.savefig(p/"measurements.svg")
