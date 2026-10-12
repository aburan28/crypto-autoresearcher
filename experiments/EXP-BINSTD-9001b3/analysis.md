# Analysis: EXP-BINSTD-9001b3 (H-BINSTD-ce918e)

Review plan: `experiments/EXP-BINSTD-9001b3/review/review-plan.yaml`
(`REVIEW-BINSTD-9001b3-20261003`), written before this analysis.
Producer release: TASK-20261003-10cb87 on tip `851f50e306`.
Snapshot owner: TASK-20261003-4eb554. Approval: DEC-20261003-a50644.
Parent evidence: EV-BINSTD-602614 / DEC-20261003-cff91a (inconclusive
floor); also cites EV-BINSTD-cd47a8. Decision target: **replicate**
(Stage-1 `instrument_clears_floor=true`, median ΔRSS=591872,
`n_clamped_zero=0`, `peak_band_holds_all=true`; first unreplicated
clear-floor O-SUPPORT at densified multi-n cells).

## Observation

**Validity (J1).** Two completed runs: `RUN-BINSTD-31cc54` (Stage 0),
`RUN-BINSTD-aead63` (Stage 1). Each has `manifest.yaml`,
`raw-result.json`, `environment.json`, `stdout.log`, `command.txt`,
`execution-receipt.json` (`status: output_validated`), and
`check.stdout.log` = `PASS`. Independent `check.py` re-invocation on
the archived run directories also returned `PASS` (artifact check, not
a scientific re-run). Required artifacts present:
`stage0/preregistered-predictions.json`, `stage0/v-catalog.json`,
`stage1/panels.json`, `stage1/control-table.json`, `RESULTS.md`.
Amazon Bedrock not used. Producer claims: `break: false`,
`exponent_move: false`. No solve/relation certificate (memory
instrument). No parent re-run of 55feb5/eb9e5e/ff5050/cb15a4.
`AMD-EXP-BINSTD-9001b3-20261003-admission` changes queue handoff fields
only; scientific thresholds unchanged.

**Stage 0 (J2).** `RUN-BINSTD-31cc54` reports `twin_ok: true`,
`rss_probe_ok: true`, `allocator_ok: true`,
`floor_clear_calibration_ok: true`, `density_batch_size: 32`,
`shared_baseline_rss_bytes: 31391744`, `outcome: O-STAGE0-OK`. Freeze
binds `(α,M₀)=(1.0, 16777216)`, `catalog_seed=2026100390013`
(≠ parent seeds 2026100377593 / 2026100343342 / 2026100375050),
inherited XOR-SAT pin, process-isolated shared baseline (median of 7
Field-import workers) → `os_rss_floor_bytes=31391744`. Allocator
probes at 2/8/16 MiB all recover vs that shared baseline (16 MiB
delta ≈16605184). Density-batch calibration on package calib cells
`{(23,6),(29,8),(29,10),(31,12)}` cleared at batch=32
(`median_delta_rss_bytes=604160`, `n_clamped_zero=0`,
`instrument_clears_floor=true` on the calib trial). Shared baseline
is frozen for Stage 1 (`baseline_source=stage0_shared_frozen`); no
per-cell paired baseline.

**Stage 1 peak band (J3) — blind band recompute from frozen (α,M₀).**

| cell | twin N_var | peak_rss | shared_baseline | ΔRSS | band (recomputed) | holds | rss_mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (23,6) | 10=10 | 31797248 | 31391744 | 405504 | 1073741824 | true | process_isolated_delta_shared_baseline |
| (23,8) | 15=15 | 31895552 | 31391744 | 503808 | 4294967296 | true | process_isolated_delta_shared_baseline |
| (29,8) | 15=15 | 31756288 | 31391744 | 364544 | 4294967296 | true | process_isolated_delta_shared_baseline |
| (29,10) | 19=19 | 32071680 | 31391744 | 679936 | 17179869184 | true | process_isolated_delta_shared_baseline |
| (31,10) | 19=19 | 32288768 | 31391744 | 897024 | 17179869184 | true | process_isolated_delta_shared_baseline |
| (31,12) | 23=23 | 32407552 | 31391744 | 1015808 | 68719476736 | true | process_isolated_delta_shared_baseline |

Blind recompute: `band_bytes = int(16777216 * 2**(1.0*ell))` matches
`stage1/panels.json` on all six cells. `peak_rss ≤ band` on all.
`peak_band_holds_all=true`. Twin N_var agrees on every cell. All six
cells use the same frozen shared baseline; `n_clamped_zero=0` (no
encode peak below baseline).

**Stage 1 floor gate (J4) — blind instrument_clears_floor recompute.**

From Stage-1 `delta_rss_bytes = [405504, 503808, 364544, 679936, 897024, 1015808]`:

