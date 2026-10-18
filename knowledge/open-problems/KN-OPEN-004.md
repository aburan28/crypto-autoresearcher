---
id: KN-OPEN-004
type: open_problem
title: Does support-aware (BKK / mixed-volume) elimination undercut dense resultants for prime-field Semaev systems, and at what m does Newton saturation set in?
tags: [bkk, mixed-volume, newton-polytope, semaev, sparse-elimination, prime-field, groebner, open]
confidence: reported
status: open
source_refs: [KN-LIT-014, KN-LIT-015, KN-TECH-007, KN-OPEN-002]
added: 2026-07-21
superseded_by: null
---

## Statement
For the target-sectioned Semaev summation family S_m(x_1,...,x_{m-1}; x_R) over
prime fields, are the Newton polytopes proper subpolytopes of their degree box,
so that the mixed volume MV is strictly below the Bezout bound -- making
support-aware (sparse-resultant / polyhedral) elimination asymptotically cheaper
than dense composed resultants -- or are they Newton-saturated (MV = Bezout),
in which case sparse == dense? If MV < Bezout, does the gap MV/Bezout persist
(and shrink) as m grows?

## Current state (as reported)
BKK/mixed-volume theory (KN-LIT-014, KN-LIT-015, KN-TECH-007) is standard, but
the Newton polytopes of the Semaev family had apparently never been computed.
The program's toy-scale BKK experiments (RQ-BKK-001, RQ-BKKMV-001; hypotheses
H-BKK-001 / H-BKKMV-001) measured this at m <= 5 over toy primes and returned a
SCOPED NEGATIVE (Newton saturation / no support-aware advantage at reachable m).
By rule 6, that closes only the tested scope: the asymptotic-m behavior and
whether any curve family gives a proper subpolytope remain open, and a
saturation proof for all m would be a theorem the program does not yet have.

## Why it matters here
It is decidable in both directions at small scale (compute exact supports, MV,
and brute-force F_p solution counts), so it is a high-value stage-0 gate: a
persistent MV/Bezout < 1 would change the complexity driver of point
decomposition (KN-OPEN-002) from degree to mixed volume; a saturation theorem
kills the whole BKK route cheaply. Either outcome tightens the prime-field
index-calculus picture (KN-OPEN-001) without over-claiming from toy scale.

## Reconciliation note, 2026-10-18 (appended; the entry above is unchanged)

Register status stays `open`. The recorded results are toy-scale scoped negatives (m <= 5, p <= 1009); this entry's own text says asymptotic m and curve families remain open, and no saturation theorem is on record.

Premise check: the request that prompted this note cited DEC-20260722-003..006 as the proving decisions. They are not: DEC-20260722-003 targets GOAL-MLKEM-001/IDEA-20260722-001, -004 and -005 target GOAL-ECDLP-001 BATCH-002 task handling, and no DEC-20260722-006 exists. The records that do bear on this problem are below.

- EV-BKK-001 (H-BKK-001, `contradicts`, `replicated`): toy primes {101, 431, 1009}, m in {3,4,5}; closes only the tested scope.
- EV-BKKMV-001, EV-BKKMV-002 (H-BKKMV-001, `neutral`, `replicated`): mixed volume equals the box Bezout bound at the tested m; certification at p ~ 2^20, m <= 4.
- DEC-20260723-007 (BATCH-008 Newton screen): `revise`; conditional negative proof gate, next action a normalization-locked proof packet before any knowledge promotion. No such packet is committed under this id.
- DEC-20260804-139a86 (survey) lists this problem as "Addressed - MV = box Bezout (H-BKKMV-001 supported)". That decision's `knowledge_promotion.promoted` names only KN-FIND-e7a3b1 and KN-FIND-f8c290; it closes no KN-OPEN entry. The hypothesis files H-BKK-001 and H-BKKMV-001 were not found under `ledger/hypotheses/` in this checkout.
- Closure needs a Coordinator decision whose `knowledge_promotion` authorizes it, or a saturation theorem.

Decision request: `coordination/remediation/DECISION-REQUEST-20261018-ic-integrity.md`, item R-3.
