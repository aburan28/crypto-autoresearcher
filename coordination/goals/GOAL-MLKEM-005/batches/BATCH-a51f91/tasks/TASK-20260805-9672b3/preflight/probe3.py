import math, time
from estimator import RC, ND, schemes
from estimator.lwe_primal import primal_bdd
from estimator.lwe_parameters import LWEParameters
from estimator.reduction import delta as deltaf

r = primal_bdd(schemes.Kyber512, red_cost_model=RC.MATZOV)
print("cost keys:", list(r.keys()))
print("repr:", repr(r))

# arm B: does optimize_d=False propagate?
try:
    rB = primal_bdd(schemes.Kyber512, red_cost_model=RC.MATZOV, optimize_d=False)
    print("optimize_d=False:", math.log2(float(rB["rop"])), int(rB["beta"]), int(rB["eta"]), int(rB["d"]))
except Exception as e:
    print("optimize_d=False FAILED:", type(e).__name__, e)

# toy candidates
for n in (40, 60, 80, 100, 120, 150, 200):
    p = LWEParameters(n=n, q=3329, Xs=ND.DiscreteGaussian(1.0), Xe=ND.DiscreteGaussian(1.0), m=n,
                      tag=f"toy{n}")
    t0=time.time()
    rr = primal_bdd(p, red_cost_model=RC.MATZOV)
    print(f"toy n={n:4d} beta={int(rr['beta']):4d} eta={int(rr['eta']):4d} d={int(rr['d']):5d} "
          f"log2rop={math.log2(float(rr['rop'])):8.4f}  ({time.time()-t0:.2f}s)")
for b in (30, 40, 60, 100, 200, 389, 606, 855):
    d_ = float(deltaf(b)); ld = math.log(d_)
    print(f"beta={b:4d} delta={d_:.8f} lnd={ld:.6f} 4*b*lnd={4*b*ld:8.4f} ratio 1/(4b lnd)={1/(4*b*ld):8.5f}")
