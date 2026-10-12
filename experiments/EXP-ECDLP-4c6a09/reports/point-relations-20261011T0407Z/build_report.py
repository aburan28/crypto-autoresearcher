#!/usr/bin/env python3
"""Build a dated, evidence-linked report from immutable point/relation records."""
import csv
import hashlib
import json
import math
import platform
import shutil
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import typst

REPO = Path('/workspace/solinas-run')
BASE = REPO/'experiments/EXP-ECDLP-4c6a09'
RUN = BASE/'runs/RUN-ECDLP-6d910b'
OUT = BASE/'reports/point-relations-20261011T0407Z'
COLORS = {'Solinas':'#1f6d87','Random hidden':'#dd9231','Q only':'#8b5d9b','BSGS':'#4a7b43','Pure cubic':'#be6946','Random field':'#619cab'}

def dump(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def csv_write(path,rows):
    columns=list(rows[0])
    with path.open('x',newline='') as f:
        w=csv.DictWriter(f,columns)
        w.writeheader()
        w.writerows(rows)

def gp_cpu(coverage_row,kind):
    values=[]
    for t in coverage_row['NF_timings']:
        v=t['values']
        if t['kind']!=kind or v[0]!=4:continue
        if kind=='NF_REDUCE' and v[2]!=[6,7,12].index(coverage_row['k'])+1:continue
        values.append(v[2] if kind=='NF_PRECOMPUTE' else v[4])
    return statistics.median(values)/1000

def savefig(fig,name):
    fig.tight_layout()
    fig.savefig(OUT/name,metadata={'Creator':'Measured RUN-ECDLP-6d910b; build_report.py'})
    plt.close(fig)

def draw_diagram():
    fig,ax=plt.subplots(figsize=(10.7,3.15))
    ax.set(xlim=(0,11),ylim=(0,3.2))
    ax.axis('off')
    boxes=[(.12,1.5,2.4,1.15,'Checked points in E(K)\nsmall coefficient box\nrank 3 or 4', '#e9f1f4'),
           (3.15,1.5,2.5,1.15,'Reduce, then use F_p\nfinite subgroup of order ell\npoint table + coefficients','#e9f1f4'),
           (6.25,1.5,2.25,1.15,'Target hits\nc · u − q = −j M\nindependent equations','#fcf0d9'),
           (9.1,1.5,1.75,1.15,'Global row rank\nreuse seed logs\nrecover q if fixed','#edf3e9')]
    for x,y,w,h,label,color in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',facecolor=color,edgecolor='#64727a'))
        ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=10)
    for x,z in [(2.56,3.10),(5.69,6.20),(8.54,9.05)]:
        ax.add_patch(FancyArrowPatch((x,2.05),(z,2.05),arrowstyle='-|>',mutation_scale=15,color='#64727a'))
    ax.text(5.5,.83,'A collision counts as useful only when it adds modular matrix rank.\nKnown-scalar BSGS points avoid unknown seed logs.',ha='center',va='center',fontsize=11)
    ax.text(5.5,.18,'Measured toy pipeline; the field identity alone does not reveal u or q.',ha='center',fontsize=10,color='#36434d')
    savefig(fig,'relation-pipeline.svg')

