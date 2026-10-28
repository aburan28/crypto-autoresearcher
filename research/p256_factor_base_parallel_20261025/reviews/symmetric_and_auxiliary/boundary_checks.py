"""Bind fibre completeness to actual chain degree and replay constructed sums."""
import json,sys,hashlib,time
from pathlib import Path
import independent_check as ic
out=Path(__file__).resolve().parent;start=time.monotonic();directory=ic.BASE/'tracks/f2/receipts/validation-001'
cases={};degrees=[]
for path in sorted((directory/'cases').glob('*/summary.json')):
    s=ic.read(path);rows=[r for chunk in s['certificate_chunks'] for r in ic.read(directory/chunk)]
    good=sorted((r['target_point'] for r in rows if r['target_point'] is not None),key=lambda p:p[0])
    meta=s['metadata'];family=s['family'];n=s['raw_x_size'];matched=s['matched_accepted_M']
    if family=='elliptic_kernel':
        ic.need(meta['kernel_order']==2**meta['chain_length']==2*n,'actual chain degree gives kernel x bound')
        K=tuple(meta['kernel_generator'])
        ic.need(ic.mul(meta['kernel_order'],K,ic.AUX) is None and ic.mul(meta['kernel_order']//2,K,ic.AUX) is not None,'exact cyclic kernel metadata')
    elif family=='elliptic_generic':ic.need(2**meta['chain_length']==n,'actual generic chain degree')
    else:ic.need(2**meta['composition_depth']==n,'actual Dickson degree')
    cases[s['case']]={'summary':s,'matched':good[:matched],'all_accepted':len(good)}
    degrees.append({'case':s['case'],'raw':n,'matched_M':matched})
for n in [64,256,1024,4096]:
    group=[v for v in cases.values() if v['summary']['raw_x_size']==n]
    minimum=min(v['all_accepted'] for v in group)
    ic.need(all(v['summary']['matched_accepted_M']==minimum for v in group),'matched M is common minimum')
relations=ic.read(ic.BASE/'tracks/f2/receipts/relation-positive.json');verified=[]
for cert in relations['certificates']:
    stored=cases[cert['case']];points=list(map(tuple,cert['points']));Q=tuple(cert['target'])
    ic.need([list(p) for p in points]==stored['matched'][:3],'constructed points belong to sorted matched base')
    ic.need(len({p[0] for p in points})==3 and all(ic.on(p,ic.TARGET) for p in points),'distinct genuine target points')
    ic.need(ic.add(ic.add(points[0],points[1],ic.TARGET),points[2],ic.TARGET)==Q,'constructed target exact sum')
    ic.need(ic.resultant4(*(p[0] for p in points),Q[0])==0,'independent relation resultant')
    ic.need(ic.shortmul(ic.R,Q,-3)[2]==0,'constructed target subgroup')
    ic.need(cert['recovery_claim'] is False,'no mistaken search/recovery interpretation')
    verified.append(cert['case'])
ic.need(len(verified)==12,'all constructed positives replayed')
record={'status':'PASS','assertions':ic.count,'observations':{'degree_metadata':degrees,'constructed_positive_certificates':verified,
'matched_sizes':[26,121,515,2066],'ordinary_public_target_search_tested':False},'command':[sys.executable,*sys.argv],
'wall_seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
'reviewer_dependency_sha256':hashlib.sha256((out/'independent_check.py').read_bytes()).hexdigest(),
'producer_imports':False,'official_research_gate':False}
p=out/'boundary-checks.json'
if p.exists():raise SystemExit('refuse overwrite')
p.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
