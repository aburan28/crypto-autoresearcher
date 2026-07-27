---
id: KN-FIND-006
type: finding
title: >-
  Adversarial survey of the Pollard-rho frontier finds no live generic speedup:
  0 live, 9 capped, 17 dead across six lenses — only constant-factor engineering
  remains on the baseline
tags: [pollard-rho, baseline, generic, distinguished-points, negation-map, survey, lower-bound, ecdlp, negative-result, external-corpus]
confidence: reported
status: established
source_refs: [KN-OPEN-001, KN-TECH-001, KN-TECH-006, KN-TECH-018, KN-TECH-005, KN-LIT-008, KN-LIT-012, KN-LIT-011]
added: 2026-07-26
superseded_by: null
---

## Finding

A six-lens adversarial survey of proposed improvements to the Pollard-rho
baseline classified every candidate as **LIVE = 0, capped = 9, dead = 17**.

No generic speedup survives: every candidate either (a) is already absorbed by the
known constant-factor toolkit — negation map, distinguished points, parallel
collision search (KN-TECH-006, KN-TECH-018) — or (b) fails outright. What remains
on the baseline is **constant-factor engineering and honest measurement**, not
exponent improvement, which is exactly what the generic-group lower bound
(KN-TECH-005, KN-LIT-011) predicts.

This matters for KN-OPEN-001's accounting side: the denominator in
"does index calculus beat rho?" is **not** going to move by an exponent, so any
index-calculus claim must beat a baseline whose exponent is fixed at 1/2 and whose
constants are already well optimized. The identified next measurements are
joules-per-step and a negation-ON bitsliced implementation on ecc2k130 — i.e.
cost-model refinement, not algorithmic advance.

## Scope and limitations

- **External-corpus provenance.** Produced in a separate workspace
  (`/Volumes/Volume/research/POLLARD_RHO_FRONTIER.md`), *not* under this repo's
  ledger or run-receipt discipline; not Coordinator-approved evidence here.
- It is a **survey with adversarial screening**, not an execution campaign: the
  dispositions are argued, cited classifications, and the "dead" verdicts close
  only the exact stated mechanism boundaries.
- "capped" means the candidate is real but bounded by a known constant-factor
  ceiling; it does not mean the constant is worthless in practice (a 2x matters
  for a record attempt, and is the correct baseline to benchmark against).
- Related operational context: a detached 96-bit rho attempt in the external
  corpus reached ~7.2% of expected work before being stopped, illustrating the
  practical cost of the baseline at that size — that run produced no solve and is
  not evidence about the algorithm's exponent.

## Evidence

- External: `/Volumes/Volume/research/POLLARD_RHO_FRONTIER.md` (six-lens survey,
  26 classified candidates).
- External operational: `/Volumes/Volume/research/ecdlp-cost-challenge/research/rho96/`
  (checkpointed 96-bit attempt, stopped at ~7.2%, `solved 0`).
