#!/usr/bin/env python3
"""Derived communication and requested confidence sensitivity; preserves raw files."""
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RUN = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUN / 'measurement-source'))
from common import sha, write
from curve_identity import curve_identity
from finite_math import Curve


def load(path):
    return json.loads((RUN / path).read_text())


def bootstrap(rows, key, exponent=True):
    rng = np.random.default_rng(2026101121)
    counts, draws = [], []
    for bits in sorted({r['bits'] for r in rows}):
        xs = np.asarray([r[key] for r in rows if r['bits'] == bits])
        counts.append(len(xs))
        draws.append(xs[rng.integers(len(xs), size=(200000, len(xs)))].mean(axis=1))
    values = sum(n * v for n, v in zip(counts, draws)) / sum(counts)
    convert = math.exp if exponent else float
    return {'estimate': convert(np.mean([r[key] for r in rows])),
            'CI99_9': [convert(v) for v in np.quantile(values, [.0005, .9995])],
            'prime_blocks': len(rows)}


def main():
    out = RUN / 'report'
    out.mkdir(exist_ok=False)
    summary = load('analysis/summary.json')
    groups = load('preparation/public-groups.json')
    gm = {g['group_id']: g for g in groups}
    jobs = {j['job_id']: j for j in load('attacks/job-index.json')}
    targets = {t['id']: t for t in load('preparation/public-targets.json')}
    identities = [{**g, 'purpose': 'original attack group'} for g in groups]
    bsgs_count = 0
    censored = defaultdict(int)
    actual_endpoints, endpoint_jobs = {}, []
    for path in sorted((RUN / 'attacks').glob('block-*/raw-results.jsonl')):
        raw = {r['job_id']: r for r in map(json.loads, path.read_text().splitlines())}
        for r in raw.values():
            censored[r['mode']] += r['censored']
            if r['mode'] == 'bsgs':
                M = r['M']
                assert r['counts']['setup']['group_calls'] == M + M.bit_count() + M.bit_length() - 1
                assert r['counts']['search']['group_calls'] == r['scalar'] // M
                bsgs_count += 1
        for line in (path.parent / 'public-jobs.txt').read_text().splitlines():
            jid, mode, adding, seed, *vals = line.split()
            if mode not in ['native_iso', 'transport']:
                continue
            p, A, B, ell, h, gx, gy, qx, qy, u = map(int, vals)
            j, g = jobs[jid], gm[jobs[jid]['group_id']]
            t = targets[j['target_id']]
            assert u % p and A == g['A'] * pow(u, 4, p) % p and B == g['B'] * pow(u, 6, p) % p
            assert [gx, gy] == [g['G'][0] * pow(u, 2, p) % p, g['G'][1] * pow(u, 3, p) % p]
            assert [qx, qy] == [t['Q'][0] * pow(u, 2, p) % p, t['Q'][1] * pow(u, 3, p) % p]
            curve = Curve(p, A, B)
            assert curve.on_curve((gx, gy)) and curve.on_curve((qx, qy))
            assert curve.mul((gx, gy), ell) is None
            assert raw[jid]['scalar'] is not None and curve.mul((gx, gy), raw[jid]['scalar']) == (qx, qy)
            model = {**g['curve'], 'a4': A, 'a6': B, 'generator': [gx, gy]}
            identity = curve_identity(g['field'], model, 'primecomparison')
            actual_endpoints[g['group_id']] = {**g, 'group_id': g['group_id'] + '-iso', 'A': A, 'B': B,
                'G': [gx, gy], 'curve': model, 'identity': identity, 'purpose': 'degree-1 isomorphic control',
                'source_curve_uid': g['identity']['curve_uid'], 'map_degree': 1, 'u': u}
            endpoint_jobs.append({'job_id': jid, 'mode': mode, 'endpoint_curve_uid': identity['curve_uid'],
                                  'subgroup_and_recovered_scalar_checked_on_actual_endpoint': True})
    identities.extend(actual_endpoints.values())
    write(out / 'isomorphism-identities.json', {'endpoints': list(actual_endpoints.values()), 'jobs': endpoint_jobs,
          'map': '(x,y) -> (u^2*x,u^3*y), nonzero u in F_p, degree 1; inverse uses u^-1'})
    arithmetic_identities = []
    arithmetic_rows = []
    for path in sorted((RUN / 'arithmetic').glob('m*/result.json')):
        r = json.loads(path.read_text())
        m = r['modulus']
        row = load('preparation/curves/' + m['id'] + '/curves.json')['curves'][0]
        pc = r['public_curve']
        assert (pc['p'], pc['A'], pc['B']) == (row['p'], row['A'], row['B'])
        field = {'characteristic': pc['p'], 'degree': 1, 'representation': 'prime field, canonical integer residues',
                 'element_encoding': 'integers 0..p-1', 'modulus': pc['p']}
        curve = {'model': 'short-Weierstrass', 'a4': pc['A'], 'a6': pc['B'], 'subgroup_order': row['ell'],
                 'cofactor': row['h'], 'generator': pc['G'], 'target_group': 'prime-order cyclic subgroup of E(F_p)'}
        assert Curve(pc['p'], pc['A'], pc['B']).mul(tuple(pc['G']), row['ell']) is None
        arithmetic_identities.append({**m, **pc, 'group_id': 'arithmetic-' + m['id'], 'ell': row['ell'], 'h': row['h'],
            'field': field, 'curve': curve, 'identity': curve_identity(field, curve, 'primecomparison'),
            'purpose': 'arithmetic microbenchmark'})
        arithmetic_rows.extend({**m, **v} for v in r['observations'])
    identities.extend(arithmetic_identities)
    write(out / 'arithmetic-curve-identities.json', arithmetic_identities)
    with (out / 'all-curve-identities.csv').open('x', newline='') as handle:
        columns = ['purpose', 'group_id', 'curve_uid', 'field_sha256', 'p', 'A', 'B', 'ell', 'h', 'Gx', 'Gy']
        w = csv.DictWriter(handle, fieldnames=columns, lineterminator='\n')
        w.writeheader()
        w.writerows({**{k: g[k] for k in columns[:2] + ['p', 'A', 'B', 'ell', 'h']},
          'curve_uid': g['identity']['curve_uid'], 'field_sha256': g['identity']['field_sha256'],
          'Gx': g['G'][0], 'Gy': g['G'][1]} for g in identities)
    blocks = load('analysis/prime-block-metrics.json')
    requested = {'status': 'Post-run sensitivity requested by user; original prespecified CI99 unchanged',
        'confidence_level': .999, 'bootstrap_replicates': 200000, 'seed': 2026101121,
        'method': 'Percentile bootstrap of whole prime blocks, resampled within bit-size strata; marginal intervals',
        'attack_comparisons': {}, 'population_generic_proxy_difference_bits': {}, 'arithmetic': {}}
    for key in summary['attack_comparisons']:
        mode, _, arm = key.split('_')
        requested['attack_comparisons'][key] = bootstrap([r for r in blocks if r['mode'] == mode and r['contrast'] == 'S/' + arm], 'log_ratio')
    audit = load('analysis/unconditional-audit.json')
    for arm in ['R', 'C']:
        rows = []
        for block in range(36):
            s = next(r for r in audit if r['block'] == block and r['arm'] == 'S')
            c = next(r for r in audit if r['block'] == block and r['arm'] == arm)
            rows.append({'bits': s['bits'], 'difference': s['mean_generic_proxy_bits'] - c['mean_generic_proxy_bits']})
        requested['population_generic_proxy_difference_bits']['S_' + arm] = bootstrap(rows, 'difference', False)
    for work in ['products', 'inversions', 'point_additions']:
        rows = []
        for block in range(36):
            times = {arm: np.median([r['seconds_per_operation'] for r in arithmetic_rows if r['block'] == block
                and r['arm'] == arm and r['workload'] == work and r['backend'] == 'generic']) for arm in ['S', 'R', 'C']}
            rows.append({'bits': next(r['bits'] for r in audit if r['block'] == block),
                         'S_R': math.log(times['S'] / times['R']), 'S_C': math.log(times['S'] / times['C'])})
        requested['arithmetic'][work] = {key: bootstrap(rows, key) for key in ['S_R', 'S_C']}
    write(out / 'requested-confidence-99_9.json', requested)
    write(out / 'post-run-diagnostics.json', {'label': 'Derived accounting; not a new attack trial or changed primary analysis',
        'BSGS_jobs_exactly_accounted': bsgs_count, 'BSGS_setup_calls': 'M + popcount(M) + bit_length(M) - 1',
        'BSGS_search_calls': 'floor(recovered_scalar/M)',
        'interpretation': 'With M fixed from ell, measured BSGS group calls depend on ell and scalar position; no p-shape term',
        'censored_jobs_by_mode': dict(censored), 'actual_isomorphism_endpoint_checks': len(endpoint_jobs),
        'curve_identity_rows': len(identities), 'source_sha256': sha(Path(__file__)),
        'graphs_checked': ['This run communication figures', 'historical prime-resistance design report', 'knowledge/frontiers/ecdlp/'],
        'canonical_graph_change': 'None: observations do not supply a new mechanism, sealed bound or paired challenge verdict',
        'dominated_by': 'Generic rho and memory-accounted BSGS; no asymptotic algorithm or ledger cost-bound claim'})

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.fonttype': 'none', 'svg.hashsalt': 'RUN-ECDLP-a24605'})
    fig, ax = plt.subplots(figsize=(8, 3.8))
    names, xs = [], []
    for mode, label in [('rho', 'Native rho, 16 adding'), ('oracle', 'Opaque rho, 16 adding'), ('rho32', 'Native rho, 32 adding'), ('bsgs', 'BSGS, fixed memory cap')]:
        names.append(label)
        xs.append(requested['attack_comparisons'][mode + '_S_R'])
    for y, v in enumerate(xs):
        a, z = v['CI99_9']
        ax.errorbar(v['estimate'], y, xerr=[[v['estimate'] - a], [z - v['estimate']]], fmt='o', capsize=4, color='#236478')
        ax.annotate(f"{v['estimate']:.4f} [{a:.4f}, {z:.4f}]", (1.09, y), fontsize=9, va='center')
    ax.axvline(1, color='gray', linestyle='--')
    ax.set(yticks=range(4), yticklabels=names, xlim=(.93, 1.20), xlabel='Solinas / random normalized group work (dimensionless)')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=.2)
    fig.suptitle('36 prime blocks · marginal 99.9% whole-block bootstrap intervals')
    fig.text(.5, .01, 'RUN-ECDLP-a24605; BSGS accounting depends exactly on ell, M and scalar position.', ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .05, 1, .95))
    fig.savefig(out / 'attack-ratios.svg')
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 2.7))
    ax.axis('off')
    boxes = [(.02, '36 sampled Solinas primes\n+ 72 matched random primes'), (.36, '32 unconditional models / prime\n512 candidate models / prime'), (.70, '8 matched groups / arm\n4 targets × 4 rho seeds')]
    for x, text in boxes:
        ax.text(x + .135, .58, text, ha='center', va='center', fontsize=9,
                bbox={'boxstyle': 'round,pad=.7', 'facecolor': '#e7f0f3', 'edgecolor': '#236478'})
    for x in [.30, .64]:
        ax.annotate('', xy=(x + .045, .58), xytext=(x, .58), arrowprops={'arrowstyle': '->', 'color': '#236478'})
    ax.text(.5, .18, 'Conditional attacks separate subgroup-size effects from group work.\nOpaque, independent walk, sham, replay and isomorphism controls accompany native rho.', ha='center', fontsize=10)
    fig.suptitle('Frozen sample → group matching → synthetic unknown-scalar trials')
    fig.text(.5, .02, 'Cohort workflow; not an isogeny graph. Six exact-prime case studies remain separate.', ha='center', fontsize=8)
    fig.tight_layout()
    fig.savefig(out / 'workflow.svg')
    plt.close(fig)

    primary = requested['attack_comparisons']['rho_S_R']
    lo, hi = primary['CI99_9']
    table = '\n'.join(f"| {key} | {v['estimate']:.6f} | {v['CI99_9'][0]:.6f}–{v['CI99_9'][1]:.6f} |" for key, v in requested['attack_comparisons'].items())
    md = f'''# Solinas prime comparison — 2026-10-11

Measured primary native-rho Solinas/random ratio: **{primary['estimate']:.6f}**, requested marginal **99.9% CI [{lo:.6f}, {hi:.6f}]**. The originally frozen 99% CI is [0.974189, 1.030343]. Both lie inside the declared practical-similarity margin [1/1.2, 1.2]. This sample does not support a material increase in generic attack cost from the sampled sparse prime forms.

The requested 99.9% intervals are a labeled post-run sensitivity analysis with 200,000 whole-prime-block bootstrap replicates. They do not replace the immutable prespecified analysis. A larger prospective sample follows the user's subsequent request; these intervals do not claim joint family-wise coverage or exact finite-sample coverage.

## Measured scope and controls

EXP-ECDLP-5184f7 / RUN-ECDLP-a24605 sampled 36 distinct 24/28/32-bit sparse primes with one size-matched random control and one size-and-mod-12-matched random control each. The sparse catalog is p=2^b−2^a+s2^c+t, 1≤c<a≤b−2, s,t∈{{−1,1}}, deduplicated by integer. Prime blocks receive equal weight; seeds and targets are repetitions, not independent prime samples.

There are 108 main moduli, 18 additional exact-prime case-study moduli, 61,632 nonsingular prepared models, 864 matched main groups, 96 case-study groups and three easy groups. All **47,292** attack jobs completed without infrastructure failure. All returned scalars and collision equations passed the runner checks. Main rho censoring is zero; two easy rho jobs reached their cap, and their complete-coverage BSGS positive controls passed. All **288** sham/replay/transport checks passed. The derived supplement checks 192 isomorphic jobs on their actual endpoint curves and lists 1,095 exact EC1 identities.

![Workflow](workflow.svg)

## Attack comparisons

| Contrast | Ratio | Marginal 99.9% interval |
|---|---:|---:|
{table}

![Work ratios](attack-ratios.svg)

Rho measures restricted mean search group calls / sqrt(ell), horizon 20; setup and verification are retained separately. BSGS uses setup+search divided by M+ell/(2M), with M=min(4096,ceil(sqrt(ell))) and allocated table bytes retained. The memory boundary is unchanged across prime arms.

**The small BSGS difference is retained.** Its original 99% S/R interval excluded 1, with ratio 1.027099. A deterministic post-run accounting check passed for every one of 3,852 BSGS jobs: setup calls=M+popcount(M)+bit_length(M)−1, search calls=floor(q/M). Once ell and table size are set, this count follows target scalar position. It is not evidence of a prime-shape-dependent obstacle. The diagnostic does not alter the frozen primary rho analysis.

## Population and arithmetic

The unconditional 3,456-model main audit gives S−R generic proxy difference −0.153680 bits (proxy=0.5 log2 largest prime factor of #E). Requested 99.9% interval: {requested['population_generic_proxy_difference_bits']['S_R']['CI99_9']}. This proxy is not a certified security bound, and this sample does not show larger usable subgroups.

Python arithmetic measured 2,520 batches over 126 moduli with exact output equality. Generic S/R ratios for products, inverses and point additions are 1.026673, 1.029412 and 1.065883; their intervals include 1. The Python binary-fold prototype was slower than builtin reduction (median product ratio 9.1994; point-addition ratio 1.7259). Inversion intentionally uses the identical builtin pow in both backends. These measurements describe this prototype and machine; they do not measure optimized Solinas C/assembly arithmetic or a deployed attack.

## Theory and limits

Q=qG is tested on synthetic prime-order subgroups. Generic rho's collision search takes order sqrt(ell) group operations. Sparse binary expressions help represent and reduce field integers; that alone gives no new relation for q. Equal-order cyclic groups are abstractly isomorphic, but this statement does not provide an efficient map between arbitrary coordinate curves. Opaque rho reduces access to coordinate structure in this implemented solver; it is not an adversarially enforced oracle against reflection.

The test concerns the declared finite prime catalog, toy-sized groups, uniform nonsingular short-Weierstrass coefficient models, matching rules and implemented attacks. It does not settle structure-aware attacks, industrial-size ECDLP, number-field rank, production arithmetic, or all primes called Solinas. The 56/72-bit anchors were audited and timed but not forced into toy attack groups. Four attack-eligible exact anchors are case studies and are not pooled into the main confidence intervals. No hypothesis, frontier, asymptotic algorithm claim or sealed measured bound is promoted.

## Provenance and artifacts

Implementation sources were committed before selection (fa315f9efc97fdd4c6b1e484aa720cc828a79beb); arithmetic and analysis were committed before attacks (054f1988e). See [run manifest](../manifest.json), [frozen measurement source](../measurement-source-freeze.json), [original analysis](../analysis/summary.json), [requested confidence sensitivity](requested-confidence-99_9.json), [derived accounting](post-run-diagnostics.json), [all exact curve identities](all-curve-identities.csv), [raw attack index](../attacks/job-index.json), and the retained preparation, attack and arithmetic directories. This report's source and SVGs are generated by finish_baseline.py, copied alongside. Scientific review is not independent; observations remain unpromoted. Historical reports and canonical frontier graphs are unchanged.
'''
    (out / 'report.md').write_text(md)
    typ = f'''#set page(paper: "a4", margin: 18mm, footer: context align(center)[#text(size: 8pt)[RUN-ECDLP-a24605 · #counter(page).display()]])
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false)
= Solinas prime comparison
2026-10-11 · EXP-ECDLP-5184f7 · RUN-ECDLP-a24605

#text(size: 17pt, weight: "bold")[Native rho ratio {primary['estimate']:.4f}]

Requested marginal 99.9% interval: *{lo:.4f}–{hi:.4f}*. Original prespecified 99% interval: 0.9742–1.0303. Both fall within the predeclared practical-similarity margin 0.8333–1.2000. The sampled primes show similar normalized generic rho cost.

*Measured scope:* 36 sampled prime blocks across 24/28/32-bit fields; 72 random control primes; 864 matched main groups; 96 separate anchor groups; three easy groups. All 47,292 attack jobs completed. Raw outputs, exact seeds, curves, points and counts are retained.

#image("workflow.svg", width: 100%)

The prime family is p = 2^b − 2^a + s 2^c + t, with 1 ≤ c < a ≤ b−2 and s,t = ±1. Integer duplicates are removed. Random primes match size within 1%; the second control also matches p mod 12. Curves match largest prime subgroup order within 10%, with fixed weak-curve exclusions for conditional attacks. The first 32 unconditional curves per modulus are retained separately.

The higher-confidence sensitivity was requested after trials. It uses 200,000 whole-prime-block percentile bootstrap samples within bit-size strata. Original frozen results stay unchanged. Larger prospective sampling is recorded separately. Nominal bootstrap coverage is approximate; intervals are marginal, not simultaneous.

#pagebreak()
= Attacks and controls
#image("attack-ratios.svg", width: 100%)

Rho's primary endpoint is search group calls / sqrt(ell), restricted at horizon 20. Setup and scalar verification counts are separate. BSGS includes setup and search, normalizes by M+ell/(2M), and retains memory allocation with M ≤ 4096.

All 288 sham, replay and transported-isomorphism controls passed. All recovered scalars and collision equations passed independent arithmetic checks within the runner. Main rho censoring is zero. Two tiny easy-group rho attempts hit their cap; all complete-coverage BSGS easy controls succeeded. Tiny capped attempts are not interpreted as mathematical resistance.

*BSGS difference retained:* the original 99% Solinas/random interval excluded 1 (ratio 1.027099). Every one of 3,852 BSGS jobs matches exact operation accounting: setup = M + popcount(M) + bit_length(M) − 1; search = floor(q/M). At fixed ell and M, scalar position explains this count. This is a derived diagnostic, not a changed primary endpoint.

Six explicit degree-1 isomorphic endpoints and 192 associated jobs are additionally checked on the actual transported models. The full endpoint UIDs and subgroup checks are in isomorphism-identities.json.

#pagebreak()
= What the findings mean
Generic collision attacks depend mainly on subgroup order ell. Sparse binary expressions can change the cost of field reduction. That is a separate question from how many group operations an attack needs. An abstract cyclic-group isomorphism does not supply an efficient coordinate map between arbitrary curves.

The unconditional audit gives a Solinas/random difference of −0.153680 generic-proxy bits, with requested 99.9% interval {requested['population_generic_proxy_difference_bits']['S_R']['CI99_9'][0]:.4f}–{requested['population_generic_proxy_difference_bits']['S_R']['CI99_9'][1]:.4f}. The proxy is 0.5 log2(largest prime factor of curve order). It is not a certified security bound.

The Python arithmetic panel has 2,520 observations over 126 moduli, all output-equal. Generic Solinas/random timings have ratios 1.0267 (products), 1.0294 (inversions), and 1.0659 (point additions), with intervals including 1. The Python folding prototype is slower than builtins: median product ratio 9.1994 and point-addition ratio 1.7259. The inverse code is identical in both paths. These observations describe a prototype, not optimized assembly or deployed resistance.

This run does not establish a result for production-size ECDLP, structural attacks, all Solinas primes, number-field rank, or industrial field arithmetic. The 56/72-bit anchors were audited and timed only. Four smaller anchors are descriptive case studies, excluded from main confidence intervals. No sealed bound, frontier update or scientific claim promotion is made.

= Reproduce and inspect
All raw preparation, attack and arithmetic records are adjacent to this report. See analysis/summary.json for the unchanged prespecified results and report/requested-confidence-99_9.json for every higher-confidence contrast. all-curve-identities.csv contains 1,095 exact curve identities including generators and subgroup orders. Sources froze at fa315f9ef before selection and 054f1988e before attacks. report.md links all supporting files. This is not an independently reviewed result.
'''
    (out / 'report.typ').write_text(typ)
    import shutil
    shutil.copyfile(__file__, out / 'finish_baseline.py')
    print(json.dumps({'report': str(out), 'CI99_9': primary, 'identity_rows': len(identities), 'BSGS_exact': bsgs_count}))


if __name__ == '__main__':
    main()
