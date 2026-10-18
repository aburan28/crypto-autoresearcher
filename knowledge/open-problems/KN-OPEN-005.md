---
id: KN-OPEN-005
type: open_problem
title: Is a non-generic ECDLP representation (jets, elliptic nets, incidence reporting) generic-group-model simulable, or can it supply k-dependent relations below the birthday bound?
tags: [generic-group-model, birthday, jets, elliptic-nets, incidence, representation, prime-field, ecdlp, open]
confidence: reported
status: open
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

## Reconciliation note, 2026-10-18 (appended; the entry above is unchanged)

Register status stays `open`. DEC-20260804-4f37d5 records `kn_open_005_disposition: PARTIALLY_ADDRESSED ... technically open (no existence proof one way or another)`. That is a Coordinator disposition of `open`.

Premise check: the request that prompted this note cited DEC-20260722-003..006 as the proving decisions. They are not: DEC-20260722-003 targets GOAL-MLKEM-001/IDEA-20260722-001, -004 and -005 target GOAL-ECDLP-001 BATCH-002 task handling, and no DEC-20260722-006 exists. The records that do bear on this problem are below.

- DEC-20260804-4f37d5: no publicly computable non-simulable oracle found among five analysed types; the formal-group route reduces to Smart's attack (anomalous curves only). `official_research_state_changed: false`.
- DEC-20260723-006 (BATCH-007 GGM-simulability screen): `revise`; scoped no-distinct-unaudited-family disposition, not a classification theorem.
- H-GGM-001 `analyzed`; EV-JET-001 (`contradicts`, preliminary), EV-JETB-001 (`supports`, preliminary, toy p <= 431), EV-NET-001 (`weakens`, preliminary): jets and elliptic nets screened at toy scale only.
- The owed promotion `pending_kn_find_oracle_obstruction` in DEC-20260804-4f37d5 was never made as a KN-FIND entry.

Decision request: `coordination/remediation/DECISION-REQUEST-20261018-ic-integrity.md`, item R-3.
