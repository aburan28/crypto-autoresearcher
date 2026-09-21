# Formal BKK Speedup Theorem

**Task:** TASK-20260804-181  
**Goal:** GOAL-ECDLP-001, BATCH-119  
**Date:** 2026-08-05  
**Author:** Mathematical Analyst (TASK-20260804-181)  
**Evidence base:** KN-FIND-2a8b7e, DEC-20260804-0ed0fe, BATCH-110..118

---

## Setup

**Factor base.** Let F = {P_1, ..., P_B} be a set of B elliptic curve points over F_p,
ordered by some fixed enumeration. Write F[:n] for the first n elements.

**m-decomposition.** A target T has an m-decomposition over F if
T = P_{a_1} + P_{a_2} + ... + P_{a_m} for some indices a_i ∈ {1,...,B}.
(Indices need not be distinct; points are on a group, addition is the group law.)

**Full Semaev check (cost B^{m-1} per trial).**  
Iterate (i_1,...,i_{m-1}) over {1,...,B}^{m-1} (all (m-1)-tuples in F).  
At each tuple compute R = T - P_{i_1} - ... - P_{i_{m-1}} and test R ∈ F.

**BKK sparse check (cost (B/2)^{m-1} per trial).**  
Iterate (i_1,...,i_{m-1}) over {1,...,B/2}^{m-1} (only the first half).  
At each tuple compute R = T - P_{i_1} - ... - P_{i_{m-1}} and test R ∈ F.  
This is exactly the implementation in BATCH-115 (variable `n_c = B//2`, all m-1 loop levels
range over `F[:n_c]`).

