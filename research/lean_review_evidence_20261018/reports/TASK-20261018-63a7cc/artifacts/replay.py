from pathlib import Path
import hashlib, json, os, shutil, subprocess, time

TASK='TASK-20261018-63a7cc'
BASE=Path('/tmp/review-'+TASK)
ROOT=BASE/'lean'
ART=BASE/'artifacts'
ROOT.mkdir(parents=True, exist_ok=True)
ART.mkdir(exist_ok=True)
repo=Path('/workspace/review-lean-evidence')
inputs=json.loads((repo/'research/lean_review_evidence_20261018/inputs.json').read_text())
rows=[]
selected=[x for x in inputs['files'] if x['repository'] in ('crypto','cryptanalysis') and (x['path'].endswith(('.lean','.json','.toml','.md','.sh')) or x['path'].endswith('lean-toolchain'))]
selected=[x for x in selected if not any(t in x['path'] for t in ('inventory.','proof-chain.','render-report'))]
selected += [x for x in inputs['files'] if x['repository']=='crypto-lean' and x['path']=='tools/AuditAxioms.lean']
for x in selected:
    frozen=Path('/workspace/lean-review-inputs')/x['repository']/x['path']
    actual=hashlib.sha256(frozen.read_bytes()).hexdigest()
    row={**x,'actual_sha256':actual,'matches':actual==x['sha256']}
    if '/lean/' in x['path']:
        orig=Path('/workspace')/x['repository']/x['path']
        if orig.exists():
            row['cache_workspace_sha256']=hashlib.sha256(orig.read_bytes()).hexdigest()
            row['cache_workspace_matches']=row['cache_workspace_sha256']==actual
    rows.append(row)
(ART/'input-hash-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
assert all(r['matches'] and r.get('cache_workspace_matches',True) for r in rows)
for name,source in [('Transport','crypto'),('RhoCollision','cryptanalysis')]:
    src=Path('/workspace/lean-review-inputs')/source/'research/lean_retrospective_20261018/lean/Retrospective'/f'{name}.lean'
    dst=ROOT/'Retrospective'/f'{name}.lean'
    dst.parent.mkdir(exist_ok=True)
    shutil.copyfile(src,dst)
(ROOT/'lean-toolchain').write_text('leanprover/lean4:v4.35.0\n')
manifest=json.loads(Path('/workspace/lean-review-inputs/crypto/research/lean_retrospective_20261018/lean/lake-manifest.json').read_text())
deps=[]
for p in manifest['packages']:
    loc=Path('/workspace/crypto-lean') if p['name']=='CryptoLean' else Path('/workspace/crypto-lean/.lake/packages')/p['name']
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=loc,text=True).strip()
    dirty=subprocess.run(['git','diff','--quiet','HEAD','--'],cwd=loc).returncode
    deps.append({'name':p['name'],'path':str(loc),'expected_rev':p['rev'],'actual_rev':actual,'tracked_clean':dirty==0})
    assert actual==p['rev'] and dirty==0, deps[-1]
(ART/'dependency-checks.json').write_text(json.dumps(deps,indent=2)+'\n')
torsion=Path('/workspace/crypto-lean/CryptoLean/Group/Torsion.lean')
torsion_pinned=subprocess.check_output(['git','show','68117089795313bc2ffe3a3b5f72052d5fa7cb91:CryptoLean/Group/Torsion.lean'],cwd='/workspace/crypto-lean')
assert torsion.read_bytes()==torsion_pinned
(ART/'torsion-hash.json').write_text(json.dumps({'path':str(torsion),'sha256':hashlib.sha256(torsion_pinned).hexdigest(),'matches_git_blob':True},indent=2)+'\n')
env=os.environ.copy()
env.update(PATH='/workspace/.elan/bin:'+env['PATH'],ELAN_HOME='/workspace/.elan',XDG_CACHE_HOME='/workspace/.cache')
paths=[ROOT/'build']+[Path(d['path'])/'.lake/build/lib/lean' for d in deps]
env['LEAN_PATH']=':'.join(map(str,paths))
(BASE/'environment.json').write_text(json.dumps({k:env[k] for k in ('PATH','ELAN_HOME','XDG_CACHE_HOME','LEAN_PATH')},indent=2)+'\n')
commands=[]
def run(label,args):
    start=time.time()
    r=subprocess.run(args,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (ART/(label+'.log')).write_text(r.stdout)
    commands.append({'label':label,'command':args,'cwd':str(ROOT),'exit_status':r.returncode,'elapsed_seconds':time.time()-start,'log':label+'.log'})
    (ART/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    print(label,r.returncode,r.stdout[-1600:],flush=True)
    return r.returncode
run('lean-version',['lean','--version'])
for name in ('Transport','RhoCollision'):
    out=ROOT/'build/Retrospective'/f'{name}.olean'
    out.parent.mkdir(parents=True,exist_ok=True)
    assert run('recompile-'+name,['lean','-o',str(out),f'Retrospective/{name}.lean'])==0
assert run('axiom-audit',['lean','--run','/workspace/lean-review-inputs/crypto-lean/tools/AuditAxioms.lean','Retrospective.Transport','Retrospective.RhoCollision'])==0
