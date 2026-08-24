# Hybrid MITM-Decomposition Analysis

**Task**: TASK-20260804-138  
**Batch**: BATCH-099  
**Goal**: GOAL-ECDLP-001  
**Date**: 2026-08-04

---

## Setup

Let E be an elliptic curve over F_p with a prime-order subgroup of order N, and let
G be a generator. The ECDLP instance is: given Q in <G>, find k in [0, N) such that
[k]G = Q.

The proposed hybrid writes k in a "mixed radix" form:

    k = a * N^{1/4} + b

where:
- a in A = [0, N^{3/4})   (the "large" part, |A| = N^{3/4})
- b in B = [0, N^{1/4})   (the "small" part, |B| = N^{1/4})

Since a * N^{1/4} + b ranges over [0, N^{3/4} * N^{1/4} + N^{1/4}) = [0, N + N^{1/4}),
and k < N, every k in [0, N) has at least one such representation. The bijection is
well-defined modulo N.

The corresponding group identity is:

    Q = [k]G = [a * N^{1/4}]G + [b]G =: P_a + R_b

where P_a = [a * N^{1/4}]G and R_b = [b]G.

The MITM approach builds two tables T1 = {P_a : a in A} and T2 = {R_b : b in B}
and looks for a pair (P_a, R_b) such that P_a + R_b = Q, i.e. P_a = Q - R_b.

---

## The AM-GM lower bound for two-table MITM

**Theorem (BSGS lower bound).** Let A, B be finite sets and f: A x B -> Z_N a
function with the property that for the target k, there exist a in A, b in B with
f(a, b) = k (coverage condition). Any two-table algorithm that:

1. Precomputes table T1 = {g(a) : a in A} of cost Theta(|A|), and
2. Precomputes table T2 = {h(b) : b in B} of cost Theta(|B|), and
3. Finds a collision T1[a] + T2[b] = Q,

has total cost Theta(|A| + |B|).

For the collision to succeed with probability 1 over a uniformly random k in Z_N,
the tables must together cover all of Z_N:

    |A| * |B| >= N.

By the AM-GM inequality:

    |A| + |B| >= 2 * sqrt(|A| * |B|) >= 2 * sqrt(N).

Equality holds when |A| = |B| = N^{1/2}, which is precisely Baby-step Giant-step
(BSGS). The lower bound Omega(sqrt(N)) is therefore achieved by BSGS, and no
two-table MITM can do better.

**Applied to the proposed hybrid.** With |A| = N^{3/4} and |B| = N^{1/4}:

    |A| + |B| = N^{3/4} + N^{1/4} = Theta(N^{3/4}).

This is strictly worse than BSGS. The decomposition k = a * N^{1/4} + b does not
improve on the symmetric split k = a * N^{1/2} + b; it merely shifts mass from the
small table to the large one. By AM-GM, any asymmetric split of the (|A|, |B|) pair
away from (N^{1/2}, N^{1/2}) increases |A| + |B|.

---

## Can index calculus "replace" one table?

The motivation for introducing b in [0, N^{1/4}) is that N^{1/4} is small, raising
the hope that index calculus over a factor base F of size B_0 = N^epsilon can compute
discrete logs in the range [0, N^{1/4}) faster than a direct table of size N^{1/4}.

**Why this fails for prime-order curves.**

Index calculus in Z_N^* exploits the multiplicative structure of the integers: a
smooth integer factors completely over a factor base {p_1, ..., p_{B_0}}, and
collecting O(B_0) such relations over-determines the system log_{g}(p_i), so the
full discrete log in Z_N^* costs roughly exp(O(sqrt(log N log log N))). This sub-
exponential improvement is possible because:

(a) The group Z_N^* embeds naturally into Z (via the ring structure of Z), and
(b) Random elements of Z_N^* have a non-negligible probability of being B_0-smooth,
    which decays slowly as a function of N.

Neither condition holds for a generic prime-order elliptic curve group:

(a) The group <G> has no ring structure. There is no analogue of "smooth element"
    for a group element [b]G — smoothness is a property of integers, not of elliptic
    curve points.

(b) Computing the discrete log of [b]G for b in [0, N^{1/4}) is itself an ECDLP
    instance over the same curve. There is no sub-exponential reduction from the
    small-range ECDLP to a system of linear equations.

**Formalizing the reduction argument.**

Suppose an oracle O_small solves the small-range ECDLP: given R in <G>, determine
whether R = [b]G for some b in [0, N^{1/4}), and if so, return b. Any algorithm
that uses O_small to solve the full ECDLP must call O_small with inputs of the form
Q - P_a = Q - [a * N^{1/4}]G for each candidate a. If a is unknown (as it is), this
requires either:

