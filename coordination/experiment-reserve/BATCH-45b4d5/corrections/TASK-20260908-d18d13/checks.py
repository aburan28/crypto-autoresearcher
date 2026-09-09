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
PLANNED=[]

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
    if component in SCHEMA.get('x-component-plane-arm-relation',{}):
        rel=next((x for x in SCHEMA['x-component-plane-arm-relation'][component] if x['plane']=='selection'),SCHEMA['x-component-plane-arm-relation'][component][0])
        r.update(plane=rel['plane'],arm=rel['arms'][0],seed=606101,q=256)
    return r

def edge():
    return {'record_type':'allocation_edge','raw_cost_row_id':'cost-0','strategy_view':'actual_only_scaffolding','scenario':{'kind':'actual_only'},'target':{'kind':'physical_owner','raw_cost_row_id':'cost-0'},'weight':{'numerator':1,'denominator':1},'allocated_CPU_nanoseconds':37,'allocated_CPU_unavailable_reason':None,'allocated_wall_nanoseconds':40,'allocated_wall_unavailable_reason':None,'reason_code':'actual_only'}

def manifest():
    h='0'*64;r={'id':'RUN-ECDLP-abcdef','experiment_id':'EXP-ECDLP-1b1b99','status':'partial_inconclusive','code':{'commit':'0'*40,'dirty':False,'command':'fixed synthetic object only','dirty_diff_sha256':None,'source_sha256':{'fixed.py':h}},'inference':{k:None for k in ['requested_policy','canonical_policy','backend','provider','resolved_model_id','model_provenance','requested_reasoning_effort','reasoning_effort','fallback_reason','adapter_version','config_digest']},'environment':{'operating_system':'fixed-Darwin','architecture':'arm64','sage_version':None,'python_version':'fixed','dependencies':{},'runtime_binding_sha256':CONTRACT['effective_contract']['runtime_and_public_trust_binding']['sha256']},'inputs':{'curve_id':None,'seed':None,'parameters':{'fixture_ids':['I0F0','I0F1','I1F0','I1F1','I2F0','I2F1'],'endpoint_ids':['K0','K1','K2','K3'],'coordinate_values':[1,2,3],'seed_values':[606101,606103],'q_values':[1,16,256,4096],'arm_values':[1,2,3,4,5,6,7],'timing_block_values':[0,1,2,3,4,5,6],'primary_seed':606103,'primary_q':4096,'required_primary_cells':36,'effective_contract_sha256':h},'fixture_artifact':'fixtures.json'},'timing':{'started_at':'2026-09-08T00:00:00Z','finished_at':'2026-09-08T00:00:01Z','wall_seconds':1,'wall_nanoseconds':1000000000},'resources':{'peak_rss_bytes':None,'peak_rss_unavailable_reason':'infrastructure_stopped','cpu_seconds':None,'cpu_nanoseconds':None,'cpu_unavailable_reason':'not_observed_before_stop','measurement_scope':'whole_process_group'},'result':{'metrics':{'R_cells':[],'R_global':[],'q_star':[],'branch':'inconclusive','coverage':{'accepted_fixtures':0,'resolved_primary_cells':0,'main_block_rows':0,'selection_block_rows':0,'top_block_rows':0,'identity_block_rows':0,'all_controls_passed':False}},'valid':False,'invalid_reason':'fixed_incomplete','certificate':{'kind':'none','verified':None,'verifier':None}},'artifacts':{},'directory':{'path':'/synthetic/not-a-real-run','path_sha256':hashlib.sha256(b'/synthetic/not-a-real-run').hexdigest()},'admission':{'authorization_payload_sha256':h,'effective_contract_sha256':h,'schema_sha256':h,'handoff_sha256':h,'implementation_snapshot_commit':'0'*40,'review_archive_commit':'0'*40,'review_report_sha256':h}}
    r['inference'].update(model_verified=False,fallback_used=False,degraded_requirements=[],independent_session=False)
    r['inference']=deterministic_inference()
    r['result'].update(reason_code='MATRIX_INCOMPLETE',stage='run_complete_timing_and_control_matrices',invalid_reason='MATRIX_INCOMPLETE')
    return {'run':r}

def reject(fn):
    try:fn()
    except (ValueError,jsonschema.ValidationError):return True
    return False

