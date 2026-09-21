# Red Team Falsification Review

**Review task:** TASK-20260805-80676e  
**Producer task:** TASK-20260805-755738  
**Batch:** BATCH-56498f  
**Goal:** GOAL-HAWK-001  
**Date:** 2026-08-05  
**Reviewer role:** Red Team (independent session)  
**Model:** amazon-bedrock/us.anthropic.claude-sonnet-4-6  

---

## Scope declaration

This review attacks the mathematical derivation in
`TASK-20260805-755738/derivation.md` across the five objection axes specified in
the handoff.  It does NOT assess HAWK's security in either direction, does NOT
change any hypothesis or experiment status, and does NOT extrapolate to
cryptographic parameter sizes.  The claim tier of the artifact under review is
**toy**; all objections are at that tier.

---

## Summary verdict

**pass_with_constraints.**  The derivation's central mathematical conclusion —
that the set of fractional left O-ideals of fixed reduced norm q' in an
indefinite maximal quaternion order over Q is infinite — is correct.  The
derivation is epistemically honest: it declares a toy claim tier, states no
finding, explicitly identifies three cases, and acknowledges that case selection
requires the algorithm body.  However, two of its formal proofs contain
substantive gaps (one circular argument, one theorem misapplication), and the
three-case analysis systematically understates the algorithm-design evidence that
makes Case B or bounded-C the more likely scenarios for the specific
re-randomization step described in available sources.  These gaps do not
invalidate the infinite-ideal-count conclusion; they do prevent the derivation
from being used as a basis for any complexity classification more specific than
"unknown, three cases consistent with available information."

---

## OBJ-1: Canonical form uniqueness proof is circular

**Status: blocking proof gap (claim correct, proof invalid as written)**

**Claim 2.1** asserts that the representation I = (1/r)·J is unique, where r is
the exact denominator of I.  The derivation proves this using a norm argument.
Attack:

Starting from (1/r₁)J₁ = (1/r₂)J₂, multiply both sides by r₁r₂ to obtain
r₂J₁ = r₁J₂.  ✓  
Taking norms: r₂²·nrd(J₁) = r₁²·nrd(J₂).  ✓  
The derivation then says nrd(J₂) = q'·r₂² and concludes nrd(J₁) = r₁²·q'.

But nrd(J₁) = r₁²·q' is already known *by construction* (J₁ = r₁·I with
nrd(I) = q' ⟹ nrd(J₁) = r₁²·nrd(I) = r₁²q').  The norm computation therefore
produces:

    r₂² · (r₁²q') = r₁² · (r₂²q')  →  r₁²r₂²q' = r₁²r₂²q'

which is a tautology.  The claim "similarly nrd(J₁) = r₂²·q' from the other
side" is unsupported: applying the same reasoning from the J₂ side gives
nrd(J₂) = r₂²q', also what was already known.  **The derivation never produces
the equation nrd(J₁) = r₁²q' AND nrd(J₁) = r₂²q' from independent sources; it
derives each equation from the same substitution.**  The conclusion r₁ = r₂ does
NOT follow from the norm argument as written.

**Correct proof (not in the derivation):** r₁ and r₂ are both defined as "the
smallest positive integer s with sI ⊆ O."  The minimum of a set has a unique
value; therefore r₁ = r₂, and then J₁ = r₁I = r₂I = J₂.  This proof is
trivially valid and requires no norm computation.

**Impact:** The claim is true; the proof is wrong.  The derivation should not be
cited as a formal proof of Claim 2.1 uniqueness until the proof is replaced.
The infinite-ideal-count conclusion (Claim 3.1) is not affected because it rests
on Claims 2.2 and 2.3, not on the uniqueness branch of 2.1 (distinct denominators
give distinct ideals, and this follows from the correct uniqueness argument, not
the broken one).

---

## OBJ-2: Norm surjectivity cites the wrong theorem

**Status: blocking proof gap for Claim 2.2 (conclusion likely correct, cited
theorem does not apply)**

**Claim 2.2** asserts that for each r ≥ 1 there exists an integral left O-ideal
of norm q'r².  The derivation justifies this via:

> "The Hasse-Minkowski theorem guarantees a Z-point on the quadric {nrd = n}
> for every n ≥ 1 (the indefinite condition ensures isotropy at the real place)."

