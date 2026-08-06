# Weyl Differencing Approach for H-PSEUDO

**Task:** TASK-20260804-104  
**Batch:** BATCH-082  
**Context:** DEC-20260804-53c89f (Weil closed, Weyl proposed as the last analytic candidate)  
**Date:** 2026-08-04

---

## Setup and strategy

### The sum to bound

Define the indicator function of the factor base:

    f(j) = 1_{x([j]G) < t}   (1 if the j-th discrete-log preimage has x-coord in [0,t))

The DFT coefficient is:

    hat{1_F}(k) = Σ_{j=0}^{N-1} f(j) · e^{2πi kj/N}

where N = #E(F_p), B = |F| = #{j : f(j)=1} ≈ tN, and t = B/N is the factor-base density.

**H-PSEUDO target:** |hat{1_F}(k)| = O(B^{1/2}) for k ≠ 0.

### Weyl strategy

Weyl differencing reduces bounding |hat{f}(k)| to bounding the **correlations**:

    C_h = Σ_j f(j) · f(j+h) = |{j : x([j]G) < t  AND  x([(j+h)]G) < t}|
        = |{P ∈ F : P + [h]G ∈ F}|

For h = 0: C_0 = B (trivially).  
For h ≠ 0 and R = [h]G "random": if x(P) and x(P+R) were independent, then
C_h ≈ B · (B/N) = B²/N.

The excess C_h − B²/N is the "correlation signal" that Weyl differencing bounds.

---

## Van der Corput inequality and the correlation sum

### Exact form applied here

The van der Corput / Weyl-van der Corput (WvdC) inequality states: for
a_j = f(j) e^{2πi kj/N},

    |hat{f}(k)|² = |Σ_j a_j|²
                 ≤ (N/H) · Σ_{|h| < H} (1 − |h|/H) · |Σ_j a_{j+h} ā_j|

where ā_j = f(j) e^{−2πi kj/N}. Computing the inner product:

    a_{j+h} ā_j = f(j+h) · f(j) · e^{2πi kh/N}

    ⟹  Σ_j a_{j+h} ā_j = e^{2πi kh/N} · C_h,   so   |Σ_j a_{j+h} ā_j| = C_h

Therefore:

    |hat{f}(k)|² ≤ (N/H) · Σ_{h=0}^{H-1} C_h                             (WvdC)

### Sum of all correlations is exact

**Exact identity:**

    Σ_{h=0}^{N-1} C_h
      = Σ_h |{j : f(j)=1, f(j+h)=1}|
      = Σ_{j: f(j)=1} |{h : f(j+h)=1}|
      = Σ_{j: f(j)=1} B
      = B · B = B²

This is an exact combinatorial identity; it holds regardless of the distribution
of EC points.

### WvdC with H = N gives the trivial bound

Setting H = N in (WvdC):

    |hat{f}(k)|² ≤ (1/N) · Σ_{h=0}^{N-1} C_h · (1 − h/N)
                 ≤ (1/N) · B² = B²/N... 

Wait — the WvdC with the triangle inequality on |Σ_j a_{j+h} ā_j| = C_h:

    |hat{f}(k)|² ≤ (N/H) · H · max_h C_h = N · max_h C_h ≤ N · B

gives |hat{f}| ≤ sqrt(NB), which for B ≪ N is **worse than the trivial bound B**.

Alternatively, taking H = N and summing all correlations:

    |hat{f}(k)|² ≤ (N/N) · Σ_{h=0}^{N-1} C_h = B²   ⟹   |hat{f}| ≤ B

This recovers exactly the trivial triangle-inequality bound. WvdC with the
full correlation sum yields no improvement.

---

## First-order Weyl bound via estimated correlations

### Optimized WvdC with window H

For an arbitrary window H, bound C_h ≤ C_0 + error:

- C_0 = B (h = 0 term)
- C_h ≤ B for all h (trivial)

