# TASK-20260809-a79e4f -- Matched-pair measurement report

Observations only. This is the Executor's report of what was measured and
the mechanical facts of how it was measured. It draws no conclusion about
whether H-HQC-18d1b4 is supported or refuted, does not apply
DEC-20260809-46e85c's pre-registered decision rule, and asserts nothing
about HQC, assumption A17, its decoding-failure rate, or any standardized
parameter set. Claim tier: TOY, hard ceiling, PS-R3 only. Full numeric
detail, including per-k arrays for k=2..26 and per-trial S arrays, is in
`matched_pair_results.json`; `run_manifest.yaml` carries the reproduction
record (commit, dirty state, seeds, environment, timings, spend, validity).

## 0. What was run

Two pre-registered stages, one script (`matched_pair.py`), two invocations,
exactly as `design.md` specifies:

- **Stage 1** (`--stage 1`): zero-new-entropy reconstruction of matched
  pairs from the already-committed shards 5000 and 6000, crossing shard x
  decode variant to obtain the missing half of each pair. Fail-closed
  determinism gate against `pilot_results.json`'s committed S-histograms.
- **Stage 2** (`--stage 2`): a matched-pair arm at fresh shards 8001/8002,
  sized by `T2 = clamp(round(10000 * (SE_pooled_measured * 2.80 / 0.20) ** 2), 20000, 60000)`
  using stage 1's own measured pooled SE at k=17.

Both runs completed with exit code 0 and are `valid_measurement`. Both
`stderr.log`s are empty.

## 1. Determinism gate (stage 1, fail-closed, run first)

**PASS.** The reconstructed S-histograms for the original configuration
(shard 5000 through the defected wrapper, shard 6000 through the unmodified
decoder) are bit-identical, elementwise, to
`pilot_results.json`'s committed `MEASUREMENT.defected.S_histogram` and
`MEASUREMENT.undefected.S_histogram` arrays. Both crossed arms (shard 5000
undefected, shard 6000 defected) were then run to complete each shard's
matched-pair set. Per-trial `S` values, in trial order, for all four stage-1
arms are persisted in `matched_pair_results.json.stage_1.per_trial_S`
(5,000 integers per arm, four arms).

## 2. Fail-closed checks (both stages)

- sha256 pin mismatch selftest: PASS (both runs).
- Injection-invariant mismatch selftest: PASS (both runs).
- D2 (exact generation weight) violations: 0, all 8 arms across both stages.
- D3 (support-cap) violations: 0, all 8 arms across both stages.
- No arm was truncated by its wall-clock cap, either stage.

## 3. Primary cell (k = m = 17)

### Stage 1 (10,000 reconstructed pairs, zero new entropy)

| | shard 5000 | shard 6000 | pooled |
|---|---|---|---|
| point (defected) | -1.085705 | -0.867975 | -0.972172 |
| point (undefected) | -1.187483 | -0.878798 | -1.023739 |
| diff (defected - undefected) | +0.101778 | +0.010823 | +0.051567 |
| SE, matched-pair jackknife | 0.125106 | 0.149899 | 0.096781 |
| SE, unpaired (quadrature) | 0.363062 | 0.483266 | 0.304663 |
| unpaired/paired ratio | 2.902 | 3.224 | 3.148 |
| z (paired) | 0.814 | 0.072 | 0.533 |

Stage-2 sizing, substitution shown:
`T2 = clamp(round(10000 * (0.09678123828590589 * 2.80 / 0.20) ** 2), 20000, 60000) = clamp(18359, 20000, 60000) = 20000`
(the raw rounded value 18,359 falls below the pre-registered floor, so the
floor of 20,000 governs).

### Stage 2 (T2 = 20,000 matched pairs, fresh shards 8001/8002, 10,000 each)

| | shard 8001 | shard 8002 | pooled |
|---|---|---|---|
| point (defected) | -0.689438 | -1.645598 | -1.074529 |
| point (undefected) | -0.695988 | -1.659520 | -1.085614 |
| diff (defected - undefected) | +0.006549 | +0.013921 | +0.011085 |
| SE, matched-pair jackknife | 0.024506 | 0.022097 | 0.017905 |
| SE, unpaired (quadrature) | 0.401896 | 0.216868 | 0.277781 |
| unpaired/paired ratio | 16.400 | 9.814 | 15.514 |
| z (paired) | 0.267 | 0.630 | 0.619 |

## 4. Unpaired-vs-paired SE ratio across k=2..26

Reported alongside the paired SE at every k, both stages (full table in
`matched_pair_results.json`; k=17 pooled ratios above: stage 1 = 3.148x,
stage 2 = 15.514x). Selected cells:

| k | stage-1 pooled ratio | stage-2 pooled ratio |
|---|---|---|
| 2 | 10.17x | 10.38x |
| 10 | 6.24x | 10.33x |
| 17 | 3.15x | 15.51x |
| 24 | 1.94x | 51.55x |
| 26 | 1.76x | 92.50x |

## 5. Fitted SE-versus-trial-count exponent

Three points, k=17, ordinary-least-squares fit of `log(SE) = log(c) - alpha * log(T)`:

