---
id: KN-FIND-ALLM-CLOSURE-001
type: internal_finding
title: All-m closure -- no decomposition length beats rho via MITM; and the m=3 vs m>=4 free-oracle dichotomy
tags: [prime-field, index-calculus, all-m, mitm, 3sum-indexing, closure, dichotomy, scope-correction]
confidence: established
internal_refs: [research/THM-collection-lower-bound-20260722.md, KN-FIND-SP4-EQUIV-001]
added: 2026-07-22
superseded_by: null
---

## Result (unconditional; numerically verified at N=10^18)
With a = ceil(m/2), the meet-in-the-middle family costs
Total = B^a + Theta(N/B^{a-1}) = Theta(N^{a/(2a-1)}) at B ~ N^{1/(2a-1)}.
Since a/(2a-1) > 1/2 for every finite a, **every decomposition length m >= 3 is
strictly worse than rho**: 2/3 (m=3,4), 3/5 (m=5,6), 4/7 (m=7,8), ... -> 1/2
from above, never reaching it. This closes the "larger m escapes" hatch.

## Dichotomy + scope correction (important)
With the same space but a FREE query (T=1):
- m=3 -> exactly 2*sqrt(N): NO gain. Binding resource = SPACE.
- m>=4 -> beats rho (N^0.416 at m=4, N^0.391 at m=6). Binding resource = QUERY.
Therefore KN-FIND-SP4-EQUIV-001's Corollary 9 ("speeding up the decomposition
test cannot beat rho") is **specific to m=3** and must NOT be read as universal.
At m>=4, solve-acceleration work (Groebner / degree of regularity / elimination)
targets the correct variable; it must merely reach the k-SUM-Indexing frontier
(at m=4: space M=B^2 on the pair-set with query o(M^{1/2})).

## Unified conclusion
At every m >= 3, beating rho is equivalent to violating the k-SUM-Indexing
frontier for elliptic-curve point sets -- on the space side at m=3, on the query
side at m>=4. The barrier is uniform in m.

## Boundaries (honest)
- Theorem 10 is unconditional but covers the meet-in-the-middle family (the
  achievable upper-bound family); the general lower bound remains conditional on
  k-SUM-Indexing.
- Not a breakthrough: a closure/dichotomy result that completes the barrier map
  over the m-axis and corrects the scope of a previously recorded corollary.
