#!/usr/bin/env python3
"""Implementation checks on declared small synthetic controls, not study samples."""
import argparse
import json
import subprocess
from pathlib import Path

from common import generator, gp_file, sha, write
from finite_math import Curve
from run_attacks import stable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--kernel', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    gp = out / 'control-orders.gp'
    gp.write_text('for(i=1,2,p=if(i==1,1000003,1000033);if(!isprime(p),error("control not prime"));'
                  'N=ellcard(ellinit([2,3],p));print([p,N,Vec(factor(N)[,1])]));\nquit;\n')
    raw, timing = gp_file(gp, out / 'control-orders')
    groups = []
    for i, line in enumerate(raw.splitlines()):
        p, N, factors = json.loads(line)
        row = {'p': p, 'A': 2, 'B': 3, 'N': N, 'ell': max(factors), 'modulus_id': f'control-{i}', 'index': 0}
        G, _ = generator(row)
        row['G'] = G
        groups.append(row)
    # Exact public historical group exercises five-byte coordinates as well.
    groups.append({'p': 68719472639, 'A': 68719472636, 'B': 3, 'N': 68719579720,
                   'ell': 5385547, 'G': [39306801954, 30775010499]})
    expected, jobs, public = {}, {}, out / 'public-jobs.txt'
    with public.open('x') as handle:
        for i, g in enumerate(groups):
            curve = Curve(g['p'], g['A'], g['B'])
            for ti, q in enumerate([1, 2, 17, g['ell'] - 2]):
                Q = curve.mul(tuple(g['G']), q)
                for mode in ['rho', 'sham', 'replay', 'transport', 'native_iso', 'oracle', 'rho32', 'bsgs']:
                    A, B, G, target, u = g['A'], g['B'], g['G'], Q, 1
                    if mode in ['transport', 'native_iso']:
                        u = 7
                        A, B = A * pow(u, 4, g['p']) % g['p'], B * pow(u, 6, g['p']) % g['p']
                        G = [G[0] * u * u % g['p'], G[1] * u ** 3 % g['p']]
                        target = [Q[0] * u * u % g['p'], Q[1] * u ** 3 % g['p']]
                    idx = f'control{i}t{ti}{mode}'
                    adding, seed = (32, 101) if mode == 'rho32' else (0, 0) if mode == 'bsgs' else (16, 1)
                    handle.write(' '.join(map(str, [idx, mode, adding, seed, g['p'], A, B, g['ell'],
                                                   g['N'] // g['ell'], *G, *target, u])) + '\n')
                    expected[idx], jobs[idx] = q, (i, ti, mode)
    result = subprocess.run([str(args.kernel.resolve()), str(public)], capture_output=True, text=True, timeout=600)
    (out / 'kernel.stdout').write_text(result.stdout)
    (out / 'kernel.stderr').write_text(result.stderr)
    assert result.returncode == 0, result.stderr
    rows = {r['job_id']: r for r in map(json.loads, result.stdout.splitlines())}
    assert len(rows) == len(expected)
    checked = 0
    for idx, row in rows.items():
        assert row['scalar'] is None or row['scalar'] == expected[idx], (idx, row)
        if row['mode'] == 'bsgs':
            assert row['scalar'] == expected[idx]
        i, ti, mode = jobs[idx]
        primary = rows[f'control{i}t{ti}rho']
        if mode in ['sham', 'replay']:
            assert stable(row) == stable(primary)
            checked += 1
        if mode == 'transport':
            assert row['trace_sha256'] == primary['trace_sha256']
            assert row['scalar'] == primary['scalar'] and row['collisions'] == primary['collisions']
            assert row['counts']['search']['group_calls'] == primary['counts']['search']['group_calls']
            checked += 1
    write(out / 'checks.json', {'scope': 'Implementation controls only, excluded from study statistics',
          'public_groups': groups, 'jobs': len(rows), 'correctness': 'Every returned scalar checked; all BSGS targets covered',
          'exact_replay_sham_transport_checks': checked, 'kernel_sha256': sha(args.kernel), 'GP_process': timing,
          'censored_rho_controls': sum(r['scalar'] is None for r in rows.values())})
    print('INSTRUMENT_PASS', len(rows), checked, flush=True)


if __name__ == '__main__':
    main()
