# PREREGISTRATION -- TASK-20260803-05e072 (BATCH-008, GOAL-AES-003)

Written **before any measurement run of this task**. The only prior act of this
task was writing the opening budget stamp (C2 clock) into `budget_stamps.jsonl`.

- task: TASK-20260803-05e072
- role: executor
- goal: GOAL-AES-003, batch BATCH-008
- written_at_utc: 2026-08-03T20:13Z (opening stamp 2026-08-03T20:09:55Z,
  binding stop 2026-08-03T21:39:55Z)
- claim tier: **toy**. Reduced-round AES-shaped SPN, one software T-table
  implementation, at most 2^30 trials per arm. Nothing here is a statement
  about full-round or deployed AES and no comparison to published
  cryptanalysis is made in either direction (RQ-AES-003 R3).
- certificate kind: **none**. Both ranks are pure counting measurements. No
  discrete log, no factor-base relation and no key recovery is claimed or
  attempted, so there is nothing to certify. Stated explicitly per the
  Executor contract.

## inference

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: claude-opus-5
  fallback_used: false
  model_verified: false
  model_verified_reason: >-
    No `python3 -m orchestration.adapter doctor --probe` exists under this
    harness; the model identifier is unverified configuration.
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

## 0. THIS PREREGISTRATION IS NOT BLIND, AND I SAY SO FIRST

The task card states, as the premise of RANK 1, that "nobody has measured r=3
or r=4". **Before writing this document I read files in the repository that
contradict that premise**, and I record that here rather than after the fact,
because a preregistration that hides prior knowledge is worthless.

What I read, with paths:

- `coordination/goals/GOAL-AES-003/batches/BATCH-006/tasks/TASK-20260803-0764fc/runs/A2-R4-K1.json`
  -- `aes`, r=4, amask 1, smask 1, log2N 30, seed 531001, armid 1, i.e.
  **D-AES-K1's exact parameters with only the round count changed**:
  `W_ge1_nontrivial = 1073741824` out of `nontrivial_trials = 1073741824`
  (rate 1.0, `whist = [0,0,0,1073741824,0]`, every trial W=3).
- `.../runs/A1-R4-MAIN.json` -- r=4, seed 431001, 2^31: 2147483648 / 2147483648
  (rate 1.0).
- `.../runs/A5-R4-R1-K1.json` -- r=4, random S-box `rand:20260803001`, seed
  531001, 2^30: rate 1.0.
- `.../runs/A3-R3-MAIN.json` -- r=3, seed 431001, 2^24: 16711503 / 16711503
  (rate 1.0).
- `.../runs/A4-R2-MAIN.json` -- r=2, seed 431001, 2^20: 1048576 / 1048576
  (rate 1.0).
- `coordination/goals/GOAL-AES-003/batches/BATCH-006/tasks/TASK-20260803-0764fc/RESULTS.json`
  `HEADLINE`: "THE RANK-1 FALSIFIER DID NOT FIRE. r=4 read SATURATED ... far
  above r=5's 13.5x", and `HEADLINE_SECOND_LINE` reporting that
  `BATCH-001/tasks/yoyo5/analysis.json` already carried saturated r=3 and r=4
  arms on 2026-08-02.

Consequences for the discipline of this task, all binding on me:

1. **RANK 1 here is a REPLICATION, not a first measurement.** I still run it
   exactly as the card specifies (fresh runs, seed 531001, armid 1, r=4 at
   2^22 and r=3 at 2^20), because an independent re-execution at a different
   exposure is worth having and because the card is binding. But I will not
   report it as the first reading of r=3 or r=4, and I will tabulate the prior
   BATCH-006 readings beside mine.
2. **My RANK-1 expectation is therefore informed, not blind**, and the
   preregistered decision rule below is weaker evidence than it would be if I
   had not read those files. I say so in RESULTS.json too.
3. RANK 2 (RC-10) **is** blind: I have found no k-byte-prefix measurement
   anywhere in this repository, and no instrument in the campaign emits one.

## 1. RANK 1 -- RC-9, the round profile below the peak

### Runs (exactly as specified by the card; pinned binary, unmodified)

Binary: `coordination/goals/GOAL-AES-003/batches/BATCH-005/tasks/TASK-20260803-48a239/yoyo_sbox_v2`,
sha256 pinned at `d30e4d720317706043b263742062273d22fbe054f56a58a8b351f3bbb3fd9ff0`;
verified before use and the check recorded in RESULTS.json.

```
yoyo_sbox_v2 arm R9-R4-K1 aes 4 1 1 22 531001 1 2
yoyo_sbox_v2 arm R9-R3-K1 aes 3 1 1 20 531001 1 2
```

