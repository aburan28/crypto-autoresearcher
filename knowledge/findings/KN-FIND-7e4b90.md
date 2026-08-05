---
id: KN-FIND-7e4b90
type: internal_finding
title: Wesolowski degree bound requires 4D quaternion algebra — blocked for ordinary prime-field ECDLP
tags: [wesolowski, quaternion-algebra, ordinary-curves, structural-theorem, 4d-lattice, blocked]
confidence: proved_negative
evidence_level: mathematical_argument
source_refs: [BATCH-096, DEC-20260804-bfbb09, inputs/P13-WESOLOWSKI-2026]
internal_refs: [DEC-20260804-bfbb09]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-7e4b90.md]
added: '2026-08-04'
superseded_by: null
---

## Finding

Wesolowski's p^{1/3} theorem (Theorem 1.5) for the supersingular isogeny problem requires:
- End(E) = B_{p,∞}, the definite quaternion algebra ramified at p and ∞
- A 4D lattice over the maximal order in B_{p,∞}
- Short elements of norm O(p^{1/3}) found via 4D LLL

For ordinary prime-field curves:
- End(E) = imaginary quadratic order O ⊂ Q(sqrt(D)) — commutative, rank 2 over Z
- The analogue lattice is 2D with shortest vector of norm O(sqrt(N)) ~ O(sqrt(p))
- No short element of norm p^{1/3} exists (this would require |D| ~ p^{2/3} and class
  number 1, which is not the case for generic curves)

**Blocked by:**
The 4-dimensional quaternion algebra structure is ESSENTIAL for Wesolowski's proof.
Ordinary curves have a 2-dimensional commutative endomorphism ring — no quaternion structure,
no 4D short-vector argument, no p^{1/3} degree bound.

## Implication

No direct transfer of Wesolowski's structural theorem to ordinary prime-field ECDLP.
The ECDLP scalar k ∈ Z/N has no "short representation" beyond the trivial k ≤ N/2,
which corresponds to the 2D lattice shortest vector of norm ~ sqrt(N) = Pollard rho.
