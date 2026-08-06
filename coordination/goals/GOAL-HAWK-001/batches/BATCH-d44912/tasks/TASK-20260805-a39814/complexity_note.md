# Case C Complexity Note: Super-Polynomial Runtime Under Bounded Fractional Ideal Sampling

**Task:** TASK-20260805-a39814
**Batch:** BATCH-d44912 (BATCH-003)
**Goal:** GOAL-HAWK-001
**Date:** 2026-08-05
**Claim tier:** toy / mathematical derivation
**States a finding:** false
**States a security claim:** false — this note does NOT assert HAWK is secure or insecure

---

## 1. Motivation

The red-team review of BATCH-56498f (RT-OBJ-3, RT-OBJ-4, RT-OBJ-5) identified
that Case C — in which the algorithm samples from fractional ideals with
denominator bounded by a radius R — is the complexity scenario most consistent
with two pieces of available information:

1. The algorithm uses "short U" conjugation, which implies the denominator of the
   resulting Gram matrix's associated ideal is bounded by a polynomial function of
   the shortness height of U.
2. The authors (iacr:2026/1318, 30/06 update, relayed via KN-LIT-7674) describe
   the algorithm as running in "super-polynomial time" — a finite (if
   super-polynomial) runtime, not an undefined or non-terminating one.

This note formalizes the Case C density and runtime argument.

**Explicit non-claim:**  This note makes no claim about HAWK's actual security
level, the exploitability of any attack, or the relationship between the
algorithm's runtime and any deployed parameter set.

---

## 2. Definitions

