#!/usr/bin/env python3
"""Measure new seeded number fields with the unchanged public-target solver."""
import hashlib
import json
import shutil
import statistics
import time
from collections import Counter
from pathlib import Path

from benchmark import build_table, known_seed_logs, measured, point_list, sha_value
from finite_math import Curve, grid_points
from gp_tables import write
from shared_relations import solve_batch

RUN=Path(__file__).resolve().parent.parent
PREP=RUN/'point-preparation-attempt-01'

def main():
    stage=RUN/'benchmark-attempt-01'
    stage.mkdir(exist_ok=False)
    (stage/'methods').mkdir()
    (stage/'source').mkdir()
    for name in ['benchmark_random_fields.py','shared_relations.py','benchmark.py','finite_math.py']:
        shutil.copy2(RUN/'source'/name,stage/'source'/name)
    write(stage/'launch.json',{'command_argv':['python3',str(Path(__file__).resolve())],
                             'plan_sha256':hashlib.sha256((RUN/'plan.json').read_bytes()).hexdigest(),
                             'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (stage/'source').iterdir()}})
    prior=json.loads((RUN/'inputs/prior-cold-result.json').read_text())
    public_groups=prior['public_groups']
    groups={(g['A'],g['B'],g['k']):g for g in public_groups}
    targets=json.loads((RUN/'inputs/targets-public.json').read_text())
    truth={t['id']:t['synthetic_scalar'] for t in json.loads((RUN/'inputs/synthetic-truth.json').read_text()) if 'synthetic_scalar' in t}
    specs=json.loads((PREP/'seed-specs.json').read_text())
    fields=json.loads((RUN/'sampling-result.json').read_text())['fields']
    prep=json.loads((PREP/'result.json').read_text())
    missing=[{'spec_id':o['id'],'reason':'Point preparation failed','detail':o.get('error')} for o in prep['outcomes'] if o['status']!='complete']
    methods=[]
    start=time.monotonic()
    for spec in sorted(specs,key=lambda s:s['id']):
        exact=json.loads((PREP/'exact-grids'/spec['id']/'tables.json').read_text()) if any(r['eligible'] for r in spec['reductions'].values()) else None
        for kj,red in spec['reductions'].items():
            public=groups[(spec['A'],spec['B'],red['k'])]
            for key in ['p','group_order','ell','cofactor','G']:assert red[key]==public[key]
            if not red['eligible']:
                missing.append({'spec_id':spec['id'],'curve_uid':public['identity']['curve_uid'],'k':red['k'],'reason':'No degree-one prime over fixed p'})
                continue
            raw_seeds=[None if p is None else tuple(p) for p in red['seeds_full']]
            validation_ec=Curve(public['p'],public['A'],public['B'])
            actual=[point_list(p) for _,p in grid_points(validation_ec,raw_seeds,4)]
            oracle=exact['tables'][f'4:{kj}']
            assert actual==oracle
            proj=Curve(public['p'],public['A'],public['B'])
            seeds,setup_timing=measured(lambda:[proj.mul(p,public['cofactor']) for p in raw_seeds])
            known=known_seed_logs(seeds,tuple(public['G']))
            for i,p in enumerate(seeds):
                if p==proj.neg(tuple(public['G'])):known[i]=-1
            timing_reps=[]
            op_reps=[]
            for rep in range(3):
                ec=Curve(public['p'],public['A'],public['B'])
                built,timing=measured(lambda:build_table(ec,seeds,4,known,public['ell']))
                timing_reps.append(timing)
                op_reps.append(dict(ec.count))
            assert all(op_reps[0]==x for x in op_reps)
            chosen_targets=[t for t in targets if t['curve_uid']==public['identity']['curve_uid']]
            solved=solve_batch(public,seeds,known,built,chosen_targets,len(actual),32768)
            for result in solved['targets']:
                if result['resolved_at_batch_end']:assert result['recovered_scalar']==truth[result['target_id']]
            total=Counter(proj.count)+Counter(ec.count)+Counter(solved['query_operations'])
            recoveries=sum(r['resolved_at_batch_end'] for r in solved['targets'])
            rank=solved['global_relation_rank']
            assert rank<=solved['global_relation_columns']
            record={'id':spec['id']+f'-k{red["k"]}','arm':'random_cubic','field_id':spec['field'],
                    'g':spec['g'],'canonical_polynomial_gp':spec['canonical_polynomial_gp'],
                    'field_discriminant':spec['field_discriminant'],'draw_seed':spec['draw_seed'],
                    'A':public['A'],'B':public['B'],'k':public['k'],'p':public['p'],'ell':public['ell'],
                    'cofactor':public['cofactor'],'curve_uid':public['identity']['curve_uid'],
                    'curve_id':public['identity']['curve_id'],'seed_spec_id':spec['id'],
                    'seed_count':len(seeds),'rank_bounds':spec['rank_bounds'],'rank_status':spec['rank_status'],
                    'seed_discovery_available':spec['seed_discovery_available'],
                    'unknown_seed_count':len(seeds)-len(known),'known_seed_logs':known,
                    'seeds':[point_list(p) for p in seeds],'bound':4,
                    'table_entries_requested':len(actual),'distinct_full_group_points':len({None if p is None else tuple(p) for p in actual}),
                    'distinct_subgroup_points':len(built['table']),
                    'subgroup_coverage_fraction':len(built['table'])/public['ell'],
                    'coverage_per_build_group_call':len(built['table'])/max(1,ec.count['group_calls']),
                    'factorbase_collisions':built['collision_count'],
                    'factorbase_table_sha256':sha_value(built['rows']),
                    'table_point_set_sha256':sha_value(sorted([point_list(p) for p in built['table']],key=lambda v:(-1,-1) if v is None else tuple(v))),
                    'factorbase_relation_witnesses':built['witnesses'],
                    'table_build_operations':dict(ec.count),'table_build_timing_repetitions':timing_reps,
                    'cached_build_cpu_median_seconds':statistics.median(t['cpu_seconds'] for t in timing_reps),
                    'seed_projection_operations':dict(proj.count),'seed_projection_timing':setup_timing,
                    'rank_discovery_elapsed_seconds':spec['rank_seed_discovery_elapsed_seconds'],
                    'NF_timings':exact['timings'],'exact_grid_process':exact['process'],
                    'target_count':len(chosen_targets),'target_recoveries':recoveries,
                    'query_step_cap':32768,'total_algorithm_operations':dict(total),
                    'useful_relations_per_1000_group_calls':rank*1000/max(1,total['group_calls']),
                    'recoveries_per_1000_group_calls':recoveries*1000/max(1,total['group_calls']),
                    'batch_result':solved,'exact_K_vs_cached_agree':True,
                    'all_recovered_target_scalars_correct':True}
            write(stage/'methods'/(record['id']+'.json'),record)
            methods.append(record)
            print('METHOD',record['id'],'seeds',len(seeds),'D',len(built['table']),
                  'recovered',recoveries,'rank',rank,'calls',total['group_calls'],flush=True)
    assert len(methods)+sum(m['reason']=='No degree-one prime over fixed p' for m in missing)+3*sum(m['reason']=='Point preparation failed' for m in missing)==144
    write(stage/'raw-result.json',{'run_id':RUN.name,'methods':methods,'unavailable':missing,
          'public_groups':public_groups,'actual_scope':{'distinct_random_fields':len(fields),
          'field_model_pairs':len(prep['outcomes']),'planned_cohorts':144,'completed_cohorts':len(methods),
          'unique_target_points':len(targets),'target_count_per_cohort':16},
          'elapsed_seconds':time.monotonic()-start,
          'validation':{'all_exact_K_grids_agree_with_cached_reductions':True,
                        'all_recovered_target_scalars_correct':True,'all_relation_witnesses_checked':True,
                        'same_public_groups_and_targets_as_prior_run':True}})
    print('FINISHED_RANDOM_FIELDS',len(methods),'completed',len(missing),'unavailable',round(time.monotonic()-start,3),flush=True)

if __name__=='__main__':main()
