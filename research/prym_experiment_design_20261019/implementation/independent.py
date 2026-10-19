"""Independent public row verifier: no imports from producer arithmetic."""
from math import isqrt


def prime(n):
    return n>=2 and all(n%d for d in range(2,isqrt(n)+1))


def add(p,a2,a4,left,right):
    if left is None:return right
    if right is None:return left
    x,y=left;u,v=right
    if x==u:
        if (y+v)%p==0:return None
        slope=(3*x*x+2*a2*x+a4)*pow(2*y,-1,p)%p
    else:slope=(v-y)*pow(u-x,-1,p)%p
    xx=(slope*slope-a2-x-u)%p
    return xx,(slope*(x-xx)-y)%p


def multiply(p,a2,a4,n,point):
    # Left-to-right binary evaluation, unlike the producer's right-to-left.
    if n<0:return multiply(p,a2,a4,-n,None if point is None else (point[0],-point[1]%p))
    out=None
    for bit in bin(n)[2:]:
        out=add(p,a2,a4,out,out)
        if bit=='1':out=add(p,a2,a4,out,point)
    return out


def convolution(p,a,b):
    result=[sum(a[j]*b[i-j] for j in range(len(a)) if 0<=i-j<len(b))%p
            for i in range(len(a)+len(b)-1)]
    while len(result)>1 and result[-1]==0:result.pop()
    return result


def evaluate(p,coefficients,x):
    return sum(c*pow(x,j,p) for j,c in enumerate(coefficients))%p


def vandermonde(p,points):
    matrix=[[pow(x,j,p) for j in range(4)]+[y] for x,y in points]
    for j in range(4):
        pivot=next(k for k in range(j,4) if matrix[k][j])
        matrix[j],matrix[pivot]=matrix[pivot],matrix[j]
        inverse=pow(matrix[j][j],-1,p)
        matrix[j]=[v*inverse%p for v in matrix[j]]
        for k in range(4):
            if k!=j:
                scale=matrix[k][j]
                matrix[k]=[(x-scale*y)%p for x,y in zip(matrix[k],matrix[j])]
    result=[matrix[j][4] for j in range(4)]
    while len(result)>1 and result[-1]==0:result.pop()
    return result


