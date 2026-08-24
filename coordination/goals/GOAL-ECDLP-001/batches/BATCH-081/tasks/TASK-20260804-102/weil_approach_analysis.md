# Weil Bound Approach for H-PSEUDO

**Task:** TASK-20260804-102  
**Goal:** GOAL-ECDLP-001  
**Batch:** BATCH-081  
**Analyst role:** Mathematical analyst  
**Source decision:** DEC-20260804-ba880f (BATCH-080: DDH closed, Weil approach proposed)

---

## Setup and reformulation

**H-PSEUDO (H-PSEUDO-83817b):** For F = {P ∈ E(F_p) : x(P) < t},

    max_{k≠0} |hat{1_F}(k)| ≤ C(p) · √B

where B = |F|, N = |E(F_p)| ≈ p, and C(p) ~ p^{0.079} empirically (5-point fit, BATCH-079).

**The character sum in two equivalent forms:**

*Form A (DL space, j-indexed):*

    hat{1_F}(k) = Σ_{j=0}^{N-1} 1_{x([j]G) < t} · e^{2πi kj/N}

This is the DFT at frequency k of the binary sequence f(j) = 1_{x([j]G) < t}.

*Form B (curve space, P-indexed):*

    hat{1_F}(k) = Σ_{P ∈ E(F_p)} 1_{x(P) < t} · e^{2πi k DL_G(P)/N}
               = Σ_{P ∈ E(F_p)} χ_k(P) · 1_{x(P) < t}

where χ_k(P) = e^{2πi k DL_G(P)/N} is a character of the abstract group Z/N evaluated
at the discrete log of P.

**Fourier decomposition over F_p:**  
Expanding the indicator 1_{x < t} as a Fourier series over F_p:

    1_{x < t} = (t/p) + Σ_{m≠0} â_m e^{2πi mx/p}

where |â_m| ≤ min(t/p, 1/(π|m|)) for m ≠ 0, so Σ_{m≠0} |â_m| = O(log p).

Substituting and using character orthogonality (Σ_{P∈E(F_p)} e^{2πi k DL_G(P)/N} = 0 for k≠0):

    hat{1_F}(k) = Σ_{m≠0} â_m · T_{k,m}

where the mixed exponential sum is:

    T_{k,m} = Σ_{j=0}^{N-1} e^{2πi kj/N} · e^{2πi m x([j]G)/p}
            = Σ_{P ∈ E(F_p)} χ_k(P) · ψ_m(x(P))

with ψ_m(x) = e^{2πimx/p} an additive character of F_p. If T_{k,m} could be bounded by O(√p),
then |hat{1_F}(k)| ≤ O(√p) · Σ_{m≠0} |â_m| = O(√p · log p) = O(√N · log N).

---

## Can the Weil bound be applied?

**What Weil bounds.** The Weil bound (Riemann Hypothesis for curves over F_q) applies to
character sums of the form:

    Σ_{x ∈ F_q} ψ(f(x))   or   Σ_{P ∈ C(F_q)} χ(φ(P))

where ψ is an additive character, χ is a multiplicative character, and **f, φ are algebraic
(rational) functions** defined over F_q on a curve C. The key requirement is that the function
appearing in the exponent is a rational map on the algebraic variety being summed over.

**Why T_{k,m} does not qualify.** T_{k,m} = Σ_{P ∈ E(F_p)} χ_k(P) · ψ_m(x(P)) involves
two factors:

- ψ_m(x(P)) = e^{2πi m x(P)/p}: this IS algebraic in P. The x-coordinate is a rational function
  on the curve E, so ψ_m ∘ x is a legitimate geometric character of E over F_p.
- χ_k(P) = e^{2πi k DL_G(P)/N}: this is a character of the abstract cyclic group Z/N evaluated
  at the group isomorphism DL_G: E(F_p) → Z/N. The function DL_G is NOT a rational map on the
  algebraic variety E. It is the inverse of the multi-valued EC multiplication map [·]: Z/N → E,
  and it has no polynomial or rational expression in the affine coordinates (x, y) of P.

