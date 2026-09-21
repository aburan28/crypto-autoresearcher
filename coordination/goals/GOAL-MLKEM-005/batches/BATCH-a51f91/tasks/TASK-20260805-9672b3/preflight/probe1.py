"""Exploratory probe 1 (NOT a deliverable run): is the gap an attack-function
identity mismatch? Compare estimator.lwe_dual.dual_hybrid(fft=True) against
estimator.lwe_dual.matzov (which is what LWE.dual_hybrid resolves to)."""
import math, time, sys
from estimator import RC, schemes
from estimator.lwe_dual import dual_hybrid, matzov

sets = {"Kyber512": schemes.Kyber512, "Kyber768": schemes.Kyber768,
        "Kyber1024": schemes.Kyber1024}

for name, p in sets.items():
    t0 = time.time()
    r = dual_hybrid(p, red_cost_model=RC.MATZOV, fft=True)
    t1 = time.time()
    print(f"[dual_hybrid fft=True] {name}: log2rop={math.log2(float(r['rop'])):.6f} "
          f"{ {k: (float(v) if hasattr(v,'__float__') and not isinstance(v,str) else v) for k,v in r.items() if k!='problem'} } "
          f"({t1-t0:.1f}s)")
    sys.stdout.flush()

for name, p in sets.items():
    t0 = time.time()
    r = matzov(p, red_cost_model=RC.MATZOV)
    t1 = time.time()
    print(f"[matzov] {name}: log2rop={math.log2(float(r['rop'])):.6f} "
          f"{ {k: (float(v) if hasattr(v,'__float__') and not isinstance(v,str) else v) for k,v in r.items() if k!='problem'} } "
          f"({t1-t0:.1f}s)")
    sys.stdout.flush()
