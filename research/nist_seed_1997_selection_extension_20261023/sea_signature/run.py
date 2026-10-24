#!/usr/bin/env python3
"""Exact, bounded Frobenius-discriminant signature comparison."""
import hashlib
import json
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OMITTED = ROOT / 'research/nist_seed_skipped_curves_20261016/assessed.json'
PUBLISHED = ROOT / 'research/nist_seed_skipped_curves_20261016/traits.json'
NAMES = ('prime192v1', 'prime192v2', 'prime192v3', 'prime239v1', 'prime239v2',
         'prime239v3', 'secp224r1', 'prime256v1')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primes_to(bound):
    out = []
    for n in range(3, bound + 1, 2):
        if all(n % p for p in out if p * p <= n):
            out.append(n)
    return out


def symbol(d, ell):
    v = pow(d % ell, (ell - 1) // 2, ell)
    if v == 0:
        return '0'
    if v == 1:
        return '+'
    assert v == ell - 1
    return '-'


def controls():
    assert symbol(1, 11) == '+'
    assert symbol(2, 11) == '-'
    assert symbol(0, 11) == '0'
    assert 4 * 4 == 16 * 1
    assert not (4 * 4 > 16 * 1)
    assert 5 * 5 > 16 * 1
    return 5


def metric_pairs(rows, key, smaller_better):
    pairs = []
    fields = sorted({r['field_bits'] for r in rows})
    for bits in fields:
        omitted = [r for r in rows if r['field_bits'] == bits and r['label'] == 'omitted']
        published = [r for r in rows if r['field_bits'] == bits and r['label'] == 'published']
        for o in omitted:
            for p in published:
                a, b = o[key], p[key]
                pub_better = (b < a) if smaller_better else (b > a)
                pairs.append({'field_bits': bits, 'omitted': o['name'], 'published': p['name'],
                              'omitted_value': a, 'published_value': b,
                              'published_better': pub_better, 'tie': a == b})
    assert len(pairs) == 25
    return {'published_better': sum(x['published_better'] for x in pairs),
            'omitted_better': sum(not x['published_better'] and not x['tie'] for x in pairs),
            'ties': sum(x['tie'] for x in pairs), 'pairs': pairs}


def main():
    assert len(sys.argv) == 2, 'usage: run.py OUTPUT_DIRECTORY'
    signal.alarm(60)
    out = Path(sys.argv[1])
    assert not out.exists(), 'output must be write-once'
    start = time.monotonic()
    cpu_start = time.process_time()
    omitted_data = json.loads(OMITTED.read_text())['candidate_rows']
    published_data = json.loads(PUBLISHED.read_text())['published_controls']
    assert len(omitted_data) == 11 and all(name in published_data for name in NAMES)
    cases = []
    for r in omitted_data:
        cases.append(('omitted', f"omitted_{int(r['p_hex'], 16).bit_length()}_{r['seed_ordinal_one_based']}", r))
    cases += [('published', name, published_data[name]) for name in NAMES]
    assert len(cases) == 19
    primes = primes_to(997)
    assert len(primes) == 167 and primes[-1] == 997
    checks = controls()
    rows = []
    seen = set()
    for label, name, r in cases:
        p, n = int(r['p_hex'], 16), int(r['n_hex'], 16)
        uid = r['identity']['curve_uid']
        assert uid not in seen
        seen.add(uid)
        assert r['identity']['field']['characteristic'] == p
        assert r['identity']['curve']['subgroup_order'] == n
        t = p + 1 - n
        delta = t * t - 4 * p
        assert t * t <= 4 * p and delta < 0
        assert t == int(r['trace_hex_signed'], 16)
        assert delta == int(r['delta_pi_hex_signed'], 16)
        m = 1
        cutoff = None
        observed = {'+': 0, '-': 0, '0': 0}
        signs = []
        at_cutoff = None
        for idx, ell in enumerate(primes):
            assert ell != p
            s = symbol(delta, ell)
            signs.append(s)
            observed[s] += 1
            if s == '+':
                m *= ell
            if cutoff is None and m * m > 16 * p:
                cutoff = ell
                at_cutoff = {'primes_scanned': idx + 1, 'elkies': observed['+'],
                             'atkin': observed['-'], 'ramified': observed['0'], 'product': str(m)}
        assert cutoff is not None, name
        row = {'label': label, 'name': name, 'curve_uid': uid, 'field_bits': p.bit_length(),
               'p_hex': hex(p), 'n_hex': hex(n), 'trace_hex_signed': hex(t),
               'delta_hex_signed': hex(delta), 'signature': ''.join(signs),
               'cutoff_ell': cutoff, 'at_cutoff': at_cutoff,
               'elkies_through_101': sum(s == '+' for ell, s in zip(primes, signs) if ell <= 101),
               'elkies_through_251': sum(s == '+' for ell, s in zip(primes, signs) if ell <= 251)}
        rows.append(row)
    assert sorted({r['field_bits'] for r in rows}) == [192, 224, 239, 256]
    comparisons = {key: metric_pairs(rows, key, smaller) for key, smaller in
                   [('cutoff_ell', True), ('elkies_through_101', False), ('elkies_through_251', False)]}
    max_published = max(r['cutoff_ell'] for r in rows if r['label'] == 'published')
    min_omitted = min(r['cutoff_ell'] for r in rows if r['label'] == 'omitted')
    summary = {'global_threshold_separates': min_omitted > max_published,
               'min_omitted_cutoff': min_omitted, 'max_published_cutoff': max_published,
               'per_field': {str(bits): {'min_omitted_cutoff': min(r['cutoff_ell'] for r in rows if r['label']=='omitted' and r['field_bits']==bits),
                                        'max_published_cutoff': max(r['cutoff_ell'] for r in rows if r['label']=='published' and r['field_bits']==bits)}
                             for bits in [192, 224, 239, 256]}}
    result = {'protocol_sha256': sha(HERE / 'PROTOCOL.md'), 'amendment_sha256': sha(HERE / 'AMENDMENT.md'),
              'sources': {str(OMITTED.relative_to(ROOT)): sha(OMITTED), str(PUBLISHED.relative_to(ROOT)): sha(PUBLISHED)},
              'prime_bound': 997, 'odd_primes': primes, 'synthetic_controls_passed': checks,
              'rows': rows, 'comparisons': comparisons, 'summary': summary}
    out.mkdir(parents=True)
    output = out / 'raw.json'
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    git_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
    receipt = {'command': ' '.join(sys.argv), 'git_head': git_head, 'dirty': dirty,
               'python': platform.python_version(), 'platform': platform.platform(),
               'wall_seconds': time.monotonic() - start, 'cpu_seconds': time.process_time() - cpu_start,
               'raw_sha256': sha(output), 'rows': len(rows), 'synthetic_controls_passed': checks}
    (out / 'receipt.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'summary': summary, 'pair_counts': {k: {s: v[s] for s in ('published_better','omitted_better','ties')} for k,v in comparisons.items()},
                      'raw_sha256': receipt['raw_sha256']}, sort_keys=True))


if __name__ == '__main__':
    main()
