# Oracle-H-PSEUDO Analysis: IDEA-20260805-62ef74
**Task:** TASK-20260805-004, BATCH-121, GOAL-ECDLP-001  
**Sources:** IDEA-20260805-62ef74, KN-FIND-9d2f56, H-PSEUDO-83817b, BATCH-060/TASK-20260804-051  
**Date:** 2026-08-05

---

## Executive summary

IDEA-62ef74's core insight — that C_t is the minimal non-simulable oracle enabling IC in
the GGM — is valid and non-trivial. Its stated biconditional, however, has two defects:
the H-PSEUDO condition is inverted, and "sub-rho" is conflated between two distinct uses.
Correcting both defects yields a coherent and weaker result. None of the four questions
below support a polynomial-time ECDLP path.

---

## Q1 — Does Semaev IC in GGM+C_t achieve sub-rho complexity?

**Answer: YES, unconditionally.**

Sub-rho means cost < O(sqrt(N)). Semaev IC with heuristic yield achieves complexity
L[1/2, c] = exp(c * sqrt(log N * log log N)) for c = sqrt(2m/(m-1)) → sqrt(2) as m → ∞.

For N = 2^256:
```
N^{1/2}           = 2^128       ≈ exp(88.7)
L[1/2, sqrt(2)]   ≈ exp(42.8)   ≈ 2^{61.7}
```
L[1/2, sqrt(2)] << N^{1/2} for N = 2^256, and more generally for all N above a small
threshold (log N dominates log log N). Semaev IC is sub-rho.

With GGM+C_t: factor-base membership test F = {P : x(P) < B/p} costs ONE C_{B/p}
query per point (not O(log p) — threshold testing is a single comparison query, not
binary search). Full x-coordinate recovery costs O(log p) adaptive C_t calls, but IC
does not need the full coordinate, only the membership bit. So GGM+C_t adds exactly O(1)
overhead per relation check vs. the concrete model. Asymptotic complexity is unchanged.

**Sub-rho in GGM+C_t holds unconditionally. It is not conditioned on H-PSEUDO.**

---

## Q2 — Would H-PSEUDO failure enable polynomial-time ECDLP?

**Answer: NO, not via yield enhancement.**

H-PSEUDO bounds max_k |hat{1_F}(k)| <= C * sqrt(B). If it fails with maximum coefficient
M at frequency k*, the per-target Semaev yield becomes:

```
S_m(R) = B^m/N  +  (1/N) * sum_{k != 0} hat{1_F}(k)^m * char(k, DL(R))
       ~ B^m/N  +  M^m / N     (for optimally aligned targets)
```

