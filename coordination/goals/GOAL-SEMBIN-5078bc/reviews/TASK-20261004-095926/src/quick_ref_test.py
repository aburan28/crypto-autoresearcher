import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from ref_closure import *
from gen_systems import system
for fam, N, M in [('quad',10,10),('quad',12,12),('sparsequad',12,12),('cubic',12,12),('bilinear',12,12),('planted',12,10),('toeplitz',12,12)]:
    gens = system(fam, N, M, 1)
    t=time.time()
    C = Closure(gens, N, 4).run()
    lms = C.lm_set()
    pts, lmI, stdI = ground_truth(N, gens)
    nstd = count_std(N, lms)
    print(fam,N,M,'rank',len(C.basis),'hist',C.history,'|V|',len(pts),'Nstd',nstd, verdict(nstd,len(pts)),
          'LM(W)<=LM(I)',set(lms)<=lmI,'LM(W)==LM(I<=4)',set(lms)==lmI,'sat',C.saturated(),'t=%.1fs'%(time.time()-t))
