"""Lossless record sharding and portable/full data archives; no observations edited."""
import gzip
import hashlib
import json
import zipfile
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
TASK=REPO/'tasks/solinas_generator_cohorts'
RUN=TASK/'runs/cohorts-20261012'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def new_json(path,value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')


def portable_bundle():
    target=Path('/workspace/solinas-generator-cohorts-runner.zip')
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted(TASK.rglob('*')):
            if not path.is_file():continue
            relative=path.relative_to(TASK)
            if relative.parts[0] in ('runs','publication','__pycache__','.venv') or '__pycache__' in relative.parts:continue
            archive.write(path,'solinas-generator-cohorts/'+str(relative))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:raise ValueError('Portable ZIP CRC failure')
    result={'path':str(target),'bytes':target.stat().st_size,'sha256':sha(target),
            'contents':'Standalone sources, tests, frozen public input pool, configuration, protocol and instructions. No measured coordinate data.'}
    new_json(HERE/'runner-bundle.json',result);print(json.dumps(result),flush=True)


def shard_records():
    folder=RUN/'record-shards';folder.mkdir(exist_ok=True)
    groups=defaultdict(list)
    for path in sorted((RUN/'records').glob('*.json')):
        row=json.loads(path.read_text());job=row['job']
        suffix=job['cohort'] if job['mode']!='field' else job['arm']
        groups[f"{job['case']}-{job['mode']}-{suffix}"].append(path)
    shards=[]
    for group,paths in sorted(groups.items()):
        target=folder/(group+'.jsonl.gz')
        with target.open('xb') as binary:
            with gzip.GzipFile(fileobj=binary,mode='wb',mtime=0,compresslevel=6) as stream:
                for path in paths:
                    payload=path.read_bytes()
                    if b'\n' in payload.rstrip(b'\n'):raise ValueError('Record is not canonical single-line JSON')
                    stream.write(payload)
        restored=gzip.decompress(target.read_bytes()).splitlines(keepends=True)
        if len(restored)!=len(paths) or any(raw!=path.read_bytes() for raw,path in zip(restored,paths)):
            raise ValueError('Lossless record shard verification failed')
        shards.append({'path':str(target.relative_to(RUN)),'sha256':sha(target),'bytes':target.stat().st_size,
                       'records':len(paths),'record_names':[p.name for p in paths],
                       'record_sha256':[sha(p) for p in paths]})
    new_json(RUN/'record-shards.json',{'schema':1,'lossless_bytes_verified':True,'shards':shards,
                                     'records':sum(s['records'] for s in shards),
                                     'note':'Original single-line JSON records reconstructed by splitting uncompressed lines, preserving their final newline; names and SHA-256 values retained.'})
    print(json.dumps({'record_shards':len(shards),'records':sum(s['records'] for s in shards)}),flush=True)


def dataset_bundle():
    target=Path('/workspace/solinas-generator-cohorts-20261012-data-v2.zip')
    entries=[]
    for root in (TASK,HERE):
        for path in sorted(root.rglob('*')):
            if not path.is_file():continue
            relative=path.relative_to(root)
            if '__pycache__' in relative.parts or 'build' in relative.parts or '.venv' in relative.parts:continue
            if path.name in ('runner.lock','dataset-bundle-v2.json','dataset-inventory-v2.json') or path.suffix=='.tmp':continue
            if path.name.startswith('dataset-build') and path.suffix=='.log':continue
            entries.append(path)
    inventory={'files':[{'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in entries],
               'raw_coordinate_bytes':json.loads((RUN/'receipt.json').read_text())['raw_bytes'],
               'note':'All task sources, measured records and raw points, frozen executable copies, inputs, manifests, verification/analysis, and derived report. Compiled libraries, locks, and actively written archive-generation progress logs excluded. Earlier auxiliary manifest is superseded by archive-correction.json.'}
    new_json(HERE/'dataset-inventory-v2.json',inventory)
    with zipfile.ZipFile(target,'x',allowZip64=True) as archive:
        for index,path in enumerate(entries):
            compression=zipfile.ZIP_STORED if path.suffix=='.raw' else zipfile.ZIP_DEFLATED
            archive.write(path,str(path.relative_to(REPO)),compress_type=compression,compresslevel=6)
            if (index+1)%4096==0:print(json.dumps({'archived_files':index+1,'total_files':len(entries)}),flush=True)
        archive.write(HERE/'dataset-inventory-v2.json',str((HERE/'dataset-inventory-v2.json').relative_to(REPO)),compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(target) as archive:
        for entry in inventory['files']:
            h=hashlib.sha256()
            with archive.open(entry['path']) as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
            # ZipExtFile validates CRC at EOF as well as this stronger content
            # hash. No success record exists until every member matches.
            if h.hexdigest()!=entry['sha256']:
                raise ValueError('Archived member differs from manifest: '+entry['path'])
        if archive.read(str((HERE/'dataset-inventory-v2.json').relative_to(REPO)))!=(HERE/'dataset-inventory-v2.json').read_bytes():
            raise ValueError('Archived inventory bytes differ')
    result={'path':str(target),'bytes':target.stat().st_size,'sha256':sha(target),
            'entries':len(entries)+1,'all_crc_verified':True,'all_member_sha256_verified':True,
            'raw_bytes':inventory['raw_coordinate_bytes'],'supersedes':'dataset-bundle.json'}
    new_json(HERE/'dataset-bundle-v2.json',result);print(json.dumps(result),flush=True)


if __name__=='__main__':
    import sys
    {'runner':portable_bundle,'records':shard_records,'dataset':dataset_bundle}[sys.argv[1]]()
