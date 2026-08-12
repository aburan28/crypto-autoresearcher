# ECCG Security → H-PSEUDO Reduction Analysis

**Task**: TASK-20260804-144  
**Idea analyzed**: IDEA-20260804-28c15f  
**Date**: 2026-08-05

---

## Setup

**The ECCG sequence.** Fix a prime p, an elliptic curve E/F_p, a point G of order N, and a threshold B < N. Define:

- x_j = x([j]G) ∈ F_p, the x-coordinate of the j-th multiple of G (j = 0, 1, …, N−1).
- The indicator set S = {j ∈ Z/N : x_j < B} with |S| = B (approximately, up to ±O(sqrt(N)) by Hasse).
- The indicator function f : Z/N → {0,1}, f(j) = 1_{x_j < B}.

**H-PSEUDO (Fourier flatness hypothesis).** For all k ∈ Z/N with k ≠ 0:

    |hat{f}(k)| := |Σ_{j=0}^{N-1} f(j) · e^{2πi kj/N}| ≤ C · sqrt(B)

where C is a small absolute constant (e.g., C = O(sqrt(log N))).

**ECCG security assumption.** Given a prefix x_0, x_1, …, x_{t−1} for t = poly(log N), no PPT algorithm can predict x_t with non-negligible advantage, nor distinguish the prefix from uniform random values in F_p.

**Proposed reduction.** IDEA-20260804-28c15f claims: H-PSEUDO false → ECCG distinguisher exists → ECCG security false. Hence ECCG security → H-PSEUDO.

---

## The statistical detection question

Suppose H-PSEUDO is false: there exists k* ≠ 0 with |hat{f}(k*)| = A >> C·sqrt(B).

This means the set S has a k*-fold rotational bias in Z/N: the indicator f is not equidistributed across the N-th roots of unity, but correlates with the character χ_{k*}(j) = e^{2πi k*j/N}.

Concretely, the normalized bias is:

    δ := (1/N) · |hat{f}(k*)| = A/N >> C·sqrt(B)/N

**Can an ECCG observer detect this bias?**

An observer with a consecutive window j_0, j_0+1, …, j_0+t−1 sees t binary values f(j_0), f(j_0+1), …, f(j_0+t−1). They can compute the partial Fourier sum:

    T := (1/t) · Σ_{j=j_0}^{j_0+t-1} f(j) · e^{2πi k*j/N}

The question is whether T reliably estimates δ and whether that estimate is statistically distinguishable from zero.

---

## Signal-to-noise analysis

**Signal magnitude.** If H-PSEUDO fails with A = |hat{f}(k*)| > C·sqrt(B), then in the worst admissible case:

    δ = A/N

Since the hypothesis is that A > C·sqrt(B) ≈ C·sqrt(p) (with B ≈ p/N · N = p for threshold B = p, or more precisely A ≤ C·sqrt(B) is the *passing* bound), the failure signal satisfies:

    A/N > C·sqrt(B)/N

At cryptographic scale with N ≈ p ≈ 2^256 and B ≈ p:

    δ > C · sqrt(p) / p = C / sqrt(p) ≈ C · 2^{-128}

This is the *largest* signal H-PSEUDO failure at the prescribed threshold can provide. The signal is exponentially small.

**Noise magnitude.** The partial sum T is an average of t independent-ish terms bounded in magnitude by 1. By standard concentration (Hoeffding or CLT), the standard deviation of |T| is:

    σ_T = O(1/sqrt(t))

**Detection condition.** Statistical detection of δ requires t such that:

    δ >> σ_T, i.e., C · 2^{-128} >> 1/sqrt(t), i.e., t >> 2^{256} / C^2

**Required observation count.** To detect a bias of δ ≈ C·2^{-128} from a sequence of Bernoulli observations, one needs t >> 2^{256} observations. This is astronomically beyond any polynomial in log(N) ≈ 256.

**Comparison to Pollard rho.** Pollard rho solves ECDLP in expected O(sqrt(N)) = O(2^{128}) steps. The detection threshold of t >> 2^{256} far exceeds 2^{128}, so the detection regime is even harder than directly solving ECDLP. The proposed statistical test affords no computational advantage.

---

## Result: ECCG security does not imply H-PSEUDO (insufficient precision)

**Theorem (informal).** The proposed reduction ECCG-security → H-PSEUDO is not valid. Specifically:

1. **The bias is exponentially small.** H-PSEUDO at cryptographic scale bounds |hat{f}(k)| ≤ C·sqrt(p) ≈ C·2^{128}, giving a normalized bias δ ≤ C·2^{-128}. This is below the detection threshold of any polynomial-time statistical test.

