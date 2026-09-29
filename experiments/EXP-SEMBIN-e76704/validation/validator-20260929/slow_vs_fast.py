import sys, random; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
from fastfall import Kernel
from truekernel import gl_rowsets
import boolring as B
gs=R.cell_systems(6,3)[0]; N=6; K=Kernel(gs,N); cache={}
sets=list(gl_rowsets(5)); rng=random.Random(7)
with26=[M for M in sets if 26 in M]; without=[M for M in sets if 26 not in M]
for label,pool,k in (("containing row 26",with26,1500),("not containing 26",without,1500)):
    samp=rng.sample(pool,k); dis=0; ex=None
    for M in samp:
        slow=B.ffd([B.from_set(f) for f in recombine(gs,M)],N,B.mul_mono_or)   # == src slow semantics (cross-validated)
        fast=K.ffd(M,cache)
        if slow!=fast:
            dis+=1; ex=ex or (M,slow,fast)
    print(f"{label}: sampled {k} row-sets, slow-instrument ffd != fast-kernel ffd in {dis}; example {ex}")
