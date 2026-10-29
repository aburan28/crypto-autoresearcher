"""Final local seal and input-byte check; no network or Git mutation."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,zipfile
p=Path(__file__).resolve().parent;study=p.parents[1];repo=study.parents[1]
seal=p/'final-seal.json'
if seal.exists():raise SystemExit('refuse overwrite')
def need(x,msg):
    if not x:raise AssertionError(msg)
need(hashlib.sha256((p/'blind-derivation.md').read_bytes()).hexdigest()=='cd079c507aad1c0225c83bc33b7a17f14b35628bb1a69f268ae37052df58cbd8','blind derivation unchanged')
exc=json.loads((study/'reviews/local-custody-exception.json').read_text());zpath=Path(exc['custody']['local_delta_zip'])
need(hashlib.sha256(zpath.read_bytes()).hexdigest()==exc['custody']['zip_sha256'],'ZIP digest')
zipfiles=0
with zipfile.ZipFile(zpath) as z:
    for n in z.namelist():
        if '/tracks/f1/' in n or '/tracks/f2/' in n or '/archive/payload-' in n:
            need(z.read(n)==(repo/n).read_bytes(),'sealed delta unchanged '+n);zipfiles+=1
base=exc['custody']['base_commit'];prefix=str(study.relative_to(repo));env=dict(os.environ,GIT_NO_LAZY_FETCH='1')
raw=subprocess.check_output(['git','ls-tree','-r',base,'--',prefix+'/baseline',prefix+'/tracks/f1'],cwd=repo,env=env)
basefiles=0
for row in raw.decode().splitlines():
    meta,name=row.split('\t');mode,kind,oid=meta.split()
    if kind!='blob':continue
    content=(repo/name).read_bytes();got=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    need(got==oid,'base input unchanged '+name);basefiles+=1
for n in ['custody-independent.json','f1-independent.json','cubic-independent.json','basis-independent.json','f2-independent.json','algebra-independent.json','controls-and-depth.json','boundary-checks.json','custody-supplement-v2.json']:
    need(json.loads((p/n).read_text())['status']=='PASS','check result '+n)
items=[]
for f in sorted(p.iterdir()):
    if not f.is_file() or f==seal:continue
    content=f.read_bytes();need(len(content)<65536,'artifact size '+f.name)
    items.append({'path':f.name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
record={'schema':'local-review-final-content-seal/v1','task':'TASK-20261025-1a83bb','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'LOCAL_PACKET_SEALED','blind_derivation_unchanged':True,'producer_delta_and_custody_files_rechecked':zipfiles,'base_original_f1_and_baseline_files_rechecked':basefiles,
 'all_delivered_files_under_64KiB':True,'artifacts':items,'procedure_addendum':'procedure-addendum.md',
 'canonical_review_gate_satisfied':False,'publication_authorized':False,'official_or_model_attestation_supplied':False,
 'command':[sys.executable,*sys.argv]}
seal.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='artifacts'}))