- Sorted median `(503808 + 679936) / 2 = 591872`
  (≥ `clear_floor_delta_bytes=262144`).
- `max(encode_peak) − os_rss_floor = 32407552 − 31391744 = 1015808`
  (≥ `clear_floor_margin_bytes=524288`).
- `n_clamped_zero = 0`.
- Therefore `instrument_clears_floor = true` (matches producer /
  control-table / RESULTS.md). Both median and margin thresholds clear.
- Per-ℓ medians: ℓ=6 → 405504; ℓ=8 → 434176; ℓ=10 → 788480; ℓ=12 →
  1015808. `delta_ell_spread = (1015808 − 405504) / 405504 ≈ 1.505`
  (≥ 0.05) and median ≥ 262144 → `floor_dominant_delta=false`.
- Contract success criterion: band hold AND instrument_clears_floor AND
  `n_clamped_zero=0` AND not `floor_dominant_delta` → producer
  **O-SUPPORT** is the correct Stage-1 label under the frozen contract.
  Producer O-SUPPORT is observation, not a Coordinator decision.

**Scope / non-claims (J5).** RESULTS.md and raw-results claim no
break, no exponent move, no Bedrock, no n≥131 transfer, and no
support / KN-FIND in-packet. Memory / densified shared-baseline
delta-RSS instrument only at n∈{23,29,31}, ℓ∈{6,8,10,12}.

## Comparison

Against H-BINSTD-ce918e distinguishable outcomes and this successor's
frozen gates:

- Twin agreement: **holds** on Stage 0 and all Stage-1 cells → not
  O-ARTIFACT.
- RSS probe + allocator: **finite**, process-isolated, allocator
  recovers multi-MiB probes vs shared baseline → not O-IMPEDIMENT.
- Stage-0 `floor_clear_calibration_ok`: **true** at density_batch=32
  on package calib cells → Stage 1 was allowed to run.
- Peak band `peak_rss ≤ M₀·2^{α·ℓ}`: **holds** on all Stage-1 cells →
  continuity with EV-BINSTD-602614 / cd47a8 / 0fed43 / 375f15.
- Package `instrument_clears_floor`: **true** (median ΔRSS=591872;
  margin 1015808; `n_clamped_zero=0`) → discharges the floor gate that
  blocked EV-BINSTD-602614 (median 98304) and EV-BINSTD-cd47a8
  (median 0).
- `floor_dominant_delta`: **false** (spread ≈1.505) → ΔRSS varies
  across ℓ rather than collapsing to a floor-flat envelope.
- O-FAIL-BAND: **not met** (would require instrument_clears_floor true
  AND peak_rss > band).
- O-SUPPORT (package): **met** under the frozen contract. Coordinator
  reading of that producer label is still **replicate**, not support /
  KN-FIND, on first unreplicated clear-floor observation (AGENTS.md /
  skill: surprising first positives get replicate).

Versus parent EV-BINSTD-602614: shared baseline removes paired-baseline
clamp-to-zero (`n_clamped_zero` 2→0); density_batch 8→32 moves median
ΔRSS 98304→591872 past the package gate. Versus EV-BINSTD-375f15
(n=17 O-SUPPORT with identical peak across ℓ): this package is the
first densified multi-n reading where ΔRSS clears the floor and
spreads with ℓ.

## Inference

The package is **valid**. Stage 0 freeze, new seed, shared baseline,
allocator calibration, and density-batch calibration stand. Stage 1
shows that the six-cell package median of shared-baseline-subtracted
densified encode+solve ΔRSS at n∈{23,29,31} ℓ∈{6,8,10,12} is 591872
with `n_clamped_zero=0` and `floor_dominant_delta=false`, while every
cell's peak_rss stays ≤ `M₀·2^{α·ℓ}`. Official Coordinator decision:
**replicate** — first unreplicated clear-floor O-SUPPORT continuing the
peak-RSS thread; not support / KN-FIND; not reject_scoped; not
inconclusive (floor gate clears on re-check). Hypothesis remains
`analyzed`. Experiment `approved→analyzed`.

## Limitation

- First unreplicated clear-floor O-SUPPORT at this densified
  shared-baseline package; strength is preliminary, not replicated.
- Toy n∈{23,29,31}, ℓ≤12 only; no n≥131 transfer; no break; no
  exponent.
- Coordinator-direct review without independent validator/red-team
  (PD-1).
- OS getrusage peak RSS remains an upper envelope, not exact heap
  accounting — cleared floor gate reduces but does not erase that
  instrument caveat.
- `certificate.kind=none` (measurement package).
- Admission AMD is infra-only and asserts nothing about outcomes.
- Default no KN-FIND until independent replication (and any later
  support decision) warrants promotion.
