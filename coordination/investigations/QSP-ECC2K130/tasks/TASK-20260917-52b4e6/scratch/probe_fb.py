"""Standalone probe: what does the F-b fault (polymod stops one degree early)
actually DO to a single Stage-1 candidate?  Observed under an external timeout."""
import importlib.util, os, sys, random
HERE=os.path.dirname(os.path.abspath(__file__))
BASE=open(os.path.join(HERE,"faultcopy","qspcore_base.py")).read()
old="def polymod(a: int, m: int) -> int:\n    dm = deg(m)\n    while a and deg(a) >= dm:"
new="def polymod(a: int, m: int) -> int:\n    dm = deg(m)\n    while a and deg(a) > dm:"
assert old in BASE
src=BASE.replace(old,new,1)
p=os.path.join(HERE,"faultcopy","pfb.py"); open(p,"w").write(src)
spec=importlib.util.spec_from_file_location("pfb",p); m=importlib.util.module_from_spec(spec)
sys.modules["pfb"]=m; spec.loader.exec_module(m)
print("module imported OK (no import-time assert)",flush=True)
rng=random.Random(1)
K=m.KField(7); print("KField(7) constructed OK -- the irreducibility self-check PASSED under the fault",flush=True)
lam=0b110   # X^2 + X at (7,3): the Type 2 complete splitter, true N = 8
print("I1 ...",flush=True); print("  I1 =", m.i1_brute_f2(K,lam,3)[0],flush=True)
print("I2 ...",flush=True); print("  I2 =", m.i2_gcd_f2(7,3,lam),flush=True)
print("I3 ...",flush=True); print("  I3 =", m.i3_injection_f2(K,lam,3,rng),flush=True)
