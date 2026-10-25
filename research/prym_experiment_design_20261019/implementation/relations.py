"""Explicit principal-divisor witnesses on y²=x6+A*x²+B; synthetic use only."""
from hashlib import sha256
from itertools import combinations, product
import json

from arithmetic import (Elliptic, Field, interpolate, padd, pdiv, peval, pmul,
                        quadratic_roots)


def uid(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


class Context:
    def __init__(self,fixture):
        self.fixture = fixture
        self.p,self.a,self.b = (fixture[k] for k in ('p','a','b'))
        self.r = fixture['r']
        self.f = Field(self.p)
        self.e = Elliptic(self.f,0,self.a,self.b)
        self.aux = Elliptic(self.f,self.a,0,self.b*self.b % self.p)
        self.P = tuple(fixture['P'])
        self.base = [tuple(v['point']) for v in fixture['factor_base']]
        self.lifts = [tuple(v['lift']) for v in fixture['factor_base']]
        self.by_x = {point[0]:j for j,point in enumerate(self.base)}
        self.source_cache={}
        self.aux_cache={}

    def pi2(self,point):
        if point in self.aux_cache:
            self.f.counts['aux_cache_hits']+=1
            return self.aux_cache[point]
        self.f.counts['aux_cache_misses']+=1
        x,y = point
        if not x:
            return None  # both affine C points above x=0 map to infinity.
        inverse = self.f.inv(x)
        square = self.f.mul(inverse,inverse)
        result=(self.f.mul(self.b,square),
                self.f.mul(self.f.mul(self.b,y),self.f.mul(square,inverse)))
        self.aux_cache[point]=result
        return result

    def lift_source(self,scalar,source=None):
        source = self.P if source is None else source
        key=(scalar,source)
        if key in self.source_cache:
            self.f.counts['source_cache_hits']+=1
            return self.source_cache[key]
        self.f.counts['source_cache_misses']+=1
        point = self.e.neg(self.e.mul(scalar,source))
        if point is None:
            self.source_cache[key]=None
            return None
        x = self.f.sqrt(point[0])
        result=None if x is None or not x else (x,point[1])
        self.source_cache[key]=result
        return result

    def descriptor(self,scalar,triple,options,source=None):
        first = self.lift_source(scalar,source)
        if first is None:
            return None,'source_no_nonzero_rational_lift'
        points=[first]
        labels=[]
        for j,option in zip(triple,options):
            x,y=self.lifts[j]
            sign=-1 if option&1 else 1
            x=(-x)%self.p if option&2 else x
            points.append((x,sign*y%self.p))
            labels.append((j,sign,option))
        if any(x==0 for x,y in points):
            return None,'exceptional_interpolation_x_zero'
        if len({x for x,y in points})<4:
            return None,'duplicate_interpolation_x'
        return {'source_scalar':scalar,'points':points,'labels':labels},None

    def canonical_identity(self,descriptor):
        """Quotient source scaling, FB permutations, global deck and negation."""
        candidates=[]
        for deck in (1,-1):
            for neg in (1,-1):
                points=[(deck*x%self.p,neg*y%self.p) for x,y in descriptor['points']]
                signed=[]
                for (j,sign,option),point in zip(descriptor['labels'],points[1:]):
                    signed.append((j,neg*sign,point[0],point[1]))
                signed.sort()
                # The chosen source lift is bound explicitly in an ID. This
                # prevents opposite lift branches from being merged incorrectly.
                identity={'curve_uid':self.fixture['uid'],
                          'source_scalar':neg*descriptor['source_scalar']%self.r,
                          'lambda':1,
                          'signed_fb_lift_ids':{'source_lift':points[0], 'base_lifts':signed}}
                candidates.append(identity)
        return min(candidates,key=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')))

    def bucket(self,descriptor):
        total=None
        for point in descriptor['points']:
            total=self.aux.add(total,self.pi2(point))
        if total is None:
            return 'infinity'
        w,_=total
        self.f.counts['modular_pow']+=1
        symbol=pow(w,(self.p-1)//2,self.p)
        symbol=-1 if symbol==self.p-1 else symbol
        return f'{symbol:+d}:{16*w//self.p:02d}'

    def construct(self,descriptor):
        f=self.f
        points=descriptor['points']
        v=interpolate(f,points)
        F=[self.b,0,self.a,0,0,0,1]
        intersection=padd(f,pmul(f,v,v),F,sign=-1)
        if len(intersection)!=7:
            return None,'exceptional_pole_order'
        known=[1]
        for x,y in points:
            known=pmul(f,known,[-x%self.p,1])
        residual,remainder=pdiv(f,intersection,known)
        if remainder != [0]:
            raise ArithmeticError('interpolation did not divide intersection')
        roots=quadratic_roots(f,residual)
        if roots is None or len(roots)!=2:
            return None,'residual_not_two_distinct_rational_roots'
        if set(roots)&{x for x,y in points}:
            return None,'intersection_not_squarefree'
        extras=[(x,peval(f,v,x)) for x in roots]
        coefficients=[0]*len(self.base)
        for j,sign,option in descriptor['labels']:
            coefficients[j]+=sign
        for x,y in extras:
            u=f.mul(x,x)
            j=self.by_x.get(u)
            if j is None:
                return None,'residual_endpoint_outside_factor_base'
            if y==self.base[j][1]:
                coefficients[j]+=1
            elif y==(-self.base[j][1])%self.p:
                coefficients[j]-=1
            else:
                raise ArithmeticError('factor-base endpoint orientation mismatch')
        return {'schema':'prym-principal-row/v1','curve_uid':self.fixture['uid'],
                'source_scalar':descriptor['source_scalar'],
                'coefficients':[c%self.r for c in coefficients],
                'constraints':[list(p) for p in points],
                'base_labels':[list(t) for t in descriptor['labels']],
                'v_coefficients':v,'residual_coefficients':residual,
                'residual_roots':roots,
                'pole_orders_at_infinity':[3,3],
                'source_locator':'explicit interpolation and residual quadratic; no post-hoc kernel'},None


def descriptors(context,scalars=None):
    """Finite exact order; failures remain explicit attempted events."""
    scalars=range(1,context.r) if scalars is None else scalars
    for scalar in scalars:
        for triple in combinations(range(len(context.base)),3):
            for options in product(range(4),repeat=3):
                descriptor,reason=context.descriptor(scalar,triple,options)
                yield descriptor,reason


class Rank:
    """Incremental affine rank with an explicit consistency check modulo r."""
    def __init__(self,columns,modulus):
        self.columns,self.modulus=columns,modulus
        self.pivots={}
        self.ops=0

    def add(self,coefficients,rhs):
        r=self.modulus
        row=[x%r for x in coefficients]+[rhs%r]
        for pivot,old in sorted(self.pivots.items()):
            if row[pivot]:
                scale=row[pivot]
                row=[(a-scale*b)%r for a,b in zip(row,old)]
                self.ops+=len(row)
        pivot=next((j for j in range(self.columns) if row[j]),None)
        if pivot is None:
            if row[-1]:
                raise ArithmeticError('inconsistent affine source relation')
            return False
        inv=pow(row[pivot],-1,r)
        row=[x*inv%r for x in row]
        self.ops+=len(row)
        self.pivots[pivot]=row
        return True

    def solve(self):
        if len(self.pivots)!=self.columns:
            return None
        solution=[0]*self.columns
        for pivot,row in sorted(self.pivots.items(),reverse=True):
            solution[pivot]=(row[-1]-sum(a*b for a,b in zip(row[:-1],solution)))%self.modulus
        return solution
