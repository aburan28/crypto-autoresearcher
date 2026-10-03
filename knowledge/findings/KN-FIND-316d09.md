---
id: KN-FIND-316d09
type: internal_finding
title: >-
  Absolute Frobenius is equivariance between conjugate targets (not
  per-instance symmetry) at HOLD-R toys n=19/17: certified same_instance_hits=0,
  conjugate_instance_hits=1.0, solutions_lost=11 under single-instance
  shift-canonical constraint; K17 stable-V in_V=1.0; ECC2K-130 and K-163
  STRUCTURALLY_EMPTY for orbit-batched V — no leaf-ratio~1/mu, no deployed
  break, no exponent claim
tags:
  - ecdlp
  - koblitz
  - frobenius
  - equivariance
  - unsoundness
  - hold-r
  - a77711
  - toy-tier
  - negative-boundary
  - binary-fields
  - reachability-census
confidence: reported
confidence_note: >-
  Promoted from EV-BINSTD-780165 (strength replicated) under
  DEC-20261001-795812. Multi-arm / multi-seed agreement within one
  frozen protocol and Coordinator-direct review (no independent
  validator/red-team). Confidence is `reported` at toy tier — not
  `established` for any deployed curve. HEUR-H1 free-action median
  band is NOT part of the promoted claim (measured miss disclosed).
evidence_level: toy_tier_multi_arm_certified_census
source_refs: []
internal_refs:
  - EV-BINSTD-780165
  - DEC-20261001-795812
  - EXP-BINSTD-375338
  - H-BINSTD-74b002
  - TASK-20261001-ff051b
related_refs:
  - RQ-BINSTD-b6f698
  - GOAL-ECDLP2M-001
  - IDEA-20260922-7ab503
  - IDEA-20260906-a77711
  - RQ-FROB-7d8dd4
  - DEC-20261001-495bd1
  - KN-FIND-b69b8e
sibling_findings_narrowed: []
sibling_findings_note: >-
  Distinct from KN-FIND-b69b8e (HOLD-S fixed-target tau-orbit CNF
  unsoundness at n=17). This finding is HOLD-R absolute-Frobenius
  equivariance vs per-instance symmetry at q=2, plus EMPTY census for
  ECC2K-130/K-163 on the orbit-batched seam.
proof_status: certificate
proof_refs:
  - experiments/EXP-BINSTD-375338/stage1/certified-decompositions/BIN-TOY-K19-decompositions-RUN-BINSTD-822306.json
  - experiments/EXP-BINSTD-375338/stage0/reachability-table-cells.yaml
  - experiments/EXP-BINSTD-375338/analysis.md
  - ledger/evidence/EV-BINSTD-780165.yaml
proof_status_note: >-
  Stage 1 K19 metrics rest on verified m=2 decomposition certificates
  (85/85). Stage 0 EMPTY cells are derivation-checkable from ord_n(2).
  No discrete_log / key_recovery claim.
added: '2026-10-01'
superseded_by: null
---

# Absolute Frobenius equivariance (not per-instance symmetry) at HOLD-R toys

## Scoped claim

At the frozen HOLD-R Stage 1 cells:

- **BIN-TOY-K19**: Koblitz `y^2+xy=x^3+1` over `F_2[t]/(t^19+t^5+t^2+t+1)`,
  `#E=4·130873` (`l` prime), `m=2`, non-stable `V={deg<10}`, 50 targets
  with certified decompositions (`RUN-BINSTD-822306`);
- **BIN-TOY-K17-STABLE**: Frobenius-stable `V` control (`RUN-BINSTD-d89f6a`);
- **Z/l replica**: five seeds (`RUN-BINSTD-8d5245`);

the program measured:

- `same_instance_hits = 0`
- `conjugate_instance_hits = 1.0`
- `leg_swap_hit_rate = 1.0`
- `solutions_lost_under_canonical_constraint = 11 > 0`
- K17 `shifted_legs_in_V_fraction = 1.0`; K19 `= 0.0`

Stage 0 arithmetic census marks **ECC2K-130** and **K-163**
`STRUCTURALLY_EMPTY` for useful mid-dimension Frobenius-stable `V`
(`ord_131(2)=130`, `ord_163(2)=162`); live rows route to the FROB seam.

This is `DO-1-equivariance-confirmed` / `HEUR-BINSTD-74b002-H0` and the
qualitative half of `HEUR-BINSTD-74b002-H1`: coordinate squaring maps
solutions of one instance into the conjugate instance (a77711 Lemma A1
at `q=2`), solution sets are disjoint when `σ(R)≠R` (Lemma A2), and a
single-instance shift-canonical constraint therefore drops solutions.

## Explicit non-claims

- No deployed-curve break; no security claim at `n≥131`.
- No per-instance leaf-ratio `~1/μ` result (that source-IDEA alternative
  is rejected at these toys).
- No exponent-moving claim.
- HEUR-H1's free-action **median** band `[0.7,1.0]·(1−1/19)` was **not**
  confirmed (`median_fraction=0.0` outside band under V-orbit-lex-min
  bias); do not cite the median band as supported.

## Provenance

Promoted from `EV-BINSTD-780165` under `DEC-20261001-795812` after
`/review-evidence` of `EXP-BINSTD-375338` / `TASK-20261001-ff051b`.
