"""Bind delta directly to sealed ZIP and original F1/baseline to local base object."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
out=Path(__file__).resolve().parent;study=out.parents[1];repo=study.parents[1]
exc=json.loads((study/'reviews/local-custody-exception.json').read_text());base=exc['custody']['base_commit'];zip_path=Path(exc['custody']['local_delta_zip'])
need=lambda ok,msg:None if ok else (_ for _ in ()).throw(AssertionError(msg))
need(hashlib.sha256(zip_path.read_bytes()).hexdigest()==exc['custody']['zip_sha256'],'ZIP SHA256')
prefix=str(study.relative_to(repo));delta=[]
with zipfile.ZipFile(zip_path) as z:
    for name in z.namelist():
        if '/tracks/f1/' in name or '/tracks/f2/' in name or '/archive/payload-' in name:
            need(z.read(name)==(repo/name).read_bytes(),'direct ZIP byte mismatch: '+name);delta.append(name)
paths=[prefix+'/baseline',prefix+'/tracks/f1']
raw=subprocess.check_output(['git','ls-tree','-r',base,'--',*paths],cwd=repo)
basefiles=[]
for row in raw.decode().splitlines():
    meta,path=row.split('\t');mode,kind,oid=meta.split()
    if kind!='blob':continue
    content=subprocess.check_output(['git','cat-file','blob',oid],cwd=repo)
    need((repo/path).read_bytes()==content,'base tree byte mismatch: '+path);basefiles.append(path)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
status=subprocess.check_output(['git','status','--short','--untracked-files=no'],cwd=repo,text=True)
record={'status':'PASS','logical_base_object':base,'observed_checkout_HEAD':head,
'base_tree_baseline_and_original_f1_files':len(basefiles),'direct_ZIP_delta_and_custody_files':len(delta),
'ZIP_sha256':exc['custody']['zip_sha256'],'tracked_dirty_tree_status':status.splitlines(),
'canonical_dispatch_precondition_satisfied':False,'publication_authorized':False,
'interpretation':'The base object and all checked source bytes exist locally. Checkout HEAD remains older; no claim of pushed-input admission.',
'command':[sys.executable,*sys.argv],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
p=out/'custody-supplement.json'
if p.exists():raise SystemExit('refuse overwrite')
p.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
