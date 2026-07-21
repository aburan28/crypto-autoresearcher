import sys, random
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
for n in [6,9]:
    ms,nb,meta=build_boolean_semaev(n,3,1)
    rng=random.Random(stable_seed("null",n,3,1)); nm=boolean_null(ms,nb,rng)
    s=brute(ms,nb); sn=brute(nm,nb)
    print("n=%d nb=%d : sem #F2 solutions s=%d ; null #F2 solutions=%d"%(n,nb,s,sn), flush=True)
