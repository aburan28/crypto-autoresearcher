# confound_break_report.md -- TASK-20260817-c603c0

**Executor observations report. OBSERVATIONS ONLY.**

- task: TASK-20260817-c603c0 / batch BATCH-91929e / goal GOAL-HQC-001
- experiment: EXP-HQC-982268; hypothesis H-HQC-18d1b4 (**stays PROPOSED**;
  this task changes no record's status)
- authorized_by: DEC-20260815-176614
- claim tier: **TOY, hard ceiling**
- runs: 2 of 2 authorized (Part A, Part B). Both terminal, both
  `valid_measurement`.

**WHAT THIS REPORT DOES NOT DO.** It applies none of batch.yaml's frozen
four-branch reading rule (N / R / S / X) and names no branch. It decides
nothing about whether this diagnostic's behaviour is shard-driven,
regime-driven or noise. It concludes nothing about HQC's IND-CCA security, its
decoding-failure rate, assumption A17 or A5, or any standardized parameter
set. It recommends no scaling, pausing, or dispatch of V1. Adjudication
belongs to the Coordinator and the two independent reviews.

---

## 1. Validity gates -- every one, with its verdict

| gate | verdict | detail |
| --- | --- | --- |
| window arithmetic (pairwise disjoint, above prefix, union = `[30000:75000)`) | **PASS** | all four windows |
| high-water re-derivation, shard 5000 | **PASS** | derived 15000, card states 15000 |
| high-water re-derivation, shard 8002 | **PASS** | derived 30000, card states 30000 |
| `START_INDEX=30000` strictly above both high-waters | **PASS** | 30000 >= max(15000, 30000) |
| fail-closed selftest: sha256 pin mismatch | **PASS** | run via `mp.*` before any real trial |
| fail-closed selftest: injection invariant deliberate break | **PASS** | idem |
| module pins (stage_a.py / measure.py / matched_pair.py) | **PASS** | all three measured sha256 match |
| wrapper genuinely calls unmodified `decode_blocks` | **PASS** | `wrapped_original_id` identity check |
| **Arm A DIRECT disjointness proof** | **PASS** | 5000 elements per variant, 10000 total; elementwise per-trial S bit-identical AND S-histogram bit-identical, both variants |
| **Arm B adapted proof, step 1** | **PASS** | exact float64 **bit-identity** on all 8 statistic arrays at k=2..26, both variants; `tolerance_fallback_fired: false`; hard-invariant integers exact |
| **Arm B adapted proof, step 2** | **PASS** | analysis `[0:10000)` prefix bit-identical to the dedicated verification call, both variants |
| **F[:, 0:n_e-1] structural invariant** | **PASS** | all **eight** (shard, window) combinations, mismatch count **0** in every one; 2,475,000 elements total |
| D2 / D3 hard invariants | **PASS** | 0 violations on **all six** decoder calls; D3_cap 4641 |
| no call truncated | **PASS** | all six delivered their full requested trial count |
| one-call-vs-two-call batch structure check | **PASS** | see Section 5 |
| all eight (shard, window) cells finite, `se_paired > 0` at k=17 | **PASS** | |

Full detail: `disjointness_proof_results.json`.

**Arm B's proof is WEAKER than Arm A's and is stated as such.** Arm A's
comparator is a COMMITTED RAW per-trial S array produced in a different
session, process and (here) on a different machine and platform. Arm B has no
such array: TASK-20260809-a79e4f stage 2 persisted only derived statistics.

**The [5000:15000) supplementary check on Arm A: ABSENT-BY-DETERMINATION, not
skipped.** TASK-20260814-8bbdd2's `matched_pair_repeat_results.json` was
scanned mechanically for any integer array of length >= 5000. **None exists.**
That file persists derived statistics, gate verdicts, and
`per_trial_S_retained_tail_length` (an integer, 10000), never a raw array. The
determination is recorded in `disjointness_proof_results.json`
(`task_20260814_8bbdd2_raw_array_determination`), it was made by reading, and
it is not assumed.

**Arm B residual risk -- THE REQUIRED CORRECTION, discharged here
(DEC-20260815-176614 next_actions item (2)).** The genuine residual risk of the
adapted proof is the **SAME-PROCESS-vs-CROSS-PROCESS GAP**: it shows only that
the n_trials=75000 analysis call is self-consistent with a verification call
made inside THIS SAME task's own process, plus a match against previously
committed *derived* statistics. It does NOT compare the analysis call's raw
trial stream against independently generated or previously committed RAW data,
because no such raw data exists for shard 8002. It is **NOT** numpy RNG drift
or platform drift: BATCH-174014's Red Team traced CTRStream directly and
confirmed that a pure SHA-256 counter-mode construction has no numpy-RNG or
platform-dependent component, so TASK-20260815-e61cca design.md Section 3 Step
4's example was wrong and is corrected here.

**Honest narrowing, not closure.** Arm A's direct check did pass on a
different machine, platform, CPython and numpy from the one that produced its
committed comparator, which is a genuine cross-process/cross-machine
determinism datum for this decoder path on this machine. That **NARROWS** Arm
B's gap. It does **NOT CLOSE** it: shard 5000 is a different shard with a
different CTRStream key and a different trial stream. **This task does not
close Arm B's gap.**

---

## 2. PART A -- what ran

Exactly **six** decoder calls, as authorized. Two dedicated verification calls
on shard 8002 at `n_trials=10000` (made first, separately), then **exactly ONE**
`n_trials=75000` analysis call per (shard, variant) -- never split, because a
second call restarts trial indexing at 0 and would silently re-derive an
already-consumed domain. Each `run_arm` invocation carried its own 300-trial
warmup (6 x 300 = 1800). 321,800 trial-decodes total.

Windows, identical for both shards, sliced out of that one call; the prefix
`[0:30000)` was COMPUTED, never skipped, because it carries the proofs.

| window | index range | T | jack batch size |
| --- | --- | --- | --- |
| P1 | `[30000:35000)` | 5,000 | 25 |
| P2 | `[35000:45000)` | 10,000 | 50 |
| N1 | `[45000:55000)` | 10,000 | 50 |
| N2 | `[55000:75000)` | 20,000 | 100 |

`evaluable_k` = 2..26 in **all eight** (shard, window) cells; k=17 reachable
everywhere. **No cross-shard pooling appears anywhere in Part A.**

### 2.1 Measured `se_paired` and `diff` at k=17, per cell

| shard | window | index range | T | batch | `se_paired` | `diff` | `z_paired` | unpaired/paired |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5000 | P1 | `[30000:35000)` | 5,000 | 25 | 0.06980985 | 0.00746666 | 0.1070 | 6.694 |
| 5000 | P2 | `[35000:45000)` | 10,000 | 50 | 0.01687185 | 0.00403561 | 0.2392 | 15.266 |
| 5000 | N1 | `[45000:55000)` | 10,000 | 50 | 0.28196317 | 0.25886125 | 0.9181 | 2.338 |
| 5000 | N2 | `[55000:75000)` | 20,000 | 100 | 0.03621777 | 0.06128523 | 1.6921 | 6.843 |
| 8002 | P1 | `[30000:35000)` | 5,000 | 25 | 0.02509839 | 0.01227076 | 0.4889 | 28.691 |
| 8002 | P2 | `[35000:45000)` | 10,000 | 50 | 0.02005514 | -0.02113451 | -1.0538 | 17.260 |
| 8002 | N1 | `[45000:55000)` | 10,000 | 50 | 0.07458571 | -0.05172586 | -0.6935 | 5.604 |
| 8002 | N2 | `[55000:75000)` | 20,000 | 100 | 0.02470089 | -0.04953396 | -2.0054 | 15.662 |

Per-k results across k=2..26 for every cell are in
`cross_regime_arms_results.json` -> `per_shard_per_window`.

### 2.2 THE FOUR FRESH LOCAL EXPONENTS (the 2x2, fully disjoint, all fresh)

Method, not re-derived and not varied:
`alpha = -[log(SE_hi) - log(SE_lo)] / [log(T_hi) - log(T_lo)]` on `se_paired`
at k=17.

| | regime P (25->50, P1->P2) | regime N (50->100, N1->N2) |
| --- | --- | --- |
| **shard 5000** | **alpha = +2.0488128380076307** | **alpha = +2.960737268597787** (cross-regime) |
| **shard 8002** | **alpha = +0.32362272345795423** (cross-regime) | **alpha = +1.5943364808460014** |

### 2.3 The three pre-registered contrasts

| contrast | definition | value |
| --- | --- | --- |
| regime main effect | mean(P cells) - mean(N cells) | **-1.091319093989102** (mean P = 1.1862177807327925; mean N = 2.2775368747218945) |
| shard main effect | mean(5000 cells) - mean(8002 cells) | **+1.545795451150731** (mean 5000 = 2.504775053302709; mean 8002 = 0.9589796021519779) |
| interaction | (a(5000,P) - a(5000,N)) - (a(8002,P) - a(8002,N)) | **+0.3587893267978908** |

### 2.4 Replication of two historical cells on fresh, disjoint data

The first time any cell in this family has been replicated at the same
(shard, regime) on disjoint data. Historical values are **CITED, NEVER
RECOMPUTED**.

| cell | fresh (this task) | historical (cited) | source | fresh - historical |
| --- | --- | --- | --- | --- |
| shard 5000, regime P | +2.0488128380076307 | +2.836 | EV-HQC-469c08 O6 | **-0.7871871619923692** |
| shard 8002, regime N | +1.5943364808460014 | -0.8662355237627483 | EV-HQC-927899 O4 | **+2.46057200460875** |

Also cited, never recomputed, and **not tested by this task**: shard 6000
regime P = 1.402 (EV-HQC-469c08 O6); shard 8001 regime N =
-0.2682495157085447 (EV-HQC-927899 O3).

Observation recorded without adjudication: all four fresh cells are positive;
the shard-8002/regime-N replication differs in **sign** from its cited
historical value.

---

## 3. PART B -- the null-object control on the diagnostic itself

No decoder calls. Object: per-trial `S ~ Binomial(n_e=56, p)`, both arms drawn
from the IDENTICAL law, differing only in RNG stream.

**Calibrated constant, frozen once before any replicate:** mean per-trial S of
the REAL, UNDEFECTED arm of shard 5000 on window P2 `[35000:45000)`, T=10,000,
= **17.8771**, so **p = 17.8771 / 56 = 0.31923392857142857**, mu = 17.8771.
Held fixed for every rung, every replicate, both arms, and the sensitivity
leg; never retuned.

**The pipeline was the object under test and accepted synthetic input at every
stage without modification**: `mp.arm_hists` (-> `sa.hist_of`,
`sa.batch_hists`) -> `sa.evaluable_k` -> `measure.comb_matrix` ->
`mp.matched_pair_stats` (-> `measure.log2_A_from_hists`) -> the same 2-point
OLS-in-log-log slope. No stage was bypassed, shortcut, approximated or
reimplemented; no pinned module was edited. Nothing had to be reported as a
stage that refused synthetic input.

**Achieved:** R = **200** replicates per rung (the pre-registered value), rungs
**{5000, 10000, 20000, 40000}** (all four). `evaluable_k` = 2..26 at every
rung, identical across all 200 replicates at every rung. **No reduction fired**
-- the projection (5.039 core-seconds) was far under the 540 core-second
trigger; `cost_projection.json` was written unconditionally and records
`no_reduction_fired: true`. Part B is **not** underpowered relative to its own
pre-registration.

### 3.1 Forced value 1 -- `log2 A_k = 0` exactly, at every k, per arm

Measured mean over 200 replicates (arm 0; arm 1 is reported alongside it in
the JSON and behaves the same way):

| rung T | batch | k=2 | k=5 | k=10 | **k=17** | k=26 | max abs dev (any k, any replicate) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5,000 | 25 | 0.00003 | -0.00003 | -0.00349 | **-0.14408** | -3.35952 | 8.089437 |
| 10,000 | 50 | -0.00007 | -0.00067 | -0.00411 | **-0.10164** | -2.71938 | 7.204245 |
| 20,000 | 100 | -0.00000 | -0.00012 | -0.00047 | **-0.02655** | -1.93000 | 5.721446 |
| 40,000 | 200 | 0.00001 | 0.00008 | -0.00114 | **-0.04764** | -1.73307 | 4.619897 |

Replicate SD at k=17: 0.49633, 0.40194, 0.38552, 0.23749 for T = 5,000 /
10,000 / 20,000 / 40,000.

Recorded as measured: the deviation from the forced 0 is negligible at low k,
grows sharply with k, and its magnitude at fixed k decreases with T. Full
per-k means, SDs and mean absolute deviations for both arms at all four rungs
are in `null_object_control_results.json` ->
`ladder_rungs.<T>.forced_value_1_log2_A_k_vs_zero`. **No interpretation of
this pattern is offered here.**

### 3.2 Forced value 2 -- paired diff = 0 exactly, at every k

Measured mean paired diff over 200 replicates:

| rung T | k=2 | k=5 | k=10 | **k=17** | k=26 | k=17 SD | k=17 max abs | max abs dev (any k) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5,000 | 0.00015 | 0.00145 | 0.00677 | **0.01947** | 0.08478 | 0.77227 | 3.24378 | 12.243493 |
| 10,000 | -0.00012 | -0.00123 | -0.00680 | **-0.03894** | -0.04871 | 0.62698 | 2.28725 | 9.062353 |
| 20,000 | -0.00004 | -0.00032 | -0.00062 | **0.02979** | 0.23278 | 0.49067 | 1.82420 | 7.922589 |
| 40,000 | -0.00005 | -0.00069 | -0.00617 | **-0.05446** | -0.24300 | 0.36925 | 1.55817 | 9.284890 |

### 3.3 Forced value 3 -- the 2-point local exponent, forced alpha = 0.5

R = 200 replicates. `se_paired` at k=17: mean (SD) = 0.714552 (0.340570) at
T=5,000; 0.562720 (0.286910) at 10,000; 0.445360 (0.248391) at 20,000;
0.340001 (0.169557) at 40,000.

| rung pair | batch transition | mean | SD | 2.5% | 50% | 97.5% | **null 95% band** | mean - 0.5 | median - 0.5 | forced 0.5 inside band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5000->10000 (**regime P exactly**) | 25->50 | 0.3538522468512989 | 0.7998511073945878 | -1.4498060022752233 | 0.40443932237249225 | 1.7379173378262338 | **[-1.4498, 1.7379]** | -0.14615 | -0.09556 | yes |
| 10000->20000 (**regime N exactly**) | 50->100 | 0.3321988738985283 | 0.7006658834251578 | -1.0295584295881741 | 0.30705949625601725 | 1.7588760235887884 | **[-1.0296, 1.7589]** | -0.16780 | -0.19294 | yes |
| 20000->40000 (beyond both) | 100->200 | 0.37430594487938224 | 0.6843533316009405 | -1.032605597147907 | 0.3707925359761395 | 1.8643962074991292 | **[-1.0326, 1.8644]** | -0.12569 | -0.12921 | yes |

### 3.4 Full-ladder OLS fit (4 rungs, 2 residual degrees of freedom)

`numpy.polyfit(log(T), log(se_paired_k17), 1)`, `alpha = -slope`, per
replicate, R = 200:

- alpha mean **0.35132700707861575**, SD **0.2343335278332064**
- 2.5 / 50 / 97.5 percentiles: **-0.09525689286568811 / 0.3545340158319973 /
  0.7891288122319279**
- mean minus forced 0.5: **-0.14867299292138425**
- mean RMS residual of the 4-point fit: 0.2135568768427767

Scatter of the 2-point estimates about that line (2-point minus full-ladder,
mean / SD / RMS):

| rung pair | mean | SD | RMS |
| --- | --- | --- | --- |
| 5000->10000 | +0.002525239772683152 | 0.7461302430214789 | 0.744266863893217 |
| 10000->20000 | -0.019128133180087402 | 0.6655455884509122 | 0.6641551483907159 |
| 20000->40000 | +0.022978937800766444 | 0.6575149650153659 | 0.6562715376698226 |

### 3.5 REQUIRED DELIVERABLE -- the two contested regimes compared on the null object

Decoder-free, shard-free, defect-free comparison of rung pair 5000->10000
(batch 25->50, regime P exactly) against 10000->20000 (batch 50->100, regime N
exactly), over the same 200 replicates:

- difference of means: **+0.02165337295277059**
- difference of medians: **+0.097379826116475**
- paired-by-replicate mean difference: **+0.021653372952770544**, SD
  **1.2975171744587772**
- regime-N median lies inside the regime-P null band: **yes**
- regime-P median lies inside the regime-N null band: **yes**

Reported as measured. **No conclusion is drawn here** about whether the
confound is a property of the instrument.

### 3.6 SENSITIVITY / ANTI-BLINDNESS LEG -- the verdict

Construction: at T = 20,000, arm B replaced by
`clip(round_half_away_from_zero(mu + g*(S_base - mu)), 0, 56)`, arm A
unchanged, same replicate seeds, R = 200 per g. `rho_g` **MEASURED, never
predicted**.

| g | measured rho_g mean (SD) | rho_g median | planted alpha mean | planted alpha median | unmodified null 95% band | forced-identity residual (mean abs / max abs) | fraction of planted replicates outside band | **verdict** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.25 | 1.1336488355482954 (0.08161838595313571) | 1.1413894366166897 | 0.15494328151690062 | 0.12989469962495886 | [-1.0295584295881741, 1.7588760235887884] | 1.4521890634444645e-15 / 6.217248937900877e-15 | 0.055 | **IN_BAND** |
| 1.5 | 1.213031876791954 (0.1357452545678792) | 1.1666256082070845 | 0.062194354299181215 | 0.05942931364700886 | same | 1.4467799788059344e-15 / 6.217248937900877e-15 | 0.070 | **IN_BAND** |
| 2.0 | 1.3921051777323885 (0.2297092543428978) | 1.3461932792891067 | -0.12650787881952918 | -0.11571936074307773 | same | 1.458215059119139e-15 / 6.217248937900877e-15 | 0.095 | **IN_BAND** |

The forced identity
`alpha_planted(10000 unmodified -> 20000 planted) = alpha_unmodified(10000->20000) - log2(rho_g)`
(exact, since `log2(20000/10000) = 1`) was checked **per replicate with
measured inputs** and holds to float64 rounding: max absolute residual
**6.2e-15** across all three g and all 600 planted replicates.

> ### THE NULL-OBJECT CONTROL IS **BLIND**.
>
> No pre-registered planted magnitude -- not g = 1.25, not g = 1.5, not
> g = 2.0, the largest planted -- produced a planted alpha distribution whose
> median lies outside the unmodified null 95% band at rung pair
> 10000->20000. Under the pre-registered fail-closed rule (design.md Section
> 3.6; batch.yaml `anti_blindness_leg_is_mandatory`), **the control is
> reported BLIND and its null band carries NO interpretive weight at the
> ledger archive.**
>
> This is a **FINDING**, not a failure to route around, and it is the
> **fifth** recorded instance in this campaign of a control found blind to
> what it was built to catch (after CTRL-BS, CTRL-POSHOM, CTRL-IDXMAP and
> BATCH-4b8ad3's planted arm). The risk was named in advance in the task card
> and in batch.yaml, and it fired.
>
> The measurements that make the blindness auditable are all above and in
> `noc_replicate_summary.csv`: the planted departure WAS realized (measured
> rho_g rose monotonically 1.134 -> 1.213 -> 1.392 with g), the forced
> identity linking it to alpha held to 6e-15, and the resulting median shift
> in alpha (-0.18, -0.27, -0.45) was simply small against a null band roughly
> 2.79 wide.
>
> **Scope of the blindness statement:** ONE planted departure class
> (dispersion scaling of one arm) at ONE rung pair, at R = 200, under the
> pre-registered median-outside-band rule. A control blind to that class is
> not thereby shown blind to every class, and this task tested no other.

---

## 4. Declared limitations (stated by the executor, not left for a reviewer)

1. **ONE-CALL-VERSUS-TWO-CALL PROCEDURAL DIFFERENCE, named regardless of the
   check.** In every historical cell the two T-points of a local exponent came
   from DIFFERENT calls in DIFFERENT tasks and processes; in all four fresh
   cells both T-points are sliced from ONE call in ONE process. The check
   performed (Section 5) shows the batch STRUCTURE is identical; it does not
   and cannot show the two procedures are identical in every respect.
2. Only two of the four historically measured shards are represented. **Shards
   6000 and 8001 are not tested at either regime by this task.**
3. Arm A and Arm B share `START_INDEX = 30000`, so absolute index position is
   common to both arms, but the windows still span different index ranges
   within each call. Every window's exact index range is reported above and in
   the JSON so a reviewer can check this directly.
4. **The null object's `Binomial(56, p)` law is not the real S distribution.**
   It is chosen because it makes three values analytically forced. Measured and
   flagged here: the null object's `se_paired` at k=17 (0.71 / 0.56 / 0.45 /
   0.34 across the ladder) is one to two orders of magnitude LARGER than the
   real arms' (0.0169 to 0.2820 across the eight fresh cells). Whether the
   calibration transfers to the real arms' distribution is a scoped question
   the reviews are directed to attack; this task does not assert that it does.
5. **Arm B's disjointness proof remains weaker than Arm A's** and is **not
   closed by this task** (Section 1).
6. The sensitivity leg plants ONE departure class at ONE rung. See the scope
   note in Section 3.6.
7. Environment differs from the environment that produced the committed
   comparator statistics: macOS 26.6 arm64 / CPython 3.13.1 / numpy 2.4.0 here
   versus Linux x86_64 / CPython 3.11.15 / numpy 2.4.6 there. Disclosed in
   advance; in the event, exact float64 bit-identity held and **no tolerance
   fallback was needed or applied.**
8. Claim tier TOY, hard ceiling: PS-R3 reduced parameters, one defect class
   (V3, last-block-window-read-early), one injection point, k range 2..26,
   m = 17. What was measured is the behaviour of an INSTRUMENT this program
   built, not a property of HQC.

## 5. The one-call-versus-two-call check, as performed

For each of the 32 (shard, variant, window) combinations: (a) `sa.batch_hists`
applied to a standalone `np.array` COPY of that window's per-trial S was
bit-identical to `sa.batch_hists` applied to the slice view taken out of the
75000-length array; (b) the batch-edge vector `np.linspace(0, T, 201)
.astype(int)` gave 200 batches of width exactly `T/200` in every case (25, 50,
50, 100 for P1, P2, N1, N2). **PASS**, all 32. The limitation is named anyway
(Section 4 item 1).

## 6. Measured spend -- MEASURED, never estimated

| | wall-clock (s) | core-seconds (s) |
| --- | --- | --- |
| **Part A** (run 1, `cross_regime_arms.py`) | **71.863** | **72.409** |
| **Part B** (run 2, `null_object_control.py`) | **6.508** | **7.664** |
| **TOTAL (executor-measured, debitable)** | **78.371** | **80.073** |
| authorized | 1800 | 900 |
| fraction of authorization used | 4.35% | 8.90% |

Peak RSS: 82,182,144 bytes (Part A), 52,428,800 bytes (Part B) -- both far
under the 4 GB cap. Runs used: 2 of 2 authorized. Decoder calls: 6 of 6
authorized.

Per-call decoder timings (each includes its own 300-trial warmup):
verification 8002 defected 2.295 s / undefected 2.271 s; analysis 5000
defected 16.520 s / undefected 17.070 s; analysis 8002 defected 16.480 s /
undefected 16.468 s.

## 7. Artifacts

All twelve declared artifact paths exist under
`coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/`
and no file outside that directory was created or modified:
`design.md`, `cross_regime_arms.py`, `cross_regime_arms_results.json`,
`disjointness_proof_results.json`, `null_object_control.py`,
`null_object_control_results.json`, `noc_replicate_summary.csv` (1,200 data
rows: 3 unmodified rung pairs x 200 plus 3 planted legs x 200),
`cost_projection.json`, `confound_break_report.md`, `run_manifest.yaml`,
`stdout.log`, `stderr.log`.

## 8. Protocol deviations

One, disclosed in advance and anchored by content hash rather than mtime:
design.md's Section 3.2 calibrated constant `p` is by construction a Part A
measurement, so that one marked block was filled in after Part A's run and
before any Part B replicate. Everything else in design.md -- every constant,
gate, rule, forced value, ladder, R, g list, blindness rule and reduction
protocol -- was frozen before any datum existed. design.md's sha256 immediately
before Part A ran was
`7511ecc1698749156cf89c8c476b93d3baf7c35980a36d5812f21b21f7ba25e0`; after the
block was filled it is
`c3954dcde718818e126d773ab4e6c2ade19bb43bbcea900fe396cc839109be54`. Both are
recorded in `stdout.log` (the first written before the run) and in
`run_manifest.yaml`.

No other deviation. No infrastructure failure, timeout, crash or missing
dependency occurred. No run was discarded, repeated, or omitted.
