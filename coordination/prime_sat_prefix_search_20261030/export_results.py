#!/usr/bin/env python3
"""Frozen extraction of PSEARCH observations; no solver or reference producer."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
import artifact_store as store
import experiment_protocol as ep
STRATEGIES=('model_only','partial_prefix','partial_prefix_aa')
ENCODINGS=('quartic','membership','quadratic','quadratic_aa')
ARM_ROLES={'model_only':'baseline','partial_prefix':'candidate','partial_prefix_aa':'control_aa','reference':'reference','positive_controls':'control_positive','negative_controls':'control_negative'}

def available(path):
    return store.resolve(path) is not None

def load(path, default=None):
    return store.read_json(path) if available(path) else default

def ref(path,base,kind='raw'):
    p=store.resolve(path)
    if p is None:raise FileNotFoundError(path)
    return {'path':os.path.relpath(p,base),'sha256':ep.sha256_file(p),'bytes':p.stat().st_size,'kind':kind}

def flatten(obj, prefix=''):
    out={}
    if isinstance(obj,dict):
        for k,v in obj.items():out.update(flatten(v,prefix+'_'+k if prefix else k))
    elif type(obj) is int:out[prefix]=obj
    return out

def accumulate(total,key,value):
    if any(x in key for x in ('max_','peak_')):total[key]=max(total.get(key,value),value)
    else:total[key]=total.get(key,0)+value

def raw_rows(directory,raw,package):
    meta=raw.get('packages',{}).get(package)
    if meta:
        path=directory/meta['artifact'];b=store.read_bytes(path)
        if hashlib.sha256(b).hexdigest()!=meta['sha256']:raise ValueError('package hash mismatch '+package)
        payload=json.loads(b)
        if payload['config']!=raw['config']:raise ValueError('package config mismatch')
        return payload['rows'],payload
    journal=directory/(package+'-rows.jsonl')
    if available(journal):return [json.loads(x) for x in store.read_text(journal).splitlines()],{}
    return [],{}

def analyze(directory,raw,search,controls,references,checked,native_ok):
    pairs=[];lookup={(x['cell_id'],x['encoding'],x['strategy']):x for x in search}
    valid_ids={x['id'] for x in checked.get('rows',[]) if x.get('valid')}
    for i in range(12):
        for enc in ENCODINGS:
            cell=f'c{i:02d}';rows=[lookup.get((cell,enc,s)) for s in STRATEGIES]
            eligible=native_ok and checked.get('valid') is True and all(x and x['id'] in valid_ids and x['result']['declared_status']=='complete' and not x['censoring']['watchdog'] for x in rows)
            rec={'cell_id':cell,'encoding':enc,'eligible_complete_pair':bool(eligible),'observation':'inconclusive'}
            if eligible:
                b,c,a=rows
                require_equal=(b['result']['projected_models']==c['result']['projected_models']==a['result']['projected_models'])
                if not require_equal:raise ValueError('analysis model-set mismatch')
                bc=b['phases']['search_events']['model_checks'];cc=c['phases']['search_events']['model_checks']
                early=c['phases']['search_events']['partial_refutations']
                rec.update(observation='genuine_partial_pruning_with_fewer_model_checks' if early>0 and cc<bc else 'no_joint_mechanism_signature',baseline_model_checks=bc,candidate_model_checks=cc,difference=cc-bc,genuine_partial_refutations=early,reference_model_count=len(b['result']['projected_models']))
                bf,cf=flatten(b['phases']),flatten(c['phases'])
                rec['recorded_vector_difference']={k:cf.get(k,0)-bf.get(k,0) for k in sorted(set(bf)|set(cf))}
                rec['vector_zero_convention']='Absent additive counters normalize to zero only inside these displayed differences; missing entire phases are never zero. Classification and peak fields are displayed, not priced or summed.'
            pairs.append(rec)
    eligible=sum(x['eligible_complete_pair'] for x in pairs);positive=sum(x['observation']=='genuine_partial_pruning_with_fewer_model_checks' for x in pairs)
    observation=('invalid_or_incomplete_native_run' if not native_ok or checked.get('valid') is not True else 'inconclusive_fixed_inventory' if eligible<48 else 'mechanism_signature_observed' if positive else 'mechanism_signature_not_observed')
    return {'schema':'prime-prefix-search-analysis/v1','native_output_validated':native_ok,'ordinary_pairs_planned':48,'eligible_complete_pairs':eligible,'inconclusive_pairs':48-eligible,'mechanism_signature_pairs':positive,'fixed_inventory_observation':observation,'pairs':pairs,'underlying_flow':{'search_planned':144,'search_present':len(search),'control_planned':9,'control_present':len(controls),'reference_planned':12,'reference_present':len(references),'search_complete':sum(x['result']['declared_status']=='complete' for x in search),'search_censored':sum(x['result']['declared_status']=='censored' for x in search),'search_failed':sum(x['result']['declared_status']=='failed' for x in search)},'aa_complete_pairs':checked.get('aa_pairs'),'aa_censored':checked.get('aa_censored',[]),'cost_boundary':'Recorded vector only: legacy arithmetic omissions, callback bookkeeping, serialization/fsync and complete checker execution are not total machine work. Reference counts are function/pow events. No runtime or full-cost advantage.','goal_complete':False,'general_ecdlp_speedup_established':False,'scientific_status_changed':False}

def build(raw_path,protocol_path,out,analysis_out):
    directory=raw_path.parent;base=out.parent;p=ep.read_json(protocol_path);raw=load(raw_path)
    receipt=load(directory/'execution-receipt.json');env=load(directory/'environment.json');launch=load(directory/'launch.json')
    if not all(isinstance(x,dict) for x in [raw,receipt,env,launch]):raise ValueError('native records unavailable')
    if raw['config_sha256']!=p['extensions']['input_sha256'][p['study_dir']+'/config.json']:raise ValueError('config hash mismatch')
    for path,want in p['extensions']['source_sha256'].items():
        if env['source_sha256'].get(path)!=want:raise ValueError('native source hash mismatch '+path)
    for key,want in p['extensions']['native_environment'].items():
        if raw.get('environment',{}).get(key)!=want:raise ValueError('native runtime mismatch '+key)
    native_ok=receipt.get('status')=='output_validated' and receipt.get('returncode')==0 and receipt.get('check_returncode')==0
    checked=load(directory/'check-result.json',{})
    if available(directory/'check.stdout.log'):
        for line in store.read_text(directory/'check.stdout.log').splitlines():
            try:v=json.loads(line)
            except ValueError:continue
            if isinstance(v,dict) and 'valid' in v:checked=v
    search,_=raw_rows(directory,raw,'search');controls,control_payload=raw_rows(directory,raw,'controls');references,_=raw_rows(directory,raw,'reference')
    analysis=analyze(directory,raw,search,controls,references,checked,native_ok)
    groups={s:[x for x in search if x['strategy']==s] for s in STRATEGIES}
    groups.update(reference=references,positive_controls=[x for x in controls if x['cell_id'] in ('control-positive','control-empty_clause')],negative_controls=[x for x in controls if x['cell_id']=='control-negative'])
    e=ep.export_skeleton(p,os.path.relpath(protocol_path,base),'local',p['protocol_id']+'-export')
    e['producer']={'runtime':'native_codex','model':None,'session':'prime-prefix-search-execution','role':'executor'}
    e['source']={'repo':p['repository'],'commit':env['commit'],'dirty':None}
    e['arms']=[{'id':a['id'],'role':a['role'],'binary_sha256':a['instrument']['binary_sha256'],'commit':a['instrument']['commit']} for a in p['arms']]
    files=[]
    for name in p['extensions']['trial_artifacts']+p['extensions']['supervisor_artifacts']:
        if available(directory/name):files.append(ref(directory/name,base))
    files.append(ref(protocol_path,base,'protocol'))
    e['files']=files
    host=ref(directory/'environment.json',base);e['host']['path']=host['path'];e['host']['sha256']=host['sha256']
    e['analysis']['script']=ref(Path(__file__).resolve(),base,'analysis')
    plans={'model_only':48,'partial_prefix':48,'partial_prefix_aa':48,'reference':12,'positive_controls':6,'negative_controls':3}
    for arm,rows in groups.items():
        counts={'underlying_planned':plans[arm],'underlying_present':len(rows),'underlying_missing':plans[arm]-len(rows),'verification_pass':int(native_ok and checked.get('valid') is True)}
        if arm=='reference':
            counts['reference_models']=sum(len(x['answer']['projected_pairs']) for x in rows)
            for row in rows:
                for key,value in flatten({'reference_source_events':row['source_events'],'reference_check_source_events':row['checking_source_events']}).items():accumulate(counts,key,value)
        else:
            for label in ('complete','censored','failed'):counts['search_'+label]=sum(x['result']['declared_status']==label for x in rows)
            counts['models_found']=sum(len(x['result'].get('projected_models',[])) for x in rows)
            for row in rows:
                if row.get('phases') is not None:
                    for key,value in flatten(row['phases'],'phase').items():accumulate(counts,key,value)
            counts['phases_unavailable']=sum(x.get('phases') is None for x in rows)
        if arm=='negative_controls':counts['mutation_checks_pass']=sum(v.get('rejected') is True for v in control_payload.get('mutations',{}).values())
        status='succeeded' if native_ok else 'interrupted' if receipt.get('status')=='interrupted' else 'failed'
        e['runs'].append(ep.run_row(run_id=directory.name+'-'+arm,arm=arm,instance_id='fixed_inventory',seed=0,replicate=0,status=status,attempts=1,measurements={'counted':counts,'wall_valid':False},verification={'status':'verified' if native_ok and checked.get('valid') is True else 'not_run','verifier':'Frozen native checker plus accepted arithmetic/coverage adapter; execution counters consistency only'},exclusion={'excluded':not native_ok,'rule':None if native_ok else 'native_output_not_validated'},artifacts=[f for f in files if Path(f['path']).name in ('raw-result.json','search.json','controls.json','reference.json','execution-receipt.json','check-result.json')],started_at=launch.get('started_at'),finished_at=receipt.get('finished_at'),backend_ref=directory.name,isolation={'tier':'none','contended':None,'blockers':['Counted search observations only; all timing descriptive.']}))
    e['flow']=ep.compute_flow(e['runs'])
    e['notes']=[{'kind':'observation','by':'frozen-analysis','text':t} for t in ['Six export rows package one fixed inventory each to satisfy the rectangular native schema; they are not independent observations. The 144 ordinary search, 9 synthetic solver-control and 12 reference executions remain individually identified and hash-bound in raw files and analysis.json.','positive_controls includes all three empty-clause controls and three positive-prefix controls; negative_controls includes three viable-prefix solver controls plus three separate certificate/model mutation checks.','Reference execution costs are included once for each of 12 reference cells; no multiplication across encodings or strategies. Complete/censored counts remain distinct from native package validity; a censored A/A pair is inconclusive.','Every phase retains its own units. Vector differences are instrument observations only, never total work/runtime advantage, intrinsic regularity or ECDLP recovery. Prior curves/targets were seen with another search instrument; no population or novelty inference.']]
    errors=ep.schema_errors(e,'experiment.export/v1') or ep.lint_export(e,p,base,True)
    if errors:raise ValueError('\n'.join(errors))
    ep.write_once(out,e);ep.write_once(analysis_out,analysis)
    print(json.dumps({'export':str(out),'analysis':str(analysis_out),'bundle_flow':e['flow'],'underlying_flow':analysis['underlying_flow'],'observation':analysis['fixed_inventory_observation']},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--raw',type=Path,required=True);ap.add_argument('--protocol',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--analysis-out',type=Path,required=True);a=ap.parse_args();build(a.raw.resolve(),a.protocol.resolve(),a.out.resolve(),a.analysis_out.resolve())
