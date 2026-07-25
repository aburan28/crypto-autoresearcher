---
id: KN-FIND-INTERNAL-REL-001
type: internal_finding
title: The internal-relation index-calculus variant also never beats rho, for every m
tags: [prime-field, index-calculus, internal-relations, all-m, closure, barrier]
confidence: established
internal_refs: [research/THM-collection-lower-bound-20260722.md, KN-FIND-ALLM-CLOSURE-001, KN-FIND-SP4-EQUIV-001]
added: 2026-07-22
superseded_by: null
---

## Result (unconditional; numerically verified at N=10^18)
For the classical variant that harvests zero-sum m-subsets WITHIN the factor
base (no random target draws): needing ~B relations forces
B >~ (m! N)^{1/(m-1)}, and the meet-in-the-middle search costs >= B^a with
a = ceil(m/2). Hence Total = Omega(N^{a/(m-1)}), and a/(m-1) > 1/2 for every m
(since 2*ceil(m/2) >= m > m-1). Exponents: 1 (m=3), 2/3 (m=4), 3/5 (m=6),
4/7 (m=8), 5/9 (m=10) -> 1/2 from above, never reaching it. At m=3 the required
factor base is already B ~ N^{0.52} > sqrt(N) before any search begins.

## Why it matters
This closes the last structural variant: the earlier theorems all assumed the
target-sectioned (single-relation) architecture, so a reader could object that
classical index calculus works differently. It does -- and it also fails.
Combined coverage: both principal architectures, every m, every factor base,
generic-group methods, the naive algebraic oracle, and the standard toolkit.

## Boundaries (honest)
- Unconditional for the MITM search family (the achievable upper bound); a
  general lower bound for arbitrary relation-search algorithms remains
  conditional on k-SUM-Indexing.
- A closure result completing the barrier map, not a breakthrough.
