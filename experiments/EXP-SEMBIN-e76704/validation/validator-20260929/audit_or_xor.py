import sys; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine, new_falls_at, _tables
from fastfall import Kernel
from boolring import *
N=6
sem,null,xR=R.cell_systems(6,3)
I=[from_set(f) for f in sem]
Mrows=[1,2,4,8,26]
H=[from_set(f) for f in recombine(sem,Mrows)]
# how many (generator, monomial) rows differ OR vs XOR
for name,G in (("identity",I),("witness M",H)):
    bad=[(i,m) for i,g in enumerate(G) for m in range(1<<N) if mul_mono_true(g,m)!=mul_mono_or(g,m)]
    print(f"{name}: {len(bad)} of {len(G)*64} rows m*g differ between OR (src) and XOR (true)")
    for D in (1,2,3):
        bd=[(i,m) for (i,m) in bad if min(deg(mul_mono_true(G[i],m)),deg(mul_mono_or(G[i],m)))<=D]
        print(f"   rows that enter V_{D} under either convention and differ: {len(bd)}")
print()
for name,G in (("identity",I),("witness M",H)):
    print(name, " new_falls D=1..4  OR (src convention):", [new_falls(G,N,D,mul_mono_or) for D in (1,2,3,4)],
          "  XOR (true product):", [new_falls(G,N,D,mul_mono_true) for D in (1,2,3,4)])
    print("   ffd OR:",ffd(G,N,mul_mono_or),"  ffd XOR:",ffd(G,N,mul_mono_true))
# cross-check my OR implementation against the src slow instrument, to be sure I reproduce it
tabs=_tables(N)
print("src slow new_falls identity:",[new_falls_at(sem,N,D,tabs) for D in (1,2,3,4)])
print("src slow new_falls M       :",[new_falls_at(recombine(sem,Mrows),N,D,tabs) for D in (1,2,3,4)])
K=Kernel(sem,N)
print("src fast-kernel new_falls M :",[K.new_falls(Mrows,D,{}) for D in (1,2,3,4)])
