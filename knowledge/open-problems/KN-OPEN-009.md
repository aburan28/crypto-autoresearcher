---
id: KN-OPEN-009
type: open_problem
title: Is the geometric monodromy of the m-th Semaev summation cover the full symmetric/wreath group for generic ordinary curves, or is there an exceptional locus with smaller monodromy giving deviant relation rates?
tags: [monodromy, galois, chebotarev, semaev-cover, relation-rate, imprimitive, exceptional-curves, open]
confidence: reported
status: open
source_refs: [KN-LIT-039, KN-LIT-001]
added: 2026-07-22
superseded_by: null
---

## Statement
For the m-th Semaev summation cover over the parameter space of (x_1,...,x_{m-1}),
is the geometric monodromy (Galois) group the full symmetric (resp. wreath)
group for all ordinary E/F_p outside an explicit exceptional locus -- so that the
Chebotarev/Frobenius cycle-type census yields only the quasirandom relation rate
-- or does an exceptional family (e.g. CM curves) have imprimitive/smaller
monodromy, giving curve-specific relation-rate deviations (or a block system
exploitable by resolvent decomposition)?

## Current state (as reported)
Chebotarev equidistribution (KN-LIT-039) and monodromy computation are standard
mathematics, but no work computing or exploiting the Galois/monodromy group of
Semaev summation covers was located (documented search in the program's
research-direction docs). The program's monodromy candidates (round-2 A1
Chebotarev census, C2 imprimitive-resolvent; EXP-MONO-001) executed a harness-
validation phase; the substantive m=3 census is the gate. Generic curves are
EXPECTED to have full symmetric monodromy (which would make the attack content
vacuous and promote the barrier), but this is unproven.

## Why it matters here
It is a genuinely two-sided experiment: a full-monodromy proof (or census
agreement within the Weil error across sizes) closes the attack content and
yields a barrier theorem; an exceptional locus with strictly smaller monodromy
narrows an exploitable family. Either replaces the *assumed* uniform relation
probability of index-calculus budget planning (KN-OPEN-002) with a theorem-backed
rate. The census is cheap (Frobenius cycle-type histograms), so the value/cost
ratio is high. Any exceptional-curve claim must exclude j=0/1728 extra-
automorphism artifacts from the random controls.
