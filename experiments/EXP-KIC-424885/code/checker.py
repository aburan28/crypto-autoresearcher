"""Independent finite oracle, model replay and group checks for GFB-SAT-N7."""
from __future__ import annotations
import itertools,json
from typing import Any
import field,circuits

# This oracle uses its own bitwise field arithmetic and point formulas. It
# shares only public curve parameters and point encoding with the producer.
def _mul(a:int,b:int)->int:
    p=0
    for bit in range(7):
        if b>>bit&1:p^=a<<bit
    for degree in range(12,6,-1):
        if p>>degree&1:p^=0x83<<(degree-7)
    return p
def _sq(a:int)->int:return _mul(a,a)
def _inv(a:int)->int:
    if a==0:raise ZeroDivisionError
    result=1;power=a;exponent=126
    while exponent:
        if exponent&1:result=_mul(result,power)
        power=_sq(power);exponent>>=1
    return result
def _neg(p:field.Point)->field.Point:
    return None if p is None else (p[0],p[1]^p[0])
def _on_curve(p:field.Point)->bool:
    return p is None or (_sq(p[1])^_mul(p[0],p[1]))==(_mul(_sq(p[0]),p[0])^_sq(p[0])^1)
def _lifts(x:int)->tuple[field.Point,...]:
    return tuple((x,y) for y in range(128) if _on_curve((x,y)))
def _add(p:field.Point,q:field.Point)->field.Point:
    if p is None:return q
    if q is None:return p
    x1,y1=p;x2,y2=q
    if x1==x2:
        if y1^y2==x1:return None
        if p!=q:raise ValueError("invalid same-x points")
        if x1==0:return None
        slope=x1^_mul(y1,_inv(x1));x3=_sq(slope)^slope^1
        return x3,_sq(x1)^_mul(slope^1,x3)
    slope=_mul(y1^y2,_inv(x1^x2));x3=_sq(slope)^slope^x1^x2^1
    return x3,_mul(slope,x1^x3)^x3^y1
def _scalar_mul(p:field.Point,n:int)->field.Point:
    out=None
    while n:
        if n&1:out=_add(out,p)
        p=_add(p,p);n>>=1
    return out

def base_points(base:dict)->tuple[field.Point,...]:
    return tuple(tuple(p) for p in base["points"])
def oracle_witness(q:field.Point,base:dict,ordered_x:bool=True)->tuple[field.Point,field.Point,field.Point]|None:
    points=base_points(base)
    for p1,p2,p3 in itertools.product(points,repeat=3):
        if ordered_x and not (p1[0]<=p2[0]<=p3[0]):continue
        if _add(_add(p1,p2),p3)==q:return p1,p2,p3
    return None
def oracle_status(q:field.Point,base:dict)->str:
    return "SAT" if oracle_witness(q,base) is not None else "UNSAT"
def prefix_extendible(q:field.Point,base:dict,x1:int,x2:int|None=None)->bool:
    points=base_points(base)
    for p1,p2,p3 in itertools.product(points,repeat=3):
        if not(p1[0]<=p2[0]<=p3[0]):continue
        if p1[0]!=x1 or (x2 is not None and p2[0]!=x2):continue
        if _add(_add(p1,p2),p3)==q:return True
    return False
def check_witness(q:field.Point,base:dict,witness:list[list[int]]|None)->bool:
    if witness is None:return False
    if len(witness)!=3:return False
    pts=tuple(tuple(p) for p in witness)
    allowed=set(base_points(base))
    return all(p in allowed and _on_curve(p) and _scalar_mul(p,71) is None for p in pts) and _add(_add(pts[0],pts[1]),pts[2])==q
def assignment_from_cms(stdout:str,nvars:int)->dict[int,bool]:
    values={}
    for line in stdout.splitlines():
        if line.startswith("v "):
            for token in line.split()[1:]:
                lit=int(token)
                if lit:
                    var=abs(lit)
                    if not 1<=var<=nvars:raise ValueError(f"CMS model variable out of range: {var}")
                    if var in values and values[var]!=(lit>0):raise ValueError(f"CMS model contradicts variable {var}")
                    values[var]=lit>0
    if set(values)!=set(range(1,nvars+1)):raise ValueError(f"CMS model incomplete: {len(values)} of {nvars}")
    return values
def decode_model(c:circuits.Circuit,assignment:dict[int,bool],q:field.Point,base:dict)->tuple[field.Point,field.Point,field.Point]:
    if not circuits.evaluate(c,assignment):raise ValueError("CMS assignment fails original CNF/XOR")
    xs=[]
    for name in ("x1","x2","x3"):
        xs.append(sum(1<<i for i,v in enumerate(c.inputs[name]) if assignment[v]))
    if not(xs[0]<=xs[1]<=xs[2]) or any(x not in base["x_values"] for x in xs):
        raise ValueError("CMS model violates ordered factor-base domain")
    allowed=set(base_points(base))
    for lifts in itertools.product(*(_lifts(x) for x in xs)):
        if all(p in allowed and _on_curve(p) for p in lifts) and _add(_add(lifts[0],lifts[1]),lifts[2])==q:
            return lifts
    raise ValueError("complete SAT model has no exact group witness")
def replay_result(result:dict[str,Any],q:field.Point,base:dict)->dict[str,Any]:
    status=result.get("status");truth=oracle_status(q,base)
    if status=="SAT":
        if not check_witness(q,base,result.get("witness")):raise ValueError("invalid three-point witness")
    elif status=="UNSAT":
        if truth!="UNSAT":raise ValueError("false UNSAT")
    else:raise ValueError(f"nonterminal or invalid worker status {status!r}")
    if status!=truth:raise ValueError("worker differs from independent exact oracle")
    return {"valid":True,"worker_status":status,"oracle_status":truth,"witness":result.get("witness")}
