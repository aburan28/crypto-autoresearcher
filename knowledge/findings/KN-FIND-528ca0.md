# KN-FIND-528ca0: Fractional Left O-Ideals of Norm q' in an Indefinite Maximal Quaternion Order Are Infinite — SCOPE CORRECTION: Does NOT Apply to HAWK's Totally Definite Algebra

**ID:** KN-FIND-528ca0
**Type:** finding
**Proof status:** derivation (repaired, BATCH-d44912; scope-corrected DEC-20260805-a62164)
**Claim tier:** toy
**States a finding:** true (mathematical finding — for INDEFINITE quaternion algebras)
**States a security claim:** false
**Added:** 2026-08-05
**Scope corrected:** 2026-08-05 — HAWK uses A = (-1,-1|K), a TOTALLY DEFINITE algebra. This finding applies to indefinite algebras only (DEC-20260805-a62164).
**Source task:** TASK-20260805-a39814

**Prior evidence:** EV-HAWK-af783e
**Goal:** GOAL-HAWK-001

---

## Finding statement

**Theorem (derivation, toy tier).**  Let B be an indefinite quaternion algebra
over Q with maximal order O.  Then:

1. **(Ideal count)** The set of fractional left O-ideals of reduced norm q'
   is **infinite**.

2. **(Case C density)** Let F_R denote the set of fractional left O-ideals of
   norm q' with denominator d(I) ≤ R.  Then |F_R| = Θ(q'·R³).  If the set E of
   "easy" nrd-PIP instances satisfies |E ∩ F_R| = o(R³), then the density
   |E ∩ F_R| / |F_R| → 0 as R → ∞, and the expected number of re-randomization
   trials is super-polynomial in R with no derivable upper bound.

---

## Key algebraic steps

### Step 1: Canonical form for fractional ideals

Every fractional left O-ideal I of norm q' has a unique representation
I = (1/r)·J where:
- r = min{s ∈ ℤ_{>0} : sI ⊆ O} is the denominator d(I),
- J = rI is an integral left O-ideal of norm q'·r².

**Uniqueness (repaired):** Both r₁ and r₂ equal min{s ∈ ℤ₊ : sI ⊆ O}; the
minimum of a nonempty set of positive integers is unique; hence r₁ = r₂ and
J₁ = J₂.  *(Repair 1: the BATCH-56498f derivation used a circular norm
argument r₁²r₂²q' = r₁²r₂²q'; the correct proof is the one-sentence minimality
argument above.)*

### Step 2: Norm surjectivity by Eichler's theorem

For every r ≥ 1 there exists at least one integral left O-ideal of norm q'·r².
This follows from **surjectivity of nrd: O → ℤ_{≥0}** for indefinite maximal
orders over Q, established by **Eichler's theorem** via strong approximation
(Voight, *Quaternion Algebras* (2021), Theorem 17.3 / Section 30.1):

- At every finite prime p: O_p is either M_2(ℤ_p) (split; every non-negative
  integer is represented by [[n,0],[0,1]]) or the unique maximal order in the
  ramified division algebra over Q_p (surjectivity by strong approximation).
- At the real place: B ⊗_Q R ≅ M_2(R) is indefinite, so the norm form
  represents all positive reals.
- Global integral representation follows by strong approximation for spinor genera.

