# Execution report — TASK-20260913-39f7a4 / EXP-SEMBIN-2c40bb / RUN-SEMBIN-3ae91c

Observations only. Nothing below is a statement about the security of any curve. Every crossover
quoted carries its cell label; where a label is fixed for a whole table it is stated once at the top
of that table. Unless stated otherwise: `processors_log2 = 0`, `kappa = 1`, `cofactor_h = 1`,
`k_reading = unceiled_n_over_m_as_in_table3`, `m_selection = stage1_argmin`, degree bound 4 (GIVEN),
omega 3.0, crossover = `persistent_crossover_n` over n in [3, 700].

## ARM R — reproduction gate: PASSED

Cell: `store_log2 = 30, processors_log2 = 0, baseline_charging_mode = record_point_M1_w30, kappa = 1,
cofactor_h = 1, k_reading = unceiled, m_selection = stage1_argmin`, parent window [250, 650].

| figure | this run | COST-SEMBIN-8d123b |
| --- | --- | --- |
| crossover time_only / dense, sparse | 303, 303 | 303, 303 |
| crossover product / dense, sparse | 435, 375 | 435, 375 |
| margin n = 409 time_only, product dense, product sparse | +37.7816, −8.7946, +11.5175 | +37.78, −8.79, +11.52 |

Largest disagreement vs the record: 4.82e-5 bits; vs `recomputations.json` step 0: 4.82e-5 bits
(both compared files print 4 decimals; this is their printing precision). `recomputations.json` was
read as data, not imported, and agreement with it is a comparison against this experiment's own input.

## ARM N — prime-field nearby-object control: UNREACHED

Concrete missing pieces (`arm-n-prime-field-control.json`): EXP-ICEX-c32447 defines `C_LA`,
`C_descent`, index-calculus memory ("peak stored elements") and the multi-target rho baseline with its
shared DP table as MEASURED counters with no closed form, and the experiment is `draft` with no runs; its
one closed-form term (`m! N B^(m-1)(sigma-1)` → `m! N` at sigma = 1) carries no memory and no B, so
charging it under the store grid tests nothing about memory charging; and its N range (2^20–2^30)
declares no transfer to the 2^256 scale C6 asks about. The PFDR model the red team located is a
different model and was NOT substituted (stopping rule 4). C6 is therefore not run and every row
below is reported without it.

## ARM S — the surface (254,016 cells in `raw-result.json`; grids in `surface.json`)

Crossover range over `store_log2` BESIDE range over the metric set, per storage reading, at
`baseline_charging_mode = record_point_M1_w30` (store sweeps under `time_memory_product`; metric sweeps
at `store_log2 = 30`):

| storage reading | store ∈ {30,40,48,60} | store full {0,10,20,30,40,48,60} | parent metric set {time_only, product} | full metric set (28 instances) | store(declared) > parent-metric range? |
| --- | --- | --- | --- | --- | --- |
| dense_row_echelon | 435, 406, 382, 342 → **93** | 522…342 → **180** | 303, 435 → **132** | 162 | **no** |
| semaev_sparse | 375, 344, 319, 279 → **96** | 462…279 → **183** | 303, 375 → **72** | 103 | **yes** |
| rows_times_cols_dense | 376, 346, 321, 280 → 96 | 464…280 → 184 | 303, 376 → 73 | 105 | yes |
| nonzeros_with_index_sparse | 344, 314, 288, 248 → 96 | 432…248 → 184 | 303, 344 → 41 | 390 (one budget cell at 693) | yes |

Under `k_reading = ceil_n_over_m`: dense 430/397/370/331 (range 99) vs parent metric set 287/430
(143); sparse 361/331/298/271 (90) vs 287/361 (74). Under `m_selection = metric_reoptimised`: dense
433/402/377/339 vs 303/433; sparse 375/344/318/279 vs 303/375.

Other one-axis ranges at store 30, product metric: processors_log2 {0,20,40} → dense 435/495/550,
sparse 375/434/491; baseline mode → dense 435/520/486, sparse 375/460/424; kappa {1,10,100} → dense
435/425/416, sparse 375/364/354 (time_only: 303/293/283); cofactor {1,2,4} → dense 435/436/438,
sparse 375/376/378 (time_only 303/304/305; baseline gets cheaper).

Low-n artefact (C8): under the product with the record baseline, Semaev is "cheaper" on n ∈ [3, 4]
(dense) / [3, 3] (sparse) and up to [3, 10] at store 60, because the baseline is charged a 2^30–2^60
store in a group of 2^3 elements; labelled in every cell's `semaev_cheaper_intervals`, and
`first_crossing_n` (3) is distinguished from `persistent_crossover_n` (435 / 375).

Collision pairs: 1,556,684 pairs of cells share a persistent crossover while differing in
(store, processors, mode); structural sources listed in `surface.json` (time_only ignores the store;
both coherent modes ignore the store; record-mode product depends on store − processors; budget metrics
cap the store). 400 labelled examples are exhibited.

