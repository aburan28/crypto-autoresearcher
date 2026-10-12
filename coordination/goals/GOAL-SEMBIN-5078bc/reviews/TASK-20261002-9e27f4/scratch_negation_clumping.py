"""SCRATCH (TASK-20261002-9e27f4, validator). ABSTRACT cyclic group Z/l only.

Tests STATEMENTS of HEUR-HARVEST-FV-1 (heuristic-restatement.md section 4) on the
NULL object the heuristic itself defines -- a uniformly random negation-closed
list in Z/l -- never on a curve and never on any F_V (card: no N_2 or
decomposition-count measurement of F_V at any scale).

  C1. Clause 1(a) says N_2 "is Poisson-distributed with mean lambda_2". On a
      negation-closed list every non-excluded coincidence a+b=c+d comes with 5
      companions (negation, and the two other 2+2 splits of the zero-sum
      4-set {a, b, -c, -d}), so N_2 = 6 * (number of +-classes of primitive
      zero-sum 4-sets) + rare degenerate terms: compound Poisson, var/mean ~ 6.
  C2. Consequence for the stated Poisson tail check: the null itself exceeds
      the Poisson(lambda_hat_null) tail at p < 1e-3 in a large fraction of lists.
  C3. Clause 1(b): m-multisets containing an inverse pair {a, -a} are counted
      (only "formal identities" are excluded in 1(a), nothing in 1(b)), so for
      m = 3 a target R in F gains |F|/2 decompositions {a, -a, R}; for m = 4 every
      2-decomposition of R gains |F|/2 companions. Heavy tail, not Poisson.

Usage: python3 scratch_negation_clumping.py > scratch_negation_clumping_output.txt
Deterministic (fixed seed). Standard library only.
"""
import itertools
import math
import random
from collections import Counter


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def neg_closed_list(rng, l, r):
    reps = set()
    while len(reps) < r:
        u = rng.randrange(1, l)
        if u not in reps and (l - u) not in reps:
            reps.add(u)
    return sorted(reps | {(l - u) for u in reps})


def N2(lst, l):
    """Clause 1(a) as worded: unordered pairs {{a,b},{c,d}} of 2-subsets with
    a+b = c+d, excluding {a,b}={c,d} and (a=-b and c=-d)."""
    sums = Counter()
    zero_pairs = 0
    for a, b in itertools.combinations(lst, 2):
        s = (a + b) % l
        sums[s] += 1
    tot = 0
    for s, k in sums.items():
        if s == 0:
            continue  # both sides zero is excluded; a pair summing to 0 with a pair summing to 0
        tot += k * (k - 1) // 2
    return tot


def main():
    rng = random.Random(20261003)
    print("C1/C2: N_2 on uniformly random negation-closed lists in Z/l (the clause's own null)")
    for l, r in [(100003, 18), (100003, 26), (1000003, 40), (1000003, 56)]:
        assert is_prime(l)
        F = 2 * r
        lam2 = F ** 4 / (8 * l)
        vals = [N2(neg_closed_list(rng, l, r), l) for _ in range(3000)]
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
        mod6 = sum(v % 6 == 0 for v in vals)
        # Poisson tail at the null's own mean: smallest k with P(X >= k) < 1e-3
        lam = mean
        cdf, k, p = 0.0, 0, math.exp(-lam)
        while 1 - cdf >= 1e-3:
            cdf += p
            k += 1
            p *= lam / k
        exceed = sum(v >= k for v in vals)
        print(f"  l={l} |F|={F}: lambda_2=|F|^4/(8l)={lam2:.3f}; null mean={mean:.3f} var={var:.3f} "
              f"var/mean={var/mean if mean else float('nan'):.2f}; N_2 % 6 == 0 in {mod6}/{len(vals)}; "
              f"Poisson({mean:.3f}) 1e-3 tail starts at k={k}; null lists at/above it: "
              f"{exceed}/{len(vals)} = {exceed/len(vals):.3f}")
    print()
    print("C3: m-decomposition counts with inverse pairs (clause 1(b) as worded), one random list")
    l, r = 10007, 40
    lst = neg_closed_list(rng, l, r)
    S = set(lst)
    F = len(lst)

    def count(R, m, exclude_inverse_pairs):
        c = 0
        for ms in itertools.combinations_with_replacement(lst, m):
            if sum(ms) % l != R:
                continue
            if exclude_inverse_pairs and any((x + y) % l == 0 for x, y in itertools.combinations(ms, 2)):
                continue
            c += 1
        return c
    inF = [x for x in lst[:3]]
    notF = []
    while len(notF) < 3:
        R = rng.randrange(1, l)
        if R not in S:
            notF.append(R)
    for R in inF + notF:
        a = count(R, 3, False)
        b = count(R, 3, True)
        print(f"  m=3 R={R:5d} (R in F: {R in S}): count as worded={a}, without inverse pairs={b}, "
              f"difference={a-b} (|F|/2={F//2})")
    mean3 = math.comb(F + 2, 3) / l
    print(f"  m=3 Poisson mean |F|^3/(3! l) ~ {F**3/(6*l):.2f}; exact multiset mean binom(|F|+2,3)/l = {mean3:.2f}")


if __name__ == "__main__":
    main()