def mutate(d,**values):d=copy.deepcopy(d);d.update(values);return d

def case(name,fn):
    PLANNED.append((name,fn))

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



# Prospective fixed-object relations. No scientific runner or allocator is imported.
RELATION=SCHEMA['x-component-plane-arm-relation']
OUTCOMES={x['reason_code']:x for x in SCHEMA['x-outcome-relation']}
BASE_VALIDATE=validate_record
FIXTURES=['I0F0','I0F1','I1F0','I1F1','I2F0','I2F1']
ENDPOINTS=['K0','K1','K2','K3']
TARGETS=[{'kind':'endpoint_coordinate','fixture':f,'endpoint':e,'coordinate':u} for f in FIXTURES for e in ENDPOINTS for u in [1,2,3]]

def deterministic_inference(note='deterministic harness execution — no model in the loop'):
    return {'requested_policy':'executor-implementation','canonical_policy':'executor-implementation','backend':None,'provider':None,'resolved_model_id':None,'model_provenance':'not-applicable','model_verified':True,'requested_reasoning_effort':None,'reasoning_effort':None,'fallback_used':False,'fallback_reason':None,'degraded_requirements':[],'independent_session':False,'adapter_version':'fixed-no-serving-probe','config_digest':None,'note':note}

def validate_record(d):
    BASE_VALIDATE(d)
    if d.get('record_type')=='raw_cost' and d['component'] in RELATION:
        if not any(d.get('plane')==r['plane'] and type(d.get('arm')) is int and d['arm'] in r['arms'] for r in RELATION[d['component']]):raise ValueError('component_plane_arm')
    if 'run' in d:
        r=d['run'];i=r['inference'];result=r['result'];o=OUTCOMES[result['reason_code']]
        if 'note' in i and i['requested_policy']!=i['canonical_policy']:raise ValueError('deterministic_policy_identity')
        if (r['status'],result['valid'])!=(o['status'],o['valid']) or result['stage'] not in o['stages'] or result['metrics']['branch'] not in o['branches']:raise ValueError('outcome_relation')
        for cell in result['metrics']['R_cells']:
            labels=[x['omitted_block'] for x in cell['leave_one_out']]
            if cell['seed']==606103 and cell['q']==4096 and sorted(labels)!=list(range(7)):raise ValueError('omitted_block_identity')
    return True

def expected_reason(raw_row,edge_row,context):
    family=next(x['family'] for x in C['component_crosswalk']['rows'] if x['component']==raw_row['component'])
    v=edge_row['strategy_view'];kind=edge_row['scenario']['kind'];component=raw_row['component']
    if raw_row['charge_kind']!='exclusive_leaf':raise ValueError('rollup_has_edge')
    if v=='actual_only_scaffolding' and kind=='actual_only':return 'actual_only'
    if family=='shared' and v in ['scalar','transport'] and kind=='cold':return 'shared_setup'
    if family=='transport' and v=='transport' and kind=='cold':return 'transport_setup'
    if component in ['global_library_initialization','baseline_selection_stratum_overhead'] and v=='scalar' and kind=='cold':return 'selection_actual_spend'
    if component=='global_library_initialization' and v=='selection_score_candidate' and kind=='selection_score' and edge_row['scenario']['candidate_arm']==7:return 'selection_score'
    if family=='arm_context' and raw_row['plane']=='selection':
        if v=='scalar' and kind=='cold':return 'selection_actual_spend'
        if v=='selection_score_candidate' and kind=='selection_score' and edge_row['scenario']['candidate_arm']==raw_row['arm']:return 'selection_score'
    if family=='arm_context' and raw_row['plane']=='main' and kind=='cold' and edge_row['scenario']=={'kind':'cold','seed':raw_row['seed'],'q':raw_row['q']}:
        winner=context['winners'][(raw_row['fixture'][:2],raw_row['coordinate'])]
        if (raw_row['arm']==1 and v=='transport') or (raw_row['arm']==winner and v=='scalar'):return 'selected_main_work'
    raise ValueError('forbidden_edge_relation')

