# Tropical Geometry Analysis for ECDLP-IDEA-103

Task: TASK-20260804-160  
Batch: BATCH-109  
Idea: ECDLP-IDEA-103 (faithful tropical source atlas)  
Date: 2026-08-05

---

## Setup: tropical Semaev polynomial

The Semaev summation polynomial S_m(x_1,...,x_m) ∈ F_p[x_1,...,x_m] is the
polynomial whose zero locus encodes all tuples of x-coordinates of points
P_1,...,P_m ∈ E(F_p) with P_1 + ... + P_m = O.  It is defined recursively:

    S_2(x_1,x_2) = (x_1 - x_2)^2 + ... (degree-2 in each variable)
    S_m(x_1,...,x_m) = Res_{x_m}(S_{m-1}(x_1,...,x_{m-1}),S_2(x_{m-1},x_m))

The **tropical Semaev polynomial** T_m is obtained by lifting to a polynomial
f ∈ Z[x_1,...,x_m] with the same support (Newton polytope vertices) and then
applying the min-plus semiring: replace ordinary addition with min, ordinary
multiplication with +.  This produces a piecewise-linear function
T_m: R^m → R.

The **tropical variety** V^trop(S_m) is the corner locus of T_m — the set of
points w ∈ R^m at which the minimum in T_m(w) is attained by at least two
distinct monomials.  It is a pure polyhedral complex (a balanced fan) of
codimension 1 in R^m.

For the index study, the key object is the restricted system:

    S_m(x_1,...,x_{m-1}, Q_x) = 0

with Q_x the x-coordinate of the target Q.  Fixing Q_x specializes the
last variable and yields a tropical hypersurface in R^{m-1}.

---

## Tropical variety vs Newton polytope

**Theorem (Kapranov, Speyer).** For a polynomial f with Newton polytope
Newt(f), the tropical variety V^trop(f) is dual to the regular subdivision of
Newt(f) induced by the coefficient valuation.  In particular, the combinatorial
type of V^trop(f) is determined entirely by Newt(f) and the valuation of the
coefficients; the face structure of the tropical variety is the normal fan of the
secondary polytope of Newt(f).

**Consequence.** The tropical variety carries the same combinatorial information
as the Newton polytope.  It is a polyhedral re-encoding, not a finer invariant.

**For the Semaev system.**  The BKK bound from BATCH-055/056 is the mixed
volume MV(Newt(S_{m-1}), Newt(linear)^{m-2}) of the Semaev hypersurface
specialized at Q_x together with linear constraints x_i - b_i = 0.  This mixed
volume equals the **tropical degree** of the corresponding tropical polynomial
system: the number of tropical solutions counted with multiplicity is bounded
by the same BKK mixed volume.

The tropical degree is not a new bound.  It IS the BKK mixed volume, re-derived
through polyhedral duality.

---

## Does tropical improve beyond BKK?

**No.** Here is the chain of equalities:

    (tropical solution count) = BKK mixed volume = (BKK bound from BATCH-055/056)

This follows from the Bernstein-Kushnirenko theorem: for a generic system, the
number of isolated solutions in (C*)^m equals the mixed volume, and the
tropical approach recovers this same count as the number of vertices of the
mixed-cell subdivision.

The BATCH-055/056 analysis showed BKK gives a factor-2 improvement over naive
Bézout for the Semaev system (the Newton polytopes of S_m have half the volume
of the Bézout simplex due to the bipartite structure of the support).  Tropical
geometry gives:

    factor-2 over Bézout, identical to BKK — no further improvement.

**Could tropical geometry count F_p-rational solutions more tightly?**  No.
Tropical geometry bounds the number of solutions over the algebraically closed
field (or over C).  Restricting to F_p requires arithmetic input — étale
cohomology bounds, Weil conjectures, or character sum estimates.  The tropical
complex is defined over R and sees no finite-field structure; it cannot
distinguish F_p-rational solutions from non-rational ones without additional
arithmetic geometry on top.

---

## DL circularity: does tropical avoid it?

**Yes, tropical geometry avoids DL circularity.**  Here is the precise statement.

