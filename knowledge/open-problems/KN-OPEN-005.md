---
id: KN-OPEN-005
type: open_problem
title: Is a non-generic ECDLP representation (jets, elliptic nets, incidence reporting) generic-group-model simulable, or can it supply k-dependent relations below the birthday bound?
tags: [generic-group-model, birthday, jets, elliptic-nets, incidence, representation, prime-field, ecdlp, open]
confidence: reported
status: closed_scoped
closed_scoped_at: '2026-10-24'
closed_scoped_by: [DEC-20260722-004, DEC-20260722-006]
closed_scoped_as: >-
  CLOSED FOR TWO BRANCHES ONLY. (1) Jet / dual-number representations: DEC-20260722-004
  records the simulation theorem T4 (THM_JETBARRIER1), so the Omega(sqrt(l)) bound lifts
  to the jet-augmented generic-group model, in-model. (2) Chord / incidence reporting:
  DEC-20260722-006 records the EC-chord richness ceiling (THM_INCBARRIER1), proved in
  the uniform-x sampling model only.
still_open_in:
  - >-
    ELLIPTIC NETS (Somos values). Neither DEC addresses this branch.
  - >-
    SCOPE LIMITS OF THE TWO CLOSURES: jet closure is in-model (maximality of the
    simulable class C2 and Weil-restriction / descent G2 are open); chord closure is
    uniform-x only, with fixed / adversarial factor bases at B = p^alpha, alpha <= 1/2,
    not certified.
source_refs: [KN-LIT-011, KN-LIT-018, KN-TECH-005, KN-TECH-009]
added: 2026-07-21
superseded_by: null
---

## Statement
Several candidate ECDLP representations augment the group with extra structure:
first-jet / dual-number data of the addition law (F_p[eps]/eps^2), elliptic-net
(Somos) values, or output-sensitive incidence reporting of chord relations. For
each, is the augmented oracle *simulable in the generic group model* with O(1)
overhead -- in which case the candidate is closed at exponent 1/2 by the generic
lower bound (KN-TECH-005) -- or does it provide genuinely k-DEPENDENT relations
arriving below the birthday bound?

## Current state (as reported)
The generic sqrt(n) bound (KN-LIT-011) is the barrier; a representation beats it
only if non-generic and non-simulable. The recurring kill argument is
simulability/tautology: jet data may be determined by the zeroth-order solution
(the eps-block implied, no gain), and elliptic-net Somos identities are universal
(hold for every k), so on a single k-fiber they may encode only the group law,
not k (KN-TECH-009). The program's own candidates pose this directly -- RQ-JETB-001
asks whether the dual-number oracle is "simulable with O(1) overhead, closing all
dual-number candidates at exponent 1/2"; RQ-JET-001, RQ-NET-001, and the
incidence line (RQ-INC-001) are instances. Whether any of these representations
is non-simulable over prime fields is unsettled.

## Why it matters here
This is the sharp, reusable screen for the program's "genuine representation
change" candidates: before spending compute, ask whether the new oracle is
GGM-simulable. A simulability proof closes a whole candidate family by theorem
(cheap, decisive); a measured sub-birthday, k-dependent relation supply would be
a genuine non-generic signal. It operationalizes the boundary of KN-OPEN-001 for
representation-based attacks.

## Status 2026-10-24
Scoped closure of the jet branch (DEC-20260722-004) and the chord/incidence branch
(DEC-20260722-006) only, each with the limitations those decisions record.
Still open: the elliptic-net branch. Status field changed from `open` by the
2026-10-24 refutation-propagation audit; nothing above this section was rewritten.
