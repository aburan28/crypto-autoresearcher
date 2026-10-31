#!/usr/bin/env python3
"""Independent retained-data cost audit. No producer import/call or new science.

Render/report source will be appended after preserving this executed version.
"""
import collections
import datetime
import hashlib
import json
import math
import os
import pathlib
import sys

OUT=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path('/workspace/classical-ecdlp-validation-ready')
TASK='TASK-20261030-f55ebb'
RUN='experiments/EXP-ECDLP-080f41/runs/RUN-ECDLP-939237/'
COL=RUN+'modal/collected/'
RAW=COL+'raw/'
POST='experiments/EXP-ECDLP-080f41/postrun-from-view-346631/'
ALLOWED_EXACT={
 'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/releases/'+TASK+'.json',
 'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/reviews/'+TASK+'/derivation.json',
 'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/reviews/'+TASK+'/seal.json'}
ALLOWED_PREFIX=(RUN,POST,'harness/classical_ecdlp_controlled_followup/')
Counter=collections.Counter

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds').replace('+00:00','Z')
def sha(data):return hashlib.sha256(data).hexdigest()
def jwrite(name,value):(OUT/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON key:'+k)
  d[k]=v
 return d

def parse(data):return json.loads(data,object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))

class Reader:
 def __init__(self):self.inventory=[]
 def begin(self,rel):
  p=pathlib.PurePosixPath(rel)
  assert not p.is_absolute() and '..' not in p.parts
  assert rel in ALLOWED_EXACT or any(rel.startswith(x) for x in ALLOWED_PREFIX),rel
  row={'actual_read_at_utc':utc(),'canonical_relative_path':rel,'phase':2,'extent':'full stream'}
  with (OUT/'read-log.phase2.jsonl').open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
  return row
 def finish(self,row,h,size,n):
  row={**row,'sha256':h.hexdigest(),'bytes':size,'records':n};self.inventory.append(row)
  with (OUT/'read-cache.phase2.jsonl').open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
 def read(self,rel):
  row=self.begin(rel);data=(ROOT/rel).read_bytes();self.finish(row,hashlib.sha256(data),len(data),1)
  return parse(data)
 def rows(self,rel):
  row=self.begin(rel);h=hashlib.sha256();size=n=0
  with (ROOT/rel).open('rb') as f:
   for line in f:
    assert len(line)<=64<<20 and line.endswith(b'\n'), 'partial/oversize row'
    h.update(line);size+=len(line);n+=1
    yield n,parse(line)
  self.finish(row,h,size,n)

def addflat(dst,vector,prefix=''):
 assert isinstance(vector,dict)
 for k,v in vector.items():
  if isinstance(v,dict):addflat(dst,v,prefix+k+'/')
  else:
   assert type(v) is int and v>=0,(prefix+k,v)
   dst[prefix+k]+=v

def norm(v):return {k:x for k,x in v.items() if x!=0}
def flat(v):
 c=Counter();addflat(c,v);return dict(c)
def primitive_sum(groups):
 c=Counter()
 for group,v in groups.items():
  for key,amount in v.items():c[key.rsplit('/',1)[-1]]+=amount
 return dict(c)
def euclid_steps(b,r):
 n=0
 while b:r,b=b,r%b;n+=1
 return n

