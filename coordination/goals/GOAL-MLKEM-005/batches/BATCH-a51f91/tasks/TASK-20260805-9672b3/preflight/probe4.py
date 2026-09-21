import math
from estimator import RC, ND, schemes
from estimator.lwe_primal import primal_bdd, PrimalHybrid
from estimator.reduction import delta as deltaf
from sage.all import log, sqrt, ceil, oo

p = schemes.Kyber512
m_allowed = p.m + p.n
xi = 1
for b in (388, 389, 390):
    dlt = float(deltaf(b))
    dh = max(b, min(int(ceil(float(sqrt(p.n * math.log(p.q / xi) / math.log(dlt))))), m_allowed))
    bp = PrimalHybrid.beta_params(beta=b, params=p, zeta=0, babai=False, mitm=False, m=m_allowed,
                                  red_cost_model=RC.MATZOV)
    print(f"beta={b} heuristic_d(my calc)={dh} beta_params d={int(bp['d'])} eta={int(bp['eta'])}")

for c in (1.0, 0.99, 0.95, 0.90):
    q1 = p.updated(Xs=ND.DiscreteGaussian(c*float(p.Xs.stddev)), Xe=ND.DiscreteGaussian(c*float(p.Xe.stddev)))
    a = primal_bdd(q1, red_cost_model=RC.MATZOV)
    b_ = primal_bdd(q1, red_cost_model=RC.MATZOV, optimize_d=False)
    print(f"c={c}: A log2rop={math.log2(float(a['rop'])):.6f} beta={int(a['beta'])} d={int(a['d'])} | "
          f"B log2rop={math.log2(float(b_['rop'])):.6f} beta={int(b_['beta'])} d={int(b_['d'])}")
