# Corrected Derivation: Fractional Left O-Ideals of Norm q' in an Indefinite Maximal Quaternion Order

**Task:** TASK-20260805-a39814
**Batch:** BATCH-d44912 (BATCH-003)
**Supersedes derivation from:** TASK-20260805-755738 (BATCH-56498f)
**Goal:** GOAL-HAWK-001
**Date:** 2026-08-05
**Claim tier:** toy
**States a finding:** false
**Model:** amazon-bedrock/us.anthropic.claude-sonnet-4-6

**Repairs applied:**
- Repair 1: Claim 2.1 uniqueness proof — replaced circular norm argument with correct minimality argument (per RT-OBJ-1)
- Repair 2: Claim 2.2 theorem citation — replaced Hasse-Minkowski with Eichler's theorem / strong approximation (per RT-OBJ-2)

---

## Scope and obligations

This derivation computes a mathematical quantity (the cardinality of the set of
fractional left O-ideals of fixed reduced norm q' in a maximal quaternion order
O over Q) using standard algebra and numerical verification on M_2(Z) as a
concrete model.  It does NOT assess HAWK's security in either direction, does
NOT state that any attack succeeds or fails, and does NOT extrapolate to
cryptographic parameter sizes.  All claims are at toy/algebraic level.

Uncertainty is stated explicitly wherever it arises.

---

## Setting

Let B be a quaternion algebra over Q that is **indefinite** (i.e., B ⊗_Q R ≅
M_2(R)).  The HAWK attack (iacr:2026/1318, KN-LIT-7670 / KN-LIT-7674) uses a
maximal order O_F inside such a B.

A **left O-ideal** I is a full Z-rank-4 sublattice of B with O·I ⊆ I.  It is
**integral** if I ⊆ O, and **fractional** otherwise (I ⊈ O in general).  The
**reduced norm** of I is

    nrd(I) = ( Z-span of {nrd(x) : x ∈ I} ) ∩ Q

which equals a positive rational number; we write nrd(I) = q' when that number
is q'.

---

## Step 1 — Integral left O-ideals of norm q' (standard result)

**Theorem (Eichler).** For a maximal order O in an indefinite quaternion algebra
B over Q and a prime q', the number of **integral** left O-ideals of reduced
norm q' is:

    #{ integral left O-ideals I : nrd(I) = q' } =
        q' + 1   if q' is unramified in B,
        1        if q' ramifies in B.

For large q', almost all primes are unramified, so the count is q' + 1.

*Source:* This is the classical Eichler–Brandt formula; see e.g. Voight,
"Quaternion Algebras" (2021), Theorem 23.3.7 and surrounding material.

**Concrete model.**  Taking B = M_2(Q) (the split quaternion algebra, indefinite
everywhere) and O = M_2(Z):

- nrd(α) = det(α) for α ∈ M_2(Q).
- Integral left O-ideals of norm q' correspond to Hermite Normal Form matrices
  [[a, b], [0, d]] with ad = q', a,d ∈ Z_{>0}, 0 ≤ b < d.