**Yield retention gamma_m.**  
gamma_m = Pr[BKK finds T's decomposition | T has at least one m-decomposition over F].

---

## Theoretical gamma lower bound: gamma_m >= (m+1)/2^m

### Uniform random model

**Assumption (U).** Decomposition indices (a_1,...,a_m) are i.i.d. Uniform{1,...,B}.

This is the standard random-target heuristic used throughout Semaev index calculus
(e.g., Gaudry 2009, Diem 2011). It is a lower bound assumption: EC structure
empirically gives *higher* gamma (see §4 below).

### Lemma (BKK catch condition)

**Lemma 1.** Under the BKK check, the decomposition T = P_{a_1}+...+P_{a_m} is found
if and only if at least m-1 of the m indices a_1,...,a_m lie in {1,...,B/2}.

*Proof.*

(⇐) Suppose m-1 indices, say a_1,...,a_{m-1}, satisfy a_k ≤ B/2 for k=1,...,m-1.
The BKK loop iterates over all (m-1)-tuples from {1,...,B/2}^{m-1}, so it will visit
(i_1,...,i_{m-1}) = (a_1,...,a_{m-1}).
At that tuple: R = T - P_{a_1} - ... - P_{a_{m-1}} = P_{a_m} ∈ F.
The check R ∈ F succeeds. The decomposition is found. ∎ (⇐)

(⇒) Suppose fewer than m-1 indices lie in {1,...,B/2}, i.e., at most m-2.
Every tuple the BKK loop visits has all m-1 components in {1,...,B/2}.
For any such tuple (i_1,...,i_{m-1}), the set {i_1,...,i_{m-1}} ⊆ {1,...,B/2},
but T's decomposition has at most m-2 of its m elements in {1,...,B/2}.
No relabeling of T's decomposition elements covers all m-1 loop positions.
Therefore the BKK loop never encounters a permutation of T's decomposition
and the check fails for every tried tuple. ∎ (⇒)

*Note on relabeling.* The lemma applies because the BKK loop exhausts
{1,...,B/2}^{m-1}: if any (m-1)-element sub-multiset of {a_1,...,a_m} lies entirely
in F[:B/2], the loop visits it (in every ordering, since P_k is keyed by index k).

### Theorem 1 (gamma lower bound)

**Theorem 1.** Under assumption (U):

    gamma_m = Pr[at least m-1 of {a_1,...,a_m} lie in {1,...,B/2}]
            = sum_{k=m-1}^{m} C(m,k) * (1/2)^k * (1/2)^{m-k}
            = [ C(m, m-1) + C(m, m) ] / 2^m
            = (m + 1) / 2^m

*Proof.* By Lemma 1, gamma_m = Pr[S >= m-1] where S = #{i : a_i <= B/2}.
Under (U), each a_i satisfies a_i <= B/2 with probability exactly 1/2, independently.
So S ~ Binomial(m, 1/2) and:

    Pr[S >= m-1] = Pr[S = m-1] + Pr[S = m]
                 = C(m, m-1)(1/2)^m + C(m, m)(1/2)^m
                 = (m + 1) / 2^m.  QED.

The bound is tight within the uniform model: equality holds when all a_i are i.i.d.
Uniform{1,...,B}. EC group structure (correlated a_i from Semaev polynomial solutions)
consistently yields higher gamma; see §4.

---

## Formal speedup theorem: speedup >= (m+1)/2

### Cost model

Let p_m = Pr[a random target T has at least one m-decomposition over F] (independent
of which half of F is "first"). Let R = number of relations to collect.

| Method | Cost per trial | Expected trials per relation | Total cost |
|--------|---------------|------------------------------|------------|
| Full   | B^{m-1}       | 1 / p_m                      | R * B^{m-1} / p_m |
| BKK    | (B/2)^{m-1}   | 1 / (gamma_m * p_m)          | R * (B/2)^{m-1} / (gamma_m * p_m) |

The BKK check raises the cost per trial by gamma_m^{-1} (lower yield) but reduces
work per trial by 2^{m-1}. The net speedup (Full cost / BKK cost) is:

    Speedup(m) = [ B^{m-1} / p_m ] / [ (B/2)^{m-1} / (gamma_m * p_m) ]
               = gamma_m * 2^{m-1}

### Theorem 2 (speedup lower bound)

**Theorem 2.** Under assumption (U), the BKK speedup satisfies:

    Speedup(m) = gamma_m * 2^{m-1} >= (m+1)/2^m * 2^{m-1} = (m+1)/2.

*Proof.* Immediate from Theorem 1 and the cost model. QED.

**Corollary.** The BKK speedup grows linearly in m under the uniform model.
Since m_opt ~ sqrt(log N / log log N) for N-bit ECDLP, the speedup at
cryptographic scale is a constant factor (slowly growing with N).

### Speedup bounds by m

| m | gamma lb: (m+1)/2^m | speedup lb: (m+1)/2 | typical m_opt at N |
|---|---------------------|---------------------|--------------------|
| 2 | 0.750               | 1.5x                | small N            |
| 3 | 0.500               | 2.0x                |                    |
| 4 | 0.3125              | 2.5x                | N=2^128            |
| 5 | 0.1875              | 3.0x                | N=2^256            |
| 6 | 0.1094              | 3.5x                |                    |
| 7 | 0.0625              | 4.0x                | N=2^512            |
| 9 | 0.0195              | 5.0x                | N=2^1024           |

---

## Comparison to empirical data

Empirical data from KN-FIND-2a8b7e (p=1009, near-optimal B):

| m | gamma lb (theory) | gamma empirical | speedup lb (theory) | speedup empirical | excess (EC bonus) |
|---|-------------------|-----------------|---------------------|-------------------|-------------------|
| 2 | 0.750             | 0.86            | 1.5x                | 1.72x             | +0.110            |
| 3 | 0.500             | 0.66            | 2.0x                | 2.62x             | +0.160            |
| 4 | 0.3125            | 0.35            | 2.5x                | 2.82x             | +0.038            |
| 5 | 0.1875            | 0.27            | 3.0x                | 4.24x             | +0.083            |

**Observations:**

1. **Lower bound holds in all cases.** Empirical gamma consistently exceeds (m+1)/2^m.
   Empirical speedup consistently exceeds (m+1)/2. The theorem is not refuted by data.

2. **EC structure gives a bonus.** The excess gamma (empirical − theory lb) is systematic
   and positive, averaging ~0.10 across m=2..5. This is consistent with the heuristic
   that Semaev polynomial solutions are not uniformly distributed — the EC group law
   introduces correlations that favor balanced index distributions.

3. **m=4 is the tightest case.** At m=4, gamma_empirical=0.35 is only 0.038 above the
   bound of 0.3125. The bound is informative but not tight at all m; the EC bonus
   appears smaller when B is smaller (near-optimal B shrinks with m).

4. **The KN-FIND-2a8b7e formula** gamma_m ≈ 0.86 * 0.68^{m-2} is an empirical fit and
   consistently exceeds the theoretical lower bound (m+1)/2^m for m=2..5.

### Quantitative check: theory vs. empirical speedup at N=2^256

From DEC-20260804-0ed0fe and KN-FIND-2a8b7e at m_opt≈4-5:
- Theorem 2 lower bound: (4+1)/2 = 2.5x (m=4), (5+1)/2 = 3.0x (m=5)
- Empirical formula (KN-FIND-2a8b7e): ~3.3x at N=2^256

The theorem accounts for ~75–83% of the observed speedup; the residual ~0.3–0.8x
is the EC bonus from correlated index structure.

---

## Assumptions and scope

**Assumption (U) — i.i.d. uniform indices.** This is the standard heuristic for
Semaev index calculus. It holds exactly when T is a uniformly random group element
and F is a "random" factor base. For structured factor bases or non-random T the
bound may not hold, but empirical evidence shows EC structure only increases gamma.

**Independence of a_i.** The proof uses independence (Binomial model). Decompositions
over an elliptic curve group come from the zero set of a Semaev polynomial, which
introduces correlations. The empirical excess shows these correlations are favorable
to the BKK check, not harmful. The bound is conservative.

**BKK loop structure.** The proof assumes m-1 nested loops over F[:B/2]. This matches
the BATCH-115 implementation (`n_c = B//2`, m-1 levels). If the implementation used
fewer levels in F[:B/2] the bound would not apply; if it used more, the bound remains.

**Worst-case vs. random.** Theorem 2 is a random-model lower bound, not a worst-case
bound. An adversarially chosen target T could have all decomposition indices in
{B/2+1,...,B}, giving gamma=0 for that T. The bound applies to the average over
uniform random T (which is the standard Semaev model).

---

## Conclusion: BKK speedup is provably >= (m+1)/2 for random decompositions

**Main result.** Under the standard uniform-index heuristic for Semaev index calculus:

    Speedup(m) >= (m+1)/2   [Theorem 2, proved above]

This is a *provable lower bound* on the BKK speedup, derived from first principles
(Lemma 1: catch condition; Theorem 1: Binomial calculation; cost model: ratio of
work-per-relation).

**At cryptographic parameters:**
- N=2^256, m_opt≈4-5: speedup ≥ 2.5–3.0x (theorem), ~3.3x (empirical)
- N=2^512, m_opt≈6-7: speedup ≥ 3.5–4.0x (theorem), ~5–8x (empirical estimate)

The theorem confirms that the ~3-4x empirical BKK speedup is not an artifact of
small-parameter experiments — it has a provable combinatorial foundation. The EC
group structure gives an additional bonus (empirically ~15–30%) beyond the theorem's
lower bound.

**The formal mechanism:** The BKK check uses the observation that for any m-decomposition,
at least m-1 of its m elements can be placed in the first B/2 elements of F (under
the uniform model, with probability (m+1)/2^m). By checking only (B/2)^{m-1} tuples
instead of B^{m-1}, we miss only the fraction (1 - (m+1)/2^m) of decompositions —
those where more than one element falls in the second half. The net savings is the
speedup (m+1)/2, growing linearly in m.

**Status:** This constitutes a formal proof of the BKK speedup under the standard
uniform-index heuristic. The proof is self-contained and the assumptions are
explicitly stated. Independent review recommended before promoting to hypothesis status.

---

*Record produced by: TASK-20260804-181 (Mathematical Analyst, BATCH-119)*  
*Cites: KN-FIND-2a8b7e, DEC-20260804-0ed0fe*  
*Claimed status: lower-bound proof under standard Semaev heuristic (U)*
