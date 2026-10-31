"""Validate a prospective prefix-adapter software queue; only root may invoke --apply."""
import argparse, copy, hashlib, json, sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R))
from tools import research_dispatch as rd
from tools import validate_ledger as vl
from tools import check_review_independence as cri
import yaml
C=Path(__file__).resolve().parent

def prepare():
    patch=json.loads((C/'queue-append.json').read_text())
    sources=json.loads((C/'source-inputs.json').read_text())
    mismatches=[p for p,h in sources['sources_sha256'].items() if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
    if mismatches: raise ValueError('Frozen source mismatch: '+repr(mismatches))
    qpath=R/patch['queue']; original=qpath.read_bytes(); q=json.loads(original)
    if next(t for t in q['tasks'] if t['id']=='TASK-20261029-5a7c65')['state']!='completed': raise ValueError('Prior completed archive state missing')
    existing={t['id']:t for t in q['tasks']}
    additions=patch['append_tasks']
    if any(t['id'] in existing for t in additions): raise ValueError('Task already present; refuse duplicate admission')
    candidate=copy.deepcopy(q);candidate['tasks'].extend(additions)
    taskmap=rd.validate_queue(candidate,repository_verifier=rd.GitRepositoryVerifier(R))
    assert isinstance(taskmap,dict)
    ctx=vl.Ctx(set())
    for t in additions:
        stage=C/'records/ledger/handoffs'/f"{t['id']}.yaml"
        vl.check_ledger_record(str(stage),'handoff',ctx)
        assert yaml.safe_load(stage.read_text())['handoff']==t['handoff']
    if ctx.errors: raise ValueError('Handoff errors: '+repr(ctx.errors))
    plan=yaml.safe_load((C/'review-plan.yaml').read_text())['review_plan']
    missing=cri.check(plan,[])
    unexpected=[s for s in missing if 'filed no review_attestation' not in s]
    if unexpected: raise ValueError('Unexpected plan errors: '+repr(unexpected))
    return patch,qpath,original,candidate,ctx,missing

def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--check',action='store_true');g.add_argument('--apply',action='store_true');args=ap.parse_args()
    patch,qpath,original,candidate,ctx,missing=prepare()
    if args.apply:
        assert qpath.read_bytes()==original,'Queue changed during validation'
        for t in patch['append_tasks']:
            target=R/'ledger/handoffs'/f"{t['id']}.yaml"
            if target.exists():raise ValueError('Refuse existing canonical handoff '+str(target))
        for t in patch['append_tasks']:
            target=R/'ledger/handoffs'/f"{t['id']}.yaml"
            with target.open('xb') as f:f.write((C/'records/ledger/handoffs'/target.name).read_bytes())
        qpath.write_text(json.dumps(candidate,indent=2)+'\n')
    print(json.dumps({'queue_errors':[],'handoff_errors':ctx.errors,'handoff_advisories':ctx.advisories,'expected_missing_review_attestations':missing,'unexpected_plan_errors':[],'frozen_input_hash_mismatches':[],'applied':args.apply,'tasks':[t['id'] for t in patch['append_tasks']],'scientific_runs':0,'software_tests_executed':0},indent=2))

if __name__=='__main__': main()
