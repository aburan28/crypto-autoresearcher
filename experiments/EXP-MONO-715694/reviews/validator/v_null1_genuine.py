# Independent supplementary check: a GENUINE null-object control for NULL-1/NULL-2,
# distinct from what was actually implemented (sub_law==full_law, which makes the
# LR table identically zero regardless of RNG and therefore cannot fail by construction).
#
# The genuine null-object question: using the REAL calibrated S4-vs-A4 and S4-vs-D4
# thresholds (calibrated from one S4-generated batch), what is the classification
# rate of a FRESH, INDEPENDENT, out-of-sample S4-generated batch (not the
# calibration batch itself)? This directly probes whether the empirical
# (1-alpha)-quantile threshold estimate, built from a finite 20,000-trial batch,
# generalizes to control the false-positive rate near alpha=0.05 on new S4 data,
# which is exactly what a real "S4 vs an independent second S4 stream" control
# should measure and which the as-implemented NULL-1 (log_ratio_table(S4,S4)=0
# everywhere) cannot measure at all.
import math, random

S4 = [1/24,6/24,3/24,8/24,6/24]
A4 = [1/12,0,3/12,8/12,0]
D4 = [6105/44310, 11100/44310, 16050/44310, 0/44310, 11055/44310]
NEG = -1e18

def log_ratio_table(p_full,p_sub):
    return [0.0 if (ps==0.0 and pf==0.0) else (NEG if ps==0.0 else math.log(ps/pf)) for pf,ps in zip(p_full,p_sub)]

def cumulative(law):
    cum=[]; running=0.0
    for p in law: running+=p; cum.append(running)
    cum[-1]=1.0
    return cum

def draw_counts(law,cum,n,rng):
    counts=[0]*len(law)
    for _ in range(n):
        u=rng.random()
        for i,c in enumerate(cum):
            if u<=c: counts[i]+=1; break
    return counts

def lr_from_counts(counts,tab):
    total=0.0; hit=False
    for ni,t in zip(counts,tab):
        if ni==0: continue
        if t<=NEG: hit=True
        total+=ni*t
    return NEG if hit else total

def percentile(vals,q):
    vals=sorted(vals)
    if len(vals)==1: return vals[0]
    idx=q*(len(vals)-1); lo=int(math.floor(idx)); hi=int(math.ceil(idx))
    if lo==hi: return vals[lo]
    return vals[lo]+(idx-lo)*(vals[hi]-vals[lo])

TRIALS = 20000
cum_s4 = cumulative(S4)

for name, sub in [("A4", A4), ("D4", D4)]:
    tab = log_ratio_table(S4, sub)
    n = 10
    # calibration batch (in-sample threshold, as the real Stage-2 does)
    rng_cal = random.Random(repr(("null-genuine-cal", name, n, 1)))
    cal_lrs = [lr_from_counts(draw_counts(S4, cum_s4, n, rng_cal), tab) for _ in range(TRIALS)]
    threshold = percentile(cal_lrs, 0.95)
    # genuine held-out null batch: a FRESH, independent S4 stream, never seen by calibration
    rng_null = random.Random(repr(("null-genuine-heldout", name, n, 2)))
    null_lrs = [lr_from_counts(draw_counts(S4, cum_s4, n, rng_null), tab) for _ in range(TRIALS)]
    fp_out_of_sample = sum(1 for v in null_lrs if v > threshold) / TRIALS
    fp_in_sample = sum(1 for v in cal_lrs if v > threshold) / TRIALS
    print(f"S4-vs-{name} @ N=10: threshold={threshold:.6g}  in-sample FP={fp_in_sample:.5f}  "
          f"OUT-OF-SAMPLE FP (genuine null-object, independent 2nd S4 stream)={fp_out_of_sample:.5f}")
