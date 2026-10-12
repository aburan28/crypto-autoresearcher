#!/usr/bin/env python3
"""Freeze synthetic point pairs and record signed-square eligibility; no lift search."""
import hashlib, itertools, json, random
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def main():
    raw=(ROOT/'parameters.json').read_bytes(); pms=json.loads(raw)
    rng=random.Random(pms['seed']); records=[]; cells=0
    for p in pms['primes']:
        assert p>2 and all(p%d for d in range(2,int(p**0.5)+1))
        A=pms['source_curve']['A']; B=pms['source_curve']['B']
        assert (16*B*B*(A*A-4*B))%p
        points=[(x,y) for x in range(1,p) for y in range(1,p) if (y*y-x*(x*x+A*x+B))%p==0]
        pairs=[(P,Q) for P,Q in itertools.product(points,repeat=2) if P[0]!=Q[0]]
        chosen=rng.sample(pairs,pms['pairs_per_prime'])
        for i,(P,Q) in enumerate(chosen):
            arms=[]
            for signs in pms['sign_patterns']:
                reps=[[t for t in range(1,pms['positive_t_max']+1) if (sign*t*t-point[0])%p==0][:pms['t_representatives_per_point']] for sign,point in zip(signs,(P,Q))]
                count=len(reps[0])*len(reps[1])*(pms['ordinate_shift_max']-pms['ordinate_shift_min']+1)**2
                cells+=count
                arms.append(dict(signs=signs,t_representatives=reps,proposal_cells=count))
            records.append(dict(id=f'p{p}-pair{i:02}',p=p,P=P,Q=Q,quadratic_character_x=[1 if pow(point[0],(p-1)//2,p)==1 else -1 for point in (P,Q)],arms=arms))
    assert len(records)==32 and cells<=pms['budget']['maximum_proposal_cells']
    result=dict(schema='xedni-frozen-targets-v1',parameters_sha256=hashlib.sha256(raw).hexdigest(),seed=pms['seed'],pairs=records,actual_eligible_proposal_cells=cells,selection='Targets fixed before fitting; no relation labels used.',status='frozen_design_inputs_not_a_scientific_run')
    (ROOT/'targets.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(pair_count=len(records),eligible_proposal_cells=cells,ineligible_sign_arms=sum(a['proposal_cells']==0 for r in records for a in r['arms']),target_sha256=hashlib.sha256((ROOT/'targets.json').read_bytes()).hexdigest()),indent=2))

if __name__=='__main__': main()
