"""Fixed schema and cross-field checks only; never imports an experimental runner."""
from pathlib import Path
from fractions import Fraction
import copy,datetime,hashlib,json,math,resource,signal,time
import jsonschema,yaml
HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/'schema.json').read_text())
CONTRACT=yaml.safe_load((HERE/'EXP-ECDLP-1b1b99.yaml').read_text())
C=CONTRACT['effective_contract']['cost_contract']
VALIDATOR=jsonschema.Draft202012Validator(SCHEMA,format_checker=jsonschema.FormatChecker())
CASES=[]

def strict_json(text):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('duplicate_key')
            d[k]=v
        return d
    def constant(_):raise ValueError('nonfinite_number')
    return json.loads(text,object_pairs_hook=pairs,parse_constant=constant)

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

def finite(value):
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('nonfinite_number')
    if isinstance(value,dict):
        for v in value.values():finite(v)
    elif isinstance(value,list):
        for v in value:finite(v)

def numeric_profile(value,path=()):
    if isinstance(value,float) and path not in [('run','timing','wall_seconds'),('run','resources','cpu_seconds')]:raise ValueError('noncanonical_integer_lexeme')
    if isinstance(value,dict):
        for key,item in value.items():numeric_profile(item,path+(key,))
    elif isinstance(value,list):
        for index,item in enumerate(value):numeric_profile(item,path+(index,))

def validate_record(d):
    finite(d);numeric_profile(d);VALIDATOR.validate(d)
    if d.get('record_type')=='raw_cost':
        if d['scope']=='scaffolding' and d['scaffold_kind']!=d['component']:raise ValueError('scaffold_component_mismatch')
        if d['charge_kind']=='exclusive_leaf':
            if any(d[k]=='derived_rollup' for k in ['CPU_unavailable_reason','wall_unavailable_reason','RSS_unavailable_reason','operation_counts_unavailable_reason']):raise ValueError('exclusive_rollup_reason')
        if len(d['source_leaf_ids'])!=len(set(d['source_leaf_ids'])):raise ValueError('duplicate_leaf')
        cap=d['capture_interval']
        for start,end in [('cpu_started_ns','cpu_finished_ns'),('wall_started_ns','wall_finished_ns')]:
            if (cap[start] is None)!=(cap[end] is None):raise ValueError('partial_clock_pair')
            if cap[start] is not None and cap[end]<cap[start]:raise ValueError('clock_reversed')
        if d['charge_kind']=='exclusive_leaf' and d['status'] in ['complete','below_resolution']:
            if cap['reason'] is not None or any(cap[k] is None for k in ['process_group_id','cpu_started_ns','cpu_finished_ns','wall_started_ns','wall_finished_ns']):raise ValueError('missing_complete_capture')
    elif d.get('record_type')=='allocation_edge':
        w=d['weight']
        if math.gcd(w['numerator'],w['denominator'])!=1:raise ValueError('noncanonical_weight')
        for v,r in [('allocated_CPU_nanoseconds','allocated_CPU_unavailable_reason'),('allocated_wall_nanoseconds','allocated_wall_unavailable_reason')]:
            if (d[v] is None)!=(d[r] is not None):raise ValueError('allocation_reason_mismatch')
        if d['strategy_view']=='actual_only_scaffolding':
            if d['target']['raw_cost_row_id']!=d['raw_cost_row_id'] or w!={'numerator':1,'denominator':1} or d['reason_code']!='actual_only':raise ValueError('actual_only_identity')
    else:
        r=d['run'];res=r['resources']
        for v,reason in [('peak_rss_bytes','peak_rss_unavailable_reason'),('cpu_nanoseconds','cpu_unavailable_reason')]:
            if (res[v] is None)!=(res[reason] is not None):raise ValueError('resource_reason_mismatch')
        if (res['cpu_seconds'] is None)!=(res['cpu_nanoseconds'] is None):raise ValueError('cpu_display_missing')
        if datetime.datetime.fromisoformat(r['timing']['finished_at'].replace('Z','+00:00'))<datetime.datetime.fromisoformat(r['timing']['started_at'].replace('Z','+00:00')):raise ValueError('reversed_utc')
        if 'manifest.yaml' in r['artifacts']:raise ValueError('manifest_self_hash')
        if r['directory']['path_sha256']!=hashlib.sha256(r['directory']['path'].encode()).hexdigest():raise ValueError('directory_path_hash')
        keys=[(x['fixture'],x['class'],x['coordinate'],x['seed'],x['q']) for x in r['result']['metrics']['R_cells']]
        if len(keys)!=len(set(keys)):raise ValueError('duplicate_primary_metric')
        for x in r['result']['metrics']['R_cells']:
            expected=7 if x['seed']==606103 and x['q']==4096 else 0
            if len(x['leave_one_out'])!=expected:raise ValueError('omission_cardinality')
        if r['status']=='completed_valid':
            expected={(f,c,u,s,q) for f in ['I0F0','I0F1','I1F0','I1F1','I2F0','I2F1'] for c in ['C0','C1'] for u in [1,2,3] for s in [606101,606103] for q in [1,16,256,4096]}
            if set(keys)!=expected:raise ValueError('incomplete_ratio_matrix')
    return True

