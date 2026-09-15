# Validation report — TASK-20260913-67ab4f

- Review round: REVIEW-SEMBIN-20260913-2c40bb (`coordination/review/sembin-20260913-2c40bb/review-plan.yaml`)
- Reviewed: RUN-SEMBIN-3ae91c of EXP-SEMBIN-2c40bb, hypothesis H-SEMBIN-97ea23, snapshot TASK-20260913-a10005 at `be240e540`
- Role: validator (review-adversarial). Joints owned: M1, M2, M3, M4, M5, proves_too_much.
- Scratch (all scripts and outputs): `coordination/review/sembin-20260913-9d649f/TASK-20260913-67ab4f/scratch/`

Committed bytes: `git diff be240e540 -- experiments/EXP-SEMBIN-2c40bb/` is empty; every run artifact read here is the committed byte content. The manifest's recorded `sha256` for each retained artifact matches my own hash of the file (`scratch/check_surface.json` → `M1_4_determinism`).

This report speaks to the joints only. It gives no whole-claim verdict, moves no status, says nothing about any curve's security in either direction, and measures or asserts no degree: the degree bound 4 used in every Macaulay width below is a GIVEN parameter of the run (IMP-SEMBIN-ENGINE). All arithmetic is closed-form log2 arithmetic in Python 3 `math` with exact integers for factorials and binomials.

## Sequencing and procedure deviation (read this first)

The plan requires M1(1), M4(1) and M5(4) to be re-derived BEFORE `code/surface_cost.py`, `code/sparse_independent.py` or `experiments/EXP-SEMBIN-f4a17b/code/memory_charged_cost.py` is opened. What the scratch directory records, honestly:

| file | mtime (UTC) | what it is |
|---|---|---|
| `scratch/own_rederivation.py` / `.json` | 07:04 | my two-sided model from the statements only; docstring names the sources (H-SEMBIN-97ea23, tables.yaml Table 3, implementation.md prose, KN-LIT-e77232) and declares it written before the three code files were opened |
| `scratch/own_model.py` | 07:10 | my full-axis re-implementation; its docstring says it was written AFTER the blind step and AFTER reading `surface_cost.py` |
| `scratch/check_surface.py` / `.json` | 07:11–07:13 | M1(2)(3)(4), M2, PTM object 1 against raw-result.json / surface.json |
| `scratch/rederive_pre_code.py` / `.json` / `.stdout.txt` | 07:27 | a SECOND derivation of M1(1), M4(1), M5(4) whose note claims it ran before the code was opened |
| `scratch/sequencing_log.txt` | 07:31 | "code files opened at 07:31, after rederive_pre_code.py ran" |
| `scratch/validate_surface.py` / `.json` / `.stdout.txt` | 07:37–07:38 | M1(2)(3), M2, M3(C3, C4), M4(2)(4), PTM 1 and 2 |
| `scratch/validate_c10.py` / `.json` / `.stdout.txt` | 07:40–07:43 | M3(3) C10 residuals |
| `scratch/rerun_determinism/`, `rerun_determinism_hashes.json` | 07:50–07:52 | my own re-execution of the producer's `run_all.py` and hashes |

**PD-V1 (my deviation).** My session's context was compacted mid-task. The post-compaction context, not knowing `own_rederivation.py` existed, re-did the blind step as `rederive_pre_code.py` at 07:27 and wrote `sequencing_log.txt` — but `own_model.py`'s own docstring records that `surface_cost.py` had already been read by this session at about 07:10. Therefore:

