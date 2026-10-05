# Analysis — EXP-SEMBIN-d830d5 Stage 2 (H-SEMBIN-558848)

Review plan: `experiments/EXP-SEMBIN-d830d5/review/review-plan-stage2.yaml`
(`REVIEW-SEMBIN-d830d5-stage2-20261003`), written before this analysis.
Producer: TASK-20261003-130c83. Snapshot: TASK-20261003-de0fa2 at tip
`ec7485ec7d6e38a8d9ee4af69dc0b3a72ee7423f`. Prior expand: EV-SEMBIN-36f27d /
DEC-20261003-32e9a4. Amendment: AMD-EXP-SEMBIN-d830d5-20261003-stage2.
Amazon Bedrock: NOT SELECTED.

## Observation

- **RUN-SEMBIN-a1bd6e** (Stage 2): `status=output_validated`,
  `check_returncode=0`, `outcome=O-IMPEDIMENT`, `completed_valid`.
  Wall ≈ 844.3 s; peak RSS ≈ 352.6 MB. `amazon_bedrock=NOT SELECTED`.
- C2 re-scope recorded: `sizes_required` 3→2 on cells `{(30,7,3),(36,8,4)}`
  (`stage2/c2-rescope.json`), authorized by DEC-20261003-32e9a4.
- Image measurability under exhaustive domain cap 2_500_000:
  - `(30,7,3)`: image_measurable=true; typed `image_over_finite_k_cap` =
    0.7362003326416016 (image_size 1543924 / 2^{21}); untyped =
    0.07251548767089844; degenerate matches untyped; randomized-null
    matches typed image on this cell.
  - `(36,8,4)`: all four arms `domain_exceeds_cap` (domains ≫ 2.5e6);
    image_measurable=false; `typed_image_over_cap=null`.
- `image_measurable_cells=1` of 2; C1 under rescope needs 2 → **C1 unscored**.
- Degree/cost arms recorded on both cells via pure_python_macaulay_closure
  (not msolve d_F4). Controls_ok=true (degenerate match on measurable cell;
  unscored control note on impediment cell).
- Stages 0–1 artifacts unchanged inputs (S0-FREEZE-OK / SMOKE_PASS).
- Claims: break/exponent/fips all false. No Magma/Sage/AUXIN/Bedrock.

## Comparison

- Blind re-derivation of typed image_over_cap on `(30,7,3)` from
  ladder-rows alone: 1543924 / 2097152 = 0.7362003326416016 — matches
  arm-summaries.
- Against C1 threshold ≥0.9: the single measurable typed reading is
  **below** 0.9, but C1 is contractually unscored until ≥2 cells are
  measurable — do not promote O-NO-YIELD from one cell.
- Against C2/C3: cost and degree columns exist, but conservation scoring
  requires the rescoped two-size ladder with scored images; impediment
  blocks the official C2/C3 reading.
- Proves-too-much: treating domain_exceeds_cap as O-NO-YIELD would convert
  an infrastructure cap into a mathematical falsifier — forbidden by
  H-SEMBIN-558848 O-IMPEDIMENT clause and AGENTS.md rule 5.

## Inference

- Stage-2 package is **valid** and correctly labeled **O-IMPEDIMENT**.
- Direction on H-SEMBIN-558848 C1–C3 remains **neutral**.
- Official decision: **refine** — amend the Stage-2 image instrument
  (raise exhaustive cap, adopt a sampling estimator with disclosed error,
  and/or replace `(36,8,4)` with a Stage-0-feasible cell whose domain fits
  the cap) under a new versioned amendment, then `/run` Stage 2 only.
  Do **not** support / weaken / reject_scoped on this package.
- Strength: **preliminary** (single unreplicated Stage-2 run; PD-1
  coordinator-inline).
- Hypothesis remains `approved` (science unscored). Experiment Stage-2
  contract moves toward analyzed under this review's DEC.

## Limitation

- Exhaustive multiset/product image at domain cap 2.5e6 cannot score
  `(36,8,4)` (domains up to ~4.45e9).
- Single measurable cell cannot decide C1 (≥2/2 under rescope).
- Typed reading 0.736 < 0.9 on `(30,7,3)` is disclosed but not an
  official O-NO-YIELD.
- msolve/WDSat still unavailable; degree instrument is pure-Python
  Macaulay closure, not F4 step-degree.
- PD-1: no independent validator/red-team session for this impediment
  refine call.
- No break / exponent / FIPS / deployed-curve claim. Bedrock unused.
