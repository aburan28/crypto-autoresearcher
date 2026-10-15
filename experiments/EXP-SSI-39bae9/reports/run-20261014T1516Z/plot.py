import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
d=json.loads(Path(__file__).with_name("plot-data.json").read_text())
fig,ax=plt.subplots(figsize=(8,3.5))
width=0.75/len(d["series"])
for k,(name,values) in enumerate(d["series"].items()):
 ax.bar([i+k*width for i in range(len(values))],values,width=width,label=name)
ax.set_xticks([i+width*(len(d["series"])-1)/2 for i in range(len(d["labels"]))],d["labels"])
ax.set_ylabel(d["y_label"])
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(Path(__file__).with_name("observations.svg"))
