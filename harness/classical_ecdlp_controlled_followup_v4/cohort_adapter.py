#!/usr/bin/env python3
"""Frozen old sampling/schedule adapter; generation requires actual native context."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d
ARMS=tuple(f'circuit{c}.a{a}' for c in (1,2) for a in (1,2,3,5))
FULL={'setups':216,'intents':36864,'singles':345600,'traces':36864,'cells':73728}
JOB_KEYS={'kind','id','curve_id','target_id','arm_id','point_index','replicate','proposal_limit'}
def expected_from_jobs(public,plan):
 d.need(set(plan)=={'jobs','expected'} and type(plan['jobs']) is list,'job plan')
 curves={c['curve_id']:c for c in public['curves']};ids=set();setups=set();counts=dict.fromkeys(FULL,0)
 for j in plan['jobs']:
  d.need(set(j)==JOB_KEYS and type(j['id']) is str and len(j['id'])<=160 and j['id'] not in ids,'duplicate/unfrozen job')
  ids.add(j['id']);d.need(j['curve_id'] in curves and j['arm_id'] in ARMS,'job curve/arm')
  d.need(type(j['proposal_limit']) is int and 1<=j['proposal_limit']<=1024,'point proposal guard')
  setups.add((j['curve_id'],j['arm_id']))
  if j['kind']=='single':
   d.need(j['target_id'] is None and type(j['point_index']) is int and j['point_index']>=0 and j['replicate'] is None,'single slot')
   counts['singles']+=1
  elif j['kind']=='calibration-trace':
   d.need(j['target_id'] is None and type(j['point_index']) is int and j['point_index']>=0 and j['replicate'] is None,'calibration slot')
   counts['traces']+=1;counts['intents']+=1
  else:
   d.need(j['kind']=='confirmation-trace' and j['arm_id']=='circuit2.a1' and j['point_index'] is None and type(j['replicate']) is int and 0<=j['replicate']<8,'confirmation slot')
   d.need(j['target_id'] in {t['target_id'] for t in curves[j['curve_id']]['targets']},'target ID')
   counts['traces']+=1;counts['intents']+=1;counts['cells']+=6
 counts['setups']=len(setups);d.need(type(plan['expected']) is dict and set(plan['expected'])==set(FULL) and all(type(v) is int and v>=0 for v in plan['expected'].values()) and counts==plan['expected'],'independent job counts')
 return counts
def make_input(public,plan,fixture_only,protocol_hash,source_fingerprint,status='complete'):
 if status=='complete':expected_from_jobs(public,plan)
 else:d.need(type(plan['expected']) is dict and all(type(v) is int and v>=0 for v in plan['expected'].values()),'planned counts remain explicit on incomplete generation')
 return {'schema':'controlled-followup-v4.public-input/v1','fixture_only':fixture_only,'generation_status':status,'public':public,'plan':plan,'provenance':{'protocol_sha256':protocol_hash,'source_fingerprint':source_fingerprint,'cohort_sha256':d.sha(d.canonical(public))}}
def fixed_input(protocol_hash,source_fingerprint):
 fixed=d.read(d.HERE/'fixtures.json')['fixed_input']
 return make_input(fixed['public'],fixed['plan'],True,protocol_hash,source_fingerprint)
def static_schedule(repo):
 root=d.dependencies(repo);sys.path.insert(0,str(root));import cohort
 jobs=[]
 for stage in cohort.STAGES:
  for bits in cohort.TIERS:
   for slot in range(4):jobs.extend(cohort.jobs_for_curve(f'{stage}-{bits}-{slot}',stage,1024))
 # No sampler, entropy or public points are drawn.
 public={'curves':[{'curve_id':f'{stage}-{bits}-{slot}','targets':[{'target_id':f'target{i:04d}'} for i in range(64)] if stage in cohort.STAGES[2:] else []} for stage in cohort.STAGES for bits in cohort.TIERS for slot in range(4)]}
 counts=expected_from_jobs(public,{'jobs':jobs,'expected':FULL})
 return {'status':'static_plan_only','jobs':len(jobs),'counts':counts,'curves':len(public['curves']),'scientific_draws':0,'fresh_entropy':0}
def generate(repo,ctx,out):
 d.need(ctx['fixture_only'] is False and ctx.get('config') and ctx['launch']['supervisor_pid']==__import__('os').getppid(),'actual native context required before any draw')
 config=ctx['config'];sampler=config['sampler']
 d.need(set(sampler)=={'nonce','curve_proposal_limit','point_proposal_limit','target_proposal_limit','excluded_p_j'},'frozen sampler fields')
 d.need((sampler['curve_proposal_limit'],sampler['point_proposal_limit'],sampler['target_proposal_limit'])==(10000,1024,1024),'original sampler proposal caps')
 d.need(type(sampler['excluded_p_j']) is list and len({tuple(x) for x in sampler['excluded_p_j']})==len(sampler['excluded_p_j']),'exclusion inventory')
 out=Path(out);out.mkdir(parents=True,exist_ok=False)
 d.write(out/'generation-start.json',{'started_at':d.now(),'sampler':sampler,'source_sha256':ctx['source_sha256'],'source_publication_commit':ctx['publication'],'launch_context_commit':ctx['context'],'phase':'shared public generation; separately paid'})
 root=d.dependencies(repo);sys.path.insert(0,str(root));import cohort
 before=d.snapshot(repo,repo);generated=cohort.build_public(sampler);after=d.snapshot(repo,repo);d.need(d.source_map(before)==d.source_map(after),'source changed during public generation')
 d.write(out/'generation.json',generated,ctx['limits']['generation_bytes'])
 if generated['status']=='complete':
  plan=generated['plan'];d.need(plan['expected']==FULL,'full original schedule');expected_from_jobs(generated['public'],plan)
 else:
  plan={'jobs':generated['jobs'],'expected':dict(FULL)}
 x=make_input(generated['public'],plan,False,config['protocol']['protocol_sha256'],d.sha(d.canonical(ctx['source_sha256'])),generated['status'])
 d.write(out/'input.json',x,ctx['limits']['input_bytes'])
 d.write(out/'generation-process.json',{'finished_at':d.now(),'source_before':before,'source_after':after,'status':generated['status'],'common_generation_not_bsgs_or_candidate_solve_cost':True,'source_publication_commit':ctx['publication'],'launch_context_commit':ctx['context'],'wall_valid':False},ctx['limits']['document_bytes'])
 return out/'input.json'

