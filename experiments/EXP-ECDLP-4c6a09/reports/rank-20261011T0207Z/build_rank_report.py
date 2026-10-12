#!/usr/bin/env python3
"""Derive rank tables, explanatory figure, and PDF from immutable run records."""
import csv
import hashlib
import json
import os
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import typst

REPO = Path('/workspace/solinas-run')
BASE = REPO / 'experiments/EXP-ECDLP-4c6a09'
OLD = BASE / 'runs/RUN-ECDLP-aba670'
RUN = BASE / 'runs/RUN-ECDLP-7cfef7'
BOUND = BASE / 'runs/RUN-ECDLP-280de8'
BOUND12 = BASE / 'runs/RUN-ECDLP-959b32'
OUT = BASE / 'reports/rank-20261011T0207Z'
SHAPES = ['P-192', 'P-224', 'P-256', 'P-384']

def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')

def classified(r):
    gain = r['rank_gain_bounds']
    if r.get('conditional_on_grh') and gain:
        return 'GRH conditional'
    if r['status'] == 'exact' and gain:
        return f'Gain {gain[0]}'
    if r['nf_bounds']:
        return 'Bound interval'
    return 'Unresolved'

def group_stats(name, rows):
    exact = [r for r in rows if r['status'] == 'exact']
    positive = [r for r in rows if r['rank_gain_bounds'] and r['rank_gain_bounds'][0] > 0 and not r.get('conditional_on_grh')]
    return {'name': name, 'distinct_pairs': len(rows),
            'status_histogram': dict(Counter(r['status'] for r in rows)),
            'certified_exact_rank_histogram': dict(sorted(Counter(r['nf_bounds'][0] for r in exact).items())),
            'certified_exact_gain_histogram': dict(sorted(Counter(r['rank_gain_bounds'][0] for r in exact).items())),
            'certified_positive_gain_instances': len(positive),
            'rank_gain_intervals': [{'id': r['job']['id'], 'bounds': r['rank_gain_bounds'],
                                     'conditional_on_grh': r.get('conditional_on_grh', False)} for r in rows]}

def diagram():
    fig, ax = plt.subplots(figsize=(10.3, 3.45))
    ax.set(xlim=(0, 10), ylim=(0, 3.4))
    ax.axis('off')
    boxes = [(0.15, 1.55, 2.8, 1.25, '$E(\\mathbb{Q})$\nrank 1\none independent direction', '#e9f1f4'),
             (3.6, 1.55, 3.15, 1.25, '$E(K),\\quad K=\\mathbb{Q}(\\alpha)$\n$\\alpha^3-\\alpha-1=0$\nrank 3: two added directions', '#e9f1f4'),
             (7.4, 1.55, 2.45, 1.25, 'E(F_p)\nfinite point group\nreduction sends points here', '#edf3e9')]
    for x, y, w, h, label, color in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02', facecolor=color, edgecolor='#506776'))
        ax.text(x + w / 2, y + h / 2, label, ha='center', va='center', fontsize=11)
    for a, b in [(2.98, 3.56), (6.8, 7.36)]:
        ax.add_patch(FancyArrowPatch((a, 2.17), (b, 2.17), arrowstyle='-|>', mutation_scale=15, color='#506776'))
    ax.text(3.26, 1.3, 'extend scalars', ha='center', fontsize=10)
    ax.text(7.1, 1.21, 'good reduction\n$\\alpha\\mapsto 2^k$ (mod p)', ha='center', fontsize=10)
    ax.text(5, .49, '$y^2=x^3-3x+3$  •  descent bounds agree: $r_K=3$, $r_{\\mathbb{Q}}=1$\n$P$, $-P$, $2P$ occupy one direction; rank measures independence.', ha='center', fontsize=11)
    ax.set_title('Measured cubic example; finite-field scalar recovery remains a separate question', fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / 'rank-construction.svg')
    plt.close(fig)