Setting H = sqrt(N/(2t)) where t = B/N optimizes the bound (details below), but
with only the trivial C_h ≤ B available:

    |hat{f}(k)|² ≤ (N/H) · (B + 2H · B) ≈ 3NB

    |hat{f}(k)| ≤ sqrt(3NB) = sqrt(3) · sqrt(N) · sqrt(B)

For B ≪ N this is worse than the trivial bound B.

### Can C_h ≈ B²/N be established non-circularly?

The deviation C_h − B²/N counts:

    C_h − B²/N = |{P ∈ E(F_p) : x(P) < t, x(P + R) < t}| − (B/N)²

For fixed R = [h]G, the value x(P+R) as P varies over F is a function of the
EC arithmetic. Bounding this deviation by O(B/sqrt(N)) requires knowing that the
pairs (x(P), x(P+R)) are nearly uniformly distributed in [0,t) × [0,t) — a
Weil-type equidistribution statement.

However, proving |C_h − B²/N| = O(B/sqrt(N)) requires applying the Weil bound
to the character sum:

    Σ_{P ∈ E(F_p)} ψ_1(x(P)) · ψ_2(x(P + R))

This sum involves the structure of the isogeny [h], which encodes the discrete
log of R. Every non-circular route to bounding this sum either (a) reduces to
the Weil bound on a curve-specific L-function that requires factoring or DL, or
(b) gives only the trivial bound C_h ≤ B.

**DL circularity recurs.** Any correlation bound sharper than C_h ≤ B that
holds for all h would, by summing over h, imply equidistribution of the sequence
(x([j]G))_{j<N} beyond what Weil gives unconditionally — and that stronger
equidistribution is essentially equivalent to H-PSEUDO itself.

### Bound obtained assuming C_h ≈ B²/N (hypothetically, and circularly)

If we assume |C_h − B²/N| ≤ B/sqrt(N) for all h ≠ 0, then:

    Σ_{h=0}^{N-1} C_h ≤ B + (N-1)(B²/N + B/sqrt(N))
                       ≈ B + B² + B·sqrt(N)

Applying (WvdC) with H = N (and the extra N factor from the task statement's
form where S_h carries no 1/N normalization):

    |hat{f}(k)|² ≤ N · (B + B² + B·sqrt(N))
                  ≈ N · B · sqrt(N) = B · N^{3/2}

    |hat{f}(k)| ≤ B^{1/2} · N^{3/4}

For B = tN: N^{3/4} = (B/t)^{3/4} · t^{3/4} = B^{3/4}/t^{3/4} · t^{3/4} · (N/B)^{3/4} · (B/N)^{3/4}...

More directly: H-PSEUDO needs |hat{f}| = O(B^{1/2}); this bound gives O(B^{1/2} · N^{3/4}).
Since N ≫ 1, this is **much worse** than the H-PSEUDO target, even under the circular
assumption C_h ≈ B²/N.

The h = 0 term C_0 = B dominates Σ_h C_h only when B ≫ B²: i.e., B ≪ 1. For any
non-trivial factor base (B ≥ 1), the off-diagonal sum B² is at least as large as B.
**The correlation sum Σ C_h = B² is too large to give a useful Weyl bound.**

---

## Difference operator approach (s = 1 Weyl differencing)

### Setup

Define the first difference operator Δ_h f(j) = f(j+h) − f(j). Since f is
{0,1}-valued, Δ_h f takes values in {−1, 0, +1}.

The L² norm of Δ_h f:

    ||Δ_h f||_2² = Σ_j |Δ_h f(j)|²
                 = |{j : f(j)=1, f(j+h)=0}| + |{j : f(j)=0, f(j+h)=1}|
                 = (B − C_h) + (B − C_h)
                 = 2(B − C_h) ≤ 2B

### Why additive differencing is tautological

Note that hat{Δ_h f}(k) and hat{f}(k) are directly related:

    hat{Δ_h f}(k) = Σ_j (f(j+h) − f(j)) e^{2πi kj/N}
                  = e^{−2πi kh/N} hat{f}(k) − hat{f}(k)
                  = (e^{−2πi kh/N} − 1) · hat{f}(k)

