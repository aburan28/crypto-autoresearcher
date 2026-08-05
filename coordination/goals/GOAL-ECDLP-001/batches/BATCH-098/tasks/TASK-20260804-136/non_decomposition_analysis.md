# Non-Decomposition Approaches to Prime-Field ECDLP: Analysis

**Task:** TASK-20260804-136  
**Batch:** BATCH-098  
**Goal:** GOAL-ECDLP-001  
**Date:** 2026-08-04  
**Author:** Mathematical analyst (Coordinator-dispatched)

---

## 1. Scope and Motivation

KN-FIND-9d2f56 (Betti-Yield Duality) establishes that **every decomposition-based
ECDLP algorithm achieving sub-rho critical-complex size requires H-PSEUDO** — yield above
the heuristic random baseline.  This closes the sub-rho question for the full class of
factor-base/chain-complex approaches, conditional on H-PSEUDO.

The residual question is:

> Do any **non-decomposition** approaches to prime-field ECDLP achieve sub-rho complexity
> **without** needing yield bounds?

This document answers: **No** — for all known approach families, and gives the exact
obstruction for each.

---

## 2. Approach Taxonomy

We partition candidate approaches into four families:

| Family | Representative algorithms | Generic? |
|---|---|---|
| BSGS / Pollard-type | Baby-step giant-step, Pollard ρ/λ, parallel collision | Yes |
| k-way MITM | k-part scalar decomposition + table join | Yes |
| Pohlig-Hellman | Subgroup CRT reduction | Generic (exploits order factorisation) |
| Structure-specific | MOV/FR (embedding), anomalous (Satoh-Araki/Smart/Semaev) | Non-generic |

Families 1–2 are the focus of this document; 3 and 4 are already closed in the ledger
(prime order ⇒ Pohlig-Hellman is useless; cryptographic curves are chosen to exclude
small embedding degree and trace-one anomaly).

---

## 3. BSGS and Pollard-type Algorithms

Baby-step giant-step computes a 2-part scalar decomposition:

    k = a · ⌈√N⌉ + b,   a, b ∈ [0, ⌈√N⌉)

Time: O(√N), Memory: O(√N).

Pollard ρ and λ achieve the same asymptotic time with O(1) memory via random walks and
Floyd/Brent cycle detection.  Parallel Pollard ρ with r processors improves the wall-clock
constant to O(√N / √r) but does not change the group-operation count; it still requires
Ω(√N) total group operations.

No variant of these algorithms achieves sub-rho for a generic prime-order group.

---

## 4. k-way MITM: Complete Analysis

### 4.1 Setup

Let N be the group order (prime).  Write the scalar k in base L = N^{1/k}:

    k = a_1 + a_2 · L + a_3 · L² + ⋯ + a_k · L^{k-1},   each a_i ∈ [0, L)

Define tables

    T_i = { [a_i · L^{i-1}]G : a_i ∈ [0, L) },   |T_i| = L = N^{1/k}

A solution satisfies [k]G = Q iff

    [a_1]G + [a_2 · L]G + ⋯ + [a_k · L^{k-1}]G = Q

### 4.2 Naive sequential join (the approach proposed)

Build accumulated tables:

    S_1 := T_1                                     |S_1| = N^{1/k}
    S_2 := {P1 + P2 : P1 ∈ S_1, P2 ∈ T_2}         |S_2| = N^{2/k}
    ⋮
    S_{k-1} := {P + P_{k-1} : P ∈ S_{k-2}, P_{k-1} ∈ T_{k-1}}   |S_{k-1}| = N^{(k-1)/k}

Then intersect S_{k-1} with { Q − [a_k · L^{k-1}]G : a_k ∈ [0,L) } (size N^{1/k}).

Expected collisions: |S_{k-1}| · |T_k| / N = N^{(k-1)/k} · N^{1/k} / N = 1. ✓

**Cost: O(N^{(k-1)/k}) group operations, O(N^{(k-1)/k}) memory.**

### 4.3 Cost table

| k | Cost | Memory | vs. BSGS (N^{1/2}) |
|---|---|---|---|
| 2 | N^{1/2} | N^{1/2} | = BSGS |
| 3 | N^{2/3} | N^{2/3} | **worse** by N^{1/6} |
| 4 | N^{3/4} | N^{3/4} | **worse** by N^{1/4} |
| k | N^{(k-1)/k} | N^{(k-1)/k} | worse for all k ≥ 3 |
| k → ∞ | N^{1−ε} → N | N → brute force | worst |

The function f(k) = (k−1)/k is strictly increasing in k (f′(k) = 1/k² > 0), so the
minimum is achieved at **k = 2**, which is exactly BSGS.  No k ≥ 3 improves on BSGS.

### 4.4 Balanced binary split does not escape N^{1/2}

One might hope to avoid the N^{(k-1)/k} bottleneck by grouping the k pieces into two
balanced halves.  For k parts with a balanced ⌊k/2⌋ vs ⌈k/2⌉ split:

