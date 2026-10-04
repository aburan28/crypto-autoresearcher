import sys, time, resource
sys.path.insert(0, '.')
import numpy as np
import boolsys as BS, gf2lin as GL
B = 126251
rng = np.random.default_rng([2058812, 903])
t0=time.time(); MI = BS.MonomialIndex(5); print('MI5', time.time()-t0)
M5 = BS.Macaulay(5, MI); print(M5.R, M5.C)
xR = int(rng.integers(512, 1<<17))
eqs = BS.descended_equations(xR, B)
t0=time.time(); rows = M5.rows(eqs); print('rows', time.time()-t0)
t0=time.time(); S = GL.rank_of(rows); print('rank5', S.dim, S.has_one(), time.time()-t0)
print('maxrss MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