def main_audit():
 reader=Reader();issues=[];checks=Counter();examples={};groups=collections.defaultdict(Counter);statuses=collections.defaultdict(Counter)
 def check(label,ok,witness=None):
  checks[label+'/checked']+=1
  if not ok:
   checks[label+'/failed']+=1
   if len(issues)<100:issues.append({'check':label,'witness':witness})
 def add(group,v):addflat(groups[group],v)
 def sample(group,s):
  if s is None:return
  add(group,s['counts']);statuses[group][s['status']]+=1
  check('sampling.coordinate_proposal_count',s['counts'].get('coordinate_proposal')==len(s['proposals']))
  check('sampling.hash_reduction_count',s['counts'].get('rng_modular_reduction')==2*len(s['proposals']))
  statuses[group]['REJECTED_COORDINATE_PROPOSALS']+=sum(x['status']=='REJECTED' for x in s['proposals'])

 # The exact published note, seal and release are independently bound first.
 pubbase='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/'
 published_note=reader.read(pubbase+'reviews/'+TASK+'/derivation.json')
 published_seal=reader.read(pubbase+'reviews/'+TASK+'/seal.json')
 release=reader.read(pubbase+'releases/'+TASK+'.json')
 check('seal.note_digest',sha((OUT/'derivation.json').read_bytes())==published_seal['derivation_sha256'])
 check('seal.release_note',release['derivation_sha256']==published_seal['derivation_sha256'])
 check('seal.release_seal',sha((OUT/'seal.json').read_bytes())==release['seal_sha256'])
 check('seal.times',published_note['generated_at']<published_seal['recorded_at']<release['recorded_at'])

 public=reader.read(COL+'public-cohort.json');curves={x['curve_id']:x for x in public['curves']}
 check('population.curves',len(curves)==48)
 check('population.targets',sum(len(c['targets']) for c in curves.values())==1536)
 cohort=reader.read(COL+'cohort-ledger.json');proposal_reasons=Counter();target_duplicates=0;cohort_proposals=0
 for c in cohort:
  cid=c['curve_id'];add('worker.cohort_generation',c['counts']);sample('worker.base_sampling',c.get('base_sampling'))
  statuses['cohort'][c['status']]+=1;cohort_proposals+=len(c['proposals'])
  for p in c['proposals']:proposal_reasons[str(p['reason'])]+=1
  check('cohort.hash_reduction',c['counts'].get('rng_modular_reduction')==3*len(c['proposals']),cid)
  for t in c.get('target_sampling',[]):
   sample('worker.target_sampling',t['sampling']);target_duplicates+=t['duplicate']
 del cohort
 setup_map={};setup_rows=[]
 for rowno,r in reader.rows(RAW+'setups.jsonl'):
  key=(r['curve_id'],r['arm_id']);check('setup.unique',key not in setup_map,key);setup_map[key]=r
  add('worker.prepared_setup',r['counts']);statuses['setup'][str(r['setup_reason'])]+=1
  setup_rows.append({'curve_id':r['curve_id'],'arm_id':r['arm_id'],'setup_reason':r['setup_reason'],'counts':r['counts']})
 check('setup.count',len(setup_map)==216)
 n_single=0
 for rowno,r in reader.rows(RAW+'single-points.jsonl'):
  n_single+=1;add('worker.calibration_single_evaluation',r['counts']);sample('worker.calibration_single_sampling',r['sampling']);statuses['single_answers'][r['answer']['status']]+=1
 check('single.count',n_single==345600)
 intents={}
 for rowno,r in reader.rows(RAW+'attempt-intents.jsonl'):
  tid=r['trace_id'];check('intent.unique',tid not in intents,tid)
  intents[tid]={'draw_sha':sha(canonical(r['draw'])),'curve':r['curve_id'],'target':r['target_id'],'a':r['base_multiplier'],'b':r['target_multiplier']}
  add('worker.intent_rng',r['draw']['counts']);sample('worker.calibration_trace_sampling',r['draw'].get('point_sampling'))
 check('intent.count',len(intents)==36864)
 traces={};physical=collections.defaultdict(Counter);methods=collections.defaultdict(lambda:{'attempts':0,'queries':0,'statuses':Counter(),'targets':set(),'recovered':set(),'counts':Counter()});query_totals=Counter();failed_trace_vectors=Counter()
 for rowno,r in reader.rows(RAW+'traces.jsonl'):
  tid=r['trace_id'];cid=r['curve_id'];confirmation=r['target_id'] is not None
  check('trace.unique',tid not in traces,tid)
  check('trace.intent_draw_duplicate',sha(canonical(r['draw']))==intents[tid]['draw_sha'],tid)
  L=curves[cid]['model']['r'].bit_length()+1
  traces[tid]={**intents[tid],'L':L,'original_status':r['original']['status'],'original_scalar':r['original']['scalar'],'original_counts_sha':sha(canonical(r['original']['counts'])),'row':rowno}
  for method in ['original','incremental']:
   attempt=r[method]
   if attempt is None:continue
   phase='confirmation' if confirmation else 'calibration'
   name='worker.'+phase+'.'+method
   add(name,attempt['counts']);addflat(physical[(cid,method)],attempt['counts'])
   statuses[name][attempt['status']]+=1
   q=attempt['predicate_trace'];n=len(q)
   query_totals[name]+=n
   check('trace.length',n==L==attempt['L']==attempt['predicate_evaluations'],tid)
   check('trace.query_index',[x['index'] for x in q]==list(range(L)),tid)
   query_vector=Counter()
   for query in q:addflat(query_vector,query['counters'])
   check('trace.evaluate_sum',norm(query_vector)==norm(attempt['counts']['evaluate']),tid+'/'+method)
   check('trace.inverse_paid',attempt['counts']['conversion'].get('order_inverse_call')==1,tid)
   check('trace.blinding_paid',attempt['counts']['blinding'].get('scalar_multiply_call')==1,tid)
   nonempty=attempt['interval']['nonempty']
   reduction=attempt['counts']['reduction']
   check('trace.both_public_checks_paid',reduction.get('scalar_multiply_call',0)==2*nonempty and reduction.get('point_equal',0)==2*nonempty,tid)
   check('trace.digit_updates',reduction.get('recovery_scalar_digit_update')==L,tid)
   if attempt['status']!='RECOVERED':addflat(failed_trace_vectors,attempt['counts'])
   if confirmation:
    item=methods[method];item['attempts']+=1;item['queries']+=n;item['statuses'][attempt['status']]+=1;item['targets'].add((cid,r['target_id']));addflat(item['counts'],attempt['counts'])
    if attempt['status']=='RECOVERED':item['recovered'].add((cid,r['target_id']))
  if confirmation:
   check('trace.paired_count',r['incremental'] is not None,tid)
   traces[tid]['incremental_counts_sha']=sha(canonical(r['incremental']['counts']))
 check('trace.count',len(traces)==36864)
 # Aggregate every word, every cell, all zero/failure branches. No group oracle is called.
 cell_meta={};cell_aggregates={};cell_global=collections.defaultdict(lambda:{'attempts':0,'successes':0,'retained':set(),'recovered':set(),'outcomes':Counter(),'counts':Counter(),'words':0,'legal':0,'M':0,'zero':0,'M0':0,'max_M':0,'max_words':0,'retained_word_bits':0})
 memory_max=Counter();total_words=0;legal_total=0;zero_total=0;M0_rows=0;M0_decoder_vectors=Counter();cell_witnesses={};word_statuses=Counter()
 for rowno,r in reader.rows(RAW+'decoder-cells.jsonl'):
  tid=r['trace_id'];meta=traces[tid];cid=meta['curve'];cell=r['cell_id'].rsplit('/',1)[1];model=curves[cid]['model'];order=model['r'];b=meta['b'];a=meta['a'];L=meta['L'];words=r['words'];W=len(words);e=r['erasures'];cap=e>r['erasure_cap'];t=r['radius']
  check('cell.unique',r['cell_id'] not in cell_meta,r['cell_id'])
  check('cell.word_count',W==r['word_count']==r['expected_word_count']==(0 if cap else (1<<e)*sum(math.comb(L-e,j) for j in range(min(t,L-e)+1))),r['cell_id'])
  check('cell.length',r['L']==L,r['cell_id'])
  legal=[w for w in words if w['legal']];nlegal=len(legal);zero=sum(w['candidate_scalar']==0 for w in legal);distinct={w['candidate_scalar'] for w in legal if w['candidate_scalar']!=0};success=r['status']=='RECOVERED'
  check('cell.M',len(distinct)==r['M'] and sorted(distinct)==r['distinct_nonzero_candidates'],r['cell_id'])
  check('cell.zero',zero==r['zero_candidate_checks'],r['cell_id'])
  check('cell.memory',r['memory']['retained_word_records']==W and r['memory']['retained_word_bits']==L*W and r['memory']['distinct_nonzero_scalars']==len(distinct),r['cell_id'])
  expected_wrapper={'decoder_cap_test':1,'decoder_word_construct':W,'integer_word_bit':L*W,'integer_interval_round':W,'integer_mul':3*W,'integer_add':3*W,'integer_divide':W,'integer_compare':3*W,'public_candidate_check':nlegal,'candidate_set_lookup':nlegal}
  check('cell.wrapper_vector',norm(expected_wrapper)==norm(r['counts']['wrapper']),r['cell_id'])
  conv=r['counts']['conversion'];verify=r['counts']['verification']
  check('cell.inverse_conversion_paid',conv.get('order_inverse_call')==1 and conv.get('order_reduce')==2+2*nlegal and conv.get('order_mul',0)==2*nlegal and conv.get('order_euclid_iteration')==euclid_steps(b,order),r['cell_id'])
  scalarbits=0;groupadds=0
  for w in words:
   word_statuses[w['status']]+=1
   check('word.check_presence',all(type(v) is bool for v in w['public_checks'].values()) if w['legal'] else all(v is None for v in w['public_checks'].values()),r['cell_id'])
   if w['legal']:
    for scalar in (w['candidate_scalar_prime'],w['candidate_scalar']):scalarbits+=max(1,scalar.bit_length());groupadds+=max(1,scalar.bit_length())+scalar.bit_count()
  check('cell.both_checks_paid',verify.get('scalar_multiply_call',0)==2*nlegal and verify.get('point_equal',0)==2*nlegal and verify.get('scalar_multiply_bit',0)==scalarbits and verify.get('group_add_call',0)==groupadds,r['cell_id'])
  if cell=='t0.e0':check('cell.strict_embedding',r['status']==meta['original_status'] and r['scalar']==meta['original_scalar'],r['cell_id'])
  item=cell_aggregates.setdefault((cid,cell),{'attempts':0,'successes':0,'outcomes':Counter(),'counts':Counter(),'targets':set(),'recovered':set(),'zero':0})
  item['attempts']+=1;item['successes']+=success;item['outcomes'][r['status']]+=1;item['targets'].add(meta['target']);item['zero']+=zero;addflat(item['counts'],r['counts'])
  if success:item['recovered'].add(meta['target'])
  g=cell_global[cell];g['attempts']+=1;g['successes']+=success;g['retained'].add((cid,meta['target']));g['outcomes'][r['status']]+=1;addflat(g['counts'],r['counts']);g['words']+=W;g['legal']+=nlegal;g['M']+=r['M'];g['zero']+=zero;g['M0']+=r['M']==0;g['max_M']=max(g['max_M'],r['M']);g['max_words']=max(g['max_words'],W);g['retained_word_bits']+=L*W
  if success:g['recovered'].add((cid,meta['target']))
  add('worker.decoder.'+cell,r['counts']);statuses['worker.decoder.'+cell][r['status']]+=1
  total_words+=W;legal_total+=nlegal;zero_total+=zero;M0_rows+=r['M']==0
  if r['M']==0:
   addflat(M0_decoder_vectors,r['counts'])
   if not cell_witnesses.get('M0'):cell_witnesses['M0']={'path':RAW+'decoder-cells.jsonl','row':rowno,'cell_id':r['cell_id'],'word_count':W,'counts':r['counts'],'status':r['status']}
  for k,v in r['memory'].items():
   if type(v) is int:memory_max[k]=max(memory_max[k],v)
  cell_meta[r['cell_id']]={'M':r['M'],'counts_sha':sha(canonical(r['counts'])),'success':success,'zero':zero,'words':W,'legal':nlegal,'row':rowno}
 check('cell.count',len(cell_meta)==73728)
 # Compare every declared producer aggregate against own raw aggregation.
 analysis=reader.read(POST+'analysis.json')
 check('analysis.setup_components',setup_rows==analysis['setup_components'])
 for row in analysis['physical_trace_components_once']:
  key=(row['curve_id'],row['method']);check('analysis.physical_vector',dict(physical[key])==row['counts'],key)
 check('analysis.physical_count',len(physical)==len(analysis['physical_trace_components_once'])==72)
 for row in analysis['per_curve_six_cell']:
  own=cell_aggregates[(row['curve_id'],row['cell'])]
  check('analysis.cell_aggregate',own['attempts']==row['attempts'] and own['successes']==row['successes'] and dict(own['outcomes'])==row['outcomes'] and dict(own['counts'])==row['decoder_component_costs'] and len(own['targets'])==row['unique_targets_retained'] and len(own['recovered'])==row['unique_targets_recovered'] and own['zero']==row['zero_candidate_checks'],[row['curve_id'],row['cell']])
 check('analysis.cell_pair_count',len(cell_aggregates)==len(analysis['per_curve_six_cell'])==144)
 completion=reader.read(RAW+'engine-completion.json');summary=reader.read(RAW+'engine-summary.json')
 for inv in reader.inventory:
  if inv['canonical_relative_path'].startswith(RAW) and inv['canonical_relative_path'].endswith('.jsonl'):
   name=pathlib.PurePosixPath(inv['canonical_relative_path']).name;entry=completion['files'][name]
   check('raw.manifest_binding',inv['sha256']==entry['sha256'] and inv['bytes']==entry['bytes'] and inv['records']==entry['records'],name)
 check('raw.summary_coverage',summary['observed']=={'setups':len(setup_map),'intents':len(intents),'singles':n_single,'traces':len(traces),'cells':len(cell_meta)} and summary['status']=='complete' and not summary['errors'])
 exported=reader.read(POST+'export.json');export_matches=[]
 # Search exact known method metrics in the exported run records; preserve schema-specific scope.
 for r in exported['runs']:
  export_matches.append({'keys':list(r),'record':r})

 # Host decoder streams carry duplicated worker vectors plus separate host components.
 host_cell_rows=0;host_vectors=Counter()
 for rowno,r in reader.rows(POST+'host-cells.jsonl'):
  host_cell_rows+=1;meta=cell_meta[r['cell_id']]
  check('hostcell.worker_disclosure',sha(canonical(r['worker_counts']))==meta['counts_sha'],r['cell_id'])
  addflat(host_vectors,r['host_decoder_counts'])
 check('hostcell.count',host_cell_rows==len(cell_meta))

 refs=reader.read(POST+'references.json');host_totals=Counter();oracle_vectors=Counter();bsgs_setup=Counter();bsgs_setup_primitive=Counter();bsgs_online=Counter();bsgs_online_primitive=Counter();bsgs_status=Counter();bsgs_memory=Counter();uniform_vector=Counter();uniform_stream=Counter();uniform_info=Counter();null_stream=Counter();null_info=Counter();host_residual={};uniform_by_cell=collections.defaultdict(Counter)
 uniform_seen=set();null_statuses=Counter()
 for c in refs['curves']:
  cid=c['curve_id'];addflat(host_totals,c['independent_host_backend_counts']);addflat(oracle_vectors,c['independent_oracle_setup_counts']);local_components=Counter(c['independent_oracle_setup_counts']);ts=c['bsgs_targets']
  if ts:
   first=ts[0]['bsgs'];addflat(bsgs_setup,first['setup']);addflat(bsgs_setup_primitive,first['setup_primitive_vector']);local_components.update(first['setup_primitive_vector'])
   bsgs_memory['tables']+=1;bsgs_memory['stored_points_sum_across_tables']+=first['setup']['stored_points'];bsgs_memory['max_single_table_points']=max(bsgs_memory['max_single_table_points'],first['setup']['stored_points'])
   for target in ts:
    b=target['bsgs'];check('bsgs.shared_setup',b['setup']==first['setup'] and b['setup_primitive_vector']==first['setup_primitive_vector'],cid+'/'+target['target_id']);check('bsgs.warm_increment',b.get('warm_setup_increment')==0,cid)
    addflat(bsgs_online,b['online']);addflat(bsgs_online_primitive,b['online_primitive_vector']);local_components.update(b['online_primitive_vector']);bsgs_status[b['status']]+=1
  local_uniform=Counter()
  for rowno,r in reader.rows(POST+c['uniform_file']):
   cidcell=r['cell_id'];u=r['uniform'];meta=cell_meta[cidcell];m=meta['M'];eff=min(m,curves[cid]['model']['r']-1)
   check('uniform.unique_cell',cidcell not in uniform_seen,cidcell);uniform_seen.add(cidcell)
   check('uniform.M',r['M']==u['requested_M']==m and u['effective_M']==eff and len(u['guesses'])==len(u['checks'])==eff and len(set(u['guesses']))==eff,cidcell)
   check('uniform.public_checks_paid',u['public_equations']==eff and u['primitive_vector'].get('scalar_multiply_call',0)==eff,cidcell)
   check('uniform.conditioning',u['conditioning']=='M measured by candidate; M-determination work excluded here and must be charged',cidcell)
   check('uniform.zero',bool(u['success'])==any(u['checks']) and (m!=0 or (not u['guesses'] and not u['primitive_vector'])),cidcell)
   addflat(uniform_vector,u['primitive_vector']);addflat(local_uniform,u['primitive_vector']);addflat(uniform_stream,u['stream_counts'])
   uniform_info['rows']+=1;uniform_info['M0_rows']+=m==0;uniform_info['effective_guesses']+=eff;uniform_info['success_events']+=u['success'];uniform_info['stored_scalar_words_sum']+=u['stored_scalar_words'];uniform_info['max_stored_scalar_words']=max(uniform_info['max_stored_scalar_words'],u['stored_scalar_words'])
   uniform_by_cell[cidcell.rsplit('/',1)[1]]['success_events']+=u['success']
  local_components.update(local_uniform)
  residual={k:v-local_components[k] for k,v in c['independent_host_backend_counts'].items() if v!=local_components[k]}
  check('host.nonnegative_residual',all(v>=0 for v in residual.values()),cid)
  if ts:check('host.confirmation_reconciliation',not residual,cid)
  host_residual[cid]=residual
  if c['null_file']:
   n=reader.read(POST+c['null_file']);mask=n['mask_reference'];null_statuses[mask['status']]+=1
   addflat(null_stream,mask.get('stream_counts',{}));null_info['files']+=1;null_info['draws']+=mask.get('draw_count',0);null_info['packed_bytes_stored_sum']+=mask.get('packed_bytes_stored',0);null_info['max_one_curve_packed_bytes']=max(null_info['max_one_curve_packed_bytes'],mask.get('packed_bytes_stored',0))
   stats=n['retained_bank_statistics']
   if stats:
    null_info['label_lookups']+=stats['diagnostic_label_lookups'];check('null.lookup_arithmetic',stats['diagnostic_label_lookups']==mask['draw_count']*(n['bank_n']+(curves[cid]['model']['r'].bit_length()+1)*n['start_n']),cid)
 check('uniform.coverage',len(uniform_seen)==len(cell_meta)==73728)
 check('bsgs.coverage',bsgs_memory['tables']==24 and sum(bsgs_status.values())==1536)
 check('query.calibration',query_totals['worker.calibration.original']==344064)
 check('query.confirmation.original',query_totals['worker.confirmation.original']==172032)
 check('query.confirmation.incremental',query_totals['worker.confirmation.incremental']==172032)
 check('query.physical_total',n_single+sum(query_totals.values())==1033728)

 # Freeze independent aggregates and comparison witnesses, excluding sets from JSON.
 method_results={}
 for method,item in methods.items():
  method_results[method]={k:(dict(v) if isinstance(v,Counter) else v) for k,v in item.items() if k not in ('targets','recovered')}
  method_results[method].update(unique_targets_retained=len(item['targets']),unique_targets_recovered=len(item['recovered']))
 cells={}
 for cell,g in sorted(cell_global.items()):
  cells[cell]={k:(dict(v) if isinstance(v,Counter) else v) for k,v in g.items() if k not in ('retained','recovered')}
  V=len(g['recovered']);cells[cell]['unique_targets_retained']=len(g['retained']);cells[cell]['unique_targets_recovered']=V
  cells[cell]['decoder_component_cost_per_unique_recovered']={k:({'numerator':v,'denominator':V} if V else None) for k,v in g['counts'].items()}
 result={'schema':'independent-retained-cost-audit/v1','task_id':TASK,'joint_id':'J-cost','generated_at':utc(),'scientific_runs':0,'new_scientific_inputs':0,'producer_imports_calls':0,
 'coverage':{'curves':len(curves),'cohort_curve_proposals':cohort_proposals,'curve_proposal_reasons':dict(proposal_reasons),'target_duplicate_proposals':target_duplicates,'setups':len(setup_map),'single_rows':n_single,'intents':len(intents),'traces':len(traces),'decoder_cells':len(cell_meta),'host_cells':host_cell_rows,'physical_predicate_calls':n_single+sum(query_totals.values()),'queries_by_stream':dict(query_totals),'all_word_records':total_words,'legal_word_checks':legal_total,'zero_candidate_checks':zero_total,'M0_cell_rows':M0_rows,'cell_pairs':len(cell_aggregates)},
 'raw_worker_cost_groups':{k:dict(v) for k,v in sorted(groups.items())},'outcomes':{k:dict(v) for k,v in statuses.items()},'methods':method_results,'cells':cells,'word_statuses':dict(word_statuses),'memory_max_one_decoder_cell':dict(memory_max),'failed_trace_vectors':dict(failed_trace_vectors),'M0_decoder_vectors':dict(M0_decoder_vectors),'witnesses':cell_witnesses,
 'host':{'decoder_counts':dict(host_vectors),'backend_counts':dict(host_totals),'oracle_setup':dict(oracle_vectors),'bsgs_setup_once':dict(bsgs_setup),'bsgs_setup_primitive_once':dict(bsgs_setup_primitive),'bsgs_online':dict(bsgs_online),'bsgs_online_primitive':dict(bsgs_online_primitive),'bsgs_statuses':dict(bsgs_status),'bsgs_memory':dict(bsgs_memory),'uniform_primitive':dict(uniform_vector),'uniform_PRNG':dict(uniform_stream),'uniform':dict(uniform_info),'uniform_by_cell':{k:dict(v) for k,v in uniform_by_cell.items()},'null_PRNG':dict(null_stream),'null':dict(null_info),'null_statuses':dict(null_statuses),'calibration_mask_evaluator_residual_by_curve':host_residual},
 'checks':dict(checks),'issues':issues,'all_machine_checks_passed':not issues,'inventory':reader.inventory,'export_runs_for_comparison':export_matches,
 'missing_dimensions':['Independent full native worker counter replay is absent; arithmetic invariants here do not qualify all field counters.','RSS, simultaneous full cache/retained-word memory, Python/interpreter allocations, I/O, integer bit cost, currency and energy are not measured.','Abstract PRNG hash blocks are separate from physical entropy and hash-input bytes; only 32 output bytes per SHA-256 block are derivable.','Host final vectors omit separate mask-evaluator component serialization; calibration residual is disclosed, not assigned to BSGS or uniform.','Host verifier costs outside serialized decoder/orbit/reference vectors are not a complete host-process counter total.','Clock values are unqualified; no clock ratio or total attack cost is identified.'],
 'interpretation':'Bounded retained component accounting only. All observed cost groups have physical owners. No iid complete-restart inference, scalar mixed-unit sum, speedup, exponent or whole-claim verdict.'}
 jwrite('cost-results.json',result)
 print(json.dumps({'task_id':TASK,'coverage':result['coverage'],'all_machine_checks_passed':result['all_machine_checks_passed'],'issues':issues,'cell_outcomes':{k:{'success_events':v['successes'],'unique_targets_recovered':v['unique_targets_recovered'],'M0':v['M0'],'words':v['words']} for k,v in cells.items()},'host_uniform':result['host']['uniform'],'bsgs':result['host']['bsgs_statuses']},indent=2,sort_keys=True))
 return 0 if not issues else 2