To apply Weil to T_{k,m}, we would need DL_G to be a rational function E(F_p) → F_p. This is
equivalent to asking for an algebraic formula for the discrete logarithm on E — which is
precisely what ECDLP asserts does not exist. The Weil approach requires the very answer
we are trying to bound.

**Direct application via Form A also fails.** In Form A, the sum is over j ∈ Z/N (DL space),
not over a geometric variety. There is no elliptic curve structure on the index space j, and
no Frobenius endomorphism acts on it. The Weil machinery has no foothold.

**Verdict:** The Weil bound cannot be applied directly to hat{1_F}(k) in either Form A or
Form B, and cannot be applied to T_{k,m} without resolving the algebraic nature of DL_G.

---

## The circularity problem (same as DEC-20260804-1b22b2)

The obstruction encountered here is structurally identical to the one identified in the
DDH analysis (DEC-20260804-1b22b2) and is worth naming precisely:

**Weil circularity.** Every attempt to bound hat{1_F}(k) using algebraic geometry requires,
at some point, that the map j → x([j]G) (or its inverse DL_G) be algebraic. But:

1. The EC multiplication map [j]: E → E is algebraic in P (as an algebraic map of varieties),
   but it goes in the wrong direction: it maps Z/N × E → E, not E → Z/N.
2. For fixed P, the map j ↦ [j]P from Z/N to E(F_p) is a bijection of sets but is not a
   rational map from any algebraic variety to E.
3. The inverse of this bijection (DL_G: E(F_p) → Z/N) is not the restriction of any rational
   function on E to the F_p-points, because Z/N has no natural scheme structure compatible
   with the Zariski topology on E.

**Why this is intrinsic, not a proof technique gap.** The non-algebraicity of DL_G is not a
failure of current proof techniques — it is the definition of hardness in ECDLP. Any algebraic
formula DL_G = f/g with f, g ∈ F_p[x, y]/(curve eq) would constitute an algorithm for
ECDLP with runtime O(deg(f) + deg(g)), running in polynomial time on the curve's coordinate
ring. The assumed hardness of ECDLP implies that no such formula exists (over F_p, for generic
curves). The Weil approach therefore runs into ECDLP hardness as a hard obstruction, not a
soft one.

**Contrast with the Weil-applicable case.** For comparison: if F were instead defined as
{j : r(j) < t} for a polynomial r: Z → Z with r([j]G) = j, the Weil bound would apply to
that sum. The difficulty is entirely in the factor-base definition using x-coordinates, which
mixes the algebraic (x-coordinate) and non-algebraic (DL index) structure.

---

## Alternative: Can we use L-function theory instead?

L-function theory provides several other tools. We assess each.

### A. L-function of E/F_p and point-count distribution

The L-function of E over F_p is L(s, E/F_p) = (1 − αp^{−s})^{−1}(1 − βp^{−s})^{−1}
where α, β are the Frobenius eigenvalues with |α| = |β| = √p and α + β = p + 1 − N.

This L-function encodes |E(F_{p^n})| = p^n + 1 − α^n − β^n for varying extensions.
It says nothing about the distribution of DL values of specific structural subsets F ⊂ E(F_p)
for a fixed prime p. The L-function is a statement about the variation of N across extensions,
not about the DL labeling of points within E(F_p).

**Verdict A:** L-function of E/F_p is not applicable to H-PSEUDO.

### B. Hecke characters and CM curves

For CM elliptic curves E over F_p whose endomorphism algebra is an imaginary quadratic field
K = Q(√(−d)), the Frobenius π acts as an element of O_K with |π|^2 = p. Characters of E(F_p)
that factor through the CM structure — Hecke Grössencharacters χ of K — satisfy:

    L(s, χ, E) = Σ_n a_n n^{−s}

