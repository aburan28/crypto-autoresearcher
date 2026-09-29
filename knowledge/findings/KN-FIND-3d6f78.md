---
id: KN-FIND-3d6f78
type: internal_finding
title: Defect-scaled hyperplane-signature zero-minor ECDLP route is closed as non-sub-rho under its own pinned published model (d=1, replicated derivation)
tags: [hzm, zero-minor, hyperplane-signature, guess-and-determine, cost-gate, non-sub-rho, scoped-negative, ecdlp, derivation]
confidence: replicated_derivation
evidence_level: toy_demonstration
source_refs: [BATCH-98edec, EV-CRYPTO-ad7fa2, DEC-20260908-1d04cc]
internal_refs: [EV-CRYPTO-ad7fa2, DEC-20260908-1d04cc, DEC-20260907-5b500d, RUN-HZM-001-c-primary-gate-only, H-HZM-001, EXP-HZM-001]
proof_status: derivation
proof_refs:
  - experiments/EXP-HZM-001/refutation-note-primary-gate-20260908.md
  - coordination/goals/GOAL-CRYPTO-001/batches/BATCH-98edec/reviews/TASK-20260908-422afa/blind-rederivation.yaml
review_chain_note: >-
  Review records cited by path in the body (validator record index
  does not cover them): red-team RT-20260908-5d29c2 at
  coordination/goals/GOAL-CRYPTO-001/batches/BATCH-98edec/reviews/TASK-20260908-5d29c2/red-team-report.yaml;
  inherited validator VAL-20260907-612101 at
  experiments/EXP-HZM-001/reviews/validator-primary-gate/report.yaml.
added: '2026-09-08'
superseded_by: null
---

## Finding

Under its own pinned published formulas — q(N,L,d) = 1-(1-1/N)^M,
M = binom(L+d,d), H = binom(L+d,d-1), charged expected per-target
work >= H/q + omitted stages (Mahalanobis, arXiv:2607.09814v1 as
quoted in the immutable TASK-20260723-301 snapshot; mechanism prior
art INDOCRYPT 2018 / arXiv:2310.04132) — the defect-scaled
hyperplane-signature zero-minor ECDLP route FAILS the frozen sub-rho
cost gate at d=1:

- Exact gate characterization (blind-derived, machine-checked): with
  m = L+1 and s = ceil(sqrt(N)), charged >= s  <=>  s(N-1)^m >=
  (s-1)N^m. Holds at both primary gate points with huge slack
  (s*m <= (s-1)^2: 832 <= 3969 and 4352 <= 65025).
- (N=4096, L=12, d=1): charged = 2^156/(2^156-4095^13) ~= 315.54 vs
  rho bound 64 (ratio 4.93). (N=65536, L=16, d=1): charged =
  2^272/(2^272-65535^17) ~= 3855.53 vs 256 (ratio 15.06).
  survives_rho_gate = False at both.
- Bernoulli bound: charged >= N/(L+1); for L = Theta(log N) this is
  N^(1-o(1)) > N^(1/2) for all sufficiently large N — conditional
  algebra under the pinned formulas, not a measurement.
- The result is base-invariant at d=1 (H = binom(L+1,0) = 1 for any
  base), so the manuscript's unresolved l-vs-l' ambiguity cannot
  affect it; even the most route-favorable base-2L reading of M fails
  both gates (164.32 vs 64; 1986.42 vs 256).
- Controls: passing-point (64,16,1) survives (4.2575 < 8) — the
  machinery is not constant-false; q-bound sensitivity confirms the
  exact formula; five independent derivations/reproductions agree
  (producer, Coordinator, validator RECOMP-1/2/3, blind exact-rational,
  red-team re-execution).

## Significance

- A proven scoped negative (promoted like a positive per the standing
  gate): the pre-registered falsification_criterion(b) of
  EXP-HZM-001 fired exactly as the prior static audit expected. The
  zero-minor route, as modeled by its own published formulas, offers
  no sub-rho path at d=1.
- Durable boundary for ideation and novelty checks: any proposal
  routing through EXPLICIT defect-signature enumeration carries this
  H/q bottleneck as its floor; Gray-code/rank-one updates shave only
  polylog factors and cannot erase it.
- Resource reading (EV obstruction.resource_check): the obstruction is
  the hypothesis of relation-structure-first approaches — viable
  routes must replace enumeration with structured relation discovery
  (the premise of the program's Semaev/index-calculus lanes,
  EV-CRYPTO-009 / EV-CRYPTO-3374a2).

## Boundaries

- Closes EXACTLY: gate survival at d=1 under the pinned published
  formulas at the two primary gate sizes, plus the conditional-algebra
  statement for L = Theta(log N) under the same formulas (rule 6).
- Does NOT close: the general d in {2,3} manuscript-alignment question
  (l-vs-l' base ambiguity live; inconclusive_misalignment stands); the
  enumeration leg (factor-of-2 realization untested, moot for gate
  survival); external-publication correctness beyond the pinned model;
  any standardized curve. No sub-rho route is certified by this
  finding.
- The asymptotic statement is conditional algebra from the pinned
  formulas (spec scale_relevance), not a toy measurement; HEUR-001's
  occupancy law was the model under audit, not a validated theorem.
- Precision: committed floats are float64-pipeline values (10/588 ulp
  from correctly-rounded exact doubles); the exact rationals are the
  load-bearing values; verdict-insensitive at 4.93x/15.06x margins.
