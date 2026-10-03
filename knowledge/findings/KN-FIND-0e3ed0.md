---
id: KN-FIND-0e3ed0
type: internal_finding
title: >-
  HEUR-BINSTD-0fcbe2-H1 ≥1.25 τ-closed vs open Semaev m=3 yield band fails
  at toy Koblitz n=17 / ℓ∈{8,9} under exhaustive_fb_sum_m3_stdlib_gf2 on two
  independent seeds (ell89 ratios 0.4/1.0; ell89r1 ratios 0.5/1.0) —
  E-TAU-NOT-RICHER; no Stage 2 with ℓ∈{3,4}; no break / exponent / n≥131 claim
tags:
  - ecdlp
  - koblitz
  - binary-fields
  - tau-closed
  - frobenius-invariant-fb
  - semaev
  - yield-band
  - negative-boundary
  - toy-tier
  - binstd
  - 8bdf86
  - 0fcbe2
confidence: reported
confidence_note: >-
  Promoted from EV-BINSTD-9ac9c5 (strength replicated) under
  DEC-20261003-62f43b, citing prior EV-BINSTD-0db227. Two independent
  Stage 0–1 packages with distinct seeds agree on E-TAU-NOT-RICHER at
  both admissible cells. Coordinator-direct review (no independent
  validator/red-team). Confidence is `reported` at toy tier — not
  `established` for any deployed curve or other pin.
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
  - TASK-20261003-6e0c8a
related_refs:
  - RQ-BINSTD-b6f698
  - GOAL-ECDLP2M-001
  - IDEA-20261001-0fcbe2
  - EV-BINSTD-3685c4
  - HEUR-BINSTD-0fcbe2-H1
sibling_findings_narrowed: []
sibling_findings_note: >-
  Distinct from EV-BINSTD-3685c4 / structural E-NO-TAU-CLOSED-AT-ELL at
  ℓ∈{3,4}. This finding is the yield-band failure at admissible
  ℓ∈{8,9}, not structural emptiness.
proof_status: empirical_only
proof_refs:
  - experiments/EXP-BINSTD-8bdf86/stage1-ell89/yield-matrix.json
  - experiments/EXP-BINSTD-8bdf86/stage1-ell89r1/yield-matrix.json
  - experiments/EXP-BINSTD-8bdf86/RESULTS-ell89.md
  - experiments/EXP-BINSTD-8bdf86/RESULTS-ell89r1.md
  - experiments/EXP-BINSTD-8bdf86/analysis-ell89r1.md
  - ledger/evidence/EV-BINSTD-9ac9c5.yaml
  - ledger/evidence/EV-BINSTD-0db227.yaml
proof_status_note: >-
  Band failure rests on empirical hit counts under the admitted
  exhaustive m=3 pin across two seeds. Admissible φ-invariant dims at
  n=17 are derivation-checkable. No discrete_log / key_recovery claim.
added: '2026-10-03'
superseded_by: null
---

# τ-closed ≥1.25 yield band fails at n=17 / ℓ∈{8,9} (exhaustive pin)

## Scoped claim

At toy Koblitz `Y^2+XY=X^3+1` over `F_2[t]/(t^17+t^3+1)`, with factor base
abscissae in an F_2-subspace V, τ-closed meaning φ-invariant, and solver pin
`exhaustive_fb_sum_m3_stdlib_gf2`, on ≥40 matched random targets:

- **Admissible φ-invariant dims at n=17** are `{0,1,8,9,16,17}` (subset sums
  of irreducible degrees `{1,8,8}` of `x^17-1` over F_2).
- For each Stage-0-frozen admissible cell **ℓ∈{8,9}**, measured
  `R_τ / R_open` is **strictly below 1.25** with both arms nonzero
  (`E-TAU-NOT-RICHER`) on **two independent Stage-0 seeds**:
  - ell89 (`AMD-EXP-BINSTD-8bdf86-20261003-ell89`, seed `9049049433885666`):
    ℓ=8 ratio `0.4`, ℓ=9 ratio `1.0` (`RUN-BINSTD-43abd4` /
    `EV-BINSTD-0db227`).
  - ell89r1 (`AMD-EXP-BINSTD-8bdf86-20261003-ell89r1`, seed
    `8999122336642658`): ℓ=8 ratio `0.5`, ℓ=9 ratio `1.0`
    (`RUN-BINSTD-a2a24c` / `EV-BINSTD-9ac9c5`).

Therefore **HEUR-BINSTD-0fcbe2-H1's ≥1.25 τ-closed vs matched-open yield
band is rejected at this exact toy scope** (`DEC-20261003-62f43b`,
`reject_scoped`).

## What this does NOT claim

- No break, discrete-log, exponent, or deployed insecurity claim.
- No transfer to `n∈{23,31}`, `n≥131`, other pins (e.g. XOR-SAT), or
  other admissible dimensions.
- Does not authorize Stage 2 with ℓ∈{3,4}.
- Does not overwrite the structural emptiness reading at ℓ∈{3,4}
  (`EV-BINSTD-3685c4`).
- Does not reject the definition of τ-stable / φ-invariant FB
  (`KR-IC-b0fcda`); only the ≥1.25 success-rate band at the tested cells.

## Resource reading

τ-closed V can be larger in FB size yet not ≥1.25× richer in m=3 hits —
an asset for open-FB preference theories and for pin-sensitivity studies.
Those require new contracts; they do not reopen this band silently.
