#!/usr/bin/env python3
"""Render descriptive solver observations; no EC operation or experiment runs."""
from pathlib import Path
import os,json,datetime as dt,textwrap,math,statistics
HERE=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'.inspection/mpl'))
os.environ.setdefault('XDG_CACHE_HOME',str(HERE/'.inspection/cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import fitz
import shutil

D=HERE/'data'
def read(name):return json.loads((D/name).read_text())
def rows(name):
    idx=read(name+'-index.json');out=[]
    for item in idx['parts']:
        p=read(item['path']);out.extend(dict(zip(p['columns'],r)) for r in p['rows'])
    assert len(out)==idx['rows'];return out
S=read('summary.json');R=read('runtime.json');C=rows('per-curve-costs');P=rows('paired-curve-ratios');Q=rows('candidate-outcomes')
RUN=S['experiment_id']+' / '+S['run_id'];BITS=[12,14,16,18]
M=['rho_upstream_auto','rho_upstream_auto_aa','hybrid_xmod7_exact_b8_then_rho','bernstein_lange_precomp','bsgs_complete']
NAME={M[0]:'AutoRho',M[1]:'Rho A/A',M[2]:'Candidate + rho',M[3]:'Bernstein-Lange',M[4]:'BSGS'}
COLOR={M[0]:'#246c91',M[1]:'#7d8790',M[2]:'#b95a35',M[3]:'#6b8753',M[4]:'#805f9e'}
STAMP=dt.datetime(2026,10,25,tzinfo=dt.timezone.utc)
META={'Title':'Larger classical ECDLP solver validation and measured baseline costs','Author':'Codex','CreationDate':STAMP,'ModDate':STAMP}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,
 'pdf.fonttype':42,'pdf.use14corefonts':False,'svg.fonttype':'none','svg.hashsalt':'larger-solver-validation-report',
 'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,'grid.linewidth':.6})
FIG=HERE/'figures';FIG.mkdir(exist_ok=True)

def gs(fig,rect,n=2):
    left,bottom,right,top=rect;return fig.add_gridspec(1,n,left=left,bottom=bottom,right=right,top=top,wspace=.35)

def save(fig,name):
    fig.savefig(FIG/(name+'.svg'));p=FIG/(name+'.svg');p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
    fig.savefig(FIG/(name+'.pdf'),metadata=META)

def geom(v):return math.exp(statistics.fmean(math.log(x) for x in v)) if v else None
def num(x,d=3):return 'unresolved' if x is None else f'{x:.{d}g}'

def cpu_axes(fig,rect):
    grid=gs(fig,rect);axes=[fig.add_subplot(grid[0,i]) for i in range(2)]
    for ax,key,title in zip(axes,['cold_mean_cpu_s','amortized_cpu_s'],['Reconstructed mean cold target','Amortized over 16 targets/curve']):
        for j,method in enumerate([M[0],M[3],M[4],M[2]]):
            group=[r for r in C if r['panel']=='full' and r['method']==method]
            for bit in BITS:
                z=[r for r in group if r['bits']==bit and r[key]>0]
                offsets=np.linspace(-.035,.035,len(z)) if z else []
                ax.scatter([bit+(j-1.5)*.085+o for o in offsets],[r[key]*1000 for r in z],s=13,alpha=.6,color=COLOR[method])
            means=[geom([r[key] for r in group if r['bits']==b and r[key]>0]) for b in BITS]
            ax.plot(BITS,[x*1000 if x else np.nan for x in means],marker='o',ms=3,lw=1,color=COLOR[method],label=NAME[method])
        ax.set_yscale('log');ax.set_xticks(BITS);ax.set_xlabel('Prime subgroup order (bits)');ax.set_title(title,fontsize=9)
    axes[0].set_ylabel('Recorded CPU cost (ms, log scale)');axes[1].legend(fontsize=6.5,loc='best')
    return axes

def ratio_axes(fig,rect):
    grid=gs(fig,rect);axes=[fig.add_subplot(grid[0,i]) for i in range(2)]
    for ax,method,title in [(axes[0],M[2],'Hybrid / rho, full m16 batches'),(axes[1],M[1],'Rho A/A / rho, same deterministic work')]:
        ax.axhline(1,color='#444',lw=.8,ls='--')
        for bit in BITS:
            z=[r for r in P if r['panel']=='full' and r['method']==method and r['bits']==bit and r['complete_pair'] and r['consumed_cpu_ratio'] is not None]
            v=[r['consumed_cpu_ratio'] for r in z]
            ax.scatter([bit+x for x in np.linspace(-.11,.11,len(v))],v,color=COLOR[method],s=17,alpha=.65)
            if v:ax.errorbar(bit,geom(v),yerr=[[geom(v)-min(v)],[max(v)-geom(v)]],fmt='s',ms=4,color='#222',capsize=3,lw=.9)
        ax.set_xticks(BITS);ax.set_xlabel('Prime subgroup order (bits)');ax.set_title(title,fontsize=8.7);ax.set_yscale('log')
    axes[0].set_ylabel('Paired per-curve CPU ratio (log scale)')
    return axes

def stage_axes(fig,rect):
    grid=gs(fig,rect,n=1);ax=fig.add_subplot(grid[0,0]);z=[r for r in S['hybrid_stage_totals'] if r['bits'] is not None]
    setup=np.array([r['setup_cpu_s']/r['targets']*1000 for r in z]);prefix=np.array([r['prefix_cpu_s']/r['targets']*1000 for r in z]);fallback=np.array([r['fallback_cpu_s']/r['targets']*1000 for r in z])
    ax.bar(BITS,setup,width=.8,color='#628654',label='Required setup /16')
    ax.bar(BITS,prefix,bottom=setup,width=.8,color='#bd6442',label='Prefix/views/checks')
    ax.bar(BITS,fallback,bottom=setup+prefix,width=.8,color='#286c94',label='Rho fallback')
    ax.plot(BITS,[(r['setup_cpu_s']+r['outer_target_cpu_s'])/r['targets']*1000 for r in z],'k.',ms=7,label='Outer measured CPU')
    ax.set_xticks(BITS);ax.set_xlabel('Prime subgroup order (bits)');ax.set_ylabel('Mean CPU cost per target (ms)');ax.legend(fontsize=7,loc='best');return ax

def recovery_axes(fig,rect):
    grid=gs(fig,rect);a,b=[fig.add_subplot(grid[0,i]) for i in range(2)]
    z=[r for r in S['primary_recovery'] if r['panel']=='full' and r['bits'] is not None]
    a.bar(BITS,[r['candidate_only_hits'] for r in z],width=.85,color=COLOR[M[2]])
    for r in z:a.text(r['bits'],r['candidate_only_hits']+.4,f"{r['candidate_only_hits']}/{r['targets']}",ha='center',fontsize=8)
    a.set_xticks(BITS);a.set_xlabel('Prime subgroup order (bits)');a.set_ylabel('Checked candidate-only recoveries');a.set_ylim(0,max(2,max(r['candidate_only_hits'] for r in z)*1.3+1));a.set_title('Frozen x-mod-7 exact-prefix beam 8')
    for i,m in enumerate(M):
        z=next(r for r in S['complete_arms'] if r['method']==m);ok=z['statuses'].get('solved',0)
        b.barh(i,ok,color=COLOR[m]);b.text(max(ok,1),i,f" {ok}/{z['requested']}",va='center',fontsize=8)
    b.set_yticks(range(5),[NAME[m] for m in M],fontsize=8);b.invert_yaxis();b.set_xlim(0,900);b.set_xlabel('Returned checked answers');b.set_title('Complete arms; A/A is a repeat')
    return a,b

def timeline_axes(fig,rect):
    grid=gs(fig,rect,n=1);ax=fig.add_subplot(grid[0,0]);start=dt.datetime.fromisoformat(R['receipt_started_at'])
    for i,j in enumerate(R['module_execution']):
        for key,color in [('build','#afbbc1'),('self_test','#688c6f'),('measurement','#277494' if j['name'].startswith('candidate') else '#b86643')]:
            if key not in j:continue
            r=j[key];left=(dt.datetime.fromisoformat(r['started_utc'])-start).total_seconds()
            ax.barh(i,r['wall_seconds'],left=left,height=.5,color=color)
    ax.set_yticks(range(len(R['module_execution'])),[j['name'] for j in R['module_execution']],fontsize=8);ax.invert_yaxis();ax.set_xlabel('Seconds since supervisor start');return ax

def page(title,subtitle,n,total=6):
    f=plt.figure(figsize=(8.27,11.69));f.text(.085,.95,title,fontsize=17,color='#214f62',weight='bold');f.text(.085,.916,subtitle,fontsize=9.6,color='#555')
    f.text(.085,.035,RUN+' | descriptive observations',fontsize=7,color='#666');f.text(.91,.035,f'{n}/{total}',ha='right',fontsize=8,color='#666');return f

def para(f,y,text,width=98,size=9.5,gap=.021):
    lines=textwrap.wrap(text,width=width);f.text(.085,y,'\n'.join(lines),va='top',fontsize=size,linespacing=1.25)
    return y-len(lines)*.0155-gap

def tab(f,rect,headers,values,size=8):
    ax=f.add_axes(rect);ax.axis('off');t=ax.table(cellText=values,colLabels=headers,cellLoc='left',colLoc='left',bbox=[0,0,1,1]);t.auto_set_font_size(False);t.set_fontsize(size)
    for (r,c),cell in t.get_celld().items():
        cell.set_edgecolor('#dce5e8');cell.set_linewidth(.5)
        if r==0:cell.set_facecolor('#eaf1f3');cell.set_text_props(weight='bold')
    return t

def pair_summary(method,bits,panel='full'):
    return next(r for r in S['paired_cost_ratios'] if r['numerator']==method and r['bits']==bits and r['panel']==panel)

def bl_summary(method,bits,panel='full'):
    return next(r for r in S['additional_baseline_ratios'] if r['numerator']==method and r['bits']==bits and r['panel']==panel)

for name,fn in [('solver-recovery',recovery_axes),('cpu-costs',cpu_axes),('paired-ratios',ratio_axes),('hybrid-stages',stage_axes),('execution-timeline',timeline_axes)]:
    f=plt.figure(figsize=(10,3.7));fn(f,[.10,.17,.96,.88]);f.text(.10,.015,RUN,fontsize=7,color='#666');save(f,name);plt.close(f)

with PdfPages(HERE/'report.pdf',metadata=META) as pdf:
    f=page('Larger-cohort solver validation','Correctness, candidate-only recovery and matched baseline costs',1)
    y=para(f,.87,f"AutoRho, Bernstein-Lange and BSGS each returned checked answers for 768/768 targets. The candidate-then-rho solver also recovered all 768; the frozen prefix alone supplied {S['hybrid']['candidate_only_hits']}. This report separates working correctness and measured baseline cost from novelty.")
    pr=[r for r in S['primary_recovery'] if r['panel']=='full' and r['bits'] is not None]
    tab(f,[.085,.57,.83,.16],['Subgroup bits','Curves','Targets','Candidate hits','Hybrid solved'],[[r['bits'],12,r['targets'],r['candidate_only_hits'],r['hybrid_statuses'].get('solved',0)] for r in pr],8.5)
    tab(f,[.085,.30,.83,.21],['Arm','Solved','Failed','Censored','Invalid'],[[NAME[r['method']],r['statuses'].get('solved',0),r['statuses'].get('failed',0),r['statuses'].get('censored',0),r['statuses'].get('invalid',0)] for r in S['complete_arms']],8.2)
    y=para(f,.25,f"Each arm requests 768 targets. The primary bounded candidate supplies {S['hybrid']['candidate_only_hits']} answers; the hybrid invokes rho {S['hybrid']['fallback_invocations']} times. A complete hybrid answer via rho is not a candidate-only recovery. Rho A/A repeats the same solver and seed rather than adding a fifth independent algorithm.")
    y=para(f,y,f"The cohort has six curves per size/stratum cell. Full reuse is 16 targets per curve. The fixed 192-target core uses eight targets on 24 of these curves; its 576-target extension and full panel overlap. Curves are the replication units.")
    pdf.savefig(f);plt.close(f)
    f=page('CPU cost at the tested sizes','Required setup and target work; operation counters retained separately',2)
    cpu_axes(f,[.13,.51,.95,.86])
    y=para(f,.46,'Each dot is one curve; lines are equal-curve geometric means. Left: setup plus mean target CPU, reconstructed as a cold-use cost. Right: setup amortized over 16 targets. These are not independently rerun cold targets.',size=9)
    vals=[]
    for r in S['complete_arms']:
        vals.append([NAME[r['method']],f"{r['setup_cpu_seconds']:.6g}",f"{r['target_cpu_seconds']:.6g}",f"{(r['setup_cpu_seconds']+r['target_cpu_seconds'])/r['requested']*1000:.6g}"])
    tab(f,[.085,.20,.83,.17],['Arm','Setup CPU(s)','Online CPU(s)','Aggregate ms/target'],vals,8)
    y=para(f,.15,'The aggregate table divides summed measured setup plus target CPU by 768; it is not a mean of paired ratios. Shared curve/target validation, parsing, JSON, orchestration and final teardown are excluded from arm timers and reported separately. Full per-curve data retain all statuses.',size=9)
    pdf.savefig(f);plt.close(f)
    f=page('Matched paired costs and A/A','Every point is a curve; complete positive-time pairs only',3)
    ratio_axes(f,[.13,.55,.95,.85])
    vals=[]
    for bits in BITS:
        vals.append([bits,*[f"{num(pair_summary(m,bits)['geometric_mean'])} ({pair_summary(m,bits)['comparable_complete_curves']}/{pair_summary(m,bits)['requested_curves']})" for m in [M[2],M[3],M[4],M[1]]],*[f"{num(bl_summary(m,bits)['geometric_mean'])} ({bl_summary(m,bits)['comparable_complete_curves']}/{bl_summary(m,bits)['requested_curves']})" for m in [M[2],M[4]]]])
    tab(f,[.085,.31,.83,.16],['Bits','Hybrid/rho','BL/rho','BSGS/rho','A/A/rho','Hybrid/BL','BSGS/BL'],vals,7.2)
    y=para(f,.26,'Table entries are per-size geometric means with comparable/requested curve counts. Dots retain all valid curve ratios; squares and whiskers show the geometric mean and complete range, not confidence intervals. A/A uses identical seed, returned scalar and deterministic work.',size=9)
    y=para(f,y,f"A/A work/answer equality holds for {S['aa']['exact_seed_work_answer_pairs']} pairs. There are {len(S['aa']['unresolved_zero_cpu_cases'])} target pairs with unresolved zero timing. Censored or invalid pairs remain in the outcome counts; their successful-only ratios cannot establish a full-panel gain.",size=9)
    y=para(f,y,'The BL-referenced columns are additional descriptive arithmetic; the registered primary comparator remains rho. Ratios describe this revision, toy sizes and reuse regime. No bootstrap, p-value or asymptotic exponent fit was computed.',size=9)
    pdf.savefig(f);plt.close(f)
    f=page('Where the primary hybrid spends work','Prefix work, charged setup and exact-seeded rho fallback',4)
    stage_axes(f,[.14,.57,.94,.86])
    y=para(f,.52,'Bars show recorded stage CPU per target with setup amortized over 16; dots show the outer hybrid CPU envelope. Small differences reflect wrapper/timing boundaries. Views, inference and candidate checks are nested inside prefix CPU, not extra additive stages.',size=9)
    z=next(r for r in S['hybrid_stage_totals'] if r['bits'] is None)
    tab(f,[.085,.27,.83,.17],['Stage','Group adds','Field multiplies','Scalar calls','DP terms'],[[name,f"{z[key].get('group_additions',0):,}",f"{z[key].get('field_multiplications',0):,}",f"{z[key].get('scalar_multiplications',0):,}",f"{z[key].get('dp_multiply_add_terms',0):,}"] for name,key in [('Setup','setup_counters'),('Prefix','prefix_counters'),('Fallback','fallback_counters')]],7.8)
    y=para(f,.22,'Scalar multiplication invokes group operations, and powers/inversions invoke field multiplies. These call counts are not disjoint work units and must not be added. Full process CPU also captures the candidate DP/log/sort and upstream table/hash work omitted by the field-operation vector.',size=9)
    y=para(f,y,'Memory values are partial kernel/vector payloads and upstream byte estimates. Measured per-arm peak RSS is unavailable; the 12GiB operational limit is not measured memory consumption.',size=9)
    pdf.savefig(f);plt.close(f)
    f=page('Complete secondary confirmation matrix','Descriptive bounded-candidate outcomes; no post-hoc winner selection',5)
    z=[r for r in Q if r['panel']=='full' and r['bits'] is None and r['stratum'] is None]
    labels={'constant':'constant','x_hash_7':'x hash 7','x_mod_7':'x mod 7','power_residue_5':'fifth residue'}
    tab(f,[.085,.32,.83,.54],['Feature','Mode','Beam','Hits/cases','Checks','Sum B/r'],[[labels[r['feature']],r['mode'],r['beam'],f"{r['hits']}/{r['cases']}",r['checks'],f"{r['uniform_guess_expected_hits']:.4f}"] for r in z],8)
    y=para(f,.27,f"The secondary study has {S['rows']['kernels']} kernels, {S['rows']['secondary_targets']:,} target cases and {S['rows']['not_applicable']} structural NAs. The primary x-mod-7 exact beam 8 lists match their secondary counterparts. Counting both would duplicate the same candidate answers.",size=9)
    y=para(f,y,'B/r is an ideal-uniform guessing expectation for the constant control and only a candidate-budget reference for nonconstant features. Constant modes can duplicate guesses; reused targets/configurations are not independent curve observations.',size=9)
    y=para(f,y,'Training, heldout calibration, shared views and all other configurations remain charged study work. They are not silently added to or subtracted from the separately executed primary algorithm.',size=9)
    pdf.savefig(f);plt.close(f)
    f=page('Execution, custody and practical limits','Raw observations are published before this report',6)
    timeline_axes(f,[.17,.61,.95,.85])
    y=para(f,.56,'Gray: build; green: fixed self-test; blue/orange: measurement jobs. Up to three jobs run concurrently. These intervals describe execution and do not replace the paired per-arm CPU measurements.',size=9)
    y=para(f,y,f"The receipt reports {R['status']}. Hash checks cover {S['custody']['receipt_artifacts_hash_checked']} receipt artifacts, {S['custody']['producer_slots_checked']} producer slots, all six original byte streams and {S['custody']['verification_case_rows_aligned']} aligned independent verification cases. All recorded candidates/final answers were compared with separately coded Jacobian results.",size=9)
    y=para(f,y,'Public scalar labels and generation seeds were excluded from solver/checker inputs. This is source-enforced separation, not OS-isolated blindness. The source revision, source/input digests, exact commands and byte-level parts index are linked in HEADER.md and data/summary.json.',size=9)
    y=para(f,y,'The 48 curves cover four small subgroup-bit levels. The nested core overlaps the full panel; full versus core reuse must remain explicit. Observed CPU scaling and differences at these inputs do not establish an asymptotic exponent. Working correctness and incremental comparison are distinct from novelty and later independent review.',size=9)
    y=para(f,y,'Retained data identify the actual dominant stages, fallback dependence and table/reuse costs for the next implementation iteration. No mathematical direction is closed by this finite cohort.',size=9)
    pdf.savefig(f);plt.close(f)

for p in HERE.rglob('*.pdf'):
    if '.inspection'in p.parts:continue
    # Preserve every rendered page while compressing object/content storage.
    cache=HERE/'.inspection';cache.mkdir(exist_ok=True);temporary=cache/(p.stem+'-compact.pdf')
    original=fitz.open(p);original.save(temporary,garbage=4,deflate=True,use_objstms=1,compression_effort=100)
    compact=fitz.open(temporary);assert len(original)==len(compact)
    for a,b in zip(original,compact):assert a.get_pixmap(alpha=False).samples==b.get_pixmap(alpha=False).samples
    original.close();compact.close()
    if temporary.stat().st_size<p.stat().st_size:shutil.copyfile(temporary,p)
    assert p.stat().st_size<65536,(p,p.stat().st_size)
print(json.dumps({'report_pages':6,'report_bytes':(HERE/'report.pdf').stat().st_size,'figure_pdfs':len(list(FIG.glob('*.pdf')))}))
