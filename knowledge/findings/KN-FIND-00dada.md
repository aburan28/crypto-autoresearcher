---
id: KN-FIND-00dada
type: internal_finding
title: >-
  HOLD-X7 H1 spurious-factor factor-4 band fails at RC-1 n=17 m=3 scored
  l in {5,6}: two independent sampled e-space packages (seeds 2026092731
  and 2026100391 with 4× denser budgets) measure ratios ≈0.139/0.0 and
  ≈0.069/0.0 outside [1/4,4] with lift_agreement=1.0; P4 null holds;
  dimension certificate (A) stands — no deployed break or exponent claim
tags:
  - ecdlp
  - binary-fields
  - subspace-descent
  - symmetrisation
  - spurious-lift
  - hold-x7
  - toy-tier
  - negative-boundary
  - replicated
confidence: reported
confidence_note: >-
  Promoted from EV-BINSTD-f9c882 (strength replicated) under
  DEC-20261003-adddf4, citing prior weaken package EV-BINSTD-2f89cc.
  Two independent seeds within one frozen pin; Coordinator-direct review
  (no independent validator/red-team). Confidence is `reported` at toy
  tier — not `established` for any deployed curve.
evidence_level: toy_tier_two_seed_sampled_e_space
source_refs: []
internal_refs:
  - EV-BINSTD-f9c882
  - EV-BINSTD-2f89cc
  - DEC-20261003-adddf4
  - DEC-20261003-ef74c5
  - EXP-BINSTD-591d28
  - H-BINSTD-5fdceb
  - RUN-BINSTD-2b5b2c
  - RUN-BINSTD-453b8d
  - RUN-BINSTD-d4a2b8
  - RUN-BINSTD-3849a9
related_refs:
  - RQ-BINSTD-b6f698
  - GOAL-ECDLP2M-001
  - IDEA-20260926-120d6a
  - EV-BINSTD-f0a4ab
  - DEC-20261003-d4e5ea
sibling_findings_narrowed: []
sibling_findings_note: >-
  Distinct from EV-BINSTD-f0a4ab's Stage-0/1 dimension certificate (A),
  which this finding does not overturn. This finding is only the
  replicated H1 / clause (C) band miss at scored toy cells.
proof_status: empirical_only
proof_refs:
  - experiments/EXP-BINSTD-591d28/RESULTS-stages2-3-repl.md
  - experiments/EXP-BINSTD-591d28/RESULTS-stages2-3.md
  - experiments/EXP-BINSTD-591d28/stage2-repl/p1-fillin-summary.json
  - experiments/EXP-BINSTD-591d28/stage3-repl/p4-comparison.json
  - experiments/EXP-BINSTD-591d28/analysis-stages2-3-repl.md
  - ledger/evidence/EV-BINSTD-f9c882.yaml
  - ledger/evidence/EV-BINSTD-2f89cc.yaml
proof_status_note: >-
  Replicated empirical sampled e-space estimators; no counterexample
  certificate. certificate.kind=none on all runs — no solve/relation claim.
added: '2026-10-03'
superseded_by: null
---

# HOLD-X7 H1 factor-4 band fails at RC-1 scored cells

## Scoped claim

At the frozen RC-1 toy setting `n=17`, `m=3`, polynomial-basis subspace
`V=span{1,z,...,z^{l-1}}`, two independent Stages 2–3 packages under
`EXP-BINSTD-591d28` / `H-BINSTD-5fdceb` measured the sampled e-space
spurious factor `(estimated e-solutions)/(genuine V^m decompositions)`
outside the preregistered factor-4 band of
`m! · 2^{∑_k dim V^{(k)} − ml}` at scored `l∈{5,6}`:

| package | seed | l=5 ratio | l=6 ratio |
| --- | --- | --- | --- |
| EV-BINSTD-2f89cc (d4a2b8/3849a9) | 2026092731 | ≈0.1389 | 0.0 |
| EV-BINSTD-f9c882 (2b5b2c/453b8d) | 2026100391 (4× denser) | ≈0.0694 | 0.0 |

Both packages report `lift_agreement_stage1=1.0`, `p4_null_holds=true`,
and producer outcome `O-NEGATIVE`. `l=4` remains unscored (zero genuine)
in both packages and is **not** part of this boundary.

## What this does not claim

- It does **not** overturn the Stage-0/1 dimension certificate (A)
  recorded in `EV-BINSTD-f0a4ab`.
- It does **not** transfer to `n=131` balanced cells, any deployed curve,
  or any ECDLP exponent.
- It does **not** assert a closed-form refutation of the factor formula —
  `proof_status: empirical_only`.

## Provenance

Promoted under `DEC-20261003-adddf4` (`reject_scoped`, strength
`replicated`) from `EV-BINSTD-f9c882`, which replicates the prior weaken
package `EV-BINSTD-2f89cc` / `DEC-20261003-ef74c5`. Amazon Bedrock was
not selected, configured, probed, contacted, or used.
