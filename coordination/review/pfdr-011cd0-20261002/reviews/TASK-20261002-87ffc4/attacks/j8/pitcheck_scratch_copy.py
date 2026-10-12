import numpy as np, math, sys
sys.path.insert(0, "attacks/j4")
import j4lib as L
rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 999]))
def pit_D(cnt, lam, u):
    kmax = int(cnt.max()) + 1
    Fm = np.zeros(len(cnt)); F = np.zeros(len(cnt))
    term = np.exp(-lam); cum = term.copy()
    F[cnt == 0] = cum[cnt == 0]
    for k in range(1, kmax + 1):
        sel = cnt == k
        Fm[sel] = cum[sel]
        term = term * lam / k
        cum = cum + term
        F[sel] = cum[sel]
    pv = np.sort(Fm + u * (F - Fm)); n = len(pv)
    return float(max(np.max(np.arange(1, n + 1) / n - pv), np.max(pv - np.arange(0, n) / n)))
for lam0, n in ((0.25, 24000), (100.0, 3600)):
    Ds = []
    for _ in range(300):
        lam = np.full(n, lam0)
        cnt = rng.poisson(lam)
        Ds.append(pit_D(cnt, lam, rng.random(n)))
    Ds = np.array(Ds)
    ps = np.array([L.kolmogorov_sf(d, n) for d in Ds])
    print(lam0, n, "mean asympt p (should be ~0.5):", round(ps.mean(), 3), "frac p<0.1:", round(np.mean(ps < 0.1), 3), "frac p<0.01:", round(np.mean(ps<0.01),3))
