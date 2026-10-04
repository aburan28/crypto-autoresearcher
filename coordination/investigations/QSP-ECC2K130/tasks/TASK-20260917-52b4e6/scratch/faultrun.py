"""One fault, one subprocess. argv[1] = fault key, argv[2] = 'base' or 'fault'.
Prints a single JSON line with the agreement matrix over the (7,3) and (11,4)
Stage-1 cells, degrees 2..5 (120 candidates)."""
import importlib.util, os, sys, random, json
HERE=os.path.dirname(os.path.abspath(__file__))
BASE=open(os.path.join(HERE,"faultcopy","qspcore_base.py")).read()

FAULTS={
 "F-c  clmul(): drop the highest set bit of the sparser operand [shared by I1,I2,I3]":
  ("    r = 0\n    while a:\n        low = a & -a\n        r ^= b << (low.bit_length() - 1)\n        a ^= low\n    return r",
   "    r = 0\n    if a and a.bit_count() > 1:\n        a ^= 1 << (a.bit_length() - 1)\n    while a:\n        low = a & -a\n        r ^= b << (low.bit_length() - 1)\n        a ^= low\n    return r"),
 "F-d  gcd(): Euclid swaps one step early [shared by I2,I3; NOT I1]":
  ("def gcd(a: int, b: int) -> int:\n    while b:\n        a = polymod(a, b)\n        a, b = b, a\n    return a",
   "def gcd(a: int, b: int) -> int:\n    while b:\n        a, b = b, polymod(a, b)\n    return a if a else b"),
 "F-e  polymod_sparse_tail(): corrupt the tail [I2 path ONLY]":
  ("    mask = (1 << np2) - 1\n    while a >> np2:",
   "    mask = (1 << np2) - 1\n    a ^= 1\n    while a >> np2:"),
 "F-f  frob_power_mod(): seed X+1 instead of X [I3 path ONLY]":
  ('def frob_power_mod(k: int, m: int) -> int:\n    """X^(2^k) mod m, dense reduction."""\n    x = 0b10',
   'def frob_power_mod(k: int, m: int) -> int:\n    """X^(2^k) mod m, dense reduction."""\n    x = 0b11'),
 "F-g  _frob_table(): one Frobenius too few [I1 path ONLY]":
  ("        t = list(range(1 << K.n))\n        for _ in range(npr):",
   "        t = list(range(1 << K.n))\n        for _ in range(max(0, npr - 1)):"),
 "G-a  square(): flip the constant coefficient when deg > 40 [shared by I1,I2,I3; invisible to the n<=13 self-checks]":
  ('def square(a: int) -> int:\n    """a(X)^2 = a(X^2) over F_2: spread the bits with zeros in between."""\n    if a == 0:\n        return 0',
   'def square(a: int) -> int:\n    """a(X)^2 = a(X^2) over F_2: spread the bits with zeros in between."""\n    if a == 0:\n        return 0\n    if a.bit_length() > 40:\n        a ^= 1'),
 "G-b  polymod(): corrupt when deg m > 40 [shared by I1,I2,I3; invisible to the n<=13 self-checks]":
  ("def polymod(a: int, m: int) -> int:\n    dm = deg(m)",
   "def polymod(a: int, m: int) -> int:\n    dm = deg(m)\n    if dm > 40 and a.bit_length() > dm:\n        a ^= 1"),
 "G-d  gcd(): corrupt when both operands have deg > 60 [shared by I2,I3; NOT I1]":
  ("def gcd(a: int, b: int) -> int:\n    while b:",
   "def gcd(a: int, b: int) -> int:\n    if a.bit_length() > 60 and b.bit_length() > 60:\n        b ^= 1\n    while b:"),
}
key=sys.argv[1]; mode=sys.argv[2]
src=BASE
if mode=="fault":
    old,new=FAULTS[key]
    assert old in BASE, "anchor missing"
    src=BASE.replace(old,new,1)
tag="fr_"+str(abs(hash(key+mode))%10**8)
p=os.path.join(HERE,"faultcopy",tag+".py"); open(p,"w").write(src)
spec=importlib.util.spec_from_file_location(tag,p); m=importlib.util.module_from_spec(spec)
sys.modules[tag]=m; spec.loader.exec_module(m)
rng=random.Random(20260917)
rows=[]; d12=d13=d23=0; err=0
for (n,npr) in [(7,3),(11,4)]:
    K=m.KField(n)
    for d in range(2,6):
        for low in range(1<<d):
            lam=(1<<d)|low
            i1=m.i1_brute_f2(K,lam,npr)[0]
            i2=m.i2_gcd_f2(n,npr,lam)
            r3=m.i3_injection_f2(K,lam,npr,rng)
            i3=None if r3.get("degenerate") else r3["N"]
            rows.append([n,npr,lam,i1,i2,i3])
            if i1!=i2: d12+=1
            if i3 is not None and i1!=i3: d13+=1
            if i3 is not None and i2!=i3: d23+=1
print(json.dumps({"key":key,"mode":mode,"n":len(rows),"I1_vs_I2":d12,"I1_vs_I3":d13,
                  "I2_vs_I3":d23,"rows":rows}))
