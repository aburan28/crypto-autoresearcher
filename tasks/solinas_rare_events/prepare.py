#!/usr/bin/env python3
"""Freeze public candidates and coefficient/x matched ordinary-prime models."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from oracle import sqrt_mod,add,multiply
HERE=Path(__file__).resolve().parent


def score_bits(bits):
    runs=[];run=1
    for i in range(1,len(bits)):
        if bits[i]==bits[i-1]:run+=1
        else:runs.append(run);run=1
    runs.append(run)
    parity=abs(sum(1 if bits[i]^bits[i+1]^bits[i+2] else -1 for i in range(len(bits)-2)))
    counts=[0]*16
    for i in range(len(bits)-3):counts[8*bits[i]+4*bits[i+1]+2*bits[i+2]+bits[i+3]]+=1
    motif=16*sum(c*c for c in counts)-(len(bits)-3)**2
    return [max(runs),parity,motif]


def freeze(path,data):
    raw=json.dumps(data,indent=2,sort_keys=True).encode()+b'\n'
    if path.exists() and path.read_bytes()!=raw:raise ValueError('Prepared inputs already differ')
    path.write_bytes(raw)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--gp',default='/workspace/solinas-runtime/pari/usr/bin/gp');args=parser.parse_args()
    prior=json.loads((HERE/'prior-inputs.json').read_text());old=json.loads((HERE/'prior-candidates.json').read_text())
    candidates=[]
    for candidate in old['candidates']:
        c=dict(candidate);q=multiply(c['curve'],tuple(c['G']),17);bits=[]
        for i in range(256):bits.append((q[0]>>64)&1);q=add(c['curve'],q,tuple(c['G']))
        metric={'longrun64':0,'triple64':1,'motif64':2}[c['metric']]
        c['metric_index']=metric;c['threshold_integer']=score_bits(bits)[metric]
        c['windows']=4194304 if metric==0 else 1048576
        c['point_step_identity_sha256']=hashlib.sha256(json.dumps({'curve':c['curve'],'G':c['G']},sort_keys=True).encode()).hexdigest()
        candidates.append(c)
    anchor=next(c for c in candidates if c['metric_index']==0);curve=anchor['curve'];step_x=anchor['G'][0]
    checks=[];controls=[]
    for arm in ('R','C'):
        eligible=[f for f in prior['fields'] if f['case']=='P-224' and f['arm']==arm]
        chosen=0
        for field in eligible:
            p=field['curves'][0]['p'];a=(p-3)%p;b=curve['B']%p;singular=(4*a*a*a+27*b*b)%p==0
            y=None if singular else sqrt_mod((step_x**3+a*step_x+b)%p,p)
            selected=not singular and y is not None and chosen<32
            checks.append({'source_field_id':field['id'],'arm':arm,'p':p,'singular':singular,'x_lifts':y is not None,'selected':selected})
            if selected:
                point=(step_x,y);q=None;small_order=None
                for i in range(1,257):
                    q=add({'p':p,'A':a},q,point)
                    if q is None:small_order=i;break
                controls.append({'id':f'ordinary-{arm}-{chosen:03d}','arm':arm,'source_field_id':field['id'],'p':p,'A':a,'B':b,
                                 'G':list(point),'small_order_at_most_256':small_order,'windows':65536,
                                 'population':'Uniform affine starts in full E(F_p); supplied point is a step, not a certified full-group generator'})
                chosen+=1
        if chosen!=32:raise ValueError('Not enough liftable fields in frozen source pool; no enlargement from outcomes')
    program=[]
    for i,c in enumerate(controls):program.append(f"p={c['p']};a={c['A']};b={c['B']};E=ellinit([a,b],p);N=ellcard(E);print({i},\" \",N,\" \",isprime(p),\" \",isprime(N));")
    env=os.environ.copy();env['LD_LIBRARY_PATH']='/workspace/solinas-runtime/pari/usr/lib/x86_64-linux-gnu'
    process=subprocess.run([args.gp,'-q','-f','-s','256M'],input='\n'.join(program)+'\n',capture_output=True,text=True,env=env,check=True)
    freeze(HERE/'control-preparation.json',{'schema':1,'field_checks':checks,'gp_program':program,'gp_stdout':process.stdout,'gp_stderr':process.stderr,
         'scope':'Public input/order preparation only, no rare-window score used for control selection'})
    lines=process.stdout.strip().splitlines()
    if len(lines)!=len(controls) or process.stderr.strip():raise ValueError('PARI card/proof output incomplete or warned')
    for line in lines:
        index,order,prime,orderprime=map(int,line.split());assert prime==1
        c=controls[index];c['N']=order;c['order_is_prime']=bool(orderprime);c['trace']=c['p']+1-order
        c['model_uid']='urn:ec-model:sha256:'+hashlib.sha256(json.dumps({k:c[k] for k in ('p','A','B')},sort_keys=True).encode()).hexdigest()
        if multiply(c,tuple(c['G']),c['N']) is not None:raise ValueError('Independent order/step membership check failed')
    freeze(HERE/'inputs.json',{'schema':1,'candidates':candidates,'ordinary_controls':controls,'prior_inputs_sha256':hashlib.sha256((HERE/'prior-inputs.json').read_bytes()).hexdigest(),
          'prior_candidates_sha256':hashlib.sha256((HERE/'prior-candidates.json').read_bytes()).hexdigest(),'provenance':'Internal frozen public parameters from previous study; ordinary fields reused, new coefficient-matched models; exact PARI isprime/ellcard, independent affine membership'})
    config={'schema':1,'seed':'solinas-rare-events-20261012-powered-v1','chunk_windows':16384,'window_points':256,'primary_tests':11,'familywise_alpha':.001,
            'rate_interval_alpha':.001,'longrun_spectrum':[18,20,22,24,26,28,30,32],'workers':3,'save_full_coordinates':False,
            'measurement_encoding':'Every bit-64 sequence and all exact integer scores; public random-G scalars; full rare/witness coordinate frames; SHA256 of complete transient coordinate stream per chunk/arm',
            'stopping':'Fixed windows. Native failure or disk failure stops with partial attempt artifacts; no result-based enlargement or stopping.'}
    freeze(HERE/'config.json',config)
    named=sum(c['windows']*3*256 for c in candidates);ordinary=sum(c['windows']*256 for c in controls)
    print(json.dumps({'selected_candidates':len(candidates),'ordinary_fields':len(controls),'named_point_observations':named,'ordinary_point_observations':ordinary,'total':named+ordinary}))


if __name__=='__main__':main()
