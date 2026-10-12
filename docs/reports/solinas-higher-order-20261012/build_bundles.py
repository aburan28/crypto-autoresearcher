"""Standalone source+training bundle and separate immutable follow-up dataset."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2];TASK=REPO/'tasks/solinas_higher_order'
BASE=TASK/'runs/higher-order-20261012';FOLLOW=TASK/'runs/rare-followup-20261012'


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while data:=stream.read(1<<20):h.update(data)
    return h.hexdigest()


def pack(path,entries,compressed=False):
    path=Path(path)
    if path.exists():raise ValueError('Existing bundle preserved; choose a new path/version')
    compression=zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED
    with zipfile.ZipFile(path,'x',compression=compression,allowZip64=True) as archive:
        for source,name in entries:
            archive.write(source,name,compress_type=compression)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:raise ValueError('ZIP CRC failed')
        for source,name in entries:
            with archive.open(name) as stream:
                h=hashlib.sha256()
                while data:=stream.read(1<<20):h.update(data)
            if h.hexdigest()!=digest(source):raise ValueError('Bundled content SHA differs')
    return {'bundle_name':path.name,'bytes':path.stat().st_size,'sha256':digest(path),'files':len(entries),'zip_crc_and_all_entry_sha256':'passed'}


def main(runner_only=False):
    files=[]
    for path in sorted(FOLLOW.rglob('*')):
        if not path.is_file():continue
        relative=path.relative_to(FOLLOW)
        if any(p in ('records','build','__pycache__') for p in relative.parts) or path.name=='runner.lock' or path.suffix=='.tmp':continue
        if path.name=='dataset-inventory.json':continue
        files.append(path)
    inventory={'schema':1,'run_name':FOLLOW.name,'files':[{'path':str(p.relative_to(FOLLOW)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files],
               'scope':'All raw follow-up points, lossless JSONL records, source, configuration, environment, receipts, analysis and completed run log'}
    ip=FOLLOW/'dataset-inventory.json'
    if ip.exists() and json.loads(ip.read_text())!=inventory:raise ValueError('Follow-up inventory differs')
    ip.write_text(json.dumps(inventory,sort_keys=True,indent=2)+'\n');files.append(ip)
    if runner_only:
        result=json.loads((TASK/'publication/rare-followup-20261012-bundle.json').read_text())
    else:
        result=pack('/workspace/solinas-rare-followup-20261012-data.zip',[(p,FOLLOW.name+'/'+str(p.relative_to(FOLLOW))) for p in files])
        (TASK/'publication/rare-followup-20261012-bundle.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

    entries=[]
    for path in sorted(TASK.iterdir()):
        if path.is_file() and path.suffix in ('.py','.c','.json','.md','.txt','.sh'):
            entries.append((path,'solinas-higher-order-runner/'+path.name))
    for folder in ('tests','followup','utilities'):
        for path in sorted((TASK/folder).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                entries.append((path,'solinas-higher-order-runner/'+str(path.relative_to(TASK))))
    for path in sorted((BASE/'discovery/record-shards').glob('*.jsonl.gz')):
        entries.append((path,'solinas-higher-order-runner/training/discovery/record-shards/'+path.name))
    for name in ('receipt.json','provenance.json','record-shards.json'):
        entries.append((BASE/'discovery'/name,'solinas-higher-order-runner/training/discovery/'+name))
    guide=HERE/'RUNNER_GUIDE.txt'
    guide.write_text('''Self-contained public-point research package. Linux: Python 3.12+, cc, OpenSSL 3 headers/libcrypto.

bash bootstrap.sh /path/to/venv
/path/to/venv/bin/python research.py batch --output /data/seed-002 --seed your-public-seed-002 --reuse-discovery training/discovery --workers 3

Run from the extracted solinas-higher-order-runner directory. This package
includes all old-data training features, so no old raw rescan or agent is needed.
Every future independent batch needs a new seed AND a new output directory.
All outputs are immutable and resume requires identical source/configuration.
Use a scheduler for fixed batches; freeze a pooling/inference policy before
combining multiple seeds or repeatedly searching for favorable p values.

The followup/runner.py program is a separate fixed-candidate study. Its seed
is in followup/config.json; for an independent repeat, prospectively change
that public seed and use a new output directory. Preserve old config/source.

For a downloaded completed dataset, restore original JSON records before
re-verifying or re-analyzing it:
python utilities/restore_records.py /data/higher-order-20261012
python /data/higher-order-20261012/source/research.py verify --output /data/higher-order-20261012 --workers 3
Use the completed batch's frozen source/ for replay. The restoration helper
checks all gzip SHA hashes and never overwrites differing record bytes.

Main scientific results: 77,414,912 new points, 78 primary comparisons,
nominal 99.9% family; selected-candidate follow-up: 6,291,456 new points,
9 comparisons, separate nominal 99.99% family. Mean intervals are approximate.
No relative ECDLP-resistance or scalar/key-recovery claim is measured.
''')
    entries.append((guide,'solinas-higher-order-runner/guide/RUNNER_GUIDE.txt'))
    runner=pack('/workspace/solinas-higher-order-runner-v2.zip' if runner_only else '/workspace/solinas-higher-order-runner.zip',entries,True)
    if runner_only:
        runner['supersedes_for_distribution']='solinas-higher-order-runner.zip; additive archive-restoration utility, no scientific source/input change'
    (HERE/'runner-bundle.json').write_text(json.dumps(runner,indent=2,sort_keys=True)+'\n')
    (HERE/'data-bundles.json').write_text(json.dumps({'schema':1,'primary':json.loads((TASK/'publication/higher-order-20261012-bundle.json').read_text()),
        'followup':result,'runner':runner,'scope':'Local standalone artifacts; no new cloud upload claimed'},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'followup':result,'runner':runner}))


if __name__=='__main__':main(runner_only='--runner-only' in __import__('sys').argv)
