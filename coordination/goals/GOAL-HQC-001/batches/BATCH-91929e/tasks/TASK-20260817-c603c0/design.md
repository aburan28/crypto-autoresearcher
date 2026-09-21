# design.md -- TASK-20260817-c603c0 (executor)

PRE-REGISTERED DESIGN. WRITTEN AND FROZEN BEFORE ANY DATUM WAS GENERATED.

- task: TASK-20260817-c603c0
- goal: GOAL-HQC-001
- batch: BATCH-91929e
- experiment: EXP-HQC-982268
- hypothesis: H-HQC-18d1b4 (stays PROPOSED; this task changes no record status)
- authorized_by: DEC-20260815-176614
- claim tier: **TOY, hard ceiling**
- role boundary: **OBSERVATIONS ONLY.** This document and every artifact it
  governs record measurements. batch.yaml's frozen four-branch reading rule
  (N / R / S / X) is applied by the Coordinator at the ledger archive. It is
  NOT applied here, and no reported number is shaped toward any branch.

## 0. Scope statement (verbatim ceiling)

PS-R3 reduced parameters only (n=7187, n_e=56, n_2=128, dup=1, N=7168,
k range 2..26, m_load_bearing_order=17). One defect class (V3,
last-block-window-read-early), one injection point (decode_blocks's block
window, LAST BLOCK ONLY, index n_e-1, shifted left by one bit position).
Nothing in this task is a statement about HQC's IND-CCA security, its
decoding-failure rate, assumption A17 or A5, or any standardized parameter
set. Standardized-parameter runs are out of scope and unauthorized. What is
measured here is the behaviour of a scaling-characterization INSTRUMENT this
program built.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics in either
direction (AGENTS.md rule 5).

## 1. Reused, pinned, read-only inputs

| file | expected sha256 | reuse |
| --- | --- | --- |
| `.../BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py` | `06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405` | `_t_shard`, `decode_blocks`, `hist_of`, `batch_hists`, `evaluable_k`, `N_JACK_BATCHES`, `PARAM_SETS` |
| `.../BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py` | `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8` | `comb_matrix`, `log2_A_from_hists` |
| `.../BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py` | `66266a6178eb46e0b37ec0afdb2620064db56bff82318498e2dd83af1bd1c821` | `make_defected_decode_blocks`, `arm_hists`, `matched_pair_stats`, `cell`, `run_arm`, both fail-closed selftests |

All three are loaded READ-ONLY through a fail-closed sha256-pinned loader and
are never written. Their measured sha256 is recorded at run time in
`run_manifest.yaml` and in both results JSON files.

**REUSE CLAIM AND ITS ONE EXCEPTION, STATED IN THE SAME BULLET (the
documentation-accuracy defect EV-HQC-469c08 O10 recorded).** The estimator and
sampler are genuinely IMPORTED, never rebuilt: `mp.make_defected_decode_blocks`,
`mp.arm_hists`, `mp.matched_pair_stats`, `mp.cell`, `mp.run_arm`,
`mp.selftest_fail_closed_sha_mismatch`, `mp.selftest_injection_invariant_fail`,
`sa._t_shard`, `sa.hist_of`, `sa.batch_hists`, `sa.evaluable_k`,
`measure.comb_matrix`, `measure.log2_A_from_hists`. The four bootstrap
utilities `sha256_file`, `core_seconds`, `git_state` and
`load_module_fail_closed` ARE locally re-defined in this task's scripts,
because `matched_pair.py`'s own loader cannot be used to load
`matched_pair.py` itself (chicken-and-egg); this is the identical, disclosed
exception TASK-20260814-8bbdd2 and TASK-20260815-e61cca carried. The locally
re-defined `load_module_fail_closed` is verified byte-identical in behaviour
by asserting it produces the same measured sha256 for the two pinned modules
as `mp.sha256_file` does, and both selftests are run through `mp.*` before any
real trial is decoded.

## 2. PART A -- the confound-breaking 2x2 factorial

### 2.1 Constants (frozen)

