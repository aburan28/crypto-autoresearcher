"""Deterministic complete-case fixture generator and ordered V01--V12 gate."""
from __future__ import annotations
from dataclasses import dataclass

PRIMES={101:(100,((2,2),(5,2))),241:(240,((2,4),(3,1),(5,1)))}
PANELS={"P00":[],"P01":[10],"P02":[10,10,10],"P03":[5,10,20],"P04":[4,10],"P05":[4,5],"P06":[20],"P07":[4,5,20,20],"P10":[1],"P11":[1,4,10]}
def primitive(r,n,factors):
    for z in range(2,r):
        if pow(z,n,r)==1 and all(pow(z,n//q,r)!=1 for q,_ in factors): return z
    raise ValueError("no primitive")
def panel_moduli(pid,r):
    if pid=="P08": return [100 if r==101 else 240]
    if pid=="P09": return [4,25] if r==101 else [16,3,5]
    return list(PANELS[pid])
def ordered(values, variant):
    if variant=="forward" or len(values)<2:return values[:]
    if variant=="reverse":return list(reversed(values))
    if variant=="rotate_left_one":return values[1:]+values[:1]
    raise ValueError("bad order")
def fixture(r,k,moduli,variant="forward",wrong=False,inconsistent=False):
    n,factors=PRIMES[r]; z=primitive(r,n,factors); rows=[]
    for i,m in enumerate(moduli):
        a=(k+(1 if wrong or (inconsistent and i==len(moduli)-1) else 0))%m
        rows.append({"a":a,"m":m,"d":n//m,"token":{"index":i,"exponent":n//m,"source_kind":"synthetic_placeholder"}})
    return {"r":r,"n":n,"factorization":[list(x) for x in factors],"zeta":z,"k":k,"x":pow(z,k,r),"mode":"nonzero","constraints":ordered(rows,variant)}
def gate(data, allowed=PRIMES):
    # exact fixed first-error sequence V01--V12
    r=data.get("r")
    if r not in allowed:return "INPUT_UNSUPPORTED_R"
    n,factors=allowed[r]
    given=data.get("factorization")
    if not isinstance(given,list) or sorted(map(tuple,given))!=sorted(factors):return "INPUT_BAD_FACTORIZATION"
    if data.get("zeta") is None or any(pow(data["zeta"],n//q,r)==1 for q,_ in factors) or pow(data["zeta"],n,r)!=1:return "INPUT_NOT_PRIMITIVE"
    if data.get("mode") == "zero": return "ZERO" if data.get("x")==0 and not data.get("constraints") else "INPUT_ZERO_NONZERO_MODE"
    if data.get("x")==0:return "INPUT_ZERO_NONZERO_MODE"
    rows=data.get("constraints")
    if not isinstance(rows,list):return "INPUT_MISSING_SUPPLY"
    for i,row in enumerate(rows):
        d,m,a,t=row.get("d"),row.get("m"),row.get("a"),row.get("token")
        if not isinstance(d,int) or d<=0 or d>n:return "INPUT_BAD_D"
        if not isinstance(m,int) or m<=0 or n%m:return "INPUT_BAD_M"
        if m*d != n:return "INPUT_M_D_MISMATCH"
        if not isinstance(a,int) or not 0<=a<m:return "INPUT_BAD_RESIDUE"
        if not isinstance(t,dict):return "INPUT_MISSING_SUPPLY"
        if t.get("index")!=i or t.get("exponent")!=d or t.get("source_kind")!="synthetic_placeholder":return "INPUT_SUPPLY_BINDING_MISMATCH"
    return "OK"
def all_case_identities():
    # Metadata enumeration only; no CRT/reference arithmetic.
    out=[]
    for family in ("malformed","zero","inconsistent","wrong_target","positive"):
      for r,(n,_) in PRIMES.items():
       if family=="malformed": out += [f"{family}:{r}:V{i:02}" for i in range(1,13)]
       elif family=="zero": out += [f"{family}:{r}"]
       else:
        ids=(['I01','I02','I03','I04'] if family=='inconsistent' else (['P01','P02','P03','P04','P05','P06','P07','P08','P09','P11'] if family=='wrong_target' else list(PANELS)+['P08','P09']))
        for p in ids:
         for k in range(n):
          for v in ('forward','reverse','rotate_left_one'): out.append(f"{family}:{r}:{p}:{k}:{v}")
    return out
