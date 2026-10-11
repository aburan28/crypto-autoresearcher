import sys, time
sys.path.insert(0, '.')
import numpy as np
import boolsys as BS, closure as CL, gf2lin as GL, sroutes as SR, wcert_check as WC, xcheck as XC
B = 126251
rng = np.random.default_rng([2058812, 902])
MI = BS.MonomialIndex(4); M4 = BS.Macaulay(4, MI); M3 = BS.Macaulay(3, MI); mult = CL.Multiplier(MI, 4)
t0=time.time(); X = XC.XCheck(4); print('xsetup', time.time()-t0)
n=0
for trial in range(30):
    xR = int(rng.integers(512, 1<<17))
    eqs = BS.descended_equations(xR, B)
    s1,_ = SR.route1_exhaustive(eqs)
    if n>=1 and s1: continue
    rows = M4.rows(eqs)
    S4 = GL.rank_of(rows); S3 = GL.rank_of(M3.rows(eqs))
    r = CL.literal_closure(rows, MI, 4, mult)
    t0=time.time(); x = X.run(WC.equations_curve(xR, B)); tx=time.time()-t0
    eng = {"rank_3":S3.dim, "one_in_R3":S3.has_one(), "rank_4":S4.dim, "one_in_R4":S4.has_one(), "R4_cap_dims":[S4.dim_below(MI.N[d]) for d in range(4)], "W4_dims":r['dims'], "W4_fixpoint_index":r['fixpoint_index'], "W4_first_one_iteration":r['first_one_iteration'], "W4_final_dim":r['final_dim'], "W4_cap_dims":r['dim_cap']}
    print('s', s1, 'agree', eng==x, 'xcheck %.1fs'%tx)
    if eng != x: print(eng); print(x)
    n+=1
    if n>=4: break