The effective complexity shifts from L[1/2, c] to L[1/2, c'] where c' < c. The
complexity class remains L[1/2, *] (subexponential); the exponent does not drop to 0.

### Why polynomial time is blocked

For polynomial time (L[0, *] = poly(log N)), one would need:

```
B / S_m(R) = poly(log N)     (trials to collect one relation)
```

The maximum S_m(R) is bounded by B^m/N (the number of m-tuples over F cannot exceed B^m,
and each sum hits target R with probability ~1/N). To achieve poly(log N) trials per
relation with m = 3 and B = sqrt(N) (already the LA-budget limit):

```
S_m = B^3/N = N^{3/2}/N = sqrt(N) >> 0,  but B/S_m = sqrt(N)/sqrt(N) = 1 trial.
```

One might hope this gives polynomial time, but at B = sqrt(N) the linear algebra cost
B^omega dominates at B^omega >= sqrt(N)^2 = N — larger than rho. Reducing B to poly(log N)
makes LA cheap but S_m drops to (log N)^{3m}/N = negligibly small, requiring N/poly(log N)
trials per relation — worse than rho.

No assignment of B and m simultaneously achieves poly(log N) total cost via yield
enhancement. The L[1/2, *] barrier persists regardless of yield magnitude.

### Why maximum H-PSEUDO failure doesn't help with general ECDLP

If |hat{1_F}(k*)| = B (maximal failure), all factor-base DLs are multiples of N/k*.
The factor base generates only the index-k* subgroup H ⊂ E(F_p) of order N/k*. IC over
F can only decompose targets whose DL is divisible by k* — a fraction 1/k* of all targets.
For random targets, IC simply fails. For the targets it does reach, the subgroup ECDLP
has order N/k*, giving complexity L[1/2, c] in N/k* — smaller but not polynomial.

**H-PSEUDO failure shifts the L[1/2, c] constant downward; it does not enable
polynomial-time ECDLP.**

---

## Q3 — Is C_t GGM-simulable or non-simulable?

**Answer: NON-SIMULABLE (Tier 3 encoding-dependent oracle).**

### Formal argument

In Shoup's GGM, two instances (E_1, G_1) and (E_2, G_2) are GGM-indistinguishable if
they assign identical labels sigma_i([j]G_i) for all queried j and are indistinguishable
by the group law. Two distinct Weierstrass equations over F_p with the same group order N
satisfy this condition (they are abstractly isomorphic as groups), yet their x-coordinate
functions differ.

**Non-simulability witness:** Let E_1, E_2 be two prime-order curves over F_p with
#E_i(F_p) = N. Set labels sigma_1([j]G_1) = sigma_2([j]G_2) for all j queried. Choose
a scalar k and threshold t such that x_{E_1}([k]G_1) < t but x_{E_2}([k]G_2) >= t.
(Such pairs exist for any t in (0,p) since the x-coordinate function is curve-specific.)
The two instances are GGM-indistinguishable yet C_t gives opposite answers. No GGM
simulator can reproduce this.

### Classification in the BATCH-060 taxonomy

From BATCH-060/TASK-20260804-051 three-tier taxonomy:
- **Tier 1 (simulable, e.g., Incidence, Endomorphism):** output determined by group law
- **Tier 2 (non-simulable, privately computable):** requires k — equivalent to DLP oracle
- **Tier 3 (non-simulable, encoding-dependent, e.g., Elliptic Net):** requires x-coordinates but not k

C_t is **Tier 3**: it is publicly computable (anyone with the concrete curve can evaluate
it), encoding-dependent (x-coordinate is curve-specific), and does not require knowing k.

BATCH-060 also classifies the encoding oracle (P → x(P)) as NON-SIMULABLE (control). C_t
is a coarser version of the encoding oracle (1-bit threshold instead of full coordinate);
by the same argument it is non-simulable.

### Oracle minimality

IDEA-62ef74's claim that C_t is the MINIMAL non-simulable 1-bit oracle enabling IC is
directionally correct but requires a precise qualification. Among threshold oracles
C_t(P) = [x(P) < t?], C_t at t = B/p is precisely what identifies F-membership.
Among all 1-bit non-simulable oracles, minimality depends on the ordering chosen:
- C_t is minimal in the sense of using the 1-bit threshold of the order structure on F_p
- A random-1-bit hash of x(P) is also non-simulable but does not identify the ordered
  factor base F; it is less useful for IC despite being equally minimal in oracle complexity

The correct statement: **C_t is the weakest ORDER-BASED non-simulable oracle that enables
threshold factor-base membership for IC.** The 0-bit (trivial) oracle provides no
information; any 1-bit threshold enables IC. There is no strictly weaker non-trivial
threshold oracle between 0-bit and C_t.

### Status relative to H-GGM-001

H-GGM-001 classified four oracle types (jet, elliptic-net, incidence, endomorphism) and
did not study C_t. C_t falls into the same class as the NON-SIMULABLE encoding control
oracle from H-GGM-001's control set, and is therefore classified NON-SIMULABLE by the
same argument. No new experiment is needed; the classification follows from the
encoding-control verdict in BATCH-060.

---

## Q4 — Correct complexity-theoretic formulation of IDEA-62ef74

### Two defects in the stated biconditional

**Defect 1: H-PSEUDO condition is inverted.**

H-PSEUDO-83817b (hypothesis text) states:
```
max_{k=1..N-1} |hat{1_F}(k)| <= C * sqrt(B)
```
This HOLDS when DLs are pseudorandom (equidistribute in Z/N, similar to a random set).
H-PSEUDO HOLDING → yield ≈ heuristic B^m/N (not above heuristic).

IDEA-62ef74 Direction A writes "H-PSEUDO ↔ (yield above random baseline)." This is
backwards: H-PSEUDO HOLDING means yield IS AT the random baseline (heuristic level).
H-PSEUDO FAILING (large Fourier coefficient) is what potentially raises yield above
heuristic for aligned targets.

The correct direction of KN-FIND-9d2f56 Corollary:
```
Sub-rho chain complex requires above-heuristic yield
  ↔ requires H-PSEUDO to FAIL (large Fourier coefficient)
  ↔ DLs NOT pseudorandom
```
NOT "requires H-PSEUDO to HOLD."

**Defect 2: Two distinct uses of "sub-rho" are conflated.**

- **Semaev IC algorithmic sub-rho**: cost(IC) < sqrt(N). This holds with HEURISTIC yield
  (H-PSEUDO holding). No H-PSEUDO failure required.
- **Chain-complex sub-rho (KN-FIND-9d2f56)**: β_1(C_R^F) < sqrt(N). This requires
  above-heuristic yield, i.e., H-PSEUDO FAILS.

IDEA-62ef74 applies the chain-complex duality to conclude that algorithmic sub-rho
requires H-PSEUDO — but this conflates the two uses. Standard Semaev IC is
algorithmically sub-rho even when chain-complex β_1 >= sqrt(N).

### What IDEA-62ef74 gets right

1. **C_t is non-simulable in the GGM.** ✓ (proved above)
2. **C_t enables factor-base membership in O(1) queries.** ✓ (one threshold call)
3. **GGM+C_t IC is complexity-equivalent to concrete-model IC.** ✓ (O(1) overhead per relation)
4. **C_t does not change the Semaev complex structure.** ✓ (C_t identifies membership;
   it does not alter which decompositions exist over F)
5. **ECCG connection.** ✓ ECCG security (x([j]G) computationally indistinguishable from
   uniform) implies the character sum ∑_{j} e^{2πi k j / N} is bounded for the sequence
   {x([j]G)}, which is the IC-relevant restriction of H-PSEUDO. ECCG → H-PSEUDO for
   structured sequences.
6. **Direction B logic (GGM layer only).** ✓ The observation that C_t cannot CREATE
   yield that does not exist in the Semaev complex is correct: C_t provides membership
   identification, not new decompositions.

### Corrected formulations

**Correct Claim A (unconditional IC):**
> Semaev IC is sub-rho (L[1/2, c] << sqrt(N)) in GGM+C_t with heuristic yield (H-PSEUDO
> holding). H-PSEUDO failure improves the constant c but does not change the sub-rho
> character.

**Correct Claim B (chain-complex characterization):**
> The Semaev chain complex C_R^F achieves sub-rho Betti number (β_1 < sqrt(N)) if and
> only if the factor base F has above-heuristic yield, which requires H-PSEUDO to FAIL.
> (Follows from KN-FIND-9d2f56 Corollary, with H-PSEUDO correctly oriented.)

**Correct Claim C (oracle equivalence):**
> GGM+C_t is complexity-equivalent to the concrete model for all IC algorithms. C_t is
> the minimal non-simulable order-based oracle that enables threshold factor-base
> membership identification.

**Correct Claim D (ECCG/H-PSEUDO unification):**
> C_t-augmented IC over the sequence {[j]G} is sub-rho whenever ECCG holds (x([j]G)
> pseudorandom), because ECCG implies the IC yield is at the heuristic level — which is
> already sub-rho. This unifies ECCG security and the H-PSEUDO Fourier bound under the
> C_t-augmented oracle model.

### The biconditional, correctly stated

The iff claimed by IDEA-62ef74 is recoverable only in the chain-complex framing:

> **∃F [chain-complex C_R^F is sub-rho (β_1 < sqrt(N))]  ↔  ∃F [H-PSEUDO fails for F
> (yield(F) > heuristic)]**

Both sides have the SAME existence witness F. This is the content of KN-FIND-9d2f56 with
the oracle layer: C_t does not alter which factor bases have above-heuristic yield, so
the iff holds in GGM+C_t for exactly the same reason it holds in the concrete model. The
contribution of IDEA-62ef74 is the reduction of the GGM+C_t question to the concrete-model
question via the O(1) membership-identification property of C_t.

The ALGORITHMIC iff ("IC is sub-rho in GGM+C_t iff H-PSEUDO holds") is false as stated:
IC is sub-rho unconditionally. The conditional improves the constant but does not control
the sub-rho character.

---

## Summary table

| Question | Answer | Key point |
|---|---|---|
| Q1: Does GGM+C_t IC achieve sub-rho? | **YES, unconditionally** | L[1/2, c] << sqrt(N) with heuristic yield; C_t adds O(1) overhead |
| Q2: Does H-PSEUDO failure enable poly-time? | **NO** | Yield enhancement shifts constant in L[1/2,c]; L[1/2] barrier persists; max failure restricts IC to subgroup |
| Q3: Is C_t GGM-simulable? | **NON-SIMULABLE (Tier 3)** | Encoding-dependent, non-simulability witness via distinct Weierstrass equations with same group order |
| Q4: Correct formulation of IDEA-62ef74? | **Two defects: H-PSEUDO inverted; "sub-rho" conflated** | Valid core: C_t ≡ concrete model for IC; corrected iff is chain-complex sub-rho ↔ H-PSEUDO FAILS |

---

## Recommendation for Coordinator

IDEA-62ef74 contains a valid and non-trivial structural observation — that GGM+C_t is the
exact oracle model for concrete-model IC, and that C_t is the minimal non-simulable oracle
enabling IC — embedded in an incorrectly stated biconditional. Approval for further
investment should require correcting the H-PSEUDO orientation before any experiment design.
The corrected claim (chain-complex iff, oracle equivalence) is worth formalizing as a
standalone theorem if the proof of C_t minimality can be made rigorous. No polynomial-time
ECDLP path is opened by this analysis.

---

*Analysis by mathematical analyst, TASK-20260805-004, BATCH-121, GOAL-ECDLP-001.*  
*Sources: IDEA-20260805-62ef74, KN-FIND-9d2f56, H-PSEUDO-83817b, BATCH-060/ggm_analysis.md, KN-FIND-c7d31e.*
