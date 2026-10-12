---
id: KN-FIND-b69b8e
type: internal_finding
title: >-
  Fixed-target tau-orbit CNF clauses are unsound at the HOLD-S toy cell
  n=17 m=2 l=8 on a tau-stable V: exhaustive census over four seeds
  (800 eligible targets) measures closure_fraction=0,
  conjugate_overlap=0, equivariance_agreement=1.0 (a77711 A1/A2 null);
  mid-dimension tau-stable lanes are empty on n in {163,29,37}; H2
  |x(E)∩V| direct=per-orbit count agreement is preprocessing-only —
  no deployed break or exponent claim
tags:
  - ecdlp
  - koblitz
  - frobenius
  - orbit-clauses
  - soundness
  - hold-s
  - a77711
  - toy-tier
  - negative-boundary
  - binary-fields
confidence: reported
confidence_note: >-
  Promoted from EV-BINSTD-a816da (strength replicated) under
  DEC-20261001-e045af. Seed-replicated exhaustive census within one
  frozen protocol and Coordinator-direct review (no independent
  validator/red-team). Confidence is `reported` at toy tier — not
  `established` for any deployed curve.
evidence_level: toy_tier_multi_seed_exhaustive_census
source_refs: []
internal_refs:
  - EV-BINSTD-a816da
  - DEC-20261001-e045af
  - EXP-BINSTD-38e4ad
  - H-BINSTD-c3d68f
  - TASK-20261001-b78ef3
related_refs:
  - RQ-BINSTD-b6f698
  - GOAL-ECDLP2M-001
  - IDEA-20260922-2a3771
  - IDEA-20260906-a77711
  - KN-FIND-47da4e
  - DEC-20261001-6a7a25
sibling_findings_narrowed: []
sibling_findings_note: >-
  Distinct from KN-FIND-47da4e (sound orbit-system WDSat conflict ratios).
  This finding is the fixed-target / single-instance unsoundness census
  and empty mid-lane lattice certificate under HOLD-S.
proof_status: empirical_only
proof_refs:
  - experiments/EXP-BINSTD-38e4ad/stage1/soundness-census.yaml
  - experiments/EXP-BINSTD-38e4ad/stage0/lattice.yaml
  - experiments/EXP-BINSTD-38e4ad/analysis.md
  - ledger/evidence/EV-BINSTD-a816da.yaml
proof_status_note: >-
  Empirical exhaustive census confirming a77711 A1/A2 at one toy cell,
  plus derivation-checkable ord_n(2) lattice empties. certificate.kind=none
  on all runs — no solve/relation claim.
added: '2026-10-01'
superseded_by: null
---

# Fixed-target Frobenius orbit clauses fail the HOLD-S soundness census

## Scoped claim

At the frozen toy cell `n=17`, `m=2`, `l=8` on the Koblitz-shaped curve
`y^2+xy=x^3+x^2+1` over `F_2[t]/(t^17+t^3+1)`, with `V=ker f1(tau)` of
dimension 8 verified tau-stable, an exhaustive unordered-pair census over
four target-draw seeds (`2026100117`–`2026100120`, 800 eligible prime-order
targets with `sigma(R)≠±R`) measured:

- `closure_fraction = 0`
- `conjugate_overlap = 0`
- `equivariance_agreement = 1.0`

This is the pre-registered null of `HEUR-BINSTD-c3d68f-H1` /
`DO-1-null-confirms-HOLD-S`: coordinate squaring maps solutions of one
fixed-target instance into the conjugate instance (a77711 Lemma A1), and
solution sets of `R` and `sigma(R)` are disjoint when `sigma(R)≠±R`
(Lemma A2). Adding tau-orbit-equivalence / canonical-representative clauses
to a **single** fixed-target CNF is therefore **unsound** at this cell —
it drops solutions rather than ranging over orbit classes of one instance.

Stage 0 recomputed `ord_n(2)` and marked mid-dimension tau-stable lanes
**empty** (and forbidden as measurement cells) for `n ∈ {163,29,37}`.
Stage 2 controls held polarity: random non-stable `V'` had
`leave_Vprime_fraction ≈ 0.992`; an ordinary curve with `b∉F_2` had
`equivariance_agreement = 0`; on the tau-stable `V`,
`|x(E)∩V|` direct count equalled the per-orbit sum (`103=103`) —
preprocessing-only, not an exponent lever.

## What this does not claim

- No deployed-curve break, attack, or security-ordering statement.
- No transfer of the null to `n≥131` or other `(n,m,l)` without new evidence.
- No satisfiability-preserving reading of fixed-target orbit clauses.
- No exponent-class or K-163-vs-rho claim.
- No WDSat conflict-ratio re-measurement (KN-FIND-47da4e remains a separate
  prior on the *sound* orbit-system encoding).

## Provenance

Promoted under Coordinator decision `DEC-20261001-e045af` from evidence
`EV-BINSTD-a816da` (experiment `EXP-BINSTD-38e4ad`, hypothesis
`H-BINSTD-c3d68f`, producer `TASK-20261001-b78ef3`). Cited runs:
`RUN-BINSTD-f9fb37`, `b50f23`, `099730`, `1d2240`, `06a5e0`, `46f8b5`,
`1041c0`, `a1c040`.
