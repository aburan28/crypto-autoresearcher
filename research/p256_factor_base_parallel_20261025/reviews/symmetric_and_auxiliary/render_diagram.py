"""Exact algebraic counts from independently checked finite fixtures."""
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
N=[4,8,16];x=list(range(3));series=[([n**3 for n in N],'Original terminal length','#bb6050'),([math.comb(n,3) for n in N],'Distinct-divisor length','#32758c'),([math.comb(n+2,3) for n in N],'Full reduced union','#728c3b')]
plt.rcParams.update({'font.size':9,'svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(7.2,3.5))
for j,(values,label,color) in enumerate(series):
    bars=ax.bar([t+(j-1)*.23 for t in x],values,.22,label=label,color=color)
    for bar,v in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,v*1.15,str(v),ha='center',va='bottom',fontsize=8)
ax.set_xticks(x,[str(n) for n in N]);ax.set_xlabel('Scalar membership degree N (actual P-256 field)');ax.set_ylabel('Exact algebraic length / point count')
ax.set_yscale('log');ax.set_ylim(1,18000);ax.grid(axis='y',alpha=.15);ax.legend(loc='upper left',frameon=False)
ax.set_title('F1 checked representation sizes; no solver-runtime interpretation',fontsize=10)
fig.text(.5,.01,'TASK-20261025-1a83bb | cubic-independent.json; controls-and-depth.json | exact counts, no sampling uncertainty',ha='center',fontsize=7)
fig.tight_layout(rect=[0,.04,1,1])
fig.savefig(p/'coverage-diagram.svg');fig.savefig(p/'coverage-diagram.pdf');plt.close(fig)