def export_reconcile(result):
 checks=[]
 for row in result['export_runs_for_comparison']:
  r=row['record'];method=r['arm'].removeprefix('confirmation_');own=result['methods'][method];m=r['measurements']
  expected={'retained_attempts':own['attempts'],'retained_predicate_queries':own['queries'],'strict_recovered_events':own['statuses'].get('RECOVERED',0),'unique_targets_retained':own['unique_targets_retained'],'unique_targets_recovered':own['unique_targets_recovered']}
  numeric={k:v for k,v in m['counters'].items() if type(v) is int}
  checks.append({'method':method,'check':'exact counted metrics','passed':m['counted']==expected,'independent':expected})
  checks.append({'method':method,'check':'exact numeric component vector','passed':numeric==own['counts'],'primitive_dimensions':len(numeric)})
  for key in expected:
   mutant=dict(m['counted']);mutant[key]+=1
   checks.append({'method':method,'check':'known-false export mutation:'+key,'passed':mutant!=expected,'mutant_delta':{key:1}})
 return {'generated_at':utc(),'checks':checks,'all_passed':all(x['passed'] for x in checks),'no_source_reread':True,'raw_aggregate_source':'cost-results.json from preserved first invocation'}

# The SVG is editable source retained here; there are no external design assets.
def diagram_source():
 return '''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="185" viewBox="0 0 1100 185">
<rect width="1100" height="185" fill="#f5f8fb"/>
<g font-family="DejaVu Sans, sans-serif" font-size="15" fill="#17364f">
<rect x="12" y="17" width="238" height="111" rx="8" fill="#e2edf4" stroke="#507a96"/>
<text x="28" y="44" font-weight="bold">Shared preparation</text><text x="28" y="72">48 curves; 216 arm setups</text><text x="28" y="99">Rejected proposals stay paid</text>
<rect x="278" y="17" width="260" height="111" rx="8" fill="#e6f2eb" stroke="#527f67"/>
<text x="294" y="44" font-weight="bold">Two physical evaluators</text><text x="294" y="72">172,032 confirmation queries</text><text x="294" y="99">per method; each runs once</text>
<rect x="566" y="17" width="248" height="111" rx="8" fill="#fff0dc" stroke="#a77d3d"/>
<text x="582" y="44" font-weight="bold">Six decoder cell views</text><text x="582" y="72">Shared incremental trace</text><text x="582" y="99">3,068,802 words, all retained</text>
<rect x="842" y="17" width="246" height="111" rx="8" fill="#ede8f6" stroke="#80699b"/>
<text x="858" y="44" font-weight="bold">Separate host references</text><text x="858" y="72">BSGS setup once per curve</text><text x="858" y="99">Uniform M is conditional</text>
<path d="M252 73 H273 M540 73 H561 M816 73 H837" stroke="#526779" stroke-width="2"/>
<text x="16" y="159" font-size="14">Physical ownership determines cost. Logical rows and repeated setup disclosures do not multiply shared work.</text>
</g></svg>'''

