"""No-draw planning and prospective public coordinate sampler.

Source stage only: exact nonce, limits, exclusions and source/protocol bindings
must be supplied later. This module draws no nonce and imports no truth solver.
"""
from engine import arm_specs, uniform_below, sample_coordinate
from curve import Curve, Counter, certify_public_parameters, point_json
STAGES=('discovery','validation','confirmation-A','confirmation-B')
TIERS=(10,13,16)


def plan():
    return {'status':'source_only_not_admitted','draws':0,
        'stages':[{'stage':s,'tiers':[{'bits':b,'curves':4} for b in TIERS],
                   'single_draws_per_curve':1800 if i<2 else 0,
                   'trace_starts_per_curve':128 if i<2 else 0,
                   'arms':[a['id'] for a in arm_specs()] if i<2 else ['circuit2.a1'],
                   'targets_per_curve':0 if i<2 else 64,'replicates':0 if i<2 else 8}
                  for i,s in enumerate(STAGES)],
        'required_inputs':['nonce','curve_proposal_limit','point_proposal_limit','excluded_p_j','source_fingerprint','protocol_sha256'],
        'curve_eligibility':'ordinary nonsingular prime-order curve, p=3 mod4, r!=p, exact r bit tier, unique (p,j) across stages and exclusions',
        'counts':{'curves':48,'calibration_singles':345600,'calibration_traces':24576,
                  'calibration_trace_queries':344064,'confirmation_traces':12288,
                  'confirmation_cells':73728,'confirmation_queries_each_evaluator':172032,
                  'all_physical_predicate_queries_before_controls':1033728},
        'scientific_execution_authorized':False}


def is_prime(n,counter):
    if n<2:return False
    d=2
    while d*d<=n:
        counter.tick('certification_trial_division')
        if n%d==0:return False
        d+=1
    return True