```
SHARDS            : arm_A = 5000, arm_B = 8002
VARIANTS          : unmodified decode_blocks; V3-defected wrapper
START_INDEX       : 30000
N_TOTAL_PER_CALL  : 75000
DISCARDED PREFIX  : [0:30000)   -- COMPUTED, never skipped; it carries the proof
ANALYSIS CALLS    : 4  (one per (shard, variant); n_trials=75000; ONE call each,
                        NEVER split -- a second call restarts trial indexing at 0
                        and would silently re-derive an already-consumed domain)
VERIFICATION CALLS: 2  (shard 8002 only, n_trials=10000, one per variant, made
                        BEFORE and separately from the analysis calls)
WARMUP            : 300 trials per run_arm invocation (6 x 300 = 1800)
BATCH             : mp.BATCH = 64 (decoder batching inside _t_shard)
N_JACK_BATCHES    : sa.N_JACK_BATCHES = 200, fixed throughout this task family
PRIMARY CELL      : k = 17
k RANGE REPORTED  : 2..26, intersected with each window's own evaluable_k
```

### 2.2 Retained windows (identical for both shards)

| window | index range | T | jackknife batch size (T/200) |
| --- | --- | --- | --- |
| P1 | `[30000:35000)` | 5,000 | 25 |
| P2 | `[35000:45000)` | 10,000 | 50 |
| N1 | `[45000:55000)` | 10,000 | 50 |
| N2 | `[55000:75000)` | 20,000 | 100 |

