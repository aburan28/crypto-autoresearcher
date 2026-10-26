"""Fixed implementation checks, not a prospective performance trial."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import sympy
import divisor as d

HERE = Path(__file__).resolve().parent

def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    start, cpu = time.perf_counter(), time.process_time()
    started = datetime.now(timezone.utc).isoformat()
    assert d.on_curve(d.G) and d.mul(d.r) is None
    assert sympy.Poly(d.x**3+d.a*d.x+d.b, d.x, modulus=d.p).is_irreducible
    points = {i: d.mul(i) for i in range(-210, 211)}
    cases = []
    def case(name, F, provenance, anchors=()):
        c = d.divisor(F)
        c.update(id=name, provenance=provenance, declared_anchors=[list(P) for P in anchors])
        cases.append(c)
        write(out/(name+'.json'), c)
        return c
    line = lambda i, j: d.line(points[i], points[j])
    para = lambda *indices: d.parabola([points[i] for i in indices])
    # All of the following split inputs are hand-arranged correctness fixtures.
    constructed = []
    for name, F, anchor_indices in [
        ('pole3', line(3,12), [3,12]), ('pole4', para(3,4,5), [3,4,5]),
        ('pole5', d.function_product(line(2,-2), line(3,12)), [2,-2,3,12]),
        ('pole6', d.function_product(line(1,2), line(4,5)), [1,2,4,5]),
        ('pole7', d.function_product(line(1,2), para(1,4,7)), [1,2,1,4,7]),
        ('pole8', d.function_product(para(3,4,5), para(1,4,7)), [3,4,5,1,4,7]),
        ('tangent', line(1,1), [1,1]), ('inverse_only', line(2,-2), [2,-2])]:
        constructed.append(case(name, F, 'hand-arranged split correctness case',
                                [points[i] for i in anchor_indices]))
    assert [c['pole_order'] for c in constructed[:6]] == list(range(3,9))
    assert all(c['fully_rational'] for c in constructed)
    # Deterministic coefficient samples check extraction, not empirical success.
    sampled = []
    controls = []
    for m, anchor_indices, seed in [(3,[],4100), (4,[3],4101),
                                    (5,[2,-2],4102), (6,[3,4],4103),
                                    (7,[3,4,5],4104), (8,[3,4],4105)]:
        anchors = [points[i] for i in anchor_indices]
        F, control = d.conditioned_sampler(m, anchors, seed)
        c = case('coefficient_m'+str(m), F, 'fixed uniform-kernel coefficient implementation check', anchors)
        control['case'] = c['id']
        sampled.append(c)
        controls.append(control)
    # One-outside-point edges to the hub. 15G is excluded from the base.
    base = {d.orbit(points[i])[0] for i in range(1,13)}
    one = []
    for i,j in [(3,12),(4,11),(5,10),(6,9),(7,8)]:
        one.append(case('one_'+str(i)+'_'+str(j), line(i,j), 'hand-arranged repeated outside point', [points[i],points[j]]))
    one.append(case('one_duplicate', line(12,3), 'deliberate duplicate relation', [points[12],points[3]]))
    one.append(case('one_inverse_augmented', d.function_product(line(2,-2),line(3,12)),
                    'deliberate inverse-pair augmentation; no new signed row', [points[i] for i in [2,-2,3,12]]))
    # Balanced signed cycle: oriented differences telescope at outside points.
    two = []
    for i,j in [(100,101),(101,103),(103,106),(106,100)]:
        two.append(case('two_'+str(i)+'_'+str(j), line(i,-j), 'hand-arranged oriented outside cycle', [points[i],points[-j]]))
    two.append(case('two_duplicate', line(-101,100), 'deliberate duplicate edge', [points[-101],points[100]]))
    # Odd cycle with same-sign endpoints: underlying graph cycle is insufficient.
    odd_base = {d.orbit(points[i])[0] for i in [201,203,204]}
    odd = [case('odd_'+str(i)+'_'+str(j), line(i,j), 'same-sign odd-cycle negative cancellation control', [points[i],points[j]])
           for i,j in [(100,101),(101,103),(103,100)]]
    graphs = {'one_outside': d.stitch(one, base), 'two_outside': d.stitch(two, base),
              'combined': d.stitch(one+two+constructed, base), 'unbalanced_triangle': d.stitch(odd, odd_base)}
    for name, graph in graphs.items():
        assert graph['dimension_identity_holds']
        graph['case_ids'] = ([c['id'] for c in one] if name == 'one_outside' else
                             [c['id'] for c in two] if name == 'two_outside' else
                             [c['id'] for c in odd] if name == 'unbalanced_triangle' else
                             [c['id'] for c in one+two+constructed])
        write(out/('graph_'+name+'.json'), graph)
    assert graphs['one_outside']['zero_cancelled_rows'] >= 2
    assert graphs['two_outside']['rank_after_cancellation'] == 1
    assert graphs['unbalanced_triangle']['kernel_dimension'] == 0
    negative = []
    for name, action in [('zero_function', lambda: d.divisor(([0],[0]))),
                         ('anchors_exhaust_space', lambda: d.conditioned_sampler(3,[points[i] for i in [1,2,4]],77)),
                         ('anchor_forces_lower_pole', lambda: d.conditioned_sampler(3,[points[2],points[-2]],78))]:
        try:
            action()
        except ValueError as error:
            negative.append({'case':name,'expected_rejection':str(error),'passed':True})
        else:
            raise AssertionError('expected rejection '+name)
    write(out/'sampling_controls.json', controls)
    write(out/'expected_rejections.json', negative)
    evidence = {'schema':'f4-implementation-check/v1', 'task':'TASK-20261025-ce1163',
                'scope':'fixed correctness fixtures; no performance or yield trial',
                'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),
                'command':[sys.executable]+sys.argv, 'cwd':os.getcwd(),
                'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                'dirty_tree':subprocess.check_output(['git','status','--porcelain=v1'],text=True).splitlines(),
                'python':sys.version,'platform':platform.platform(),'sympy':sympy.__version__,
                'sympy_ground_types':os.environ.get('SYMPY_GROUND_TYPES','auto'),
                'p':d.p,'a':d.a,'b':d.b,'r':d.r,'generator':d.G,
                'parameters_sha256':hashlib.sha256(d.PARAMETERS.read_bytes()).hexdigest(),
                'sources_sha256':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['divisor.py','validate.py']},
                'construction_scalars':'public small multiples, correctness only, not hidden from generation',
                'divisor_cases':len(cases),'fully_rational_cases':sum(c['fully_rational'] for c in cases),
                'unresolved_cases':sum(bool(c['unresolved']) for c in cases),
                'pole_orders_checked':sorted(set(c['pole_order'] for c in cases)),
                'expected_rejections':len(negative),'failures':[],
                'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,
                'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                'graph_ranks':{k:{name:v[name] for name in ['input_rows','rank_before_all_columns',
                    'rank_projected_base_before_cancellation','outside_incidence_rank','kernel_dimension',
                    'rank_after_cancellation','zero_cancelled_rows']} for k,v in graphs.items()},
                'status':'passed'}
    write(out/'receipt.json', evidence)
    print(json.dumps({k:evidence[k] for k in ['status','divisor_cases','fully_rational_cases',
                     'unresolved_cases','pole_orders_checked','graph_ranks','wall_seconds']},indent=2))

if __name__ == '__main__':
    main()
