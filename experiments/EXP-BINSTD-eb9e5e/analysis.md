# Analysis: EXP-BINSTD-eb9e5e (H-BINSTD-ce918e)

Review plan: `experiments/EXP-BINSTD-eb9e5e/review/review-plan.yaml`
(`REVIEW-BINSTD-eb9e5e-20261003`), written before this analysis.
Producer release: TASK-20261003-7fb8cc on tip `7e4af40ca2`.
Snapshot archive: TASK-20261003-22ef38. Approval: DEC-20261003-53838e.
Parent evidence: EV-BINSTD-0fed43 / DEC-20261003-e86acd (refine);
also cites EV-BINSTD-375f15. Decision target: **inconclusive**
(Stage-1 `instrument_clears_floor=false`, median ΔRSS=0; peak band
holds as continuity only). Do **not** support / KN-FIND. Do **not**
invent O-FAIL-BAND. No break; no exponent; no n≥131 transfer; no
Bedrock/AUXIN. No re-run this tick.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-BINSTD-f0b4ee` (Stage 0), `RUN-BINSTD-b819fc` (Stage 1). Each has
`manifest.yaml`, additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`,
`execution-receipt.json` (`status: output_validated`), and
`check.stdout.log` = `PASS`. Within `maximum_runs: 4`. Required
artifacts present: `stage0/preregistered-predictions.json`,
`stage0/v-catalog.json`, `stage1/panels.json`,
`stage1/control-table.json`, `RESULTS.md`. Amazon Bedrock not used.
Producer claims: `break: false`, `exponent_move: false`. No
solve/relation certificate (`certificate.kind=none` / memory
instrument). No parent re-run of ff5050/cb15a4.

**Stage 0 (J2).** `RUN-BINSTD-f0b4ee` reports `twin_ok: true`,
`rss_probe_ok: true`, `allocator_ok: true`, `outcome: O-STAGE0-OK`.
Freeze binds `(α,M₀)=(1.0, 16777216)`, `catalog_seed=2026100343342`
(≠ parent `2026100375050`), inherited XOR-SAT pin, process-isolated
baseline repeats → `os_rss_floor_bytes=31014912`. Allocator probes at
2/8/16 MiB all recover with `recovery_frac` above 0.5 on the largest
(delta ≈16.9 MiB on the 16 MiB probe) — the delta-RSS instrument is
**live**.

**Stage 1 peak band (J3) — blind band recompute from frozen (α,M₀).**

| cell | twin N_var | peak_rss | baseline | ΔRSS | band (recomputed) | holds | rss_mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (17,3) | 5=5 | 31084544 | 31055872 | 28672 | 134217728 | true | process_isolated_delta |
| (17,4) | 8=8 | 31055872 | 31055872 | 0 | 268435456 | true | process_isolated_delta |
| (17,5) | 10=10 | 31055872 | 31072256 | 0 | 536870912 | true | process_isolated_delta |
| (17,6) | 12=12 | 31055872 | 31105024 | 0 | 1073741824 | true | process_isolated_delta |

Blind recompute: `band_bytes = int(16777216 * 2**(1.0*ell))` matches
`stage1/panels.json` on all four cells. `peak_rss ≤ band` on all.
`peak_band_holds_all=true`. Twin N_var agrees on every cell. Peaks sit
≈29.6 MiB — same OS-floor envelope as EV-BINSTD-0fed43 / 375f15.

**Stage 1 floor gate (J4) — blind instrument_clears_floor recompute.**

From Stage-1 `delta_rss_bytes = [28672, 0, 0, 0]`:

- `median_delta_rss_bytes = 0` (< `clear_floor_delta_bytes=262144`).
- `max(encode_peak) − os_rss_floor = 31084544 − 31014912 = 69632`
  (< `clear_floor_margin_bytes=524288`).
- Therefore `instrument_clears_floor = false` (matches producer /
  control-table).
- `floor_dominant_delta = false` on the producer control-table (delta
  spread definition); the operative gate for mechanism reading is
  `instrument_clears_floor`.
- Contract `tail_checks` / success criterion: gate false →
  **O-INCONCLUSIVE** for mechanism reading even when peak band holds —
  diagnostic, not O-FAIL-BAND.

**Scope / non-claims (J5).** RESULTS.md and raw-results claim no
break, no exponent move, no Bedrock, no n≥131 transfer, and no
support / KN-FIND. Memory / delta-RSS instrument only at n=17, ℓ≤6.

## Comparison

Against H-BINSTD-ce918e distinguishable outcomes and this successor's
frozen gates:

- Twin agreement: **holds** on Stage 0 and all Stage-1 cells → not
  O-ARTIFACT.
- RSS probe + allocator: **finite**, process-isolated, allocator
  recovers multi-MiB probes → not O-IMPEDIMENT (instrument alive).
- Peak band `peak_rss ≤ M₀·2^{α·ℓ}`: **holds** on all Stage-1 cells →
  continuity with EV-BINSTD-0fed43 / 375f15, **not** a mechanism
  reading while the floor gate fails.
- `instrument_clears_floor`: **false** → producer **O-INCONCLUSIVE**
  is the only honest Stage-1 label under the frozen contract.
- O-FAIL-BAND: **not met** (would require instrument_clears_floor true
  AND peak_rss > band).
- O-SUPPORT (package): **not met** (requires band hold AND
  instrument_clears_floor AND not floor_dominant_delta).

## Inference

The package is **valid**. Stage 0 freeze, new seed, allocator
calibration, and process-isolated delta-RSS stand. Stage 1 shows that
baseline-subtracted encode+solve ΔRSS at n=17 ℓ∈{3,4,5,6} remains
≈0 (median 0; only ℓ=3 shows 28672 bytes), so the instrument still
cannot clear the ≈30 MiB OS RSS floor despite a live allocator probe
that recovers 16 MiB allocations. Peak-band continuity is observed and
must **not** be promoted to HEUR mechanism support.

Official decision: **inconclusive**. Strength: **inconclusive**.
Hypothesis remains **analyzed** (not supported). Experiment
`approved → analyzed`. Do **not** reject_scoped (no band falsifier;
floor gate is diagnostic). Do **not** support / KN-FIND. Successor:
design/approve a further instrument refine that pushes encode working
set above the clear-floor thresholds (larger/denser cells, or
heap-only accounting that does not baseline-subtract to zero when the
encode heap is small) — before any support / KN-FIND reading. No
break; no exponent; no n≥131 transfer. No re-run of this package this
tick.

## Limitation

- Toy n=17, ℓ≤6 only; no transfer of a RSS band into an n≥131 attack.
- `instrument_clears_floor=false` — baseline-subtracted ΔRSS does not
  resolve ℓ-channel growth at these cells even though the allocator
  probe proves the instrument can see multi-MiB growth.
- Coordinator-direct review without independent validator/red-team
  (review-plan PD-1).
- `certificate.kind=none` — measurement package, not a solve
  certificate.
- Memory instrument only; does not predict yield or beat rho
  (KR-IC-1fcdbc).
- First observation of this delta-RSS successor; unreplicated.
