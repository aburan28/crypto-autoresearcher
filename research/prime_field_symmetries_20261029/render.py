"""Render committed/retained observations only; no scientific computation."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RUN=ROOT/'research/prime_field_c1_execution_20261029/runs/c1-fixed-panel-4f8ab9'
REPORT=ROOT/'research/prime_field_c1_execution_20261029/reports/c1-fixed-panel-4f8ab9'
REPORT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'svg.fonttype':'none','font.size':10})

def save(fig,path):
    fig.savefig(path)
    path.write_text('\n'.join(s.rstrip() for s in path.read_text().splitlines())+'\n')

catalog=json.loads((HERE/'catalog.json').read_text())
analysis=json.loads((RUN/'analysis.json').read_text())
triples=[row for row in analysis['cases'] if row['kind']=='triple']
summary=[]
for case in triples:
    path=RUN/'raw'/(case['case_id']+'.stages.jsonl')
    counters=Counter()
    for line in path.read_text().splitlines():
        row=json.loads(line)
        counters[row['phase']]+=row['cpu_ns']
    summary.append(dict(case_id=case['case_id'],cpu_ns_by_phase=dict(counters),
                        source_journal_sha256=sha256(path.read_bytes()).hexdigest()))
with (HERE/'stage-summary.json').open('x') as stream:
    json.dump(dict(schema='c1-derived-stage-summary/v1',cases=summary,
                   method='Sum recorded cpu_ns within each named phase; solver_total is inclusive, not added to inner phases.',
                   scope='Shared-host diagnostics only; no isolated timing or performance claim.'),stream,indent=2)
    stream.write('\n')

fig,axes=plt.subplots(1,2,figsize=(11,3.8),constrained_layout=True)
labels=['d3 positive','d3 generator','d4 positive','d4 generator']
bars=axes[0].bar(range(4),[row['signed_solutions'] for row in triples],color='#3f817a')
axes[0].bar_label(bars,padding=3)
axes[0].set_xticks(range(4),labels,rotation=20)
axes[0].set_ylim(0,1.35);axes[0].set_yticks([0,1])
axes[0].set_ylabel('Complete signed solutions (exact count)')
axes[0].set_title('Original fixed P-256 queries')
for offset,phase,label,color in [(-.19,'solver_total','Solver, inclusive','#467aab'),(.19,'finite_oracle','Separate finite oracle','#c18b49')]:
    values=[row['cpu_ns_by_phase'][phase]/1e9 for row in summary]
    bars=axes[1].bar([i+offset for i in range(4)],values,width=.38,label=label,color=color)
    axes[1].bar_label(bars,fmt='%.2f',fontsize=8,padding=2)
axes[1].set_xticks(range(4),labels,rotation=20)
axes[1].set_ylabel('Recorded process CPU seconds (diagnostic)')
axes[1].legend(fontsize=8)
axes[1].set_title('Shared host; wall_valid=false; no cost bound')
fig.suptitle('C1: one physical panel, four triple cases; exact oracle equality',fontsize=12)
save(fig,HERE/'native.svg')
(REPORT/'native.svg').write_bytes((HERE/'native.svg').read_bytes())
plt.close(fig)

fig,ax=plt.subplots(figsize=(8,3.2),constrained_layout=True)
curves=catalog['retained_bases']
for offset,key,label,color in [(-.18,'original_rank','Original rank','#467aab'),(.18,'rank_after','After negated old rows','#3f817a')]:
    values=[c[key] if key in c else c['negation_action_audit'][key] for c in curves]
    bars=ax.bar([i+offset for i in range(2)],values,width=.36,label=label,color=color)
    ax.bar_label(bars,padding=3)
ax.axhline(15,color='#777',ls='--',label='15 projected columns')
ax.set_xticks([0,1],['p=4099, a=2, b=13, r=4021','p=4099, a=2, b=16, r=4111'])
ax.set_ylim(0,17);ax.set_ylabel('Exact rank over subgroup field')
ax.legend(fontsize=8,loc='upper right')
ax.set_title('Retained RUN-ECDLP-967315 matrices; no new relation draws')
save(fig,HERE/'retained.svg');plt.close(fig)
print('Rendered native and retained figures; wrote derived stage summary.')