2. **The required observation window is super-polynomial.** Any test distinguishing δ from zero with constant advantage requires at least t = Ω(δ^{-2}) = Ω(2^{256}/C^2) observations. This is super-polynomial in the security parameter λ = log N ≈ 256, so it is not a PPT algorithm.

3. **Contradiction.** The proposed reduction implicitly assumes that observing t = poly(log N) values of x_j is sufficient to detect the Fourier bias. By the signal-to-noise analysis above, this assumption is false when δ ≤ C·2^{-128}. No contradiction of ECCG security arises.

4. **The circularity of the large-k strategy.** If one instead tries to detect the bias by computing the full DFT hat{f}(k) over all j = 0,…,N−1, this requires observing all N ≈ p ≈ 2^{256} values of x([j]G). Observing all N outputs is equivalent to constructing the full discrete log table, which solves ECDLP. The reduction is circular: it presupposes the ability to solve the problem it aims to contradict.

**Summary.** ECCG security (polynomial-time indistinguishability) operates at the level of computationally undetectable biases. H-PSEUDO is a statement about exact Fourier coefficients, which H-PSEUDO allows to be as large as C·sqrt(p) ≈ C·2^{128} in absolute terms but only as large as C·2^{-128} in normalized terms (as a fraction of N). A PPT ECCG distinguisher detecting a normalized bias of C·2^{-128} would need Ω(2^{256}) samples. No such algorithm is polynomial-time, and no contradiction of ECCG security is obtained.

**ECCG security does not imply H-PSEUDO at the required precision.**

---

## What a valid reduction would require

For the reduction to succeed, one of the following would need to hold:

### Option A: Stronger H-PSEUDO failure

If H-PSEUDO were defined with A >> N^{1/2+ε} for some ε > 0 (i.e., normalized bias δ >> N^{-1/2+ε}), then t = O(N^{1−2ε}) observations would suffice to detect the bias. For the reduction to yield a poly(log N)-time distinguisher, one would need:

    δ = A/N ≥ 1/poly(log N), i.e., A ≥ N/poly(log N)

This is vastly stronger than what H-PSEUDO permits (which allows A up to C·sqrt(N)). No algorithm exploiting only the weak ECCG security assumption could establish such a strong uniformity result.

### Option B: Non-black-box reduction

A non-black-box reduction that uses the algebraic structure of EC multiplication (beyond treating x_j as black-box random-looking values) might convert Fourier information about x_j into a prediction advantage. This is conceivable but would require techniques beyond the information-theoretic signal-to-noise argument above, and no such technique is currently known or suggested by the ECCG literature.

### Option C: Connecting to known ECCG pseudorandomness results

Shparlinski and collaborators have established unconditional pseudorandomness properties of x([j]G) (uniformity of distribution over short intervals, correlation measures, etc.) using exponential sum bounds. These results go in the opposite direction: they prove pseudorandomness properties unconditionally, not by assuming ECCG security. A valid reduction would need to run the other way: from a Fourier anomaly to a predictability algorithm. No such result appears in the ECCG literature.

---

## Conclusion

The proposed reduction IDEA-20260804-28c15f (ECCG security → H-PSEUDO) is **not valid** for the following reasons:

1. **Precision mismatch.** H-PSEUDO failure produces a normalized Fourier bias δ ≤ C·2^{-128} at cryptographic scale. This is exponentially below the detection threshold of any polynomial-time statistical test applied to a polynomial-length ECCG prefix.

2. **Circular full-DFT strategy.** Computing the full Fourier transform to find the biased frequency k* requires observing all N ECCG outputs, which is computationally equivalent to solving ECDLP by brute-force table construction.

3. **ECCG security operates at polynomial-time scale.** The security assumption concerns computationally indistinguishable biases — biases that are present but exponentially small and hence undetectable in polynomial time. H-PSEUDO is a statement about the exact size of Fourier coefficients, not their computational detectability.

**Disposition of IDEA-20260804-28c15f**: The reduction route is **blocked by the signal-to-noise argument**. The idea is not falsified as a direction for H-PSEUDO research; it is falsified as a valid polynomial-time reduction from ECCG security. An alternative conditional proof of H-PSEUDO would need to proceed via algebraic structure theorems (e.g., Weil/Deligne bounds for character sums over EC groups) rather than via information-theoretic reduction from computational assumptions.

**The secondary idea IDEA-20260804-24b025** (linear complexity → H-PSEUDO) is similarly blocked: F_p linear complexity of x([j]G) and the Z/N DFT of 1_{x([j]G)<B} live in unrelated algebraic settings, and no general connection is available. This warrants separate analysis.
