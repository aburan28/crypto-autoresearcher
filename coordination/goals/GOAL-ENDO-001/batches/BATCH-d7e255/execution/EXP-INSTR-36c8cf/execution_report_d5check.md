# Execution report: D3/D4/D5 truncated-window catch-rate check (TASK-20260811-409237)

`EXP-INSTR-36c8cf` · GOAL-ENDO-001 · BATCH-d7e255 · run `RUN-INSTR-d5check-b8faf7`

Dispatched directly from `DEC-20260811-45583f.next_actions` (the PRIMARY
item), following the same `not_a_new_experiment_contract` shape as
`TASK-20260811-bc336d`: no new `specification.yaml`, no amendment, a new
module (`harness/exp_instr_36c8cf/ctrl_r3r4_d5check.py`) producing one new
immutable run under the existing, approved `EXP-INSTR-36c8cf` contract.
`harness/exp_instr_36c8cf/ctrl_r3r4.py` was **not edited** — every constant
this task needed (`R4_MASTER_SEED`, `R4_RUNG_SIZES`, `R4_REPLICATIONS`) was
imported from it, not retyped.

**The question.** `experiments/EXP-INSTR-36c8cf/amendments/v3.yaml` change
E11 adds D3 (a leave-one-out tail diagnostic), D4 (a Monte-Carlo-calibrated
null threshold) and D5 (a recurrence-across-more-than-one-rung trigger),
scoped to fb=18 and fb=22, into the NOW-APPROVED v3 contract, in response to
V1's (`VAL-20260810-eddc0c`) self-masking finding. `DEC-20260811-45583f`
paused dispatching a REAL successor run against v3 because it was not yet
known whether E11's D3/D4/D5, as specified, would actually have caught the
kind of alternative `RUN-INSTR-r3r4-nullobj-d3efd7` already demonstrated
slips past v3's UNCHANGED T2 acceptance rule 18.8% of the time (94/500
Student-t(df=5) null-object replications). This task answers that
empirically, **reusing the exact same 500-replication simulation** (same
master seed, same draws), by computing D3/D4/D5 exactly as amendment v3
change E11 specifies and checking, per replication, whether D5 would have
fired **within the rung window T2's own first-pass-wins rule would actually
have measured before stopping** — not across all 8 rungs, since rungs after
`accepted_rung` are never measured in the real contract.

This report **records observations only**. It does not conclude that
amendment v3 change E11 closes or fails to close the gap
`DEC-20260811-45583f`'s rationale identifies, does not approve, reject,
withdraw or amend `EXP-INSTR-36c8cf` amendment v3, does not draft a v4, and
does not move `H-INSTR-444c7b` or any other hypothesis status. That judgement
belongs to the Coordinator, after independent review, in a decision record.

## What ran

One run, one new module, four stages, no elliptic-curve arithmetic, no
isogeny-class enumeration, no new random draws for the accept/reject question
itself:

