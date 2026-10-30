"""Validate staged design admission; --apply is reserved for root."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
import yaml
R=Path(__file__).resolve().parents[2]; C=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from tools import research_dispatch as rd
from tools import validate_ledger as vl

def prepare():
    patch=json.loads((C/'queue-append.json').read_text())
    bindings=json.loads((C/'source-inputs.json').read_text())['sources_sha256']
    for p,h in bindings.items():
        if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h:raise ValueError('Input changed: '+p)
    qpath=R/patch['queue']; original=qpath.read_bytes(); q=json.loads(original)
    prior=next(t for t in q['tasks'] if t['id']=='TASK-20261030-2e1cb1')
    if prior['state']!='completed':raise ValueError('Prior archive terminal state mismatch')
    if q['max_concurrent']!=1:raise ValueError('Serial queue capacity changed')
    existing={t['id'] for t in q['tasks']}
    if existing & {t['id'] for t in patch['append_tasks']}:raise ValueError('Refuse duplicate task admission')
    candidate=copy.deepcopy(q);candidate['tasks'].extend(patch['append_tasks'])
    result=rd.validate_queue(candidate,repository_verifier=rd.GitRepositoryVerifier(R))
    if not isinstance(result,dict):raise ValueError('Unexpected native validator return')
    ctx=vl.Ctx(set())
    for t in patch['append_tasks']:
        stage=C/'records/ledger/handoffs'/f"{t['id']}.yaml"
        vl.check_ledger_record(str(stage),'handoff',ctx)
        if yaml.safe_load(stage.read_text())['handoff']!=t['handoff']:raise ValueError('Staged handoff differs')
    if ctx.errors:raise ValueError('Handoff schema errors: '+repr(ctx.errors))
    return patch,qpath,original,candidate,ctx

def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--check',action='store_true');g.add_argument('--apply',action='store_true');a=ap.parse_args()
    patch,qpath,old,candidate,ctx=prepare()
    if a.apply:
        if qpath.read_bytes()!=old:raise ValueError('Queue changed during validation')
        for t in patch['append_tasks']:
            if (R/'ledger/handoffs'/f"{t['id']}.yaml").exists():raise ValueError('Canonical handoff exists')
        for t in patch['append_tasks']:
            name=f"{t['id']}.yaml";target=R/'ledger/handoffs'/name
            with target.open('xb') as f:f.write((C/'records/ledger/handoffs'/name).read_bytes())
        qpath.write_text(json.dumps(candidate,indent=2)+'\n')
    print(json.dumps({'schema':'prime-prefix-search-design-preflight/v1','applied':a.apply,'queue_errors':[],'handoff_errors':ctx.errors,'handoff_advisories':ctx.advisories,'input_hash_mismatches':[],'tasks':[t['id'] for t in patch['append_tasks']],'scientific_execution_authorized':False,'solver_instantiated':False},indent=2))

if __name__=='__main__':main()
