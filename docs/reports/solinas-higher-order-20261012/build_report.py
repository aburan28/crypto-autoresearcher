"""Derived figures/report from frozen measured and analyzed artifacts only."""
import csv
import hashlib
import io
import json
import math
import os
import subprocess
from pathlib import Path

os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ.setdefault('MPLCONFIGDIR', '/tmp/solinas-higher-order-mpl')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/solinas-higher-order-cache')
for name in ('MPLCONFIGDIR', 'XDG_CACHE_HOME'): Path(os.environ[name]).mkdir(exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import typst

HERE = Path(__file__).resolve().parent; REPO = HERE.parents[2]
RUN = REPO/'tasks/solinas_higher_order/runs/higher-order-20261012'
OLD_COMMIT = '195227dac94f03034eb0978b0214282c20a4da97'
BASE_URL = 'https://github.com/aburan28/crypto-autoresearcher/blob/'+OLD_COMMIT+'/'
LABELS = {'mi_lag1': 'MI lag 1', 'mi_lag4': 'MI lag 4', 'triple64': 'Parity triple bit 64', 'triple96': 'Parity triple bit 96',
          'motif64': 'Four-bit motifs', 'longrun64': 'Longest bit run', 'spectral64': 'Largest spectral peak',
          'hankel64_deficit': 'GF(2) rank deficit', 'perm_gap': 'Ordinal entropy gap', 'lowx_pairs': 'Adjacent low x',
          'xy_mi': 'Joint x/y MI', 'x_tail64': 'Low-x frequency', 'xy_tail64': 'Joint low-x/y', 'x_mod64_dispersion': 'x mod 64 dispersion'}


def json_read(name): return json.loads((RUN/name).read_text())


def save(fig, name):
    fig.savefig(HERE/(name+'.svg')); fig.savefig(HERE/(name+'.png'), dpi=160); plt.close(fig)
    path = HERE/(name+'.svg'); path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')


def forest(axis, rows, title):
    for i, row in enumerate(rows):
        scale = row['standard_error'] or 1.0
        lo, hi = np.asarray(row['interval'])/scale; center = row['difference']/scale
        axis.errorbar(center, i, xerr=[[center-lo], [hi-center]], fmt='o', color='#27638c', ms=4, capsize=3)
    axis.set_yticks(range(len(rows)), [LABELS[r['metric']]+(' / '+r['right'][0] if 'fields' in r['right'] else '') for r in rows])
    axis.invert_yaxis(); axis.axvline(0, color='#555', lw=.8, ls='--'); axis.grid(axis='x', alpha=.18)
    axis.set_title(title, loc='left', fontweight='bold', fontsize=10); axis.set_xlabel('Mean difference / recorded standard error')


def main():
    analysis = json_read('analysis.json'); receipt = json_read('receipt.json'); verification = json_read('verification.json')
    discovery = json_read('discovery/receipt.json'); environment = json_read('environment.json'); config = json_read('design.json')['config']
    inputs = json_read('inputs.json'); freeze = json.loads((REPO/'tasks/solinas_higher_order/publication/source-freeze.json').read_text())
    comparisons = analysis['comparisons']; benchmarks = analysis['prefix_benchmarks']; counts = verification['counts']
    plt.rcParams.update({'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none'})
    subprocess.run(['dot', '-Tsvg', str(HERE/'workflow.dot'), '-o', str(HERE/'workflow.svg')], check=True)
    fig, axes = plt.subplots(2, 2, figsize=(9, 8), constrained_layout=True)
    for column, case in enumerate(config['cases']):
        for row, population in enumerate(('fresh walks', 'targeted-generator walks')):
            selected = [r for r in comparisons if r['case'] == case and r['population'] == population]
            forest(axes[row, column], selected, case+' / '+population)
    fig.suptitle('Higher-order ordering features — nominal 99.9% primary-family intervals\nhigher-order-20261012; 2,560 walk pairs or 160 target units per case', fontsize=10)
    save(fig, 'ordering-intervals')
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), constrained_layout=True)
    for axis, case in zip(axes, config['cases']):
        forest(axis, [r for r in comparisons if r['case'] == case and r['population'] == 'fresh affine points'], case+' / R,C field controls')
    fig.suptitle('Spatial point features — fixed S prime versus control field means\n512 S models; 144 R + 144 C fields/case, 4 models/field; 1,024 points/model', fontsize=10)
    save(fig, 'field-intervals')
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.8), constrained_layout=True)
    for axis, case in zip(axes, config['cases']):
        rows = [r for r in benchmarks if r['case'] == case]
        for i, r in enumerate(rows):
            fraction = r['as_or_more_extreme']/r['bank_generators']; lo, hi = r['tail_probability_interval']
            display = max(fraction, .5/r['bank_generators']); low = max(lo, .1/r['bank_generators'])
            axis.errorbar(display, i, xerr=[[max(0, display-low)], [hi-display]], fmt='o', capsize=3, color='#8e6430')
        axis.set_xscale('log'); axis.set_xlim(1e-6, 1.1); axis.set_yticks(range(len(rows)), [LABELS[r['metric']] for r in rows])
        axis.invert_yaxis(); axis.grid(axis='x', alpha=.18); axis.set_title(case, loc='left', fontweight='bold')
        axis.set_xlabel('Fraction of random H with score ≥ published G')
    fig.suptitle('Published trimmed-prefix rarity: 98,304 independent random H per curve\nClopper–Pearson bounds for each tail fraction; Monte Carlo rank tests reported separately', fontsize=10)
    save(fig, 'prefix-rarity')
    sizes = np.linspace(0, 500000, 400)
    fig, axis = plt.subplots(figsize=(7.2, 3.1), constrained_layout=True)
    for q, color in [(1e-4, '#27638c'), (1e-5, '#53865c'), (1e-6, '#b07b34')]:
        axis.plot(sizes, -np.expm1(sizes*np.log1p(-q)), label=f'Type frequency q={q:g}', color=color)
        axis.plot(config['bank_generators'], analysis['rare_coverage'][str(q)], 'o', color=color)
    axis.axvline(config['bank_generators'], color='#777', ls='--', lw=.8)
    axis.set(xlabel='Independent generator draws', ylabel='Probability of ≥1 encounter', ylim=(0, 1.02))
    axis.legend(frameon=False, fontsize=8); axis.grid(alpha=.18)
    axis.set_title('Derived encounter probability: 1 − (1 − q)^B; B=98,304 in this run', loc='left', fontsize=10)
    save(fig, 'rare-coverage')

    # Additional descriptive joint-score view; no new tests or sampling.
    correlations = {}; joint_rows = []; target_prefix_rows = []
    for case in config['cases']:
        values = []
        for path in sorted((RUN/'records').glob(case+'-bank-*.json')):
            record = json.loads(path.read_text())
            values.extend([[u['features'][m] for m in config['walk_metrics']] for u in record['units']])
        matrix = np.asarray(values); correlations[case] = np.corrcoef(matrix, rowvar=False).tolist()
        target_records = [json.loads(p.read_text()) for p in sorted((RUN/'records').glob(case+'-target-*.json'))]
        for record in target_records:
            prefix = next(u for u in record['units'] if u['label'] == 'target-prefix')
            for i, metric in enumerate(config['walk_metrics']):
                score = prefix['features'][metric]; hits = int(np.count_nonzero(matrix[:, i] >= score))
                target_prefix_rows.append({'case': case, 'region': record['job']['target']['region'], 'target_index': record['job']['target']['index'],
                    'G': prefix['generator'], 'metric': metric, 'score': score, 'bank_as_or_more_extreme': hits,
                    'bank_tail_fraction': hits/len(matrix), 'bank_generators': len(matrix),
                    'u2_score': prefix['isomorphic_u2'][metric]})
        thresholds = np.quantile(matrix, .99, axis=0); tail = matrix > thresholds
        for i, left in enumerate(config['walk_metrics']):
            for j in range(i+1, len(config['walk_metrics'])):
                observed = int(np.count_nonzero(tail[:, i] & tail[:, j])); product = float(tail[:, i].mean()*tail[:, j].mean())
                joint_rows.append({'case': case, 'left': left, 'right': config['walk_metrics'][j], 'generators': len(matrix),
                                   'left_threshold': thresholds[i], 'right_threshold': thresholds[j], 'joint_hits': observed,
                                   'observed_fraction': observed/len(matrix), 'product_of_marginals': product,
                                   'scope': 'Exploratory; empirical 99th thresholds use the same bank; scores share points/bits, independence is not assumed'})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), constrained_layout=True)
    for axis, case in zip(axes, config['cases']):
        plot = axis.imshow(correlations[case], vmin=-1, vmax=1, cmap='RdBu_r'); axis.set_title(case+' / random-G prefix scores')
        axis.set_xticks(range(10), [LABELS[m] for m in config['walk_metrics']], rotation=65, ha='right', fontsize=6)
        axis.set_yticks(range(10), [LABELS[m] for m in config['walk_metrics']], fontsize=6)
    fig.colorbar(plot, ax=axes, shrink=.8, label='Pearson correlation of score pairs (descriptive)')
    save(fig, 'score-correlations')
    (HERE/'bank-score-correlation.json').write_text(json.dumps({'schema': 1, 'cases': correlations, 'features': config['walk_metrics'],
        'sample': '98,304 random-generator prefixes/case, higher-order-20261012', 'inference': 'Exploratory correlated descriptors, not evidence of a prime-specific effect'}, indent=2)+'\n')
    stream = io.StringIO(newline=''); writer = csv.DictWriter(stream, fieldnames=joint_rows[0].keys(), lineterminator='\n'); writer.writeheader(); writer.writerows(joint_rows)
    (HERE/'bank-joint-tails.csv').write_text(stream.getvalue())
    target_extreme = [r for r in target_prefix_rows if r['bank_tail_fraction'] <= .001]
    (HERE/'target-prefix-ranks.json').write_text(json.dumps({'schema': 1, 'comparisons': target_prefix_rows,
        'at_or_below_empirical_0_1pct_tail_count': len(target_extreme), 'tested_descriptors': len(target_prefix_rows),
        'scope': 'Exploratory ranks of a fixed deliberately selected G set, not p values for its selection process. Threshold chosen for communication after sampling; no new primary test or trial. Random-start effects were tested prospectively in the primary finite-set comparisons.'}, indent=2)+'\n')

    resolved = [r for r in comparisons if r['excludes_zero']]; rare = [r for r in benchmarks if r['crosses_threshold']]
    finding = f"{len(resolved)} of 58 primary mean/accuracy intervals exclude zero; {len(rare)} of 20 published-prefix reference tests cross the corrected threshold."
    if not resolved and not rare:
        finding += ' The tested features did not resolve a published-generator or fixed-S-prime effect in this fresh batch.'
    elif resolved or rare:
        finding += ' These observations need further independent confirmation and mechanism review before any broader interpretation.'
    ml = [r for r in comparisons if r['metric'] == 'accuracy_minus_half']
    ml_rows = '\n'.join(f"| {r['case']} | {r['accuracy']:.6%} | [{r['interval'][0]+.5:.6%}, {r['interval'][1]+.5:.6%}] | {r['left_units']} |" for r in ml)
    primary_rows = '\n'.join(f"| {r['case']} | {r['population']} | {r['metric']} | {r['right']} | {r['difference']:.7g} | [{r['interval'][0]:.7g}, {r['interval'][1]:.7g}] | {r['left_units']}/{r['right_units']} |" for r in comparisons)
    prefix_rows = '\n'.join(f"| {r['case']} | {r['metric']} | {r['official_score']:.6g} | {r['as_or_more_extreme']:,}/{r['bank_generators']:,} | {r['monte_carlo_p']:.7g} | {r['bonferroni_p']:.6g} |" for r in benchmarks)
    identities = '\n'.join(f"- {a['case']}: `{a['identity']['curve_id']}`; full UID `{a['identity']['curve_uid']}`. p={a['p']}; A={a['A']}; B={a['B']}; n={a['N']}; cofactor 1; G={a['G']}." for a in inputs['anchors'])
    follow_run = REPO/'tasks/solinas_higher_order/runs/rare-followup-20261012'
    follow = json.loads((follow_run/'analysis.json').read_text()); follow_receipt = json.loads((follow_run/'receipt.json').read_text())
    follow_verify = json.loads((follow_run/'verification.json').read_text())
    follow_config = json.loads((REPO/'tasks/solinas_higher_order/followup/config.json').read_text())
    fig, axes = plt.subplots(1, 3, figsize=(9, 3.2), constrained_layout=True)
    for axis, candidate in zip(axes, follow_config['candidates']):
        rows = [r for r in follow['comparisons'] if r['candidate'] == candidate['id']]
        for i, r in enumerate(rows):
            lo, hi = r['interval']; center = r['difference']
            axis.errorbar(center, i, xerr=[[center-lo], [hi-center]], fmt='o', capsize=3, color='#27638c')
        axis.set_yticks(range(2), ['Canonical', 'Same-point u=2']); axis.invert_yaxis(); axis.axvline(0, color='#777', ls='--')
        axis.grid(axis='x', alpha=.18); axis.set_title(candidate['case']+' / '+LABELS[candidate['metric']], fontsize=9, loc='left')
        axis.set_xlabel('Candidate − random mean\n'+('run length (points)' if candidate['metric'] == 'longrun64' else 'dimensionless score'))
    fig.suptitle('Independent candidate follow-up — six mean intervals in a separate nominal 99.99% family\nrare-followup-20261012; 4,096 paired random-start windows ×256 points/candidate/cohort', fontsize=9)
    save(fig, 'rare-followup-intervals')
    follow_mean_rows = '\n'.join(f"| {r['candidate']} | {r['representation']} | {r['difference']:.7g} | [{r['interval'][0]:.7g}, {r['interval'][1]:.7g}] |" for r in follow['comparisons'])
    follow_rate_rows = '\n'.join(f"| {r['candidate']} | {r['threshold']:.6g} | {r['target_hits']}/{r['pairs']} | {r['random_hits']}/{r['pairs']} | {r['exact_paired_p']:.7g} | [{r['target_rate_interval'][0]:.7g}, {r['target_rate_interval'][1]:.7g}] |" for r in follow['rare_event_rates'])
    follow_text = f'''## Independent fresh checks of the three rare-prefix candidates

**Measured:** all three exploratory candidates received a second frozen,
committed-and-pushed protocol before new sampling. Each fixed G was compared
with fresh random generators in 4,096 independent paired 256-point windows
with uniform random starts. {follow_receipt['points']:,} additional points;
{follow_receipt['jobs']} jobs; zero failures. Total fresh coordinates in both
stages: {receipt['points']+follow_receipt['points']:,}. The same selected
prefix is never counted as fresh confirmation.

**Derived fresh observations:** {follow['mean_excludes_zero_count']} of six
mean intervals excludes zero; {follow['rate_threshold_count']} of three
exact paired rare-event tests crosses the corrected threshold. This separate
nine-test family has nominal 99.99% confidence, not a combined 87-test 99.9%
family. A simple two-family union bound is nominal 99.89%, subject to the
mean-interval approximation. Each event is score≥the original discovery
score; rare rate tests use exact discordant-pair McNemar/binomial calculations.
Six arm-rate Clopper–Pearson intervals use their own .0001 family correction.

![Fresh per-candidate mean intervals](rare-followup-intervals.svg)

| Candidate | Coordinates | Mean difference | Corrected approximate interval |
|---|---|---:|---:|
{follow_mean_rows}

| Candidate | Original threshold | Target hits | Random hits | Exact paired p | Target-rate corrected CP interval |
|---|---:|---:|---:|---:|---:|
{follow_rate_rows}

The P224 22-bit-run candidate had zero repeats in 4,096 windows in both
arms, with an upper arm-rate bound of about 0.285%. This does not exclude
events as rare as its original bank rank (3/98,304) or an effect concentrated
in its known deterministic prefix. The prefix remains exactly reproducible;
these fresh tests concern **random-start effects**, not erasing that earlier
observation. Motif-threshold hits were 2 versus 1; parity-threshold hits 7
versus 5, with no corrected difference resolved. The candidates' ordinary
random-start mean scores were near their random-G controls.

**Measured integrity:** all {follow_verify['counts']['points']:,} follow-up
points, file hashes and canonical/u=2 score replays passed. The separate
affine oracle checked {follow_verify['counts']['transitions']:,} transitions,
{follow_verify['counts']['scalar_starts']:,} starts and
{follow_verify['counts']['generator_scalars']:,} control generators. Sampling
wall {follow_receipt['final_invocation_wall_seconds']:.2f}s, summed job CPU
{follow_receipt['summed_job_cpu_seconds']:.2f}s. Same-session verification only.

[Follow-up protocol](../../../tasks/solinas_higher_order/followup/PROTOCOL.md),
[candidate configuration](../../../tasks/solinas_higher_order/followup/config.json),
[run results](../../../tasks/solinas_higher_order/runs/rare-followup-20261012/analysis.json)
and separate raw-data bundle preserve every observation. A further test of
prime specificity would require the same targeted construction on matched
ordinary-prime curve models and a prospective subgroup/order policy; this
fixed-standard-curve follow-up does not supply that causal comparison.

'''
    candidates = [r for r in analysis['discovery']['comparisons'] if r['excludes_zero']]
    candidate_text = '; '.join(r['case']+' '+r['population']+' '+r['metric'] for r in candidates) or 'none'
    secondary_hits = [r for r in analysis['target_region_secondary'] if r['excludes_zero']]
    secondary_text = '; '.join(r['case']+' '+r['population']+' '+r['metric'] for r in secondary_hits) or 'none'
    md = f'''# Rare and higher-order Solinas point patterns

2026-10-12. **Measured and derived descriptive observations only.** Run
`higher-order-20261012`; frozen source `{freeze['source_commit']}`. No official
scientific status transition, independent research review or security claim.

**Measured:** {finding}

**Measured follow-up:** {follow_receipt['points']:,} additional independent
points checked all three exploratory rare-prefix candidates. None of its
nine corrected comparisons resolved a random-start effect. The two stages
contain {receipt['points']+follow_receipt['points']:,} fresh public coordinates;
their confidence families are separate as described below.

The earlier statement “Rare or higher-order patterns remain open” motivated
this extension. It narrows that open question for the declared feature menu,
generator populations and point windows. It does not close it universally.

## What higher-order structure actually appeared

**Derived universal identity:** for consecutive Q−H,Q,Q+H, with x coordinates
L,X,R and u=x(H), the addition law implies

`(L+R)(X−u)^2 = 2((Xu+A)(X+u)+2B) mod p`.

Add the affine formulas for x(Q−H) and x(Q+H), substitute y²=x³+Ax+B,
and collect terms. This equation applies to any nonsingular short Weierstrass
curve when the three points are affine; it is not tied to the form of p.
The x-only relation does not distinguish H from −H and does not identify
an unknown scalar. It is a positive arithmetic control showing why small
pairwise correlations never imply an absence of algebraic relations.

**Measured:** {counts['triple_relations']:,} spread triple checks all satisfied
the identity. Deliberately wrong x(2G) steps gave
{counts['wrong_step_hits']}/{counts['wrong_step_trials']} hits; within-block
shuffling gave {counts['shuffled_triple_hits']}/{counts['shuffled_triple_trials']}.
The separate affine oracle also checked {counts['affine_transitions']:,}
transitions and {counts['scalar_checks']:,} scalar/generator starts.

## Fixed discovery and fresh sample

**Measured:** all {discovery['points']:,} old points, {discovery['records']:,}
records, were scanned without altering historical data. The scan records 56
exploratory comparisons; zero-excluding discovery intervals: {len(candidates)}
({candidate_text}). They are not counted as fresh confirmation.

**Measured:** {receipt['points']:,} new points, {receipt['jobs']:,} jobs,
{receipt['raw_bytes']:,} raw bytes, zero job failures. Per exact standard
curve: 2,560 paired blocks ×2,048 points/cohort, 98,304 random-generator
prefixes ×256 points, 160 deliberately targeted generators, four paired
random-start walks ×1,024 points/target plus trimmed prefixes. All deterministic
prefixes cover multiples 17 through 272. Rare targets are near x=0,2^64,
2^96,p−2^64,p−1; only the smaller y root is selected.

New field-point samples reuse 3,328 frozen random models on 578 distinct
primes: each case has 512 models on one fixed S prime, 144 R +144 C fields,
four models/field, 1,024 uniform affine points/model. R matches field size
within 1%; C also matches p modulo 12. No new independent field draw is
claimed. Orders/models were retained without favorable filtering.

**Derived exact baseline:** H=rG with nonzero r modulo prime n permutes all
nonzero multiples. Uniform kG and kH have identical distributions. An effect
must involve ordering, selected scalar windows or a different curve/field
population. Official G is one fixed point, not 2,560 independent generator
choices. Its coordinates are never transferred to unrelated random fields.

![Fixed workflow and populations](workflow.svg)

## Controls, confidence and ML holdout

Ten fixed ordering descriptors: lag-1/4 mutual information, triple parity at
x bits 64/96, four-bit motifs, longest equal-bit run, largest spectral peak,
32×32 binary Hankel-rank deficiency, ordinal entropy gap and adjacent low-x
events. Four spatial features: joint x/y mutual information, low-x frequency,
joint low-x/y frequency and x modulo 64 dispersion. Binary matrix rank is
not elliptic-curve group rank or ECDLP difficulty.

**Derived inference:** 78 primary comparisons: 58 approximate mean/accuracy
intervals and 20 Monte Carlo random-generator reference tests. Bonferroni
family α=.001, α/test={analysis['per_test_alpha']:.9g}; nominal mean interval
confidence {(1-analysis['per_test_alpha'])*100:.7f}%. Approximate Student/Welch
coverage relies on independent seeded blocks/targets or control field means.
Four target starts are averaged per target; targets are a fixed selected set,
not a random sample of a whole generator population. No per-point inference.
Secondary region tests are a separate exploratory family, not extra primary
discoveries. Its zero-excluding intervals: {len(secondary_hits)} ({secondary_text}).

**Exploratory targeted prefixes:** {len(target_extreme)} of {len(target_prefix_rows):,}
score descriptors in the fixed selected set fell in a tail containing at most
0.1% of the random-generator bank. [All targeted-prefix ranks](target-prefix-ranks.json)
are retained, including G, the score and its u=2 companion. This threshold is
a descriptive summary chosen after sampling, not an added primary test.
The targets were selected deliberately; these ranks do not quantify their
density in the field. Independent random-start primary comparisons test the
pooled finite-set effect, not every individual selected generator separately.

**Measured controls:** 32 blocks/case have within-block shuffled, sorted-x
positive and u=2 isomorphic companions. The positive sorted controls passed.
u=2 rescales x→4x,y→8y,A→16A,B→64B and preserves the group. Numerical score
changes under it are coordinate dependence, not independent curve evidence.

**Measured ML:** the locked ten-feature classifier was trained only on old
walks trimmed to 2,048 points and evaluated once on new 2,048-point blocks.
No generator coordinates, field identifiers, seeds, scalar values or labels
enter its feature vector. Labels are used solely as training targets.

| Case | Fresh accuracy | Corrected approximate accuracy interval | Test pairs |
|---|---:|---:|---:|
{ml_rows}

![Fresh walk and targeted-walk intervals](ordering-intervals.svg)

![Fresh spatial point intervals](field-intervals.svg)

## Rare-prefix comparison and what sample size can see

Published G's trimmed-prefix score is compared with all 98,304 random H
on its exact curve. Reference p=(1+number of scores ≥ official)/(98,304+1);
ties count conservatively, and all ten score tails/case are in the primary
family. This describes unusualness under a uniform-generator benchmark;
it does not prove the original generator selection was random.

![Published-prefix tail fractions with uncertainty](prefix-rarity.svg)

**Derived encounter probabilities:** the uniform bank encounters at least
one q-frequency generator type with probability 1−(1−q)^98,304. For q=10^−4:
{analysis['rare_coverage']['0.0001']:.6%}; q=10^−5:
{analysis['rare_coverage']['1e-05']:.6%}; q=10^−6:
{analysis['rare_coverage']['1e-06']:.6%}. This is encounter probability,
not a guarantee that the 256-point descriptors recognize the effect. Patterns
of frequency about 1/p require targeted designs, not a proportional blind
sample of a 192-/224-bit field. The special-coordinate generators address
five named sets without pretending to cover every algebraic rare family.

![Derived probability of encountering rare generator types](rare-coverage.svg)

**Exploratory:** prefix scores share points/bits and are correlated. The
matrix below and [joint-tail counts](bank-joint-tails.csv) describe that
dependence, using empirical 99th-percentile thresholds within the same bank;
they are not independent tests or a Solinas-specific mechanism. Selected
bank maxima in `analysis.json` are expected order statistics in a large
search, not discoveries simply because their values look unusual.

![Descriptive score correlations](score-correlations.svg)

{follow_text}
## Full numerical primary results

Raw mean intervals, with actual independent unit counts. Plot units are
differences divided by their recorded standard errors; this table and
[comparisons.csv](../../../tasks/solinas_higher_order/runs/higher-order-20261012/comparisons.csv)
retain the original feature units.

| Case | Population | Metric | Comparator | Mean difference | Corrected interval | Units L/R |
|---|---|---|---|---:|---:|---:|
{primary_rows}

| Case | Prefix score | Published value | Random H at least as extreme | Reference p | Bonferroni p |
|---|---|---:|---:|---:|---:|
{prefix_rows}

## Integrity, reproducibility and scope

**Measured verification:** every one of {counts['points']:,} raw points
passed its equation/range check and every raw SHA-256 matched. All
{counts['unit_feature_replays']:,} feature units were replayed with the same
locked feature code; separate synthetic tests checked formulas and GF(2)
matrix rank. {counts['generator_checks']:,} generator instances were checked
on-curve and {counts['transport_points']:,} transported points checked.
This is same-session verification, not an independent scientific review.
Fresh sampling used {receipt['final_invocation_wall_seconds']:.2f} seconds
wall and {receipt['summed_job_cpu_seconds']:.2f} summed job CPU seconds on
three workers. Old scan wall: {discovery['final_invocation_seconds']:.2f} seconds.
Execution host/software, exact command and dirty-state entries are preserved
in `environment.json`; frozen source/input hashes matched throughout.

Exact measured standard identities (internal frozen public-parameter
provenance, not a new externally retrieved standards citation):

{identities}

**Limits:** two fixed standard primes; one official G per curve; finite
feature menu and scalar windows; the existing random-field/model pool;
fixed targeted generator sets. No relative ECDLP resistance, scalar recovery,
security exponent or bound is measured. Exact universal triple structure is
distinct from the absence/presence of a resolved cohort mean difference.

Use the [agent-free runner](../../../tasks/solinas_higher_order/README.md),
new seed and new output folder for every future batch. Reuse archived old
discovery features with `--reuse-discovery`; no old raw rescan or agent is
needed. Keep immutable raw/feature shards, hashes and environment metadata.
Before pooling future runs, freeze a cross-batch inference plan rather than
repeating until a p value looks favorable. A useful next controlled extension
would target additional algebraically defined generator/model families or
longer lags, with matched ordinary-prime instances and fresh confirmation.

Internal sources read: [prior generator-cohort report]({BASE_URL}docs/reports/solinas-generator-cohorts-20261012/report.md),
[prior distribution report]({BASE_URL}docs/reports/solinas-point-distribution-20261012/report.md),
[prior ML relation flow]({BASE_URL}docs/reports/ec-relation-ml-20261011/report.md).
New artifacts: [protocol](../../../tasks/solinas_higher_order/PROTOCOL.md),
[source freeze](../../../tasks/solinas_higher_order/publication/source-freeze.json),
[run receipt](../../../tasks/solinas_higher_order/runs/higher-order-20261012/receipt.json),
[analysis](../../../tasks/solinas_higher_order/runs/higher-order-20261012/analysis.json),
[verification](../../../tasks/solinas_higher_order/runs/higher-order-20261012/verification.json),
lossless JSONL record/feature shards and raw-data checksum inventory.
Historical reports and ECDLP frontier records were checked for affected
graph content; no isogeny, endomorphism or attack-cost edge is changed.
'''
    (HERE/'report.md').write_text(md)

    ml_typst = '\n'.join(f"[{r['case']}], [{r['accuracy']*100:.4f}%], [{(r['interval'][0]+.5)*100:.4f}% to {(r['interval'][1]+.5)*100:.4f}%], [{r['left_units']}]," for r in ml)
    typ = f'''#set page(paper: "a4", margin: 15mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.45em)
#show heading: set text(fill: rgb("#254f76"))
= Rare and higher-order Solinas point patterns
2026-10-12 · higher-order-20261012 · measured descriptive observations

*Measured:* {finding}

*Scope:* 77.4 million fresh public points; two exact standard curves; one
published G per curve; matched random generators and random-field models.
Page 6 adds 6.29 million fresh points for three selected rare-prefix candidates.
No independent scientific review, official hypothesis transition or relative
ECDLP-resistance result. Full values and provenance: report.md, comparisons.csv,
analysis.json and verification.json next to the portable task.

== A higher-order relation did appear — the ordinary curve law
For a generator with x coordinate u and consecutive points with x values L,X,R,
`(L+R)(X−u)^2 = 2((Xu+A)(X+u)+2B) mod p`.
Add the formulas for x(Q−H),x(Q+H), then substitute y²=x³+Ax+B. This exact
identity is derived for every nonsingular short Weierstrass curve with affine
neighbors. It is not specific to a Solinas prime and reveals no unknown scalar.

*Measured:* {counts['triple_relations']:,} spread triples satisfied it;
wrong step {counts['wrong_step_hits']}/{counts['wrong_step_trials']}, shuffled
{counts['shuffled_triple_hits']}/{counts['shuffled_triple_trials']} hits.
Low simple correlations never imply an absence of algebraic structure.

#image("workflow.svg", width: 100%, height: 106mm, fit: "contain")

#pagebreak()
= Fresh ordered-walk and targeted-generator comparisons
2,560 paired independent-start blocks ×2,048 points/cohort/case. 160
selected generators/case near x=0,2^64,2^96,p−2^64,p−1; four 1,024-point
starts averaged per generator. Targets are a finite chosen set, not a uniform
sample. All prefix comparisons use multiples 17 through 272, excluding the
first 16 multiples. Larger prefix scores measure the declared anomaly tails.

#image("ordering-intervals.svg", width: 100%, height: 174mm, fit: "contain")

Nominal 99.9% confidence for the 78-comparison primary family: Bonferroni
α/test={analysis['per_test_alpha']:.7g}. 58 mean/accuracy intervals use
Student/Welch approximations; 20 reference tests use random-generator ranks.
Mean plot units = difference / recorded standard error. Original units and
all values are in comparisons.csv. Binary Hankel rank is a sequence matrix
statistic, not group rank or ECDLP complexity. Companion controls are not
independent samples.

#pagebreak()
= Fresh spatial point comparisons and ML holdout
3,328 existing frozen random models; 578 distinct primes. Per case: 512
models on fixed S p, 144 R plus 144 C fields, four models/field, 1,024
uniform affine points/model. R matches field size; C also matches p mod 12.
Random control models are averaged by field. New points are independent of
the old scan; field/model draws themselves are reused, not new replicates.

#image("field-intervals.svg", width: 100%, height: 106mm, fit: "contain")

== Feature-only ML, evaluated once on fresh seed blocks
Train only on old walks trimmed to 2,048 points; test on new 2,048-point
walks. Algorithm and settings were fixed before scanning. Input = ten
numerical descriptors, with no G coordinates, IDs, seed, scalar or label.
Pair correctness values before interval estimation; no per-point inference.

#table(columns: (1fr, 1fr, 2fr, 0.7fr), inset: 5pt,
  [Case], [Accuracy], [Corrected approximate interval], [Pairs],
  {ml_typst}
)

Old scan: {discovery['points']:,} points, 56 exploratory comparisons;
{len(candidates)} zero-excluding intervals. Fresh primary results are reported
separately. Secondary region intervals (100-test exploratory family):
{len(secondary_hits)} exclude zero. All observations, favorable or otherwise,
remain in analysis.json. Uniform nonzero multiples have exactly identical
distributions for every generator; only ordering/window effects could differ.

#pagebreak()
= Published-prefix rarity and sampling limits
The random-generator bank has 98,304 independent H per exact standard curve.
Reference p = (1 + count with score ≥ official)/(98,304+1), ties included;
minimum p≈1.017×10^−5. {len(rare)} of 20 tests cross the corrected threshold.
This is a uniform-G benchmark, not a claim about historical G selection.

#image("prefix-rarity.svg", width: 100%, height: 127mm, fit: "contain")

#image("rare-coverage.svg", width: 100%, height: 72mm, fit: "contain")

Encounter probabilities: q=10^−4 → {analysis['rare_coverage']['0.0001']*100:.4f}%;
q=10^−5 → {analysis['rare_coverage']['1e-05']*100:.4f}%;
q=10^−6 → {analysis['rare_coverage']['1e-06']*100:.4f}%.
Encountering a type does not guarantee recognition by these features. Types
with density near 1/p need deliberate targeting. Point count does not imply
proportional coverage of a 192-/224-bit field.

#pagebreak()
= Joint score behavior, integrity and reproducibility
#image("score-correlations.svg", width: 100%, height: 120mm, fit: "contain")
*Exploratory:* these descriptors share bits/points. Correlations and joint
tail counts (bank-joint-tails.csv) describe that dependence. Empirical 99th
thresholds use the same bank; no independence or prime-specific effect is
inferred. Selected bank maxima are expected order statistics in a large search.

*Measured integrity:* {counts['points']:,} points on-curve; all raw SHA-256
matched; {counts['unit_feature_replays']:,} feature units replayed. Separate
integer EC oracle: {counts['affine_transitions']:,} transitions,
{counts['scalar_checks']:,} scalar/start checks. All sorted positive controls
passed; {counts['transport_points']:,} isomorphic u=2 points checked. Same-session
verification is not an independent research review.

Sampling: {receipt['final_invocation_wall_seconds']:.2f} s wall,
{receipt['summed_job_cpu_seconds']:.2f} summed job CPU s, three workers,
{receipt['jobs']:,} jobs, zero failures. Frozen source:
`{freeze['source_commit']}`.
Exact standard aliases: EC1P192Cniststandardhb4bdde6340ec and
EC1P224Cniststandardhe2397ca7cfb5. Full UIDs, p,A,B,n,G and internal certificate
provenance are in inputs.json and report.md. Environment/command/dirty-state
metadata and content hashes are retained.

Agent-free reruns: use research.py batch with a new public seed and a new
output directory. The dataset includes old discovery features for
--reuse-discovery; no old raw rescan is needed. Keep coordinate/JSONL shards
and manifests for future analyses; pool batches only under a prospective plan.

No relative ECDLP hardness, recovery, security exponent or attack-cost bound
is measured. Finite feature scope and rare families remain open beyond the
declared observations. Historical reports/frontier graphs remain unchanged.

#pagebreak()
= Three rare-prefix candidates: independent fresh follow-up
Three of 3,200 targeted descriptors fell in a tail containing at most 0.1%
of the random-G bank. Strongest: P224 x(H)=2^64+2, bit-64 run length 22
in its trimmed prefix (3/98,304 bank generators as extreme); same-point
u=2 changes that score to 13. These are exploratory selected outliers.

New protocol frozen and pushed before its distinct public seed: 4,096 paired
random-start windows ×256 points per candidate/cohort, fresh random control
G per pair. {follow_receipt['points']:,} additional points, all verified;
total in both scientific stages: {receipt['points']+follow_receipt['points']:,}.

#image("rare-followup-intervals.svg", width: 100%, height: 104mm, fit: "contain")

*Measured:* {follow['mean_excludes_zero_count']} of six mean intervals excludes
zero; {follow['rate_threshold_count']} of three exact paired event-rate tests
crosses the corrected threshold. This is a separate nominal 99.99% nine-test
family (α=.0001), alongside the primary 99.9% family. Do not combine them
into a claimed 87-test 99.9% family; simple union coverage is nominal 99.89%,
with approximate mean-interval assumptions.

#table(columns: (1.3fr, 1fr, 1fr, 1fr), inset: 5pt,
  [Original rare score], [Threshold], [Target hits], [Random hits],
  [P192 motifs], [4.2685], [2/4096], [1/4096],
  [P224 triple parity], [0.2126], [7/4096], [5/4096],
  [P224 longest run], [22], [0/4096], [0/4096],
)

The exact paired p values are 1, 0.7744 and 1. Zero 22-bit runs leave a
corrected arm-rate upper bound of 0.285%; very rare effects remain possible.
The earlier deterministic prefix remains reproducible. Fresh tests concern
random starts, not erasing a selected scalar-window observation. Same-point
u=2 is a coordinate control, not an independent curve.

All {follow_verify['counts']['points']:,} points/hash/score replays passed;
independent integer oracle checked {follow_verify['counts']['transitions']:,}
transitions, {follow_verify['counts']['scalar_starts']:,} starts and
{follow_verify['counts']['generator_scalars']:,} control generators. Wall
{follow_receipt['final_invocation_wall_seconds']:.2f}s; CPU sum
{follow_receipt['summed_job_cpu_seconds']:.2f}s; zero job failures. Full raw
mean/rate bounds and candidate G are in report.md and follow-up analysis.json.
Ordinary-prime matched candidates would be needed for prime-specific inference.
'''
    (HERE/'report.typ').write_text(typ)
    typst.compile(str(HERE/'report.typ'), output=str(HERE/'report.pdf'))
    inventory = []
    for directory in ('docs/reports/ec-relation-ml-20261011', 'docs/reports/solinas-point-distribution-20261012',
                      'docs/reports/solinas-generator-cohorts-20261012', 'knowledge/frontiers/ecdlp'):
        for path in sorted((REPO/directory).rglob('*')):
            if path.is_file() and path.suffix in ('.dot', '.svg', '.typ', '.pdf'):
                inventory.append(str(path.relative_to(REPO)))
    (HERE/'graph-inventory.json').write_text(json.dumps({'schema': 1, 'checked_materialized_related_graph_forms': inventory,
        'canonical_update': 'none', 'reason': 'Coordinate feature observations and a universal addition identity establish no new isogeny, endomorphism or attack-cost graph edge. Historical evidence preserved.',
        'scope': 'Exact internal reports/inputs and materialized frontier graph sources; no claim of exhaustive literature search'}, indent=2)+'\n')
    print(json.dumps({'report': str(HERE/'report.pdf'), 'primary_intervals': len(comparisons), 'rarity_benchmarks': len(benchmarks),
                      'outcome': finding, 'post_render_visual_inspection_required': True}))


if __name__ == '__main__': main()
