---
id: KN-TECH-003
type: technique
title: Point-decomposition index calculus for ECDLP
tags: [index-calculus, point-decomposition, factor-base, relations, ecdlp]
confidence: established
complexity: dominated by relation-collection (decomposition tests) and linear algebra; regime-dependent
applicability: strong over small-degree extension fields; no advantage known over prime fields
source_refs: [KN-LIT-002, KN-LIT-003, KN-LIT-006]
added: 2026-07-19
superseded_by: null
---

## Method
1. Fix a factor base F of points with x-coordinate in a chosen small set V.
2. Relation collection: for many random R = a*P + b*Q, test whether R
   decomposes as a sum of m factor-base points via a summation-polynomial
   system (KN-TECH-002); a success yields a linear relation among discrete
   logs of factor-base elements plus (a, b).
3. Linear algebra: once > |F| independent relations are collected, solve the
   sparse linear system mod n to recover factor-base logs, then k.

## Regime dependence
- Extension fields GF(q^n), small n: the factor base (x in a subfield) has
  favorable decomposition probability -> subexponential (KN-LIT-002/003).
- Prime fields GF(p): no good structured factor base is known; decomposition
  probability and Gröbner cost make it uncompetitive with rho (KN-LIT-006,
  KN-OPEN-001).

## Verifiability
Each collected relation is independently checkable (sum the points, confirm
== O), so relation records carry verifiable certificates.
