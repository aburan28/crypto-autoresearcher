"""Independent fixed-pool relation truth; no producer arithmetic imports."""
from independent import convolution,evaluate,multiply,vandermonde,verify_row


class Census:
    def __init__(self,fixture):
        self.fixture=fixture;self.p=fixture['p'];self.sources={}
        self.roots={}
        for x in range(self.p):self.roots.setdefault(x*x%self.p,x)

    def descriptor(self,scalar,triple,options):
        f=self.fixture;p=self.p
        if scalar not in self.sources:
            point=multiply(p,0,f['a'],scalar,tuple(f['P']))
            self.sources[scalar]=None if point is None or not point[0] or point[0] not in self.roots else (self.roots[point[0]],-point[1]%p)
        source=self.sources[scalar]
        if source is None:return None
        points=[source]
        for j,option in zip(triple,options):
            x,y=f['factor_base'][j]['lift']
            points.append(((-x if option&2 else x)%p,(-y if option&1 else y)%p))
        return None if any(x==0 for x,y in points) or len({x for x,y in points})!=4 else points

    def accepted(self,scalar,triple,options):
        f=self.fixture;p=self.p;points=self.descriptor(scalar,triple,options)
        if points is None:return None
        v=vandermonde(p,points);leading=v[3] if len(v)==4 else 0
        if leading*leading%p==1:return None
        vv=convolution(p,v,v);F=[f['b'],0,f['a'],0,0,0,1]
        remainder=[((vv[j] if j<len(vv) else 0)-F[j])%p for j in range(7)]
        divisor=[1]
        for x,y in points:divisor=convolution(p,divisor,[-x%p,1])
        quotient=[0,0,0]
        for j in [2,1,0]:
            quotient[j]=remainder[j+4]
            for i,c in enumerate(divisor):remainder[j+i]=(remainder[j+i]-quotient[j]*c)%p
        if any(remainder):raise ArithmeticError('independent interpolation factor failed')
        c,b,a=quotient;discriminant=(b*b-4*a*c)%p
        if not a or not discriminant or discriminant not in self.roots:return None
        root=self.roots[discriminant];inverse=pow(2*a,-1,p)
        roots=sorted({(-b-root)*inverse%p,(-b+root)*inverse%p})
        if len(roots)!=2 or len(set(roots+[x for x,y in points]))!=6:return None
        coefficients=[0]*len(f['factor_base']);labels=[]
        for j,option in zip(triple,options):
            sign=-1 if option&1 else 1;coefficients[j]+=sign;labels.append([j,sign,option])
        for x in roots:
            y=evaluate(p,v,x)
            found=[(j,sign) for j,atom in enumerate(f['factor_base']) for sign in (1,-1)
                   if atom['point'][0]==x*x%p and sign*atom['point'][1]%p==y]
            if len(found)!=1:return None
            j,sign=found[0];coefficients[j]+=sign
        row={'schema':'prym-principal-row/v1','curve_uid':f['uid'],'source_scalar':scalar,
             'coefficients':[c%f['r'] for c in coefficients],'constraints':[list(t) for t in points],
             'base_labels':labels,'v_coefficients':v,'residual_coefficients':quotient,
             'residual_roots':roots,'pole_orders_at_infinity':[3,3],
             'source_locator':'explicit interpolation and residual quadratic; no post-hoc kernel'}
        verify_row(f,row)
        return row
