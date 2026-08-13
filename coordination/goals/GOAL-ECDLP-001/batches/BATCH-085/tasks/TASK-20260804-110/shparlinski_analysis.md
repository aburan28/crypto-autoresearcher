# Shparlinski EC Sequence Analysis for H-PSEUDO

**Task**: TASK-20260804-110  
**Batch**: BATCH-085  
**Goal**: GOAL-ECDLP-001  
**Date**: 2026-08-04

---

## Shparlinski's ECCG bounds

Shparlinski (1998–2000) studied the elliptic curve congruential generator (ECCG)
sequence x([j]G) mod p. The central exponential-sum result is:

**Complete sum** (j runs over all N group elements, [j]G sweeps E(F_p)):

    |S_{a,0}| = |Σ_{j=0}^{N-1} e^{2πi a x([j]G)/p}|
              = |Σ_{P ∈ E(F_p)} e^{2πi a x(P)/p}|
              ≤ 2√p

This is immediate from Weil's theorem: the sum is a standard additive-character sum on an
elliptic curve, and the function x(P) is a degree-2 rational map on E. No EC-specific
argument is needed; the bound is O(√p).

**Partial sum** (j runs over T < N consecutive group elements):

    |Σ_{j=0}^{T-1} e^{2πi a x([j]G)/p}| = O(p^{1/4} √T + p^{1/2})

Shparlinski's proof: square, introduce correlation variable h = j - j', and apply
Weil to each correlation sum T_{a,h} = Σ_P e^{2πi a(x(P)−x(P+[h]G))/p}.

For T = N ~ p: the partial-sum formula gives O(p^{3/4}), which is weaker than the
complete-sum Weil bound O(√p). This is not a contradiction — for the full sum the
algebraic periodicity of E(F_p) restores the Weil bound; for a proper initial
segment it does not.

---

## Expansion of 1_{x<t} via Fourier on F_p

The factor-base indicator 1_{x<t} is a function on F_p = {0,...,p−1}. Its DFT is:

    1_{x<t} = (t/p) + (1/p) Σ_{a=1}^{p-1} 1̂_{[0,t)}(a) · e^{2πi ax/p}

where the Fourier coefficient is the geometric sum:

    1̂_{[0,t)}(a) = Σ_{x=0}^{t-1} e^{-2πi ax/p}  =  (1 − e^{−2πi at/p}) / (1 − e^{−2πi a/p})

Pointwise bound: |1̂_{[0,t)}(a)| ≤ 1/|sin(πa/p)| ≤ p/(πa)  for  1 ≤ a ≤ p/2.

L^1 bound: Σ_{a=1}^{p-1} |1̂_{[0,t)}(a)| = O(p log p)  (harmonic sum).

L^2 bound: Σ_{a=1}^{p-1} |1̂_{[0,t)}(a)|^2 = p·t − t^2 ≈ p·t  (Parseval on F_p).

Since B = |F| ≈ t (each x-value in [0,t) is an x-coordinate of approximately one
point on E by the Hasse bound and Chebotarev equidistribution), we have t ≈ B and:

    Σ_{a=1}^{p-1} |1̂_{[0,t)}(a)|^2 ≈ pB.

---

## Mixed sum S_{a,k} formulation

Substituting the Fourier expansion into the H-PSEUDO character sum:

    1̂_F(k) = Σ_{j=0}^{N-1} 1_{x([j]G)<t} · e^{2πi kj/N}   (k ≠ 0)

    = (t/p) · Σ_{j=0}^{N-1} e^{2πi kj/N}           [= 0 for k ≠ 0]
      + (1/p) Σ_{a=1}^{p-1} 1̂_{[0,t)}(a) · S_{a,k}

where the **mixed sum** is:

    S_{a,k} = Σ_{j=0}^{N-1} e^{2πi a x([j]G)/p} · e^{2πi kj/N}
            = Σ_{P ∈ E(F_p)} e^{2πi a x(P)/p} · e^{2πi k·DL_G(P)/N}

It combines two characters:

- ψ_a(P) = e^{2πi a x(P)/p}:  an **additive character of F_p** applied to x(P),
  which is an algebraic rational function of the coordinates of P.

