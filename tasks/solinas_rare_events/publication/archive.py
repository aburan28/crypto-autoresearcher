#!/usr/bin/env python3
"""Seal lossless compact data after completion; no sampling or source changes."""
import argparse
import gzip
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research import put_json,sha


def archive(run,output,publication):
    run=Path(run).resolve();output=Path(output).resolve();publication=Path(publication).resolve()
    if not json.loads((run/'completion.json').read_text())['fixed_sample_complete']:raise ValueError('Incomplete fixed sample')
    if json.loads((run/'verification.json').read_text())['validity']!='passed stated checks':raise ValueError('Missing verification')
    publication.mkdir(parents=True,exist_ok=True)
    files=sorted(p for p in run.rglob('*') if p.is_file() and p.name!='runner.lock' and not p.name.endswith('.tmp'))
    manifest={str(p.relative_to(run)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
    total=sum(x['bytes'] for x in manifest.values())
    if shutil.disk_usage(output.parent).free<total+128*1024**2:raise OSError('Insufficient space for conservative archive estimate; originals preserved')
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as archive:
        for p in files:archive.write(p,str(p.relative_to(run)))
        archive.writestr('MANIFEST.json',json.dumps({'schema':1,'files':manifest},indent=2,sort_keys=True)+'\n')
    with zipfile.ZipFile(output) as archive:
        if set(archive.namelist())!=set(manifest)|{'MANIFEST.json'}:raise ValueError('Archive inventory mismatch')
        for name,item in manifest.items():
            digest=hashlib.sha256();size=0
            with archive.open(name) as handle:
                for block in iter(lambda:handle.read(1024*1024),b''):digest.update(block);size+=len(block)
            if size!=item['bytes'] or digest.hexdigest()!=item['sha256']:raise ValueError(f'Archive content mismatch: {name}')
    receipt={'schema':1,'archive':str(output),'archive_sha256':sha(output),'archive_bytes':output.stat().st_size,
             'file_count':len(manifest),'uncompressed_bytes':total,'all_entries_verified':True,
             'coordinate_scope':'All measured bit strings and scores; complete rare/witness frames; non-event full xy streams are hashes and regenerable seeds, unless full mode was enabled'}
    put_json(publication/'dataset.json',receipt);put_json(publication/'dataset-manifest.json',{'schema':1,'files':manifest})
    with (publication/'records.jsonl.gz').open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as handle:
            for p in sorted((run/'records').glob('*.json')):
                handle.write((json.dumps(json.loads(p.read_text()),sort_keys=True,separators=(',',':'))+'\n').encode())
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--publication',type=Path,default=Path(__file__).resolve().parent);args=parser.parse_args()
    print(json.dumps(archive(args.run,args.output,args.publication),sort_keys=True))
