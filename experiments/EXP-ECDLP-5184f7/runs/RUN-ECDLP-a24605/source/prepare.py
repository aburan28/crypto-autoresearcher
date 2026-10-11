#!/usr/bin/env python3
"""Freeze prime catalogs, unconditional curve audits, matching and public targets."""
import argparse
import concurrent.futures
import hashlib
import json
import math
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

from common import Stream, generator, gp_file, sha, write
from curve_identity import curve_identity
from finite_math import Curve


def catalogs(out, bits):
    representations = defaultdict(list)
    for b in bits:
        for a in range(2, b - 1):
            for c in range(1, a):
                for s in [-1, 1]:
                    for t in [-1, 1]:
                        p = (1 << b) - (1 << a) + s * (1 << c) + t
                        if p.bit_length() == b:
                            representations[p].append([b, a, c, s, t])
    candidates = sorted(representations)
    path = out / 'catalog-primality.gp'
    path.write_text('v=[' + ','.join(map(str, candidates)) + '];\nfor(i=1,#v,print([v[i],isprime(v[i])]));\nquit;\n')
    stdout, timing = gp_file(path, out / 'catalog-primality')
    tests = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    assert [r[0] for r in tests] == candidates
    primes = {p: representations[p] for p, flag in tests if flag}
    write(out / 'prime-catalog.json', {'catalogs_for_bit_lengths': bits,
          'candidate_records': [{'p': p, 'representations': representations[p], 'isprime': bool(flag)} for p, flag in tests],
          'exact_primality': 'PARI isprime', 'process': timing})
    return primes


