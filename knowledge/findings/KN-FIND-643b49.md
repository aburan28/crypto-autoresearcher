---
id: KN-FIND-643b49
type: internal_finding
title: >-
  Usable-dimensions emptiness gate holds at stub odd primes when
  ord_n(2)=n-1 (HEUR-BINSTD-11aa69-H1): Stages 0-1 E-GATE-HOLDS on
  |F|=12 / |C|=4 plus Stage-2 independent pow-only re-derive
  S2-REPLICATE-AGREE on {11,13,19} — no break, no exponent, no n>=131
  security transfer
tags:
  - ecdlp
  - binary-fields
  - usable-dimensions
  - emptiness-gate
  - ord-n-2
  - instrument
  - toy-tier
  - binstd
  - internal-finding
confidence: reported
confidence_note: >-
  Promoted from EV-BINSTD-8a1bbf (strength replicated, with prior
  EV-BINSTD-93aee1) under DEC-20261003-31466e. Stage-2 independent
  re-derive covers the protocol's first 3 of 12 forced-negatives only;
  Coordinator-direct review (no independent validator/red-team).
  Confidence is `reported` at toy tier — not `established` for any
  deployed curve or n>=131 security claim.
evidence_level: toy_tier_stage2_independent_rederive
source_refs: []
internal_refs:
  - EV-BINSTD-8a1bbf
  - EV-BINSTD-93aee1
  - DEC-20261003-31466e
  - DEC-20261003-947da5
  - EXP-BINSTD-27f623
  - H-BINSTD-b1f016
  - TASK-20261003-a5bab8
related_refs:
  - RQ-BINSTD-b6f698
  - GOAL-ECDLP2M-001
  - IDEA-20261001-11aa69
  - DEC-20261003-6d20b7
  - DEC-20261003-e9b17b
  - EXP-BINSTD-178742
  - EV-BINSTD-fba851
sibling_findings_narrowed: []
sibling_findings_note: >-
  Instrument gate finding for Part-1 usable_dimensions emptiness when
  ord_n(2)=n-1. Distinct from HOLD-R/HOLD-S equivariance findings
  (KN-FIND-316d09, KN-FIND-b69b8e). Does not supersede EV-BINSTD-fba851
  observational n=131/163 empty usable notes.
proof_status: empirical_only
proof_refs:
  - experiments/EXP-BINSTD-27f623/stage2/independent-rederive.json
  - experiments/EXP-BINSTD-27f623/stage1/census-matrix.json
  - experiments/EXP-BINSTD-27f623/stage0/frozen-panels.json
  - experiments/EXP-BINSTD-27f623/analysis.md
  - ledger/evidence/EV-BINSTD-8a1bbf.yaml
  - ledger/evidence/EV-BINSTD-93aee1.yaml
proof_status_note: >-
  Instrument / observational. certificate.kind=none on all runs. Blind
  ord_n(2) re-derivation agrees on Stage-2 members. No discrete_log /
  decomposition / key_recovery claim.
added: '2026-10-03'
superseded_by: null
---

# Stub-scale usable-emptiness gate (HEUR-BINSTD-11aa69-H1)

## Scoped claim

At the frozen EXP-BINSTD-27f623 / H-BINSTD-b1f016 instrument cells:

- **Stages 0–1** (`EV-BINSTD-93aee1`): Stage-0 freeze of forced-negative
  panel F (`|F|=12`, each `ord_n(2)=n−1`) and positive panel C (`|C|=4`,
  each `ord_n(2)<n−1`); Stage-1 Part-1 dual-route census with synthetic
  non-empty injection null → **E-GATE-HOLDS**
  (`empty_usable_rate=1.0`, `injection_catch=1.0`,
  `positive_nonempty=4`, `route_agreement=1.0`).
- **Stage 2** (`EV-BINSTD-8a1bbf` / `RUN-BINSTD-d15ac1`): independent
  pow-only divisor-ladder re-derive of `ord_n(2)` on the first 3
  Stage-0 forced-negatives `{11,13,19}` that does not call Stage-1
  `score_ord_row` → **S2-REPLICATE-AGREE** (all rates `1.0`).

the program supports HEUR-BINSTD-11aa69-H1 as a **stub/toy instrument
claim only**.

## Explicit non-claims

- No break, exponent-moving, or deployed insecurity claim.
- No transfer of stub gate rates to a security claim about `n≥131`.
- Stage-2 independent re-derive does **not** cover the remaining 9
  members of F under this contract.
- Empty usable ≠ a security property of any curve.

## Provenance

Promoted under `DEC-20261003-31466e` from `EV-BINSTD-8a1bbf` (strength
`replicated`) citing prior `EV-BINSTD-93aee1` / `DEC-20261003-947da5`.
Amazon Bedrock was not selected, configured, probed, contacted, or used.
