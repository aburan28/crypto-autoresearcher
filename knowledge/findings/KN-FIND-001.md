---
id: KN-FIND-001
type: internal_finding
title: Prime-field decomposition yield saturates the birthday bound; no structured or m-dependent sub-rho signal (toy)
tags: [prime-field, index-calculus, factor-base, relation-collection, yield, pollard-rho, barrier, negative-result]
confidence: reported
internal_refs: [EV-SEMAEV-003, DEC-20260721-002, EXP-SEMAEV-003, EXP-SEMAEV-002]
added: 2026-07-21
superseded_by: null
---

## Finding (toy scale, generic prime fields)
Over generic prime-field curves at toy scale, the m-point decomposition yield of
a size-B factor base follows the birthday bound

    Pr[random target decomposes] ~= k * B^m / #E ,

with a BOUNDED constant k that does not grow with field size:
- m=2: k ~= 1.85, flat (k in [1.71, 1.86]) across #E in [2.4e3, 2.5e5] (~100x).
- m=3: k ~= 1.30, flat (k in [1.25, 1.35]) across the same range,
  after controlling the small-#E saturation confound (B chosen so B^m/#E ~ 0.08).

No factor-base geometry tested beats a matched random base by >1.5x yield at
m=2 (EV-SEMAEV-003, replicated across 15 instances, all 95% CIs below 1.5x;
consistent in spirit with the campaign's m=3 rejected_scoped H-FB-001).

## Mechanism / why this is essentially a cap (m=2)
For m=2 the decomposable targets are exactly the sumset {P_i + P_j} of the
factor base, which has at most C(B,2)+B ~ B^2/2 distinct points (x2 for the two
sign choices). Hence yield <= ~B^2/#E for ANY factor base, and the measured
bases nearly saturate it (k ~= 1.85 vs. the ceiling ~2). A structured base
cannot manufacture more decomposable targets than its sumset contains, so no
m=2 factor base over prime fields can escape this bound. Higher m relaxes the
count (sumset up to ~B^m/m!) but the measured k stays O(1).

## Implication (scoped)
This is a quantitative, confound-controlled reproduction of the prime-field
relation-collection barrier (KN-OPEN-001, KN-LIT-006): to collect ~B relations
one needs a factor base large enough that the linear-algebra/collection cost is
not below generic Pollard-rho (KN-TECH-001). No sub-rho signal appears on the
factor-base / relation-yield axis at toy scale.

## Boundaries (what this is NOT)
- Toy prime fields only (#E up to ~2.5e5); NOT crypto-scale (AGENTS rule 7).
- NOT a theorem: the k-flatness is an empirical, reproducible (deterministic,
  seed=3) measurement over a bounded range; the m=2 sumset cap is a simple
  counting bound, not a hardness proof.
- A NEGATIVE / barrier-confirming result. It closes the tested factor-base-yield
  directions; it does not touch the degree-of-regularity / Groebner-cost axis
  (KN-OPEN-002), which over prime fields remains open and is the live frontier.
- Provenance: the structured-vs-random null is committed replicated evidence
  (EV-SEMAEV-003); the k-scaling constants are reproducible exploratory
  measurements, not yet frozen as immutable run records.