## ARM B — coherent baseline (product metric, store 30, p = 0)

| storage | record | own_curve_product_minimum | sect113r2_calibrated_ratio | shift record→own (n, bits@409) |
| --- | --- | --- | --- | --- |
| dense_row_echelon | 435, −8.79 | 520, −37.79 | 486, −25.49 | +85, −29.0 |
| semaev_sparse | 375, +11.52 | 460, −17.48 | 424, −5.18 | +85, −29.0 |
| rows_times_cols_dense | 376, +10.62 | 462, −18.38 | 427, −6.08 | +86, −29.0 |
| nonzeros_with_index_sparse | 344, +21.96 | 429, −7.04 | 394, **+5.26** | +85, −29.0 |

With `m_selection = metric_reoptimised` (Semaev at the minimum of his own product): dense 433 → 518
(−36.69 at 409), sparse 375 → 460 (−17.33). vOW product excess of the record charge over the minimum of
its own product: 29.0 bits at every n (sect113r2 ratio: 12.30 bits). Semaev's product-minimising m at
409: dense 9 (within 1 bit: 8–10), sparse 10 (9–11); the stage-1 argmin 11 is inside the 1-bit band in
every reading.

## ARM F — fixed memory budget and alpha (record baseline, n = 409 unless stated)

| storage | Semaev cheapest memory (m; within 1 bit) | hard threshold | soft threshold |
| --- | --- | --- | --- |
| dense_row_echelon | 2^80.07 (m = 6; 6–7) | 2^80.07 | 2^47.95 |
| semaev_sparse | 2^65.33 (m = 8; 8–10) | 2^65.33 | 2^28.59 |
| rows_times_cols_dense | 2^64.64 (m = 8; 8–9) | 2^64.64 | 2^28.97 |
| nonzeros_with_index_sparse | 2^55.83 (m = 10; 10–13) | 2^55.83 | 2^18.30 |

Dense-vs-sparse disagreement band at 409: hard **[2^65.33, 2^80.07]** (width 14.74 bits, sparse turns
first); soft **[2^28.59, 2^47.95]**. Over the declared grid, hard: both vOW at ≤ 2^65, sparse Semaev
from 2^70, dense Semaev from 2^89. At n = 571: sparse 2^69.90 (m = 11), dense 2^86.66 (m = 8); soft
thresholds fall below 3n bits (Semaev already wins time-only there).

Alpha flip at 409 (`T · M^alpha`, stage1_argmin m): dense **0.8112** (metric-reoptimised scan: first
loss at 0.828); semaev_sparse alpha* = 1.44, rows_times_cols 1.39, nonzeros_with_index 2.39 — no flip in
[0, 1] for any non-dense reading.

## ARM I — independent sparse working set

Largest cell-wise disagreement over n ∈ [3, 700], m ∈ [2, 30] (19,894 cells): **2.84e-14 bits** (at
n = 215, m = 28; float rounding). n = 571, m = 12: columns 2^46.384, nonzeros/row 2^23.887, total
2^70.271 — agrees with KN-LIT-e77232's 46.38 / 23.89 / 70.3 at printed precision. Independence is
weakened (PD-I below).

## Controls (all ten, stated separately)

- C1 reproduction gate: passed (above).
- C2 Table 3: 36/36 cells under the parent's truncation convention (printed 3-s.f. mantissa vs recomputed mantissa floored to 2 decimals, exponent exact); 35/36 within 0.7% relative (the miss is 0.704%); argmin m = 10/11/12 at 310/409/571; paper's-own-convention crossover 302. Passed.
- C3 informative matched null: decomposition in n, product metric — dense: time_only 303 → informative null (3n-bit baseline) 522 (+219) → record 435 (−87); sparse 303 → 462 (+159) → 375 (−87); rows×cols +161/−88; nz-index +129/−88. Baseline-store contribution is 30.0 bits, **not near zero**. Zero-memory comparator under product and alpha metrics: **DEGENERATE** (−inf), reported as such, never as a share; under the budget metrics it is a feasible baseline and is reported numerically with that note.
- C4 free-yield: passed — every crossover moves down or is pinned at the domain floor n = 3 with the n = 409 margin moving in Semaev's favour (+36 to +46 bits); one cell (hard budget 2^70, rows×cols, stage1_argmin) is an m-selection interaction (deleting log2 m! moves the stage-1 argmin to m = 30, which blows the budget); its metric_reoptimised counterpart moves down. 0 genuine failures in 80 rows.
- C5 eq.(4): passes by 1957 / 3432 / 5977 bits at 310 / 409 / 571. Typo detector only; not counted as a validity check.
- C6 prime-field nearby object: UNREACHED (ARM N).
- C7 independent sparse working set: 2.84e-14 bits; n = 571 check agrees; independence weakened (PD-I).
- C8 full scan domain: n from 3; artefact labelled; first vs persistent crossings distinguished in every cell.
- C9 invalid input: all seven cases rejected with an error (m < 2, m > n, t > m, non-integer n, negative store, budget below 3n bits, kappa ≤ 0).
- C10 measurements (33 rows with a MB figure in Tables 1–2, both readings, neither picked): reading A (MB = per-system peak): no accounting upper-bounds every row (dense exceeds 11 rows, min residual −16.3 bits; semaev_sparse 30 rows; rows×cols 33; nz-index 33). Reading B (MB = total over 100 systems): semaev_sparse and nonzeros_with_index upper-bound every row (min residuals +1.02, +0.45 bits); dense_row_echelon and rows×cols do not (5 and 6 rows exceeded). Dense−sparse gap widens from 6.5–9.7 bits at N ≈ 50 to 15.1 / 17.8 / 18.1 / 20.3 / 21.5 bits at n = 163 / 233 / 283 / 409 / 571.

