#!/usr/bin/env python3
"""Render descriptive random-field results from immutable matched observations."""
import csv
import hashlib
import json
import platform
import shutil
import statistics
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import typst

REPO=Path('/workspace/solinas-run')
BASE=REPO/'experiments/EXP-ECDLP-4c6a09'
RUN=BASE/'runs/RUN-ECDLP-9e6cc1'
OUT=BASE/'reports/random-fields-20261011T0523Z'
MODELS=[(-3,3),(7,1)]
COLORS={'random':'#6e8496','solinas':'#216778','bsgs':'#53823d'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def csv_write(p,rows):
    with p.open('x',newline='') as f:
        writer=csv.DictWriter(f,list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
def stats(values):
    return {'n':len(values),'min':min(values),'median':statistics.median(values),'max':max(values)} if values else {'n':0,'min':None,'median':None,'max':None}
def fmt(value,digits=3):return 'unavailable' if value is None else f'{value:,.{digits}f}'
def nf_cost(method,kind):
    rows=[t['values'] for t in method['NF_timings'] if t['kind']==kind]
    if kind=='NF_REDUCE':
        rows=[r for r in rows if r[2]==[6,7,12].index(method['k'])+1]
    return statistics.median(r[2] if kind=='NF_PRECOMPUTE' else r[4] for r in rows)/1000
def fig_save(fig,name):
    fig.tight_layout();fig.savefig(OUT/name,metadata={'Creator':RUN.name+'; editable build_random_report.py'})
    plt.close(fig)

def figures(methods,cohorts):
    fig,ax=plt.subplots(figsize=(10.6,2.55));ax.axis('off');ax.set(xlim=(0,11),ylim=(0,2.4))
    boxes=[(.1,1.1,2.3,'3 RNG seeds\n24 distinct cubic fields'),
           (3,1.1,2.3,'48 checked descents\nkeep bounds / timeouts'),
           (5.9,1.1,2.3,'Fixed prime has a root?\nNo: retain unavailable'),
           (8.8,1.1,2.1,'Same target batch\ncoverage + relations')]
    for x,y,w,label in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,.95,boxstyle='round,pad=.03',facecolor='#edf1f4',edgecolor='#6c7c86'))
        ax.text(x+w/2,y+.47,label,ha='center',va='center',fontsize=10)
    for x,z in [(2.5,2.95),(5.4,5.85),(8.3,8.75)]:
        ax.add_patch(FancyArrowPatch((x,1.57),(z,1.57),arrowstyle='-|>',mutation_scale=15,color='#6c7c86'))
    ax.text(5.5,.45,'No selection on rank or coverage. Isomorphic draws rejected before any descent.\nGeneric control: known G multiples on identical curves, subgroups and public targets.',ha='center',fontsize=10)
    fig_save(fig,'sampling-pipeline.svg')
    fig,axes=plt.subplots(1,2,figsize=(10.6,3.8))
    for ax,(a,b) in zip(axes,MODELS):
        for row in [c for c in cohorts if (c['A'],c['B'])==(a,b)]:
            x=[6,7,12].index(row['k'])
            observed=[m for m in methods if (m['A'],m['B'],m['k'])==(a,b,row['k'])]
            offsets=[(i-(len(observed)-1)/2)*.014 for i in range(len(observed))]
            ax.scatter([x+d for d in offsets],[m['useful_relations_per_1000_group_calls'] for m in observed],s=22,color=COLORS['random'],alpha=.6)
            ax.scatter([x-.22],[row['solinas_relation_rate']],s=65,marker='D',color=COLORS['solinas'])
            ax.scatter([x+.22],[row['bsgs_relation_rate']],s=65,marker='s',color=COLORS['bsgs'])
        ax.set(yscale='log',xticks=[0,1,2],xticklabels=[f'k={k}\nn={next(c for c in cohorts if (c["A"],c["B"],c["k"])==(a,b,k))["eligible_fields"]}' for k in [6,7,12]],
               ylabel='Independent equations / 1,000 group calls',title=f'y² = x³ {a:+d}x {b:+d}')
        ax.grid(axis='y',alpha=.2)
    for label,color,marker in [('Random fields',COLORS['random'],'o'),('Solinas',COLORS['solinas'],'D'),('Declared best BSGS',COLORS['bsgs'],'s')]:
        axes[0].scatter([],[],label=label,color=color,marker=marker)
    axes[0].legend(fontsize=8)
    fig.suptitle('All eligible field cases; supplied point counts vary (strata in CSV)',fontsize=11)
    fig_save(fig,'relation-rates.svg')
    fig,axes=plt.subplots(1,2,figsize=(10.6,3.65))
    for ax,(a,b) in zip(axes,MODELS):
        rows=[m for m in methods if (m['A'],m['B'],m['k'])==(a,b,12)]
        for n in sorted({r['seed_count'] for r in rows}):
            obs=[r for r in rows if r['seed_count']==n]
            ax.scatter([n+(i-(len(obs)-1)/2)*.055 for i in range(len(obs))],[r['distinct_subgroup_points'] for r in obs],s=30,color=COLORS['random'])
        row=next(c for c in cohorts if (c['A'],c['B'],c['k'])==(a,b,12))
        ax.scatter([row['solinas_seed_count']],[row['solinas_distinct_points']],marker='D',s=75,color=COLORS['solinas'],label='Solinas')
        ax.set(yscale='log',xticks=[1,2,3,4],xlabel='Supplied point seeds; not asserted independent',ylabel='Distinct subgroup points in [-4,4] box',title=f'y² = x³ {a:+d}x {b:+d}; k=12')
        ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8)
    fig.suptitle('Point supply depends on returned seeds and reduction, beyond number-field degree',fontsize=11)
    fig_save(fig,'point-supply.svg')

