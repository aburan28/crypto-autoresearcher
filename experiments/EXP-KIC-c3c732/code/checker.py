"""Independent N19 arithmetic and complete CNF/XOR/model/group replay."""
from __future__ import annotations
import itertools
import json
from typing import Any
import circuits

N=19
MASK=(1<<N)-1
POLY=(1<<N)|39
R=262543
Point=tuple[int,int]|None

def fmul(a:int,b:int)->int:
    product=0
    for bit in range(N):
        if b>>bit&1:product^=a<<bit
    for degree in range(2*N-2,N-1,-1):
        if product>>degree&1:product^=POLY<<(degree-N)
    return product
def fsq(a:int)->int:return fmul(a,a)
def finv(a:int)->int:
    if not a:raise ZeroDivisionError("zero inverse")
    u,v,g,h=a,POLY,1,0
    while u!=1:
        if not u:raise ValueError("noninvertible field value")
        shift=u.bit_length()-v.bit_length()
        if shift<0:u,v=v,u;g,h=h,g;shift=-shift
        u^=v<<shift;g^=h<<shift
    while g.bit_length()>N:g^=POLY<<(g.bit_length()-N-1)
    return g
def oncurve(p:Point)->bool:
    if p is None:return True
    x,y=p
    return 0<=x<=MASK and 0<=y<=MASK and (fsq(y)^fmul(x,y))==(fmul(fsq(x),x)^fsq(x)^1)
def negative(p:Point)->Point:return None if p is None else (p[0],p[1]^p[0])
def plus(p:Point,q:Point)->Point:
    if p is None:return q
    if q is None:return p
    x,y=p;u,v=q
    if x==u:
        if y^v==x:return None
        if p!=q or x==0:raise ValueError("independent equal-x input invalid")
        slope=x^fmul(y,finv(x));z=fsq(slope)^slope^1
        return z,fsq(x)^fmul(slope^1,z)
    slope=fmul(y^v,finv(x^u));z=fsq(slope)^slope^x^u^1
    return z,fmul(slope,x^z)^z^y
def times(p:Point,n:int)->Point:
    out=None
    while n:
        if n&1:out=plus(out,p)
        p=plus(p,p);n>>=1
    return out
def require(value:bool,reason:str)->None:
    if not value:raise ValueError(reason)
def base_points(base:dict)->tuple[Point,...]:
    return tuple(tuple(p) for p in base["points"])
def verify_witness(q:Point,base:dict,witness:list[list[int]]|None)->tuple[Point,Point,Point]:
    require(witness is not None and len(witness)==3,"missing three-point witness")
    points=tuple(tuple(p) for p in witness)
    allowed=set(base_points(base))
    require(all(p in allowed and oncurve(p) and times(p,R) is None for p in points),
            "witness contains a nonbase/offcurve/nonsubgroup point")
    require(plus(plus(points[0],points[1]),points[2])==q,
            "witness group identity differs from Q")
    return points
def parse_cms(stdout:str,exit_code:int,nvars:int)->tuple[str,dict[int,bool]|None]:
    declared=[]
    values={}
    for line in stdout.splitlines():
        if line.startswith("s "):
            declared.append(line[2:].strip())
        if line.startswith("v "):
            for token in line.split()[1:]:
                try:literal=int(token)
                except ValueError:raise ValueError("malformed CMS model literal") from None
                if not literal:continue
                variable=abs(literal)
                require(1<=variable<=nvars,"CMS model variable outside declared range")
                if variable in values and values[variable]!=(literal>0):
                    raise ValueError("contradictory repeated CMS assignment")
                values[variable]=literal>0
    require(len(declared)==1,"missing or multiple CMS status lines")
    expected={10:("SATISFIABLE","SAT"),20:("UNSATISFIABLE","UNSAT"),
              15:("INDETERMINATE","UNKNOWN")}
    require(exit_code in expected,"unexpected CMS exit code; zero is not a solved result")
    phrase,status=expected[exit_code]
    require(declared[0]==phrase,"CMS status text contradicts exit code")
    if status=="SAT":
        require(set(values)==set(range(1,nvars+1)),
                "CMS SAT model missing/out-of-range declared variable")
        return status,values
    require(not values,"non-SAT CMS result contains a model")
    return status,None
def decode_sat(c:circuits.Circuit,assignment:dict[int,bool],q:Point,base:dict)->tuple[Point,Point,Point]:
    require(c.public_q==q,"public Q differs from the archived original relation rows")
    require(circuits.evaluate(c,assignment),"CMS assignment violates original CNF or native XOR")
    xs=[sum(1<<bit for bit,var in enumerate(c.inputs[name]) if assignment[var])
        for name in ("x1","x2","x3")]
    require(xs==sorted(xs) and all(x in base["x_values"] for x in xs),
            "SAT model violates ordered exact x domain")
    lifts={x:[] for x in xs}
    for point in base_points(base):
        if point[0] in lifts:lifts[point[0]].append(point)
    require(all(len(lifts[x])==2 for x in xs),"SAT x has wrong rational signed lifts")
    for witness in itertools.product(*(lifts[x] for x in xs)):
        if plus(plus(witness[0],witness[1]),witness[2])==q:
            verify_witness(q,base,[list(p) for p in witness])
            return witness
    raise ValueError("complete SAT model has no exact group witness")
def independent_oracle(q:Point,base:dict)->tuple[Point,Point,Point]|None:
    points=base_points(base)
    table={}
    for i,p in enumerate(points):
        for j in range(i,len(points)):
            table.setdefault(plus(p,points[j]),(p,points[j]))
    for p in points:
        remainder=plus(q,negative(p))
        if remainder in table:
            pair=table[remainder]
            witness=(pair[0],pair[1],p)
            verify_witness(q,base,[list(x) for x in witness])
            return witness
    return None
def replay_result(result:dict[str,Any],q:Point,base:dict,expected:str,case_id:str,arm:str)->dict[str,Any]:
    require(result.get("Q")==list(q) and result.get("case_id")==case_id and
            result.get("arm")==arm,"result identity/case label mismatch")
    status=result.get("status")
    require(status in ("SAT","UNSAT","UNKNOWN"),"unknown worker result status")
    if status=="SAT":
        points=verify_witness(q,base,result.get("witness"))
        require(expected=="SAT","false SAT against frozen independent oracle")
        return {"valid":True,"status":status,"witness":[list(p) for p in points]}
    if status=="UNSAT":
        require(expected=="UNSAT","false UNSAT against frozen independent oracle")
        require(result.get("witness") is None,"UNSAT carries witness")
        return {"valid":True,"status":status,"witness":None}
    require(result.get("witness") is None,"UNKNOWN carries witness")
    return {"valid":False,"status":"UNKNOWN","witness":None,"censored":True}
