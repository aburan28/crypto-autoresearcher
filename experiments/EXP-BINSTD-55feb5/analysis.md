# Analysis: EXP-BINSTD-55feb5 (H-BINSTD-ce918e)

Review plan: `experiments/EXP-BINSTD-55feb5/review/review-plan.yaml`
(`REVIEW-BINSTD-55feb5-20261003`), written before this analysis.
Producer release: TASK-20261003-3f416e on tip `c17a6eb978`.
Snapshot archive: TASK-20261003-eee623. Approval: DEC-20261003-0a117b.
Parent evidence: EV-BINSTD-cd47a8 / DEC-20261003-495a2e (inconclusive);
also cites EV-BINSTD-0fed43 / EV-BINSTD-375f15. Decision target:
**inconclusive** (Stage-1 `instrument_clears_floor=false`, median
ΔRSS=98304; peak band holds as continuity only; Stage-0 calibration
cleared on probe (31,12) at density_batch=8).

## Observation

**Validity (J1).** Two completed runs: `RUN-BINSTD-15c58d` (Stage 0),
`RUN-BINSTD-5b96e9` (Stage 1). Each has `manifest.yaml`, additive
`manifest_v2.yaml`, `raw-result.json`, `environment.json`, `stdout.log`,
`command.txt`, `execution-receipt.json` (`status: output_validated`),
and `check.stdout.log` = `PASS`. Independent `check.py` re-invocation
on the archived run directories also returned `PASS` (artifact check,
not a scientific re-run). Within `maximum_runs: 4`. Required artifacts
present: `stage0/preregistered-predictions.json`,
`stage0/v-catalog.json`, `stage1/panels.json`,
`stage1/control-table.json`, `RESULTS.md`. Amazon Bedrock not used.
Producer claims: `break: false`, `exponent_move: false`. No
solve/relation certificate (`certificate.kind=none` / memory
instrument). No parent re-run of eb9e5e/ff5050/cb15a4.

**Stage 0 (J2).** `RUN-BINSTD-15c58d` reports `twin_ok: true`,
`rss_probe_ok: true`, `allocator_ok: true`,
`floor_clear_calibration_ok: true`, `density_batch_size: 8`,
`outcome: O-STAGE0-OK`. Freeze binds `(α,M₀)=(1.0, 16777216)`,
`catalog_seed=2026100377593` (≠ parent `2026100343342`), inherited
XOR-SAT pin, process-isolated baseline repeats →
`os_rss_floor_bytes=31305728`. Allocator probes at 2/8/16 MiB all
recover; largest (16 MiB) delta ≈16744448 (`recovery_frac` well above
0.5) — the delta-RSS instrument is **live**. Density-batch calibration
on probe (31,12) doubled 1→2→4→8; batch=8 reported
`delta_rss_bytes=360448` and `instrument_clears_floor=true` on that
single probe trial. That is a **calibration** pass, not a Stage-1
package median.

**Stage 1 peak band (J3) — blind band recompute from frozen (α,M₀).**

| cell | twin N_var | peak_rss | baseline | ΔRSS | band (recomputed) | holds | rss_mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (23,6) | 10=10 | 31162368 | 31088640 | 73728 | 1073741824 | true | process_isolated_delta |
| (23,8) | 15=15 | 31473664 | 30965760 | 507904 | 4294967296 | true | process_isolated_delta |
| (29,8) | 15=15 | 31002624 | 31354880 | 0 | 4294967296 | true | process_isolated_delta |
| (29,10) | 19=19 | 31203328 | 31256576 | 0 | 17179869184 | true | process_isolated_delta |
| (31,10) | 19=19 | 31338496 | 31215616 | 122880 | 17179869184 | true | process_isolated_delta |
| (31,12) | 23=23 | 31571968 | 31133696 | 438272 | 68719476736 | true | process_isolated_delta |

Blind recompute: `band_bytes = int(16777216 * 2**(1.0*ell))` matches
`stage1/panels.json` on all six cells (1073741824 / 4294967296 /
17179869184 / 68719476736). `peak_rss ≤ band` on all.
`peak_band_holds_all=true`. Twin N_var agrees on every cell. Peaks sit
≈29.6–30.1 MiB — same OS-floor envelope as EV-BINSTD-cd47a8 / 0fed43 /
375f15. Two cells clamp `delta_rss` to 0 because encode peak < paired
baseline (`(29,8)`, `(29,10)`).

**Stage 1 floor gate (J4) — blind instrument_clears_floor recompute.**

From Stage-1 `delta_rss_bytes = [73728, 507904, 0, 0, 122880, 438272]`:

- Sorted `[0, 0, 73728, 122880, 438272, 507904]`; even-n median
  `(73728 + 122880) / 2 = 98304` (< `clear_floor_delta_bytes=262144`).
