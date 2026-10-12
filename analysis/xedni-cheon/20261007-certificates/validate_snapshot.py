#!/usr/bin/env python3
"""Scoped repo-schema, immutable-import and frozen-target checks; no trial."""
import hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
sys.path.insert(0,str(REPO/'tools'))
import validate_ledger as v

def main():
    ctx=v.Ctx(set())
    records=[('questions','RQ-XEDN-3bfe2e'),('hypotheses','H-XEDN-0ea2b6'),('hypotheses','H-XEDN-4a5b50'),('handoffs','TASK-20261007-af0dee')]
    for folder,identifier in records:
        v.check_ledger_record(str(REPO/'ledger'/folder/(identifier+'.yaml')),v.LEDGER_DIRS[folder],ctx)
    v.check_cross_refs(ctx)
    if ctx.errors: raise ValueError(ctx.errors)
    provenance=json.loads((ROOT/'imported/provenance.json').read_text())
    for name,expected in provenance['file_sha256'].items():
        assert hashlib.sha256((ROOT/'imported'/name).read_bytes()).hexdigest()==expected,name
    p=json.loads((ROOT/'parameters.json').read_text()); t=json.loads((ROOT/'targets.json').read_text())
    assert t['parameters_sha256']==hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest()
    assert len(t['pairs'])==32
    seen=set(); total=0
    for pair in t['pairs']:
        prime=pair['p']; P,Q=pair['P'],pair['Q']; key=(prime,tuple(P),tuple(Q))
        assert key not in seen and P[0]!=Q[0]; seen.add(key)
        for x,y in [P,Q]: assert (y*y-x*(x*x-x+16))%prime==0
        for arm in pair['arms']:
            total+=arm['proposal_cells']
            for sign,point,reps in zip(arm['signs'],[P,Q],arm['t_representatives']):
                expected=[z for z in range(1,65) if (sign*z*z-point[0])%prime==0][:4]
                assert reps==expected
    assert total==t['actual_eligible_proposal_cells']<=p['budget']['maximum_proposal_cells']
    print(json.dumps(dict(status='passed',scoped_record_count=4,imported_historical_hash_count=len(provenance['file_sha256']),target_pair_count=32,eligible_proposal_cells=total,scientific_followup_runs=0,independent_scientific_review=False),indent=2))

if __name__=='__main__': main()