Therefore:

    |hat{Δ_h f}(k)| = 2|sin(πkh/N)| · |hat{f}(k)|

Any inequality of the form |hat{f}|² ≤ N · Σ_h |hat{Δ_h f}(k)| is equivalent
to an inequality in |hat{f}| itself:

    |hat{f}| ≤ N · Σ_h 2|sin(πkh/N)| = O(N²)

This is completely trivial. The additive difference hat{Δ_h f}(k) carries no new
information beyond hat{f}(k) — Fourier and differencing commute.

### Cauchy–Schwarz applied to difference norms

A bound that genuinely separates hat{f} from Δ_h f must go through the L² norm
of Δ_h f directly. By Cauchy–Schwarz:

    |hat{Δ_h f}(k)| = |Σ_j Δ_h f(j) · e^{2πi kj/N}|
                    ≤ sqrt(N) · ||Δ_h f||_2      (Cauchy–Schwarz)
                    ≤ sqrt(N) · sqrt(2B)          (using ||Δ_h f||_2 ≤ sqrt(2B))
                    = sqrt(2NB)

If the WvdC inequality could be written as |hat{f}|² ≤ N · Σ_h |hat{Δ_h f}|
(treating it as independent of hat{f}), then summing over h = 0, ..., N−1:

    |hat{f}|² ≤ N · N · sqrt(2NB) = N^{5/2} · sqrt(2B)

    |hat{f}| ≤ N^{5/4} · (2B)^{1/4}

For B = tN:

    N^{5/4} · (2tN)^{1/4} = 2^{1/4} · t^{1/4} · N^{5/4} · N^{1/4} = 2^{1/4} · t^{1/4} · N^{3/2}

This is catastrophically worse than both the trivial bound B = tN and the
H-PSEUDO target B^{1/2} = t^{1/2} N^{1/2}.

**Note on task-description bound:** The task description reaches |hat{f}| ≤ N · (2B)^{1/4}
(omitting one sqrt(N) from the Cauchy–Schwarz step). With the correct sqrt(N) factor the
bound becomes N^{5/4} · (2B)^{1/4}. In both forms the conclusion is the same: the bound
grows with N and is far worse than the H-PSEUDO target.

---

## Result: Weyl gives |hat| = O(N^{5/4} · B^{1/4}) — worse than H-PSEUDO target O(B^{1/2})

Comparison table for the cryptographically relevant parameter range B ~ N^{0.1}–N^{0.5}:

| Bound                          | Form                     | Notes                            |
|-------------------------------|--------------------------|----------------------------------|
| Trivial (triangle inequality) | B                        | Reference                        |
| Cauchy–Schwarz                | sqrt(NB)                 | Worse than trivial for B ≪ N    |
| WvdC via C_h ≤ B             | sqrt(NB) or worse        | No improvement                   |
| WvdC + assumed C_h ≈ B²/N   | B^{1/2} · N^{3/4}       | Worse than trivial; circular     |
| Difference-norm (s=1)        | N^{5/4} · B^{1/4}       | Much worse; tautological step    |
| **H-PSEUDO target**          | **B^{1/2}**              | Required for index-calculus      |

No version of Weyl differencing reaches the H-PSEUDO target B^{1/2} from above.

---

## Why Weyl doesn't work here

### Structural mismatch

Weyl differencing is designed for exponential sums of the form:

    Σ_j e^{2πi g(j)}

where the **amplitude is constant 1** and the **phase g(j) is a polynomial**
(or has polynomial-like iterated differences). The power of the method is that
iterated differences Δ_{h_1} · · · Δ_{h_{s-1}} g(j) become "equidistributed"
after s steps if the degree-s coefficient of g is irrational (resp., has
bounded rational approximation). The amplitude being 1 ensures no "indicator
function oscillation" — the whole difficulty is in the phase.

