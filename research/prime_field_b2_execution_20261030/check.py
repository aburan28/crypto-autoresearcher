"""Full independent shifted replay; imports no producer arithmetic or solver."""
from collections import Counter
from hashlib import sha256
from itertools import combinations,product
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/prym_experiment_design_20261019/implementation'))
from independent import add,multiply,convolution,evaluate,vandermonde,verify_fixture,dense_rank,verify_row as verify_old_row
sys.path.insert(0,str(ROOT/'research/prym_factor_base_width_20261025'))
from check_inputs import public_projection

LEGEND=dict(S='source_no_rational_lift',D='duplicate_interpolation_x',P='exceptional_pole_order',
            R='residual_not_two_distinct_rational_roots',X='intersection_not_squarefree',
            B='residual_endpoint_outside_active_subset',A='canonical_alias',**{'+':'accepted'})


def polynomial(p,a,b,h):
    coefficients=[1]
    for _ in range(3):coefficients=convolution(p,coefficients,[h,0,1])
    coefficients[0]=(coefficients[0]+a*h+b)%p;coefficients[2]=(coefficients[2]+a)%p
    return coefficients


class Reference:
    def __init__(self,fixture,h,active):
        self.fixture=fixture;self.p=fixture['p'];self.h=h;self.active=list(active)
        if type(h) is not int or not 0<=h<self.p or active!=sorted(set(active)) or len(active)<3:
            raise ValueError('canonical shift/active atoms required')
        self.F=polynomial(self.p,fixture['a'],fixture['b'],h)
        if not self.F[0]:raise ValueError('singular shifted cover')
        self.roots={};self.sources={};self.lifts={}
        for x in range(self.p):self.roots.setdefault(x*x%self.p,x)
        for j in active:
            u,y=fixture['factor_base'][j]['point'];x=self.roots.get((u-h)%self.p)
            if x is None:raise ValueError('active atom has no cover lift')
            self.lifts[j]=(x,y)

    def descriptor(self,scalar,triple,options):
        if scalar not in self.sources:
            point=multiply(self.p,0,self.fixture['a'],scalar,tuple(self.fixture['P']))
            root=None if point is None else self.roots.get((point[0]-self.h)%self.p)
            self.sources[scalar]=None if root is None else (root,-point[1]%self.p)
        source=self.sources[scalar]
        if source is None:return None,'S'
        points=[source]
        for j,option in zip(triple,options):
            x,y=self.lifts[j];points.append(((-x if option&2 else x)%self.p,(-y if option&1 else y)%self.p))
        return (None,'D') if len({x for x,y in points})!=4 else (points,None)

    def outcome(self,scalar,triple,options,seen):
        points,status=self.descriptor(scalar,triple,options)
        if points is None:return status,None,None
        identities=[]
        for deck,sign in product((1,-1),repeat=2):
            transformed=[(deck*x%self.p,sign*y%self.p) for x,y in points]
            labels=sorted((j,sign*(-1 if op&1 else 1),*point) for j,op,point in zip(triple,options,transformed[1:]))
            identities.append(dict(curve_uid=self.fixture['uid'],source_scalar=sign*scalar%self.fixture['r'],
                **{'lambda':1},signed_fb_lift_ids=dict(source_lift=transformed[0],base_lifts=labels)))
        encode=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'))
        chosen=min(identities,key=encode)
        chosen.update(cover_shift=self.h,active_atoms=self.active)
        key=sha256(encode(chosen).encode()).hexdigest()
        if key in seen:return 'A',key,None
        seen.add(key);v=vandermonde(self.p,points)
        if len(v)==4 and v[-1]*v[-1]%self.p==1:return 'P',key,None
        vv=convolution(self.p,v,v)
        remainder=[((vv[j] if j<len(vv) else 0)-self.F[j])%self.p for j in range(7)]
        divisor=[1]
        for x,y in points:divisor=convolution(self.p,divisor,[-x%self.p,1])
        quotient=[0]*3
        for j in (2,1,0):
            quotient[j]=remainder[j+4]
            for i,c in enumerate(divisor):remainder[j+i]=(remainder[j+i]-quotient[j]*c)%self.p
        if any(remainder):raise ValueError('independent shifted residual division failed')
        c,b,a=quotient;disc=(b*b-4*a*c)%self.p
        if not a or not disc or disc not in self.roots:return 'R',key,None
        root=self.roots[disc];inv=pow(2*a,-1,self.p)
        roots=sorted({(-b-root)*inv%self.p,(-b+root)*inv%self.p})
        if len(roots)!=2 or set(roots)&{x for x,y in points}:return 'X',key,None
        coefficients=[0]*len(self.fixture['factor_base'])
        for j,option in zip(triple,options):coefficients[j]+=(-1 if option&1 else 1)
        for x in roots:
            y=evaluate(self.p,v,x)
            matches=[(j,sign) for j in self.active for sign in (1,-1)
                     if self.fixture['factor_base'][j]['point']==[(x*x+self.h)%self.p,sign*y%self.p]]
            if len(matches)!=1:return 'B',key,None
            j,sign=matches[0];coefficients[j]+=sign
        row=dict(schema='prym-shifted-row/v1',curve_uid=self.fixture['uid'],cover_shift=self.h,
            active_atoms=self.active,source_scalar=scalar,coefficients=[c%self.fixture['r'] for c in coefficients],
            constraints=[list(p) for p in points],base_labels=[[j,-1 if op&1 else 1,op] for j,op in zip(triple,options)],
            v_coefficients=v,residual_coefficients=quotient,residual_roots=roots,pole_orders_at_infinity=[3,3],
            source_locator='shifted cubic interpolation and residual quadratic; no post-hoc kernel')
        return '+',key,row