**Attack:** Hasse-Minkowski is a theorem about **rational representations** of
quadratic forms.  Its statement is: a quadratic form over Q is isotropic over Q
iff it is isotropic over R and over Q_p for every prime p.  This guarantees
**Q-rational points** (or rational representations of n), not **Z-integer
points** (integral representations of n).  Transitioning from a Q-rational
solution to a Z-integer solution requires an additional argument — in general,
a quadratic form can represent a rational number without representing that number
as an integer (e.g., x² + y² represents 2/5 over Q but not over Z for x,y ∈ Z).

The correct theorem is **Eichler's theorem on integral representation by
indefinite quaternary forms**, sometimes stated as: for an indefinite maximal
quaternion order O over Z, the reduced norm map nrd: O → Z_{≥0} is surjective.
This follows from strong approximation (the spinor genus is a single genus for
indefinite forms in four or more variables), and is stated and proved in Voight
"Quaternion Algebras" (2021), Theorem 30.1.1 and surrounding material on spinor
genera.  For the split case B = M_2(Q), O = M_2(Z), it is trivial (set the
diagonal matrix [[n,0],[0,1]]).

**Impact:** The cited justification does not prove what it claims.  The conclusion
(nrd is surjective) is almost certainly correct and well-known, but the derivation
as written contains an incorrect proof.  The numerical verification (r=1,2,3
checked exhaustively) provides empirical confirmation for small cases but does not
constitute a proof for all r.  Claim 2.2 should be re-justified using Eichler's
theorem; the numerical check is then supporting illustration, not the primary
argument.

---

## OBJ-3: "Infinite pool → density 0" conflates Case A with the general conclusion,
and misidentifies the effective pool size for the specific algorithm

**Status: substantive constraint on the complexity conclusion**

The derivation correctly identifies three cases (A, B, C) and says "which case
applies requires the algorithm body."  However, the summary classification
labels the regime "undefined-degenerate" (Case A framing) as the primary result,
with Case B and C as alternatives.  This priority assignment is not supported by
the available evidence.

**Attack — short-U mechanism points away from unbounded denominators:**

The algorithm description available in KN-LIT-7670 and KN-LIT-7674 specifies
that re-randomization uses conjugation by a **short** lower-triangular unimodular
matrix U (short meaning small entries, to keep G' computationally tractable and
near the original lattice).  If U has entries bounded by some height B (which
must be bounded for the algorithm to be practical), then the conjugated Gram
matrix G' = U·G·U^T has a natural associated ideal with denominator bounded by a
polynomial in B.  This is Case B (B = 1, integral ideals only) or bounded-R Case
C (R polynomial in B), NOT Case A (unbounded denominators).

The derivation does not engage with this algorithmic constraint.  The claim that
the effective pool is infinite rests on Case A, which requires sampling from
ideals with denominators growing without bound — inconsistent with any
finite-height-shortness constraint on U.  If U is "short" in the algorithm's
sense, the effective pool is finite, and the density question collapses back to
the structure of easy instances within that finite pool.

