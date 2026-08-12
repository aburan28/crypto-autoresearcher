---
id: KN-TECH-009
type: technique
title: Elliptic nets and elliptic divisibility sequences (EDS)
tags: [elliptic-nets, elliptic-divisibility-sequence, eds, somos, recurrence, division-polynomial, representation, ecdlp]
confidence: reported
complexity: net values computable in linear time via the recurrence; NO sub-birthday ECDLP mechanism is known
applicability: computing pairings and encoding point/scalar relations via nonlinear recurrences; ECDLP advantage unestablished
source_refs: [KN-LIT-018]
added: 2026-07-21
superseded_by: null
---

## Method
An *elliptic divisibility sequence* is an integer sequence W_n satisfying the
nonlinear recurrence W_{m+n}W_{m-n}W_1^2 = W_{m+1}W_{m-1}W_n^2 -
W_{n+1}W_{n-1}W_m^2, tied to the division polynomials of an elliptic curve
(Ward 1948). An *elliptic net* (Stange, KN-LIT-018) generalizes this to a map
Z^n -> ring satisfying a Somos-type quadratic recurrence, encoding several curve
points at once. Net values compute the Tate/Weil pairing in linear time.

## Role / why it is recorded
It is a genuinely non-generic *representation* of curve arithmetic: net terms
are algebraic functions of x(kP), and Somos identities give exact multiplicative
relations among them. This is the object the program's elliptic-net candidate
re-encodes ECDLP into (RQ-NET-001, EXP-NET-001), testing whether Somos-identity
collisions supply relations below the birthday bound.

## Program usage and the key caveat
Per the program's own literature search, nets were built to COMPUTE pairings, and
NO sub-rho EDS/net DLOG mechanism is known. The strongest kill argument: Somos
identities are universal (hold for every k), so restricted to a single k-fiber
they may yield only tautologies -- relations encoding the group law itself, not
k -- in which case the net is a relabeling inside the generic group model and the
sqrt(n) bound (KN-TECH-005) closes it (KN-OPEN-005). The measurable question is
whether net-relation collision statistics beat the random-oracle birthday model;
this entry records the representation and its recurrence, NOT an advantage.

## Applicability limits
Nets discard sign/y information (an x-line-like quotient). Any claimed relation
supply must be shown to be non-tautological (k-dependent) and to arrive
sub-birthday; absent that, the representation is generic.
