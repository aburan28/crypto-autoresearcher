#!/usr/bin/env python3
"""Derived visual record; consumes sealed output, never samples new points."""
import hashlib
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/solinas-rare-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/solinas-rare-cache')
for key in ('MPLCONFIGDIR','XDG_CACHE_HOME'):Path(os.environ[key]).mkdir(exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import typst

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2];TASK=REPO/'tasks/solinas_rare_events'
RUN=TASK/'runs/powered-20261012';PUB=TASK/'publication'
COLORS={'selected':'#216589','published':'#a76b2c','random':'#568547'}
NAMES={'selected':'Selected point','published':'Published G','random':'Random rG'}


def read(path):return json.loads(Path(path).read_text())


def save(fig,name):
    fig.savefig(HERE/(name+'.svg'));fig.savefig(HERE/(name+'.png'),dpi=150);plt.close(fig)
    path=HERE/(name+'.svg');path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')


def main():
    analysis=read(RUN/'analysis.json');verification=read(RUN/'verification.json');completion=read(RUN/'completion.json')
    design=read(RUN/'design.json');runtime=read(RUN/'runtime.json');power=read(TASK/'power-plan.json');dataset=read(PUB/'dataset.json')
    extreme=read(PUB/'extreme-windows.json')
    wall=(datetime.fromisoformat(completion['finished'])-datetime.fromisoformat(runtime['started'])).total_seconds()
    cpu=sum(read(p)['cpu_seconds'] for p in (RUN/'records').glob('*.json'))
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    subprocess.run(['dot','-Tsvg',str(HERE/'design.dot'),'-o',str(HERE/'design.svg')],check=True)
    candidates=analysis['candidates'];labels=['P-192 motif threshold','P-224 parity threshold','P-224 run ≥22']
    fig,axes=plt.subplots(1,3,figsize=(10.2,3.4),constrained_layout=True)
    for axis,candidate,label in zip(axes,candidates,labels):
        for i,row in enumerate(candidate['rates']):
            center=row['rate']*1e5;lo,hi=np.array(row['cp_interval'])*1e5
            axis.errorbar(i,center,yerr=[[center-lo],[hi-center]],fmt='o',capsize=4,color=COLORS[row['cohort']])
            axis.annotate(f"{row['hits']:,} hits",(i,hi),xytext=(0,6),textcoords='offset points',ha='center',fontsize=8)
        axis.set_xticks(range(3),['Selected','Published','Random']);axis.set_title(label,loc='left',fontsize=10)
        axis.set_ylabel('Events per 100,000 windows');axis.grid(axis='y',alpha=.2)
        axis.set_xlim(-.5,2.5);axis.set_ylim(0,max(r['cp_interval'][1] for r in candidate['rates'])*1e5*1.2)
    fig.suptitle('powered-20261012 — marginal CP intervals, separate nominal 99.9% family (9 rates)\n1,048,576 windows/arm for motif/parity; 4,194,304 for run ≥22',fontsize=10)
    save(fig,'rare-rates')
    fig,axis=plt.subplots(figsize=(8.8,4.3),constrained_layout=True)
    for i,arm in enumerate(COLORS):
        rows=[r for r in analysis['tail_spectrum'] if r['cohort']==arm]
        for row in rows:
            x=row['threshold']+(i-1)*.12;lo,hi=row['cp_interval'];center=row['rate']
            if row['hits']:
                axis.errorbar(x,center,yerr=[[center-lo],[hi-center]],fmt='o',capsize=3,color=COLORS[arm])
            else:axis.plot(x,hi,marker='v',color=COLORS[arm],markersize=6)
        axis.plot([],[],marker='o',linestyle='none',color=COLORS[arm],label=NAMES[arm])
    benchmark=[r for r in analysis['tail_spectrum'] if r['cohort']=='selected']
    axis.plot([r['threshold'] for r in benchmark],[r['fair_coin_reference'] for r in benchmark],ls='--',color='#333',label='IID fair-coin reference only')
    axis.set_yscale('log');axis.set_xlabel('Identical consecutive x-bit-64 run threshold (points)');axis.set_ylabel('Event probability per 256-point window')
    axis.set_xticks([r['threshold'] for r in benchmark]);axis.grid(alpha=.2);axis.legend(fontsize=8)
    axis.set_title('powered-20261012 — 4,194,304 windows/arm\n24 corrected CP intervals; triangles are zero-hit upper bounds',loc='left',fontsize=10)
    save(fig,'longrun-tails')
    fields=analysis['ordinary_fields'];tests=analysis['primary_tests']
    fig,axes=plt.subplots(1,2,figsize=(10.2,3.7),constrained_layout=True)
    longrun=candidates[2]['rates'][0]
    for i,arm in enumerate(('R','C')):
        rows=[r for r in fields if r['arm']==arm]
        axes[0].scatter(i+np.linspace(-.12,.12,len(rows)),[r['rate']*1e5 for r in rows],s=18,alpha=.6,color=['#a76b2c','#568547'][i],label=arm+' fields')
        axes[0].plot(i,np.mean([r['rate'] for r in rows])*1e5,marker='D',color='#222')
    axes[0].axhline(longrun['rate']*1e5,color=COLORS['selected'],ls='--',label='Selected S curve rate')
    axes[0].set_xticks([0,1],['32 R fields','32 C fields']);axes[0].set_ylabel('Run ≥22 events per 100,000 windows');axes[0].legend(fontsize=7)
    axes[0].set_title('65,536 windows per ordinary model',loc='left',fontsize=10);axes[0].grid(axis='y',alpha=.2)
    for i,row in enumerate(tests[-2:]):
        center=row['difference']*1e5;lo,hi=np.array(row['interval'])*1e5
        axes[1].errorbar(center,i,xerr=[[center-lo],[hi-center]],fmt='o',color=COLORS['selected'],capsize=4)
    axes[1].set_yticks([0,1],['S − R mean','S − C mean']);axes[1].axvline(0,color='#555',ls='--')
    axes[1].set_xlabel('Rate difference per 100,000 windows');axes[1].set_title('Corrected approximate Welch intervals',loc='left',fontsize=10);axes[1].grid(axis='x',alpha=.2)
    fig.suptitle('powered-20261012 — coefficients and step x matched; group orders unmatched\nField is the control unit; fixed S curve is not a Solinas-prime population',fontsize=10)
    save(fig,'ordinary-controls')
    fig,axis=plt.subplots(figsize=(8.8,4.1),constrained_layout=True)
    rows=[r for r in power['rows'] if r['candidate']==candidates[2]['id']]
    for q in sorted({r['control_rate'] for r in rows}):
        sub=[r for r in rows if r['control_rate']==q]
        axis.plot([r['target_ratio'] for r in sub],[r['exact_model_power']*100 for r in sub],marker='o',label=f'Baseline {q:.3g}/window')
    axis.set_xlabel('Target / control event-rate ratio');axis.set_ylabel('Modeled rejection power (%)');axis.set_ylim(0,105);axis.grid(alpha=.2);axis.legend(fontsize=8)
    axis.set_title('Prospective power for 4,194,304 paired windows\nIndependent-arm-flag planning model; exact paired-test alpha =0.001/11',loc='left',fontsize=10)
    save(fig,'planning-power')
    rows=[]
    for candidate,label in zip(candidates,labels):
        for row in candidate['rates']:
            rows.append(f"| {label} | {NAMES[row['cohort']]} | {row['hits']:,}/{row['windows']:,} | {row['rate']*1e5:.4f} | [{row['cp_interval'][0]*1e5:.4f}, {row['cp_interval'][1]*1e5:.4f}] |")
    rates_table='\n'.join(rows)
    test_table='\n'.join(f"| {r['id']} | {r.get('a_only','—')}/{r.get('b_only','—')} | {r.get('p_two_sided_exact',r.get('p_two_sided_approx')):.6g} | {r['passes_family_threshold']} |" for r in tests)
    tail_table='\n'.join(f"| {r['threshold']} | {r['cohort']} | {r['hits']:,} | {r['rate']:.8g} | [{r['cp_interval'][0]:.8g}, {r['cp_interval'][1]:.8g}] | {r['fair_coin_reference']:.8g} |" for r in analysis['tail_spectrum'])
    totals=verification['totals'];passed=sum(r['passes_family_threshold'] for r in tests)
    longrun_rates=candidates[2]['rates'];selected=longrun_rates[0];random=longrun_rates[2]
    ratio_interval=[selected['cp_interval'][0]/random['cp_interval'][1],selected['cp_interval'][1]/random['cp_interval'][0]]
    identity_lines='\n'.join(f"- {m['case']}: `{m['anchor_identity']['curve_uid']}`; subgroup order N={m['curve']['N']}; published G={tuple(m['published_G'])}." for m in design['inputs']['candidates'][:2])
    text=f'''# Powered rare point-pattern study — 12 October 2026

**Observations only.** This report records the user-requested pursuit of the
remaining rare-effect question. It changes no official research status and
makes no ECDLP security, attack-cost, or prime-family causal claim. Run ID:
`powered-20261012`. {passed} of 11 predeclared comparisons crossed their
corrected threshold; see all counts and limits below. A threshold crossing is
a replication lead; no crossing closes only the measured event-rate scope.

## Measured scope and controls

**Measured:** {completion['point_observations']:,} point observations in
{totals['windows_with_all_scores_replayed']:,} 256-point window observations;
640 requested/completed jobs; {completion['actual_failures']} failed attempts.
There are 10,485,760 independent-start draws; named cohorts share their start
within each three-arm window. Points inside a window are dependent and the
observation count does not mean distinct or independent points.
Elapsed wall time was {wall:,.2f}s; summed measured job CPU time was
{cpu:,.2f}s. Host platform: `{runtime['platform']}`. These are runtime facts,
not performance-advantage or ECDLP-cost measurements.

Three historical candidates from [PR #2107](https://github.com/aburan28/crypto-autoresearcher/pull/2107)
have selected-point, actual published-generator, and fresh random rG cohorts.
They use precisely the same uniformly drawn Q=kG per matched window. P-192
motif and P-224 parity candidates each have 1,048,576 windows/cohort; the P-224
22-bit-run candidate has 4,194,304/cohort. Additional controls are 32 R and32 C
ordinary-prime models, each with65,536 uniform affine starts. All have A=-3,
the same B integer modulo p, and step x=2^64+2. Selection uses liftability,
not event scores. Full group/step orders are not matched. R/C primes reuse the
prior pools; they are not new independent primes.

![Fixed study design](design.svg)

## Derived event-rate observations

Rates below are events per100,000 windows. Intervals are two-sided exact
Clopper-Pearson with Bonferroni alpha0.001/9, a separate nominal at-least-99.9%
family under independent windows. A zero count has a nonzero upper bound.

| Event | Cohort | Hits/windows | Rate/100,000 | Corrected CP interval/100,000 |
| --- | --- | ---: | ---: | ---: |
{rates_table}

![All three cohort rates](rare-rates.svg)

The nine paired comparisons use exact conditional McNemar tests on discordant
windows. Two field comparisons use approximate Welch intervals on S chunk
rates and ordinary field rates. Primary family alpha0.001; per-test threshold
{analysis['primary_family']['per_test_alpha']:.9g}. Bonferroni coverage is
nominal for the field approximation, not an exact finite-sample guarantee.

| Comparison | A-only/B-only | Two-sided p | Crosses primary threshold |
| --- | ---: | ---: | --- |
{test_table}

Exact paired p-values preserve the empirical within-window dependence.
Conservative difference intervals in `analysis.json` subtract the simultaneous
marginal CP bounds; they are not exact paired-difference intervals.
**Derived:** selected/random run≥22 rate ratio is
{selected['rate']/random['rate']:.4f}, with conservative interval
[{ratio_interval[0]:.4f}, {ratio_interval[1]:.4f}] from the already declared
simultaneous marginal bounds. This constrains this specific generator contrast
and event; it is not a prime-family or ECDLP conclusion.

## Measured long-run spectrum and ordinary-prime controls

The spectrum was declared before sampling. Its 24 corrected CP intervals form
a separate exploratory nominal99.9% family. The IID fair-coin line is an exact
integer-DP reference, not a premise that elliptic-curve bits are IID.

![Tail probabilities and bounds](longrun-tails.svg)

| Run threshold | Cohort | Hits | Probability/window | Corrected CP interval | Fair-coin reference |
| --- | --- | ---: | ---: | ---: | ---: |
{tail_table}

**Measured rare example:** one selected-point window contained32 consecutive
zero bits, starting at point offset160. The largest observed run lengths were
{extreme['max_observed_longrun_by_selected_published_random']} for selected,
published, random respectively. This descriptive characterization adds no
test or sample. At threshold32, the simultaneous CP intervals include the
fair-coin reference in all three arms. A single selected hit versus zero other
hits does not resolve a generator effect. Its complete coordinates and public
start/step data are preserved in `publication/extreme-windows.json` and the
raw event frame; all are covered by the separate verifier.

![Ordinary field controls](ordinary-controls.svg)

The ordinary comparison unit is the field, not billions of pooled points.
There are32 fields/pool and only one fixed S prime for this candidate.
Different group orders, subgroup orders and lifted step y limit causal
interpretation. The comparisons are conditional on the declared models and
the reused prime pools. A general effect of sparse prime representation is
not identified by these controls alone.

## Theory and remaining rare-effect scope

**Derived:** On a finite prime-order curve, each nonzero generator traverses
the same full point set. Uniform Q makes the single-point marginal invariant
under translation, up to the prospectively excluded infinity/start convention.
Changing H changes the ordering and joint distribution of consecutive points;
it can therefore change bit-run, parity and motif frequencies without changing
the full-orbit marginal point coverage. The sparse Solinas modulus is a field
representation and arithmetic property, not evidence of an ECDLP advantage.

The original deterministic prefix outliers still exist. This fresh study
measures their descriptors' **global random-start rates**, not the probability
of revisiting the exact historical start. A phenomenon confined to a few
specific starts in a ~2^192 or~2^224 group can be real and essentially invisible
to any feasible uniform sample. Sampling design depends on event prevalence
and effect size, rather than a fixed percentage of the entire field.

**Derived prospective planning:** At baseline3e-5, a doubled long-run event
rate has about99.54% modeled power with4,194,304 paired windows. At baseline
1e-6, doubling has about0.057% power. These figures use independent arm flags
for planning; correlated observed arms can change power. Motif/parity have
about97.83% modeled power for doubling a1e-4 baseline. No interval or negative
test excludes every higher-order, alternate-coordinate or rarer effect.

![Prospective power limits](planning-power.svg)

The primary, marginal-rate, and exploratory-tail families are separate.
Their simple union has at most0.003 nominal error (nominal99.7%), subject to
the two Welch approximations; the report does not call all outputs a single
99.9% family. Old PR2107 families are not combined with this new family.

Next discriminating work is fresh-seed replication of any threshold crossing;
for events below the powered regime, accumulate additional preplanned seeds
with the included standalone runner, or define a separate prospective
structured-start study for the exact historical prefixes. These are future
tasks, not results of this run. No adaptive post-outcome enlargement occurred.

## Independently checked implementation and preserved data

**Measured native validity:** all{totals['online_oncurve_checks']:,} points
were finite and on-curve. **Separate Python verification:** every stored
window's three scores was recomputed from its complete bit string;
{totals['independent_coordinate_checks']:,} rare/witness point coordinates,
{totals['independent_affine_transitions']:,} affine transitions,
{totals['independent_starts']:,} start draws,
{totals['independent_scalar_multiplications']:,} public scalar multiplications,
and{totals['universal_relation_checks']:,} universal x-triple relations passed.
The verifier inventories every rare frame and checks its paired arms.
Four engineering tests passed, including full-coordinate hashes, independent
point arithmetic, planted/negative bit sequences, exact DP brute force,
write-once resume and corrupt-data refusal. This is independent arithmetic in
one session, not a separate research review.

Compact retention includes **every measured bit64 string**, all three exact
integer scores, all fresh public generator scalars, full256-point coordinates
for every threshold-event window (all paired arms), four predetermined witness
windows per chunk, and SHA256 of every full transient coordinate stream. Most
non-event full xy streams are not stored; seeds/source regenerate them.
`--full-coordinates` prospectively retains every coordinate on a large disk.
Do not describe the compact dataset as a saved survey of all coordinate bits.

Lossless archive: `{Path(dataset['archive']).name}`; {dataset['archive_bytes']:,}
bytes; SHA256 `{dataset['archive_sha256']}`. All{dataset['file_count']:,}
entries were checked against their SHA256 and byte count after compression.
Earlier raw datasets and reports remain immutable. The repository commits
small records, full manifests, protocol, source and analysis; the large ZIP is
a local download artifact, not asserted to be uploaded to any cloud service.

## Reproduce and provenance

Frozen scientific source commit:
[`{runtime['source_commit']}`](https://github.com/aburan28/crypto-autoresearcher/tree/{runtime['source_commit']}/tasks/solinas_rare_events).
The source was pushed before launch. Seed:
`{design['config']['seed']}`. Python{runtime['python'].split()[0]},
NumPy{runtime['numpy']}, SciPy{runtime['scipy']}; {runtime['openssl']}; workers3.
Runtime dirty status was `{runtime['dirty_tree']}` because the newly created
run records were untracked; the sampling source was committed and clean.
All frozen source-file hashes are in `design.json`; exact command, compiler
stdout/stderr, job CPU/wall facts and source copies are preserved. Runtime
facts are not performance-advantage claims. Unexposed model/usage fields are null.

Run `python research.py --output /large-disk/study`, then `python verify.py`
and `python analyze.py` with that output path. A new public seed and a new
directory enable independent accumulation without an agent. Scripts refuse
source/config changes on resume and preserve failed attempt artifacts.
The portable runner bundle and README include all public models and dependencies.

**Internal evidence links:** [protocol](../../../tasks/solinas_rare_events/PROTOCOL.md),
[analysis](../../../tasks/solinas_rare_events/runs/powered-20261012/analysis.json),
[verification](../../../tasks/solinas_rare_events/runs/powered-20261012/verification.json),
[completion](../../../tasks/solinas_rare_events/runs/powered-20261012/completion.json),
[power plan](../../../tasks/solinas_rare_events/power-plan.json),
[dataset manifest](../../../tasks/solinas_rare_events/publication/dataset-manifest.json).
Exact curve/subgroup parameters and full UIDs are in `inputs.json`; no curve
identity is inferred from bit length. Previous report and diagram at PR2107
and the canonical `knowledge/frontiers/ecdlp/` inventory/schema were checked;
no verified mechanism, attack cost, or official scientific state changed, so
historical diagrams and canonical frontier rows remain unchanged.

Named curve identities:

{identity_lines}

Sources are internal immutable experiment artifacts read in this session;
no external literature claim or exhaustive novelty assertion is made.
'''
    (HERE/'report.md').write_text(text)
    def escaped(value):return str(value).replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')
    def paragraph(value):return '#par("'+escaped(value)+'")\n'
    rate_lines='\n'.join(f"{label}: "+'; '.join(f"{r['cohort']} {r['hits']}/{r['windows']:,} ({r['rate']*1e5:.3f}/100,000)" for r in c['rates']) for c,label in zip(candidates,labels))
    source='''#set page(paper: "a4", margin: (x: 17mm, y: 16mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9.3pt)
#set par(leading: 0.65em)
#set heading(numbering: none)
= Powered rare point-pattern study
'''
    source+=paragraph('12 October 2026 | run powered-20261012 | observations only; no scientific-state transition')
    source+=paragraph(f"{completion['point_observations']:,} point observations; {totals['windows_with_all_scores_replayed']:,} 256-point window observations; 640/640 jobs; {completion['actual_failures']} failures. {passed}/11 predeclared comparisons cross the corrected threshold.")
    source+=paragraph(f"Elapsed wall {wall:,.2f}s; summed measured job CPU {cpu:,.2f}s. Host platform: {runtime['platform']}. Runtime facts only; no speedup or ECDLP-cost claim.")
    source+=paragraph('Same uniform Q in selected, actual published, and fresh random-generator cohorts. 64 ordinary-prime models match A=-3, B and step x; group orders are unmatched. Points within each window are dependent.')
    source+='#image("design.svg", width: 100%)\n'
    source+=paragraph('Locked seed: '+design['config']['seed']+'. Source committed and pushed before launch: '+runtime['source_commit']+'. Exact parameters and curve UIDs: tasks/solinas_rare_events/inputs.json.')
    source+='#pagebreak()\n= Event rates and uncertainty\n'
    source+=paragraph(rate_lines)
    source+='#image("rare-rates.svg", width: 100%)\n'
    source+=paragraph('Intervals: separate nine-rate CP family, Bonferroni alpha0.001/9. Primary tests: nine exact paired McNemar comparisons plus two approximate field comparisons; per-test alpha0.001/11. Tests with no crossing do not establish a zero effect; all outputs are scoped to the measured descriptors.')
    source+=paragraph('Full counts, discordant pairs, p-values and conservative difference intervals: tasks/solinas_rare_events/runs/powered-20261012/analysis.json. Ordinary comparisons use field means, not pooled point counts.')
    source+=paragraph(f"Derived selected/random run≥22 rate ratio: {selected['rate']/random['rate']:.4f}; conservative simultaneous-marginal interval [{ratio_interval[0]:.4f}, {ratio_interval[1]:.4f}]. This is conditional on this event and curve/point contrast.")
    source+='#pagebreak()\n= Long-run tails and field controls\n#image("longrun-tails.svg", width: 100%)\n'
    source+=paragraph('Eight fixed thresholds ×three cohorts; separate24-interval CP family at alpha0.001. Downward triangles mark zero-hit upper bounds. The fair-coin line is a benchmark, not an IID assumption for point bits.')
    source+=paragraph('One selected-point window contained32 consecutive zero bits. Maxima: selected32, published31, random30. Threshold32 intervals include the fair-coin reference in all arms; this one hit does not resolve a generator effect. Full raw frames and descriptive start data are preserved.')
    source+='#image("ordinary-controls.svg", width: 100%)\n'
    source+=paragraph('Each ordinary field has65,536 independent affine starts; 32 fields per pool. The S curve has256 chunks of16,384 starts. Welch intervals are approximate, conditional on a fixed S curve and reused ordinary-prime pools.')
    source+='#pagebreak()\n= What the experiment can detect\n#image("planning-power.svg", width: 100%)\n'
    source+=paragraph('At baseline3e-5 per window, doubling has99.54% modeled power. At baseline1e-6, doubling has only0.057% modeled power. These are prospective independent-arm planning assumptions; actual pair dependence may change power.')
    source+=paragraph('Every generator on the prime-order named curve visits the same full point set; it changes the walk order. Consecutive-bit events concern that ordering. Solinas sparsity alone does not establish ECDLP resistance or a solver advantage.')
    source+=paragraph('Historical deterministic outliers still exist. Random-start measurements estimate global event prevalence, not revisiting a specific known prefix. A phenomenon confined to a few starts in a2^192 or2^224 group is essentially invisible to a feasible uniform sample. Sample size follows prevalence, effect size, uncertainty and power, not a fixed field-coverage percentage.')
    source+=paragraph('The primary, marginal-rate and tail families are separate. Their union is nominal99.7%, subject to Welch approximation. No result excludes all alternate-bit, alternate-coordinate, higher-order or substantially rarer effects. Future work: fresh-seed replication or a separately frozen structured-start study.')
    source+='#pagebreak()\n= Verification, retention and reproduction\n'
    source+=paragraph(f"Native online checks: {totals['online_oncurve_checks']:,} finite on-curve point observations. Separate Python: {totals['windows_with_all_scores_replayed']:,} score-replayed windows; {totals['independent_coordinate_checks']:,} coordinate checks; {totals['independent_affine_transitions']:,} affine transitions; {totals['independent_starts']:,} starts; {totals['independent_scalar_multiplications']:,} scalar multiplications; {totals['universal_relation_checks']:,} x-triple-law checks. No separate research reviewer has signed these observations.")
    source+=paragraph('Retained: every measured bit string and exact score; public random-generator scalars; complete rare/witness coordinate frames; per-file and complete transient coordinate-stream hashes. Most non-event full coordinates are regenerated from seeds, rather than stored. Full-coordinate mode is available prospectively for a large filesystem.')
    source+=paragraph(f"Lossless compact archive: {Path(dataset['archive']).name}; {dataset['archive_bytes']:,} bytes; {dataset['file_count']:,} entries independently checked after compression. SHA256: {dataset['archive_sha256']}. Earlier datasets and reports are immutable. No cloud upload is asserted.")
    source+=paragraph('Reproduce with research.py --output /large-disk/study, then verify.py and analyze.py. No agent, key or service credential is needed. Choose a new public seed and new directory to accumulate a new fixed run. Changed source/config on resume and corrupt artifacts are refused; failed attempts are preserved.')
    source+=paragraph(f"Runtime: Python{runtime['python'].split()[0]}, NumPy{runtime['numpy']}, SciPy{runtime['scipy']}, {runtime['openssl']}; workers3. Exact command/commit/dirty state, source copies, compiler logs and CPU/wall facts are retained; unexposed model/usage metadata is null. Runtime facts are not attack-cost or performance claims.")
    source+=paragraph('Evidence: tasks/solinas_rare_events/{PROTOCOL.md,inputs.json,power-plan.json}; runs/powered-20261012/{design.json,completion.json,analysis.json,verification.json}; publication/{dataset.json,dataset-manifest.json,records.jsonl.gz}. Prior evidence: PR2107, source ef9e09d96fa845f0a1614a421e47a5a25b950256. Sources are internal artifacts read in this session; no external literature novelty claim. Canonical ECDLP frontier and prior graph inventory checked; no affected mechanism or official scientific status to change.')
    (HERE/'report.typ').write_text(source)
    typst.compile(str(HERE/'report.typ'),output=str(HERE/'report.pdf'),root=str(HERE))
    print(json.dumps({'report':str(HERE/'report.pdf'),'primary_threshold_crossings':passed},sort_keys=True))


if __name__=='__main__':main()
