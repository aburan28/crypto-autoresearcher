#!/usr/bin/env python3
"""Run the frozen public jobs. Validation-only scalars never enter kernel jobs."""
import argparse
import hashlib
import json
import math
import os
import platform
import random
import resource
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path

from common import Stream, limits, sha, write
from finite_math import Curve


def stable(record):
    return {k: v for k, v in record.items() if k not in
            ['job_id', 'mode', 'cpu_seconds', 'wall_seconds', 'process_max_RSS_KiB']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prep', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--kernel', type=Path, required=True)
    args = parser.parse_args()
    out, prep = args.out.resolve(), args.prep.resolve()
    out.mkdir(parents=True, exist_ok=False)
    groups = json.loads((prep / 'public-groups.json').read_text())
    targets = json.loads((prep / 'public-targets.json').read_text())
    # This table is used only after the kernel returns, in external validation.
    truth = {r['id']: r['synthetic_scalar'] for r in json.loads((prep / 'validation-only/synthetic-truth.json').read_text())}
    by_group = defaultdict(list)
    for t in targets:
        by_group[t['group_id']].append(t)
    group_map = {g['group_id']: g for g in groups}
    primary_for_controls = set()
    for bits in [24, 28, 32]:
        chosen = sorted([g for g in groups if g['bits'] == bits and g['cohort'] == 'main'
                         and g['arm'] == 'S' and g['kind'] == 'matched'], key=lambda g: (g['block'], g['slot']))[:2]
        primary_for_controls.update(g['group_id'] for g in chosen)
    jobs = []
    for g in groups:
        for t in by_group[g['group_id']]:
            modes = [('rho', 16, [1, 2, 3, 4]), ('bsgs', 0, [0])]
            if g['cohort'] == 'main' and g['kind'] == 'matched':
                modes += [('oracle', 16, [1, 2, 3, 4]), ('rho32', 32, [101, 102, 103, 104])]
            if g['group_id'] in primary_for_controls:
                modes += [('sham', 16, [1, 2, 3, 4]), ('replay', 16, [1, 2, 3, 4]),
                          ('transport', 16, [1, 2, 3, 4]), ('native_iso', 16, [1, 2, 3, 4])]
            for mode, adding, seeds in modes:
                for seed in seeds:
                    jobs.append({'job_id': 'j' + hashlib.sha256(f'{t["id"]}/{mode}/{seed}'.encode()).hexdigest()[:24],
                                 'group_id': g['group_id'], 'target_id': t['id'], 'mode': mode,
                                 'adding': adding, 'seed': seed})
    random.Random(2026101108).shuffle(jobs)
    write(out / 'job-index.json', jobs)
    by_block = defaultdict(list)
    for j in jobs:
        by_block[group_map[j['group_id']]['block']].append(j)
    # A single CPU-affine worker after every preparation worker has exited.
    cpus = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {cpus[0]})
    command_env = {'python': platform.python_version(), 'platform': platform.platform(),
                   'allowed_CPUs_before_pinning': cpus, 'timing_CPU': cpus[0],
                   'kernel_sha256': sha(args.kernel), 'preparation_sha256': sha(prep / 'preparation-result.json'),
                   'clock_semantics': 'Kernel phase wall and process CPU; verification phase excluded from primary search',
                   'watchdog_seconds_per_block': 600, 'memory_limit_bytes': 4 << 30,
                   'opaque_interface': 'Value coordinates private; solver receives only Group operations/encoding, G,Q,ell,seeds',
                   'sham_labels': 'Job labels only; the kernel has no family-tag input or family branch'}
    cpuinfo = Path('/proc/cpuinfo').read_text()
    command_env['CPU_model'] = next((line.split(':', 1)[1].strip() for line in cpuinfo.splitlines() if line.startswith('model name')), None)
    write(out / 'environment.json', command_env)
    blocks = list(by_block)
    random.Random(2026101109).shuffle(blocks)
    completed, failures, validation = [], [], []
    all_records = {}
    started = time.monotonic()
    for block in blocks:
        stage = out / f'block-{block:02d}'
        stage.mkdir()
        public = stage / 'public-jobs.txt'
        with public.open('x') as handle:
            for j in by_block[block]:
                g = group_map[j['group_id']]
                t = next(t for t in by_group[g['group_id']] if t['id'] == j['target_id'])
                A, B, G, Q, u = g['A'], g['B'], g['G'], t['Q'], 1
                if j['mode'] in ['transport', 'native_iso']:
                    rng = Stream(f'isomorphism/{g["group_id"]}/20261011')
                    u = 1 + rng.below(g['p'] - 1)
                    A, B = A * pow(u, 4, g['p']) % g['p'], B * pow(u, 6, g['p']) % g['p']
                    G = [G[0] * pow(u, 2, g['p']) % g['p'], G[1] * pow(u, 3, g['p']) % g['p']]
                    Q = [Q[0] * pow(u, 2, g['p']) % g['p'], Q[1] * pow(u, 3, g['p']) % g['p']]
                handle.write(' '.join(map(str, [j['job_id'], j['mode'], j['adding'], j['seed'],
                             g['p'], A, B, g['ell'], g['h'], *G, *Q, u])) + '\n')
        stdout, stderr = stage / 'raw-results.jsonl', stage / 'kernel.stderr'
        tick = time.monotonic()
        with stdout.open('x') as so, stderr.open('x') as se:
            try:
                result = subprocess.run([str(args.kernel.resolve()), str(public)], stdout=so, stderr=se,
                                        timeout=600, preexec_fn=limits)
                exit_code = result.returncode
            except subprocess.TimeoutExpired:
                exit_code = 'watchdog'
        records = [json.loads(line) for line in stdout.read_text().splitlines() if line.strip()]
        indexed = {j['job_id']: j for j in by_block[block]}
        scalar_checks = 0
        for r in records:
            assert r['job_id'] in indexed and r['job_id'] not in all_records
            j = indexed[r['job_id']]
            g = group_map[j['group_id']]
            t = next(t for t in by_group[g['group_id']] if t['id'] == j['target_id'])
            assert r['ell'] == g['ell']
            if r['scalar'] is not None:
                curve = Curve(g['p'], g['A'], g['B'])
                assert r['verified'] and curve.mul(tuple(g['G']), r['scalar']) == tuple(t['Q'])
                assert r['scalar'] == truth[t['id']]
                scalar_checks += 1
            elif j['mode'] == 'bsgs':
                raise RuntimeError('BSGS failed despite complete coverage boundary')
            for c in r['collisions']:
                assert c['denominator'] == (c['bprime'] - c['b']) % g['ell']
                curve = Curve(g['p'], g['A'], g['B'])
                left = curve.add(curve.mul(tuple(g['G']), c['a']), curve.mul(tuple(t['Q']), c['b']))
                right = curve.add(curve.mul(tuple(g['G']), c['aprime']), curve.mul(tuple(t['Q']), c['bprime']))
                assert left == right
                if c['scalar'] is not None:
                    assert c['scalar'] == (c['a'] - c['aprime']) * pow(c['denominator'], -1, g['ell']) % g['ell']
            all_records[r['job_id']] = r
        missing = sorted(set(indexed) - {r['job_id'] for r in records})
        check = {'block': block, 'expected_jobs': len(indexed), 'completed_jobs': len(records),
                 'independently_verified_scalars': scalar_checks, 'exit_code': exit_code,
                 'elapsed_seconds': time.monotonic() - tick, 'missing_job_ids': missing,
                 'public_jobs_sha256': sha(public), 'raw_sha256': sha(stdout)}
        write(stage / 'checks.json', check)
        if missing or exit_code != 0:
            failures.append(check)
        else:
            completed.append(block)
        print('ATTACK_BLOCK', block, len(records), '/', len(indexed), round(check['elapsed_seconds'], 2), flush=True)
    lookup = {(j['target_id'], j['mode'], j['seed']): j['job_id'] for j in jobs}
    for j in jobs:
        if j['mode'] not in ['sham', 'replay', 'transport'] or j['job_id'] not in all_records:
            continue
        key = (j['target_id'], 'rho', j['seed'])
        if lookup[key] not in all_records:
            continue
        primary, other = all_records[lookup[key]], all_records[j['job_id']]
        if j['mode'] == 'transport':
            passed = all(primary[k] == other[k] for k in ['scalar', 'censored', 'trace_sha256', 'iterations', 'restarts', 'collisions'])
            passed &= all(primary['counts'][phase]['group_calls'] == other['counts'][phase]['group_calls'] for phase in ['setup', 'search', 'verification'])
        else:
            passed = stable(primary) == stable(other)
        validation.append({'job_id': j['job_id'], 'control': j['mode'], 'pass': bool(passed)})
    write(out / 'control-checks.json', validation)
    write(out / 'attack-result.json', {'expected_jobs': len(jobs), 'completed_jobs': len(all_records),
          'completed_blocks': completed, 'failures': failures, 'mode_counts': dict(Counter(j['mode'] for j in jobs)),
          'all_recovered_scalars_independently_correct': True, 'all_collision_equations_checked': True,
          'sham_replay_transport_pass': all(v['pass'] for v in validation),
          'elapsed_seconds': time.monotonic() - started})
    print('ATTACKS_COMPLETE', len(all_records), 'control_failures', sum(not v['pass'] for v in validation), flush=True)


if __name__ == '__main__':
    main()
