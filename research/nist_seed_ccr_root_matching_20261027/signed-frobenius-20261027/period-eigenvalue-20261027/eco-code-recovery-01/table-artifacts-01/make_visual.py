"""Draw the newly established coefficient identity and the unknown historical I/O."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

P=Path(__file__).resolve().parent
plt.rcParams.update({'svg.fonttype':'none','font.size':10})
fig,ax=plt.subplots(figsize=(11,4.0))
ax.axis('off');ax.set_xlim(0,11);ax.set_ylim(0,4)
boxes=[
 (0.2,2.7,3.1,.85,'Le94 p78: ell=5','Printed integer coefficients','#e8f3ee',False),
 (4.0,2.7,3.1,.85,'Later ASCII meq5','All 14 coefficient entries match','#e8f3ee',False),
 (.2,.55,3.1,1.1,'May 1997 binary interfaces','libI: native int / unsigned long\nFreeLIP: native long / limb data\nGMP: separate raw codec','#e9f0fa',False),
 (4.0,.55,3.1,1.1,'Original files and build','Bytes, backend, ABI, visitation\nand error policy: UNKNOWN','#fff3dd',True),
 (7.8,.55,2.9,1.1,'Historical predictions','All 21: UNDETERMINED\n10 published / 11 omitted','#fff3dd',True),
]
for x,y,w,h,t,b,c,d in boxes:
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',facecolor=c,
              edgecolor='#43566a',linewidth=1.1,linestyle='--' if d else '-'))
 ax.text(x+w/2,y+h-.22,t,ha='center',va='center',fontweight='bold',fontsize=10)
 ax.text(x+w/2,y+.33,b,ha='center',va='center',fontsize=9,linespacing=1.4)
ax.annotate('',xy=(3.94,3.12),xytext=(3.36,3.12),
            arrowprops={'arrowstyle':'<->','color':'#2f8d78','lw':1.4})
ax.text(3.66,3.62,'exact identity',ha='center',fontsize=9,color='#2f8d78')
for a,b in [((3.36,1.1),(3.94,1.1)),((7.16,1.1),(7.74,1.1))]:
 ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','linestyle':'--','color':'#9d6b13','lw':1.3})
ax.text(5.65,2.1,'No demonstrated path from coefficient identity\nto an original curve rejection',ha='center',fontsize=10,color='#8b5e12')
fig.suptitle('A real compatibility dependency; original execution remains unknown',fontsize=13,fontweight='bold',y=.98)
fig.text(.5,.035,'T-5518 | COLLATION.json / SOURCE-REVIEW.json | source collation; zero native curve trials',
         ha='center',fontsize=9,color='#536477')
fig.tight_layout(rect=(0,.08,1,.94))
for ext in ['svg','png']:fig.savefig(P/('table-boundary.'+ext),dpi=160)
p=P/'table-boundary.svg';p.write_text('\n'.join(l.rstrip() for l in p.read_text().splitlines())+'\n')
print('Editable source boundary diagram rendered.')
