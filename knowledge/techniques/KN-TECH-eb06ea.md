---
id: KN-TECH-eb06ea
type: technique
title: "Galois-eigenspace rank certificates: replace an n x n height regulator by distinctness of n squarefree integers modulo squares"
tags: [elliptic-curves, mordell-weil-rank, quadratic-twists, multiquadratic-fields, galois-cohomology, eigenspace-decomposition, mazur-torsion, certificate-design, exact-verification, independence-proofs]
confidence: standard_algebra_applied_as_a_certificate_design_verified_in_practice
evidence_level: exact_algebraic_argument_with_a_working_implementation
source_refs: [EXP-ECRANK-e1e30e]
internal_refs: [KN-FIND-fd382f, H-ECRANK-28dba7, EV-ECRANK-b6c9b6]
proof_status: derivation
proof_refs:
  - experiments/EXP-ECRANK-e1e30e/source/twist_family.py
  - experiments/EXP-ECRANK-e1e30e/source/verify_certificate.py
  - experiments/EXP-ECRANK-e1e30e/source/quadratic_lift.py
added: '2026-08-22'
superseded_by: null
---

# Galois-eigenspace rank certificates

## The problem this solves

A rank lower bound is only as good as its independence proof. The default tool
is the Néron–Tate height pairing: exhibit n points, compute the n×n regulator,
show it is nonsingular. That works, and it is what the rank literature runs on,
but it is **numerical** — the certificate ends in a floating-point determinant.
For a claim you want machine-checkable in exact arithmetic, that is the weak
joint.

## The device

Work over a multiquadratic field. Let V ≤ Q*/(Q*)² be a subgroup of order 2^k
and K = Q(√d : d ∈ V), so G = Gal(K/Q) ≅ (Z/2)^k. Put E : y² = x³ + Ax + B.

For squarefree d, the quadratic twist E^(d) : v² = u³ + Ad²u + Bd³ admits

    φ_d(u, v) = ( u/d , (v/d²)·√d ) ∈ E(K),

an injective group homomorphism. For σ ∈ G, σ(√d) = χ_d(σ)√d, so

    σ(φ_d P) = χ_d(σ) · φ_d P :

**the image is a χ_d-eigenvector.** Since E(K) ⊗ Q is a Q[G]-module and G is
elementary abelian, the projector e_χ = |G|⁻¹ Σ_σ χ(σ)σ annihilates every
eigenvector of a different character. Applying e_{χ_j} to a relation Σ nᵢPᵢ = 0
leaves n_j P_j = 0.

**Consequence.** Non-torsion points attached to *pairwise distinct* classes d are
Z-independent, and the proof involves no metric, no archimedean place, and no
limit. The independence certificate is: *these squarefree integers are pairwise
distinct modulo squares*.

## What the certificate reduces to

1. each point satisfies its twist equation — exact rational arithmetic;
2. each point is non-torsion — by **Mazur**, a torsion point of E/Q has order in
   {1,…,10,12}, so exhibiting m·P ≠ O for m = 1..12 is a complete proof;
3. the classes are pairwise distinct mod squares — compare squarefree parts;
4. V is closed under multiplication mod squares and contains 1 — so K really is
   the field named and [K:Q] = |V|.

All four are finite exact checks. A verifier doing only these needs nothing but
`fractions` from the standard library.

## Costing it honestly

- **Ceiling.** Only 2^k characters exist, so this argument alone certifies at
  most 2^k. Rank ≥ 31 forces [K:Q] ≥ 32. Below that you must put several points
  in one class, and *within-class* independence is a height computation again —
  the device buys nothing there, and a certificate that mixes the two should say
  which part rests on which.
- **It does not help over Q.** At k = 0 it degenerates to the base curve's own
  rank. Anyone hoping to attack the rank-over-Q record with it is misreading it.
- **Points still have to be found.** Descent (PARI `ellrank`) does that work. The
  device changes what must be *trusted*, not what must be *computed*: found
  points are re-checked, never inherited.

## Two constructions worth keeping

**Free twists with points.** For *any* rational x₀, set d = f(x₀) = x₀³+Ax₀+B.
Then E^(d) carries the rational point (d·x₀, d²), since d⁴ = d³·f(x₀). No point
search, and **no factorisation of d** — Q(√d) depends only on d mod squares, and
"d is not a square" is an integer-square-root test. This makes "add 1 to the rank
of any curve, over an explicit quadratic field" a one-line construction, and it
is what lifts a rank-r curve over Q to rank ≥ r+1 over Q(√d) with the added point
provably independent of *all* of E(Q) (it is in the minus eigenspace, E(Q) is in
the plus eigenspace). Extending to m seeds gives rank ≥ r+m over degree 2^m,
with [K:Q] certified by checking that every non-empty subset product is a
non-square.

**Cosets, not just subgroups.** Twisting the base curve by d₀ carries the family
{E^(d) : d ∈ V} to {E^(d) : d ∈ d₀V}. So scanning *affine* subspaces of the
support group covers every quadratic twist of every base curve at no extra
descent cost — the same 2^|S| rank computations serve all cosets.

**Implementation trap, found the hard way.** If classes are stored as F₂ bitmasks
over a prime support, XOR *cancels* shared primes, so class(m₀ ⊕ v) and d₀·d
differ by the square of the shared primes. Points must be transported along
(u,v) ↦ (ut², vt³) with t² = d₀d / class(m₀⊕v), or they land on an isomorphic but
different model. In this experiment the independent verifier rejected 16 such
points before the transport factor was added.
