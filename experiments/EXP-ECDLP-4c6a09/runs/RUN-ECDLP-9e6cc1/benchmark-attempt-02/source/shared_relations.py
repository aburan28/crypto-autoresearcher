#!/usr/bin/env python3
"""Share learned factor-base information across the same frozen target batch."""
import hashlib
import json
import platform
import shutil
import time
from collections import Counter
from pathlib import Path

from benchmark import build_table, scalar_table, measured, point_list, sha_value
from finite_math import Curve, Relations, split_coefficients
from gp_tables import write

RUN = Path(__file__).resolve().parent.parent
OLD = RUN/'benchmark-attempt-01'

def solve_batch(public, seeds, known, built, targets, width, cap):
    """No synthetic truth or hidden seed scalar is an argument."""
    start_cpu,start_wall = time.process_time(),time.perf_counter()
    ec,verify = Curve(public['p'],public['A'],public['B']),Curve(public['p'],public['A'],public['B'])
    ell,g = public['ell'],tuple(public['G'])
    unknown_count = len(seeds)-len(known)
    space = Relations(ell,unknown_count+len(targets))
    for row in built['space'].rows.values():
        space.add(row[:-1]+[0]*len(targets),row[-1])
    before = space.rank
    space.count.clear()
    jump = ec.mul(g,-(width%ell))
    witness,out = [],[]
    for ti,target in enumerate(targets):
        q = tuple(target['point'])
        functional = [0]*space.dimension
        functional[unknown_count+ti] = 1
        point,hits,resolved_when_stopped = q,0,False
        count_before = Counter(ec.count)
        relations_before = space.rank
        for probe in range(cap):
            if point in built['table']:
                hits += 1
                coefficients = built['table'][point]
                u,constant = split_coefficients(coefficients,known)
                row = u+[0]*len(targets)
                row[unknown_count+ti] = -1
                rhs = -probe*width-constant
                if space.add(row,rhs):
                    checkpoint = verify.combination(seeds,coefficients)
                    assert checkpoint==verify.add(q,verify.mul(g,-(probe*width%ell)))
                    witness.append({'target_id':target['id'],'probe':probe,'coefficients':list(coefficients),
                                    'equation_coefficients':row,'rhs':rhs%ell,'global_rank_after':space.rank})
                value = space.value(functional)
                if value is not None:
                    resolved_when_stopped = True
                    break
            if probe+1<cap:
                point = ec.add(point,jump)
        out.append({'target_id':target['id'],'probes':probe+1,'hits':hits,
                    'query_operations':dict(Counter(ec.count)-count_before),
                    'new_independent_global_relations':space.rank-relations_before,
                    'resolved_when_query_stopped':resolved_when_stopped})
    for ti,(target,result) in enumerate(zip(targets,out,strict=True)):
        functional = [0]*space.dimension
        functional[unknown_count+ti] = 1
        value = space.value(functional)
        result.update({'recovered_scalar':value,'resolved_at_batch_end':value is not None,
                       'recovered_retroactively':value is not None and not result['resolved_when_query_stopped']})
        if value is not None:
            assert verify.mul(g,value)==tuple(target['point'])
    return {'targets':out,'useful_relation_witnesses':witness,'independent_factorbase_relations':before,
            'new_independent_batch_relations':space.rank-before,'global_relation_rank':space.rank,
            'global_relation_columns':space.dimension,'generator_unknown_count':unknown_count,
            'query_operations':dict(ec.count),'relation_algebra_operations':dict(space.count),
            'verification_operations':dict(verify.count),
            'query_timing':{'cpu_seconds':time.process_time()-start_cpu,'wall_seconds':time.perf_counter()-start_wall}}