**Attack — the Case C growth rate O(q'R³) conflates easy-instance growth:**

The derivation computes the pool size as O(q'R³) for Case C using
σ₁(q'r²) ≈ q'r²π²/6.  But the density of **easy** instances within this pool
is unknown.  If the Lenstra-Silverberg algorithm applies to instances with a
subfield structure that becomes more common (or less common) as the denominator r
grows, the easy-to-total ratio could be constant, growing, or decaying,
independently of the R³ total growth.  The "density → 0 as R grows" conclusion
in Case C requires that the number of easy instances grows strictly slower than
R³, which is not derived — it is assumed.

**Narrowing the supported claim:** Under Case C with bounded R (the scenario most
consistent with the "short U" constraint), the effective pool is polynomial in n,
and the question of termination is entirely determined by the easy-instance
density within that pool.  The derivation does not have this information, which
is the correct epistemic position — but the "undefined-degenerate" label should
not be exported as the complexity classification.

---

## OBJ-4: "Of which there are many" — the mathematical fact is infinite, but the
paper's phrase does not determine which effective pool the algorithm uses

**Status: moderate interpretive constraint**

The derivation interprets the paper's phrase "fractional ideals, of which there
are many" as "infinitely many (the full infinite set of fractional left O-ideals
of norm q')."  This interpretation is mathematically correct for the full set
(Claim 3.1 is valid with a repaired proof).  However, the paper's phrase is
compatible with:

(a) **Infinitely many** — the derivation's conclusion, supported by the algebra.  
(b) **A finite but large correction factor** — if the algorithm's re-randomization
     step naturally produces a set of fractional ideals that is polynomial in q'
     (e.g., those with denominator bounded by q'^{1/k} for some k), the phrase
     "many" correctly describes this polynomial-factor correction without invoking
     the infinite full set.

The paper's actual retraction reads: "the main algorithm appears to run in
super-polynomial time" (verbatim from KN-LIT-7674).  The authors' conclusion is
"super-polynomial time" — not "undefined" or "non-terminating in expectation."
Super-polynomial but potentially sub-exponential is a meaningful regime; "non-
terminating" (Case A) is a different and stronger claim.  The authors' language
is consistent with Case C (density decaying as a polynomial in a growing
parameter) more than with Case A (density = 0, no natural probability).

**Attack on interpretation:** The derivation's primary complexity label
("undefined-degenerate") is stronger than the authors' own label ("super-
polynomial time").  The derivation should either adopt the authors' label or
explicitly argue why the authors' label understates the situation — neither is
done in the current artifact.

---

## OBJ-5: Without the paper body, the "undefined/degenerate" primary label is
not the uniquely supported conclusion

**Status: substantive framing concern**

The derivation explicitly says "all four cases are algebraically consistent with
the available abstract-level description."  Given this, labelling the complexity
class as "undefined-degenerate" as the primary classification in the summary and
results.yaml (under `classification.label`) is an unjustified asymmetric choice.

Cases B, C, and A are listed as "alternatives" to the primary "undefined-
degenerate" label — but Case B (integral ideals only, polynomial density, original
polynomial claim restored) is equally consistent with the available information.
The paper's retraction merely says Heuristic 4 is wrong and the algorithm appears
super-polynomial; it does not say the algorithm samples from an infinite pool with
no natural finite approximation.

**Attack — the three-case framing should be symmetric:**

The honest representation of the state of knowledge is:
- Under Case B: polynomial (but this case is disfavored by the authors' own
  correction, since they report super-polynomial, not polynomial).
- Under Case A: undefined/non-terminating.
- Under Case C: super-polynomial with unknown upper bound (consistent with
  authors' characterization).

Of these, Case C is the most consistent with the authors' own statement
("appears to run in super-polynomial time"), and it should be the primary label,
not an alternative.  Case A should be noted as possible but less supported by
the algorithmic description.

**Impact:** The results.yaml `classification.label: "undefined-degenerate"` is
an overclaim relative to the available evidence.  The correct primary label is
"super-polynomial (consistent with authors' characterization, sub-exponential
upper bound unknown)."  "Undefined-degenerate" is the Case A scenario and should
be labelled as such.

---

## Proof-architecture attacks applied

Per `agents/red-team.md` Section "Proof-architecture attacks":

**Observation-fiber attack (OBJ-1):** Held the hypothetical identity
(1/r₁)J₁ = (1/r₂)J₂ fixed and traced the norm computation.  Found it collapses
to a tautology.  Named the missing separator: the correct proof needs to use the
definition of "exact denominator" as a minimum, not norm computation.

**Quantifier-order attack (OBJ-2):** The derivation says "Hasse-Minkowski
guarantees a Z-point."  Hasse-Minkowski quantifies over Q, not Z.  This is a
quantifier-domain error: the theorem's conclusion is in the wrong set.

**Method-ceiling attack (OBJ-5):** The method of the derivation (algebraic
counting + three-case analysis) cannot produce a definitive complexity
classification without the algorithm body.  The ceiling of the method is
"unknown, three cases consistent" — and the derivation reaches that ceiling
correctly in the body, but then overclaims in the summary.

**Nearby-object attack (OBJ-3):** The nearby object is the case where U is
short.  Applying the same "infinite pool" reasoning to a short-U conjugation
produces a finite pool (Case C with bounded R), not an infinite one.  The
derivation does not distinguish the nearby object.

---

## Controlled numerical check

**Verification of table row r=2, q'=7 (M_2(Z) model):**

- Integral left M_2(Z)-ideals of norm 28: σ₁(28) = 1+2+4+7+14+28 = 56. ✓
- Those with gcd = 2 (i.e., 2·J' where J' has norm 7): σ₁(7) = 1+7 = 8. ✓
- Exact-denominator-2 count: 56 - 8 = 48. ✓

The table arithmetic is internally correct for the M_2(Z) split model.

**Observation:** The "exact-denom-r count" computation implicitly uses a
"primitive ideal" definition where the denominator divisibility condition is
gcd(r, gcd_of_all_entries(J)) = 1.  This definition is natural for M_2(Z) but
may not generalize directly to non-split indefinite quaternion orders, where the
GCD of elements is not as straightforwardly defined.  The derivation acknowledges
the caveat that verification uses the split model; the infinite-count conclusion
in other models rests on the algebraic argument (repaired), not the numerical
table.

---

## What survives attack

1. **The set of fractional left O-ideals of fixed reduced norm q' in an
   indefinite maximal quaternion order over Q is infinite.** Proof: (a) Eichler's
   theorem (not Hasse-Minkowski) implies nrd is surjective onto Z_{≥0}, so
   integral ideals of norm q'r² exist for each r ≥ 1.  (b) For each such r, the
   fractional ideal (1/r)·J has denominator dividing r; choosing a J not
   divisible by any proper factor of r gives exact denominator r.  (c) The
   minimality argument (not the norm argument) gives uniqueness, so distinct r
   values give distinct fractional ideals.  Conclusion: infinite.

2. **Three complexity scenarios are all consistent with the available description
   of the algorithm.** The case classification (A/B/C) is correct.

3. **The density of easy instances in the full infinite pool (Case A) is 0 in any
   natural limiting sense.** Correct and follows from the infinite-count result.

4. **Case C with slowly-growing easy-instance count yields super-polynomial
   expected runtime.** Correct conditional on the case.

5. **The paper's "super-polynomial" characterization is most consistent with
   Case C** (bounded height, decaying density), not Case A (ill-posed density)
   or Case B (polynomial density unchanged).

---

## Narrowest supported statement

> *The set of fractional left O-ideals of reduced norm q' in an indefinite
> maximal quaternion order O over Q is infinite (Claim 3.1, proved with repaired
> proofs of Claims 2.1 and 2.2).  Under the scenario in which the
> re-randomization step samples from this infinite pool without height bound
> (Case A), the density of any fixed finite set of "easy" instances is 0 and the
> algorithm does not terminate in expectation.  Under bounded-height sampling
> consistent with the "short U" description (Case B or bounded-C), the pool is
> finite, the density question is determined by easy-instance structure within
> that pool, and no complexity conclusion can be drawn without the algorithm body.
> The authors' own characterization ("super-polynomial time") is most consistent
> with Case C.  No statement about HAWK security follows from this derivation.*

---

## Required follow-up actions (for Coordinator, not for Red Team)

1. **Repair Claim 2.1 proof:** Replace the circular norm argument with the
   minimality argument.  One sentence.

2. **Repair Claim 2.2 citation:** Replace "Hasse-Minkowski guarantees a Z-point"
   with "Eichler's theorem (Voight §30.1) gives surjectivity of nrd onto Z_{≥0}
   for indefinite maximal orders."

3. **Revise primary complexity label in results.yaml:** Change
   `classification.label` from "undefined-degenerate" to something like
   "super-polynomial (Case C most consistent with available evidence; Case A
   possible but requires unbounded denominators inconsistent with short-U
   re-randomization)."

4. **Add the short-U effective-pool constraint to Case C analysis:** Note that if
   the U entries are bounded by height B, the denominator R ≤ B^k for some k,
   giving a finite pool polynomial in B.  Whether this is sub-exponential in n
   requires knowing B as a function of n.

5. **Obtain iacr:2026/1318 body text** before any further complexity analysis.
   Without it, all three cases remain open and the above corrections are the
   maximum achievable.

---

*This review was produced by an independent Red Team session.  It does not
constitute a finding about HAWK security in either direction.  The Coordinator
owns all status decisions.*
