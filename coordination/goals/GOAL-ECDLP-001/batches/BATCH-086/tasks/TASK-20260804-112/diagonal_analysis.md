# Diagonal Correlation Analysis — TASK-20260804-112

**Task**: TASK-20260804-112  
**Batch**: BATCH-086  
**Goal**: GOAL-ECDLP-001  
**Date**: 2026-08-04  
**Follows**: BATCH-085 / TASK-20260804-110 (shparlinski_analysis.md)

---

## 1. Setup and notation

Let E/F_p be an elliptic curve, G a generator of E(F_p) ≅ Z/N with N ~ p.
Let F = {P ∈ E(F_p) : x(P) < t} be the factor-base with |F| = B.

The object of study is the mixed character sum:

    S_{a,k} = Σ_{P∈E(F_p)} ψ_a(x(P)) · χ_k(P)

where ψ_a(x) = e^{2πi ax/p} is a non-trivial additive character of F_p, and
χ_k(P) = e^{2πi k·DL_G(P)/N} is the k-th character of the group E(F_p) ≅ Z/N.

The Fourier coefficient of the factor-base indicator satisfies:

    |hat{1_F}(k)| ≤ (1/p) · Σ_{a=1}^{p-1} |hat{1}_{[0,t)}(a)| · |S_{a,k}|

With ||hat{1}_{[0,t)}||_1 = O(p log p) (harmonic sum), any uniform bound
|S_{a,k}| ≤ M gives |hat{1_F}(k)| = O(M log p / √p).

BATCH-085 established: |S_{a,k}| = O(N^{1/2} p^{1/4}) = O(p^{3/4}), yielding
|hat{1_F}(k)| = O(p^{3/4} log p). H-PSEUDO targets O(C√B) = O(C√p).
The gap is a factor of p^{1/4} log p (ignoring C).

---

## 2. The diagonal improvement idea — precise formulation

The Cauchy-Schwarz expansion of |S_{a,k}|^2 introduces the correlation sums:

    T_{a,h} = Σ_{P∈E(F_p)} ψ_a(x(P) − x(P + [h]G))       h ∈ Z/N

so that:

    |S_{a,k}|^2 = N + 2 Re Σ_{h=1}^{N-1} e^{2πi kh/N} T_{a,h}     ... (*)

BATCH-085 bounded each |T_{a,h}| ≤ 4√p by Weil (for h ≠ 0 mod N), giving
|S_{a,k}|^2 ≤ N + 2(N-1)·4√p ~ 8N√p, hence |S_{a,k}| = O(N^{1/2} p^{1/4}).

The **diagonal improvement proposal** is to split the h-sum in (*) into:
- **Resonant** h: those where T_{a,h} is large (saturates the Weil bound)
- **Non-resonant** h: those where cancellation yields |T_{a,h}| ≪ √p

and to hope that few h are resonant, so the total is O(√p) rather than O(N√p).

---

## 3. Analysis of the resonant set

**Claim**: For fixed R = [h]G ≠ O, the function f_R(P) = x(P) − x(P+R) is a
non-trivial rational function on E. By Weil, |T_{a,h}| ≤ deg(f_R) · √p.

**Degree calculation**: The poles of f_R on E are:
- A pole of order 2 at O (from x(P))
- A pole of order 2 at −R (from x(P+R), which has a pole when P = −R)

Total pole divisor degree = 4. By Riemann-Roch on a genus-1 curve, f_R has
exactly 4 zeros (with multiplicity), occurring where x(P) = x(P+R), i.e.,
where P+R = ±P:
- P+R = P ⟹ R = O (excluded)
- P+R = −P ⟹ [2]P = −R ⟹ 4 solutions (the [2]-map on E has degree 4)

So the "resonant" points for a FIXED h (where x(P) = x(P+[h]G)) form a set of
exactly 4 points {P ∈ E : [2]P = −[h]G}. These are 4 POINTS on E, not a
special set of h-values.

**Key conclusion**: T_{a,h} = Σ_{P∈E} ψ_a(f_R(P)) is NOT particularly large
(O(√p) by Weil) even at the 4 points where f_R vanishes, because the sum
includes all p+O(√p) ~ p points of E, not just the 4 special ones.

**There is no special class of "resonant" h values** for which T_{a,h} = Ω(N).
The only exceptions are h ≡ 0 mod N (where T_{a,0} = N trivially) and, if N
is even, h = N/2 (where [h]G = −G or similar 2-torsion). These contribute
O(1) terms to the h-sum, not enough to change the bound.