- `own_rederivation.py` (07:04) IS the attestable blind derivation: it predates every code read the scratch directory records.
- `rederive_pre_code.py` (07:27) is NOT attestable as blind, whatever its note says; `sequencing_log.txt` is superseded by this paragraph.
- The two derivations agree on every quantity they share: crossovers 303 / 435 / 375 / 520 / 460 identically, margins at 409 to ≤ 9e-3 bits (own_rederivation used one relation-store convention; rederive_pre_code evaluated three and reproduced the parent's cells only with the `3n·2^k`-bit convention), excess 29.0 at all five labels, cheapest sparse memory 65.33 at m = 8 and dense 80.07 at m = 6, sparse working set at (571, 12) = 70.2714 to 1e-6 bits. So the blind result stands as recorded in `own_rederivation.json`, and the second derivation adds only the relation-store-convention disclosure.

Script runs: 6 scripted computations against the budget of 10 — `own_rederivation.py`, `check_surface.py`, `rederive_pre_code.py`, `validate_surface.py`, `validate_c10.py`, and one re-execution of the producer's `run_all.py`. Inline inspection one-liners (JSON field dumps, hash comparisons, one re-keying of the C10 table) were used freely and are not counted. Wall clock: the scratch directory was created 07:02 UTC; this report is written at ~08:00 UTC (≈ 58 min of the 90 allowed).

---

## M1 — reproduction gate and surface arithmetic

### M1(1) Own two-sided code, before opening the producer's code

Semaev side (Table 3 as stated in `inputs/SEMAEV-2015-310/tables.yaml`): stage 1 = m!·2^{n/m}·n^{4ω}, ω = 3, stage 2 = 2^{2n/m}, un-ceiled n/m in the exponents (the parent's truncation convention), argmin over m ∈ [2, 30]. Memory: relation store 2^{⌈n/m⌉} rows × (m⌈n/m⌉ + 2n) bits, log2-summed with the working set; dense = width² of the degree-≤4 Macaulay matrix in N = (m−2)n + km Boolean variables (width = Σ_{d≤4} C(N, d)); sparse = (nm)^4/24 columns × n^3/m nonzeros. Baseline (HEUR-VOW-CURVE): W = 0.886·2^{n/2}, T = W(1/M + 1/w), Mem = 3n·max(w, M) bits.

The per-row bit width of the relation store is NOT stated in any record I had read; `rederive_pre_code.py` evaluated three conventions (none / 2^k bits / 3n·2^k bits) and only `3n·2^k` reproduces the parent's five sparse cells to ≤ 4e-5 bits (the others miss n = 571 sparse by 4.5e-4). That convention is what `own_rederivation.py` had already used. It is disclosed rather than chosen silently; it does not move any crossover below.

| quantity | expected (gate / plan) | mine (blind) | run |
|---|---|---|---|
| time-only crossover, dense / sparse, record point | 303 / 303 | 303 / 303 | 303 / 303 |
| product crossover, record point (M = 1, w = 2^30), dense / sparse | 435 / 375 | 435 / 375 (persistent; first crossing is n = 3, the low-n artefact) | 435 / 375 |
| product crossover, own-curve minimum (w = M = 1), dense / sparse | 520 / 460 | 520 / 460 | 520 / 460 |
| margins at n = 409: time-only / product-dense / product-sparse (record) | 37.78 / −8.79 / 11.52 | 37.7816 / −8.7946 / 11.5175 | 37.781583 / −8.794616 / 11.517467 |
| margins at 409, own-curve: dense / sparse | −37.79 / −17.48 | −37.7946 / −17.4825 | −37.7946 / −17.4825 |
| shift record → own-curve, in n / in bits | +85 / −29.0 | +85 (both readings) / −29.0 | +85 / −29.0 |
| record-point excess over 6nW at 163 / 233 / 283 / 409 / 571 | 29.0 each | 29.000000 each | 29.0 each |
| T×Mem − 6nW along the ray w = M at log2 M ∈ {0, 10, 13.3, 20, 30, 40} | 0 | 0.000000 at every point | (ARM B invariance) |

The `6nW` minimum: on w = M, T = 2W/M and Mem = 3nM, so T·Mem = 6nW independent of M — reproduced. Off the ray, (M, w) = (2^0, 2^30) or (2^30, 2^0) both give exactly +29.0 bits = 30 − 1: the record point pays 2^30 of memory for a 1-bit time saving over w = M = 1.

### M1(2) Twelve surface cells recomputed

`validate_surface.py` (`M1_twelve_cells`) recomputes 12 cells chosen across all five metric families, store ∈ {0, 20, 30, 48, 60}, processors ∈ {0, 20, 40}, all three charging modes, κ ∈ {1, 10, 100}, h ∈ {1, 2, 4}, all four storage readings, both k readings and both m selections, from raw-result.json's per-cell record and my own `own_model.py`. Every crossover (first, persistent, parent-window), every `semaev_cheaper_intervals` list and every m agrees exactly; **worst margin disagreement 4.85e-5 bits** (the run's printing precision). `check_surface.py` recomputed a different 12 with the same result (worst 4.87e-5). Twelve of the 24 cells, one line each:

| metric | store | p | mode | κ | h | reading | k | m_sel | persistent (mine = run) | margin@409 (mine = run) |
|---|---|---|---|---|---|---|---|---|---|---|
| time_only | 30 | 0 | record | 1 | 1 | dense | unceiled | argmin | 303 | 37.7816 |
| product | 30 | 0 | record | 1 | 1 | sparse | unceiled | argmin | 375 | 11.5175 |
| product | 30 | 0 | own_curve | 1 | 1 | dense | unceiled | argmin | 520 | −37.7946 |
| product | 60 | 20 | record | 10 | 2 | rows×cols | ceil | reopt | 320 | 32.2166 |
| α = 0.5 | 48 | 40 | sect113r2 | 100 | 4 | nnz+index | unceiled | argmin | 331 | 27.1666 |
| α = 0.811 | 0 | 0 | record | 1 | 1 | dense | ceil | argmin | 466 | −15.6194 |
| hard[70] | 20 | 0 | record | 1 | 1 | sparse | unceiled | reopt | none | 37.7816 |
| hard[89] | 40 | 20 | own_curve | 10 | 1 | dense | unceiled | reopt | none | semaev_infeasible |
| soft[40] | 10 | 0 | record | 1 | 4 | sparse | ceil | argmin | 361 | 19.4768 |
| soft[65] | 30 | 40 | sect113r2 | 100 | 1 | rows×cols | unceiled | reopt | 402 | 2.6749 |
| product | 0 | 40 | own_curve | 100 | 2 | nnz+index | ceil | argmin | 397 | 8.4259 |
| α = 1.0 | 48 | 0 | record | 10 | 1 | sparse | ceil | reopt | 297 | 42.0597 |

### M1(3) Collision pairs

My recount from surface.json: **1,556,684** pairs of cells sharing (metric, reading, k reading, κ, h, m selection) and the same non-null persistent crossover — equal to the run's count. Counting null crossovers as a shared value would give 3,850,388; the run's definition (non-null only) is the sensible one and is the one it states.

Classification of 20 pairs. `check_surface.py` drew 20 with a seeded `random.sample` over all metric families (`M1_3_sample_20`): **9 "genuinely different curves sharing a crossover"** (margins at 409 differ by 1e-6 to 3e-3 bits — two distinct (store, processors) operating points whose integer crossover coincides, i.e. the ⌈n/m⌉/integer-n saw-tooth pinning, not two mechanisms), **8 "axis does not act"** (store under own_curve / sect113r2 modes; store under a budget metric that caps it), **3 "exact cancellation"** (store and processors shifted together under the record product where the working set dominates). `validate_surface.py` drew a second 20 from a stream that happened to be all `time_only` groups: 20/20 inert-axis (store is a labelled axis that does not act under time_only). **Zero of 40 sampled pairs are two mechanisms reaching one number.** The Coordinator's prior — reproducible but uninformative — is confirmed; the 9 "saw-tooth" pairs are the nearest thing to the interesting kind and they are coincidences of integer rounding, with margins that differ.

### M1(4) Determinism

(a) My sha256 of each retained artifact equals both the `sha256_execution_1` and `sha256_execution_2` values in `determinism-check.json` for all 10 JSON files (`check_surface.json` → `M1_4_determinism.all_match = true`). The producer deleted its second-execution copies after hashing, so those hashes alone would be self-report. (b) I therefore **re-executed `run_all.py` myself** into `scratch/rerun_determinism/` (two further executions, 45.6 s compute, peak RSS 1.04 GB): every arm/surface/controls JSON — `arm-b`, `arm-f`, `arm-n`, `controls`, `measurement-comparison`, `raw-result` (21.9 MB), `reproduction-gate`, `sensitivities`, `sparse-implementation-comparison`, `surface`, and even `determinism-check.json` — is **byte-identical** to the committed run (`scratch/rerun_determinism_hashes.json`); only `resources.json` differs (timings). The identical copies were deleted after hashing to avoid archiving a 23 MB duplicate; the hash file, `stdout.log` and `determinism-check.json` are kept.

**Unexpected observation (M1).** None material. The gate's 4.8e-5-bit residual is the printing precision of the compared records, as the plan said.

**Verdict M1: holds.** Artifacts: `scratch/own_rederivation.{py,json}`, `scratch/rederive_pre_code.{py,json,stdout.txt}`, `scratch/check_surface.{py,json}`, `scratch/validate_surface.{py,json,stdout.txt}`, `scratch/rerun_determinism_hashes.json`.

---

## M2 — the store-versus-metric range claim (H-SEMBIN-97ea23 C2)

Recomputed from surface.json at (processors = 1, κ = 1, h = 1, record_point_M1_w30, unceiled k, stage1_argmin): the crossover under time_memory_product at store ∈ {30, 40, 48, 60} (the parent's declared grid), and the crossover at store 30 over (a) the parent's metric set {time_only, time_memory_product} and (b) this contract's full 28-metric set (nulls excluded). Three crossover definitions. `validate_surface.json` → `M2_ranges`; my own recompute of the persistent values from `own_model.py` agrees cell-for-cell (`M2_independent_recompute`).

| reading | crossover definition | range over store {30,40,48,60} (values) | range over parent metric set | C2 vs parent set | range over full metric set | C2 vs full set |
|---|---|---|---|---|---|---|
| dense_row_echelon | persistent | 93 (435, 406, 382, 342) | 132 | **false** | 162 | false |
| dense_row_echelon | first crossing | 0 (3, 3, 3, 3) | 300 | false | 462 | false |
| dense_row_echelon | parent window 250–650 | 93 (435, 406, 379, 342) | 132 | false | 162 | false |
| semaev_sparse | persistent | 96 (375, 344, 319, 279) | 72 | **true** | 103 | **false** |
| semaev_sparse | first crossing | 0 (3, 3, 3, 3) | 300 | false | 403 | false |
| semaev_sparse | parent window | 96 | 72 | true | 103 | false |
| rows_times_cols_dense | persistent | 96 (376, 346, 321, 280) | 73 | true | 105 | false |
| rows_times_cols_dense | first crossing | 0 | 300 | false | 405 | false |
| rows_times_cols_dense | parent window | 96 | 73 | true | 105 | false |
| nonzeros_with_index_sparse | persistent | 96 (344, 314, 288, 248) | 41 | true | 390 (10 nulls in set) | false |
| nonzeros_with_index_sparse | first crossing | 0 | 300 | false | 372 | false |
| nonzeros_with_index_sparse | parent window | 94 (344, 314, 288, 250) | 41 | true | 72 | true |

All persistent-crossover numbers equal the run's ARM S figures (manifest `arm_S_...`: 93/132/162; 96/72/103; 96/73/105; 96/41/390). Over the full store grid {0,…,60} the ranges are 180 / 183 / 184 / 184.

Points the plan asked for:

1. **Persistent versus first crossing.** The Coordinator expected a move of < 10 in n. It is much larger and it is not a saw-tooth effect: with store ≥ 30 the record-point baseline pays 2^30·3n bits of memory at every n, so at n = 3..9 Semaev's product cost is below it and the FIRST crossing is n = 3 for every store ≥ 30 and every reading. Under the first-crossing definition the store range is 0 and the metric range is 300, so **C2 is false for every reading under first-crossing** — but that definition is dominated by the low-n artefact the contract's C8 labels, and it is the parent window (250–650) and the persistent definition that carry the run's figures. The parent-window definition moves the dense store-48 cell by 3 (379 vs 382: Semaev is cheaper on [379, 380], loses at 381, wins from 382) and nonzeros-with-index store-60 by 2; no ordering flips.
2. **Which metric set the wording names.** H-SEMBIN-97ea23 C2: "Over the store values the parent contract itself declared, the sparse crossover ranges more widely than it does over the whole metric set." The falsification criterion: "range over the parent contract's own declared store values does not exceed its range over the metric set." The store grid is explicitly the PARENT's; "the whole metric set" is unnamed. The parallel construction reads most naturally as the parent's metric set (the object the parent record published a crossover per metric for), under which the claim is 96 > 72 and holds. Read as this contract's own full set, the claim is 96 < 103 and fails. **The hypothesis does not say which; the contract's falsification criterion does not either.** That is a wording defect, and the claim's truth value depends on it.
3. **Contract's sparse criterion versus the unqualified statement.** The contract's falsification wording ("for the sparse reading") is satisfied against the parent set (96 > 72). The hypothesis's own statement is ALREADY qualified — it says "the sparse crossover", not "the crossover" — so "the store is the larger parameter" without the qualifier is the plan's paraphrase, and it is **false for dense_row_echelon under every crossover definition and both metric sets** (93 < 132; 93 < 162). Across the four readings: true for three against the parent set, false for all four against the full set (except the nonzeros-with-index parent-window cell, where 10 nulls in the full set shrink its range to 72 < 94).

**Unexpected observation (M2).** The dense_row_echelon ordering is reversed not because the store range is small (93, comparable to the other readings' 96) but because the dense working set is so large that the product metric moves the crossover 132 in n from time_only; the "which parameter is larger" question is therefore decided by the storage reading's size, i.e. by C10's data (M3), not by the store.

**Verdict M2: holds as a measurement — the ranges are what the surface says and reproduce exactly; the plan's own attack on the crossover definition breaks the claim under first-crossing and the wording's unnamed metric set leaves C2 true for (sparse, parent set) and false for (sparse, full set) and for dense under both.** Recorded as `holds` on the joint's reproduction question with the table above carrying C2's truth value per cell; the Coordinator's prior on M2 (reading- and metric-set-dependent; ordering not flipped by the definition) is confirmed on the first two points and **overturned on the third**: first-crossing does flip every ordering, by 300 versus 0, for the artefact reason stated. Artifacts: `scratch/validate_surface.json` (`M2_ranges`, `M2_independent_recompute`), `scratch/check_surface.json` (`M2_ranges`, `M2_own_recompute`).

---

## M3 — controls C3, C4, C10

### M3(1) C3 informative-null decomposition

Recomputed with `own_model.py` at store 0 (informative null: baseline memory = 3n bits, log2 = 10.26 at n = 409) and store 30 (record), record_point mode, p = 0, κ = h = 1, stage1_argmin, unceiled k (`validate_surface.json` → `M3_C3_decomposition`):

| reading | time_only | null (3n) | record (2^30) | step 1: Semaev's memory | step 2: baseline store | net | step 1 bits @409 | step 2 bits @409 | sums |
|---|---|---|---|---|---|---|---|---|---|
| dense_row_echelon | 303 | 522 | 435 | **+219** | **−87** | **132** | **−76.58** | **+30.00** | yes |
| semaev_sparse | 303 | 462 | 375 | +159 | −87 | 72 | −56.26 | +30.00 | yes |
| rows_times_cols_dense | 303 | 464 | 376 | +161 | −88 | 73 | −57.16 | +30.00 | yes |
| nonzeros_with_index_sparse | 303 | 432 | 344 | +129 | −88 | 41 | −45.82 | +30.00 | yes |

(Under ceil_n_over_m the dense triple is 287 → 505 → 430: 218 / −75 / 143.) The margins at 409: null −38.79, record −8.79 (dense) — the run's `informative_null_store0_3n_bits.margin_409_bits = −38.7946`, `record_store30 = −8.7946`. Step 2 is exactly 30.0 bits = log2(2^30) because the baseline's 3n unit is common to both. The baseline-store contribution (−87 in n, 30 bits) is not near zero, which is what the run reports. Zero-memory comparator: under time_memory_product the baseline's metric cost is log2(0) = −∞, so Semaev never wins — **DEGENERATE**, labelled so by the run; under fixed_budget_hard[70] and fixed_budget_soft[40] it is numerical (204.33 = the baseline's time; memory −∞ satisfies any budget) and the run says so (`M3_zero_memory_comparator`). The correction EV-SEMBIN-71e5cd O-10 demanded is present.

### M3(2) C4 and the criterion moved between attempts

stdout.log retains attempt 2's C4 line only as `C4 free-yield: all moved down = False` (three times, lines 43/86/128) — attempt 2's per-cell list was NOT retained; attempt 3's arm files overwrote attempt 2's. So the "eight failures" cannot be read from the log; they can only be reconstructed. The run of record's `controls.json` → `C4_known_false_free_yield` lists `floor_pinned = 8` and `m_selection_interactions = 1`, and I recomputed every C4 cell (40 metric×reading×m_selection cells × 2 crossover fields) with `own_model.py`, deleting exactly log2(m!) + (n − mk) from stage 1 and re-taking the argmin (`validate_surface.json` → `M3_C4_free_yield_at_record_point`):

| cell (record point, time_memory_product) | first crossing with / free | persistent with / free | margin@409 with → free | my verdict |
|---|---|---|---|---|
| dense / stage1_argmin | 3 / 3 | 435 / 339 | −8.79 → +27.73 | floor-pinned; persistent moved down 96; margin toward Semaev |
| dense / metric_reoptimised | 3 / 3 | 433 / 339 | −7.69 → +27.73 | floor-pinned; moved down; toward Semaev |
| sparse / stage1_argmin | 3 / 3 | 375 / 265 | 11.52 → 55.97 | floor-pinned; moved down 110; toward Semaev |
| sparse / metric_reoptimised | 3 / 3 | 375 / 265 | 11.67 → 55.97 | floor-pinned; moved down; toward Semaev |
| rows×cols / stage1_argmin | 3 / 3 | 376 / 282 | 10.62 → 50.22 | floor-pinned; moved down; toward Semaev |
| rows×cols / metric_reoptimised | 3 / 3 | 376 / 282 | 11.29 → 50.22 | floor-pinned; moved down; toward Semaev |
| nnz+index / stage1_argmin | 3 / 3 | 344 / 237 | 21.96 → 67.62 | floor-pinned; moved down; toward Semaev |
| nnz+index / metric_reoptimised | 3 / 3 | 344 / 237 | 21.96 → 67.62 | floor-pinned; moved down; toward Semaev |

These eight are exactly the `first_crossing_n` field of the eight time_memory_product cells, and in every one the with-factor first crossing is ALREADY n = 3 (the low-n artefact at which Semaev's product cost is below the 2^30-store baseline), so "did not move down" is unsatisfiable, while the persistent crossover moves down by 94–110 and the 409 margin moves toward Semaev by 36–46 bits. **All eight are genuinely floor-pinned; none hides a sign inversion.** All 32 time_only, product-persistent and feasible budget cells move down (time_only: 303 → 197 for every reading, margin 37.78 → 86.58).

m_selection interaction: at n ∈ {303, 409, 571} deleting log2(m!) moves the stage-1 argmin from 10/11/12 to **m = 30** (the top of the grid) for all readings; at n = 409 the m = 30 memory is 99.11 (dense), 70.87 (sparse), 76.63 (rows×cols) bits, all **> 70**, so under fixed_budget_hard[70] the stage1_argmin free-yield cell is infeasible rather than more expensive (`M3_C4_free_yield_argmin_and_budget`). The run lists exactly one such interaction (hard[70] / rows_times_cols_dense / stage1_argmin, first crossing 303 → none) and its metric_reoptimised counterpart moves down 303 → 197 (margin 37.78 → 71.00 at m = 14). Verified.

**Is the refinement a correction or a criterion moved?** A correction. The moved criterion excludes only cells whose with-factor crossover is already at the domain floor and re-labels only cells where the free-yield argmin blows the hard budget; both conditions are checkable from the with-factor cell alone, neither depends on the free-yield result's sign, and the disclosed refinement (manifest PD-A, stdout line 133) is accurate. It would have been better to retain attempt 2's per-cell list; its absence is why the reconstruction above was necessary.

**Unexpected observation (M3-C4).** Two cells the run scores as `moved_down: true` on the first crossing have a 409 margin that moves AGAINST Semaev by becoming infeasible: hard[70] / semaev_sparse / stage1_argmin (37.78 → semaev_infeasible, because the free-yield argmin m = 30 has sparse memory 70.87 > 70) and hard[70] / rows_times_cols_dense / stage1_argmin (the listed interaction). The run's criterion records `margin_409_improved: null` for a non-numeric margin and so does not score it. This is the same m_selection interaction, not a sign inversion of the cost model, but the run's C4 block labels only one of the two.

### M3(3) C10 residuals

`validate_c10.py` re-parses `tables.yaml` (12 Table 1 rows + 21 Table 2 rows = **33**, not the contract's "34"; the run compares 33) and recomputes, for every row at its own (n, t, k) with N = (t−2)n + kt, the four working-set accountings and the residual model − measured under both MB readings (A: printed MB is a per-system peak; B: it is a total over 100 systems, i.e. A − log2 100 = A − 6.64). Neither reading is picked. Row-by-row against `measurement-comparison.json`, keyed on (table, n, t, k, printed MB): **worst disagreement 0 bits at 4 decimals in every field** (nvars, Macaulay width, both measured values, all four model values, all eight residuals). (My first keying without the MB collapsed the four (17, 3, 6) Table 1 rows and reported a spurious 0.97-bit "disagreement"; the re-keyed check is in `validate_c10.stdout.txt`'s follow-up and above.)

| accounting | reading A: rows exceeded / 33 | reading A residual min..max | reading B: rows exceeded | reading B residual min..max | upper-bounds every row? |
|---|---|---|---|---|---|
| dense_row_echelon | 11 | −16.34 .. +6.99 | 5 | −9.69 .. +13.63 | A: no; B: no |
| semaev_sparse | 30 | −5.62 .. +1.16 | 0 | +1.02 .. +7.80 | A: no; **B: yes** |
| rows_times_cols_dense | 33 | −15.46 .. −0.17 | 6 | −8.81 .. +6.47 | A: no; B: no |
| nonzeros_with_index_sparse | 33 | −6.19 .. −2.05 | 0 | +0.45 .. +4.60 | A: no; **B: yes** |

Identical to the run's `upper_bound_check_per_reading`. Dense-minus-sparse gap (working sets, same row): at the measured scale (N ≈ 30–60) it ranges from **−14.1 to +9.7 bits** (negative where t = 2, where the sparse formula's n³/t exceeds the tiny dense width; +6.3 to +9.7 at t = 4–6); at the labels with the run's argmin m: 15.07 (163), 17.77 (233), 18.07 (283), **20.31 (409)**, **21.50 (571)**.

**What the data says about the dense reading, in one sentence:** the dense_row_echelon accounting — the reading on which the parent's n = 409 verdict rests — is BELOW the printed MAGMA measurement in 11 of 33 rows under reading A and in 5 of 33 under reading B (by up to 16.3 and 9.7 bits), so it is not an upper bound on the only measurements that exist under either reading of the column, while both sparse accountings upper-bound every row under reading B and none does under reading A. The contract's failure_meaning ("NO accounting upper-bounds under EITHER reading") **did not fire**: two accountings upper-bound under reading B.

Caveat I must state: the model rows use the table's t for m (chain length as arity, as the run does) and count the working set only, without the relation store; the rows with t = 2 have N = kt ≤ 24 variables and the dense width² there is tiny, which is why dense sits below the measurement mostly at t = 2 and at the largest N (n = 40, t = 2). This is a comparison of a cryptographic-scale formula against N ≤ 60 measurements and transfers only as the run states (none claimed).

**Verdict M3: holds** — the decomposition sums with DEGENERATE labelled; the eight attempt-2 "failures" are floor-pinned and the refinement is a correction, with the two-cell criterion gap above recorded; the C10 residual table matches to 4 decimals and the dense reading does not upper-bound the measurements under either reading. The Coordinator's prior on M3 is confirmed on all three points. Artifacts: `scratch/validate_surface.json` (`M3_*`), `scratch/validate_c10.{py,json,stdout.txt}`.

---

## M4 — budget bands and alpha flips (H-SEMBIN-97ea23 C3)

### M4(1) Semaev's cheapest memory over m at n = 409 (blind)

From the memory formulas with relation store 3n·2^k bits (k = ⌈n/m⌉) log2-summed with the working set (`own_rederivation.json` → `M4_1`; `rederive_pre_code.json` → `M4_cheapest_memory_over_m_at_409`; `validate_surface.json` → `M4_cheapest_memory_over_m_at_409_run_convention`):

| reading | cheapest m | cheapest memory (bits) | m within 1 bit | run |
|---|---|---|---|---|
| dense_row_echelon | **6** | **80.07** (store 79.27 ⊕ working set 78.86) | 6, 7 | 80.0685 at m = 6 |
| semaev_sparse | **8** | **65.33** (store 62.27 ⊕ working set 65.15) | 8, 9, 10 | 65.3308 at m = 8 |
| rows_times_cols_dense | 8 | 64.64 | 8, 9 | 64.6416 at m = 8 |
| nonzeros_with_index_sparse | 10 | 55.83 | 10–13 | 55.8289 at m = 10 |

The plan's "62.31 bits at m = 4 (sparse)" is **not** the n = 409 figure: 62.3118 at m = 4 is arm-f's cheapest DENSE memory at **n = 163**. At n = 409 the sparse cheapest is 65.33 at m = 8 (and the contract's own predicted 65.33 at m = 8 / 80.07 at m = 6 is what re-derives). Note the structure: at m = 8 the RELATION STORE (2^52 rows × 1227 bits = 62.27) is already within 3 bits of the sparse working set, and for m ≤ 7 the store (k ≥ 59) dominates entirely; the cheapest-memory m is set by the store–working-set trade, not by the working set alone. Without the relation store the cheapest sparse memory would be 59.15 at m = 2 (rederive_pre_code, convention "none"), so the band's lower edge is a relation-store fact as much as a working-set fact.

### M4(2) Hard-budget flips at n = 409

Hard semantics (from the code, read after M4(1)): the baseline shrinks w and M to fit (room = B − log2 3n; p_eff = min(p, room); w_eff = min(store, room)); Semaev's cost is T if Mem ≤ B else ∞; at the arm's slice p = 0 the baseline's time is W(1 + 2^{−w_eff}) ≈ 204.33 at every B ≥ 10.26. Semaev wins at the first B at which SOME m has Mem ≤ B and T(m) < 204.33; the m attaining the cheapest memory has T well below that (181.77 at m = 6 dense, 174.84 at m = 8 sparse; small m are ruled out by time — stage 2 alone is 2^{2n/m}, 2^409 at m = 2 — but those m also carry the largest relation stores, 92–215 bits, so they never fit first), so the flip is exactly Semaev's cheapest memory over m:

| reading | my flip (bits) | run | budgets on the grid |
|---|---|---|---|
| semaev_sparse | **65.33** (turns first) | 65.3308 | vOW at 30–65, Semaev at 70–90 |
| dense_row_echelon | **80.07** | 80.0685 | vOW at 30–80, Semaev at 89, 90 |
| rows_times_cols_dense | 64.64 | 64.6416 | — |
| nonzeros_with_index_sparse | 55.83 | 55.8289 | — |

Band dense vs sparse: **65.33–80.07**, width 14.74, sparse turns first — matches the run to < 1e-3 bits under both blind conventions (`M4_hard_budget_flips_at_409`, "w_fills_budget" and "w = M = 1" give the same flips because at p = 0 the baseline's time is B-independent). A third convention I tried (M = w both filling the budget) never flips, because it hands the baseline 2^{room} processors; it is not the contract's semantics and is recorded only to show the flip depends on the baseline being held at p = 0.

### M4(3) Soft semantics — what it is

From `surface_cost.py` `metric_cost`: `fixed_budget_soft[B]` = T + max(0, Mem − B) in log2, i.e. **cost = T × max(1, Mem/B)**; the baseline is still shrunk to fit (its penalty is always 0), Semaev may exceed and is charged the exceedance RATIO multiplicatively. Recomputed flips at 409 with m re-optimised under the metric: **sparse 28.59, dense 47.95** (`M4_flip_budgets_at_409`; run 28.5897 / 47.9533; own_curve mode gives 27.59 / 46.95, one bit lower because that baseline's time is W·2). Algebraically, at p = 0 the soft flip is B* = min_m (T_s + Mem_s) − T_v = Mem_v(record) − margin_product(409, metric-reoptimised m) = 40.26 − (−7.69) = 47.95 (dense) and 40.26 − 11.67 = 28.59 (sparse): **the soft band is the product metric's n = 409 margin re-expressed as a budget**, not an independent measurement.

Is it a budget in an operational sense? **No, not as a bound on memory**: at B = 2^28.59 bits (≈ 50 MB) the sparse Semaev cell that "wins" uses 2^66.5 bits and is charged 2^38 × its time for doing so; nothing prevents the exceedance, and the winner's memory is 2^38 over the "budget". It is a defensible PENALTY model (a threshold-linear multiplicative memory charge with the free allowance B), and H-SEMBIN-97ea23 C3's own wording — "any cost model that fixes a physical memory budget **rather than charging memory multiplicatively**" — arguably EXCLUDES it, since above B it charges memory multiplicatively. The contract's falsification criterion names the hard budget only. So the soft band is a legitimate row of the surface and a caveat C3 needs; it is not a second budget semantics on equal footing with the hard one.

### M4(4) Alpha flips at n = 409 (T × Mem^α, record point, stage1_argmin m = 11)

α* = (T_v − T_s)/(Mem_s − Mem_v) with T_v = 204.33, Mem_v = 40.26, T_s = 166.54:

| reading | Mem_s | my α* | run | inside [0, 1] |
|---|---|---|---|---|
| dense_row_echelon | 86.84 | **0.8112** | 0.8112 | yes |
| semaev_sparse | 66.53 | **1.4385** | 1.4385 | no |
| rows_times_cols_dense | 67.42 | 1.3912 | 1.3912 | no |
| nonzeros_with_index_sparse | 56.09 | 2.3875 | 2.3875 | no |

Blind values 0.8112 / 1.4385 from `rederive_pre_code.json`; at the own-curve baseline point the flips move to 0.51 (dense) and 0.69 (sparse) — both inside [0, 1] — which is the coherent-baseline version of the same fact and is reported for completeness (it is a cell of the surface, not a claim of the hypothesis).

### M4(5) C3's truth value

| semantics | dense/sparse disagreement band at 409 | C3 "agree below 2^65" | margin |
|---|---|---|---|
| hard (wall; the contract's falsification wording) | 65.33–80.07 | **true** | **0.33 bits** — a knife-edge, as the plan says |
| soft (T × max(1, Mem/B); a penalty, not a bound) | 28.59–47.95 | **false** — the readings disagree at every budget in 2^28.6–2^47.9, inside realisable budgets | — |
| hard, but across all four storage readings | dense vs rows_times_cols_dense: 64.64–80.07; dense vs nnz+index: 55.83–80.07 | **false by 0.36 bits** for the rows_times_cols_dense reading (flips at 64.64 < 65) | — |

The third row is not a reading of C3 the hypothesis makes (it names "the dense and sparse readings", i.e. dense_row_echelon and semaev_sparse), but it is the honest complement to "0.33 bits to spare": the third accounting the run itself carries crosses 2^65 from the other side by a comparable amount, so the "below 2^65" clause is a property of which two readings are compared, at the ±0.35-bit level.

**Unexpected observation (M4).** The plan's cheapest-memory figure (62.31 at m = 4) was the n = 163 dense value; corrected above. No band boundary moved by more than 1e-3 bits under my recomputation.

**Verdict M4: holds** — the hard band 65.33–80.07 and the soft band 28.59–47.95 re-derive to < 1e-3 bits, the cheapest-m values re-derive, the alpha flips re-derive to 1e-4; C3 holds under hard by 0.33 bits and does not hold under soft, and the soft semantics is a threshold-multiplicative penalty rather than a budget. The Coordinator's prior on M4 is confirmed, with its m = 4 / 62.31 detail corrected and the rows_times_cols_dense 64.64 edge added. Artifacts: `scratch/own_rederivation.json` (`M4_1`), `scratch/rederive_pre_code.json` (`M4_*`), `scratch/validate_surface.json` (`M4_*`).

---

## M5 — the unreached prime-field control and ARM I's independence

### M5(1) EXP-ICEX-c32447's specification, read myself

`experiments/EXP-ICEX-c32447/` contains only `specification.yaml` (status `draft`, no `runs/` directory). For the four pieces `arm-n-prime-field-control.json` names as missing:

| piece | what ICEX states | closed form the producer missed? | carries a memory term? | my verdict |
|---|---|---|---|---|
| C_LA and C_descent | metrics "charged GROUP OPERATIONS, per (N, B, m, seed)", read off an instrumented exhaustive solver at N ∈ [2^20, 2^30] (lines 164–170) | **none** — measured counters only | no | missing, as stated |
| index-calculus memory | "peak memory, STORED GROUP ELEMENTS, per arm per cell (factor base plus relation matrix on the IC side)" (175–177); the control at 144–146 charges the IC arm "N^β stored elements" | **partial**: the FACTOR BASE is stated in closed form as N^β stored elements; the relation matrix is a measured peak; β is an admission parameter of a Stage-0 map, not a fixed number | the N^β term is a memory term, but incomplete and un-fixed | missing as a usable model; the producer's "declared as a measured counter, not a formula" understates the N^β term but the conclusion stands |
| multi-target rho with shared DP table | "the multi-target baseline sqrt(T·N)" is named as the shape the fit must reach (line 21); the arm itself is "MEASURED at T ∈ {1,4,16,64}" (84–85) and "measured here, not cited" (335); its DP-table memory is a measured peak | **partial**: sqrt(T·N) is a closed-form TIME shape; there is no closed-form memory for its table | time only | missing as a chargeable baseline; the producer's account omits the sqrt(T·N) shape but nothing about memory |
| extrapolation to cryptographic size | "TRANSFER ASSUMPTION — none is claimed … neither T = Θ(N) nor cryptographic N is reachable here" (207–209) | none | — | missing, as stated |

The one closed form the producer names — C_rel = m!·N·B^{(m−1)(σ−1)}, equal to m!·N at σ = 1, "INDEPENDENT OF B AND m" (193–197) — is there and has no memory term and no B-dependence at σ = 1, exactly as arm-n says. **No closed form that would make C6 instantiable was missed.** The producer's disclosure is slightly incomplete in two places (the N^β factor-base term; the sqrt(T·N) shape) and correct in its conclusion.

### M5(2) No substitution

`controls.json` → `C6_prime_field_nearby_object.status = UNREACHED` with the same four `missing` items; the surface's code tables contain three baseline modes (record_point / own_curve / sect113r2), four storage readings and 28 metrics, none prime-field; `surface.json` contains zero occurrences of "PFDR", "ICEX" or "prime"; `COST-SEMBIN-e9960c.yaml` mentions prime only to say C6 is UNREACHED (lines 1496, 1524). arm-n names the red team's PFDR object and says explicitly it was NOT charged. **No same-family object was substituted or counted as C6.** The consequence is stated in arm-n (`consequence`) and in the cost record: every row of this run AND of RUN-SEMBIN-121b59 is reported without the prime-field control.

### M5(3) Reachability

A reachable C6 needs a DESIGNED closed-form prime-field index-calculus cost model with a memory term (at minimum C_LA and the relation-matrix memory as functions of (N, B, m), plus a fixed β) and a multi-target rho baseline whose distinguished-point-table memory is a formula rather than a measured peak, then a Coordinator amendment naming that model as the C6 comparator — a design task, not a run; ICEX completing its own runs at N ≤ 2^30 would supply measured counters but, by its own transfer statement, no verdict at cryptographic N.

### M5(4) Sparse working set at n = 571, m = 12, before opening either implementation

From KN-LIT-e77232's statement alone: columns (nm)^4/24 = (6852)^4/24 = 2,204,293,485,609,216/24 = 91,845,561,900,384 → **log2 = 46.3843**; nonzeros per row n³/m = 186,169,411/12 → **log2 = 23.8871**; total (rows ≈ columns) = n^7 m^3/24 exactly → **log2 = 70.271354** (`own_rederivation.json` → `M5_4`, 07:04; `rederive_pre_code.json` → `M5_sparse_working_set_571_12`, exact rational check).

| quantity | KN-LIT-e77232 printed | mine | run `sparse_independent` | run `surface` | parent record 70.2718 |
|---|---|---|---|---|---|
| columns | 2^46.38 | 46.3843 | 46.384275 | — | — |
| nonzeros/row | 2^23.89 | 23.8871 | 23.887078 | — | — |
| total | 2^70.3 | **70.271354** | 70.271354 | 70.271354 | the parent's 70.2718 is total ⊕ relation store (k = 48: 58.74), +0.0004 bits — reproduced under the 3n·2^k convention |

Disagreement with both implementations: **0 bits at 6 decimals**; with KN-LIT's printing: 0 at printed precision; with the parent's 70.2718: 4.5e-4 bits, fully accounted for by the relation store. At the labels with the run's argmin m: 55.2782 / 59.9741 / 61.9374 / 66.5250 / 70.2714 — the run's `samples_at_fips_n` rows at (163,7), (233,9), (283,9), (409,11), (571,12) to 1e-6.

Then, having opened both: `sparse_independent.py` forms n^7 m^3/24 as an exact `Fraction` and takes log2 of numerator and denominator; `memory_charged_cost.py`'s `semaev_memory_log2` sums 4·log2(nm) − log2 24 + 3·log2 n − log2 m in floats. Same formula, two arithmetic routes; the 2.8e-14-bit agreement is float-versus-exact agreement of one formula. **PD-I's disclosure — that the parent's implementation was read in full before the "independent" one was written and that independence is therefore weaker than specified — is accurate**, and the contract's C7 (`sparse_working_set_second_implementation`, "independently written … agrees to within 0.01 bits") is discharged on arithmetic and not on modelling. My own derivation supplies the within-session blind check the plan asked for, with the temporal-not-structural independence the plan itself names (and the PD-V1 caveat above on which of my two derivations is the blind one).

**Unexpected observation (M5).** None beyond the two small omissions in arm-n's account of what ICEX does state.

**Verdict M5: holds** — the four missing pieces are real (two of them with partial closed forms that do not change reachability), nothing was substituted, the consequence is stated for both runs, and the sparse term re-derives from the statement to 1e-6 bits against both implementations. The Coordinator's prior on M5 is confirmed. Artifacts: `scratch/own_rederivation.json` (`M5_4`), `scratch/rederive_pre_code.json` (`M5_*`), arm-n and controls.json as read.

---

## proves_too_much

### Object 1 — time-only invariance across store and reading, at κ = h = 1, p = 0

Recomputed from raw-result.json for every store ∈ {0, 10, 20, 30, 40, 48, 60}, all four storage readings, all three baseline modes (`validate_surface.json` → `PTM1_*`; `check_surface.json` → `PTM1_time_only`):

| mode | crossover at every store, every reading | spread over store | spread over reading |
|---|---|---|---|
| record_point_M1_w30 | 303 (margin@409 37.7816) | 0 | 0 |
| sect113r2_calibrated_ratio | 303 (37.7817) | 0 | 0 |
| own_curve_product_minimum | 300 (38.7816) | 0 | 0 |

Under time_only the machinery charges no memory anywhere: the crossover is independent of store_log2 and of the storage reading at fixed mode, exactly as required. Across modes it moves by **3 units of n**, not the "one or two" the plan's object text estimated; the move is exactly the one disclosed bit (own_curve sets w = M = 1, T = 2W, one bit more than the record point's W(1 + 2^{−30})), and one bit at a local slope of (37.78 bits)/(409 − 303 n) ≈ 0.36 bits per unit n is 2.8 ≈ 3 units of n. The failure signature (> 2 units across store or reading at fixed mode) is not met: those spreads are 0.

### Object 2 — C4 free yield at the coherent mode (own_curve_product_minimum), both readings, both m selections, both k readings

Run by me, not by the producer (`validate_surface.json` → `PTM2_free_yield_at_coherent_mode`), under time_memory_product at store 30 (inert in this mode), p = 0, κ = h = 1, all four readings:

| reading | m_sel | k | crossover with → free (first / persistent) | margin@409 with → free | moved down / toward Semaev |
|---|---|---|---|---|---|
| dense | argmin | unceiled | 520 → 413 | −37.79 → −1.27 | yes / yes |
| dense | argmin | ceil | 493/501 → 413 | −29.30 → −1.64 | yes / yes |
| dense | reopt | unceiled | 518 → 413 | −36.69 → −1.27 | yes / yes |
| dense | reopt | ceil | 493/501 → 413 | −29.30 → −1.64 | yes / yes |
| sparse | argmin | unceiled | 460 → 342 | −17.48 → +26.97 | yes / yes |
| sparse | argmin | ceil | 433/441 → 343 | −8.26 → +26.61 | yes / yes |
| sparse | reopt | unceiled | 460 → 342 | −17.33 → +26.97 | yes / yes |
| sparse | reopt | ceil | 433/441 → 343 | −8.26 → +26.61 | yes / yes |
| rows×cols | argmin / reopt | unceiled / ceil | 462 / 441 → 357 | −18.4 / −9.6 → +21.2 / +20.8 | yes / yes (4 cells) |
| nnz+index | argmin / reopt | unceiled / ceil | 429 / 417 → 313 / 314 | −7.0 / +2.3 → +38.6 / +38.3 | yes / yes (4 cells) |

Sixteen cells; every crossover moves down (by 80–118 in n), every 409 margin moves toward Semaev (by 28–46 bits), none is floor-pinned at the coherent point (the own-curve baseline's product is 6nW, small at low n, so there is no low-n artefact and the first crossing equals the persistent one). No cell moves up, no margin moves against Semaev. The sign convention holds where the producer did not tune.

**Verdict proves_too_much: passed** (both objects; neither failure signature met). Artifacts: `scratch/validate_surface.json` (`PTM1_time_only_invariance`, `PTM1_across_readings_at_fixed_mode`, `PTM1_across_modes`, `PTM2_free_yield_at_coherent_mode`), `scratch/check_surface.json` (`PTM1_time_only`).

---

## Summary table

| joint | verdict | prior confirmed / overturned | most consequential number |
|---|---|---|---|
| M1 | holds | confirmed | every gate and coherent figure re-derives blind; 24 surface cells to 4.9e-5 bits; 1,556,684 pairs recounted; my own re-execution byte-identical (10/10 JSON) |
| M2 | holds (as reproduction); C2 truth value is a table | confirmed on reading/metric-set dependence; **overturned on crossover definition** (first-crossing flips every ordering: store range 0 vs metric range 300, low-n artefact) | sparse 96 vs 72 (parent set) vs 103 (full set); dense 93 vs 132 |
| M3 | holds | confirmed | 219 / −87 / 132; 8/8 floor-pinned; dense accounting below the measurements in 11/33 (A) and 5/33 (B) rows; gap 20.3 bits at 409 |
| M4 | holds | confirmed, with the plan's 62.31/m = 4 corrected to 65.33/m = 8 at 409 (62.31 is n = 163 dense) | hard band 65.33–80.07 (C3 by 0.33 bits); soft 28.59–47.95 is the product margin re-expressed and is a penalty, not a bound; rows×cols reading flips at 64.64 |
| M5 | holds | confirmed | 70.271354 bits from the statement, 0 bits from both implementations; ICEX states m!·N, sqrt(T·N) and N^β but no complete memory term |
| proves_too_much | passed | confirmed (3 units across modes, not 1–2, explained by the one disclosed bit) | time-only spread over store and reading = 0 at every mode; 16/16 coherent free-yield cells move down |

Limitations of this review: one session performed every joint (no structural independence between joints); the blind derivation's independence is temporal (PD-V1); the collision classification is 40 sampled pairs of 1.56 million; C10's model rows use t for m and omit the relation store, as the run does; nothing here was checked against the van Oorschot–Wiener paper, which no agent in this program has opened (manifest `heuristic_under_test`), so HEUR-VOW-CURVE is re-derived from its internal statement only.
