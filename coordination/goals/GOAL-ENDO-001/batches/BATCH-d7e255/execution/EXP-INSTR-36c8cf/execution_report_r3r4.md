# Execution report: R3/R4 reanalysis and control (TASK-20260811-bc336d)

`EXP-INSTR-36c8cf` · GOAL-ENDO-001 · BATCH-d7e255 · run `RUN-INSTR-r3r4-nullobj-d3efd7`

Dispatched directly from `DEC-20260811-a4c7ec.next_actions` as a bounded
reanalysis and control under the CTRL-VALUESHUFFLE precedent
(`not_a_new_experiment_contract`, per the task handoff): no new
`specification.yaml`, no amendment, a new module
(`harness/exp_instr_36c8cf/ctrl_r3r4.py`) producing one new immutable run
under the existing, approved `EXP-INSTR-36c8cf` contract. R3 and R4 are
specified verbatim by `RT-20260811-35ab34` (report lines 294-299, 434-444)
and required as the next concrete step by `DEC-20260811-a4c7ec`.

This report **records observations only**. It does not conclude that
HEUR-INSTR-4 is supported or refuted, does not approve, reject, withdraw or
amend `EXP-INSTR-36c8cf` amendment v2 (`approved_by` stays null there), and
does not move `H-INSTR-444c7b` or any other hypothesis status. That judgement
belongs to the Coordinator, after independent review, in a decision record.

## What ran

One run, one module, three analyses on already-collected and freshly-simulated
data — no elliptic-curve arithmetic, no isogeny-class enumeration:

- **R3a**: leave-one-out (jackknife) exceedance-rate reanalysis of family
  `4001`, rung 3 (`n_seeds=48`) of the committed reference-sampling data
  (`RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-reference-sampling.json`).
- **R3b**: exact Fisher's-exact correlation test on the 13-row 2x2 table
  "row has ≥1 jackknife exceedance" × "row fails `sr3v3.stability_check` at
  the rung2→rung3 transition."
- **R4**: a Student-t(df=5) null-object control (finite variance, heavy
  tail), replicated 500 times through the identical, unmodified
  `sr3v3.interval_for_rung` / `sr3v3.stability_check` /
  `sr3v3.z_from_coverage` pipeline functions the real characterisation uses.
  An **optional** matched-variance Gaussian calibration arm (500 replications,
  supplementary context only, not part of R3/R4's own required text) ran
  alongside it.

**Budget.** Wall clock 68.008 s against the handoff's 1800 s cap (3.8% of
budget); CPU 73.005 s; peak RSS 79.7 MB against the 8 GB cap. No timeout, no
resource exhaustion, no infrastructure failure.

**Certificate.** `certificate.kind: none`, explicit. No discrete-log solve,
no factor-base relation, no solver of any kind runs in this module; there is
nothing to certify (`docs/claims-and-verification.md`).

**Determinism.** Two declared master seeds, arbitrary fixed integers, neither
borrowed from the contract's own declared seed schedule (which the task
handoff explicitly disallowed): `R4_MASTER_SEED = 314159265` (Student-t(df=5)
arm) and `R4_GAUSSIAN_MASTER_SEED = 271828182` (optional Gaussian arm). Both
feed `numpy.random.SeedSequence(...).spawn(n_replications)`, further spawned
per row (13 sub-sequences per replication), so every replication and every
row's draw is independently reproducible from the master seed alone.

**z, never transcribed.** `sr3v3.z_from_coverage(519, 520)["z"] =
2.890511560691739`, computed at run time in every place a z is used (the
jackknife refits and every R4 rung), matching (up to float repr) the z the
committed file itself recorded (`2.8905115606917384`) — same double, not a
copy.

**Frozen parameters, read not hardcoded.** The 5% stability threshold
(`amendment_frozen_parameters()["stability_relative_half_width_pct"] = 5.0`)
and the 13 density rows
(`icinv_frozen_grid()["factor_base_sizes"] = [4, 5, 6, 7, 8, 9, 10, 11, 12,
13, 15, 18, 22]`) are both read from their records at run time, never
transcribed as literals.

## R3a — jackknife exceedance reanalysis (observations)

13 rows × 48 held-out seeds = **624 trials**.

| quantity | value |
|---|---|
| jackknife (out-of-sample) exceedances, below | 1 |
| jackknife (out-of-sample) exceedances, above | 2 |
| **jackknife (out-of-sample) exceedances, total** | **3** |
| in-sample exceedances, below | 0 |
| in-sample exceedances, above | 2 |
| **in-sample exceedances, total** | **2** |
| Gaussian-rule expected count (`624/260`) | **2.4000** |
| jackknife total > in-sample total | **True** |

Per-row breakdown (all 13 fb sizes; rows with any exceedance shown with
non-zero counts, all others 0/0):