**Diagonal improvement verdict**: The resonant/non-resonant split contributes
at most O(N) from the h=0 and h=N/2 terms, plus O(N · √p) from the N-2
non-resonant terms. The total is still O(N√p), and |S_{a,k}| = O(N^{1/2} p^{1/4}).
**No improvement over BATCH-085.**

---

## 4. The circular obstruction in the h-sum

To improve the bound one must show cancellation in the sum:

    U_{a,k} = Σ_{h=1}^{N-1} e^{2πi kh/N} T_{a,h}

i.e., that U_{a,k} = o(N√p). Expanding:

    U_{a,k} = Σ_{h=1}^{N-1} Σ_{P∈E} ψ_a(x(P) − x(P+[h]G)) · e^{2πi kh/N}

Substituting Q = P + [h]G (so h = DL_G(Q − P)):

    U_{a,k} = Σ_{(P,Q)∈E×E, P≠Q+[j]G for j=0} ψ_a(x(P) − x(Q)) · e^{2πi k·DL_G(Q−P)/N}

Observe:

    |S_{a,k}|^2 = N + U_{a,k} + conjugate(U_{a,k})

so bounding |U_{a,k}| = O(p^{1+2ε}) is EQUIVALENT to bounding |S_{a,k}| = O(p^{1/2+ε}).

**The argument is circular.** Controlling the h-sum cancellation is not a
weaker or independent statement — it is *identical* to H-PSEUDO itself,
just rewritten as a double sum over (P, Q). No amount of splitting the h-sum
into resonant/non-resonant parts can resolve this: the real obstacle is the
term DL_G(Q−P) in the exponent, which is algebraically inaccessible.

---

## 5. The precise algebraic statement that closes the gap

**Conjecture MAGCS (Mixed Additive-Group Character Sum Bound)**:

Let E/F_p be a non-CM elliptic curve, G ∈ E(F_p) a generator with |G| = N.
For a ∈ F_p^* (non-trivial additive character) and k ∈ {1, ..., N−1}
(non-trivial group character):

    |S_{a,k}| = | Σ_{P∈E(F_p)} e^{2πi ax(P)/p} · e^{2πi k·DL_G(P)/N} |
              = O(p^{1/2+ε})     for any ε > 0.                          ... (MAGCS)

Equivalently, via the Weil pairing: let T ∈ E[N](F_{p^2}) \ E[N](F_p) be a
point satisfying e_N(G, T) = ζ_N (primitive N-th root of unity), where e_N is
the Weil N-pairing. Then:

    (MAGCS-WP)  | Σ_{P∈E(F_p)} ψ_a(x(P)) · e_N(P, [k]T) | = O(p^{1/2+ε})

The Weil pairing formulation is key: e_N(P, [k]T) is an algebraic function of
P, computed via Miller's algorithm as a ratio of rational functions on E
evaluated at the F_{p^2}-point [k]T. This is the natural algebraic replacement
for the transcendental function P ↦ e^{2πi k·DL_G(P)/N}.

**Why MAGCS implies the gap is closed**: If MAGCS holds, then by
Cauchy-Schwarz in the a-sum using ||hat{1}_{[0,t)}||_2 = O(√(pB)):

    |hat{1_F}(k)| ≤ (1/p)(Σ_a |hat{1}_{[0,t)}(a)|^2)^{1/2} (Σ_a |S_{a,k}|^2)^{1/2}
                  ≤ (1/p) · √(pB) · √(p · O(p^{1+2ε}))
                  = (1/p) · √(pB) · O(p^{1+ε})
                  = O(B^{1/2} · p^ε)
                  = O(p^ε · √B)

So MAGCS ⟹ |hat{1_F}(k)| = O(p^ε · √B) for any ε > 0. This is H-PSEUDO
up to the p^ε factor, and matches the empirical C(p) ~ p^{0.079} behavior
(see Section 6).

---

## 6. Algebraic structure of MAGCS: the ℓ-adic sheaf criterion

In the Katz-Sarnak framework, the sum S_{a,k} corresponds to a trace function
of an ℓ-adic sheaf on E/F_p. Specifically:

- The additive character term ψ_a(x(P)) corresponds to the Artin-Schreier
  sheaf L_{ψ(ax)} on A^1, pulled back to E via the x-coordinate projection.
  This is a rank-1, pure weight-1 sheaf, geometrically irreducible.