def check_local_ledger(rows,edges):
    """Grammar, identities and local sums; full run/freeze/class admission is not performed."""
    for r in rows:validate_record(r)
    for e in edges:validate_record(e)
    by={r['raw_cost_row_id']:r for r in rows}
    if len(by)!=len(rows):raise ValueError('duplicate_raw_id')
    physical=[r['physical_event_id'] for r in rows if r['charge_kind']=='exclusive_leaf']
    if len(physical)!=len(set(physical)):raise ValueError('duplicate_physical_event')
    groups={};seen=set()
    for e in edges:
        r=by.get(e['raw_cost_row_id'])
        if r is None or r['charge_kind']!='exclusive_leaf':raise ValueError('bad_edge_source')
        key=(e['raw_cost_row_id'],e['strategy_view'],canonical(e['scenario']));edgekey=key+(canonical(e['target']),)
        if edgekey in seen:raise ValueError('duplicate_edge')
        seen.add(edgekey);groups.setdefault(key,[]).append(e)
    for row in rows:
        if row["charge_kind"]=="exclusive_leaf" and not any(key[0]==row["raw_cost_row_id"] for key in groups):raise ValueError("missing_allocation_edges")
        if row["charge_kind"]=="derived_rollup" and any(x not in by or by[x]["charge_kind"]!="exclusive_leaf" for x in row["source_leaf_ids"]):raise ValueError("bad_rollup_source")
    for key,es in groups.items():
        r=by[key[0]]
        if sum(Fraction(e['weight']['numerator'],e['weight']['denominator']) for e in es)!=1:raise ValueError('weight_sum')
        for raw,allocated,raw_reason,edge_reason in [('CPU_nanoseconds','allocated_CPU_nanoseconds','CPU_unavailable_reason','allocated_CPU_unavailable_reason'),('wall_nanoseconds','allocated_wall_nanoseconds','wall_unavailable_reason','allocated_wall_unavailable_reason')]:
            if r[raw] is None:
                if any(e[allocated] is not None or e[edge_reason]!=r[raw_reason] for e in es):raise ValueError('unknown_not_propagated')
            elif any(e[allocated] is None for e in es) or sum(e[allocated] for e in es)!=r[raw]:raise ValueError('integer_cost_sum')
    return True

def raw(component='reporting_and_artifact_publication'):
    row=next(x for x in C['component_crosswalk']['rows'] if x['component']==component);scope=row['allowed_scopes'][0]
    r={'record_type':'raw_cost','raw_cost_row_id':'cost-0','physical_event_id':'event-0','event_ordinal':0,'component':component,'phase':row['allowed_phases'][0],'status':'complete','CPU_nanoseconds':37,'CPU_unavailable_reason':None,'wall_nanoseconds':40,'wall_unavailable_reason':None,'process_group_peak_RSS_bytes':1000,'RSS_unavailable_reason':None,'operation_counts':None,'operation_counts_unavailable_reason':'uninstrumented_backend','capture_interval':{'stream_id':'fixed-stream','process_group_id':1,'cpu_started_ns':0,'cpu_finished_ns':37,'wall_started_ns':0,'wall_finished_ns':40,'reason':None},'charge_kind':'exclusive_leaf','source_leaf_ids':[],'scope':scope}
    values={'interval':'I0','fixture':'I0F0','kernel':'K0','class':'C0','endpoint':'K0','coordinate':1,'plane':'selection','seed':606101,'q':256,'arm':7,'block':0,'repetition':1}
    if scope=='scaffolding':r.update(scaffold_kind=component,owner={'scope':'global'})
    else:r.update({k:values[k] for k in C['raw_cost_tensor']['scope_variants'][scope]['required_indices']})
    if component in ['level_and_multiplicity_certificate','all_six_algorithm_selection_trials']:
        r.update(charge_kind='derived_rollup',source_leaf_ids=['source-fixed'],CPU_nanoseconds=None,CPU_unavailable_reason='derived_rollup',wall_nanoseconds=None,wall_unavailable_reason='derived_rollup')
    return r

