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
    if len(v)!=4 or (v[3]*v[3]-1)%p==0:raise ValueError('exceptional pole order')
    roots=row['residual_roots']
    if len(roots)!=2 or len(set(roots+[x for x,y in points]))!=6:
        raise ValueError('repeated/missing intersection roots')
    residual=row['residual_coefficients']
    if len(residual)!=3 or not residual[-1]:raise ValueError('invalid residual degree')
    expected=[1]
    for x,y in points:expected=convolution(p,expected,[-x%p,1])
    intersection=convolution(p,v,v)
    F=[b,0,a,0,0,0,1]
    intersection=[(x-y)%p for x,y in zip(intersection,F)]
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
