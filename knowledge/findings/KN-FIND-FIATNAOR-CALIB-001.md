---
id: KN-FIND-FIATNAOR-CALIB-001
type: internal_finding
title: The best known 3SUM-Indexing structure lands exactly ON the rho boundary, never below it
tags: [prime-field, index-calculus, 3sum-indexing, fiat-naor, calibration, barrier, tightness]
confidence: established
internal_refs: [research/THM-collection-lower-bound-20260722.md, KN-FIND-SP4-EQUIV-001, KN-LIT-011]
added: 2026-07-22
superseded_by: null
---

## Result (calibration of Theorem 8 against the state of the art)
Theorem 8 requires S*T = o(B^2) to beat rho at m=3. The best known
3SUM-with-preprocessing data structure (Fiat-Naor inversion, GGHPV STOC 2020,
KN-LIT-011) achieves S^3 * T = O~(B^6). On that curve S*T = B^6/S^2, so
        S*T < B^2  <=>  S > B^2  (superquadratic space),
while feasibility T >= 1 forces S <= B^2. The two are incompatible: the
Fiat-Naor curve **touches** S*T = B^2 exactly at (S,T) = (B^2, 1) and never
enters the o(B^2) region.

Moreover (S,T) = (B^2,1) at the m=3 optimum B = N^{1/4} gives S = sqrt(N) --
which is precisely Corollary 9's break-even 2*sqrt(N).

## Why this matters
1. **Consistency:** the barrier theorem is not contradicted by the best known
   upper bound -- a real check that could have falsified it and did not.
2. **Tightness / non-vacuity:** the equivalence is calibrated, not empty. The
   state of the art sits exactly ON the Pollard-rho boundary; beating ECDLP this
   way requires strictly improving the known 3SUM-Indexing frontier.
3. **Literature bridge confirmed:** GGHPV's lower bounds explicitly cover "three
   points on a line", which by the chord-tangent law IS the m=3 EC decomposition
   condition -- independently supporting Prop. 4's collinearity framing.

## Novelty assessment (honest)
- The 3SUM-Indexing framework, its Fiat-Naor upper bound, and the collinear
  ("three points on a line") lower-bound family are **known** (GGHPV 2020).
- The *bridge* from prime-field EC index calculus to 3SUM-Indexing, and
  Theorems 8/10/11/12 of this program, were **not found** in two targeted
  literature searches. Status remains **unverified**, not "novel": two searches
  are not a literature review, and the components are standard. Anyone building
  on this must do a proper survey before claiming priority.