def main():
    raw=json.loads((RUN/'benchmark-attempt-02/raw-result.json').read_text())
    ranks=json.loads((RUN/'random-ranks-result.json').read_text())
    sample=json.loads((RUN/'sampling-result.json').read_text())
    prior=json.loads((RUN/'inputs/prior-shared-result.json').read_text())
    additional=json.loads((RUN/'additional-generic-controls/raw-result.json').read_text())
    prior['methods']+=additional['methods']
    specs=json.loads((RUN/'point-preparation-attempt-02/seed-specs.json').read_text())
    methods=raw['methods']
    OUT.mkdir(exist_ok=False)
    shutil.copy2(Path(__file__),OUT/'build_random_report.py')
    shutil.copy2(RUN/'source/GPL-2.txt',OUT/'GPL-2.txt')
    cohorts=[];strata=[]
    for a,b in MODELS:
        for k in [6,7,12]:
            previous=[m for m in prior['methods'] if (m['A'],m['B'],m['k'])==(a,b,k)]
            sol=next(m for m in previous if m['arm']=='solinas')
            bg=min((m for m in previous if m['arm'].startswith('bsgs') and m['target_recoveries']==16),key=lambda m:m['total_algorithm_operations']['group_calls'])
            bg_same=next(m for m in previous if m['arm'].startswith('bsgs') and m['table_entries_requested']==sol['table_entries_requested'])
            obs=[m for m in methods if (m['A'],m['B'],m['k'])==(a,b,k)]
            matched=[m for m in obs if m['seed_count']==sol['seed_count'] and m['unknown_seed_count']==sol['unknown_seed_count']]
            full=[m for m in obs if m['target_recoveries']==16]
            row={'A':a,'B':b,'k':k,'p':sol['p'],'ell':sol['ell'],'eligible_fields':len(obs),
                 'unavailable_fields':24-len(obs),'random_full_recovery_fields':len(full),
                 'random_verified_target_recoveries':sum(m['target_recoveries'] for m in obs),
                 'random_target_attempts':16*len(obs),'relation_rate_all':stats([m['useful_relations_per_1000_group_calls'] for m in obs]),
                 'coverage_all':stats([m['distinct_subgroup_points'] for m in obs]),
                 'solinas_seed_count':sol['seed_count'],'solinas_unknown_seed_count':sol['unknown_seed_count'],
                 'solinas_distinct_points':sol['distinct_subgroup_points'],'solinas_group_calls':sol['total_algorithm_operations']['group_calls'],
                 'solinas_relation_rate':sol['useful_relations_per_1000_group_calls'],'solinas_recoveries':sol['target_recoveries'],
                 'bsgs_id':bg['id'],'bsgs_group_calls':bg['total_algorithm_operations']['group_calls'],
                 'bsgs_table_entries_requested':bg['table_entries_requested'],'bsgs_stored_points':bg['distinct_subgroup_points'],
                 'bsgs_relation_rate':bg['useful_relations_per_1000_group_calls'],
                 'same_table_BSGS_id':bg_same['id'],'same_table_BSGS_group_calls':bg_same['total_algorithm_operations']['group_calls'],
                 'same_table_BSGS_relation_rate':bg_same['useful_relations_per_1000_group_calls'],
                 'same_seed_count_fields':len(matched),'same_seed_count_relation_rate':stats([m['useful_relations_per_1000_group_calls'] for m in matched]),
                 'same_seed_count_coverage':stats([m['distinct_subgroup_points'] for m in matched]),
                 'same_seed_count_full_recovery_fields':sum(m['target_recoveries']==16 for m in matched),
                 'same_seed_count_fields_more_efficient_than_solinas':sum(m['recoveries_per_1000_group_calls']>sol['recoveries_per_1000_group_calls'] for m in matched),
                 'random_full_recovery_fields_cheaper_than_bsgs':sum(m['total_algorithm_operations']['group_calls']<bg['total_algorithm_operations']['group_calls'] for m in full)}
            cohorts.append(row)
            for n in sorted({m['seed_count'] for m in obs}):
                s=[m for m in obs if m['seed_count']==n]
                rt=stats([m['useful_relations_per_1000_group_calls'] for m in s]);cv=stats([m['distinct_subgroup_points'] for m in s])
                strata.append({'A':a,'B':b,'k':k,'seed_count':n,'n_fields':len(s),
                               'coverage_min':cv['min'],'coverage_median':cv['median'],'coverage_max':cv['max'],
                               'relation_rate_min':rt['min'],'relation_rate_median':rt['median'],'relation_rate_max':rt['max'],
                               'full_recovery_fields':sum(m['target_recoveries']==16 for m in s),
                               'verified_recoveries':sum(m['target_recoveries'] for m in s),'target_attempts':16*len(s)})
    rank_summary=[]
    for a,b in MODELS:
        rs=[r for r in ranks['nf'] if (r['job']['A'],r['job']['B'])==(a,b)]
        rq=1 if a==-3 else 2
        rank_summary.append({'A':a,'B':b,'r_Q':rq,'attempts':len(rs),'exact':sum(r['status']=='exact' for r in rs),
                             'interval':sum(r['status']=='bounds' for r in rs),'unfinished_or_error':sum(r['status'] not in ['exact','bounds'] for r in rs),
                             'certified_positive_rank_gain':sum(r['nf_bounds'] is not None and r['nf_bounds'][0]>rq for r in rs),
                             'exact_rank_histogram':dict(Counter(r['nf_bounds'][0] for r in rs if r['status']=='exact'))})
    summary={'run_id':RUN.name,'experiment_id':'EXP-ECDLP-4c6a09','scope':raw['actual_scope'],
             'raw_run_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
             'rank_results':rank_summary,'cohorts':cohorts,'strata':strata,
             'verified_target_recoveries':sum(m['target_recoveries'] for m in methods),'target_attempts':16*len(methods),
             'full_recovery_field_cohorts':sum(m['target_recoveries']==16 for m in methods),
             'full_recovery_field_cohorts_cheaper_than_bsgs':sum(c['random_full_recovery_fields_cheaper_than_bsgs'] for c in cohorts),
             'uncertainty':'Observed sample ranges only; no IID field/population significance or confidence interval. The same 24 fields occur on two selected curves and up to three primes.',
             'dominated_by':{'control':'predeclared generic BSGS sizes and ceil(sqrt(ell)) reused on identical groups/targets',
                             'boundary':'Cached group-call comparison; discovery and exact-K costs recorded separately',
                             'all_full_recovery_random_cases_more_expensive':all(c['random_full_recovery_fields_cheaper_than_bsgs']==0 for c in cohorts)},
             'sota_delta':'Measured paired primitive-count differences only; no asymptotic or ECBND claim'}
    write(OUT/'summary.json',summary)
    scalar_fields=['id','field_id','draw_seed','A','B','k','p','ell','curve_uid','seed_count','unknown_seed_count','rank_status',
                   'table_entries_requested','distinct_subgroup_points','subgroup_coverage_fraction','coverage_per_build_group_call',
                   'target_recoveries','target_count','useful_relations_per_1000_group_calls','recoveries_per_1000_group_calls',
                   'cached_build_cpu_median_seconds','rank_discovery_elapsed_seconds']
    csv_write(OUT/'methods.csv',[{**{key:m[key] for key in scalar_fields},'rank_bounds':json.dumps(m['rank_bounds']),
                               'group_calls':m['total_algorithm_operations']['group_calls'],
                               'global_relation_rank':m['batch_result']['global_relation_rank']} for m in methods])
    csv_write(OUT/'strata.csv',strata)
    csv_write(OUT/'costs.csv',[{'id':m['id'],'seed_count':m['seed_count'],
                              'rank_discovery_elapsed_seconds':m['rank_discovery_elapsed_seconds'],
                              'exact_K_precompute_cpu_median_seconds':nf_cost(m,'NF_PRECOMPUTE'),
                              'exact_K_generate_cpu_median_seconds':nf_cost(m,'NF_GENERATE'),
                              'exact_K_reduce_cpu_median_seconds':nf_cost(m,'NF_REDUCE'),
                              'maximum_coordinate_fraction_bits':max(t['values'][5] for t in m['NF_timings'] if t['kind']=='NF_GENERATE'),
                              'cached_table_cpu_median_seconds':m['cached_build_cpu_median_seconds'],
                              'query_cpu_seconds_including_witness_verification':m['batch_result']['query_timing']['cpu_seconds'],
                              'finite_field_group_calls':m['total_algorithm_operations']['group_calls']} for m in methods])
    csv_write(OUT/'fields.csv',[{'field_id':f['field_id'],'rng_seed':f['seed'],'draw_index':f['draw'],
                               'polynomial_coefficients_low_to_high':json.dumps(f['g']),
                               'canonical_polynomial_gp':f['canonical_polynomial_gp'],'field_discriminant':f['field_discriminant'],
                               **{f'roots_at_k{k}':json.dumps(f['roots'][str(k)]) for k in [6,7,12]}} for f in sample['fields']])
    csv_write(OUT/'rank-results.csv',[{'id':r['job']['id'],'field_id':r['job']['field'],'A':r['job']['A'],'B':r['job']['B'],
                                     'status':r['status'],'rank_bounds':json.dumps(r['nf_bounds']),
                                     'elapsed_seconds':r['elapsed_seconds'],'timed_out':r['timed_out'],
                                     'raw_point_vectors_emitted':len(r['nf_raw_vectors_gp'])} for r in ranks['nf']])
    csv_write(OUT/'curve-identities.csv',[{'curve_id':g['identity']['curve_id'],'curve_uid':g['identity']['curve_uid'],
                                         'field_sha256':g['identity']['field_sha256'],'A':g['A'],'B':g['B'],'k':g['k'],'p':g['p'],
                                         'group_order':g['group_order'],'subgroup_order':g['ell'],'cofactor':g['cofactor'],
                                         'G_x':g['G'][0],'G_y':g['G'][1]} for g in raw['public_groups']])
    figures(methods,cohorts)
    big=[c for c in cohorts if c['k']==12]
    table='| Curve rhs | Eligible / 24 | Same seed count | Random relation rate: median [min, max] | Solinas rate | BSGS rate |\n|---|---:|---:|---|---:|---:|\n'
    for c in big:
        r=c['same_seed_count_relation_rate']
        table+=f"| x³{c['A']:+d}x{c['B']:+d} | {c['eligible_fields']} | {r['n']} | {fmt(r['median'])} [{fmt(r['min'])}, {fmt(r['max'])}] | {c['solinas_relation_rate']:.3f} | {c['bsgs_relation_rate']:.3f} |\n"
    rank_text='\n'.join(f"* x³{r['A']:+d}x{r['B']:+d}: rational rank {r['r_Q']}; {r['exact']} exact, {r['interval']} bounded, {r['unfinished_or_error']} unfinished/error descents. {r['certified_positive_rank_gain']}/24 fields have certified positive rank gain; exact-rank histogram {r['exact_rank_histogram']}." for r in rank_summary)
    matched_text='\n'.join(f"* x³{c['A']:+d}x{c['B']:+d}, k=12: {c['same_seed_count_fields']} random fields match the Solinas supplied point count and unknown-log count; {c['same_seed_count_full_recovery_fields']} recover all 16 targets. {c['same_seed_count_fields_more_efficient_than_solinas']} have a higher verified-recovery rate per group call than Solinas." for c in big)
    case=[next(m for m in methods if m['field_id']=='random-12' and (m['A'],m['B'],m['k'])==(a,b,12)) for a,b in MODELS]
    case_text='\n'.join(f"* x³{m['A']:+d}x{m['B']:+d}: random-12 rank {m['rank_bounds'][0]}, {m['distinct_subgroup_points']:,} points, {m['target_recoveries']}/16 recovered, **{m['total_algorithm_operations']['group_calls']:,} group calls**, {m['useful_relations_per_1000_group_calls']:.4f} useful relations/1,000 calls. Exact-K component medians total {sum(nf_cost(m,k) for k in ['NF_PRECOMPUTE','NF_GENERATE','NF_REDUCE']):.3f} CPU s; coordinate-fraction proxy reaches {max(t['values'][5] for t in m['NF_timings'] if t['kind']=='NF_GENERATE')} bits (not canonical height)." for m in case)
    pdf_conclusion=("None of the random-field cases that recovered all 16 targets used fewer group calls than the declared best generic BSGS control." if summary['full_recovery_field_cohorts_cheaper_than_bsgs']==0 else f"{summary['full_recovery_field_cohorts_cheaper_than_bsgs']} random-field cases recovered all 16 targets with fewer group calls than the declared best BSGS control; see paired records for this fixed toy sample.")
    md=f'''# Random cubic fields: seeded matched controls — 2026-10-11 UTC

**Measured observations:** {RUN.name}, EXP-ECDLP-4c6a09, H-ECDLP-4da36f, GOAL-ECDLP-001.
User request: “Run random seed fields.” Raw records are locally committed at `{summary['raw_run_commit']}`.

## Results

Ran **24 distinct cubic number fields**, **48 field/model descents**, and **{len(methods)} eligible field/model/prime relation benchmarks** out of 144 fixed comparisons. The same six groups and 96 public synthetic targets from RUN-ECDLP-6d910b were reused. **{summary['verified_target_recoveries']}/{summary['target_attempts']} repeated field-target attempts** recovered correctly, with {summary['full_recovery_field_cohorts']} complete 16-target batches. These attempts reuse targets and are not independent samples.

{pdf_conclusion} Solinas still recovers 16/16 in every fixed cohort; its unchanged largest-prime costs are 92,149 and 81,266 group calls. Generic table sizes 9, 81, 729, 6,561 and ceil(sqrt(ell)) are now present in every cohort; only previously missing sizes were run. The selected full-recovery generic costs at this prime are {next(c for c in cohorts if c['A']==-3 and c['k']==12)['bsgs_group_calls']:,} and {next(c for c in cohorts if c['A']==7 and c['k']==12)['bsgs_group_calls']:,} calls. Coverage and useful-relation rates must be read with seed count and recovery completeness.

{table}

Rates are independent global equations per 1,000 cached finite-field group calls, including seed projection, table construction and queries. The random rate in this table is restricted to the same supplied point count and unknown-log count as Solinas; it is not matched on field discriminant or exact rank. An unfinished search does not establish that a point or rank gain is absent.

Memory boundary: the selected generic controls at k=12 store {next(c for c in cohorts if c['A']==-3 and c['k']==12)['bsgs_stored_points']:,} and {next(c for c in cohorts if c['A']==7 and c['k']==12)['bsgs_stored_points']:,} points; Solinas stores 729 and 6,561. The stricter equal-entry controls use 729 and 6,561 entries and require **{next(c for c in cohorts if c['A']==-3 and c['k']==12)['same_table_BSGS_group_calls']:,}** and **{next(c for c in cohorts if c['A']==7 and c['k']==12)['same_table_BSGS_group_calls']:,}** calls for 16/16 recoveries. Table size, coefficient payloads, relation matrix storage and exact-K coordinates have different memory costs; no portable byte estimate is asserted.

{matched_text}

![Sampling and comparison](sampling-pipeline.svg)
![Observed relation rates](relation-rates.svg)

## Rank and point supply

{rank_text}

One concrete non-Solinas example is **random-12**: its sampled polynomial is t³+t²−2t−4 and its canonical field polynomial is t³+2t−1 (field discriminant −59). Its exact ranks are **3 and 4**, matching the highlighted Solinas ranks on both curves. It has a degree-one reduction at k=12 and none at k=6,7. This example establishes that those rank gains also occur in a different cubic field; efficiency is measured separately.

{case_text}

Only one sampled field matches the Solinas supplied seed count at k=12 for each model. Its first-curve rate is lower than Solinas and its second-curve rate is higher. This mixed result does not establish a general field ranking; both are slower than equal-entry BSGS for complete recovery.

Every emitted rank bound uses certified class/unit data and checked points. Bounds do not imply an exact rank; a timeout retains the emitted information. If no point vector was emitted, inherited rational points provide an explicitly labeled fallback for coverage. Those fields remain in the sample, but their measured seed set is not asserted to span E(K). At most four seeds are used. The first rational point is anchored, then returned points are added in order, omitting exact/sign duplicates. Raw point vectors are preserved.

![Point supply by supplied seed count](point-supply.svg)

**Derived theory.** Rank describes independent infinite-order directions in E(K). Reduction at a degree-one prime sends checked points to E(F_p); multiplication by h projects into the same cyclic subgroup of prime order ell. In that subgroup all seeds have the form F_i=u_iG. More rank can supply more reduced points, but it does not reveal the u_i.

For P_c=Σc_iF_i, a collision P_c=P_d gives (c-d)·u=0. A target hit Q-jMG=P_c gives c·u-q=-jM modulo ell. A useful relation increases one global modular matrix rank; recovery requires q to be uniquely determined. Seed information is shared across 16 targets. Known-scalar BSGS uses iG and immediately gets q=i+jM from a hit. Rank alone therefore does not establish a scalar-recovery advantage.

The inherited label policy recognizes only seeds equal to G, −G or infinity. Other scalar labels must be learned by the measured collision/hit system, even for rational multiples that a more optimized implementation might recognize cheaply. Comparisons apply to this declared algorithm, with its counters and information boundary, rather than all methods using these fields.

## Sampling, missing reductions and costs

RNG seeds: **2026101102, 2026101103, 2026101104**, eight accepted fields per seed. Draw monic t³+a₂t²+a₁t+a₀ with a₂,a₁ in [-4,4] and nonzero a₀ in [-4,4]. Reject reducible polynomials and duplicate `polredabs` field classes; exclude the prior Solinas, random low-weight and pure-cubic control classes. All used draws and rejections are retained, and the 24 accepted fields pass pairwise `nfisisom` checks. This is a seeded polynomial ensemble with rejection, not a uniform distribution of number fields. No rank, roots or coverage outcomes influenced acceptance.

The fixed primes are p=262,079; 2,097,023; 68,719,472,639. For each original polynomial choose its least modular root. No degree-one prime means unavailable; p and the field sample are never replaced. Roots, including absent roots, appear in [fields.csv](fields.csv), and all unavailable statuses in the benchmark raw result. Multiple embeddings can give different reductions; only the declared least-root embedding is tested.

Exact-K boxes [-4,4]^s were generated with three timing repetitions and reduced entry-for-entry against independent cached finite-field generation. Every eligible completed table agrees. Because reduction is a group homomorphism, reducing the seeds and then adding in F_p yields the same reduced table. Prior descent times and exact-K CPU timers are retained separately; the primary primitive counts use the cached implementation and exclude discovery, exact-K arithmetic and validation. This boundary favors algebraic fields by omitting discovery cost and is not an end-to-end cryptographic runtime claim.

Limits: two curves selected for prior Solinas rank gains, coefficient bound four, at most four supplied points, a fixed 32,768-probe cap per target, and small subgroups. Fields are reused across curves/primes, and canonical rejection induces dependence. Observed ranges describe this sample; no population confidence interval or significance claim is made. Equal point count is not equal rank, saturation, coordinate height or discriminant.

An initial point-export attempt emitted no terminal marker because the GP execution command was on the function-definition line. Every such first attempt was rejected before measurement, and a fresh corrected exporter uses separate lines. These attempts and the resulting all-unavailable intermediate benchmark are preserved; they are not mathematical outcomes.

One Python sampler parse initially failed on PARI's trailing column-vector tilde after successful sampling. The failed script/logs are preserved; a new parser reused the same completed draw output, with no resampling. Any resource or implementation failures are recorded as unavailable computations, not mathematical negative evidence.

## Evidence and reproduction

* [Frozen plan](../../runs/{RUN.name}/plan.json), [sample and rejected draws](../../runs/{RUN.name}/sampling-result.json).
* [Premeasurement generic-control addendum](../../runs/{RUN.name}/generic-controls-addendum.json), [only missing generic table sizes](../../runs/{RUN.name}/additional-generic-controls/raw-result.json).
* [48 descent records](../../runs/{RUN.name}/random-ranks-result.json).
* [Coverage, relation witnesses, cost counters and unavailable comparisons](../../runs/{RUN.name}/benchmark-attempt-02/raw-result.json).
* [Exact-field grids and raw GP processes](../../runs/{RUN.name}/point-preparation-attempt-02/).
* [Methods CSV](methods.csv), [seed-count strata](strata.csv), [discovery/exact-K/cached costs](costs.csv), [field identities](fields.csv), [ranks](rank-results.csv), [complete curve/subgroup/G identities](curve-identities.csv).
* [Summary JSON](summary.json), [prior point/relation report](../point-relations-20261011T0407Z/report.md), [source and reproduction](../../runs/{RUN.name}/README.md).

Source provenance: internal immutable run/source records, copied with SHA-256. No independent scientific review or hypothesis/frontier status change occurred. Historical graphs/reports remain unchanged; fresh figures describe these additive observations. Scoped group-call counts do not update a sealed ECBND bound. GitHub publication remains unavailable under the preceding unchanged authentication failure; local commits and the downloadable archive preserve the work.
'''
    (OUT/'report.md').write_text(md)
    table_typ=[]
    for c in big:
        s=c['same_seed_count_relation_rate']
        table_typ.extend([f"[x³{c['A']:+d}x{c['B']:+d}]",f"[{c['eligible_fields']}/24]",f"[{s['n']}]",f"[{fmt(s['median'])}]",f"[{c['solinas_relation_rate']:.3f}]",f"[{c['bsgs_relation_rate']:.3f}]"])
    rank_typ='\n'.join(f"• x³{r['A']:+d}x{r['B']:+d}: {r['exact']} exact, {r['interval']} bounded, {r['unfinished_or_error']} unfinished/error; {r['certified_positive_rank_gain']}/24 certified rank gains.\\" for r in rank_summary)
    identities='\n'.join(f"#text(size:7pt)[A={g['A']}, B={g['B']}, k={g['k']}, ell={g['ell']}, h={g['cofactor']}\\\nG=({g['G'][0]}, {g['G'][1]})\\\n{g['identity']['curve_uid']}]\n" for g in raw['public_groups'])
    typ=f'''#set page(paper:"a4",margin:15mm,footer:context [#text(size:8pt)[{RUN.name} • toy observations] #h(1fr) #counter(page).display()])
#set text(font:"DejaVu Sans",size:9.1pt)
#set par(leading:.5em)
= Seeded random cubic fields
Measured 2026-10-11 UTC • EXP-ECDLP-4c6a09

*24 distinct fields, 48 rank descents, {len(methods)} eligible matched benchmarks.*
Reused six identical curve/prime/subgroup/generator cases and 96 synthetic target points from RUN-ECDLP-6d910b. {summary['verified_target_recoveries']}/{summary['target_attempts']} repeated field-target attempts recovered correctly; {summary['full_recovery_field_cohorts']} complete 16-target batches. Repeated attempts share targets and fields.

{pdf_conclusion}

== Largest prime: p=68,719,472,639
Independent global equations per 1,000 finite-field group calls. Random medians below match the Solinas supplied-point count and unknown-log count.
#table(columns:(1.1fr,.8fr,.8fr,1fr,1fr,1fr),inset:5pt,
 [Curve rhs],[Eligible],[Matched n],[Random median],[Solinas],[BSGS],{','.join(table_typ)})
The selected generic controls store {big[0]['bsgs_stored_points']:,} and {big[1]['bsgs_stored_points']:,} points; Solinas stores 729 and 6,561. Equal-entry BSGS costs {big[0]['same_table_BSGS_group_calls']:,} and {big[1]['same_table_BSGS_group_calls']:,} calls for 16/16. Storage payloads differ; all declared controls are retained.

#image("sampling-pipeline.svg",width:100%)

== Rank is not a known discrete logarithm
{rank_typ}
Rank supplies independent directions over the number field. After reduction and cofactor projection, all seeds lie in a cyclic group and satisfy F_i=u_iG. Their u_i remain unknown. A collision gives (c−d)·u=0; a hit Q−jMG=Σc_iF_i gives c·u−q=−jM. Only matrix-rank increases count as useful. Recover q only when uniquely implied. BSGS instead stores known iG and gets q=i+jM immediately from a hit.

#pagebreak()
= Observed coverage and useful relations
#image("relation-rates.svg",width:100%)
All eligible random cases are shown; their supplied point counts vary. Dots are individual observations, not confidence intervals. The same 24 fields are reused on two selected curves and three fixed primes. A partial target batch cannot be compared as a complete recovery merely by its total cost.

#image("point-supply.svg",width:100%)
Coefficients in [-4,4], capped at four supplied points. Point representatives need not form an independent or saturated basis. Exact/sign duplicates are removed before selection; reduction can create further dependencies, measured through table collisions.

#pagebreak()
= Scope, evidence and complete group identities
RNG seeds 2026101102, 2026101103, 2026101104: eight accepted fields each. Monic cubic coefficients are drawn from [-4,4], with nonzero constant. Rejections remove reducible and isomorphic duplicate fields, plus prior control classes. All draws are retained. Acceptance never uses rank, roots, points or coverage. This is not a uniform ensemble of number fields.

Least modular root selects one embedding; absent degree-one reductions remain unavailable with no replacement. Timeouts retain emitted rank bounds and checked points. If no descent vector is emitted, coverage uses labeled inherited rational points. Exact-K grids agree entry-for-entry with cached finite-field generation; three exact-K timing repeats and coordinate-bit proxies are retained separately.

Primary work counts include seed projection, finite-field table construction and shared queries. Descent, exact-K arithmetic, and validation are reported separately. No universal CPU conversion or deployed-curve security conclusion is asserted. Fixed toy models were selected for earlier Solinas rank gains; at most four points and 32,768 probes per target were tested. No independent scientific review or official status change occurred.

== Same identities for every eligible method
{identities}
== Reproduction and supporting records
The adjacent report.md links plan.json, sampling-result.json, random-ranks-result.json and benchmark-attempt-02/raw-result.json under {RUN.name}. Fields, ranks, method costs, seed-count strata and full identities are exported to CSV. Editable build_random_report.py generates every figure and this PDF. Raw source, GP scripts, stdout/stderr, per-process timing and source hashes are preserved; provenance is internal immutable run evidence. Initial sampler parse failure is retained and its correction reuses the exact original draw output. Earlier report and raw evidence remain unchanged. GitHub authentication is still unavailable; publication is local with a downloadable archive.
'''
    (OUT/'report.typ').write_text(typ)
    typst.compile(str(OUT/'report.typ'),output=str(OUT/'report.pdf'),root=str(OUT))
    write(OUT/'render-environment.json',{'python':platform.python_version(),'typst':'0.15.0',
          'matplotlib':matplotlib.__version__,'rendered_at_utc':datetime.now(timezone.utc).isoformat(),
          'pdf_sha256':sha(OUT/'report.pdf')})
    print(OUT,sha(OUT/'report.pdf'),flush=True)

if __name__=='__main__':main()
