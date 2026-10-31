"""Editable diagram source for TASK-20261027-8805a4 (derived, no native data)."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
here=Path(__file__).resolve().parent
fig, ax=plt.subplots(figsize=(9.6,3.1))
fig.patch.set_facecolor('#f8fafc'); ax.set_facecolor('#f8fafc')
ax.set(xlim=(0,10),ylim=(0,3.4)); ax.axis('off')
def box(x,y,w,h,label,color):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08',linewidth=1.4,edgecolor=color,facecolor='white'))
 ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=11,color='#152138',linespacing=1.5)
box(.35,1.45,4.05,1.35,'One group event per add entry\nG = popcount(k) + max(L - 1, 0)\nIncludes identity / inverse / double','#245ad1')
box(5.4,2.05,4.1,.8,'Scalar-nested group events S = G\nDiagnostic subset of G','#167b5e')
box(5.4,.85,4.1,.8,'Scheduled base-double calls D = max(L - 1, 0)\nDiagnostic subset of S','#167b5e')
for y in (2.45,1.25):
 ax.annotate('',xy=(5.3,y),xytext=(4.55,2.1),arrowprops=dict(arrowstyle='->',color='#5a6577',lw=1.4))
ax.text(5,.35,'Charge G once. Do not charge G + S + D.',ha='center',fontsize=12,weight='bold',color='#9b2c2c')
ax.text(.3,3.13,'TASK-20261027-8805a4 | J-primitive-law | fixed public pseudocode',fontsize=11,color='#38465a')
fig.subplots_adjust(left=.01,right=.99,top=.99,bottom=.02)
fig.savefig(here/'diagram.svg'); fig.savefig(here/'diagram.pdf'); plt.close(fig)
