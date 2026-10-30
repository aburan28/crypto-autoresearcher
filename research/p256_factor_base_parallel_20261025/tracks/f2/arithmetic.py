"""Exact affine arithmetic. None encodes O. Integers encode F_p canonically."""
from hashlib import sha256

P = 2**256 - 2**224 + 2**192 + 2**96 - 1
TARGET_B = int('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b',16)
TARGET_R = int('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551',16)
AUX = (0, 1, 0) # y^2=x^3+A*x^2+B*x+C
TARGET = (0, -3 % P, TARGET_B)

def rhs(x, curve):
    a,b,c=curve
    return ((x+a)*x*x+b*x+c)%P

def on_curve(point, curve):
    return point is None or (point[1]*point[1]-rhs(point[0],curve))%P==0

def neg(point):
    return None if point is None else (point[0], -point[1]%P)

def add(left, right, curve):
    if left is None: return right
    if right is None: return left
    x,y=left; z,w=right; a,b,_=curve
    if x==z:
        if (y+w)%P==0: return None
        slope=(3*x*x+2*a*x+b)*pow(2*y,-1,P)%P
    else:
        slope=(w-y)*pow(z-x,-1,P)%P
    xx=(slope*slope-a-x-z)%P
    return xx,(slope*(x-xx)-y)%P

def mul(n, point, curve):
    if n<0: return mul(-n,neg(point),curve)
    acc=None
    while n:
        if n&1: acc=add(acc,point,curve)
        point=add(point,point,curve); n>>=1
    return acc

def root(value):
    value%=P
    result=pow(value,(P+1)//4,P)
    if result*result%P != value: return None
    return min(result,-result%P)

def point_from_seed(seed, curve, cap=10000):
    for counter in range(cap):
        x=int.from_bytes(sha256((seed+':'+str(counter)).encode()).digest(),'big')%P
        y=root(rhs(x,curve))
        if y is not None: return (x,y),counter+1
    raise RuntimeError('bounded point search exhausted')

def exact_two_power(point, exponent, curve):
    return (point is not None and mul(1<<exponent,point,curve) is None
            and (exponent==0 or mul(1<<(exponent-1),point,curve) is not None))

def make_edge(curve, kernel):
    a0,b0,c0=curve; r,y=kernel
    assert y==0 and on_curve(kernel,curve)
    a=(3*r+a0)%P
    b=(3*r*r+2*a0*r+b0)%P
    assert b and (a*a-4*b)%P
    destination=(-2*a%P,(a*a-4*b)%P,0)
    return dict(source=list(curve), destination=list(destination), r=r,a=a,b=b,
                degree=2, separable=True, field='Fp', direction='unresolved')

def map_point(point, edge):
    if point is None: return None
    x,y=point; u=(x-edge['r'])%P
    if not u: return None
    inverse=pow(u,-1,P); b=edge['b']; a=edge['a']
    return ((u+a+b*inverse)%P,y*(1-b*inverse*inverse)%P)

def map_x(x, edge):
    if x is None: return None
    u=(x-edge['r'])%P
    return None if not u else (u+edge['a']+edge['b']*pow(u,-1,P))%P

def map_chain(point, edges):
    for edge in edges: point=map_point(point,edge)
    return point

def dual(point, edge):
    # Standard second quotient followed by (X,Y)->(X/4,Y/8), then x=u+r.
    if point is None: return None
    x,y=point
    if not x: return None
    a,b=edge['a'],edge['b']; aa=-2*a%P; bb=(a*a-4*b)%P
    inv=pow(x,-1,P)
    u=(x+aa+bb*inv)*pow(4,-1,P)%P
    yy=y*(1-bb*inv*inv)*pow(8,-1,P)%P
    return (u+edge['r'])%P,yy

def inverse_fibre(terminal, edges):
    values={terminal}
    levels=[]
    inv2=pow(2,-1,P)
    for edge in reversed(edges):
        prev=set()
        for value in values:
            v=(value-edge['a'])%P
            sq=root(v*v-4*edge['b'])
            if sq is not None:
                for s in {sq,-sq%P}:
                    prev.add(((v+s)*inv2+edge['r'])%P)
        values=prev; levels.append(len(values))
    return values,levels
