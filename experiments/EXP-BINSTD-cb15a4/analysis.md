# Analysis: EXP-BINSTD-cb15a4 (H-BINSTD-ce918e)

Review plan: `experiments/EXP-BINSTD-cb15a4/review/review-plan.yaml`
(`REVIEW-BINSTD-cb15a4-20261003`), written before this analysis.
Producer: TASK-20261003-bbf477. Snapshot: TASK-20261003-5ee58a.
Approval: DEC-20261003-f15665. Decision target: **replicate**
(first unreplicated O-SUPPORT at n=17 toys; OS RSS floor confound
disclosed). Prefer replicate over support. No break; no exponent; no
n≥131 transfer; no Bedrock/AUXIN. No re-run this tick.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-BINSTD-de7f9a` (Stage 0) and `RUN-BINSTD-70923a` (Stage 1). Each
has `manifest.yaml`, additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`, `execution-receipt.json`,
and `check.stdout.log` = `PASS`. Both receipts
`status: output_validated`, `check_returncode: 0`. Within
`maximum_runs: 4`. Required Stage-0 freeze artifacts
(`stage0/v-catalog.json`, `stage0/preregistered-predictions.json`) and
Stage-1 artifacts (`stage1/panels.json`, `stage1/control-table.json`,
`RESULTS.md`) present. Amazon Bedrock not used. `certificate.kind: none`
on both runs (memory instrument; no discrete_log / key_recovery).
Producer claims: `break: false`, `exponent_move: false`.

**Stage 0 (J2).** `RUN-BINSTD-de7f9a` reports `twin_ok: true`,
`rss_probe_ok: true`, `outcome: O-STAGE0-OK`, freeze paths bound to
`stage0/preregistered-predictions.json` and `stage0/v-catalog.json`.
Frozen `(α,M₀)=(1.0, 16777216)`; catalog_seed `202610032056`;
authorized Stage-1 cells `{(17,3),(17,4)}`. Stage-0
`peak_rss_bytes=29417472` (probe). Independent `check.py` PASS.

**Stage 1 (J3) — blind band recompute from frozen (α,M₀).**

| cell | twin N_var | peak_rss | band (recomputed) | panels band | holds |
| --- | --- | --- | --- | --- | --- |
| (17,3) | 5=5 | 28631040 | 134217728 | 134217728 | true |
| (17,4) | 8=8 | 28631040 | 268435456 | 268435456 | true |

Blind recompute: `band_bytes = int(16777216 * 2**(1.0*ell))` matches
producer `panels.json` `band_bytes` on both cells. `peak_rss ≤ band`
on both. `control-table.json` records `twin_ok: true` and
`band_holds: [true, true]`. Identical `peak_rss_bytes=28631040` at
ℓ=3 and ℓ=4 (and near Stage-0 probe 29417472) is disclosed as the
proof_search_map OS-RSS-floor observation collision — not a protocol
fail and not a band-arithmetic error.

**Scope / non-claims (J4).** RESULTS.md and raw-result claim no break,
no exponent move, no Bedrock, and no n≥131 transfer. Memory / peak-RSS
instrument only at toy n=17.

## Comparison

Against H-BINSTD-ce918e distinguishable outcomes and frozen band:

- Twin agreement: **holds** on Stage-0 probe and both Stage-1 cells →
  not O-ARTIFACT.
- RSS probe: **finite integer** on Stage 0 and Stage 1 → not
  O-INCONCLUSIVE / O-IMPEDIMENT.
- Band `peak_rss ≤ M₀·2^{α·ℓ}`: **holds** on every Stage-1 cell →
  **O-SUPPORT** by contract.
- O-FAIL-BAND: **not met** (both cells inside band with large margin).
- O-IMPEDIMENT: **not met** (runs completed; check PASS).

## Inference

The package is **valid**. Stage 0 freeze, twin meters, and RSS probe
stand. Official producer label **O-SUPPORT** is retained for the
declared Stage-1 scope: at n=17, ℓ∈{3,4}, under frozen
`(α,M₀)=(1.0, 16777216)` and the shared XOR-SAT pin, measured
`peak_rss_bytes=28631040 ≤` band on both cells. Decision: **replicate**
— first unreplicated positive observation; strength **preliminary**;
hypothesis and experiment `approved → analyzed`. Do **not** support
on first unreplicated package (review-evidence skill). Do **not**
reject_scoped (band holds; no falsifier). Do **not** invent break /
exponent / n≥131 transfer. Disclosed confound: identical peak RSS
across ℓ suggests an OS RSS floor that may hide ℓ-growth — Stage-2
multi-n + random-Boolean null (not authorized under this card) is the
protocol's own separation; successor design/replication should address
it before any stronger reading. No re-run this tick.

## Limitation

- Toy n=17 cells only; Stage-2 (n∈{19,23,29,31} + random-Boolean null)
  not authorized under this card.
- Identical peak_rss at ℓ=3 and ℓ=4 (≈28.6 MiB) vs Stage-0 probe
  ≈29.4 MiB — OS RSS floor may dominate encode growth at these toys.
- First unreplicated observation; no independent validator/red-team
  (review-plan PD-1).
- `certificate.kind=none` — measurement package, not a solve certificate.
- Memory instrument only; does not predict yield or beat rho
  (KR-IC-1fcdbc).
- Strength preliminary — insufficient for support or KN-FIND promotion.
- No break; no exponent; no n≥131 transfer.
