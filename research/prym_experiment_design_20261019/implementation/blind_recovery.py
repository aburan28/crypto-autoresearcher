"""Conditional synthetic E-stage worker and secret-separated challenge driver.

No scientific panel is launched by importing this module. The full E contract
still needs released W/S and matched complete-S/reference bindings.
"""
from hashlib import sha256
from collections import Counter
from copy import deepcopy
from itertools import combinations,product
import json
import os
from pathlib import Path
import random
import secrets
import subprocess
import sys
import tempfile
from time import perf_counter,process_time

from independent import multiply,verify_fixture,verify_row
from projection import certificate,projection
from relations import Context
from witness import attempt_schedule

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from curve_identity import curve_identity


def require_gates(gates):
    """A status report never manufactures a science admission or an advantage."""
    required=['source_rows_verified','nontrivial_full_rank','selector_cost_benefit_reviewed',
              'matched_ic_baseline_verified','complete_S_weights_bound','native_E_admission']
    missing=[key for key in required if gates.get(key) is not True]
    if missing:raise RuntimeError('E prerequisite gates closed: '+', '.join(missing))


def candidate(public):
    fixture=public['fixture'];config=public['algorithm'];seed=public['seed']
    verify_fixture(fixture)
    context=Context(fixture);r=context.r;target=tuple(public['Q']);training=None;selector=None
    if target is None or not context.e.on(target) or context.e.mul(r,target) is not None:
        raise ValueError('invalid public target')
    source_bound=max(config['public_source_max'],config.get('selector_training',{}).get('public_source_max',0)
                     if config.get('use_selector') else 0)
    scalars=list(range(1,min(source_bound,r-1)+1))
    projected=projection(context,scalars);rows=[];events=[]
    if config.get('use_selector'):
        from selector_pipeline import phase
        training=phase({'fixture':fixture,'config':config['selector_training'],'seed':seed,'mode':'train'},lambda v:None)
        if training['status']!='complete':
            return {'status':'finite_training_support_exhausted','k':None,'training':training}
        selector=training['models'][public['arm'] if public['arm'] in ['permuted','split_product'] else 'real']
    for scalar,triple,options,branch in attempt_schedule(context,seed,config):
        descriptor,reason=context.descriptor(scalar,triple,options)
        if descriptor is not None:
            if selector is not None:
                from selector_pipeline import accepts,split_bucket
                feature=split_bucket(context,descriptor) if public['arm']=='split_product' else context.bucket(descriptor)
                context.f.counts['selector_lookups']+=1
                if not accepts(selector,feature):events.append('selector_reject');continue
            row,reason=context.construct(descriptor)
            if row is not None:verify_row(fixture,row);rows.append(row)
        events.append(reason or 'accepted')
    rank=certificate(rows,projected,r);logs=rank['solution']
    output={'status':'insufficient_base_rank','k':None,'projection':rank,'source_rows':rows,
            'source_attempts':len(events),'source_statuses':dict(Counter(events)),
            'operation_vector':dict(context.f.counts),'matrix_operation_units':rank['matrix_operation_units'],
            'descent_attempts':0,'descent_witness':None}
    output['public_source_bound']=source_bound
    output['training']=training
    output['cold_start_raw_vector']=dict(Counter(context.f.counts)+Counter({} if training is None else training['operation_vector']))
    if logs is None:return output
    full_logs=dict(projected['known']);full_logs.update(zip(projected['unknown_columns'],logs))
    # A finite public randomized branch schedule, with the same exact branch
    # count and source grid, applied to Q; no unknown target log is used.
    for multiplier,triple,options,branch in attempt_schedule(context,seed,config):
        output['descent_attempts']+=1
        descriptor,reason=context.descriptor(multiplier,triple,options,source=target)
        if descriptor is None:continue
        row,reason=context.construct(descriptor)
        if row is None:continue
        row.update(source_scalar=0,target_coefficient=multiplier)
        verify_row(fixture,row,target=target)
        k=sum(c*full_logs[j] for j,c in enumerate(row['coefficients']))*pow(multiplier,-1,r)%r
        if context.e.mul(k,context.P)!=target:raise ArithmeticError('public final verification failed')
        output.update(status='recovered',k=k,descent_witness=row);break
    else:output['status']='finite_descent_exhausted'
    output['operation_vector']=dict(context.f.counts)
    output['cold_start_raw_vector']=dict(Counter(context.f.counts)+Counter({} if training is None else training['operation_vector']))
    return output