def render_report():
 import typst
 result=parse((OUT/'cost-results.json').read_bytes());extra=export_reconcile(result);jwrite('export-reconciliation.json',extra)
 if not extra['all_passed']:raise ValueError('export reconciliation failed')
 verdict='inconclusive'
 G=result['raw_worker_cost_groups'];H=result['host'];C=result['coverage']
 def primitive(group,unit):return sum(v for k,v in G[group].items() if k.rsplit('/',1)[-1]==unit)
 def sums(names,unit):return sum(primitive(n,unit) for n in names)
 def nums(n):return f'{n:,}'
 cost_rows=[
  ('Base + target coordinate preparation',['worker.base_sampling','worker.target_sampling']),
  ('Prepared base/circuit setup',['worker.prepared_setup']),
  ('Calibration coordinate generation',['worker.calibration_single_sampling','worker.calibration_trace_sampling']),
  ('Calibration evaluator + traces',['worker.calibration_single_evaluation','worker.calibration.original']),
  ('Confirmation original',['worker.confirmation.original']),
  ('Confirmation incremental',['worker.confirmation.incremental']),
  ('All six physical decoder enumerations',[k for k in G if k.startswith('worker.decoder.')])]
 table=[]
 for label,names in cost_rows:table.append([label]+[nums(sums(names,u)) for u in ['group_add_call','field_mul','field_inverse']])
 cost_md='\n'.join('| '+' | '.join(r)+' |' for r in table)
 cell_rows=[]
 for cell,g in result['cells'].items():cell_rows.append([cell,nums(g['words']),nums(g['legal']),nums(g['M0']),str(g['successes']),str(g['unique_targets_recovered'])])
 cell_md='\n'.join('| '+' | '.join(r)+' |' for r in cell_rows)
 source_hashes={pathlib.PurePosixPath(i['canonical_relative_path']).name:i['sha256'] for i in result['inventory']}
 md=f'''# Fully paid cost accounting — {TASK}

**J-cost: inconclusive for a fully paid end-to-end total.** Retained component bookkeeping agrees in every inspected row and exported aggregate. Missing native and full-process dimensions prevent a stronger conclusion. This is an independent deterministic audit of RUN-ECDLP-939237 / EXP-ECDLP-080f41, with zero new scientific trials, inputs, queries or producer calls.

## Observations

The audit streamed all 216 setups, 345,600 single-point records, 36,864 intents, 36,864 physical trace records, 73,728 decoder cells, 73,728 host cells, 48 uniform files and 24 null files. Raw JSONL digests, byte counts and row counts match the completion manifest. All 144 curve/cell aggregates, 72 curve/method vectors, 216 setup disclosures and both export method count/vector records match independent sums. The 5,401,187 primary checks and {len(extra['checks'])} export/sensitivity checks pass. The original 21 fixed public controls pass; executed source, command output and actual times are retained in checks.json.

There are 1,033,728 physical predicate calls: 345,600 calibration singles + 344,064 calibration trace calls + 172,032 original and 172,032 incremental confirmation calls. Six cells reuse one incremental trace. Intent draw/sampling fields are duplicated in trace records; their physical work is charged once from intents. Shared logical calibration coordinates regenerated by eight arms remain charged on all actual executions.

![Physical cost ownership](diagram.svg)

## Paid worker vectors

Each column has its own unit; columns overlap through nested arithmetic and must never be added. These are source instrumented abstract event counts with algebraic checks, not native replay or machine costs. Common curve certification/proposal integer work and RNG have separate vectors in checks.json.

| Physical component | Group-add calls | Field multiplications | Field inversions |
| --- | ---: | ---: | ---: |
{cost_md}

Curve generation retains 49,155 proposals: 46,596 field rejects, 2,511 order rejects and 48 accepted curves. The target ledger retains 19 duplicate proposals. All generation, base and target sampling vectors are kept separately. A curve is generated once; prepared setup is once per actual curve/arm cache lifetime. Setup cannot be divided away from the batch.

## Decoder outcomes and paid failure work

| Cell | Words | Legal checks | M=0 rows | Success events | Unique targets recovered |
| --- | ---: | ---: | ---: | ---: | ---: |
{cell_md}

All 3,068,802 word records were inspected. For every legal word both public check invocations, scalar conversion, scalar-bit and group-add counts agree with the retained scalar/check schedule. The 1,140,281 legal words include 452 zero-candidate checks. All 15,820 M=0 cell rows retain paid inversion/cap/list work; they also depend on already-paid trace and preparation work. The smallest witness is decoder-cells.jsonl row 1, confirmation-A-10-0/target0000/rep0/t0.e0: one empty word, M=0, one inverse and the full wrapper work remain recorded.

Both strict methods have 12,288 attempts, 172,032 queries and 1,536 retained targets: 4 recovered, 4,469 rejected, 7,688 empty and 127 undefined attempts. No failure work was omitted. Per-cell cost divided by unique targets recovered is descriptive; component fractions are in checks.json. Repeated successful blindings do not create more unique recovered targets. Zero-success per-curve cells have undefined cost-per-success, not mathematical q=0.

## Host work and matched comparisons

BSGS has 24 setup instances, 1,536 successful online target solves and 2,594 stored table points summed across tables (largest individual table 249 points). The host primitive vector charges setup 3,338 group-add calls once, then online 141,042 calls; these are separate from the higher-level setup/online counters and the full-orbit oracle. Setup disclosed in 64 target rows is not charged 64 times. Cold and warm policies stay separate.

The conditional uniform reference has 73,728 calls, 1,139,829 distinct nonzero guesses and 404 success events; its 21,464,021 host group-add calls exclude candidate M-determination. That work remains paid in the candidate path. Its 15,820 M=0 calls are empty conditional references, not zero-cost candidate attempts. The 24 null files retain 24,552 orientation draws, 198,521,334 SHA-256 blocks and 88,190,784 label lookups. Hash blocks, lookups, group work, stored entries and bytes are distinct dimensions. Calibration mask/evaluator residual vectors are disclosed without inventing component attribution.

An operational solver choosing one method/cell differs from this study, which physically ran both evaluators, all six decoders, calibration and host controls. A cold comparison includes curve/setup/target preparation. Warm reuse states the actual number of shared targets and table memory. Same curve/target distribution, success/stop policy, units/backend, memory and censoring are required. Worker and host field/group definitions are different; no automatic ratio is justified. No P1/3 reference, speedup or exponent is inferred.

## Inference and limitations

The identity S+T+E[C_complete]/q requires iid complete fresh restarts with fixed conditional law, q>0 and finite expected cost. Repeated cells and heterogeneous curves are not iid observations; caps and right censoring retain paid work and do not identify q. No expected restart cost is inferred here.

Native worker counter replay, full host-verifier process cost, RSS and simultaneous full-cache memory, byte representations, interpreter/integer/I/O work, energy/currency and qualified clocks are absent. The maximum retained decoder-cell payload is {result['memory_max_one_decoder_cell'].get('retained_word_records',0)} words / {result['memory_max_one_decoder_cell'].get('retained_word_bits',0)} bits; this is not RSS. Some branches have no retained case. These gaps leave J-cost inconclusive for a fully paid total while the stated retained component identities hold. No scientific status changes.

Evidence: canonical raw directory runs/RUN-ECDLP-939237/modal/collected/raw; host references postrun-from-view-346631; exact paths, row witnesses, full vectors and SHA-256 inventory in checks.json. Decoder raw SHA-256 {source_hashes['decoder-cells.jsonl']}. No producer or sibling report was used. Original protocol/spec/trial historical embedded metadata exposure is disclosed in the sealed derivation.
'''
 views=parse((OUT/'operational-views.json').read_bytes()) if (OUT/'operational-views.json').exists() else build_operational_views(result)
 native_reader=Reader();native_receipt=native_reader.read(RUN+'execution-receipt.json');native_raw=native_reader.read(RUN+'raw-result.json')
 native_facts={'status':native_receipt['status'],'check_returncode':native_receipt['check_returncode'],'published':native_receipt['published'],'driver_returncode':native_receipt['returncode'],'scientific_validity':native_raw['scientific_validity'],'source_inventory':native_reader.inventory}
 jwrite('native-receipt-facts.json',native_facts)
 md+='\nNative receipt is preserved: status='+native_facts['status']+', checker return code='+str(native_facts['check_returncode'])+', published='+str(native_facts['published']).lower()+', scientific validity='+native_facts['scientific_validity']+'. This audit does not repair or promote that execution status.\n'
 op_md,op_typst=operational_report_sections(views)
 md+=op_md
 (OUT/'report.md').write_text(md)
 (OUT/'diagram.svg').write_text(diagram_source())
 def typst_rows(rows):return ',\n'.join('['+cell.replace('%','\\%')+']' for row in rows for cell in row)
 typst_text=r'''#set page(paper: "a4", margin: (x: 13mm, y: 13mm), numbering: "1 / 1")
#set text(font: "DejaVu Sans", size: 9pt)
#set par(justify: false, leading: 0.52em)
#set heading(numbering: none)
#show heading: set text(fill: rgb("#17364f"))
#let small(body) = text(size: 8pt, fill: rgb("#4d5b67"), body)
#text(size: 17pt, weight: "bold", fill: rgb("#17364f"))[Paid cost accounting]
#v(2mm)
#text(size: 9pt)[TASK-20261030-f55ebb · J-cost · RUN-ECDLP-939237 · 30 October 2026]
#v(2mm)
#block(fill: rgb("#fff0dc"), inset: 8pt, radius: 4pt)[*Inconclusive for a fully paid end-to-end total.* Retained component bookkeeping matches all checked rows and exported aggregates. Native and full-process dimensions remain missing. No new scientific trial, input or producer call.]
== Physical ownership and coverage
All 216 setups, 345,600 singles, 36,864 intents/traces, 73,728 decoder/host cells, 48 uniform files and 24 null files were inspected. Raw digests, byte counts and row counts match the completion manifest. All 144 curve/cell aggregates, 72 curve/method vectors, setup disclosures and both export vectors match independent sums. The 5,401,187 primary checks and EXPORTCHECKS export/sensitivity checks pass; 21 original fixed controls pass.
#image("diagram.svg", width: 100%)
#small[Six decoder views reuse one incremental trace. Original and incremental are physical streams. Repeated intent fields are charged once; calibration coordinates regenerated across eight arms stay physically paid.]
== Retained worker vectors
#small[Unit of each numeric column: the named abstract event. Columns contain nested arithmetic; never add columns or convert them to elapsed time.]
#table(columns: (2.4fr, 1fr, 1fr, 1fr), inset: 4pt, stroke: 0.4pt + rgb("#c5d0d9"), align: (left,right,right,right),
 [*Physical component*], [*Group-add calls*], [*Field mult.*], [*Field inversions*],
WORKERROWS
)
There are *1,033,728 predicate calls*: 345,600 calibration singles + 344,064 calibration trace calls + 172,032 confirmation calls per method. Curve generation retains 49,155 proposals (46,596 field rejects; 2,511 order rejects; 48 accepted); target preparation retains 19 duplicates. Common generation integer/RNG vectors stay separate.
== What remains paid
Curve generation once per curve; prepared setup once per actual curve/arm cache lifetime; target preparation; every actual blinding, query, word, conversion and both public checks. All 15,820 M=0 cell rows retain their paid work. Empty, undefined, capped and failed work is preserved. A solver choosing one method/cell needs a separately stated operational path; this study physically paid both methods, six decoders, calibration and host references.
#small[Derived from the same retained EXP-ECDLP-080f41 data only. Full vectors, exact row witnesses, source bytes, commands and hash inventory: checks.json. The report source and editable diagram are embedded in audit.py.]
#pagebreak()
#text(size: 15pt, weight: "bold", fill: rgb("#17364f"))[Outcomes, references and limits]
== All decoder work retained
#table(columns: (0.7fr,1.05fr,1.05fr,0.85fr,0.8fr,0.9fr), inset: 4pt, stroke: 0.4pt + rgb("#c5d0d9"), align: (left,right,right,right,right,right),
 [*Cell*], [*Words*], [*Legal checks*], [*M=0 rows*], [*Success events*], [*Unique targets*],
CELLROWS
)
All *3,068,802 words* were inspected; the *1,140,281 legal checks* include 452 zero candidates. For every legal candidate, both equation invocations and conversion/scalar-bit/group-add counts match the retained schedule. Decoder row 1 has one empty word and M=0 but still pays one inverse and wrapper work. Per-cell component cost / unique targets recovered is descriptive; repeat successes on one target do not enlarge that denominator.
Both strict methods retain 12,288 attempts and 1,536 targets: 4 recoveries, 4,469 final-check rejects, 7,688 empty and 127 undefined. Failed work stays in the numerator. Zero observed recoveries do not prove q=0.
== Host vectors: separate units and purposes
*BSGS:* 24 tables; 1,536 successful target solves. Host primitive setup = *3,338 group-add calls once*; online = *141,042*. Setup is disclosed in 64 rows per curve but charged once. Stored table points sum to 2,594; largest individual table 249. Table entries do not determine bytes or peak RSS. Cold setup and warm reuse remain separate.
*Conditional uniform:* 73,728 calls; 1,139,829 distinct guesses; 404 success events; 21,464,021 host group-add calls. Candidate M-determination is excluded from this reference vector and remains paid on the candidate path. The 15,820 empty uniform calls do not make candidate attempts free. No standalone-solver or exchangeable-null interpretation follows.
*Null/orbit work:* 24 null files retain 24,552 draws, 198,521,334 SHA-256 blocks and 88,190,784 label lookups; oracle setup is separately recorded. Hash blocks, lookups, memory entries, bytes and group operations are distinct. Calibration mask/evaluator residual vectors are disclosed.
== Inference boundary
S + T + E[C_complete]/q requires iid complete fresh restarts with a fixed conditional law, q > 0 and finite mean cost. Shared cells, targets and heterogeneous curves do not supply iid restart observations. Right censoring preserves paid work and does not identify q. No expected retry cost is inferred.
A comparison must match public inputs/target distribution, success/stop policy, cold/warm reuse, memory, backend/primitive units and failures/censoring. Worker and host definitions differ. No speedup, P1/3 baseline, exponent or scientific status conclusion is supplied.
== Why J-cost remains inconclusive
Missing: independent native worker counter replay; full host-verifier process cost; simultaneous cache/retained memory and RSS; entry/byte representations; interpreter, integer and I/O work; currency/energy; qualified clocks. One decoder cell retains at most MAXWORDS word records / MAXBITS bits, which is an abstract payload measure. Unobserved branches remain untested. The retained component identities hold within these limits; a fully paid total is not identified.
#small[Evidence: RUN-ECDLP-939237 raw tables and postrun-from-view-346631 host streams. Exact canonical paths, SHA-256 values and actual read/seal/release chronology are in checks.json and read-attestation.yaml. Historical metadata embedded in original frozen protocol/spec/trial was permitted and disclosed. No sibling report was read.]
'''
 typst_text=typst_text.replace('WORKERROWS',typst_rows(table)).replace('CELLROWS',typst_rows(cell_rows)).replace('EXPORTCHECKS',str(len(extra['checks']))).replace('MAXWORDS',str(result['memory_max_one_decoder_cell'].get('retained_word_records',0))).replace('MAXBITS',str(result['memory_max_one_decoder_cell'].get('retained_word_bits',0)))
 typst_text=typst_text.replace('No new scientific trial, input or producer call.]','No new scientific trial, input or producer call. Native receipt remains '+native_facts['status']+'; checker RC '+str(native_facts['check_returncode'])+'; published='+str(native_facts['published']).lower()+'.]')
 typst_text+=op_typst
 (OUT/'report.typ').write_text(typst_text)
 typst.compile(str(OUT/'report.typ'),output=str(OUT/'report.pdf'))
 jwrite('render-metadata.json',{'generated_at':utc(),'joint_id':'J-cost','verdict':verdict,'pdf_sha256':sha((OUT/'report.pdf').read_bytes()),'typst_sha256':sha(typst_text.encode()),'diagram_sha256':sha((OUT/'diagram.svg').read_bytes()),'report_md_sha256':sha(md.encode()),'export_reconciliation':extra})
 print(json.dumps({'rendered_at':utc(),'pdf_bytes':(OUT/'report.pdf').stat().st_size,'pdf_sha256':sha((OUT/'report.pdf').read_bytes()),'export_checks':len(extra['checks']),'export_all_passed':extra['all_passed'],'verdict':verdict},indent=2))
 return 0


