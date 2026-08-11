# Executor report — matched-pair measurement at the V3/decode_blocks injection point

`TASK-20260809-a79e4f` (executor) / `BATCH-412513` / `GOAL-HQC-001` /
`EXP-HQC-982268`. Authorized by `DEC-20260809-46e85c`. Pre-registered design:
`design.md`, written and frozen before either stage ran.

Claim tier: **toy, hard ceiling.** PS-R3 only. Nothing here is a statement
about HQC, A17, its decoding-failure rate, or any standardized parameter
set. **This is the Executor's own report: observations only. The
pre-registered decision rule in `DEC-20260809-46e85c` is applied by the
Coordinator, not here.**

---

## 1. Mechanical facts

### 1.1 Determinism gate (Stage 1, fail-closed, run first)

**PASS.** The crossed-arm generation was re-run at the ORIGINAL pilot
configuration (shard 5000 through the defected wrapper, shard 6000 through
the unmodified `decode_blocks`) and both whole-arm `S_histogram` arrays were
bit-identical to `pilot_results.json`'s committed
`MEASUREMENT.defected.S_histogram` and `MEASUREMENT.undefected.S_histogram`.
As additional corroboration beyond the histogram check, the rederived
shard-5000-defected point estimate `log2_Ahat_17 = -1.0857050120231229`
matches the pilot's own committed value to full float precision — on a
different machine, OS, Python version, and numpy version than the pilot ran
on (`run_manifest.yaml` records both environments). Full side-by-side
arrays: `matched_pair_results.json.gate_determinism`.

### 1.2 Fail-closed self-tests

Both deliberate-mismatch dry runs — the sha256 pin mismatch and the
injection-invariant break — ran automatically at the start of **both**
stage invocations and reported `PASS` (genuinely aborted with `SystemExit`
for the stated reason) in all four instances. Neither dry run wrote a
`matched_pair_results.json`. See
`matched_pair_results.json.stage{1,2}_run.fail_closed_selftests`.

### 1.3 Hard invariants (D2/D3)

Zero violations on every generated trial, both stages:

- Stage 1 (10,000 trials generated across shards 5000/6000, each decoded
  twice): `stage1_hard_invariants` — `d2_fail=0`, `d3_fail=0` on both
  shards.
- Stage 2 (20,000 trials generated across shards 8000–8003, each decoded
  twice): `stage2_hard_invariants` — `total_d2_fail=0`, `total_d3_fail=0`,
  `max_d3_w_observed=2753` (cap 4641).

D5 (`CTRL-REPLAY`) was not run, matching `pilot_injection.py`'s own
convention of calling the generation primitives with no replay budget; this
is noted as a disclosed convention, not a gap discovered after the fact.

### 1.4 Pairing auditability

Stage 1's four per-trial `S` arrays (shard 5000 true/defected, shard 6000
true/defected), 5,000 entries each in trial order, are persisted verbatim in
`matched_pair_results.json.stage1_per_trial_S`. Entry `i` of a shard's true
and defected arrays derive from the same generated bit array by
construction (one generation pass, two decode calls — `design.md` Section
1), not by post-hoc alignment. Stage 2's raw per-trial arrays are not
persisted (bounded-artifact-size deviation, see `run_manifest.yaml`
`protocol_deviations`); every stage-2 statistic is reproducible bit-for-bit
by re-running `matched_pair.py --stage 2` (deterministic PRNG).

### 1.5 Run counts and spend

Two runs, one per stage, as authorized (`maximum_runs: 2`).

| stage | core-seconds | wall-seconds | authorized (core-s / wall-s) |
|---|---|---|---|
| 1 | 3.73 | 3.337 | 400 / 1800 |
| 2 | 6.565 | 6.102 | 400 / 1800 |
| **total** | **10.295** | **9.439** | 400 / 1800 |

Both stages well within budget individually and combined. Full detail:
`run_manifest.yaml`.

### 1.6 Stage-2 trial count substitution

