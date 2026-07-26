---
id: KN-FIND-SP4-EQUIV-002
type: internal_finding
title: Corrected reading of the (S,T) frontier -- a Theta(B)-space decomposition test with query o(B) beats rho (supersedes the 'space is binding' claim)
tags: [prime-field, index-calculus, 3sum-indexing, space-time-tradeoff, groebner, dreg, correction, m3]
confidence: established
internal_refs: [CORR-20260722-001, KN-FIND-SP4-EQUIV-001, research/THM-collection-lower-bound-20260722.md]
added: 2026-07-22
superseded_by: null
---

## Corrected statement
Theorem 8 (unchanged, correct): a sub-rho m=3 index calculus exists iff a
decomposition oracle achieves S*T = o(B^2). The frontier has TWO usable corners:
- **High-space corner** S = Theta(B^2): then T must be o(1) -- impossible. This
  is Corollary 9 (T=1, S=B^2 gives exactly 2*sqrt N, never better).
- **Low-space corner** S = Theta(B) (store only the factor base and the
  summation-polynomial system -- i.e. an algebraic/Groebner test): then
  S*T = o(B^2) iff **T = o(B)**. A sublinear-in-B decomposition test beats rho:
  with T = B^{1-eps}, total = Theta(N^{1/(2+eps)}) < sqrt N for every eps > 0
  (numerically: N^0.473 at eps=0.2, N^0.418 at eps=0.5, N=1e16).

## Why this matters (direction change)
The earlier reading ("space is the binding resource; solving-degree work is aimed
at the wrong variable", KN-FIND-SP4-EQUIV-001) generalised one corner of the
trade-off to the whole frontier and is withdrawn (CORR-20260722-001). The
summation-polynomial / Groebner line is inherently LOW-SPACE, so it sits in the
corner where solve time IS the binding resource. The campaign's degree-of-
regularity program (DREG/SIG) is therefore a VALID route, with a now-sharp target:

    a decomposition test for "is R a sum of 3 factor-base points"
    running in o(B) time using O(B) space.

Equivalently: beat 3SUM-Indexing at its S = Theta(B) corner using the algebraic
structure of S_4. Current status of that target: the naive algebraic oracle is
Theta(B^2) (KN-FIND-S4-ORACLE-001), so the gap to close is from B^2 down to o(B).

## Boundaries (honest)
- This is a correction of interpretation, not a new algorithm: no test with
  T = o(B) is known, and 3SUM-Indexing conjecturally forbids it for arbitrary
  sets. Whether curve structure evades that is the open crux.
- Theorem 8 and Corollary 9's arithmetic are unaffected and remain correct.
