---
id: KN-LIT-86e77b
type: literature
title: "Cofactor-torsion attacks on hinted scalar multiplications in SNARK circuits"
authors:
  - "Youssef El Housni"
year: 2026
venue: "Cryptology ePrint Archive, Paper 2026/1776"
identifiers:
  eprint: iacr:2026/1776
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1776"
tags: [elliptic-curve, snark, scalar-multiplication, hinted-computation, cofactor, torsion, subgroup, lattice-decomposition, fake-glv, soundness, attack]
confidence: reported
citation_verified: read
added: "2026-08-24"
superseded_by: null
---

## Contribution
Shows that a family of fast hinted elliptic-curve scalar-multiplication gadgets for
SNARK circuits is unsound when used over curves with nontrivial cofactor unless the
hinted output is additionally bound to the intended prime-order subgroup. The gadgets
replace direct computation of `Q = [k]P` with a short lattice/fraction decomposition of
the scalar and a compact group identity. That identity is checked in the ambient group
`E(F_p)`, so on a cofactor curve it can accept an output that differs from the correct
prime-subgroup result by a nonzero rational torsion point.

## Key claims (as reported)
- The affected optimization family includes the Eagen--El Housni--Masson--Piellard
  (Latincrypt 2025) hinted scalar-multiplication techniques based on short
  lattice/fraction decompositions and a single group identity.
- The soundness argument implicitly needs a prime-order-group hypothesis. When
  `#E(F_p) = h*r` with `h > 1`, checking the certifying identity in all of `E(F_p)`
  does not by itself force the hinted output into the subgroup of order `r`.
- **Any-scalar forgery:** for a scalar fixed by the statement, the decomposition can
  be adapted so that a small rational torsion component cancels from the certifying
  identity.
- **Chosen-scalar forgery:** output-side coefficients can be made to vanish modulo a
  small prime dividing the cofactor, after which a compatible scalar is chosen.
- Both attack classes can make the verifier accept
  `Q' = [k]P + T` for nonzero torsion `T` as though `Q' = [k]P`.
- The paper relates which torsion orders are reachable to the range bound imposed on
  the decomposition's sub-scalars and reports concrete validation on BLS12-381,
  BN254, and BW6-761.
- A direct subgroup-membership check fixes the issue but is expensive in-circuit.
  The proposed lower-cost mitigation binds the hinted output through a hinted
  preimage and chooses a constant sufficient to eliminate the torsion reachable in
  the relevant attack model.

## Relevance to this program
This paper establishes a useful distinction for the elliptic-curve research spine:
**cofactor torsion need not make ECDLP in the large prime-order subgroup easier, but
it can invalidate protocol/circuit identities that silently reason as if the ambient
curve group were prime order.** Future agents should not translate a small cofactor
into an ECDLP speedup without a reduction; instead they should separately audit
whether a protocol exposes full-curve points to algebraic checks that are blind to
small torsion components.

For any proposed scalar-multiplication shortcut, GLV/fake-GLV decomposition,
endomorphism identity, lattice/fraction certificate, or prover-supplied elliptic-curve
hint, add the following soundness obligations before treating the construction as
valid:

1. State whether every point variable is known to lie in the intended prime-order
   subgroup or only on the ambient curve.
2. Re-evaluate the verifier identity in the full group `E(F_p)`, not merely after
   projecting into the order-`r` component.
3. Factor the cofactor sufficiently to enumerate relevant small prime-power torsion
   orders and determine whether the verifier's output-side coefficients annihilate
   any of them.
4. If sub-scalars are range-bounded, compare that bound with the torsion orders that
   can be reached/cancelled; do not assume that clearing the entire cofactor is the
   only possible repair.
5. Red-team hinted outputs by substituting `Q + T` for nonzero small-order `T` and
   checking whether any valid decomposition/certificate remains satisfiable.
6. Benchmark a subgroup-safe computed-output path against a hinted-output path plus
   its clearing/binding cost; an asymptotically shorter decomposition can lose after
   the soundness repair is included.

## Program deductions (not claims attributed to the paper)
- **Ambient-group soundness is a reusable attack surface.** Any optimization that
  proves a relation about an EC point via a compressed algebraic identity should be
  tested on every direct-sum/torsion component of the ambient group. This is a more
  general search heuristic than looking only for conventional small-subgroup attacks.
- **Coefficient-annihilator search can be automated.** Given a verifier identity,
  extract coefficients multiplying prover-controlled point variables, reduce them
  modulo each small prime power dividing the cofactor, and search for parameter or
  decomposition choices that make a coefficient zero. This is a promising generic
  red-team pass for the autoresearcher.
- **Range bounds are cryptographic parameters.** A decomposition bound that was
  introduced as a performance/range-check parameter can also determine which torsion
  orders an adversary can exploit. Treat it as part of the soundness model.
- **Endomorphism reasoning is subgroup-scoped.** Eigenvalue relations used by GLV-like
  decompositions are properties of the targeted prime-order eigenspace; agents must
  not extend them to arbitrary ambient-curve points without checking the torsion
  action of the endomorphism.

## Independent implementation signal
As of 2026-08-24, the published gnark v0.16.1 `sw_emulated` API documents a
`CofactorClearing` constant for fake-GLV / GLV+fake-GLV hinted scalar multiplication.
Its documentation states that the constant must be divisible by each cofactor
prime-power below the sub-scalar range so that a hinted preimage check binds the
result into the prime-order subgroup. The same API can prefer classic GLV on cofactor
curves when the clearing overhead outweighs the fake-GLV savings; its BLS12-381 G1
comment reports roughly 105k R1CS constraints for classic GLV versus roughly 116k for
GLV+fake-GLV+clearing. This is independent implementation evidence for the practical
importance of including subgroup repair cost in optimization comparisons.

Implementation reference:
`https://pkg.go.dev/github.com/consensys/gnark@v0.16.1/std/algebra/emulated/sw_emulated`

## Not verified here
The primary IACR metadata page and abstract were read directly and support the claims
above. The PDF endpoint was not retrievable in the current research environment, so
this entry does **not** claim independent verification of the paper's proofs, theorem
numbering, exact attack algorithms beyond the abstract, curve-specific torsion
constants, constraint tables, or the formal minimality proof for the proposed
preimage-binding constant. Those details should be upgraded from reported to
reproduced only after a full-paper read and/or local reproduction.