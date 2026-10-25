"""Frozen finite public-source audit; CLI is the native experiment launcher."""
from collections import Counter
from copy import deepcopy
from itertools import combinations,product
import json
import random
from time import perf_counter,process_time

from independent import verify_fixture,verify_row
from projection import certificate,projection
from relations import Context,uid


def controls():
    # Deliberately planted SOFTWARE control, never an unknown-log test cell.
    fixture={'p':19,'a':0,'b':3,'r':13,'P':[1,17],'uid':'planted-software-control',
             'factor_base':[{'point':[1,2],'lift':[1,2]},
                            {'point':[7,2],'lift':[8,2]},
                            {'point':[11,2],'lift':[7,2]}]}
    context=Context(fixture)
    descriptor,reason=context.descriptor(1,(0,1,2),(2,0,0))
    row,reason=context.construct(descriptor)
    if reason or not verify_row(fixture,row):raise ArithmeticError('planted control failed')
    records=[{'control':'valid_principal_function','expected':'accept','observed':'accept'}]
    mutations={
      'false_public_scalar':lambda v:v.update(source_scalar=2),
      'wrong_sign':lambda v:v['base_labels'][0].__setitem__(1,-v['base_labels'][0][1]),
      'missing_infinity_term':lambda v:v.update(pole_orders_at_infinity=[3,0]),
      'repeated_intersection':lambda v:v['residual_roots'].__setitem__(0,v['constraints'][0][0]),
      'post_hoc_kernel':lambda v:v.update(source_locator='K=i(R)-sum(eD); constructed after tuple'),
      'unknown_tuple_source':lambda v:v.update(source_scalar=None),
    }
    for label,mutate in mutations.items():
        bad=deepcopy(row);mutate(bad)
        try:verify_row(fixture,bad)
        except (ValueError,TypeError,KeyError,IndexError,StopIteration):observed='reject'
        else:raise ArithmeticError('false witness accepted: '+label)
        records.append({'control':label,'expected':'reject','observed':observed})
    # An unrelated auxiliary point may cancel with its negative but does not
    # provide the missing public source label. Never give it to a log oracle.
    bad=deepcopy(row);bad['source_scalar']=None
    try:verify_row(fixture,bad)
    except (ValueError,TypeError):pass
    else:raise ArithmeticError('split-product control manufactured a source')
    records.append({'control':'split_product_cancellation_without_source','expected':'reject','observed':'reject'})
    # Exact projected rank controls: zero, duplicate and sign columns merge;
    # known columns leave no unknowns and do not count as new useful rank.
    from independent import canonical_columns,dense_rank
    columns=canonical_columns(19,[[1,2],[1,17],None,[7,2],[1,2]],{(7,2):4})
    if columns['U']!=1 or columns['column_map']!=[[0,1],[0,-1],None,['known',4],[0,1]]:
        raise ArithmeticError('column quotient control failed')
    if dense_rank([[1,0],[1,0],[0,0]],13)!=1 or dense_rank([[1,0],[0,1]],13)!=2:
        raise ArithmeticError('rank control failed')
    all_known=canonical_columns(19,[[1,2],[1,17]],{(1,2):1})
    if all_known['U']!=0:raise ArithmeticError('known-log control failed')
    records.extend([{'control':label,'expected':'exact','observed':'exact'}
                    for label in ['duplicate_sign_zero_columns','all_known_base_U_zero','dependent_matrix_rank']])
    return records


def attempt_schedule(context,seed,config):
    scalars=list(range(1,min(config['public_source_max'],context.r-1)+1))
    random.Random(f"{config['domain']}|sources|{context.fixture['uid']}|{seed}").shuffle(scalars)
    tuples=list(product(list(combinations(range(len(context.base)),3)),list(product(range(4),repeat=3))))
    rng=random.Random(f"{config['domain']}|tuples|{context.fixture['uid']}|{seed}")
    for scalar in scalars:
        indices=rng.sample(range(len(tuples)),config['branches_per_source'])
        for branch in indices:
            triple,options=tuples[branch]
            yield scalar,triple,options,branch


def transported(fixture,row,seed):
    permutation=list(range(len(fixture['factor_base'])))
    random.Random(f"prym-W-reencode-v1|{seed}").shuffle(permutation)
    inverse={old:new for new,old in enumerate(permutation)}
    other=deepcopy(fixture);other['factor_base']=[fixture['factor_base'][j] for j in permutation]
    witness=deepcopy(row)
    witness['coefficients']=[row['coefficients'][j] for j in permutation]
    witness['base_labels']=[[inverse[j],sign,option] for j,sign,option in row['base_labels']]
    verify_row(other,witness)
    restored=[witness['coefficients'][inverse[j]] for j in range(len(permutation))]
    if restored!=row['coefficients']:raise ArithmeticError('A/A transport failed')
    return uid(witness)


def run(config,panel,event):
    start,clock=perf_counter(),process_time()
    result={'schema':'prym-witness-audit/v1','controls':controls(),'cells':[],
            'complete':False,'secret_labels_present':False,'generator':'fixed PO003 cubic interpolation'}
    for fixture in panel['fixtures']:
        verify_fixture(fixture)
        for seed in config['seeds']:
            context=Context(fixture)
            scalars=list(range(1,min(config['public_source_max'],context.r-1)+1))
            projected=projection(context,scalars)
            rows=[];reasons=Counter();seen=set();aa=[];attempts=0
            for scalar,triple,options,branch in attempt_schedule(context,seed,config):
                attempts+=1
                descriptor,reason=context.descriptor(scalar,triple,options)
                ident=None
                if descriptor is not None:
                    ident=uid(context.canonical_identity(descriptor));context.f.counts['candidate_hashes']+=1
                    if ident in seen:reason='canonical_alias'
                    else:
                        seen.add(ident)
                        row,reason=context.construct(descriptor)
                        if row is not None:
                            verify_row(fixture,row)
                            aa.append(transported(fixture,row,seed))
                            rows.append(row)
                reasons[reason or 'accepted']+=1
                event({'curve_uid':fixture['uid'],'seed':seed,'attempt':attempts,'scalar':scalar,
                       'triple':triple,'options':options,'branch':branch,'candidate_id':ident,
                       'status':reason or 'accepted','row_index':len(rows)-1 if reason is None else None})
            rank=certificate(rows,projected,context.r)
            result['cells'].append({'curve_uid':fixture['uid'],'p':fixture['p'],'seed':seed,
                'attempts':attempts,'reasons':dict(reasons),'distinct_candidates':len(seen),
                'rows':rows,'projection':rank,'transported_witness_hashes':aa,
                'attack_operation_vector':dict(context.f.counts),
                'cache_entries':{'source':len(context.source_cache),'auxiliary':len(context.aux_cache)},
                'checker_cost_included_in_attack_vector':False,
                'qualifying_unknown_rank':rank['U']>0 and rank['rank']==rank['U']})
    result.update(complete=True,wall_seconds=perf_counter()-start,cpu_seconds=process_time()-clock,
                  input_construction_costs=panel['search_trace'],
                  scope='Public source validity and exact projected rank; no DLP speed claim.')
    return result