def expected_groups(raw_row,context):
    # Applies only to supplied abstract source rows and supplied metadata.
    # Does not discover fixtures, classes, winners, events or allocation inputs.
    if raw_row['charge_kind']=='derived_rollup':return []
    component=raw_row['component'];family=next(x['family'] for x in C['component_crosswalk']['rows'] if x['component']==component)
    scope=raw_row['scope'];targets=TARGETS
    unknown=any(raw_row[k] is None for k in ['CPU_nanoseconds','wall_nanoseconds'])
    if scope=='interval':
        fixture=context.get('accepted_candidate_owner',{}).get((raw_row['interval'],raw_row['event_ordinal']))
        if fixture is None:unknown=True
        targets=[t for t in targets if t['fixture']==fixture]
    elif scope in ['fixture','kernel','class','endpoint_coordinate','arm_workload','timing_block','block_repetition']:
        targets=[t for t in targets if t['fixture']==raw_row['fixture']]
        if scope=='kernel':targets=[t for t in targets if t['endpoint']==raw_row['kernel']]
        if scope=='class':
            members=context.get('class_members',{}).get((raw_row['fixture'],raw_row['class']))
            if members is None:unknown=True;targets=[]
            else:targets=[t for t in targets if t['endpoint'] in members]
        if scope in ['endpoint_coordinate','arm_workload','timing_block','block_repetition']:targets=[t for t in targets if t['endpoint']==raw_row['endpoint'] and t['coordinate']==raw_row['coordinate']]
    elif scope=='selection_stratum':targets=[t for t in targets if t['fixture'][:2]==raw_row['interval'] and t['coordinate']==raw_row['coordinate']]
    groups=[]
    cold=[{'kind':'cold','q':q,'seed':s} for q in [1,16,256,4096] for s in [606101,606103]]
    if not unknown:
        if family=='shared':groups=[(v,s,targets) for v in ['scalar','transport'] for s in cold]
        elif family=='transport':groups=[('transport',s,targets) for s in cold]
        elif component in ['global_library_initialization','baseline_selection_stratum_overhead']:
            groups=[('scalar',s,targets) for s in cold]
            if component=='global_library_initialization':groups.append(('selection_score_candidate',{'kind':'selection_score','candidate_arm':7},targets))
        elif family=='arm_context' and raw_row['plane']=='selection':groups=[('scalar',s,targets) for s in cold]+[('selection_score_candidate',{'kind':'selection_score','candidate_arm':raw_row['arm']},targets)]
        elif family=='arm_context' and raw_row['plane']=='main':
            winner=context['winners'][(raw_row['fixture'][:2],raw_row['coordinate'])]
            view='transport' if raw_row['arm']==1 else 'scalar' if raw_row['arm']==winner else None
            if view:groups=[(view,{'kind':'cold','q':raw_row['q'],'seed':raw_row['seed']},targets)]
    if not groups:groups=[('actual_only_scaffolding',{'kind':'actual_only'},[{'kind':'physical_owner','raw_cost_row_id':raw_row['raw_cost_row_id']}])]
    return groups

def check_closed_relations(rows,edges,context):
    check_local_ledger(rows,edges)
    by={r['raw_cost_row_id']:r for r in rows};expected={}
    for r in rows:
        for v,s,targets in expected_groups(r,context):expected[(r['raw_cost_row_id'],v,canonical(s))]=targets
    actual={}
    for e in edges:
        r=by[e['raw_cost_row_id']]
        if e['reason_code']!=expected_reason(r,e,context):raise ValueError('edge_reason_relation')
        key=(e['raw_cost_row_id'],e['strategy_view'],canonical(e['scenario']));actual.setdefault(key,[]).append(e)
    if set(actual)!=set(expected):raise ValueError('edge_group_completeness')
    for key,targets in expected.items():
        es=actual[key];r=by[key[0]];n=len(targets)
        if {canonical(e['target']) for e in es}!={canonical(t) for t in targets} or len(es)!=n:raise ValueError('complete_target_domain')
        by_target={canonical(e['target']):e for e in es}
        for j,t in enumerate(targets):
            e=by_target[canonical(t)]
            if Fraction(e['weight']['numerator'],e['weight']['denominator'])!=Fraction(1,n):raise ValueError('equal_target_weight')
            for source,dest in [('CPU_nanoseconds','allocated_CPU_nanoseconds'),('wall_nanoseconds','allocated_wall_nanoseconds')]:
                if r[source] is not None and e[dest]!=r[source]//n+(j<r[source]%n):raise ValueError('canonical_integer_remainder')
    return True

