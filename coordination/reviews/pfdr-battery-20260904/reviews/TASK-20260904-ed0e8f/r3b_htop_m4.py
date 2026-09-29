#!/usr/bin/env python3
"""R3b: m = 4 H-TOP, with pairwise-distinct specialisation constants, and with
x_R (then a, b) kept symbolic so that 'c is a constant, not a polynomial that
can vanish' is tested rather than sampled."""
import json, random, sys, sympy as sp
sys.path.insert(0,'.')
from r3_htop_m4 import S3, S4, S5, t

def run():
    rng=random.Random(20260904)
    out={"m4_numeric":[], "m4_xR_symbolic":[], "m4_ab_symbolic":[], "degenerate_note":[]}
    for _ in range(6):
        c=rng.sample(range(2,40),4)          # pairwise distinct
        a,b,xR=(rng.randrange(1,500) for _ in range(3))
        poly=sp.Poly(S5(c[0]*t,c[1]*t,c[2]*t,c[3]*t,xR,a,b),t)
        d=int(poly.degree()); lead=int(poly.LC())
        den=c[0]**8*c[1]**8*c[2]**8*c[3]**8
        out["m4_numeric"].append({"c":c,"a":a,"b":b,"x_R":xR,"deg_t":d,
            "coeff_8888": str(sp.Rational(lead,den)) if d==32 else None})
    # x_R symbolic
    X=sp.Symbol('xR')
    c=[3,5,7,11]; a,b=17,23
    poly=sp.Poly(sp.expand(S5(c[0]*t,c[1]*t,c[2]*t,c[3]*t,X,a,b)),t)
    d=int(poly.degree()); lead=sp.expand(poly.LC())
    out["m4_xR_symbolic"]={"c":c,"a":a,"b":b,"deg_t":d,
        "lead_is_constant_in_xR": lead.free_symbols==set(),
        "coeff_8888": str(sp.simplify(lead/ (c[0]**8*c[1]**8*c[2]**8*c[3]**8))) if d==32 else None}
    # a, b symbolic, x_R numeric
    A,Bs=sp.symbols('a b')
    c=[3,5,7,11]; xR=29
    poly=sp.Poly(sp.expand(S5(c[0]*t,c[1]*t,c[2]*t,c[3]*t,xR,A,Bs)),t)
    d=int(poly.degree()); lead=sp.expand(poly.LC())
    out["m4_ab_symbolic"]={"c":c,"x_R":xR,"deg_t":d,
        "lead_is_constant_in_ab": lead.free_symbols==set(),
        "coeff_8888": str(sp.simplify(lead/(c[0]**8*c[1]**8*c[2]**8*c[3]**8))) if d==32 else None}
    out["degenerate_note"].append(
      "A specialisation with c_1 = c_2 (or x_3 = x_4) makes the leading T-coefficient "
      "(x_1 - x_2)^2 resp. (x_3 - x_4)^2 vanish and drops the resultant's t-degree "
      "below 32; observed once in r3_results.json (c = [5,5,7,9], deg_t 24) and once in "
      "the per-variable test (x_3 = x_4 = 3, deg 4). Those are degeneracies of the "
      "SPECIALISATION, not of H-TOP; pairwise-distinct constants are used here.")
    json.dump(out,sys.stdout,indent=1,default=str)
run()