| T | SE_paired (k=17) | source |
|---|---|---|
| 5,000 | 0.137502 | mean of shard 5000's own paired SE (0.125106) and shard 6000's own paired SE (0.149899) |
| 10,000 | 0.096781 | stage 1 pooled |
| 20,000 | 0.017905 | stage 2 pooled |

**Fitted exponent alpha = 1.470.**

The pre-registered consistency band (declared in advance, `design.md`
Section 5 / DEC-20260809-46e85c) is `alpha` in `[0.4, 0.6]` for consistency
with `1/sqrt(T)` scaling. The measured value (1.470) falls **outside** that
band. Per DEC-20260809-46e85c's pre-registered rule, this supersedes
branches A/B/C of the Coordinator's decision rule; the Executor reports the
number and does not apply that rule or draw a conclusion from it.

## 6. Budget and spend (measured, not modeled)

| | stage 1 | stage 2 | total |
|---|---|---|---|
| core-seconds | 9.66 | 18.857 | 28.517 |
| wall-seconds | 9.45 | 18.649 | 28.099 |

Authorized: 400 core-seconds, 1800 wall-clock seconds, 2 runs. Both runs
completed well inside budget. Total measured spend (28.099 wall-seconds) is
the figure the campaign's ledger archive should debit against
`campaign_budget.total_wall_clock_seconds` (10,800), not an estimate carried
forward.

## 7. Protocol deviations and anomalies (recorded, not discarded)

1. **Infrastructure**: numpy was not installed in this session's Python
   environment at task start. The first `--stage 1` invocation exited 1 with
   `ModuleNotFoundError: No module named 'numpy'` before any data was
   generated -- no result was reported from that attempt. `pip3 install
   --user numpy` installed 2.4.6, matching the version every prior task in
   this campaign records using. This is an infrastructure/environment event
   (AGENTS.md rule 5) and does not bear on either stage's reported validity.
2. **Anomaly, recorded per AGENTS.md rule 8**: stage 1's two shards' matched-
   pair point estimates at k=17 agree in sign (+0.1018, +0.0108) and are
   both individually well under `|z|=1.96`, so DEC-20260809-46e85c's BRANCH
   E anomaly definition (opposite-sign, both individually significant) is
   NOT triggered. Noted for completeness, not as a fired branch.
3. **Anomaly, recorded**: stage 1's measured pooled SE at k=17 (0.0968) is
   materially smaller than the ~0.140 the derivation's own 1/sqrt(T)-scaled
   expectation predicted in advance from the Red Team's single-shard SE
   (0.1982 at T=5,000). This deviation from the pre-run expectation is one
   of the three inputs to the exponent fit in Section 5, which shows
   substantial deviation from 1/sqrt(T) scaling over these three points.
   Not smoothed over, not treated as evidence for or against the design's
   viability -- reported as measured.

## 8. What this task did and did not test (stated precisely)

Tested: defect class V3 (last-block-window-read-early), injection point
`decode_blocks`'s block window (last block only, index `n_e-1`), parameter
set PS-R3 (`n=7187, n_e=56, n_2=128, dup=1, N=7168`), k range 2..26, primary
cell k=m=17. Stage 1: 10,000 matched pairs (5,000 per shard) reconstructed
with zero new PRNG consumption from shards 5000/6000. Stage 2: 20,000
matched pairs (10,000 per shard) from fresh shards 8001/8002.

Not tested here, and not licensed by anything in this report: any other
defect class (in particular V1, global circular shift), any other injection
point, any parameter set other than PS-R3, any standardized HQC parameter
set, HQC's IND-CCA security, its decoding-failure rate, or assumption A17 or
A5. The full 3.09e5-trial run remains unauthorized and unrun. This task's
own `design.md` Section 2 states in advance that stage 1's pooled minimum
detectable effect (~0.275 at z=1.96) exceeds both existing point estimates,
so stage 1 alone cannot produce an effect-excluding null.

## 9. Completion gate (self-check against the handoff, not a verdict)

- `design.md` exists and predates `matched_pair_results.json`: yes (design.md
  was written and reviewed before either `--stage` invocation ran).
- Determinism gate reported PASS with bit-identical committed arrays: yes
  (Section 1 above; full arrays in `matched_pair_results.json.stage_1.determinism_gate`).
- Per-trial S arrays, trial order, all four stage-1 arms: yes
  (`matched_pair_results.json.stage_1.per_trial_S`).
- Per-shard and pooled matched-pair diff, paired SE, unpaired SE, ratio, z
  at k=17 and k=2..26, both stages: yes (Sections 3-4 above; full arrays in
  `matched_pair_results.json`).
- Fitted SE-vs-trial-count exponent across the three points: yes (Section 5).
- Stage-2 trial count equals the pre-registered clamp formula applied to
  stage 1's measured SE, substitution shown: yes (Section 3; T2=20,000).
- `matched_pair.py` reuses `stage_a.py`/`measure.py` via sha256-pinned
  read-only import, only new code is the injection wrapper, driver, and
  matched-pair jackknife: yes (see `matched_pair.py` source; both hashes
  verified matching in `run_manifest.yaml.reused_inputs`).
- `run_manifest.yaml` carries command, git commit/dirty state, environment,
  seeds/shard indices, timings, per-stage core-seconds/wall-clock, validity:
  yes.
- No file outside `write_scope` was created or modified: yes (see final
  report message for the explicit file listing).
