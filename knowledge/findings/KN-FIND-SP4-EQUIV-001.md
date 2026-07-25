---
id: KN-FIND-SP4-EQUIV-001
type: internal_finding
title: SP4 resolved -- sub-rho m=3 prime-field index calculus is EQUIVALENT to breaking 3SUM-Indexing; the binding resource is space, not solve time
tags: [prime-field, index-calculus, 3sum-indexing, equivalence, space-lower-bound, m3, crux, sp4]
confidence: established
internal_refs: [research/THM-collection-lower-bound-20260722.md, research/PLAN-prime-field-ecdlp-program-20260722.md, IDEA-20260722-002, KN-FIND-3SUM-NOGO-001]
added: 2026-07-22
superseded_by: null
---

## Result (proved both directions; numerically verified)
For m=3 target-sectioned index calculus on E/F_p with an oracle of space S and
query T: Total = S + B + Theta(T*N/B^2).
- **Necessity:** Total = o(sqrt N) forces S = o(sqrt N) AND T = o(B^2/sqrt N),
  whose product is *exactly* S*T = o(B^2) (ratio 1.000 at every B, N tested).
- **Sufficiency:** S = B^{2-delta}, T = O(1) gives Total = N^{(2-delta)/(4-delta)}
  < sqrt N for EVERY delta > 0.
Hence: **a sub-rho m=3 algorithm exists iff a 3SUM-Indexing structure with
S*T = o(B^2) exists for curve-point sets.** Under the 3SUM-Indexing conjecture,
none does. SP4 is equivalent to, not merely analogous to, that open problem.

## Corollary (research-redirecting; non-obvious)
Even a FREE oracle (T=1) with quadratic space S=Theta(B^2) gives exactly
2*sqrt(N) at B=N^{1/4} -- matching rho, never beating it. Therefore every
approach that only speeds up the decomposition TEST (Groebner solving, degree of
regularity, summation-polynomial elimination) provably cannot beat rho at m=3,
no matter how fast it gets. The binding resource is preprocessing SPACE.
This says the campaign's degree-of-regularity axis (DREG/SIG), and the
summation-polynomial solving effort generally, are aimed at the wrong variable
for the m=3 sub-rho goal.

## Boundaries (honest)
- The negative direction is conditional on the 3SUM-Indexing conjecture; the
  cost model (space S, query T, unit ops) and the m=3 target-sectioned scheme are
  the stated hypotheses. Corollary 9 (T=1, S=B^2 -> 2 sqrt N) is unconditional.
- This resolves SP4 as an EQUIVALENCE; it does not construct the structure and
  is not a break of ECDLP. Constructing one would refute 3SUM-Indexing.
- Novelty vs. full literature: unverified.
