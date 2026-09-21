---
id: KN-FIND-fd382f
type: internal_finding
title: "Mordell-Weil rank >= 31 is certifiable for explicit elliptic curves over explicit multiquadratic fields with a witness checkable in exact rational arithmetic: degree 32 by pure Galois algebra, degree 16 with a height regulator, degree 8 out of reach"
tags: [elliptic-curves, mordell-weil-rank, quadratic-twists, multiquadratic-fields, galois-eigenspace, mazur-torsion, height-regulator, descent, certificate, exact-verification, rank-records, toy-scale]
confidence: exact_certificate_verified_by_an_independent_pari_free_verifier_in_one_session
evidence_level: exact_algebraic_certificate_plus_numerical_regulator_for_the_multiplicity_bounds
source_refs: [EXP-ECRANK-e1e30e, RUN-ECRANK-e1e30e-001, RUN-ECRANK-e1e30e-002, RUN-ECRANK-e1e30e-003]
internal_refs: [RQ-ECRANK-27dcc5, H-ECRANK-28dba7, EV-ECRANK-b6c9b6, DEC-20260822-5a5635]
sibling_findings_narrowed: []
sibling_findings_note: "New lane; this entry narrows no prior finding. The technique it relies on is abstracted separately as KN-TECH-eb06ea."
proof_status: certificate
proof_refs:
  - experiments/EXP-ECRANK-e1e30e/certificates/cert_deg32_eigenspace.json
  - experiments/EXP-ECRANK-e1e30e/certificates/cert_deg64_eigenspace.json
  - experiments/EXP-ECRANK-e1e30e/certificates/cert_deg16_multiplicity.json
  - experiments/EXP-ECRANK-e1e30e/certificates/cert_deg32_multiplicity.json
  - experiments/EXP-ECRANK-e1e30e/certificates/cert_deg2_rank31.json
  - experiments/EXP-ECRANK-e1e30e/certificates/cert_deg8_control.json
  - experiments/EXP-ECRANK-e1e30e/source/verify_certificate.py
  - experiments/EXP-ECRANK-e1e30e/source/verify_quadratic_lift.py
  - experiments/EXP-ECRANK-e1e30e/source/verify_record_curve.py
review_refs:
  - experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-002/verify_all.stdout.log
  - experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-003/record_curve_verification.json
added: '2026-08-22'
superseded_by: null
---

# Certified rank >= 31 over small multiquadratic fields

## The distinction that has to come first

"An elliptic curve of rank greater than 30" means two incompatible things.

**Over Q it is an open world-record problem.** The largest rank known for any
explicit curve over Q is **30**, found by Alpöge and Howell in 2026, superseding
Elkies–Klagsbrun's 29 (2024) and Elkies' 28 (2006). Rank >= 31 over Q is open.
Nothing in this finding bears on it.

**Over number fields of growing degree it is classical and constructible.** Rank
is unbounded there, so the mathematical content is not existence but *how small
a field*, *how explicit a witness*, and *how strong a certificate*. That is what
this entry measures.

## Results

All bounds below are lower bounds on rank, each backed by a certificate checked
by a verifier that shares no code with the search and never calls PARI.

| [K:Q] | certified rank | certificate strength | curve (minimal model) |
|---|---|---|---|
| 2 | >= 31 | relative: external 30 + 1 exact | Alpöge–Howell 2026 record curve |
| 8 | >= 20 | control — falls short of 31 | `[0,-1,1,8,-50]` |
| 16 | >= 32 | exact + height regulator | `y^2 = x^3 - 22275x - 232733250` |
| 32 | >= 32 | **exact, no numerics at all** | `[1,-1,1,0,0]`, conductor 53 |
| 32 | >= 52 | exact + height regulator | `y^2 = x^3 - 891x - 1861866` |
| 64 | >= 64 | **exact, no numerics at all** | `[1,0,1,4,21]` |

The two bold rows are the ones with no floating point anywhere in the argument.

The flagship exact statement:

> **E : y² = x³ + 405x + 16038** (minimal model `[1,-1,1,0,0]`, conductor 53)
> has **rank E(K) ≥ 32** over
> **K = Q(√-2, √-3, √-5, √7, √13)**, of degree 32.

At degree 64 the curve `[1,0,1,4,21]` attains **rank ≥ 64**: *every one* of the
64 twist classes carries a point, which is the ceiling of the method at k = 6.

## Why the exact rows are possible

For squarefree d the twist E^(d) injects into E(K) as a χ_d-eigenvector for
Gal(K/Q) ≅ (Z/2)^k. Points attached to **distinct classes d** therefore live in
distinct isotypic components of a Q[G]-module and are Z-independent *by algebra*.
The usual n×n Néron–Tate regulator disappears; what replaces it is the
distinctness of n squarefree integers modulo squares. Non-torsion is certified by
Mazur's theorem — exhibit m·P ≠ O for m = 1..12. See KN-TECH-eb06ea.

The structural ceiling is the same fact: only 2^k characters exist, so rank >= 31
by this argument alone forces [K:Q] >= 32. Below that the method must use several
points per class, and independence *within* a class is a genuine height
computation again — which is exactly why the degree-16 row is marked weaker.

## The negative half, which is the more reusable half

- **Degree 8 is out of reach.** Across the whole 502-curve pool the best k = 3
  configuration reaches 20, not 31. The method's reach ends before degree 8.
- **High rank over Q was not obtainable here.** A Mestre–Nagao prefilter over
  364,756 squarefree twists of five small-conductor curves (|d| ≤ 300000, primes
  to 1500), with `ellrank` on the 400 best-scoring twists of each, produced **no
  twist of rank ≥ 5**. Enumerating 49,692 small-coefficient curves gave 497
  distinct j-invariants of rank ≥ 3 and exactly **2** of rank 4.
- Consequently the degree floor reported here is **a property of the search, not
  a theorem**. The degree-2 row proves the point: given a rank-30 curve as input,
  degree 2 is immediate. The ladder is limited by base rank over Q, nothing else.

## The instrument check that fired

The first build of the multiplicity certificates was **rejected** by the exact
verifier: where the twist coset representative shared primes with a class, XOR
cancellation put 16 transported points on an isomorphic but *different* model.
The builder was wrong; the verifier caught it; the builder was corrected with an
explicit transport factor and rebuilt. This is recorded because it is the only
direct measurement of whether the independent verifier does any work, and it is
the reason the "verifier shares no code with the search" rule is not decorative.
