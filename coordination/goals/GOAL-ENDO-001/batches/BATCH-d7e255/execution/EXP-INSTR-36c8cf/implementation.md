# EXP-INSTR-36c8cf — implementation notes (Phase A, contract version 2)

**Task** TASK-20260810-c98659 · **Goal** GOAL-ENDO-001 · **Batch** BATCH-d7e255
· **Contract** `experiments/EXP-INSTR-36c8cf/specification.yaml` version 1, as
amended to version 2 by `experiments/EXP-INSTR-36c8cf/amendments/v1.yaml`
(amendment ordinal 1, recorded by DEC-20260810-56db2d)
· **Run** `RUN-INSTR-36c8cf-phaseA-v2-57ca9a` · **claim_tier** toy

This file records *how the code was built and what was run*, including every
attempt that produced no run record. It interprets nothing.

---

## 1. Modules

All new code is under `harness/exp_instr_36c8cf/`, this task's own write scope.
`harness/exp_icinv.py`, `harness/exp_icinv_fullgroup.py`,
`harness/run_saturation.py`, `harness/isogeny_class.py`, `harness/toycurve.py`
and `harness/runner.py` were **read and called, never edited**.

| module | status | role |
|---|---|---|
| `refvalues.py` | **untouched** (version-1 run's module) | published NULL-C profile, detection-bound table, superseded band + slacks, committed p=4001 rate_m3 |
| `sr1.py` | **untouched** (version-1 run's module) | the version-1 seven-construction SR1 driver. **Not imported by this run.** |
| `phase_a.py` | **untouched** (version-1 run's module) | the version-1 driver |
| `refvalues_v2.py` | new | reads every number the amendment freezes, the frozen density grid, and the SR3 v3 reference runs, all at run time with sha256 binding |
| `sr1_g1.py` | new | SR1 as narrowed by change G1 — the two construction-free quantities only |
| `sr3v3.py` | new | the SR3 v3 characterisation: class selection, measurement, estimator, rungs, stability, faithfulness checks |
| `phase_a_v2.py` | new | the Phase A driver for contract version 2 |

The version-1 modules are left byte-identical **on purpose**: the version-1 run
`RUN-INSTR-36c8cf-phaseA-2a5cd1` pins their hashes in its own manifest, and its
code path must stay re-executable. Nothing in this run re-scores, re-keys,
supersedes or edits that run.

## 2. Where every frozen parameter came from

Nothing is transcribed. `refvalues_v2.amendment_frozen_parameters()` parses the
amendment itself; the coverage is taken as the **exact fraction** `519/520`, and

```
z = statistics.NormalDist().inv_cdf(519/520) = 2.8905115606917384
```

is **computed inside the run**. The amendment's own approximate `2.8905` is
never read into the arithmetic. The thirteen density rows and `T = 400` are read
from `experiments/EXP-ICINV-4d33aa/specification.yaml`
(`inputs.parameters.factor_base_sizes`, `target_count_primary`) — which is where
change G5/D1 says they are cited from — and cross-checked against the
amendment's own list; a disagreement would have been fatal, and there was none.

The SR3 v3 **reference runs are not chosen by this task**. They are read from
`harness/exp_icinv_fullgroup.py:BASELINE_RUNS_V2`, the committed map that
EXP-ICINV-4d33aa amendment v2 change A1 fixes, and then read from their own run
records through that module's own `read_baseline_record()`, which hashes both
`raw-result.json` and `manifest.yaml`:

* p = 4001 → `EXP-ICINV-55c2d8 / RUN-ICINV-p4001-fixed`, seed 20260807, T = 400
* p = 6007 → `EXP-ICINV-55c2d8 / RUN-ICINV-f09176`, seed 20260807, T = 400

## 3. The measurement, and the one code-path departure

The characterisation re-measures the reference run at **its own** class
selection rule, factor-base sizes, target count and sampler
(`exp_icinv.targets_uniform`, via `harness/run_saturation.py`).

**Departure, declared and then verified:** the reference driver recomputes the
exact m = 3 sum set per `(curve, fb_size)` on *every* call, so a 48-seed sweep
through it would recompute the same seed-independent object 48 times. The
contract states the sum sets "are computed once and reused, which is what bounds
the cost", so `sr3v3.measure()` computes them once per `(curve, fb_size)` and
scores every seed against that one object. Because that is a different code path
(not different arithmetic), the run calls
`harness.run_saturation.measure_at_density` **unmodified** at all thirteen rows
at two seeds and requires **bit-exact** equality of the variance ratio:

* seed 20260807 (the reference run's own): 13/13 rows exact
* seed 20260810 (the first contract seed): 13/13 rows exact

A mismatch is fatal in the driver and would have prevented any characterisation
being reported.

## 4. Attempts, including the one that produced no run record

| attempt | suffix | outcome |
|---|---|---|
| 1 | `36c8cf-phaseA-v2-479dc9` | **ABORTED before any run record was written.** `implementation_error` in the *faithfulness check*, not in the measurement. Exit code 0 from the wrapper, `RuntimeError` from the driver; **no run directory was created and no run id was consumed.** |
| 2 | `36c8cf-phaseA-v2-57ca9a` | the run reported here |

**What attempt 1's defect was.** `verify_against_reference_driver` required both
the variance ratio *and* the row mean rate to match bit-exactly. The reference
driver reports its row mean as `statistics.mean(rates)` while the NULL-B verdict
object it returns computes `sum(rates)/n`; those two aggregations differ in the
last bits at rows fb = 7 and fb = 18 **inside the reference driver itself**. The
check was therefore comparing two different quantities. It was corrected to test
bit-exact equality of **the variance ratio**, which is the statistic being
characterised, and to *report* both mean-rate values with their difference.
**No measurement code was changed**, and the corrected check passes bit-exactly
at 13/13 rows at both check seeds. Attempt 1's incremental checkpoints are
retained at
`coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/staging-36c8cf-phaseA-v2-479dc9/`.

No result of attempt 1 is used anywhere, and attempt 1 generated no SR3 v3
interval: it aborted at the faithfulness check, before any rung was computed.

## 5. Session survival

Every gate writes an incremental checkpoint to
`.../execution/EXP-INSTR-36c8cf/staging-<suffix>/` as it completes
(`frozen-parameters.json`, `nullc-reproduction.json`, `load-observations.json`,
`sr3v3-family-p4001.json`). Nothing was held only in memory. These staging
directories are **extra paths** not named in the handoff's deliverables list;
they are retained rather than deleted, because they are the record of what
existed at each point.

## 6. Deviations from the approved protocol

See the execution report, section "Protocol deviations", for the numbered list.
The deviations are: the report filename (D1), attempt 1 (D2), sum-set sharing
(D3), measuring the reference run's own seed in addition to the rung seeds (D4),
non-bit-exact agreement with the committed reference rows at ≤ 1.56e-14 relative
(D5), CONFLICT-1 on the sampler (D6), p = 6007 not reached (D7), the inference
policy fallback (D8), the staging directories (D9) and three artifacts beyond
the twenty required (D10).

## 7. What this run does not do

It runs no planting construction, no geometry-specific control, no Phase B cell,
no within-class use of NULL-C, and no curve-side computation of any kind. It
moves no hypothesis status, writes no evidence record, commits nothing, and
claims no completion criterion.
