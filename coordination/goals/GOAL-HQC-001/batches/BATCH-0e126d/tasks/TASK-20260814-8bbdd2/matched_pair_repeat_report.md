# Report: TASK-20260814-8bbdd2 -- discard-prefix repeat of the T=20,000 matched-pair extension on shards 5000/6000

Executor report. Observations separated from interpretation. Per the
handoff, this report does NOT apply DEC-20260809-186c86's shard-specific-vs-
general-refutation framing, does not conclude anything about A17, HQC's DFR,
any standardized parameter set, and does not change any record's status.
Claim tier: **TOY, hard ceiling**, scoped exactly as stated in `design.md`.

## 1. What was tested, precisely

- Parameter set: **PS-R3** (`n=7187, n_e=56, n_2=128, dup=1, N=7168`),
  identical to `TASK-20260809-a79e4f`.
- Defect class: **V3** (last-block-window-read-early), injection point
  `decode_blocks`'s block window, last block only (index `n_e-1`).
- Shards: **5000 and 6000 only** (never 8001/8002).
- Trial indices requested per call: `[0, 15000)`, one `_t_shard` call per
  `(shard, variant)`, 4 calls total (`(5000,defected)`, `(5000,undefected)`,
  `(6000,defected)`, `(6000,undefected)`).
- Trial indices **retained for every statistic in this report**:
  `[5000, 15000)` per call -- 10,000 new trials per shard, 20,000 pooled.
- Trial indices **discarded from analysis but computed** (for the
  disjointness self-check only): `[0, 5000)` per call.
- k range: 2..26 (authorized range), primary cell k = m = 17.

## 2. Mechanical facts (checked before any statistic below is trusted)

### 2.1 Fail-closed selftests

- sha256 pin mismatch selftest: **PASS**
- Injection-invariant mismatch selftest: **PASS**

### 2.2 Disjointness self-check (fail-closed, run before any statistic was computed from the retained tail)

For each of the 4 `(shard, variant)` calls, the discarded prefix `[0:5000)`
of this run's own freshly generated per-trial `S` was compared, elementwise,
to `TASK-20260809-a79e4f`'s committed `stage_1.per_trial_S` array for the
same `(shard, variant)`, and separately as `S`-histograms:

| shard | variant     | elementwise per-trial S bit-identical | S-histogram bit-identical | verdict |
|-------|-------------|:--------------------------------------:|:---------------------------:|:-------:|
| 5000  | defected    | true | true | PASS |
| 5000  | undefected  | true | true | PASS |
| 6000  | defected    | true | true | PASS |
| 6000  | undefected  | true | true | PASS |

