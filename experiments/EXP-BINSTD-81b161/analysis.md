# Analysis — EXP-BINSTD-81b161 Stages 0–2

Hypothesis: `H-BINSTD-af1faf`
Experiment: `EXP-BINSTD-81b161` (v1, approved `DEC-20261003-31801d`)
Producer: `TASK-20261003-7da304`
Review: `TASK-20261003-74ada0` / `REVIEW-BINSTD-81b161-20261003`
Predecessor: `EV-BINSTD-f1d8e2` / `DEC-20261003-4bb57d`
Producer tip: `bdc7f33974958d31144958468d9e0c317250213d`

This note is Coordinator review of archived observations. It does not re-run any trial.

Review-plan prior (recorded before this analysis): expect **inconclusive** because raised floors 5/4 were unmet; the 0.70 null-ceiling HEUR was **not tested**; Stage-2 `O-IMPEDIMENT` is the declared gate, not weaken/reject of `HEUR-BINSTD-81b161-H1-NULLCEIL` and not a replicate of `EV-BINSTD-f1d8e2`.

---

## Observation

Three runs with `check.py` stdout `OK`, `claims.break: false`, `claims.exponent_move: false`, `amazon_bedrock: NOT_USED`. `n_runs = 3 ≤ maximum_runs = 6`. Catalog seed `2026100350` is outside the forbidden set `{2026100317, 2026100320, 2026100330, 2026100340}`.

| Run | Stage | Producer outcome | Manifest status |
| --- | --- | --- | --- |
| `RUN-BINSTD-bd4cb6` | 0 | `O-STAGE0-OK` (`twin_ok: true`) | `completed` |
| `RUN-BINSTD-96709d` | 1 | package `O-INCONCLUSIVE`; diagnostic `O-INSTRUMENT-BOUNDARY-17-3` | `completed` |
| `RUN-BINSTD-7e503a` | 2 | `O-IMPEDIMENT` (floors unmet or twin_fail) | `impediment` |

Stage-0 freeze binds `stage0/preregistered-predictions.json` and `stage0/v-catalog.json`. Catalog sizes on Stage-1 cells are 128 (within `[48, 128]`).

Blind re-count from `stage1/panels.json` **rows only** (not RESULTS / raw-result summaries):

| Cell | Role | n_rows | distinct dimVV | distinct N_var | all `twin_ok` | floors (≥5 dimVV, ≥4 N_var) |
| --- | --- | --- | --- | --- | --- | --- |
| `n17_l4` | package | 128 | `{7, 9, 10}` (3) | `{7, 8}` (2) | true | **fail** (both meters) |
| `n17_l3` | diagnostic | 128 | `{5, 6}` (2) | `{4, 5, 6}` (3) | true | **fail** (dimVV; N_var 3<4) |

Control-table: `any_twin_fail: false`, `stage1_package_outcome: O-INCONCLUSIVE`, `stage2_authorized_if: false`, `diagnostic_17_3_outcome: O-INSTRUMENT-BOUNDARY-17-3`, `not_a_weil_uniqueness_retest: true`.

Package `band_reading_authorized_for_null: false` on both cells. Official Spearman fields are `nan`. A pre-admission disclosed ρ exists on the panel object (`n17_l4` ≈ 0.153; `n17_l3` ≈ −0.021) and is **not** a HEUR verdict.

Stage-2: `stage2/null-results.json` is **absent**. Stage-2 `raw-result.json` has no Spearman / ci95 fields. Outcome `O-IMPEDIMENT` with reason `Stage-2 gate failed: (17,4) floors unmet or twin_fail`. Twin fail is false; the gate is floors.

Required Stage-0/1 artifacts (`preregistered-predictions.json`, `v-catalog.json`, `panels.json`, `control-table.json`, `RESULTS.md`, three run directories) are present. No Magma / Sage / AUXIN / Bedrock path.

Infra: Stage-2 `impediment` is the **declared scientific gate** (floors unmet), not a timeout/crash. It is not negative mathematical evidence against the HEUR.

---

## Comparison

Producer `RESULTS.md` package label `O-INCONCLUSIVE` agrees with the row recount: (17,4) distinct_dimVV=3 < 5 and distinct_N_var=2 < 4. Continuity label `O-NOT-WEIL-UNIQUENESS` agrees: this card never authorized a Weil uniqueness band verdict.

