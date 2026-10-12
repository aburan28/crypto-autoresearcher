# Protocol: does any curve isogenous to a Koblitz curve make Pollard rho faster?

Frozen before the main run (2026-10-05). Toy-scale proxy for ECC2K-130.

## Object
Koblitz curve E: y^2 + xy = x^3 + 1 over F_2^37 (modulus x^37+x^9+x^2+x+1),
#E = 4 * 149 * l, l = 230603167 (prime, ~2^27.78). Same mechanism as ECC2K-130
(Koblitz, a=0, End = Z[(1+sqrt(-7))/2], prime extension degree), smaller scale.

Isogenous curves: 8 curves I1..I8 obtained by explicit 73-isogenies from E
(PARI/GP `iso.gp`; 73 is the smallest prime dividing the conductor
[O_K : Z[pi]] = 73 * 2663). Each image verified #I_i(F_q) = #E(F_q), j(I_i) != j(E),
and all j-invariants pairwise distinct. `curves.txt` holds the output.

## Arms
- K-tau : E, classes {+-tau^i R} (negation + Frobenius)
- K-neg : E, classes {+-R} (control: same curve, Frobenius unused)
- I1..I8: isogenous curves, classes {+-R} (the only automorphisms they have;
  the solver refuses mode tau on them because tau is not an endomorphism)

## Solver (rho.c, identical code for every arm)
vOW distinguished points (theta = 2^-5), r = 128 adding walk, BKL look-ahead,
cycle escape by doubling. Counted: every group op after Q is known
(R_j setup, walk starts, walk steps, look-aheads, cycle escapes). Not counted:
Q-independent multiples of P (same on every curve). Every solution checked
against the secret AND by recomputing [k]P == Q.

## Sample plan
n = 5000 solves per arm, random secret per solve, run sequentially on one
pinned core in 10 round-robin chunks of 500 per arm (seed = 1000*arm + round),
so drift spreads evenly across arms. Per-step timing: separate benchmark,
2^20 steps x 21 reps per arm, interleaved round-robin, pinned core.

## Pre-declared analysis (alpha = 0.05)
0. Validity: 100% verified solutions, else the arm is invalid.
1. H1 "some isogenous curve is faster than K-tau": one-sided Mann-Whitney
   (I_i < K-tau) on ops and on wall-clock seconds, Holm over 8 curves; ratio
   of means with 95% bootstrap CI (10,000 resamples).
2. H2 "curve choice within the class changes rho cost (absent tau)":
   Kruskal-Wallis over {K-neg, I1..I8} on ops and on seconds; TOST
   equivalence of each I_i vs K-neg, ratio of means, margin +-5% (90% CI).
3. Per-step ns: Kruskal-Wallis over the 9 negation-only arms; equivalence
   margin +-3% vs K-neg on medians (bootstrap 90% CI).
4. Speedup K-neg/K-tau in ops and in seconds with 95% CI, against
   sqrt(37) = 6.08.
5. Theory fit: mean ops / sqrt(pi*l/(2*|class|)) per arm (descriptive).

## Scope
Results are scoped to m = 37, this solver and this hardware. Transfer to
ECC2K-130 (m = 131) rests on the algebraic argument, not on this measurement.