For our sum hat{f}(k) = Σ_j 1_F(j) · e^{2πi kj/N}:

- The **phase kj/N is already linear** — Weyl would normally need only 1 step
  to eliminate it entirely, and indeed: Δ_h (kj/N) = kh/N is constant, so the
  "polynomial structure" is as favorable as possible.
- But the **amplitude 1_F(j) is an irregular indicator function**, and
  differencing the amplitude (not the phase) does nothing useful: ||Δ_h f||_2²
  is bounded only by 2B regardless of h, so each differencing step leaves a
  factor of B^{1/2} unimproved.

### The correlation sum is exactly B²

The fundamental obstruction is the exact identity Σ_h C_h = B². Any WvdC
application that bounds |hat{f}|² in terms of Σ_h C_h immediately yields
|hat{f}| ≤ B (trivial). Improving on this requires showing that C_h is much
smaller than B/N for most h — which is equidistribution of EC point pairs, and
that requires either the Weil bound (DL-circular) or already knowing H-PSEUDO.

### DL circularity recurs in any sharper correlation bound

The only route to |C_h − B²/N| = o(B) requires bounding a two-point character
sum over E(F_p). For varying h (and hence R = [h]G varying over group elements),
this sum is an instance of a mixed character sum on the curve, and its evaluation
requires knowing the factored form of [h] or its isogeny structure. Unconditional
non-circular results bound C_h only by the trivial B.

### Generic bounded functions achieve the trivial bound

For any {0,1}-valued function f on Z/NZ with Σ f(j) = B, the Parseval identity gives:

    Σ_k |hat{f}(k)|² = N · B

Therefore max_{k≠0} |hat{f}(k)|² ≥ (NB − B²)/(N−1) ≈ B for B ≪ N.

The trivial bound |hat{f}| ≤ B is not improvable by any method that treats f as a
generic L∞ function. H-PSEUDO asserts that the specific EC structure of the
sequence ([j]G) makes |hat{f}| ≪ B — this is a statement about the arithmetic of
the curve, not about the indicator function in isolation. Weyl/WvdC is an
arithmetic-analysis tool for polynomial phases, not an EC arithmetic tool, and
so cannot see this structure.

---

## Conclusion

**The Weyl differencing approach does not give a useful bound for H-PSEUDO.**

Summary of findings:

1. **WvdC via correlations C_h:** The exact identity Σ_h C_h = B² forces the
   WvdC bound back to |hat{f}| ≤ B (trivial). No improvement is possible
   unless C_h can be bounded below B for h ≠ 0.

2. **C_h bounds require DL structure:** Proving C_h ≈ B²/N requires
   equidistribution of point pairs (P, P+R) on the curve, which every known
   non-circular method cannot do better than the trivial bound.

3. **Even with circular C_h ≈ B²/N assumption:** The WvdC bound gives
   |hat{f}| ≤ B^{1/2} · N^{3/4}, which is much weaker than the H-PSEUDO target
   B^{1/2} (by a factor N^{3/4}).

4. **Difference-norm approach (s=1):** Gives |hat{f}| ≤ N^{5/4} · B^{1/4},
   dramatically worse than both trivial and target. The additive-difference step
   is tautological (Fourier and differencing commute).

5. **Root cause:** Weyl differencing exploits polynomial-phase structure; 1_F
   has trivial (linear) phase structure and all difficulty resides in the
   irregular amplitude. Methods that work for generic bounded-amplitude
   indicator functions cannot reach the H-PSEUDO target.

**Verdict: CLOSED.** Weyl differencing is not a viable route to H-PSEUDO.

**Remaining candidate:** Hecke characters for CM curves (conditional on
non-generic structure; not applicable to standard cryptographic curves).
Practically, this means H-PSEUDO is unproven by all identified analytic methods.

**Evidence record:** DEC-20260804-53c89f (Weil closed), this analysis (Weyl closed).
