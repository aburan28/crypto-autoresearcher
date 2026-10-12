# Analysis: EXP-BINSTD-5b2fd0 (H-BINSTD-880e8b)

Review plan: `experiments/EXP-BINSTD-5b2fd0/review/review-plan.yaml`
(`REVIEW-BINSTD-5b2fd0-20261003`), written before this analysis.
Producer: TASK-20261003-1deeb5. Snapshot: TASK-20261003-2d31b9.
Approval: DEC-20261003-672507. Decision target: **inconclusive**
(preregistered O-INCONCLUSIVE — distinct-value floors fail). Prefer
inconclusive over inventing O-FAIL-BAND or support. No break; no
exponent; no n≥131 transfer; no Bedrock/AUXIN. No re-run this tick.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-BINSTD-d295f2` (Stage 0) and `RUN-BINSTD-c11148` (Stage 1). Each
has `manifest.yaml`, additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`, `execution-receipt.json`,
and `check.stdout.log` = `OK`. Stage-1 receipt
`status: output_validated`, `check_returncode: 0`. Within
`maximum_runs: 4`. Required Stage-0 freeze artifacts
(`stage0/v-catalog.json`, `stage0/preregistered-predictions.json`) and
Stage-1 artifacts (`stage1/panels.json`, `stage1/control-table.json`,
`RESULTS.md`) present. Amazon Bedrock not used. `certificate.kind: none`
on both runs (encoding-size instrument; no discrete_log / key_recovery).
Producer claims: `break: false`, `exponent_move: false`.

**Stage 0 (J2).** `RUN-BINSTD-d295f2` reports `twin_ok: true`,
`outcome_hint: O-STAGE0-OK`, freeze paths bound to
`stage0/preregistered-predictions.json` and `stage0/v-catalog.json`.
Frozen band 0.70; catalog_seed 2026100317; bootstrap_seed 2026100318;
authorized Stage-1 cells `{(17,3),(17,4)}`. Independent `check.py` OK.

**Stage 1 (J3) — blind floor re-count from `panels.json` rows.**

| cell | catalog | distinct_dimVV (rows) | distinct_Nvar (rows) | floors (≥3,≥2) | twin_fail | ρ | CI95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n17_l3 | 12 | 2 ({5×6, 6×6}) | 2 ({5×2, 6×10}) | **fail** (dimVV) | false | 0.447… | [0.255, 0.775] |
| n17_l4 | 12 | 2 ({7×6, 10×6}) | 1 ({8×12}) | **fail** (both) | false | nan | [nan, nan] |

Blind re-count of distinct values from row lists matches producer
`distinct_dimVV` / `distinct_Nvar` summary fields. Every row has
`twin_ok: true` (dimVV_a=dimVV_b, Nvar_a=Nvar_b). `control-table.json`
records `any_twin_fail: false` and notes the Stage-2 random-Boolean null
is not authorized.

**Scope / non-claims (J4).** RESULTS.md and raw-result claim no break,
no exponent move, no Bedrock, and no n≥131 transfer. Encoding-size /
XOR-SAT N_var instrument only at toy n=17.

## Comparison

Against H-BINSTD-880e8b distinguishable outcomes and frozen floors:

- Twin agreement: **holds** on Stage-0 probe and all Stage-1 Vs → not
  O-ARTIFACT.
- Distinct-value floors (≥3 dimVV, ≥2 N_var): **fail** on both Stage-1
  cells (dimVV=2 everywhere; N_var collapses to 1 on ℓ=4) →
  **O-INCONCLUSIVE** by contract.
- Spearman band ≥0.70: **not readable** as O-SUPPORT or O-FAIL-BAND
  while floors fail. Observed ρ≈0.447 on (17,3) and undefined on (17,4)
  are disclosed observations only — not band verdicts.
- O-SUPPORT: **not met**.
- O-FAIL-BAND: **not licensed** (floors gate the band reading).
- O-IMPEDIMENT: **not met** (runs completed; check OK).

## Inference

The package is **valid**. Stage 0 freeze and twin meters stand. The
frozen ≥12-shape catalog does not produce enough distinct product-space
dimensions (or, on ℓ=4, enough N_var variation) to decide HEUR-BINSTD-febbe1-H1
against the 0.70 band at the declared Stage-1 cells. Official reading:
**O-INCONCLUSIVE** as preregistered. Decision: **inconclusive**.
Hypothesis and experiment `approved → analyzed`. Do **not** support.
Do **not** reject_scoped (no checkable HEUR falsifier when floors fail;
unreplicated empirical-only). Do **not** invent O-FAIL-BAND from
ρ≈0.447. No break; no exponent; no n≥131 transfer. Successor (not this
tick): catalog-expansion refine/amendment aiming for ≥3 distinct dimVV
(and ≥2 distinct N_var) before any Spearman band verdict.

## Limitation

- Toy n=17 cells only; Stage-2 (n=19,23 + random-Boolean null) not
  authorized under this card.
- Catalog diversity insufficient for a Spearman decision (2 dimVV values
  on both cells; constant N_var on ℓ=4).
- First unreplicated observation; no independent validator/red-team
  (review-plan PD-1).
- `certificate.kind=none` — measurement package, not a solve certificate.
- Encoding-size instrument only; does not predict usable_dimensions
  yield (fbee3f) or beat rho.
- Strength inconclusive — insufficient for support or KN-FIND promotion.
