# EXP-REPL-1d1287 -- Execution Report (pilot scope; see implementation.md for full deviation list)

Observations and measured values only. No interpretation, no status change,
no evidence record. See `agents/executor.md` / `AGENTS.md` for role limits.

## Run tally

- Total training runs executed: **372**, all terminal status `completed_valid`
  at the individual-run level (no crash, OOM, or driver failure; 0
  `implementation_error` / `infrastructure_error`).
- **Post-hoc reclassification**: 180 of the 372 runs (all runs under
  `contiguous_block_by_logarithm`: 135 `MAIN-real` + 45 `C1C6-scrambled`)
  are `invalid_measurement` for the structure_gap comparison, because that
  split's held-out set is confounded with the MSB target (see
  `invalidations.json` and implementation.md item 9). The runs themselves
  completed without technical error; the invalidity is in what the split
  measures, not in run execution.
- Remaining runs contributing valid structure_gap measurements: 192
  (135 `MAIN-real` + 45 `C1C6-scrambled` under `random_by_logarithm`, wait:
  actual count is 135 `MAIN-real`(random)=135? -- see exact breakdown below)
  Exact breakdown: `MAIN-real`/random = 135, `C1C6-scrambled`/random = 45,
  `C2-shuffled` = 6, `C3-planted` = 6. Total valid = 192.

## Git commit / dirty-tree state

Recorded per run at execution time (per manifest.yaml). Three distinct
commit hashes were observed across this task's execution window despite
this task never running `git commit`, indicating concurrent write activity
on the shared branch: `40459ba9...` (session start), `1ba846482a...`
(during early-run manifest writes), `5a0d24c27b...` (at analysis time). All
372 run manifests recorded `git_dirty: true`. See implementation.md item 10.

## Scope actually covered vs. frozen design

Frozen design: 72 real matched cells (3 capacities x 2 architectures x
2 curve sizes x 2 split modes x 3 real presentations), each needing 5 seeds
paired with a matched scrambled arm -- 480+ training runs, exceeding the
spec's own `maximum_runs: 400`.

Executed: 54 real matched cells attempted (curve_1: full 36-cell grid, both
architectures; curve_2: 18-cell grid, MLP only -- transformer/curve_2 not
run). Of these 54, **27 are valid** (random_by_logarithm) and **27 are
invalid_measurement** (contiguous_block_by_logarithm, split-confound). 18
cells (transformer x curve_2, both split modes) were never run --
budget-scope-limited, named explicitly, no interpolation performed.

Curve sizes are 2^12 and 2^16, not the frozen 2^20 / 2^28 (implementation.md
item 1).

## C6: seed variance on the scrambled arm (ran first)

Timestamped window: 2026-08-07 13:35:18.24 -- 13:38:09.82 (local), entirely
before any curve-arm (`MAIN-real`) run began (`MAIN-real` runs are
RUN-0103 onward by construction of `code/orchestrate.py`'s fixed phase
order).

- Mean binomial SE (single seed, single arm): 0.00638
- Mean empirical across-seed std (scrambled arm, per config): 0.08015
- Ratio: **12.56x** the binomial floor -- exceeds the spec's factor-3
  trigger by a wide margin.
