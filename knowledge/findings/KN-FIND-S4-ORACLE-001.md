---
id: KN-FIND-S4-ORACLE-001
type: internal_finding
title: The natural S_4 algebraic decomposition oracle gives no speedup over generic MITM (m=3, prime field)
tags: [prime-field, index-calculus, summation-polynomial, s4, 3sum, oracle, m3, no-speedup]
confidence: reported
internal_refs: [research/PLAN-prime-field-ecdlp-program-20260722.md, research/THM-collection-lower-bound-20260722.md]
added: 2026-07-22
superseded_by: null
---

## Result (computationally verified, no Sage; p in {101,251,509,1009})
For m=3 decomposition over a prime-field elliptic curve, the natural algebraic
oracle built from the 4th summation polynomial S_4 -- for each x_3 in the factor
base V, solve the degree-4 curve S_4(x_1,x_2,x_3,x_R)=0 for V-points -- costs
Theta(B^2) field operations, identical to the generic meet-in-the-middle
pairwise-sum table. The S_4=0 test is correct (it detects the decompositions,
in fact all sign patterns +/-P_1+/-P_2+/-P_3+/-R=O). So the OBVIOUS use of the
summation polynomial provides NO asymptotic speedup over generic 3SUM/MITM.

## Consequence for the crux (SP4)
Combined with the localization theorem, the m=2 no-go, the conditional m=3
3SUM-Indexing no-go, and the collinearity/GPT bridge: a sub-rho prime-field
algorithm cannot come from the straightforward algebraic oracle. Any escape must
exploit a NON-obvious property of S_4 -- e.g. fast multipoint evaluation of its
resultant (Kedlaya-Umans-style) or the curve's group structure -- to break the
3SUM-Indexing barrier. This is the one remaining open locus; the naive algebraic
route is now ruled out empirically.

## Boundaries (honest)
- Rules out only the NAIVE algebraic oracle (root-finding on the summation
  curve); does not prove no non-obvious algebraic oracle exists (that is the
  open crux). Toy scale, small p; the B^2 vs B^3 accounting is standard.
- Not a breakthrough and not a full no-go: a negative result for one approach
  that sharpens where the open question lives.
