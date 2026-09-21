# Independent re-implementation of the LR test + Monte Carlo at N=10, fresh RNG,
# NOT importing the Executor's run_experiment.py.
import math, random
from collections import Counter

ORDER = ["identity","transposition","double_transposition","three_cycle","four_cycle"]
S4 = [1/24,6/24,3/24,8/24,6/24]
A4 = [1/12,0,3/12,8/12,0]
# D4 law from independently-tabulated real data (v_stage0.py output): [6105, 11100, 16050, 0, 11055]/44310
D4 = [6105/44310, 11100/44310, 16050/44310, 0/44310, 11055/44310]

def kl(p, q):
    # D_KL(p || q) = sum p*log(p/q), terms with p==0 contribute 0
    total = 0.0
    for pi, qi in zip(p, q):
        if pi == 0:
            continue
        if qi == 0:
            return float("inf")
        total += pi * math.log(pi/qi)
    return total

print("D_KL(S4||S4) =", kl(S4,S4))
print("D_KL(A4||S4) =", kl(A4,S4))
print("D_KL(D4||S4) =", kl(D4,S4))
print("D_KL(S4||A4) =", kl(S4,A4), " (should be +inf: S4 has mass on transposition/4cycle where A4=0)")
print("D_KL(S4||D4) =", kl(S4,D4), " (should be +inf: S4 has mass on three_cycle where D4=0)")

alpha, beta = 0.05, 0.01
cs_a4 = math.log(1/(alpha*beta)) / kl(A4, S4)
cs_d4 = math.log(1/(alpha*beta)) / kl(D4, S4)
print("Chernoff-Stein N~ln(1/(alpha*beta))/D_KL(sub||full): A4=%.6f D4=%.6f" % (cs_a4, cs_d4))
print("D4 > A4 (predicted ordering)?", cs_d4 > cs_a4)

# Sign-convention / rejection-direction re-derivation:
# LR(sample) = sum_i n_i * log(P_sub(i)/P_full(i))
# Under true S4 data: E[LR] = N * sum_i S4(i) * log(sub(i)/S4(i)) = -N * D_KL(S4 || sub)
# Since sub excludes a category S4 has mass on, D_KL(S4||sub) = +inf => E[LR|S4] = -inf. CONFIRMED analytically.
# Under true sub data: E[LR] = N * sum_i sub(i) * log(sub(i)/S4(i)) = +N * D_KL(sub || S4) >= 0. CONFIRMED (KL>=0 always, Gibbs' inequality).
print()
print("Rejection-direction check: E[LR|S4]=-D_KL(S4||sub)=-inf (since sub excludes an S4-supported class);")
print("E[LR|sub]=+D_KL(sub||S4)>=0 (Gibbs inequality, always non-negative).")
print("=> real S4 data pushes LR very negative, real sub data pushes LR near/above 0.")
print("=> Neyman-Pearson optimal rejection region for 'reject H0:S4 in favor of H1:sub' is LR > threshold (upper tail),")
print("   which is exactly what run_experiment.py implements (LR > threshold classifies as 'it's the subgroup').")
print("This confirms the Executor's chosen convention is the internally consistent, NP-correct one, not merely plausible.")

# ---- Independent Monte Carlo re-implementation at N=10, >=20000 trials, fresh RNG object/style ----
def log_ratio_table(p_full, p_sub):
    tab = []
    NEG = -1e18
    for pf, ps in zip(p_full, p_sub):
        if ps == 0.0:
            tab.append(0.0 if pf == 0.0 else NEG)
        else:
            tab.append(math.log(ps/pf))
    return tab

def draw_categorical_counts(law, n, rng):
    # LITERAL per-draw categorical sampling (not the multinomial shortcut) --
    # deliberately the slow-but-maximally-transparent method, as an independent check
    # on the Executor's claimed equivalence. Use smaller trial count where this matters (N=10 is cheap).
    counts = [0]*len(law)
    cum = []
    running = 0.0
    for p in law:
        running += p
        cum.append(running)
    cum[-1] = 1.0
    for _ in range(n):
        u = rng.random()
        for i, c in enumerate(cum):
            if u <= c:
                counts[i]+=1
                break
    return counts

def lr_from_counts(counts, tab):
    NEG = -1e18
    total = 0.0
    hit = False
    for ni, t in zip(counts, tab):
        if ni == 0: continue
        if t <= NEG:
            hit = True
        total += ni*t
    return NEG if hit else total

def percentile(vals, q):
    vals = sorted(vals)
    if len(vals)==1: return vals[0]
    idx = q*(len(vals)-1)
    lo=int(math.floor(idx)); hi=int(math.ceil(idx))
    if lo==hi: return vals[lo]
    return vals[lo] + (idx-lo)*(vals[hi]-vals[lo])

def power_at_n(sub_law, n, trials, seed):
    rng_full = random.Random(repr(("indep-full", seed, n)))
    rng_sub = random.Random(repr(("indep-sub", seed, n)))
    tab = log_ratio_table(S4, sub_law)
    s4_lrs = [lr_from_counts(draw_categorical_counts(S4, n, rng_full), tab) for _ in range(trials)]
    sub_lrs = [lr_from_counts(draw_categorical_counts(sub_law, n, rng_sub), tab) for _ in range(trials)]
    thr = percentile(s4_lrs, 0.95)
    fp = sum(1 for v in s4_lrs if v > thr)/trials
    power = sum(1 for v in sub_lrs if v > thr)/trials
    se = math.sqrt(power*(1-power)/trials)
    return thr, fp, power, se

TRIALS = 20000
for name, law in [("A4", A4), ("D4", D4)]:
    thr, fp, power, se = power_at_n(law, 10, TRIALS, seed=99)
    print(f"[independent MC, literal per-draw sampling] N=10 S4-vs-{name}: threshold={thr:.6g} fp_rate={fp:.5f} power={power:.5f} se={se:.6f}")
