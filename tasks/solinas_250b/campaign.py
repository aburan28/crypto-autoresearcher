#!/usr/bin/env python3
"""Resumable fixed 250-billion public-point campaign; no agent is required."""
import argparse
import concurrent.futures
import fcntl
import gzip
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
import numpy as np
import scipy
from common import HERE,ARMS,now,sha,put_json,jobs_for,model_for,source_hashes
from counts import summarize
from native import Engine,build,seed_for
from stores import make_archive,persist_archive,check_destination
from verify_chunk import verify_job


def read_record(path):
    expected=Path(path).parent.joinpath('record.sha256').read_text().strip()
    if sha(path)!=expected:raise ValueError('Immutable chunk record checksum mismatch')
    with gzip.open(path,'rt') as handle:return json.load(handle)


def save_record(path,record):
    path=Path(path);directory=path.parent
    temporary=directory.with_name('.'+directory.name+'.'+uuid.uuid4().hex+'.tmp');temporary.mkdir()
    with (temporary/path.name).open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as handle:
            handle.write((json.dumps(record,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())
        raw.flush();os.fsync(raw.fileno())
    (temporary/'record.sha256').write_text(sha(temporary/path.name)+'\n')
    os.rename(temporary,directory)


def selection(jobs,config):
    witnesses=[];examples=[]
    for named,key in ((True,'aggregate_witness_named_jobs'),(False,'aggregate_witness_ordinary_jobs')):
        group=[j for j in jobs if j['named']==named]
        witnesses.extend(j['id'] for j in sorted(group,key=lambda j:seed_for(config['seed'],'witness-retention',j['id']))[:config[key]])
    for model in sorted({j['model'] for j in jobs}):
        group=[j for j in jobs if j['model']==model]
        examples.extend(j['id'] for j in sorted(group,key=lambda j:seed_for(config['seed'],'example-retention',j['id']))[:2])
    return {'witness_jobs':sorted(witnesses),'example_jobs':sorted(examples),'event_frame_cap':8,'extreme_frame_cap':8}


def execute_job(run,job,model,config,settings,design_hash,library,retention):
    run=Path(run);record_path=run/'records'/job['id']/'record.json.gz'
    if record_path.exists():
        record=read_record(record_path)
        if record['design_sha256']!=design_hash or record['job']!=job:raise ValueError('Changed resume record/design')
        if settings['kind']!='aggregate':check_destination(record['destination'],settings)
        else:
            for name,item in record['retained_files'].items():
                path=run/'retained'/job['id']/name
                if path.stat().st_size!=item['bytes'] or sha(path)!=item['sha256']:raise ValueError('Changed retained frame file')
        return record
    attempt=run/'attempts'/f"{job['id']}-{uuid.uuid4().hex}";attempt.mkdir()
    start=now();wall=time.perf_counter();cpu=time.process_time()
    curve=model['curve'] if job['named'] else {k:model[k] for k in ('p','A','B','N')}
    named=(1 if model.get('case')=='P-192' else 2) if job['named'] else 0
    metric=model['metric_index'] if job['named'] else 0;threshold=model['threshold_integer'] if job['named'] else 22
    starts=seed_for(config['seed'],job['id'],'starts');generators=seed_for(config['seed'],job['id'],'generators')
    cap=8 if settings['kind']=='aggregate' else None
    invocation={'started':start,'job':job,'curve':curve,'step':model['G'],'start_seed':starts.hex(),'generator_seed':generators.hex(),
                'design_sha256':design_hash,'event_frame_cap':cap,'native_mode':named,'metric_index':metric,'threshold_integer':threshold}
    put_json(attempt/'invocation.json',invocation)
    try:
        data=Engine(library).sample(curve,model['G'],named,job['count'],metric,threshold,starts,generators,attempt,
                                   max_event_frames=cap,event_limit_bytes=32*1024**2)
        data['bits'].tofile(attempt/'bits.bin');data['scores'].astype('<u4',copy=False).tofile(attempt/'scores.bin')
        if named:data['public_scalars'].tofile(attempt/'public-scalars.bin')
        files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(attempt.iterdir()) if p.is_file()}
        points=job['count']*(3 if named else 1)*256
        record={'schema':1,'id':job['id'],'job':job,'design_sha256':design_hash,'started':start,'finished_sampling':now(),
            'cohorts':ARMS if named else ['ordinary_step'],'point_observations':points,'online_oncurve_checks':data['oncurve_checks'],
            'counter_consumed':data['counter_consumed'],'coordinate_stream_sha256':data['coordinate_sha256'],'files':files,
            'event_frame_cap':cap,'selected_metric_event_counts':np.sum(data['scores'][:,:,metric]>=threshold,axis=0).tolist(),
            'counts':summarize(data['scores'],model,config,job['named'])}
        # Reuse the independently checked verifier on immutable temporary layout.
        alias=run/'artifacts'/job['id']
        if alias.is_symlink():
            if not alias.resolve().is_relative_to(run/'attempts'):raise ValueError('Unexpected artifact alias')
            alias.unlink()
        os.symlink(attempt,alias)
        try:record['verification']=verify_job(run,job,model,record)
        finally:alias.unlink()
        put_json(attempt/'verification.json',record['verification'])
        record['files']['verification.json']={'bytes':(attempt/'verification.json').stat().st_size,'sha256':sha(attempt/'verification.json')}
        if settings['kind']!='aggregate':
            archive=attempt/'compact.zip';make_archive(attempt,archive,record['files'])
            record['destination']=persist_archive(archive,settings,design_hash,job['id'])
            record['raw_retention']='All compact measurement files in checksum-confirmed immutable shard'
            record['retained_files']={}
        else:
            retained=[]
            if job['id'] in retention['witness_jobs']:retained.append('witness.frames')
            if job['id'] in retention['example_jobs']:retained.extend(('events.frames','events.frames.extreme'))
            target=run/'retained'/job['id'];target.mkdir(parents=True,exist_ok=True)
            for name in retained:shutil.copyfile(attempt/name,target/name)
            record['retained_files']={name:record['files'][name] for name in retained}
            record['destination']={'kind':'aggregate','verified':True}
            record['raw_retention']='Explicit bounded aggregate mode: exact sufficient counts and stream hashes; only prospectively selected witness/example jobs persist full frames; bit strings and other raw values are not persisted'
        record.update(finished=now(),wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu,validity='passed_online_and_independent_chunk_checks')
        save_record(record_path,record)
        # Only this new verified transfer/measurement scratch is removed.
        shutil.rmtree(attempt)
        return record
    except BaseException as error:
        failure={'finished':now(),'error':type(error).__name__,'reason':str(error),'native_code':getattr(error,'native_code',None),
                 'partial_oncurve_checks':getattr(error,'oncurve_checks',None),'partial_counter_consumed':getattr(error,'counter_consumed',None),
                 'asserts_nothing_about':'Partial/failed attempts are not completed scientific observations'}
        if attempt.exists():put_json(attempt/'failure.json',failure)
        raise


def git(*args):
    result=subprocess.run(['git','-C',str(HERE),*args],capture_output=True,text=True)
    return result.stdout.strip() if not result.returncode else None


def run_campaign(output,inputs,config,settings,workers,max_new_jobs=None):
    if config['window_points']!=256:raise ValueError('This measured-bit engine supports exactly256-point windows')
    output=Path(output).resolve();jobs=jobs_for(inputs,config)
    total=sum(j['count']*(3 if j['named'] else 1)*256 for j in jobs)
    if total!=config['requested_point_observations']:raise ValueError('Source/config exact target differs')
    if max_new_jobs is not None and max_new_jobs<1:raise ValueError('Partial invocation limit must be positive')
    if settings['kind']=='filesystem':
        root=Path(settings['root']);root.mkdir(parents=True,exist_ok=True)
        reserve=int(70*1024**3*total/250000000000)+32*1024**2
        if not (Path(output)/'design.json').exists() and shutil.disk_usage(root).free<reserve:raise OSError('Full retained campaign needs sufficient archive capacity (~70 GB for the default target)')
    required=(244+8*workers if settings['kind']=='aggregate' else 164+80*workers)*1024**2
    output.mkdir(parents=True,exist_ok=True)
    with (output/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        design={'inputs':inputs,'config':config,'storage':settings,'source_sha256':source_hashes(),'retention_selection':selection(jobs,config)}
        design_hash=hashlib.sha256(json.dumps(design,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if (output/'design.json').exists():
            if json.loads((output/'design.json').read_text())!=design:raise ValueError('Changed source/model/config/storage on resume; refuse')
        else:
            if shutil.disk_usage(output).free<required:raise OSError('Insufficient scratch/metadata headroom; no scientific sampling started')
            if settings['kind']=='s3':
                from stores import s3_client
                # Normal SDK identity is selected externally; never embed credentials.
                s3_client(settings).head_bucket(Bucket=settings['bucket'])
            put_json(output/'design.json',design);(output/'source').mkdir()
            for name in design['source_sha256']:shutil.copyfile(HERE/name,output/'source'/name)
            put_json(output/'runtime.json',{'started':now(),'command':sys.argv,'source_commit':git('rev-parse','HEAD'),'dirty_tree':git('status','--porcelain'),
                'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),
                'openssl':subprocess.run(['openssl','version'],capture_output=True,text=True).stdout.strip(),'workers':workers,
                'model_metadata':{'policy':None,'model':None,'effort':None,'usage':None,'provenance':'Not exposed by API'},
                'scope':'Fixed public point-distribution observations; no official scientific transition or ECDLP-cost inference'})
        for name in ('attempts','artifacts','records','build','retained'):(output/name).mkdir(exist_ok=True)
        if shutil.disk_usage(output).free<(64 if settings['kind']=='aggregate' else 260)*1024**2:raise OSError('Scratch headroom exhausted; preserve previous attempts and restore capacity before resuming')
        library=str(build(output/'build'/'engine.so'));done={};pending=[]
        for job in jobs:
            path=output/'records'/job['id']/'record.json.gz'
            if path.exists():
                record=read_record(path)
                if record['design_sha256']!=design_hash or record['job']!=job or record['validity']!='passed_online_and_independent_chunk_checks':raise ValueError('Resume record mismatch')
                if settings['kind']!='aggregate':check_destination(record['destination'],settings)
                else:
                    for name,item in record['retained_files'].items():
                        p=output/'retained'/job['id']/name
                        if p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('Retained frame changed')
                done[job['id']]=record
            else:pending.append(job)
        if max_new_jobs is not None:pending=pending[:max_new_jobs]
        points=sum(r['point_observations'] for r in done.values());start=time.perf_counter();iterator=iter(pending);active={}
        executor=concurrent.futures.ProcessPoolExecutor(max_workers=workers)
        def schedule(job):
            future=executor.submit(execute_job,str(output),job,model_for(inputs,job),config,settings,design_hash,library,design['retention_selection'])
            active[future]=job
        try:
            for _ in range(min(workers,len(pending))):schedule(next(iterator))
            while active:
                finished,_=concurrent.futures.wait(active,return_when=concurrent.futures.FIRST_COMPLETED)
                for future in finished:
                    job=active.pop(future);record=future.result();done[job['id']]=record;points+=record['point_observations']
                    progress={'recorded_at':now(),'completed_jobs':len(done),'requested_jobs':len(jobs),'point_observations':points,
                              'requested_point_observations':total,'elapsed_this_invocation_seconds':time.perf_counter()-start}
                    tmp=output/'status.json.tmp'
                    tmp.write_text(json.dumps(progress,sort_keys=True)+'\n');os.replace(tmp,output/'status.json')
                    print(json.dumps(progress,sort_keys=True),flush=True)
                    next_job=next(iterator,None)
                    if next_job:schedule(next_job)
        except BaseException as error:
            for future in active:future.cancel()
            put_json(output/f'infrastructure-stop-{uuid.uuid4().hex}.json',{'at':now(),'error':type(error).__name__,'reason':str(error),
                'recorded_points_at_stop':points,'fixed_target':total,'scope':'Operational stop; partial science is not a completed study'})
            raise
        finally:executor.shutdown(wait=True,cancel_futures=True)
        complete=len(done)==len(jobs) and points==total
        receipt={'schema':1,'at':now(),'design_sha256':design_hash,'completed_jobs':len(done),'requested_jobs':len(jobs),
                 'point_observations':points,'requested_point_observations':total,'fixed_sample_complete':complete,
                 'failed_attempts':len(list((output/'attempts').glob('*/failure.json')))}
        if complete and not (output/'completion.json').exists():put_json(output/'completion.json',receipt)
        return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--storage',choices=('filesystem','s3','aggregate'),required=True)
    parser.add_argument('--archive-root',type=Path);parser.add_argument('--bucket',default='crypto-autoresearcher')
    parser.add_argument('--prefix',default='datasets/solinas-250b-20261012');parser.add_argument('--aws-profile');parser.add_argument('--region',default='us-east-1')
    parser.add_argument('--workers',type=int,default=3);parser.add_argument('--max-new-jobs',type=int)
    parser.add_argument('--inputs',type=Path,default=HERE/'inputs.json');parser.add_argument('--config',type=Path,default=HERE/'config.json');args=parser.parse_args()
    if args.workers<1:parser.error('workers must be positive')
    if args.storage=='filesystem' and not args.archive_root:parser.error('--archive-root is required for filesystem storage')
    settings={'kind':args.storage}
    if args.storage=='filesystem':settings['root']=str(args.archive_root.resolve())
    if args.storage=='s3':settings.update(bucket=args.bucket,prefix=args.prefix,aws_profile=args.aws_profile,region=args.region)
    inputs=json.loads(args.inputs.read_text());config=json.loads(args.config.read_text())
    result=run_campaign(args.output,inputs,config,settings,args.workers,args.max_new_jobs)
    print(json.dumps(result,sort_keys=True))
    if result['fixed_sample_complete']:
        run=Path(args.output)
        if not (run/'analysis.json').exists():subprocess.run([sys.executable,str(HERE/'analyze.py'),str(run)],check=True)


if __name__=='__main__':main()
