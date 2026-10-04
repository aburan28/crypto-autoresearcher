"""Null-model control: is 'four lambdas with a full 131-orbit' a signal or the
generic outcome?

Null model.  Fix x in K with deg_F2(x) = 131 (so 1, x, ..., x^6 are F_2-independent,
as 131 > 7).  For lambda(X) = X^d + sum_{i<d} c_i X^i with the c_i uniform, the value
sum_i c_i x^i is uniform on the 2^d-element F_2-span V_x of {1,...,x^{d-1}}, so
   P[x is a root] = 2^{-d} * 1[ x^(2^33) + x^d  in  V_x ],
and modelling x^(2^33)+x^d as uniform in K gives P[in V_x] = 2^d/2^131, hence
   E[# non-F_2 roots per lambda] ~ 2^131 * 2^d/2^131 * 2^{-d} = 1.
Non-F_2 roots arrive only in Frobenius orbits of size 131 (131 prime), so the
expected number of lambdas carrying a full orbit is ~ 244/131.
Separately E[# F_2 roots] = P[lambda(0)=0] + P[lambda(1)=1] = 1/2 + 1/2 = 1.
"""
import json, math
d = json.load(open('../out/rederivation_results.json'))
counts = {int(k): v for k, v in d['all_counts'].items()}
n = 131
tot = sum(counts.values())
f2 = sum((1 if (l & 1) == 0 else 0) + (1 if bin(l).count('1') % 2 == 1 else 0)
         for l in counts)
allroots = sum(counts.values()) and sum(counts[l] for l in counts)
clumps = sum(1 for l in counts if counts[l] > 2)
print(f'candidates                              : {len(counts)}')
print(f'total roots found                       : {allroots}')
print(f'  of which F_2 roots (0 and 1)          : {f2}   -> {f2/len(counts):.3f} per lambda'
      f'   [null model predicts 1.000]')
print(f'  of which non-F_2 roots                : {allroots-f2} -> '
      f'{(allroots-f2)/len(counts):.3f} per lambda  [null model predicts ~1]')
print(f'lambdas carrying a full 131-orbit       : {clumps}   '
      f'[null model predicts {len(counts)/n:.2f}]')
lam_ = len(counts) / n
p_ge = 1 - sum(math.exp(-lam_) * lam_**k / math.factorial(k) for k in range(clumps))
print(f'Poisson(mean {lam_:.2f}) P[>= {clumps} such lambdas]    : {p_ge:.3f}')
print()
print('The involution lambda(X) -> lambda(X+1)+1 pairs them, so the number of')
print('INDEPENDENT events is 2, against an expected 244/(2*131) = '
      f'{len(counts)/(2*n):.2f} pairs;')
lam2 = len(counts) / (2 * n)
p2 = 1 - sum(math.exp(-lam2) * lam2**k / math.factorial(k) for k in range(2))
print(f'Poisson(mean {lam2:.2f}) P[>= 2 pairs] = {p2:.3f}')
print()
print('CONCLUSION (stated as a control, not as a finding):')
print('  the observed maximum is exactly 1 + 131 = one F_2 root plus ONE Frobenius')
print('  orbit, which is the smallest non-trivial value the orbit structure permits')
print('  above 2, and the number of lambdas reaching it is consistent with the null')
print('  model at ordinary significance.  Nothing in this computation is evidence that')
print('  the four maximizing lambdas are algebraically special; they are the lambdas')
print('  that happened to pick up one orbit.  A claim that they are special would need')
print('  its own evidence, which this task neither sought nor produced.')
print()
print('Sanity check on the null model at small n, where 2^n\' can be SMALLER than n:')
print("  n=11, n'=3: deg L = max(2^3, d) = 8 < 11, so a non-F_2 root would need 11")
print('  conjugates inside a degree-8 polynomial -- impossible.  The n=11 sweep indeed')
print('  found NO non-F_2 roots at all (histogram {0:62, 1:124, 2:62}), which is a')
print("  prediction of the structure, not an accident.  For n=131, n'=33, deg L = 2^33")
print('  >> 131, so the obstruction is absent and orbits are possible -- as observed.')
