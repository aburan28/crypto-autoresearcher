#!/usr/bin/env python3
"""Descriptive arithmetic on an already sealed and published solver batch.

This reads no private scalar/seed records and runs no elliptic-curve operation.
Invocation is intentionally deferred until the Coordinator supplies publication.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import statistics

METHODS = ['rho_upstream_auto', 'rho_upstream_auto_aa', 'hybrid_xmod7_exact_b8_then_rho',
           'bernstein_lange_precomp', 'bsgs_complete']
FEATURES = ['constant', 'x_hash_7', 'x_mod_7', 'power_residue_5']

def digest(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def load(p): return json.loads(Path(p).read_text())

def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, separators=(',', ':'), allow_nan=False)+'\n')
    assert p.stat().st_size < 1048576, (p, p.stat().st_size)

def stat(v):
    v=list(v)
    return {'n':len(v),'min':min(v) if v else None,'median':statistics.median(v) if v else None,
            'max':max(v) if v else None,'mean':statistics.fmean(v) if v else None}

def ratio_stat(v):
    v=list(v);x=stat(v)
    x['geometric_mean']=math.exp(statistics.fmean(map(math.log,v))) if v else None
    return x

def counters(rows, field='counters'):
    z=Counter()
    for row in rows: z.update(row.get(field, {}))
    return dict(z)

def verify_part(run, item):
    p=run/item['path'];assert p.stat().st_size==item['bytes'],p
    assert digest(p)==item['sha256'],p
    assert p.stat().st_size<=61440,p
    return p.read_bytes()

def json_rows(data):
    return [json.loads(x) for x in data.splitlines() if x.strip()]

def table(out, name, columns, rows):
    """JSON row-preserving parts, each below60KiB, with explicit index."""
    parts=[];current=[]
    for row in rows:
        test={'columns':columns,'rows':current+[row]}
        if len(json.dumps(test,separators=(',',':')).encode())>60000 and current:
            p=out/f'{name}-part-{len(parts):02}.json';dump(p,{'columns':columns,'rows':current})
            parts.append({'path':p.name,'sha256':digest(p),'rows':len(current)});current=[]
        current.append(row)
    if current:
        p=out/f'{name}-part-{len(parts):02}.json';dump(p,{'columns':columns,'rows':current})
        parts.append({'path':p.name,'sha256':digest(p),'rows':len(current)})
    dump(out/f'{name}-index.json',{'columns':columns,'rows':len(rows),'parts':parts})

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo-root',type=Path,required=True)
    ap.add_argument('--run-dir',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--source-prefix',default='harness/classical_ecdlp_solver_validation')
    ap.add_argument('--raw-commit',required=True)
    ap.add_argument('--archive-commit',default=None)
    a=ap.parse_args();repo=a.repo_root.resolve();run=a.run_dir.resolve();out=a.out_dir.resolve()
    assert a.raw_commit.strip(), 'The Coordinator must supply actual raw publication.'
    receipt=load(run/'execution-receipt.json')
    assert receipt['status']=='output_validated' and receipt['returncode']==0,receipt['status']
    assert receipt.get('check_returncode')==0,receipt
    checked=0
    for name,expected in receipt['artifact_sha256'].items():
        p=run/name;assert p.is_file() and digest(p)==expected,p;checked+=1
    parts=load(run/'parts-manifest.json');raw=load(run/'raw-result.json')
    assert digest(run/'parts-manifest.json')==raw['parts_manifest_sha256']
    assert not parts['errors'] and not raw['errors']
    occupied=0
    for slot in parts['slots']:
        verify_part(run,slot);occupied+=bool(slot['bytes'])
    modules={};allrows=[]
    for m in parts['modules']:
        data=b''.join(verify_part(run,p) for p in m['parts'])
        assert len(data)==m['original_bytes'] and hashlib.sha256(data).hexdigest()==m['original_sha256']
        rows=json_rows(data);assert len(rows)==m['row_count']
        modules[m['name']]=rows;allrows.extend(rows)
    assert len(allrows)==raw['metrics']['rows']
    vm=load(run/'verification-manifest.json');verified=[]
    for p in vm['parts']: verified.extend(json_rows(verify_part(run,p)))
    assert len(verified)==vm['candidate_cases']
    for v in verified:
        row=modules[v['module']][v['row_index']];lead='prefix_' if v['kind']=='prefix' else ''
        assert len(row[lead+'candidates'])==v['candidate_count']
        assert row[lead+'candidate_verification_hits']==v['verification_hits']
        assert row[lead+'verified_scalar']==v['verified_scalar']
    base=repo/a.source_prefix/'cohort/public'
    with (base/'fixtures.tsv').open() as f: fixtures={r['id']:{**r,'r':int(r['r']),'p':int(r['p']),'N':int(r['N'])} for r in csv.DictReader(f,delimiter='\t')}
    for f in fixtures.values(): f['bits']=f['r'].bit_length()
    with (base/'target-subsets.tsv').open() as f: subsets={r['target_id']:r for r in csv.DictReader(f,delimiter='\t')}
    assert len(fixtures)==48 and len(subsets)==768
    core_fixtures={r['fixture_id'] for r in subsets.values() if r['subset']=='core'}
    targetrows=[r for r in allrows if r['row_kind']=='baseline_target']
    sec=[r for r in allrows if r['row_kind']=='target']
    kernels=[r for r in allrows if r['row_kind']=='kernel']
    nas=[r for r in allrows if r['row_kind']=='not_applicable']
    setup={(r['fixture'],r['method']):r for r in allrows if r['row_kind'] in ('baseline_setup','hybrid_setup')}
    validation=[r for r in allrows if r['row_kind']=='fixture_validation']
    arms={m:[r for r in targetrows if r['method']==m] for m in METHODS}
    pairs=defaultdict(dict)
    for r in targetrows:pairs[(r['fixture'],r['target_id'])][r['method']]=r
    assert len(pairs)==768 and all(set(p)==set(METHODS) for p in pairs.values())
    aa_good=fallback_good=prefix_good=0
    aa_ratios=[];aa_unresolved=[]
    for key,p in pairs.items():
        r,aa,h=(p[m] for m in METHODS[:3])
        assert r['rho_seed']==aa['rho_seed']==h['rho_seed']
        assert r['counters']==aa['counters'] and r['status']==aa['status'] and r['verified_scalar']==aa['verified_scalar'];aa_good+=1
        if r['process_cpu_seconds']>0 and aa['process_cpu_seconds']>0:
            aa_ratios.append(aa['process_cpu_seconds']/r['process_cpu_seconds'])
        else:aa_unresolved.append(list(key))
        assert h['candidate_alone_recovered']==bool(h['prefix_candidate_verification_hits'])
        assert h['fallback_used']==(not h['candidate_alone_recovered'])
        assert all(h['counters'][k]==h['stages']['prefix_total'][k]+h['stages']['fallback'][k] for k in h['counters'])
        if h['fallback_used']:
            assert h['stages']['fallback']==r['counters'];fallback_good+=1
        else:prefix_good+=1
    cost_columns=['fixture','bits','stratum','method','panel','targets','solved','failed','censored','invalid',
                  'setup_cpu_s','online_cpu_s','batch_cpu_s','amortized_cpu_s','cold_mean_cpu_s','cold_min_cpu_s','cold_max_cpu_s',
                  'batch_group_additions','batch_field_multiplications','batch_scalar_mul_calls','batch_dp_terms','payload_bytes','target_table_estimate_max_bytes']
    cost_rows=[];cost_map={}
    for panel in ['full','core']:
      for fixture,f in fixtures.items():
        if panel=='core' and fixture not in core_fixtures:continue
        for method in METHODS:
            rows=[r for r in arms[method] if r['fixture']==fixture and (panel=='full' or subsets[r['target_id']]['subset']=='core')]
            expected=16 if panel=='full' else 8;assert len(rows)==expected
            s=setup.get((fixture,method));scpu=s['process_cpu_seconds'] if s else 0
            online=sum(r['process_cpu_seconds'] for r in rows);batch=scpu+online
            cold=[scpu+r['process_cpu_seconds'] for r in rows]
            state=Counter(r['status'] for r in rows);cnt=counters(rows)
            if s:cnt=dict(Counter(cnt)+Counter(s['counters']))
            target_memory=max((r.get('upstream_stats',{}).get('table_bytes_peak_estimate',0) for r in rows),default=0)
            payload=(s.get('kernel_numeric_payload_bytes') or s.get('table_payload_bytes') or s.get('upstream_stats',{}).get('table_bytes_peak_estimate')) if s else target_memory
            z=[fixture,f['bits'],f['stratum'],method,panel,len(rows),state['solved'],state['failed'],state['censored'],state['invalid'],scpu,online,batch,batch/len(rows),statistics.fmean(cold),min(cold),max(cold),cnt.get('group_additions',0),cnt.get('field_multiplications',0),cnt.get('scalar_multiplications',0),cnt.get('dp_multiply_add_terms',0),payload,target_memory]
            cost_rows.append(z);cost_map[(fixture,method,panel)]={**dict(zip(cost_columns,z)),'counters':cnt}
    paired=[];pair_summaries=[]
    for panel in ['full','core']:
      for numerator in METHODS[1:]:
        for fixture,f in fixtures.items():
            if panel=='core' and fixture not in core_fixtures:continue
            den=cost_map[fixture,METHODS[0],panel];num=cost_map[fixture,numerator,panel]
            complete=den['solved']==den['targets'] and num['solved']==num['targets']
            positive=den['batch_cpu_s']>0 and num['batch_cpu_s']>0
            ratio=num['batch_cpu_s']/den['batch_cpu_s'] if positive else None
            paired.append([fixture,f['bits'],f['stratum'],panel,numerator,complete,ratio,num['batch_cpu_s'],den['batch_cpu_s']])
        for bits in [None,12,14,16,18]:
            group=[r for r in paired if r[3]==panel and r[4]==numerator and (bits is None or r[1]==bits)]
            valid=[r[6] for r in group if r[5] and r[6] is not None]
            pair_summaries.append({'panel':panel,'numerator':numerator,'denominator':METHODS[0],'bits':bits,
                'requested_curves':len(group),'comparable_complete_curves':len(valid),**ratio_stat(valid)})
    candidate_cols=['panel','feature','mode','beam','bits','stratum','cases','hits','checks','uniform_guess_expected_hits']
    extra_pairs=[];extra_summaries=[]
    for panel in ['full','core']:
      for numerator in [METHODS[2],METHODS[4]]:
        denominator=METHODS[3]
        for fixture,f in fixtures.items():
            if panel=='core' and fixture not in core_fixtures:continue
            den=cost_map[fixture,denominator,panel];num=cost_map[fixture,numerator,panel]
            complete=den['solved']==den['targets'] and num['solved']==num['targets']
            positive=den['batch_cpu_s']>0 and num['batch_cpu_s']>0
            ratio=num['batch_cpu_s']/den['batch_cpu_s'] if positive else None
            extra_pairs.append([fixture,f['bits'],f['stratum'],panel,numerator,denominator,complete,ratio,num['batch_cpu_s'],den['batch_cpu_s']])
        for bits in [None,12,14,16,18]:
            group=[r for r in extra_pairs if r[3]==panel and r[4]==numerator and (bits is None or r[1]==bits)]
            valid=[r[7] for r in group if r[6] and r[7] is not None]
            extra_summaries.append({'panel':panel,'numerator':numerator,'denominator':denominator,'bits':bits,'requested_curves':len(group),'comparable_complete_curves':len(valid),'scope':'Additional descriptive arithmetic; registered primary comparator remains rho.',**ratio_stat(valid)})
    candidate_rows=[]
    for panel in ['full','core','extension']:
      for feature in FEATURES:
       for mode in ['model','exact']:
        for beam in [1,8]:
         for bits,stratum in [(None,None)]+[(b,None) for b in [12,14,16,18]]+[(b,s) for b in [12,14,16,18] for s in ['ordinary','power5']]:
            rows=[r for r in sec if r['feature']==feature and r['prefix_mode']==mode and r['beam_width']==beam and (panel=='full' or subsets[r['target_id']]['subset']==panel) and (bits is None or fixtures[r['fixture']]['bits']==bits) and (stratum is None or fixtures[r['fixture']]['stratum']==stratum)]
            candidate_rows.append([panel,feature,mode,beam,bits,stratum,len(rows),sum(r['candidate_verification_hits'] for r in rows),sum(len(r['candidates']) for r in rows),sum(len(r['candidates'])/fixtures[r['fixture']]['r'] for r in rows)])
    primary=[]
    for panel in ['full','core','extension']:
      for bits in [None,12,14,16,18]:
        rows=[r for r in arms[METHODS[2]] if (panel=='full' or subsets[r['target_id']]['subset']==panel) and (bits is None or fixtures[r['fixture']]['bits']==bits)]
        primary.append({'panel':panel,'bits':bits,'targets':len(rows),'candidate_only_hits':sum(r['candidate_alone_recovered'] for r in rows),'fallback_used':sum(r['fallback_used'] for r in rows),'hybrid_statuses':dict(Counter(r['status'] for r in rows))})
    secondary_primary={(r['fixture'],r['target_id']):r for r in sec if r['feature']=='x_mod_7' and r['prefix_mode']=='exact' and r['beam_width']==8}
    for key,p in pairs.items():
        h=p[METHODS[2]];s=secondary_primary[key]
        assert h['prefix_candidates']==s['candidates'] and h['prefix_verified_scalar']==s['verified_scalar']
    stage_rows=[]
    for bits in [None,12,14,16,18]:
        rows=[r for r in arms[METHODS[2]] if bits is None or fixtures[r['fixture']]['bits']==bits]
        fs={r['fixture'] for r in rows}
        stage_rows.append({'bits':bits,'curves':len(fs),'targets':len(rows),
            'setup_cpu_s':sum(setup[f,METHODS[2]]['process_cpu_seconds'] for f in sorted(fs)),
            'prefix_cpu_s':sum(r['prefix_process_cpu_seconds'] for r in rows),
            'fallback_cpu_s':sum(r['fallback_process_cpu_seconds'] for r in rows),
            'outer_target_cpu_s':sum(r['process_cpu_seconds'] for r in rows),
            'views_cpu_s':sum(r['views_process_cpu_seconds'] for r in rows),
            'inference_cpu_s':sum(r['inference_process_cpu_seconds'] for r in rows),
            'verification_cpu_s':sum(r['verification_process_cpu_seconds'] for r in rows),
            'setup_counters':counters([setup[f,METHODS[2]] for f in sorted(fs)]),
            'prefix_counters':counters([{'counters':r['stages']['prefix_total']} for r in rows]),
            'fallback_counters':counters([{'counters':r['stages']['fallback']} for r in rows])})
    study=defaultdict(Counter);study_cpu=Counter();seen_views={};seen_val={}
    for row in kernels:
        study['secondary_training'].update(row['construction_counters']);study_cpu['secondary_training']+=row['construction_cpu_seconds']
        study['secondary_heldout'].update(row['heldout_calibration_counters']);study_cpu['secondary_heldout']+=row['heldout_calibration_cpu_seconds']
        if row['fixture'] not in seen_val:
            seen_val[row['fixture']]=row['fixture_validation_counters_shared'];study['secondary_public_validation'].update(row['fixture_validation_counters_shared'])
        else:assert seen_val[row['fixture']]==row['fixture_validation_counters_shared']
    for row in sec:
        key=(row['fixture'],row['feature'],row['target_id'])
        if key not in seen_views:
            seen_views[key]=(row['shared_view_counters'],row['shared_view_cpu_seconds']);study['secondary_views'].update(row['shared_view_counters']);study_cpu['secondary_views']+=row['shared_view_cpu_seconds']
        else:assert seen_views[key]==(row['shared_view_counters'],row['shared_view_cpu_seconds'])
        assert all(row['inference_and_verification_counters'][k]==row['inference_counters'][k]+row['verification_counters'][k] for k in row['inference_and_verification_counters'])
        study['secondary_inference'].update(row['inference_counters']);study_cpu['secondary_inference']+=row['inference_cpu_seconds']
        study['secondary_verification'].update(row['verification_counters']);study_cpu['secondary_verification']+=row['verification_cpu_seconds']
    summary={'kind':'sealed_solver_validation_descriptive_summary','experiment_id':raw['experiment_id'],'run_id':raw['run_id'],
        'source_commit':raw['source_commit'],'raw_publication_commit':a.raw_commit,'archive_commit':a.archive_commit,
        'observations_only':True,'independent_scientific_review':False,'private_scalar_or_seed_reads':False,
        'scope':{'curves':len(fixtures),'targets':len(subsets),'core_targets':sum(r['subset']=='core' for r in subsets.values()),'extension_targets':sum(r['subset']=='extension' for r in subsets.values()),'bits':[12,14,16,18],'strata':['ordinary','power5'],'curves_per_size_stratum':6,'reuse_full':16,'reuse_core':8,'subgroup_order_range':[min(f['r'] for f in fixtures.values()),max(f['r'] for f in fixtures.values())],'field_prime_range':[min(f['p'] for f in fixtures.values()),max(f['p'] for f in fixtures.values())],'cofactor_counts':dict(Counter(str(f['N']//f['r']) for f in fixtures.values()))},
        'custody':{'receipt_artifacts_hash_checked':checked,'producer_slots_checked':len(parts['slots']),'occupied_producer_slots':occupied,'module_streams_checked':len(modules),'verification_slots_checked':len(vm['parts']),'verification_case_rows_aligned':len(verified),'parts_manifest_sha256':digest(run/'parts-manifest.json'),'verification_manifest_sha256':digest(run/'verification-manifest.json'),'raw_result_sha256':digest(run/'raw-result.json'),'all_original_module_hashes_and_bytes_match':True},
        'input_sha256':{'fixtures':digest(base/'fixtures.tsv'),'public_targets':digest(base/'public-targets.tsv'),'target_subsets':digest(base/'target-subsets.tsv')},
        'rows':{'all':len(allrows),'secondary_targets':len(sec),'kernels':len(kernels),'not_applicable':len(nas),'baseline_targets':len(targetrows),'setup':len(setup),'shared_validation':len(validation)},
        'complete_arms':[{'method':m,'requested':len(arms[m]),'statuses':dict(Counter(r['status'] for r in arms[m])),'target_cpu_seconds':sum(r['process_cpu_seconds'] for r in arms[m]),'setup_cpu_seconds':sum(r['process_cpu_seconds'] for (f,k),r in setup.items() if k==m)} for m in METHODS],
        'primary_recovery':primary,'paired_cost_ratios':pair_summaries,'additional_baseline_ratios':extra_summaries,'hybrid_stage_totals':stage_rows,
        'aa':{'exact_seed_work_answer_pairs':aa_good,'target_cpu_ratio_aa_over_rho':ratio_stat(aa_ratios),'unresolved_zero_cpu_cases':aa_unresolved},
        'hybrid':{'candidate_only_hits':prefix_good,'fallback_invocations':fallback_good,'every_fallback_counter_vector_matches_rho':True,'primary_and_secondary_candidate_lists_match':True},
        'common_public_validation':{'rows':len(validation),'process_cpu_seconds':sum(r['process_cpu_seconds'] for r in validation),'counters':counters(validation),'scope':'Curve plus all16 target membership checks once before all arms; excluded from per-arm method CPU totals and retained separately.'},
        'study_secondary':{'stage_cpu_seconds':dict(study_cpu),'stage_counters':{k:dict(v) for k,v in study.items()},'distinct_shared_views':len(seen_views),'distinct_shared_validations':len(seen_val),'heldout_diagnostics_not_primary_algorithm_work':True},
        'timing_scope':'Per-arm setup and solve/check CPU excludes input parsing, shared public validation, JSON formatting, orchestration and final table teardown. Reconstructed cold totals are setup+one recorded target, not rerun cold invocations.',
        'memory_scope':'Only recorded payload/CA byte estimates; no measured per-arm peak RSS. Declared12GiB operational envelope is not measured memory use.',
        'memory_sources':{'rho_upstream_auto':'Maximum per-target upstream table_bytes_peak_estimate per curve.','rho_upstream_auto_aa':'Maximum per-target upstream table_bytes_peak_estimate per curve.','hybrid_xmod7_exact_b8_then_rho':'Setup kernel_numeric_payload_bytes only; excludes views/beam/objects and fallback table. Target upstream estimate is retained separately.','bernstein_lange_precomp':'Setup upstream table_bytes_peak_estimate; constructor/table estimate, not RSS.','bsgs_complete':'Setup baby-vector capacity payload; excludes object, allocator and sort stack.'},
        'limits':['48 curve replication units; targets and secondary configurations share setup.','Nested core and full panel overlap.','CPU ratios use finite positive complete pairs, with exclusions retained.','No bootstrap, p-value or asymptotic fit is computed.','Novelty is separate from working correctness and incremental baseline comparison.']}
    out.mkdir(parents=True,exist_ok=True);dump(out/'summary.json',summary)
    table(out,'per-curve-costs',cost_columns,cost_rows)
    table(out,'paired-curve-ratios',['fixture','bits','stratum','panel','method','complete_pair','consumed_cpu_ratio','numerator_batch_cpu_s','rho_batch_cpu_s'],paired)
    table(out,'additional-baseline-ratios',['fixture','bits','stratum','panel','numerator','denominator','complete_pair','consumed_cpu_ratio','numerator_batch_cpu_s','denominator_batch_cpu_s'],extra_pairs)
    table(out,'candidate-outcomes',candidate_cols,candidate_rows)
    runtime={k:raw[k] for k in ['source_commit','compiler','module_execution','metrics','errors']};runtime.update({'receipt_started_at':receipt['started_at'],'receipt_finished_at':receipt['finished_at'],'status':receipt['status'],'plan_sha256':receipt['plan_sha256']});dump(out/'runtime.json',runtime)
    print(json.dumps({'summary':str(out/'summary.json'),'rows':summary['rows'],'complete_arms':summary['complete_arms'],'primary_recovery':primary[:5],'hybrid_cpu_ratio':[x for x in pair_summaries if x['panel']=='full' and x['numerator']==METHODS[2]]},indent=2))

if __name__=='__main__': main()