- For q' prime unramified: the only factorizations are (a,d) ∈ {(1,q'), (q',1)},
  giving exactly q' + 1 matrices (b ranges 0..(q'-1) for the (1,q') case, plus
  one for (q',1)).  ✓

---

## Step 2 — Fractional left O-ideals of norm q': canonical decomposition

**Claim 2.1 (Canonical form).** Every fractional left O-ideal I of norm q' has a
unique representation I = (1/r)·J where:
- r is the smallest positive integer with rI ⊆ O   (the *denominator* d(I)),
- J = rI is an integral left O-ideal of norm q'·r².

**[REPAIR 1 — Claim 2.1 uniqueness proof: corrected from BATCH-56498f]**

*Proof of uniqueness.*  Both r₁ and r₂ equal min{s ∈ ℤ₊ : sI ⊆ O}; the minimum
of a set is unique; hence r₁ = r₂, and then J₁ = r₁I = r₂I = J₂.  □

*Note on the repair.*  The BATCH-56498f derivation attempted to prove r₁ = r₂ by
a norm computation from (1/r₁)J₁ = (1/r₂)J₂, obtaining r₁²r₂²q' = r₁²r₂²q',
which is a tautology (the second equation for nrd(J₁) repeats the first with
variables swapped without adding new information).  The correct argument simply
appeals to uniqueness of the minimum: r is defined as min{s ∈ ℤ₊ : sI ⊆ O},
which is a specific value of a nonempty set of positive integers and is therefore
uniquely determined by I.  Two representations (1/r₁)J₁ = I = (1/r₂)J₂ must
have r₁ = r₂ = min{...}, and then J₁ = J₂ follows immediately.

**Claim 2.2.** For every r ≥ 1, there exists at least one integral left O-ideal of
norm q'·r².

**[REPAIR 2 — Claim 2.2 theorem citation: corrected from BATCH-56498f]**

*Justification.*  For O an indefinite maximal order over Q, the reduced norm map
nrd: O → ℤ is surjective onto ℤ_{≥0}.  The correct theorem establishing this is
**Eichler's theorem** (via the strong approximation theorem for quaternion
algebras): for an indefinite quaternion algebra B over Q with maximal order O,
the spinor norm map — and consequently the reduced norm map nrd: O → ℤ_{≥0} — is
surjective.  This follows from strong approximation applied to the algebraic group
of norm-1 elements together with the local surjectivity at each prime.

*Reference:* Voight, *Quaternion Algebras* (2021), Section 30.1 (strong
approximation for quaternion algebras over global fields) and Theorem 17.3 (norm
representation by indefinite maximal orders).  See also the local verification:
at every finite prime p, the local order O_p is either M_2(ℤ_p) (split case,
where det: M_2(ℤ_p) → ℤ_p is surjective by [[n,0],[0,1]]) or the unique maximal
order in the ramified division algebra over ℚ_p (where every non-negative integer
is represented by strong approximation).  At the real place, B ⊗_Q R ≅ M_2(R)
is indefinite, so the norm form is indefinite over R and represents all positive
reals.  The Hasse-Minkowski theorem is **not** the relevant tool here: it
guarantees Q-rational isotropy (existence of a Q-point on the norm-zero quadric),
not Z-integral representations of positive integers.

*Note on the repair.*  The BATCH-56498f derivation cited "Hasse-Minkowski theorem
guarantees a Z-point on {nrd = n}" for every n ≥ 1.  This is incorrect:
Hasse-Minkowski establishes Q-rational isotropy (that a quadratic form represents
0 non-trivially over Q iff it does so over all completions), not Z-integer
representations of a given positive value.  The integral representation of n by
the norm form of O requires either a direct construction (available for M_2(Z))
or Eichler's theorem / strong approximation for the general indefinite case.

*Concrete model check.*  For B = M_2(Q), O = M_2(Z), and q' = 7:
- r=1: norm 7.  HNF count (σ₁(7)) = 8.  ✓
- r=2: norm 28.  HNF count (σ₁(28)) = 56.  ✓
- r=3: norm 63.  HNF count (σ₁(63)) = 104.  ✓
Computed exhaustively; all positive.  (Split-case direct verification: for any
positive integer n, the matrix [[n,0],[0,1]] ∈ M_2(Z) has det = n, confirming
surjectivity without invoking any global principle.)

**Claim 2.3 (Distinct ideals across denominators).** For r₁ ≠ r₂, no fractional
ideal with canonical denominator r₁ equals one with canonical denominator r₂.

*Proof.*  Immediate from the uniqueness in Claim 2.1.  □

---

## Step 3 — Total count of fractional left O-ideals of norm q'

By Claims 2.1–2.3, the set of fractional left O-ideals of norm q' is in
injective correspondence with pairs (r, J) where r ≥ 1 and J is an integral
left O-ideal of norm q'·r² with exact denominator r (i.e., gcd(r, J) = 1 in an
appropriate sense).

**Claim 3.1 (Divergence).** The count of fractional left O-ideals of norm q' is
**infinite**.