Everything except `rounds` is identical to the existing arm D-AES-K1
(`BATCH-005/tasks/TASK-20260803-48a239/runs/D-AES-K1.json`: aes, r=5, amask 1,
smask 1, 2^30, seed 531001, armid 1, threads 2, W_ge1 = 14). The pairing is the
entire point and I change nothing else.

### Reported statistic

`rate = W_ge1_nontrivial / nontrivial_trials`, and
`excess = W_ge1_nontrivial / null_expectation_analytic` where the analytic null
is the binary's own `nontrivial_trials * 4 * 2^-32`.

### Preregistered expectation (the red team's, restated so a miss is visible)

From `BATCH-005/tasks/TASK-20260803-33f760/red_team_report.yaml`, RC-9
`predicted_if_the_reading_is_right`:

> r=3 saturated or near it, r=4 strictly and substantially above r=5's 13-15x,
> plausibly saturated too.

That is the preregistered expectation of this task. **A miss is a miss and will
be reported as one in the first line of RESULTS.json.**

### Decision rule, fixed before the run

Let `X4` be the excess factor at r=4 and `X5 = 13.5` the campaign's r=5 reading
under these parameters (D-AES-K1: 14 hits against analytic null 1.0 at 2^30;
the campaign's quoted band is 13-15.6x across arms).

- **F1 (FALSIFYING, primary):** `X4 <= X5`, i.e. r=4 reads at or below r=5.
  This includes the special case of r=4 reading at the null. If this happens
  the profile is not monotone below r=5, and I write it as the FIRST LINE of
  RESULTS.json, unsoftened, unburied, and not attributed to the instrument
  unless a control in this same task establishes that the instrument is at
  fault. No such control is planned, so absent one I will simply report it.
- **F1a (escalation, mandatory if triggered):** if the r=4 arm at 2^22 reads at
  or near chance -- operationally, `W_ge1_nontrivial <= 3` at 2^22, where the
  analytic null is `2^22 * 4 * 2^-32 = 0.00390625` -- then I re-run r=4 at
  log2N=28 and report BOTH readings, labelling the 2^22 one as low-powered. A
  null reading at 2^22 reported without the escalation would be a false
  falsification exactly as surely as suppression would be a false confirmation.
- **C1 (CONFIRMING):** `X4 > X5` substantially, with r=3 at or near saturation.
  Under the modeled null this is what "round-limited decay" predicts.
- **C2 (CONFIRMING-WITH-A-WORDING-CORRECTION):** r=4 saturates (rate 1.0). Then
  the profile is monotone decreasing but the word "peak at r=5" is wrong: r=5
  is merely the largest r with a sub-saturated above-null reading. I will say
  so rather than let the queue's wording stand.
- **A1 (AMBIGUOUS):** anything else, including a non-null r=4 reading whose
  exact Poisson interval on the excess straddles `X5`.

I will state in one sentence whether the profile is monotone below the peak,
and I will state it for the profile I actually measure.

### What I will NOT do

I will not interpret hypothesis status, assign evidence strength, or recommend
promotion. Those are Coordinator acts.

## 2. RANK 2 -- RC-10, the null scaling test

### The instrument change and the equivalence obligation

`yoyo_sbox_v3.c` is built from
`BATCH-004/tasks/TASK-20260803-367b1b/src/yoyo_sbox_v2.c` by **adding**
counters for the number of trials in which the difference `d` is zero on the
first `k` bytes of `PW[j]` for some `j`, for k = 1,2,3, alongside the existing
k = 4 count, and by printing them. Nothing else changes: no change to the RNG,
the trial loop, the draw-rejection logic, the trivial-swap exclusion, the
existing counters, or the cipher.

Because k = 4 is exactly the existing `W>=1` condition, the new k=4 counter
**must** equal `W_ge1_nontrivial` in every run. That is an internal consistency
check, not the equivalence proof.

**The equivalence proof, preregistered as load-bearing:** re-run D-AES-K1's
exact parameters (`aes 5 1 1 30 531001 1 2`) on v3 and require it to reproduce
the v2 numbers BIT-EXACTLY -- field by field: `key_hex`, `thread_seeds`,
`trivial_swaps_excluded`, `nontrivial_trials`, `W_ge1_nontrivial`,
`W_ge1_by_word`, `whist`, `sbox_first8`. I ship the unified diff, both
binaries' sha256, and the equivalence run.

- **STOP CONDITION:** if any of those fields differs, I STOP, report that the
  two binaries are not the same instrument, and **withdraw every RC-10 number**
  as uninterpretable. That finding then replaces all of them. I will not
  "explain" a mismatch and proceed.

### Runs

```
yoyo_sbox_v3 arm K-EQUIV-R5-K1 aes 5 1 1 30 531001 1 2     # equivalence proof
yoyo_sbox_v3 arm K-R10-NULL    aes 10 1 1 24 531001 1 2    # null object
yoyo_sbox_v3 arm K-R5-LIVE     aes 5  1 1 24 531001 1 2    # live arm
```

### Preregistered predictions

Under the independence assumption behind the analytic null
`P(W>=1) ~ 4 * 2^-32`, the rate for k constrained bytes is
`p_k = 1 - (1 - 2^-8k)^4`, which is `~ 4 * 2^-8k` for k >= 2. So:

- **Prediction N1 (the decision content at r=10):** each additional constrained
  byte divides the rate by `2^8 = 256`. Formally the successive ratios
  `R_1 = n_1/n_2`, `R_2 = n_2/n_3`, `R_3 = n_3/n_4` should each be consistent
  with 256 (R_1's exact prediction is `p_1/p_2 = 254.02` because the union
  bound is not tight at k=1; I use the exact `p_k` throughout and state both).
- **FALSIFIES N1:** any successive ratio at r=10 whose confidence interval
  excludes the exact-model prediction. That would mean the analytic null is
  wrong and every excess factor in five batches is wrong by the corresponding
  factor.
- **CONFIRMS N1:** all three ratios' intervals cover the model prediction. The
  honest reading is then that the null is confirmed to within the width of
  those intervals, which I will state numerically rather than as a verdict.
- **Power note, fixed in advance:** at 2^24 trials the expected counts under
  the model are ~261,000 (k=1), ~1024 (k=2), ~4.0 (k=3), ~0.0156 (k=4). So
  `R_1` and `R_2` will be well determined, `R_3` will be dominated by Poisson
  noise on a handful of k=3 events, and the k=4 cell will be empty or nearly
  so. **`R_3` is expected to be uninformative at this exposure, and I say so
  now rather than after seeing it.** I will report its interval and let it be
  wide; I will not upgrade it by re-running until it looks good.

- **Prediction M1 (the mechanism question, at r=5):** if the r=5 excess is a
  genuine full-32-bit-word coincidence, the k=1,2,3 rates at r=5 should sit at
  their model values while k=4 sits ~13x high. If instead the excess is already
  present at k=1 or k=2, the four-byte framing is not doing the work and the
  mechanism is byte-local.
  - **Excess-already-at-k=1** is operationally: the r=5 k=1 rate exceeds the
    model `p_1` by more than the exact Poisson interval allows, and/or exceeds
    the measured r=10 k=1 rate by more than its interval allows. The r=10 arm
    is the null object for this comparison and is run at the same exposure and
    seed for exactly that reason.
  - Either outcome is reportable. I have no preference and register none.

### Confidence intervals

All intervals are exact Poisson (Garwood) 95% intervals on counts, propagated
to ratios by the exact conditional-binomial method for a ratio of two Poisson
means at known relative exposure. Computed in a script shipped with the run.
Point estimates alone are not sufficient and I will not report them alone.

## 3. Budget and halting

Declared wall clock 5400 s from 2026-08-03T20:09:55Z; binding stop
2026-08-03T21:39:55Z. Memory cap 8 GB (the instrument allocates well under
1 MB). Maximum runs 30.

**Halting at the stop is full compliance, not failure.** If I halt I will list
what was not reached and what each unreached item would have settled.

Order of execution, fixed now, cheapest-and-most-falsifying first:

1. sha256 verification of the pinned binary (seconds)
2. RANK 1 arms r=4 @ 2^22 and r=3 @ 2^20 (seconds)
3. RANK 1 escalation to 2^28 if and only if F1a triggers (~40 s)
4. v3 source edit, build, diff, sha256 (seconds)
5. v3 equivalence run at 2^30 (~160 s) -- STOP if it does not reproduce
6. RC-10 k-scaling at r=10 and r=5, 2^24 each (~10 s each)
7. statistics with intervals, RESULTS.json, parser check

## 4. Failure taxonomy, fixed in advance

A timeout, crash, OOM, or killed process is an **infrastructure fact**
(`resource_exhaustion` / `infrastructure_error`) and is **never** negative
mathematical evidence. It will be recorded as such and never as a null result.
A v3/v2 mismatch is an `implementation_error` invalidating the RC-10 numbers,
not an observation about the cipher.

## 5. Parser confirmation

This file is prose (Markdown) and carries no machine-parsed payload beyond the
fenced YAML/command blocks, which are illustrative. The structured artifacts of
this task -- `RESULTS.json` and `budget_stamps.jsonl` -- are parsed in full
with `json.load` / line-wise `json.loads` before this task finishes, and each
records that it was.
