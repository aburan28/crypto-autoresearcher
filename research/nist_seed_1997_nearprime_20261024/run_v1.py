#!/usr/bin/env python3
"""Classify retained positive exact orders under the dated near-prime rule."""

import datetime as dt
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PDF = Path('/private/tmp/x962-11-17-97.pdf')
TARGETS = ROOT / 'research/nist_seed_selection_20261016/targets.json'
CROSS = ROOT / 'research/nist_seed_selection_20261016/raw/full_census_crosscheck_v4.json'
ORDERS = ROOT / 'research/nist_seed_provenance_20261016/census'
PDF_SHA = '0c231d5176fcf0b239b44732213d281b518a0e16cc6f13f7bd4039ec99807b6e'
STREAMS = {'prime239v3':863711343, 'prime192v2':863966734,
           'P-521':871002724, 'P-256':871696354,
           'P-384':872952608, 'P-224':891607927}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primes_through(limit):
    return [n for n in range(2, limit+1)
            if all(n % d for d in range(2, math.isqrt(n)+1))]


PRIMES = primes_through(255)


def divide_small(order):
    h, n = 1, order
    for ell in PRIMES:
        while n % ell == 0:
            n //= ell
            h *= ell
    assert order == h*n and n > 0
    return h, n


def get_git(args):
    return subprocess.run(['git', *args], cwd=ROOT, text=True,
                          capture_output=True, check=True).stdout.strip()