## Preregistered predictions, each answered

1. `reproduction_gate` 303/303/435/375, +37.78/−8.79/+11.52 — **met**.
2. `coherent_baseline` 460 / 520, −17.48 / −37.79, shift 85, excess 29.0 — **met** (stage1_argmin; 518 dense with metric-reoptimised m).
3. `store_vs_metric_range` sparse declared 96, metric 72, full-grid dense 180, sparse 183 — **met** (persistent crossover).
4. `budget_band` 65.33 / 80.07, m 8 sparse / 6 dense — **met**; the Coordinator's prior that the band would come out narrower than 2^65–2^89 is answered: the upper boundary is 2^80.07 (dense feasible-and-winning at m = 6), narrower than 2^89.
5. `alpha_flip` dense 0.811, sparse none in [0, 1] — **met** (0.8112; sparse alpha* = 1.44).
6. `matched_null` 219 / 159 / −87 / 132 / 72 — **met**.
7. `cofactor` shift per h [0, 1, 3], direction baseline cheaper — **met** for sparse product (375/376/378) and dense (435/436/438); time-only shifts 0/1/2.
8. `sect113r2_calibrated` 486 / 424 / −5.18 — **met**.
9. `all_corrections_B409` 481 / 421, −24.80 / −3.76 — **not evaluable at its own cell and missed at the nearest ones**: the red team's S4 combination charges a unit conversion of 2^5 (kappa = 32), which is not on the declared kappa grid, and the predicted figures also differ from S4 itself (481/430, −25.30/−4.26). Nearest declared cells (own-curve, ceiled k, h = 2): kappa 1 → 501 / 441 (−29.80 / −8.76); kappa 10 → 501 / 441 (−26.48 / −5.44); kappa 100 → 481 / 430 (−23.16 / −2.12). A 0.5-bit offset against the red team's S6 (same cell at kappa 1: 496 / 441, −30.30 / −9.26) is present and is consistent with a different cofactor charge convention (this run: −0.5 log2 h); not resolved here.

## Falsification criterion of H-SEMBIN-97ea23 (data only, no verdict)

C2 of the hypothesis is falsified if the sparse reading's crossover range over {30, 40, 48, 60} does
not exceed its range over the metric set: measured 96 vs 72 (parent metric set) — the store range is the
larger. For the dense reading the store range (93) is smaller than the parent metric range (132). C1 of
the hypothesis is falsified if the coherent baseline moves the crossover by less than 50 in n or leaves
a crossover at or below 409: measured +85 in n, crossovers 460 / 520. C3 of the hypothesis is falsified
if the two readings disagree at 409 under any hard budget below 2^65: the lowest hard threshold of any
reading at 409 is 2^55.83 (nonzeros_with_index_sparse) and 2^64.64 (rows_times_cols_dense); for the
dense-vs-semaev_sparse pair the disagreement starts at 2^65.33. These are reported for the Reviewer;
no judgement is made here.

## validate_ledger

`python3 tools/validate_ledger.py 2>&1 | grep RUN-SEMBIN-3ae91c` → (empty). The validator reports 20
pre-existing errors in other records (TASK-20260910-* handoffs, EXP-AES-14352a manifests), none in this
run's write scope.

## Determinism

Two complete executions inside one invocation of `command.txt`; all eleven arm JSON files identical by
SHA-256 (`determinism-check.json`); only `stdout.log` differs (timestamps). The second copies were
deleted after hashing; the hashes are the evidence. The record checker: 576 figures, 0 failures.

## Protocol deviations

PD-I (ARM I blindness not achieved), PD-N (ARM N UNREACHED), PD-S (omega/degree/curve as sensitivity
tables; m_selection added as an axis), PD-A (three attempts, all logged), PD-M (mpmath absent; float64).
Detail in `runs/RUN-SEMBIN-3ae91c/implementation.md`.

## Resources

Compute 44.2 s per execution, 91.8 CPU-s for both, peak RSS 1.08 GB (declared 2 GB), 2 cores declared;
wall clock of the session from provisional manifest to finalisation ≈ 25 min.
