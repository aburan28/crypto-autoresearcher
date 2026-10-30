"""Separate complete E enumeration and pair-query/affine/kernel checks; no producer imports."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/prym_experiment_design_20261019/implementation'))
sys.path.insert(0,str(ROOT/'research/prym_factor_base_width_20261025'))
from independent import add, multiply, dense_rank, verify_fixture, verify_row as verify_old_row
from check_inputs import public_projection


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()+b'\n'


def key(row):
    return (row['source_scalar'],tuple(row['triple']),tuple(row['signs']))


def projected(row,projection,r):
    vector = [0]*projection['U']; rhs = row['source_scalar']
    if len(row['coefficients'])!=len(projection['native_to_projected']): raise ValueError('coefficient width differs')
    for c,m in zip(row['coefficients'],projection['native_to_projected'],strict=True):
        if m[0]=='known': rhs -= c*m[1]
        elif m[0]=='unknown': vector[m[1]] += c*m[2]
    return [v%r for v in vector],rhs%r


def normalized(rows,projection,r):
    values=set()
    for row in rows:
        v,b=projected(row,projection,r); affine=v+[b]; first=next((x for x in affine if x),None)
        values.add(tuple(x*pow(first,-1,r)%r for x in affine) if first else tuple(affine))
    return [list(v) for v in sorted(values)]


def check_elimination(record,rows,projection,r):
    width=projection['U']; matrix=[v+[b] for v,b in [projected(row,projection,r) for row in rows]]
    rank=dense_rank([v[:-1] for v in matrix],r)
    if (record['rank']!=rank or record['columns']!=width or record['nullity']!=width-rank or dense_rank(matrix,r)!=rank):
        raise ValueError('affine rank differs or inconsistent')
    indices=record['independent_row_indices']; pivots=record['pivots']
    if (len(indices)!=rank or indices!=sorted(set(indices)) or any(type(i)is not int or not 0<=i<len(rows) for i in indices) or
        dense_rank([matrix[i] for i in indices],r)!=rank or len(pivots)!=rank): raise ValueError('pivot row basis differs')
    pivotrows=[]
    for text,row in pivots.items():
        column=int(text)
        if str(column)!=text or not 0<=column<width or len(row)!=width+1 or row[column]!=1 or any(row[:column]):
            raise ValueError('bad normalized pivot')
        if any(type(v)is not int or not 0<=v<r for v in row): raise ValueError('noncanonical pivot entry')
        pivotrows.append(row)
    if dense_rank(matrix+pivotrows,r)!=rank or dense_rank(pivotrows,r)!=rank: raise ValueError('pivot span differs')


def check_kernel(vectors,rows,projection,r,rank):
    width=projection['U']; matrix=[projected(row,projection,r)[0] for row in rows]
    if (len(vectors)!=width-rank or any(len(v)!=width for v in vectors) or dense_rank(vectors,r)!=len(vectors) or
        any(sum(x*y for x,y in zip(v,k))%r for v in matrix for k in vectors)):
        raise ValueError('incomplete or false kernel')


def check_analysis(cell,result):
    rows=result['rows']; projection=result['projection']; r=cell['fixture']['r']; analysis=result['analysis']; old=cell['preprocessing_rows']
    for label,selected in [('preprocessing',old),('new',rows),('combined',old+rows)]: check_elimination(analysis[label],selected,projection,r)
    equations=normalized(rows,projection,r)
    if (analysis['rows']!=len(rows) or analysis['normalized_equations']!=equations or analysis['distinct_equations']!=len(equations) or
        analysis['rank_gain']!=analysis['combined']['rank']-analysis['preprocessing']['rank']): raise ValueError('equation count or rank gain differs')
    check_kernel(analysis['old_kernel'],old,projection,r,analysis['preprocessing']['rank'])
    check_kernel(analysis['kernel'],old+rows,projection,r,analysis['combined']['rank'])
    action=[[sum(x*y for x,y in zip(projected(row,projection,r)[0],k))%r for k in analysis['old_kernel']] for row in rows]
    if analysis['old_kernel_syndromes']!=action or analysis['nonzero_old_kernel_syndromes']!=sum(any(v) for v in action):
        raise ValueError('old kernel action differs')
    phases=result['collection_phases']+analysis['analysis_phases']; total=Counter()
    if len({p['phase'] for p in phases})!=len(phases): raise ValueError('overlapping phase labels')
    for phase in phases:
        if phase['status']!='complete' or phase['wall_valid']is not False: raise ValueError('phase not complete or invalid clock claim')
        if any(type(v)is not int or v<0 for v in phase['counters'].values()): raise ValueError('invalid counters')
        total.update(phase['counters'])
    if dict(total)!=analysis['total_counters']: raise ValueError('counter conservation differs')
    collection=Counter()
    for phase in result['collection_phases']: collection.update(phase['counters'])
    if dict(collection)!=result['collection_counters']: raise ValueError('collection counters differ')
    return dict(arm=result['arm'],rank_gain=analysis['rank_gain'],combined_rank=analysis['combined']['rank'],
                new_rank=analysis['new']['rank'],base_rank=analysis['preprocessing']['rank'],
                distinct_equations=len(equations),accepted_witnesses=len(rows))


def check(cell,aggregate):
    fixture=cell['fixture']; verify_fixture(fixture); p,r=fixture['p'],fixture['r']; n=len(fixture['factor_base']); order=cell['source_order']
    if (aggregate['schema']!='direct-three-sum-cell/v1' or aggregate['cell_id']!=cell['id'] or aggregate['curve_uid']!=fixture['uid'] or
        aggregate['complete']is not True or len(aggregate['arms'])!=2): raise ValueError('wrong aggregate identity')
    base=[tuple(a['point']) for a in fixture['factor_base']]
    signed={(j,s):(q[0],s*q[1]%p) for j,q in enumerate(base) for s in (1,-1)}
    sources={s:multiply(p,0,fixture['a'],s,tuple(fixture['P'])) for s in order}
    plus=lambda x,y:add(p,0,fixture['a'],x,y)
    rows=[]; blocks=[]; digest=sha256(); attempts=0
    for scalar in order:
        statuses=[]; source_digest=sha256()
        for triple in combinations(range(n),3):
            for signs in product((1,-1),repeat=3):
                attempts+=1; total=plus(plus(signed[triple[0],signs[0]],signed[triple[1],signs[1]]),signed[triple[2],signs[2]])
                hit=total==sources[scalar]; statuses.append('+' if hit else '.')
                if hit:
                    coefficients=[0]*n
                    for j,s in zip(triple,signs): coefficients[j]=s%r
                    rows.append(dict(schema='direct-three-sum-row/v1',curve_uid=fixture['uid'],source_scalar=scalar,
                                     triple=list(triple),signs=list(signs),coefficients=coefficients))
                data=encoded([scalar,triple,signs,hit]);digest.update(data);source_digest.update(data)
        blocks.append(dict(scalar=scalar,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest()))
    rows.sort(key=key); enumeration=dict(attempts=attempts,status_blocks=blocks,branch_sha256=digest.hexdigest(),pair_entries=[])
    pairs=[]; table=defaultdict(list)
    for (j,k),signs in product(combinations(range(n),2),product((1,-1),repeat=2)):
        point=plus(signed[j,signs[0]],signed[k,signs[1]])
        pairs.append(dict(indices=[j,k],signs=list(signs),point=None if point is None else list(point)));table[point].append(len(pairs)-1)
    blocks=[];digest=sha256();queries=0;extracted=[]
    for scalar in order:
        records=[]; source_digest=sha256()
        for third,sign in product(range(n),(1,-1)):
            queries+=1;point=signed[third,sign]; wanted=plus(sources[scalar],(point[0],-point[1]%p));bucket=table.get(wanted,[])
            accepted=[i for i in bucket if pairs[i]['indices'][1]<third]
            for i in accepted: extracted.append((scalar,tuple(pairs[i]['indices']+[third]),tuple(pairs[i]['signs']+[sign])))
            record=dict(third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=list(bucket),accepted=accepted)
            records.append(record);data=encoded([scalar,record]);digest.update(data);source_digest.update(data)
        blocks.append(dict(scalar=scalar,attempts=queries,queries=records,branch_sha256=source_digest.hexdigest()))
    if sorted(extracted)!=[key(row) for row in rows]: raise ValueError('reference table fails enumerated relation equality')
    pair_table=dict(attempts=queries,status_blocks=blocks,branch_sha256=digest.hexdigest(),pair_entries=pairs)
    projection=public_projection(fixture,order); summaries=[]
    for result,name,expected in zip(aggregate['arms'],('enumeration','pair_table'),(enumeration,pair_table),strict=True):
        expected.update(schema='direct-three-sum/v1',curve_uid=fixture['uid'],arm=name,source_order=order,complete=True,rows=rows,projection=projection)
        if any(result.get(k)!=v for k,v in expected.items()): raise ValueError('complete direct branch/row/query replay differs')
        counters=result['collection_counters']
        if name=='enumeration':
            if counters.get('descriptors')!=attempts or counters.get('point_comparisons')!=attempts+len(rows): raise ValueError('logical enumeration counters differ')
        elif (counters.get('queries')!=queries or counters.get('pair_table_lookups')!=queries or counters.get('pair_table_insertions')!=len(pairs) or
              counters.get('bucket_entries_inspected',0)!=sum(len(q['bucket']) for block in blocks for q in block['queries'])):
            raise ValueError('logical pair-table counters differ')
        summaries.append(check_analysis(cell,result))
    for row in cell['preprocessing_rows']: verify_old_row(fixture,row)
    index={key(row):i for i,row in enumerate(rows)}; matches=[]
    for row in cell['archived_norm_rows']:
        labels=row['base_labels']; candidate=(row['source_scalar'],tuple(v[0] for v in labels),tuple(v[1] for v in labels))
        if row['norm_completed']is not True or row['curve_uid']!=fixture['uid'] or candidate not in index: raise ValueError('archived norm row missing in direct census')
        direct=rows[index[candidate]]
        if direct['coefficients']!=row['coefficients']: raise ValueError('archived norm coefficient identity differs')
        images=row['residual_E_images']
        if images[0][0]!=images[1][0] or (images[0][1]+images[1][1])%p: raise ValueError('archived norm images do not cancel')
        matches.append(index[candidate])
    return dict(checked=True,complete_branch_replay=True,attempts_replayed=attempts,pair_entries_checked=len(pairs),queries_checked=queries,
                rows_verified=len(rows),arms=summaries,archived_norm_subset=dict(witnesses=len(matches),
                distinct_direct_descriptors=len(set(matches)),direct_row_indices=matches),
                scope='Separate full E and pair-query replay/dense affine/kernel checks. No staffed review, producer field-counter audit or archived C replay.')
