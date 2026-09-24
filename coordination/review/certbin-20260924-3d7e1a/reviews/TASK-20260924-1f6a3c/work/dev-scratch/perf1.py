import sys, time
sys.path.insert(0, '.')
import numpy as np
import boolsys as BS, closure as CL, gf2lin as GL, sroutes as SR
B = 126251
rng = np.random.default_rng([2058812, 900])
t0=time.time(); MI = BS.MonomialIndex(4); M4 = BS.Macaulay(4, MI); M3 = BS.Macaulay(3, MI); mult = CL.Multiplier(MI, 4); print('setup', time.time()-t0)
for trial in range(2):
    xR = int(rng.integers(512, 1<<17))
    t0=time.time(); eqs = BS.descended_equations(xR, B); rows = M4.rows(eqs); print('build', time.time()-t0, M4.R, M4.C)
    t0=time.time(); S = GL.rank_of(rows); print('rank4', S.dim, 'one', S.has_one(), [S.dim_below(MI.N[d]) for d in range(4)], time.time()-t0)
    t0=time.time(); r = CL.literal_closure(rows, MI, 4, mult); print('W4', r['dims'], r['multiplied_basis_sizes'], r['first_one_iteration'], r['dim_cap'], time.time()-t0)
    t0=time.time(); s1,_ = SR.route1_exhaustive(eqs); s2,_,bad = SR.route2_rootfinding(xR,B); print('s', s1, s2, bad, time.time()-t0)
    if r['one_in_W']:
        t0=time.time(); c = CL.extract_certificate(rows, M4, MI, 4, mult); print('cert', c['level_dims'], c['elements_before_prune'], c['elements_after_prune'], time.time()-t0)
        cert = c['certificate']; print('rowrefs', sum(len(e['rows']) for e in cert['elements']), 'prodrefs', sum(len(e['products']) for e in cert['elements']))
