#!/usr/bin/env python3
"""Engineering regression fixture only; no experiment/legacy program runs."""
import json, os, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
TOOL=ROOT/'tools/artifacts/artifacts.py'
OUT=Path(__file__).with_name('partial-clone-check-receipt.json')
assert not OUT.exists()
TMP=Path(tempfile.mkdtemp(prefix='nistseed-artifact-gate-',dir='/Volumes/SSD990/llm/tmp'))
ENV=dict(os.environ,GIT_AUTHOR_NAME='fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
records=[]
def call(argv,cwd):
 r=subprocess.run(argv,cwd=cwd,env=ENV,capture_output=True,text=True)
 rec={'argv':argv,'cwd':str(cwd),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
 records.append(rec)
 return r

def must(argv,cwd):
 r=call(argv,cwd)
 if r.returncode: raise RuntimeError(r.stderr)
 return r.stdout.strip()
started=datetime.now(timezone.utc).isoformat()
results=[]
for name,nbytes in [('small',1024),('large',1100000)]:
 src=TMP/(name+'-src');src.mkdir()
 must(['git','init','-q'],src)
 (src/'README.md').write_text('partial-clone fixture\n')
 must(['git','add','README.md'],src);must(['git','commit','-qm','base'],src)
 (src/'data').mkdir();(src/'data'/'sample.bin').write_bytes(b'x'*nbytes)
 must(['git','add','data/sample.bin'],src);must(['git','commit','-qm','candidate'],src)
 remote=TMP/(name+'-remote.git')
 must(['git','clone','--bare',str(src),str(remote)],TMP)
 must(['git','config','uploadpack.allowFilter','true'],remote)
 dst=TMP/(name+'-clone')
 must(['git','clone','--no-checkout','--filter=blob:none','--depth=2',remote.as_uri(),str(dst)],TMP)
 blob=must(['git','rev-parse','HEAD:data/sample.bin'],dst)
 # GIT_NO_LAZY_FETCH provides a read-only absence check before the actual gate.
 absent=subprocess.run(['git','cat-file','-e',blob],cwd=dst,env=dict(ENV,GIT_NO_LAZY_FETCH='1'),capture_output=True,text=True).returncode
 default=call([sys.executable,str(TOOL),'check','HEAD^','HEAD'],dst)
 must(['git','config','--local','core.abbrev','40'],dst)
 fixed=call([sys.executable,str(TOOL),'check','HEAD^','HEAD'],dst)
 results.append({'case':name,'bytes':nbytes,'blob':blob,'blob_absent_before_gate':absent!=0,'default_returncode':default.returncode,'default_stderr':default.stderr,'full_oid_returncode':fixed.returncode,'full_oid_stdout':fixed.stdout,'full_oid_stderr':fixed.stderr})
assert all(r['blob_absent_before_gate'] for r in results)
assert all(r['default_returncode']==2 and 'Not a valid object name' in r['default_stderr'] for r in results)
assert results[0]['full_oid_returncode']==0
assert results[1]['full_oid_returncode']==1 and 'data file(s) belong in the store' in results[1]['full_oid_stderr']
OUT.write_text(json.dumps({'scope':'artifact CI regression fixture only','started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'temporary_repository_root':str(TMP),'results':results,'commands':records,'named_orders_executed':0,'successful':True},indent=2)+'\n')
print(json.dumps({'successful':True,'results':results,'receipt':str(OUT)},indent=2))
