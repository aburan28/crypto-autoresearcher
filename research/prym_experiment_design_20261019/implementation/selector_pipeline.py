"""Conditional S-stage implementation, with separate isolated phase workers.

No experiment executes on import. Direct CLI supports only the isolated
worker IPC protocol. Native S admission is intentionally still required.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations,product
import json
from math import gcd
from pathlib import Path
import subprocess
import sys

from census import Census
from independent import verify_row
from projection import certificate,projection,row_project
from relations import Context,Rank,uid

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from companion_selector import accepts,fit,split


def require_w_gate(result,verification):
    if verification.get('status')!='passed' or not result.get('complete'):
        raise RuntimeError('S source/witness prerequisite has no complete passed check')
    bad=[(v['curve_uid'],v['seed']) for v in result['cells'] if not v['qualifying_unknown_rank']]
    if bad:raise RuntimeError(f'S nontrivial full-rank prerequisite unmet in {len(bad)} W cells')


def candidate_identity(context,descriptor):
    if context.fixture.get('coordinate_negated'):
        descriptor=deepcopy(descriptor)
        descriptor['points']=[(x,-y%context.p) for x,y in descriptor['points']]
        context.f.counts['coordinate_normalizations']+=1
    return context.canonical_identity(descriptor)


def stream(context,config,seed,event):
    branches=list(product(list(combinations(range(len(context.base)),3)),list(product(range(4),repeat=3))))
    scalars=min(config['public_source_max'],context.r-1);total=scalars*len(branches)
    domain=f"{config['domain']}|{context.fixture['uid']}|{seed}"
    step=int(sha256((domain+'|step').encode()).hexdigest(),16)%total
    while gcd(step,total)!=1:step=(step+1)%total
    offset=int(sha256((domain+'|offset').encode()).hexdigest(),16)%total;seen=set()
    for index in range(total):
        code=(step*index+offset)%total;scalar=code//len(branches)+1
        triple,options=branches[code%len(branches)]
        descriptor,reason=context.descriptor(scalar,triple,options);ident=None
        if descriptor is not None:
            ident=uid(candidate_identity(context,descriptor));context.f.counts['candidate_hashes']+=1
            if ident in seen:reason='canonical_alias'
            else:seen.add(ident)
        event({'phase':'enumerate','index':index,'scalar':scalar,'triple':triple,'options':options,
               'candidate_id':ident,'status':reason or 'eligible'})
        if reason is None:yield ident,scalar,triple,options,descriptor


def split_bucket(context,descriptor):
    # Independent auxiliary points on the same-dimensional elliptic factor,
    # fixed by public point encodings. No relation outcome or source log is used.
    total=None
    cache=getattr(context,'split_cache',None)
    if cache is None:context.split_cache={};cache=context.split_cache
    identity=candidate_identity(context,descriptor)
    context.f.counts['split_canonicalizations']+=1
    encoded=identity['signed_fb_lift_ids']
    points=[tuple(encoded['source_lift'])]+[(x,y) for j,sign,x,y in encoded['base_lifts']]
    for point in points:
        if point not in cache:
            x=int(uid({'domain':'prym-S-split-v1','curve':context.fixture['uid'],'point':point}),16)%context.p
            context.f.counts['split_point_hashes']+=1
            for _ in range(context.p):
                y=context.f.sqrt(context.aux.rhs(x))
                if y is not None:cache[point]=(x,y);break
                x=(x+1)%context.p
            else:raise ArithmeticError('auxiliary curve has no affine point')
        else:context.f.counts['split_cache_hits']+=1
        total=context.aux.add(total,cache[point])
    if total is None:return 'infinity'
    w=total[0];context.f.counts['modular_pow']+=1
    symbol=pow(w,(context.p-1)//2,context.p);symbol=-1 if symbol==context.p-1 else symbol
    return f'{symbol:+d}:{16*w//context.p:02d}'


def phase(public,event):
    config=public['config'];fixture=public['fixture'];seed=public['seed'];mode=public['mode']
    arm=public.get('arm','identity')
    if arm=='coordinate':
        fixture=deepcopy(fixture);p=fixture['p'];fixture['coordinate_negated']=True
        fixture['P'][1]=-fixture['P'][1]%p
        for atom in fixture['factor_base']:
            atom['point'][1]=-atom['point'][1]%p;atom['lift'][1]=-atom['lift'][1]%p
    context=Context(fixture);quota=config['candidates_per_split'];collected=0
    scalars=range(1,min(config['public_source_max'],context.r-1)+1)
    projected=projection(context,scalars);rank=Rank(len(projected['unknown_columns']),context.r)
    records=[];rows=[];counts=Counter();models=public.get('models',{})
    reference=Census(fixture) if mode=='census' else None
    wanted='train' if mode=='train' else 'holdout'
    if mode=='arm' and rank.columns==0:
        return {'status':'all_columns_publicly_known','qualifying':False,'U':0,'rank':0,'candidates':0,
                'operation_vector':dict(context.f.counts),'rows':[]}
    for ident,scalar,triple,options,descriptor in stream(context,config,seed,event):
        if split(ident)!=wanted:continue
        collected+=1
        if mode=='train':
            real=context.bucket(descriptor);null=split_bucket(context,descriptor)
            row,reason=context.construct(descriptor)
            if row is not None:verify_row(fixture,row)
            record={'candidate_id':ident,'bucket':real,'split_bucket':null,'accepted':row is not None}
            records.append(record);event({'phase':'training_label',**record})
        elif mode=='census':
            row=reference.accepted(scalar,triple,options)
            if row is not None:
                rows.append(row);rank.add(*row_project(row,projected,context.r))
            real=context.bucket(descriptor);null=split_bucket(context,descriptor)
            predictions={name:accepts(model,null if name=='split_product' else real)
                         for name,model in models.items()}
            event({'phase':'census_label','candidate_id':ident,'accepted':row is not None,
                   'rank':len(rank.pivots),'frozen_predictions':predictions})
        else:
            if arm in ['identity','identity_aa']:keep=True
            else:
                feature=split_bucket(context,descriptor) if arm=='split_product' else context.bucket(descriptor)
                context.f.counts['selector_lookups']+=1
                keep=accepts(models['real' if arm=='coordinate' else arm],feature)
            row,reason=context.construct(descriptor) if keep else (None,'selector_reject')
            counts[reason or 'accepted']+=1
            if row is not None:
                verify_row(fixture,row);rows.append(row);rank.add(*row_project(row,projected,context.r))
            event({'phase':'holdout_attack','arm':arm,'candidate_id':ident,'keep':keep,
                   'accepted':row is not None,'rank':len(rank.pivots),'status':reason or 'accepted'})
            if len(rank.pivots)==rank.columns:break
        if collected==quota:break
    finite_enough=collected==quota or (mode=='arm' and len(rank.pivots)==rank.columns)
    output={'status':'complete' if finite_enough else 'finite_support_exhausted','qualifying':False,
            'candidates':collected,'requested':quota,'U':rank.columns,'rank':len(rank.pivots),
            'operation_vector':dict(context.f.counts),'matrix_operation_units':rank.ops,
            'rows':rows,'counts':dict(counts),'cache_entries':len(context.source_cache)+len(context.aux_cache),
            'scope':'Raw partial work vectors only; no complete S or IC gain.'}
    if arm=='coordinate':
        for row in output['rows']:
            row['constraints']=[[x,-y%context.p] for x,y in row['constraints']]
            row['v_coefficients']=[-x%context.p for x in row['v_coefficients']]
    if mode=='train' and finite_enough:
        perm=sorted(range(len(records)),key=lambda j:sha256(f'prym-S-null|{seed}|{records[j]["candidate_id"]}'.encode()).digest())
        labels=[records[j]['accepted'] for j in perm]
        plain=lambda row,bucket,accepted:{'candidate_id':row['candidate_id'],'bucket':bucket,'accepted':accepted}
        output['models']={'real':fit([plain(v,v['bucket'],v['accepted']) for v in records]),
          'permuted':fit([plain(v,v['bucket'],label) for v,label in zip(records,labels)]),
          'split_product':fit([plain(v,v['split_bucket'],v['accepted']) for v in records])}
        output['null_permutation']=perm;output['model_hashes']={k:uid(v) for k,v in output['models'].items()}
        output['advice_bytes']=len(json.dumps(output['models'],sort_keys=True).encode())
    return output


def invoke(public,event):
    process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,close_fds=True)
    process.stdin.write(json.dumps(public));process.stdin.close();result=None
    for line in process.stdout:
        record=json.loads(line)
        if record.get('type')=='result':result=record['value']
        else:event({**record,'curve_uid':public['fixture']['uid'],'seed':public['seed'],
                    'worker_mode':public['mode'],'worker_arm':public.get('arm')})
    if process.wait()!=0 or result is None:raise RuntimeError('isolated selector worker failed')
    return result


def run(config,panel,event):
    # This cannot be admitted as a successful S-stage experiment until the
    # fixed W prerequisite and complete baseline/cost bindings are released.
    root=Path(__file__).resolve().parents[3]
    require_w_gate(json.loads((root/config['w_result']).read_text()),json.loads((root/config['w_verification']).read_text()))
    cells=[]
    for fixture in panel['fixtures']:
        for seed in config['seeds']:
            public={'config':config,'fixture':fixture,'seed':seed}
            training=invoke({**public,'mode':'train'},event)
            if training['status']!='complete':
                cells.append({'curve_uid':fixture['uid'],'p':fixture['p'],'seed':seed,
                              'status':'finite_support_exhausted','training':training,
                              'projection':{'rank':0,'U':training['U']}});continue
            # Models frozen before census. No census object or truth file is
            # passed to attack workers; Landlock denies the run directory.
            arms={}
            order=['identity','identity_aa','real','permuted','split_product','coordinate']
            if seed%2:order.reverse()
            for arm in order:
                arms[arm]=invoke({**public,'mode':'arm','arm':arm,'models':training['models']},event)
            census=invoke({**public,'mode':'census','models':training['models']},event)
            aa=all(arms['identity'][k]==arms['identity_aa'][k] for k in ['rank','candidates','operation_vector','rows'])
            coordinate=all(arms['real'][k]==arms['coordinate'][k] for k in ['rank','candidates','rows'])
            for arm,value in arms.items():
                training_vector=training['operation_vector'] if arm not in ['identity','identity_aa'] else {}
                value['cold_start_raw_vector']=dict(Counter(training_vector)+Counter(value['operation_vector']))
                value['cold_start_accounting']='Full joint real/null training charged to each treatment; no training charged to identity. Partial raw units only.'
            cells.append({'curve_uid':fixture['uid'],'p':fixture['p'],'seed':seed,'training':training,
                          'arms':arms,'census':census,'aa_exact':aa,'coordinate_exact':coordinate,
                          'projection':{'rank':arms['identity']['rank'],'U':arms['identity']['U']},
                          'complete_S_claim':False})
    return {'schema':'prym-selector-audit/v1','complete':True,'cells':cells,
            'scope':'Conditional finite engineering diagnostics; no complete S or current-IC advantage.'}


if __name__=='__main__':
    if sys.argv[1:]!=['--worker']:raise SystemExit('Only isolated worker IPC; scientific S requires native admission.')
    from isolation import isolate
    isolation=isolate();public=json.load(sys.stdin)
    def emit(record):print(json.dumps(record,sort_keys=True),flush=True)
    answer=phase(public,emit);answer['isolation']=isolation
    emit({'type':'result','value':answer})
