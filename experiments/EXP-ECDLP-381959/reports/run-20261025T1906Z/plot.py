#!/usr/bin/env python3
"""Render the compiler-stopped attempt from retained metadata; no trial runs."""
from pathlib import Path
import os,json,datetime as dt,textwrap
HERE=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'.inspection/mpl'))
os.environ.setdefault('XDG_CACHE_HOME',str(HERE/'.inspection/cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

X=json.loads((HERE/'data/failed-attempt.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'pdf.use14corefonts':False,'svg.fonttype':'none','svg.hashsalt':'failed-ecdlp-9f18c9','axes.spines.top':False,'axes.spines.right':False})
STAMP=dt.datetime(2026,10,25,tzinfo=dt.timezone.utc)
META={'Title':'Compiler-stopped larger solver-validation attempt','Author':'Codex','CreationDate':STAMP,'ModDate':STAMP}
RUN='EXP-ECDLP-381959 / RUN-ECDLP-9f18c9'

def timeline():
    fig,ax=plt.subplots(figsize=(9,3.7),layout='constrained')
    start=dt.datetime.fromisoformat(X['started_at'])
    for y,j in enumerate(X['module_execution']):
        b=j['build'];a=(dt.datetime.fromisoformat(b['started_utc'])-start).total_seconds()
        ax.barh(y,b['wall_seconds'],left=a,height=.55,color='#bd5a44' if b['returncode'] else '#2a789a')
        if 'self_test'in j:
            a=(dt.datetime.fromisoformat(j['self_test']['started_utc'])-start).total_seconds()
            ax.plot(a,y,'|',color='#2f8353',markersize=14,markeredgewidth=2)
    ax.set_yticks(range(6),[j['name'] for j in X['module_execution']]);ax.invert_yaxis()
    ax.set_xlabel('Seconds since supervisor start (UTC19:06:32.953559)')
    ax.set_title('Recorded preparation stages; no measurement job dispatched',fontsize=12)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    ax.legend(handles=[Patch(color='#bd5a44',label='Build exit 1'),Patch(color='#2a789a',label='Build exit 0'),Line2D([0],[0],color='#2f8353',marker='|',ls='',markersize=12,label='269-check self-test exit 0')],fontsize=8,loc='lower right')
    ax.set_xlim(0,49);ax.grid(axis='x',alpha=.2)
    return fig

def page(title,subtitle,n):
    fig=plt.figure(figsize=(8.27,11.69));fig.text(.085,.95,title,fontsize=18,color='#214f62',weight='bold');fig.text(.085,.916,subtitle,fontsize=10,color='#555')
    fig.text(.085,.035,RUN+' | operational observations only',fontsize=7,color='#666');fig.text(.9,.035,f'{n}/2',ha='right',fontsize=8,color='#666')
    return fig

def para(fig,y,text,width=98,size=10):
    lines=textwrap.wrap(text,width=width)
    fig.text(.085,y,'\n'.join(lines),va='top',fontsize=size,linespacing=1.3)
    return y-len(lines)*.0165-.025

fig=timeline();fig.savefig(HERE/'execution.svg');p=HERE/'execution.svg';p.write_text('\n'.join(t.rstrip() for t in p.read_text().splitlines())+'\n');fig.savefig(HERE/'execution.pdf',metadata=META);plt.close(fig)
with PdfPages(HERE/'report.pdf',metadata=META) as pdf:
    f=page('Larger solver validation: stopped at build','The admitted run reached no confirmation measurements',1)
    y=.87
    y=para(f,y,'This is an observations-only report of an operational attempt. Three candidate builds failed the admitted warning policy. Three baseline builds and their fixed self-tests passed. The larger-cohort solver comparison did not start.')
    y=para(f,y,'Requested: 48 fresh curves, subgroup sizes 12/14/16/18 bits, and 768 public targets. Recorded solver observations: 0. Supervisor status: infrastructure_error; exit 2. The output checker and public-witness verification were not reached.')
    rows=[]
    for j in X['module_execution']:
        rows.append([j['name'],str(j['build']['returncode']),f"{j['build']['wall_seconds']:.6f}",f"{j['self_test']['wall_seconds']:.6f}" if 'self_test'in j else 'not run','not dispatched'])
    ax=f.add_axes([.085,.48,.83,.235]);ax.axis('off');tab=ax.table(cellText=rows,colLabels=['Module','Build exit','Build(s)','Self-test(s)','Measurement'],loc='upper left',cellLoc='left',colLoc='left',bbox=[0,0,1,1]);tab.auto_set_font_size(False);tab.set_fontsize(8.5)
    for (r,c),cell in tab.get_celld().items():
        cell.set_edgecolor('#dce4e8');cell.set_linewidth(.5)
        if r==0:cell.set_facecolor('#eaf0f3');cell.set_text_props(weight='bold')
    y=.44
    f.text(.085,y,'Exact compiler stop',fontsize=13,weight='bold',color='#214f62');y-=.035
    y=para(f,y,'The admitted command includes -Wshadow and -Werror. The compiler reports that the local b in decoder.hpp:311 shadows the local b at line 300, inside dec::self_test(). All three candidate builds emit the same stderr digest and exit 1.')
    y=para(f,y,'The driver dispatches its pool only if all six builds and self-tests succeed. Because only three modules were eligible, no measurement command was invoked. The aggregate records six incomplete modules; this is not six compilation failures.')
    y=para(f,y,'The baseline self-tests each report 269 development checks. These repeat the same fixed development suite; they are neither independent replications nor results from the 768-target confirmation cohort.')
    pdf.savefig(f);plt.close(f)
    f=page('Retained evidence and next action','No solver correctness or performance conclusion follows from this attempt',2)
    ax=f.add_axes([.16,.60,.75,.25])
    # Recreate the exact vector timeline on this report page.
    start=dt.datetime.fromisoformat(X['started_at'])
    for y,j in enumerate(X['module_execution']):
        b=j['build'];a=(dt.datetime.fromisoformat(b['started_utc'])-start).total_seconds();ax.barh(y,b['wall_seconds'],left=a,height=.55,color='#bd5a44' if b['returncode'] else '#2a789a')
        if 'self_test'in j:ax.plot((dt.datetime.fromisoformat(j['self_test']['started_utc'])-start).total_seconds(),y,'|',color='#2f8353',ms=10,mew=2)
    ax.set_yticks(range(6),[j['name'] for j in X['module_execution']],fontsize=8);ax.invert_yaxis();ax.set_xlim(0,49);ax.set_xlabel('Seconds since supervisor start',fontsize=9);ax.grid(axis='x',alpha=.2)
    f.text(.16,.55,'Red: build exit 1; blue: build exit 0; green ticks: self-test exit 0.',fontsize=8,color='#555')
    y=.50
    y=para(f,y,'The supervisor ran 19:06:32.953559-19:07:20.789667 UTC on 25 October 2026, taking 47.836108 seconds. These are preparation durations, not solver-comparison measurements.')
    y=para(f,y,'All 2,612 receipt-listed hashes match. There are 2,613 actual files including the receipt, versus 2,883 required paths. The 270 unstarted checker/verification artifacts remain absent. All 2,560 producer slots are empty: 0 rows.')
    y=para(f,y,'Raw publication: c395a3c6ae40c6647a16a4c1ec4b4541b0bb9a92. Source/claim: af72d170c751d4210eec09d6670af43cd4b2743d. Exact commands, stdout/stderr, digests and failure records remain sealed.',width=92,size=9.5)
    y=para(f,y,'Next: repair the self-test identifier in a new version, test the exact admitted flags, and obtain fresh admission. No confirmation solver outcomes exist to tune on. A later execution gets its own records and report.')
    y=para(f,y,'Correctness, candidate recovery, fallback dependence and baseline costs remain unanswered here. This same-session report reads no private labels and supplies no independent scientific review.')
    pdf.savefig(f);plt.close(f)
for p in HERE.glob('*.pdf'):assert p.stat().st_size<65536,(p,p.stat().st_size)
print(json.dumps({'pages':2,'pdf_bytes':(HERE/'report.pdf').stat().st_size,'timeline_pdf_bytes':(HERE/'execution.pdf').stat().st_size}))