The classical character-sum yield bound requires estimating

    hat{1_F}(k) = sum_{x in F_p} 1_F(x) * chi_k(x)

where chi_k is a multiplicative character of order dividing k.  For the factor
base F = {x ∈ F_p : x is B-smooth in some embedding}, the character sum
hat{1_F}(k) involves the multiplicative structure of F_p indexed by DL values —
creating circular dependence (to know hat{1_F}(k) for all k requires knowing
the DL indices of elements of F).

Tropical geometry operates on:

1. The Newton polytope of S_m — a purely combinatorial object, computed from
   the monomial support, which is target- and key-independent.
2. The piecewise-linear structure of T_m over R — no field arithmetic, no
   Fourier analysis, no DL.
3. The valuations of the coefficients of S_m — these are determined by the
   curve equation and the embedding, not by discrete logarithms.

So a tropical bound on the number of solutions to S_m = 0 is derived without
knowledge of any DL value.  The construction is public and target-independent,
matching the requirement in ECDLP-IDEA-103 §Assumptions.

**However, this avoidance is not an advantage without qualification.**  See the
next section: the non-circularity is purchased at the price of losing exactly
the arithmetic information needed to bound the yield over the factor base.

---

## Can tropical give a yield bound?

**No, not without additional structure that tropical geometry does not supply.**

The yield problem is: how many tuples (x_1,...,x_{m-1}) ∈ F^{m-1} satisfy
S_m(x_1,...,x_{m-1}, Q_x) = 0?  Here F is the factor base — the set of
x-coordinates of factor-base points.

**What tropical geometry provides.** The tropical variety of S_m counts
algebraic solutions over (C*)^{m-1}.  It gives an upper bound on the TOTAL
number of solutions over C.  The bound is the BKK mixed volume (as established
above).

**What a yield bound requires.** A yield bound requires counting solutions that
additionally satisfy x_i ∈ F for all i.  This is an INTERSECTION of the
algebraic solution set with the Cartesian product F^{m-1}.

The factor base F is defined by a smoothness (or height) condition:
    F = {x ∈ F_p : x = x(P) for some P ∈ E(F_p), and P satisfies the
                   chosen smoothness criterion with respect to p}

Smoothness is a multiplicative arithmetic condition.  There is no tropical
polynomial whose zero set equals F inside F_p.  The set F is not an algebraic
variety; it is a number-theoretically defined subset of finite density inside
F_p.

**The tropical variety says nothing about the density of its solutions in
F^{m-1}.**  The fraction of algebraic solutions that happen to land in F^{m-1}
is:

    yield ~ (BKK solutions) * Pr[solution ∈ F^{m-1}]

The factor Pr[solution ∈ F^{m-1}] is a statement about the distribution of the
solutions of S_m = 0 within F_p — exactly a Fourier-analytic / exponential-sum
question.  It is this factor that H-PSEUDO addresses.

**H-PSEUDO requires a bound on hat{1_F}(k) for nonzero k.**  The H-PSEUDO
heuristic (or its proved form) asserts that the solutions of S_m = 0 are
equidistributed enough that

    sum_{x in F_p} 1_F(x) * (number of completions to a solution of S_m)

behaves like a random function, with yield ~ B^{m-1}/p.

This equidistribution statement is a claim about the arithmetic geometry of the
Semaev variety over F_p — specifically about how its points project onto each
coordinate axis.  It requires:

- Weil-type bounds on character sums twisted by S_m
- Or an independent equidistribution argument for S_m's F_p-solutions
- Or an explicit count via étale cohomology

None of these is provided by the polyhedral structure of the Newton polytope or
the piecewise-linear structure of the tropical variety.

**Summary of the tropical yield bound gap.**

| Bound type          | Source                     | Factor base condition | DL-free? |
|---------------------|----------------------------|-----------------------|----------|
| Bézout              | degree product             | no                    | yes      |
| BKK                 | mixed volume / tropical    | no                    | yes      |
| H-PSEUDO yield      | char. sum / equidistrib.   | yes (essential)       | no*      |
| Tropical yield      | **does not exist**         | —                     | —        |

