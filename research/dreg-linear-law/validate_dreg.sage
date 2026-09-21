import sys, random
from math import comb
EXP = "/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-005"
sys.path.insert(0, EXP + "/src")
load(EXP + "/src/h013_f5_signatures.sage")

def model(n,N=40):
    nb=2*n; a=[comb(nb,j) if j<=nb else 0 for j in range(N)]
    for d in ([2]*n+[3]*n):
        for j in range(d,N): a[j]-=a[j-d]
    return a
def pred_dreg(n):
    a=model(n); return next(D for D in range(len(a)) if a[D]<=0)
def sr_pred_cum(n,D):
    a=model(n); HF=[];ok=True
    for d in range(len(a)):
        if not ok or a[d]<=0:
            HF.append(0)
            if a[d]<=0: ok=False
        else: HF.append(a[d])
    tot=0
    for dd in range(D+1): tot+=comb(2*n,dd)-HF[dd]
    return tot

for n in [6, 9]:
    dr=pred_dreg(n)
    monosets, nb, meta = build_boolean_semaev(n, 3, 1)
    rng=random.Random(stable_seed("null",n,3,1)); null_ms=boolean_null(monosets,nb,rng)
    print("=== n=%d  nb=%d  PREDICTED d_reg=%d ===" % (n,nb,dr))
    print("  D | null: rank==sr_pred? quo | sem: quo  | (quo=ncols-rank; null collapses at d_reg)")
    for D in range(2, 7):
        rn,*_=analyze_syzygy_space(null_ms,nb,D,extract=False,block_size=n)
        rs,*_=analyze_syzygy_space(monosets,nb,D,extract=False,block_size=n)
        srp=sr_pred_cum(n,D)
        qn=rn["ncols"]-rn["rank"]; qs=rs["ncols"]-rs["rank"]
        tag = "<-- D>=d_reg: NULL COLLAPSED" if D>=dr else ("match" if rn["rank"]==srp else "MISMATCH")
        print("  %d | rank=%d sr_pred=%d %-6s quo_null=%5d | quo_sem=%5d %s" % (
            D, rn["rank"], srp, "OK" if rn["rank"]==srp else "NEQ", qn, qs, tag))