- χ_k(P) = e^{2πi k·DL_G(P)/N}:  a **group character of E(F_p) ≅ Z/N**. This
  factors as e^{2πi k·DL_G(P)/N}, where DL_G(P) is the discrete logarithm of P
  base G in Z/N.

The H-PSEUDO bound max_k |1̂_F(k)| ≤ C√B is equivalent (via this expansion) to:

    max_k |(1/p) Σ_{a≠0} 1̂_{[0,t)}(a) · S_{a,k}| ≤ C√B.

---

## Can Shparlinski extend to mixed sums?

### The Weil machine requires algebraic characters

Shparlinski's proof for the complete sum S_{a,0} uses Weil's theorem: the sum
Σ_{P ∈ E} ψ(f(P)) is bounded by O(√p) when f is a rational function on E and ψ
is a non-trivial additive character of F_p.

For S_{a,k} with k ≠ 0, the second factor χ_k(P) = e^{2πi k·DL_G(P)/N} is NOT
an algebraic character of E:

1. **DL_G is not a rational map.** The function P ↦ DL_G(P) takes the discrete
   value j ∈ {0,...,N−1} such that [j]G = P. There is no polynomial or rational
   expression in x(P), y(P) over F_p that computes DL_G(P) — if there were,
   ECDLP would be in polynomial time.

2. **Weil requires algebraic input.** The Weil machine (étale cohomology, Bombieri,
   Deligne) bounds sums Σ_P ψ(f(P))χ(P) where f is a rational function on E and
   χ is a multiplicative character of F_p applied to a rational function. The
   character χ_k is a character of the GROUP Z/N; it is algebraic only if it factors
   through a rational map E → G_m or E → A^1. It does not.

3. **This is the same DL-circularity obstruction as BATCH-067 (Weil/étale approach).**
   The table in KN-FIND-e7a3b1 explicitly lists this: "DL_G(P) is non-algebraic;
   wrong functional form." The Shparlinski route arrives at the same wall.

### The Weil-correlation workaround (and its limit)

