#!/usr/bin/env python3
"""Fixed, resumable public-point study. No agent or private key required."""
import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import scipy
from native import Engine, build, seed_for

HERE = Path(__file__).resolve().parent
ARMS = ['selected', 'published', 'random']


def now(): return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''): digest.update(block)
    return digest.hexdigest()


def put_json(path, value):
    with Path(path).open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False); handle.write('\n')


def source_files():
    return sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py', '.c', '.json', '.txt', '.md'))


def jobs_for(inputs, config):
    jobs=[]
    for selected, models in ((True, inputs['candidates']), (False, inputs['ordinary_controls'])):
        for model in models:
            for offset in range(0, model['windows'], config['chunk_windows']):
                jobs.append({'id':f"{model['id']}-{offset:08d}", 'model':model['id'], 'named':selected,
                             'offset':offset, 'count':min(config['chunk_windows'], model['windows']-offset)})
    return sorted(jobs, key=lambda j: seed_for(config['seed'], 'order', j['id']))


def model_for(inputs, job):
    return next(m for m in inputs['candidates' if job['named'] else 'ordinary_controls'] if m['id']==job['model'])


def check_record(run, record):
    for name, item in record['files'].items():
        path=Path(run)/'artifacts'/record['id']/name
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError(f'Immutable artifact mismatch: {path}')


def execute_job(run, job, model, config, library, design_hash):
    run=Path(run); record_path=run/'records'/f"{job['id']}.json"
    if record_path.exists():
        record=json.loads(record_path.read_text()); check_record(run,record)
        if record['design_sha256']!=design_hash or record['job']!=job: raise ValueError('Resume design mismatch')
        return record
    destination=run/'artifacts'/job['id']
    if destination.exists(): raise ValueError(f'Unrecorded completed directory preserved; inspect {destination}')
    attempt=run/'attempts'/f"{job['id']}-{uuid.uuid4().hex}"
    attempt.mkdir(parents=True)
    start=now(); wall=time.perf_counter(); cpu=time.process_time()
    start_seed=seed_for(config['seed'], job['id'], 'starts'); gen_seed=seed_for(config['seed'], job['id'], 'generators')
    curve=model['curve'] if job['named'] else {k:model[k] for k in ('p','A','B','N')}
    named=(1 if model.get('case')=='P-192' else 2) if job['named'] else 0
    metric=model['metric_index'] if job['named'] else 0
    threshold=model['threshold_integer'] if job['named'] else 22
    invocation={'job':job, 'started':start, 'start_seed':start_seed.hex(), 'generator_seed':gen_seed.hex(),
                'design_sha256':design_hash, 'curve':curve, 'step':model['G'], 'native_mode':named,
                'metric_index':metric, 'threshold_integer':threshold}
    put_json(attempt/'invocation.json',invocation)
    try:
        result=Engine(library).sample(curve,model['G'],named,job['count'],metric,threshold,start_seed,gen_seed,attempt,config['save_full_coordinates'])
        result['bits'].tofile(attempt/'bits.bin')
        result['scores'].astype('<u4',copy=False).tofile(attempt/'scores.bin')
        if named: result['public_scalars'].tofile(attempt/'public-scalars.bin')
        cohorts=3 if named else 1
        counts=np.sum(result['scores'][:,:,metric]>=threshold,axis=0).tolist()
        files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(attempt.iterdir()) if p.is_file()}
        record={'schema':1,'id':job['id'],'job':job,'design_sha256':design_hash,'started':start,'finished':now(),
                'wall_seconds':time.perf_counter()-wall,'cpu_seconds':time.process_time()-cpu,
                'cohorts':ARMS if named else ['ordinary_step'], 'windows_per_cohort':job['count'],
                'point_observations':job['count']*cohorts*256, 'online_oncurve_checks':result['oncurve_checks'],
                'coordinate_stream_sha256':result['coordinate_sha256'],'counter_consumed':result['counter_consumed'],
                'selected_metric_event_counts':counts, 'files':files,'validity':'completed_native_checks',
                'coordinate_retention':'full' if config['save_full_coordinates'] else 'all measured bits, exact scores, all rare and fixed witness coordinate frames'}
        os.rename(attempt,destination); put_json(record_path,record)
        return record
    except BaseException as error:
        if attempt.exists(): put_json(attempt/'failure.json',{'finished':now(),'error_type':type(error).__name__,'reason':str(error)})
        raise


def run_study(output, inputs, config, workers):
    output=Path(output).resolve(); output.mkdir(parents=True,exist_ok=True)
    with (output/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        files={p.name:sha(p) for p in source_files()}
        design={'inputs':inputs,'config':config,'source_sha256':files}
        design_hash=hashlib.sha256(json.dumps(design,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if (output/'design.json').exists():
            if json.loads((output/'design.json').read_text())!=design: raise ValueError('Refuse changed source/config on resume; use a new directory')
        else:
            put_json(output/'design.json',design); (output/'source').mkdir()
            for p in source_files(): shutil.copyfile(p,output/'source'/p.name)
            def git(*args):
                result=subprocess.run(['git','-C',str(HERE),*args],capture_output=True,text=True)
                return result.stdout.strip() if result.returncode==0 else None
            put_json(output/'runtime.json',{'started':now(),'command':sys.argv,'source_commit':git('rev-parse','HEAD'),
                'dirty_tree':git('status','--porcelain'),'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
                'platform':platform.platform(),'openssl':subprocess.run(['openssl','version'],capture_output=True,text=True).stdout.strip(),
                'workers':workers,'model_metadata':{'requested_policy':None,'resolved_model':None,'reasoning_effort':None,'usage':None,'provenance':'not exposed by API'},
                'scope':'Public point distribution observations; no key recovery or attack-cost measurement'})
        for name in ('artifacts','attempts','records','build'): (output/name).mkdir(exist_ok=True)
        library=build(output/'build'/'engine.so')
        jobs=jobs_for(inputs,config)
        expected=sum(j['count']*(3 if j['named'] else 1)*256 for j in jobs)
        completed=0; points=0; start=time.perf_counter()
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures=[executor.submit(execute_job,str(output),j,model_for(inputs,j),config,str(library),design_hash) for j in jobs]
            for future in concurrent.futures.as_completed(futures):
                record=future.result(); completed+=1; points+=record['point_observations']
                print(json.dumps({'completed_jobs':completed,'requested_jobs':len(jobs),'point_observations':points,
                                  'requested_point_observations':expected,'elapsed_seconds':time.perf_counter()-start}),flush=True)
        receipt={'schema':1,'finished':now(),'design_sha256':design_hash,'requested_jobs':len(jobs),'completed_jobs':completed,
                 'point_observations':points,'requested_point_observations':expected,'actual_failures':len(list((output/'attempts').glob('*/failure.json'))),
                 'fixed_sample_complete':completed==len(jobs) and points==expected,'resumable':True}
        if not (output/'completion.json').exists(): put_json(output/'completion.json',receipt)
        return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--inputs',type=Path,default=HERE/'inputs.json');parser.add_argument('--config',type=Path,default=HERE/'config.json')
    parser.add_argument('--workers',type=int);parser.add_argument('--seed');parser.add_argument('--full-coordinates',action='store_true')
    args=parser.parse_args();inputs=json.loads(args.inputs.read_text());config=json.loads(args.config.read_text())
    if args.seed:config['seed']=args.seed
    if args.full_coordinates:config['save_full_coordinates']=True
    workers=args.workers or config['workers']
    if workers<1:parser.error('workers must be positive')
    print(json.dumps(run_study(args.output,inputs,config,workers),sort_keys=True))


if __name__=='__main__':main()
