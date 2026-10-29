#!/usr/bin/env python3
"""Blind re-derivation from specification.yaml only (not run.py/check.py).
Spec: xorshift32 from seed 20261017; each draw counts steps until state % 50 == 0
("stop when the state is divisible by 50"); 64 draws; xorshift32 shifts 13,17,5
(the standard Marsaglia triple; the spec does not state them -> recorded as underspecification).
Draw k counts the stopping state itself (k>=1); the spec says 'geometric counts' so support {1,2,..}.
Draw i+1 continues from the state at which draw i stopped (spec silent: variant B restarts from seed).
"""
import json, sys
M = 0xFFFFFFFF
def step(x):
    x ^= (x << 13) & M; x ^= x >> 17; x ^= (x << 5) & M
    return x & M
def sample(seed, n, p, continue_state=True):
    s, out = seed, []
    for _ in range(n):
        if not continue_state: s = seed
        k = 0
        while True:
            s = step(s); k += 1
            if s % p == 0: break
        out.append(k)
    return out
def moments(d):
    n = len(d); sd = sorted(d)
    S = sum(d); Q = sum(v*v for v in d)
    med_lo, med_hi = sd[n//2-1], sd[n//2]
    num, den = n*Q - S*S, S*S           # CV^2 = num/den
    cv_ok = 81*den <= 100*num <= 121*den
    mr_ok = 3*n*1 <= 0 or (5*med_lo*n >= 3*S and 5*med_lo*n <= 4*S)
    return dict(sample_sum=S, sum_squares=Q, median=med_lo, split=med_lo != med_hi, cv_in_band=cv_ok, median_ratio_in_band=mr_ok)
if __name__ == "__main__":
    a = moments(sample(20261017, 64, 50, True))
    b = moments(sample(20261017, 64, 50, False))
    claimed = json.load(open(sys.argv[1]))
    print("variant A (continue state):", a)
    print("variant B (restart seed):  ", b)
    keys = ["sample_sum","sum_squares","median","cv_in_band","median_ratio_in_band"]
    print("claimed:", {k: claimed[k] for k in keys})
    print("A matches claimed:", all(a[k]==claimed[k] for k in keys))