| fb | jackknife below | jackknife above | in-sample below | in-sample above |
|---|---|---|---|---|
| 11 | 0 | 1 | 0 | 1 |
| 12 | 1 | 0 | 0 | 0 |
| 22 | 0 | 1 | 0 | 1 |
| (all other 10 rows) | 0 | 0 | 0 | 0 |

Observation stated plainly, per the handoff's own instruction: the jackknife
(out-of-sample) exceedance count (3) is greater than the in-sample count (2)
recoverable directly from the committed file's own recorded
`max_per_seed_ratio`/`min_per_seed_ratio` against `interval_high`/
`interval_low` at the already-computed rung-3 interval. This is the direction
V2's F3 finding (in-sample checking mechanically suppresses the true rate)
predicts. The extra jackknife exceedance is at fb=12, on the **below** side —
a row that shows no in-sample exceedance at all, at either tail. Both the
jackknife total (3) and the in-sample total (2) sit below the Gaussian-rule
expected count of 2.4 for the jackknife figure is above it and the in-sample
figure is below it; no tail check or threshold is applied to this comparison
beyond reporting the three numbers side by side, as specified.

## R3b — stability-failure correlation (observations)

`stability_check` recomputed directly from the raw rung-2/rung-3 interval
dicts in the committed file (not from any derived report). Rows failing the
5% rule at the rung2→rung3 transition: **[4, 7, 8, 9, 11, 15, 18, 22]** (8 of
13 rows).

Sanity cross-check against the committed
`sr3v3-interval-stability.json`'s own rung-3 `stability_vs_previous_rung`
(not the source of the reported number — recorded per the handoff's
instruction): `met_at_every_row` agrees (both `False`); `rows_failing` agrees
exactly (`[4, 7, 8, 9, 11, 15, 18, 22]` both ways).

2×2 contingency table ("row has ≥1 jackknife exceedance" × "row fails
stability"):

| | fails stability | does not fail stability | row total |
|---|---|---|---|
| **has jackknife exceedance** | 2 | 1 | 3 |
| **no jackknife exceedance** | 6 | 4 | 10 |
| **column total** | 8 | 5 | 13 |

Exact Fisher's-exact test, direct hypergeometric enumeration (`math.comb`,
no scipy):

```
P(X = x) = C(row1, x) * C(row2, col1 - x) / C(n, col1)
```

with `row1 = 3` (has exceedance), `row2 = 10` (no exceedance), `col1 = 8`
(fails stability), `n = 13`; two-sided p-value = sum of `P(X = x)` over the
support `x ∈ [1, 3]` for every `x` whose probability is ≤ the observed
table's own probability (`x = 2`).

**Fisher's-exact two-sided p-value: 1.000000.**

Observation stated plainly: at 13 rows and 3 total exceedances, this table
carries essentially no power to detect an association between "jackknife
exceedance" and "stability failure" one way or the other; the p-value of
1.0 reflects the small-sample support of the test at this margin
configuration, not a demonstrated absence of association. No permutation-test
cross-check was run (optional, not required); none was needed to compute the
exact result above.

## R4 — Student-t(df=5) null-object control (observations)

500 replications, each redrawing all 13 rows independently, each row's
target location/scale set to that row's own observed rung-3 mean and
`sd_sample_n_minus_1`, drawn as `loc + scale/sqrt(5/3) * standard_t(df=5,
size=1536)` and nested into the 8-rung ladder `[12, 24, 48, 96, 192, 384,
768, 1536]` exactly as E2/E6 nest, run through the identical, unmodified
`interval_for_rung`/`stability_check` pipeline (same computed z, same frozen
5% threshold).

| quantity | value |
|---|---|
| replications completed | 500 / 500 declared |
| **accept-by-rung-8 fraction** | **0.1880 (94 / 500)** |
| first-accept-rung histogram | rung 7: 6; rung 8: 88; **not accepted by rung 8: 406** |

Observation stated plainly: a synthetic heavy-tailed-but-finite-variance
process, matched in location/scale to each row's own observed data and run
through the exact same E2/E3/T1/T2/T3-equivalent pipeline code the real
characterisation uses, reaches `accepted_rung` within the declared 8-rung
ladder in 18.8% of 500 independent replications (94/500) — never at any rung
before 7, and only at rung 7 or 8 when it does. In the remaining 81.2%
(406/500) the simulated ladder does not stabilise by rung 8 at all (the
simulated analogue of F4 firing), exactly as the handoff instructed to record
explicitly when it occurs.

**Diagnostics (gate nothing; reported as raw distributions across
replications, no new pass/fail threshold invented):**

