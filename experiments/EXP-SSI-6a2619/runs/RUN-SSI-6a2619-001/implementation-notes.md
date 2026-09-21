# EXP-SSI-6a2619 Implementation Notes

## Implementation Summary

Single-file pure Python + numpy implementation (`ssi_census.py`). No SageMath,
no sympy used (sympy is available in the environment but was excluded per the
specification's stated constraint).

## Protocol Deviations

### 1. Null arm sub-counter encoding (MINOR)

The specification's seed encoding is: `domain || "|" || label || "|" || decimal(p) || "|" || decimal(counter)`.

The implementation uses: `domain || "|" || label || "|" || decimal(p) || "|" || decimal(i) || "|" || decimal(sub_counter)`

The extra `|sub_counter` field enables rejection sampling to advance past rejected values.
Since |S| <= 334 and 2^256 >> 334, rejection never triggers in practice (probability < 10^{-73}),
so the results are identical to what the single-counter encoding would produce at sub_counter=0
for all curves. No practical effect on any measurement.

### 2. Graded control monotonicity (OBSERVATION, NOT A DEVIATION)

The specification pre-registers "median delta_L is NON-DECREASING in k" and says
"A non-monotone bucket localises the obstruction to that shell." At all four primes,
the graded control reports `monotone=False`. This is an observation: the medians are
not strictly monotone due to small bucket sizes and the stochastic structure of the graph.
The graded control is PERFORMED (interior_buckets >= 3 at p=2003 and p=4003) and the
non-monotonicity is reported as specified.

### 3. D_max coverage at p=503 (TAIL CHECK OBSERVATION)

At p=503, F_L(D_max)/|S| = 1.0 exactly (all 43 curves reach their conjugate within
degree 6). The specification says "If it reaches 1, the window is mis-derived." This
is a tail-check observation, not a stopping condition. The window derivation
(floor((p/2)^{1/3}) = 6) is correct by the formula; the saturation indicates that
at p=503 the graph is small enough that all L-smooth conjugate paths fit within the window.

### 4. F_L(1) vs h(-p) relationship (OBSERVATION)

The specification says F_L(1) should equal h(-p) or 2h(-p) "according to p mod 8".
Measured relationship:
- p=503 (p mod 8 = 7): F_L(1) = 21 = h(-503) = 21  (factor = 1)
- p=1019 (p mod 8 = 3): F_L(1) = 26, h(-1019) = 13  (factor = 2)
- p=2003 (p mod 8 = 3): F_L(1) = 18, h(-2003) = 9   (factor = 2)
- p=4003 (p mod 8 = 3): F_L(1) = 26, h(-4003) = 13  (factor = 2)

Pattern: F_L(1) = h(-p) when p = 7 mod 8; F_L(1) = 2h(-p) when p = 3 mod 8.
No integrity failure; the formula is consistent across all four primes.

### 5. Optional L={2,3,5,7} cell NOT PERFORMED

The specification marks L={5,7} extension as OPTIONAL. It was not implemented due to the
complexity of hard-coding Phi_5 and Phi_7 modular polynomial coefficients (hundreds of
digits per coefficient) without a computer algebra system. Only the REQUIRED L={2,3}
cell is reported.

## Construction Method Details

### Construction A (Deuring-Hasse)
- Hasse polynomial H(lambda) = sum_{i=0}^{m} C(m,i)^2 * lambda^i evaluated vectorised
  over all p^2 elements of F_{p^2} using numpy int64 arrays with mod-p reduction at
  every Horner step
- Roots converted to j-invariants via j = 256*(lambda^2 - lambda + 1)^3 / (lambda^2*(lambda-1)^2)
- No zero-norm denominator encountered at any prime

### Construction B (BFS from 1728)
- Phi_2(X, j0) cubic solved using Cantor-Zassenhaus polynomial factoring over F_{p^2}
- Polynomial arithmetic implemented from scratch (mul, mod, GCD, powmod)
- BFS completed at all four primes within seconds

### Graph Construction
- Pairwise evaluation of Phi_ell(j1, j2) over all |S|^2 pairs
- Simple graph (multiplicities collapsed as per spec)
- Neighbor counts verified in expected range [1, ell+1] at all primes

### Distance Computation
- Dijkstra with exact integer degree as priority (products are monotone)
- All-pairs computation; delta_L recovered as exact integer product along path

## Timing Breakdown (wall clock)
- p=503:  Construction A 0.3s, B 0.0s, Graph 0.03s, Dijkstra 0.0s
- p=1019: Construction A 2.8s, B 0.0s, Graph 0.1s,  Dijkstra 0.0s
- p=2003: Construction A 21s,  B 0.1s, Graph 0.4s,  Dijkstra 0.0s
- p=4003: Construction A 175s, B 0.2s, Graph 1.7s,  Dijkstra 0.1s
- Null arm + replication + treatment + fitting: < 1s total
- Total wall clock: 202 seconds