def sample_primes(out, plan):
    anchors = plan['exact_anchor_cohort']['anchors']
    all_bits = sorted({24, 28, 32} | {a['p_bits'] for a in anchors})
    sparse = catalogs(out, all_bits)
    used = {int(a['p']) for a in anchors}
    selected, blocks = [], []
    for bits in [24, 28, 32]:
        available = sorted(p for p in sparse if p.bit_length() == bits and p not in used)
        if len(available) < 12:
            raise RuntimeError(f'Insufficient fixed catalog at {bits} bits')
        for seed in plan['main_prime_sample']['seeds']:
            rng = Stream(f'prime-sample/{seed}/{bits}')
            for _ in range(4):
                p = available.pop(rng.below(len(available)))
                used.add(p)
                blocks.append({'block': len(blocks), 'cohort': 'main', 'bits': bits, 'seed': seed,
                               'pS': p, 'representations': sparse[p]})
    for anchor in anchors:
        blocks.append({'block': len(blocks), 'cohort': 'anchor', 'bits': anchor['p_bits'],
                       'pS': int(anchor['p']), 'anchor': anchor})
    # One persistent exact-primality GP process; each input/output also retained.
    from common import GP, gp_environment, limits
    import subprocess
    process = subprocess.Popen([str(GP), '-q', '-f', '-s', '128M'], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=(out / 'control-primality.stderr').open('w'),
                               text=True, env=gp_environment(), preexec_fn=limits)
    rejections = []
    try:
        for block in blocks:
            p = block['pS']
            for arm in ['S', 'R', 'C']:
                if arm == 'S':
                    q = p
                else:
                    rng = Stream(f'control-prime/{block["block"]}/{arm}/20261011')
                    lo = max((99 * p + 99) // 100, 1 << (block['bits'] - 1))
                    hi = min(101 * p // 100, (1 << block['bits']) - 1)
                    lo += lo % 2 == 0
                    for draw in range(20000):
                        q = lo + 2 * rng.below((hi - lo) // 2 + 1)
                        why = 'used' if q in used else 'sparse_catalog' if q in sparse else 'residue' if arm == 'C' and q % 12 != p % 12 else None
                        prime = None
                        if why is None:
                            process.stdin.write(f'print(isprime({q}));\n')
                            process.stdin.flush()
                            prime = int(process.stdout.readline().strip())
                            why = None if prime else 'composite'
                        rejections.append({'block': block['block'], 'arm': arm, 'draw': draw,
                                           'p': q, 'isprime': prime, 'rejection': why})
                        if why is None:
                            used.add(q)
                            break
                    else:
                        raise RuntimeError('Control-prime candidate limit reached')
                selected.append({'id': f'm{len(selected):03d}', 'block': block['block'], 'arm': arm,
                                 'p': q, 'bits': block['bits'], 'cohort': block['cohort'],
                                 'attack_eligible': block['bits'] <= 40})
    finally:
        process.stdin.write('quit;\n')
        process.stdin.flush()
        process.wait(timeout=10)
    write(out / 'control-prime-draws.json', rejections)
    write(out / 'prime-sample.json', {'blocks': blocks, 'moduli': selected,
                                     'source_plan_sha256': sha(out / 'plan.json')})
    return blocks, selected


def prepare_modulus(out, modulus):
    stage = out / 'curves' / modulus['id']
    stage.mkdir(parents=True, exist_ok=False)
    p = modulus['p']
    rng = Stream(f'curve-pool/{modulus["block"]}/20261011')
    desired = 512 if modulus['attack_eligible'] else 32
    rows, draws = [], []
    while len(rows) < desired:
        A, B = rng.below(p), rng.below(p)
        singular = (4 * pow(A, 3, p) + 27 * B * B) % p == 0
        draws.append({'draw': len(draws), 'A': A, 'B': B, 'singular': singular})
        if not singular:
            rows.append({'index': len(rows), 'modulus_id': modulus['id'], 'p': p, 'A': A, 'B': B})
    write(stage / 'coefficient-draws.json', draws)
    source = stage / 'point-counts.gp'
    source.write_text(f'p={p};setrand({int(sha(stage / "coefficient-draws.json")[:12],16)});\n'
        + 'v=[' + ','.join(f'[{r["A"]},{r["B"]}]' for r in rows) + '];\n'
        + 'for(i=1,#v,E=ellinit([v[i][1],v[i][2]],p);N=ellcard(E);F=factor(N);T=factor(2*p+2-N);'
          'for(j=1,matsize(F)[1],if(!isprime(F[j,1]),error("uncertified factor")));'
          'for(j=1,matsize(T)[1],if(!isprime(T[j,1]),error("uncertified twist factor")));'
          'print([i-1,N,lift(E.j),Vec(F[,1]),Vec(F[,2]),Vec(T[,1]),Vec(T[,2])]));\nquit;\n')
    stdout, process = gp_file(source, stage / 'point-counts')
    measured = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    assert len(measured) == desired
    for row, result in zip(rows, measured, strict=True):
        idx, N, j, primes, exponents, twist_primes, twist_exponents = result
        assert idx == row['index']
        factors = list(zip(primes, exponents))
        assert math.prod(q ** e for q, e in factors) == N
        twist = 2 * p + 2 - N
        assert math.prod(q ** e for q, e in zip(twist_primes, twist_exponents)) == twist
        ell, multiplicity = primes[-1], exponents[-1]
        trace = p + 1 - N
        embedding = next((k for k in range(1, 21) if pow(p, k, ell) == 1), None)
        flags = {'anomalous': N == p, 'supersingular': trace % p == 0,
                 'j_special': j in [0, 1728 % p], 'embedding_degree_le20': embedding}
        row.update(N=N, j=j, factors=factors, ell=ell, ell_multiplicity=multiplicity,
                   h=N // ell, trace=trace, frobenius_discriminant=trace * trace - 4 * p,
                   twist_order=twist, twist_factors=list(zip(twist_primes, twist_exponents)), flags=flags,
                   attack_candidate=not any([flags['anomalous'], flags['supersingular'], flags['j_special'],
                                             embedding is not None, multiplicity != 1, not 16 <= ell.bit_length() <= 26]))
    write(stage / 'curves.json', {'modulus': modulus, 'curves': rows, 'process': process,
                                 'unchecked_features': ['general endomorphism ring and all structural attacks']})
    print('CURVES', modulus['id'], modulus['bits'], desired,
          sum(r['attack_candidate'] for r in rows), round(process['elapsed_seconds'], 2), flush=True)
    return modulus['id'], rows


def matching(left, right):
    if not left or not right:
        return {}, []
    # Dummies cost 100; each forbidden edge costs 1e6. Thus cardinality
    # precedes aggregate log-order distance (<512*log(1.1)); sorted candidate
    # rows/columns and the fixed assignment implementation resolve ties.
    costs = np.full((len(left), len(right) + len(left)), 100.0)
    edges = []
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            distance = abs(math.log(x['ell'] / y['ell']))
            allowed = max(x['ell'], y['ell']) * 10 <= min(x['ell'], y['ell']) * 11
            costs[i, j] = distance if allowed else 1e6
            if allowed:
                edges.append([x['index'], y['index'], distance])
    ixs, jxs = linear_sum_assignment(costs)
    pairs = {left[i]['index']: right[j]['index'] for i, j in zip(ixs, jxs)
             if j < len(right) and costs[i, j] < 100}
    return pairs, edges


def make_group(row, modulus, slot, ell=None, kind='matched'):
    ell = ell or row['ell']
    G, draws = generator(row, ell)
    field = {'characteristic': row['p'], 'degree': 1, 'representation': 'prime field, canonical integer residues',
             'element_encoding': 'integers 0..p-1', 'modulus': row['p']}
    curve = {'model': 'short-Weierstrass', 'a4': row['A'], 'a6': row['B'], 'subgroup_order': ell,
             'cofactor': row['N'] // ell, 'generator': G, 'target_group': 'prime-order cyclic subgroup of E(F_p)'}
    return {'group_id': f'g{modulus["block"]:02d}{modulus["arm"]}{slot:02d}{kind}',
            'block': modulus['block'], 'arm': modulus['arm'], 'cohort': modulus['cohort'],
            'bits': modulus['bits'], 'slot': slot, 'modulus_id': modulus['id'], 'candidate_index': row['index'],
            'p': row['p'], 'A': row['A'], 'B': row['B'], 'ell': ell, 'h': row['N'] // ell,
            'N': row['N'], 'G': G, 'generator_draws': draws, 'field': field, 'curve': curve,
            'identity': curve_identity(field, curve, 'primecomparison'), 'kind': kind}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--boundary', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(args.plan, out / 'plan.json')
    shutil.copyfile(args.boundary, out / 'measurement-boundary.json')
    plan = json.loads(args.plan.read_text())
    started = time.monotonic()
    blocks, moduli = sample_primes(out, plan)
    print('FROZEN_PRIMES', len(moduli), flush=True)
    curves = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(prepare_modulus, out, m) for m in moduli]
        for future in concurrent.futures.as_completed(futures):
            key, rows = future.result()
            curves[key] = rows
    groups, match_logs = [], []
    for block in blocks:
        ms = {m['arm']: m for m in moduli if m['block'] == block['block']}
        if not ms['S']['attack_eligible']:
            continue
        eligible = {arm: [r for r in curves[m['id']] if r['attack_candidate']] for arm, m in ms.items()}
        sr, er = matching(eligible['S'], eligible['R'])
        sc, ec = matching(eligible['S'], eligible['C'])
        selected = sorted(set(sr) & set(sc))[:8]
        match_logs.append({'block': block['block'], 'S_R_matches': sr, 'S_C_matches': sc,
                           'S_R_edges': er, 'S_C_edges': ec, 'selected_S_indices': selected,
                           'candidate_counts': {k: len(v) for k, v in eligible.items()}})
        for slot, idx in enumerate(selected):
            for arm, candidate in [('S', idx), ('R', sr[idx]), ('C', sc[idx])]:
                groups.append(make_group(curves[ms[arm]['id']][candidate], ms[arm], slot))
    write(out / 'matching.json', match_logs)
    for bits in [24, 28, 32]:
        done = False
        for m in moduli:
            if done or m['cohort'] != 'main' or m['bits'] != bits or m['arm'] != 'S':
                continue
            for row in curves[m['id']]:
                small = next((q for q, e in row['factors'] if q in [5, 7, 11, 13] and e == 1), None)
                if small:
                    groups.append(make_group(row, m, 0, small, 'easy'))
                    done = True
                    break
    targets, truth = [], []
    for group in groups:
        curve = Curve(group['p'], group['A'], group['B'])
        rng = Stream(f'targets/{group["group_id"]}/20261011')
        for index in range(4):
            q = 1 + rng.below(group['ell'] - 1)
            Q = list(curve.mul(tuple(group['G']), q))
            target = {'id': f'{group["group_id"]}t{index}', 'group_id': group['group_id'],
                      'target_index': index, 'Q': Q, 'curve_uid': group['identity']['curve_uid']}
            targets.append(target)
            truth.append({'id': target['id'], 'synthetic_scalar': q})
    write(out / 'public-groups.json', groups)
    write(out / 'public-targets.json', targets)
    write(out / 'validation-only/synthetic-truth.json', truth)
    write(out / 'preparation-result.json', {'blocks': len(blocks), 'moduli': len(moduli),
          'nonsingular_models': sum(len(v) for v in curves.values()), 'matched_groups': sum(g['kind'] == 'matched' for g in groups),
          'easy_groups': sum(g['kind'] == 'easy' for g in groups), 'elapsed_seconds': time.monotonic() - started,
          'sample_and_matching_frozen_before_attacks': True, 'source_hashes': {p.name: sha(p) for p in Path(__file__).parent.glob('*.py')}})
    print('PREPARATION_COMPLETE', len(groups), len(targets), flush=True)


if __name__ == '__main__':
    main()