Although we cannot directly apply Weil to S_{a,k}, we can bound |S_{a,k}|^2 by
expanding and applying Weil to each correlation term:

    |S_{a,k}|^2 = |Σ_j e^{2πi(ax([j]G)/p + kj/N)}|^2
                = Σ_{j,j'} e^{2πi(a(x([j]G)−x([j']G))/p + k(j−j')/N)}
                = N + Σ_{h=1}^{N-1} e^{2πi kh/N} T_{a,h} + conj.

where the **correlation sum** is:

    T_{a,h} = Σ_{j=0}^{N-1} e^{2πi a(x([j]G) − x([j+h]G))/p}
            = Σ_{P ∈ E(F_p)} e^{2πi a(x(P) − x(P+[h]G))/p}

For each fixed h, the function P ↦ x(P) − x(P+[h]G) IS a rational function on E
(translation by [h]G is an algebraic automorphism). By Weil:

    |T_{a,h}| ≤ C·√p    for each h ≠ 0 and a ≠ 0.

Bounding |S_{a,k}|^2 in the worst case (all Weil bounds saturate, no sign cancellation
across h):

    |S_{a,k}|^2 ≤ N + 2Σ_{h=1}^{N-1} |T_{a,h}| ≤ N + 2(N−1)·C√p ≤ 2CN·√p

For N ~ p:

    |S_{a,k}| ≤ √(2CN·√p) = O(N^{1/2} p^{1/4}) = O(p^{3/4}).

This mirrors Shparlinski's partial-sum bound: both use "Cauchy-Schwarz + Weil on
correlations." The DL character e^{2πi kj/N} plays the same role as the partial-sum
truncation indicator 1_{j<T}: it prevents using the algebraic periodicity of the
complete orbit, so the correlation method gives p^{3/4} rather than p^{1/2}.

### The circular obstruction in the h-sum

The Weil-correlation bound loses a factor of N^{1/2} p^{-1/4} relative to the k=0
case. To recover it, one would need sign cancellation in Σ_h e^{2πi kh/N} T_{a,h},
specifically:

    |Σ_{h=1}^{N-1} e^{2πi kh/N} T_{a,h}| = O(√p)    (rather than O(N√p))

But this expression is the Fourier transform (in h) of h ↦ T_{a,h}, evaluated at
frequency k. Asking for this to be O(√p) is a pseudorandomness statement about the
correlation sequence h ↦ T_{a,h} — which, by a second application of the same
Fourier expansion, reduces to bounding a sum of the form S_{a,k} again. The
argument is circular: the h-sum cancellation is equivalent to (a two-index version
of) H-PSEUDO itself.

---

## Quantitative bound from the Weil-correlation method

Combining the pointwise bound |S_{a,k}| = O(p^{3/4}) with the L^1 norm of the
Fourier coefficients of 1_{x<t}:

    |1̂_F(k)| ≤ (1/p) · Σ_{a=1}^{p-1} |1̂_{[0,t)}(a)| · |S_{a,k}|
              ≤ (1/p) · O(p log p) · O(p^{3/4})
              = O(p^{3/4} log p)

**Comparison of rigorous upper bounds:**

| Method                        | Bound on |1̂_F(k)|          | Bound for B=O(p), N~p |
|-------------------------------|-------------------------------|----------------------|
| Trivial (|S_{a,k}| ≤ N)       | O(N log p) = O(p log p)       | O(p log p)           |
| Cauchy-Schwarz + Parseval     | √(BN) = O(p) for B=O(p)      | O(p)                 |
| Weil-correlation (this work)  | O(p^{3/4} log p)              | O(p^{3/4} log p)     |
| **H-PSEUDO target**           | C·√B                          | **O(√p)**            |

The Weil-correlation method gives the best rigorous bound, but falls short of
H-PSEUDO by a factor of p^{1/4} log p. Note also that the Parseval identity on Z/N:

    Σ_{k=0}^{N-1} |1̂_F(k)|^2 = N·B

gives the average |1̂_F(k)|^2 ≈ B over k ≠ 0 (consistent with H-PSEUDO as an
average statement), but does not bound the maximum.

---

## Verdict and obstruction

**Conclusion**: Shparlinski's ECCG work does NOT provide a proof of H-PSEUDO.

**The DL-circularity obstruction recurs.** The mixed sum S_{a,k} requires bounding
a character sum that combines an algebraic additive character of F_p (via x(P)) with
a non-algebraic group character of E(F_p) ≅ Z/N (via DL_G(P)). Weil-type tools can
handle the former but not the latter. This is the same obstruction recorded in
BATCH-067 and tabulated in KN-FIND-e7a3b1.

**Shparlinski bounds the wrong object.** His ECCG result is about the
OUTPUT pseudorandomness of x([j]G): the sequence of x-coordinates is
equidistributed in F_p. H-PSEUDO requires INPUT pseudorandomness: the INDEX SET
{j : x([j]G) < t} ⊆ Z/N is equidistributed in Z/N. These are different levels
of pseudorandomness. Equidistribution of outputs controls |S_{a,0}| (via Weil);
equidistribution of input positions requires controlling |S_{a,k}| for k ≠ 0,
which involves DL_G.

**Best achievable bound.** The Weil-correlation method gives a rigorous, Shparlinski-
compatible bound of |1̂_F(k)| = O(p^{3/4} log p), which is O(p^{1/4} log p) weaker
than H-PSEUDO's O(√p) target. Closing this gap would require establishing that the
correlation sequence h ↦ T_{a,h} has pseudorandom Fourier coefficients in h — a
statement that self-referentially reduces to H-PSEUDO. No further progress is possible
via Shparlinski's techniques without an external source of pseudorandomness for DL.

**H-PSEUDO remains an open problem.** This analysis adds a seventh negative
result to the six documented in KN-FIND-e7a3b1: Shparlinski's ECCG approach reaches
the same DL-circularity wall as Weil/étale, Michel-Venkatesh, DDH, BGS, Weyl, and
the random-permutation assumption. The empirical C(p) ~ p^{0.079} is consistent with
O(p^{3/4}·log p) being a loose upper bound; the true bound appears to be O(p^{0.079}·√B),
which is strictly between O(√B) (H-PSEUDO) and O(p^{3/4} log p) (this analysis).
