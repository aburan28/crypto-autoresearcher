# Analysis: EXP-BINSTD-16ee30 (H-BINSTD-7cbce1)

Review plan: `experiments/EXP-BINSTD-16ee30/review/review-plan.yaml`
(`REVIEW-BINSTD-16ee30-20261003`), written before this analysis.
Producer: TASK-20261003-a7b01e. Snapshot: TASK-20261003-9cd068.
Approval: DEC-20261003-928974. Predecessor: EV-BINSTD-a99d47 /
EXP-BINSTD-5b2fd0. Decision target: **inconclusive** (package
O-INCONCLUSIVE — Stage-1 admission floors unmet on (17,3)). Prefer
inconclusive over inventing package O-FAIL-BAND from the (17,4)
floors-met out-of-band cell. No break; no exponent; no n≥131 transfer;
no Bedrock/AUXIN. No re-run this tick. Not a re-run of frozen v1.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-BINSTD-597863` (Stage 0) and `RUN-BINSTD-fb30de` (Stage 1). Each
has `manifest.yaml`, additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`, `execution-receipt.json`,
and `check.stdout.log` = `OK`. Stage-1 receipt
`status: output_validated`. Within `maximum_runs: 4`. Required Stage-0
freeze artifacts (`stage0/v-catalog.json`,
`stage0/preregistered-predictions.json`) and Stage-1 artifacts
(`stage1/panels.json`, `stage1/control-table.json`, `RESULTS.md`)
present. Amazon Bedrock not used. `certificate.kind: none` (encoding-size
instrument; no discrete_log / key_recovery). Producer claims:
`break: false`, `exponent_move: false`. Catalog seed 2026100320 ≠ v1
seed 2026100317 (`not_a_rerun_of: EXP-BINSTD-5b2fd0`).

**Stage 0 (J2).** `RUN-BINSTD-597863` reports `twin_ok: true`,
`outcome_hint: O-STAGE0-OK`, freeze paths bound to
`stage0/preregistered-predictions.json` and `stage0/v-catalog.json`.
Frozen band 0.70; catalog_seed 2026100320; bootstrap_seed 2026100321;
admission floors ≥3 dimVV / ≥2 N_var; authorized Stage-1 cells
`{(17,3),(17,4)}`. Catalog sizes: n17_l3=30, n17_l4=29 (≥24 min).
Independent `check.py` OK.

**Stage 1 (J3) — blind floor re-count from `panels.json` rows.**

| cell | catalog | distinct_dimVV (rows) | distinct_Nvar (rows) | floors (≥3,≥2) | twin_fail | ρ | CI95 | band_auth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n17_l3 | 30 | 2 ({5,6}) | 4 ({3,4,5,6}) | **fail** (dimVV) | false | nan (pre-adm ≈−0.093) | [nan, nan] | false |
| n17_l4 | 29 | 3 ({7,9,10}) | 2 ({7,8}) | **met** | false | −0.241… | [−0.441, −0.178] | true |

Blind re-count of distinct values from row lists matches producer
`distinct_dimVV` / `distinct_Nvar` / `admission_floors_met` summary
fields. Every row has `twin_ok: true` (dimVV_a=dimVV_b, Nvar_a=Nvar_b).
`control-table.json` records `any_twin_fail: false`. On (17,4),
floors met and ρ with CI entirely below the 0.70 band → cell-level
out-of-band reading is disclosed; package label remains gated by the
(17,3) floor fail.

**Scope / non-claims (J4).** RESULTS.md and raw-result claim no break,
no exponent move, no Bedrock, and no n≥131 transfer. Encoding-size /
XOR-SAT N_var instrument only at toy n=17. Not a re-run of
EXP-BINSTD-5b2fd0 v1.

## Comparison

Against H-BINSTD-7cbce1 distinguishable outcomes and frozen admission
floors (successor to EV-BINSTD-a99d47):

- Twin agreement: **holds** on Stage-0 probe and all Stage-1 Vs → not
  O-ARTIFACT.
- Distinct-value admission floors (≥3 dimVV, ≥2 N_var): **fail** on
  (17,3) (dimVV=2); **met** on (17,4). FORALL Stage-1 admission fails
  → package **O-INCONCLUSIVE** by contract.
- Spearman band ≥0.70: **not readable as package O-SUPPORT or
  package O-FAIL-BAND** while any Stage-1 cell fails floors. The
  (17,4) ρ≈−0.241 (CI entirely <0.70) is a disclosed floors-met
  cell reading only — not a package band verdict.
- Relative to EV-BINSTD-a99d47 (v1: both cells floor-fail; ℓ=4
  distinct_Nvar=1): diversity-seeking catalog repaired N_var diversity
  on (17,3) (4 values) and met both floors on (17,4); (17,3) dimVV
  diversity remains at 2.
- O-SUPPORT: **not met**.
- Package O-FAIL-BAND: **not licensed** (floors gate the package band
  reading under FORALL).
- O-IMPEDIMENT: **not met** (runs completed; check OK).

## Inference

The package is **valid**. Stage 0 diversity-seeking freeze and twin
meters stand. Catalog expansion partially repaired the EV-BINSTD-a99d47
floor failure (ℓ=4 floors now met; ℓ=3 N_var diversity improved) but
(17,3) still collapses to only two dim(V·V) values, so
HEUR-BINSTD-febbe1-H1 cannot be decided as a package against the 0.70
band. Official reading: **O-INCONCLUSIVE** as preregistered. Decision:
**inconclusive**. Hypothesis and experiment `approved → analyzed`. Do
**not** support. Do **not** invent package O-FAIL-BAND from the (17,4)
cell. Do **not** weaken/reject_scoped from the unreplicated (17,4)
floors-met out-of-band reading under a package O-INCONCLUSIVE label
(PD-1; empirical_only). No break; no exponent; no n≥131 transfer.
Successor (not a re-run of this freeze or v1): further catalog work
targeting ℓ=3 dimVV ≥3 and/or a scoped (17,4) fail-band replication
under floors-met.

## Limitation

- Toy n=17 cells only; Stage-2 (n=19,23 + random-Boolean null) not
  authorized under this card.
- (17,3) catalog still yields only two dimVV values despite ≥30 shapes.
- (17,4) floors-met out-of-band ρ is unreplicated; strength capped.
- First unreplicated successor observation; no independent
  validator/red-team (review-plan PD-1).
- `certificate.kind=none` — measurement package, not a solve certificate.
- Encoding-size instrument only; does not predict usable_dimensions
  yield or beat rho.
- Strength inconclusive — insufficient for support or KN-FIND promotion.
