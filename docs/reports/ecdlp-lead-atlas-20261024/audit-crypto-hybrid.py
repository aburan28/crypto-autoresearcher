#!/usr/bin/env python3
"""Independently compare the merged crypto hybrid summary with its raw logs.

Run with a checkout containing the pinned crypto commit::

    python3 audit-crypto-hybrid.py --crypto-repo /path/to/crypto --output /tmp/hybrid-audit.json
"""
import argparse, datetime, hashlib, io, json, math, os, re, subprocess, tarfile, tempfile
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--crypto-repo',required=True,help='local crypto checkout with the pinned commit')
parser.add_argument('--head',default='c6c65bcab4c06d1a5b96ad03f882646691721982',help='immutable crypto source commit')
parser.add_argument('--output',required=True,help='receipt JSON path')
args=parser.parse_args()
REPO = args.crypto_repo
HEAD = args.head
PREFIX = 'research/dreg_hybrid_guess_20261024/'
OUT = Path(args.output)

def git(*args):
    return subprocess.check_output(['git','-C',REPO,*args])

def close(a,b):
    return math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-7)

summary_blob=git('show',HEAD+':'+PREFIX+'summary.json')
summary=json.loads(summary_blob)
paths=git('ls-tree','-r','--name-only',HEAD,PREFIX+'runs').decode().splitlines()
paths=[p for p in paths if p.endswith('.jsonl')]
archive=tarfile.open(fileobj=io.BytesIO(git('archive','--format=tar',HEAD,PREFIX+'runs')),mode='r:')
pattern=re.compile(r'(m3-\d+-\d+f?)\.d(\d+)\.([A-Za-z0-9]+)\.k(\d+)\.b(\d+)\.jsonl$')
raw={}
errors=[]
for path in paths:
    m=pattern.search(path)
    if not m:
        errors.append('unrecognized path '+path);continue
    cell,draw,rule,k,b=m.groups();key=(cell,int(draw),rule,int(k),int(b))
    data=archive.extractfile(path).read()
    try:
        records=[json.loads(line) for line in data.splitlines() if line.strip()]
    except Exception as e:
        errors.append(f'bad JSON {path}: {e}');continue
    if not records:
        errors.append('empty '+path);continue
    if len(records)!=1:
        errors.append(f'multiple records {path}: {len(records)}')
    raw[key]=(records[-1],hashlib.sha256(data).hexdigest())
rows={}
fields_checked=0
for row in summary['rows']:
    key=(row['cell'],row['draw'],row['rule'],row['k'])
    if key in rows:errors.append('duplicate summary row '+str(key))
    rows[key]=row
    branches=row['per_branch']
    if len(branches)!=row['branches_run']:
        errors.append('branches_run mismatch '+str(key))
    if len({p['b'] for p in branches})!=len(branches):
        errors.append('duplicate branch '+str(key))
    refuted=0;ops=0;products=0
    for p in branches:
        b=p['b'];rkey=key+(b,)
        if rkey not in raw:
            errors.append('summary branch missing raw '+str(rkey));continue
        obj,_=raw[rkey];scan=obj['scan']; last=scan[-1]
        exp={
            'refuted': bool(last['closure_refuted']),
            'cols': max(s['columns'] for s in scan),
            'rank': last['closure_rank'],
            'to':obj['measured_to'],
            'word_ops':sum(s['closure_word_ops'] for s in scan),
            'products':sum(s['closure_products'] for s in scan),
            'secs':sum(s['secs'] for s in scan),
        }
        for field,value in exp.items():
            fields_checked+=1
            if not close(p[field],value):
                errors.append(f'{rkey} {field}: summary={p[field]} raw={value}')
        if obj['draw']!=row['draw']:
            errors.append(f'{rkey} raw draw mismatch')
        refuted+=exp['refuted'];ops+=exp['word_ops'];products+=exp['products']
    for field,value in [('refuted',refuted),('sum_word_ops',ops),('sum_products',products)]:
        fields_checked+=1
        if not close(row[field],value):
            errors.append(f'{key} {field}: summary={row[field]} raw={value}')
    expected_status='all-refute' if len(branches)==2**row['k'] and refuted==len(branches) else ('fails' if refuted<len(branches) else 'incomplete')
    if row['kind']=='sat':expected_status='control'
    if row['status']!=expected_status:
        errors.append(f'{key} status: {row["status"]} vs {expected_status}')

unused=sorted(set(raw)-{key+(p['b'],) for key,row in rows.items() for p in row['per_branch']})
# Some raw logs are legitimately outside the scored summary; retain their keys for review.
unsat={}
for (cell,draw,rule,k),row in rows.items():
    if rule=='R1' and row['kind']=='unsat':
        unsat.setdefault((cell,draw),[]).append(row)
computed_kstar=[]
for (cell,draw),rs in sorted(unsat.items()):
    accepted=sorted(r['k'] for r in rs if r['status']=='all-refute' and r['branches_run']==2**r['k'])
    computed_kstar.append({'cell':cell,'draw':draw,'kstar':accepted[0] if accepted else None})
registered={(x['cell'],x['draw']):x['kstar'] for x in summary['kstar'] if x['rule']=='R1' and (x['cell'],x['draw']) in unsat}
for x in computed_kstar:
    if registered.get((x['cell'],x['draw']))!=x['kstar']:
        errors.append('kstar mismatch '+str(x))
for cost in summary['costs']:
    key=(cost['cell'],cost['draw'],'R1',cost['kstar']);row=rows[key]
    if not close(cost['hybrid_ops'],row['sum_word_ops']):
        errors.append('hybrid_ops mismatch '+str(key))
    expected=[row['sum_word_ops']/(cost['ops4_unspecialised']*cost['col_ratio_5_over_4']**e) for e in (3.0,4.1,4.25)]
    for i,(a,b) in enumerate(zip(cost['ratios'],expected)):
        if not close(a,b):errors.append(f'ratio mismatch {key} exponent {i}: {a} vs {b}')
receipt={
    'schema':'hybrid-raw-audit/v1','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'repo':'aburan28/crypto','head':HEAD,'summary_sha256':hashlib.sha256(summary_blob).hexdigest(),
    'raw_jsonl_count':len(paths),'raw_parsed_count':len(raw),'summary_rows':len(rows),
    'branch_fields_checked':fields_checked,'unsat_draws':len(computed_kstar),
    'computed_kstar':computed_kstar,'unused_raw_keys':[list(x) for x in unused],
    'cost_rows':len(summary['costs']),'errors':errors,
    'limits':['Checks committed JSONL records against committed summary, not binary execution or mathematical soundness of closure.','Does not verify control logs or independent degree-5 projection inputs.','The study reports no below-rho result and no m=4 improvement under its registered linear-k scenario.'],
    'status':'pass' if not errors else 'fail'
}
fd,tmp=tempfile.mkstemp(prefix='.hybrid-audit-',suffix='.json',dir=OUT.parent)
with os.fdopen(fd,'w') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
os.chmod(tmp,0o600);os.replace(tmp,OUT)
print(json.dumps({k:receipt[k] for k in ('status','raw_jsonl_count','raw_parsed_count','summary_rows','branch_fields_checked','unsat_draws','cost_rows','errors')},sort_keys=True))
