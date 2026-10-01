import sys, time
sys.path.insert(0, '.')
import numpy as np
import boolsys as BS, gf2lin as GL, sroutes as SR
B = 126251
rng = np.random.default_rng([2058812, 903])
MI = BS.MonomialIndex(5); M5 = BS.Macaulay(5, MI)
xR = int(rng.integers(512, 1<<17))
eqs = BS.descended_equations(xR, B)
print('s', SR.route1_exhaustive(eqs)[0])
rng2 = np.random.default_rng([2058812, 904])
for _ in range(20):
    xR = int(rng2.integers(512, 1<<17))
    eqs = BS.descended_equations(xR, B)
    s, sols = SR.route1_exhaustive(eqs)
    if s:
        S = GL.rank_of(M5.rows(eqs))
        # soundness: every basis vector vanishes at every solution
        bad = 0
        for v in sols:
            ev = 0
            for b, m in enumerate(MI.mono):
                if m & v == m: ev |= 1 << b
            for w in S.basis.values():
                if bin(w & ev).count('1') & 1: bad += 1
        print('sat s', s, 'rank5', S.dim, 'one', S.has_one(), 'nonvanishing', bad)
        break
