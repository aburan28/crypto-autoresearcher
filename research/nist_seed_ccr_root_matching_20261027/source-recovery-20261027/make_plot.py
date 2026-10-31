"""Plot exact retained counts; no new scientific trials."""
import csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
P=Path(__file__).resolve().parent
rows=list(csv.DictReader((P/'curve-summary.csv').open()))
plt.rcParams.update({'svg.fonttype':'none','font.size':9})
fig,ax=plt.subplots(figsize=(10,7.7));y=list(range(len(rows)))
colors=['#8b62ad' if r['label']=='omitted' else '#117d84' for r in rows]
ax.barh(y,[int(r['successful_parameters']) for r in rows],color=colors,height=.55)
ax.scatter([int(r['neighbor_checks']) for r in rows],y,marker='D',facecolors='none',edgecolors='#243243',s=30,zorder=3)
ax.set_yticks(y,[r['name'] for r in rows]);ax.invert_yaxis();ax.set_xlim(0,29);ax.set_xticks(range(0,30,5));ax.set_xlabel('Exact count per curve, one arithmetic width and one run')
ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
for k,r in enumerate(rows):ax.text(int(r['successful_parameters'])+.2,k+.1,r['successful_parameters'],fontsize=8)
ax.legend(handles=[Patch(color='#117d84',label='Published: successful parameters'),Patch(color='#8b62ad',label='Omitted: successful parameters'),Line2D([0],[0],marker='D',color='none',markeredgecolor='#243243',markerfacecolor='none',label='Candidate branch checks')],loc='lower right',fontsize=8)
ax.set_title('All 21 curves pass the reconstructed Atkin interface',loc='left',fontweight='bold',pad=15)
fig.text(.03,.012,'ATKIN-NATIVE-GETALL-01 / -02 | 299 parameters, 433 branch checks per width | exact finite census; no sampling interval',fontsize=8,color='#435169')
fig.tight_layout(rect=(0,.035,1,1));fig.savefig(P/'counts.svg');fig.savefig(P/'counts.png',dpi=190);plt.close(fig)
f=P/'counts.svg';f.write_text('\n'.join(line.rstrip() for line in f.read_text().splitlines())+'\n')
