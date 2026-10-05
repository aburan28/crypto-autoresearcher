# Analysis: EXP-BINSTD-9b18fc (H-BINSTD-73ea03)

Review plan: `experiments/EXP-BINSTD-9b18fc/review/review-plan.yaml`
(`REVIEW-BINSTD-9b18fc-20261003`), written before this analysis.
Producer: TASK-20261003-a8c19c. Snapshot: TASK-20261003-598467.
Approval: DEC-20261003-6e578e. Predecessor: EV-BINSTD-69cb29 /
EXP-BINSTD-16ee30 (also cites EV-BINSTD-a99d47). Tip: `d4502db2…` on
`cursor/run-binstd-9b18fc-stages01-ed0c`.

Decision target: **inconclusive** (package **O-INCONCLUSIVE** — Stage-1
admission floors unmet on (17,3)) with honest first-class scoped
secondary **O-CELL-FAIL-BAND-17-4** on (17,4). Prefer package
inconclusive over inventing package O-FAIL-BAND from the scoped cell.
No break; no exponent; no n≥131 transfer; no Bedrock/AUXIN. No re-run
this tick. Not a re-run of EXP-BINSTD-16ee30 or EXP-BINSTD-5b2fd0 v1.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-BINSTD-54a677` (Stage 0) and `RUN-BINSTD-6e9fde` (Stage 1). Each
has `manifest.yaml`, additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`, `execution-receipt.json`,
and `check.stdout.log` = `OK`. Stage-1 receipt
`status: output_validated`. Within `maximum_runs: 4`. Required Stage-0
freeze artifacts (`stage0/v-catalog.json`,
`stage0/preregistered-predictions.json`) and Stage-1 artifacts
(`stage1/panels.json`, `stage1/control-table.json`, `RESULTS.md`)
present. Amazon Bedrock not used. `certificate.kind: none` (encoding-size
instrument; no discrete_log / key_recovery). Producer claims:
`break: false`, `exponent_move: false`. Catalog seed 2026100330 ∉
forbidden priors {2026100317, 2026100320}
(`not_a_rerun_of: [EXP-BINSTD-16ee30, EXP-BINSTD-5b2fd0]`).

**Stage 0 (J2).** `RUN-BINSTD-54a677` reports `twin_ok: true`,
`outcome_hint: O-STAGE0-OK`, freeze paths bound to
`stage0/preregistered-predictions.json` and `stage0/v-catalog.json`.
Frozen band 0.70; catalog_seed 2026100330; bootstrap_seed 2026100331;
admission floors ≥3 dimVV / ≥2 N_var; scoped (17,4) fail-band
replication authorized; authorized Stage-1 cells `{(17,3),(17,4)}`.
Catalog sizes: n17_l3=72, n17_l4=72 (≥32 min / ≤72 max). Independent
`check.py` OK. Stage-0 prescreen already showed (17,3) dimVV diversity
stuck at {5,6} after enhanced seek.

**Stage 1 (J3) — blind floor re-count from `panels.json` rows.**

| cell | catalog | distinct_dimVV (rows) | distinct_Nvar (rows) | floors (≥3,≥2) | twin_fail | ρ | CI95 | band_auth | ci_below_band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n17_l3 | 72 | 2 ({5,6}) | 3 ({4,5,6}) | **fail** (dimVV) | false | nan (pre-adm ≈0.226) | [nan, nan] | false | false |
| n17_l4 | 72 | 3 ({7,9,10}) | 2 ({7,8}) | **met** | false | 0.1099… | [−0.139, 0.296] | true | **true** |

Blind re-count of distinct values from row lists matches producer
`distinct_dimVV` / `distinct_Nvar` / `admission_floors_met` summary
fields. Every row has `twin_ok: true` (dimVV_a=dimVV_b, Nvar_a=Nvar_b).
`control-table.json` records `any_twin_fail: false` and
`scoped_17_4_outcome: O-CELL-FAIL-BAND-17-4`. On (17,4), floors met and
CI entirely below the 0.70 band → scoped cell fail-band fires by
contract. Package label remains gated by the (17,3) floor fail →
**O-INCONCLUSIVE**.

