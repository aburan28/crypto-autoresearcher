---
id: KN-TECH-059
type: technique
title: Formal groups of elliptic curves
tags: [formal-group, elliptic-curve, p-adic, anomalous, logarithm, lubin-tate, local-field, foundational, number-theory]
confidence: established
complexity: structural — not an algorithm; the formal logarithm is O(p-adic precision) to evaluate when defined
applicability: every elliptic curve; algorithmic payoff known only in special cases (notably anomalous / trace-one)
source_refs: [KN-LIT-7621, KN-LIT-7623, KN-LIT-087, KN-LIT-088, KN-LIT-089, KN-TECH-033]
added: 2026-07-31
superseded_by: null
---

## Method
An elliptic curve E over a ring R in which a prime p is not invertible on the
identity component of the formal completion yields a one-dimensional formal
group law Ê over R. The formal logarithm log_Ê : Ê → Ĝ_a is a homomorphism
of formal groups; when it converges on the prime-to-the-identity kernel of
reduction, it converts the group law into addition.

## Why it matters for this program
Two distinct formal-group stories must not be collapsed:

1. **Elliptic formal group** (Silverman Ch. IV, KN-LIT-7621). This is the
   object behind the anomalous additive transfer (KN-TECH-033 / Satoh–Araki /
   Smart / Semaev): when #E(F_p)=p the formal logarithm is globally defined
   on E(F_p) and ECDLP becomes a division in (F_p,+).
2. **Lubin–Tate formal A-modules** (KN-LIT-7623). These construct local
   abelian extensions; they are not a drop-in ECDLP oracle on a random
   cryptographic curve.

A proposal that writes “use the formal group” must name which formal group,
over which ring, and which kernel the logarithm is evaluated on. Without that,
the claim is underspecified relative to KN-TECH-033.

## Applicability limits
The elliptic formal logarithm does **not** yield a sub-rho attack for generic
trace. Away from the anomalous locus it is a local analytic tool (p-adic
heights, formal immersion criteria), not a global discrete-log algorithm.
Lubin–Tate theory likewise does not solve ECDLP on E(F_q).

## Verified vs reported
Existence of the elliptic formal group and its logarithm is textbook
(`confidence: established`, KN-LIT-7621). The anomalous collapse is reported
from KN-LIT-087–089 / KN-TECH-033. Lubin–Tate identity is reported from
KN-LIT-7623. No new computation was performed here.
