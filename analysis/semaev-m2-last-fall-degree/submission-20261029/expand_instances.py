#!/usr/bin/env python3
"""Generate the preregistered panel and retain exact counts/closure attempts.

Ten fresh draws per integer n=33..45 and n=47..51 (five polynomial,
five random), plus ten trace-zero draws at n=33. No rejection based on
solvability or degree. A second, degree-five pass covers the 50 frontier
draws subject to prospective matrix memory admission.
"""
import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time

from certificate_campaign import command, digest, run_item, save


def make_plan(dossier):
    sys.path.insert(0,str(dossier/'code'))
    from gf2n import Field,find_modulus
    from s3sys import Subspace,poly_basis,random_basis,random_curve_point_x
    items=[]
    for n in [*range(33,46),*range(47,52)]:
        field=Field(n,find_modulus(n)); k=(n+1)//2
        for family,reps in [('poly',5),('rand',5)]+([('tr0',10)] if n==33 else []):
            for rep in range(reps):
                name=f'fresh-n{n}-{family}-{rep:02d}'
                seed=int.from_bytes(hashlib.sha256(('SEMAEV-PANEL-20261029-v1\n'+name).encode()).digest()[:8],'big')
                rng=random.Random(seed)
                if family=='poly':basis=poly_basis(field,k)
                elif family=='rand':basis=random_basis(field,k,rng)
                else:
                    basis=[]
                    while len(basis)<k:
                        v=rng.randrange(1,1<<n)
                        if field.trace(v):continue
                        try:Subspace(field,basis+[v])
                        except AssertionError:continue
                        basis.append(v)
                a2=rng.randrange(2);a6=rng.randrange(1,1<<n)
                z=random_curve_point_x(field,a2,a6,rng)
                record=dict(name=name,n=n,k=k,basis=family,zmode='curve',seed=seed,index=rep,
                            modulus_hex=format(field.f,'x'),a2=a2,a6_hex=format(a6,'x'),z_hex=format(z,'x'),
                            V_basis_hex=[format(v,'x') for v in basis],boolean_solutions=None)
                items.append(dict(id=name,degree=4,chain=False,record=record))
    frontier=[dict(x,id=x['id']+'-D5',degree=5) for x in items if x['record']['n']>=47]
    return dict(schema='semaev.certificate-plan/v1',kind='prospective_panel',items=items+frontier)


def process(item,args,plan_hash):
    record=item['record']; countdir=args.out/'counts'/record['name'];countdir.mkdir(parents=True,exist_ok=True)
    with open(countdir/'lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        existing=sorted(countdir.glob('attempt-*/result.json'))
        counted=json.loads(existing[-1].read_text()) if existing else None
        if counted is None or counted['status']!='completed':
            attempt=countdir/f'attempt-{len(list(countdir.glob("attempt-*")))+1:03d}';attempt.mkdir()
            argv=[args.count_binary,record['n'],record['modulus_hex'],record['z_hex'],record['a6_hex'],record['k'],*record['V_basis_hex']]
            counted=command(argv,attempt,'count',args.timeout,2**30,lock.fileno())
            counted.update(parameters=record,binary_sha256=digest(args.count_binary),plan_sha256=plan_hash)
            text=(attempt/'count.stdout.txt').read_text().strip()
            if counted['returncode']==0 and text.isdigit():counted['ordered_solutions']=int(text)
            else:counted['status']='failed'
            save(attempt/'result.json',counted)
    result=run_item(item,args,plan_hash)
    result_hash=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
    inference=args.out/item['id']/f'inference-{result_hash}.json'
    if not inference.exists():
        lower=None
        if counted['status']=='completed' and result['status']=='certificate_verified' and counted['ordered_solutions']<result['certified_codimension_lower_bound']:
            lower=item['degree']+1
        save(inference,dict(id=item['id'],last_fall_degree_lower_bound=lower,
             justification='Dossier Proposition 1.4: exact exhaustive count < independently certified codimension lower bound' if lower else 'No certified LFD lower bound inferred',
             count=counted,closure_result_canonical_sha256=result_hash,
             scope='Exact named Boolean presentation only; no asymptotic or solver-runtime inference.'))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--dossier',type=Path,required=True)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--count-binary',type=Path,required=True)
    p.add_argument('--source-commit',required=True)
    p.add_argument('--wait-for-replay',type=Path)
    p.add_argument('--workers',type=int,default=2)
    p.add_argument('--memory',type=int,default=40*2**30)
    p.add_argument('--timeout',type=int,default=21600)
    p.add_argument('--chunk',type=int,default=60000)
    p.add_argument('--generate-only',action='store_true')
    args=p.parse_args()
    if args.workers not in (1,2) or args.memory>40*2**30:p.error('maximum two workers at 40 GiB each')
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True)
    # The caller freezes and commits expansion-protocol.json before this command.
    with open(args.out/'expansion.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        path=args.out/'plan.json'
        if not path.exists():save(path,make_plan(args.dossier))
        plan=json.loads(path.read_text());plan_hash=digest(path)
        print(json.dumps({'phase':'inputs_retained','instances':190,'closure_requests':len(plan['items']),'plan_sha256':plan_hash}),flush=True)
        if args.generate_only:return 0
        if args.wait_for_replay:
            # At most two closure workers across both campaigns. Do not launch
            # while the original replay owner retains its flock.
            with open(args.wait_for_replay/'campaign.lock','a') as replay:
                print('Waiting for the existing historical replay owner to release its lock.',flush=True)
                fcntl.flock(replay,fcntl.LOCK_EX)
                if len(list(args.wait_for_replay.glob('*/attempt-*/result.json')))<13:
                    raise RuntimeError('historical replay ended without all 13 result records; reconcile before expansion')
        with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
            results=list(pool.map(lambda item:process(item,args,plan_hash),plan['items']))
        print(json.dumps({'phase':'finished','rows':len(results),'statuses':{s:sum(x['status']==s for x in results) for s in sorted({x['status'] for x in results})}}),flush=True)
        return int(any(x['status']=='failed' for x in results))


if __name__=='__main__':sys.exit(main())
