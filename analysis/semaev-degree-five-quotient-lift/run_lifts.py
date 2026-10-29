#!/usr/bin/env python3
"""Retained, bounded native D4-to-D5 attempts under a frozen input plan."""
import argparse
import fcntl
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'semaev-m2-last-fall-degree/submission-20261029'))
from certificate_campaign import command, digest, save


def run_item(item,args,plan_hash,lockfd):
    root=args.out/item['id'];root.mkdir(exist_ok=True)
    existing=sorted(root.glob('attempt-*/result.json'))
    if existing:
        old=json.loads(existing[-1].read_text())
        if old['plan_sha256']!=plan_hash:raise ValueError('different plan already owns output')
        if old['status'] in ('certificate_verified','projection_kills_one','resource_capped'):
            if old.get('certificate_sha256') and digest(existing[-1].parent/'certificate.bin')!=old['certificate_sha256']:
                raise ValueError('retained certificate changed')
            return old
    attempt=root/('attempt-%03d'%(len(list(root.glob('attempt-*')))+1));attempt.mkdir()
    record=item['record'];seed=args.seed_data/item['id']/'attempt-001/certificate.bin'
    result=dict(schema='semaev.quotient-lift-result/v1',id=item['id'],parameters=item,
        plan_sha256=plan_hash,source_commit=args.source_commit,status='started',steps={},
        last_fall_degree_lower_bound=None,scope='Exact named presentation only; a killed constant in an over-approximating quotient does not prove membership in W5.')
    save(attempt/'started.json',result)
    steps=result['steps']
    try:
        if digest(seed)!=item['expected_sha256']:raise ValueError('seed hash mismatch')
        replay=json.loads((seed.parent/'result.json').read_text())
        if replay['status']!='certificate_verified' or replay['certificate_sha256']!=item['expected_sha256']:
            raise ValueError('seed lacks matching independent acceptance receipt')
        result['seed_sha256']=item['expected_sha256']
        counter=args.runtime/'bin'/('s3c3count' if item.get('chain') else 'count_by_sum')
        count_argv=[counter,record['n'],record['modulus_hex'],record['z_hex'],record['a6_hex'],record['k'],*record['V_basis_hex']]
        steps['count']=command(count_argv,attempt,'count',args.timeout,2**30,lockfd)
        count_text=(attempt/'count.stdout.txt').read_text().strip()
        if steps['count']['returncode']==0 and count_text.isdigit():
            result['exact_solutions']=int(count_text)
            result['matches_historical_solution_count']=int(count_text)==record['boolean_solutions']
        else:
            result['count_error']='Exact counter did not complete with a nonnegative integer'
        cert=attempt/'certificate.bin'
        steps['producer']=command([args.runtime/'bin/quotient_lift',seed,cert,args.chunk,args.memory],attempt,'producer',args.timeout,args.memory,lockfd)
        if steps['producer']['returncode']:
            stderr=(attempt/'producer.stderr.txt').read_text()
            result['status']='resource_capped' if 'allocation gate refused' in stderr else 'failed'
            result['error']='Native producer did not complete; see retained logs'
        else:
            observation=json.loads((attempt/'producer.stdout.txt').read_text().strip())
            result['producer_observation']=observation
            if observation['status']=='projection_kills_one':
                if cert.exists():raise ValueError('unexpected certificate for killed constant')
                result['status']='projection_kills_one'
            elif observation['status']=='candidate_certificate':
                result['certificate_sha256']=digest(cert)
                argv=[sys.executable,args.dossier/'verify/cert_check.py']
                if item.get('chain'):argv.append('--t3')
                argv += [cert,record['n'],record['modulus_hex'],record['a2'],record['a6_hex'],record['z_hex'],*record['V_basis_hex']]
                steps['check']=command(argv,attempt,'check',args.timeout,args.memory,lockfd)
                valid=re.search(r'VALID: 1 is not in W_5\(F\), and codim W_5\(F\) >= (\d+)',(attempt/'check.stdout.txt').read_text())
                if steps['check']['returncode'] or not valid:raise ValueError('independent checker did not accept')
                bound=int(valid[1]);result['certified_codimension_lower_bound']=bound
                result['status']='certificate_verified'
                if result.get('matches_historical_solution_count') and result['exact_solutions']<bound:
                    result['last_fall_degree_lower_bound']=6
            else:raise ValueError('unrecognized producer outcome')
    except Exception as error:
        result['status']='failed';result['error']=str(error)
    result['artifacts']={p.name:dict(sha256=digest(p),bytes=p.stat().st_size) for p in attempt.iterdir() if p.is_file()}
    save(attempt/'result.json',result)
    print(json.dumps({k:result[k] for k in ('id','status','last_fall_degree_lower_bound')}),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','runtime','dossier','seed-data','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--source-commit',required=True)
    p.add_argument('--memory',type=int,default=16*2**30)
    p.add_argument('--timeout',type=int,default=21600)
    p.add_argument('--chunk',type=int,default=60000)
    args=p.parse_args()
    if args.memory>16*2**30 or not 1<=args.chunk<=60000:p.error('at most 16 GiB, one worker, 60000 rows per chunk')
    plan=json.loads(args.plan.read_text())
    for name,sha in plan['binary_sha256'].items():
        if digest(args.runtime/'bin'/name)!=sha:raise ValueError('binary hash mismatch: '+name)
    here=Path(__file__).resolve()
    for name,sha in plan['source_sha256'].items():
        if digest(here.parent/name)!=sha:raise ValueError('source hash mismatch: '+name)
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True)
    with open(args.out/'owner.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        results=[run_item(item,args,digest(args.plan),lock.fileno()) for item in plan['items']]
    return int(any(r['status']=='failed' for r in results))


if __name__=='__main__':sys.exit(main())