def rho(public):
    """Finite plain Floyd-rho comparator; no best-usable-action claim."""
    fixture=public['fixture'];ctx=Context(fixture);r=ctx.r;Q=tuple(public['Q'])
    config=public['algorithm'];rng=random.Random(f'prym-rho-v1|{fixture["uid"]}|{public["seed"]}')
    def step(state):
        R,a,b=state;part=0 if R is None else R[0]%3
        if part==0:return ctx.e.add(R,ctx.P),(a+1)%r,b
        if part==1:return ctx.e.add(R,R),2*a%r,2*b%r
        return ctx.e.add(R,Q),a,(b+1)%r
    iterations=0
    for restart in range(config['rho_restarts']):
        a,b=rng.randrange(r),rng.randrange(r)
        state=(ctx.e.add(ctx.e.mul(a,ctx.P),ctx.e.mul(b,Q)),a,b);slow=fast=state
        for _ in range(config['rho_iterations_per_restart']):
            slow=step(slow);fast=step(step(fast));iterations+=1
            if slow[0]==fast[0]:
                denominator=(fast[2]-slow[2])%r
                if not denominator:break
                k=(slow[1]-fast[1])*pow(denominator,-1,r)%r
                if ctx.e.mul(k,ctx.P)!=Q:raise ArithmeticError('rho public verification failed')
                return {'status':'recovered','k':k,'iterations':iterations,'restarts':restart,
                        'operation_vector':dict(ctx.f.counts),'stored_states':2,
                        'scope':'Plain three-partition Floyd rho; optimized usable-action baseline not certified.'}
    return {'status':'finite_restarts_exhausted','k':None,'iterations':iterations,
            'operation_vector':dict(ctx.f.counts),'stored_states':2}


def baseline(public):
    """Concrete existing IC comparator, not a claim that it is globally best."""
    sys.path.insert(0,str(ROOT/'src'))
    from crypto_autoresearcher.index_calculus.curve import Curve
    from crypto_autoresearcher.index_calculus.factor_base import FactorBase
    from crypto_autoresearcher.index_calculus.solver import solve_index_calculus
    f=public['fixture'];curve=Curve(f['p'],f['a'],f['b'],f['r'])
    fb=FactorBase('prym_liftable_matched',[tuple(a['point']) for a in f['factor_base']],
                  {'uid':f['uid'],'rule':f['base_rule']},f['p'])
    answer=solve_index_calculus(curve,tuple(f['P']),tuple(public['Q']),m=2,
            factor_base=fb,engine='mitm',accelerate=False,seed=public['seed'],
            max_attempts=public['algorithm']['baseline_max_attempts'],harvest='off')
    return {'status':'recovered' if answer.verified else 'finite_attempts_exhausted',
            'k':answer.k,'ic':answer.to_dict(),
            'scope':'Concrete source-bound mitm m=2 comparator on identical FB; current-best qualification and complete S absent.'}


def worker(public):
    from isolation import isolate
    isolation=isolate();start,clock=perf_counter(),process_time()
    arm=public['arm']
    if arm not in ['ic','ic_aa','candidate','coordinate','permuted','split_product','rho']:
        raise ValueError('undeclared attack arm')
    if arm=='coordinate':
        public=deepcopy(public);fixture=public['fixture'];p=fixture['p']
        fixture['P'][1]=-fixture['P'][1]%p;public['Q'][1]=-public['Q'][1]%p
        for atom in fixture['factor_base']:
            atom['point'][1]=-atom['point'][1]%p;atom['lift'][1]=-atom['lift'][1]%p
        if 'ec1' in fixture:
            identity=fixture['ec1'];identity['curve']['generator']=fixture['P']
            identity.update(curve_identity(identity['field'],identity['curve'],'prymtoy'))
            identity['curve']['curve_id']=identity['curve_id']
    if arm in ['permuted','split_product'] and not public['algorithm'].get('use_selector'):
        raise ValueError('null arm requires the same declared selector treatment')
    result=(baseline if arm.startswith('ic') else rho if arm=='rho' else candidate)(public)
    result.update(isolation=isolation,curve_identity=public['fixture'].get('ec1'),
                  wall_seconds=perf_counter()-start,cpu_seconds=process_time()-clock)
    return result


