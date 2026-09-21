#!/usr/bin/env python3
"""EXP-ECDLP-abf981 finite instrument; no scientific work occurs on import.

Only --mechanical-check is executable without a separately published run
approval and a verified repository LOCKED plan. The original spec stays frozen.
No arbitrary formula input, external arithmetic, optimization, or extra cells.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import resource
import re
import signal
import sys
import time
import traceback

EXPERIMENT = "EXP-ECDLP-abf981"
SPEC_PATH = "experiments/EXP-ECDLP-abf981/specification.yaml"
SPEC_SHA256 = "7d9a6cccbfdaf8d9efc1d565cf437c1e833d4de964c5fdc3cd77b72e3d3dbf93"
SOURCE_PATH = "experiments/EXP-ECDLP-abf981/source/run_model_comparison.py"
OUTSIDE = {k: "outside_frozen_diagnostic" for k in (
    "first_fall_degree", "Groebner_solving_degree", "geometric_summation_degree",
    "geometric_elimination_degree", "rank_accumulation", "descent", "DLP_solving")}


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


class GateFailure(Exception):
    def __init__(self, gate, evidence):
        self.gate, self.evidence = gate, evidence
        super().__init__(f"{gate}: {evidence!r}")


def require(condition, gate, evidence):
    if not condition:
        raise GateFailure(gate, evidence)


class Meter:
    """Instrumented primitive counts, separate from modeled term evaluation."""
    def __init__(self):
        self.counts = Counter()
        self.modeled = Counter()
        self.phases = []
        self.integer_bits = Counter()

    def tick(self, name, count=1):
        self.counts[name] += count

    def integer(self, value):
        self.integer_bits[abs(value).bit_length()] += 1
        return value

    @staticmethod
    def rss():
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if sys.platform == "darwin" else value * 1024)

    @contextlib.contextmanager
    def phase(self, name):
        w, c, before, model = time.perf_counter(), time.process_time(), self.counts.copy(), self.modeled.copy()
        try:
            yield
        finally:
            self.phases.append({"phase": name, "wall_seconds": time.perf_counter()-w,
                "process_cpu_seconds": time.process_time()-c, "peak_rss_bytes": self.rss(),
                "peak_rss_semantics": "process cumulative high-water mark at phase end",
                "instrumented_operations": dict(self.counts-before),
                "modeled_term_evaluation_operations": dict(self.modeled-model)})


class Field:
    def __init__(self, p, meter):
        self.p, self.m = p, meter

    def red(self, x):
        self.m.tick("field_reductions")
        self.m.integer(x)
        return x % self.p

    def add(self, a, b):
        self.m.tick("field_additions_subtractions")
        return self.red(a+b)

    def sub(self, a, b):
        self.m.tick("field_additions_subtractions")
        return self.red(a-b)

    def mul(self, a, b):
        self.m.tick("field_multiplications_squares")
        return self.red(a*b)

    def power(self, a, n):
        result = 1
        for _ in range(n):
            result = self.mul(result, a)
        return result

    def inv(self, a):
        self.m.tick("field_inversions")
        a = self.red(a)
        if self.eq(a, 0):
            raise ZeroDivisionError("inverse of zero")
        # Python modular inverse is one instrumented field inversion, not a
        # claimed measured count of its internal integer/Euclidean operations.
        return pow(a, -1, self.p)

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def eq(self, a, b):
        self.m.tick("field_comparisons")
        return a % self.p == b % self.p


class Poly:
    """Sparse exact expansion; never reduces powers using field equations."""
    def __init__(self, field, variables, terms=None):
        self.f, self.variables = field, tuple(variables)
        self.terms = {tuple(e): field.red(c) for e, c in (terms or {}).items() if field.red(c)}

    @classmethod
    def const(cls, f, variables, c):
        return cls(f, variables, {(0,)*len(variables): c})

    @classmethod
    def var(cls, f, variables, name):
        e = [0]*len(variables)
        e[variables.index(name)] = 1
        return cls(f, variables, {tuple(e): 1})

    def lift(self, other):
        if isinstance(other, int):
            return Poly.const(self.f, self.variables, other)
        if not isinstance(other, Poly) or other.variables != self.variables or other.f.p != self.f.p:
            raise TypeError("incompatible polynomial ring")
        return other

    def __add__(self, other):
        other = self.lift(other)
        terms = self.terms.copy()
        for e, c in other.terms.items():
            self.f.m.tick("polynomial_support_table_lookups")
            terms[e] = self.f.add(terms.get(e, 0), c)
        return Poly(self.f, self.variables, terms)

    __radd__ = __add__

    def __neg__(self):
        return Poly(self.f, self.variables, {e: self.f.sub(0, c) for e,c in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.lift(other))

    def __rsub__(self, other):
        return self.lift(other) + (-self)

    def __mul__(self, other):
        other = self.lift(other)
        terms = {}
        for e, c in self.terms.items():
            for q, d in other.terms.items():
                exponent = tuple(a+b for a,b in zip(e,q))
                self.f.m.tick("polynomial_support_table_lookups")
                terms[exponent] = self.f.add(terms.get(exponent,0), self.f.mul(c,d))
        return Poly(self.f, self.variables, terms)

    __rmul__ = __mul__

    def __pow__(self, n):
        if type(n) is not int or n < 0:
            raise TypeError("only nonnegative integer exponents")
        result = Poly.const(self.f, self.variables, 1)
        for _ in range(n):
            result = result*self
        return result

    def terms_list(self):
        return [[c,list(e)] for e,c in sorted(self.terms.items())]

    def normalized(self):
        if not self.terms:
            return self
        leading = self.terms[max(self.terms)]
        inverse = self.f.inv(leading)
        return Poly(self.f, self.variables, {e:self.f.mul(c,inverse) for e,c in self.terms.items()})

    def descriptor(self, category, formula):
        normal = self.normalized()
        exps = list(normal.terms)
        return {"category":category,"formula":formula,"raw_terms":self.terms_list(),
            "normalized_terms":normal.terms_list(),"is_zero":not exps,
            "total_degree":max((sum(e) for e in exps),default=None),
            "per_variable_degree":[max((e[i] for e in exps),default=None) for i in range(len(self.variables))]}

    def evaluate(self, assignment):
        # No cache across terms or polynomials: exactly the frozen cost rule.
        values = [assignment[v] for v in self.variables]
        self.f.m.tick("polynomial_evaluations")
        value = 0
        for exps, coeff in sorted(self.terms.items()):
            term = coeff
            for x, exponent in zip(values,exps):
                power = 1
                for _ in range(exponent):
                    power = self.f.mul(power,x)
                    self.f.m.modeled["field_multiplications_squares"] += 1
                term = self.f.mul(term,power)
                self.f.m.modeled["field_multiplications_squares"] += 1
            value = self.f.add(value,term)
            self.f.m.modeled["field_additions_subtractions"] += 1
        return value


def formula_python_syntax(text):
    # Lexical parser alias only; declared variables/formulas remain unchanged.
    return re.sub(r"\blambda\b", "_frozen_lambda_symbol", text.replace("^","**").removesuffix("=0"))


def expression(text, f, variables, constants):
    """Parse only frozen arithmetic formulas, never eval or arbitrary code."""
    tree = ast.parse(formula_python_syntax(text),mode="eval")
    def walk(node):
        if isinstance(node,ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node,ast.Name):
            name = "lambda" if node.id == "_frozen_lambda_symbol" else node.id
            if name in variables:
                return Poly.var(f,variables,name)
            if name in constants:
                return constants[name]
            raise ValueError(f"undeclared symbol {name}")
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):
            return -walk(node.operand)
        if isinstance(node,ast.BinOp):
            a,b = walk(node.left),walk(node.right)
            if isinstance(node.op,ast.Add): return a+b
            if isinstance(node.op,ast.Sub): return a-b
            if isinstance(node.op,ast.Mult): return a*b
            if isinstance(node.op,ast.Pow) and type(b) is int: return a**b
        raise ValueError("unsupported frozen expression grammar")
    ans = walk(tree.body)
    return Poly.const(f,variables,ans) if isinstance(ans,int) else ans


def membership(f,variables,u,v,points):
    f.m.tick("membership_constructions")
    x,y = Poly.var(f,variables,u),Poly.var(f,variables,v)
    total = Poly.const(f,variables,0)
    for a,b in points:
        total = total + (1-(x-a)**(f.p-1))*(1-(y-b)**(f.p-1))
    return total-1


def json_point(model,P,p):
    if P is None:
        return {"kind":"O"} if model=="W" else {"kind":"O","projective":[1,p-1,0]}
    if model=="Ed": return {"e":P[0],"t":P[1]}
    names = ("X","Y") if model=="W" else ("h","k")
    return {"kind":"affine",names[0]:P[0],names[1]:P[1]}


class Geometry:
    def __init__(self,row,meter):
        self.row,self.m = row,meter
        self.p,self.f = row["p"],Field(row["p"],meter)
        self.T = (row["r"],0)

    def on_curve(self,model,P):
        f=self.f
        self.m.tick("on_curve_"+model)
        if P is None:return model in ("W","H")
        x,y=P
        if model=="W":return f.eq(f.power(y,2),f.sub(f.power(x,3),432))
        if model=="H":return f.eq(f.add(f.add(f.power(x,3),f.power(y,3)),1),0)
        if model=="Ed":return f.eq(f.add(f.power(x,2),f.power(y,2)),
            f.add(1,f.mul(self.row["d_edwards"],f.mul(f.power(x,2),f.power(y,2)))))
        raise ValueError(model)

    def neg(self,model,P):
        if P is None:return None
        if model=="W":return (P[0],self.f.sub(0,P[1]))
        if model=="H":return (P[1],P[0])
        return (self.f.sub(0,P[0]),P[1])

    def add_W(self,P,Q):
        f=self.f
        self.m.tick("group_additions_W")
        if P is None:return Q
        if Q is None:return P
        x,y=P; xx,yy=Q
        if f.eq(x,xx) and f.eq(f.add(y,yy),0):return None
        if f.eq(x,xx):
            require(P==Q,"W_equal_x",[P,Q])
            slope=f.div(f.mul(3,f.power(x,2)),f.mul(2,y))
        else:slope=f.div(f.sub(yy,y),f.sub(xx,x))
        xn=f.sub(f.sub(f.power(slope,2),x),xx)
        yn=f.sub(f.mul(slope,f.sub(x,xn)),y)
        return xn,yn

    def from_W(self,model,P):
        if model=="W":return P
        self.m.tick("map_W_to_"+model)
        f=self.f;r,s,c=(self.row[k] for k in ("r","s","c"))
        if model=="H":
            if P is None:self.m.tick("map_identity_branch");return None
            x,y=P
            return f.div(f.sub(-36,y),f.mul(6,x)),f.div(f.add(-36,y),f.mul(6,x))
        if P is None:self.m.tick("map_identity_branch");return (0,1)
        if P==self.T:self.m.tick("map_torsion_branch");return (0,self.p-1)
        x,y=P; xr=f.sub(x,r)
        return f.div(f.mul(c,xr),y),f.div(f.sub(xr,s),f.add(xr,s))

    def to_W(self,model,P):
        if model=="W":return P
        self.m.tick("map_"+model+"_to_W")
        f=self.f;r,s,c=(self.row[k] for k in ("r","s","c"))
        if model=="H":
            if P is None:self.m.tick("map_identity_branch");return None
            h,k=P;x=f.div(-12,f.add(h,k))
            return x,f.mul(f.mul(3,x),f.sub(k,h))
        e,t=P
        if f.eq(e,0):
            if f.eq(t,1):self.m.tick("map_identity_branch");return None
            if f.eq(t,-1):self.m.tick("map_torsion_branch");return self.T
            raise ZeroDivisionError("unexpected Edwards e=0 exception")
        u=f.div(f.add(1,t),f.sub(1,t));v=f.div(f.mul(c,u),e)
        return f.add(r,f.mul(s,u)),f.mul(s,v)

    def add_native(self,model,P,Q):
        self.m.tick("group_additions_"+model+"_native")
        if model=="W":return self.add_W(P,Q)
        f=self.f
        if model=="Ed":
            e,t=P;ee,tt=Q
            product=f.mul(self.row["d_edwards"],f.mul(f.mul(e,ee),f.mul(t,tt)))
            return (f.div(f.add(f.mul(e,tt),f.mul(t,ee)),f.add(1,product)),
                    f.div(f.sub(f.mul(t,tt),f.mul(e,ee)),f.sub(1,product)))
        if P is None:return Q
        if Q is None:return P
        h,k=P;hh,kk=Q
        D=f.sub(f.mul(hh,kk),f.mul(h,k))
        if f.eq(D,0):
            self.m.tick("H_Dzero_W_fallback")
            return self.from_W("H",self.add_W(self.to_W("H",P),self.to_W("H",Q)))
        return (f.div(f.sub(f.mul(f.power(k,2),hh),f.mul(f.power(kk,2),h)),D),
                f.div(f.sub(f.mul(f.power(h,2),kk),f.mul(f.power(hh,2),k)),D))

    def coordinate(self,name,P):
        self.m.tick("coordinate_evaluations_"+name)
        if name=="WX":return "infinity" if P is None else P[0]
        if name=="Edt":return self.from_W("Ed",P)[1]
        if name=="Hh":return "infinity" if P is None else self.from_W("H",P)[0]
        if name=="Hs":
            if P is None:return 0
            h,k=self.from_W("H",P)
            return self.f.add(h,k)
        raise ValueError(name)

    def mu(self,t):
        self.m.tick("PGL2_evaluations")
        if t=="infinity":return 1
        if self.f.eq(t,-2):return "infinity"
        return self.f.div(self.f.add(t,1),self.f.add(t,2))


def availability(g, cert, controls):
    """Exactly the frozen point-candidate sets; called only after run gate."""
    f,p,r = g.f,g.p,g.row
    checks = {
        "prime":p>=2 and all(p%d for d in range(2,math.isqrt(p)+1)),
        "3r2_s2":f.eq(f.mul(3,f.power(r['r'],2)),f.power(r['s'],2)),
        "r3_432":f.eq(f.power(r['r'],3),432),
        "A":f.eq(r['A'],f.div(f.mul(3,r['r']),r['s'])),
        "B":f.eq(r['B'],f.inv(r['s'])),
        "a":f.eq(r['a'],f.add(f.mul(3,r['r']),f.mul(2,r['s']))),
        "c2":f.eq(r['a'],f.power(r['c'],2)),
        "d_twisted":f.eq(r['d_twisted'],f.sub(f.mul(3,r['r']),f.mul(2,r['s']))),
        "d_edwards":f.eq(r['d_edwards'],f.div(r['d_twisted'],r['a'])),
        "W_nonsingular":not f.eq(f.mul(27,f.power(-432,2)),0),
        "H_nonsingular":p!=3,
        "Ed_nonsingular":r['d_edwards'] not in (0,1),
        "Ed_d_nonsquare":not any(f.eq(f.power(x,2),r['d_edwards']) for x in range(p)),
        "M_nonsingular":r['B']%p!=0 and not f.eq(f.power(r['A'],2),4),
        "twisted_Ed_nonsingular":r['a']%p!=0 and r['d_twisted']%p!=0 and not f.eq(r['a'],r['d_twisted'])}
    cert['parameter_gate']=checks
    require(all(checks.values()),'parameter_gate',checks)
    points={}
    for model in ('W','H','Ed'):
        candidates=[]; affine=[]
        for x,y in itertools.product(range(p),repeat=2):
            ok=g.on_curve(model,(x,y))
            candidates.append({'coordinates':[x,y],'on_curve':ok})
            if ok:affine.append((x,y))
        cert['candidates_'+model]=candidates
        points[model]=([None] if model in ('W','H') else [])+affine
    infinity_candidates=[[1,k,0] for k in range(p)]+[[0,1,0]]
    infinity=[q for q in infinity_candidates if f.eq(f.add(f.power(q[0],3),f.power(q[1],3)),0)]
    cert['H_infinity_candidates']=[{'projective':q,'on_curve':q in infinity} for q in infinity_candidates]
    require(infinity==[[1,p-1,0]],'unique_H_infinity',infinity)
    W=points['W'];idx={P:i for i,P in enumerate(W)}
    cert['points']={M:[json_point(M,P,p) for P in Ps] for M,Ps in points.items()}
    cert['actual_group_order']=len(W)
    require(len(W)==r['expected_group_order'],'group_order',len(W))
    require(g.T in W,'torsion_on_curve',g.T)
    exceptional={
        'W_Xzero_equation':[y for y in range(p) if f.eq(f.power(y,2),-432)],
        'W_Yzero':[P for P in W if P is not None and f.eq(P[1],0)],
        'W_X_r_plus_s_zero':[P for P in W if P is not None and f.eq(f.add(f.sub(P[0],r['r']),r['s']),0)],
        'H_finite_h_plus_k_zero':[P for P in points['H'] if P is not None and f.eq(f.add(*P),0)],
        'H_impossible_system_residuals':[[h,f.add(f.add(f.power(h,3),f.power(f.sub(0,h),3)),1)] for h in range(p)],
        'Ed_ezero':[P for P in points['Ed'] if f.eq(P[0],0)],
        'Ed_tone_nonzero_e':[P for P in points['Ed'] if f.eq(P[1],1) and not f.eq(P[0],0)]}
    cert['exceptions']=exceptional
    require(not exceptional['W_Xzero_equation'],'W_H_denominator',exceptional)
    require(exceptional['W_Yzero']==[g.T] and not exceptional['W_X_r_plus_s_zero'],'W_Ed_denominator',exceptional)
    require(not exceptional['H_finite_h_plus_k_zero'] and all(v==1 for _,v in exceptional['H_impossible_system_residuals']),'H_impossible_system',exceptional)
    require(set(exceptional['Ed_ezero'])=={(0,1),(0,p-1)} and not exceptional['Ed_tone_nonzero_e'],'Ed_denominator',exceptional)
    point_checks=[]
    for M in ('H','Ed'):
        transported=[]
        for P in W:
            Q=g.from_W(M,P);back=g.to_W(M,Q)
            ok=g.on_curve(M,Q) and back==P and g.to_W(M,g.neg(M,Q))==g.neg('W',P)
            point_checks.append({'model':M,'W_index':idx[P],'point':json_point(M,Q,p),'back_W':json_point('W',back,p),'pass':ok})
            require(ok,'map_point',point_checks[-1]);transported.append(Q)
        require(len(set(transported))==len(W) and set(transported)==set(points[M]),'map_full_coverage',M)
        for Q in points[M]:require(g.from_W(M,g.to_W(M,Q))==Q,'reverse_roundtrip',json_point(M,Q,p))
    cert['point_roundtrip_negation']=point_checks
    composition=[]
    for H in points['H']:
        intermediate=g.to_W('H',H);Ed=g.from_W('Ed',intermediate)
        backW=g.to_W('Ed',Ed);backH=g.from_W('H',backW)
        row={'H':json_point('H',H,p),'intermediate_W':json_point('W',intermediate,p),'Ed':json_point('Ed',Ed,p),'back_W':json_point('W',backW,p),'back_H':json_point('H',backH,p),'pass':backH==H}
        composition.append(row);require(row['pass'],'H_Ed_composition',row)
    cert['H_Ed_compositions']=composition
    intermediate=[]
    for P in W:
        if P is None or P==g.T:continue
        x,y=P;U=f.div(f.sub(x,r['r']),r['s']);V=f.div(y,r['s'])
        e,t=g.from_W('Ed',P);z=f.div(e,r['c'])
        M_ok=f.eq(f.mul(r['B'],f.power(V,2)),f.add(f.add(f.power(U,3),f.mul(r['A'],f.power(U,2))),U))
        twisted_ok=f.eq(f.add(f.mul(r['a'],f.power(z,2)),f.power(t,2)),f.add(1,f.mul(r['d_twisted'],f.mul(f.power(z,2),f.power(t,2)))))
        row={'W_index':idx[P],'U':U,'V':V,'z':z,'t':t,'M_pass':M_ok,'twisted_pass':twisted_ok}
        intermediate.append(row);require(M_ok and twisted_ok,'intermediate_curves',row)
    cert['M_twisted_intermediates']=intermediate
    table=[];pair_checks=[];ed_denominators=[]
    for i,P in enumerate(W):
        table.append([])
        for j,Q in enumerate(W):
            N=g.add_W(P,Q)
            require(N in idx and g.on_curve('W',N),'W_closure',[i,j,json_point('W',N,p)])
            table[i].append(idx[N]);g.m.tick('group_table_insertions')
            for M in ('H','Ed'):
                MP,MQ=g.from_W(M,P),g.from_W(M,Q)
                if M=='Ed':
                    product=f.mul(r['d_edwards'],f.mul(f.mul(MP[0],MQ[0]),f.mul(MP[1],MQ[1])))
                    plus,minus=f.add(1,product),f.sub(1,product)
                    erow={'P':i,'Q':j,'Dplus':plus,'Dminus':minus}
                    ed_denominators.append(erow)
                    require(not f.eq(f.mul(plus,minus),0),'Ed_complete_denominator',erow)
                elif MP is not None and MQ is not None:
                    D=f.sub(f.mul(MQ[0],MQ[1]),f.mul(MP[0],MP[1]))
                    require(not (N is None and not f.eq(D,0)),'H_D_nonzero_to_infinity',[i,j,D])
                native=g.add_native(M,MP,MQ);back=g.to_W(M,native)
                row={'model':M,'P':i,'Q':j,'sum_W':idx[N],'native_sum':json_point(M,native,p),'touches_O_or_T':P in (None,g.T) or Q in (None,g.T),'pass':back==N and g.on_curve(M,native)}
                pair_checks.append(row);require(row['pass'],'native_addition',row)
    cert['Ed_pair_denominators']=ed_denominators
    cert['full_group_pair_checks']=pair_checks;cert['W_addition_table']=table
    controls['C1_exact_transport']={'pass':True,'full_group_points':len(W),'ordered_pairs':len(W)**2,'certificate':'map-certificates.json'}
    eligible=[P for P in W if P not in (None,g.T)]
    require(len(eligible)>=6,'S_p_cardinality',eligible)
    chosen={None,g.T,*eligible[:6]}
    S=[i for i,P in enumerate(W) if P in chosen]
    require(len(S)==8,'S_p_unique',S)
    outside=next((i for i in range(len(W)) if i not in S),None)
    require(outside is not None,'C2_outside_point',S)
    bad=sorted((set(S)-{idx[None]})|{outside})
    diff=sorted(set(S)^set(bad))
    bad_transports=[]
    for M in ('H','Ed'):
        native_bad=[g.from_W(M,W[i]) for i in bad]
        recovered_bad=[idx[g.to_W(M,P)] for P in native_bad]
        bad_transports.append({'model':M,'native_points':[json_point(M,P,p) for P in native_bad],
            'recovered_W_indices':recovered_bad,'coordinate_only_accepted':recovered_bad==S,
            'same_cardinality':len(recovered_bad)==len(S)})
    controls['C2_mismatched_points']={'pass':len(bad)==8 and len(diff)==2 and all(x['same_cardinality'] and not x['coordinate_only_accepted'] for x in bad_transports),'S_indices':S,'S_bad_indices':bad,'symmetric_difference':diff,'transported_mutants':bad_transports,'coordinate_only_accepted':S==bad}
    require(controls['C2_mismatched_points']['pass'],'C2_mismatched_points',controls['C2_mismatched_points'])
    omissions=[]
    for M in ('H','Ed'):
        partial=[]
        for P in W:
            native=g.from_W(M,P)
            decoded=g.to_W(M,native)
            if decoded is not None:partial.append(idx[decoded])
        omissions.append({'model':M,'partial_decoded_W_indices':partial,
            'missing_W_indices':sorted(set(range(len(W)))-set(partial)),
            'accepted':len(partial)==len(W)})
    missing=omissions[0]['missing_W_indices']
    try:
        e,t=(0,p-1)
        U=f.div(f.add(1,t),f.sub(1,t));f.div(f.mul(r['c'],U),e)
        mutant_failure=None
    except ZeroDivisionError as exc:mutant_failure={'class':'undefined_map','message':str(exc),'Ed_point':[e,t]}
    controls['C3_map_exceptions']={'pass':missing==[0] and mutant_failure is not None,'omitted_identity_mutants':omissions,'ordinary_T_mutant':mutant_failure,'correct_OT_pair_checks':[x for x in pair_checks if x['touches_O_or_T']]}
    require(controls['C3_map_exceptions']['pass'],'C3_map_exceptions',controls['C3_map_exceptions'])
    H=(0,p-1);true=g.to_W('H',H);wrong=(f.add(true[0],1),true[1]);on=g.on_curve('W',wrong)
    try:roundtrip=g.from_W('H',wrong)==H
    except ZeroDivisionError:roundtrip=False
    controls['C4_wrong_map']={'pass':not on or not roundtrip,'H':H,'correct_W':true,'mutated_W':wrong,'on_curve':on,'roundtrip':roundtrip,'accepted':on and roundtrip}
    require(controls['C4_wrong_map']['pass'],'C4_wrong_map',controls['C4_wrong_map'])
    wrong_neg=[]
    for H in points['H']:
        P=g.to_W('H',H);sumP=g.add_W(P,g.to_W('H',H))
        wrong_neg.append({'H':json_point('H',H,p),'wrong_negation_sum':json_point('W',sumP,p),'fails':sumP is not None})
    controls['C5_wrong_negation']={'pass':any(x['fails'] for x in wrong_neg),'status':'detected' if any(x['fails'] for x in wrong_neg) else 'inconclusive','scan':wrong_neg}
    require(controls['C5_wrong_negation']['pass'],'C5_wrong_negation_inconclusive',wrong_neg)
    return W,idx,S,table


def density_audit(g,W,table,controls):
    p=g.p;values=list(range(p))+['infinity'];data={};adapted={}
    for name,n in (('WX',2),('Edt',2),('Hh',3),('Hs',2)):
        with g.m.phase('membership_density_'+name):
            coords=[g.coordinate(name,P) for P in W]
            fibers={str(t):[] for t in values}
            for i,t in enumerate(coords):fibers[str(t)].append(i);g.m.tick('fiber_table_lookups')
            full=[t for t in values if len(fibers[str(t)])==n]
            windows=[]
            for window in itertools.combinations(values,2):
                ids=[]
                for i,t in enumerate(coords):
                    g.m.tick('coordinate_window_comparisons',2)
                    if t in window:ids.append(i)
                windows.append({'window':list(window),'w':2,'B':len(ids),'point_indices':ids})
            fixed=[i for i,t in enumerate(coords) if t in (0,1)];adapted['A_'+name]=fixed
            full_ids=[i for i,t in enumerate(coords) if t in full]
            require(sum(len(v) for v in fibers.values())==len(W),'C6_histogram',name)
            require(sum(row['B'] for row in windows)==p*len(W),'C6_double_count',name)
            require(len(full_ids)==n*len(full),'C6_full_fiber',name)
            if name=='WX':require(bool(full) and len(full_ids)!=len(full),'C6_false_universal_density',{'full':full,'points':full_ids})
            all_windows=windows+[{'kind':'full_fiber','window':full,'w':len(full),'B':len(full_ids),'point_indices':full_ids}]
            transports=[]
            mu_values=[g.mu(t) for t in values]
            require(len(set(mu_values))==p+1,'C7_projective_bijection',mu_values)
            for window_row in all_windows:
                window=window_row['window'];A=window_row['point_indices'];mu_window=[g.mu(t) for t in window]
                for k in (0,1,2):
                    lifted=[]
                    for slot in (0,1):
                        ids=[]
                        for i,t in enumerate(coords):
                            mapped=g.mu(t) if slot<k else t
                            target_window=mu_window if slot<k else window
                            g.m.tick('PGL2_window_membership_comparisons',len(target_window))
                            if mapped in target_window:ids.append(i)
                        lifted.append(ids)
                    expected=defaultdict(list);observed=defaultdict(list)
                    for i,j in itertools.product(A,repeat=2):
                        expected[table[i][j]].append([i,j]);g.m.tick('PGL2_baseline_group_table_lookups')
                    for i,j in itertools.product(*lifted):
                        observed[table[i][j]].append([i,j]);g.m.tick('PGL2_transported_group_table_lookups')
                    ok=lifted==[A,A] and dict(expected)==dict(observed)
                    row={'window':window,'mu_window':mu_window,'k':k,'slot_point_indices':lifted,'per_sum_counts':[len(observed[t]) for t in range(len(W))],
                        'canonical_relation_hash':digest([observed[t] for t in range(len(W))]),'pass':ok}
                    transports.append(row);require(ok,'C7_count_transport',row)
            collisions=defaultdict(list)
            for i,j in itertools.product(range(len(W)),repeat=2):
                collisions[encode([coords[i],coords[j]]).decode().strip()].append([i,j])
                g.m.tick('coordinate_pair_collision_table_lookups')
            data[name]={'coordinate_values':coords,'geometric_coordinate_degree_label':n,
                'coordinate_expression':{'WX':'X; O -> infinity','Edt':'(X-r-s)/(X-r+s); O -> 1; T -> -1','Hh':'(-36-Y)/(6X); O -> infinity','Hs':'-12/X; O -> 0'}[name],
                'mu_expression':'(f+1)/(f+2); infinity->1; -2->infinity',
                'direct_membership_algorithm':'Evaluate declared rational coordinate including exceptions, then compare to every serialized window value; discovery, maps, evaluations and tables charged.',
                'histogram':[{'value':t,'n_f':len(fibers[str(t)]),'point_indices':fibers[str(t)]} for t in values],
                'size_two_windows':windows,'mean_B_exact':{'numerator':2*len(W),'denominator':p+1},
                'full_fiber_window':{'values':full,'w':len(full),'B':len(full_ids),'point_indices':full_ids,'empty':not full,'density':n if full else None},
                'fixed_window':{'values':[0,1],'w':2,'B':len(fixed),'point_indices':fixed,'empty':not fixed},
                'PGL2_transports':transports,
                'lossy_coordinate_pair_collisions':[{'coordinate_pair':json.loads(k),'canonical_pairs':v} for k,v in collisions.items() if len(v)>1],
                'conditional_proxy':{'status':'conditional_historical_proxy_not_measured_degree_or_Bezout',
                    'assumed_d_rel':9 if n==3 else 2,'fixed_window_Phi':(9 if n==3 else 2)*4,
                    'full_window_applicable':bool(full),'full_window_Phi':(9 if n==3 else 2)*len(full)**2 if full else None,
                    'full_fiber_assumption':'B=n*w by explicit selection, never an unrestricted-window theorem'}}
    controls['C6_rational_density']={'pass':True,'certificate':'raw-results.json:density_audit','false_universal_B_equals_w_rejected_for_nonempty_WX_full_window':True}
    controls['C7_PGL2_count_transport']={'pass':True,'certificate':'raw-results.json:density_audit','slots':[0,1,2],'windows':'every size-two window and each full-fiber window'}
    return data,adapted


def active_branches(spec,model,N,O_in_A):
    chosen=[]
    for branch in spec['polynomial_protocol'][model+'_branches']:
        name=branch['name']
        if model=='Ed':chosen.append(branch);continue
        if N is None:
            if name in ('finite_inverse','finite_Dzero_Winverse'):chosen.append(branch)
            if name=='both_identity' and O_in_A:chosen.append(branch)
        else:
            if name.startswith('finite') and name not in ('finite_inverse','finite_Dzero_Winverse'):chosen.append(branch)
            if name in ('left_identity','right_identity') and O_in_A:chosen.append(branch)
    return chosen


def build_system(g,spec,model,branch,N,A):
    f=g.f;v=branch['variables'];name=branch['name'];polys=[];slots=[]
    constants=dict(g.row)
    if N is not None:constants.update(XN=N[0],YN=N[1])
    native=g.from_W(model,N)
    if native is not None:
        if model=='H':constants.update(hN=native[0],kN=native[1])
        if model=='Ed':constants.update(eN=native[0],tN=native[1])
    def add(poly,category,formula):
        polys.append(poly);slots.append(poly.descriptor(category,formula))
    def formula(expr,category):add(expression(expr,f,v,constants),category,expr)
    point_vars={'W':('X','Y'),'H':('h','k'),'Ed':('e','t')}[model]
    native_A=[g.from_W(model,P) for P in A]
    affine=[P for P in native_A if P is not None]
    for i in (1,2):
        x,y=(s+str(i) for s in point_vars)
        if x not in v:continue
        curve={'W':f'{y}^2-{x}^3+432=0','H':f'{x}^3+{y}^3+1=0','Ed':f'{x}^2+{y}^2-1-d_edwards*{x}^2*{y}^2=0'}[model]
        formula(curve,'curve')
        add(membership(f,v,x,y,affine),'membership',f'I_A({x},{y})-1=0')
    for z in v:formula(f'{z}^{g.p}-{z}=0','field')
    if model=='Ed':
        constants['Dplus']=expression('1+d_edwards*e1*e2*t1*t2',f,v,constants)
        constants['Dminus']=expression('1-d_edwards*e1*e2*t1*t2',f,v,constants)
    if model=='H' and name.startswith('finite'):
        constants['D']=expression('h2*k2-h1*k1',f,v,constants)
    extra=branch['extra_equations']
    if isinstance(extra,str):
        generic=next(b for b in spec['polynomial_protocol']['H_branches'] if b['name']=='finite_Dzero_Wgeneric')
        which='finite_tangent' if name.endswith('Wtangent') else 'finite_inverse'
        wb=next(b for b in spec['polynomial_protocol']['W_branches'] if b['name']==which)
        extra=generic['extra_equations'][:-4]+wb['extra_equations']
    for j,expr in enumerate(extra):
        category='native_relation'
        if model=='H' and name.startswith('finite_Dzero'):
            category='fallback_graph' if j<9 else 'fallback_W_relation'
        formula(expr,category)
    require(len(v)==branch['raw_variable_count'] and len(slots)==branch['raw_equation_count'],'frozen_slot_counts',{'model':model,'branch':name,'variables':len(v),'slots':len(slots)})
    descriptor={'model':model,'branch':name,'guard':branch['guard'],'variables':v,
        'raw_variable_count':len(v),'raw_equation_count':len(slots),'raw_slots':slots,
        'normalized_nonzero_polynomials':[{'slot':i,'terms':slot['normalized_terms']} for i,slot in enumerate(slots) if not slot['is_zero']],
        'zero_slot_indices':[i for i,slot in enumerate(slots) if slot['is_zero']],
        'membership_affine_points':[list(P) for P in affine],'infinity_in_A':None in native_A,
        'leading_coefficient_convention':'greatest exponent vector in declared lex order; terms serialized ascending',
        'normalization':'scalar division only; no factor, exponent, duplicate, or zero-slot deletion'}
    return polys,descriptor


def candidate_assignment(g,model,branch,P,Q,N):
    """Eliminate only uniquely defined auxiliaries, then test every equation.

    No lookup of the true sum or target-relation truth is permitted here.
    Membership/curve equations restrict point variables to the enumerated A;
    each auxiliary has a displayed nonzero linear coefficient, checked over Fp.
    This is finite recovery, not polynomial simplification or a Groebner solve.
    """
    f=g.f;name=branch['name'];v=branch['variables'];a={};uniqueness=[]
    MP,MQ=g.from_W(model,P),g.from_W(model,Q)
    if model!='Ed':
        if name=='both_identity':return ({},[]) if P is None and Q is None else None
        if name=='left_identity':
            if P is not None or Q is None:return None
        elif name=='right_identity':
            if Q is not None or P is None:return None
        elif P is None or Q is None:return None
    prefixes={'W':('X','Y'),'H':('h','k'),'Ed':('e','t')}[model]
    for slot,T in ((1,MP),(2,MQ)):
        if T is not None:
            for key,value in zip(prefixes,T):
                if key+str(slot) in v:a[key+str(slot)]=value
    def unique_linear(var,coef,rhs):
        roots=[]
        for x in range(g.p):
            if f.eq(f.mul(coef,x),rhs):roots.append(x)
        require(len(roots)==1,'auxiliary_uniqueness',{'variable':var,'coefficient':coef,'rhs':rhs,'roots':roots})
        a[var]=roots[0]
        uniqueness.append({'variable':var,'coefficient':coef,'rhs':rhs,'roots':roots,'candidates_tested':g.p})
    if name in ('left_identity','right_identity'):return a,uniqueness
    if model=='Ed':
        e,t=MP;ee,tt=MQ
        product=f.mul(g.row['d_edwards'],f.mul(f.mul(e,ee),f.mul(t,tt)))
        unique_linear('zplus',f.add(1,product),1)
        unique_linear('zminus',f.sub(1,product),1)
        return a,uniqueness
    if model=='H':
        h,k=MP;hh,kk=MQ;D=f.sub(f.mul(hh,kk),f.mul(h,k))
        if name=='finite_native':
            if f.eq(D,0):return None
            unique_linear('z',D,1)
            return a,uniqueness
        if not f.eq(D,0):return None
        # Recover map variables from native inputs instead of copying W values.
        for slot,T in ((1,MP),(2,MQ)):
            h,k=T;den=f.add(h,k)
            unique_linear('zmap'+str(slot),den,1)
            mapped=g.to_W('H',T)
            a['X'+str(slot)],a['Y'+str(slot)]=mapped
        P=(a['X1'],a['Y1']);Q=(a['X2'],a['Y2'])
    x,y=P;xx,yy=Q
    if name.endswith('inverse'):return a,uniqueness
    if name.endswith('generic'):
        if f.eq(x,xx):return None
        denom=f.sub(xx,x)
        unique_linear('lambda',denom,f.sub(yy,y));unique_linear('z',denom,1)
    elif name.endswith('tangent'):
        if P!=Q or f.eq(y,0):return None
        denom=f.mul(2,y)
        unique_linear('lambda',denom,f.mul(3,f.power(x,2)));unique_linear('z',denom,1)
    else:raise ValueError(name)
    require(set(a)==set(v),'assignment_variable_set',{'branch':name,'got':list(a),'expected':v})
    return a,uniqueness


def recover_pair(g,model,branch,assignment):
    name=branch['name']
    if name=='both_identity':return None,None
    pairs=[];prefixes={'W':('X','Y'),'H':('h','k'),'Ed':('e','t')}[model]
    for slot in (1,2):
        x,y=(prefix+str(slot) for prefix in prefixes)
        if x not in assignment:pairs.append(None)
        else:pairs.append(g.to_W(model,(assignment[x],assignment[y])))
    g.m.tick('canonical_pair_decodings')
    return tuple(pairs)


def descriptor_metrics(descriptors):
    slots=[s for d in descriptors for s in d['raw_slots']]
    nonzero=[s for s in slots if not s['is_zero']]
    categories={}
    for category in sorted({s['category'] for s in slots}):
        sub=[s for s in slots if s['category']==category];nz=[s for s in sub if not s['is_zero']]
        categories[category]={'raw_slots':len(sub),'nonzero_equations':len(nz),
            'zero_equations':len(sub)-len(nz),'monomials_with_multiplicity':sum(len(s['normalized_terms']) for s in nz),
            'maximum_total_degree':max((s['total_degree'] for s in nz),default=0)}
    return {'vector':[max((d['raw_variable_count'] for d in descriptors),default=0),len(slots),
                       max((s['total_degree'] for s in nonzero),default=0),
                       sum(len(s['normalized_terms']) for s in nonzero)],
        'vector_names':['maximum_branch_variables','total_raw_equation_slots','maximum_total_degree','total_nonzero_monomials_with_multiplicity'],
        'raw_branch_count':len(descriptors),'zero_equation_count':len(slots)-len(nonzero),
        'nonzero_equation_count':len(nonzero),'categories':categories,
        'per_variable_degree_histogram':dict(sorted(Counter(str(d) for s in nonzero for d in s['per_variable_degree']).items())),
        'maximum_per_variable_degree':max((d for s in nonzero for d in s['per_variable_degree']),default=0),
        'serialized_system_bytes':len(encode(descriptors)),
        'serialized_branch_metadata_bytes':sum(len(encode({k:v for k,v in d.items() if k not in ('raw_slots','normalized_nonzero_polynomials')})) for d in descriptors),
        'outside_scope':OUTSIDE}


def canonical_rename_reserialize(descriptor):
    renamed=json.loads(encode(descriptor))
    # A bijection on declared variable names; exponent positions do not move.
    names=renamed['variables'];rename={v:'identity_control_'+v for v in names}
    renamed['variables']=[rename[v] for v in names]
    inverse={v:k for k,v in rename.items()}
    renamed=json.loads(encode(renamed))
    renamed['variables']=[inverse[v] for v in renamed['variables']]
    return renamed


def relation_systems(g,spec,W,idx,sets,table,systems,certificates,controls):
    metrics={};all_c0=[];all_c8=[];membership_checks=[]
    for arm,ids in sets.items():
        A=[W[i] for i in ids]
        with g.m.phase('baseline_pair_enumeration_'+arm):
            baseline={i:[] for i in range(len(W))}
            attempts=0
            for i,j in itertools.product(ids,repeat=2):
                N=g.add_W(W[i],W[j]);attempts+=1
                R=g.neg('W',N);baseline[idx[R]].append([i,j])
            require(attempts==len(A)**2,'baseline_exact_B_squared',{'arm':arm,'attempts':attempts,'B':len(A)})
            # C8 uses full-group deterministic labels and table lookup.
            label_baseline={i:[] for i in range(len(W))}
            for i,j in itertools.product(ids,repeat=2):
                g.m.tick('C8_label_group_table_lookups')
                label_baseline[idx[g.neg('W',W[table[i][j]])]].append([i,j])
            row={'arm':arm,'B':len(A),'pair_addition_attempts':attempts,
                'same_relations_after_label_decoding':baseline==label_baseline}
            all_c8.append(row);require(row['same_relations_after_label_decoding'],'C8_generic_relation_baselines',row)
        metrics[arm]={}
        for model in ('W','Ed','H'):
            with g.m.phase('membership_validation_'+arm+'_'+model):
                native_A=[g.from_W(model,P) for P in A]
                affine=[P for P in native_A if P is not None]
                member=membership(g.f,['u','v'],'u','v',affine)
                checked=0;errors=[]
                for u,v in itertools.product(range(g.p),repeat=2):
                    g.m.tick('membership_evaluations')
                    actual=member.evaluate({'u':u,'v':v})==0
                    expected=(u,v) in affine
                    checked+=1
                    if actual!=expected:errors.append({'point':[u,v],'actual':actual,'expected':expected})
                mrow={'arm':arm,'model':model,'affine_grid_checks':checked,'errors':errors,
                    'affine_points':[list(P) for P in affine],'infinity_member':None in native_A,
                    'exact_point_indices':[idx[g.to_W(model,P)] for P in native_A]}
                membership_checks.append(mrow);require(not errors and mrow['exact_point_indices']==ids,'membership_exact',mrow)
            with g.m.phase('finite_systems_'+arm+'_'+model):
                key=arm+':'+model;systems[key]=[];certificates[key]=[]
                for R_index,R in enumerate(W):
                    N=g.neg('W',R);recovered=[];accepted=[];truth_table=[]
                    branches=active_branches(spec,model,N,None in A)
                    runtime=[]
                    for branch in branches:
                        polys,desc=build_system(g,spec,model,branch,N,A)
                        desc.update(arm=arm,B=len(A),R_index=R_index,N_W=json_point('W',N,g.p))
                        systems[key].append(desc);runtime.append((branch,polys,desc))
                        if model=='W':
                            copied=canonical_rename_reserialize(desc)
                            ok=encode(copied)==encode(desc) and descriptor_metrics([copied])==descriptor_metrics([desc])
                            all_c0.append({'arm':arm,'R_index':R_index,'branch':branch['name'],'pass':ok,'descriptor_sha256':digest(desc),'reserialized_sha256':digest(copied)})
                            require(ok,'C0_W_identity',all_c0[-1])
                    for i,j in itertools.product(ids,repeat=2):
                        branch_results=[];pair_solutions=[]
                        for branch,polys,desc in runtime:
                            candidate=candidate_assignment(g,model,branch,W[i],W[j],N)
                            if candidate is None:
                                branch_results.append({'branch':branch['name'],'admitted_by_guard':False})
                                continue
                            assignment,unique=candidate
                            require(set(assignment)==set(branch['variables']),'assignment_complete',{'branch':branch['name'],'assignment':assignment})
                            values=[]
                            for poly,slot in zip(polys,desc['raw_slots']):
                                if slot['category']=='membership':g.m.tick('membership_evaluations')
                                values.append(poly.evaluate(assignment))
                            ok=all(value==0 for value in values)
                            branch_results.append({'branch':branch['name'],'admitted_by_guard':True,'equation_residuals':values,'accepted':ok})
                            if ok:
                                decoded=recover_pair(g,model,branch,assignment)
                                require(all(P in idx for P in decoded),'recovery_on_group',decoded)
                                decoded_ids=[idx[P] for P in decoded]
                                require(decoded_ids==[i,j],'recovery_identity',{'expected':[i,j],'actual':decoded_ids})
                                pair_solutions.append(decoded_ids)
                                accepted.append({'P':i,'Q':j,'branch':branch['name'],'assignment':assignment,
                                    'unique_auxiliary_constraints':unique,'decoded_pair':decoded_ids,
                                    'equation_residuals':values})
                        truth_table.append({'P':i,'Q':j,'branch_tests':branch_results,'accepted_count':len(pair_solutions)})
                        recovered.extend(pair_solutions)
                    observed=sorted(recovered);expected=sorted(baseline[R_index]);g.m.tick('canonical_relation_sort_operations',2)
                    oc,ec=Counter(map(tuple,observed)),Counter(map(tuple,expected))
                    missing=list((ec-oc).elements());spurious=list((oc-ec).elements());duplicates=sum(n-1 for n in oc.values() if n>1)
                    row={'arm':arm,'model':model,'R_index':R_index,'target_R':json_point('W',R,g.p),'B':len(A),
                        'truth_table_cells':len(truth_table),'truth_table':truth_table,'solutions':accepted,
                        'expected_ordered_pairs':expected,'recovered_ordered_pairs':observed,
                        'expected_certificate_sha256':digest(expected),'recovered_certificate_sha256':digest(observed),
                        'missing':missing,'spurious':spurious,'duplicate_count':duplicates,
                        'complete_recovery_basis':'All p^2 affine membership values checked. Enumerate each admitted A pair. Field equations retain all variables; each auxiliary is unique from the serialized linear/inverse constraints checked over Fp. Evaluate every raw slot, retain target-inconsistent pairs as rejected rows. No true-sum filter enters candidate recovery.'}
                    certificates[key].append(row)
                    require(not missing and not spurious and duplicates==0,'relation_correspondence',{'arm':arm,'model':model,'R':R_index,'missing':missing,'spurious':spurious,'duplicates':duplicates})
                metrics[arm][model]=descriptor_metrics(systems[key])
    controls['C0_W_identity']={'pass':True,'checks':all_c0,'relation_list_check':'All W decoded ordered pairs compared to direct addition for every target; descriptors rebuilt through canonical name transport.'}
    controls['C8_generic_relation_baselines']={'pass':True,'checks':all_c8}
    controls['exact_membership']={'pass':True,'checks':membership_checks}
    # Comparisons are withheld until every instrument/control gate above passed.
    comparison={}
    for arm,models in metrics.items():
        baseline=models['W']['vector'];comparison[arm]={}
        for model in ('Ed','H'):
            vector=models[model]['vector'];delta=[a-b for a,b in zip(vector,baseline)]
            comparison[arm][model]={'same_point_indices':sets[arm],'B':len(sets[arm]),
                'matched_W_vector':baseline,'native_vector':vector,'native_minus_W':delta,
                'any_strict_integer_decrease':bool(sets[arm]) and any(x<=-1 for x in delta),
                'Pareto_predicate':bool(sets[arm]) and all(x<=0 for x in delta) and any(x<0 for x in delta),
                'empty_arm':not sets[arm],'positive_simplification_eligible':bool(sets[arm]),
                'status':'observed_predicate_only_not_hypothesis_status'}
    return metrics,comparison


def mechanical_check():
    """Synthetic arithmetic/serialization only, never instantiates Geometry."""
    m=Meter();f=Field(5,m);v=['u','v']
    p=expression('(u+2*v)^2-u^2-4*u*v',f,v,{})
    require(p.terms_list()==[[4,[0,2]]],'synthetic_expansion',p.terms_list())
    require(p.normalized().terms_list()==[[1,[0,2]]],'synthetic_normalization',p.normalized().terms_list())
    for u,w in itertools.product(range(5),repeat=2):
        require(p.evaluate({'u':u,'v':w})==(4*w*w)%5,'synthetic_evaluation',[u,w])
    member=membership(f,v,'u','v',[(1,2),(3,4)])
    for u,w in itertools.product(range(5),repeat=2):
        require((member.evaluate({'u':u,'v':w})==0)==((u,w) in ((1,2),(3,4))),'synthetic_membership',[u,w])
    alias=expression('lambda*u-lambda*u',f,['lambda','u'],{})
    require(not alias.terms,'synthetic_keyword_variable',{})
    zero=expression('u-u',f,v,{})
    require(zero.descriptor('synthetic','u-u')['is_zero'],'synthetic_zero_slot',{})
    fixture={'variables':v,'raw_slots':[p.descriptor('synthetic','4*v^2'),zero.descriptor('synthetic','u-u')],
        'raw_variable_count':2,'raw_equation_count':2}
    require(canonical_rename_reserialize(fixture)==fixture,'synthetic_roundtrip',{})
    try:expression('__import__("os")',f,v,{})
    except ValueError:pass
    else:raise GateFailure('synthetic_parser_rejection',{})
    return {'status':'passed','scientific_runs':0,'curve_enumerations':0,'scientific_map_calls':0,
        'fixture_field':5,'fixture_kind':'arbitrary_affine_grid_not_curve',
        'checks':['sparse_expansion','leading_scalar_normalization','term_evaluation_25_assignments',
            'exact_membership_25_assignments','keyword_variable_preservation','zero_slot_preservation','JSON_identity_rename_roundtrip','formula_parser_rejects_calls'],
        'limitations':'Mechanical checks establish no availability, map correctness, branch correspondence, scientific validity, or lock readiness.'}


def read_frozen_spec(path):
    data=Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest()!=SPEC_SHA256:
        raise ValueError('specification bytes differ from the frozen implementation authority')
    spec=json.loads(data)['experiment']
    if spec['id']!=EXPERIMENT or spec['version']!=1:
        raise ValueError('wrong experiment/version')
    return spec


def mechanical_schema_check(spec):
    """Pure syntax/count metadata checks; does not evaluate field constants."""
    checked=[]
    for model in ('W','Ed','H'):
        branches=spec['polynomial_protocol'][model+'_branches']
        for branch in branches:
            require(len(branch['variables'])==branch['raw_variable_count'],'declared_variable_schema',branch['name'])
            formulas=branch['extra_equations']
            if isinstance(formulas,list):
                for formula in formulas:
                    ast.parse(formula_python_syntax(formula),mode='eval')
            checked.append({'model':model,'branch':branch['name'],'variables':branch['raw_variable_count'],'raw_slots':branch['raw_equation_count']})
    require(len(checked)==14,'branch_schema_count',checked)
    require(len(spec['execution_plan']['run_bindings'])==2,'run_reservation_schema',{})
    return {'status':'passed','kind':'syntax_and_declared_schema_only','branches':checked,'scientific_runs':0}


def finite_payload(spec,cell,payload):
    """Complete scientific instrument body, deliberately uninvoked in this task.

    An approved integration must supply immutable artifact ownership, verified
    LOCKED runner context and a terminal manifest adapter before calling this.
    Partial dictionaries are caller-owned so failure preserves the last object.
    """
    rows=[r for r in spec['inputs']['constants'] if r['cell']==cell]
    require(len(rows)==1,'cell_binding',cell)
    meter=Meter();payload['meter']=meter
    g=Geometry(rows[0],meter)
    started=utc();wall=time.perf_counter();cpu=time.process_time()
    payload.update(started_at=started,cell=cell,experiment_id=EXPERIMENT,
        specification_sha256=SPEC_SHA256,status='running',scoring_status='withheld_until_all_gates_pass',
        maps={},controls={},systems={},certificates={},raw={})
    try:
        with meter.phase('stage_0_parameter_point_map_control_gate'):
            W,idx,S,table=availability(g,payload['maps'],payload['controls'])
        # C6/C7 known-false checks precede structural comparison, while their
        # tables are retained as the stage-2 membership audit output.
        with meter.phase('stage_0_C6_C7_pre_scoring_gate_and_stage_2_audit'):
            density,adapted=density_audit(g,W,table,payload['controls'])
            payload['raw']['density_audit']=density
        sets={'S_p':S,**adapted}
        payload['raw']['point_sets']={name:{'canonical_W_indices':ids,'B':len(ids),
            'canonical_points':[json_point('W',W[i],g.p) for i in ids],
            'empty':not ids} for name,ids in sets.items()}
        with meter.phase('stage_1_complete_finite_relations'):
            metrics,comparison=relation_systems(g,spec,W,idx,sets,table,payload['systems'],payload['certificates'],payload['controls'])
        required={c['id'] for c in spec['controls']}
        require(required<=set(payload['controls']) and all(payload['controls'][k].get('pass') is True for k in required),'all_registered_controls',payload['controls'])
        payload['raw'].update(metrics=metrics,matched_comparisons=comparison,
            comparison_scope='Compare each model only to W on exactly the same canonical point list; across f density only unless lists coincide.',
            identical_point_set_pairs=[[a,b] for a,b in itertools.combinations(sets,2) if sets[a]==sets[b]],
            conditional_historical_proxy_resolution={
                'status':'preregistered_conditional_arithmetic_not_measured_geometry',
                'full_fiber_assumptions':{'d_rel_labels':[2,9],'w_labels':['B/2','B/3'],'Phi3_over_Phi2':{'numerator':2,'denominator':1}},
                'equal_w_assumptions':{'d_rel_labels':[2,9],'Phi3_over_Phi2':{'numerator':9,'denominator':2}},
                'unrestricted_n2_over_full_fiber_n2':{'numerator':4,'denominator':1},
                'not_Bezout':spec['membership_convention_audit']['not_bezout'],
                'applicability':'Per-coordinate full-fiber rows above are inapplicable when their enumerated window is empty.'},
            outside_scope=OUTSIDE,scale_relevance=spec['scale_relevance'],
            preregistered_prediction=spec['preregistered_prediction'],
            inference='Observations and frozen comparison predicates only; independent review and Coordinator interpretation pending.',
            sample_accounting={'W_affine_candidates':g.p**2,'H_affine_candidates':g.p**2,'H_infinity_candidates':g.p+1,
                'Ed_affine_candidates':g.p**2,'full_group_points':len(W),'full_group_ordered_pairs':len(W)**2,
                'coordinate_histogram_entries_each':g.p+1,'size_two_windows_each':g.p*(g.p+1)//2,
                'coordinate_only_truth_cells_each_model':64*len(W),
                'adapted_truth_cells_each_model':{k:len(v)**2*len(W) for k,v in adapted.items()},'random_seeds':[],
                'extension_field_operations':0,'scientific_parameter_cells_in_this_call':1})
        payload['status']='completed_valid';payload['scoring_status']='all_gates_passed'
    except GateFailure as exc:
        payload['status']='completed_invalid';payload['failure']={'class':'invalid_measurement','gate':exc.gate,'object':exc.evidence}
        raise
    except (MemoryError,TimeoutError) as exc:
        payload['status']='resource_exhaustion';payload['failure']={'class':'resource_exhaustion','message':str(exc)}
        raise
    except BaseException as exc:
        payload['status']='failed_implementation';payload['failure']={'class':'implementation_error','exception':type(exc).__name__,'message':str(exc)}
        raise
    finally:
        payload['ended_at']=utc();payload['wall_seconds']=time.perf_counter()-wall
        payload['process_cpu_seconds']=time.process_time()-cpu;payload['peak_rss_bytes']=meter.rss()
        payload['costs']={'measurement_labels':{'phases':'measured process timing and cumulative peak RSS',
            'instrumented_operations':'counted calls/primitives in this implementation, including arithmetic used by controls',
            'modeled_term_evaluation_operations':'frozen term-by-term convention; excludes interpreter overhead'},
            'phases':meter.phases,'instrumented_operations':dict(meter.counts),'modeled_term_evaluation_operations':dict(meter.modeled),
            'integer_bit_length_histogram':dict(sorted(meter.integer_bits.items())),
            'integer_histogram_boundary':'Inputs to modular reduction; Python interpreter bookkeeping and internal pow(a,-1,p) integers are not instrumented.',
            'total_wall_seconds':payload['wall_seconds'],'total_process_cpu_seconds':payload['process_cpu_seconds'],
            'peak_rss_bytes':payload['peak_rss_bytes'],'extension_field_operations':0,
            'independent_validation':{'status':'not_performed_by_producer','cost':None},
            'attack_baselines':spec['cost_model']['attack_baselines'],
            'optimistic_assumptions':spec['cost_model']['optimistic_assumptions']}


def write_new(path,data):
    """Exclusive write; never replace a result, partial file, or symlink."""
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    if hasattr(os,'O_NOFOLLOW'):flags|=os.O_NOFOLLOW
    fd=os.open(path,flags,0o644)
    with os.fdopen(fd,'wb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())


def scientific_artifact_data(payload):
    """Pure serialization map for the seven instrument-owned output files.

    stdout/stderr/manifest and lifecycle ownership belong to the repository
    runner adapter; this function does not invent their schema or approval.
    """
    raw={**payload.get('raw',{}),'cell':payload.get('cell'),'experiment_id':EXPERIMENT,
        'terminal_status':payload.get('status'),'scoring_status':payload.get('scoring_status'),
        'failure':payload.get('failure'),'started_at':payload.get('started_at'),'ended_at':payload.get('ended_at'),
        'specification_sha256':SPEC_SHA256}
    objects={'raw-results.json':raw,'map-certificates.json':payload.get('maps',{}),
        'relation-certificates.json':payload.get('certificates',{}),
        'polynomial-systems.json':payload.get('systems',{}),'control-results.json':payload.get('controls',{})}
    result={name:encode(obj) for name,obj in objects.items()}
    costs=dict(payload.get('costs',{}))
    costs['serialized_bytes']={name:len(data) for name,data in result.items()}
    costs['serialized_size_scope']='UTF-8 JSON including terminal newline. Costs and report are self-describing overhead; final all-artifact bytes/hash table belongs to runner manifest.'
    result['costs.json']=encode(costs)
    lines=[f'# {EXPERIMENT} execution report', '',
        f"Cell: {payload.get('cell')}; terminal status: {payload.get('status')}.",
        f"Scoring status: {payload.get('scoring_status')}.",
        f"Specification SHA-256: {SPEC_SHA256}.",'',
        'The machine-readable artifacts retain all evaluated points, exceptions, controls, systems,',
        'ordered-pair certificates and costs. Failure objects are retained in raw-results.json.',
        'Structural predicates are observations under the frozen toy diagnostic. No hypothesis',
        'status, geometric summation degree, DLP speedup, or exponent improvement is asserted.', '',
        f"Failure object: {json.dumps(payload.get('failure'),sort_keys=True)}",'',
        'Independent Validator and Red Team review remain separate requirements.', '']
    result['execution-report.md']='\n'.join(lines).encode()
    return result


def emit_scientific_artifacts(run_dir,payload):
    """Called only inside the future approved adapter's owned new directory."""
    target=Path(run_dir)
    if not target.is_dir() or target.is_symlink():
        raise ValueError('runner must exclusively create the reserved run directory')
    data=scientific_artifact_data(payload)
    for name in data:
        if (target/name).exists() or (target/name).is_symlink():
            raise FileExistsError(target/name)
    for name,value in data.items():write_new(target/name,value)
    return {name:{'sha256':hashlib.sha256(value).hexdigest(),'bytes':len(value)} for name,value in data.items()}


