# Analysis: EXP-BINSTD-6c199f (H-BINSTD-5c4afb)

Review plan: `experiments/EXP-BINSTD-6c199f/review/review-plan.yaml`
(`REVIEW-BINSTD-6c199f-20261003`), written before this analysis.
Producer: TASK-20261003-e05c49. Snapshot: TASK-20261003-28ed82.
Approval: DEC-20261003-b240df. Source idea: IDEA-20261002-adb7bb.
Package tip at review: `c6584878bc0f98fb2955146760d1f9b1e6909c89`
(`cursor/run-binstd-6c199f-stages01-ed0c`). Decision target: **weaken**
(package O-FAIL-BAND — cell (17,3) median_ratio=1.0 vs band≤0.90 with
matched=12, twin OK). Not reject_scoped (unreplicated empirical_only).
No break; no exponent; no n≥131 transfer; no Bedrock/AUXIN. No re-run
this tick.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-BINSTD-603c00` (Stage 0) and `RUN-BINSTD-ba5da0` (Stage 1). Each
has `manifest.yaml`, additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`, `execution-receipt.json`,
and `check.stdout.log` = `OK`. Stage-1 receipt
`status: output_validated`. Within `maximum_runs: 4`. Required Stage-0
freeze artifacts (`stage0/v-catalog.json`,
`stage0/preregistered-predictions.json`) and Stage-1 artifacts
(`stage1/panels.json`, `stage1/control-table.json`, `RESULTS.md`)
present. Amazon Bedrock not used. `certificate.kind: none` (encode-size
instrument; no discrete_log / key_recovery). Producer claims:
`break: false`, `exponent_move: false`. Snapshot
TASK-20261003-28ed82 bound the run package.

**Stage 0 (J2).** `RUN-BINSTD-603c00` reports `twin_ok: true`,
`outcome_hint: O-STAGE0-OK`, freeze paths bound to
`stage0/preregistered-predictions.json` and `stage0/v-catalog.json`.
Frozen δ=0.10 → band_upper=0.90; ε_null=0.15 frozen not run;
catalog_seed 2026100327; GP seeds
`{3,5,7,9,11,13,17,19,21,25,27,33}`; authorized Stage-1 cell
`{(17,3)}`. Catalog: n17_l3 authorized with
`match_feasibility_hits_per_64=64`; n17_l4
`authorized_stage1=false` with disclosed deferred note (unstructured
random dimVV support does not overlap GP dimVV within ±1 on this pin).
Independent `check.py` OK.

**Stage 1 (J3) — blind median recompute from `panels.json` pair rows.**

| cell | matched | min | median_ratio (blind) | band_upper | in_band | twin_fail | all \|ΔdimVV\|≤1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n17_l3 | 12 | 8 | **1.0** | 0.90 | **false** | false | yes (all δ=1) |

Blind recompute: ratios sorted
`[0.833…, 1.0×7, 1.2×4]`; `statistics.median = 1.0` matches producer
`median_ratio_GP_over_rand=1.0`. Every pair `twin_ok=true` and
`dimVV_delta=1`. Pair polarity: 1 GP-cheaper, 7 equal, 4 GP-worse.
`control-table.json` records `outcome: O-FAIL-BAND`,
`matched_pair_count: 12`, `in_band: false`. Matched ≥8 and twins OK →
package **O-FAIL-BAND** by contract (not O-INCONCLUSIVE, not O-ARTIFACT).

**Scope / non-claims (J4).** RESULTS.md and raw-result claim no break,
no exponent move, no Bedrock, and no n≥131 transfer. Construction-family
encode N_var instrument only at toy n=17 ℓ=3. Stage-2
(n∈{19,23} + random-vs-random null with ε=0.15) frozen but not
authorized. Deferred ℓ=4 is a match-feasibility disclosure, not a
band verdict.

## Comparison

Against H-BINSTD-5c4afb distinguishable outcomes and frozen δ band:

- Twin agreement: **holds** on Stage-0 probe and all 12 Stage-1 pairs →
  not O-ARTIFACT.
- Matched pairs: **12 ≥ 8** with `|Δ dim(V·V)| ≤ 1` on every pair →
  not O-INCONCLUSIVE.
- Median N_var(GP)/N_var(rand) vs 1−δ=0.90: **1.0 > 0.90** → package
  **O-FAIL-BAND** (GP-not-cheaper-at-matched-product-dim at this scale).
- O-SUPPORT: **not met**.
- O-IMPEDIMENT: **not met** (runs completed; check OK).
- Blind median / match / twin recompute: **agrees** with producer
  panels, control-table, RESULTS.md, and RUN-BINSTD-ba5da0 raw-result.

## Inference

The package is **valid**. Stage 0 freeze and twin meters stand. Stage 1
meets the preregistered O-FAIL-BAND criterion on the sole authorized
cell (17,3): enough matched pairs, twins OK, median ratio exactly 1.0
against band ≤0.90. Official reading: **O-FAIL-BAND** as preregistered.
This is an unreplicated empirical_only adverse reading of
HEUR-BINSTD-adb7bb-H1 at toy scope → decision **weaken** + replication
next_action; **not** reject_scoped (docs/claims-and-verification.md).
Do **not** support. Do **not** treat deferred ℓ=4 or unrun Stage-2 as
further falsification or repair. No break; no exponent; no n≥131
transfer. Hypothesis and experiment `approved → analyzed` under this
decision (HEUR weakened at tested scope; strength preliminary). No
re-run of this frozen package this tick.

## Limitation

- Toy n=17 ℓ=3 only; Stage-2 multi-n + random-vs-random null not
  authorized under this card.
- First unreplicated O-FAIL-BAND observation; no independent
  validator/red-team (review-plan PD-1).
- `certificate.kind=none` — measurement package, not a solve certificate.
- Encode-size N_var may still hide harder clauses; instrument is
  construction-family only.
- All 12 pairs have GP dimVV=5 vs rand dimVV=6 (δ=1 at the match edge);
  whether exact dimVV equality would change the median is untested here.
- Strength preliminary — insufficient for reject_scoped or KN-FIND.
- No break; no exponent; no n≥131 transfer.
