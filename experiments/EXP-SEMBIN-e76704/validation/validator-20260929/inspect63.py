import sys; sys.dont_write_bytecode=True
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
from ffd_semaev import popcount
N=6
sem,null,xR=R.cell_systems(6,3)
def show(f):
    ms=sorted(f,key=lambda m:(-popcount(m),m))
    def mono(m):
        if m==0: return "1"
        return "*".join(("u%d"%j if j<3 else "w%d"%(j-3)) for j in range(N) if (m>>j)&1)
    return " + ".join(mono(m) for m in ms)
print("xR =",xR)
for i,f in enumerate(sem): print("f%d (deg %d, %d terms): %s"%(i,max(popcount(m) for m in f),len(f),show(f)))
h=recombine(sem,[1,2,4,8,26])
print("h4 = f1+f3+f4 =", show(h[4]), " constant term:", 0 in h[4])