*DL circularity in H-PSEUDO can sometimes be broken via Weil descent or
independence arguments, but those are separate techniques; tropical geometry
does not supply them.

---

## Verdict

**1. Tropical geometry ≈ BKK (not an improvement).**

The tropical variety of S_m is the dual of its Newton polytope.  The tropical
solution count equals the BKK mixed volume.  The BKK mixed volume is a
factor-2 improvement over Bézout for the Semaev system (established in
BATCH-055/056).  Tropical geometry recovers that same constant-factor
improvement and no more.

**2. Tropical geometry avoids DL circularity — but only for the algebraic
solution count, not for the yield.**

The polyhedral structure of S_m is public and key-independent.  A tropical
bound on the total number of solutions is circularity-free.  However, this
bound counts all algebraic solutions, not only those in F^{m-1}.  The
transition from "total algebraic solutions" to "yield over the factor base"
requires arithmetic information (character sums, equidistribution) that
re-introduces the non-algebraic factor base condition — and with it the
non-circularity breaks down or the bound weakens.

**3. H-PSEUDO cannot be reached by tropical geometry alone.**

H-PSEUDO is a statement of the form:

    (yield over F^{m-1}) ~ B^{m-1} / p  (random-like equidistribution)

This is a quantitative assertion about the Fourier transform of the indicator
of a non-algebraic set F.  Tropical geometry is a polyhedral tool operating
over R; it has no mechanism to bound exponential sums or to detect the
arithmetic distribution of rational points of an algebraic variety relative to
a smooth-number filter.

The fundamental structural gap: to go from BKK (constant-factor improvement) to
H-PSEUDO (asymptotic exponent improvement), one must prove that S_m's solutions
are "spread" across F_p in a quantitative sense.  That spreading claim is an
arithmetic geometry result (requiring Deligne-Weil, Bombieri-Weil, or similar);
the Newton polytope / tropical structure is a necessary but not sufficient input.

**4. ECDLP-IDEA-103's additional obstruction: source separation.**

Beyond the yield bound, IDEA-103 requires a tropical atlas that SEPARATES
distinct source tuples (x_1,...,x_{m-1}) ∈ F^{m-1} via their tropical
coordinates.  For a factor base of size B = N^β:

- The number of source tuples to separate is up to |F|^{m-1} = N^{β(m-1)}.
- Two distinct tuples can share the same valuation vector and tropical cell
  whenever their difference is "tropically invisible" (lies in the same open
  cone of V^trop(S_m)).
- Separating N^{β(m-1)} points by tropical cells requires at least N^{β(m-1)}
  distinct cells, and encoding N^{β(m-1)} cells with their sources recovers the
  full B^{m-1} incidence object.

For β(m-1) ≥ 1/2, this is at least as expensive as the factor-base incidence
matrix — the tropical atlas gives no compression.  This is the "likely fatal
obstruction" stated in IDEA-103 §Likely fatal obstruction.

**5. Overall assessment.**

| Criterion                              | Tropical outcome                     |
|----------------------------------------|--------------------------------------|
| Solution-count improvement over BKK   | None (tropical degree = BKK MV)      |
| Solution-count improvement over Bézout| Factor-2 (same as BKK)               |
| DL circularity for algebraic count    | Avoided (polyhedral, key-free)        |
| DL circularity for yield bound        | Not resolved (need char. sums)        |
| Yield bound reaching H-PSEUDO         | Not achievable by tropical alone      |
| Source separation for IDEA-103        | Requires N^{β(m-1)} cells — no gain  |
| Exponent improvement toward below-rho | Not demonstrated                     |

Tropical geometry is a valid re-derivation of the BKK bound for the Semaev
system with the advantage of avoiding DL circularity in the solution-count
step.  It does not provide an exponent improvement, cannot bound the yield over
a non-algebraic factor base without arithmetic supplement, and the faithful
source-atlas mechanism of IDEA-103 remains blocked by the source-separation
cardinality obstruction.  The idea remains correctly classified as
`deferred_theorem_required`.