which is an entire function with functional equation, and whose coefficients bound certain
character sums over E(F_p) via Hecke's theory.

For a Hecke character χ of conductor f and a rational function φ on E:

    |Σ_{P ∈ E(F_p)} χ(P) · ψ(φ(P))| ≤ (conductor bound) · √p

This would apply to T_{k,m} IF χ_k(P) = e^{2πi k DL_G(P)/N} were a Hecke character.
A Hecke character of O_K evaluated at the Frobenius at P gives a specific complex number
that is algebraically tied to P's position in E(F_p). Whether e^{2πi k DL_G(P)/N} is a
Hecke character depends on the specific curve and generator.

**Obstruction:** For a general prime p and standard NIST/secp-type curves, the group
E(F_p) ≅ Z/N is cyclic of a specific order N determined by the Frobenius. The generator G
is chosen arbitrarily; DL_G relative to a specific G has no canonical tie to the CM structure.
Even for CM curves, the Hecke character lift of e^{2πi k DL_G/N} requires G to align with
the CM action, which is a non-generic condition.

**Verdict B:** For CM curves with CM-aligned generators, Hecke L-function theory might give
|T_{k,m}| = O(√p). For the general case (including standard cryptographic curves), this route
requires non-generic structure not known to hold.

### C. Katz-Sarnak equidistribution

The Katz-Sarnak program (Monodromy, Frobenius eigenvalues) bounds character sums for families
of L-functions as the family varies (e.g., over all elliptic curves over F_p as p varies, or
over all twists of a fixed curve). It produces equidistribution results for the statistical
distribution of Frobenius eigenvalues across the family.

This is orthogonal to H-PSEUDO: we need a bound for a fixed curve and fixed structural set F,
not an average over a family. Katz-Sarnak averaging cannot produce the pointwise bound H-PSEUDO
requires.

**Verdict C:** Katz-Sarnak theory is not applicable to the pointwise bound in H-PSEUDO.

### D. Summary of L-function routes

| Route | Bound on |hat{1_F}(k)| | Applicable? | Notes |
|---|---|---|---|
| L-function of E/F_p | None directly | No | Encodes |E(F_{p^n})|, not DL distribution |
| Hecke chars (CM curves) | O(√p · log p) | Conditional | Requires G aligned with CM action |
| Katz-Sarnak | None pointwise | No | Applies to families, not fixed curves |
| Weil + T_{k,m} decomposition | O(√p · log p) | No | DL circularity blocks T_{k,m} bound |

Even in the best applicable case (Hecke, CM), the resulting bound is O(√p · log p) = O(√N · log N),
which is MUCH weaker than H-PSEUDO's O(√B · p^{0.079}) for small B_frac. This is taken up
in the empirical section below.

---

## Empirical check: does C ~ sqrt(N/B) = 1/sqrt(B_frac)?

If the Weil-type bound |hat{1_F}(k)| = O(√N) were tight, then
C = |hat|/√B = O(√N/√B) = O(√(N/B)) = O(1/√(B_frac)).

This section tests whether this is consistent with the 5-point empirical dataset.

### Raw data (BATCH-079 empirical record)

| p | B_frac | B ≈ | C (empirical) | √(N/B) = 1/√B_frac | C / √(N/B) |
|---|---|---|---|---|---|
| 1009 | 0.05 | 50 | 3.0 | √20 ≈ 4.47 | 0.67 |
| 4001 | 0.05 | 200 | 3.5 | √20 ≈ 4.47 | 0.78 |
| 9001 | 0.01 | 90 | 3.7 | √100 = 10.0 | 0.37 |
| 50021 | 0.005 | 250 | 3.84 | √200 ≈ 14.1 | 0.27 |
| 100003 | 0.003 | 300 | 4.32 | √333 ≈ 18.3 | 0.24 |

**Observation 1: The ratio C / √(N/B) is NOT constant.** It ranges from 0.24 to 0.78 —
a 3× variation. This directly falsifies C ~ √(N/B) as a description of the data.