def sample_curve(stage,bits,index,nonce,curve_proposal_limit,point_proposal_limit,excluded_p_j):
    """Exact rejection sampler; trial counting/certification are common costs.

    Domain p lies [2^(bits-1),2^(bits+1)); only p=3 mod4 accepted.
    Coordinates and curves have no scalar labels. Caller carries exclusions
    across every stage. No candidate response enters eligibility.
    """
    if stage not in STAGES or bits not in TIERS or index not in range(4):raise ValueError('unfrozen slot')
    if type(curve_proposal_limit) is not int or curve_proposal_limit<1:raise ValueError('positive frozen cap required')
    counter=Counter();proposals=[];low=1<<(bits-1);span=(1<<(bits+1))-low
    slot=f'{stage}-{bits}/{index}'
    for i in range(curve_proposal_limit):
        role='curve/'+stage+'-'+str(bits);draws={}
        for key,bound in [('p',span),('a',None),('b',None)]:
            v,draw=uniform_below(nonce,role,f'{slot}/{i}/{key}',bound or p,counter);draws[key]=draw
            if key=='p':p=low+v
            elif key=='a':a=v
            else:b=v
        reason=None;r=None;j=None
        if p%4!=3 or not is_prime(p,counter):reason='FIELD_REJECTED'
        elif (4*a**3+27*b*b)%p==0:reason='SINGULAR'
        else:
            r=1
            for x in range(p):
                rhs=(x*x*x+a*x+b)%p;counter.tick('curve_point_count_x');counter.tick('common_integer_mul',4);counter.tick('common_integer_mod',2)
                chi=pow(rhs,(p-1)//2,p);counter.tick('common_modular_power');counter.tick('common_modular_power_bit',((p-1)//2).bit_length())
                r+=1 if rhs==0 else 2 if chi==1 else 0
            if r.bit_length()!=bits or r==p or not is_prime(r,counter):reason='ORDER_REJECTED'
            elif (p+1-r)%p==0:reason='SUPERSINGULAR'
            else:
                counter.tick('common_modular_inverse');j=1728*4*a**3*pow((4*a**3+27*b*b)%p,-1,p)%p
                if (p,j) in excluded_p_j:reason='EXCLUDED_P_J'
        proposals.append({'proposal':i,'draws':draws,'p':p,'a':a,'b':b,'r':r,'j':j,'reason':reason})
        if reason is None:
            model={'p':p,'a':a,'b':b,'r':r};cid=f'{stage}-{bits}-{index}'
            base,sampling=sample_coordinate(model,nonce,'points/'+cid,'base',point_proposal_limit)
            return {'status':'ACCEPTED' if base else 'CAPPED_PROPOSALS','curve_id':cid,'model':model,'base':point_json(base),'p_j':[p,j],
                    'proposals':proposals,'base_sampling':sampling,'counts':counter.snapshot()}
    return {'status':'CAPPED_PROPOSALS','proposals':proposals,'counts':counter.snapshot()}


def jobs_for_curve(curve_id,stage,point_proposal_limit):
    if stage not in STAGES:raise ValueError('unknown stage')
    jobs=[]
    def add(kind,id,target,arm,point,rep):
        jobs.append({'kind':kind,'id':id,'curve_id':curve_id,'target_id':target,'arm_id':arm,'point_index':point,'replicate':rep,'proposal_limit':point_proposal_limit})
    if stage in STAGES[:2]:
        for i in range(1800):
            for arm in arm_specs():add('single',f"{curve_id}/single{i:04d}/{arm['id']}",None,arm['id'],i,None)
        for i in range(128):
            for arm in arm_specs():add('calibration-trace',f"{curve_id}/trace{i:04d}/{arm['id']}",None,arm['id'],i,None)
    else:
        for i in range(64):
            for rep in range(8):add('confirmation-trace',f'{curve_id}/target{i:04d}/rep{rep}',f'target{i:04d}','circuit2.a1',None,rep)
    return jobs


def build_public(config):
    """Future producer, never called by plan(). Preserve all proposal outcomes.

    Explicit limits are input requirements, not fitted defaults. Entire returned
    proposal ledger is common generation cost; failure is operational coverage.
    """
    required={'nonce','curve_proposal_limit','point_proposal_limit','target_proposal_limit','excluded_p_j'}
    if set(config)!=required:raise ValueError('exact frozen sampler configuration required')
    for key in ('curve_proposal_limit','point_proposal_limit','target_proposal_limit'):
        if type(config[key]) is not int or config[key]<1:raise ValueError('positive frozen cap required')
    excluded={tuple(k) for k in config['excluded_p_j']};curves=[];ledger=[];jobs=[]
    for stage in STAGES:
        for bits in TIERS:
            for index in range(4):
                proposal=sample_curve(stage,bits,index,config['nonce'],config['curve_proposal_limit'],config['point_proposal_limit'],excluded)
                ledger.append(proposal)
                if proposal['status']!='ACCEPTED':return {'status':'incomplete','public':{'nonce':config['nonce'],'curves':curves},'ledger':ledger,'jobs':jobs}
                excluded.add(tuple(proposal['p_j']));targets=[];seen=set();target_ledger=[]
                if stage in STAGES[2:]:
                    for attempt in range(config['target_proposal_limit']):
                        point,sampling=sample_coordinate(proposal['model'],config['nonce'],'points/'+proposal['curve_id'],f'target-proposal/{attempt}',config['point_proposal_limit'])
                        duplicate=point in seen
                        target_ledger.append({'attempt':attempt,'point':point_json(point),'duplicate':duplicate,'sampling':sampling})
                        if point is not None and not duplicate:
                            seen.add(point);targets.append({'target_id':f'target{len(targets):04d}','point':point_json(point)})
                        if len(targets)==64:break
                    proposal['target_sampling']=target_ledger
                    if len(targets)!=64:return {'status':'incomplete','public':{'nonce':config['nonce'],'curves':curves},'ledger':ledger,'jobs':jobs}
                curves.append({'curve_id':proposal['curve_id'],'model':proposal['model'],'base':proposal['base'],'targets':targets})
                jobs.extend(jobs_for_curve(proposal['curve_id'],stage,config['point_proposal_limit']))
    expected={'setups':216,'intents':36864,'singles':345600,'traces':36864,'cells':73728}
    return {'status':'complete','public':{'nonce':config['nonce'],'curves':curves},'ledger':ledger,'plan':{'jobs':jobs,'expected':expected}}
