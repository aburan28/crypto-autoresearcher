"""Bit-exact S3 CNF/native-XOR circuits and deterministic static propagation."""
from __future__ import annotations
import itertools,json
from typing import Any,Iterable
import field

def reduce_poly(poly:int)->int:
    for bit in range(poly.bit_length()-1,6,-1):
        if poly>>bit&1:poly^=field.MODULUS<<(bit-7)
    return poly
def s3(a:int,b:int,c:int)->int:
    ab=field.mul(a,b)
    return field.mul(field.sq(a^b),field.sq(c))^field.mul(ab,c)^field.sq(ab)^1
def relation_field_holds(x1:int,x2:int,x3:int,xq:int)->bool:
    return any(s3(x1,x2,t)==0 and s3(t,x3,xq)==0 for t in range(128))

class Circuit:
    def __init__(self)->None:
        self.nvars=0;self.clauses:list[list[int]]=[];self.xors:list[tuple[list[int],int]]=[]
        self.cache:dict[tuple, int]={};self.zero=self.var();self.one=self.var()
        self.ops:list[tuple[str,int,int,int]]=[]
        self.clause([-self.zero]);self.clause([self.one]);self.inputs:dict[str,list[int]]={}
    def var(self)->int:self.nvars+=1;return self.nvars
    def bits(self,name:str,n:int=7)->list[int]:
        result=[self.var() for _ in range(n)];self.inputs[name]=result;return result
    def clause(self,literals:Iterable[int])->None:
        # Preserve first-occurrence order while reducing to logical literals.
        # A clause containing both signs is tautological and contributes no
        # constraint; repeated same-sign literals must not mask a unit.
        normalized=[];seen=set()
        for lit in literals:
            if -lit in seen:return
            if lit not in seen:normalized.append(lit);seen.add(lit)
        self.clauses.append(normalized)
    def const(self,value:int)->int:return self.one if value else self.zero
    def and_(self,a:int,b:int)->int:
        key=("and",min(a,b),max(a,b))
        if key in self.cache:return self.cache[key]
        z=self.var();self.clause([-z,a]);self.clause([-z,b]);self.clause([z,-a,-b]);self.cache[key]=z;self.ops.append(("and",z,a,b));return z
    def or_(self,a:int,b:int)->int:return -self.and_(-a,-b)
    def xor_row(self,literals:Iterable[int],rhs:int)->None:
        parity=rhs&1;counts:dict[int,int]={}
        for lit in literals:
            if lit<0:parity^=1
            var=abs(lit);counts[var]=counts.get(var,0)^1
        vars_=sorted(var for var,count in counts.items() if count)
        if not vars_:
            if parity:self.clause([])
            return
        self.xors.append((vars_,parity))
    def xor2(self,a:int,b:int)->int:
        key=("xor",min(a,b),max(a,b))
        if key in self.cache:return self.cache[key]
        z=self.var();self.xor_row((a,b,z),0);self.cache[key]=z;self.ops.append(("xor",z,a,b));return z
    def xor_many(self,terms:Iterable[int])->int:
        out=self.zero
        for term in terms:out=self.xor2(out,term)
        return out
    def mux(self,selector:int,zero:int,one:int)->int:
        return self.or_(self.and_(-selector,zero),self.and_(selector,one))
    def fadd(self,a:list[int],b:list[int])->list[int]:return [self.xor2(x,y) for x,y in zip(a,b)]
    def fsquare(self,a:list[int])->list[int]:
        outputs=[[] for _ in range(7)]
        for i,bit in enumerate(a):
            image=reduce_poly(1<<(2*i))
            for k in range(7):
                if image>>k&1:outputs[k].append(bit)
        return [self.xor_many(terms) for terms in outputs]
    def fmul(self,a:list[int],b:list[int])->list[int]:
        outputs=[[] for _ in range(7)]
        for i,x in enumerate(a):
            for j,y in enumerate(b):
                term=self.and_(x,y);image=reduce_poly(1<<(i+j))
                for k in range(7):
                    if image>>k&1:outputs[k].append(term)
        return [self.xor_many(terms) for terms in outputs]
    def constant_bits(self,value:int)->list[int]:return [self.const(value>>i&1) for i in range(7)]
    def equal_field(self,a:list[int],b:list[int])->None:
        for x,y in zip(a,b):self.xor_row((x,y),0)
    def zero_field(self,a:list[int])->None:
        for x in a:self.clause([-x])
    def s3(self,a:list[int],b:list[int],c:list[int])->list[int]:
        ab=self.fmul(a,b)
        term1=self.fmul(self.fsquare(self.fadd(a,b)),self.fsquare(c))
        term2=self.fmul(ab,c);term3=self.fsquare(ab)
        return self.fadd(self.fadd(term1,term2),self.fadd(term3,self.constant_bits(1)))
    def leq(self,a:list[int],b:list[int])->None:
        # From low to high, the current bit overrides lower-bit comparison
        # unless equal. `lt` means a<=b on the processed prefix.
        lt=self.one
        for x,y in zip(a,b):
            less=self.and_(-x,y)
            equal=-self.xor2(x,y)
            lt=self.or_(less,self.and_(equal,lt))
        self.clause([lt])
    def force_bits(self,bits:list[int],value:int)->None:
        for i,bit in enumerate(bits):self.clause([bit if value>>i&1 else -bit])
    def explicit_domain(self,x:list[int],xs:list[int],name:str)->list[int]:
        width=max(1,(len(xs)-1).bit_length());idx=self.bits(name,width)
        for value in range(1<<width):
            match=[idx[k] if value>>k&1 else -idx[k] for k in range(width)]
            if value>=len(xs):self.clause([-lit for lit in match]);continue
            for k,out in enumerate(x):self.clause([-lit for lit in match]+[out if xs[value]>>k&1 else -out])
        return idx
    def structured_domain(self,x:list[int],base:dict,name:str)->dict[str,list[int]]:
        t=self.bits(name+"_t",1)[0];j=self.bits(name+"_j",3);u=self.bits(name+"_u",1)[0];v=self.bits(name+"_v",1)[0]
        self.clause([-j[0],-j[1],-j[2]]) # j=7 forbidden
        columns=tuple(base["columns"])
        # The archived flat triples are polynomial-coordinate values. Convert
        # once to normal coefficient masks before the cyclic Frobenius mux;
        # rotating polynomial bits would represent a different mathematical map.
        flats=[[field.poly_to_normal(value,columns) for value in triple]
               for triple in base["flats"]]
        normal=[]
        for k in range(7):
            a=self.mux(t,self.const(flats[0][0]>>k&1),self.const(flats[1][0]>>k&1))
            b=self.mux(t,self.const(flats[0][1]>>k&1),self.const(flats[1][1]>>k&1))
            c=self.mux(t,self.const(flats[0][2]>>k&1),self.const(flats[1][2]>>k&1))
            normal.append(self.xor_many((a,self.and_(u,b),self.and_(v,c))))
        for shift,selector in ((1,j[0]),(2,j[1]),(4,j[2])):
            normal=[self.mux(selector,normal[k],normal[(k-shift)%7]) for k in range(7)]
        poly=[]
        for bit in range(7):poly.append(self.xor_many(normal[k] for k in range(7) if columns[k]>>bit&1))
        self.equal_field(x,poly)
        # Each noncanonical assignment and each nonadmitted x is explicitly
        # forbidden, not merely mapped onto a duplicate coordinate.
        for mapping in base["all_mappings"]:
            if mapping["valid"]:continue
            t0,j0,u0,v0=mapping["selector"]
            bits=[t,*j,u,v];value=[t0,*((j0>>k)&1 for k in range(3)),u0,v0]
            self.clause([(-lit if bit else lit) for lit,bit in zip(bits,value)])
        return {"t":[t],"j":j,"u":[u],"v":[v]}
    def relation(self,base:dict,q:field.Point,arm:str)->dict:
        assert q is not None
        xs=base["x_values"]
        x=[self.bits(f"x{i}") for i in (1,2,3)];t=self.bits("t")
        for i,bits in enumerate(x,1):
            if arm=="flat_sat":self.structured_domain(bits,base,f"sel{i}")
            else:self.explicit_domain(bits,xs,f"idx{i}")
        self.leq(x[0],x[1]);self.leq(x[1],x[2])
        self.zero_field(self.s3(x[0],x[1],t))
        self.zero_field(self.s3(t,x[2],self.constant_bits(q[0])))
        return {"x_vars":x,"t_vars":t,"nvars":self.nvars,"clauses":len(self.clauses),"xor_rows":len(self.xors)}
    def dimacs(self)->str:
        lines=[f"p cnf {self.nvars} {len(self.clauses)+len(self.xors)}"]
        lines.extend(" ".join(map(str,clause))+" 0" for clause in self.clauses)
        for vars_,rhs in self.xors:
            assert vars_
            lits=vars_.copy()
            if rhs==0:lits[0]=-lits[0]
            lines.append("x "+" ".join(map(str,lits))+" 0")
        return "\n".join(lines)+"\n"
    def manifest(self)->dict[str,Any]:return {"nvars":self.nvars,"clauses":self.clauses,"xor_rows":[{"vars":v,"rhs":r} for v,r in self.xors],"inputs":self.inputs}