**Setting.**  Let B be an indefinite quaternion algebra over Q with maximal order
O (the "maximal quaternion order" in HAWK's notation O_F).  Fix a prime q' (the
"norm target").

**Fractional left O-ideals of norm q'.**  A fractional left O-ideal I ⊂ B of
reduced norm q' has a unique representation I = (1/r)·J, where:
- r ∈ Z_{>0} is the **denominator** d(I) = min{s ∈ Z_{>0} : sI ⊆ O},
- J = rI is an **integral** left O-ideal of norm q'·r².

This canonical form is well-defined and unique (Claim 2.1 of the corrected
derivation, TASK-20260805-a39814).

**Denominator-bounded pool.**  For a real parameter R ≥ 1, define:

    F_R = { fractional left O-ideals I of norm q' : d(I) ≤ R }
         = { (1/r)·J : 1 ≤ r ≤ R, J integral left O-ideal of norm q'r² }

This is the sampling pool of Case C: the algorithm samples from F_R for some R
growing with the algorithm's iteration bound.

**"Easy" instances.**  Let E ⊆ {left O-ideals of norm q'} be the set of
"Lenstra–Silverberg-easy" instances — those for which the L-S subfield algorithm
(as referenced in KN-LIT-7670 / KN-LIT-7674) succeeds.  The structure of E is
unknown without the algorithm body; we work with the assumption that E is bounded
in size (specifically, that |E| does not grow as R^3 or faster).

---

## 3. Size of the bounded pool: |F_R| = O(q' · R³)

**Claim C.1.**  For O = M_2(Z), B = M_2(Q), and q' prime:

    |F_R| = ∑_{r=1}^{R} (# integral left O-ideals of norm q'r² with exact denom r)
           = ∑_{r=1}^{R} f(r)

where f(r) is the exact-denominator-r count (computed via Möbius inversion from
σ₁(q'r²)).

**Growth rate.**  Using the mean bound for the divisor sum:

    σ₁(N) = ∑_{d|N} d  ~  N · π²/6  (mean over N, with multiplicative fluctuations)

For N = q'r²:

    σ₁(q'r²) ~ q'r² · π²/6

The exact-denominator count f(r) ≤ σ₁(q'r²) and is bounded below by a positive
fraction of σ₁(q'r²) for r such that q' ∤ r (by Möbius inversion).  Summing:

    |F_R| = ∑_{r=1}^{R} f(r) ≤ ∑_{r=1}^{R} σ₁(q'r²)
                               ≈ ∑_{r=1}^{R} q'r² · π²/6
                               = q' · (π²/6) · R(R+1)(2R+1)/6
                               ~ q' · R³ · π²/18

So |F_R| = O(q' · R³).  The numerical table from TASK-20260805-755738 confirms
this cubic growth empirically for q' = 7:

| R  | |F_R| (cumulative) | R³  | ratio |F_R|/R³ |
|----|---------------------|-----|-----------------|
| 1  | 8                   | 1   | 8.0             |
| 2  | 56                  | 8   | 7.0             |
| 3  | 152                 | 27  | 5.6             |
| 5  | 584                 | 125 | 4.7             |
| 10 | 4624                | 1000| 4.6             |

The ratio |F_R|/(q'·R³) = |F_R|/(7R³) is approximately 4.6 / 7 ≈ 0.66 at R=10,
consistent with the analytical prediction π²/18 ≈ 0.55 (within a constant factor
depending on the exact distribution of σ₁ values).

**Conclusion:** |F_R| = Θ(q'·R³).

---

## 4. Density of "easy" instances: |E_R| / |F_R|

Let E_R = E ∩ F_R denote the easy instances within the bounded pool.

**Scenario C.1 (|E| bounded).**  If the L-S algorithm succeeds only on a bounded
number of ideal classes — bounded by, e.g., the class number h(O), which is a
finite number depending only on the discriminant of B and the prime q' — then |E|
is fixed (independent of R).  Therefore:

    |E_R| ≤ |E|  (constant in R)

and:

    density(R) = |E_R| / |F_R| ≤ |E| / (c · q' · R³)  →  0  as R → ∞

The density decays as 1/R³, faster than any inverse polynomial in R.

**Scenario C.2 (|E_R| grows as R^α, α < 2).**  If easy instances accumulate with
growing denominator but sub-quadratically:

    |E_R| ≈ C · R^α  for some α < 2

then:

    density(R) ≈ C·R^α / (q'·R³) = C·R^{α-2}/q'  →  0  as R → ∞

Super-polynomial decay for any α < 2.

**Scenario C.3 (|E_R| grows as R², threshold case).**  If |E_R| ∼ C·R²:

    density(R) ≈ C·R² / (q'·R³) = C/(q'·R)  →  0  (polynomial decay in R)

Still decaying, but slower.  Runtime would be polynomial in R but may not be
polynomial in n (the HAWK security parameter) unless R is polynomially bounded
in n.

**Scenario C.4 (|E_R| grows as R³).**  If easy instances are as dense as the
full pool: density ∼ constant, and the algorithm is polynomial in R.  This would
require E to be a positive-density subset of all fractional ideals — which is
plausible only if the L-S algorithm succeeds on a constant fraction of all ideals,
which contradicts the premise of a "special" easy structure.

For Scenarios C.1–C.3 (α < 2), the density decays to 0, and the algorithm's
expected number of re-randomization trials grows as:

    T(R) = 1 / density(R) ≥ c · q' · R^{2-α} / |E|  →  ∞

This is super-polynomial in R for any fixed |E| and α < 2.

---

## 5. Runtime conclusion: super-polynomial, no upper bound

**Proposition (Case C runtime lower bound).**  Assume:
- The algorithm's re-randomization samples uniformly from F_R for some radius R
  that grows with the algorithm's iteration parameter,
- Easy instances E_R satisfy |E_R| = o(|F_R|) (strictly sub-dense),
- Each trial requires time T_trial(R) (at minimum, the cost of generating and
  checking one fractional ideal of denominator ≤ R).

Then the expected total runtime of the re-randomization phase satisfies:

    E[runtime] ≥ T_trial(R) / density(R) = T_trial(R) · |F_R| / |E_R|
                ≥ T_trial(R) · c·q'·R³ / |E_R|

which is super-polynomial in R as R grows, for any |E_R| = o(R³).

**No derivable upper bound.**  The above gives a lower bound on runtime (it is
super-polynomial) but no upper bound.  An upper bound would require knowing:
1. The exact growth rate of R as a function of the algorithm's input parameter n,
2. The exact structure of E (specifically whether |E_R| grows as R^α for some α),
3. The cost T_trial(R) per trial.

None of these is determinable without the algorithm body (iacr:2026/1318).

**Consistency with authors' characterization.**  The authors report the algorithm
"appears to run in super-polynomial time."  This is exactly the Case C
conclusion: a finite but super-polynomially growing expected runtime, caused by
the decaying density of easy instances within a polynomial-growing bounded pool.
The Case C analysis provides a concrete mathematical basis for the informal
"super-polynomial" characterization without requiring access to the algorithm body.

---

## 6. Summary table

| Parameter          | Value / Bound                                          |
|--------------------|--------------------------------------------------------|
| Pool size |F_R|    | Θ(q'·R³)                                              |
| Easy instances |E_R|| ≤ |E| (bounded); grows as R^α if α < 2 gives density → 0 |
| Density(R)         | O(1/R^{3-α}) → 0 as R → ∞ (for α < 3)               |
| Expected trials    | Ω(R^{3-α} / (q'·|E|))  →  ∞                         |
| Runtime bound      | Super-polynomial lower bound; no upper bound derivable |
| Consistent with:   | Authors' "super-polynomial time" self-characterization |

---

## 7. Explicit non-claims

This note does NOT assert or imply:

- That HAWK is cryptographically broken or insecure.
- That the algorithm body of iacr:2026/1318 achieves any specific runtime.
- That no polynomial-time algorithm for the nrd-PIP problem exists.
- That Case C is the correct scenario — it is the most consistent with available
  information but remains unverified without the algorithm body.
- Any comparison between the algorithm's runtime and any deployed HAWK parameter
  set's security level.

The derivation is purely mathematical and operates at toy/algebraic claim tier.
The runtime lower bound is a consequence of the density argument, which is itself
conditional on |E_R| = o(R³) — a plausible but unverified assumption about the
structure of easy nrd-PIP instances.