**Observation 2: The variation is driven by B_frac, not p.** The last three rows have
decreasing B_frac (0.01, 0.005, 0.003), and the ratio falls sharply (0.37, 0.27, 0.24).
By contrast, the first two rows share B_frac = 0.05 and the ratio is 0.67 and 0.78 — closer
but still growing with p.

### Controlled comparison at fixed B_frac = 0.05

At fixed B_frac, √(N/B) = 1/√(B_frac) = √20 ≈ 4.47 is constant. So if C ~ √(N/B), C
should also be constant. We observe:

- p = 1009: C = 3.0
- p = 4001: C = 3.5

C grows from 3.0 to 3.5 (a 17% increase) as p grows by a factor of 4. This growth is:
- Consistent with C ~ p^{0.079}: (4001/1009)^{0.079} = 3.97^{0.079} ≈ 1.11. The 17% vs 11%
  discrepancy is within what could be noise at these small scales.
- Inconsistent with C ~ √(N/B) = constant.

**Conclusion from fixed-B_frac test:** C has a genuine p-dependent growth component beyond
1/√(B_frac). Even at fixed B_frac, C grows slowly with p.

### What the empirical scaling implies for |hat|/√N

Letting |hat| ~ C · √B = p^{0.079} · √(B_frac · p) = p^{0.079} · √B_frac · p^{0.5}:

    |hat| / √N ~ p^{0.079} · √B_frac

At B_frac = 0.05: |hat|/√N ~ p^{0.079} · 0.224. At p = 1009: ≈ 0.224 · 1009^{0.079} ≈ 0.224 · 1.55 ≈ 0.35. (Empirical: 3.0 · √0.05 ≈ 0.67 — the p^{0.079} scaling is not tight at p = 1009.)

The key structural point: |hat|/√N is NOT constant across the dataset. It varies from
about 0.67 to 0.24, meaning that |hat| grows more slowly than √N as p increases (holding B_frac
fixed). The Weil bound |hat| = O(√N) is a valid upper bound but is a 1.3–4× overestimate
at observable scales, and the overestimate worsens as B_frac decreases.

### Quantitative gap: Weil bound vs. empirical

For B_frac = 0.003, p = 100003:
- Weil-type bound: |hat| = O(√N · log N) ≈ √100003 · ln(100003) ≈ 316 · 11.5 ≈ 3635
- Empirical: |hat| ~ C · √B = 4.32 · √300 ≈ 4.32 · 17.3 ≈ 74.7
- Weil overestimates by factor ~49×

The Weil bound is asymptotically correct in sign (|hat| ≤ √N up to log factors), but it
captures the wrong B-dependence: the empirical sum scales as √B (not √N), which makes the
Weil bound increasingly loose as B_frac → 0. The quantity H-PSEUDO bounds — C = |hat|/√B —
is roughly constant (slowly growing), not growing as √(N/B).

---

## Conclusion and verdict

### Q1: Is the Weil bound applicable to the H-PSEUDO sum?

**No.** The Weil bound (and its generalizations via étale cohomology) requires the function
being summed to be algebraic (a rational map on the algebraic variety). The H-PSEUDO character
sum involves the discrete logarithm function DL_G: E(F_p) → Z/N, which is NOT algebraic.
This is intrinsic: any polynomial formula for DL_G would be an efficient ECDLP algorithm.

Via the T_{k,m} Fourier decomposition (proposed in BATCH-080/DEC-20260804-ba880f), the same
obstruction recurs at T_{k,m}: bounding this sum using Weil requires χ_k(P) = e^{2πi k DL_G(P)/N}
to be a rational character of E, which is precisely the Weil circularity.

**The circularity is identical in structure to DEC-20260804-1b22b2** (the DDH categorical
mismatch): in both cases, a tool that bounds "algebraic" or "computational" structure
fails to reach H-PSEUDO because H-PSEUDO is a statement about the distribution of DL
values on a structured set, which requires non-algebraic input.

