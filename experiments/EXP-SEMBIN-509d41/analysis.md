# Analysis: EXP-SEMBIN-509d41 Stages 0–1

Review: `REVIEW-SEMBIN-509d41-20261003`  
Evidence: `EV-SEMBIN-d1cf99` · Decision: `DEC-20261003-c77494`  
Producer: `TASK-20261003-af0d91` · Snapshot: `TASK-20261003-caff4e`  
Review handoff: `TASK-20261003-d05161` · Archive: `TASK-20261003-e2ce95`

## Observation

- **Run set.** Two runs under `trial-plan-v1.json`, both `output_validated` / `completed_valid`; `certificate.kind = none`; Amazon Bedrock NOT SELECTED; no Magma/Sage/AUXIN; `n_runs=2 ≤ maximum_runs=3`.
  - `RUN-SEMBIN-9000a8` Stage 0 → `S0-FREEZE-OK` (started/finished `2026-10-03T00:49:04Z`).
  - `RUN-SEMBIN-bd538f` Stage 1 → `S1-INVARIANTS-OK` (wall ≈ 1.92 s).
- **Stage 0 freeze.** `stage0/preregistered-predictions.json` (sha256 `5633d01b…`) and `worksheet-note.md` exist with (C1)–(C6) statements, HEUR-TOP bands, DAG sketch, expected tree counts, and `HEUR_TOP.stage2_admitted_by_this_plan: false`. `frozen_at: 2026-10-03T00:49:04Z` precedes Stage-1 start.
- **Stage 1 tree census.** Counts for `t=3..8` equal `(2t-3)!! = 3, 15, 105, 945, 10395, 135135`; `invariant_hold_rate = 1.0` at every `t` (equations=`t-1`, auxiliaries=`t-2`, `N=(t-2)n+tk`, three-var blocks=`t-2`). Blind re-derivation of `(2t-3)!!` matches.
- **Stage 1 sigma_top design figures.** All producer `design_checks` report `ok: true` within absolute tolerance `5e-3`, including:
  - `(571,4,143)` min/path ≈ 0.407, max/path = 1.0
  - `(571,5,115)` min/path ≈ 0.641, max/path ≈ 2.422
  - `(571,6,96)` min/path ≈ 0.741, max/path ≈ 2.282
  - `(571,8,72)` min/path ≈ 0.832, max/path ≈ 3.325
  - `(16,5,4)` path/min ≈ 1.331
  Blind re-derivation of `(16,5,4)` path/min and `(571,5,115)` min/max-over-path matches producer tables.
- **Producer C4 gate.** `balanced_over_path_ok: true` is gated on `max_over_path > 1` for `t≥5`, not on the recursive mid-split `balanced_tree` ratio. At `t=5,6` the mid-split recursive tree coincides with the **min** shape (`balanced_over_path = min_over_path < 1`); at `t=8` mid-split is near-max (`balanced_over_path ≈ 3.158` vs max `3.325`). Producer comment records this label ambiguity explicitly.
- **DAG known-false control.** `stage1/dag-known-false.md`: `control_status: SCOPED_REFUSAL_RECORDED` — (C1) scoped to full binary trees; DAG with shared auxiliaries has `dag_distinct_auxiliaries=1 < tree_auxiliaries=2` at `t=4`.
- **Non-claims in RESULTS.md.** No exponent move, IC-vs-rho, FIPS verdict, or deployed-curve ECDLP claim. Stage 2 not admitted. No full `O-*` headline under this card.

## Comparison

| Check | Prediction / control | Observed | Agree? |
|---|---|---|---|
| Tree counts `t=3..8` | `(2t-3)!!` | Exact match | yes |
| Invariant hold rate | 1.0 | 1.0 every `t` | yes |
| Design min/path / max/path | Frozen 3-decimal figures | Within `5e-3` | yes |
| `(16,5,4)` path/min | 1.331 | 1.331168… | yes |
| DAG known-false | Scoped refusal | `SCOPED_REFUSAL_RECORDED` | yes |
| Stage 2 | Not in trial-plan-v1 | `stage2_admitted: false` | yes |
| Mid-split `balanced/path` vs claim prose “balanced/path > 1 for all t≥5” | Claim prose | Mid-split < 1 at t=5,6; producer gates on max/path | label note (not gate fail) |

## Inference

Stages 0–1 combinatorial package is **valid** and **supports** the Stage-1 half of H-SEMBIN-9af7e1: (C1) invariance on the enumerated binary-merge-tree class; (C3) design min/max sigma_top figures at the frozen FIPS-label cells; path is not the sigma_top minimiser (`path_over_min > 1` at tested cells with `t≥4`); DAG proves-too-much control passes.

This does **not** license full hypothesis support: Stage-2 HEUR-TOP at `(16,5,4)` was not run; no `O-*` headline is decidable yet. Official decision is **expand** — admit Stage 2 under `TASK-20261002-d67dd7`.

The mid-split recursive “balanced” coinciding with the minimiser at `t=5,6` is a **wording/shape-binding note** for Stage 2 arms (path / cherry-caterpillar / balanced): Stage 2 must bind “balanced” to a near-worst / high-`sigma_top` shape (or the published maximiser of `(n,n,n)` blocks), not assume the recursive mid-split is near-worst for non-power-of-two `t`. It does not fire `O-C1-FAIL` or void `S1-INVARIANTS-OK` under the producer’s declared C4 gate (`max_over_path > 1`).

Strength remains **preliminary** (single unreplicated Stages 0–1 package; Coordinator-direct review PD-1; Stage 2 outstanding).

## Limitation

- Combinatorial only; no Groebner/Macaulay/HEUR-TOP timing.
- Exhaustive enumeration through `t=8` only; no claim for larger `t`.
- Mid-split balanced label ≠ near-worst at `t=5,6` — Stage 2 shape binding must be explicit.
- (C6) / HEUR-ARITY remains conditional and unvalidated under this card.
- Coordinator-direct review without independent validator/red-team (PD-1).
- No FIPS security, IC-vs-rho, exponent, or deployed-curve claim.
- Full `O-CLOSURE` / `O-PROXY-MISLEAD` / `O-IMPEDIMENT` headline awaits Stage 2.

Amazon Bedrock: NOT SELECTED, NOT CONFIGURED, NOT PROBED, NOT CONTACTED, NOT USED.
