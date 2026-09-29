import sys, time, json, gzip
sys.path.insert(0, '.')
import numpy as np
import boolsys as BS, closure as CL, gf2lin as GL, sroutes as SR, wcert_check as WC
B = 126251
rng = np.random.default_rng([2058812, 901])
MI = BS.MonomialIndex(4); M4 = BS.Macaulay(4, MI); mult = CL.Multiplier(MI, 4)
found = 0
for trial in range(40):
    xR = int(rng.integers(512, 1<<17))
    eqs = BS.descended_equations(xR, B)
    s1,_ = SR.route1_exhaustive(eqs)
    if s1: continue
    rows = M4.rows(eqs)
    r = CL.literal_closure(rows, MI, 4, mult)
    print('unsat trial', trial, 'R4one', GL.rank_of(rows).has_one(), 'W4', r['dims'], r['first_one_iteration'])
    if r['one_in_W'] and r['first_one_iteration'] and r['first_one_iteration']>0:
        t0=time.time(); c = CL.extract_certificate(rows, M4, MI, 4, mult); t1=time.time()-t0
        cert = c['certificate']
        print('  cert', c['level_dims'], c['elements_before_prune'], c['elements_after_prune'], 'rowrefs', sum(len(e['rows']) for e in cert['elements']), 'prodrefs', sum(len(e['products']) for e in cert['elements']), '%.1fs'%t1)
        rec = {'schema':'certbin.wcert.v1','label':'SYN','D':4,**cert}
        sz = len(gzip.compress(json.dumps(rec, separators=(',',':')).encode()))
        t0=time.time(); ok = WC.check(rec, WC.equations_curve(xR, B)); print('  check', ok[0], ok[1], ok[2], 'gz bytes', sz, '%.1fs'%(time.time()-t0))
        found += 1
        if found >= 2: break