**Scope / non-claims (J4).** RESULTS.md and raw-result claim no break,
no exponent move, no Bedrock, and no n≥131 transfer. Encoding-size /
XOR-SAT N_var instrument only at toy n=17. Not a re-run of
EXP-BINSTD-16ee30 or EXP-BINSTD-5b2fd0 v1.

## Comparison

Against H-BINSTD-73ea03 distinguishable outcomes and frozen dual-label
contract (successor to EV-BINSTD-69cb29):

- Twin agreement: **holds** on Stage-0 probe and all Stage-1 Vs → not
  O-ARTIFACT.
- Distinct-value admission floors (≥3 dimVV, ≥2 N_var): **fail** on
  (17,3) (dimVV=2 across 72 shapes); **met** on (17,4). FORALL Stage-1
  admission fails → package **O-INCONCLUSIVE** by contract.
- Spearman band ≥0.70: **not readable as package O-SUPPORT or
  package O-FAIL-BAND** while any Stage-1 cell fails floors.
- Scoped (17,4): floors met, twin OK, CI95 entirely <0.70 →
  **O-CELL-FAIL-BAND-17-4** as authorized secondary. Does **not**
  upgrade package O-INCONCLUSIVE.
- Relative to EV-BINSTD-69cb29 (seed 2026100320; catalog ~30; (17,3)
  dimVV=2; (17,4) floors-met ρ≈−0.24 disclosed only): enhanced catalog
  (seed 2026100330; size 72) did **not** repair (17,3) dimVV diversity
  (still 2 values); (17,4) floors-met fail-band **replicates** under the
  new catalog with ρ≈0.110 (sign differs from prior ≈−0.24; both CIs
  entirely below 0.70). Scoped outcome is now first-class, not merely
  disclosed.
- O-SUPPORT: **not met**.
- Package O-FAIL-BAND: **not licensed** (floors gate the package band
  reading under FORALL).
- O-IMPEDIMENT: **not met** (runs completed; check OK).

## Inference

The package is **valid**. Stage 0 enhanced diversity freeze and twin
meters stand. Enhanced catalog (72 shapes, dimVV-first seek) failed to
clear the (17,3) dimVV admission floor that also blocked EV-BINSTD-69cb29,
so HEUR-BINSTD-febbe1-H1 still cannot be decided as a package against the
0.70 band. Official package reading: **O-INCONCLUSIVE**. Independently,
the contract's scoped arm records **O-CELL-FAIL-BAND-17-4** — a first
new-catalog replication of the EV-BINSTD-69cb29 (17,4) floors-met
fail-band cell. Decision: **inconclusive**. Hypothesis and experiment
`approved → analyzed`. Do **not** support. Do **not** invent package
O-FAIL-BAND from the scoped cell. Do **not** weaken/reject_scoped from
the unreplicated package-floor-fail package plus first scoped-cell
replication alone (PD-1; empirical_only). No break; no exponent; no
n≥131 transfer. Successor (not a re-run of this freeze, 16ee30, or
5b2fd0 v1): treat repeated (17,3) dimVV collapse as an instrument
boundary and/or advance the replicated (17,4) cell fail-band under a
cell-scoped / Stage-2-null contract.

## Limitation

- Toy n=17 cells only; Stage-2 (n=19,23 + random-Boolean null) not
  authorized under this card.
- (17,3) catalog still yields only two dimVV values ({5,6}) despite 72
  enhanced-diversity shapes — second consecutive seed family with the
  same floor fail.
- (17,4) scoped fail-band is a first new-catalog replication; ρ sign
  flipped vs EV-BINSTD-69cb29 (≈+0.11 vs ≈−0.24) while both stay below
  band — association magnitude/sign not stable; only the fail-band
  relative to 0.70 is replicated at the CI level.
- First unreplicated enhanced-diversity package; no independent
  validator/red-team (review-plan PD-1).
- `certificate.kind=none` — measurement package, not a solve certificate.
- Encoding-size instrument only; does not predict usable_dimensions
  yield or beat rho.
- Strength inconclusive — insufficient for support or KN-FIND promotion.