```
T2 = clamp(round(10000 * (SE_pooled_measured * 2.80 / 0.20) ** 2), 20000, 60000)
SE_pooled_measured (stage 1, pooled, k=17, matched-pair jackknife) = 0.09662406112454607
T2_raw before clamp = 10000 * (0.09662406112454607 * 2.80 / 0.20) ** 2 = 18298.97
T2 = clamp(18299, 20000, 60000) = 20000   (floor binds)
```

Stage 2 ran on fresh shards `8000, 8001, 8002, 8003` (4 of the 12 shards
pre-declared in `design.md` §3.2, used in the declared order), achieving
exactly `T2 = 20,000` trials (`stage2.achieved_equals_planned = true`, no
truncation).

---

## 2. Measured statistics

### 2.1 Stage 1 — zero-new-entropy reconstruction (T=5,000 per shard, T=10,000 pooled)

At the primary cell **k = m = 17**:

| arm | T | log2_Ahat_17 (true) | log2_Ahat_17 (defected) | diff (def − true) | paired SE (matched-pair jackknife) | unpaired SE (quadrature) | ratio (unpaired/paired) | z (paired) |
|---|---|---|---|---|---|---|---|---|
| shard 5000 | 5,000 | −1.18748 | −1.08571 | +0.10178 | 0.12511 | 0.36306 | 2.902 | 0.814 |
| shard 6000 | 5,000 | −0.87880 | −0.86798 | +0.01082 | 0.14990 | 0.48327 | 3.224 | 0.072 |
| **pooled** | **10,000** | **−1.02374** | **−0.97217** | **+0.05157** | **0.09662** | **0.30114** | **3.117** | **0.534** |

Across `k = 2..26`, the paired-jackknife SE is smaller than the unpaired
(quadrature) SE at every k reported (ratios from ~1.76x at k=26 to ~10.0x at
k=2), i.e. the matched-pair design is tighter than the between-shard design
at every reported cell, not only k=17. Full table:
`matched_pair_results.json.stage1.pooled.per_k` (and `.per_shard.{5000,6000}.per_k`).

Stage 1's own pooled minimum-detectable-effect arithmetic
(`DEC-20260809-46e85c`, restated in `design.md` §2.3) put the reachable
floor near 0.275 at z=1.96; the measured pooled diff at k=17 (0.0516) is
below that floor and the measured z (0.534) does not reach significance —
consistent with the pre-stated expectation that stage 1 alone cannot
produce an effect-excluding null.

### 2.2 Stage 2 — matched-pair extension at T2 = 20,000

At the primary cell **k = m = 17**, pooled across the 4 stage-2 shards:

```
T = 20,000
log2_Ahat_17 (true)      = -0.71728
log2_Ahat_17 (defected)  = -0.60249
diff (defected - true)   = +0.11479
paired SE (matched-pair jackknife) = 0.08841
unpaired SE (quadrature)           = 0.33320
ratio (unpaired / paired)          = 3.769
z (paired)                         = 1.298
z (unpaired)                       = 0.345
```

`|z_paired| = 1.298 < 1.96`. `|diff| + 1.96 * SE_paired = 0.1148 + 0.1733 =
0.2881`. Per-shard breakdown (shards 8000–8003) and the full `k=2..26`
table: `matched_pair_results.json.stage2.per_shard`, `.stage2.pooled.per_k`.
As in stage 1, the paired SE is smaller than the unpaired SE at every
reported k (ratios ~1.50x at k=26 to ~10.7x at k≈7).

### 2.3 SE-versus-trial-count exponent

Fitted by ordinary least squares on `log(SE)` vs `log(T)` across the three
available `(T, SE_paired@k=17)` points:

```
T=5,000  (mean of the two stage-1 per-shard paired SEs: 0.12511, 0.14990) -> SE = 0.13750
T=10,000 (stage-1 pooled paired SE)                                       -> SE = 0.09662
T=20,000 (stage-2 pooled paired SE, T2 achieved)                          -> SE = 0.08841

fitted exponent (SE ~ T^-exponent): 0.3186
```

