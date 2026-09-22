"""Public-synthetic GF(2^19), Koblitz group, normal basis, and fresh base."""
from __future__ import annotations
from typing import Iterable

N=19
MASK=(1<<N)-1
MODULUS=(1<<N)|39
R=262543
GENERATOR=(743,138613)
Point=tuple[int,int]|None

def mul(a:int,b:int)->int:
    if not (0<=a<=MASK and 0<=b<=MASK):raise ValueError("field operand outside GF(2^19)")
    out=0
    while b:
        if b&1:out^=a
        b>>=1;a<<=1
        if a&(1<<N):a^=MODULUS
    return out
def sq(a:int)->int:return mul(a,a)
def powf(a:int,n:int)->int:
    result=1
    while n:
        if n&1:result=mul(result,a)
        a=sq(a);n>>=1
    return result
def inv(a:int)->int:
    if a==0:raise ZeroDivisionError("zero field inverse")
    return powf(a,(1<<N)-2)
def on_curve(p:Point)->bool:
    if p is None:return True
    x,y=p
    return 0<=x<=MASK and 0<=y<=MASK and (sq(y)^mul(x,y))==(mul(sq(x),x)^sq(x)^1)
def neg(p:Point)->Point:return None if p is None else (p[0],p[1]^p[0])
def add(p:Point,q:Point)->Point:
    if p is None:return q
    if q is None:return p
    x,y=p;u,v=q
    if x==u:
        if y^v==x:return None
        if p!=q or x==0:raise ValueError("invalid equal-x group inputs")
        lam=x^mul(y,inv(x));z=sq(lam)^lam^1
        return z,sq(x)^mul(lam^1,z)
    lam=mul(y^v,inv(x^u));z=sq(lam)^lam^x^u^1
    return z,mul(lam,x^z)^z^y
def scalar(p:Point,n:int)->Point:
    if n<0:return scalar(neg(p),-n)
    total=None
    while n:
        if n&1:total=add(total,p)
        p=add(p,p);n>>=1
    return total
def frob(p:Point)->Point:return None if p is None else (sq(p[0]),sq(p[1]))
def binary_rank(values:Iterable[int])->int:
    pivots={}
    for value in values:
        while value:
            bit=value.bit_length()-1
            if bit not in pivots:pivots[bit]=value;break
            value^=pivots[bit]
    return len(pivots)
def normal_basis()->tuple[int,tuple[int,...]]:
    for beta in range(1,MASK+1):
        value=beta;columns=[]
        for _ in range(N):columns.append(value);value=sq(value)
        if binary_rank(columns)==N:return beta,tuple(columns)
    raise RuntimeError("no normal basis")
def normal_to_poly(mask:int,columns:tuple[int,...])->int:
    out=0
    for bit,column in enumerate(columns):
        if mask>>bit&1:out^=column
    return out
def poly_to_normal(value:int,columns:tuple[int,...])->int:
    pivots={}
    for index,column in enumerate(columns):
        row=column;mask=1<<index
        while row:
            bit=row.bit_length()-1
            if bit not in pivots:pivots[bit]=(row,mask);break
            previous,previous_mask=pivots[bit];row^=previous;mask^=previous_mask
        else:raise ValueError("normal basis not independent")
    out=0
    while value:
        bit=value.bit_length()-1
        if bit not in pivots:raise ValueError("normal conversion impossible")
        row,mask=pivots[bit];value^=row;out^=mask
    return out
def x_orbit(x:int)->tuple[int,...]:
    out=[]
    for _ in range(N):out.append(x);x=sq(x)
    return tuple(out)
def point_key(p:Point)->tuple[int,int]:return (-1,-1) if p is None else p

