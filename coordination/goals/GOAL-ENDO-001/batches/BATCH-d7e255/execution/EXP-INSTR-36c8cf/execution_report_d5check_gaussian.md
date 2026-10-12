# Execution report: Gaussian-arm null-object cross-check of D3/D4/D5 (TASK-20260811-c5a4d5)

`EXP-INSTR-36c8cf` · GOAL-ENDO-001 · BATCH-d7e255 · run `RUN-INSTR-d5check-gaussian-d7a937`

Dispatched to formalize, as a proper committed run, a Gaussian-arm null-object
cross-check of amendment v3 change E11's D3/D4/D5 diagnostic that a
Coordinator off-ledger check and two independent from-scratch reproductions
(Validator, Red Team) had already converged on but which existed nowhere as a
citable artifact. Same `not_a_new_experiment_contract` shape as
`TASK-20260811-409237` and `TASK-20260811-bc336d`: no new
`specification.yaml`, no amendment, one new sibling module
(`harness/exp_instr_36c8cf/ctrl_r3r4_d5check_gaussian.py`) producing one new
immutable run under the existing, approved `EXP-INSTR-36c8cf` contract.
`ctrl_r3r4_d5check.py` and `ctrl_r3r4.py` were **not edited** — `d3_loo`,
`window_for_replication`, `compute_d4_calibration`, `faithfulness_check_indices`,
and `run_full_analysis` are imported and reused from
`ctrl_r3r4_d5check.py`; `R4_GAUSSIAN_MASTER_SEED`, `R4_MASTER_SEED`,
`R4_RUNG_SIZES`, `R4_GAUSSIAN_REPLICATIONS` are imported from `ctrl_r3r4.py`.

This report **records observations only**. It does not conclude that
amendment v3 change E11 is a well- or poorly-calibrated discriminator, does
not clear or reaffirm `DEC-20260811-45583f`'s pause, does not approve, reject
or amend `experiments/EXP-INSTR-36c8cf/amendments/v3.yaml`, and does not move
`H-INSTR-444c7b` or any other hypothesis status. That judgement belongs to
the Coordinator, after independent review, in a decision record.

## Known hazard, and how it was avoided

The handoff named a specific defect both prior reviewers hit independently in
their own from-scratch reproductions: `numpy.random.SeedSequence.spawn()` is
**stateful** — calling `.spawn(k)` on the *same* `SeedSequence` object twice
returns *different* children the second time, silently substituting wrong
draws for whichever replication indices happened to be checked in both a
faithfulness pass and a full pass. Both reviewers' first drafts got 20/485
instead of 21/485 this way.