- Left half covers N^{⌊k/2⌋/k} scalar combinations.
- Right half covers N^{⌈k/2⌉/k} scalar combinations.
- Collision expected when left × right ≥ N → N^{⌊k/2⌋/k + ⌈k/2⌉/k} = N^1. ✓

Cost is dominated by the larger half: O(N^{⌈k/2⌉/k}).

For even k: ⌈k/2⌉/k = 1/2 → O(N^{1/2}).  Same as BSGS.  
For odd k=3: ⌈3/2⌉/3 = 2/3 → O(N^{2/3}).  Still worse.  
For odd k≥5: ⌈k/2⌉/k = (k+1)/(2k) > 1/2 → still worse.

**Every balanced binary split either equals or exceeds N^{1/2}.** The optimal k-way MITM
under any grouping strategy is O(N^{1/2}) = BSGS.

### 4.5 Why 3-way is concretely worse: worked example

For k = 3, N = 2^{256} (cryptographic scale):

    L = 2^{256/3} ≈ 2^{85.3}

Building S_2 = {[a·L² + b·L]G : a,b ∈ [0,L)} requires:
- N^{2/3} ≈ 2^{170.7} group operations and storage points.

BSGS requires only 2^{128} operations and 2^{128} storage points.

The 3-way MITM is **2^{42.7} ≈ 2.5 × 10^{12}** times more expensive than BSGS.
It is not merely theoretically worse; it is catastrophically worse in practice.

### 4.6 Impossibility of sub-rho via MITM without structure

**Claim:** In the generic group model, no k-way MITM approach achieves o(N^{1/2}) group
operations.

**Argument:** Any MITM strategy defines a function f : [N]^{k₁} × [N]^{k₂} → G that maps
two tuples of scalars to a pair of group elements and declares a solution when the two
elements collide.  In the generic group model, the only operation is equality testing
(and group law applications to produce new elements).  By the birthday bound, a collision
in a set of size M requires sampling Ω(√(N/M)) elements.  The aggregate information
extracted per group operation is bounded (logarithmic at best), so Ω(N^{1/2}) operations
are required by any collision-based strategy on a group of prime order N.  This
is formalised as:

**Theorem (Shoup 1997; Boneh–Lipton 1996):** Any generic group algorithm (deterministic
or randomised, with or without preprocessing) for the discrete logarithm problem in a
group of prime order N uses Ω(√N) group operations.

Since k-way MITM is a special case of generic group algorithms, the bound applies.

---

## 5. Other Non-Decomposition Approaches

### 5.1 Pohlig-Hellman

Reduces ECDLP to DLP in subgroups.  Cost O(√p_max) where p_max is the largest prime
factor of N.  For prime N (the cryptographic setting), p_max = N and Pohlig-Hellman
reduces to the full ECDLP.  **No improvement. Closed.**

### 5.2 MOV / FR reduction

Maps ECDLP to F_{p^k}* for embedding degree k.  If k is small (say k ≤ 6), index
calculus on F_{p^k}* runs in subexponential time.  Cryptographic curves (SEC 2, NIST
P-curves) are constructed to have embedding degree k ≈ N/2 by Hasse's theorem, making
the target field astronomically large.  **No improvement for standard curves. Closed.**

### 5.3 Anomalous curve reduction (Satoh-Araki / Smart / Semaev)

When #E(F_p) = p (trace of Frobenius = 1), a p-adic lifting (Hensel lift) reduces ECDLP
to an additive group over Z_p.  This runs in polynomial time — but applies **only** when
N = p.  No cryptographic curve is anomalous; this condition is tested and rejected during
parameter generation.  **No improvement for cryptographic curves. Closed.**

### 5.4 Quantum algorithms

Shor's algorithm solves DLP (and hence ECDLP) in polynomial time on a quantum computer
using period finding via QFT.  This operates in the quantum circuit model, not the
classical generic group model, and requires a fault-tolerant quantum computer with
~ 2000–4000 logical qubits for NIST P-256.  For **classical** algorithms over classical
hardware — the scope of this analysis — Shor's algorithm does not apply.

Grover's algorithm gives a quadratic speedup for unstructured search, yielding O(N^{1/4})
for BSGS-on-quantum.  This is better than the classical O(N^{1/2}) but still
exponential and requires a quantum computer.  It does not constitute a non-decomposition
approach; it is quantum-accelerated BSGS.

### 5.5 Algebraic geometry / Weil descent / Gaudry-type attacks

Gaudry (2000) proposed a Weil-descent index calculus for hyperelliptic curves over
extension fields F_{q^n}.  For n ≥ 2, the Weil restriction embeds E/F_{q^n} into an
abelian variety over F_q of dimension n, enabling index calculus on the Jacobian.
For **prime fields** (n = 1), there is no extension-field structure to descend, and
no analogous approach is known.  **No improvement for prime-field ECDLP. Closed.**