def verify_fixture(fixture,recount=True):
    p,a,b,r=(fixture[k] for k in ['p','a','b','r'])
    if not prime(p) or not prime(r) or r<=2 or not b%p or (4*a*a*a+27*b*b)%p==0:
        raise ValueError('invalid field/order/smoothness')
    if recount:
        symbols=[pow((x*x*x+a*x+b)%p,(p-1)//2,p) for x in range(p)]
        order=p+1+sum(-1 if s==p-1 else s for s in symbols)
        if order!=r:raise ValueError('independent curve order mismatch')
    P=tuple(fixture['P'])
    if (P[1]**2-P[0]**3-a*P[0]-b)%p or multiply(p,0,a,r,P) is not None:
        raise ValueError('invalid source generator')
    norms=set()
    for atom in fixture['factor_base']:
        x,y=atom['lift'];u,v=atom['point']
        if (x*x-u)%p or y!=v or (y*y-x**6-a*x*x-b)%p:
            raise ValueError('invalid atom lift/norm')
        key=(u,min(v,-v%p))
        if key in norms:raise ValueError('duplicate/sign-equivalent norm column')
        norms.add(key)
    return {'order_recounted':recount,'unknown_columns':len(norms),'generator_order':r}


def verify_row(fixture,row,target=None):
    p,a,b,r=(fixture[k] for k in ['p','a','b','r'])
    if row.get('schema')!='prym-principal-row/v1' or row['curve_uid']!=fixture['uid']:
        raise ValueError('wrong row/curve identity')
    if row.get('source_locator')!='explicit interpolation and residual quadratic; no post-hoc kernel':
        raise ValueError('missing explicit source locator')
    if row['pole_orders_at_infinity']!=[3,3]:raise ValueError('wrong infinity divisor')
    points=[tuple(t) for t in row['constraints']]
    if len(points)!=4 or len({x for x,y in points})!=4:raise ValueError('bad interpolation constraints')
    scalar=row['source_scalar']
    target_coefficient=row.get('target_coefficient',0)
    if not isinstance(scalar,int) or not 0<=scalar<r:raise ValueError('bad public source scalar')
    if target_coefficient and target is None:raise ValueError('missing public target')
    source=multiply(p,0,a,scalar,tuple(fixture['P']))
    if target_coefficient:source=add(p,0,a,source,multiply(p,0,a,target_coefficient,target))
    source=None if source is None else (source[0],-source[1]%p)
    if source is None or (points[0][0]**2%p,points[0][1])!=source:
        raise ValueError('false public source label')
    v=vandermonde(p,points)
    if v!=row['v_coefficients']:raise ValueError('independent interpolation mismatch')
    leading=v[3] if len(v)==4 else 0
    if len(v)>4 or (leading*leading-1)%p==0:raise ValueError('exceptional pole order')
    roots=row['residual_roots']
    if len(roots)!=2 or len(set(roots+[x for x,y in points]))!=6:
        raise ValueError('repeated/missing intersection roots')
    residual=row['residual_coefficients']
    if len(residual)!=3 or not residual[-1]:raise ValueError('invalid residual degree')
    expected=[1]
    for x,y in points:expected=convolution(p,expected,[-x%p,1])
    intersection=convolution(p,v,v)
    F=[b,0,a,0,0,0,1]
    intersection=[((intersection[j] if j<len(intersection) else 0)-F[j])%p for j in range(7)]
    if convolution(p,expected,residual)!=intersection:raise ValueError('principal-function certificate mismatch')
    all_points=points+[(x,evaluate(p,v,x)) for x in roots]
    for x,y in all_points:
        if (y*y-x**6-a*x*x-b)%p:raise ValueError('intersection point off C')
    coefficients=[0]*len(fixture['factor_base'])
    if len(row['base_labels'])!=3:raise ValueError('invalid label arity')
    for point,label in zip(points[1:],row['base_labels']):
        j,sign,option=label
        if not 0<=j<len(coefficients) or sign not in [-1,1] or option not in range(4):
            raise ValueError('invalid atom label')
        xx,yy=fixture['factor_base'][j]['lift']
        if point!=( (-xx if option&2 else xx)%p,sign*yy%p) or sign!=(-1 if option&1 else 1):
            raise ValueError('false atom label')
        coefficients[j]+=sign
    for x,y in all_points[4:]:
        options=[(j,sign) for j,atom in enumerate(fixture['factor_base']) for sign in [1,-1]
                 if atom['point'][0]==x*x%p and sign*atom['point'][1]%p==y]
        if len(options)!=1:raise ValueError('residual is outside distinct factor base')
        j,sign=options[0];coefficients[j]+=sign
    if [x%r for x in coefficients]!=row['coefficients']:raise ValueError('row coefficients differ from witness')
    total=None
    for coefficient,atom in zip(coefficients,fixture['factor_base']):
        total=add(p,0,a,total,multiply(p,0,a,coefficient,tuple(atom['point'])))
    expected_source=None if source is None else (source[0],-source[1]%p)
    if total!=expected_source:raise ValueError('public source equation fails')
    # Independent auxiliary sum; x=0 maps to infinity, infinity maps to (0,+/-B).
    auxiliary=None
    for x,y in all_points:
        if x:
            inverse=pow(x,-1,p)
            point=(b*inverse*inverse%p,b*y*inverse**3%p)
            if (point[1]**2-point[0]**3-a*point[0]**2-b*b)%p:
                raise ValueError('auxiliary map equation fails')
            auxiliary=add(p,a,0,auxiliary,point)
    if auxiliary is not None:raise ValueError('auxiliary norm does not cancel')
    return True


def dense_rank(rows,modulus):
    """Independent column-major full elimination; no producer Rank imports."""
    matrix=[[x%modulus for x in row] for row in rows]
    if not matrix:return 0
    position=0
    for column in range(len(matrix[0])):
        pivot=next((j for j in range(position,len(matrix)) if matrix[j][column]),None)
        if pivot is None:continue
        matrix[position],matrix[pivot]=matrix[pivot],matrix[position]
        inverse=pow(matrix[position][column],-1,modulus)
        matrix[position]=[x*inverse%modulus for x in matrix[position]]
        for j in range(len(matrix)):
            if j==position:continue
            scale=matrix[j][column]
            matrix[j]=[(x-scale*y)%modulus for x,y in zip(matrix[j],matrix[position])]
        position+=1
        if position==len(matrix):break
    return position


def canonical_columns(p,points,known):
    mapping=[];unknown=[];index={}
    for point in points:
        if point is None:mapping.append(None);continue
        x,y=point;key=(x,min(y,-y%p));sign=1 if tuple(point)==key else -1
        if key in known:mapping.append(['known',sign*known[key]]);continue
        if key not in index:index[key]=len(unknown);unknown.append(key)
        mapping.append([index[key],sign])
    return {'U':len(unknown),'points':unknown,'column_map':mapping}


def verify_rank(fixture,cell):
    r=fixture['r'];p=fixture['p'];a=fixture['a'];P=tuple(fixture['P'])
    public={}
    for record in cell['projection']['public_derivations']:
        j,value=record['column'],record['scalar']
        source=record['derived_from_public_source_scalar']
        if not 1<=source<=min(64,r-1) or value!=record['sign']*source%r:
            raise ValueError('undeclared public-anchor derivation')
        if multiply(p,0,a,value,P)!=tuple(fixture['factor_base'][j]['point']):
            raise ValueError('false public anchor')
        public[j]=value
    unknown=[j for j in range(len(fixture['factor_base'])) if j not in public]
    M=[];aug=[]
    for row in cell['rows']:
        verify_row(fixture,row)
        coefficients=[row['coefficients'][j] for j in unknown]
        b=(row['source_scalar']-sum(row['coefficients'][j]*value for j,value in public.items()))%r
        M.append(coefficients);aug.append(coefficients+[b])
    rank=dense_rank(M,r);aug_rank=dense_rank(aug,r)
    declared=cell['projection']
    if (len(unknown),rank,aug_rank)!=(declared['U'],declared['rank'],declared['augmented_rank']):
        raise ValueError('independent rank mismatch')
    indices=declared['independent_row_indices']
    if len(indices)!=rank or dense_rank([M[i] for i in indices],r)!=rank:
        raise ValueError('invalid pivot-row certificate')
    solution=declared['solution']
    if solution is not None:
        if rank!=len(unknown) or len(solution)!=len(unknown):raise ValueError('invalid solution shape')
        for j,value in zip(unknown,solution):
            if multiply(p,0,a,value,P)!=tuple(fixture['factor_base'][j]['point']):
                raise ValueError('recovered base logarithm fails public verification')
    return {'U':len(unknown),'rank':rank,'augmented_rank':aug_rank,'rows_verified':len(M)}
