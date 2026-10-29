#!/usr/bin/env python3
"""Separate high-memory continuation with rechecked immutable seed reuse."""
import argparse
import fcntl
import json
import os
import shutil
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'semaev-m2-last-fall-degree/submission-20261029'))
from certificate_campaign import command, digest, memory_admission, save


def attempt(item, args, plan_hash, lock):
    root = args.out/item['id']
    root.mkdir(exist_ok=True)
    previous = sorted(root.glob('attempt-*/result.json'))
    if previous:
        old = json.loads(previous[-1].read_text())
        if old['plan_sha256'] != plan_hash:
            raise ValueError('Existing output belongs to another plan')
        for name, entry in old['artifacts'].items():
            if digest(previous[-1].parent/name) != entry['sha256']:
                raise ValueError('Retained artifact changed: '+name)
        return old
    out = root/('attempt-%03d' % (len(list(root.glob('attempt-*')))+1))
    out.mkdir()
    r = dict(schema='semaev.cascade-result/v1', id=item['id'], parameters=item,
        source_commit=args.source_commit, plan_sha256=plan_hash, status='started',
        stages=[], steps={}, last_fall_degree_lower_bound=None)
    save(out/'started.json', r)
    record = item['record']
    def call(label, argv, memory=args.memory):
        step = command(argv, out, label, args.timeout, memory, lock)
        r['steps'][label] = step
        if step['returncode']:
            raise RuntimeError(label+' failed; retained logs are authoritative')
        return (out/(label+'.stdout.txt')).read_text()
    try:
        counted = call('count', [args.runtime/'bin/count_by_sum', record['n'],
            record['modulus_hex'], record['z_hex'], record['a6_hex'], record['k'],
            *record['V_basis_hex']], 2**30).strip()
        if not counted.isdigit():
            raise ValueError('Counter did not return a nonnegative integer')
        r['exact_solutions'] = int(counted)
        save(out/'instance.json', [dict(record, name=item['id'])])
        system = out/'input.sys'
        call('descent', [sys.executable, args.dossier/'code/mksys.py',
            out/'instance.json', item['id'], system])
        admission = memory_admission(system, 3, args.chunk, args.memory)
        r['seed_admission'] = admission
        if not admission['admitted']:
            r['status'] = 'resource_capped'
        else:
            seed_info=item.get('seed')
            first_degree=seed_info['degree'] if seed_info else 3
            if seed_info:
                source=Path(seed_info['path'])
                if digest(source)!=seed_info['sha256'] or digest(Path(seed_info['origin']))!=seed_info['origin_sha256']:
                    raise ValueError('Retained seed or origin changed')
                if digest(system)!=seed_info['system_sha256']:
                    raise ValueError('Retained seed belongs to a different descended system')
                save(out/'seed-origin.json',seed_info)
            for degree in range(first_degree,6):
                cert = out/f'degree{degree}.bin'
                if seed_info and degree==first_degree:
                    try:os.link(source,cert)
                    except OSError:shutil.copyfile(source,cert)
                    r['seed_reused']=dict(degree=degree,sha256=digest(cert),origin=seed_info['origin'])
                elif degree == 3:
                    call('produce3', [sys.executable, args.dossier/'submission-20261029/certificate_campaign.py',
                        'producer', '--binary', args.runtime/'bin/lfdclose2', '--system', system,
                        '--degree', 3, '--chunk', args.chunk, '--certificate', cert])
                    if not cert.exists():
                        r['status'] = 'seed_without_certificate'
                        break
                else:
                    label = f'produce{degree}'
                    step = command([args.runtime/'bin/quotient_lift_batched', out/f'degree{degree-1}.bin',
                        cert, args.chunk, args.memory], out, label, args.timeout, args.memory, lock)
                    r['steps'][label] = step
                    if step['returncode']:
                        stderr = (out/(label+'.stderr.txt')).read_text()
                        r['status'] = 'resource_capped' if 'allocation gate refused' in stderr else 'failed'
                        r['stopped_degree'] = degree
                        break
                    observation = json.loads((out/(label+'.stdout.txt')).read_text())
                    if observation['status'] == 'projection_kills_one':
                        r['status'] = 'projection_kills_one'
                        r['stopped_degree'] = degree
                        break
                    if observation['status'] != 'candidate_certificate':
                        raise ValueError('Unrecognized producer observation')
                output = call(f'check{degree}', [sys.executable, args.dossier/'verify/cert_check.py', cert,
                    record['n'], record['modulus_hex'], record['a2'], record['a6_hex'],
                    record['z_hex'], *record['V_basis_hex']])
                accepted = re.search(r'VALID: 1 is not in W_'+str(degree)+r'\(F\), and codim W_'+str(degree)+r'\(F\) >= (\d+)', output)
                if not accepted:
                    raise ValueError('Original checker did not confirm degree and codimension')
                bound = int(accepted[1])
                r['stages'].append(dict(degree=degree, certified_codimension=bound,
                    certificate_sha256=digest(cert), exact_solutions=r['exact_solutions']))
                if bound > r['exact_solutions']:
                    r['last_fall_degree_lower_bound'] = degree+1
                r['status'] = 'certificate_verified'
    except Exception as error:
        r['status'] = 'failed'
        r['error'] = str(error)
    r['artifacts'] = {p.name:dict(sha256=digest(p), bytes=p.stat().st_size)
        for p in out.iterdir() if p.is_file()}
    save(out/'result.json', r)
    print(json.dumps({k:r[k] for k in ('id','status','last_fall_degree_lower_bound')}), flush=True)
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('plan','runtime','dossier','out'):
        ap.add_argument('--'+name, type=Path, required=True)
    ap.add_argument('--source-commit', required=True)
    ap.add_argument('--memory', type=int, default=64*2**30)
    ap.add_argument('--chunk', type=int, default=60000)
    ap.add_argument('--timeout', type=int, default=21600)
    args = ap.parse_args()
    if not 0 < args.memory <= 64*2**30 or not 1 <= args.chunk <= 60000:
        ap.error('One worker, at most64 GiB and60000-row chunks')
    plan = json.loads(args.plan.read_text())
    for name, sha in plan['binary_sha256'].items():
        if digest(args.runtime/'bin'/name) != sha:
            raise ValueError('Binary hash mismatch: '+name)
    for name, sha in plan['source_sha256'].items():
        if digest(HERE/name) != sha:
            raise ValueError('Source hash mismatch: '+name)
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out/'owner.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        rows = [attempt(item,args,digest(args.plan),lock.fileno()) for item in plan['items']]
    return int(any(r['status']=='failed' for r in rows))


if __name__ == '__main__':
    sys.exit(main())
