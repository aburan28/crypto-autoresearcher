# Analysis — EXP-BINSTD-4b846c Stages 0–2

Hypothesis: `H-BINSTD-07aa73`
Experiment: `EXP-BINSTD-4b846c` (v1, approved `DEC-20261003-7fbcb8`)
Producer: `TASK-20261003-c9a4a4`
Snapshot: `TASK-20261003-5387c1`
Review: `TASK-20261003-c3607d` / `REVIEW-BINSTD-4b846c-20261003`
Predecessor: `EV-BINSTD-90c856` / `DEC-20261003-9f58a7` (also cites `EV-BINSTD-69cb29`, `EV-BINSTD-a99d47`)
Producer tip: `f51150054a68fc5212c9a075faa44658c6bf0ed3`

This note is Coordinator review of archived observations. It does not re-run any trial.

---

## Observation

Three runs completed with `check.py` stdout `OK`, `execution-receipt.json` `status: output_validated`, `certificate.kind: none`, `claims.break: false`, `claims.exponent_move: false`, `amazon_bedrock: NOT_USED`. `n_runs = 3 ≤ maximum_runs = 6`. Catalog seed `2026100340` is outside the forbidden set `{2026100317, 2026100320, 2026100330}`.

| Run | Stage | Producer outcome | Wall (receipt) |
| --- | --- | --- | --- |
| `RUN-BINSTD-2dc695` | 0 | `O-STAGE0-OK` (`twin_ok: true`) | 0.397 s |
| `RUN-BINSTD-ae1529` | 1 | `O-FAIL-BAND`; diagnostic `O-INSTRUMENT-BOUNDARY-17-3`; cell `O-CELL-FAIL-BAND-17-4` | 0.903 s |
| `RUN-BINSTD-b3d5d2` | 2 | `O-NULL-ALSO-BELOW-BAND` | 0.571 s |

Stage-0 freeze binds `stage0/preregistered-predictions.json` (Spearman band `0.70`; seeds `2026100340` / `2026100341` / `2026100342`; package cells `{(17,4)}`; diagnostic `(17,3)` product-rank-escape; Stage-2 authorized) and `stage0/v-catalog.json`. Catalog sizes on Stage-1 cells are 72 (within `[32, 72]`).

Blind re-count from `stage1/panels.json` **rows only** (not RESULTS / raw-result summaries):

| Cell | Role | n_rows | distinct dimVV | distinct N_var | all `twin_ok` | floors (≥3 dimVV, ≥2 N_var) |
| --- | --- | --- | --- | --- | --- | --- |
| `n17_l3` | diagnostic | 72 | `{5, 6}` (2) | `{5, 6}` (2) | true | fail (dimVV) |
| `n17_l4` | package | 72 | `{7, 9, 10}` (3) | `{7, 8}` (2) | true | met |

Control-table `any_twin_fail: false`. Package `band_reading_authorized` follows (17,4) floors only.

Package cell Spearman from the same panel object: ρ = `0.17385016708940756`, bootstrap CI95 = `[-0.08375481163023511, 0.3461820100189872]`, `in_band: false`, `ci_entirely_below_band: true` vs frozen band `0.70`. Diagnostic Spearman is `nan` (band not authorized).

Stage-2 `stage2/null-results.json` (200 reps):

- permutation dimVV vs fixed N_var: mean ρ = `0.002897502784823461`, `ci95_hi = 0.2332489741782888`, `reaches_band: false`, seed `2026100342`
- random-Boolean matched catalog (support `{7, 9, 10}`): mean ρ = `-0.009892882465492662`, `ci95_hi = 0.23647154446502733`, `reaches_band: false`

Required artifacts (`preregistered-predictions.json`, `v-catalog.json`, `panels.json`, `control-table.json`, `null-results.json`, `RESULTS.md`, three run directories) are present. No Magma / Sage / AUXIN / Bedrock path.

Infra: none. These are completed valid instrument runs, not timeouts.

---

## Comparison

Producer `RESULTS.md` package label `O-FAIL-BAND` agrees with the row recount: (17,4) floors met and ρ/CI entirely below `0.70`. Continuity label `O-CELL-FAIL-BAND-17-4` is the same cell reading.

Producer diagnostic `O-INSTRUMENT-BOUNDARY-17-3` agrees with the row recount: (17,3) still has only two dimVV values `{5, 6}` after the product-rank-escape recipe (Stage-0 prescreen already recorded `prescreen_escape_outside_collapse: false`). Spearman is correctly withheld (`nan`).

Producer Stage-2 `O-NULL-ALSO-BELOW-BAND` agrees with both `reaches_band: false` flags. Null upper CIs (~0.23) sit far below `0.70` and near the observed CI upper bound (0.346).