def main():
    stage = RUN/'benchmark-shared-attempt-01'
    stage.mkdir(exist_ok=False)
    (stage/'source').mkdir()
    for name in ['shared_relations.py','benchmark.py','finite_math.py','gp_tables.py','curve_identity.py']:
        shutil.copy2(RUN/'source'/name,stage/'source'/name)
    write(stage/'launch.json',{'command_argv':['python3',str(Path(__file__).resolve())],
                              'python':platform.python_version(),
                              'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (stage/'source').iterdir()},
                              'addendum_sha256':hashlib.sha256((RUN/'shared-relations-plan.json').read_bytes()).hexdigest()})
    frozen = json.loads((OLD/'raw-result.json').read_text())
    public_targets = json.loads((OLD/'targets-public.json').read_text())
    truth = json.loads((OLD/'validation/synthetic-truth.json').read_text())
    true_scalars = {t['id']:t['synthetic_scalar'] for t in truth if 'synthetic_scalar' in t}
    groups = {g['identity']['curve_uid']:g for g in frozen['public_groups']}
    results = []
    start = time.perf_counter()
    for previous in frozen['methods']:
        public = groups[previous['curve_uid']]
        targets = [t for t in public_targets if t['curve_uid']==previous['curve_uid']]
        seeds = [None if p is None else tuple(p) for p in previous['seeds']]
        known = {int(i):int(v) for i,v in previous['known_seed_logs'].items()}
        build_ec = Curve(public['p'],public['A'],public['B'])
        if previous['arm'].startswith('bsgs'):
            built,timing = measured(lambda:scalar_table(build_ec,seeds[0],previous['table_entries_requested'],public['ell']))
        else:
            built,timing = measured(lambda:build_table(build_ec,seeds,previous['bound'],known,public['ell']))
            assert sha_value(built['rows'])==previous['factorbase_table_sha256']
        assert len(built['table'])==previous['distinct_subgroup_points']
        assert dict(build_ec.count)==previous['table_build_operations']
        solved = solve_batch(public,seeds,known,built,targets,previous['table_entries_requested'],previous['query_step_cap'])
        for result in solved['targets']:
            if result['resolved_at_batch_end']:
                assert result['recovered_scalar']==true_scalars[result['target_id']]
        total = Counter(build_ec.count)+Counter(solved['query_operations'])+Counter(previous['seed_setup']['operations'])
        recoveries = sum(r['resolved_at_batch_end'] for r in solved['targets'])
        rank = solved['global_relation_rank']
        record = {k:previous[k] for k in ['id','arm','A','B','k','p','ell','cofactor','curve_id','curve_uid',
                                         'seed_count','unknown_seed_count','table_entries_requested',
                                         'distinct_subgroup_points','subgroup_coverage_fraction',
                                         'table_point_set_sha256','seed_spec_id','seed_setup']}
        record.update({'sharing':'Factor-base constraints and learned seed logs shared across all 16 target systems',
                       'target_recoveries':recoveries,'target_count':len(targets),
                       'table_build_operations':dict(build_ec.count),'table_build_timing':timing,
                       'total_algorithm_operations':dict(total),
                       'useful_relations_per_1000_group_calls':rank*1000/max(1,total['group_calls']),
                       'recoveries_per_1000_group_calls':recoveries*1000/max(1,total['group_calls']),
                       'total_build_query_cpu_seconds':timing['cpu_seconds']+solved['query_timing']['cpu_seconds'],
                       'batch_result':solved})
        results.append(record)
        if previous['arm'] in ['solinas','rational','pure_cubic','random_low_weight','bsgs_sqrt']:
            print('SHARED',record['id'],'solved',recoveries,'rank',rank,
                  'ops',total['group_calls'],'cpu',record['total_build_query_cpu_seconds'],flush=True)
    for m in results:
        if m['arm']=='bsgs_sqrt':
            assert m['target_recoveries']==16
        if m['arm']=='isomorphic_sign_control':
            original = next(o for o in results if o['id']==m['id'].replace('isomorphic_sign_control','solinas'))
            assert original['target_recoveries']==m['target_recoveries']
            assert original['total_algorithm_operations']==m['total_algorithm_operations']
            assert original['batch_result']['global_relation_rank']==m['batch_result']['global_relation_rank']
    write(stage/'raw-result.json',{'methods':results,'prior_run':str(OLD.relative_to(RUN)),
                                 'actual_scope':{'methods':len(results),'unique_targets':len(public_targets),
                                                 'matched_curve_prime_cohorts':6,'target_count_per_cohort':16},
                                 'elapsed_seconds':time.perf_counter()-start,
                                 'validation':{'all_recovered_scalars_correct':True,'all_relation_witnesses_checked':True,
                                               'all_isomorphic_controls_agree':True,'all_baseline_sqrt_targets_recovered':True,
                                               'all_global_ranks_bounded_by_unknowns_plus_targets':True}})
    print('FINISHED_SHARED',len(results),time.perf_counter()-start,flush=True)

if __name__=='__main__':
    main()
