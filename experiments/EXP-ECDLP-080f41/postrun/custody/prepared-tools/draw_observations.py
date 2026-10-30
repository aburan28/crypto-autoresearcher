#!/usr/bin/env python3
"""Render recorded source-analysis fractions only; no fitting or resampling."""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--svg',type=Path,required=True);a=p.parse_args();d=json.loads(a.data.read_text());rows=d.get('per_curve_six_cell')
import matplotlib
matplotlib.use('Agg');matplotlib.rcParams['svg.hashsalt']='RUN-ECDLP-939237-native-observations-v1'
import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(12,4.6));cells=['t0.e0','t0.e2','t1.e0','t1.e2','t2.e0','t2.e2'];markers=['o','s','^','D','v','P']
for ax,stage in zip(axes,['confirmation-A','confirmation-B']):
 selected=[] if rows is None else [r for r in rows if r.get('stage')==stage];curves=sorted({r['curve_id'] for r in selected});lookup={v:i for i,v in enumerate(curves)}
 for j,cell in enumerate(cells):
  retained=[r for r in selected if r['cell']==cell and r['attempts']>0]
  if retained:ax.scatter([lookup[r['curve_id']]+(j-2.5)*.035 for r in retained],[r['successes']/r['attempts'] for r in retained],s=24,marker=markers[j],label=cell,alpha=.8)
 if not selected:ax.text(.5,.5,'No retained source-analysis rows',ha='center',va='center',transform=ax.transAxes)
 ax.set(title=stage+'; shared traces within curve',xlabel='Retained curve index (labels in observations.json)',ylabel='Recorded success events / recorded attempts',ylim=(-.02,1.02));ax.grid(alpha=.2)
 if selected:ax.legend(fontsize=8,ncol=3)
fig.suptitle('RUN-ECDLP-939237 | source analysis '+d['source_analysis_kind']+' | host check '+str(d['host_verification_checked'])+' | descriptive only',fontsize=10);fig.tight_layout();fig.savefig(a.svg);plt.close(fig)
