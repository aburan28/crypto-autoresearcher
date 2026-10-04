import sys, time, json, math, itertools
sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from fastfall import Kernel
from truekernel import TrueKernel, gl_rowsets
which=sys.argv[1]
cells={"T2":(R.cell_systems(6,3)[0],6),"T3":(R.cell_systems(4,2)[0],4),"T4":(R.cell_systems(4,2)[1],4)}
gs,N=cells[which]; l=len(gs); perm=math.factorial(l)
out={}
for label in ("src_fast_kernel","true_product"):
    t0=time.time()
    if label=="src_fast_kernel":
        K=Kernel(gs,N); cache={}
        nf=lambda M,D: K.new_falls(M,D,cache); ff=lambda M: K.ffd(M,cache)
    else:
        K=TrueKernel(gs,N); nf=K.new_falls; ff=K.ffd
    base=ff([1<<j for j in range(l)])
    nsets=up=down=0; best=base; dist={}; up_rows_contain={}; lowgen_up=0; lowgen_total=0
    dist_all={}
    for M in gl_rowsets(l):
        nsets+=1
        d_all=ff(M); d_all=N+1 if d_all is None else d_all
        dist_all[d_all]=dist_all.get(d_all,0)+1
        if nf(M,base)>0: continue
        d=d_all
        if d>base:
            up+=1; best=max(best,d)
            for r in M: up_rows_contain[r]=up_rows_contain.get(r,0)+1
        elif d<base: down+=1
    out[label]=dict(base=base,row_sets=nsets,group_order=nsets*perm,upward=up*perm,downward=down*perm,D_ff_max=best,
                    ffd_distribution_over_GL={str(k):v*perm for k,v in sorted(dist_all.items())},
                    rows_appearing_in_every_upward_set=[r for r,c in up_rows_contain.items() if c==up],
                    seconds=round(time.time()-t0,1))
    print(which,label,out[label],flush=True)
json.dump(out,open(f"/tmp/claude-0/validator/recount_{which}.json","w"),indent=1)
