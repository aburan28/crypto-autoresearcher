# ITEM 3: independent, supplementary, exploratory fine-grained N in {1..9} search,
# using the identical LR-test procedure/calibration convention as the frozen contract,
# with fresh code (not importing run_experiment.py) and fresh RNG streams.
import math, random

ORDER = ["identity","transposition","double_transposition","three_cycle","four_cycle"]
S4 = [1/24,6/24,3/24,8/24,6/24]
A4 = [1/12,0,3/12,8/12,0]
D4 = [6105/44310, 11100/44310, 16050/44310, 0/44310, 11055/44310]  # independently tabulated in v_stage0.py

NEG = -1e18

def log_ratio_table(p_full, p_sub):
    tab = []
    for pf, ps in zip(p_full, p_sub):
        if ps == 0.0:
            tab.append(0.0 if pf == 0.0 else NEG)
        else:
            tab.append(math.log(ps/pf))
    return tab

def cumulative(law):
    cum=[]; running=0.0
    for p in law:
        running+=p; cum.append(running)
    cum[-1]=1.0
    return cum

def draw_counts(law, cum, n, rng):
    counts=[0]*len(law)
    for _ in range(n):
        u = rng.random()
        for i,c in enumerate(cum):
            if u<=c:
                counts[i]+=1
                break
    return counts

def lr_from_counts(counts, tab):
    total=0.0; hit=False
    for ni,t in zip(counts, tab):
        if ni==0: continue
        if t<=NEG: hit=True
        total += ni*t
    return NEG if hit else total

def percentile(vals, q):
    vals=sorted(vals)
    if len(vals)==1: return vals[0]
    idx=q*(len(vals)-1)
    lo=int(math.floor(idx)); hi=int(math.ceil(idx))
    if lo==hi: return vals[lo]
    return vals[lo]+(idx-lo)*(vals[hi]-vals[lo])

def power_at_n(sub_law, n, trials, seed, tag):
    cum_full = cumulative(S4)
    cum_sub = cumulative(sub_law)
    tab = log_ratio_table(S4, sub_law)
    rng_full = random.Random(repr(("fine-full", tag, seed, n)))
    rng_sub = random.Random(repr(("fine-sub", tag, seed, n)))
    s4_lrs = [lr_from_counts(draw_counts(S4, cum_full, n, rng_full), tab) for _ in range(trials)]
    sub_lrs = [lr_from_counts(draw_counts(sub_law, cum_sub, n, rng_sub), tab) for _ in range(trials)]
    thr = percentile(s4_lrs, 0.95)
    fp = sum(1 for v in s4_lrs if v>thr)/trials
    power = sum(1 for v in sub_lrs if v>thr)/trials
    se = math.sqrt(power*(1-power)/trials)
    return thr, fp, power, se

TRIALS = 20000
print(f"{'N':>3} | {'A4 power':>9} {'A4 SE':>8} {'A4 FP':>8} | {'D4 power':>9} {'D4 SE':>8} {'D4 FP':>8}")
n_req_a4 = None
n_req_d4 = None
rows = []
for n in range(1, 10):
    thr_a, fp_a, pow_a, se_a = power_at_n(A4, n, TRIALS, seed=777, tag="a4")
    thr_d, fp_d, pow_d, se_d = power_at_n(D4, n, TRIALS, seed=777, tag="d4")
    rows.append((n, pow_a, se_a, fp_a, pow_d, se_d, fp_d))
    print(f"{n:>3} | {pow_a:>9.5f} {se_a:>8.6f} {fp_a:>8.5f} | {pow_d:>9.5f} {se_d:>8.6f} {fp_d:>8.5f}")
    if n_req_a4 is None and pow_a >= 0.99:
        n_req_a4 = n
    if n_req_d4 is None and pow_d >= 0.99:
        n_req_d4 = n

print()
print("Independent exploratory N_required(S4 vs A4) at N in 1..9:", n_req_a4)
print("Independent exploratory N_required(S4 vs D4) at N in 1..9:", n_req_d4)
if n_req_a4 is not None and n_req_d4 is not None:
    print("Predicted ordering N_required(D4) > N_required(A4) emerges in this finer grid?", n_req_d4 > n_req_a4)
elif n_req_a4 is not None and n_req_d4 is None:
    print("A4 already resolved within 1..9 but D4 is NOT -- consistent with predicted ordering (D4 harder), pending N>=10 (already known: both resolve by N=10).")
