from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

root=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(11.2,6.3))
ax.set(xlim=(0,12),ylim=(0,7))
ax.axis('off')
ax.text(6,6.78,'Nine checked declarations; concrete bridges remain separate',ha='center',fontsize=14,weight='bold')
cols=[2,6,10]
titles=['Transport · 3 declarations','Range · 2 declarations','Rho · 4 declarations']
supplied=[
    'Finite subgroup; additive maps\nback(f(P)) = d·P\ngcd(|S|,d) = 1',
    'Additive map; base in range\nFor exclusion: target outside range',
    'Field collision; nonzero coefficient\nGroup case: prime p and\ninjective additive encoding']
proved=[
    'Injectivity and scalar equivalence\nActual Mathlib point specialization',
    'Generated subgroup in range\nOutside target excluded',
    'Ordinary and negated formulas\nEncoded group bridge\nZero-coefficient control']
missing=[
    'Concrete geometry and degree\nDual/reverse-map certificate\nSolver and charged execution cost',
    'Jacobians and base change\nActual base/target membership\nCardinality bound',
    'Generator-order encoding\nWalk, hash and C refinement\nComposite candidate handling']
def box(x,y,body,color):
    ax.add_patch(FancyBboxPatch((x-1.78,y-.57),3.56,1.14,boxstyle='round,pad=0.06',
        facecolor=color,edgecolor='#52606d',linewidth=1.1))
    ax.text(x,y,body,ha='center',va='center',linespacing=1.5)
for x,t,s,p,m in zip(cols,titles,supplied,proved,missing):
    ax.text(x,6.28,t,ha='center',weight='bold',fontsize=11)
    box(x,5.45,s,'#e8f0fb')
    box(x,3.65,p,'#e4f3e9')
    box(x,1.48,m,'#f1f1f1')
    ax.annotate('',xy=(x,4.27),xytext=(x,4.82),arrowprops={'arrowstyle':'->','color':'#207548','lw':1.8})
    ax.annotate('',xy=(x+1.45,4.82),xytext=(x+1.45,2.11),
        arrowprops={'arrowstyle':'->','color':'#777777','linestyle':(0,(4,4)),'lw':1.2})
ax.text(6,.42,'Green: kernel-checked implications under supplied facts. Gray: unproved concrete obligations.',ha='center',fontsize=10)
ax.text(6,.05,'TASK-20261018-63a7cc / J1 · Source-aware independent review · No performance or scientific-state claim',ha='center',fontsize=9,color='#444444')
fig.tight_layout(pad=.6)
for ext in ('svg','pdf','png'):
    fig.savefig(root/f'proof-boundaries.{ext}',dpi=160,bbox_inches='tight')