**Overall: PASS on all 4 checks.** The discarded prefix of every call
reproduces `TASK-20260809-a79e4f`'s already-consumed trial range on these
same shards bit-identically, at the strongest available granularity
(per-trial, not merely histogram). This is both the disjointness proof for
the retained tail `[5000:15000)` (it necessarily begins exactly where the
prior task's range ended) and an independent determinism check
(`stage_a.py`'s CTRStream reproduces bit-identical draws across two separate
task invocations, weeks apart, given the same seed/shard/trial-index
inputs).

### 2.3 New standing invariant: F[:, 0:n_e-1] structural check

On the retained 10,000-trial tail slice of each shard, the defected and
undefected decode's block-failure array `F`, restricted to all blocks except
the last (`F[:, 0:n_e-1]`, 55 of 56 blocks), was compared elementwise,
trial-by-trial:

| shard | trials checked | blocks checked/trial | total elements checked | mismatch count | verdict |
|-------|----------------|-----------------------|--------------------------|-----------------|---------|
| 5000  | 10,000 | 55 | 550,000 | 0 | PASS |
| 6000  | 10,000 | 55 | 550,000 | 0 | PASS |

**Overall: PASS on both shards, 0 mismatches out of 1,100,000 elements
checked.** This is the first runtime, array-level (not merely row-sum `S`)
confirmation, on new data, of the "the V3 injection wrapper only touches the
last block" claim EV-HQC-3a0372 O11 named as untested.

### 2.4 D2/D3 hard invariants

Checked over the full 15,000-trial call (not sliceable by trial range, per
the handoff), on all 4 calls:

| call | D2 violations | D3 violations | D3 cap | D3 max w observed |
|------|:---:|:---:|:---:|:---:|
| shard 5000 defected   | 0 | 0 | 4641 | 2746 |
| shard 5000 undefected | 0 | 0 | 4641 | 2746 |
| shard 6000 defected   | 0 | 0 | 4641 | 2746 |
| shard 6000 undefected | 0 | 0 | 4641 | 2746 |

All 4 calls clean (0/0), no call truncated, all 4 calls delivered the full
15,000 requested trials.

### 2.5 Overall run validity

**`valid_measurement`.** All criteria in `design.md` Section 8 were met:
both selftests PASS, the injection wrapper genuinely calls the unmodified
`decode_blocks`, the disjointness self-check PASSES on all 4 calls, the
F-invariant PASSES on both shards, D2/D3 clean on all 4 calls, no
truncation, the pooled estimator returns a finite diff and a finite,
positive `SE_paired` at k=17 on the retained tail.

### 2.6 Spend

Measured: **36.818 core-seconds / 36.785 wall-clock seconds**, against the
500 core-second / 1,800 wall-clock authorization (7.4% / 2.0% of budget).
1 of 2 authorized runs used; the single script invocation succeeded on the
first attempt with no infrastructure failure, so the second authorized run
was not needed.

## 3. Matched-pair statistics on the retained tail (T=10,000/shard, T=20,000 pooled)

### 3.1 Primary cell, k = m = 17

| | diff (defected-undefected) | SE_paired | SE_unpaired | ratio (unpaired/paired) | z_paired |
|---|---:|---:|---:|---:|---:|
| shard 5000 | -0.021471 | 0.017520 | 0.310197 | 17.706 | -1.2256 |
| shard 6000 | +0.038346 | 0.056725 | 0.481149 | 8.482 | 0.6760 |
| **pooled**  | **+0.012680** | **0.032968** | 0.296295 | 8.987 | **0.3846** |

### 3.2 Full k = 2..26 range, pooled

| k | diff | SE_paired | SE_unpaired | ratio | z_paired |
|---:|---:|---:|---:|---:|---:|
| 2 | 0.000119 | 0.000068 | 0.000722 | 10.655 | 1.752 |
| 3 | 0.000342 | 0.000204 | 0.002203 | 10.776 | 1.673 |
| 4 | 0.000650 | 0.000417 | 0.004535 | 10.868 | 1.557 |
| 5 | 0.001016 | 0.000720 | 0.007866 | 10.929 | 1.412 |
| 6 | 0.001409 | 0.001134 | 0.012414 | 10.952 | 1.243 |
| 7 | 0.001790 | 0.001691 | 0.018480 | 10.926 | 1.058 |
| 8 | 0.002116 | 0.002441 | 0.026460 | 10.840 | 0.867 |
| 9 | 0.002352 | 0.003448 | 0.036866 | 10.691 | 0.682 |
| 10 | 0.002488 | 0.004802 | 0.050332 | 10.481 | 0.518 |
| 11 | 0.002561 | 0.006612 | 0.067613 | 10.226 | 0.387 |
| 12 | 0.002677 | 0.009001 | 0.089551 | 9.949 | 0.297 |
| 13 | 0.003028 | 0.012097 | 0.117018 | 9.674 | 0.250 |
| 14 | 0.003887 | 0.016007 | 0.150832 | 9.423 | 0.243 |
| 15 | 0.005578 | 0.020798 | 0.191676 | 9.216 | 0.268 |
| 16 | 0.008425 | 0.026475 | 0.240052 | 9.067 | 0.318 |
| **17** | **0.012680** | **0.032968** | 0.296295 | 8.987 | **0.385** |
| 18 | 0.018465 | 0.040150 | 0.360678 | 8.983 | 0.460 |
| 19 | 0.025723 | 0.047859 | 0.433590 | 9.060 | 0.538 |
| 20 | 0.034217 | 0.055941 | 0.515779 | 9.220 | 0.612 |
| 21 | 0.043542 | 0.064297 | 0.608628 | 9.466 | 0.677 |
| 22 | 0.053158 | 0.072914 | 0.714484 | 9.799 | 0.729 |
| 23 | 0.062424 | 0.081902 | 0.837085 | 10.221 | 0.762 |
| 24 | 0.070610 | 0.091537 | 0.982218 | 10.730 | 0.771 |
| 25 | 0.076894 | 0.102325 | 1.158874 | 11.326 | 0.752 |
| 26 | 0.080332 | 0.115118 | 1.381481 | 12.001 | 0.698 |

`evaluable_k` reachability: k=2..26 (the full authorized range) is reachable
on both shards individually and pooled; k=17 is reached pooled
(`m_reachable_pooled: true`).

## 4. SE-vs-trial-count exponent refit, three points on shards 5000/6000 (measurement, no interpretation)

| T | SE_paired at k=17 | source |
|---:|---:|---|
| 5,000  | 0.137502 | `TASK-20260809-a79e4f` committed stage 1 (mean of per-shard SEs) |
| 10,000 | 0.096781 | `TASK-20260809-a79e4f` committed stage 1 (pooled) |
| 20,000 | 0.032968 | this task (pooled, retained tail only) |

`numpy.polyfit(log(T), log(SE), 1)` over these 3 points gives fitted
exponent **alpha = 1.030146864960655**.

The pre-registered 1/sqrt(T)-consistency band, declared in advance by
`DEC-20260809-46e85c` and carried forward unchanged, is `alpha in [0.4,
0.6]`.

**Comparison to the two reference points named in the handoff, stated as a
measurement, not a conclusion:**

- If the SE at T=20,000 on shards 5000/6000 tracked 1/sqrt(T) from the
  existing (T=5,000; T=10,000) points on these same shards, it would be
  expected to land near **0.068-0.070** (the handoff's own stated range,
  derived from `0.096781 / sqrt(2) approx 0.0684`).
- The **measured** value on this task's retained tail is **0.032968**,
  which is below that 0.068-0.070 range -- closer in magnitude to
  `TASK-20260809-a79e4f`'s own stage 2 pooled SE on shards 8001/8002 at
  T=10,000/shard (0.017905, the number the alpha=1.47 anomaly was
  originally traced to) than to the 1/sqrt(T)-continuation figure.
- The fitted 3-point exponent on shards 5000/6000 alone, alpha=1.030, falls
  outside the pre-registered `[0.4, 0.6]` band, as did the prior task's
  4-shard 3-point fit (alpha=1.470).

No conclusion is drawn here about which of DEC-20260809-186c86's two named
outcomes (shard-specific vs. general refutation of the 1/sqrt(T) scaling
assumption) this measurement supports; that judgment belongs to the
Coordinator, Validator, and Red Team.

## 5. Tested parameters and explicit scope boundary

Tested: PS-R3 only (`n=7187, n_e=56, n_2=128, dup=1, N=7168`), one defect
class (V3), one injection point (`decode_blocks`, block `n_e-1`), shards
5000 and 6000 only, trial indices `[5000, 15000)` per shard (20,000 pooled),
k = 2..26, primary cell k=m=17. Not tested and not extrapolated to: shards
8001/8002 (this task deliberately avoided them, per DEC-20260809-186c86's
design), any standardized HQC parameter set, HQC's IND-CCA security, its
decoding-failure rate, or assumption A17/A5.

## 6. Protocol deviations and anomalies

- No alternative to the discard-prefix technique that avoids editing
  `stage_a.py` was found during design; `design.md` Sections 2 and 7 record
  this as a finding, per the handoff's instruction, not as an obstacle
  routed around silently.
- `matched_pair.py`'s `run_arm()`, `selftest_fail_closed_sha_mismatch()`,
  and `selftest_injection_invariant_fail()` were reused in addition to the
  handoff's explicitly named minimum helper list
  (`make_defected_decode_blocks`, `matched_pair_stats`, `arm_hists`, `cell`,
  `load_module`, `sha256_file`, `core_seconds`, `git_state`). This is
  additional bit-for-bit reuse of the prior task's own code, not a
  re-derivation, and is disclosed rather than silently substituted.
- `matched_pair.py` itself had no pre-declared expected sha256 before this
  task (it is being reused for the first time by this task family). Its
  sha256 was measured at run time (`66266a6178eb46e0b37ec0afdb2620064db56bff82318498e2dd83af1bd1c821`)
  and recorded in `run_manifest.yaml`/`matched_pair_repeat_results.json`,
  not fabricated, per the handoff's explicit instruction.
- No infrastructure failure, timeout, crash, or missing dependency occurred.
  The single script invocation succeeded on its first attempt; the second
  authorized run was not needed.
- No other deviation from `design.md` occurred.

## 7. Completion gate (self-assessment against the handoff's declared gate)

- `design.md` exists, predates `matched_pair_repeat_results.json`, and
  states the discard-prefix technique, `N_DISCARD_PREFIX`/`N_NEW`, the two
  shard indices, the exact slice, the primary cell, the reused jackknife
  construction, and the F-invariant construction: **satisfied**.
- The disjointness self-check is reported PASS on all 4 calls: **satisfied**
  (Section 2.2 above).
- The F[:, 0:n_e-1] structural invariant is reported PASS with a stated
  mismatch count (0) on both shards: **satisfied** (Section 2.3 above).
- `matched_pair_repeat_results.json` carries per-shard and pooled diff,
  paired SE, unpaired SE, ratio, and z at k=17 and across k=2..26:
  **satisfied** (Section 3 above).
- The refitted SE-vs-trial-count exponent across all three points on shards
  5000/6000 is reported, with no conclusion drawn: **satisfied** (Section 4
  above).
- `matched_pair_repeat.py` reuses `stage_a.py`, `measure.py`, and
  `TASK-20260809-a79e4f`'s `matched_pair.py` via sha256-pinned read-only
  import, with only the discard-prefix driver, disjointness self-check, and
  F-invariant check as new code: **satisfied** (Section 6 discloses the
  additional, non-minimal reuse of `run_arm`/selftests, which strengthens
  rather than weakens this criterion).
- `run_manifest.yaml` carries command, git commit and dirty-tree state,
  environment, seeds and shard indices, timings, core-seconds and
  wall-clock, and validity status: **satisfied**.
- No file outside the task's `write_scope` was created or modified:
  **satisfied** (only files under this task's own directory were written;
  see `git status --porcelain` recorded in `run_manifest.yaml`).

All completion-gate items are satisfied.