### Q2: Is the empirical C ~ p^{0.079} consistent with C ~ √(N/B)?

**No.** The empirical data falsifies C ~ √(N/B) = 1/√(B_frac):

1. At varying B_frac: C/√(N/B) ranges from 0.24 to 0.78 (3× variation). Not constant.
2. At fixed B_frac = 0.05: C grows from 3.0 to 3.5 as p grows 4×. C is not constant.
3. The Weil-type bound |hat| = O(√N) is an upper bound but overestimates the empirical
   sum by 1.3× at B_frac = 0.05 and by ~49× at B_frac = 0.003.
4. The empirical sum scales as √B (not √N): C = |hat|/√B is roughly constant (~3–4)
   while C/√(N/B) = |hat|/√N varies sharply with B_frac.

The correct empirical scaling is |hat| ~ C(p) · √B with C(p) ~ p^{0.079} — a slowly
growing factor that goes beyond anything a Weil bound predicts or explains.

### Q3: Is there hope for a Weil-type bound on the H-PSEUDO sum?

**Very limited, and in any case insufficient for the useful form of H-PSEUDO.**

Even under the most favorable interpretation — where a Hecke-character lift exists for
CM curves with CM-aligned generators — the resulting bound is O(√p · log p), which gives:

    C = |hat|/√B ≤ const · √p · log(p) / √B = const · √(N/B) · log(N)

This is a Weil-type bound in the sense of being O(√(N/B)), but it provides NO explanation
for why C should be O(p^{0.079}) (much smaller than √(N/B) at small B_frac) and NO
unconditional proof applicable to non-CM curves.

### Status of the Weil route

The Weil / étale cohomology route is **closed as a path to a useful proof of H-PSEUDO**:

1. It cannot be applied at all without resolving DL circularity (structural obstruction).
2. If it could somehow be applied, the resulting bound (C = O(√(N/B) · log N)) would be
   much weaker than the empirical C ~ p^{0.079} << √(N/B), providing a true but useless
   bound for small B_frac.
3. The empirical data itself shows that |hat| grows as √B · p^{0.079}, not as √N — the
   Weil scaling is the wrong functional form to explain the observed behavior.

### Open route

The empirical scaling C ~ p^{0.079} with |hat| ~ √B · p^{0.079} is unexplained by any
current proof framework. The slowly growing p-exponent 0.079 requires a mechanism that:

- Provides genuine cancellation (not just trivial bounding) in the DL character sum
- Depends on the algebraic structure of the EC multiplication map (not just the group size)
- Gives exponent < 1/2 (sub-Weil) for structured subsets defined by x-coordinate thresholds

Possible routes not yet systematically explored:

- **Spectral methods on E(F_p) viewed as a Cayley graph**: bound hat{1_F}(k) via the
  spectral gap of a random walk on E(F_p), using eigenvalue bounds from Frobenius data.
- **Equidistribution via Weyl differencing**: apply Weyl differencing to the sequence
  x([j]G) viewed as a sequence over F_p, using the algebraic geometry of the EC addition
  map to bound difference character sums.
- **Sub-sum decomposition by residue classes**: decompose the sum by residue class of
  DL(P) mod small primes, and bound each piece separately — may give improved exponents.

These are not developed here; they are forward-looking candidates for BATCH-082 ideation.

---

**Summary for the Coordinator:**

The Weil bound approach is closed. DL circularity is a structural obstruction (not a proof
technique gap), the empirical scaling is C ~ p^{0.079} (not C ~ √(N/B)), and the most
optimistic Weil-type bound would give an asymptotically correct but quantitatively useless
upper bound O(√(N/B) · log N) — a 4–50× overestimate depending on B_frac. H-PSEUDO remains
unproven. The empirical p^{0.079} exponent continues to resist any available algebraic
geometry framework and likely requires a mechanism specific to the EC multiplication map's
distribution of x-coordinates.
