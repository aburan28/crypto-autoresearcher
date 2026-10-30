"""Run fixed correctness controls, preserving each invocation under receipts/NAME."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import labelled as L

HERE=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--receipt',required=True)
    args=parser.parse_args(); out=HERE/'receipts'/args.receipt
    out.mkdir(parents=True,exist_ok=False)
    started=datetime.now(timezone.utc).isoformat(); t=time.monotonic()
    checks=[]; files=[]
    def check(name, condition):
        checks.append(dict(name=name,passed=bool(condition)))
        if not condition: raise AssertionError(name)
    def rejected(name, fn):
        try: fn()
        except (ValueError,IndexError) as exc:
            checks.append(dict(name=name,passed=True,rejection=str(exc))); return
        check(name,False)
    def save(name,data):
        f=out/name; f.write_text(json.dumps(data,indent=2)+'\n'); files.append(name)
    parts=[list(range(i*8,(i+1)*8)) for i in range(3)]
    check('generator_on_curve',L.on_curve(L.G))
    check('generator_order_divides_r',L.mul(L.r,L.G) is None)
    Qnatural, increments=L.hash_point('F3 public P-256 unknown-log target 20261025')
    d=L.scalar('F3 public constructed fixture witness 20261025')
    Qfixture=L.mul(d,L.G)
    cases=[]
    for name,Q in [('natural_random',Qnatural),('arranged_zero_Q',Qnatural),
                   ('arranged_useful',Qfixture)]:
        base,ledger=L.random_base(Q,tag=name)
        if name=='arranged_zero_Q':
            # Uses additions of label vectors only: necessarily A=B=0.
            base[23]=L.record(-base[0]['a']-base[8]['a'],
                              -base[0]['b']-base[8]['b'],Q)
            ledger['replacement_label_point_evaluations']=1
        elif name=='arranged_useful':
            B=(base[0]['b']+base[8]['b']+base[23]['b']) % L.r
            check('arranged_target_coefficient_nonzero',B!=0)
            base[23]=L.record(-base[0]['a']-base[8]['a']-d*B,base[23]['b'],Q)
            ledger['replacement_label_point_evaluations']=1
            ledger['fixture_only_known_log_multiplications']=1
        points=[z['point'] for z in base]
        for i,z in enumerate(base):
            check(f'{name}_label_{i}',L.on_curve(z['point']) and
                  L.label_point(z['a'],z['b'],Q)==z['point'])
        check(f'{name}_target_valid',L.on_curve(Q) and L.mul(L.r,Q) is None)
        searched=L.aps3_search(points,parts)
        exhaustive=L.exhaustive3(points,parts)
        check(f'{name}_hybrid_matches_complete_group_search',
              searched['relations']==exhaustive['relations'])
        assessed=[L.assess(base,Q,z) for z in searched['relations']]
        if name=='natural_random': check('natural_useful_count_recorded',len(assessed)==0)
        elif name=='arranged_zero_Q':
            check('arranged_label_dependency_zero_Q',len(assessed)==1 and
                  assessed[0]['A']==assessed[0]['B']==0 and not assessed[0]['useful'])
        else:
            check('arranged_useful_recovery',len(assessed)==1 and assessed[0]['useful']
                  and assessed[0]['recovered']==d)
        polys=[L.vanishing_poly([points[i][0] for i in part]) for part in parts]
        case=dict(name=name,Q=Q,base=base,partitions=parts,construction=ledger,
                  hybrid=searched,exhaustive=exhaustive,assessments=assessed,
                  membership_polynomials_ascending=polys)
        if name=='arranged_useful':
            case['fixture_only_generation_witness']=d
            case['witness_access']='generation and expected-output check only; search called with points,partitions'
        if name=='natural_random': case['hash_to_point_increments']=increments
        save(name+'.json',case); cases.append(case)
    z=cases[1]['base'][0]; Q=Qnatural
    inv=[deepcopy(z),L.record(-z['a'],-z['b'],Q)]
    invrel=dict(indices=[0,1],signs=[1,1])
    inverse=L.assess(inv,Q,invrel)
    check('inverse_pair_not_useful',inverse['point_sum_zero'] and inverse['B']==0
          and inverse['repeated_x'] and not inverse['useful'])
    repeated=L.assess(inv,Q,dict(indices=[0,0],signs=[1,-1]))
    check('same_index_cancellation_not_useful',repeated['point_sum_zero'] and
          repeated['A']==repeated['B']==0 and repeated['repeated_index'])
    rejected('inverse_coordinates_rejected_by_search',lambda:L.aps3_search(
        [x['point'] for x in inv],[[0],[1],[]]))
    bad=deepcopy(cases[2]['base']); bad[0]['a']=(bad[0]['a']+1)%L.r
    rejected('mutated_label_rejected',lambda:L.assess(bad,Qfixture,
             dict(indices=[0,8,23],signs=[1,1,1])))
    bad=deepcopy(cases[2]['base']); bad[0]['point']=(0,0)
    rejected('off_curve_point_rejected',lambda:L.assess(bad,Qfixture,
             dict(indices=[0,8,23],signs=[1,1,1])))
    rejected('off_curve_target_rejected',lambda:L.assess(cases[2]['base'],(0,0),
             dict(indices=[0,8,23],signs=[1,1,1])))
    not_relation=L.assess(cases[2]['base'],Qfixture,
                          dict(indices=[0,8,23],signs=[1,1,-1]))
    check('wrong_sign_is_not_relation',not not_relation['point_sum_zero'])
    check('quadratic_linear_branch',L.quadratic_roots(0,1,1)[0]==[L.p-1])
    check('quadratic_nonzero_constant',L.quadratic_roots(0,0,1)[0]==[])
    check('quadratic_repeated_root',L.quadratic_roots(1,0,0)[0]==[0])
    check('quadratic_nonsquare_branch',L.quadratic_roots(1,0,1)[0]==[])
    rejected('identically_zero_polynomial_not_empty',lambda:L.quadratic_roots(0,0,0))
    points=[x['point'] for x in cases[0]['base']]
    rejected('overlapping_partition_rejected',lambda:L.aps3_search(points,[[0],[0],list(range(1,24))]))
    save('degenerate_and_invalid.json',dict(inverse_base=inv,Q=Q,inverse=inverse,
         repeated_index=repeated,wrong_sign=not_relation))
    metadata=dict(schema='f3-implementation-checks/v1',task='TASK-20261025-1f3375',
        status='passed',scope='fixed P-256 arithmetic and algorithm correctness controls',
        scientific_performance_trial=False,started=started,
        finished=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-t,
        command=[sys.executable,*sys.argv],python=sys.version,platform=platform.platform(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        git_dirty_assigned_scope=subprocess.check_output(['git','status','--porcelain','--',str(HERE)],text=True),
        baseline_sha256=sha256(L.BASELINE.read_bytes()).hexdigest(),
        source_sha256={f:sha256((HERE/f).read_bytes()).hexdigest()
                       for f in ('labelled.py','validate.py')},
        check_count=len(checks),passed_checks=sum(c['passed'] for c in checks),checks=checks,
        cases={c['name']:dict(base_size=len(c['base']),hybrid=c['hybrid']['counts'],
           exhaustive_point_sum_checks=c['exhaustive']['point_sum_checks'],
           dependencies=len(c['assessments']),useful=sum(a['useful'] for a in c['assessments']),
           zero_Q=sum(a['point_sum_zero'] and a['B']==0 for a in c['assessments'])) for c in cases},
        artifacts={f:sha256((out/f).read_bytes()).hexdigest() for f in files})
    save('checks.json',metadata)
    print(json.dumps({k:metadata[k] for k in ('status','check_count','passed_checks','cases')},indent=2))

if __name__=='__main__': main()