---

## 6. Combined Barrier Statement

Let E/F_p be an elliptic curve with #E(F_p) = N prime (the standard cryptographic
setting, e.g., NIST P-256 with N a 256-bit prime).  Then:

### Decomposition approaches (covered by KN-FIND-9d2f56)

Any factor-base algorithm achieving sub-rho critical-complex size requires:

    ⟨r₂^S(R)⟩ > B²/N   (H-PSEUDO: yield above random baseline)

Without H-PSEUDO, the Betti-Yield Duality forces β₁(C_R^S) ≥ Ω(√N) for any
non-trivial factor base S, blocking sub-rho complexity.

### MITM approaches (proved in this document)

All k-way MITM approaches with sequential join cost O(N^{(k-1)/k}).  
f(k) = (k−1)/k is strictly increasing.  
Minimum at k = 2: cost O(N^{1/2}) = BSGS.  
No k-way MITM (for any k ≥ 2, any grouping strategy) achieves o(N^{1/2}).

**Corollary:** BSGS is the unique optimal MITM approach, and it matches the generic
group lower bound exactly.

### All other approaches

| Approach | Obstruction | Status |
|---|---|---|
| Pohlig-Hellman | N prime, no subgroup structure | Closed |
| MOV/FR | Embedding degree k ≈ N/2 for crypto curves | Closed |
| Anomalous reduction | Requires N = p (trace 1); crypto curves exclude this | Closed |
| Weil descent / Gaudry | Requires extension field (n ≥ 2); prime field has n = 1 | Closed |
| Quantum (Shor) | Requires quantum hardware; classical scope | Out of scope |

### Joint conclusion

For prime-field ECDLP with prime group order on cryptographic curves:

> **Every known algorithm requires Ω(N^{1/2}) classical group operations.**

The two main structural barriers are:
1. **Betti-Yield Duality** (KN-FIND-9d2f56): decomposition approaches require H-PSEUDO.
2. **k-way MITM optimality theorem**: MITM cost ≥ N^{1/2}, minimised at k=2 (BSGS).

These two barriers together cover all known algorithm families.  No non-decomposition
approach avoids the N^{1/2} floor.

---

## 7. Implication for GOAL-ECDLP-001

The program's working hypothesis (H-PSEUDO as the sufficient condition for sub-rho
decomposition algorithms) is **not undermined** by any of the above alternatives.

- There is no known shortcut through MITM; the best MITM is BSGS = N^{1/2}.
- There is no known non-generic prime-field classical approach below N^{1/2}.
- Therefore, if sub-rho ECDLP is achievable by any classical algorithm, it **must**
  go through a decomposition algorithm, and by KN-FIND-9d2f56 it **must** require
  H-PSEUDO (or an approach outside the chain-complex framework, none of which are
  currently known).

The program's focus on establishing or refuting H-PSEUDO remains well-motivated and
is the correct bottleneck to pursue.

---

## 8. Open Questions

1. **Is H-PSEUDO achievable?** The duality theorem says it is necessary. Whether any
   constructive S achieves it for prime-field EC points remains the core open problem.

2. **Is there a fourth family?** The above analysis covers all currently known
   approach families. A genuinely new structural insight (analogous to index calculus
   for multiplicative groups, but applicable to EC groups over prime fields) could
   bypass both barriers. No such approach is known; the Boneh-Lipton lower bound
   applies to all generic algorithms but not to hypothetical non-generic ones.

3. **MITM + H-PSEUDO hybrid?** Could a sub-rho algorithm combine structured factor
   bases (exploiting H-PSEUDO) with MITM-style joins on multiple factor bases?
   This would still be a decomposition algorithm and would fall under the KN-FIND-9d2f56
   framework; it does not escape the Betti-Yield Duality.

---

## 9. References

- KN-FIND-9d2f56: Betti-Yield Duality — H-PSEUDO is the exact condition for sub-rho
  combinatorial ECDLP.
- Shoup, V. (1997): Lower bounds for discrete logarithms and related problems. EUROCRYPT 1997.
- Boneh, D., Lipton, R. (1996): Algorithms for Black-Box Fields and their Application to
  Cryptography. CRYPTO 1996.
- Pohlig, S., Hellman, M. (1978): An Improved Algorithm for Computing Logarithms over
  GF(p). IEEE Trans. Inf. Theory.
- Menezes, A., Okamoto, T., Vanstone, S. (1993): Reducing elliptic curve logarithms to
  logarithms in a finite field. IEEE Trans. Inf. Theory (MOV).
- Satoh, T., Araki, K. (1998); Smart, N. (1999); Semaev, I. (1998): anomalous curve
  reduction.
- Gaudry, P. (2000): An algorithm for solving the discrete log problem on hyperelliptic
  curves. EUROCRYPT 2000.

---

*Document status: complete. No experimental runs required; this is a mathematical
analysis of known complexity-theoretic results.*
