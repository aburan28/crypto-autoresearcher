from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/endpoint-review-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

out=Path(__file__).resolve().parent
fig,ax=plt.subplots(figsize=(10.3,2.5))
ax.set_xlim(0,10.3);ax.set_ylim(0,2.5);ax.axis('off')
nodes=[(.1,'Failed online DP\nD = Q + a P'),(2.65,'Pending (fp, a)\nnot a known log'),(5.2,'Verify x P = Q\nthen e = x + a mod r'),(7.75,'Known arena, cap C\nnext target: check x\' P = Q\'')]
for x,label in nodes:
    ax.add_patch(FancyBboxPatch((x,.9),2.4,1.05,boxstyle='round,pad=.03',fc='#edf3f8',ec='#315f7b',lw=1.2))
    ax.text(x+1.2,1.425,label,ha='center',va='center',fontsize=9,color='#123248')
for i in range(3):
    x=nodes[i][0]+2.4
    ax.annotate('',xy=(nodes[i+1][0]-.04,1.42),xytext=(x+.04,1.42),arrowprops={'arrowstyle':'->','lw':1.3,'color':'#315f7b'})
ax.text(5.15,2.3,'Endpoint recycling after public verification',ha='center',fontsize=12,weight='bold',color='#123248')
ax.text(5.15,.51,'Proposed finite study: same point-only walk; static C0, static C, adaptive C0-to-C; all costs charged.',ha='center',fontsize=8.8)
ax.text(5.15,.18,'Known precedent: Kuhn-Struik (SAC 2001, section 4). Prior repo studies: EXP-ECDLP-612fb1 and EXP-ECDLP-1de2ec.',ha='center',fontsize=8)
fig.tight_layout(pad=.3)
fig.savefig(out/'mechanism.svg',bbox_inches='tight')
fig.savefig(out/'mechanism.pdf',bbox_inches='tight',metadata={'Title':'Endpoint reuse source audit: proposed bounded admission flow','Author':'next_mechanism_selection'})
plt.close(fig)