*Argument.*  By Claim 2.2, for each r ≥ 1 there is at least one integral ideal
of norm q'r².  By Claim 2.3, ideals from distinct denominators are distinct.
Hence there are at least ∑_{r=1}^{∞} 1 = ∞ such fractional ideals.

More precisely, the count with exact denominator r equals the count of integral
left O-ideals of norm q'r² whose denominator divisibility is exactly r; this is
a positive integer for every r (verified numerically below).

**Numerical verification (B = M_2(Q), q' = 7):**

| r  | norm q'r² | σ₁(q'r²) | exact-denom-r count | cumulative |
|----|-----------|-----------|---------------------|------------|
| 1  | 7         | 8         | 8                   | 8          |
| 2  | 28        | 56        | 48                  | 56         |
| 3  | 63        | 104       | 96                  | 152        |
| 4  | 112       | 248       | 192                 | 344        |
| 5  | 175       | 248       | 240                 | 584        |
| 6  | 252       | 728       | 576                 | 1160       |
| 7  | 343       | 400       | 392                 | 1552       |
| 8  | 448       | 1016      | 768                 | 2320       |
| 9  | 567       | 968       | 864                 | 3184       |
| 10 | 700       | 1736      | 1440                | 4624       |

The partial sum grows monotonically and without bound.  Every row has a positive
exact-denominator count, confirming an infinite total.

Note: σ₁(N) is the number of integral left M_2(Z)-ideals of norm N (the divisor
sum ∑_{d|N} d counts HNF matrices [[a,b],[0,d]] with ad=N).  The exact-denominator
count is the subset of those for which gcd(r, gcd(a,b,d)) = 1 (the denominator of
(1/r)·[[a,b],[0,d]] is exactly r, not a proper divisor of r).

