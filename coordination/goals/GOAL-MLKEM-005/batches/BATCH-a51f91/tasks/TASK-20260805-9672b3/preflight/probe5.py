import math
from estimator import RC, ND, schemes
from estimator.lwe_primal import primal_bdd, PrimalHybrid
from estimator.lwe_parameters import LWEParameters

p = schemes.Kyber512
pn = LWEParameters.normalize(p)
print("normalize identity:", pn == p, " Xs<=Xe:", p.Xs <= p.Xe)
m_allowed = p.m + p.n if p.Xs <= p.Xe else p.m
print("m_allowed", m_allowed)
for od in (True, False):
    r = PrimalHybrid.cost_zeta(zeta=0, params=pn, red_cost_model=RC.MATZOV, m=m_allowed,
                               babai=False, mitm=False, optimize_d=od)
    print(f"cost_zeta optimize_d={od}: log2rop={math.log2(float(r['rop'])):.10f} beta={int(r['beta'])} "
          f"eta={int(r['eta'])} d={int(r['d'])} keys={list(r.keys())}")
a = primal_bdd(p, red_cost_model=RC.MATZOV)
print("primal_bdd            :", math.log2(float(a['rop'])), int(a['beta']), int(a['eta']), int(a['d']))