def fraction_value(d):
    if set(d)!= {'numerator','denominator'} or type(d['numerator']) is not int or type(d['denominator']) is not int or d['numerator']<0 or d['denominator']<=0 or math.gcd(d['numerator'],d['denominator'])!=1:raise ValueError('fraction_not_reduced')
    return Fraction(d['numerator'],d['denominator'])

def med(values):
    values=sorted(values)
    if len(values)==7:return values[3]
    if len(values)==6:return (values[2]+values[3])/2
    raise ValueError('median_cardinality')

def check_loo_cell(items,abstract_endpoints):
    if sorted(x['omitted_block'] for x in items)!=list(range(7)):raise ValueError('omitted_block_identity')
    if len(abstract_endpoints)!=2:raise ValueError('endpoint_pair')
    for ep in abstract_endpoints:
        for v in ['scalar','transport']:
            if type(ep[v]['setup']) is not int or ep[v]['setup']<0 or set(ep[v]['blocks'])!=set(range(7)):raise ValueError('source_block_identity')
    for item in items:
        b=item['omitted_block'];totals={}
        for view in ['scalar','transport']:
            totals[view]=sum(ep[view]['setup']+med([fraction_value(ep[view]['blocks'][j]) for j in range(7) if j!=b]) for ep in abstract_endpoints)
        if totals['transport']<=0:raise ValueError('nonpositive_denominator')
        if item['kind']!='value' or fraction_value(item['value'])!=totals['scalar']/totals['transport']:raise ValueError('loo_label_value')
    return True


def fixed_context():
    return {'winners':{(i,u):2 for i in ['I0','I1','I2'] for u in [1,2,3]},'class_members':{(f,c):(['K0','K1'] if c=='C0' else ['K2','K3']) for f in FIXTURES for c in ['C0','C1']},'accepted_candidate_owner':{('I0',0):'I0F0'}}

def fixed_global_edges():
    # One fixed73CPU/77wall event with72targets,8coldviews andcandidate7.
    row=mutate(raw('global_library_initialization'),CPU_nanoseconds=73,wall_nanoseconds=77)
    row['capture_interval'].update(cpu_finished_ns=73,wall_finished_ns=77)
    pairs=[('scalar',{'kind':'cold','q':q,'seed':s},'selection_actual_spend') for q in [1,16,256,4096] for s in [606101,606103]]+[('selection_score_candidate',{'kind':'selection_score','candidate_arm':7},'selection_score')]
    edges=[]
    for view,scenario,reason in pairs:
        for j,t in enumerate(TARGETS):edges.append({**edge(),'strategy_view':view,'scenario':scenario,'target':copy.deepcopy(t),'weight':{'numerator':1,'denominator':72},'allocated_CPU_nanoseconds':1+(j==0),'allocated_wall_nanoseconds':1+(j<5),'reason_code':reason})
    return row,edges

def fixed_loo():
    def f(n,d=1):
        x=Fraction(n,d);return {'numerator':x.numerator,'denominator':x.denominator}
    eps=[{'scalar':{'setup':3,'blocks':{j:f(j*j+1,8) for j in range(7)}},'transport':{'setup':1,'blocks':{j:f(1) for j in range(7)}}},{'scalar':{'setup':7,'blocks':{j:f([5,1,6,0,4,2,3][j]+1,7) for j in range(7)}},'transport':{'setup':2,'blocks':{j:f([2,1,3,7,4,5,6][j],3) for j in range(7)}}}]
    result=[]
    for b in range(7):
        totals={v:sum(ep[v]['setup']+med([fraction_value(ep[v]['blocks'][j]) for j in range(7) if j!=b]) for ep in eps) for v in ['scalar','transport']}
        result.append({'omitted_block':b,'kind':'value','value':f(totals['scalar']/totals['transport'])})
    return result,eps

