"""Generate the readable report and uncertainty plots from completed measurements."""
import json
import math
import os
import subprocess
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR','/tmp/solinas-cohort-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/solinas-cohort-cache')
os.environ['OPENBLAS_NUM_THREADS']='1'
for key in ('MPLCONFIGDIR','XDG_CACHE_HOME'):Path(os.environ[key]).mkdir(exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import typst

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
RUN=REPO/'tasks/solinas_generator_cohorts/runs/cohorts-20261012'


def main():
    analysis=json.loads((RUN/'analysis.json').read_text());receipt=json.loads((RUN/'receipt.json').read_text())
    verification=json.loads((RUN/'verification.json').read_text());environment=json.loads((RUN/'environment.json').read_text())
    inputs=json.loads((RUN/'inputs.json').read_text());comparisons=analysis['comparisons']
    subprocess.run(['dot','-Tsvg',str(HERE/'workflow.dot'),'-o',str(HERE/'workflow.svg')],check=True)
    plt.rcParams.update({'font.size':8,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,axes=plt.subplots(3,2,figsize=(7.2,7.8),constrained_layout=True)
    filters=[('walk',False,'Ordered walks: coordinate / bit correlation'),('walk',True,'Ordered walks: x-bin dispersion'),
             ('iid',False,'Independent multiples: x/y correlation'),('iid',True,'Independent multiples: x-bin dispersion'),
             ('random-model affine points',False,'Random models: x/y correlation'),('random-model affine points',True,'Random models: x-bin dispersion')]
    for axis,(population,dispersion,title) in zip(axes.flat,filters):
        rows=[r for r in comparisons if r['population']==population and (r['metric']=='x_bin_dispersion')==dispersion]
        for i,row in enumerate(rows):
            lo,hi=row['interval'];color='#2b618e' if row['case']=='P-192' else '#a2602b'
            axis.errorbar(row['difference'],i,xerr=[[row['difference']-lo],[hi-row['difference']]],fmt='o',color=color,capsize=3,ms=4)
        labels=[r['case'].replace('P-','P')+' '+({'x_lag1':'x lag1','bit64_lag1':'bit64','bit96_lag1':'bit96','x_bin_dispersion':'','xy_correlation':''}[r['metric']])+
                (' / '+r['right'].split()[0] if population=='random-model affine points' else '') for r in rows]
        axis.set_yticks(range(len(rows)),labels);axis.invert_yaxis();axis.axvline(0,color='#555',ls='--',lw=.8)
        axis.grid(axis='x',alpha=.18);axis.set_title(title,loc='left',fontsize=9,fontweight='bold')
        axis.set_xlabel('Mean difference (dimensionless)')
    fig.suptitle('Generator and field cohorts — nominal 99.9% simultaneous intervals',fontsize=11,fontweight='bold')
    fig.savefig(HERE/'primary-comparisons.svg');fig.savefig(HERE/'primary-comparisons.png',dpi=150);plt.close(fig)
    for path in (HERE/'primary-comparisons.svg',HERE/'workflow.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    exclusions=[r for r in comparisons if r['excludes_zero']]
    finding=('None of the 20 corrected intervals excludes zero. These data did not resolve a mean difference in the prespecified features.' if not exclusions else
             f'{len(exclusions)} of 20 corrected intervals exclude zero: '+ '; '.join(r['case']+' '+r['population']+' '+r['metric']+' vs '+r['right'] for r in exclusions)+'. These observations need independent confirmation before mechanism interpretation.')
    table='\n'.join(f"| {r['case']} | {r['population']} | {r['metric']} | {r['right']} | {r['difference']:.6g} | [{r['interval'][0]:.6g}, {r['interval'][1]:.6g}] | {r['left_units']}/{r['right_units']} | {r['approximate_90pct_power_detectable_difference']:.5g} |" for r in comparisons)
    identities='\n'.join(f"- {a['case']}: `{a['identity']['curve_id']}`; full UID `{a['identity']['curve_uid']}`. p={a['p']}; A={a['A']}; B={a['B']}; n={a['N']}; h=1; G={a['G']}." for a in inputs['anchors'])
    rare=[(q,math.ceil(math.log1p(-.999)/math.log1p(-q))) for q in (.01,.001,.0001,.000001)]
    raretable='\n'.join(f'| {q:g} | {n:,} |' for q,n in rare)
    diagnostics='\n'.join(f"| {d['case']} | {d['units']} | {d['shuffled_mean_x_lag1']:.5g} | [{d['shuffled_99pct_interval'][0]:.5g}, {d['shuffled_99pct_interval'][1]:.5g}] | {d['sorted_positive_min_x_lag1']:.7f} | {d['u2_mean_absolute_x_lag1_change']:.5g} |" for d in analysis['diagnostics'])
    graphpaths=sorted(str(p.relative_to(REPO)) for directory in
                      [REPO/'docs/reports/solinas-point-distribution-20261012',REPO/'docs/reports/ec-relation-ml-20261011',REPO/'knowledge/frontiers/ecdlp']
                      for p in directory.rglob('*') if p.suffix in ('.dot','.mmd','.svg','.typ','.pdf'))
    inventory={'checked_materialized_graph_sources_and_forms':graphpaths,'canonical_update':'none',
               'reason':'The new generator/point mean observations establish no isogeny, endomorphism, rank, recovery, or security mechanism edge. Preserve historical reports and evidence.',
               'retrieval_scope':'Exact internal immutable inputs and materialized reports/frontier directory; no claimed exhaustive literature or knowledge-index search.'}
    (HERE/'graph-inventory.json').write_text(json.dumps(inventory,sort_keys=True,indent=2)+'\n')
    markdown=f'''# Solinas primes: random and published generator cohorts

2026-10-12. Measured observations from `cohorts-20261012`, frozen source
`{environment['git_commit']}`. Derived report, with no hypothesis promotion.

**Measured:** {finding} This concerns tested mean features on two exact standard
curves and the specified random-model controls. It does not establish equality,
exclude rare or higher-order patterns, or measure relative ECDLP resistance.

## What the two cohorts mean

**Derived:** the prime defines F_p, a field of residues. A and B then define
the curve y²=x³+Ax+B. A generator G picks an ordering of its group of points.
These are three choices. P-192 uses p=2^192-2^64-1; P-224 uses
p=2^224-2^96+1. Their group orders n are different integers from p. Both exact
standard curves have prime n and cofactor one.

**Derived:** on a prime-order curve every H=[r]G with 1≤r<n is a generator.
Multiplication by r permutes the nonzero residues modulo n. Therefore uniform
k in 1..n-1 makes [k]G and [k]H have exactly the same point distribution. This
does not depend on numerical coordinate conventions. Uniform-multiple samples
are calibration checks for this identity. In an ordered walk the next point is
Q+G or Q+H, so the ordering can depend on the generator. Its consecutive points
are dependent and need block-level inference.

**Measured design:** per standard curve and generator cohort, 2,560 paired
random-start walks ×4,096 =10,485,760 points, plus 256 paired independent-multiple
blocks ×1,024 =262,144 points. Each random cohort block uses a fresh H=[r]G.
The published cohort uses the exact official G and the same public scalar
schedule. Random-model baseline: 512 models at each fixed S prime; 144 R fields
and 144 C fields per case, four models/field, 1,024 uniform affine points/model.
Controls are same-bit primes within ±1%; C also matches p mod 12. All random
models remain included, without order selection. Those points are not labelled
generators of potentially noncyclic groups. These reused fields are 578 distinct
primes, including the two fixed standard primes; they are not new field draws.

**Identification limit:** official G exists on its own standard curve. Its
coordinates cannot be assumed valid on random-prime curves. Published-vs-random
G comparisons hold the standard curve fixed; random-prime controls address the
random-model population separately. This does not identify a general prime-by-G
interaction. Standard coefficients, prime group order, and generator selection
can all differ from arbitrary models. C does not match the enormous 2-adic
valuations of P-192 p+1 or P-224 p-1.

![Frozen measurement and data pipeline](workflow.svg)

## Sampling size: fraction, coverage, precision, and power

**Derived:** n_sample/N is called the *sampling fraction*. A fixed fraction of
a 192-bit population is infeasible and is not necessary for estimating broad
distribution statistics. For simple random sampling without replacement the
finite-population correction is sqrt((N-n_sample)/(N-1)); it is effectively one
at these scales. This correction does not turn dependent walks into iid draws.
For P-192, p is about 6.28×10^57. Ten million points are a fraction about
1.6×10^-51 of that size; the number of independent walks is 2,560.

**Derived:** *power analysis* sizes a test for a chosen effect, variance,
confidence and power. *Rare-event detection* sizes a sample for a recognizable
event with probability q. With independent draws, at least one event at 99.9%
confidence needs ceil(log(0.001)/log(1-q)) draws:

| Event probability q per independent draw | Draws for ≥99.9% detection |
|---:|---:|
{raretable}

These are hypothetical recognizable events, not measured failures. For rare
generator types the draw is a generator, not one of its walk points; for rare
field types it is a new field. If q scales as 1/p, sample size scales as p.
An effect occurring in one point out of the whole field will not be located
by a few million points. Uniform marginal distributions are equal across
generators by the bijection above, irrespective of sample size. A targeted
coefficient or scalar family needs a targeted prospective cohort.

## Prespecified comparisons and uncertainty

Walks: x lag-1 correlation; exact x bits64/96 lag-1 correlations; 32-bin x
dispersion (Pearson chi-square divided by 31). Independent multiples and random
models: x-bin dispersion and x/y correlation. The latter measures a mean
feature, not all joint coordinate dependence. All values are dimensionless.

Two cases ×(4 walk +2 iid +4 field)=20 comparisons. Individual nominal confidence
99.995%, Bonferroni familywise nominal confidence 99.9%. Paired Student intervals
on generator blocks; Welch intervals on S random-model draws versus control
field means. They are approximate intervals, not guaranteed exact finite-sample
coverage. S has one fixed prime per case; 512 models do not create 512 primes.
Official G is one fixed instance; 2,560 starts do not create 2,560 official Gs.
Columns Δ90% are variance-based approximate 90%-power detectable mean differences
with this multiplicity. They do not express sensitivity to every pattern.

![Primary results and corrected uncertainty](primary-comparisons.svg)

| Case | Population | Metric | Control | Difference | Corrected interval | Independent units L/R | Δ90% |
|---|---|---|---|---:|---|---:|---:|
{table}

## Calibration and coordinate controls

First 32 blocks/cohort/case (64 per case): shuffle identical point sets as a
negative ordering control; sort x as a deliberately correlated positive control;
map the same points by (x,y)->(4x,8y) into the isomorphic model
(A,B)->(16A,64B). These are descriptive diagnostics outside the primary family.
The isomorphism preserves the group but can change numeric coordinate features.

| Case | Blocks | Shuffled mean x lag1 | Diagnostic 99% interval | Minimum sorted lag1 | Mean absolute lag1 change under u=2 |
|---|---:|---:|---|---:|---:|
{diagnostics}

**Software-verified:** all {verification['all_points_on_curve']:,} points satisfy
their exact curve equations; all {verification['records']:,} raw-file checksums
and features replay correctly; {verification['independent_walk_transition_checks']:,}
dispersed transitions and {verification['independent_scalar_multiplications']:,}
scalar multiplications match separate affine integer arithmetic. Isomorphic
checks cover {verification['isomorphic_point_checks']:,} transported points.
This is same-session software verification, not independent scientific review.
Seven prelaunch unit tests and restart/corruption/configuration/concurrent-writer
engineering checks passed. No failed job was silently discarded.

## A script you can run over time

**Implemented and exercised:** standalone Linux/Python/OpenSSL runner with public
deterministic seeds, no model/network requirement during execution, fixed queue,
atomic immutable chunk publication, checksums and restart. Every batch preserves
its executable source. `run_batch.sh OUTPUT SEED WORKERS` runs measurement,
verification and analysis. A changed source/config refuses resume; use the
frozen `source/` copy to replay an old batch. A new seed needs a new directory.

```bash
bash bootstrap.sh
bash run_batch.sh /large-filesystem/ec-study/batch-0001 batch-0001 3
.venv/bin/python catalog.py --root /large-filesystem/ec-study --output /large-filesystem/ec-study/catalog.sqlite
```

Use cron, systemd or your compute queue for future fixed batches. The SQLite
catalog deduplicates identical seed/design copies and retains field/model/G
identities, supporting clustered statistical analysis or ML splits. All exact
raw coordinates remain on the large filesystem. A default batch is
{receipt['raw_bytes']:,} bytes of coordinates plus metadata. Measured run wall
time {receipt['final_invocation_wall_seconds']:.1f}s and summed job CPU time
{receipt['summed_job_cpu_seconds']:.1f}s are descriptive timings on this machine,
not a computational security bound.

New seeds add point/start/generator replicates at fixed inputs; they do not
increase independent primes. Use held-out confirmation seeds after discovering
a feature, and group ML splits by physical field/curve where appropriate. Do not
pool individual walk points or declare repeated batches to have one-batch 99.9%
global confidence. Predeclare pooled or sequential inference before extending
claims. A family-wide prime interaction needs a separate expanded input design.

## Exact identities, sources and archive

**Internal/retrieved provenance, checked by this measurement session:** public
input constants and field pools from EXP-ECDLP-5184f7/RUN-ECDLP-d0e449, with all
source SHA-256 values in the frozen inputs. Prime/cardinality certificates are
reused source evidence; new point arithmetic is independently checked in code.
No claimed exhaustive literature search or hypothesis/status transition.

{identities}

- [Frozen protocol](../../../tasks/solinas_generator_cohorts/PROTOCOL.md), configuration and standalone README.
- [Completed receipt](../../../tasks/solinas_generator_cohorts/runs/cohorts-20261012/receipt.json), frozen design/source hashes, public inputs and environment.
- [Analysis](../../../tasks/solinas_generator_cohorts/runs/cohorts-20261012/analysis.json), [verification](../../../tasks/solinas_generator_cohorts/runs/cohorts-20261012/verification.json), comparisons CSV and lossless JSONL record shards.
- [Editable diagram](workflow.dot), source/PDF, [graph inventory](graph-inventory.json), portable-runner bundle and full data ZIP manifests. Raw bytes remain outside Git with per-chunk hashes.
- Historical point-distribution, ML and materialized frontier diagrams checked; no canonical mechanism edge changes justified by these scoped mean observations. Historical evidence remains immutable.
'''
    (HERE/'report.md').write_text(markdown)
    # Fixed four-page layout, reviewed visually after rendering.
    def cell(value):return '['+str(value).replace('[','(').replace(']',')')+']'
    rows=[]
    for r in comparisons:
        label=r['case'].replace('P-','P')+'/'+('field '+r['right'][0] if r['population']=='random-model affine points' else r['population'])
        rows.extend([cell(label),cell(r['metric']),cell(f"{r['difference']:.5g}"),cell(f"({r['interval'][0]:.5g}, {r['interval'][1]:.5g})"),cell(f"{r['left_units']}/{r['right_units']}")])
    typ=f'''#set page(paper: "a4", margin: 16mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.55em)
#show heading: set text(fill: rgb("#254f76"))
= Solinas primes and generator cohorts
2026-10-12 · Measured descriptive study · cohorts-20261012

*Measured:* {finding}

== The prime, the curve, the generator
The prime defines residues modulo p. A and B define y²=x³+Ax+B. A generator
defines an ordering of its finite group. P192 uses 2^192−2^64−1; P224 uses
2^224−2^96+1. The exact standard curves have prime group orders and cofactor 1.

*Derived:* H=rG, with r nonzero modulo prime n, permutes the nonzero multiples.
Uniform kG and kH therefore have exactly the same point distribution. Ordered
walks Q, Q+G, Q+2G versus Q, Q+H, Q+2H can expose ordering features. Consecutive
points are dependent. Generator comparisons hold each standard curve fixed.

== Fixed sample and controls
Each generator cohort on each standard curve: 2,560 random-start walks ×4,096
points (10,485,760) and 256 iid-multiple blocks ×1,024 (262,144). Random generators
are fresh per block; published generators use identical public scalar schedules.
Each case also uses 512 random models on fixed S p; 144 R and 144 C fields,
four models/field, 1,024 uniform affine points/model. C matches p mod 12.

#image("workflow.svg", width: 100%)

20 primary mean tests, nominal 99.9% simultaneous confidence via Bonferroni.
Student/Welch approximations use generator blocks and control field means.
The two fixed S primes are not a sample of all structured prime families.

#pagebreak()
= Corrected comparison intervals
Published minus random G for walks/iid; fixed-S random models minus R/C field
means for the field baseline. Correlations and bin dispersion are dimensionless.
Each interval has nominal 99.995% confidence; simultaneous nominal 99.9% applies
to these 20 tests in this batch. Sampling-distribution coverage is approximate.

#image("primary-comparisons.svg", width: 100%)

Zero-compatible intervals bound tested mean features; they do not exclude every
rare generator type, higher-order coordinate feature, or discovery from ML.
No relative ECDLP resistance is measured. Official G is one fixed instance;
many independent starts do not turn it into many independently chosen Gs.

#pagebreak()
= Values and software checks
#set text(size: 8pt)
#table(columns: (1.15fr, 1.45fr, 0.8fr, 2fr, 0.7fr), inset: 4pt,
  table.header([Case/population], [Metric], [Difference], [Corrected interval], [Units]),
  {', '.join(rows)}
)
#set text(size: 9pt)
*Verified:* {verification['all_points_on_curve']:,} points on their exact curves;
{verification['records']:,} SHA-256/feature replays; {verification['independent_walk_transition_checks']:,}
independent walk transitions; {verification['independent_scalar_multiplications']:,} scalar arithmetic
checks; {verification['isomorphic_point_checks']:,} isomorphic transports. Separate Python affine
arithmetic checks OpenSSL outputs. This is same-session software verification.

The first 32 blocks/cohort/case also test shuffle, sorted positive dependence,
and u=2 isomorphic coordinate transport on exactly the same points. Sorted
sequences are deliberately synthetic. These diagnostics do not enter primary
multiplicity or create a security claim. See the Markdown report for values.

Per-cohort walk units =2,560; iid units =256. Field baseline uses 512 fixed-prime
coefficient draws versus 144 independent field means per control arm. The data
reuse 578 prime fields. The published generator exists only on its standard
curve; the field baseline does not identify a universal prime-by-G interaction.

#pagebreak()
= Sampling size and a reusable runner
The *sampling fraction* is sampled points / population size. A fixed fraction
of a 192-bit field is infeasible. Ten million / P192 p is about 1.6×10^−51.
*Power analysis* uses effect size, variance, confidence and independent units.
*Rare-event detection* uses event probability q: independent draws needed for
99.9% chance of at least one recognizable event are ceil(log(.001)/log(1−q)).

#table(columns: (1fr, 1fr), inset: 5pt, table.header([Event probability q], [Independent draws]),
  [1%], [688], [0.1%], [6,905], [0.01%], [69,075], [1 in a million], [6,907,752])
For rare fields count independent fields; for rare generators count generator
draws. Walk points do not supply independent event trials. The finite-population
correction is negligible at these fractions and applies to simple sampling
without replacement, not to walks. Variance-based detectable effects appear in
the Markdown comparison table; they do not bound all possible patterns.

== Run batches without an agent
Linux, Python 3.10+, C compiler and OpenSSL development headers. A standalone
package bundles public inputs. Each batch freezes source, seed and configuration,
then writes restartable exact coordinate chunks, SHA-256 manifests and features.

```bash
bash bootstrap.sh
bash run_batch.sh /large-filesystem/ec-study/batch-0001 batch-0001 3
.venv/bin/python catalog.py --root /large-filesystem/ec-study --output /large-filesystem/ec-study/catalog.sqlite
```

The same batch command resumes; a new seed gets a new output directory. A
deduplicated SQLite index retains field/model/generator identities for analysis
and ML. Default raw bytes: {receipt['raw_bytes']:,} (2.41 GB). Measured wall time:
{receipt['final_invocation_wall_seconds']:.1f}s, job CPU sum {receipt['summed_job_cpu_seconds']:.1f}s, three workers.

New seeds add conditional point/start/G replicates; they add no new primes.
Use independent confirmation seeds and field/curve-aware ML splits. Repeated
batch inference needs a prospectively declared pooled or sequential policy.

== Sources and identities
Frozen source: #text(size: 7pt)[{environment['git_commit']}]. Full exact standard
EC1 identities and parameter preimages are in inputs.json and report.md; all
random-G identities retain the changed generator. Public baseline inputs:
EXP-ECDLP-5184f7 / RUN-ECDLP-d0e449. Receipt, analysis, verification, lossless
record shards, source/PDF, graphs and data bundles are linked from report.md.
No canonical frontier edge changes; no hypothesis promotion or security claim.
'''
    (HERE/'report.typ').write_text(typ)
    typst.compile(str(HERE/'report.typ'),output=str(HERE/'report.pdf'),root=str(HERE))
    print(json.dumps({'report':str(HERE/'report.pdf'),'finding':finding,'raw_bytes':receipt['raw_bytes']}))


if __name__=='__main__':main()