- `max(encode_peak) − os_rss_floor = 31571968 − 31305728 = 266240`
  (< `clear_floor_margin_bytes=524288`).
- Therefore `instrument_clears_floor = false` (matches producer /
  control-table / RESULTS.md).
- Two individual cells exceed 262144 ΔRSS ((23,8)=507904,
  (31,12)=438272); the frozen gate is the **package median**, not a
  per-cell OR.
- Producer `floor_dominant_delta=false` (spread definition); the
  operative gate for mechanism reading is `instrument_clears_floor`.
- Contract `tail_checks` / success criterion: gate false →
  **O-INCONCLUSIVE** for mechanism reading even when peak band holds
  and even when Stage-0 calibration cleared — diagnostic, not
  O-FAIL-BAND.

**Scope / non-claims (J5).** RESULTS.md and raw-results claim no
break, no exponent move, no Bedrock, no n≥131 transfer, and no
support / KN-FIND. Memory / densified delta-RSS instrument only at
n∈{23,29,31}, ℓ∈{6,8,10,12}.

## Comparison

Against H-BINSTD-ce918e distinguishable outcomes and this successor's
frozen gates:

- Twin agreement: **holds** on Stage 0 and all Stage-1 cells → not
  O-ARTIFACT.
- RSS probe + allocator: **finite**, process-isolated, allocator
  recovers multi-MiB probes → not O-IMPEDIMENT (instrument alive).
- Stage-0 `floor_clear_calibration_ok`: **true** at density_batch=8 on
  probe (31,12) → Stage 1 was allowed to run; this is **not** package
  O-SUPPORT.
- Peak band `peak_rss ≤ M₀·2^{α·ℓ}`: **holds** on all Stage-1 cells →
  continuity with EV-BINSTD-cd47a8 / 0fed43 / 375f15, **not** a
  mechanism reading while the package floor gate fails.
- Package `instrument_clears_floor`: **false** (median ΔRSS=98304) →
  producer **O-INCONCLUSIVE** is the only honest Stage-1 label under
  the frozen contract.
- O-FAIL-BAND: **not met** (would require instrument_clears_floor true
  AND peak_rss > band).
- O-SUPPORT (package): **not met** (requires band hold AND
  instrument_clears_floor AND not floor_dominant_delta).

Versus parent EV-BINSTD-cd47a8 (median ΔRSS=0 at n=17 ℓ≤6): densified
cells move the median to 98304 and produce two cells above 262144, but
do not clear the package gate. Stage-0 probe-clear vs Stage-1 median
fail is a new diagnostic, not a promotion.

## Inference

The package is **valid**. Stage 0 freeze, new seed, allocator
calibration, and density-batch calibration stand. Stage 1 shows that
the six-cell package median of baseline-subtracted densified
encode+solve ΔRSS at n∈{23,29,31} ℓ∈{6,8,10,12} remains 98304
(<262144), and max encode peak sits only 266240 bytes above the
≈29.9 MiB OS RSS floor (<524288). Peak-band continuity is observed
and must **not** be promoted to HEUR mechanism support. Stage-0
`floor_clear_calibration_ok` must **not** be read as Stage-1 support:
the calibration trial is a single probe cell, while the frozen
mechanism gate is the six-cell median.

Official decision: **inconclusive**. Strength: **inconclusive**.
Hypothesis remains **analyzed** (not supported). Experiment
`approved → analyzed`. Do **not** reject_scoped (no band falsifier;
floor gate is diagnostic). Do **not** support / KN-FIND. Successor:
design/approve a further instrument refine that clears the Stage-1
**package** `instrument_clears_floor` (raise density_batch until the
six-cell median ≥262144, or freeze a shared baseline / heap-only RSS
so cells whose encode peak sits below a noisy paired baseline do not
clamp ΔRSS to 0) — before any support / KN-FIND reading. No break;
no exponent; no n≥131 transfer. No re-run of this package this tick.

## Limitation

- Toy n∈{23,29,31}, ℓ≤12 only; no transfer of a RSS band into an
  n≥131 attack.
- `instrument_clears_floor=false` — package median ΔRSS=98304 does not
  resolve ℓ-channel growth even though two cells individually exceed
  262144 and Stage-0 probe (31,12) at batch=8 cleared.
- Process-isolated paired baselines vary cell-to-cell; two cells clamp
  ΔRSS to 0 when encode peak < baseline (OS-floor jitter).
- Coordinator-direct review without independent validator/red-team
  (review-plan PD-1).
- `certificate.kind=none` — measurement package, not a solve
  certificate.
- Memory instrument only; does not predict yield or beat rho
  (KR-IC-1fcdbc).
- First observation of this densified floor-clear successor;
  unreplicated.