def full_manifest():
    d=manifest();r=d['run'];r['status']='completed_valid';r['result'].update(valid=True,invalid_reason=None,reason_code='VALID_COMPLETE_PANEL',stage='finalize_manifest_and_atomic_publish')
    r['resources'].update(peak_rss_bytes=1000,peak_rss_unavailable_reason=None,cpu_seconds=1,cpu_nanoseconds=1000000000,cpu_unavailable_reason=None)
    r['artifacts']={name:{'sha256':'0'*64,'bytes':1} for name in CONTRACT['effective_contract']['artifact_custody']['required_artifacts'] if name!='manifest.yaml'}
    m=r['result']['metrics'];m['branch']='exact_finite_cost_gap_only';m['coverage']={'accepted_fixtures':6,'resolved_primary_cells':36,'main_block_rows':28224,'selection_block_rows':3024,'top_block_rows':2016,'identity_block_rows':2016,'all_controls_passed':True}
    value={'kind':'value','value':{'numerator':1,'denominator':1}}
    m['R_cells']=[{'fixture':f,'class':c,'coordinate':u,'seed':s,'q':q,'ratio':copy.deepcopy(value),'leave_one_out':[{**copy.deepcopy(value),'omitted_block':b} for b in range(7)] if s==606103 and q==4096 else []} for f in FIXTURES for c in ['C0','C1'] for u in [1,2,3] for s in [606101,606103] for q in [1,16,256,4096]]
    m['R_global']=[{'seed':s,'q':q,'ratio':copy.deepcopy(value)} for s in [606101,606103] for q in [1,16,256,4096]]
    m['q_star']=[{'fixture':f,'class':c,'coordinate':u,'result':{'kind':'crossing','q':1}} for f in FIXTURES for c in ['C0','C1'] for u in [1,2,3]]
    return d

def outcome_fixture(code):
    o=OUTCOMES[code];d=full_manifest() if o['valid'] else manifest();r=d['run'];r['status']=o['status'];r['result'].update(reason_code=code,stage=o['stages'][0],valid=o['valid'],invalid_reason=None if o['valid'] else code)
    if code=='POLICY_RESOLUTION_FAILED':r['inference'].update(note='policy resolution failed',resolution_error='ValueError: fixed policy unavailable',model_verified=False)
    return d

def source_derived_deterministic_writer(note=None):
    # Compile only the exact side-effect-free function from the declared writer.
    # The adapter version is a fixed stand-in; no backend/config import or probe.
    import ast
    source=HERE.parents[4]/'orchestration/adapter/manifest.py'
    module=ast.parse(source.read_text())
    definition=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='deterministic_block')
    scope={'ADAPTER_VERSION':'fixed-version-placeholder','Any':object}
    exec(compile(ast.Module(body=[definition],type_ignores=[]),str(source),'exec'),scope)
    return scope['deterministic_block']() if note is None else scope['deterministic_block'](note=note)