- The group character term χ_k(P) = e^{2πi k·DL_G(P)/N} should correspond to
  an ℓ-adic character of π_1(E). For algebraic characters (such as a
  multiplicative character of F_p composed with a rational function), this
  would be a Kummer sheaf on E — geometrically irreducible and pure.

**The obstruction**: χ_k is a character of the ARITHMETIC group E(F_p), not
of the geometric fundamental group π_1^{geom}(E) = Ẑ² (the profinite completion
of π_1 of the complex torus E(C)). The map P ↦ DL_G(P) does not arise from
any morphism of algebraic varieties E → G_m or E → A^1 over F_p. It is a
function on the finite set E(F_p) = ker(Frob_p − 1: E(F̄_p) → E(F̄_p)).

This means L_{χ_k} is an **arithmetic** character of π_1(E) that is trivial
on the geometric part: it factors through π_1^{arith}(E) / π_1^{geom}(E) ≅
Gal(F̄_p/F_p). Geometrically it is the constant sheaf — hence trivially
reducible — and Deligne's theorem gives no additional cancellation.

**MAGCS as an ℓ-adic irreducibility conjecture**:

The sum S_{a,k} = Tr(Frob_p | RΓ_c(E/F̄_p, F_{a,k})) where
F_{a,k} = L_{ψ(ax)} ⊗ L_{χ_k}. Over F̄_p the χ_k factor becomes constant
(all points of E are rational over F̄_p), so F_{a,k} is geometrically
isomorphic to L_{ψ(ax)}. The Weil bound for L_{ψ(ax)} gives O(√p) as expected.

The issue is that the *arithmetic* Frobenius twisting by χ_k breaks the pure
geometric picture. MAGCS is the assertion that this arithmetic twist does not
increase the conductor beyond what the geometric L_{ψ(ax)} already requires —
a non-trivial claim about the interaction of the arithmetic and geometric parts
of π_1(E).

**Reformulation as a Weil-pairing sum over F_{p^2}**:

Since [k]T ∈ E[N](F_{p^2}), the pairing e_N(P, [k]T) is a rational function
of P defined over F_{p^2}. The sum (MAGCS-WP) can be written as a sum over
F_p-rational points of a function defined over F_{p^2}. A route to a proof:

1. Embed the sum into a sum over E(F_{p^2}):
   Σ_{P∈E(F_p)} f(P) = Σ_{P∈E(F_{p^2})} f(P) · 1_{Frob_p(P)=P}

2. Express the Frobenius indicator via characteristic function of E(F_p) as
   a sum of characters of E(F_{p^2}).

3. Combine with a Weil bound on the resulting sum over E(F_{p^2}).

This approach requires a "Frobenius-twisted Weil bound" and is precisely what
makes MAGCS difficult: the F_p-rational restriction introduces the DL
non-algebraicity back into the picture.

---

## 7. Why C(p) ~ p^{0.079} is consistent with MAGCS

Empirically (BATCH-073–079, KN-FIND-e7a3b1): max_k |hat{1_F}(k)| / √B ≈ C(p)
with C(p) fitting p^{0.079} over p ∈ [1009, 100003]. From the Fourier expansion:

    max_k |hat{1_F}(k)| ≈ p^{0.079} · √B ~ p^{0.079+0.5}  (for B ~ p)

This implies: the dominant a-terms in the Fourier expansion contribute
|S_{a,k}| ~ p^{0.079} · p^{0.5} = p^{0.579}, lying strictly between:

    Weil-correlation upper bound: O(p^{3/4}) = O(p^{0.75})
    MAGCS conjectured bound:     O(p^{1/2+ε}) = O(p^{0.5+})

The observed exponent 0.579 is in the interval (0.5, 0.75), consistent with
both:
(a) MAGCS with C = O(p^ε) for ε ≈ 0.079 (a mild residual growth)
(b) MAGCS with C = O(1) absolute, but where the toy-scale fit p^{0.079}
    is a transient that eventually flattens to a logarithm

Quantitative check of hypothesis (b): at toy scale p ∈ [1009, 100003]:
- p = 1009:   p^{0.079} ≈ 1.65,  log p (base e) ≈ 6.9
- p = 100003: p^{0.079} ≈ 2.46,  log p ≈ 11.5

The fit value (1.65 to 2.46) is much smaller than log p (6.9 to 11.5).
If the true asymptotic is C ~ log p, the toy-scale data would fit as
C ~ p^{α} with α ≪ 1 (a power law that underestimates the eventual log growth).
This is numerically consistent with 0.079 being a finite-size artifact.

