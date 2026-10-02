import sys, random, itertools; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine, ffd as slow_ffd, new_falls_at as slow_nf, _tables
from fastfall import Kernel
from truekernel import TrueKernel, gl_rowsets, popcount
import boolring as B
class OrKernel(TrueKernel):            # my kernel with src's OR base rows (fast-kernel semantics)
    def __init__(self, gs, N):
        super().__init__(gs,N)
        self.base=[[0]*(1<<N) for _ in gs]
        for j,f in enumerate(gs):
            for m in range(1<<N):
                r=0
                for mm in f: r|=1<<self.pos[mm|m]
                self.base[j][m]=r
        self.cache={}
rng=random.Random(12345)
for label,(gs,N) in (("T2 (6,3)",(R.cell_systems(6,3)[0],6)),("T4 null(4,2)",(R.cell_systems(4,2)[1],4)),("T3 (4,2)",(R.cell_systems(4,2)[0],4))):
    l=len(gs); sets=list(gl_rowsets(l)); sample=sets if len(sets)<=1000 else rng.sample(sets,400)
    K=Kernel(gs,N); cache={}; OK=OrKernel(gs,N); TK=TrueKernel(gs,N); tabs=_tables(N)
    a=b=c=0
    for M in sample:
        # (a) my OR-mode kernel == src fast kernel, new_falls at D=1..N
        if [OK.new_falls(M,D) for D in range(1,N+1)]==[K.new_falls(M,D,cache) for D in range(1,N+1)]: a+=1
        # (b) my TrueKernel == direct boolring implementation on the recombined generators (different code path)
        Hs=[B.from_set(f) for f in recombine(gs,M)]
        if [TK.new_falls(M,D) for D in range(1,N+1)]==[B.new_falls(Hs,N,D,B.mul_mono_true) for D in range(1,N+1)]: b+=1
        # (c) boolring OR-mode == src SLOW instrument (so my OR model of the slow path is exact)
        if [B.new_falls(Hs,N,D,B.mul_mono_or) for D in (1,2,3)]==[slow_nf(recombine(gs,M),N,D,tabs) for D in (1,2,3)]: c+=1
    print(f"{label}: sample {len(sample)} | myOR==src_fast {a} | myTrue==direct_true {b} | directOR==src_slow {c}")