RUNNER_INTEGRATION_PREREQUISITES = (
    'A separately published scientific authorization and actual verified LOCKED plan are required.',
    'The current repository LOCKED runner and immutable YAML manifest wrapper must be reconciled with this frozen specification.yaml, exact hexadecimal RUN reservations, and manifest.yaml output contract.',
    'The approved adapter must bind exact argv/specification/source/environment/lock hashes, actual inference and Git provenance, exclusive run-directory ownership, stdout/stderr, terminal manifest and all artifact hashes.',
    'The approved adapter must enforce the 8 GiB process protection and 1800-second nontermination watchdog, preserve partial payloads and classify operational failures.',
)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',default=SPEC_PATH)
    parser.add_argument('--cell',choices=('p11','p23'))
    parser.add_argument('--run-dir')
    parser.add_argument('--mechanical-check',action='store_true',help='Syntax/schema and F5 non-curve fixtures only; no scientific execution')
    args=parser.parse_args(argv)
    if args.spec!=SPEC_PATH:
        parser.error('the exact frozen repository-relative specification path is required')
    spec=read_frozen_spec(args.spec)
    if args.mechanical_check:
        if args.cell is not None or args.run_dir is not None:
            parser.error('mechanical checks cannot be combined with a scientific cell/run directory')
        result={'mechanical':mechanical_check(),'schema':mechanical_schema_check(spec)}
        # Pure serializer fixture, without creating any output directory/file.
        fixture={'cell':'synthetic_noncurve_fixture','status':'not_executed','scoring_status':'not_evaluated','raw':{'fixture':True}}
        blobs=scientific_artifact_data(fixture)
        expected={'raw-results.json','map-certificates.json','relation-certificates.json','polynomial-systems.json','control-results.json','costs.json','execution-report.md'}
        require(set(blobs)==expected,'synthetic_artifact_schema',list(blobs))
        for name,data in blobs.items():
            if name.endswith('.json'):json.loads(data)
        result['synthetic_artifact_schema']={'status':'passed','files_written':0,'scientific_runs':0,'artifact_names':sorted(blobs)}
        print(json.dumps(result,sort_keys=True,indent=2))
        return 0
    if args.cell is None or args.run_dir is None:
        parser.error('supply --mechanical-check or both --cell and --run-dir')
    binding=next(r for r in spec['execution_plan']['run_bindings'] if r['cell']==args.cell)
    if args.run_dir!=binding['run_directory']:
        parser.error('cell/run-directory differs from the frozen exact reservation')
    path=Path(args.run_dir)
    if path.exists() or path.is_symlink():
        parser.error('existing output path is forbidden; retain it and use an additive authorized attempt')
    # Fail closed. A caller-controlled environment flag or invented lock JSON
    # is never treated as evidence of repository-runner approval. A separately
    # archived integration repair must wire the official verified runner here.
    print(json.dumps({'status':'not_executed','failure_class':'infrastructure_error',
        'reason':'locked_runner_integration_unresolved','experiment_id':EXPERIMENT,
        'cell':args.cell,'run_id':binding['run_id'],'scientific_runs':0,
        'prerequisites':RUNNER_INTEGRATION_PREREQUISITES},sort_keys=True),file=sys.stderr)
    return 2


if __name__=='__main__':
    raise SystemExit(main())