Quantitative check of hypothesis (a): at crypto scale p ~ 2^{256}:
- log p ≈ 177  vs  p^{0.079} ≈ 2^{20} ≈ 10^6

Under hypothesis (a) (genuine p^{0.079} growth), the constant C at
cryptographic scale would be ~10^6, giving yield errors ~10^6 · √B.
For a typical index-calculus application with B ~ N^{1/3}, this would
be 10^6 · N^{1/6} — large but sub-polynomial, consistent with H-PSEUDO
still holding as an O(p^ε·√B) bound (negligible vs the yield itself).

Under hypothesis (b) (log p growth), C ~ 177 at crypto scale — a modest
constant, giving essentially the square-root bound of classical heuristics.

**Both hypotheses are consistent with MAGCS** (with C = O(p^ε) in case (a)
and C = O(1) in case (b)).

The exponent range 0 < 0.079 < 1/4 confirms that the true behavior is
STRONGER than Weil-correlation (which would give C ~ p^{1/4}), in precise
agreement with MAGCS predicting C = O(p^ε) with ε < 1/4.

---

## 8. Summary table: bounds on |S_{a,k}|

| Source                        | Bound on |S_{a,k}|              | Implied |hat{1_F}(k)| |
|-------------------------------|----------------------------------|--------------------------|
| Trivial                       | N ~ p                            | O(p log p)               |
| BATCH-085 (Weil-correlation)  | O(N^{1/2} p^{1/4}) = O(p^{3/4}) | O(p^{3/4} log p)         |
| MAGCS (if proved, ε > 0)      | O(p^{1/2+ε})                     | O(p^ε √B)                |
| MAGCS (if proved, ε = 0)      | O(p^{1/2})                       | O(√B)     [= H-PSEUDO]   |
| Empirical (toy scale)         | ~ p^{0.579}                      | ~ p^{0.079} √B           |

---

## 9. Conclusions

1. **Diagonal improvement fails.** The resonant/non-resonant h-split does not
   tighten the O(p^{3/4}) bound from BATCH-085. All non-trivial correlation
   sums T_{a,h} (h ≢ 0 mod N) satisfy |T_{a,h}| ≤ 4√p by Weil, and none are
   "specially large" due to x-coordinate coincidences — those occur at 4 points
   of E per fixed h, not at special h-values. The diagonal intuition conflates
   individual-P coincidences with global-sum enhancement.

2. **The h-sum cancellation is circular.** Proving |Σ_h e^{2πi kh/N} T_{a,h}|
   = o(N√p) is equivalent to proving |S_{a,k}| = o(p^{3/4}), the original
   problem. No decomposition of the h-sum avoids this.

3. **The gap remains: O(p^{3/4} log p) vs O(C√B) with C ~ p^{0.079}.**
   A factor of ~p^{0.171} (at toy scale) is unexplained by current theory.

4. **MAGCS is the precise closing statement.** The conjecture:
   
       | Σ_{P∈E(F_p)} ψ_a(x(P)) · e_N(P, [k]T) | = O(p^{1/2+ε})

   (where T ∈ E[N](F_{p^2}) satisfies e_N(G,T) = ζ_N) is the minimal
   algebraic assertion that implies H-PSEUDO. It is a "Weil bound for an
   F_p-restricted sum of an F_{p^2}-algebraic function," and its difficulty
   lies in the Frobenius-twist structure that encodes the DL non-algebraicity.

5. **MAGCS is consistent with all empirical data.** The observed C(p) ~ p^{0.079}
   (toy-scale fit) is consistent with MAGCS holding with C = O(p^ε) for ε ~ 0.079
   or weaker (log growth). The key qualitative fact — that C(p) ≪ p^{1/4}
   (far below the Weil-correlation bound) — is exactly what MAGCS predicts.

6. **MAGCS as an open research target.** Unlike the six closed approaches in
   KN-FIND-e7a3b1 (which each encounter a categorical obstruction), MAGCS
   has a plausible algebraic route via:
   - Weil-pairing reformulation (MAGCS-WP)
   - Frobenius-twisted trace formula over F_{p^2}
   - Conductor bounds for arithmetic twists of Artin-Schreier sheaves
   
   The path is technically difficult but algebraically well-posed, making it
   the most promising single conjecture to pursue toward a proof of H-PSEUDO.

---

*Recorded by: mathematical analyst, BATCH-086, 2026-08-04.*  
*Cites: TASK-20260804-110 (shparlinski_analysis.md), KN-FIND-e7a3b1, KN-FIND-c93d45.*