- Per the frozen, pre-registered rule ("the ONLY permitted adjustment... it
  may only WIDEN the band"), the comparison band for every matched cell
  below uses `combined_se = max(binomial-combined SE, empirical seed-based
  SE)`, which in every cell equals the empirical seed-based SE (it always
  dominates). This widening was fixed BEFORE any curve-arm run, per the
  timestamps above.

## C2: shuffled-label null (blocking)

6 runs (2 architectures x 3 capacities, 1 seed, curve_1/random split).
Measured heldout_advantage: -0.0065 to +0.0130, all within the per-run
binomial SE (~0.01425) x 3 = ~0.0428 band around 0. **Within 3 SE of
chance for all 6 configs measured (PASS as measured).**

## C3: planted-leaky-encoding control (blocking)

6 runs (same grid as C2). Measured heldout_advantage: 0.5 for 5/6 configs
(MLP all 3 capacities, transformer capacities 1-2), 0.129 for transformer
capacity 0. **All 6 >= the 0.10 threshold (PASS as measured).** Anomaly:
MLP saturates at 0.5 at every capacity tested (ceiling effect from a very
strong plant -- see implementation.md item 5), so C4's "capacity must
respond in the expected direction" is only demonstrated cleanly for the
transformer arm (0.129 -> 0.5 rising with capacity), not for MLP (already
saturated at the smallest capacity tested).

## C5: table-attack reproduction

Classical Shanks BSGS, both curves, 30 random targets each, 100% recovery
(self-verified against direct scalar multiplication, independent of the
solver's internal state):

| curve | N | S (entries) | S (bits) | T mean (group ops) | T max | predicted T=sqrt(N) |
|---|---|---|---|---|---|---|
| curve_1 | 4096 | 64 | 2496 | 30.7 | 64 | 64.0 |
| curve_2 | 65536 | 256 | 13056 | 121.4 | 256 | 256.0 |

This is the classical S=T=O(sqrt(N)), S*T=N Shanks tradeoff, NOT a
distinguished-point/Hellman table tuned to saturate the tighter
S*T^2=Omega(N) bound (implementation.md item 6). It is the MEASURED point
used for the frontier placement below; the S*T^2 bound itself remains a
MODELED curve, never in the same column as this measured point.

## Split disjointness

Verified programmatically (`code/splits.py:verify_disjoint`, an assertion
executed at construction time for every one of the 372 runs, not merely
claimed) for train/early-stop/held-out, both split modes. All 372 runs:
`split_disjoint_verified: true`.

## structure_gap per matched cell -- VALID cells only (random_by_logarithm, n=27)

curve | split | arch | cap | presentation | real_adv | scrambled_adv | structure_gap | combined_SE | sigma_multiple
---|---|---|---|---|---|---|---|---|---
curve_1 | random | mlp | 0 | affine_xy_limbs | -0.0120 | -0.0026 | -0.0094 | 0.0202 | -0.47
curve_1 | random | mlp | 0 | projective_jacobian_limbs | -0.0008 | -0.0026 | +0.0018 | 0.0202 | +0.09
curve_1 | random | mlp | 0 | x_only_limbs | -0.0137 | -0.0026 | -0.0111 | 0.0202 | -0.55
curve_1 | random | mlp | 1 | affine_xy_limbs | -0.0239 | -0.0146 | -0.0093 | 0.0201 | -0.46
curve_1 | random | mlp | 1 | projective_jacobian_limbs | 0.0034 | -0.0146 | +0.0180 | 0.0202 | +0.90
curve_1 | random | mlp | 1 | x_only_limbs | -0.0260 | -0.0146 | -0.0114 | 0.0201 | -0.57
curve_1 | random | mlp | 2 | affine_xy_limbs | -0.0268 | -0.0076 | -0.0192 | 0.0201 | -0.95
curve_1 | random | mlp | 2 | projective_jacobian_limbs | 0.0042 | -0.0076 | +0.0119 | 0.0202 | +0.59
curve_1 | random | mlp | 2 | x_only_limbs | -0.0442 | -0.0076 | -0.0366 | 0.0201 | -1.82
curve_1 | random | transformer | 0 | affine_xy_limbs | 0.0011 | -0.0020 | +0.0031 | 0.0202 | +0.15
curve_1 | random | transformer | 0 | projective_jacobian_limbs | -0.0101 | -0.0020 | -0.0081 | 0.0202 | -0.40
curve_1 | random | transformer | 0 | x_only_limbs | -0.0153 | -0.0020 | -0.0133 | 0.0202 | -0.66
curve_1 | random | transformer | 1 | affine_xy_limbs | -0.0190 | 0.0042 | -0.0233 | 0.0202 | -1.15
curve_1 | random | transformer | 1 | projective_jacobian_limbs | -0.0007 | 0.0042 | -0.0049 | 0.0202 | -0.24
curve_1 | random | transformer | 1 | x_only_limbs | -0.0211 | 0.0042 | -0.0254 | 0.0202 | -1.26
curve_1 | random | transformer | 2 | affine_xy_limbs | -0.0239 | 0.0059 | -0.0298 | 0.0201 | -1.48
curve_1 | random | transformer | 2 | projective_jacobian_limbs | -0.0013 | 0.0059 | -0.0072 | 0.0202 | -0.35
curve_1 | random | transformer | 2 | x_only_limbs | -0.0369 | 0.0059 | -0.0428 | 0.0201 | -2.12
curve_2 | random | mlp | 0 | affine_xy_limbs | -0.0033 | -0.0027 | -0.0005 | 0.0050 | -0.11
curve_2 | random | mlp | 0 | projective_jacobian_limbs | 0.0004 | -0.0027 | +0.0031 | 0.0050 | +0.61
curve_2 | random | mlp | 0 | x_only_limbs | -0.0011 | -0.0027 | +0.0016 | 0.0050 | +0.32
curve_2 | random | mlp | 1 | affine_xy_limbs | -0.0084 | -0.0025 | -0.0060 | 0.0050 | -1.18
curve_2 | random | mlp | 1 | projective_jacobian_limbs | 0.0048 | -0.0025 | +0.0072 | 0.0050 | +1.43
curve_2 | random | mlp | 1 | x_only_limbs | -0.0033 | -0.0025 | -0.0009 | 0.0050 | -0.17
curve_2 | random | mlp | 2 | affine_xy_limbs | -0.0065 | -0.0040 | -0.0026 | 0.0050 | -0.51
curve_2 | random | mlp | 2 | projective_jacobian_limbs | 0.0039 | -0.0040 | +0.0079 | 0.0050 | +1.56
curve_2 | random | mlp | 2 | x_only_limbs | -0.0021 | -0.0040 | +0.0019 | 0.0050 | +0.37

sigma_multiple range across the 27 valid cells: -2.12 to +1.56.
**No valid cell reaches |sigma_multiple| >= 5** (the pre-registered
threshold); i.e. no valid cell's structure_gap divided by its combined SE
reaches 5x the SE in either direction.

Full raw data for ALL 54 attempted real cells (including the 27
invalid_measurement contiguous-split cells, reported not omitted) is in
`structure_gap_cells.json`. Per-run underlying numbers (including every
seed individually, not just cell means) are in each run's
`raw-result.json`.

## Tail checks (as raw data)

1. **Best/worst single cell across the (valid) grid**: best
   (highest sigma_multiple) = curve_2/random/mlp/cap2/projective_jacobian_limbs,
   sigma=+1.56; worst (most negative) =
   curve_1/random/transformer/cap2/x_only_limbs, sigma=-2.12. Neither
   reaches the 5-sigma threshold. (Across all 54 attempted cells including
   invalid ones, the largest-magnitude raw sigma value was +1.67 at
   curve_1/contiguous/transformer/cap0/projective_jacobian_limbs -- an
   invalid_measurement cell, reported for completeness, not as a finding.)
2. **contiguous vs random structure_gap, per comparable cell**: computed
   for all cells with both split modes present. Largest raw differences
   occur at capacity_id=0 (smallest models), up to |0.42| in raw gap
   magnitude -- but per item 9 above, the contiguous-split numbers in this
   comparison are invalid_measurement (split-confound), so this comparison
   is reported as a raw number, not as evidence of near-neighbor
   interpolation as the spec's tail-check intended. The comparison could
   not be validly performed in this pilot because of the split-construction
   defect; a corrected contiguous split is needed to run it.
3. **Most compressible trained model**: see (S,T) section below --
   compressed size is SMALLER than raw (32-bit) size only for the largest
   MLP capacity (cap 2: raw 3.17-6.05 Mbit vs compressed 2.93-5.61 Mbit).
   For the two smaller capacities, gzip-compressed state-dict size is
   LARGER than raw size (anomaly: small float32 weight blobs are
   near-incompressible and gzip's own overhead dominates) -- so "S = min(raw,
   compressed)" equals raw S for capacities 0-1 and compressed S for
   capacity 2 in this pilot.

## S (bits) and (S, T) frontier placement

S_bits_raw / S_bits_compressed ranges observed per (architecture,
capacity_id), pooled across curves/presentations/seeds (min-max across
that pool; input-dimension differences across presentations shift S
slightly):

architecture | capacity_id | S_bits_raw (min-max) | S_bits_compressed (min-max)
---|---|---|---
mlp | 0 | 8,480 -- 31,008 | 15,608 -- 36,840
mlp | 1 | 84,000 -- 264,224 | 86,744 -- 255,144
mlp | 2 | 3,170,336 -- 6,053,920 | 2,932,712 -- 5,612,056
transformer | 0 | 8,224 -- 9,248 | 22,112 -- 23,240
transformer | 1 | 81,952 -- 86,048 | 92,096 -- 96,416
transformer | 2 | 1,114,144 -- 1,130,528 | 1,046,456 -- 1,063,672

Frontier placement (measured vs measured; T is a separate column, never
merged): every trained model's S (whether raw or compressed) is **larger**
than the reproduced table attack's S at the matching curve
(curve_1 table: S=2,496 bits; curve_2 table: S=13,056 bits) -- by roughly
3x at the smallest capacity up to roughly 460x at the largest. **T for the
trained models is NOT measured** and is reported as not applicable: per
H-REPL-6c431d's explicit scope, "no predictor-to-solver reduction is
assumed or claimed," and none of these classifier models were operated as
an online DLP-solving procedure in this pilot, so there is no operational
online-query count to report for them. Only the table attack's T
(measured, above) and the modeled S*T^2=Omega(N) bound curve are available
on the T axis.

## Measured vs. modeled (columns never mixed)

**Measured** (this pilot): all `heldout_advantage`, `structure_gap`,
`train_accuracy` values and their SEs; C6 seed variance; S in bits (raw and
compressed) per model; the reproduced table attack's S and T.

**Modeled** (never measured in this pilot): the S*T^2=Omega(epsilon*N)
Corrigan-Gibbs-Kogan preprocessing bound (recalled from
IDEA-20260806-94676a / verified at that record's Stage 0, not re-derived
here); the binomial standard error formula at declared held-out sizes
(used only as the FLOOR component of the combined SE, superseded by the
measured seed-variance component per C6's finding above).

## Optimistic assumptions restated (direction of bias, per spec)

1. S counted as parameters x storage precision: OVERSTATES what a
   compressible model needs, flattering the learned arm's frontier
   position. Mitigated here by also reporting compressed S and noting
   (above) that compression only helps at the largest capacity tested.
2. Training cost excluded from (S,T) accounting: flatters the learned arm
   substantially (producing these 372 runs took real wall-clock time not
   charged against any model's frontier position).
3. Early-stopping slice assumed disjoint from held-out: verified
   programmatically per run in this pilot (not merely asserted), so this
   bias is not believed to apply here.

## Completion gate (per handoff TASK-20260806-6162ae) -- status as executed

- C6 measured on scrambled arm first, band fixed before curve-arm scoring,
  timestamped: **done as described above.**
- C2 shuffled-label null at chance within 3 SE: **pass, as measured, for
  the 6 configurations run** (curve_1/random only).
- C3 planted leaky >= 0.10 advantage: **pass, as measured, for the 6
  configurations run** (curve_1/random only; min 0.129).
- C5 table attack reproduced, (S,T) measured: **done, both curves.**
- Split disjointness verified and recorded, both split modes: **verified
  programmatically for both modes**; separately, `random_by_logarithm` is a
  valid instrument and `contiguous_block_by_logarithm` is NOT (target
  confound, see above) -- disjointness and instrument-validity are
  different properties and both are reported.
- Every run carries a manifest with command, commit, environment, seed,
  resolved model identifier: **all 372 runs, verified.**
- structure_gap reported with combined SE for every completed matched cell,
  alongside its matched scrambled-arm number: **done for the 54 attempted
  real cells** (27 valid + 27 invalid_measurement, both reported, not
  omitted).

**Scope note (not a judgment):** the frozen design's 72-cell grid is only
54 cells attempted (75%) and only 27 cells (37.5% of 72) are valid
measurements after the split-confound reclassification -- both figures
exceed the spec's own 15%-unresolved threshold for its success criterion.
Per role limits, this report does not conclude success, failure, support,
or refutation; that judgment belongs to Reviewer/Coordinator.
