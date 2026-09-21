import sys, random
from math import comb
EXP = "/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-005"
sys.path.insert(0, EXP + "/src")
load(EXP + "/src/h013_f5_signatures.sage")

def brute(monosets, nb):
    polys=[list(f) for f in monosets]; c=0
    for bits in range(1<<nb):
        ok=True
        for f in polys:
            v=0
            for mono in f:
                m=1
                for i in mono:
                    if not (bits>>i)&1: m=0; break
                v^=m
            if v: ok=False; break
        if ok: c+=1
    return c

n=6
monosets, nb, meta = build_boolean_semaev(n,3,1)
s=brute(monosets,nb)
rng=random.Random(stable_seed("null",n,3,1)); null_ms=boolean_null(monosets,nb,rng)
s_null=brute(null_ms,nb)
print("n=6 nb=%d  sem #F2 solutions s=%d ; null #F2 solutions=%d  (d_reg(null,semi-reg)=5)"%(nb,s,s_null), flush=True)
print(" D | q_sem=ncols-rank | q_null | note", flush=True)
d_reg_sem=None; d_reg_null=None
for D in range(2,11):
    rs,*_=analyze_syzygy_space(monosets,nb,D,extract=False,block_size=n)
    rn,*_=analyze_syzygy_space(null_ms,nb,D,extract=False,block_size=n)
    qs=rs["ncols"]-rs["rank"]; qn=rn["ncols"]-rn["rank"]
    if d_reg_sem is None and qs==s: d_reg_sem=D
    if d_reg_null is None and qn==s_null: d_reg_null=D
    note=""
    if qs==s: note+="sem@s "
    if qn==s_null: note+="null@s"
    print("  %2d | %6d | %6d | %s"%(D,qs,qn,note), flush=True)
print("=> d_reg(sem, q->s=%d) = %s ; d_reg(null, q->s=%d) = %s"%(s,d_reg_sem,s_null,d_reg_null), flush=True)