def evaluate(c:Circuit,assignment:dict[int,bool])->bool:
    for clause in c.clauses:
        if not any(assignment.get(abs(lit),False)==(lit>0) for lit in clause):return False
    for vars_,rhs in c.xors:
        if sum(bool(assignment.get(v,False)) for v in vars_)%2!=rhs:return False
    return True

def complete_assignment(c:Circuit,inputs:dict[int,bool])->dict[int,bool]:
    assignment={c.zero:False,c.one:True,**inputs}
    def value(lit:int)->bool:
        return assignment[abs(lit)] if lit>0 else not assignment[abs(lit)]
    for kind,z,a,b in c.ops:
        computed=value(a) and value(b) if kind=="and" else value(a)!=value(b)
        if z in assignment and assignment[z]!=computed:raise ValueError("input contradicts gate")
        assignment[z]=computed
    return assignment

def propagate(c:Circuit,units:dict[int,bool])->dict[str,Any]:
    assignment=units.copy();rounds=0
    while True:
        rounds+=1;changed=False
        for clause in c.clauses:
            undecided=[];satisfied=False
            for lit in clause:
                value=assignment.get(abs(lit))
                if value is None:undecided.append(lit)
                elif value==(lit>0):satisfied=True;break
            if satisfied:continue
            if not undecided:return {"contradiction":True,"assigned":len(assignment),"rounds":rounds}
            if len(undecided)==1:
                lit=undecided[0];var=abs(lit);value=lit>0
                if var in assignment and assignment[var]!=value:return {"contradiction":True,"assigned":len(assignment),"rounds":rounds}
                if var not in assignment:assignment[var]=value;changed=True
        rows=[]
        for vars_,rhs in c.xors:
            unresolved=[];parity=rhs
            for var in vars_:
                if var in assignment:parity^=int(assignment[var])
                else:unresolved.append(var)
            mask=sum(1<<(v-1) for v in unresolved);rows.append([mask,parity])
        # Deterministic GF(2) RREF with least-variable pivots. Sparse pivot
        # indexing avoids scanning all nvars against every dense original row.
        pivots={}
        for mask,rhs in rows:
            while mask:
                var=(mask&-mask).bit_length()
                if var not in pivots:
                    pivots[var]=[mask,rhs];break
                pmask,prhs=pivots[var];mask^=pmask;rhs^=prhs
            if mask==0 and rhs:return {"contradiction":True,"assigned":len(assignment),"rounds":rounds}
        pivot_vars=sorted(pivots)
        for index in range(len(pivot_vars)-1,-1,-1):
            var=pivot_vars[index];mask,rhs=pivots[var]
            for earlier in pivot_vars[:index]:
                if pivots[earlier][0]>>(var-1)&1:
                    pivots[earlier][0]^=mask;pivots[earlier][1]^=rhs
        for mask,rhs in pivots.values():
            if mask==0 and rhs:return {"contradiction":True,"assigned":len(assignment),"rounds":rounds}
            if mask.bit_count()==1:
                var=mask.bit_length();value=bool(rhs)
                if var in assignment and assignment[var]!=value:return {"contradiction":True,"assigned":len(assignment),"rounds":rounds}
                if var not in assignment:assignment[var]=value;changed=True
        if not changed:return {"contradiction":False,"assigned":len(assignment),"rounds":rounds}