def extra_cases():
    for component,relation in RELATION.items():
        def bad_arm(component=component):
            r=raw(component);r['arm']=1 if component in ['scalar_warmup','scalar_multiplication','table_setup','every_per_point_table'] else 2 if component.startswith('library_') or component=='input_output_setup_conversion' else 7 if component in ['psi_evaluation','iota_evaluation','phi_evaluation','transport_warmup'] else 99
            return reject(lambda:validate_record(r))
        case('wrong arm '+component,bad_arm)
        case('wrong control plane '+component,lambda component=component:reject(lambda:validate_record(mutate(raw(component),plane='top_control'))))
    for code in OUTCOMES:
        case('closed outcome '+code,lambda code=code:validate_record(outcome_fixture(code)))
        def wrong_status(code=code):
            d=outcome_fixture(code);d['run']['status']='completed_invalid' if d['run']['status']!='completed_invalid' else 'infrastructure_stopped';return reject(lambda:validate_record(d))
        case('wrong status '+code,wrong_status)
    case('actual writer deterministic default note',lambda:validate_record(manifest()))
    def custom_note():
        d=manifest();d['run']['inference']=deterministic_inference('');return validate_record(d)
    case('actual writer empty custom note preserved',custom_note)
    def source_writer_default():
        d=manifest();d['run']['inference']=source_derived_deterministic_writer();return validate_record(d)
    case('declared writer exact default function body',source_writer_default)
    def source_writer_note_collision():
        d=manifest();d['run']['inference']=source_derived_deterministic_writer('policy resolution failed');return validate_record(d)
    case('custom deterministic note is not a resolution-error tag',source_writer_note_collision)
    def missing_note():
        d=manifest();del d['run']['inference']['note'];return reject(lambda:validate_record(d))
    case('deterministic block must retain note',missing_note)
    def mismatched_policy():
        d=manifest();d['run']['inference']['canonical_policy']='different';return reject(lambda:validate_record(d))
    case('deterministic policy identity',mismatched_policy)
    def failure_valid():
        d=full_manifest();d['run']['inference']=outcome_fixture('POLICY_RESOLUTION_FAILED')['run']['inference'];return reject(lambda:validate_record(d))
    case('resolution error cannot be valid science',failure_valid)
    def banana():
        d=manifest();d['run']['result']['invalid_reason']='banana';d['run']['result']['reason_code']='banana';return reject(lambda:validate_record(d))
    case('archived banana reason counterexample rejected',banana)
    row,edges=fixed_global_edges()
    case('global candidate7 full72target9view allocation',lambda:check_closed_relations([row],edges,fixed_context()))
    case('global allocation missing target',lambda:reject(lambda:check_closed_relations([row],edges[:-1],fixed_context())))
    case('global allocation duplicate target',lambda:reject(lambda:check_closed_relations([row],edges+[edges[-1]],fixed_context())))
    def moved_remainder():
        es=copy.deepcopy(edges);es[0]['allocated_CPU_nanoseconds']-=1;es[1]['allocated_CPU_nanoseconds']+=1;return reject(lambda:check_closed_relations([row],es,fixed_context()))
    case('global allocation moved remainder',moved_remainder)
    def subset():return reject(lambda:check_closed_relations([row],[e for e in edges if e['target']['fixture'][:2]=='I0' and e['target']['coordinate']==1],fixed_context()))
    case('global allocation cannot become8target stratum',subset)
    def wrong_reason():
        es=copy.deepcopy(edges);es[0]['reason_code']='actual_only';return reject(lambda:check_closed_relations([row],es,fixed_context()))
    case('cold edge cannot be actual_only reason',wrong_reason)
    def candidate_wrong():
        es=copy.deepcopy(edges)
        for e in es:
            if e['scenario']['kind']=='selection_score':e['scenario']['candidate_arm']=6
        return reject(lambda:check_closed_relations([row],es,fixed_context()))
    case('library lifetime requirescandidate7',candidate_wrong)
    items,eps=fixed_loo()
    case('labelled fractional LOO joint recomputation',lambda:check_loo_cell(items,eps))
    case('whole labelled LOO item permutation allowed',lambda:check_loo_cell(list(reversed(items)),eps))
    case('LOO missing label',lambda:reject(lambda:check_loo_cell(items[:-1],eps)))
    case('LOO duplicate label',lambda:reject(lambda:check_loo_cell(items[:-1]+[items[0]],eps)))
    def relabel():
        ii=copy.deepcopy(items);ii[0]['omitted_block'],ii[6]['omitted_block']=6,0;return reject(lambda:check_loo_cell(ii,eps))
    case('LOO label-value substitution rejected',relabel)
    def unilateral():
        ee=copy.deepcopy(eps);ee[0]['transport']['blocks'].pop(6);return reject(lambda:check_loo_cell(items,ee))
    case('LOO missing source block cannot rescue',unilateral)
    def nonreduced():
        ii=copy.deepcopy(items);ii[0]['value']={k:v*2 for k,v in ii[0]['value'].items()};return reject(lambda:check_loo_cell(ii,eps))
    case('LOO nonreduced value rejected',nonreduced)
    case('complete288cell8global36qstar fixed manifest',lambda:validate_record(full_manifest()))
    def permuted_manifest():
        d=full_manifest()
        for x in d['run']['result']['metrics']['R_cells']:x['leave_one_out'].reverse()
        return validate_record(d)
    case('manifest labelled LOO permutation allowed',permuted_manifest)
    def missing_label_manifest():
        d=full_manifest();cell=next(x for x in d['run']['result']['metrics']['R_cells'] if x['leave_one_out']);del cell['leave_one_out'][0]['omitted_block'];return reject(lambda:validate_record(d))
    case('manifest missing omitted_block rejected',missing_label_manifest)
    def duplicate_label_manifest():
        d=full_manifest();cell=next(x for x in d['run']['result']['metrics']['R_cells'] if x['leave_one_out']);cell['leave_one_out'][0]['omitted_block']=1;return reject(lambda:validate_record(d))
    case('manifest duplicate omitted_block rejected',duplicate_label_manifest)

