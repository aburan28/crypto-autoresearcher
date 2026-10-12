#!/usr/bin/env python3
"""Independent fixed-candidate public-point follow-up, runnable without an agent."""
import argparse
import concurrent.futures
import fcntl
import gzip
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1'; os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE/'core'))
import numpy as np
from scipy.stats import t,beta,binomtest
from native import Sampler,build,seed_for
from metrics import features,transport,decode
from oracle import add,multiply,scalar_draw


def canonical(value): return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':')).encode()+b'\n'


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while data:=stream.read(1<<20):h.update(data)
    return h.hexdigest()


def immutable(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=data:raise ValueError('Immutable content differs: '+str(path))
        return
    temp=path.with_name('.'+path.name+f'.{os.getpid()}.tmp');temp.write_bytes(data)
    try:os.link(temp,path)
    except FileExistsError:
        if path.read_bytes()!=data:raise ValueError('Concurrent immutable mismatch')
    finally:temp.unlink(missing_ok=True)


def jobs(config):
    result=[]
    for candidate in config['candidates']:
        for chunk in range(config['pairs_per_candidate']//config['chunk_pairs']):
            result.append({'id':candidate['id']+f'-{chunk:05d}','case':candidate['case'],'kind':'rare-followup','candidate':candidate,'chunk':chunk})
    return sorted(result,key=lambda j:seed_for(config['seed'],'job-order',j['id']))


def initialize(output):
    config=json.loads((HERE/'config.json').read_text())
    if config['pairs_per_candidate']<2 or config['pairs_per_candidate']%config['chunk_pairs']:raise ValueError('Fixed pair count/chunk invalid')
    if config['points_per_window']<64 or config['primary_tests']!=3*len(config['candidates']):raise ValueError('Feature/family contract invalid')
    source=[p for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.c','.json','.md')]
    design={'schema':1,'config':config,'source_sha256':{str(p.relative_to(HERE)):digest(p) for p in source},'scope':'Fresh fixed-candidate point observations only'}
    immutable(output/'design.json',canonical(design))
    for path in source:immutable(output/'source'/path.relative_to(HERE),path.read_bytes())
    return config,hashlib.sha256(canonical(design)).hexdigest()


def one_job(job,config,output,library,design_sha,verify=False):
    output=Path(output);candidate=job['candidate'];curve=candidate['curve'];p=curve['p'];width=(p.bit_length()+7)//8
    path=output/'records'/(job['id']+'.json')
    if verify:
        record=json.loads(path.read_text());raw=(output/record['raw']['path']).read_bytes()
        if record['job']!=job or record['design_sha256']!=design_sha or hashlib.sha256(raw).hexdigest()!=record['raw']['sha256']:raise ValueError('Raw/provenance mismatch')
        coords=decode(raw,p);checks=0;starts=0
        if len(coords)!=2*config['chunk_pairs']*config['points_per_window']:raise ValueError('Wrong point count')
        for x,y in coords:
            if not(0<=x<p and 0<=y<p) or (y*y-x*x*x-curve['A']*x-curve['B'])%p:raise ValueError('Point outside curve')
        if len(record['units'])!=2*config['chunk_pairs']:raise ValueError('Wrong unit count')
        for i,unit in enumerate(record['units']):
            if unit['offset_points']!=i*config['points_per_window'] or unit['label']!=('target' if i%2==0 else 'random'):raise ValueError('Unit partition or label differs')
            if unit['label']=='target' and unit['G']!=candidate['G']:raise ValueError('Target identity differs')
            begin=unit['offset_points'];end=begin+config['points_per_window'];selected=coords[begin:end];part=raw[begin*2*width:end*2*width]
            if features(part,p)!=unit['features'] or features(transport(part,p),p)!=unit['u2_features']:raise ValueError('Score replay failed')
            h=tuple(unit['G'])
            for k in range(8):
                position=k*(len(selected)-2)//7
                if add(curve,selected[position],h)!=selected[position+1]:raise ValueError('Affine transition failed')
                checks+=1
            if i<4:
                k,used=scalar_draw(bytes.fromhex(unit['seed_hex']),curve['N'])
                if multiply(curve,h,k)!=selected[0]:raise ValueError('Independent scalar start failed')
                starts+=1
        r,used=scalar_draw(bytes.fromhex(record['control_generator_seed_hex']),curve['N'])
        if multiply(curve,tuple(candidate['published_G']),r)!=tuple(record['units'][1]['G']):raise ValueError('Independent control generator failed')
        return {'points':len(coords),'transitions':checks,'scalar_starts':starts,'generator_scalars':1}
    start=time.perf_counter();cpu=time.process_time();sampler=Sampler(library)
    gs=seed_for(config['seed'],job['id'],'control-generators');graw,used=sampler.sample(curve,candidate['published_G'],gs,0,config['chunk_pairs'])
    controls=decode(graw,p);parts=[];units=[]
    for i,control in enumerate(controls):
        seed=seed_for(config['seed'],job['id'],i,'common-start')
        for label,g in [('target',candidate['G']),('random',list(control))]:
            raw,counter=sampler.sample(curve,g,seed,1,config['points_per_window'])
            units.append({'label':label,'pair':job['chunk']*config['chunk_pairs']+i,'G':g,'seed_hex':seed.hex(),
                          'offset_points':len(parts)*config['points_per_window'],'features':features(raw,p),
                          'u2_features':features(transport(raw,p),p),'counter_used':counter})
            parts.append(raw)
    raw=b''.join(parts);rp=output/'points'/(job['id']+'.raw');immutable(rp,raw)
    record={'schema':1,'design_sha256':design_sha,'job':job,'units':units,'control_generator_seed_hex':gs.hex(),
            'control_generator_counter':used,'raw':{'path':str(rp.relative_to(output)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)},
            'cpu_seconds':time.process_time()-cpu,'elapsed_seconds':time.perf_counter()-start}
    immutable(path,canonical(record));return {'points':len(raw)//(2*width)}


def paired(values,alpha):
    values=np.asarray(values,dtype=float);se=float(values.std(ddof=1)/math.sqrt(len(values)));mean=float(values.mean());c=float(t.ppf(1-alpha/2,len(values)-1))
    return {'difference':mean,'interval':[mean-c*se,mean+c*se],'standard_error':se,'pairs':len(values),'excludes_zero':mean-c*se>0 or mean+c*se<0}


def cp(hits,count,alpha):return [0 if hits==0 else float(beta.ppf(alpha/2,hits,count-hits+1)),1 if hits==count else float(beta.ppf(1-alpha/2,hits+1,count-hits))]


def analyze(output,config):
    records=[json.loads(p.read_text()) for p in sorted((output/'records').glob('*.json'))];comparisons=[];rates=[];alpha=config['familywise_alpha']/config['primary_tests']
    for candidate in config['candidates']:
        units=[u for r in records if r['job']['candidate']['id']==candidate['id'] for u in r['units']]
        by={label:sorted([u for u in units if u['label']==label],key=lambda u:u['pair']) for label in ('target','random')}
        if any(len(by[k])!=config['pairs_per_candidate'] for k in by):raise ValueError('Pair count differs')
        metric=candidate['metric'];scores={label:np.array([u['features'][metric] for u in by[label]]) for label in by}
        for representation,key in [('canonical','features'),('isomorphic-u2','u2_features')]:
            left=np.array([u[key][metric] for u in by['target']]);right=np.array([u[key][metric] for u in by['random']])
            comparisons.append(paired(left-right,alpha)|{'candidate':candidate['id'],'metric':metric,'representation':representation,'target_mean':float(left.mean()),'random_mean':float(right.mean())})
        lt=scores['target']>=candidate['discovery_score'];rt=scores['random']>=candidate['discovery_score'];only_l=int(np.count_nonzero(lt&~rt));only_r=int(np.count_nonzero(rt&~lt));n=only_l+only_r
        pvalue=float(binomtest(only_l,n,.5).pvalue) if n else 1.0
        rates.append({'candidate':candidate['id'],'metric':metric,'threshold':candidate['discovery_score'],'pairs':len(lt),'target_hits':int(lt.sum()),'random_hits':int(rt.sum()),
                      'target_rate_interval':cp(int(lt.sum()),len(lt),config['familywise_alpha']/6),'random_rate_interval':cp(int(rt.sum()),len(rt),config['familywise_alpha']/6),
                      'target_only':only_l,'random_only':only_r,'exact_paired_p':pvalue,'bonferroni_p':min(1,pvalue*config['primary_tests']),'crosses_threshold':pvalue<=alpha})
    result={'schema':1,'status':'derived_measured_observations','comparisons':comparisons,'rare_event_rates':rates,'familywise_alpha':config['familywise_alpha'],'primary_tests':config['primary_tests'],
            'mean_excludes_zero_count':sum(c['excludes_zero'] for c in comparisons),'rate_threshold_count':sum(r['crosses_threshold'] for r in rates),
            'inference':'Six paired Student mean approximations plus three exact paired McNemar/binomial tests; separate nominal 99.99% family. Six marginal event-rate Clopper-Pearson intervals use their own .0001 family correction.',
            'limits':'Candidate selection is old-data exploratory; fresh tests conditional on each fixed G. Zero rare hits do not exclude low event rates. No ordinary-prime matched candidate construction, security or scientific-state claim.'}
    immutable(output/'analysis.json',canonical(result));print(json.dumps(result),flush=True)


def archive(output):
    values=[p.read_bytes() for p in sorted((output/'records').glob('*.json'))];data=gzip.compress(b''.join(values),mtime=0)
    immutable(output/'record-shards'/'rare-followup.jsonl.gz',data)
    immutable(output/'record-shards.json',canonical({'schema':1,'records':len(values),'sha256':hashlib.sha256(data).hexdigest(),'encoding':'Lossless canonical JSONL gzip records'}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--workers',type=int,default=3);args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True);config,sha=initialize(output)
    with (output/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);queue=jobs(config);pending=[]
        for job in queue:
            path=output/'records'/(job['id']+'.json')
            if not path.exists():pending.append(job);continue
            record=json.loads(path.read_text())
            if record['job']!=job or record['design_sha256']!=sha or digest(output/record['raw']['path'])!=record['raw']['sha256']:raise ValueError('Resume mismatch')
        library=build(output/'build'/'sampler.so')
        if not(output/'environment.json').exists():
            try:commit=subprocess.check_output(['git','-C',str(HERE),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
            except subprocess.CalledProcessError:commit=None
            immutable(output/'environment.json',canonical({'python':sys.version,'platform':platform.platform(),'workers':args.workers,'command':sys.argv,'source_commit':commit,'recorded_at':time.time()}))
        start=time.time()
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures=[pool.submit(one_job,j,config,str(output),str(library),sha) for j in pending]
            for index,future in enumerate(concurrent.futures.as_completed(futures),1):
                future.result()
                if index%32==0:print(json.dumps({'stage':'sampling','completed_new':index,'pending':len(pending)}),flush=True)
        records=[json.loads((output/'records'/(j['id']+'.json')).read_text()) for j in queue]
        if not(output/'receipt.json').exists():immutable(output/'receipt.json',canonical({'schema':1,'status':'measured_complete','jobs':len(queue),'points':2*config['pairs_per_candidate']*config['points_per_window']*len(config['candidates']),
                    'raw_bytes':sum(r['raw']['bytes'] for r in records),'summed_job_cpu_seconds':sum(r['cpu_seconds'] for r in records),'final_invocation_wall_seconds':time.time()-start,'failures':0,'design_sha256':sha}))
        totals={'points':0,'transitions':0,'scalar_starts':0,'generator_scalars':0}
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures=[pool.submit(one_job,j,config,str(output),str(library),sha,True) for j in queue]
            for future in concurrent.futures.as_completed(futures):
                for k,v in future.result().items():totals[k]+=v
        immutable(output/'verification.json',canonical({'schema':1,'status':'passed','counts':totals,'all_raw_hashes_and_features_replayed':True,'same_session':True}))
        analyze(output,config);archive(output)


if __name__=='__main__':main()
