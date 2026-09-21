import math, time
from estimator import RC, ND, schemes
from estimator.lwe_primal import primal_bdd

def run(p, c):
    q = p.updated(Xs=ND.DiscreteGaussian(c*float(p.Xs.stddev)),
                  Xe=ND.DiscreteGaussian(c*float(p.Xe.stddev)))
    r = primal_bdd(q, red_cost_model=RC.MATZOV)
    return (math.log2(float(r["rop"])), int(r["beta"]), int(r["eta"]), int(r["d"]))

t0=time.time()
for name, p in [("Kyber512", schemes.Kyber512), ("Kyber768", schemes.Kyber768),
                ("Kyber1024", schemes.Kyber1024)]:
    base = run(p, 1.0)
    print(f"{name}  base log2rop={base[0]:.6f} beta={base[1]} eta={base[2]} d={base[3]} n={p.n}")
    for c in (0.995, 0.99, 0.98, 0.95, 0.90):
        v = run(p, c)
        print(f"   c={c:<6} log2rop={v[0]:12.6f} beta={v[1]:4d} eta={v[2]:4d} d={v[3]:5d}"
              f"   dbeta={v[1]-base[1]:4d} dlog2rop={v[0]-base[0]:9.4f} dd={v[3]-base[3]:4d}")
print("elapsed", time.time()-t0)