**Algebraic principle cited.**  A Dedekind domain (commutative ring of integers)
has FINITELY MANY fractional ideals of any fixed norm because the ideal group is
generated by prime ideals and the factorization is unique and finite.  A maximal
quaternion order O over Z is NOT a Dedekind domain in the commutative sense: it
is a non-commutative order in a 4-dimensional algebra.  The norm function nrd is a
degree-2 map B → Q, and the preimage {α ∈ B : nrd(α) = q'} is a non-compact
real-algebraic variety (isomorphic to a non-degenerate quadric in A^4_Q) with
infinitely many Q-rational points.  The left O*-orbits on this variety give the
set of left O-ideals; since the variety is unbounded and O* ≅ arithmetic group
(e.g., SL_2(Z) or a finite-index subgroup for the split case) is a discrete
infinite group, the orbit count is infinite.

**Contrast with the definite case.**  For B ⊗ R ≅ H (Hamilton quaternions,
definite), the norm form is positive definite, the quadric {nrd = q'} is compact
in R^4, and the intersection with O (a discrete lattice) is FINITE — giving
finitely many integral ideals and finitely many fractional ideals of bounded
"height."  The indefinite case has no such finiteness.

---

## Step 4 — Density of "easy" nrd-PIP instances

The HAWK attack (KN-LIT-7670) works by re-randomizing the nrd-PIP instance until
a "Lenstra–Silverberg-easy" instance is obtained.  Heuristic 4 (now failed) was
that a non-negligible fraction of ideals of norm q' are "easy."

**Corrected density argument (mathematical, claim-tier: toy):**

Let E ⊆ {left O-ideals of norm q'} be the set of "easy" instances.  Assume |E|
is finite and fixed (or grows sub-exponentially in the relevant parameters).

- Under the **original (incorrect) count** of q'+1 integral ideals:
  density = |E| / (q'+1), which can be non-negligible.

- Under the **corrected count** of ∞ fractional ideals:
  the ratio |E| / ∞ is not well-defined as a natural density.  In any
  measure-theoretic sense where the "re-randomization distribution" µ is
  supported on the full infinite pool of fractional ideals:
  µ(E) depends on the specific measure µ, not just |E|.

**Case A (sampling uniform over all ideals):** No uniform measure exists on an
infinite discrete set; the question is ill-posed.  The density is 0 in any
reasonable limiting sense.

**Case B (sampling concentrated on integral ideals):** If the re-randomization
(conjugation by short unimodular U) produces only integral ideals, the pool is
q'+1 as before, and the density argument is unchanged.  In this case the
fractional ideals are not sampled and their infinitude is irrelevant.

**Case C (sampling from a finite "height-bounded" subset of fractional ideals):**
If the re-randomization has a bounded "height" (e.g., denominator r ≤ R for some
bound R growing with the parameter), the pool is approximately ∑_{r=1}^{R}
(count with denom r) ≈ O(q'·R^3) (using the growth from the table above and the
mean bound σ₁(q'r²) ∼ q'r²·π²/6).  If |E| is fixed:
density ≈ |E| / (q'R^3), which is super-polynomially small in R.

*Note on case hierarchy (per RT-OBJ-3, RT-OBJ-4, RT-OBJ-5):* The algorithm's
"short U" re-randomization constraint implies bounded denominator, placing the
algorithm in Case B or bounded-R Case C rather than Case A.  Case C is the
scenario most consistent with (a) the algorithm's bounded-height conjugation
mechanism and (b) the authors' own characterization of the runtime as
"super-polynomial."  Case A (unbounded denominators, density 0, non-terminating)
requires a separate argument that U produces ideals with arbitrarily large
denominators.  Case B (only integral ideals, polynomial density) is disfavored
by the authors' own correction that the algorithm is not polynomial.

**Algebraic uncertainty note.**  The body of iacr:2026/1318 has not been read
(the ePrint PDF is unavailable; see KN-OPEN-028).  The specific re-randomization
mechanism, the definition of "easy," and the precise statement of Heuristic 4 are
not directly accessible.  The cases above cover the natural possibilities; which
case applies to the actual algorithm is not determinable from available sources.

---

## Step 5 — Corrected complexity class (derivation, not a finding)

**The paper's statement:** The 30/06 update says the algorithm "appears to run in
super-polynomial time" (verbatim, per KN-LIT-7670 / KN-LIT-7674 / KN-OPEN-028).

**Derivable mathematical bound:**

1. **Under Case C** (height-bounded fractional ideals, most consistent with
   available information): the re-randomization generates ideals from a pool of
   size O(q'·R^3).  If easy ideals form a fixed finite set E, then the probability
   of landing in E in a single re-randomization step is ≈ |E|/(q'R^3) → 0 as R
   grows.  Expected retries = 1/probability → ∞.  This is **super-polynomial** in
   R (and worse than any polynomial if probability → 0 faster than any inverse
   polynomial).

2. **Sub-exponential bound?**  The sum ∑_{r≥1} (easy count with denom r) is a
   well-defined (possibly finite) quantity if "easy" is structured.  If there are
   C·r^α easy instances with denominator r, the total easy count is:
   ∑_{r=1}^{R} C·r^α ≈ C·R^{α+1}/(α+1).
   Easy density ≈ (C·R^{α+1}) / (q'R^3) = C·R^{α-2}/q'.
   For α < 2: density → 0 (super-polynomial runtime).
   For α = 2: density ∼ constant / q' (polynomial runtime in q', not in the security
   parameter n — still no polynomial in n unless q' is small).
   Whether α ≥ 2 for "Lenstra–Silverberg-easy" instances is unknown without the
   paper body.

3. **Comparison to 2^{n/2} lattice-reduction baseline:** The best known classical
   attack on HAWK (Straznickas–Weis, KN-LIT-7592) runs in time 2^{(n/2+1)+o(n)}.
   An algorithm with expected retries growing faster than any polynomial — and with
   no proven sub-exponential bound — does not manifestly retain a super-polynomial
   advantage over the 2^{n/2} baseline.  Whether a sub-exponential regime exists
   would require a concrete upper bound on the re-randomization cost, which is not
   derivable here without the algorithm body.

4. **Case A (unbounded denominators):**  If the re-randomization is over a truly
   infinite discrete pool with no natural finite approximation, the algorithm's
   complexity is "undefined" in the sense that no finite bound can be given from
   the density argument alone.  This scenario requires positive evidence that U
   produces arbitrarily large denominators.

**Summary of derivable complexity classification:**

| Scenario                                    | Pool size       | Density of easy instances | Runtime bound      |
|---------------------------------------------|-----------------|---------------------------|--------------------|
| Sampling integral ideals only (Case B)      | q' + 1 (finite) | |E|/(q'+1)                | polynomial (original claim, disfavored) |
| Sampling height-bounded (Case C, R grows)   | O(q'R^3)        | → 0 as R grows             | super-polynomial, no upper bound (most consistent) |
| Sampling all fractional ideals (Case A)     | ∞               | 0 (ill-posed)             | undefined / non-terminating (requires unbounded-U argument) |
| Easy ideals grow as r^2 or faster (Case C') | O(q'R^3)        | ≥ const/q'                | ≤ poly(q') per retry, unknown vs. n |

**Primary classification (per red-team repair RT-OBJ-4/5):** Case C —
super-polynomial expected runtime with no upper bound derivable without the
algorithm body.  This is the scenario most consistent with the available
algorithmic information (short-U conjugation implying bounded denominators) and
the authors' own "super-polynomial time" characterization.

**Uncertainty statement:**  The exact scenario cannot be determined without the
algorithm body (iacr:2026/1318 full text).  All four cases are algebraically
consistent with the available abstract-level description.

---

## Summary

**Q1.** Is the set of fractional left O_F-ideals of reduced norm q' finite or
infinite?  **Infinite.**  This follows from:
- Claim 2.2: integral ideals of every norm q'r² exist (norm surjectivity by
  Eichler's theorem / strong approximation for indefinite maximal orders over Q;
  Voight §30.1).
- Claim 2.3: distinct denominators give distinct fractional ideals.
- Numerical verification in M_2(Z) for q' = 7: cumulative count grows without bound.

**Q2.** Corrected complexity class (mathematical derivation only, not a finding
about the attack):  The scenario most consistent with available information is
Case C — bounded-denominator sampling — giving super-polynomial expected runtime
as the sampling radius R grows.  No sub-exponential runtime bound is derivable
from available information.  The regime is consistent with the paper's
characterization "appears to run in super-polynomial time."

**Q3.** Comparison to 2^{n/2} baseline: Retaining any advantage over lattice
reduction would require either (a) the sampling stays on integral ideals (Case B,
restoring the polynomial density, but disfavored by the authors' correction) or
(b) a sub-exponential bound on a height-bounded search, neither of which is
established from available information.  The corrected mathematical quantity —
infinite fractional ideal pool, decaying easy-instance density under bounded
sampling — does not by itself establish a sub-exponential complexity, and therefore
does not by itself establish advantage over brute force.  **This observation does
not constitute a finding about HAWK security.**

---

## Limitations and required caveats

1. **Body not read.**  iacr:2026/1318 full text is unavailable.  The exact
   re-randomization mechanism and Heuristic 4 statement are unknown.
2. **Model is M_2(Q).**  Numerical verification uses the split quaternion algebra;
   for ramified B, counts at specific primes differ, but divergence of the
   fractional ideal count still holds by the norm surjectivity argument.
3. **"Easy" instances undefined here.**  The set E of Lenstra–Silverberg-easy
   instances is not characterized in this derivation; its cardinality and structure
   are unknown.
4. **Toy claim tier.**  No computation at HAWK parameter sizes has been performed.
5. **No extrapolation.**  These observations do not support any statement about
   HAWK's security level, the practical cost of any known attack, or the relative
   security of any parameter set.
6. **Case hierarchy.**  Case C is identified as the most plausible scenario given
   available information; this identification is itself conditional on the
   algorithm using bounded-height conjugation and on the authors' self-reported
   "super-polynomial" characterization.  Determination of the exact case requires
   the algorithm body.