def edge():
    return {'record_type':'allocation_edge','raw_cost_row_id':'cost-0','strategy_view':'actual_only_scaffolding','scenario':{'kind':'actual_only'},'target':{'kind':'physical_owner','raw_cost_row_id':'cost-0'},'weight':{'numerator':1,'denominator':1},'allocated_CPU_nanoseconds':37,'allocated_CPU_unavailable_reason':None,'allocated_wall_nanoseconds':40,'allocated_wall_unavailable_reason':None,'reason_code':'actual_only'}

def manifest():
    h='0'*64;r={'id':'RUN-ECDLP-abcdef','experiment_id':'EXP-ECDLP-1b1b99','status':'partial_inconclusive','code':{'commit':'0'*40,'dirty':False,'command':'fixed synthetic object only','dirty_diff_sha256':None,'source_sha256':{'fixed.py':h}},'inference':{k:None for k in ['requested_policy','canonical_policy','backend','provider','resolved_model_id','model_provenance','requested_reasoning_effort','reasoning_effort','fallback_reason','adapter_version','config_digest']},'environment':{'operating_system':'fixed-Darwin','architecture':'arm64','sage_version':None,'python_version':'fixed','dependencies':{},'runtime_binding_sha256':CONTRACT['effective_contract']['runtime_and_public_trust_binding']['sha256']},'inputs':{'curve_id':None,'seed':None,'parameters':{'fixture_ids':['I0F0','I0F1','I1F0','I1F1','I2F0','I2F1'],'endpoint_ids':['K0','K1','K2','K3'],'coordinate_values':[1,2,3],'seed_values':[606101,606103],'q_values':[1,16,256,4096],'arm_values':[1,2,3,4,5,6,7],'timing_block_values':[0,1,2,3,4,5,6],'primary_seed':606103,'primary_q':4096,'required_primary_cells':36,'effective_contract_sha256':h},'fixture_artifact':'fixtures.json'},'timing':{'started_at':'2026-09-08T00:00:00Z','finished_at':'2026-09-08T00:00:01Z','wall_seconds':1,'wall_nanoseconds':1000000000},'resources':{'peak_rss_bytes':None,'peak_rss_unavailable_reason':'infrastructure_stopped','cpu_seconds':None,'cpu_nanoseconds':None,'cpu_unavailable_reason':'not_observed_before_stop','measurement_scope':'whole_process_group'},'result':{'metrics':{'R_cells':[],'R_global':[],'q_star':[],'branch':'inconclusive','coverage':{'accepted_fixtures':0,'resolved_primary_cells':0,'main_block_rows':0,'selection_block_rows':0,'top_block_rows':0,'identity_block_rows':0,'all_controls_passed':False}},'valid':False,'invalid_reason':'fixed_incomplete','certificate':{'kind':'none','verified':None,'verifier':None}},'artifacts':{},'directory':{'path':'/synthetic/not-a-real-run','path_sha256':hashlib.sha256(b'/synthetic/not-a-real-run').hexdigest()},'admission':{'authorization_payload_sha256':h,'effective_contract_sha256':h,'schema_sha256':h,'handoff_sha256':h,'implementation_snapshot_commit':'0'*40,'review_archive_commit':'0'*40,'review_report_sha256':h}}
    r['inference'].update(model_verified=False,fallback_used=False,degraded_requirements=[],independent_session=False)
    return {'run':r}

def reject(fn):
    try:fn()
    except (ValueError,jsonschema.ValidationError):return True
    return False

def mutate(d,**values):d=copy.deepcopy(d);d.update(values);return d

