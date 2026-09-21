import sys, os, json, random
from math import comb
EXP = "/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-005"
sys.path.insert(0, EXP + "/src")
load(EXP + "/src/h013_f5_signatures.sage")

def buggy_pred(eq_degs, nb, Dmax):
    a=[comb(nb,j) if j<=nb else 0 for j in range(Dmax+2)]
    for d in eq_degs:
        for j in range(d,Dmax+2): a[j]-=a[j-d]
    HF=[];ok=True
    for d in range(Dmax+2):
        if not ok or a[d]<=0:
            HF.append(0)
            if a[d]<=0: ok=False
        else: HF.append(a[d])
    pred={};tot=0
    for D in range(Dmax+1): tot+=comb(nb,D)-HF[D]; pred[D]=tot
    return pred

def correct_pred(eq_degs, nb, Dmax):
    a=[comb(nb,j) if j<=nb else 0 for j in range(Dmax+2)]
    for d in eq_degs:
        b=a[:]
        for j in range(d,Dmax+2): b[j]=a[j]-a[j-d]
        a=b
    HF=[];ok=True
    for d in range(Dmax+2):
        if not ok or a[d]<=0:
            HF.append(0)
            if a[d]<=0: ok=False
        else: HF.append(a[d])
    pred={};tot=0
    for D in range(Dmax+1): tot+=comb(nb,D)-HF[D]; pred[D]=tot
    return pred

n, t, seed = 9, 3, 1
monosets, nb, meta = build_boolean_semaev(n, t, seed)
eq_degs = [max(mono_deg(m) for m in f) for f in monosets]
print("n=%d nb=%d n_eqs=%d eq_deg_hist=%s" % (n, nb, len(monosets),
      {d: eq_degs.count(d) for d in sorted(set(eq_degs))}))
rng = random.Random(stable_seed("null", n, t, seed))
null_ms = boolean_null(monosets, nb, rng)

bp = buggy_pred(eq_degs, nb, 6); cp = correct_pred(eq_degs, nb, 6)
full = {D: sum(comb(nb,j) for j in range(D+1)) for D in range(7)}
print("\n D | arm  | nrows | ncols | rank  | full_cols | pred_BUGGY | pred_CORRECT | rank-buggy | rank-correct")
for D in range(3, 7):
    for arm, ms in (("sem", monosets), ("null", null_ms)):
        rec, *_ = analyze_syzygy_space(ms, nb, D, extract=False, block_size=n)
        print(" %d | %-4s | %5d | %5d | %5d | %9d | %10d | %12d | %+10d | %+12d" % (
            D, arm, rec["nrows"], rec["ncols"], rec["rank"], full[D],
            bp[D], cp[D], rec["rank"]-bp[D], rec["rank"]-cp[D]))