def build_operational_views(first_result):
 """Aggregate digest-bound, prior raw-verified vectors; no raw or producer rerun."""
 reader=Reader();analysis=reader.read(POST+'analysis.json');cohort=reader.read(COL+'cohort-ledger.json')
 original_hashes={x['canonical_relative_path']:x['sha256'] for x in first_result['inventory']}
 for r in reader.inventory:assert r['sha256']==original_hashes[r['canonical_relative_path']], 'prior verified source changed'
 assert first_result['all_machine_checks_passed'] and first_result['checks']['analysis.cell_aggregate/checked']==144 and first_result['checks']['analysis.physical_vector/checked']==72
 physical={(r['curve_id'],r['method']):r['counts'] for r in analysis['physical_trace_components_once']}
 setup={(r['curve_id'],r['arm_id']):flat(r['counts']) for r in analysis['setup_components']}
 cells={(r['curve_id'],r['cell']):r for r in analysis['per_curve_six_cell']}
 shared={}
 def prefixed(c,vec,prefix):
  for k,v in vec.items():c[prefix+'/'+k]+=v
 for c in cohort:
  if not c['curve_id'].startswith('confirmation-'):continue
  v=Counter();prefixed(v,c['counts'],'curve_generation');prefixed(v,c['base_sampling']['counts'],'base_sampling')
  for t in c['target_sampling']:prefixed(v,t['sampling']['counts'],'target_coordinate_sampling')
  shared[c['curve_id']]={'input_generation':dict(v),'prepared_setup':setup[(c['curve_id'],'circuit2.a1')],'intent_rng':Counter()}
 del cohort
 for _,r in reader.rows(RAW+'attempt-intents.jsonl'):
  if r['curve_id'] in shared:shared[r['curve_id']]['intent_rng'].update(r['draw']['counts'])
 assert reader.inventory[-1]['sha256']==original_hashes[RAW+'attempt-intents.jsonl']
 unknown={'qualified_clock_seconds':None,'native_counter_replay':None,'native_RSS_bytes':None,'full_interpreter_integer_IO_cost':None,'currency':None,'energy':None}
 def finish_view(v):
  V=v['unique_targets_recovered']
  for key in ['online_cost_vector','public_input_solver_component_vector','paid_cohort_reproduction_vector']:
   v[key]=dict(v[key]);v[key+'_per_unique_recovered']={k:({'numerator':x,'denominator':V} if V else None) for k,x in v[key].items()}
  v['unknown_dimensions']=unknown;v['zero_hit_cost_ratio_undefined']=V==0
  return v
 def mkview(cid,name,online,row):
  v={'choice':name,'attempts':row['attempts'],'success_events':row['successes'],'unique_targets_retained':row['unique_targets_retained'],'unique_targets_recovered':row['unique_targets_recovered'],'outcomes':row['outcomes'],'online_cost_vector':Counter(),'public_input_solver_component_vector':Counter(),'paid_cohort_reproduction_vector':Counter()}
  prefixed(v['online_cost_vector'],online,'online')
  v['public_input_solver_component_vector'].update(v['online_cost_vector'])
  prefixed(v['public_input_solver_component_vector'],shared[cid]['prepared_setup'],'prepared_setup_once')
  prefixed(v['public_input_solver_component_vector'],shared[cid]['intent_rng'],'blinding_rng_once')
  v['paid_cohort_reproduction_vector'].update(v['public_input_solver_component_vector'])
  prefixed(v['paid_cohort_reproduction_vector'],shared[cid]['input_generation'],'study_input_generation_once')
  return finish_view(v)
 curve_views={}
 for cid in sorted(shared):
  strict=cells[(cid,'t0.e0')];choices={}
  choices['original']=mkview(cid,'original',physical[(cid,'original')],strict)
  choices['incremental_strict']=mkview(cid,'incremental_strict',physical[(cid,'incremental')],strict)
  for cell in ['t0.e0','t0.e2','t1.e0','t1.e2','t2.e0','t2.e2']:
   online=Counter();prefixed(online,physical[(cid,'incremental')],'embedded_incremental_strict');prefixed(online,cells[(cid,cell)]['decoder_component_costs'],'selected_decoder')
   choices['incremental_plus_'+cell]=mkview(cid,'incremental_plus_'+cell,online,cells[(cid,cell)])
  curve_views[cid]={'shared_components':{k:dict(v) for k,v in shared[cid].items()},'choices':choices}
 def aggregate(cids):
  choices={}
  for choice in next(iter(curve_views.values()))['choices']:
   a={'choice':choice,'attempts':0,'success_events':0,'unique_targets_retained':0,'unique_targets_recovered':0,'outcomes':Counter(),'online_cost_vector':Counter(),'public_input_solver_component_vector':Counter(),'paid_cohort_reproduction_vector':Counter()}
   for cid in cids:
    v=curve_views[cid]['choices'][choice]
    for k in ['attempts','success_events','unique_targets_retained','unique_targets_recovered']:a[k]+=v[k]
    a['outcomes'].update(v['outcomes'])
    for k in ['online_cost_vector','public_input_solver_component_vector','paid_cohort_reproduction_vector']:a[k].update(v[k])
   a['outcomes']=dict(a['outcomes']);choices[choice]=finish_view(a)
  return {'curves':list(cids),'choices':choices}
 panels={p:aggregate([cid for cid in curve_views if cid.startswith(p+'-')]) for p in ['confirmation-A','confirmation-B']}
 view={'schema':'retained-operational-cost-views/v1','task_id':TASK,'generated_at':utc(),'basis':'Every reused analysis setup/curve/method/cell vector was compared to independently streamed raw sums in the preserved first invocation. Exact analysis/cohort/intent digests are rechecked here; no producer function is imported or called.',
 'definitions':{'original':'Actually executed strict original evaluator online vector.','incremental_strict':'Actually executed strict incremental evaluator, including its interval reduction, inversion and both checks when legal.','incremental_plus_t1.e2':'Registered primary: entire actually executed incremental strict attempt PLUS actual t1.e2 decoder/conversion/check vector. Embedded strict work is not optimized away. Other cells use the same construction.','public_input_solver_component_vector':'Chosen online path + one curve/arm prepared setup + one retained blinding RNG draw per attempt. Blinded target scalar multiplication is already in online. Original and incremental streams are alternative views, not added.','paid_cohort_reproduction_vector':'The public-input component view + actual curve generation/certification, base sampling and target-coordinate generation once. Input generation is study overhead when E,G,Q,r are already supplied, and is separately exposed so a cohort-reproduction cost cannot make it free.','cost_per_unique_recovered':'Exact numerator / number of unique target IDs recovered within that curve/panel/scope. The same fixed 64 targets*8 attempts are retained per curve; repeated hits do not create more unique targets. Every zero-hit curve yields null, not q=0. This is descriptive, not E[C]/q.'},
 'curve_views':curve_views,'panel_views':panels,'all_confirmation':aggregate(list(curve_views)),'source_inventory':reader.inventory,'unknown_dimension_reasons':first_result['missing_dimensions'],'baseline_comparability':'Same retained public targets and attempt schedule; different decoder/success behavior and unqualified counters prevent a runtime or expected-cost advantage claim. Backend and primitive dimensions remain separate.'}
 jwrite('operational-views.json',view)
 return view

