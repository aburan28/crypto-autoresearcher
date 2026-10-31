"""Draw the source boundary and retained audit coverage; no new curve trials."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

P = Path(__file__).resolve().parent
plt.rcParams.update({'font.size': 10, 'svg.fonttype': 'none'})
fig, ax = plt.subplots(figsize=(11, 3.7))
ax.set_xlim(0,11); ax.set_ylim(0,3.7); ax.axis('off')
boxes = [
    (0.1,2.1,3.1,1.1,'Le94: table precomputation','Input: auxiliary prime ell\nType1 / type2; integer coefficients','#e8f3ee',False),
    (3.9,2.1,3.1,1.1,'Saved coefficient tables','out... ASCII / libI binary\nReported coverage: primes ell < 800','#e8f3ee',False),
    (7.8,2.1,3.1,1.1,'Documented curve interface','Input: p and J = j(E)\nSubstitute J; reduce modulo p','#e8f3ee',False),
    (2.0,0.3,3.2,1.0,'Existing all 21 evidence','Later coefficient tables\n1,281 cells / 2,071 tested fibers','#e9f0fa',False),
    (6.1,0.3,3.7,1.0,'Original NIST/ANSI caller: unknown','Files, defaults, error policy, visitation\nNo historical selector identified','#fff3dd',True),
]
for x,y,w,h,t,b,c,dashed in boxes:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',facecolor=c,
                 edgecolor='#43566a',linestyle='--' if dashed else '-',linewidth=1.1))
    ax.text(x+w/2,y+h-0.25,t,ha='center',va='center',weight='bold',fontsize=10)
    ax.text(x+w/2,y+0.36,b,ha='center',va='center',fontsize=9,linespacing=1.5)
for i,(start,end) in enumerate([((3.25,2.65),(3.85,2.65)),((7.05,2.65),(7.75,2.65)),((8.7,2.0),(8.2,1.35))]):
    ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':'#43566a','lw':1.3,
                                                'linestyle':'--' if i==2 else '-'})
ax.annotate('',xy=(5.3,0.8),xytext=(6.05,0.8),
            arrowprops={'arrowstyle':'<->','color':'#9d6b13','lw':1.2,'linestyle':'--'})
ax.text(5.6,1.46,'not authenticated\nas original execution',ha='center',fontsize=8,color='#8b5e12')
fig.suptitle('The cube occurs in forward table construction; no input cube-root-of-j gate is documented',
             fontsize=12,weight='bold',y=0.99)
fig.text(.5,.02,'T-5518 | Le94 pp23-24,66,85-86,92,119-122 | dashed = historical-use gap',
         ha='center',fontsize=9,color='#536477')
fig.tight_layout(rect=(0,.07,1,.94))
for ext in ['svg','png']:fig.savefig(P/('source-boundary.'+ext),dpi=160)
plt.close(fig)

rows=list(csv.DictReader((P/'cohort-crosswalk.csv').open()))
streams=json.loads((P/'CROSSWALK.json').read_text())['streams']
labels={863711343:'239-bit ANSI',863966734:'192-bit ANSI',871002724:'P-521',
        871696354:'P-256',872952608:'P-384',891607927:'P-224'}
fig,ax=plt.subplots(figsize=(10,4.2))
for i,s in enumerate(streams):
    group=[r for r in rows if int(r['stream'])==s['stream']]
    n1=sum(int(r['type1_source_and_fricke_fibers']) for r in group)
    n2=sum(int(r['type2_fibers']) for r in group)
    ax.barh(i,n1,color='#366c9c',label='Type1 source / Fricke fibers' if i==0 else None)
    ax.barh(i,n2,left=n1,color='#2f8d78',label='Type2 fibers' if i==0 else None)
    ax.text(n1+n2+7,i,f'{n1+n2} fibers; {s["omitted"]} omitted / {s["published"]} published',va='center',fontsize=9)
ax.set_yticks(range(6),[labels[s['stream']] for s in streams])
ax.invert_yaxis()
ax.set_xlim(0,1100)
ax.set_xlabel('Number of retained tested fibers (exact count)')
ax.set_title('Retained coverage across all six streams: zero repeated-fiber triggers',weight='bold')
ax.spines[['top','right']].set_visible(False)
ax.legend(loc='lower right',frameon=False,fontsize=9)
fig.text(.5,.015,'CROSSWALK.json imports prior FIBER-AUDIT.json | later tables, rational parameters only | 0 new trials',
         ha='center',fontsize=9,color='#536477')
fig.tight_layout(rect=(0,.05,1,1))
for ext in ['svg','png']:fig.savefig(P/('retained-coverage.'+ext),dpi=160)
plt.close(fig)
# Avoid whitespace-only SVG lines in the review diff.
for p in P.glob('*.svg'):
    p.write_text('\n'.join(l.rstrip() for l in p.read_text().splitlines())+'\n')
print('Source diagram and retained-count chart rendered.')