def case(name,fn):
    if len(CASES)>=100:raise RuntimeError('suite admission ceiling')
    row={'ordinal':len(CASES)+1,'name':name,'status':'started'};CASES.append(row);t=time.perf_counter();c=time.process_time();signal.alarm(10)
    try:assert fn(),name;row['status']='passed'
    except BaseException as ex:row.update(status='failed',error=type(ex).__name__+': '+str(ex))
    finally:signal.alarm(0);row.update(wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-c)

def run():
    for row in C['component_crosswalk']['rows']:
        component=row['component'];case('valid component/phase/scope: '+component,lambda component=component:validate_record(raw(component)))
    case('publication event gets one actual-only edge without q',lambda:check_local_ledger([raw()],[edge()]))
    case('actual-only scenario rejects fabricated q',lambda:reject(lambda:validate_record(mutate(edge(),scenario={'kind':'actual_only','q':1}))))
    case('actual-only target rejects endpoint string',lambda:reject(lambda:validate_record(mutate(edge(),target='I0F0/K0/1'))))
    case('physical-owner target must name its raw event',lambda:reject(lambda:validate_record(mutate(edge(),target={'kind':'physical_owner','raw_cost_row_id':'different'}))))
    case('actual-only weight must be one',lambda:reject(lambda:validate_record(mutate(edge(),weight={'numerator':1,'denominator':2}))))
    case('zero edge weight refused',lambda:reject(lambda:validate_record(mutate(edge(),weight={'numerator':0,'denominator':1}))))
    case('unreduced edge weight refused',lambda:reject(lambda:validate_record(mutate(edge(),weight={'numerator':2,'denominator':2}))))
    case('duplicate edge cannot evade canonical semantic key',lambda:reject(lambda:check_local_ledger([raw()],[edge(),copy.deepcopy(edge())])))
    case('duplicate physical row cannot change only row id',lambda:reject(lambda:check_local_ledger([raw(),mutate(raw(),raw_cost_row_id='cost-1')],[])))
    case('integer allocation must conserve raw cost',lambda:reject(lambda:check_local_ledger([raw()],[mutate(edge(),allocated_CPU_nanoseconds=36)])))
    case('actual-only null and reason propagate unchanged',lambda:check_local_ledger([mutate(raw(),status='partial',CPU_nanoseconds=None,CPU_unavailable_reason='capture_failed')],[mutate(edge(),allocated_CPU_nanoseconds=None,allocated_CPU_unavailable_reason='capture_failed')]))
    case('unavailable cannot become fabricated zero',lambda:reject(lambda:check_local_ledger([mutate(raw(),status='partial',CPU_nanoseconds=None,CPU_unavailable_reason='capture_failed')],[mutate(edge(),allocated_CPU_nanoseconds=0)])))
    case('main uppercase alias refused',lambda:reject(lambda:validate_record(mutate(raw('scalar_multiplication'),plane='MAIN'))))
    case('banana phase refused',lambda:reject(lambda:validate_record(mutate(raw(),phase='banana'))))
    case('wrong real phase for publication refused',lambda:reject(lambda:validate_record(mutate(raw(),phase='evaluation'))))
    case('redundant stratum alias refused',lambda:reject(lambda:validate_record(mutate(raw('baseline_selection_stratum_overhead'),stratum='S0'))))
    case('selection seed cannot be confirmation',lambda:reject(lambda:validate_record(mutate(raw('scalar_multiplication'),seed=606103))))
    case('selection q cannot be one',lambda:reject(lambda:validate_record(mutate(raw('scalar_multiplication'),q=1))))
    case('source control owner has no fake endpoint',lambda:validate_record(mutate(raw('top_level_control'),owner={'scope':'control_workload','fixture':'I0F0','coordinate':1,'plane':'top_control','seed':606101,'q':1,'arm':'direct_3_iota'})))
    case('top control cannot use identity arm',lambda:reject(lambda:validate_record(mutate(raw('top_level_control'),owner={'scope':'control_workload','fixture':'I0F0','coordinate':1,'plane':'top_control','seed':606101,'q':1,'arm':'direct_iota'}))))
    case('control owner rejects added endpoint',lambda:reject(lambda:validate_record(mutate(raw('top_level_control'),owner={'scope':'control_workload','fixture':'I0F0','coordinate':1,'plane':'top_control','seed':606101,'q':1,'arm':'direct_3_iota','endpoint':'K0'}))))
    case('RSS unavailable partial row has exact reason',lambda:validate_record(mutate(raw(),status='partial',process_group_peak_RSS_bytes=None,RSS_unavailable_reason='infrastructure_stopped')))
    case('RSS null without reason refused',lambda:reject(lambda:validate_record(mutate(raw(),status='partial',process_group_peak_RSS_bytes=None))))
    case('complete raw row cannot omit RSS',lambda:reject(lambda:validate_record(mutate(raw(),process_group_peak_RSS_bytes=None,RSS_unavailable_reason='infrastructure_stopped'))))
    case('uninstrumented operation reason is exact',lambda:reject(lambda:validate_record(mutate(raw(),operation_counts_unavailable_reason='unknown-new-code'))))
    case('derived reason cannot label exclusive work',lambda:reject(lambda:validate_record(mutate(raw(),status='partial',CPU_nanoseconds=None,CPU_unavailable_reason='derived_rollup'))))
    case('manifest uses plural fields under run',lambda:validate_record(manifest()))
    case('old singular input alias refused',lambda:reject(lambda:validate_record({'run':{**manifest()['run'],'input':manifest()['run']['inputs']}})))
    case('misnested code section refused',lambda:reject(lambda:validate_record({**manifest(),'code':manifest()['run']['code']})))
    case('manifest self hash refused',lambda:reject(lambda:validate_record({'run':{**manifest()['run'],'artifacts':{'manifest.yaml':{'sha256':'0'*64,'bytes':1}}}})))
    case('manifest unknown resource reason refused',lambda:reject(lambda:validate_record({'run':{**manifest()['run'],'resources':{**manifest()['run']['resources'],'peak_rss_unavailable_reason':'not-defined'}}})))
    case('strict parser rejects nested duplicate keys',lambda:reject(lambda:strict_json('{"run":{"id":1,"id":2}}')))
    case('strict parser rejects nonfinite number',lambda:reject(lambda:strict_json('{"x":NaN}')))
    case('selection-score scenario has candidate but no stratum subset',lambda:validate_record({**edge(),'strategy_view':'selection_score_candidate','scenario':{'kind':'selection_score','candidate_arm':7},'target':{'kind':'endpoint_coordinate','fixture':'I0F0','endpoint':'K0','coordinate':1},'reason_code':'selection_score'}))
    case('selection-score scenario forbids stratum alias',lambda:reject(lambda:validate_record({**edge(),'strategy_view':'selection_score_candidate','scenario':{'kind':'selection_score','candidate_arm':7,'interval':'I0'},'target':{'kind':'endpoint_coordinate','fixture':'I0F0','endpoint':'K0','coordinate':1},'reason_code':'selection_score'})))


    case('integral float cost spelling refused',lambda:reject(lambda:validate_record(mutate(raw(),CPU_nanoseconds=37.0))))
    case('integral float target coordinate refused',lambda:reject(lambda:validate_record({**edge(),'strategy_view':'selection_score_candidate','scenario':{'kind':'selection_score','candidate_arm':7},'target':{'kind':'endpoint_coordinate','fixture':'I0F0','endpoint':'K0','coordinate':1.0},'reason_code':'selection_score'})))
    case('integral float manifest index refused',lambda:reject(lambda:validate_record({'run':{**manifest()['run'],'inputs':{**manifest()['run']['inputs'],'parameters':{**manifest()['run']['inputs']['parameters'],'q_values':[1.0,16,256,4096]}}}})))

if __name__=='__main__':
    t=time.perf_counter();c=time.process_time();run();r={'schema':'crypto.autoresearch.fixed_schema_checks.v1','task_id':'TASK-20260908-5e3d88','executed_cases':len(CASES),'passed':sum(x['status']=='passed' for x in CASES),'failed':sum(x['status']!='passed' for x in CASES),'cases':CASES,'wall_seconds':time.perf_counter()-t,'cpu_seconds':time.process_time()-c,'maximum_rss_native':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rss_units':'bytes_on_Darwin','workers':1,'scientific_runs':0,'hashes':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['EXP-ECDLP-1b1b99.yaml','schema.json','checks.py']}};print(json.dumps(r,indent=2));raise SystemExit(bool(r['failed']))
