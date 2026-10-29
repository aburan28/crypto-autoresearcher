#!/usr/bin/env python3
"""Exact five-module candidate runtime. No host labels, logs, references or BSGS."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

NAMES={'curve.py','constructor.py','cohort.py','engine.py','worker_runtime.py'}
SCHEMA='classical.ecdlp.controlled-followup.'


def unique(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError('duplicate JSON key')
        d[k]=v
    return d


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()


def write(path,value):
    with Path(path).open('xb') as stream:
        stream.write(canonical(value)+b'\n');stream.flush();os.fsync(stream.fileno())


def sha(data):return hashlib.sha256(data).hexdigest()


def runtime_check(request):
    if os.getresuid()!=(1000,1000,1000) or os.getresgid()!=(1000,1000,1000) or os.getgroups():
        raise ValueError('UID/GID1000 and no supplementary groups required')
    expected={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/work','TMPDIR':'/work/tmp','PYTHONDONTWRITEBYTECODE':'1','LC_ALL':'C.UTF-8'}
    if dict(os.environ)!=expected:raise ValueError('unexpected inherited environment')
    for fd in Path('/proc/self/fd').iterdir():
        try:target=os.readlink(fd)
        except FileNotFoundError:continue
        if int(fd.name)>2:raise ValueError('unexpected inherited descriptor')
    root=Path(__file__).resolve().parent
    if any(os.access(path,os.W_OK) for path in [root.parent,root,root.parent/'stage']):raise ValueError('immutable parent write denial failed')
    if {p.name for p in root.iterdir()}!=NAMES:raise ValueError('unlisted worker files')
    if set(request['source_files'])!=NAMES:raise ValueError('source manifest closure')
    for name,digest in request['source_files'].items():
        path=root/name
        if path.is_symlink() or sha(path.read_bytes())!=digest or os.access(path,os.W_OK):raise ValueError('worker source binding/write access')


def run(request,out,plan_only=False):
    # Import only the committed candidate closure. The plan function draws nothing.
    import cohort
    import engine
    if plan_only:
        return {'schema':SCHEMA+'worker-plan/v1','cohort_plan':cohort.plan(), 'fresh_draws':0,'candidate_queries':0,'wall_valid':False,'worker_files':sorted(NAMES)}
    runtime_check(request)
    sampler=dict(request['sampler'])
    if set(sampler)!={'curve_proposal_limit','point_proposal_limit','target_proposal_limit'}:raise ValueError('static sampler fields')
    if any(type(v)is not int or v<=0 for v in sampler.values()):raise ValueError('positive explicit sampler caps')
    exclusions=request['prior_exclusions']['excluded_p_j']
    if not isinstance(exclusions,list) or any(not isinstance(p,list) or len(p)!=2 or any(type(v)is not int or v<0 for v in p) for p in exclusions) or len({tuple(p) for p in exclusions})!=len(exclusions):raise ValueError('malformed/duplicate exposed exclusions')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    # This line is future admitted run work only; source and plan-only never call it.
    nonce=os.urandom(32).hex()
    write(out.parent/'nonce-event.json',{'public_nonce':nonce,'bytes':32,'draw_phase':'admitted_worker_before_sampling','model':'domain-separated SHA256 streams from one public nonce; no independent physical-entropy claim'})
    sampler.update(nonce=nonce,excluded_p_j=exclusions)
    write(out.parent/'runtime-facts.json',{'resuid':list(os.getresuid()),'resgid':list(os.getresgid()),'supplementary_groups':os.getgroups(),'inherited_descriptors':[0,1,2],'immutable_parent_write_denied':True,'environment_values_collected':False,'worker_files':sorted(NAMES),'wall_valid':False})
    built=cohort.build_public(sampler)
    write(out.parent/'cohort-ledger.json',built['ledger'])
    public=built['public']
    # Exact bytes bind the public domain, coordinates and nonce; scalar labels absent.
    public_bytes=canonical(public)+b'\n'
    with (out.parent/'public-cohort.json').open('xb') as f:f.write(public_bytes)
    if built['status']!='complete':
        write(out.parent/'sampler-failure.json',{'status':'incomplete','jobs':built.get('jobs',[]),'wall_valid':False})
        return {'status':'incomplete','reason':'CAPPED_PROPOSALS','wall_valid':False}
    plan=built['plan']
    if plan['expected']!={'setups':216,'intents':36864,'singles':345600,'traces':36864,'cells':73728}:raise ValueError('frozen schedule counts differ')
    provenance={**request['provenance'],'cohort_sha256':sha(public_bytes)}
    host_plan={'expected':plan['expected'], 'provenance':provenance,
               'engine_interface_canonical_sha256':request['engine_plan']['engine_interface_canonical_sha256'],
               'max_total_orbit_points':request['engine_plan']['max_total_orbit_points'],
               'setup_ids':[], 'single_ids':[], 'trace_ids':[], 'paired_trace_ids':[]}
    setups=set()
    for job in plan['jobs']:
        setups.add(job['curve_id']+'/'+job['arm_id'])
        if job['kind']=='single':host_plan['single_ids'].append(job['id'])
        else:
            host_plan['trace_ids'].append(job['id'])
            if job['kind']=='confirmation-trace':host_plan['paired_trace_ids'].append(job['id'])
    host_plan['setup_ids']=sorted(setups)
    write(out.parent/'host-plan.json',host_plan)
    return engine.run_public(plan,public,out,provenance)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--plan-only',action='store_true')
    args=parser.parse_args()
    if args.request.is_symlink() or args.request.stat().st_size>64<<20:raise ValueError('bounded regular request')
    request=json.loads(args.request.read_bytes(),object_pairs_hook=unique)
    expected={'schema','engine_plan','sampler','prior_exclusions','seed_rules','provenance','source_files','command_seconds'}
    if set(request)!=expected or request['schema']!=SCHEMA+'worker-request/v1':raise ValueError('worker request fields/schema')
    result=run(request,args.out,args.plan_only)
    print(json.dumps(result,sort_keys=True,allow_nan=False))
    return 0 if args.plan_only or result.get('status')=='complete' else 1


if __name__=='__main__':raise SystemExit(main())