Producer diagnostic `O-INSTRUMENT-BOUNDARY-17-3` agrees: (17,3) still has only two dimVV values `{5, 6}` after the product-rank-escape recipe (Stage-0 prescreen already recorded `prescreen_escape_outside_collapse: false`).

Producer Stage-2 `O-IMPEDIMENT` agrees with the absent null JSON and the floors-unmet gate. No Spearman was invented.

Relative to `EV-BINSTD-f1d8e2` (`EXP-BINSTD-4b846c`, seed `2026100340`, floors 3×2): that package was **O-FAIL-BAND** because 3×2 **admission** was met and ρ/CI sat below 0.70, with Stage-2 null ci95_hi≈0.23. This successor **raises admission to 5×4**. The observed (17,4) support is still `{7,9,10}×{7,8}` — the same 3×2 cardinality as the parent, under a **stricter** floor, so the 0.70 HEUR is **not reached as a test**. This is **not** a replicate of the parent 0.70 miss (that miss required floors-met).

Relative to `EV-BINSTD-69cb29` / `EV-BINSTD-90c856`: (17,3) dimVV `{5,6}` collapse continues as a diagnostic boundary.

Does **not** rewrite `EV-BINSTD-f1d8e2` / `DEC-20261003-4bb57d`. Does **not** re-score frozen `EXP-BINSTD-4b846c` / `9b18fc` / `16ee30` / `5b2fd0` v1.

---

## Inference

Four labels, four jobs:

1. **Package `O-INCONCLUSIVE`** is the authorized reading of this card: after raising floors to ≥5 dimVV and ≥4 N_var, cell `(n,ℓ)=(17,4)` under seed `2026100350` did not meet admission. `HEUR-BINSTD-81b161-H1-NULLCEIL` is defined **only after** those floors. Direction: **neutral**. Decision: **inconclusive**. Strength: **inconclusive**.

2. **Diagnostic `O-INSTRUMENT-BOUNDARY-17-3`** is **not** a package gate. Product-rank-escape did not produce a third dimVV value. It does **not** convert the package into weaken/reject, and it does **not** restore FORALL `{(17,3),(17,4)}`.

3. **`O-NOT-WEIL-UNIQUENESS`** is the continuity name refusing a Weil uniqueness re-test on this floors-unmet / 3×2-cardinality support.

4. **Stage-2 `O-IMPEDIMENT`** is the declared floors gate. It is **not** `O-NULL-CEILING-BELOW-LEGACY`, **not** `O-NULL-REACHES-LEGACY-BAND`, **not** a timeout treated as math, and **not** a license to invent Spearman on collapsed support.

Official decision: **inconclusive** (not `weaken` — the 0.70 HEUR was not tested; not `reject_scoped`; not `support`; not a replicate of `EV-BINSTD-f1d8e2`). Hypothesis/experiment `approved → analyzed`. No break; no exponent; no n≥131 transfer.

Refutation artifact: none required (direction is not weakens/contradicts). Floor counts are derivation-checkable from panel rows (`proof_status: empirical_only` on the instrument observation).

Review-plan prior vs outcome: **matched** on J1–J4. Blind distinct-value re-count agreed with producer summaries. No prior overturn. `PD-1` (no independent validator/red-team) recorded.

---

## Limitation

- Toy `n=17` only. Transfer of the 0.70 band, or of this floor miss, to `n≥131` is an unvalidated non-claim.
- First unreplicated successor observation; Coordinator-direct review (`PD-1`); no independent validator/red-team.
- Discrete support on (17,4) remained 3×2 under a 5×4 admission — the support-seeking catalog (128 shapes, seed `2026100350`) did not enrich dimVV/N_var beyond the parent cardinality.
- (17,3) product-rank-escape failed to leave `{5,6}`; a different escape recipe is untested under this card.
- `certificate.kind=none`. Encoding-size / XOR-SAT N_var instrument only.
- Pre-admission disclosed ρ must not be re-read as a band verdict.
- Amazon Bedrock not used. No AUXIN.

Exemplar-claim checklist (`docs/target-result-profile.md`): **does not apply**. This is a toy heuristic-validation instrument, not an exponent-first conditional complexity claim. No `support`/`expand` on an asymptotic statement.

Successor (not this tick): a new frozen catalog/seed targeting dimVV≥5 and N_var≥4 at (17,4), **or** a new contract that lowers the floor. Never silently re-score this run under 3×2 admission.