def construct_base(recipe:dict,normal:bool=True)->dict:
    if recipe.get("n")!=19 or recipe.get("modulus")!=MODULUS or recipe.get("r")!=R:
        raise ValueError("frozen curve parameters differ")
    seeds=recipe["seed_points"]
    if len(seeds)!=4 or recipe["plane_key"]!=sorted(recipe["plane_key"]):
        raise ValueError("four sorted plane seeds required")
    a,b,c=recipe["affine_coordinates"]
    expected=sorted((a,a^b,a^c,a^b^c))
    if expected!=recipe["plane_key"] or a==0 or b==0 or c==0 or b==c:
        raise ValueError("affine plane certificate mismatch")
    if sorted(row["point"][0] for row in seeds)!=expected:
        raise ValueError("seed x values differ from selected plane")
    points=[];orbit_x=[];orbit_ids=[];seen=set()
    for row in seeds:
        p=tuple(row["point"])
        if p[0]==0 or not on_curve(p) or scalar(p,R) is not None:
            raise ValueError("seed not nonzero rational prime-subgroup point")
        orbit_ids.append(row["pool_orbit_index"])
        members=[];xs=[];one=set();start=p
        for _ in range(N):
            # Frobenius preserves the subgroup already checked at the seed.
            if not on_curve(p):raise ValueError("generated conjugate fails curve membership")
            opposite=neg(p)
            for q in (p,opposite):
                if q in one or q in seen:raise ValueError("signed Frobenius orbit collision")
                one.add(q);seen.add(q);members.append(q)
            xs.append(p[0]);p=frob(p)
        if p!=start or len(one)!=38 or len(set(xs))!=19:
            raise ValueError("seed orbit is not full length 38")
        points.extend(members);orbit_x.append(xs)
    if len(set(orbit_ids))!=4 or len(seen)!=152 or len({p[0] for p in points})!=76:
        raise ValueError("base does not have four disjoint full signed orbits")
    ordered=tuple(sorted(points,key=point_key))
    xvalues=tuple(sorted({p[0] for p in ordered}))
    if recipe["expected_x_values"]!=76 or recipe["expected_signed_points"]!=152:
        raise ValueError("frozen base cardinalities differ")
    result={"points":ordered,"x_values":xvalues,"orbit_x":tuple(tuple(v) for v in orbit_x),
            "orbit_ids":tuple(orbit_ids),"plane_key":tuple(expected)}
    if normal:
        beta,columns=normal_basis()
        if binary_rank(columns)!=19:raise ValueError("normal basis rank")
        for value in (0,1,*expected):
            if normal_to_poly(poly_to_normal(value,columns),columns)!=value:
                raise ValueError("normal basis conversion mismatch")
        result.update(normal_beta=beta,normal_columns=columns,
                      plane_normal=tuple(poly_to_normal(v,columns) for v in (a,b,c)))
    return result

def construct_control_base(recipe:dict)->dict:
    if recipe.get("n")!=19 or recipe.get("modulus")!=MODULUS or recipe.get("r")!=R:
        raise ValueError("control curve parameters differ")
    generator=tuple(recipe["generator"])
    if generator[0]==0 or not on_curve(generator) or scalar(generator,R) is not None:
        raise ValueError("control generator invalid")
    opposite=neg(generator)
    points=tuple(sorted((generator,opposite)))
    if len(set(points))!=2 or points[0][0]!=points[1][0]:
        raise ValueError("small control base must be exactly {G,-G}")
    return {"points":points,"x_values":(generator[0],),"kind":"control_small"}

def in_selected_base(p:Point,recipe:dict)->bool:
    if p is None:return False
    for seed in recipe["seed_points"]:
        current=tuple(seed["point"])
        for _ in range(N):
            if p==current or p==neg(current):return True
            current=frob(current)
    return False

def batch_add_fixed(p:Point,others:list[Point])->list[Point]:
    output=[None]*len(others);indices=[];denominators=[];prefixes=[];product=1
    for index,q in enumerate(others):
        if p is None:output[index]=q
        elif q is None:output[index]=p
        elif p[0]==q[0]:output[index]=add(p,q)
        else:
            d=p[0]^q[0];indices.append(index);denominators.append(d)
            prefixes.append(product);product=mul(product,d)
    if indices:
        backwards=inv(product)
        for j in range(len(indices)-1,-1,-1):
            index=indices[j];q=others[index]
            assert p is not None and q is not None
            d_inv=mul(backwards,prefixes[j]);backwards=mul(backwards,denominators[j])
            lam=mul(p[1]^q[1],d_inv);x=sq(lam)^lam^p[0]^q[0]^1
            output[index]=(x,mul(lam,p[0]^x)^x^p[1])
    return output
def direct_mitm(q:Point,points:tuple[Point,...])->tuple[Point,Point,Point]|None:
    table={}
    for i,p in enumerate(points):
        for j,total in enumerate(batch_add_fixed(p,list(points[i:])),i):
            table.setdefault(total,(i,j))
    for i,rest in enumerate(batch_add_fixed(q,[neg(p) for p in points])):
        if rest not in table:continue
        a,b=table[rest];w=(points[a],points[b],points[i])
        if add(add(w[0],w[1]),w[2])==q:return w
        raise ValueError("direct MITM table witness failed group replay")
    return None
