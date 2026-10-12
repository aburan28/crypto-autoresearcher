#!/usr/bin/env python3
"""Restore byte-identical ignored JSON records from checked lossless shards."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while block:=stream.read(1<<20):h.update(block)
    return h.hexdigest()


def restore(root):
    root=Path(root);manifest=json.loads((root/'record-shards.json').read_text())
    shards=manifest.get('shards')
    if shards is None:shards=[{'path':'record-shards/rare-followup.jsonl.gz','sha256':manifest['sha256'],'records':manifest['records']}]
    count=0
    for item in shards:
        source=root/item['path']
        if sha(source)!=item['sha256']:raise ValueError('Shard checksum mismatch')
        restored=0
        with gzip.open(source,'rb') as stream:
            for line in stream:
                row=json.loads(line);identity=row.get('id') or row.get('job',{}).get('id')
                if not identity or Path(identity).name!=identity or identity in ('.','..'):raise ValueError('Unsafe record identity')
                path=root/'records'/(identity+'.json');path.parent.mkdir(exist_ok=True)
                if path.exists():
                    if path.read_bytes()!=line:raise ValueError('Existing record differs; refusing overwrite')
                else:
                    with path.open('xb') as target:target.write(line)
                restored+=1
        if restored!=item['records']:raise ValueError('Shard record count differs')
        count+=restored
    result={'directory':str(root),'restored_records':count,'sha256':'all shards verified'}
    if (root/'discovery/record-shards.json').exists():result['discovery']=restore(root/'discovery')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run_directory',type=Path)
    args=parser.parse_args();print(json.dumps(restore(args.run_directory)))
