---
id: KN-TECH-018
type: technique
title: Endomorphism and automorphism speedups for the rho baseline (GLV/GLS, negation)
tags: [endomorphism, automorphism, negation, glv, gls, equivalence-class, rho-speedup, baseline, ecdlp]
confidence: established
complexity: rho speedup factor ~sqrt(|Aut|) - e.g. sqrt(2) for negation, ~sqrt(2m) for order-m automorphism / Frobenius on special curves
applicability: adjusting the Pollard-rho baseline constant for curve automorphisms; sizing which curves have exploitable endomorphism structure
source_refs: [KN-LIT-041, KN-LIT-042, KN-TECH-006]
added: 2026-07-22
superseded_by: null
---

## Method
Curve automorphisms give free maps between points (negation P -> -P always;
Frobenius / CM endomorphisms on special curves). Pollard rho can walk on
*equivalence classes* modulo the automorphism group instead of on points, so a
group of order |Aut| shrinks the effective search space by |Aut| and the expected
step count by ~sqrt(|Aut|) (Wiener-Zuccherato, KN-LIT-042; Duursma-Gaudry-Morain
for larger orders). The same endomorphisms speed scalar multiplication (GLV/GLS,
KN-LIT-041).

## Program usage
Fixes the *automorphism-adjusted* constant in the rho baseline the program
charges against (KN-TECH-006): the convention "0.886*sqrt(n) with negation"
already includes the sqrt(2) negation factor. GLS (KN-LIT-041) shows exploitable
endomorphisms exist for a large curve class, so the discount is broad, not
CM-only. A claimed prime-field advantage must beat this discounted baseline.

## Applicability limits
The sqrt(|Aut|) discount is a CONSTANT factor -- it does not change the exponent
1/2 (KN-TECH-005), so it is a baseline calibration, not an attack. Generic
ordinary prime-field curves have |Aut| = 2 (negation only); larger factors need
special CM / subfield / Koblitz structure, which the program's target family
(random ordinary curves) generally excludes. Negation walks require fruitless-
cycle handling. These are baseline-tightening facts, not non-generic mechanisms.