def execute_plan(reserved):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter();c=time.process_time();limit={'requested_bytes':4*1024**3,'attempted':True,'enforced':False}
    try:resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3));limit['enforced']=True
    except (ValueError,OSError) as ex:limit['error']=type(ex).__name__+': '+str(ex)
    def alarm(signum,frame):raise TimeoutError('fixed_case_10_seconds')
    signal.signal(signal.SIGALRM,alarm)
    for ordinal,(name,fn) in enumerate(PLANNED,1):
        if time.perf_counter()-t>1800 or time.process_time()-c>1800:break
        row={'ordinal':ordinal,'name':name,'started_at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'started'};CASES.append(row);tw=time.perf_counter();tc=time.process_time();signal.alarm(10)
        try:assert fn(),name;row['status']='passed'
        except BaseException as ex:row.update(status='failed',error=type(ex).__name__+': '+str(ex))
        finally:signal.alarm(0);row.update(ended_at_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.perf_counter()-tw,cpu_seconds=time.process_time()-tc)
    return {'task_id':'TASK-20260908-d18d13','kind':'fixed_definition_checks_only','started_at_UTC':start,'ended_at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pre_reserved_cases':reserved,'planned_cases':len(PLANNED),'executed_cases':len(CASES),'passed':sum(x['status']=='passed' for x in CASES),'failed':sum(x['status']!='passed' for x in CASES),'cases':CASES,'wall_seconds':time.perf_counter()-t,'cpu_seconds':time.process_time()-c,'memory_limit':limit,'peak_rss_native':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rss_units':'bytes on Darwin; KiB on Linux','workers':1,'scientific_runs':0,'jsonschema_version':__import__('importlib.metadata',fromlist=['version']).version('jsonschema'),'hashes':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['EXP-ECDLP-1b1b99.yaml','schema.json','checks.py']}}


# Sixth carrier extension: the preceding three carrier predicates are unchanged.
FIFTH_VALIDATE=validate_record
EARLY={r['reason_code']:r for r in SCHEMA['x-pre-run-outcome-relation']}
def validate_record(d):
    if d.get('record_type')!='pre_run_outcome':return FIFTH_VALIDATE(d)
    finite(d);numeric_profile(d);VALIDATOR.validate(d)
    instant=datetime.datetime.fromisoformat(d['recorded_at_UTC'].replace('Z','+00:00'))
    if instant.utcoffset()!=datetime.timedelta(0):raise ValueError('UTC_required')
    if 'policy_resolution_failure' in d:
        i=d['policy_resolution_failure']
        if i['requested_policy']!=i['canonical_policy']:raise ValueError('policy_identity')
    return True

def validate_trusted_refusal(d,trusted):
    validate_record(d)
    if d['trusted_handoff']!=trusted:raise ValueError('trusted_handoff_mismatch')
    return True

def pre_run(code='AUTH_MALFORMED'):
    r=EARLY[code]
    d={'record_type':'pre_run_outcome','experiment_id':'EXP-ECDLP-1b1b99','status':r['status'],'reason_code':code,'stage':'authorize_and_claim_nonce','recorded_at_UTC':'2026-09-09T00:00:00Z','trusted_handoff':{'task_id':'TASK-20260908-d18d13','handoff_sha256':hashlib.sha256((HERE.parents[4]/'ledger/handoffs/TASK-20260908-d18d13.yaml').read_bytes()).hexdigest()},'observed_authorization_input':{'kind':'unavailable','reason':'not_read'}}
    if code=='POLICY_RESOLUTION_FAILED':d['policy_resolution_failure']={**source_derived_deterministic_writer('policy resolution failed'),'resolution_error':'ValueError: fixed policy unavailable','model_verified':False}
    return d

def carrier_cases():
    for reason in EARLY:
        case('pre-run allowed reason '+reason,lambda reason=reason:validate_record(pre_run(reason)))
        def wrong(reason=reason):
            d=pre_run(reason);d['status']='infrastructure_stopped' if d['status']=='refused_before_run' else 'refused_before_run';return reject(lambda:validate_record(d))
        case('pre-run wrong status '+reason,wrong)
    for field in ['run','run_id','code','source_sha256','inputs','resources','directory','admission']:
        case('pre-run forbids fabricated '+field,lambda field=field:reject(lambda:validate_record(mutate(pre_run(),**{field:{}}))))
    for field in SCHEMA['$defs']['pre_run_outcome']['required']:
        def missing(field=field):
            d=pre_run();del d[field];return reject(lambda:validate_record(d))
        case('pre-run missing '+field,missing)
    for reason in ['not_read','not_provided','read_failed','capture_unavailable']:
        case('pre-run unavailable '+reason,lambda reason=reason:validate_record(mutate(pre_run(),observed_authorization_input={'kind':'unavailable','reason':reason})))
    case('pre-run observed empty bytes',lambda:validate_record(mutate(pre_run(),observed_authorization_input={'kind':'sha256','sha256':hashlib.sha256(b'').hexdigest(),'byte_length':0})))
    case('pre-run bool is not byte length',lambda:reject(lambda:validate_record(mutate(pre_run(),observed_authorization_input={'kind':'sha256','sha256':'0'*64,'byte_length':False}))))
    case('pre-run unknown reason',lambda:reject(lambda:validate_record(mutate(pre_run(),reason_code='banana'))))
    case('pre-run wrong phase',lambda:reject(lambda:validate_record(mutate(pre_run(),stage='replay_verify_and_reduce'))))
    case('pre-run non-UTC timestamp',lambda:reject(lambda:validate_record(mutate(pre_run(),recorded_at_UTC='2026-09-09T01:00:00+01:00'))))
    case('pre-run trusted binding matches',lambda:validate_trusted_refusal(pre_run(),pre_run()['trusted_handoff']))
    case('pre-run forged binding refused',lambda:reject(lambda:validate_trusted_refusal(pre_run(),{'task_id':'TASK-20260908-d18d13','handoff_sha256':'0'*64})))
    case('AUTH refusal cannot smuggle policy block',lambda:reject(lambda:validate_record(mutate(pre_run(),policy_resolution_failure=pre_run('POLICY_RESOLUTION_FAILED')['policy_resolution_failure']))))
    def stripped_policy():
        d=pre_run('POLICY_RESOLUTION_FAILED');del d['policy_resolution_failure'];return reject(lambda:validate_record(d))
    case('policy refusal retains writer block',stripped_policy)
    predecessor=HERE.parent/'TASK-20260908-e06add'
    prior_schema=json.loads((predecessor/'schema.json').read_text())
    for key in ['raw_cost','allocation_edge','manifest']:
        case('unchanged prior schema definition '+key,lambda key=key:SCHEMA['$defs'][key]==prior_schema['$defs'][key])
    old=yaml.safe_load((predecessor/'EXP-ECDLP-1b1b99.yaml').read_text())['effective_contract']
    for key in old:
        if key!='artifact_custody':case('unchanged effective section '+key,lambda key=key:CONTRACT['effective_contract'][key]==old[key])


if __name__=='__main__':
    import argparse,sys
    parser=argparse.ArgumentParser();parser.add_argument('--count',action='store_true');parser.add_argument('--reserved-cases',type=int);parser.add_argument('--prior-attempts',type=int,default=0);parser.add_argument('--final-reserve',type=int,default=0);args=parser.parse_args()
    run();extra_cases();carrier_cases()
    if args.count:print(json.dumps({'planned_cases':len(PLANNED),'case_names':[n for n,f in PLANNED],'executed_cases':0}));raise SystemExit(0)
    if args.reserved_cases!=len(PLANNED) or args.prior_attempts+args.reserved_cases+args.final_reserve>640:parser.error('exact prospective reservation andcumulative640case bound required')
    result=execute_plan(args.reserved_cases);result['command']=sys.argv;result['prior_attempts']=args.prior_attempts;result['final_reserve']=args.final_reserve;print(json.dumps(result,indent=2));raise SystemExit(bool(result['failed'] or result['executed_cases']!=result['planned_cases']))