def verify_row(fixture,h,active,row):
    p,a,b,r=(fixture[k] for k in ('p','a','b','r'))
    if (row.get('schema')!='prym-shifted-row/v1' or row.get('curve_uid')!=fixture['uid'] or
        row.get('cover_shift')!=h or row.get('active_atoms')!=active or row.get('target_coefficient',0) or
        row.get('pole_orders_at_infinity')!=[3,3] or row.get('source_locator')!='shifted cubic interpolation and residual quadratic; no post-hoc kernel'):
        raise ValueError('wrong shifted witness identity')
    points=[tuple(point) for point in row['constraints']]
    if len(points)!=4 or len({x for x,y in points})!=4:raise ValueError('duplicate/bad interpolation points')
    if type(row['source_scalar']) is not int or not 0<row['source_scalar']<r:raise ValueError('invalid public source scalar')
    source=multiply(p,0,a,row['source_scalar'],tuple(fixture['P']))
    if source is None or ((points[0][0]**2+h)%p,points[0][1])!=(source[0],-source[1]%p):
        raise ValueError('false shifted source label')
    v=vandermonde(p,points)
    if v!=row['v_coefficients'] or len(v)==4 and v[-1]*v[-1]%p==1:raise ValueError('interpolation/pole certificate differs')
    F=polynomial(p,a,b,h);known=[1]
    for x,y in points:known=convolution(p,known,[-x%p,1])
    vv=convolution(p,v,v);intersection=[((vv[j] if j<len(vv) else 0)-F[j])%p for j in range(7)]
    residual=row['residual_coefficients'];roots=row['residual_roots']
    if len(residual)!=3 or not residual[-1] or convolution(p,known,residual)!=intersection:
        raise ValueError('shifted principal-function identity differs')
    if roots!=sorted(set(roots)) or len(roots)!=2 or len(set(roots+[x for x,y in points]))!=6 or any(evaluate(p,residual,x) for x in roots):
        raise ValueError('missing/repeated residual roots')
    all_points=points+[(x,evaluate(p,v,x)) for x in roots]
    if any((y*y-evaluate(p,F,x))%p for x,y in all_points):raise ValueError('intersection point off shifted cover')
    if len(row['base_labels'])!=3:raise ValueError('wrong active labels')
    coefficients=[0]*len(fixture['factor_base'])
    square_roots={}
    for x in range(p):square_roots.setdefault(x*x%p,x)
    for point,(j,sign,option) in zip(points[1:],row['base_labels']):
        if j not in active or sign!=(-1 if option&1 else 1) or option not in range(4):raise ValueError('inactive/bad atom label')
        u,y=fixture['factor_base'][j]['point'];x=square_roots.get((u-h)%p)
        if x is None or point!=((-x if option&2 else x)%p,sign*y%p):raise ValueError('false shifted atom lift')
        coefficients[j]+=sign
    for x,y in all_points[4:]:
        matches=[(j,sign) for j in active for sign in (1,-1) if fixture['factor_base'][j]['point']==[(x*x+h)%p,sign*y%p]]
        if len(matches)!=1:raise ValueError('residual outside active atoms')
        j,sign=matches[0];coefficients[j]+=sign
    if [c%r for c in coefficients]!=row['coefficients']:raise ValueError('native coefficient certificate differs')
    total=None
    for coefficient,atom in zip(coefficients,fixture['factor_base']):total=add(p,0,a,total,multiply(p,0,a,coefficient,tuple(atom['point'])))
    if total!=source:raise ValueError('original E equation fails')
    c0,c2,c4=F[0],F[2],F[4];auxiliary=None
    for x,y in all_points:
        if not x:continue
        inverse=pow(x,-1,p);U=c0*inverse**2%p;V=c0*y*inverse**3%p
        if (V*V-U**3-c2*U*U-c4*c0*U-c0*c0)%p:raise ValueError('shifted auxiliary map fails')
        auxiliary=add(p,c2,c4*c0%p,auxiliary,(U,V))
    if auxiliary is not None:raise ValueError('auxiliary principal sum fails')
    return True


