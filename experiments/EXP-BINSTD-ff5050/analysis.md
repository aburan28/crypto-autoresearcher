# Analysis: EXP-BINSTD-ff5050 (H-BINSTD-ce918e)

Review plan: `experiments/EXP-BINSTD-ff5050/review/review-plan.yaml`
(`REVIEW-BINSTD-ff5050-20261003`), written before this analysis.
Producer release: TASK-20261003-eabf32 on tip `0eaf4a0811`.
Approval: DEC-20261003-953dd5. Parent evidence: EV-BINSTD-375f15 /
DEC-20261003-c14256 (replicate). Decision target: **refine**
(Stage-1R replicates toy band hold; Stage-2 confirms
`floor_dominant=true` / `null_n_insensitive=true` — OS RSS floor, not
ℓ-channel). Do **not** support / KN-FIND. No break; no exponent; no
n≥131 transfer; no Bedrock/AUXIN. No re-run this tick.

## Observation

**Validity (J1).** Three run directories under `runs/`:
`RUN-BINSTD-6f3d5b` (Stage 0), `RUN-BINSTD-f9a1d3` (Stage 1R),
`RUN-BINSTD-c45fde` (Stage 2). Each has `manifest.yaml`, additive
`manifest_v2.yaml`, `raw-result.json`, `environment.json`, `stdout.log`,
`command.txt`, `execution-receipt.json` (`status: output_validated`),
and `check.stdout.log` = `PASS`. Within `maximum_runs: 6`. Required
artifacts present: `stage0/preregistered-predictions.json`,
`stage0/v-catalog.json`, `stage1r/panels.json`,
`stage1r/control-table.json`, `stage2/panels.json`,
`stage2/control-table.json`, `RESULTS-stage1r.md`, `RESULTS-stage2.md`,
`RESULTS.md`. Amazon Bedrock not used. Producer claims:
`break: false`, `exponent_move: false`. No solve/relation certificate
(`certificate.kind=none` / memory instrument).

**Stage 0 (J2).** `RUN-BINSTD-6f3d5b` reports `twin_ok: true`,
`rss_probe_ok: true`, `outcome: O-STAGE0-OK`. Freeze binds
`(α,M₀)=(1.0, 16777216)`, `catalog_seed=2026100375050`
(≠ parent `202610032056`), inherited XOR-SAT pin, process-isolated
probe. Stage-0 `peak_rss_bytes` on isolated probe is in the same
≈29–30 MiB envelope as later panels.

**Stage 1R (J3) — blind band recompute from frozen (α,M₀).**

| cell | twin N_var | peak_rss | band (recomputed) | panels band | holds | rss_mode |
| --- | --- | --- | --- | --- | --- | --- |
| (17,3) | 5=5 | 30666752 | 134217728 | 134217728 | true | process_isolated |
| (17,4) | 8=8 | 30597120 | 268435456 | 268435456 | true | process_isolated |

Blind recompute: `band_bytes = int(16777216 * 2**(1.0*ell))` matches
`stage1r/panels.json` on both cells. `peak_rss ≤ band` on both.
`floor_identical_across_ell: false` (tiny absolute delta), but both
peaks sit ≈30.6 MiB — same OS-floor envelope as parent
EV-BINSTD-375f15 (28.6 MiB) and Stage-0 probe. Independent replication
of the Stage-1 O-SUPPORT band under a new seed and process-isolated
getrusage is **observed**.

**Stage 2 (J4) — multi-n + null; floor diagnostics.**

Blind recompute of Stage-2 real peak_rss list
`[30552064, 30490624, 30650368, 30707712, 30494720, 30523392, 30908416, 30490624]`:

- `real_n_spread = (max−min)/min ≈ 0.01370` (< 0.05) →
  `floor_dominant = true` (matches producer / control-table).
- Null peak_rss list yields `null_n_spread ≈ 0.00793` →
  `null_n_insensitive = true`.
- All eight real cells: `band_holds=true`, `twin_ok=true`,
  `rss_mode=process_isolated`.
- Null RSS values sit in the same ≈30.5–30.7 MiB envelope as real
  encode+solve RSS — matched-N_var random Boolean does not separate
  an ℓ-channel above the floor at these toys.

**Scope / non-claims (J5).** RESULTS*.md and raw-results claim no
break, no exponent move, no Bedrock, and no n≥131 transfer. Memory /
peak-RSS instrument only at n≤31.

## Comparison

Against H-BINSTD-ce918e distinguishable outcomes and frozen band:

- Twin agreement: **holds** on Stage 0, Stage 1R, and Stage 2 real
  cells → not O-ARTIFACT.
- RSS probe: **finite integer**, process-isolated → not
  O-INCONCLUSIVE / O-IMPEDIMENT.
- Band `peak_rss ≤ M₀·2^{α·ℓ}`: **holds** on Stage-1R and all
  Stage-2 real cells → producer **O-SUPPORT** labels retained as
  package labels for the inequality at toys.
- O-FAIL-BAND: **not met**.
- Observation collision (proof_search_map): Stage-2
  `floor_dominant=true` + `null_n_insensitive=true` **confirms** the
  alternate preimage — OS RSS floor, not measured ℓ-dominated encode
  growth. Contract `tail_checks` explicitly blocks upgrading
  Stage-1R O-SUPPORT to support / KN-FIND when `floor_dominant=true`.

## Inference

The package is **valid**. Stage 0 freeze, new seed, and process-
isolated RSS stand. Stage 1R **independently replicates** the parent
toy band hold (EV-BINSTD-375f15) under catalog_seed `2026100375050`.
Stage 2 extends the inequality to n∈{19,23,29,31} and, critically,
**measures the floor confound**: real and null RSS are n-insensitive
(< 5% spread) and mutually indistinguishable at ≈30.5 MiB.

Official decision: **refine** — not `support`. The replicated
observation is the **band inequality at toys under a floor-dominated
RSS instrument**, not the HEUR mechanism that encode+solve memory
tracks ℓ. Strength for the narrow band-hold observation may be read as
**replicated**; that does **not** authorize support / KN-FIND while
`floor_dominant=true`. Do **not** reject_scoped (band holds; floor is
a diagnostic, not O-FAIL-BAND). Hypothesis remains **analyzed** (not
supported). Experiment `approved → analyzed`. Successor: refine the
memory instrument (heap-only / baseline-subtracted RSS, or cells whose
encode working set exceeds the OS floor) before any stronger reading.
No break; no exponent; no n≥131 transfer. No re-run this tick.

## Limitation

- Toy n≤31 only; no transfer of a RSS band into an n≥131 attack.
- `floor_dominant=true` / `null_n_insensitive=true` — OS getrusage
  peak RSS is an upper envelope that does not resolve ℓ-channel
  growth at these cells.
- Coordinator-direct review without independent validator/red-team
  (review-plan PD-1).
- `certificate.kind=none` — measurement package, not a solve
  certificate.
- Memory instrument only; does not predict yield or beat rho
  (KR-IC-1fcdbc).
- No break; no exponent; no n≥131 transfer.
