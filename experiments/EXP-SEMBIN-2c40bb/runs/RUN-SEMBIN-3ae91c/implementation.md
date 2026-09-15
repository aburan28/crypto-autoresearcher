# RUN-SEMBIN-3ae91c — implementation notes (EXP-SEMBIN-2c40bb, TASK-20260913-39f7a4)

Observations only. Nothing here is a statement about the security of any curve.

## What was built

`experiments/EXP-SEMBIN-2c40bb/code/`

- `surface_cost.py` — closed-form log2 cost model: Semaev time (stage 1 `m! 2^k 2^(n-mk) n^(4w)`, stage 2 `2^(k w')`, `w' = 2`, k per reading), Semaev memory under four storage readings (relation store `2^ceil(n/m)` rows of `mk + 2n` bits, log2-summed with the working set as the parent did), parallel Semaev (`time - p`, memory `log2add(store, ws + p)`), kappa as `time - log2(kappa)`; vOW baseline under three charging modes (`record_point_M1_w30`: `T = W/M`, `Mem = 3n w`; `own_curve_product_minimum`: `w = M`, `T = W(1/M + 1/w)`; `sect113r2_calibrated_ratio`: `w = M 2^13.3`), cofactor `-0.5 log2 h`, Frobenius `-0.5 log2 n` for K labels; five metric families; the crossover machinery (cheaper set as intervals over n in [3, 700], first crossing, persistent crossover, the parent's [250, 650] window); C2 Table 3 reproduction; C5 eq.(4) typo detector; C9 input validation.
- `sparse_independent.py` — ARM I, exact-integer `n^7 m^3 / 24` route, written from KN-LIT-e77232's statement, importing nothing from the cost modules.
- `run_all.py` — arms in the frozen order R, N, S, B, F, I, then C10, C3, C4, C5, C9 and the sensitivity tables; writes each arm's JSON as it finishes; executes the whole pipeline twice and hashes every JSON for the determinism check.
- `generate_cost_record.py` / `verify_new_record.py` — the COST record is built FROM the JSON artifacts through a figure map, and the checker re-reads both sides independently (576 figures, 0 failures).
- `finalize_manifest.py` — fills `manifest.yaml` (shape copied from RUN-SEMBIN-cbd770) from the artifacts.

## Conventions that had to be chosen (all labelled in the cell records)

- `m_selection` is a labelled axis: `stage1_argmin` (the parent's convention, used for ARM R and for the headline comparisons with the preregistered predictions) and `metric_reoptimised` (Semaev re-chooses m under the metric; the budget metrics require this by construction).
- `own_curve_product_minimum` evaluates every metric at the vOW point `w = M = 2^processors_log2`, which attains the product minimum; `store_log2` is ignored in that mode and in `sect113r2_calibrated_ratio` (both are labelled collisions). Under `time_only` this point costs one bit more than the record point (the DP tail `1/w`), as the model says.
- Under the fixed budgets the baseline shrinks `w` and `M` to fit (any `B >= 3n` bits is feasible), per the red team's reading; Semaev is infeasible where every m exceeds the hard budget and the margin is then reported as `semaev_infeasible`, not as a number.
- The zero-memory comparator gives `-inf` under `time_memory_product` and `memory_weighted_time_alpha`: DEGENERATE, reported as such. Under the budget metrics it is a feasible baseline and is reported numerically with that note.
- Memory always pays `ceil(n/m)`; the k reading is an axis of the TIME model only (as in the parent).
- `omega`, `degree_bound` and `curve_label` are one-at-a-time sensitivity tables (`sensitivities.json`) at the record and coherent points; the 254,016-cell surface fixes degree 4 / omega 3.0. Curve-label cofactors (B: 2, K: 4) are `recalled`, not verified from a source; every `h in {1, 2, 4}` is in the surface regardless.

## Attempts

1. `command.txt` attempt 1 (20:46:23Z): failed before any arm on `int('n = 163')` while parsing the parent record's `security_parameter`; parser fixed.
2. Attempt 2 (20:47:04Z): all arms completed and determinism held, but `raw-result.json` was 79 MB (indent=1, one value per line) and C4 mis-scored eight cells pinned at the domain floor n = 3 as "not moved down". Code amended: compact per-cell encoding with code tables; C4 criterion refined (floor-pinned cells reported as pinned with their margin movement; the one hard-budget/stage1_argmin interaction listed separately); second-execution copies deleted after hashing.
3. Attempt 3 (20:49:31Z): the run of record. Attempt 2 and 3 agree on every figure.

All three attempts are in `stdout.log`/`stderr.log`.

## Protocol deviations

- **PD-I** — `memory_charged_cost.py`, including `semaev_memory_log2`, was read in full during contract intake BEFORE `sparse_independent.py` was written. The module imports nothing and takes an exact-integer route, but the blindness C7 asked for was not achieved. ARM I's independence is weaker than specified.
- **PD-N** — ARM N is UNREACHED (`arm-n-prime-field-control.json`): EXP-ICEX-c32447 defines `C_LA`, `C_descent`, IC memory and the multi-target rho baseline as MEASURED counters with no closed form and has no runs; its stated closed-form term (`m! N` at sigma = 1) carries no memory and no B, so charging it under the store grid would test nothing about memory charging; and its N range is 2^20–2^30 with no declared transfer to cryptographic size. The PFDR model the red team used is a different model and was NOT substituted.
- **PD-S** — omega / degree / curve label as sensitivity tables rather than surface axes; `m_selection` added as an axis.
- **PD-A** — three execution attempts (above).
- **PD-M** — `mpmath` is not installed; float64 via `math` with exact-integer binomials. Reproduction to 4.82e-5 bits (the printing precision of the compared records) shows this suffices.
- **Prediction `all_corrections_B409`** could not be evaluated at its own cell: the red team's S4 combination uses a unit conversion of 2^5 (kappa = 32), which is not on the declared kappa grid; the nearest declared cells are reported in the execution report.

## Unexpected observations (recorded, not interpreted)

- The `semaev_sparse` formula contains no degree, so it is degree-insensitive by construction; only the Macaulay-width readings move with the given degree bound (dense: 435 → 495 → 551 at degrees 4/5/6).
- Under C10 reading A (MB = per-system peak) NO accounting upper-bounds every measured row; under reading B (MB = total over 100 systems) both sparse accountings do and neither dense accounting does. The dense-minus-sparse gap widens from 6.5–9.7 bits at N ≈ 50 to 20.3 bits at n = 409 and 21.5 at n = 571.
- Under the ceiled-k time reading the persistent crossover is identical at kappa 1 and 10 in some cells (e.g. own-curve/ceiled/h=2/dense: 501 at both) because the ceil(n/m) saw-tooth pins the last sign change; kappa 100 moves it to 481.
- C3: the informative null (3n-bit baseline) puts the baseline-store contribution at −87 to −88 in n (30.0 bits) in every storage reading, i.e. NOT near zero.
