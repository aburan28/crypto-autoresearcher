#!/usr/bin/env python3
"""Matched public toy coverage, independent relations, and target recovery costs.

Target solvers receive points, coefficient representations, and public group
metadata only. Synthetic scalar truth is written separately and used after each
solver returns, never to derive a relation or decide a table hit.
"""
import hashlib
import json
import math
import platform
import random
import resource
import shutil
import statistics
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

from finite_math import Curve, Relations, grid_points, split_coefficients
from gp_tables import write
from curve_identity import curve_identity

RUN = Path(__file__).resolve().parent.parent
PREP = RUN / 'point-preparation-attempt-02'

def sha_value(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def point_list(point):
    return None if point is None else list(point)

def measured(function):
    wall, cpu = time.perf_counter(), time.process_time()
    result = function()
    return result, {'wall_seconds': time.perf_counter()-wall, 'cpu_seconds': time.process_time()-cpu}

def nf_multiply(a, b, g):
    v = [Fraction(0) for _ in range(5)]
    for i in range(3):
        for j in range(3):
            v[i+j] += a[i]*b[j]
    for i in (4, 3):
        for j in range(3):
            v[i-3+j] -= v[i]*g[j]
    return v[:3]

def exact_seed_check(spec):
    for coords in spec['seeds_coefficients']:
        x, y = [[Fraction(a,b) for a,b in c] for c in coords]
        xx = nf_multiply(x, x, spec['g'])
        xxx = nf_multiply(xx, x, spec['g'])
        yy = nf_multiply(y, y, spec['g'])
        assert all(yy[j] == xxx[j] + spec['A']*x[j] + (spec['B'] if j==0 else 0) for j in range(3))

def isomorphic_spec(spec):
    out = json.loads(json.dumps(spec))
    out.update({'id': spec['id'].replace('solinas', 'isomorphic_sign_control'),
                'field': 'isomorphic_sign_control', 'g': [1,-1,0,1],
                'transport': 'alpha=-beta, beta^3-beta+1=0; roots beta=-2^k'})
    for point in out['seeds_coefficients']:
        for coord in point:
            coord[1][0] *= -1
    exact_seed_check(out)
    for red in out['reductions'].values():
        red['root'] = (-2**red['k']) % red['p']
        reduced = []
        for point in out['seeds_coefficients']:
            values = [sum(a*pow(b,-1,red['p'])*pow(red['root'],j,red['p']) for j,(a,b) in enumerate(coord)) % red['p']
                      for coord in point]
            reduced.append(values)
        assert reduced == red['seeds_full']
    return out

def known_seed_logs(seeds, g):
    known = {}
    negative = None if g is None else (g[0], -g[1])
    for i, point in enumerate(seeds):
        if point is None:
            known[i] = 0
        elif point == g:
            known[i] = 1
    return known

def build_table(ec, seeds, bound, known, ell):
    table = {}
    space = Relations(ell, len(seeds)-len(known))
    collision_count, witnesses, rows = 0, [], []
    validation = Curve(ec.p, ec.a, ec.b)
    for coefficient, point in grid_points(ec, seeds, bound):
        rows.append([list(coefficient), point_list(point)])
        if point in table:
            previous = table[point]
            delta = [a-b for a,b in zip(coefficient, previous, strict=True)]
            collision_count += 1
            u, constant = split_coefficients(delta, known)
            if space.add(u, -constant):
                assert validation.combination(seeds, delta) is None
                witnesses.append({'coefficients': delta, 'unknown_coefficients': u,
                                  'rhs': -constant % ell, 'rank_after': space.rank})
        else:
            table[point] = coefficient
    return {'table': table, 'space': space, 'rows': rows, 'collision_count': collision_count,
            'witnesses': witnesses, 'validation_counts': dict(validation.count)}

def scalar_table(ec, g, requested, ell):
    size = min(requested, ell)
    table, point = {}, None
    for j in range(size):
        table[point] = (j,)
        if j+1<size:
            point = ec.add(point, g)
    return {'table': table, 'space': Relations(ell, 0), 'rows': None,
            'collision_count': 0, 'witnesses': [], 'validation_counts': {},
            'requested_size': requested, 'built_size': size}

def target_solver(public, seeds, known, built, target, step_size, cap):
    """Only public points and the table-derived relation basis enter this function."""
    ec = Curve(public['p'], public['A'], public['B'])
    validate = Curve(ec.p, ec.a, ec.b)
    g, ell = tuple(public['G']), public['ell']
    jump = ec.mul(g, -(step_size % ell))
    space = built['space'].with_target()
    target_functional = [0]*space.dimension
    target_functional[-1] = 1
    point, hits, witnesses, recovered, probe = target, 0, [], None, 0
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    for probe in range(cap):
        if point in built['table']:
            hits += 1
            coeff = built['table'][point]
            u, constant = split_coefficients(coeff, known)
            row, rhs = u+[-1], -probe*step_size-constant
            if space.add(row, rhs):
                reconstructed = validate.combination(seeds, coeff)
                right = validate.add(target, validate.mul(g, -(probe*step_size % ell)))
                assert reconstructed == right
                witnesses.append({'probe': probe, 'coefficients': list(coeff),
                                  'equation_unknown_coefficients': row, 'rhs': rhs % ell,
                                  'rank_after': space.rank})
            recovered = space.value(target_functional)
            if recovered is not None:
                assert validate.mul(g, recovered) == target
                break
        if probe+1 < cap:
            point = ec.add(point, jump)
    timing = {'wall_seconds': time.perf_counter()-start_wall, 'cpu_seconds': time.process_time()-start_cpu}
    return {'recovered_scalar': recovered, 'resolved': recovered is not None, 'probes': probe+1,
            'table_hits': hits, 'new_independent_target_equations': len(witnesses),
            'relation_rank_before': built['space'].rank, 'relation_rank_after': space.rank,
            'useful_witnesses': witnesses, 'operations': dict(ec.count),
            'relation_algebra_operations': dict(space.count), 'validation_operations': dict(validate.count),
            'timing': timing, 'censored_at_query_cap': recovered is None}

def summarize_method(public, identifier, arm, seeds, known, built, build_ec, timing, seed_setup,
                     targets, cap, step_size, seed_spec=None, bound=None):
    results = []
    for target in targets:
        r = target_solver(public, seeds, known, built, tuple(target['point']), step_size, cap)
        r['target_id'] = target['id']
        results.append(r)
    query_counts = Counter()
    validation_counts = Counter(built['validation_counts'])
    for r in results:
        query_counts.update(r['operations'])
        validation_counts.update(r['validation_operations'])
    build_counts = Counter(build_ec.count)
    total_counts = build_counts + query_counts + Counter(seed_setup['operations'])
    recoveries = sum(r['resolved'] for r in results)
    independent_target = sum(r['new_independent_target_equations'] for r in results)
    useful = built['space'].rank + independent_target
    calls = total_counts['group_calls']
    out = {'id': identifier, 'arm': arm, 'curve_id': public['identity']['curve_id'],
           'curve_uid': public['identity']['curve_uid'], 'A': public['A'], 'B': public['B'],
           'k': public['k'], 'p': public['p'], 'ell': public['ell'], 'cofactor': public['cofactor'],
           'bound': bound, 'seed_count': len(seeds), 'unknown_seed_count': len(seeds)-len(known),
           'known_seed_logs': {str(i): int(v) for i,v in known.items()}, 'seeds': [point_list(x) for x in seeds],
           'seed_spec_id': None if seed_spec is None else seed_spec['id'],
           'table_entries_requested': step_size, 'table_entries_generated': len(built['rows']) if built['rows'] is not None else built['built_size'],
           'distinct_subgroup_points': len(built['table']), 'subgroup_coverage_fraction': len(built['table'])/public['ell'],
           'distinct_subgroup_points_per_build_group_call': len(built['table'])/max(1,build_counts['group_calls']),
           'table_point_set_sha256': sha_value(sorted([point_list(x) for x in built['table']], key=lambda v: (-1,-1) if v is None else tuple(v))),
           'factorbase_table_sha256': sha_value(built['rows']) if built['rows'] is not None else None,
           'factorbase_collisions': built['collision_count'], 'independent_factorbase_relations': built['space'].rank,
           'factorbase_relation_witnesses': built['witnesses'], 'factorbase_relation_algebra_operations': dict(built['space'].count),
           'seed_setup': seed_setup, 'table_build_operations': dict(build_counts), 'table_build_timing': timing,
           'target_count': len(targets), 'target_recoveries': recoveries, 'query_step_cap': cap,
           'target_table_hits': sum(r['table_hits'] for r in results), 'independent_target_relations': independent_target,
           'total_independent_useful_relations': useful, 'useful_relations_per_1000_group_calls': useful*1000/max(1,calls),
           'recoveries_per_1000_group_calls': recoveries*1000/max(1,calls),
           'total_algorithm_operations': dict(total_counts), 'verification_operations': dict(validation_counts),
           'total_build_query_cpu_seconds': timing['cpu_seconds'] + sum(r['timing']['cpu_seconds'] for r in results),
           'targets': results,
           'inference': 'Incomplete recoveries are censored; independent equations count constraints, not distinct solved targets.'}
    return out

def main():
    stage = RUN / 'benchmark-attempt-01'
    stage.mkdir(exist_ok=False)
    (stage/'source').mkdir()
    for name in ['benchmark.py', 'finite_math.py', 'gp_tables.py', 'curve_identity.py']:
        shutil.copy2(RUN/'source'/name, stage/'source'/name)
    plan = json.loads((RUN/'plan.json').read_text())
    write(stage/'launch.json', {'command_argv': ['python3', str(Path(__file__).resolve())],
                              'platform': platform.platform(), 'python': platform.python_version(),
                              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (stage/'source').iterdir()},
                              'plan_sha256': hashlib.sha256((RUN/'plan.json').read_bytes()).hexdigest(),
                              'inference_identity': 'GPT-6, system identity; no provider probe',
                              'fallback_used': False, 'scientific_review_performed': False})
    start = time.perf_counter()
    specs = json.loads((PREP/'seed-specs.json').read_text())
    exact = {s['id']: json.loads((PREP/'exact-grids'/s['id']/'tables.json').read_text()) for s in specs}
    for s in specs:
        exact_seed_check(s)
    isos = [isomorphic_spec(s) for s in specs if s['field']=='solinas']
    specs += isos
    for s in isos:
        exact[s['id']] = exact[s['id'].replace('isomorphic_sign_control','solinas')]
    groups = {}
    for s in specs:
        for key, red in s['reductions'].items():
            group_key = (s['A'],s['B'],red['k'])
            group = {'A':s['A'], 'B':s['B'], **{k:red[k] for k in ['k','p','group_order','ell','cofactor','G']}}
            if group_key in groups:
                assert group == groups[group_key]
            else:
                groups[group_key] = group
    all_methods, coverage, validations, ineligible, targets_public, truth = [], [], [], [], [], []
    for group_key, public in sorted(groups.items()):
        a,b,k = group_key
        ell,p,h,g = public['ell'],public['p'],public['cofactor'],tuple(public['G'])
        check = Curve(p,a,b)
        assert check.on_curve(g) and g is not None and check.mul(g,ell) is None
        field = {'characteristic':p,'degree':1,'representation':'prime field, canonical integer residues',
                 'element_encoding':'integers 0..p-1','modulus':p}
        curve = {'model':'short-Weierstrass','a4':a,'a6':b,'subgroup_order':ell,'cofactor':h,
                 'generator':list(g),'target_group':'prime-order cyclic subgroup of E(F_p)'}
        public['identity'] = curve_identity(field,curve,'solinaslift')
        public['field'],public['curve'] = field,curve
        rng = random.Random(plan['target_seed'] + a*1000 + b*100 + k)
        secrets = rng.sample(range(1,ell),plan['target_count_per_curve_prime'])
        targets = []
        for i,secret in enumerate(secrets):
            target = check.mul(g,secret)
            target_id = f'a{a}b{b}k{k}-target{i:02}'
            record = {'id':target_id,'curve_uid':public['identity']['curve_uid'],'point':list(target)}
            targets.append(record)
            truth.append({'id':target_id,'synthetic_scalar':secret,'construction':'seeded public synthetic benchmark'})
        targets_public += targets
        models = [s for s in specs if (s['A'],s['B'])==(a,b)]
        unique_sizes = set()
        local_methods = []
        for s in models:
            red = next(v for v in s['reductions'].values() if v['k']==k)
            kj = next(key for key,v in s['reductions'].items() if v['k']==k)
            if not red['eligible']:
                ineligible.append({'spec_id':s['id'],'curve_uid':public['identity']['curve_uid'],'k':k,'p':p,
                                   'reason':'No degree-one prime above the fixed matched reduction prime'})
                continue
            raw_seeds = [tuple(point) for point in red['seeds_full']]
            projection = Curve(p,a,b)
            reduced_seeds, projection_timing = measured(lambda:[projection.mul(point,h) for point in raw_seeds])
            known = known_seed_logs(reduced_seeds,g)
            for i,point in enumerate(reduced_seeds):
                if point == check.neg(g):
                    known[i] = -1
            for bound in plan['grid_bounds']:
                oracle_table = exact[s['id']]['tables'][f'{bound}:{kj}']
                validation_ec = Curve(p,a,b)
                actual_full = [point_list(point) for _,point in grid_points(validation_ec,raw_seeds,bound)]
                assert actual_full == oracle_table
                n = len(oracle_table)
                timings, opcounts, built = [], [], None
                for rep in range(plan['timing_repetitions']):
                    ec = Curve(p,a,b)
                    built, timing = measured(lambda:build_table(ec,reduced_seeds,bound,known,ell))
                    timings.append(timing)
                    opcounts.append(dict(ec.count))
                assert all(opcounts[0]==value for value in opcounts)
                row = {'spec_id':s['id'],'field':s['field'],'A':a,'B':b,'k':k,'p':p,'ell':ell,
                       'curve_uid':public['identity']['curve_uid'],'bound':bound,'seed_count':len(reduced_seeds),
                       'rank_bounds':s['rank_bounds'],'rank_status':s['rank_status'],
                       'grid_entries':n,'distinct_full_group_points':len({None if x is None else tuple(x) for x in actual_full}),
                       'full_group_order':public['group_order'],'distinct_subgroup_points':len(built['table']),
                       'subgroup_coverage_fraction':len(built['table'])/ell,'factorbase_collisions':built['collision_count'],
                       'independent_factorbase_relations':built['space'].rank,
                       'finite_build_operations':opcounts[0],'timing_repetitions':timings,
                       'cached_build_cpu_median_seconds':statistics.median(x['cpu_seconds'] for x in timings),
                       'seed_projection':{'operations':dict(projection.count),'timing':projection_timing},
                       'table_point_set_sha256':sha_value(sorted([point_list(x) for x in built['table']], key=lambda v:(-1,-1) if v is None else tuple(v))),
                       'NF_generation_source':s['id'].replace('isomorphic_sign_control','solinas'),
                       'NF_timings':exact[s['id']]['timings'],
                       'exact_K_vs_cached_full_group_agree':True}
                coverage.append(row)
                validations.append({'spec_id':s['id'],'k':k,'bound':bound,'all_entries_checked':n,
                                    'operations':dict(validation_ec.count),'passed':True})
                if bound != 4:
                    continue
                unique_sizes.add(n)
                # Use the first timing/cost sample for the actual pipeline. Repetitions are verification/measurement costs.
                build_ec = Curve(p,a,b)
                built, timing = measured(lambda:build_table(build_ec,reduced_seeds,bound,known,ell))
                setup = {'operations':dict(projection.count),'timing':projection_timing,
                         'prior_rank_discovery_elapsed_seconds':s['rank_seed_discovery_elapsed_seconds'],
                         'gp_seed_export_elapsed_seconds':s['export_process']['elapsed_seconds']}
                m = summarize_method(public,f"{s['id']}-k{k}",s['field'],reduced_seeds,known,built,build_ec,timing,
                                     setup,targets,plan['query_step_cap'],n,s,bound)
                local_methods.append(m)
                print('METHOD',m['id'],'D',m['distinct_subgroup_points'],'recoveries',m['target_recoveries'],
                      'ops',m['total_algorithm_operations']['group_calls'],flush=True)
                if s['field']=='isomorphic_sign_control':
                    continue
                # Matching null: same group, generator slot, box and seed count, with random finite-field directions.
                null_rng = random.Random(int(hashlib.sha256(f'{s["id"]}:{k}:20261011'.encode()).hexdigest(),16))
                null_scalars = [known[i] if i in known else null_rng.randrange(1,ell) for i in range(len(reduced_seeds))]
                null_setup_ec = Curve(p,a,b)
                null_points, null_setup_timing = measured(lambda:[null_setup_ec.mul(g,x % ell) for x in null_scalars])
                null_known = {i:v for i,v in known.items()}
                for label, known_map in [('random_hidden',null_known),('random_known',{i:x for i,x in enumerate(null_scalars)})]:
                    null_ec = Curve(p,a,b)
                    null_built,null_timing = measured(lambda:build_table(null_ec,null_points,bound,known_map,ell))
                    null_setup = {'operations':dict(null_setup_ec.count),'timing':null_setup_timing,
                                  'construction':'seeded known-scalar point creation; hidden solver receives only original known slots'}
                    nm = summarize_method(public,f'{s["id"]}-k{k}-{label}',label,null_points,known_map,null_built,
                                          null_ec,null_timing,null_setup,targets,plan['query_step_cap'],n,s,bound)
                    local_methods.append(nm)
                truth.append({'id':f'{s["id"]}-k{k}-null-seeds','synthetic_seed_scalars':null_scalars})
        for size in sorted(unique_sizes | {math.isqrt(ell)+(math.isqrt(ell)**2<ell)}):
            label = 'bsgs_sqrt' if size==math.isqrt(ell)+(math.isqrt(ell)**2<ell) else 'bsgs_matched'
            ec = Curve(p,a,b)
            built,timing = measured(lambda:scalar_table(ec,g,size,ell))
            setup = {'operations':{},'timing':{'wall_seconds':0.0,'cpu_seconds':0.0},'construction':'public G multiples'}
            m = summarize_method(public,f'{label}-a{a}-b{b}-k{k}-M{size}',label,[g],{0:1},built,ec,timing,
                                 setup,targets,plan['query_step_cap'],size)
            local_methods.append(m)
            if label=='bsgs_sqrt':
                assert m['target_recoveries']==len(targets)
        true_values = {t['id']:t['synthetic_scalar'] for t in truth if 'synthetic_scalar' in t}
        for m in local_methods:
            for r in m['targets']:
                if r['resolved']:
                    assert r['recovered_scalar']==true_values[r['target_id']]
            if m['arm']=='isomorphic_sign_control':
                original = next(x for x in local_methods if x['id']==m['id'].replace('isomorphic_sign_control','solinas'))
                for key in ['distinct_subgroup_points','table_point_set_sha256','factorbase_collisions',
                            'independent_factorbase_relations','target_recoveries','total_algorithm_operations']:
                    assert original[key]==m[key]
                assert [r['recovered_scalar'] for r in original['targets']]==[r['recovered_scalar'] for r in m['targets']]
        write(stage/f'cohort-a{a}-b{b}-k{k}.json',{'public_group':public,'methods':local_methods})
        all_methods += local_methods
        print('COHORT_COMPLETE',group_key,'methods',len(local_methods),flush=True)
    write(stage/'targets-public.json',targets_public)
    (stage/'validation').mkdir()
    write(stage/'validation/synthetic-truth.json',truth)
    write(stage/'coverage.json',coverage)
    write(stage/'verification.json',{'exact_K_vs_cached':validations,'isomorphic_control':'passed on all six eligible cohorts',
                                    'recovered_targets_all_correct':True,'bsgs_sqrt_all_96_targets_recovered':True,
                                    'solver_truth_policy':'target_solver arguments exclude synthetic truth and hidden seed logs',
                                    'ineligible':ineligible})
    u=resource.getrusage(resource.RUSAGE_SELF)
    write(stage/'raw-result.json',{'methods':all_methods,'ineligible':ineligible,'public_groups':list(groups.values()),
                                 'target_count':len(targets_public),'coverage_cells':len(coverage),
                                 'process':{'elapsed_seconds':time.perf_counter()-start,'user_cpu_seconds':u.ru_utime,
                                            'system_cpu_seconds':u.ru_stime,'peak_rss_kib':u.ru_maxrss}})
    print('FINISHED',len(all_methods),len(coverage),len(targets_public),time.perf_counter()-start,flush=True)

if __name__=='__main__':
    main()