def challenge(fixture,algorithm,seed,arms=('ic','ic_aa','candidate'),*,software_control=False,native_run_dir=None,seeds=None):
    if not software_control:
        if native_run_dir is None:raise RuntimeError('Admitted native E run directory required; no direct scientific challenge')
        from native_runtime_v2 import binding
        binding(Path(native_run_dir),'EXP-ECDLP-e193fa')
    # OS randomness is held only by this parent. The salted commitment hides
    # tiny test scalars; the worker gets neither k, salt, file path nor seed.
    r=fixture['r'];k=secrets.randbelow(r-1)+1;salt=secrets.token_hex(32)
    identifier=secrets.token_hex(16);Q=multiply(fixture['p'],0,fixture['a'],k,tuple(fixture['P']))
    commitment=sha256(f'prym-E/v1|{identifier}|{salt}|{k}'.encode()).hexdigest()
    results=[]
    order=[(s,arm) for s in ([seed] if seeds is None else seeds) for arm in arms]
    random.Random(f'prym-E-order-v1|{fixture["uid"]}|{seed}').shuffle(order)
    with tempfile.TemporaryDirectory(prefix='prym-private-verifier-') as private:
        sealed=Path(private)/'sealed.json'
        fd=os.open(sealed,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as stream:json.dump({'k':k,'salt':salt},stream)
        for paired_seed,arm in order:
            public={'fixture':fixture,'algorithm':algorithm,'Q':Q,'seed':paired_seed,'arm':arm,
                    'challenge_id':identifier,'hiding_commitment':commitment}
            completed=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker'],
                input=json.dumps(public),text=True,capture_output=True,close_fds=True)
            if completed.returncode:raise RuntimeError('isolated worker failed: '+completed.stderr)
            # Seal exact attack bytes before consulting k for correctness.
            output_hash=sha256(completed.stdout.encode()).hexdigest()
            output=json.loads(completed.stdout);guess=output.get('k')
            verified=(guess is not None and 0<guess<r and guess==k and
                      multiply(fixture['p'],0,fixture['a'],guess,tuple(fixture['P']))==Q)
            if guess is not None and not verified:raise ArithmeticError('incorrect blind answer')
            results.append({'arm':arm,'seed':paired_seed,'sealed_output_sha256':output_hash,
                            'sealed_output_utf8':completed.stdout,'output':output,'verified':verified})
    return {'schema':'prym-blind-challenge/v1','challenge_id':identifier,'Q':Q,
            'commitment_before_attack':commitment,'sealed_outputs':results,
            'reveal_after_outputs':{'k':k,'salt':salt},
            'scientific_E_panel':not software_control,'scope':'Synthetic public curves; raw costs only; no complete S or deployed-curve claim.'}


def run(config,panel,event):
    require_gates(config['gates'])
    directory=Path(sys.argv[sys.argv.index('--run-dir')+1])
    challenges=[]
    for fixture in panel['fixtures']:
        result=challenge(fixture,config['algorithm'],config['seeds'][0],arms=config['arms'],native_run_dir=directory,seeds=config['seeds'])
        challenges.append({'curve_uid':fixture['uid'],**result})
        event({'curve_uid':fixture['uid'],'challenge_id':result['challenge_id'],
               'verified':sum(v['verified'] for v in result['sealed_outputs'])})
    return {'schema':'prym-blind-recovery/v1','complete':True,'challenges':challenges,'cells':[],
            'complete_S_claim':False,'scope':'Only the future frozen matched-cost plan can qualify an improvement.'}


if __name__=='__main__':
    if sys.argv[1:]!=['--worker']:raise SystemExit('Only isolated stdin worker entrypoint is implemented; scientific E remains gated.')
    print(json.dumps(worker(json.load(sys.stdin)),sort_keys=True))
