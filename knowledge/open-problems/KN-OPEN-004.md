---
id: KN-OPEN-004
type: open_problem
title: Does support-aware (BKK / mixed-volume) elimination undercut dense resultants for prime-field Semaev systems, and at what m does Newton saturation set in?
tags: [bkk, mixed-volume, newton-polytope, semaev, sparse-elimination, prime-field, groebner, open]
confidence: reported
status: closed_scoped
closed_scoped_at: '2026-10-24'
closed_scoped_by: [DEC-20260722-003]
closed_scoped_as: >-
  CLOSED AT m <= 5 ONLY. DEC-20260722-003 records the box-saturation theorem
  (MV = box Bezout) as PROVED at m <= 5 (THM_BKKMV1) and the m = 6 mixed-volume
  certified on 6/6 instances (EXP-BKKMV-002). The sparse-elimination barrier is
  theorem-backed at those m.
still_open_in:
  - >-
    THE ALL-m LAW. DEC-20260722-003 reduces it to one explicit open gap, the
    interior-fiber non-cancellation lemma; no all-m saturation proof is recorded.
  - >-
    EVEN-m t = 0 SECTIONS are proved never saturated; this is a separate structure
    not covered by the closure.
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

## Status 2026-10-24
Scoped closure only, per DEC-20260722-003 (evidence EV-BKKMV-002; research/THM_BKKMV1.md).
Closed: the question at m <= 5, with m = 6 certified. Still open: the all-m
saturation law (interior-fiber non-cancellation lemma). Status field changed
from `open` by the 2026-10-24 refutation-propagation audit; nothing above this
section was rewritten.