def figures(methods,coverage,paired):
    fig,axes=plt.subplots(1,2,figsize=(10.7,3.85))
    names={'solinas':'Solinas','rational':'Q only','pure_cubic':'Pure cubic'}
    for ax,(a,b) in zip(axes,[(-3,3),(7,1)]):
        for arm,label in names.items():
            rows=sorted([r for r in coverage if r['A']==a and r['B']==b and r['k']==12 and r['field']==arm],key=lambda r:r['bound'])
            ax.plot([r['finite_build_operations']['group_calls'] for r in rows],
                    [r['distinct_subgroup_points'] for r in rows],'-o',color=COLORS[label],label=label)
        baselines=sorted([m for m in methods if m['A']==a and m['B']==b and m['k']==12 and m['arm'].startswith('bsgs')],key=lambda m:m['table_build_operations']['group_calls'])
        ax.plot([m['table_build_operations']['group_calls'] for m in baselines],
                [m['distinct_subgroup_points'] for m in baselines],'-s',color=COLORS['BSGS'],label='G multiples (BSGS)')
        ax.set(xscale='log',yscale='log',xlabel='Finite-field group calls to build table',ylabel='Distinct subgroup points',title=f'y² = x³ {a:+d}x {b:+d}; k = 12')
        ax.grid(True,which='major',alpha=.2)
        ax.legend(fontsize=8,loc='upper left')
    fig.suptitle('Coverage per table-building work; B = 1, 2, 4 for algebraic seed boxes',fontsize=11)
    savefig(fig,'coverage-per-work.svg')
    fig,axes=plt.subplots(1,2,figsize=(10.7,3.9))
    for ax,(a,b) in zip(axes,[(-3,3),(7,1)]):
        x=np.arange(3)
        for offset,label in enumerate(['Solinas','Random hidden','BSGS']):
            values=[]
            for k in [6,7,12]:
                row=next(p for p in paired if p['A']==a and p['B']==b and p['k']==k)
                method=next(m for m in methods if m['id']==row[{'Solinas':'solinas_id','Random hidden':'null_id','BSGS':'best_bsgs_id'}[label]])
                values.append(method['useful_relations_per_1000_group_calls'])
            ax.bar(x+(offset-1)*.25,values,.24,label=label,color=COLORS[label])
        labels=[f"k={k}\nell={next(p for p in paired if p['A']==a and p['B']==b and p['k']==k)['ell']:,}" for k in [6,7,12]]
        ax.set(yscale='log',xticks=x,xticklabels=labels,ylabel='Global independent equations / 1,000 group calls',title=f'y² = x³ {a:+d}x {b:+d}')
        ax.grid(axis='y',alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle('Useful relation rate with information shared across 16 targets per subgroup',fontsize=11)
    savefig(fig,'useful-relations-per-work.svg')
    fig,axes=plt.subplots(1,2,figsize=(10.7,3.15))
    for ax,(a,b) in zip(axes,[(-3,3),(7,1)]):
        row=next(r for r in coverage if r['field']=='solinas' and r['A']==a and r['B']==b and r['k']==12 and r['bound']==4)
        values=[sum(gp_cpu(row,kind) for kind in ['NF_PRECOMPUTE','NF_GENERATE','NF_REDUCE']),row['cached_build_cpu_median_seconds']]
        ax.bar(['Exact K, then reduce','Reduced seeds, F_p'],values,color=[COLORS['Solinas'],COLORS['BSGS']],width=.58)
        for i,v in enumerate(values):ax.text(i,v*1.09,f'{v:.4f} s',ha='center',fontsize=9)
        ax.set(yscale='log',ylabel='Instrumented CPU seconds; median of 3',title=f'{row["grid_entries"]:,} coefficients; y²=x³{a:+d}x{b:+d}')
        ax.set_ylim(min(values)*.5,max(values)*2.7)
        ax.grid(axis='y',alpha=.2)
    savefig(fig,'exact-field-cost.svg')

def main():
    OUT.mkdir(exist_ok=False)
    shutil.copy2(Path(__file__),OUT/'build_report.py')
    shutil.copy2(RUN/'source/GPL-2.txt',OUT/'GPL-2.txt')
    cold=json.loads((RUN/'benchmark-attempt-01/raw-result.json').read_text())
    shared=json.loads((RUN/'benchmark-shared-attempt-01/raw-result.json').read_text())
    coverage=json.loads((RUN/'benchmark-attempt-01/coverage.json').read_text())
    methods=shared['methods']
    paired=[]
    for s in [m for m in methods if m['arm']=='solinas']:
        rows=[m for m in methods if (m['A'],m['B'],m['k'])==(s['A'],s['B'],s['k'])]
        best=min([m for m in rows if m['arm'].startswith('bsgs')],key=lambda m:m['total_algorithm_operations']['group_calls'])
        null=next(m for m in rows if m['id']==s['id']+'-random_hidden')
        q=next(m for m in rows if m['arm']=='rational')
        paired.append({'A':s['A'],'B':s['B'],'k':s['k'],'p':s['p'],'ell':s['ell'],'curve_id':s['curve_id'],'curve_uid':s['curve_uid'],
                       'solinas_id':s['id'],'null_id':null['id'],'best_bsgs_id':best['id'],
                       'Q_points':q['distinct_subgroup_points'],'K_points':s['distinct_subgroup_points'],
                       'coverage_ratio_K_over_Q':s['distinct_subgroup_points']/q['distinct_subgroup_points'],
                       'K_coverage_percent':100*s['subgroup_coverage_fraction'],
                       'solinas_recovered':s['target_recoveries'],'bsgs_recovered':best['target_recoveries'],
                       'solinas_group_calls':s['total_algorithm_operations']['group_calls'],
                       'bsgs_group_calls':best['total_algorithm_operations']['group_calls'],
                       'group_work_ratio_K_over_BSGS':s['total_algorithm_operations']['group_calls']/best['total_algorithm_operations']['group_calls'],
                       'solinas_global_relation_rank':s['batch_result']['global_relation_rank'],
                       'bsgs_global_relation_rank':best['batch_result']['global_relation_rank'],
                       'solinas_relation_rate_per_1000':s['useful_relations_per_1000_group_calls'],
                       'bsgs_relation_rate_per_1000':best['useful_relations_per_1000_group_calls'],
                       'null_group_calls':null['total_algorithm_operations']['group_calls']})
    assert all(p['solinas_recovered']==p['bsgs_recovered']==16 for p in paired)
    assert all(p['group_work_ratio_K_over_BSGS']>1 for p in paired)
    csv_write(OUT/'paired-results.csv',paired)
    csv_write(OUT/'methods.csv',[{k:m[k] for k in ['id','arm','A','B','k','p','ell','curve_id','curve_uid','seed_count','unknown_seed_count',
                                                  'table_entries_requested','distinct_subgroup_points','subgroup_coverage_fraction','target_count',
                                                  'target_recoveries','useful_relations_per_1000_group_calls','recoveries_per_1000_group_calls',
                                                  'total_build_query_cpu_seconds']} | {'group_calls':m['total_algorithm_operations']['group_calls'],
                                                                                     'global_relation_rank':m['batch_result']['global_relation_rank']}
                                      for m in methods])
    csv_write(OUT/'coverage.csv',[{k:r[k] for k in ['spec_id','field','A','B','k','p','ell','curve_uid','bound','seed_count','grid_entries',
                                                  'distinct_full_group_points','full_group_order','distinct_subgroup_points','subgroup_coverage_fraction',
                                                  'factorbase_collisions','independent_factorbase_relations','cached_build_cpu_median_seconds']}
                                      | {'finite_build_group_calls':r['finite_build_operations']['group_calls']} for r in coverage])
    csv_write(OUT/'curve-identities.csv',[{'curve_id':g['identity']['curve_id'],'curve_uid':g['identity']['curve_uid'],
                                         'field_sha256':g['identity']['field_sha256'],'A':g['A'],'B':g['B'],'k':g['k'],'p':g['p'],
                                         'group_order':g['group_order'],'subgroup_order':g['ell'],'cofactor':g['cofactor'],
                                         'G_x':g['G'][0],'G_y':g['G'][1]} for g in cold['public_groups']])
    summary={'run_id':RUN.name,'raw_run_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
             'scope':shared['actual_scope'],'Solinas_verified_recoveries':96,'paired_results':paired,
             'dominated_by':{'method':'Declared generic BSGS controls','checked_all_six_cohorts':True,
                             'cost_boundary':'seed projection/construction, point-table build, shared target queries; exact-K and prior descent costs excluded and separately reported',
                             'comparison':'best measured control among predeclared matched table sizes and ceil(sqrt(ell)); not a universal optimum'},
             'sota_delta':{'kind':'scoped measured comparison, not frontier or asymptotic bound','recoveries_delta':0,
                           'Solinas_minus_BSGS_group_calls_per_cohort':[p['solinas_group_calls']-p['bsgs_group_calls'] for p in paired]},
             'statistics':'Fixed two selected toy models, six cohorts, 16 common targets each; one random finite-field seed set per configuration. No confidence intervals or population significance claim.',
             'raw_hashes':{str(p.relative_to(RUN)):sha(p) for p in [RUN/'raw-result.json',RUN/'benchmark-attempt-01/raw-result.json',
                                                                   RUN/'benchmark-shared-attempt-01/raw-result.json',RUN/'benchmark-attempt-01/coverage.json']}}
    dump(OUT/'summary.json',summary)
    draw_diagram()
    figures(methods,coverage,paired)
    big=[p for p in paired if p['k']==12]
    table='| Curve | r_Q → r_K | ell | Q points | K points | K coverage | K calls | BSGS calls | K/BSGS work |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    for p in big:
        rank='1 → 3' if p['A']==-3 else '2 → 4'
        table+=f"| x³{p['A']:+d}x{p['B']:+d} | {rank} | {p['ell']:,} | {p['Q_points']} | {p['K_points']:,} | {p['K_coverage_percent']:.5f}% | {p['solinas_group_calls']:,} | {p['bsgs_group_calls']:,} | {p['group_work_ratio_K_over_BSGS']:.2f}× |\n"
    md=f'''# Solinas point coverage and useful relations — 2026-10-11 UTC

**Measured** follow-up: **{RUN.name}**, **EXP-ECDLP-4c6a09**, **H-ECDLP-4da36f**, **GOAL-ECDLP-001**.
User request: “Yes measure this point coverage and useful relations per unit.”
Raw observations are locally committed at `{summary['raw_run_commit']}`. No independent review or research-status promotion was performed.

## Result

Added rank expands small-coefficient point supply. With relations shared across a
batch, the Solinas method recovered **96/96 synthetic target scalars**. The generic
BSGS controls recovered the same targets with **less group work in every one of
the six matched cohorts**. This is a result for these measured methods and toy
inputs; it is not a conclusion about every possible algebraic relation.

At the largest prime, p = **68,719,472,639**, coefficient boxes [-4,4]^s give:

{table}

Both Solinas boxes cover **81×** as many subgroup points as the corresponding
rational-only boxes. They also enumerate 81× as many coefficient vectors. At
this prime none of those box points collide. Extra rank therefore gives extra
points; it does not give extra points for free. Every row above recovered 16/16
targets for K and BSGS. BSGS is the best of the *declared* measured controls, not
an optimized claim over all batch algorithms or all table sizes.

![Relation pipeline](relation-pipeline.svg)

## Useful information per unit work

A useful relation adds rank to one modular linear system over F_ell. The unknowns
are the seed logs u_i and the 16 target logs q_j. A duplicate hit or dependent
equation adds no information. One seed equal to the public G has known log 1;
seed points equal to -G or O likewise have known labels. Every other seed label
remains unknown to the solver.

At k=12, the rank-3 case gives **18** independent global equations using
**92,149** finite-field group calls: **0.1953 relations/1,000 calls**. Its BSGS
control gives **16** using **20,396** calls: **0.7845/1,000**.
The rank-4 case gives **19** using **81,266** calls: **0.2338/1,000**;
matched-size BSGS gives **16** using **36,989** calls: **0.4326/1,000**.
The additional two or three equations pay for previously unknown generator logs.
All recovered scalars were checked both against the target point and the
separately held synthetic scalar truth.

![Coverage per work](coverage-per-work.svg)
![Independent relations per work](useful-relations-per-work.svg)

The random finite-field null uses the same curve, subgroup, seed count, known
generator slot, coefficient box and targets. At the largest prime its shared
recovery costs are **92,465** and **80,996** calls, compared with **92,149** and
**81,266** for Solinas. These near-equal costs do not establish a special Solinas
advantage. There is one random seed set per configuration, two selected models,
and no population-level confidence interval or significance claim.

## Theory and the tested relation mechanism

**Derived.** K = Q(alpha), alpha³-alpha-1=0, reduces at alpha → 2^k when
p=(2^k)^3-2^k-1 is prime. Checked algebraic points map into E(F_p). We project by
h=#E(F_p)/ell into its largest prime-order subgroup and use a common public G.
The exact field/curve/subgroup/generator identities are retained in
[curve-identities.csv](curve-identities.csv), including full EC1 UIDs.

For a coefficient vector c, P_c=Σ c_i F_i. A table collision P_c=P_d gives
(c-d)·u=0 modulo ell. A target hit Q-jMG=P_c gives c·u-q=-jM. Gaussian elimination
counts only independent equations; q is recovered only if its coordinate is
uniquely determined. All relation witnesses are verified with finite-field
arithmetic. The solver receives public points and permitted known labels only.

The shared batch can learn seed logs from one target and reuse them for others.
The preserved cold-target phase resets those constraints between targets: at
k=12 it recovered 14/16 and 16/16 Solinas targets, using 261,072 and 230,529
calls. Its per-target equation counts are not global batch rank. The additive
shared phase uses exactly the same frozen points, targets and 32,768-probe cap,
and reduces these costs to the figures above.

Ordinary BSGS stores known points iG and probes Q-jMG. A hit immediately gives
q=i+jM. It avoids unknown factor-base seed logs. It is a measured generic
control here, not a new algorithm or an asymptotic ECDLP improvement.

## What exact number-field work costs

Every exact-K grid reduction was checked entry-for-entry against generating from
the reduced seeds directly in F_p. The outputs agree. Reduction is a group
homomorphism, so once the seeds are available, finite-field generation supplies
the same reduced point set without doing all additions over K.

![Exact-field versus cached cost](exact-field-cost.svg)

Three instrumented timing repetitions are retained. For B=4, Solinas exact-K
generation, precomputation and reduction at k=12 have component medians totaling
about **0.899 CPU s** for 729 entries and **4.741 CPU s** for 6,561 entries.
The coordinate numerator/denominator proxy reaches **495** and **646 bits**.
This proxy is not a canonical height. Exact-K timers include the bit-size check;
the first reduction repeat includes row output. Cached Python table timings
include relation construction and checks. These are machine observations with
different implementations, not portable operation weights or sealed bounds.
Prior descent/seed-discovery times remain separately recorded and are excluded
from the primary finite-field counts, which already favor BSGS.

## Scope, controls and limitations

* Two previously highlighted rank-gain models; this is not a representative
  curve sample and neither is a deployed NIST curve.
* k=6,7,12; subgroup orders are 947, 2,097,833, 5,385,547 for (-3,3), and
  293, 6,803, 26,109,179 for (7,1). Small subgroups can saturate cheaply and
  must not be mistaken for cryptographic scale.
* 78 coverage cells, B=1,2,4; 90 method configurations per cold/shared phase;
  96 common synthetic targets. Unfinished target searches are censored at the
  cap, not treated as impossibility or zero rank.
* Matched pure cubic K=Q(cuberoot(3)) ranks are 2 and 3. Random low-weight
  K=Q(beta), beta³+beta-1=0, has rank 1 for (-3,3) and bounds [2,3] for (7,1).
  Its 2- and 3-dimensional labels are not asserted exact when only bounded.
  That field has no degree-one reduction at k=7,12: all four unavailable
  model/prime comparisons remain explicitly recorded.
* Sign-change control beta³-beta+1=0 with alpha=-beta gives identical reduced
  seeds, coverage, global relation rank, recoveries and group counts. It is an
  isomorphic control, not an independent field sample.
* Meaningful controls reject dependent equations, rank-deficient target
  recovery and contradictory equations. All exact-K tables match the counted
  finite-field implementation; all reported recovered scalars are correct.
* One initial GP table attempt failed because nfmodpr returns t_FFELT at degree
  one. Its source/logs are retained. The new attempt converts via degree-one
  trace, which is the identity mathematically. No failed process is evidence
  about the hypothesis. The original coverage/rank source and results stay intact.

**Remaining opportunity.** A new mechanism would need cheaper nontrivial
relations, improved height-bounded lifting, or another measured advantage over
generic known-scalar point generation. Rank gain and linear combinations alone
do not supply that advantage in this measured scope. Larger fields and deployed
curves remain untested by this benchmark.

## Evidence and reproduction

* [Frozen plan](../../runs/{RUN.name}/plan.json) and [shared-information addendum](../../runs/{RUN.name}/shared-relations-plan.json).
* [Principal shared-batch raw result](../../runs/{RUN.name}/benchmark-shared-attempt-01/raw-result.json).
* [Cold-target raw result](../../runs/{RUN.name}/benchmark-attempt-01/raw-result.json).
* [Coverage and costs](../../runs/{RUN.name}/benchmark-attempt-01/coverage.json).
* [Exact-field GP scripts, tables and repeats](../../runs/{RUN.name}/point-preparation-attempt-02/exact-grids/).
* [Matched descent records](../../runs/{RUN.name}/matched-ranks-result.json).
* [All methods CSV](methods.csv), [paired results](paired-results.csv), [coverage CSV](coverage.csv).
* [Source and reproduction notes](../../runs/{RUN.name}/README.md); PARI/GP 2.17.2, Python 3.12.14.

Every phase retains source snapshots, script hashes, commands, raw stdout/stderr,
process measurements and failed attempts. Source GPL-2 license is retained.
[Integrity checks](../../runs/{RUN.name}/integrity-check.json) verify hashes and
that historical coverage/rank raw files are unchanged. No independent review
was performed. GitHub publication remains blocked by the unchanged preceding
authentication failure; results are locally committed and downloadable.

Graph checks: historical coverage and rank report sources/renderings, plus the
canonical ECDLP frontier inventory. No canonical graph or measured-bound record
changes: these scoped primitive counts are not an ECBND sealed frontier bound.
This new report and its editable figures describe the new observations without
changing historical evidence, hypotheses, experiments or frontier statuses.
'''
    (OUT/'report.md').write_text(md)
    # A compact self-contained four-page PDF, with detailed data in adjacent CSV/JSON.
    table_rows=[]
    for p in big:
        table_rows.extend([f'[x³{p["A"]:+d}x{p["B"]:+d}]',f'[{p["ell"]:,}]',f'[{p["Q_points"]} → {p["K_points"]:,}]',
                           f'[{p["solinas_group_calls"]:,}]',f'[{p["bsgs_group_calls"]:,}]',f'[{p["group_work_ratio_K_over_BSGS"]:.2f}×]'])
    identities='\n'.join(f"#text(size:7.1pt)[{g['identity']['curve_id']} • A={g['A']}, B={g['B']}, k={g['k']}\\\n{g['identity']['curve_uid']}]\n" for g in cold['public_groups'])
    typ=f'''#set page(paper: "a4", margin: 15mm, footer: context [#text(size: 8pt)[RUN-ECDLP-6d910b • measured toy inputs] #h(1fr) #counter(page).display()])
#set text(font: "DejaVu Sans", size: 9.1pt)
#set par(leading: .5em)
#set heading(numbering: none)
= Solinas: point coverage and useful relations
Measured 2026-10-11 UTC • EXP-ECDLP-4c6a09 • H-ECDLP-4da36f

*Added rank expands point supply; these linear-combination methods do not beat generic BSGS.*
With generator information shared, Solinas recovered all *96/96* public synthetic
targets. BSGS recovered the same targets with less group work in every one of six
matched curve/prime cohorts. These are observations, not independently reviewed
claims, deployed-curve results or asymptotic bounds.

== Largest prime: p = 68,719,472,639
Coefficients in [-4,4]; rational ranks 1 → 3 and 2 → 4 over the Solinas cubic field.
#table(columns:(1.35fr,1.25fr,1.2fr,1fr,1fr,.8fr),inset:5pt,
 [Curve rhs],[Subgroup ell],[Q → K points],[K calls],[BSGS calls],[K/BSGS],
 {','.join(table_rows)})
K points cover 0.01354% and 0.02513% of these subgroups. Both are *81×* the
rational-only point counts, with 81× as many coefficient vectors. Each row
recovered 16/16 targets for both methods. Calls include seed projection, table
construction and shared queries; exact-K and prior rank-discovery work are separate.

#image("relation-pipeline.svg",width:100%)

== A useful relation is new information
Unknown seed logs u and target logs q enter one modular linear system over F_ell.
Collisions give (c−d)·u=0; a target hit gives c·u−q=−jM. Only matrix-rank increases
count. A hit alone is not scalar recovery. Learned seed constraints are shared
across all 16 targets, and q is returned only when uniquely implied.

At this prime, Solinas yields *0.1953* and *0.2338 independent relations per 1,000
group calls*; the respective BSGS controls yield *0.7845* and *0.4326*.
The extra two or three equations pay for unknown seed logs. All recovered
scalars and independent relation witnesses were checked.

#pagebreak()
= Coverage and relation efficiency
#image("coverage-per-work.svg",width:100%)
Measured build operations at k=12. Algebraic boxes use B=1,2,4. Ordinary known
multiples of G reach at least as many points per construction call. Seed
projection and prior descent cost are excluded from this build-only chart.

#image("useful-relations-per-work.svg",width:100%)
Six fixed cohorts, 16 common targets each; one random finite-field seed set per
configuration. No population confidence interval is claimed. Random hidden
seeds have matching seed count, known generator slot, box and target inputs.
At k=12, Solinas takes 92,149 and 81,266 calls; the matching random hidden
sets take 92,465 and 80,996. This run does not establish a special Solinas advantage.

BSGS denotes the best measured control among the predeclared matched table sizes
and ceil(sqrt(ell)); it is not a claim of globally optimal batch parameters.

#pagebreak()
= Exact field cost and matched controls
K=Q(alpha), alpha³−alpha−1=0, reduces through alpha → 2^k. All exact-K table
reductions agree entry-for-entry with generation directly from reduced seeds.
Once those seeds are known, the cheaper finite-field path gives the same points.

#image("exact-field-cost.svg",width:100%)
Three timing repeats. Component medians for exact-K precomputation, generation
and reduction at k=12 total about *0.899 s* and *4.741 s*. Coordinate numerator/
denominator sizes reach 495 and 646 bits; this is not canonical height. GP timing
includes bit-size checks and first-repeat row output; cached Python timing includes
relation construction/checks. These machine timings are not portable primitive weights.

The preserved cold-target boundary resets learned generator constraints between
targets: 14/16 and 16/16 recoveries at k=12, costing 261,072 and 230,529 calls.
Its per-target relation counts are not global batch rank. The shared phase uses
the identical point sets, target order and 32,768-probe cap, with one common query jump.

== Controls and actual scope
- Two selected rank-gain models; three primes k=6,7,12; 78 coverage cells; 90
  configurations in each cold/shared phase; 96 unique synthetic targets.
- Pure cubic control y³−3: ranks 2 and 3. Random low-weight control y³+y−1:
  rank 1 and bounds [2,3]. The supplied point sets are not claimed saturated bases.
- The random field has no degree-one reduction at k=7,12. Four unavailable
  model/prime comparisons are retained; no substitute prime was selected.
- Sign-change control alpha=−beta, beta³−beta+1=0 matches all six Solinas cohorts.
  It is an isomorphic null, not an independent sample.
- A first GP preparation failed on t_FFELT conversion. The retained retry uses
  the identity trace in degree one. All failures and source versions are preserved.

Incomplete searches remain censored. Small subgroups, selected models and one
random seed set restrict inference. Higher fields and deployed NIST curves are
untested. Cheaper new relations or a better height-bounded lift mechanism remain
separate opportunities; these measurements do not rule them out.

#pagebreak()
= Evidence, identities and reproduction
Full identities bind the exact prime field, rational model, subgroup, cofactor
and public generator. The same identity is used by every compared method.
{identities}

== Immutable sources
Run directory: experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-6d910b.
Raw run commit: #text(size:7.8pt)[{summary['raw_run_commit']}].

Principal result: benchmark-shared-attempt-01/raw-result.json. Frozen plan and
shared-relations-plan.json define the boundaries; benchmark-attempt-01 retains
the cold result. point-preparation-attempt-02/exact-grids retains exact GP
tables and repeats. Earlier failed preparation and four matched descents remain
beside them. Every recovered scalar was checked against both the public point
and separately held synthetic truth; solver inputs exclude that truth.

Adjacent report.md links all evidence. methods.csv, paired-results.csv,
coverage.csv and curve-identities.csv provide the full measurements. Editable
build_report.py generates the SVG figures and PDF. Source snapshots, command
arguments, logs, GPL-2 license, script hashes and integrity checks are retained.
PARI/GP 2.17.2; Python 3.12.14. Reproduction uses fresh output locations.

No independent review, research-status change or sealed frontier-bound claim
occurred. Historical coverage/rank reports remain unchanged; this new report
adds the scoped observations. Canonical ECDLP frontier graphs require reviewed
bound evidence and are unaffected. GitHub publication remains unavailable under
the prior unchanged authentication failure; records are committed locally.
'''
    (OUT/'report.typ').write_text(typ)
    typst.compile(str(OUT/'report.typ'),output=str(OUT/'report.pdf'),root=str(OUT))
    dump(OUT/'render-environment.json',{'python':platform.python_version(),'matplotlib':matplotlib.__version__,
                                     'typst':'0.15.0 installed tool','rendered_at_utc':datetime.now(timezone.utc).isoformat(),
                                     'report_pdf_sha256':sha(OUT/'report.pdf')})
    print(OUT,sha(OUT/'report.pdf'))

if __name__=='__main__':main()