Regimes: **regime P** = P1 -> P2, the 25 -> 50 trials-per-batch transition
(shards 5000/6000's historical regime). **regime N** = N1 -> N2, the
50 -> 100 transition (shards 8001/8002's historical regime).

The script ASSERTS, before computing any statistic, that the four windows are
pairwise disjoint, that none overlaps `[0:30000)`, and that their union is
`[30000:75000)`.

### 2.3 Why START_INDEX = 30000, and the high-water re-derivation

30000 is strictly above the previously consumed high-water index on BOTH
shards, and is set EQUAL for the two arms so that absolute trial-index
position is common to them rather than confounded with which arm it is.

- shard 5000: `[0,5000)` consumed by TASK-20260809-a79e4f stage 1;
  `[5000,15000)` by TASK-20260814-8bbdd2 (`n_discard_prefix`=5000,
  `n_new`=10000, `n_total_per_call`=15000). **High-water 15000.**
- shard 8002: `[0,10000)` consumed by TASK-20260809-a79e4f stage 2 (T2=20000
  split 10000/10000 across 8001/8002); `[10000,30000)` by
  TASK-20260815-e61cca (`n_discard_prefix`=10000, `n_new`=20000,
  `n_total_per_call`=30000). **High-water 30000.**

Both were re-derived from the committed records BEFORE this design was frozen
and both match the values the task card states. The script re-asserts them at
run time from the same committed JSON files and STOPS with a reported
discrepancy rather than adjusting the constants silently.

### 2.4 Validity gate -- ARM A (shard 5000): DIRECT disjointness proof, STRONG

**Check.** Slice `[0:5000)` out of Arm A's own n_trials=75000 analysis call,
per variant, and assert elementwise bit-identity against
TASK-20260809-a79e4f stage 1's COMMITTED `per_trial_S` arrays
(`shard_5000_defected`, `shard_5000_undefected`; 5000 elements each). Also
assert `sa.hist_of` bit-identity of both. This is a genuine cross-run,
cross-process, cross-session, cross-machine determinism proof.

**The `[5000:15000)` question, determined by reading, never assumed.**
TASK-20260814-8bbdd2's `matched_pair_repeat_results.json` was read in full.
It persists `disjointness_self_check`, `f_invariant_check`, `reachability`,
`matched_pair` (derived statistics) and `per_trial_S_retained_tail_length`
(an integer), and it persists **NO raw per-trial S array**. Therefore the
additional `[5000:15000)` bit-identity check **CANNOT be performed** and is
reported as ABSENT-BY-DETERMINATION, not skipped. The script re-derives this
determination mechanically at run time (it looks for a raw array under that
file's keys and records what it found).

**On fail:** `infrastructure_error` / `invalid_measurement` per AGENTS.md
rule 5. ABORT before any Arm A statistic is computed.

### 2.5 Validity gate -- ARM B (shard 8002): ADAPTED two-step proof, WEAKER

TASK-20260809-a79e4f stage 2 persisted only DERIVED statistics and
D2/D3 counts for shards 8001/8002 -- no raw per-trial S array. The direct
check is therefore unavailable on Arm B and the adapted proof is used.

- **Step 1.** One dedicated `n_trials=10000` verification call per
  (8002, variant), made BEFORE and separately from the analysis calls.
  Recompute D2 / D3 / D3_cap / D3_max_w and `matched_pair_stats` at k=2..26
  and assert (a) exact integer match of the four hard-invariant integers
  against the committed stage-2 `shard_8002` values, and (b) float64
  bit-identity of every entry of `point_defected`, `point_undefected`,
  `diff`, `se_paired`, `se_unpaired`, `z_paired`, `z_unpaired`,
  `unpaired_over_paired_ratio` against the committed stage-2
  `matched_pair.per_shard.shard_8002` arrays.
  **Disclosed environment difference:** the committed values were produced on
  Linux x86_64 / CPython 3.11.15 / numpy 2.4.6 (4 cores); this task runs on
  macOS arm64 / CPython 3.13.1 / numpy 2.4.0 (14 cores). Bit-identity is
  therefore attempted FIRST and reported as such. If and only if exact
  bit-identity fails, a stated relative tolerance of **1e-9** is applied as a
  fallback and the shortfall is **DISCLOSED AS A FINDING**, with the maximum
  observed relative deviation and the k at which it occurs, never silently
  accepted. Integer quantities admit no tolerance.
- **Step 2.** Assert the analysis call's `[0:10000)` prefix is bit-identical,
  elementwise, to the verification call's own raw per-trial S, per variant.
- **Step 3.** Fail-closed: either step failing on either variant ABORTS Arm B
  as `infrastructure_error` / `invalid_measurement`.
- **Step 4 -- REQUIRED CORRECTION, BINDING, this task's own scheduled
  carry-forward (DEC-20260815-176614 next_actions item (2)).** The genuine
  residual risk of the adapted proof is the
  **SAME-PROCESS-vs-CROSS-PROCESS GAP**: the adapted proof shows only that the
  n_trials=75000 analysis call is self-consistent with a verification call
  made inside THIS SAME task's own process, plus a match against previously
  committed *derived* statistics. It does NOT compare the analysis call's raw
  trial stream against independently generated or previously committed RAW
  data, because no such raw data exists for shard 8002. That is the risk, and
  it is the one to state. It is **NOT** numpy RNG drift or platform drift:
  BATCH-174014's Red Team traced CTRStream directly and confirmed that a pure
  SHA-256 counter-mode construction with an integer-derived key has no
  numpy-RNG or platform-dependent component, so that example -- used in
  TASK-20260815-e61cca's design.md Section 3 Step 4 -- was wrong and is
  corrected here, per DEC-20260815-176614.
- **Step 5 -- honest narrowing, not closure.** Arm A's direct check does
  supply a genuine cross-process, cross-machine determinism datum on this
  machine for this decoder path. That NARROWS Arm B's gap; it does NOT CLOSE
  it, because it is a different shard and therefore a different CTRStream key
  and a different trial stream. This task does not close Arm B's gap.

### 2.6 Validity gate -- the F[:, 0:n_e-1] structural invariant

`F_defected[:, 0:n_e-1] == F_undefected[:, 0:n_e-1]` elementwise, on every
retained trial of every retained window, for **all eight** (shard, window)
combinations. Expected mismatch count 0. Reported per combination with the
element count. A FAIL is `infrastructure_error` / `invalid_measurement`.

### 2.7 Hard invariants and selftests

D2 and D3 stay ON and fail-closed on ALL SIX decoder calls (4 analysis +
2 verification); expected 0 violations on all six, reported per call together
with `D3_cap`, `D3_max_w` and `truncated`. Both `matched_pair.py` fail-closed
selftests (`sha256_pin_mismatch`, `injection_invariant_mismatch`) are run
through `mp.*` BEFORE any real trial is decoded, and a non-PASS on either
aborts.

### 2.8 Statistics computed

Per shard, per window, using `mp.arm_hists` / `sa.evaluable_k` /
`mp.matched_pair_stats` / `measure.comb_matrix` (imported, never re-derived):
`point_defected`, `point_undefected`, `diff`, `se_paired`, `se_unpaired`,
`unpaired_over_paired_ratio`, `z_paired`, `z_unpaired`, at k=17 and at every
k in 2..26 intersected with that window's own evaluable range.

**NO CROSS-SHARD POOLING ANYWHERE IN PART A.**

### 2.9 The four fresh local exponents and the three contrasts

Method, not re-derived and not varied -- the identical 2-point OLS-in-log-log
slope TASK-20260814-8bbdd2 and TASK-20260815-e61cca used:

```
alpha = -[log(SE_hi) - log(SE_lo)] / [log(T_hi) - log(T_lo)]
```

on `se_paired` at k=17.

- `alpha(5000, P)` from P1 -> P2 -- fresh replication of the historical +2.836
- `alpha(5000, N)` from N1 -> N2 -- CROSS-REGIME cell
- `alpha(8002, P)` from P1 -> P2 -- CROSS-REGIME cell
- `alpha(8002, N)` from N1 -> N2 -- fresh replication of the historical -0.8662355237627483

Pre-registered contrasts:

```
regime_main_effect = mean(alpha(5000,P), alpha(8002,P)) - mean(alpha(5000,N), alpha(8002,N))
shard_main_effect  = mean(alpha(5000,P), alpha(5000,N)) - mean(alpha(8002,P), alpha(8002,N))
interaction        = (alpha(5000,P) - alpha(5000,N)) - (alpha(8002,P) - alpha(8002,N))
```

**CITED, NEVER RECOMPUTED** (historical cells):

| cell | value | source |
| --- | --- | --- |
| shard 5000, regime P | 2.836 | EV-HQC-469c08 O6 |
| shard 6000, regime P | 1.402 | EV-HQC-469c08 O6 |
| shard 8001, regime N | -0.2682495157085447 | EV-HQC-927899 O3 |
| shard 8002, regime N | -0.8662355237627483 | EV-HQC-927899 O4 |

### 2.10 The one-call-versus-two-call procedural difference (declared in advance)

In every historical cell the two T-points of a local exponent came from
DIFFERENT calls in DIFFERENT tasks and processes. In all four fresh cells both
T-points are sliced from ONE call in ONE process. Trials are index-keyed and
deterministic and `sa.batch_hists` applies `nb=200` to whatever slice it
receives, so the data should be identical either way.

**Check performed:** for each retained window, (a) recompute
`sa.batch_hists` on a standalone `np.array(...)` COPY of the window's
per-trial S and assert it is bit-identical to `sa.batch_hists` applied to the
slice view taken out of the 75000-length array; (b) record the batch-edge
vector `np.linspace(0, T, 201).astype(int)` and assert every batch width
equals T/200 exactly, which is the batch structure a dedicated T-trial call
would produce. The difference is named as a limitation REGARDLESS of the
check's outcome.

## 3. PART B -- the null-object control on the diagnostic itself

**PART B IS NOT OPTIONAL AND MAY NOT BE REDUCED TO A FOOTNOTE.** It is half of
the dispatched directive and the half on which Part A's interpretation
depends. If Part A overruns, Part B is NOT what gets cut: the reduction
protocol in Section 3.7 applies, and if that is insufficient PART A's scope is
reduced instead, with the reasoning recorded.

### 3.1 The null object

Decoder-free, shard-free, defect-free i.i.d. parametric object: per-trial

```
S ~ Binomial(n_e = 56, p)
```

i.e. the sum of 56 independent Bernoulli(p) block indicators. Independent
blocks are exactly the i.i.d. null under which A_k = 1 holds as an exact
rational identity (established in BATCH-003), which is what makes the three
forced values below analytic rather than assumed.

Both arms of every synthetic matched pair are drawn from the **IDENTICAL**
law and differ only in RNG stream.

### 3.2 Calibration of p -- ONCE, then FROZEN

**Rule, frozen here before any datum exists:**

```
p = (mean per-trial S of the REAL, UNDEFECTED arm of shard 5000 on window P2,
     i.e. indices [35000:45000), T = 10,000) / n_e,   n_e = 56
```

computed to full float64 and then held FIXED for every rung, every replicate,
both arms, and the sensitivity leg. p is calibrated exactly once. It is not
retuned after seeing any result, including the attained `evaluable_k` range.

> **CALIBRATED CONSTANT, FILLED IN FROM PART A'S MEASURED VALUE BY THE RULE
> ABOVE, BEFORE ANY PART B REPLICATE.**
> `mean_S_real_undefected_5000_P2 = 17.8771`
> `p = 17.8771 / 56 = 0.31923392857142857`
> `mu = n_e * p = 17.8771`
> (measured by Part A run 1, `cross_regime_arms_results.json` ->
> `part_b_p_calibration_input`; FROZEN from here on for every rung, every
> replicate, both arms and the sensitivity leg.)
>
> PROCEDURAL DISCLOSURE, MADE IN ADVANCE: this one block is the ONLY part of
> design.md written after Part A's run, because the value is by construction a
> Part A measurement. Everything else in this file -- every constant, gate,
> rule, forced value, ladder, R, g list, blindness rule and reduction protocol
> -- was frozen before any datum was generated. The sha256 of this file
> immediately before Part A's run, and immediately after this block was
> filled, are BOTH recorded in `stdout.log` and `run_manifest.yaml`, so the
> pre-registration is auditable by content rather than by mtime.

### 3.3 The pipeline IS the object under test

Synthetic per-trial S arrays are fed through the SAME path Part A uses,
imported from the same pinned modules and with no stage bypassed, shortcut,
approximated or reimplemented:

```
mp.arm_hists(sa, S, n_e, nb=200)
  -> sa.evaluable_k(H, n_e)  (intersected across arms, and with 2..26)
  -> measure.comb_matrix(n_e, ks)
  -> mp.matched_pair_stats(measure, n_e, ks, C, H_a, B_a, H_b, B_b)
        (which internally calls measure.log2_A_from_hists)
  -> the same 2-point OLS-in-log-log slope of Section 2.9
```

If any stage cannot accept synthetic input without modification, the run
STOPS and that is reported as a finding. No pinned module is edited
(prohibited) and no parallel implementation is written.

### 3.4 The three forced values

1. **log2 A_k = 0 EXACTLY, at every k, per arm.** A_k = 1 is a theorem on the
   independent-block null. The measured `point_defected` / `point_undefected`
   (arm A / arm B here) and their deviation from 0 are reported at every rung
   and every k. This is the direct decoder-free test of whether
   `log2_A_from_hists` carries a batch-size-dependent bias -- which would by
   itself be a mechanism for the entire observed confound.
2. **paired diff = 0 EXACTLY, at every k.** Both arms share one law.
3. **alpha = 0.5 EXACTLY.** Both arms are i.i.d. draws from one fixed law, so
   the true paired SE scales as `c * T^(-1/2)` and a 2-point log-log slope on
   exact SEs returns exactly 0.5. **Stated honestly:** the `T^(-1/2)` law is
   exact only asymptotically, with an `O(T^(-1))` finite-T correction. That is
   precisely why the ladder is run AT the same T values and batch sizes as the
   real arms instead of asserting 0.5 from theory: the measured centre of the
   replicate distribution quantifies the finite-T bias, and its spread is the
   noise floor that has never been measured and on which every number this
   task family has produced depends.

### 3.5 The ladder

- rungs `T in {5000, 10000, 20000, 40000}`, jackknife batch sizes
  `{25, 50, 100, 200}` (all integral at nb=200).
- adjacent pairs: `5000->10000` **is regime P exactly** (25->50);
  `10000->20000` **is regime N exactly** (50->100); `20000->40000` extends
  beyond both contested regimes (100->200).
- `R = 200` independent replicates per rung, streamed one replicate at a time.
- Replicate r's alpha for pair `(T_lo, T_hi)` uses replicate r's own
  `se_paired` at k=17 at each rung. Reported per pair: mean, SD, and the
  2.5 / 50 / 97.5 percentiles, against the forced 0.5. The
  `[2.5, 97.5]` percentile interval is the **null 95% band**.
- **Full-ladder fit:** four-rung OLS of `log(se_paired_k17)` on `log(T)` per
  replicate, giving `alpha_full = -slope` with 2 residual degrees of freedom,
  plus the scatter of the three 2-point estimates about that line.
- **Required deliverable, not an optional extra:** an explicit comparison of
  the `5000->10000` and `10000->20000` null alpha distributions. This is a
  decoder-free, shard-free, defect-free test of whether batch-size regime
  alone shifts this diagnostic.

**RNG, fully specified.** `numpy.random.Generator(PCG64(SeedSequence([
20260817, T, r, arm_index, leg_code])))`, `arm_index in {0,1}`, `leg_code = 0`
for the unmodified ladder and `leg_code = 1 + index of g` for the sensitivity
leg. Every stream is independent and every replicate is reproducible from its
seed tuple alone. `S = rng.binomial(n_e, p, size=T)`.

**Scope limitation reported, not repaired:** the attained `evaluable_k` range
per rung is reported as measured. If it does not cover 2..26 at some rung,
that is reported as a scope limitation. p is NOT retuned after seeing it.

### 3.6 Sensitivity leg -- MANDATORY, anti-blindness, fail-closed

**Why (fifth-instance risk, named in advance).** This campaign has recorded
FOUR consecutive controls found structurally blind to the defect class they
were built to catch (CTRL-BS, CTRL-POSHOM, CTRL-IDXMAP, BATCH-4b8ad3's planted
arm), with the pattern named at BATCH-4b8ad3: an invariance strong enough to
force a control's null also blinds it to any defect sharing that invariance. A
null object that can only ever return "about 0.5, looks fine" would be the
fifth instance.

**Construction, frozen.** At the `T = 20,000` rung, for each pre-registered
`g in {1.25, 1.5, 2.0}`, arm B is replaced by a **dispersion-scaled** variant
of the same draw: with `mu = n_e * p`,

```
S_planted = clip(round_half_away_from_zero(mu + g * (S_base - mu)), 0, n_e)
```

where `S_base` is the ordinary null draw for that replicate and arm. This is a
mean-preserving-in-expectation, dispersion-inflating deterministic transform:
it leaves the arm i.i.d. and shard-free but widens its S-histogram, which is
exactly the kind of departure the paired SE is supposed to see.

**MEASURED, never predicted:**

```
rho_g = se_paired(planted, T=20000) / se_paired(unmodified, T=20000)
```

computed per replicate over the same R replicates, reported as
mean / SD / median.

**Forced identity, checked per replicate.** Since `log2(20000/10000) = 1`,

```
alpha_planted(10000 unmodified -> 20000 planted)
      = alpha_unmodified(10000 -> 20000) - log2(rho_g)      EXACTLY
```

The residual of this identity is reported (max and mean absolute value). It
uses MEASURED inputs and requires no analytic prediction, so it is checkable
without additional assumptions. The identity holds per replicate; an
aggregate-level version is NOT exact (Jensen) and is reported separately and
labelled as such if reported at all.

**In-band / out-of-band verdict, pre-registered.** For each g, the planted
alpha distribution at rung pair `10000->20000` is **OUT OF BAND** iff its
MEDIAN lies outside the unmodified null 95% band `[2.5, 97.5]` percentiles at
that same rung pair. The fraction of planted replicates falling outside that
band is reported alongside, for every g, as a second descriptive figure.

**FAIL-CLOSED BLINDNESS RULE.** If NO g in `{1.25, 1.5, 2.0}` produces an
out-of-band planted distribution, the null-object control is reported
**BLIND**, in that exact word, in `confound_break_report.md`, and its null
band carries **no interpretive weight** at the ledger archive. That is a
finding, not a failure to route around.

### 3.7 Cost-projection reduction protocol -- APPLIED IN ORDER, NEVER IMPROVISED

Trigger: after the first **20** replicates of the `T = 40000` rung, project
total Part B core-second cost from the measured per-replicate cost.

1. If the projection exceeds **60% of the 900 core-second authorization**
   (i.e. > 540 core-seconds), reduce `R` to the largest multiple of 50 that
   fits, floor 50.
2. If `R` would fall below 50, restore `R = 200`, DROP the `T = 40000` rung,
   and re-project.
3. If still infeasible, report Part B as **UNDERPOWERED** with the achieved R
   and rungs, and do NOT present its band as a calibration.

`cost_projection.json` is written **UNCONDITIONALLY**, recording the
projection arithmetic, the achieved R, the achieved rungs, and
`no_reduction_fired: true` when no reduction fires -- so this declared
artifact path can never be missing because a contingency did not occur.

## 4. Budget

Authorized: **1800 wall-clock seconds, 900 core-seconds, 4 GB, maximum 2
runs.** Hard cap; it will not be raised and a raise is not self-grantable.
Run 1 = Part A (`cross_regime_arms.py`). Run 2 = Part B
(`null_object_control.py`). Measured core-seconds and wall-clock are reported
SPLIT BY PART in `run_manifest.yaml`; only executor-measured wall-clock is
debited against the campaign budget, and it is never estimated after the fact.

## 5. Validity criteria (mechanically checkable, fixed before the run)

Part A is `valid_measurement` iff ALL of:

1. both fail-closed selftests PASS;
2. the defected wrapper genuinely calls the unmodified `decode_blocks`
   (`wrapper_calls_unmodified_function` true);
3. all three module sha256 pins match;
4. Arm A's DIRECT disjointness proof PASSES on both variants;
5. Arm B's adapted two-step proof PASSES on both variants (with the tolerance
   actually used stated);
6. the F[:, 0:n_e-1] invariant PASSES with 0 mismatches on all eight
   (shard, window) combinations;
7. D2 = D3 = 0 on all six decoder calls and no call `truncated`, and every
   call delivered its full requested trial count;
8. every one of the eight (shard, window) cells returns a finite `diff` and a
   finite positive `se_paired` at k=17;
9. the four windows are pairwise disjoint and above the discarded prefix.

Any failure of 4, 5, 6 or 7 is `infrastructure_error` / `invalid_measurement`
under AGENTS.md rule 5 and is NOT evidence about the mathematics in either
direction.

Part B is `valid_measurement` iff the pipeline accepted synthetic input
unmodified at every stage, every replicate returned a finite positive
`se_paired` at k=17 at every attained rung, and the achieved R and rung set
are reported as achieved. A BLIND verdict on the sensitivity leg does NOT make
Part B invalid -- it is a recorded finding that bounds how its band may be
used.

## 6. Declared limitations (stated by the executor, not left for a reviewer)

1. **ONE-CALL-VERSUS-TWO-CALL PROCEDURAL DIFFERENCE.** Named in Section 2.10.
   Named as a limitation regardless of the check's outcome.
2. Only two of the four historically measured shards are represented. **6000
   and 8001 are not tested at either regime by this task.**
3. Arm A and Arm B share `START_INDEX = 30000`, so absolute index position is
   common to both arms, but the windows still span different index ranges
   within each call. Every window's exact index range is reported so a
   reviewer can check this directly.
4. The null object's `Binomial(56, p)` law is **not** the real S distribution.
   It is chosen because it makes three values analytically forced; whether the
   calibration transfers to the real arms' distribution is a scoped question
   the reviews are directed to attack.
5. **Arm B's disjointness proof remains weaker than Arm A's**, for the
   data-gap reason in Section 2.5, and is **not closed by this task**.
6. The sensitivity leg plants ONE departure class (dispersion scaling of one
   arm at one rung). A control shown non-blind to that class is not thereby
   shown non-blind to any other.
7. Environment differs from the environment that produced the committed
   comparator statistics (macOS arm64 / CPython 3.13.1 / numpy 2.4.0 here vs
   Linux x86_64 / CPython 3.11.15 / numpy 2.4.6 there). This is disclosed in
   Section 2.5 and its consequences are reported as measured.

## 7. What this task does NOT do

It applies no reading rule; it decides nothing about whether the diagnostic's
behaviour is shard-driven, regime-driven, or noise; it draws no conclusion
about A17, A5, HQC's decoding-failure rate, IND-CCA security, or any
standardized parameter set; it recommends no scaling, pausing, or dispatch of
V1; and it changes no record's status. Claim tier stays TOY.