This module follows exactly the pattern `ctrl_r3r4_d5check.py`'s own
`faithfulness_gate()`/`run_full_analysis()` already use correctly: every
function that needs the replication-level seed stream (`faithfulness_gate_gaussian`,
`run_full_analysis_gaussian`) instantiates its **own fresh**
`numpy.random.SeedSequence(R4_GAUSSIAN_MASTER_SEED)` and calls `.spawn()`
on it **exactly once**. No spawned-from `SeedSequence` object is shared
across two different check passes anywhere in this module. The two calls to
`run_full_analysis_gaussian` (Variant 1 and Variant 2's Gaussian rerun) each
construct their own fresh `SeedSequence(271828182)` internally and spawn
once — this is safe (not the hazard case) and gives byte-identical draws both
times, which is exactly what a deterministic reproduction requires. Verified
empirically: a full-budget rerun of the whole module (`--suffix
d5check-gaussian-d7a937`) reproduced the dry-run's headline numbers exactly.

## What ran

1. **Frozen inputs**, delegated to `ctrl_r3r4_d5check.load_frozen_inputs()`
   unmodified (13 density rows, `z_from_coverage(519, 520)`, rung-3
   mean/`sd_sample_n_minus_1` per row).
2. **Mandatory faithfulness gate, run first**: an *independent*
   reimplementation of the Gaussian draw generation
   (`numpy.random.SeedSequence(271828182).spawn(500)` called once, then per
   replication `rep_seed.spawn(13)` in ascending fb order, then per row
   `rng.normal(loc=loc, scale=scale, size=1536)`, loc/scale from the row's
   own rung-3 mean/sd — deliberately *not* calling `ctrl_r3r4`'s own
   `draw_null_object_replication`, so a transcription/logic drift between the
   reimplementation and the committed record would actually be caught), run
   through `sr3v3.interval_for_rung`/`stability_check`, checked against the
   already-committed `r4-gaussian-calibration-optional.json` for **25
   replication indices spread evenly across the full 0–499 range**
   (`ctrl_r3r4_d5check.faithfulness_check_indices`, reused unmodified):
   `[0, 21, 42, 62, 83, 104, 125, 146, 166, 187, 208, 229, 250, 270, 291, 312,
   333, 353, 374, 395, 416, 437, 457, 478, 499]`.
3. **Variant 1** (as-implemented D4, reused not recomputed): for all 500
   Gaussian-arm replications, D3/D5 computed exactly as
   `ctrl_r3r4_d5check.analyse_replication` does (`abs(D3 loo_z)` vs D4's p99,
   fb=18/fb=22, truncated to `window_for_replication(accepted_rung)` using
   the Gaussian arm's own committed `accepted_rung`), against the
   ALREADY-COMMITTED D4 p99 thresholds read directly from
   `RUN-INSTR-d5check-b8faf7/d4-calibration.json`.
4. **Variant 2** (corrected D4, recalibrated to D3's own two-sided
   extreme-point statistic): a new Monte Carlo null calibration
   (`compute_d4_calibration_extreme`) tracking `abs(LOO z-score)` of
   whichever point (max or min) is most extreme by absolute deviation — the
   exact selection rule D3 itself uses — for `n ∈ {96, 192, 384, 768, 1536}`,
   20,000 trials per `n`, this module's own new declared master seed
   (577215664, distinct from every seed already in this contract). The
   Gaussian arm (485 accepted) and, for completeness/cross-check, the
   Student-t(5) arm (94 accepted, reusing `ctrl_r3r4_d5check.run_full_analysis`
   unmodified) were both rerun through this recalibrated threshold.

**Budget.** Wall clock 16.919 s against the handoff's 1800 s cap (0.94% of
budget); CPU 17.642 s; peak RSS well under the 8 GB cap. No timeout, no
resource exhaustion, no infrastructure failure. (A prior dry run at the
`--suffix d5check-gaussian-dryrun-test` run identifier, produced while
validating this module before the declared deliverable run, is also present
under `experiments/EXP-INSTR-36c8cf/runs/` — run records are immutable and
were not deleted; it reproduced byte-identical headline numbers to the
deliverable run below, confirming determinism, and is recorded here per
"never discard" rather than silently omitted.)

**Certificate.** `certificate.kind: none`, explicit. No discrete-log solve,
no factor-base relation, no solver of any kind runs in this module.

**Determinism.** `R4_GAUSSIAN_MASTER_SEED = 271828182` and
`R4_MASTER_SEED = 314159265` (both imported from `ctrl_r3r4.py`, not
retyped). `D4_EXTREME_MASTER_SEED = 577215664` (this module's own declared
constant — the first nine digits of Euler's constant γ = 0.5772156649...,
following the same naming convention `ctrl_r3r4_d5check.py`'s own
`D4_MASTER_SEED = 141421356` (√2) uses — distinct from `314159265`,
`271828182`, and `141421356`), spawned into 5 independent sub-streams (one
per distinct `n`).

**z, never transcribed.** `sr3v3.z_from_coverage(519, 520)["z"] =
2.890511560691739`, computed at run time.

## Faithfulness gate — PASS

All 25 checked replication indices matched the committed
`r4-gaussian-calibration-optional.json` record **exactly** on
`accepted_rung`, `terminal_rung` and `exceed_total_at_terminal`:

```
all_match = True
n_checked = 25
```

Run before any D3/D4/D5 code was trusted, per the handoff's own instruction.
Full per-index detail is in the run's `faithfulness-gate.json`.

## Variant 1 — as-implemented D4 (max-only, reused)

| quantity | value |
|---|---|
| Gaussian-arm replications with `accepted_rung` set | 485 |
| **D5 fires within the truncated window** | **21** |
| **fraction** | **21/485 = 4.330%** |
| Wilson 95% CI | [2.85%, 6.53%] |

**Matches the two prior independent reproductions' expected 21/485 exactly.**
No reconciliation needed.

Source: `RUN-INSTR-d5check-b8faf7/d4-calibration.json`, sha256
`139d962be4eb6a851c73292f03d4f6aef10b5b3b9a5665d5a0e68093a08caa79`, p99
thresholds `{96: 3.8972, 192: 3.9726, 384: 4.0974, 768: 4.2479, 1536:
4.3675}`, reused directly, not recomputed.

## Variant 2 — D4 recalibrated to D3's own two-sided extreme-point statistic

New D4-extreme calibration (this module's own, 20,000 trials/`n`, master
seed 577215664):

| n (rung) | median | 90th pct. | **99th pct. (new D5 threshold)** | max |
|---|---|---|---|---|
| 96 (rung 4) | 2.7969 | 3.3918 | **4.0595** | 5.2861 |
| 192 (rung 5) | 2.9818 | 3.5231 | **4.1393** | 5.2329 |
| 384 (rung 6) | 3.1604 | 3.6843 | **4.2840** | 5.5503 |
| 768 (rung 7) | 3.3439 | 3.8370 | **4.4029** | 5.4182 |
| 1536 (rung 8) | 3.5264 | 3.9950 | **4.5262** | 5.4826 |

(These 99th-percentile values are of `abs(LOO z-score)` of the max-or-min
extreme point, D3's own selection rule — not `LOO z-score of the maximum`
only, which is what Variant 1's already-committed calibration tracks. See
the module docstring of `compute_d4_calibration_extreme` for why: the
comparison in `analyse_replication_gaussian` and
`ctrl_r3r4_d5check.analyse_replication` is `abs(D3 loo_z) > threshold`, so
calibrating the threshold on the absolute value of the exact same statistic
is the direct reading, not a symmetry argument as Variant 1 required.)

### Gaussian arm rerun

| quantity | value |
|---|---|
| Gaussian-arm replications with `accepted_rung` set | 485 |
| **D5 fires within the truncated window** | **8** |
| **fraction** | **8/485 = 1.649%** |
| Wilson 95% CI | [0.84%, 3.22%] |

**Does NOT match the Red Team's own prior finding of 7/485 (1.443%).** Per
the handoff's own explicit instruction, this is reported plainly rather than
silently reconciled. See "Investigation of the Variant 2 mismatch" below.

### Student-t(5) arm rerun (completeness/cross-check)

| quantity | value |
|---|---|
| Student-t(5) replications with `accepted_rung` set | 94 |
| **D5 fires within the truncated window** | **94** |
| **fraction** | **94/94 = 100.000%** |
| Wilson 95% CI | [96.07%, 100.00%] (Wilson interval for k=n=94; does not
  reach exactly 1 because the Wilson interval is asymptotic, not exact) |

**Matches the Red Team's own prior finding exactly**: UNCHANGED at 94/94
(100%) under the recalibrated threshold, same as under Variant 1's
max-only threshold. No reconciliation needed.

## Investigation of the Variant 2 Gaussian-arm mismatch (8/485 vs. expected 7/485)

This module's own D4-extreme p99 thresholds are a Monte Carlo estimate with
finite (20,000-trial) sampling noise, and this module's declared master seed
(577215664) is necessarily **different** from whatever seed the Red Team's
own off-ledger, uncommitted reproduction used (their reproduction has no
committed script or disclosed seed — the whole reason this task exists is to
create a citable record where none existed). Three checks were run to
distinguish "this module has a defect" from "this is ordinary Monte Carlo
threshold noise from an honestly different declared seed":

1. **Stability under trial-count increase, same seed.** Rerunning
   `compute_d4_calibration_extreme` at 200,000 trials (10× the required
   minimum) with the same declared seed 577215664 gives p99 thresholds
   `{96: 4.0733, 192: 4.1496, 384: 4.2619, 768: 4.3917, 1536: 4.5339}` —
   close to, not identical to, the 20,000-trial values — and the Gaussian-arm
   rerun through that finer calibration **still gives 8/485**, not 7/485.
   This module's own answer is internally stable; it is not an artifact of
   using exactly the amendment's stated 20,000-trial minimum.
2. **Cross-seed sensitivity of the p99 threshold itself.** Recomputing
   `compute_d4_calibration_extreme` at 20,000 trials with four other
   arbitrary seeds (1, 2, 3, 4) gives p99 thresholds that vary by roughly
   ±0.01–0.05 around this module's own values at every `n` (e.g. `n=192`:
   4.1393 (this module) vs. 4.1121–4.1704 across the four alternate seeds).
   This is the expected order of Monte Carlo sampling noise for a
   99th-percentile estimate from 20,000 trials.
