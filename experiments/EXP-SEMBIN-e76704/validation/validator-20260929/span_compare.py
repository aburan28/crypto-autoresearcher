import sys; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
from boolring import *
N=6
sem,null,xR=R.cell_systems(6,3)
I=[from_set(f) for f in sem]
Mrows=[1,2,4,8,26]
H=[from_set(f) for f in recombine(sem,Mrows)]
def same_span(A,B): return rank(A)==rank(B)==rank(A+B)
def fast_rows(Mrows,D):   # fastfall semantics: row(m, h_S) = XOR_{j in S} OR(m, f_j), kept if top degree <= D
    rows=[]
    for S in Mrows:
        for m in range(1<<N):
            r=0
            for j in range(len(I)):
                if (S>>j)&1: r^=mul_mono_or(I[j],m)
            if r and deg(r)<=D: rows.append(r)
    return rows
for name,G,Ms in (("identity",I,[1,2,4,8,16]),("witness M",H,Mrows)):
    for D in range(1,5):
        A=V(G,D,N,mul_mono_or); B=V(G,D,N,mul_mono_true); C=fast_rows(Ms,D)
        print(f"{name} D={D}: dim V_D  OR={rank(A)} XOR={rank(B)} FAST={rank(C)} | OR==XOR span:{same_span(A,B)}  FAST==XOR span:{same_span(C,B)}")
