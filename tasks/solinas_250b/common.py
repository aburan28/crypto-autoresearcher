"""Public-data identities and write-once metadata helpers."""
import hashlib
import json
import re
from datetime import datetime,timezone
from pathlib import Path
from native import seed_for
HERE=Path(__file__).resolve().parent
ARMS=['selected','published','random']


def now():return datetime.now(timezone.utc).isoformat()


def sha(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda:handle.read(1024*1024),b''):result.update(block)
    return result.hexdigest()


def put_json(path,value):
    with Path(path).open('x') as handle:json.dump(value,handle,sort_keys=True,indent=2,allow_nan=False);handle.write('\n')


def jobs_for(inputs,config):
    jobs=[]
    for named,models in ((True,inputs['candidates']),(False,inputs['ordinary_controls'])):
        for model in models:
            if not re.fullmatch(r'[A-Za-z0-9_-]+',model['id']):raise ValueError('Unsafe model identifier')
            for offset in range(0,model['windows'],config['chunk_windows']):
                jobs.append({'id':f"{model['id']}-{offset:09d}",'model':model['id'],'named':named,'offset':offset,
                             'count':min(config['chunk_windows'],model['windows']-offset)})
    return sorted(jobs,key=lambda job:seed_for(config['seed'],'order',job['id']))


def model_for(inputs,job):
    return next(model for model in inputs['candidates' if job['named'] else 'ordinary_controls'] if model['id']==job['model'])


def check_record(run,record):
    for name,item in record['files'].items():
        path=Path(run)/'artifacts'/record['id']/name
        if path.stat().st_size!=item['bytes'] or sha(path)!=item['sha256']:raise ValueError(f'Immutable content mismatch: {path}')


def source_hashes():
    return {p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.suffix in ('.py','.c','.json','.md','.txt')}


def events_for(model,config,named):
    if not named:return [{'metric':0,'threshold':t,'name':f'run{t}'} for t in config['longrun_spectrum']]
    if model['metric_index']==0:return [{'metric':0,'threshold':t,'name':f'run{t}'} for t in config['longrun_spectrum']]
    return [{'metric':model['metric_index'],'threshold':model['threshold_integer'],'name':model['metric']}]
