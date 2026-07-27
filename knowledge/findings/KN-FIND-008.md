---
id: KN-FIND-008
type: finding
title: >-
  Semaev solving complexity is an isogeny-class invariant: 3 of 4 channels null,
  and alpha-stable factor bases enrich relation yield 7-16x without lowering the
  per-relation solving degree
tags: [semaev, isogeny, isogeny-class, index-calculus, factor-base, solving-degree, groebner, symmetry, prime-field, ecdlp, negative-result, external-corpus]
confidence: reported
status: established
source_refs: [KN-OPEN-003, KN-OPEN-002, KN-TECH-002, KN-TECH-003, KN-TECH-024, KN-TECH-028]
added: 2026-07-26
superseded_by: null
---

## Finding

A four-channel sweep testing whether isogeny structure can cheapen Semaev
index calculus returned **three nulls and one carefully-bounded positive**:

- **C1, C3, C4: NULL.** Semaev solving complexity behaves as an **isogeny-class
  invariant** — walking to an isogenous curve does not move it. Choosing a
  "better" curve within an isogeny class is not a lever.
- **C2: enrichment YES, cheaper solving NO.** An alpha-stable factor base
  (FHJRV-style symmetrization applied to alpha) genuinely **enriches relation
  yield 7-16x**, but does **not** lower the per-relation solving degree:
  at n = 10 the solving-degree experiment found `corr(vsdim, gb) ~ 0.94` with a
  matched difference of ~0. More relations per unit search, same cost per
  relation.

The practical consequence is that the only surviving benefit is the orbit-folding
constant quantified in [KN-FIND-007](KN-FIND-007.md) (bounded 3-6), and the
apparent large seed-efficiency gain seen in the pilot did not survive honest
collection accounting.

Together with KN-FIND-007 this closes the isogeny/symmetry lane of KN-OPEN-003
for prime fields at the level tested: symmetry moves constants, not exponents.

## Scope and limitations

- **External-corpus provenance.** Produced in a separate workspace
  (`/Volumes/Volume/research/isogeny-semaev/`, review write-up
  `ISOGENY_SEMAEV_REVIEW.md`), *not* under this repo's ledger or run-receipt
  discipline, and not re-run under this harness. Not Coordinator-approved evidence
  here.
- The C2 solving-degree comparison is at n = 10 — a single toy size. "No
  reduction" is a matched-comparison result at that size, not an asymptotic claim.
- The folding route requires a D = 5 mod 8 prime-order curve; outside that class
  the construction was not exercised.
- A null channel closes only the exact tested boundary (per this program's
  interpretation rule): it does not prove no isogeny-based mechanism can exist,
  only that these four channels showed no effect.

## Evidence

- External: `/Volumes/Volume/research/ISOGENY_SEMAEV_REVIEW.md` and
  `/Volumes/Volume/research/isogeny-semaev/` (`RESULTS_PILOT.md`; experiments
  E2_solvedeg for the solving-degree null, E2_rankgranularity for the
  rank-granularity/folding arm).
- Companion: [KN-FIND-007](KN-FIND-007.md) (bounded-constant scaling verdict that
  superseded the pilot's apparent ~30x).