def main():
    assert not OUT.exists(), 'Never overwrite a completed historical report'
    OUT.mkdir(parents=True)
    shutil.copy2('/usr/share/common-licenses/GPL-2', OUT / 'GPL-2.txt')
    raw = json.loads((RUN / 'raw-result.json').read_text())
    supplemental = json.loads((BOUND / 'raw-result.json').read_text())
    supplemental12 = json.loads((BOUND12 / 'raw-result.json').read_text())
    plan = json.loads((RUN / 'plan.json').read_text())
    candidates = {r['job']['id']: r for r in supplemental['nf']}
    for r in supplemental12['nf']:
        previous = candidates.get(r['job']['id'])
        if not previous or not previous['nf_bounds'] or r['nf_bounds'] and r['nf_bounds'][1] < previous['nf_bounds'][1]:
            candidates[r['job']['id']] = r
    main_results = {r['job']['id']: r for r in raw['nf']}
    for r in raw['nf']:
        r['derived_source_run'] = OLD.name if r['job']['id'] in plan['reuse_exact_nf_ids'] else RUN.name
    for r in supplemental['nf']:
        r['derived_source_run'] = BOUND.name
        r['bound_method'] = 'Candidate group before local conditions; upper is not asserted equal to Selmer dimension.'
    for r in supplemental12['nf']:
        r['derived_source_run'] = BOUND12.name
        r['bound_method'] = 'Candidate group before local conditions; upper is not asserted equal to Selmer dimension.'
    nf = []
    for j in plan['jobs']:
        r = main_results.get(j['id'])
        extra = candidates.get(j['id'])
        if extra and (not r or not r['nf_bounds'] or r.get('conditional_on_grh') and extra['nf_bounds'] and extra['nf_bounds'][1] < r['nf_bounds'][1]):
            r = extra
        assert r, j['id']
        nf.append(r)
    q = raw['q']
    assert len(nf) == len(plan['jobs']) == 157
    assert len({r['job']['id'] for r in nf}) == 157
    assert len(q) == 335 and all(r['q_bounds'][0] == r['q_bounds'][1] for r in q)
    jobs = {r['job']['id']: r for r in nf}
    expected = {j['id'] for j in plan['jobs']}
    assert set(jobs) == expected
    qb = {(r['job']['A'], r['job']['B']): r['q_bounds'] for r in q}
    for r in nf:
        assert r['q_bounds'] == qb[(r['job']['A'], r['job']['B'])]
        if r['nf_bounds']:
            assert r['nf_bounds'][0] >= r['q_bounds'][0]
            assert r['nf_bounds'][1] >= r['nf_bounds'][0]
    sol = [r for r in nf if 'solinas' in r['job']['arms']]
    groups = [group_stats(s, [r for r in sol if s in r['job']['shapes']]) for s in SHAPES]
    groups += [group_stats('Random cubic', [r for r in nf if r['job']['degree'] == 3 and 'random_g' in r['job']['arms']]),
               group_stats('Pure cubic', [r for r in nf if r['job']['degree'] == 3 and 'tdc' in r['job']['arms']])]
    summary = {'run_id': RUN.name, 'predecessor_run': OLD.name, 'candidate_bound_runs': [BOUND.name, BOUND12.name], 'rank_baselines': len(q),
               'q_rank_histogram': dict(sorted(Counter(r['q_bounds'][0] for r in q).items())),
               'distinct_nf_pairs': len(nf), 'distinct_solinas_pairs': len(sol), 'groups': groups,
               'nf_status_histogram': dict(Counter(r['status'] for r in nf)),
               'main_gp_instances_started': len(list((RUN/'instances').glob('*/launch.json'))),
               'candidate_gp_instances_started': len(list((BOUND/'instances').glob('*/launch.json'))),
               'degree_12_gp_instances_started': len(list((BOUND12/'instances').glob('*/launch.json'))),
               'reused_exact_nf_count': len(plan['reuse_exact_nf_ids']),
               'failed_or_unfinished': [{'id': r['job']['id'], 'degree': r['job']['degree'], 'errors': r['errors'],
                                        'timed_out': r['timed_out'], 'status': r['status']} for r in nf if r['status'] not in ['exact', 'conditional_exact']],
               'raw_sha256': hashlib.sha256((RUN / 'raw-result.json').read_bytes()).hexdigest(),
               'candidate_raw_sha256': hashlib.sha256((BOUND / 'raw-result.json').read_bytes()).hexdigest(),
               'degree_12_raw_sha256': hashlib.sha256((BOUND12 / 'raw-result.json').read_bytes()).hexdigest(),
               'source_raw_sha256': plan['source_raw_sha256'],
               'created_at_utc': datetime.now(timezone.utc).isoformat(),
               'validation': 'Complete planned identities, exact Q baselines, matching baseline bounds, consistent extension bounds; all emitted points checked by ellisoncurve.',
               'independent_scientific_review_performed': False,
               'dominated_by': 'Standard number-field 2-descent; this is use and compatibility repair of existing Simon/PARI code, not a new rank algorithm.',
               'sota_delta': {'ecdlp_algorithmic_improvement': None, 'measured_quantity': 'r(E/K)-r(E/Q) on declared toy-input models'},
               'graphs_checked': ['Historical G3 construction/coverage/gamma/discriminant figures', 'knowledge/frontiers/ecdlp path inventory'],
               'canonical_graph_change': 'None: no ECDLP measured bound or promoted research conclusion. Add a fresh rank graph; preserve old point-search reports.'}
    dump(OUT / 'summary.json', summary)
    dump(OUT / 'combined-ranks.json', {'nf': nf, 'q': q, 'derivation': 'Use certified full descent where available, otherwise separate candidate bound. All raw records remain unchanged.'})
    headers = ['id', 'degree', 'arms', 'shapes', 'g', 'A', 'B', 'q_lower', 'q_upper', 'k_lower', 'k_upper', 'gain_lower', 'gain_upper', 'status', 'conditional_on_grh', 'elapsed_seconds', 'source_cell_indices', 'source_run']
    with (OUT / 'ranks.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for j in plan['jobs']:
            r = jobs[j['id']]
            kb, gb = r['nf_bounds'] or [None, None], r['rank_gain_bounds'] or [None, None]
            writer.writerow({'id': j['id'], 'degree': j['degree'], 'arms': ','.join(j['arms']), 'shapes': ','.join(j['shapes']),
                             'g': json.dumps(j['g']), 'A': j['A'], 'B': j['B'], 'q_lower': r['q_bounds'][0], 'q_upper': r['q_bounds'][1],
                             'k_lower': kb[0], 'k_upper': kb[1], 'gain_lower': gb[0], 'gain_upper': gb[1],
                             'status': r['status'], 'conditional_on_grh': r.get('conditional_on_grh', False),
                             'elapsed_seconds': r['elapsed_seconds'], 'source_cell_indices': json.dumps(j['source_cell_indices']),
                             'source_run': r['derived_source_run']})
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'svg.fonttype': 'none', 'figure.dpi': 160,
                         'axes.spines.top': False, 'axes.spines.right': False})
    diagram()
    rows = [('Solinas cubic', [r for r in sol if r['job']['degree'] == 3]),
            ('Random cubic', [r for r in nf if r['job']['degree'] == 3 and 'random_g' in r['job']['arms']]),
            ('Pure cubic', [r for r in nf if r['job']['degree'] == 3 and 'tdc' in r['job']['arms']])]
    max_gain = max([r['rank_gain_bounds'][0] for _, rr in rows for r in rr if r['status'] == 'exact'] + [2])
    cats = [f'Gain {i}' for i in range(max_gain + 1)] + ['Bound interval', 'Unresolved']
    colors = ['#597d8a', '#239979', '#19845c', '#075d43', '#00452f'][:max_gain + 1] + ['#c7a853', '#b7bdc2']
    fig, ax = plt.subplots(figsize=(9.5, 3.5))
    left = np.zeros(len(rows))
    for cat, color in zip(cats, colors):
        counts = np.array([sum(classified(r) == cat for r in rr) for _, rr in rows])
        vals = np.array([100 * n / len(rr) for n, (_, rr) in zip(counts, rows)])
        ax.barh(range(len(rows)), vals, left=left, color=color, label=cat)
        for i, (n, v) in enumerate(zip(counts, vals)):
            if n and v >= 6:
                ax.text(left[i] + v / 2, i, str(n), ha='center', va='center', color='white' if cat.startswith('Gain') else '#263238', fontsize=11)
        left += vals
    ax.set(yticks=range(len(rows)), yticklabels=[f'{name} (n={len(rr)})' for name, rr in rows], xlim=(0, 100),
           xlabel='Percent of distinct field/curve pairs; labels are counts', title='Certified rank gain above the rational baseline: cubic fields')
    ax.invert_yaxis()
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.25), ncol=min(5, len(cats)), frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / 'cubic-rank-gain.svg', bbox_inches='tight')
    plt.close(fig)
    states = [('exact', '#239979', 'Certified exact'), ('bounds', '#c7a853', 'Certified interval'),
              ('conditional_exact', '#6d85b2', 'GRH conditional, bounds agree'), ('conditional_bounds', '#9fadd0', 'GRH conditional interval'),
              ('error', '#d8b0ab', 'Tool error'), ('unfinished', '#b7bdc2', 'Watchdog / unfinished')]
    fig, ax = plt.subplots(figsize=(9.5, 3.5))
    bottom = np.zeros(4)
    for status, color, label in states:
        counts = np.array([sum(r['status'] == status for r in sol if s in r['job']['shapes']) for s in SHAPES])
        ax.bar(range(4), counts, bottom=bottom, color=color, label=label)
        for i, n in enumerate(counts):
            if n: ax.text(i, bottom[i] + n / 2, str(n), ha='center', va='center', fontsize=10)
        bottom += counts
    ax.set(xticks=range(4), xticklabels=['Cubic\nn=43', 'Degree 7\nn=15', 'Degree 8\nn=15', 'Degree 12\nn=15'],
           ylabel='Distinct Solinas field/curve pairs', title='Rank computation outcomes, including every unresolved case')
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.25), ncol=2, frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / 'solinas-rank-status.svg', bbox_inches='tight')
    plt.close(fig)
    table = '\n'.join(f"| {g['name']} | {g['distinct_pairs']} | {g['status_histogram'].get('exact',0)} | {g['status_histogram'].get('bounds',0)} | {g['status_histogram'].get('conditional_exact',0)+g['status_histogram'].get('conditional_bounds',0)} | {g['status_histogram'].get('error',0)+g['status_histogram'].get('unfinished',0)} | {g['certified_positive_gain_instances']} |" for g in groups)
    examples = [(r['job']['A'], r['job']['B'], r['q_bounds'][0], r['nf_bounds'][0], r['rank_gain_bounds'][0], r['job']['id']) for r in sol if r['status'] == 'exact' and r['rank_gain_bounds'][0] > 0]
    examples.sort(key=lambda x: (-x[4], x[0], x[1]))
    example_table = '\n'.join(f'| {A} | {B} | {rq} | {rk} | {gain} | `{ident}` |' for A,B,rq,rk,gain,ident in examples)
    md = f'''# Solinas rank follow-up — 2026-10-11 UTC

Measured follow-up for **EXP-ECDLP-4c6a09**, **H-ECDLP-4da36f**, **GOAL-ECDLP-001**.
The user authorized this additive work by asking “Measure rank.” The original
coverage experiment remains unchanged; it did not measure rank.

## What was measured

All **335 distinct rational curves** have exact PARI rank bounds. Their rank
distribution is **{summary['q_rank_histogram']}**. This follow-up covers **157 distinct
number-field/curve pairs**, including every **88 distinct Solinas pairs** and every
original cubic control. Higher-degree random and pure-field controls are outside
this follow-up scope. The original cells remain mapped in [ranks.csv](ranks.csv).
Rank depends on the characteristic-zero model and field, not on the toy reduction
prime, k, or original seed, so identical pairs are measured once.

| Arm / shape | Pairs | Certified exact | Certified interval | GRH conditional | Error / unfinished | Certified positive gain |
|---|---:|---:|---:|---:|---:|---:|
{table}

“Certified” means the tool's class/unit data were checked with bnfcertify,
large-prime local success required an exact square witness, and automatic
Sha-square parity lower-bound increases were disabled. This is a computation
record, not an independent review or a research-status promotion.

## Concrete positive cubic cases

For **K = Q(alpha), alpha³-alpha-1 = 0**, the following short models
**y² = x³ + Ax + B** have certified exact rank gains. The CSV contains all cases,
including zero gain and unresolved intervals.

| A | B | Rank over Q | Rank over K | Added rank | Instance |
|---:|---:|---:|---:|---:|---|
{example_table or '| — | — | — | — | — | No certified positive result |'}

For **A=-3, B=3**, rank over Q is **1** and rank over K is **3**. Three
representatives found by descent are

* (1, 1);
* (1-2 alpha, -2 alpha²+2 alpha-1);
* ((6 alpha²+7 alpha-27)/25, (-121 alpha²-162 alpha+182)/125).

All point equations were checked exactly in K. Descent certified three
independent classes modulo 2 and a 2-Selmer upper bound of three. They need not
be a saturated integral basis; equality of rank bounds determines rank without
claiming saturation. This field has no rational 2-torsion for this curve.

The field relation is doing concrete algebraic work. If x=1-2 alpha and
y=-2 alpha²+2 alpha-1, then
**y²-(x³-3x+3) = 4 alpha (alpha³-alpha-1) = 0**.
That identity supplies a point. Descent supplies the additional independence
check that turns the point supply into a rank measurement.

![Rank and reduction](rank-construction.svg)

## How to read rank

The group E(K) has a finite torsion part and a free part Z^r. Rank r is the
number of independent infinite-order directions. P, -P, and 2P belong to
one direction; many discovered points can still have rank one. Field extension
can add directions, and the measured quantity is r(E/K)-r(E/Q).

2-descent finds classes that give a lower rank bound and a Selmer group that
gives an upper bound. The raw Selmer dimension includes rational 2-torsion:
subtract dimension 0, 1, or 2 according as x³+Ax+B has 0, 1, or 3 roots in K.
The base-field lower bound also remains valid after extension. If the bounds
coincide, the tool determines the rank; otherwise it reports an interval.

This characteristic-zero rank is separate from the finite group E(F_p).
Good reduction sends algebraic points into that finite group, where they can
collapse together. Rank gain alone supplies no unknown-scalar recovery method.
The structure measured here is the Mordell-Weil group E(K). Additional
endomorphisms require explicit algebraic maps; this rank follow-up does not
compute an endomorphism ring or a GLV decomposition.

## Comparisons and missing information

![Cubic rank gains](cubic-rank-gain.svg)

Each arm counts its distinct field/model pairs. Arms overlap: the random
generator can draw the Solinas polynomial itself, and some other defining
polynomials yield isomorphic fields. We did not merge identities using an
unverified isomorphism. These counts therefore do not constitute independent
field samples or establish a Solinas advantage. No conditional bound or unknown
value is averaged as though exact. No statistical significance claim is made.

![All Solinas computation outcomes](solinas-rank-status.svg)

Higher-degree auxiliary class/unit data may retain the generalized Riemann
hypothesis (GRH) assumption of bnfinit. Every such result is explicitly labeled
conditional, even if its bounds agree. Missing number-field upper bounds remain
missing. Watchdogs, a failed local test, or an API failure do not imply rank zero
or absence of rank gain. All rational baselines remain available.
GRH is an unproved conjecture about zeros of certain L-functions. It supports
the completeness bounds used by the class-group algorithm; bnfcertify can
remove that dependency, at substantial cost in the auxiliary fields of
degrees 21, 24 and 36 arising from these larger extensions.

## Execution and source provenance

Predecessor **RUN-ECDLP-aba670** measured 335 exact rational ranks and was stopped
after exposing a projective-output compatibility error and a residue-table
allocation overflow. Its completed results are retained. **RUN-ECDLP-7cfef7**
reuses **{len(plan['reuse_exact_nf_ids'])}** error-free exact number-field results,
completes every remaining cubic instance, and preserves any higher-degree
descents actually started. **RUN-ECDLP-280de8** and **RUN-ECDLP-959b32** measure
candidate-group upper bounds for all 45 higher-degree Solinas pairs, with the
degree-12 workload split into the latter record using the identical method.
In the general no-2-torsion case,
the norm-square kernel before local tests contains the Selmer group, so its
dimension is an upper bound; it is not asserted equal to the Selmer dimension.
With 2-torsion, the two descent images inject into K(S,2), giving
r <= 2 dim K(S,2)-2. Its rough-bound controls contain known ranks 1 and 3.
No additional NF rank lower bound comes from this upper-bound-only method.

The two full-descent workers and two candidate-bound workers overlap on this
four-CPU-quota host. Each has a 4 GiB address-space cap, initial stack
128 MiB, max stack 2 GB, fixed seed 1, precision 80 decimal digits, and a 120 s
process watchdog. Cubic point searches use LIMTRIV=2 then 4 when needed,
LIM1=LIM3=2; higher-degree initial searches use zero limits and supplied rational
points. Results and all aborted stages are retained. These are machine/process
limits, not a negative mathematical conclusion or campaign closure.

Simon source is pinned to Sage commit
`46a9468cf7fccca63c6b873cb52b73ea141da068`. Original and modified files, exact
patches, URLs, and SHA256 values are retained in
[source provenance](../../runs/{RUN.name}/source/provenance.json). The modified
copy certifies class/unit data, disables both automatic Sha parity increases,
normalizes projective outputs before PARI point changes, caps exact residue
enumeration, and throws on an unresolved large-prime test. Randomized local
search only accepts an exactly verified positive witness; it never supplies a
negative obstruction after failed sampling.

Sources retrieved and read in this session: Sage's
[rank_bounds wrapper](https://github.com/sagemath/sage/blob/46a9468cf7fccca63c6b873cb52b73ea141da068/src/sage/schemes/elliptic_curves/ell_number_field.py)
and [Simon GP code](https://github.com/sagemath/sage/tree/46a9468cf7fccca63c6b873cb52b73ea141da068/src/sage/ext_data/pari/simon).
Original input source (internal/retrieved):
[PR #2035](https://github.com/aburan28/crypto-autoresearcher/pull/2035), original
coverage commit `8e1cc6c5313fdab887d09b98a712ea05996d7b18`.
No independent mathematical review was performed. This uses standard 2-descent;
no improvement to rank algorithms or ECDLP complexity is asserted.

## Evidence and reproduction

* [Frozen plan](../../runs/{RUN.name}/plan.json)
* [Cubic descent raw JSON and actual scope](../../runs/{RUN.name}/raw-result.json)
* [Higher-degree candidate-bound raw JSON](../../runs/{BOUND.name}/raw-result.json)
* [Degree-12 candidate-bound raw JSON](../../runs/{BOUND12.name}/raw-result.json)
* [Predecessor raw JSON](../../runs/{OLD.name}/raw-result.json)
* [Rational and number-field instance logs](../../runs/{RUN.name}/instances/)
* [Runner source](../../runs/{RUN.name}/source/run_rank.py)
* [Summary and consistency checks](summary.json)
* [All rank bounds and exact identities](ranks.csv)
* [Combined derived ranks with source-run identity](combined-ranks.json)

Follow-up raw SHA256: `{summary['raw_sha256']}`.
Candidate-bound raw SHA256: `{summary['candidate_raw_sha256']}`.
Degree-12 raw SHA256: `{summary['degree_12_raw_sha256']}`.
Original coverage raw SHA256: `{plan['source_raw_sha256']}`.
Use the pinned GP library and extracted PARI 2.17.2 runtime, then copy the plan
and sources into a fresh output directory before execution. Never overwrite
these completed records. GP can exit zero after errors; this runner parses
explicit sentinels, retains errors and watchdogs, and checks all returned points.

Graphs checked: historical G3 construction/coverage/gamma/discriminant figures
and the canonical ECDLP frontier path inventory. Existing historical graphs
stay intact. The new rank graph reflects this new evidence; no ECDLP bound,
frontier record, hypothesis status, or experiment status was changed.
'''
    (OUT / 'report.md').write_text(md)
    short_rows = [str(x) for g in groups[:4] for x in []]
    typ_rows = ',\n'.join('['+str(x)+']' for g in groups[:4] for x in [g['name'], g['distinct_pairs'], g['status_histogram'].get('exact',0),
                       g['status_histogram'].get('conditional_exact',0)+g['status_histogram'].get('conditional_bounds',0),
                       g['status_histogram'].get('bounds',0)+g['status_histogram'].get('error',0)+g['status_histogram'].get('unfinished',0)])
    total_exact = sum(r['status'] == 'exact' for r in nf)
    total_positive = sum(bool(r['rank_gain_bounds'] and r['rank_gain_bounds'][0]>0 and not r.get('conditional_on_grh')) for r in nf)
    typ = f'''#set page(paper: "a4", margin: 16mm)
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false, leading: .65em)
#set heading(numbering: none)
#set page(footer: context align(right)[Solinas rank follow-up · #counter(page).display()])
= Solinas rank measurements
2026-10-11 UTC · EXP-ECDLP-4c6a09 · Observations, with unresolved cases retained

*First cubic case: rank 1 over Q, rank 3 over K — two added independent directions.*
The curve is $y^2=x^3-3x+3$ and $K=QQ(alpha)$, with $alpha^3-alpha-1=0$.
Certified descent lower and upper bounds agree. This is a computation using
standard 2-descent, not an independently reviewed research-state transition.

#figure(image("rank-construction.svg", width: 100%), caption: [Measured cubic
example. Reduction can identify points; a higher characteristic-zero rank alone
does not recover an unknown finite-field scalar.])

== What rank counts
The free part of E(K) is $ZZ^r$: rank counts independent directions. P, −P,
and 2P count as one direction. The experiment measures the added rank
$r_K-r_Q$, using a rational baseline for each curve.

2-descent supplies a lower bound and a Selmer upper bound. Subtract rational
2-torsion from the raw Selmer dimension. Equal bounds determine rank;
different bounds leave an interval. Both automatic Sha-square/parity lower
bound increases in the inherited code were disabled.

== Actual input coverage
*335 distinct rational curves, all exact:* rank 0: 108; rank 1: 181;
rank 2: 45; rank 3: 1. The follow-up contains *157 distinct number-field/curve
pairs*, including all *88 Solinas pairs* and all original cubic controls.
Higher-degree random/pure-field controls are outside this scope. There are
*{total_exact} certified exact NF ranks* and *{total_positive} certified positive
rank gains* across the distinct follow-up pairs.

Source: #link("../../runs/{RUN.name}/raw-result.json")[{RUN.name}],
#link("../../runs/{BOUND.name}/raw-result.json")[{BOUND.name}],
#link("../../runs/{BOUND12.name}/raw-result.json")[{BOUND12.name}], and
#link("../../runs/{OLD.name}/raw-result.json")[{OLD.name}].

#pagebreak()
= Results, including what remains unresolved
#figure(image("cubic-rank-gain.svg", width: 100%), caption: [Cubic rank gain
above each curve's rational baseline. Labels count distinct pairs; gray means
no completed NF bound. Arm membership can overlap. No independence or
statistical-significance claim is made.])

#figure(image("solinas-rank-status.svg", width: 100%), caption: [All 88 distinct
Solinas cases. GRH-conditional data remain distinct from certified ranks.])

#table(columns: (1.35fr, .7fr, .8fr, 1fr, 1.2fr), inset: 5pt,
  [Solinas shape], [Pairs], [Certified exact], [GRH conditional], [Interval / unresolved],
  {typ_rows})

GRH means the generalized Riemann hypothesis. Higher-degree auxiliary
class/unit data were not all verified with bnfcertify. Those rank bounds keep
that assumption, including when the two bounds agree. A missing NF upper bound,
tool error or watchdog does not mean rank zero. Higher-degree curves can gain
rank even when the earlier point-search run found no new points.

#pagebreak()
= Reproduction and interpretation
== The concrete cubic example
Descent found representatives $(1,1)$,
$(1-2alpha,-2alpha^2+2alpha-1)$ and
$((6alpha^2+7alpha-27)/25,(-121alpha^2-162alpha+182)/125)$.
All equations were checked exactly. Three independent mod-2 classes and
an upper rank bound of three determine rank three. A saturated basis was
not computed or claimed.

The field relation supplies a concrete point: for
$x=1-2alpha$ and $y=-2alpha^2+2alpha-1$,
$y^2-(x^3-3x+3)=4alpha(alpha^3-alpha-1)=0$.
Descent then certifies its role among independent directions.

== Tool repairs and exact scope
The first batch measured all rational ranks, then exposed an output-format
incompatibility and an enormous residue-field allocation. It was stopped and
retained. The follow-up reuses {len(plan['reuse_exact_nf_ids'])} error-free exact
NF results and completes the remaining cubic instances. A separate run measures
candidate-group upper bounds for all 45 higher-degree pairs, before local
conditions and quartic searches. This is an upper bound, not an asserted
exact Selmer dimension. Modified Simon
code normalizes projective output and caps explicit residue enumeration.
Large-prime local search must produce an exactly checked square witness;
an unresolved search throws rather than inferring an obstruction.

PARI 2.17.2; pinned Sage source commit
#text(size: 8pt)[46a9468cf7fccca63c6b873cb52b73ea141da068].
At most four GP workers; 4 GiB address space each; 128 MiB initial stack,
2 GB maximum stack; seed 1; 80-digit real precision; 120 s process watchdog.
Cubic LIMTRIV=2 then 4, LIM1=LIM3=2. Larger-degree initial searches use
zero limits and supplied rational points. All class/unit data are certified
for cubic calculations; larger auxiliary data retain explicit GRH labels.

== Limits on the interpretation
Rank depends on K and the characteristic-zero curve model, so repeated
reduction primes do not add independent rank measurements. Random draws can
include the Solinas polynomial itself; different defining polynomials can
give isomorphic fields. These data do not establish a special Solinas rank
advantage. No unknown finite-field scalar was recovered and no ECDLP cost
bound was measured. Standard Simon/PARI 2-descent is the method being used.

== Sources and immutable evidence
#link("report.md")[Full report and concrete positive cases] ·
#link("ranks.csv")[All 157 bounds and curve/field identities] ·
#link("summary.json")[Summary and consistency checks].

#link("../../runs/{RUN.name}/plan.json")[Frozen input plan] ·
#link("../../runs/{RUN.name}/source/provenance.json")[Exact source patches and hashes] ·
#link("https://github.com/sagemath/sage/blob/46a9468cf7fccca63c6b873cb52b73ea141da068/src/sage/schemes/elliptic_curves/ell_number_field.py")[Sage rank-bounds wrapper] ·
#link("https://github.com/sagemath/sage/tree/46a9468cf7fccca63c6b873cb52b73ea141da068/src/sage/ext_data/pari/simon")[Simon GP source].

Raw follow-up SHA256: #text(size: 7pt)[{summary['raw_sha256']}].
The original coverage report and raw JSON remain unchanged. No canonical
ECDLP frontier graph or scientific status was promoted. Sources are retrieved
or internal; algebraic explanations are derived; ranks/bounds are measured.
'''
    (OUT / 'report.typ').write_text(typ)
    typst.compile(str(OUT / 'report.typ'), output=str(OUT / 'report.pdf'), root=str(BASE))
    shutil.copy2(Path(__file__), OUT / 'build_rank_report.py')
    print(json.dumps({'report': str(OUT / 'report.pdf'), 'status_histogram': summary['nf_status_histogram'], 'groups': [{k:v for k,v in g.items() if k!='rank_gain_intervals'} for g in groups]}, indent=2))

if __name__ == '__main__':
    main()
