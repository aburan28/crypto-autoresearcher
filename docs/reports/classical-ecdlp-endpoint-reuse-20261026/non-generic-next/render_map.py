from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/non-generic-proof-map-mpl')
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.use14corefonts']=True
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

out=Path(__file__).resolve().parent
fig,ax=plt.subplots(figsize=(10.3,3.1))
ax.set_xlim(0,10.3);ax.set_ylim(0,3.1);ax.axis('off')
def box(x,y,label,edge,face,style='solid'):
    ax.add_patch(FancyBboxPatch((x,y),3.1,.77,boxstyle='round,pad=.03',fc=face,ec=edge,lw=1.2,ls=style))
    ax.text(x+1.55,y+.385,label,ha='center',va='center',fontsize=9,color='#183041')
box(.12,1.83,'Cheap field square root\nroot equation + P anchor','#687b86','#eef1f3')
box(3.59,1.83,'Even negation covariance\ndoes not specify scalar order','#687b86','#eef1f3')
box(7.06,1.83,'Known-false control: F11\nanchored -f^3 fails at 3P','#9b4945','#f9eeee')
box(.12,.55,'Uniform ordered-root circuit\nconstructor UNSUPPLIED','#315f7b','#eef4f9','dashed')
box(3.59,.55,'Exact two-pulse antiderivative\nH(R+P) - H(R) = delta difference','#315f7b','#eef4f9')
box(7.06,.55,'Half bits of doubled targets\nrecover k, then verify kP = Q','#315f7b','#eef4f9')
for y in [2.22,.935]:
    for x in [3.28,6.75]:
        ax.annotate('',xy=(x+.24,y),xytext=(x,y),arrowprops={'arrowstyle':'->','lw':1.3,'color':'#315f7b'})
ax.text(5.15,2.91,'Order-sensitive root: separate existence, selection, and computational price',ha='center',fontsize=11.2,weight='bold')
ax.text(5.15,1.52,'The lower row is a conditional reduction, not an implemented solver.',ha='center',fontsize=8.8)
ax.text(5.15,.15,'Derived proof-search map, 2026-10-26. No trials or claimed exponent gain. Previous bounded L2/L6/L7-L8 results remain intact.',ha='center',fontsize=8)
fig.tight_layout(pad=.3)
fig.savefig(out/'proof-map.svg',bbox_inches='tight')
fig.savefig(out/'proof-map.pdf',bbox_inches='tight',metadata={'Title':'Ordered root constructor proof-search map','Author':'next_mechanism_selection'})
plt.close(fig)
