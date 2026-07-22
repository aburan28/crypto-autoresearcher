---
id: KN-FIND-3SUM-NOGO-001
type: internal_finding
title: Conditional (3SUM-Indexing) no-go for generic m=3 prime-field EC index calculus
tags: [prime-field, index-calculus, 3sum-indexing, fine-grained, lower-bound, no-go, m3]
confidence: reported
internal_refs: [research/THM-collection-lower-bound-20260722.md, research/PLAN-prime-field-ecdlp-program-20260722.md, IDEA-20260722-001]
added: 2026-07-22
superseded_by: null
---

## Result (proved, conditional on the 3SUM-Indexing conjecture)
Any curve-structure-oblivious m=3 target-sectioned index calculus over E/F_p is a
2-SUM-indexing data structure used B times per target. Optimizing total cost
S + B + Theta(NT/B) on the conjectured frontier S*T = Theta(B^2) gives
Theta~(N^{2/3}), at the MITM corner (T~1, B~N^{1/3}). Since N^{2/3} > sqrt(N),
generic m=3 index calculus is asymptotically slower than Pollard rho under the
3SUM-Indexing conjecture. Analytic optimum verified numerically.

## Role in the program
Completes the "generic" side of the barrier: m=2 (unconditional), Shoup
(generic Omega(sqrt N)), and now m=3 (3SUM-conditional) all give no speedup. By
the localization theorem the ONLY remaining locus for a sub-rho algorithm is a
NON-generic decomposition oracle that beats 3SUM-Indexing using the algebraic
structure of the summation polynomial S_{m+1} (the crux; IDEA-20260722-002).

## Boundaries (honest)
- Conditional on the 3SUM-Indexing conjecture AND on the oracle being structure-
  oblivious; the crux is precisely whether S_{m+1} escapes both.
- The 2-SUM<->3-sum reduction and the tradeoff optimization are elementary; the
  fine-grained-complexity framing of EC index calculus is the contribution.
  Novelty vs. full literature: unverified.