3. **Margin of the borderline replication(s).** Inspecting the 8 fired
   replications' per-rung records, replication 149 (fb=22) fires with
   `exceed_count_in_window = 3`, and one of its three exceedances — rung 5,
   `loo_z = 4.1523` against threshold `4.1393` — has a margin of **0.013**,
   an order of magnitude smaller than the ±0.01–0.05 cross-seed threshold
   variation observed in check 2. If a different declared seed's
   Monte-Carlo-estimated threshold at `n=192` happened to land at, say,
   4.153 or higher (well within the observed cross-seed spread), that single
   exceedance would flip to non-exceeding, `exceed_count_in_window` for
   replication 149 would drop to 2 (still ≥2, so D5 would still fire on that
   replication via its other two exceedances) — so this particular
   replication's margin does not by itself explain a full flip from
   "fires" to "does not fire". A full accounting of which single replication
   among the 8 would flip under the Red Team's own (undisclosed) seed was
   not attempted, since their seed and script are not available to reproduce
   directly; the point of checks 1–3 is only to establish that an 8-vs-7
   discrepancy of this size is consistent with ordinary Monte Carlo
   threshold-estimation noise between two honestly different, individually
   valid declared seeds, not necessarily a defect in this module.

**Conclusion of the investigation, stated plainly and not overclaimed:**
this module's own result — 8/485 (1.649%), stable across trial counts and
internally consistent — is reported as the headline Variant 2 Gaussian-arm
figure. It differs from the Red Team's own prior 7/485 finding by exactly
one replication out of 485, a difference that is plausibly, though not
provably (their draws are not reproducible without their own script/seed),
attributable to Monte Carlo threshold-estimation noise from an honestly
different declared master seed. This is **not** silently reconciled to 7/485,
and is flagged prominently for Coordinator/Validator/Red Team scrutiny,
exactly as the handoff instructs.

