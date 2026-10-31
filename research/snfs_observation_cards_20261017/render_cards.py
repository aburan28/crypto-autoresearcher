"""Render saved observation tables; no curve or solver runs."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
import pymupdf


folder = Path(__file__).resolve().parent
saved = json.loads((folder/'observations.json').read_text())
plt.rcParams.update({'font.size':10,'svg.hashsalt':'snfs-observation-cards-20261017'})

fig,axes=plt.subplots(1,3,figsize=(10,3.4),sharey=True)
colors={'rot':'#2368a0','hash':'#c76c19','size_random_prime':'#40833d'}
labels={'rot':'rotation points','hash':'hash points','size_random_prime':'size / other prime'}
for ax,m in zip(axes,(1,2,4)):
    for arm in colors:
        rows=[r for r in saved['rotation'] if r['m']==m and r['arm']==arm]
        yy=[100*r['point_density'] for r in rows]
        errors=[[100*(r['point_density']-r['point_density_min']) for r in rows],
                [100*(r['point_density_max']-r['point_density']) for r in rows]]
        ax.errorbar([r['c'] for r in rows],yy,yerr=errors,marker='o',ms=4,
                    lw=1,color=colors[arm],label=labels[arm])
    reference=[r for r in saved['rotation'] if r['m']==m and r['arm']=='rot']
    ax.plot([r['c'] for r in reference],[100*r['exact_x_density'] for r in reference],
            color='black',ls='--',lw=1,label='exact uniform-x reference')
    ax.set(xlabel='Bit length c',title=f'm = {m}',ylim=(-2,103),xticks=[13,19,31,61])
axes[0].set_ylabel('Subset density (%)')
handles,legendlabels=axes[0].get_legend_handles_labels()
fig.legend(handles,legendlabels,loc='lower center',ncol=2,fontsize=8)
fig.suptitle('Six saved seed/curve cells per (c,m); bars are cell min/max, not confidence intervals',fontsize=10)
fig.tight_layout(rect=(0,.16,1,.91));fig.savefig(folder/'rotation-density.svg');plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(9,3.6),sharey=True)
status_colors={'sat':'#347bb1','unsat':'#a7abb0','timeout':'#d18b2d'}
for ax,record in zip(axes,saved['e3_summary']):
    bottoms=[0,0,0]
    for status,color in status_colors.items():
        heights=[record[key].get(status,0) for key in ('raw_statuses','jet_statuses','geometry_statuses')]
        ax.bar(range(3),heights,bottom=bottoms,label=status,color=color)
        for i,(height,bottom) in enumerate(zip(heights,bottoms)):
            if height:ax.text(i,bottom+height/2,str(height),ha='center',va='center')
        bottoms=[a+b for a,b in zip(bottoms,heights)]
    ax.set(xticks=range(3),xticklabels=['raw','jet','geometry'],ylim=(0,10),
           title=f'Historical pencil degree d = {record["d"]}',ylabel='Saved target outcomes (count)')
handles,status_labels=axes[1].get_legend_handles_labels()
fig.legend(handles,status_labels,loc='lower center',ncol=3,fontsize=9)
fig.suptitle('Nine shared targets per panel; generic degree-2 attempts have a four-second wall cap',fontsize=10)
fig.tight_layout(rect=(0,.15,1,.90));fig.savefig(folder/'e3-outcomes.svg');plt.close(fig)

field=saved['field_lift_summary'];hist={int(k):v for k,v in field['multiplicity_histogram'].items()}
fig,ax=plt.subplots(figsize=(8,3.8));keys=list(hist)
ax.bar(range(len(keys)),[hist[k] for k in keys],color='#4c769d')
for i,k in enumerate(keys):ax.text(i,hist[k]*1.12,str(hist[k]),ha='center',fontsize=10)
ax.set(xticks=range(len(keys)),xticklabels=keys,yscale='log',ylim=(1,1500),
       xlabel='Rows per seed-inclusive algebraic key',ylabel='Number of keys (log scale)',
       title='1,395 saved rows; 966 seed-inclusive keys; original rows retained')
fig.tight_layout();fig.savefig(folder/'field-lift-multiplicity.svg');plt.close(fig)
for path in folder.glob('*.svg'):
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')

pages=[
    ('Rotation subsets: fixed m, changing density','rotation-density.svg',[
        'Observation cards, 2026-10-17. Recorded values and derived arithmetic for owner inspection; no official scientific conclusion. Sources and hashes: observations.json. Curve and solver programs were not rerun.',
        'At m=4, saved rotation point density is 38.264%, 46.407%, 50.561%, 68.119%, 89.292% for c=13,17,19,31,61. Hash/size densities stay near their nominal 6.25%. Each point entry aggregates six cells and 120,000 saved density draws. Bars show six-cell spread, not confidence intervals.',
        'Definition to inspect: rotmin accepts a representative if any cyclic rotation begins with m zero bits. At m=1 every allowed representative is accepted; all 30 saved m=1 rotation cells have sampled density 1.',
        'Exact integer reference: an m-state zero-run automaton counts cyclic words avoiding m zeros via trace(A_m^c). The accepted representative count is 2^c - trace(A_m^c), out of 2^c-1. The all-ones word is excluded; all-zero is accepted. All 27 small direct enumeration checks agree. At m=4 the exact x-densities are 38.103%, 46.589%, 50.388%, 68.134%, 89.464%.',
        'Domains remain separate: point sampling weights x by the curve equation and excludes y=0 and O. Uniform-x counts are not exact point-density predictions. The size arm uses other-prime curves. These are descriptive comparisons with no significance test.',
        'Next check proposed: measure integer and point membership separately; use consistent O/y=0 domains and a separate calibration sample to match control cardinalities to rotation. Keep the original nominal-density tables alongside any calibrated tables.',
        'Source: EXP-ECDLP-ad27ad / RUN-ECDLP-a5281a. Producer/checker exit codes 0; supervisor receipt remains invalid_output for legacy manifest format. No status is upgraded by these plots.',
    ]),
    ('E3: degree step and censored solver outcomes','e3-outcomes.svg',[
        'What stands out: both generic encodings finish all nine degree-1 targets; both time out on all nine degree-2 targets under the saved four-second wall cap. The geometry construction has explicit verified sections for six of those degree-2 targets.',
        'Every panel contains the same nine targets across methods, at p=101,257,1021: two fresh and one planted per prime. There are 18 unique targets and 36 generic attempts. Degree-2 geometry successes comprise three fresh and three planted cases; degree 1 has one fresh and three planted.',
        'The geometry program reads the same target rows and recovers pencil base points from the cubic. It searches a fixed catalog of line/conic classes. Literal sat/unsat statuses describe the relevant encoding/catalog, not unrestricted sections. All ten geometry sat records carry verification flags.',
        'The degree-step discontinuity is worth inspecting by phase. Timeout records do not identify whether coefficient construction, Groebner computation, conversion/root recovery or a combination consumed the cap. Raw uses 3d+1 unknowns and jet uses 2d+1, including saturation; both retain the degree-2 timeout pattern.',
        'Next check proposed: freeze these exact targets; persist phase markers outside the child process; record equation degrees, variable counts, saturation, memory and censored phases. Preserve the four-second outcomes and declare any additional observation schedule separately. Verify every returned section by substitution.',
        'Sources: imported blind-results.json / geometry-results.json and their source programs, hash-pinned in observations.json. Historical finite controls; no new canonical E3 trial. This plane-pencil d differs from D in the newer Weierstrass encoding.',
    ]),
    ('Field-lift table: repeated concrete inputs','field-lift-multiplicity.svg',[
        'What stands out: 1,395 saved rows partition into 966 seed-inclusive keys (g,p,reduction root,A,B,seed). There are 169 repeated-key groups and 429 additional rows beyond one per key. Five keys each occur ten times. Every repeated-key group has identical saved work-rung profiles and sampled point lists.',
        'Example: g=t^3+t-1, p=4111, reduction root 16, A=-16, B=11, seed 3. Ten zero-based row indices and their labels are retained in field-lift-repeat-groups.json. Dropping seed gives 962 distinct algebraic inputs; different seeds remain separately identified.',
        'Construction feature to inspect: monic degree-d, weight-w random polynomials have at most 2^(w-1) binomial(d-1,w-2) coefficient patterns before filtering. For d=3,w=3, this is eight. The source permits repeated draws, picks the first admissible prime for each polynomial, and reuses curve seed keys (seed,shape,k).',
        'This is a literal-key partition, not a field-isomorphism classification or an independence test. It does not change the original weighting or discard any row. Rank descent was skipped in the source run; point/residue counts and rank certificates remain separate.',
        'Next check proposed: record finite sampler support and draw multiplicities by shape/seed; collect unique field/prime/curve inputs with multiple separately recorded search seeds. Present both row-weighted and input-grouped tables with their sampling definitions.',
        'Sources: EXP-ECDLP-4c6a09 / RUN-ECDLP-e89532, plus random_shape and the construction loop in implementation/src/main.rs. Producer/checker exit codes 0; supervisor receipt retains invalid_output for legacy manifest format. Full sources and hashes are pinned. Canonical graphs and scientific statuses remain unchanged.',
    ]),
]
source='#set page(paper:"a4",margin:17mm)\n#set text(size:9.5pt)\n'
for i,(title,svg,paragraphs) in enumerate(pages):
    if i:source+='\n#pagebreak()\n'
    source+='\n= '+title+'\n\n'
    for j,paragraph in enumerate(paragraphs):
        source+='#text('+json.dumps(paragraph)+')\n\n'
        if j==0:source+='#image('+json.dumps(svg)+',width:100%)\n\n'
(folder/'report.typ').write_text(source.rstrip()+'\n')
typst.compile(str(folder/'report.typ'),output=str(folder/'report.pdf'),root=str(folder))
pdf=pymupdf.open(folder/'report.pdf')
for i,page in enumerate(pdf):
    page.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25)).save(f'/tmp/snfs-observation-card-{i+1}.png')
print(json.dumps({'pdf_pages':len(pdf),'pdf':str(folder/'report.pdf')}))
