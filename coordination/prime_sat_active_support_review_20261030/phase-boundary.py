"""Root-only mechanical custody helper; no scientific execution or source mutation."""
import argparse, datetime as dt, hashlib, json, subprocess
from pathlib import Path
import yaml
C = Path('coordination/prime_sat_active_support_review_20261030')
R = 'TASK-20261030-94b46f'
D = Path('research/prime_sat_active_support_review_20261030') / R

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha(p): return sha_bytes(Path(p).read_bytes())
def obj(p): return json.loads(Path(p).read_text())
def save(p, value):
    with Path(p).open('x') as f: f.write(json.dumps(value, indent=2) + '\n')
def stamp_after(value):
    now = dt.datetime.now(dt.timezone.utc)
    prior = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if prior.utcoffset() != dt.timedelta(0) or now <= prior: raise ValueError('Need actual later UTC observation; no synthetic timestamp.')
    return now.isoformat()
def git(*argv): return subprocess.check_output(['git', *argv])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('action', choices=['seal','release']);ap.add_argument('--published-commit');args=ap.parse_args()
    planp=C/'review-plan.yaml';plan=yaml.safe_load(planp.read_text())['review_plan'];contract=plan['blind_rederivation']['phased_release']
    derp=Path(contract['derivation_path']);der=obj(derp);md=D/'blind-derivation.md'
    if der['task_id']!=R or not der.get('quantities') or not der.get('sources_read'): raise ValueError('Incomplete blind derivation.')
    if der.get('readable_markdown_sha256')!=sha(md): raise ValueError('Readable derivation binding absent or wrong.')
    if dt.datetime.fromisoformat(der['generated_at'].replace('Z','+00:00'))<=dt.datetime.fromisoformat(plan['recorded_at'].replace('Z','+00:00')): raise ValueError('Plan must precede derivation.')
    for record in obj(C/'input-bindings.json')['source_bindings']:
        if sha(record['path'])!=record['sha256']: raise ValueError('Bound input changed: '+record['path'])
    base={'schema':'sealed-blind-review/v1','task_id':R,'plan_sha256':sha(planp),'derivation_path':str(derp),'derivation_sha256':sha(derp)}
    sealp=Path(contract['seal_path']);relp=Path(contract['release_path'])
    if args.action=='seal':
        if args.published_commit: raise ValueError('seal takes no commit.')
        save(sealp,dict(base,recorded_at=stamp_after(der['generated_at'])))
        print(json.dumps({'seal':str(sealp),'sha256':sha(sealp),'next':'Root publish exact derivation.md/json and seal, then release --published-commit FULL_SHA.'}));return
    if not args.published_commit: raise ValueError('A published full commit is required.')
    commit=git('rev-parse',args.published_commit+'^{commit}').decode().strip()
    if commit!=args.published_commit or len(commit)!=40: raise ValueError('Use exact full commit SHA.')
    seal=obj(sealp)
    if any(seal.get(k)!=v for k,v in base.items()): raise ValueError('Seal bytes/input binding changed.')
    paths=[md,derp,sealp,planp]
    records=[]
    for p in paths:
        b=git('show',commit+':'+str(p))
        if b!=p.read_bytes(): raise ValueError('content_at_commit mismatch: '+str(p))
        records.append({'path':str(p),'sha256':sha_bytes(b),'bytes':len(b)})
    parent=git('rev-parse',commit+'^').decode().strip()
    custody={'schema':'prime-active-support-blind-phase-custody/v1','task_id':R,'observed_at':stamp_after(seal['recorded_at']),'commit_sha':commit,'parent_sha':parent,'path_bindings':records,'content_at_commit_verified':True,'publication':'Root-supplied published commit; this helper verifies Git content, not remote-host identity or push timing.','final_ledger_archive_complete':False,'native_claim_completion':False}
    save(D/'phase-custody.json',custody)
    release=dict(base,recorded_at=stamp_after(custody['observed_at']),seal_path=str(sealp),seal_sha256=sha(sealp))
    save(relp,release)
    print(json.dumps({'release':str(relp),'sha256':sha(relp),'recorded_at':release['recorded_at'],'custody':str(D/'phase-custody.json'),'custody_sha256':sha(D/'phase-custody.json'),'warning':'Publish custody/release before notifying reviewer; no scientific hint.'}))
if __name__=='__main__': main()