## Comparison table (both variants, both arms)

| variant | arm | fired / accepted | fraction | Wilson 95% CI | matches prior finding? |
|---|---|---|---|---|---|
| 1 (max-only D4, reused) | Gaussian | 21/485 | 4.330% | [2.85%, 6.53%] | **yes**, exactly |
| 2 (D4-extreme, this module's own seed) | Gaussian | 8/485 | 1.649% | [0.84%, 3.22%] | **no** — expected 7/485; investigated above, not reconciled |
| 2 (D4-extreme, this module's own seed) | Student-t(5) | 94/94 | 100.000% | [96.07%, 100.00%] | **yes**, exactly |

## Underspecified judgment calls, stated explicitly

1. **D3-vs-D4 two-sided comparison** (Variant 1): inherited unmodified from
   `ctrl_r3r4_d5check.py`'s own documented judgment call — `abs(D3 loo_z)`
   against D4's one-sided max-only p99 threshold, by the symmetry argument
   recorded there. Not re-litigated here; see that module's own docstring
   and `execution_report_d5check.md` item 2.
2. **D4-extreme statistic reported as `abs(LOO z)`, not the signed value.**
   Since D5's comparison is `abs(D3 loo_z) > threshold`, this module's own
   new D4-extreme calibration reports percentiles of `abs(loo_z)` of the
   max-or-min extreme point directly, rather than reporting the signed
   distribution and requiring a separate symmetry argument at comparison
   time (as Variant 1's inherited threshold does). This is a direct reading
   of "recalibrate D4 to the actual D3 statistic," stated explicitly since
   it is a departure in presentation (not in the underlying comparison,
   which is identical: `abs(D3 loo_z) > threshold` in both variants).
3. **Tie-break in the extreme-point selection** (`compute_d4_calibration_extreme`):
   `np.argmax` over `abs(X - mean)` breaks ties by first occurrence, the
   same "first-encountered wins" rule `d3_loo`'s own docstring documents for
   Python's `max()`. Continuous N(0,1) draws make exact ties probability
   zero; none were observed to matter.
4. **D4-extreme master seed: 577215664** (Euler's constant γ's first nine
   digits), declared explicitly per the handoff's own requirement that it be
   distinct from 314159265, 271828182 and 141421356. No attempt was made to
   search for a seed that would reproduce the Red Team's own 7/485 figure —
   doing so would be exactly the "outcome shopping" this campaign's SR7
   prohibits; the seed was chosen once, before any Variant 2 result was
   seen, for its recognisability, following the same convention the two
   prior modules in this thread already use.
5. **D4-extreme trial count.** 20,000 per `n` (the amendment's own stated
   minimum, and the handoff's own stated minimum), with a stability check at
   200,000 trials (see "Investigation" above) confirming the headline number
   does not change with more trials at this seed.
6. **Faithfulness-gate check count and spread.** 25 indices (the handoff's
   own stated minimum), via `ctrl_r3r4_d5check.faithfulness_check_indices`
   reused unmodified (`np.linspace(0, 499, 25)`, deduplicated, endpoints
   included).
7. **Prior dry-run artifact.** A test invocation of this module under
   `--suffix d5check-gaussian-dryrun-test` was run before the declared
   deliverable run, while validating the module's correctness before trusting
   its output. Per the immutability rule, that run directory was not deleted
   or overwritten; it is recorded here rather than silently discarded, and
   its headline numbers are byte-identical to the deliverable run
   (`RUN-INSTR-d5check-gaussian-d7a937`) reported throughout this document,
   which is the intended deliverable and the one cited in the YAML block
   below.

## What this does not do

- Does not edit `harness/exp_instr_36c8cf/ctrl_r3r4_d5check.py`,
  `ctrl_r3r4.py`, `sr3v3.py`, or anything under `experiments/`. Both
  existing modules' hashes in this run's manifest are `status: clean`
  (untouched).
- Does not touch `RUN-INSTR-r3r4-nullobj-d3efd7` or `RUN-INSTR-d5check-b8faf7`
  (both read-only inputs, sha256-pinned).
- Does not approve, reject, withdraw or amend
  `experiments/EXP-INSTR-36c8cf/amendments/v3.yaml`, and does not draft a v4.
- Does not itself clear or reaffirm `DEC-20260811-45583f`'s pause. That is a
  Coordinator act, after independent review, in a decision record.
- Makes no curve-side, within-class or between-class claim. `claim_tier:
  toy`, `sota_delta: 0` on every axis.
- Does not move any hypothesis status. `H-INSTR-444c7b` stays `specified`.
- Does not conclude that E11's diagnostic is or is not well-calibrated. Both
  headline figures (4.330% and 1.649%/1.443%) are reported as measurements
  against the frozen prediction targets stated in the handoff, not as a
  verdict on the diagnostic's adequacy.

---

```yaml
execution_report:
  experiment_id: EXP-INSTR-36c8cf
  task_id: TASK-20260811-c5a4d5
  goal_id: GOAL-ENDO-001
  batch_id: BATCH-d7e255
  implementation_commit: 0878cc444de0d291a66338c65f7c9d576ccf2d01
  new_module: harness/exp_instr_36c8cf/ctrl_r3r4_d5check_gaussian.py
  protocol_deviations: []
  runs:
    completed:
      - RUN-INSTR-d5check-gaussian-d7a937
    invalid: []
    failed: []
  anomalies:
    - >-
      A prior dry-run invocation of this module (--suffix
      d5check-gaussian-dryrun-test) was run before the declared deliverable
      run, while validating module correctness. Its run directory
      (RUN-INSTR-d5check-gaussian-dryrun-test) was not deleted, per the
      immutability rule; its headline numbers are byte-identical to the
      deliverable run RUN-INSTR-d5check-gaussian-d7a937, confirming
      determinism. Recorded here rather than silently discarded.
    - >-
      Variant 2's Gaussian-arm headline (8/485, 1.649%) does NOT match the
      Red Team's own prior off-ledger finding (7/485, 1.443%), unlike every
      other headline in this task (Variant 1's 21/485 and Variant 2's
      Student-t 94/94, both of which match exactly). Investigated (see
      "Investigation of the Variant 2 mismatch" in the full report): stable
      across a 10x trial-count increase at the same declared seed;
      consistent with ordinary Monte-Carlo threshold-estimation noise
      (observed cross-seed p99 variation of order 0.01-0.05, versus a
      0.013-margin borderline exceedance in the fired set) given that this
      module's declared seed (577215664) necessarily differs from the Red
      Team's own undisclosed, uncommitted seed. NOT silently reconciled to
      7/485; reported plainly as 8/485, flagged for Coordinator/Validator/
      Red Team scrutiny.
  observations:
    faithfulness_gate:
      all_match: true
      n_checked: 25
      checked_indices: [0, 21, 42, 62, 83, 104, 125, 146, 166, 187, 208, 229,
                        250, 270, 291, 312, 333, 353, 374, 395, 416, 437,
                        457, 478, 499]
    variant1_maxonly_d4:
      source_run: RUN-INSTR-d5check-b8faf7
      source_file: d4-calibration.json
      source_sha256: 139d962be4eb6a851c73292f03d4f6aef10b5b3b9a5665d5a0e68093a08caa79
      gaussian_arm:
        n_accepted: 485
        d5_fired_count: 21
        d5_fired_fraction: 0.04329896907216495
        wilson_95_ci: {lower: 0.02845336, upper: 0.06527538}
        matches_prior_reproductions_expected_21_of_485: true
    variant2_extreme_d4:
      master_seed: 577215664
      trials_per_n: 20000
      p99_by_n:
        n_96_rung4: 4.0595
        n_192_rung5: 4.1393
        n_384_rung6: 4.2840
        n_768_rung7: 4.4029
        n_1536_rung8: 4.5262
      gaussian_arm:
        n_accepted: 485
        d5_fired_count: 8
        d5_fired_fraction: 0.01649484536082474
        wilson_95_ci: {lower: 0.00838137, upper: 0.03220737}
        matches_red_team_expected_7_of_485: false
        investigated: true
        investigation_conclusion: >-
          Own result stable under 10x trial-count increase at the same seed;
          discrepancy of 1/485 vs. the Red Team's own undisclosed-seed
          finding is plausibly attributable to Monte-Carlo threshold
          estimation noise (observed cross-seed p99 spread ~0.01-0.05 at
          n=192, vs. a 0.013-margin borderline exceedance), not proven
          identical without the Red Team's own script/seed. Not reconciled.
      student_t_arm:
        n_accepted: 94
        d5_fired_count: 94
        d5_fired_fraction: 1.0
        wilson_95_ci: {lower: 0.96069758, upper: 1.0}
        matches_red_team_expected_unchanged_94_of_94: true
  artifact_paths:
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/manifest.yaml
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/command.txt
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/environment.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/stdout.log
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/stderr.log
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/raw-result.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/faithfulness-gate.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/d4-extreme-calibration.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/d4-maxonly-calibration-reused.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/variant1-maxonly-d4-per-replication.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/variant1-maxonly-d4-summary.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/variant2-extreme-d4-gaussian-per-replication.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/variant2-extreme-d4-gaussian-summary.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/variant2-extreme-d4-student-t-per-replication.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/variant2-extreme-d4-student-t-summary.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-gaussian-d7a937/frozen-inputs.json
    - harness/exp_instr_36c8cf/ctrl_r3r4_d5check_gaussian.py
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/execution_report_d5check_gaussian.md
  executor_assessment:
    protocol_complete: true
    data_quality: good
    requires_rerun: false
  inference:
    requested_policy: executor-implementation
    resolved_model_id: claude-sonnet-5
    reasoning_effort: medium
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness cannot resolve the policy aliases in
      orchestration/model-policies.yaml; every alias falls back to the one
      model the session runs on (AGENTS.md rule 11; CLAUDE.md "Model policy
      note"). Recorded, never silently substituted.
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: No adapter probe receipt exists for this session.
  claim_tier: toy
  sota_delta: 0
  certificate:
    kind: none
    note: >-
      No discrete-log solve, no factor-base relation claim anywhere in this
      task. Pure post-hoc statistics and numpy simulation over already-
      committed synthetic null-object simulations, plus one new Monte Carlo
      D4-extreme calibration (also pure numpy simulation, no solve).
  authority_note: >-
    This report records observations only. It does not approve, reject,
    withdraw or amend EXP-INSTR-36c8cf amendment v3, does not draft a v4, and
    does not move H-INSTR-444c7b or any other hypothesis status. It does not
    itself clear or reaffirm DEC-20260811-45583f's pause. Interpretation is
    the Coordinator's, after independent review, in a decision record.
```