def operational_report_sections(view):
 def count(v,unit,key='public_input_solver_component_vector'):return sum(x for k,x in v[key].items() if k.rsplit('/',1)[-1]==unit)
 def frac(v,unit):
  d=v['unique_targets_recovered'];return f"{count(v,unit):,}/{d}" if d else 'undefined (0)'
 names={'original':'Strict original','incremental_strict':'Incremental strict','incremental_plus_t1.e2':'Incremental + primary t1.e2'}
 rows=[]
 for k,label in names.items():
  v=view['all_confirmation']['choices'][k];rows.append([label,f"{count(v,'group_add_call'):,}",f"{count(v,'field_mul'):,}",f"{count(v,'field_inverse'):,}",str(v['unique_targets_recovered']),frac(v,'group_add_call')])
 panelrows=[]
 for p,a in view['panel_views'].items():
  for k in ['original','incremental_plus_t1.e2']:
   v=a['choices'][k];panelrows.append([p.removeprefix('confirmation-'),names[k],str(v['success_events']),str(v['unique_targets_recovered']),frac(v,'group_add_call')])
 zero_baseline=sum(c['choices']['original']['unique_targets_recovered']==0 for c in view['curve_views'].values())
 zero_primary=sum(c['choices']['incremental_plus_t1.e2']['unique_targets_recovered']==0 for c in view['curve_views'].values())
 examples=[]
 for cid in ['confirmation-A-10-0','confirmation-A-10-1','confirmation-B-16-3']:
  c=view['curve_views'][cid]['choices'];examples.append([cid,frac(c['original'],'group_add_call'),frac(c['incremental_plus_t1.e2'],'group_add_call')])
 def mdtable(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(r)+' |' for r in rows)
 md='\n## Retained operational component views\n\nThese alternative paths charge the chosen online execution plus once-paid prepared setup and blinding RNG. Blinded target multiplication is already in online. The registered primary includes the entire actually executed incremental strict reduction/conversion/check work and the actual t1.e2 decoder; it does not assume a future optimized program. The original evaluator and the other five decoder cells are not added to that path. The study physically executed all streams and all cells.\n\n'+mdtable(['Choice','Group-add calls','Field multiplications','Field inversions','Unique recovered','Group calls / unique recovered'],rows)+'\n\n'+mdtable(['Panel','Choice','Success events','Unique recovered','Group calls / unique recovered'],panelrows)+f'\n\nAll 24 curve vectors, two panel vectors, global vectors and six selected-cell views are retained in checks.json. Zero-hit curves: original {zero_baseline}/24; primary {zero_primary}/24. Their cost-per-recovered-target values are null. Examples:\n\n'+mdtable(['Curve','Original group calls / recovered','Primary group calls / recovered'],examples)+'\n\nA separate paid-cohort-reproduction vector additionally charges actual curve certification/generation, base sampling and target-coordinate generation; those remain study input-generation overhead for a solver given public E,G,Q,r. All primitive dimensions and shared-component vectors are preserved. Exact fractions use unique-target denominators, not successful attempt events. This is a descriptive observed component comparison with unmatched recovery behavior and missing native/full-process costs; it is not an expected-cost or runtime advantage.\n'
 def tc(rows):return ',\n'.join('['+c+']' for r in rows for c in r)
 typ=r'''
#pagebreak()
#text(size: 15pt, weight: "bold", fill: rgb("#17364f"))[Original and primary component views]
== Alternative operational paths
The original baseline and candidate use the same retained public inputs and 512 attempts per curve. Each component view charges chosen online work, prepared setup once per curve/arm, and one blinding RNG draw per attempt. Target blinding multiplication is already online. The registered primary includes *all actually executed incremental strict work plus the t1.e2 decoder*. Its embedded strict interval reduction, inversion and public checks remain paid; no optimized future program is imagined.
The original stream and the other five decoders are excluded from this one chosen path. The physical study total keeps all streams. Input-generation overhead is a separate cost vector.
== Global observed worker vectors
#small[Named abstract events only. Columns are nested and cannot be added. Denominator is unique target IDs recovered, not successful blindings. All 1,536 targets remain in each schedule.]
#table(columns: (1.7fr,1fr,1fr,1fr,0.65fr,1.2fr), inset: 4pt, stroke: 0.4pt + rgb("#c5d0d9"), align: (left,right,right,right,right,right),
 [*Choice*],[*Group calls*],[*Field mult.*],[*Field inversions*],[*Unique*],[*Group / unique*],
OPROWS
)
== Separate confirmation panels
#table(columns: (0.45fr,1.8fr,0.85fr,0.85fr,1.4fr), inset: 4pt, stroke: 0.4pt + rgb("#c5d0d9"), align: (left,left,right,right,right),
 [*Panel*],[*Choice*],[*Events*],[*Unique*],[*Group / unique*],
PANELROWS
)
== Curve scope and zero recovery
All 24 curve vectors and every selected-cell view are retained with exact numerators and unique-target denominators in checks.json. Original has ZBASE zero-hit curves; primary has ZPRIMARY. Every such ratio is null / undefined; zero observations are not q=0.
#table(columns: (1.2fr,1.1fr,1.1fr), inset: 4pt, stroke: 0.4pt + rgb("#c5d0d9"), align: (left,right,right),
 [*Curve*],[*Original group / unique*],[*Primary group / unique*],
EXAMPLEROWS
)
== Cold scope and what comparison establishes
The public-input component vector adds prepared setup exactly once. A separate *paid cohort reproduction* vector also charges actual curve generation/certification, base sampling and target-coordinate generation. When public E,G,Q,r are already supplied these are study input-generation costs; they remain visible and paid in the study. All shared components are exposed separately.
These fractions describe observed component work across different recovery behavior. They do not estimate repeated-solver E[C]/q. Unqualified worker counters, missing native/full-process/memory costs, and unmatched complete-success policies prevent a runtime or expected-cost advantage conclusion. Worker/host units remain separate.
#small[Reaggregation used digest-bound serialized curve/method/cell vectors already independently checked against every raw record in the first invocation, plus the same retained cohort and intent ledgers. No producer code was imported or called; no trial, entropy or new input was generated. Full command/source history is preserved in checks.json.]
'''
 typ=typ.replace('OPROWS',tc(rows)).replace('PANELROWS',tc(panelrows)).replace('EXAMPLEROWS',tc(examples)).replace('ZBASE',str(zero_baseline)).replace('ZPRIMARY',str(zero_primary))
 return md,typ

if __name__=='__main__':
 if sys.argv[1:]==['audit']:raise SystemExit(main_audit())
 if sys.argv[1:]==['render']:raise SystemExit(render_report())
 raise SystemExit('use audit or render')