Relative to `EV-BINSTD-90c856` (`EXP-BINSTD-9b18fc`, seed `2026100330`): that package was **O-INCONCLUSIVE** because FORALL floors failed on (17,3) (`distinct_dimVV=2`); scoped `O-CELL-FAIL-BAND-17-4` was secondary (ρ≈0.110, CI entirely below 0.70). This successor **cell-scopes the package to (17,4)**, so the same style of (17,4) miss is now the **package** label, while (17,3) remains diagnostic. (17,4) ρ≈0.174 here vs ≈0.110 there: both CIs entirely below 0.70; neither is a sign-stable magnitude claim.

Relative to `EV-BINSTD-69cb29` (`EXP-BINSTD-16ee30`): (17,3) dimVV `{5,6}` collapse is the third consecutive catalog family; (17,4) fail-band vs 0.70 continues (prior disclosed ρ≈−0.24; sign not stable).

Does **not** rewrite `EV-BINSTD-90c856` / `EV-BINSTD-69cb29` / `EV-BINSTD-a99d47`. Does **not** re-score frozen `EXP-BINSTD-9b18fc` / `16ee30` / `5b2fd0` v1.

---

## Inference

Four labels, four jobs:

1. **Package `O-FAIL-BAND`** is the authorized reading of `HEUR-BINSTD-4b846c-H1-CELL-17-4`: after (17,4) admission floors, Spearman ρ(dim(V·V), N_var) was predicted ≥ 0.70 and measured ≈0.174 with CI entirely below 0.70, twins agreeing. That is a miss of the preregistered 0.70 HEUR at toy `(n,ℓ)=(17,4)` under catalog seed `2026100340`. Direction: **weakens** that HEUR at that scope. Strength: **preliminary** (first unreplicated cell-scoped package; `PD-1`; `empirical_only`).

2. **Diagnostic `O-INSTRUMENT-BOUNDARY-17-3`** is **not** a package gate. Product-rank-escape did not produce a third dimVV value. This crystallizes the (17,3) instrument boundary already seen under `EV-BINSTD-90c856` and `EV-BINSTD-69cb29`. It does **not** convert package `O-FAIL-BAND` into `O-INCONCLUSIVE`, and it does **not** restore FORALL `{(17,3),(17,4)}`.

3. **`O-CELL-FAIL-BAND-17-4`** is the continuity name for the same (17,4) CI-below-band cell. It is not a second independent package.

4. **`O-NULL-ALSO-BELOW-BAND`** refuses `O-STRUCTURE-SPECIFIC-FAIL-BAND`. Permutation and random-Boolean pairings of the observed 3-valued dimVV support also fail to reach 0.70 (`ci95_hi ≈ 0.23`). The 0.70 miss is therefore **not** evidence that Weil product-space pairing uniquely lacks correlation: the frozen band sits above what this discrete 3×2 support's nulls reach. That qualifies **interpretation** of the fail-band (possible instrument/threshold artifact). It does **not** un-authorize the package label: floors were met, so `O-FAIL-BAND` vs the stated 0.70 HEUR still holds as a threshold miss.

Official decision: **weaken** (not `reject_scoped` — unreplicated `empirical_only`; not `support`; not package `inconclusive`). Hypothesis/experiment `approved → analyzed`. No break; no exponent; no n≥131 transfer.

Refutation artifact: empirical panel + Stage-2 null JSON (`proof_status: empirical_only`). No counterexample certificate.

---

## Limitation

- Toy `n=17` only. Transfer of the 0.70 band, or of this miss, to `n≥131` is an unvalidated non-claim.
- First unreplicated cell-scoped package; Coordinator-direct review (`PD-1`); no independent validator/red-team.
- Discrete support on (17,4) is exactly the admission floor (3 dimVV × 2 N_var). Spearman dynamic range vs a 0.70 band is correspondingly limited; Stage-2 makes that quantitative (`ci95_hi ≈ 0.23`).
- (17,3) product-rank-escape failed to leave `{5,6}`; a different escape recipe is untested under this card.
- `certificate.kind=none`. Encoding-size / XOR-SAT N_var instrument only.
- Bootstrap 200 / null 200 are the frozen budgets; they are not a second independent catalog.
- Spearman sign/magnitude on (17,4) is not stable across `EV-BINSTD-69cb29` / `90c856` / this package; only “CI entirely below 0.70 after floors” replicates at the cell level.
- Amazon Bedrock not used. No AUXIN.

Exemplar-claim checklist (`docs/target-result-profile.md`): **does not apply**. This is a toy heuristic-validation instrument, not an exponent-first conditional complexity claim. No `support`/`expand` on an asymptotic statement.
