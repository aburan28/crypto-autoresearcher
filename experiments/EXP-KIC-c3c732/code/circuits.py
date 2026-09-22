"""Common S3 arithmetic and three frozen exact-domain CNF/native-XOR encodings."""
from __future__ import annotations
from typing import Any,Iterable
import field

Literal=int|bool
Form=tuple[tuple[int,...],int]

def s3(a:int,b:int,c:int)->int:
    ab=field.mul(a,b)
    return field.sq(field.mul(c,a^b))^field.mul(c,ab)^field.sq(ab)^1

def neg(lit:Literal)->Literal:return (not lit) if isinstance(lit,bool) else -lit
def lit_value(lit:Literal,assignment:dict[int,bool])->bool:
    return lit if isinstance(lit,bool) else (assignment[abs(lit)] if lit>0 else not assignment[abs(lit)])

class Circuit:
    def __init__(self)->None:
        self.nvars=0
        self.clauses:list[list[int]]=[]
        self.xors:list[tuple[list[int],int]]=[]
        self.inputs:dict[str,list[int]]={}
        self.domain:dict[str,dict[str,list[int]]]={}
        self.public_q:tuple[int,int]|None=None
        self.ops:list[dict[str,Any]]=[]
        self.memo:dict[tuple,Literal]={}
        self.forms:dict[Form,int]={}
    def var(self)->int:
        self.nvars+=1
        return self.nvars
    def bits(self,name:str,count:int=field.N)->list[int]:
        out=[self.var() for _ in range(count)]
        self.inputs[name]=out
        return out
    def clause(self,terms:Iterable[Literal])->None:
        seen=set();out=[]
        for item in terms:
            if isinstance(item,bool):
                if item:return
                continue
            if -item in seen:return
            if item not in seen:seen.add(item);out.append(item)
        self.clauses.append(out)
    def xor_row(self,terms:Iterable[Literal],rhs:int=0)->None:
        parity=rhs&1;counts={}
        for item in terms:
            if isinstance(item,bool):
                parity^=int(item)
                continue
            if item<0:parity^=1
            v=abs(item);counts[v]=counts.get(v,0)^1
        variables=sorted(v for v,odd in counts.items() if odd)
        if not variables:
            if parity:self.clause(())
            return
        self.xors.append((variables,parity))
    def and_(self,a:Literal,b:Literal)->Literal:
        if isinstance(a,bool):return b if a else False
        if isinstance(b,bool):return a if b else False
        if a==b:return a
        if a==-b:return False
        key=("and",min(a,b),max(a,b))
        if key in self.memo:return self.memo[key]
        z=self.var()
        self.clause((-z,a));self.clause((-z,b));self.clause((z,-a,-b))
        self.memo[key]=z
        self.ops.append({"kind":"and","out":z,"inputs":[a,b]})
        return z
    def or_(self,a:Literal,b:Literal)->Literal:return neg(self.and_(neg(a),neg(b)))
    def xor2(self,a:Literal,b:Literal)->Literal:
        if isinstance(a,bool):return neg(b) if a else b
        if isinstance(b,bool):return neg(a) if b else a
        if a==b:return False
        if a==-b:return True
        key=("xor",min(a,b),max(a,b))
        if key in self.memo:return self.memo[key]
        z=self.var();self.xor_row((a,b,z),0)
        self.memo[key]=z
        self.ops.append({"kind":"xor","out":z,"inputs":[a,b]})
        return z
    def mux(self,selector:Literal,zero:Literal,one:Literal)->Literal:
        if type(zero) is type(one) and zero==one:return zero
        if isinstance(selector,bool):return one if selector else zero
        key=("mux",selector,(type(zero).__name__,zero),(type(one).__name__,one))
        if key in self.memo:return self.memo[key]
        result=self.or_(self.and_(neg(selector),zero),self.and_(selector,one))
        self.memo[key]=result
        return result
    def form(self,items:Iterable[Literal],parity:int=0)->Form:
        state=parity&1;counts={}
        for item in items:
            if isinstance(item,bool):
                state^=int(item)
            else:
                if item<0:state^=1
                v=abs(item);counts[v]=counts.get(v,0)^1
        return tuple(sorted(v for v,odd in counts.items() if odd)),state
    def fadd(self,a:list[Form],b:list[Form])->list[Form]:
        return [self.form((*x[0],*y[0]),x[1]^y[1]) for x,y in zip(a,b)]
    def fconstant(self,value:int)->list[Form]:
        return [((),(value>>bit)&1) for bit in range(field.N)]
    def fbits(self,name:str)->list[Form]:
        return [((v,),0) for v in self.bits(name)]
    def materialize(self,form:Form)->Literal:
        variables,parity=form
        if not variables:return bool(parity)
        if len(variables)==1:return -variables[0] if parity else variables[0]
        if form in self.forms:return self.forms[form]
        out=self.var()
        self.xor_row((*variables,out),parity)
        self.forms[form]=out
        self.ops.append({"kind":"linear","out":out,"variables":list(variables),"parity":parity})
        return out
    def fsquare(self,a:list[Form])->list[Form]:
        output=[[] for _ in range(field.N)]
        for bit,form in enumerate(a):
            image=field.sq(1<<bit)
            for destination in range(field.N):
                if image>>destination&1:output[destination].append(form)
        return [self.sum_forms(terms) for terms in output]
    def sum_forms(self,forms:Iterable[Form])->Form:
        variables=[];parity=0
        for row,p in forms:variables.extend(row);parity^=p
        return self.form(variables,parity)
    def fconstmul(self,a:list[Form],constant:int)->list[Form]:
        output=[[] for _ in range(field.N)]
        for bit,form in enumerate(a):
            image=field.mul(1<<bit,constant)
            for destination in range(field.N):
                if image>>destination&1:output[destination].append(form)
        return [self.sum_forms(terms) for terms in output]
    def fmul(self,a:list[Form],b:list[Form])->list[Form]:
        if all(not row for row,_ in a):
            return self.fconstmul(b,sum(parity<<bit for bit,(_,parity) in enumerate(a)))
        if all(not row for row,_ in b):
            return self.fconstmul(a,sum(parity<<bit for bit,(_,parity) in enumerate(b)))
        output=[[] for _ in range(field.N)]
        for i,ai in enumerate(a):
            left=self.materialize(ai)
            for j,bj in enumerate(b):
                term=self.and_(left,self.materialize(bj))
                image=field.mul(1<<i,1<<j)
                for destination in range(field.N):
                    if image>>destination&1:output[destination].append(self.form((term,)))
        return [self.sum_forms(terms) for terms in output]
    def s3(self,a:list[Form],b:list[Form],c:list[Form])->list[Form]:
        ab=self.fmul(a,b)
        term1=self.fsquare(self.fmul(c,self.fadd(a,b)))
        term2=self.fmul(c,ab)
        term3=self.fsquare(ab)
        return self.fadd(self.fadd(term1,term2),self.fadd(term3,self.fconstant(1)))
    def zero_field(self,a:list[Form])->None:
        for variables,parity in a:self.xor_row(variables,parity)
    def equal_field(self,a:list[Form],b:list[Form])->None:
        self.zero_field(self.fadd(a,b))
    def exactly_one(self,selectors:list[int])->None:
        if not selectors:self.clause(());return
        self.clause(selectors)
        if len(selectors)==1:return
        count=[self.var() for _ in range(len(selectors)-1)]
        self.clause((-selectors[0],count[0]))
        self.ops.append({"kind":"prefix_or","out":count[0],"selectors":selectors[:1]})
        for k in range(1,len(selectors)-1):
            self.clause((-selectors[k],count[k]))
            self.clause((-count[k-1],count[k]))
            self.clause((-selectors[k],-count[k-1]))
            self.ops.append({"kind":"prefix_or","out":count[k],"selectors":selectors[:k+1]})
        self.clause((-selectors[-1],-count[-1]))
    def explicit_domain(self,x:list[Form],xs:tuple[int,...],name:str)->None:
        selectors=self.bits(name,len(xs))
        self.exactly_one(selectors)
        raw=[self.materialize(bit) for bit in x]
        if not xs:raise ValueError("empty explicit domain")
        for selector,value in zip(selectors,xs):
            for bit,coordinate in enumerate(raw):
                self.clause((-selector,coordinate if value>>bit&1 else neg(coordinate)))
        for bit,coordinate in enumerate(raw):
            self.clause((neg(coordinate),*(selectors[i] for i,v in enumerate(xs) if v>>bit&1)))
            self.clause((coordinate,*(selectors[i] for i,v in enumerate(xs) if not(v>>bit&1))))
        self.domain[name]={"selectors":selectors}
    def flat_onehot(self,x:list[Form],plane_normal:tuple[int,int,int],columns:tuple[int,...],name:str)->None:
        shifts=self.bits(name+"_j",19)
        u,v=self.bits(name+"_uv",2)
        self.exactly_one(shifts)
        u_terms=[self.and_(j,u) for j in shifts]
        v_terms=[self.and_(j,v) for j in shifts]
        a,b,c=plane_normal
        normal=[]
        for bit in range(field.N):
            terms=[]
            for j in range(19):
                source=(bit-j)%19
                if a>>source&1:terms.append(shifts[j])
                if b>>source&1:terms.append(u_terms[j])
                if c>>source&1:terms.append(v_terms[j])
            normal.append(self.form(terms))
        poly=[self.sum_forms(normal[k] for k in range(19) if columns[k]>>bit&1)
              for bit in range(19)]
        self.equal_field(x,poly)
        self.domain[name]={"shifts":shifts,"u":[u],"v":[v]}
    def flat_binary(self,x:list[Form],plane_normal:tuple[int,int,int],columns:tuple[int,...],name:str)->None:
        shifts=self.bits(name+"_j",5)
        u,v=self.bits(name+"_uv",2)
        for value in range(19,32):
            self.clause((neg(shifts[bit]) if value>>bit&1 else shifts[bit]
                         for bit in range(5)))
        a,b,c=plane_normal
        normal=[self.form((bool(a>>k&1),
                          u if b>>k&1 else False,
                          v if c>>k&1 else False)) for k in range(19)]
        for amount,selector in ((1,shifts[0]),(2,shifts[1]),(4,shifts[2]),
                                (8,shifts[3]),(16,shifts[4])):
            material=[self.materialize(item) for item in normal]
            normal=[self.form((self.mux(selector,material[k],material[(k-amount)%19]),))
                    for k in range(19)]
        poly=[self.sum_forms(normal[k] for k in range(19) if columns[k]>>bit&1)
              for bit in range(19)]
        self.equal_field(x,poly)
        self.domain[name]={"shift_bits":shifts,"u":[u],"v":[v]}
    def leq(self,a:list[Form],b:list[Form])->None:
        lower:Literal=True
        for left,right in zip(a,b):
            x=self.materialize(left);y=self.materialize(right)
            less=self.and_(neg(x),y)
            equal=neg(self.xor2(x,y))
            lower=self.or_(less,self.and_(equal,lower))
        self.clause((lower,))
    def relation(self,base:dict,q:field.Point,arm:str)->dict[str,Any]:
        if q is None:raise ValueError("infinity target")
        self.public_q=q
        xs=base["x_values"]
        x=[self.fbits(f"x{k}") for k in (1,2,3)]
        t=self.fbits("t")
        for k,bits in enumerate(x,1):
            name=f"d{k}"
            if arm=="explicit_onehot":self.explicit_domain(bits,xs,name)
            elif arm=="flat_onehot":self.flat_onehot(bits,base["plane_normal"],base["normal_columns"],name)
            elif arm=="flat_binary":self.flat_binary(bits,base["plane_normal"],base["normal_columns"],name)
            else:raise ValueError("unknown SAT arm")
        self.leq(x[0],x[1]);self.leq(x[1],x[2])
        self.zero_field(self.s3(x[0],x[1],t))
        self.zero_field(self.s3(t,x[2],self.fconstant(q[0])))
        return {"nvars":self.nvars,"clauses":len(self.clauses),"xor_rows":len(self.xors),
                "domain_arm":arm}
    def dimacs(self)->str:
        lines=[f"p cnf {self.nvars} {len(self.clauses)+len(self.xors)}"]
        lines.extend(" ".join(map(str,row))+" 0" for row in self.clauses)
        for variables,rhs in self.xors:
            line=variables.copy()
            if rhs==0:line[0]=-line[0]
            lines.append("x "+" ".join(map(str,line))+" 0")
        return "\n".join(lines)+"\n"
    def manifest(self)->dict[str,Any]:
        return {"nvars":self.nvars,"clauses":self.clauses,
                "xor_rows":[{"variables":v,"rhs":r} for v,r in self.xors],
                "inputs":self.inputs,"domain":self.domain,"ops":self.ops,
                "public_q":list(self.public_q) if self.public_q else None,
                "xor_export_convention":"RHS1 all positive; RHS0 first literal negated"}

def evaluate(c:Circuit,assignment:dict[int,bool])->bool:
    if set(assignment)!=set(range(1,c.nvars+1)):return False
    if not all(any(lit_value(lit,assignment) for lit in row) for row in c.clauses):return False
    return all(sum(assignment[v] for v in variables)%2==rhs for variables,rhs in c.xors)

def complete_assignment(c:Circuit,inputs:dict[int,bool])->dict[int,bool]:
    assignment=inputs.copy()
    for op in c.ops:
        kind=op["kind"]
        if kind=="and":value=all(lit_value(lit,assignment) for lit in op["inputs"])
        elif kind=="xor":value=lit_value(op["inputs"][0],assignment)!=lit_value(op["inputs"][1],assignment)
        elif kind=="linear":value=bool(op["parity"]^
                                        (sum(assignment[v] for v in op["variables"])%2))
        elif kind=="prefix_or":value=any(assignment[v] for v in op["selectors"])
        else:raise ValueError("unknown gate operation")
        if op["out"] in assignment and assignment[op["out"]]!=value:
            raise ValueError("assigned gate contradicts deterministic output")
        assignment[op["out"]]=value
    return assignment