- Iterating over all a in [0, N^{3/4}) and calling O_small each time: cost
  N^{3/4} * cost(O_small) >= N^{3/4}, which is worse than BSGS even if O_small is
  free.

- Or precomputing the "large" table {P_a : a in [0, N^{3/4})} first, then matching
  Q - P_a against the small-range ECDLP results. This requires the large table of
  size N^{3/4}, again worse than BSGS.

In either case, a non-trivial use of O_small forces the large table cost, and the
AM-GM argument from the previous section applies.

**Index calculus in the hidden-number problem and lattice settings.**

One might object that lattice-based hybrid algorithms (e.g., for the hidden number
problem) do beat BSGS. This is true, but those algorithms exploit additional
structure not present in the generic ECDLP:

- The hidden number problem has a *linear* constraint relating multiple ECDLP
  instances (e.g., known partial bits of the nonce), enabling lattice reduction.
- The short-integer solution problem has a *ring* structure that makes lattice
  attacks efficient.
- Index calculus on hyperelliptic curves of genus g >= 2 works because the Jacobian
  has a non-trivial algebraic structure that embeds into a vector space.

For a prime-order elliptic curve with no auxiliary structure, none of these
reductions apply. The group <G> is cyclic of prime order and acts as a black-box
group for the purposes of ECDLP algorithms (Shoup's generic group lower bound: any
algorithm making T queries to the group oracle solves the ECDLP with probability at
most O(T^2 / N), confirming Omega(sqrt(N)) is tight).

**Amortization does not help.**

One might further argue that index calculus amortizes the cost of computing many
small-range logs simultaneously. This is accurate: if we need to compute discrete
logs for M distinct small-range targets R_1, ..., R_M, index calculus over a factor
base of size B_0 costs roughly O(B_0^2 + M) group operations in Z_N^* — each new
target costs only O(1) after the initial sieve. However, on elliptic curves:

- There is no sieve: finding a relation [b]G = sum_i e_i * F_i for factor base
  elements F_i requires solving an ECDLP, which is the original problem.
- Even granting a hypothetical elliptic curve "sieve" that produced relations at
  cost C each, generating B_0 + 1 independent relations to solve the linear system
  costs (B_0 + 1) * C. For the small-range ECDLP, B_0 = O(N^{1/4}) (to cover the
  range), so this is not better than a direct table.

---

## Conclusion: hybrid doesn't beat sqrt(N) for prime-order curves

The hybrid MITM-decomposition approach k = a * N^{1/4} + b does not improve on
Baby-step Giant-step (BSGS) for any of the following reasons:

1. **AM-GM is binding.** The two-table MITM cost |A| + |B| >= 2 sqrt(N) is
   minimized at |A| = |B| = N^{1/2}, achieved by BSGS. The (N^{3/4}, N^{1/4})
   split gives cost Theta(N^{3/4}), strictly worse.

2. **Index calculus cannot replace the small table.** On a prime-order elliptic
   curve, there is no analogue of integer smoothness. Computing small-range ECDLP
   values is as hard as ECDLP itself at the same scale. The black-box generic group
   model (Shoup) forbids sub-square-root algorithms unconditionally.

3. **The large table cannot be avoided.** Any strategy that avoids building a table
   of size N^{1/2} for one of the two parts must build a compensating structure for
   the other part, whose cost is at least as large by the AM-GM argument.

4. **Lattice and algebraic hybrids do not apply.** Improvements in the hidden number
   problem and related settings exploit linear or ring structure absent in the
   generic prime-order curve ECDLP.

**Consequence for the research program.** The hybrid MITM-decomposition direction
reduces, under formal analysis, to either:
- Standard BSGS (the optimal two-table MITM), or
- Standard index calculus (which requires algebraic structure absent on generic
  prime-order curves).

No improvement over Omega(sqrt(N)) is achieved. This is consistent with BATCH-098's
closure of all non-decomposition approaches and the identification of H-PSEUDO as the
only live path to sub-rho complexity. The present analysis closes the hybrid
MITM-decomposition sub-lane formally.

**Open boundary.** The argument above applies to algorithms that operate strictly in
the generic group model. It does not exclude algorithms that exploit:
- Specific curve parameters (CM curves, special j-invariants),
- Side-channel or fault information about the target,
- Quantum computation (Shor's algorithm, Omega(log N) qubits),
- The H-PSEUDO structure hypothesized in the live path.

These remain outside the scope of this analysis.

---

*Analysis produced for TASK-20260804-138, BATCH-099, GOAL-ECDLP-001.*
