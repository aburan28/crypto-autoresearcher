---
id: KN-FIND-48f0ae
type: internal_finding
title: >-
  BINSTD toy 1.25 tau/open yield band fails at n=17 and ell 8/9 with
  open-arm saturation under the exhaustive m=3 pin
tags:
  - ecdlp
  - koblitz
  - binary-fields
  - tau-closed
  - frobenius-invariant-fb
  - semaev
  - yield-band
  - ceiling-effect
  - negative-boundary
  - toy-tier
  - binstd
confidence: reported
confidence_note: >-
  Supersedes KN-FIND-0e3ed0 without changing DEC-20261003-62f43b's
  reject_scoped decision. EV-BINSTD-9ac9c5 is replicated toy-tier evidence
  from two seed-specific packages; the reviews were Coordinator-direct and
  no independent elliptic-curve arithmetic oracle is recorded. The extra
  ceiling observation is arithmetic on the same archived hit counts, not a
  new measured result or a confidence upgrade.
evidence_level: toy_tier_two_seed_empirical_yield
source_refs: []
internal_refs:
  - EV-BINSTD-9ac9c5
  - EV-BINSTD-0db227
  - DEC-20261003-62f43b
  - DEC-20261003-637059
  - EXP-BINSTD-8bdf86
  - H-BINSTD-5a212b
  - AMD-EXP-BINSTD-8bdf86-20261003-ell89
  - AMD-EXP-BINSTD-8bdf86-20261003-ell89r1
related_refs:
  - KN-FIND-0e3ed0
  - RQ-BINSTD-b6f698
  - GOAL-ECDLP2M-001
  - IDEA-20261001-0fcbe2
  - EV-BINSTD-3685c4
  - HEUR-BINSTD-0fcbe2-H1
proof_status: empirical_only
proof_refs:
  - experiments/EXP-BINSTD-8bdf86/stage1-ell89/yield-matrix.json
  - experiments/EXP-BINSTD-8bdf86/stage1-ell89r1/yield-matrix.json
  - experiments/EXP-BINSTD-8bdf86/RESULTS-ell89.md
  - experiments/EXP-BINSTD-8bdf86/RESULTS-ell89r1.md
  - experiments/EXP-BINSTD-8bdf86/analysis-ell89.md
  - experiments/EXP-BINSTD-8bdf86/analysis-ell89r1.md
  - ledger/evidence/EV-BINSTD-0db227.yaml
  - ledger/evidence/EV-BINSTD-9ac9c5.yaml
proof_status_note: >-
  The band failure is based on empirical hit counts under the frozen
  exhaustive m=3 toy pin. The ceiling statement follows from those counts:
  each open arm hit 40/40 targets, while a tau success rate cannot exceed 1.
  Neither fact is a Lean proof or an ECDLP attack certificate.
added: '2026-10-22'
superseded_by: null
---

# Scoped BINSTD yield-band failure with an observed open-arm ceiling

This entry supersedes `KN-FIND-0e3ed0`. It preserves the existing
`reject_scoped` reading in `DEC-20261003-62f43b` and removes an internal
reference to `TASK-20261003-6e0c8a`, which was never filed as a handoff.
No dispatch record has been created. The archived original remains unchanged;
the effective superseded copy and both SHA-256 pins are registered in
`tools/schema_supersession_registry.yaml`.

## Exact observed scope

Toy Koblitz `Y^2+XY=X^3+1` over `F_2[t]/(t^17+t^3+1)`, admissible
Frobenius-invariant dimensions `ell` 8 and 9, 40 matched random targets per
cell, frozen band 1.25, and solver pin
`exhaustive_fb_sum_m3_stdlib_gf2`. Stage 2 and larger fields are outside
these packages.

| Panel / Stage-1 run | Seed | ell | Tau hits | Open hits | Derived tau/open ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| ell89 / `RUN-BINSTD-43abd4` | 9049049433885666 | 8 | 16/40 | 40/40 | 0.4 |
| ell89 / `RUN-BINSTD-43abd4` | 9049049433885666 | 9 | 40/40 | 40/40 | 1.0 |
| ell89r1 / `RUN-BINSTD-a2a24c` | 8999122336642658 | 8 | 20/40 | 40/40 | 0.5 |
| ell89r1 / `RUN-BINSTD-a2a24c` | 8999122336642658 | 9 | 40/40 | 40/40 | 1.0 |

Each measured ratio is below 1.25, as recorded by both evidence records.
This is the exact toy band rejected by `DEC-20261003-62f43b`; it does not
reject tau-closed factor bases or transfer to another solver pin.

## Ceiling interpretation

The observed open success rate is `40/40 = 1` in all four cells. A tau
success rate is at most 1, so `R_tau / R_open <= 1 < 1.25` on those measured
cells. The band could not be met **given the observed open-arm saturation**.
This limits causal interpretation of the toy comparison: the cells record a
failed pre-registered band, but do not by themselves show that tau geometry
would underperform under a non-saturated open arm or another pin. The ell=9
arms tied at 40/40; the ell=8 tau arms had fewer hits.

## Limits

Confidence remains `reported` and proof status remains `empirical_only`.
There is no independently implemented elliptic-curve group law in these
records, no Lean proof of the run output, no per-target archived oracle, and
no claim of a discrete-log break, exponent improvement, deployed-curve
weakness, `n>=131` transfer, or rho competitiveness. The two packages use
distinct seeds under the same toy computation. The structural absence of
tau-closed dimensions 3 and 4 belongs to `EV-BINSTD-3685c4`, a separate
scope, and Stage 2 with those dimensions remains unauthorized.
