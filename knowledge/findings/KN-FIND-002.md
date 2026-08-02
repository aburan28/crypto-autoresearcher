---
id: KN-FIND-002
type: internal_finding
title: >-
  Jet and endomorphism ECDLP oracles are GGM-simulable with O(1) overhead,
  closing their candidate families at exponent 1/2; elliptic-net and incidence
  oracles are GGM-simulable with non-constant overhead, providing no
  sub-birthday advantage
tags: [ggm, simulability, jet, endomorphism, elliptic-net, incidence, ecdlp, closure, exponent-half, generic-group-model]
confidence: strong
status: established
source_refs: [EV-GGM-001, DEC-20260726-007, EXP-GGM-001, KN-TECH-005, KN-OPEN-005]
added: 2026-07-26
superseded_by: null
---

## Finding

A machine-checkable GGM simulability test (EXP-GGM-001) correctly classifies
four augmented ECDLP oracles, validated against four controls (4/4 correct).

### SIMULABLE with O(1) overhead (closed at exponent 1/2 by KN-TECH-005)

1. **Jet oracle** (C=1): the dual-number (eps) data from F_p[eps]/eps^2 is a
   deterministic function of (P, Q, P+Q, curve_parameters). The derivative of
   the addition map is a rational function of the coordinates, which are
   determined by the group element + the public curve equation. The generic
   simulator computes P+Q (1 group operation) and then evaluates the rational
   function. **This closes all jet-based ECDLP candidates** (ECDLP-IDEA-004
   and related) at exponent 1/2.

2. **Endomorphism oracle** (C=0): the endomorphism phi (e.g.,
   phi(x,y) = (zeta_3*x, y) for j=0 curves) is a public, deterministic map
   from the curve parameters. No group operations needed. **This contextualizes
   H-STR-002**: the block-circulant LA advantage (387x displacement rank
   reduction at B=397) is non-generic — phi is available to the generic model,
   and the structured LA advantage does not provide sub-birthday information.

### SIMULABLE with non-constant overhead (NOT closed at 1/2)

3. **Elliptic-net oracle** (O(log N)): the net value W(a,b) = a*P + b*Q is
   computable via group operations, but requires O(log a + log b) = O(log N)
   operations. The Somos identities are universal (hold for every k), so the
   net encodes only the group law on a single k-fiber. Not closed at 1/2 by
   the constant-overhead bound, but O(log N) << sqrt(N), so no sub-birthday
   advantage.

4. **Incidence oracle** (O(B^m)): decompositions are found by brute-force
   summing m-subsets of the factor base, costing O(B^m) group operations. For
   fixed B, m this is constant, but B grows with problem size. Not closed at 1/2
   by the constant-overhead bound.

## Scope and limitations

- The classification uses the **structured GGM** (curve equation is public),
  not the strictest Shoup GGM (opaque labels). Under the strictest GGM, jet
  and endomorphism would be NON-SIMULABLE because they require coordinate
  access.
- The O(1) closures for jet and endomorphism are **scale-independent
  mathematical results** (derivation-level), valid at toy, medium, and crypto
  scales.
- The test operates on oracle **specifications**, not implementations. Real
  implementations may leak timing or side-channel information outside the GGM.

## Evidence

- EV-GGM-001 (theoretical, strong, derivation proof_status)
- EXP-GGM-001: 9 runs, control gate 4/4, all 4 augmented oracles classified
- DEC-20260726-007: decision = support
