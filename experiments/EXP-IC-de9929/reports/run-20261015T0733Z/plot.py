from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent;x=json.loads((p/"summary.json").read_text())
fig,axes=plt.subplots(1,2,figsize=(9.4,3.5),layout="constrained")
labels=["direct","transported","reused power"]
axes[0].bar(labels,[v["field_mul_calls"]for v in x["arms"]],color=["#2f789c","#638a55","#ab8044"])
axes[0].set(ylabel="field.mul API calls (recorded)",title="Cold pairing arms; shared admission extra",ylim=(0,25000))
for i,v in enumerate(x["arms"]):axes[0].text(i,v["field_mul_calls"]+350,str(v["field_mul_calls"]),ha="center",fontsize=8)
axes[1].bar(["relations","with anchor","columns"],[x["unanchored_rank"],x["anchored_rank"],x["columns"]],color=["#2f789c","#638a55","#a5acb8"])
axes[1].set(ylabel="matrix rank / column count",title="Recorded linear system over F11",ylim=(0,7))
fig.suptitle("RUN-IC-a784bc; one deterministic order-11 fixture; no sampling uncertainty recorded",fontsize=10)
fig.savefig(p/"measurements.svg")