def main():
    assert sha(PDF) == PDF_SHA
    cross = json.loads(CROSS.read_text())
    assert cross['status'] == 'validated'
    targets = {x['name']:x for x in json.loads(TARGETS.read_text())}
    source_hashes = {str(PDF):sha(PDF), str(CROSS.relative_to(ROOT)):sha(CROSS),
                     str(TARGETS.relative_to(ROOT)):sha(TARGETS),
                     str((HERE/'PROTOCOL.md').relative_to(ROOT)):sha(HERE/'PROTOCOL.md')}
    assert source_hashes[str(TARGETS.relative_to(ROOT))] == cross['input_sha256'][str(TARGETS.relative_to(ROOT))]
    start = dt.datetime.now(dt.timezone.utc)
    run_dir = HERE / 'runs' / ('positive-'+start.strftime('%Y%m%dT%H%M%SZ'))
    run_dir.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    rows, zeros = [], []
    for name, timestamp in STREAMS.items():
        t = targets[name]
        assert t['unix_time'] == timestamp
        p = int(t['p'])
        assert p.bit_length() == cross['streams'][name]['p_bits']
        order_file = ORDERS / f'orders_{timestamp}.txt'
        relative = str(order_file.relative_to(ROOT))
        source_hashes[relative] = sha(order_file)
        assert source_hashes[relative] == cross['input_sha256'][relative]
        indices = set()
        for line in order_file.read_text().splitlines():
            index, canonical, other = map(int, line.split())
            assert index not in indices and 1 <= index <= t['candidate_index']
            indices.add(index)
            if canonical == 0 and other == 0:
                zeros.append({'stream':name, 'index':index, 'kind':'both_zero'})
            for side, u in [('canonical',canonical), ('other',other)]:
                if u == 0:
                    continue
                assert abs(u-(p+1)) <= 2*math.isqrt(p)+1
                h, n = divide_small(u)
                rows.append({'stream':name, 'timestamp':timestamp, 'index':index,
                             'side':side, 'p':str(p), 'order':str(u),
                             'smooth_cofactor':str(h), 'residual':str(n)})
        assert len(indices) == cross['streams'][name]['seeded_coefficients']
    assert len(rows) > 82 and sum(cross['streams'][x]['seeded_coefficients'] for x in STREAMS) == 11042

    commands = ['default(parisizemax, 1000000000);']
    for i,row in enumerate(rows):
        commands.append(f'print("R {i} ", isprime({row["residual"]}));')
    for i,n in enumerate((9,21,341)):
        commands.append(f'print("C {i} ", isprime({n}));')
    commands.append('quit;')
    gp_input = '\n'.join(commands)+'\n'
    (run_dir/'gp_input.gp').write_text(gp_input)
    cmd = ['gp','-q','-f']
    try:
        completed = subprocess.run(cmd, input=gp_input, text=True,
                                   capture_output=True, timeout=120)
    except subprocess.TimeoutExpired as e:
        (run_dir/'failure.json').write_text(json.dumps({'status':'timeout','timeout_seconds':120,
                                                       'stdout':str(e.stdout),'stderr':str(e.stderr)},indent=2)+'\n')
        raise
    (run_dir/'gp_stdout.log').write_text(completed.stdout)
    (run_dir/'gp_stderr.log').write_text(completed.stderr)
    assert completed.returncode == 0
    results = {}
    controls = {}
    for line in completed.stdout.splitlines():
        kind,index,value = line.split()
        index,value = int(index),int(value)
        assert value in (0,1)
        bucket = results if kind == 'R' else controls
        assert index not in bucket
        bucket[index] = value
    assert set(results) == set(range(len(rows)))
    assert controls == {0:0,1:0,2:0}
    for i,row in enumerate(rows):
        p,u,n = int(row['p']),int(row['order']),int(row['residual'])
        prime = bool(results[i])
        base = prime and n > 2**160 and u != p and all(pow(p,k,n) != 1 for k in range(1,21))
        row['residual_isprime_gp'] = prime
        row['eligible_1997_minimum_255'] = base
        row['eligible_plus_1998_rmin'] = base and n*n > 16*p
    seed_groups = {}
    for row in rows:
        seed_groups.setdefault((row['stream'],row['index']),[]).append(row)
    cert_streams = cross['streams']
    for name in STREAMS:
        for index in cert_streams[name]['broad_family_both_seeded_roots']:
            assert any(x['eligible_1997_minimum_255'] and x['smooth_cofactor']=='1'
                       for x in seed_groups[(name,index)]), (name,index)
    summaries = {}
    for name in STREAMS:
        subset = [x for x in rows if x['stream']==name]
        summaries[name] = {
            'positive_exact_branches':len(subset),
            'positive_exact_seed_positions':len({x['index'] for x in subset}),
            'both_zero_positions':sum(x['stream']==name for x in zeros),
            'prime_full_order_positions':len(cert_streams[name]['broad_family_both_seeded_roots']),
            'nearprime_1997_positions':len({x['index'] for x in subset if x['eligible_1997_minimum_255']}),
            'nearprime_plus_1998_rmin_positions':len({x['index'] for x in subset if x['eligible_plus_1998_rmin']}),
            'nearprime_1997_branches':sum(x['eligible_1997_minimum_255'] for x in subset),
        }
    summary = {'positive_exact_branches':len(rows),
               'positive_exact_seed_positions':len(seed_groups),
               'both_zero_positions':len(zeros),
               'prime_full_order_positions':69,
               'nearprime_1997_positions':len({(x['stream'],x['index']) for x in rows if x['eligible_1997_minimum_255']}),
               'nearprime_plus_1998_rmin_positions':len({(x['stream'],x['index']) for x in rows if x['eligible_plus_1998_rmin']})}
    receipt = {'status':'completed', 'started_utc':start.isoformat(),
               'ended_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
               'elapsed_seconds':time.monotonic()-started,
               'command':[sys.executable, str(Path(__file__).resolve())],
               'gp_command':cmd, 'gp_version':subprocess.run(['gp','--version-short'],text=True,capture_output=True,check=True).stdout.strip(),
               'python':sys.version, 'platform':platform.platform(),
               'git_head':get_git(['rev-parse','HEAD']), 'git_status':get_git(['status','--porcelain']),
               'source_sha256':source_hashes, 'gp_input_sha256':sha(run_dir/'gp_input.gp'),
               'gp_stdout_sha256':sha(run_dir/'gp_stdout.log'),
               'gp_stderr_sha256':sha(run_dir/'gp_stderr.log'),
               'gp_exit_code':completed.returncode, 'wall_timeout_seconds':120,
               'gp_controls':controls}
    (run_dir/'analysis.json').write_text(json.dumps({'summary':summary,'streams':summaries,
                                                    'rows':rows,'zero_rows':zeros},indent=2,sort_keys=True)+'\n')
    (run_dir/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'run_dir':str(run_dir.relative_to(ROOT)),**summary},sort_keys=True))


if __name__ == '__main__':
    main()