def project(row,projection,r):
    vector,rhs=[0]*projection['U'],row['source_scalar']
    for c,mapping in zip(row['coefficients'],projection['native_to_projected'],strict=True):
        if mapping[0]=='known':rhs-=c*mapping[1]
        elif mapping[0]=='unknown':vector[mapping[1]]+=c*mapping[2]
    return [x%r for x in vector],rhs%r


def quality(rows,projection,r):
    projected=[project(row,projection,r) for row in rows];M=[v for v,b in projected]
    rank=dense_rank(M,r)
    if dense_rank([v+[b] for v,b in projected],r)!=rank:raise ValueError('inconsistent affine rows')
    equations=set()
    for v,b in projected:
        affine=v+[b];first=next((x for x in affine if x),None)
        equations.add(tuple(x*pow(first,-1,r)%r for x in affine) if first else tuple(affine))
    return dict(rows=len(rows),unique_affine_equations=len(equations),duplicate_equations=len(rows)-len(equations),rank=rank,columns=projection['U'],nullity=projection['U']-rank)


def check(cell,h,arm,result):
    fixture=cell['fixture'];r=fixture['r'];verify_fixture(fixture)
    expected=dict(schema='prym-shifted-subset/v1',cell_id=cell['id'],arm=arm,curve_uid=fixture['uid'],
                  cover_shift=h,active_atoms=cell['active_atoms'],source_order=cell['source_order'],complete=True)
    if any(result.get(k)!=v for k,v in expected.items()):raise ValueError('wrong complete shifted result identity')
    projection=public_projection(fixture,cell['source_order'])
    if result['projection']!=projection:raise ValueError('original projection changed')
    for row in cell['preprocessing_rows']:verify_old_row(fixture,row)
    reference=Reference(fixture,h,cell['active_atoms']);seen=set();counts=Counter();digest=sha256();rows=[];blocks=[];attempts=0;progress=[]
    for scalar in cell['source_order']:
        statuses=[];source_digest=sha256()
        for triple in combinations(cell['active_atoms'],3):
            for options in product(range(4),repeat=3):
                attempts+=1;code,identity,row=reference.outcome(scalar,triple,options,seen);status=LEGEND[code]
                counts[status]+=1;statuses.append(code)
                encoded=json.dumps([scalar,list(triple),list(options),identity,status],separators=(',',':')).encode()+b'\n'
                digest.update(encoded);source_digest.update(encoded)
                if row is not None:
                    verify_row(fixture,h,cell['active_atoms'],row);rows.append(row)
                    progress.append(dict(attempt=attempts,row_index=len(rows)-1,new_rank=quality(rows,projection,r)['rank'],
                                         combined_rank=quality(cell['preprocessing_rows']+rows,projection,r)['rank']))
        blocks.append(dict(scalar=scalar,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest()))
    if result['rows']!=rows or result['attempts']!=attempts or result['statuses']!=dict(counts) or result['branch_sha256']!=digest.hexdigest() or result['status_blocks']!=blocks or result['status_legend']!=LEGEND or result['rank_progress']!=progress:
        raise ValueError('full shifted branch/row/status/rank replay differs')
    for name,values in [('preprocessing_quality',cell['preprocessing_rows']),('new_quality',rows),('combined_quality',cell['preprocessing_rows']+rows)]:
        if result[name]!=quality(values,projection,r):raise ValueError('shifted quality differs')
    for key,values,q in [('old_kernel',cell['preprocessing_rows'],result['preprocessing_quality']),('kernel',cell['preprocessing_rows']+rows,result['combined_quality'])]:
        kernel=result[key];M=[project(row,projection,r)[0] for row in values]
        if len(kernel)!=q['nullity'] or any(len(v)!=projection['U'] for v in kernel) or dense_rank(kernel,r)!=q['nullity'] or any(sum(a*b for a,b in zip(v,k))%r for v in M for k in kernel):
            raise ValueError('incomplete/false shifted right kernel')
    syndromes=[[sum(a*b for a,b in zip(project(row,projection,r)[0],k))%r for k in result['old_kernel']] for row in rows]
    if result['old_kernel_syndromes']!=syndromes:raise ValueError('old-kernel action differs')
    return dict(checked=True,attempts_replayed=attempts,rows_verified=len(rows),new_rank=result['new_quality']['rank'],
                combined_rank=result['combined_quality']['rank'],preprocessing_rank=result['preprocessing_quality']['rank'],
                old_kernel_syndromes_checked=True,scope='Complete separate arithmetic replay; counters not audited; not independent scientific review.')
