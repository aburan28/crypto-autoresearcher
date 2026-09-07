# ITEM 5: independently tabulate N3 histograms and re-derive step4b classification
# with fresh code, fresh thresholds recalibrated at N=2000 and N=44310.
import json, math, random, sys

ORDER = ["identity","transposition","double_transposition","three_cycle","four_cycle"]
LABEL_MAP = {"1^4":"identity","2.1.1":"transposition","2^2":"double_transposition","3+1":"three_cycle","4":"four_cycle"}
S4 = [1/24,6/24,3/24,8/24,6/24]
A4 = [1/12,0,3/12,8/12,0]
D4 = [6105/44310, 11100/44310, 16050/44310, 0/44310, 11055/44310]
NEG = -1e18

def tabulate_n3(path):
    counts = {c:0 for c in ORDER}
    used=0; discarded=0; total=0
    with open(path) as f:
        for line in f:
            line=line.strip()
            if not line: continue
            total+=1
            rec=json.loads(line)
            if rec.get("discarded"):
                discarded+=1
                continue
            ct = LABEL_MAP[rec["label"]]
            counts[ct]+=1
            used+=1
    return total, used, discarded, [counts[c] for c in ORDER]

def log_ratio_table(p_full,p_sub):
    tab=[]
    for pf,ps in zip(p_full,p_sub):
        tab.append(0.0 if ps==0.0 and pf==0.0 else (NEG if ps==0.0 else math.log(ps/pf)))
    return tab

def lr_from_counts(counts, tab):
    total=0.0; hit=False
    for ni,t in zip(counts,tab):
        if ni==0: continue
        if t<=NEG: hit=True
        total+=ni*t
    return NEG if hit else total

def cumulative(law):
    cum=[]; running=0.0
    for p in law: running+=p; cum.append(running)
    cum[-1]=1.0
    return cum

def draw_multinomial_literal(law,cum,n,rng):
    counts=[0]*len(law)
    for _ in range(n):
        u=rng.random()
        for i,c in enumerate(cum):
            if u<=c: counts[i]+=1; break
    return counts

def percentile(vals,q):
    vals=sorted(vals)
    if len(vals)==1: return vals[0]
    idx=q*(len(vals)-1); lo=int(math.floor(idx)); hi=int(math.ceil(idx))
    if lo==hi: return vals[lo]
    return vals[lo]+(idx-lo)*(vals[hi]-vals[lo])

def calibrate_threshold(sub_law, n, trials, seed, tag):
    cum = cumulative(S4)
    tab = log_ratio_table(S4, sub_law)
    rng = random.Random(repr(("indep-thr", tag, seed, n)))
    lrs = [lr_from_counts(draw_multinomial_literal(S4, cum, n, rng), tab) for _ in range(trials)]
    return percentile(lrs, 0.95), tab

repo = sys.argv[1]
n3_run1 = repo+"/experiments/EXP-MONO-a20e48/runs/RUN-MONO-a20e48-1/per_base_point_log/N3_k1.jsonl"
n3_run2 = repo+"/experiments/EXP-MONO-a20e48/runs/RUN-MONO-a20e48-2/per_base_point_log/N3_k1.jsonl"

for label, path in [("run1", n3_run1), ("run2", n3_run2)]:
    total, used, discarded, vec = tabulate_n3(path)
    print(f"N3 {label}: total_rows={total} used={used} discarded={discarded} counts={vec}")

# Use N=2000 threshold recalibrated independently, 20000 trials (matches contract's own trial count)
TRIALS = 20000
thr_a4_2000, tab_a4 = calibrate_threshold(A4, 2000, TRIALS, seed=555, tag="a4")
thr_d4_2000, tab_d4 = calibrate_threshold(D4, 2000, TRIALS, seed=555, tag="d4")
print(f"\nIndependent recalibrated threshold at N=2000: A4={thr_a4_2000:.6g}  D4={thr_d4_2000:.6g}")

for label, path in [("run1", n3_run1), ("run2", n3_run2)]:
    total, used, discarded, vec = tabulate_n3(path)
    lr_a4 = lr_from_counts(vec, tab_a4)
    lr_d4 = lr_from_counts(vec, tab_d4)
    cls_a4 = lr_a4 > thr_a4_2000
    cls_d4 = lr_d4 > thr_d4_2000
    print(f"N3 {label}: LR_vs_A4={lr_a4:.4g} classified_as_sub={cls_a4} | LR_vs_D4={lr_d4:.4g} classified_as_sub={cls_d4}")
    print(f"  Expected: classifies as S4 (not A4, not D4) -> classified_as_sub should be False for both: {'MATCH' if (cls_a4==False and cls_d4==False) else 'MISMATCH'}")

# N1 exhaustive check at N=44310, independently recalibrated
thr_a4_44310, tab_a4_44 = calibrate_threshold(A4, 44310, TRIALS, seed=555, tag="a4-44310")
thr_d4_44310, tab_d4_44 = calibrate_threshold(D4, 44310, TRIALS, seed=555, tag="d4-44310")
n1_vec = [6105, 11100, 16050, 0, 11055]  # independently tabulated in v_stage0.py
lr_a4_n1 = lr_from_counts(n1_vec, tab_a4_44)
lr_d4_n1 = lr_from_counts(n1_vec, tab_d4_44)
cls_a4_n1 = lr_a4_n1 > thr_a4_44310
cls_d4_n1 = lr_d4_n1 > thr_d4_44310
print(f"\nN1 exhaustive (both runs, identical vec): LR_vs_A4={lr_a4_n1:.6g} classified_as_sub={cls_a4_n1} | LR_vs_D4={lr_d4_n1:.6g} classified_as_sub={cls_d4_n1}")
print(f"  Expected: classifies as D4 (not S4, not A4) -> should be A4:False, D4:True: {'MATCH' if (cls_a4_n1==False and cls_d4_n1==True) else 'MISMATCH'}")
