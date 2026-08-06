---
id: KN-FIND-b7e091
type: internal_finding
title: GGM closure of incidence and endomorphism oracle classes for prime-field ECDLP
tags: [ggm, generic-group-model, incidence, endomorphism, shoup-lower-bound, oracle, closed]
confidence: proved
evidence_level: theorem_backed
source_refs: [BATCH-060, EV-GGM-79e710, DEC-20260804-3b4258]
internal_refs: [EV-GGM-79e710, DEC-20260804-3b4258]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-b7e091.md]
added: '2026-08-04'
superseded_by: null
---

## Finding

For prime-order prime-field elliptic curves, two classes of augmented ECDLP oracles
are GGM-simulable, and their use is therefore closed at exponent 1/2 by the Shoup
generic group model lower bound:

1. **Incidence oracle** (Oracle C): An oracle reporting which factor-base subsets sum
   to the target Q. This is simulable in O(m) group operations per query — the oracle
   output is determined by group operations and equality tests alone.

2. **Endomorphism images oracle** (Oracle D): An oracle returning phi(G), phi(Q) for
   any endomorphism phi of E. For prime-order prime-field curves with End_{F_p}(E) = Z,
   every phi = [m], so phi(Q) = [m]Q is computable in m group operations from Q alone.

## Implication

The Shoup lower bound (1997) states: any algorithm using only a generic group oracle
(group operations + equality tests) requires Omega(sqrt(N)) operations to solve DLP.
Since both Oracle C and Oracle D are generic-group-simulable, algorithms using them
are subject to this lower bound. These oracle classes are CLOSED at exponent 1/2.

## Non-simulable but non-useful oracles (for completeness)

Oracle A (first-jet): non-simulable but privately computable (requires k).
Oracle B (elliptic net): non-simulable but no k-recovery below standard DLP.
Neither provides a publicly computable sub-birthday DLP oracle.
