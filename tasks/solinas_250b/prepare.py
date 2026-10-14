#!/usr/bin/env python3
"""Expand input controls without using any new point-window outcomes."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from common import HERE,put_json,sha
from oracle import sqrt_mod,add,multiply


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--gp',default='/workspace/solinas-runtime/pari/usr/bin/gp')
    parser.add_argument('--gp-library',default='/workspace/solinas-runtime/pari/usr/lib/x86_64-linux-gnu');args=parser.parse_args()
    prior=json.loads((HERE/'prior-study.json').read_text());fields=json.loads((HERE/'prior-fields.json').read_text())
    candidates=prior['candidates']
    for candidate in candidates:candidate['windows']=177556850 if candidate['metric_index']==0 else 44389200
    anchor=next(c for c in candidates if c['metric_index']==0);controls=[];checks=[];counts={}
    for arm in ('R','C'):
        chosen=0
        for field in fields['fields']:
            if field['case']!='P-224' or field['arm']!=arm:continue
            p=field['curves'][0]['p'];a=(p-3)%p;b=anchor['curve']['B']%p;x=anchor['G'][0]
            singular=(4*a*a*a+27*b*b)%p==0;y=None if singular else sqrt_mod((x*x*x+a*x+b)%p,p)
            checks.append({'id':field['id'],'arm':arm,'p':p,'singular':singular,'liftable':y is not None})
            if y is None:continue
            curve={'p':p,'A':a,'B':b};point=(x,y);q=None;small=None
            for j in range(1,257):
                q=add(curve,q,point)
                if q is None:small=j;break
            controls.append({'id':f'ordinary-{arm}-{chosen:03d}','arm':arm,'source_field_id':field['id'],**curve,'G':list(point),
                'small_order_at_most_256':small,'windows':1420454,'population':'Uniform affine full-group starts; fixed public step, not certified full-group generator'})
            chosen+=1
        counts[arm]=chosen
    if counts!={'R':62,'C':63}:raise ValueError(f'Public eligible-field count differs: {counts}; stop before sampling')
    if len({m['p'] for m in controls})!=len(controls):raise ValueError('Control prime identities repeat; refuse field-unit inference')
    program=[f"p={m['p']};E=ellinit([{m['A']},{m['B']}],p);N=ellcard(E);print({i},\" \",N,\" \",isprime(p),\" \",isprime(N));" for i,m in enumerate(controls)]
    env=dict(os.environ,LD_LIBRARY_PATH=args.gp_library)
    command=[args.gp,'-q','-f','-s','256M'];result=subprocess.run(command,input='\n'.join(program)+'\n',capture_output=True,text=True,env=env)
    put_json(HERE/'control-preparation.json',{'schema':1,'command':command,'returncode':result.returncode,'field_checks':checks,'gp_program':program,
        'stdout':result.stdout,'stderr':result.stderr,'selection':'Every nonsingular liftable model in the frozen 144R+144C prime pool; no event-score or order filter'})
    if result.returncode or result.stderr.strip() or len(result.stdout.strip().splitlines())!=125:raise ValueError('PARI preparation incomplete or warned; no sampling')
    for row in result.stdout.strip().splitlines():
        index,n,prime,orderprime=map(int,row.split());model=controls[index]
        if not prime:raise ValueError('Control field is not prime')
        model.update(N=n,order_is_prime=bool(orderprime),trace=model['p']+1-n)
        model['model_uid']='urn:ec-model:sha256:'+hashlib.sha256(json.dumps({k:model[k] for k in ('p','A','B')},sort_keys=True).encode()).hexdigest()
        if multiply(model,tuple(model['G']),n) is not None:raise ValueError('Independent [N]H failed')
    total=256*(3*sum(m['windows'] for m in candidates)+sum(m['windows'] for m in controls))
    if total!=250000000000:raise ValueError('Exact requested observation count mismatch')
    put_json(HERE/'inputs.json',{'schema':1,'candidates':candidates,'ordinary_controls':controls,'source_sha256':{'prior-study.json':sha(HERE/'prior-study.json'),'prior-fields.json':sha(HERE/'prior-fields.json')},
        'provenance':'Internal PR2108 inputs and original prime pools; 61 more coefficient/x-matched models added without viewing new window outcomes','point_observations':total})
    config={'schema':1,'seed':'solinas-250-billion-20261012-v1','chunk_windows':16384,'window_points':256,'workers':3,
        'requested_point_observations':250000000000,'primary_tests':20,'familywise_alpha':.0001,'rate_interval_alpha':.0001,
        'longrun_spectrum':[18,20,22,24,26,28,30,32],'primary_longrun_thresholds':[22,28,30,32],
        'storage_selection':'Required at launch: filesystem, S3, or explicitly selected bounded aggregate retention',
        'aggregate_witness_named_jobs':64,'aggregate_witness_ordinary_jobs':64,'aggregate_event_examples_per_model':8,
        'stopping':'Fixed exact target; no outcome-based selection, stopping, or sample enlargement; failures preserve attempts and stop scheduling new work.'}
    put_json(HERE/'config.json',config)
    print(json.dumps({'point_observations':total,'named_windows_per_cohort':[m['windows'] for m in candidates],'ordinary_fields':counts,'ordinary_windows_per_field':1420454}))


if __name__=='__main__':main()