*(Repair 2: the BATCH-56498f derivation cited Hasse-Minkowski, which guarantees
Q-rational isotropy — not Z-integer representations.  The correct theorem is
Eichler's theorem / strong approximation.)*

### Step 3: Divergence

By Step 2, for each r ≥ 1 there exists at least one fractional ideal with exact
denominator r.  By the canonical-form uniqueness (Step 1), distinct denominators
yield distinct fractional ideals.  Therefore the set of fractional left O-ideals
of norm q' contains a copy of ℕ indexed by r, hence is infinite.

### Step 4: Pool size Θ(q'·R³)

Using σ₁(q'r²) ~ q'r²·π²/6 and summing over r = 1, …, R:

    |F_R| = ∑_{r=1}^{R} f(r) ≤ ∑_{r=1}^{R} σ₁(q'r²) ~ q'·(π²/18)·R³

Numerically confirmed for q' = 7, R = 1..10 (all entries in the table verified
exact by the validator, TASK-20260805-36cc26).

### Step 5: Density decay and super-polynomial runtime

If |E ∩ F_R| = o(R³) (plausible when E is bounded by the class number h(O) of
the relevant ideal class set, or grows sub-cubically):

    density(R) = |E ∩ F_R| / |F_R| → 0   as R → ∞

Expected trials T(R) = 1/density(R) → ∞.  For |E ∩ F_R| = O(1) (bounded E):
T(R) = Ω(q'·R³/|E|), which is super-polynomial in R for any fixed |E|.

---

## Scope and limitations

**In scope:**
- Indefinite maximal quaternion order O over Q (B ⊗_Q R ≅ M_2(R)).
- Numerical verification in the split model B = M_2(Q), O = M_2(Z), q' = 7.
- Mathematical statement about ideal cardinality and density under bounded
  sampling.

**Not in scope — explicit non-claims:**
- This is **not** a claim about HAWK cryptographic security in any direction.
- This does **not** establish that the HAWK nrd-PIP algorithm runs in any
  specific time complexity, only that one plausible scenario (Case C) gives a
  super-polynomial lower bound on expected trials.
- This does **not** establish whether Case C applies to the actual algorithm
  (requires iacr:2026/1318 algorithm body, unavailable as of 2026-08-05;
  see KN-OPEN-028).
- The set E of easy instances is not characterized; |E| is a parameter of the
  bound, not a derived quantity.
- No extrapolation to HAWK cryptographic parameters.

**Required controls before reliance:**
1. Verify Eichler's theorem applies to the specific quaternion algebra B = O_F
   used in HAWK (not just M_2(Q)).
2. Verify the notion of "fractional left O-ideal" in iacr:2026/1318 matches the
   definition used here.
3. Verify the "short U" re-randomization constraint implies denominator ≤ R for
   some polynomially bounded R.
4. Verify the GCD-based exact-denominator extraction transfers from M_2(Z) to
   non-split indefinite maximal orders.

---

## Case hierarchy (per red-team RT-OBJ-3/4/5)

| Case | Description                                  | Pool size | Runtime           | Consistency |
|------|----------------------------------------------|-----------|-------------------|-------------|
| B    | Algorithm samples only integral ideals       | q'+1      | Polynomial        | Disfavored (authors' correction) |
| C    | Bounded denominator (d(I) ≤ R)              | O(q'·R³)  | Super-polynomial  | Most consistent with available info |
| A    | Unbounded denominator sampling               | ∞         | Undefined/non-terminating | Requires additional argument |

Case C is the primary supported scenario given: (a) short-U conjugation implies
bounded denominator; (b) authors report "super-polynomial time," not undefined.

---

## Proof gaps repaired in BATCH-d44912

| Gap ID  | Location        | Original error                              | Repair                                               |
|---------|-----------------|---------------------------------------------|------------------------------------------------------|
| RT-OBJ-1 | Claim 2.1 proof | Circular norm argument (tautology r₁²r₂²q' = r₁²r₂²q') | Minimality uniqueness: r₁ = r₂ = min{s: sI ⊆ O}   |
| RT-OBJ-2 | Claim 2.2 proof | Hasse-Minkowski cited for Z-representation   | Eichler's theorem via strong approximation (Voight §30.1) |

The conclusions of both claims were correct; only their proofs were defective.

---

## Prior evidence

- **EV-HAWK-af783e** (BATCH-56498f): original derivation, validator accepted with
  qualifications, red team passed with constraints (identified both proof gaps).
- Corrected derivation: TASK-20260805-a39814/corrected_derivation.md

---

## References

- Voight, J. *Quaternion Algebras* (2021), Theorem 17.3, Section 30.1 (strong
  approximation, norm surjectivity for indefinite maximal orders).
- Voight, J. *Quaternion Algebras* (2021), Theorem 23.3.7 (Eichler–Brandt formula
  for integral ideal counts).
- iacr:2026/1318 (HAWK attack paper body, KN-LIT-7674): body text obtained 2026-08-05.
  Section 6.3 (Babai reduction with ‖β‖ < O(n^{13/2})) confirms Case C applies.
  Section 9 (Heuristic 4 and 30/06 correction) confirms the number-field O_F
  version of the same fractional-ideal infinity principle.
- DEC-20260805-ed4cd3: Case C confirmed from algorithm structure.
- Straznickas–Weis (KN-LIT-7592): best known classical attack on HAWK, cost
  2^{(n/2+1)+o(n)}. No sub-exponential advantage established by GuessingGame.