1. **Frozen inputs**, read at run time from their own records (13 density
   rows, `z_from_coverage(519, 520)`, the rung-3 mean/`sd_sample_n_minus_1`
   per row used as the Student-t(5) location/scale, exactly as
   `ctrl_r3r4.py`'s own `load_frozen_inputs`/`load_rung3_family`).
2. **Faithfulness gate** (mandatory, run first): an *independent*
   reimplementation of the Student-t(df=5) draw generation
   (`numpy.random.SeedSequence(314159265).spawn(500)`, then per replication
   `rep_seed.spawn(13)` in ascending fb order, then per row
   `loc + (scale/sqrt(5/3)) * rng.standard_t(df=5, size=1536)`), run through
   `sr3v3.interval_for_rung`/`stability_check` exactly as `ctrl_r3r4.py`
   does, checked against the already-committed
   `r4-student-t5-nullobject.json` for **25 replication indices spread
   evenly across the full 0–499 range** (`np.linspace(0, 499, 25)`,
   deduplicated): `[0, 21, 42, 62, 83, 104, 125, 146, 166, 187, 208, 229,
   250, 270, 291, 312, 333, 353, 374, 395, 416, 437, 457, 478, 499]`.
3. **D4**: a Monte Carlo null calibration, once per distinct rung-4-through-8
   seed count `n ∈ {96, 192, 384, 768, 1536}` (not per replication, not per
   row, per amendment v3 change E11's own text), 20,000 trials per `n`,
   this module's own declared master seed.
4. **D3/D5**: per replication, per row (fb=18, fb=22 only), per rung in the
   **truncated window T2 would actually have measured**, the leave-one-out
   tail diagnostic and the recurrence trigger.

**Budget.** Wall clock 11.378 s against the handoff's 1800 s cap (0.63% of
budget); CPU 12.422 s; peak RSS well under the 8 GB cap. No timeout, no
resource exhaustion, no infrastructure failure.

**Certificate.** `certificate.kind: none`, explicit. No discrete-log solve,
no factor-base relation, no solver of any kind runs in this module.

**Determinism.** `R4_MASTER_SEED = 314159265` (imported from `ctrl_r3r4.py`,
not retyped — reused so the D3/D4/D5 draws are the identical draws the
committed 18.8% figure was measured on). `D4_MASTER_SEED = 141421356` (this
module's own declared constant, the first nine digits of √2, distinct from
`ctrl_r3r4.py`'s `314159265` and `271828182`), spawned into 5 independent
sub-streams (one per distinct `n`).

**z, never transcribed.** `sr3v3.z_from_coverage(519, 520)["z"] =
2.890511560691739`, computed at run time, matching `ctrl_r3r4.py`'s own
computation (same double).

## Faithfulness gate — PASS

All 25 checked replication indices matched the committed
`r4-student-t5-nullobject.json` record **exactly** on `accepted_rung`,
`terminal_rung` and `exceed_total_at_terminal`:

```
all_match = True
n_checked = 25
```

Per the handoff's own instruction, this gate was run **before** any D3/D4/D5
code was trusted, and D3/D4/D5 were computed only after it passed. Full
per-index detail (recomputed vs. committed) is in the run's
`faithfulness-gate.json`.

## D4 — Monte Carlo null calibration (observations)

20,000 trials per `n`, LOO z-score of the sample maximum of `n` i.i.d.
N(0,1) draws:

| n (rung) | median | 90th pct. | **99th pct. (D5 threshold)** | max (of 20,000 trials) |
|---|---|---|---|---|
| 96 (rung 4) | 2.5508 | 3.1771 | **3.8972** | 5.4498 |
| 192 (rung 5) | 2.7468 | 3.3217 | **3.9726** | 5.5668 |
| 384 (rung 6) | 2.9468 | 3.4881 | **4.0974** | 5.6186 |
| 768 (rung 7) | 3.1391 | 3.6633 | **4.2479** | 5.2538 |
| 1536 (rung 8) | 3.3364 | 3.8287 | **4.3675** | 5.4354 |

The 99th-percentile column is what D3's per-row, per-rung LOO z-score is
compared against for D5's recurrence count.

## D3/D5 — truncated to T2's own stopping window (the central result)

**"Stopping" means, for this check:** for each of the 94 replications that
reach `accepted_rung` under T2 (per the already-committed
`r4-student-t5-nullobject.json`), D3/D4/D5 were computed using **only**
rungs 4 through `min(accepted_rung, 8)` — i.e. only the rungs that would
ACTUALLY have been measured before T2's own first-pass-wins rule stopped the
run. All 94 accepted replications in this dataset accept at rung 7 (6
replications) or rung 8 (88 replications) — never earlier — so the truncated
window is either **4 rungs** (rungs 4–7, for the 6 rung-7 accepts) or **5
rungs** (rungs 4–8, for the 88 rung-8 accepts). For the 406 replications that
never reach `accepted_rung` by rung 8, all five rungs 4–8 are available
(informational completeness only — not the central question).

### THE HEADLINE NUMBER

| quantity | value |
|---|---|
| replications with `accepted_rung` set | 94 |
| **replications where D5 fires within the truncated window** | **94** |
| **fraction** | **1.0000 (94/94)** |

**Every one of the 94 replications that T2 would have accepted also has D5
fire within the exact rung window T2 itself would have measured**, at
fb=18, fb=22, or both. Breakdown:

| | count |
|---|---|
| accepted at rung 7 (window = rungs 4–7, 4 rungs), D5 fires | 6 / 6 |
| accepted at rung 8 (window = rungs 4–8, 5 rungs), D5 fires | 88 / 88 |
| D5 fires at fb=18 only | 5 |
| D5 fires at fb=22 only | 3 |
| D5 fires at both fb=18 and fb=22 | 86 |
| accepted replications with fewer than 2 rungs of D3/D4 data available for D5 to check recurrence against | **0** |

The last row directly addresses the structural concern named in
`DEC-20260811-45583f`'s own rationale ("if a heavy-tailed alternative
happens to pass E3 early... fewer than two rungs of D3/D4 data might exist
for D5 to check recurrence against"): in this dataset, that structural gap
does **not** manifest, because first-accepts under this particular
Student-t(df=5) null object never land earlier than rung 7 — leaving at
least 4 rungs of D3/D4 data available in every one of the 94 accepted
replications. This is an observation about *this* alternative and *this*
seed, not a general claim that no alternative could ever accept early enough
to foreclose D5 (see "What this does not do" below).

**When, relative to `accepted_rung`, does D5 first fire** (earliest
qualifying rung across fb=18/fb=22, among the 94 fired replications):

| earliest `d5_fire_rung` | count |
|---|---|
| rung 5 | 58 |
| rung 6 | 22 |
| rung 7 | 12 |
| rung 8 | 2 |

| relative to `accepted_rung` | replications |
|---|---|
| D5 fires **before** `accepted_rung` (at least one of fb=18/fb=22) | 90 |
| D5 fires only **at** `accepted_rung` (both rows, where applicable) | 4 |
| impossible (only one rung existed) | 0 |

D5 fires strictly before T2's own accept point in 90 of the 94 cases (96%),
and no later than T2's own accept point in all 94.

### Informational completeness — the 406 not-accepted-by-rung-8 replications

Not the central question (per the handoff), reported for completeness. All
five rungs 4–8 are available for these (the simulated ladder runs to rung 8
without T2 ever firing):

| quantity | value |
|---|---|
| D5 fires (fb=18 or fb=22, across all 5 rungs) | 404 / 406 (0.9951) |

Full per-replication D3/D5 records (per-rung LOO z-score, excluded point,
LOO mean/sd, D4 threshold, exceed flag, per row) for all 500 replications are
in `d3-d5-per-replication.json` under the run directory; the aggregate is in
`summary.json`.

## Underspecified judgment calls, stated explicitly

Per the handoff's own instruction, every choice below was underspecified by
amendment v3's own D3/D4/D5 text and is recorded here rather than picked
silently:

1. **D3 "single most extreme point" tie-break.** Ties in absolute deviation
   from the row's own in-sample mean are broken by first occurrence (lowest
   seed index within the rung's own ordering) — Python's `max()` over a list
   naturally returns the first-encountered maximal element, so no separate
   tie-break code path was written; stated here since amendment v3's text
   does not specify a rule and no tie was in fact observed in this dataset
   (Student-t(5) draws are continuous; exact ties have probability 0 and none
   occurred).
2. **D3-vs-D4 comparison is two-sided, D4's own calibration is one-sided —
   the most consequential judgment call in this task.** D4 (per amendment
   v3's own text) calibrates only the LOO z-score of the sample *maximum* of
   `n` i.i.d. N(0,1) draws — a one-sided quantity, always effectively
   positive. D3's "single most extreme point" can be the row's *high or low*
   tail. This module compares `abs(D3's LOO z-score)` against D4's
   99th-percentile threshold. Rationale: under the null (N(0,1), symmetric),
   "the most extreme point is the maximum" and "the most extreme point is the
   minimum" each occur with probability 1/2, and the two conditional
   distributions are mirror images of each other by the symmetry of N(0,1) —
   so the distribution of `abs(LOO z-score of the most-extreme-by-absolute-
   deviation point)` has the same magnitude distribution as `LOO z-score of
   the maximum`, which is exactly what D4 calibrates. Comparing absolute
   values is therefore the natural symmetric reading of "exceeds that rung's
   own D4-calibrated 99th-percentile threshold." A one-sided reading (compare
   the signed D3 z-score directly against the positive D4 threshold) would
   make D5 structurally unable to fire on a negative (low-tail) exceedance at
   all, which does not match D5's own stated purpose ("evidence FOR the
   heavy-tail explanation") for a two-sided heavy-tailed alternative. This
   choice is load-bearing for the headline number and is flagged for
   Coordinator/Validator/Red Team scrutiny.
3. **D4 calibration seed derivation.** "A single declared, disclosed master
   seed... one stream reused sequentially... or five independently spawned
   sub-streams — your choice, state which" (handoff's own wording). This
   module uses `numpy.random.SeedSequence(141421356).spawn(5)` — five
   independently spawned sub-streams, one per distinct `n`, in ascending
   rung order — rather than one stream reused sequentially, for the same
   reason `ctrl_r3r4.py` itself prefers `SeedSequence.spawn` over ad hoc
   stream reuse: independence between the five calibrations is then
   structural, not merely assumed.
4. **D4 trial count.** 20,000 per `n` (the amendment's own stated minimum),
   not increased, since the observed wall-clock cost (11.4 s total for the
   whole run) left large headroom under the 1800 s cap and this was judged
   sufficient for stable 99th-percentile estimates at this trial count
   (the five values compare consistently: median/p90/p99/max all increase
   monotonically with `n`, as expected for a maximum-order-statistic
   quantity).
5. **Faithfulness-gate check count and spread.** 25 indices (above the
   handoff's ">= 20" floor), chosen via `np.linspace(0, 499, 25)` for even
   coverage across the full range including both endpoints, rather than a
   random or clustered sample.
6. **"Truncated window" boundary is inclusive of `accepted_rung` itself.**
   Read `window_for_replication` as `range(4, min(accepted_rung, 8) + 1)` —
   i.e. the accepting rung's own D3/D4 data IS included in the window, since
   the real contract's characterisation would have measured that rung (rung
   4 through the accepting rung inclusive) before T2 fired on it; only rungs
   *strictly after* `accepted_rung` are excluded as never-measured.

## What this does not do

- Does not edit `harness/exp_instr_36c8cf/ctrl_r3r4.py`, `sr3v3.py`,
  `refvalues_v2.py`, or anything under `experiments/`. `ctrl_r3r4.py`'s own
  hash in this run's manifest is `status: clean` (untouched).
- Does not touch `RUN-INSTR-r3r4-nullobj-d3efd7` or
  `RUN-INSTR-36c8cf-phaseA-v2-57ca9a`. Both are read-only inputs.
- Does not approve, reject, withdraw or amend
  `experiments/EXP-INSTR-36c8cf/amendments/v3.yaml`, and does not draft a v4.
  `approved_by` stays `coordinator` there exactly as filed; nothing here
  changes it.
- Does not itself clear or reaffirm `DEC-20260811-45583f`'s pause. That is a
  Coordinator act, after independent review, in a decision record.
- Does not generalize beyond the tested alternative. This dataset's 94
  accepted replications all accept at rung 7 or rung 8 — never earlier —
  under the *specific* Student-t(df=5), row-matched-location/scale null
  object `ctrl_r3r4.py` constructs. Whether some *other* heavy-tailed
  alternative (a different distribution family, a different degrees-of-
  freedom, a different seed) could accept earlier than rung 6 — closing the
  "fewer than two rungs available" door `DEC-20260811-45583f`'s rationale
  names — is **not tested here** and is not asserted to be impossible.
- Makes no curve-side, within-class or between-class claim. `claim_tier:
  toy`, `sota_delta: 0` on every axis.
- Does not move any hypothesis status. `H-INSTR-444c7b`, `H-ICINV-d5e351`
  and `H-ICINV-6c7920` are all outside this task's authority to change.

---

```yaml
execution_report:
  experiment_id: EXP-INSTR-36c8cf
  task_id: TASK-20260811-409237
  goal_id: GOAL-ENDO-001
  batch_id: BATCH-d7e255
  implementation_commit: 6bcdcea5d59fad2ee1fe27daddf1f83397cf4524
  new_module: harness/exp_instr_36c8cf/ctrl_r3r4_d5check.py
  protocol_deviations: []
  runs:
    completed:
      - RUN-INSTR-d5check-b8faf7
    invalid: []
    failed: []
  observations:
    faithfulness_gate:
      all_match: true
      n_checked: 25
      checked_indices: [0, 21, 42, 62, 83, 104, 125, 146, 166, 187, 208, 229,
                        250, 270, 291, 312, 333, 353, 374, 395, 416, 437,
                        457, 478, 499]
    d4_calibration:
      trials_per_n: 20000
      master_seed: 141421356
      p99_by_n:
        n_96_rung4: 3.8972
        n_192_rung5: 3.9726
        n_384_rung6: 4.0974
        n_768_rung7: 4.2479
        n_1536_rung8: 4.3675
    headline_d5_catch_rate_within_truncated_window:
      n_replications_with_accepted_rung_set: 94
      d5_fired_count: 94
      d5_fired_fraction: 1.0
      accepted_replications_with_fewer_than_2_rungs_available: 0
      d5_fires_before_accepted_rung_count: 90
      d5_fires_only_at_accepted_rung_count: 4
    informational_not_accepted_by_rung8:
      n_replications: 406
      d5_fired_count: 404
      d5_fired_fraction: 0.9950738916256158
  anomalies: []
  artifact_paths:
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/manifest.yaml
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/command.txt
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/environment.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/stdout.log
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/stderr.log
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/raw-result.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/faithfulness-gate.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/d4-calibration.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/d3-d5-per-replication.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/summary.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-d5check-b8faf7/frozen-inputs.json
    - harness/exp_instr_36c8cf/ctrl_r3r4_d5check.py
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/execution_report_d5check.md
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
      task. Pure post-hoc statistics and numpy simulation over an
      already-committed synthetic null-object simulation.
  authority_note: >-
    This report records observations only. It does not approve, reject,
    withdraw or amend EXP-INSTR-36c8cf amendment v3, does not draft a v4, and
    does not move H-INSTR-444c7b or any other hypothesis status. It does not
    itself clear or reaffirm DEC-20260811-45583f's pause. Interpretation is
    the Coordinator's, after independent review, in a decision record.
```
