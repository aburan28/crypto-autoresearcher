#!/usr/bin/env python3
"""Derive presentation assets from frozen receipts; never launch an experiment."""
from pathlib import Path
import hashlib,json,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'research/pair_reuse_20260922'
R=ROOT/'experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9'
analysis=json.loads((R/'analysis.json').read_text())
rows=[json.loads(x) for x in (R/'benchmark_receipts.jsonl').read_text().splitlines()]
assert analysis['all384_complete_valid'] and len(rows)==384
out={'scope':'Derived presentation of frozen receipts; no fresh timing or experiment.','source_sha256':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['analysis.json','benchmark_receipts.jsonl']},'cells':[]}
for cell in analysis['cells']:
    item={'regime':cell['regime'],'M':cell['M'],'paired_ratio':cell['median_of_8_paired_ratios'],'bootstrap_95':cell['bootstrap_95'],'arms':{}}
    for arm in ('expanded','canonical_normal_x'):
        selected=[r for r in rows if r['regime']==cell['regime'] and r['M']==cell['M'] and r['arm']==arm]
        assert len(selected)==32
        stages={k:statistics.median(r['result']['stages'][k] for r in selected) for k in selected[0]['result']['stages']}
        residual=[r['wall_seconds']-sum(r['result']['stages'].values())-r['output_timing']['serialization_seconds']-r['output_timing']['result_write_seconds'] for r in selected]
        item['arms'][arm]={'jobs':32,'median_wall_seconds':statistics.median(r['wall_seconds'] for r in selected),'median_cpu_user_seconds':statistics.median(r['wait4']['user_seconds'] for r in selected),'median_cpu_system_seconds':statistics.median(r['wait4']['system_seconds'] for r in selected),'median_peak_rss_bytes':statistics.median(r['wait4']['peak_rss'] for r in selected),'logical_payload_bytes':selected[0]['result']['table']['logical_key_row_payload_bytes'],'median_stage_seconds':stages,'median_serialization_seconds':statistics.median(r['output_timing']['serialization_seconds'] for r in selected),'median_result_write_seconds':statistics.median(r['output_timing']['result_write_seconds'] for r in selected),'median_unattributed_process_seconds':statistics.median(residual),'unattributed_scope':'Per-job primary wall minus disjoint reported native stages and serialization/result-write; includes startup, timing-file output, cleanup/reaping and other unpartitioned work. Stage medians are not summed into a total.'}
    out['cells'].append(item)
out['measured_native_wall_sum_seconds']=sum(r['wall_seconds'] for r in rows)
out['parent_validation_sum_seconds']=sum(r['parent_validation_seconds'] for r in rows)
out['repeated_query_executions']=sum(r['M'] for r in rows)
(P/'cost_breakdown.json').write_text(json.dumps(out,indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(10.8,5.6),dpi=160)
ys=[6,5,4,2,1,0];labels=[]
for y,c in zip(ys,out['cells']):
    primary=c['regime']=='n23_k16' and c['M']==512
    color='#176b78' if c['regime']=='n19_k4' else '#6249a5'
    ratio=c['paired_ratio'];ci=c['bootstrap_95']
    ax.errorbar(ratio,y,xerr=[[ratio-ci['lower']],[ci['upper']-ratio]],fmt='*' if primary else 'o',markersize=13 if primary else 7,color=color,ecolor=color,capsize=4,elinewidth=1.6,zorder=3)
    labels.append(('N19 / 4 orbits' if c['regime']=='n19_k4' else 'N23 / 16 orbits')+f'   ·   M = {c["M"]}'+('  *' if primary else ''))
    ax.text(1.025,y,f'{ratio:.3f}  [{ci["lower"]:.3f}, {ci["upper"]:.3f}]',transform=ax.get_yaxis_transform(),va='center',fontsize=9)
ax.axvline(1,color='#59616a',linestyle='--',linewidth=1)
ax.set_yticks(ys,labels);ax.set_ylim(-.65,6.65);ax.set_xlim(.2,1.08)
ax.set_xticks([.25,.5,.75,1.0]);ax.set_xlabel('Complete-job wall-time ratio: canonical / expanded  (lower is faster)')
ax.grid(axis='x',color='#e5e9ed',linewidth=.8);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0,pad=10)
fig.suptitle('Does the compressed pair table still help when reused?',x=.025,ha='left',fontsize=15,fontweight='bold')
fig.text(.025,.91,'Eight fixed public panels × four fresh jobs per arm; one table construction per job.',fontsize=10,color='#424b55')
fig.text(.025,.045,'Intervals: frozen 95% panel bootstrap. * Preregistered primary cell; all other cells descriptive.',fontsize=9,color='#424b55')
fig.text(.025,.014,'RUN-KIC-ba86d9 · finite point-decomposition jobs · field degree and base size vary together.',fontsize=9,color='#424b55')
fig.subplots_adjust(left=.25,right=.72,top=.84,bottom=.16)
fig.savefig(P/'pair_reuse_ratios.png',dpi=180)
fig.savefig(P/'pair_reuse_ratios.svg')
print(json.dumps({'cells':len(out['cells']),'repeated_query_executions':out['repeated_query_executions'],'figure':str(P/'pair_reuse_ratios.png')}))