| diagnostic (at the accepted-or-terminal rung, per replication) | n | mean | sd | min | median | max |
|---|---|---|---|---|---|---|
| terminal-rung total exceedance count (of 13 rows × 2 sides = max 26) | 500 | 26.0 | 0.0 | 26 | 26.0 | 26 |
| terminal-rung side asymmetry (above − below) | 500 | 0.0 | 0.0 | 0 | 0.0 | 0 |
| per-replication mean sample skewness (biased Fisher-Pearson `g1`, averaged over the 13 rows' own terminal-rung skewness) | 500 | -0.0000069 | 0.1459 | -1.0299 | -0.0005 | 0.5664 |

Unexpected observation, recorded rather than discarded (AGENTS.md rule 8):
the terminal-rung exceedance count is **exactly 26 (all 13 rows, both sides)
in every one of the 500 replications**, with side-asymmetry exactly 0 in
every replication. This looked like a possible code defect and was checked
independently before being reported: a standalone 200-trial check (`rng.
standard_t(df=5, size=1536)`, in-sample interval at the same z ≈ 2.8905)
confirms both the sample max exceeds `mean + z*sd` and the sample min falls
below `mean - z*sd` in 200/200 trials at n=1536 — i.e. this is a genuine,
reproducible property of the Student-t(df=5) heavy tail at this sample size
under an in-sample-fit interval, not an artifact of this module's code. The
mean per-replication skewness diagnostic is centred near zero (mean
-0.0000069, median -0.0005) with sd 0.1459, consistent with a heavy-tailed
but still roughly *symmetric* generating distribution (Student-t is
symmetric by construction; skewness is not expected to depart materially
from zero for this null object, unlike a purely asymmetric heavy tail
would). This diagnostic gates nothing and is reported as an observation, not
an interpretation.

The full per-replication records (accepted rung, terminal rung, per-row
terminal-rung skewness, terminal-rung exceedance counts and side asymmetry)
are in `r4-student-t5-nullobject.json` under the run directory.

### Supplementary, optional: matched-variance Gaussian calibration arm

Not part of R3/R4's own required text; run for contrast only, same
machinery, `Generator.normal(loc, scale)` in place of the rescaled
`standard_t(df=5)` draw, independent master seed (`271828182`), 500
replications.

| quantity | value |
|---|---|
| **accept-by-rung-8 fraction** | **0.9700 (485 / 500)** |

Reported as context showing the two synthetic arms side by side (0.188 for
the heavy-tailed arm vs 0.970 for the matched-variance Gaussian arm); no
interpretation of what this contrast means for HEUR-INSTR-4 or
`competing_explanation_not_excluded` is offered here — that is the
Coordinator's, after independent review.

## Underspecified judgment calls, stated explicitly

The handoff's own standing rule against unstated judgment calls in a
nominally mechanical task applies; every choice below was underspecified by
the handoff and is recorded here rather than picked silently:

1. **R4 diagnostics aggregation.** The handoff asks for "the per-replication
   sample skewness" and "exceedance count/side-asymmetry at the accepted (or
   terminal) rung" without specifying how to aggregate 13 per-row values into
   one per-replication number. This module computes each row's own skewness
   at the terminal rung's own sample and reports both the full 13-row vector
   per replication (`skewness_per_row_at_terminal`, in the raw artifact) and
   its mean/median across rows as the single per-replication summary used in
   the reported distribution. Exceedance count and side-asymmetry are summed
   /differenced across all 13 rows at the terminal rung, mirroring the R3a
   in-sample construction (each row's own `max_per_seed_ratio`/
   `min_per_seed_ratio` against its own `interval_high`/`interval_low` at
   that rung).
2. **Skewness formula.** Biased (uncorrected) Fisher-Pearson third
   standardised moment, `g1 = mean((x-mean)^3) / std(x)^3` with `std` the
   population (`ddof=0`) standard deviation — the plain textbook definition,
   no small-sample bias correction, since this is a diagnostic on
   already-large rung sizes rather than an inferential statistic anything
   gates on. Stated in `harness/exp_instr_36c8cf/ctrl_r3r4.py::_skewness`.
3. **R4 master seeds.** The handoff requires "a single declared master seed
   of your choice... NOT a contract seed borrowed from elsewhere." Two
   distinct fixed integers were chosen for the two arms (`314159265` for
   Student-t(df=5), `271828182` for the optional Gaussian arm) — recognisable
   fixed constants with no other role anywhere in this campaign, declared
   explicitly here and in the run's `raw-result.json` `parameters` block.
4. **Replication count.** 500 for each arm — within the handoff's own "a few
   hundred is almost certainly enough" guidance, chosen because the observed
   wall-clock cost (68 s total for both arms combined) left large headroom
   under the 1800 s cap and a higher count costs seconds, not budget, exactly
   as the handoff anticipated.
5. **R3b Fisher's-exact "at least as extreme" rule.** Tables with
   `P(X=x) ≤ P(X=a_observed) * (1 + 1e-9)` are summed into the two-sided
   p-value (a floating-point tolerance guard so the observed table's own
   probability is never excluded by rounding) — the standard exact-test
   convention, equivalent to `scipy.stats.fisher_exact`'s default two-sided
   definition, stated in `fishers_exact_2x2`'s own docstring.

## What this does not do

- Does not discharge R1, R2 or R5 (edits to `experiments/EXP-INSTR-36c8cf/
  amendments/v2.yaml` or a successor v3 amendment, filed only by the
  Coordinator).
- Does not approve, reject, withdraw or amend `EXP-INSTR-36c8cf` amendment
  v2. `approved_by` stays null there. No successor run of the real SR3 v3
  characterisation is authorized by this task or by these results.
- Does not touch `RUN-INSTR-36c8cf-phaseA-v2-57ca9a` or
  `RUN-INSTR-36c8cf-phaseA-2a5cd1`. Both are read-only inputs, unedited,
  unre-scored, unre-classified.
- Does not touch `EXP-ICINV-4d33aa` or its SR3 v3 gate. That lane stays
  paused regardless of this task's outcome.
- Makes no curve-side, within-class or between-class claim. `claim_tier:
  toy`, `sota_delta: 0` on every axis.
- Does not move any hypothesis status. `H-INSTR-444c7b`, `H-ICINV-d5e351`
  and `H-ICINV-6c7920` are all outside this task's authority to change.

---

```yaml
execution_report:
  experiment_id: EXP-INSTR-36c8cf
  task_id: TASK-20260811-bc336d
  goal_id: GOAL-ENDO-001
  batch_id: BATCH-d7e255
  implementation_commit: 77b504ce5631d6d52919b5a18fa7e16432fc081c
  new_module: harness/exp_instr_36c8cf/ctrl_r3r4.py
  protocol_deviations: []
  runs:
    completed:
      - RUN-INSTR-r3r4-nullobj-d3efd7
    invalid: []
    failed: []
  observations:
    r3a_jackknife_exceedance_reanalysis:
      trials: 624
      jackknife_exceed_below: 1
      jackknife_exceed_above: 2
      jackknife_exceed_total: 3
      in_sample_exceed_below: 0
      in_sample_exceed_above: 2
      in_sample_exceed_total: 2
      gaussian_rule_expected_count: 2.4
      jackknife_exceeds_in_sample: true
      per_row_nonzero:
        fb_11: {jackknife_above: 1, in_sample_above: 1}
        fb_12: {jackknife_below: 1, in_sample_below: 0, in_sample_above: 0}
        fb_22: {jackknife_above: 1, in_sample_above: 1}
    r3b_stability_correlation:
      rows_failing_stability_rung2_to_rung3: [4, 7, 8, 9, 11, 15, 18, 22]
      contingency_table:
        exceed_and_fails: 2
        exceed_and_ok: 1
        noexceed_and_fails: 6
        noexceed_and_ok: 4
      fisher_exact_p_two_sided: 1.0
      cross_check_vs_committed_stability_report: agrees
    r4_student_t5_null_object_control:
      master_seed: 314159265
      replications: 500
      accept_by_rung8_fraction: 0.188
      accept_by_rung8_count: 94
      first_accept_rung_histogram:
        rung_7: 6
        rung_8: 88
        not_accepted_by_rung8: 406
      diagnostics_note: >-
        Skewness and terminal-rung exceedance/side-asymmetry gate nothing,
        exactly as D2 gates nothing in the real E9 design; full distributions
        in run artifact r4-student-t5-nullobject.json.
    r4_gaussian_calibration_optional_supplementary:
      master_seed: 271828182
      replications: 500
      accept_by_rung8_fraction: 0.97
      accept_by_rung8_count: 485
  anomalies: []
  artifact_paths:
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/manifest.yaml
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/command.txt
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/environment.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/stdout.log
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/stderr.log
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/raw-result.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/jackknife-exceedance.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/stability-correlation.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/stability-correlation-cross-check.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/r4-student-t5-nullobject.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/r4-gaussian-calibration-optional.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/frozen-inputs.json
    - harness/exp_instr_36c8cf/ctrl_r3r4.py
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/execution_report_r3r4.md
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
      task. Pure post-hoc statistics and numpy simulation.
  authority_note: >-
    This report records observations only. It does not approve, reject,
    withdraw or amend EXP-INSTR-36c8cf amendment v2, and does not move
    H-INSTR-444c7b or any other hypothesis status. Interpretation against
    HEUR-INSTR-4 or the amendment's approval is the Coordinator's, after
    independent review, in a decision record.
```