This exponent is **outside** the pre-specified `[0.4, 0.6]` band that
`DEC-20260809-46e85c` / the task card names as superseding branches A/B/C.
Recorded as a mechanical fact (AGENTS.md rule 8); the Executor draws no
conclusion from it about the campaign's required-T derivation or the
1/sqrt(T) assumption it rests on.

---

## 3. What was tested and what was not

- **Defect class**: V3 (last-block-window-read-early) only. V1 (global
  circular shift) was not tested here, as in the pilot.
- **Injection point**: `decode_blocks`'s block window, last block only
  (`n_e - 1`), shifted left by one bit position. No other injection point
  was tested.
- **Parameter set**: PS-R3 only (`n=7187, n_e=56, n_2=128, dup=1, omega=45,
  omega_r=omega_e=51, N=7168, m=17`). No standardized HQC parameter set was
  run.
- **Shards**: stage 1 reused the pilot's own committed shards 5000/6000
  (zero new entropy). Stage 2 used fresh shards 8000–8003 (4 of the 12
  pre-declared in `design.md`; 8004–8011 were not needed at T2=20,000).
- **Trial counts**: 10,000 matched pairs (stage 1, pooled), 20,000 matched
  pairs (stage 2). Not the full `T_req` run at any scale this campaign has
  derived.
- **Solver / estimator**: the real, unmodified `stage_a.py` generation
  primitives and `decode_blocks`, and `measure.py`'s own `comb_matrix` /
  `log2_A_from_hists`, reused via sha256-pinned read-only import throughout.
  The only new code is the injection wrapper (copied in behaviour from
  `pilot_injection.py`), the `dual_decode_shard` driver (a generation-body
  copy of `stage_a.py`'s `_t_shard`, extended to decode twice per batch —
  see `run_manifest.yaml` `protocol_deviations` for why `_t_shard` itself
  could not be reused unmodified for this), and the matched-pair jackknife
  on the per-batch difference.
- No conclusion is drawn here about A17, HQC's decoding-failure rate, any
  standardized parameter set, or whether the campaign should scale up or
  pause. The pre-registered branch rule in `DEC-20260809-46e85c` is applied
  by the Coordinator against the numbers reported above, not by this report.

---

## 4. Deviations and anomalies (see `run_manifest.yaml` for full detail)

1. `os.sched_getaffinity()` unavailable on the macOS host this task ran on;
   fell back to `os.cpu_count()` for the `affinity` provenance field only.
2. `stage_a.py`'s own `_t_shard()` calls `decode_blocks` exactly once per
   batch and cannot itself produce a single-generation-pass matched pair;
   `dual_decode_shard()` is a new driver whose generation body is a
   byte-identical copy of `_t_shard`'s own generation lines, decoding twice
   instead of once. Flagged explicitly per the handoff's own instruction
   that a reused-function rewrite is a finding, not something to route
   around silently. The determinism gate is the check on whether this
   substitution changed anything observable, and it PASSED.
3. D5 (`CTRL-REPLAY`) not run, matching `pilot_injection.py`'s convention.
4. Stage 2's raw per-trial `S` arrays are not persisted (bounded-artifact-
   size choice); every stage-2 statistic is reproducible by re-running
   `--stage 2` (deterministic PRNG).
5. **Anomaly**: the fitted SE-vs-T exponent (0.3186) falls outside the
   pre-specified `[0.4, 0.6]` band (Section 2.3 above).

---

## 5. Artifacts

- `design.md` — pre-registered before any run.
- `matched_pair.py` — the implementation (sha256-pinned reuse of
  `stage_a.py`/`measure.py`, new driver/wrapper/jackknife only).
- `matched_pair_results.json` — full raw results, both stages, per-shard and
  pooled, per-trial `S` arrays for stage 1.
- `run_manifest.yaml` — commands, git/environment state, seeds, timings,
  budget, fail-closed check log, deviations.
- `stdout.log`, `stderr.log` — concatenated console output, stage 1 then
  stage 2.
