"""J4 (b) part 2: REALISTIC faults -- ones that fire ONLY ON LARGE INPUTS, so
they slip past the package's own self-consistency asserts (field-polynomial
irreducibility, orbit-size assertions) exactly as a real off-by-one at a word
boundary would.  Question: does M2 still read 0?"""
import importlib.util, os, random, sys, json, re, signal
HERE=os.path.dirname(os.path.abspath(__file__))
BASE=open(os.path.join(HERE,"faultcopy","qspcore_base.py")).read()
CELLS=[(7,3),(11,4)]
class _TO(Exception): pass
def _h(s,f): raise _TO()
signal.signal(signal.SIGALRM,_h)

def load(src,name):
    p=os.path.join(HERE,"faultcopy",name+".py"); open(p,"w").write(src)
    spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m; spec.loader.exec_module(m); return m

def run_matrix(mod, per_cand_s=2):
    rng=random.Random(20260917); rows=[]; d12=d13=d23=0; err=0
    for (n,npr) in CELLS:
        try: K=mod.KField(n)
        except Exception as e:
            err+=60*4; continue
        for d in range(2,6):
            for low in range(1<<d):
                lam=(1<<d)|low
                try:
                    signal.alarm(per_cand_s)
                    i1=mod.i1_brute_f2(K,lam,npr)[0]
                    i2=mod.i2_gcd_f2(n,npr,lam)
                    r3=mod.i3_injection_f2(K,lam,npr,rng)
                    i3=None if r3.get("degenerate") else r3["N"]
                    signal.alarm(0)
                except _TO: signal.alarm(0); err+=1; i1=i2=i3="TIMEOUT"
                except Exception as e: signal.alarm(0); err+=1; i1=i2=i3="ERR:"+type(e).__name__
                rows.append((n,npr,lam,i1,i2,i3))
                if i1!=i2: d12+=1
                if i3 is not None and i1!=i3: d13+=1
                if i3 is not None and i2!=i3: d23+=1
    return rows, dict(I1_vs_I2=d12,I1_vs_I3=d13,I2_vs_I3=d23,errors=err,n=len(rows))

# faults gated on input SIZE so the package's own asserts (degree<=13 field
# polynomials, 2^n-element tables) never see them
G = {
 "G-a square() wrong for deg > 40 only (shared by I1, I2, I3)":
   ("def square(a: int) -> int:\n    \"\"\"a(X)^2 = a(X^2) over F_2: spread the bits with zeros in between.\"\"\"\n    if a == 0:\n        return 0",
    "def square(a: int) -> int:\n    \"\"\"a(X)^2 = a(X^2) over F_2: spread the bits with zeros in between.\"\"\"\n    if a == 0:\n        return 0\n    if a.bit_length() > 40:\n        a ^= 1        # INJECTED FAULT: flip the constant coefficient on large inputs"),
 "G-b polymod() wrong for deg m > 40 only (shared by I1, I2, I3)":
   ("def polymod(a: int, m: int) -> int:\n    dm = deg(m)",
    "def polymod(a: int, m: int) -> int:\n    dm = deg(m)\n    if dm > 40 and a.bit_length() > dm:\n        a ^= 1        # INJECTED FAULT"),
 "G-c clmul() wrong for large operands only (shared by I1, I2, I3)":
   ("def clmul(a: int, b: int) -> int:\n    \"\"\"Carry-less product; loops over the set bits of the sparser operand.\"\"\"",
    "def clmul(a: int, b: int) -> int:\n    \"\"\"Carry-less product; loops over the set bits of the sparser operand.\"\"\"\n    if a.bit_length() > 40 and b.bit_length() > 40:\n        return (_clmul_ok(a, b)) ^ 1   # INJECTED FAULT"),
 "G-d gcd() wrong for large operands only (shared by I2 and I3, NOT I1)":
   ("def gcd(a: int, b: int) -> int:\n    while b:",
    "def gcd(a: int, b: int) -> int:\n    if a.bit_length() > 60 and b.bit_length() > 60:\n        b ^= 1        # INJECTED FAULT\n    while b:"),
 "G-e polymod_sparse_tail() wrong (I2 path ONLY)":
   ("    mask = (1 << np2) - 1\n    while a >> np2:",
    "    mask = (1 << np2) - 1\n    a ^= 1            # INJECTED FAULT\n    while a >> np2:"),
 "G-f frob_power_mod() wrong (I3 path ONLY)":
   ("def frob_power_mod(k: int, m: int) -> int:\n    \"\"\"X^(2^k) mod m, dense reduction.\"\"\"\n    x = 0b10",
    "def frob_power_mod(k: int, m: int) -> int:\n    \"\"\"X^(2^k) mod m, dense reduction.\"\"\"\n    x = 0b10\n    if deg(m) > 8: x ^= 1      # INJECTED FAULT"),
 "G-g _frob_table() wrong (I1 path ONLY)":
   ("        t = list(range(1 << K.n))\n        for _ in range(npr):",
    "        t = list(range(1 << K.n))\n        t = [v ^ 1 if v > 3 else v for v in t]   # INJECTED FAULT\n        for _ in range(npr):"),
}
# helper needed by G-c
PRE = "\ndef _clmul_ok(a, b):\n    if a.bit_count() > b.bit_count(): a, b = b, a\n    r = 0\n    while a:\n        low = a & -a\n        r ^= b << (low.bit_length() - 1)\n        a ^= low\n    return r\n"

base=load(BASE,"g_base"); brows,bdis=run_matrix(base)
bmap={(r[0],r[1],r[2]):(r[3],r[4],r[5]) for r in brows}
print("BASELINE over %d candidates: %s"%(bdis["n"],bdis)); sys.stdout.flush()
out=[]
for name,(old,new) in G.items():
    if old not in BASE: print("%-62s ANCHOR NOT FOUND -- fault not applied"%name); continue
    src=BASE.replace(old,new,1)
    if "_clmul_ok" in new: src=src.replace("def clmul(", PRE+"\ndef clmul(",1)
    tag="g_"+re.sub(r'\W','_',name)[:20]
    try:
        m=load(src,tag); rows,dis=run_matrix(m)
    except Exception as e:
        print("%-62s MODULE LOAD FAILED: %s (the package's own self-check caught it)"%(name,type(e).__name__)); sys.stdout.flush(); continue
    changed=sum(1 for r in rows if (r[3],r[4],r[5])!=bmap[(r[0],r[1],r[2])])
    clean = dis["I1_vs_I2"]==0 and dis["I1_vs_I3"]==0 and dis["I2_vs_I3"]==0 and dis["errors"]==0
    print("%-62s changed=%-5d M2=(%d,%d,%d) err=%-4d AGREEMENT STILL CLEAN: %s"
          %(name,changed,dis["I1_vs_I2"],dis["I1_vs_I3"],dis["I2_vs_I3"],dis["errors"],clean)); sys.stdout.flush()
    out.append(dict(fault=name,changed=changed,**dis,agreement_clean=clean))
json.dump(out,open(os.path.join(HERE,"scratch","j4_faults2_out.json"),"w"),indent=1)
