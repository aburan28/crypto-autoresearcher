---
id: KN-FIND-ead2ac
type: internal_finding
title: "A precision minimum bisected at one (dimension, beta, seed) instance of an fpylll isolated-LLL-preprocessing step is not evidence it holds at a different instance of the identical cheap sub-step"
tags: [fpylll, fplll, bkz, lll, numerical-stability, gso-row-expo, mpfr, precision-bisection, instrument-design, methodology, calibration-generality, ml-kem, negative-result, toy-scale]
confidence: derivation_via_two_independent_live_executed_counterexamples_across_two_batches_reconciled_by_one_session
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-d1a736, TASK-20260814-9cf080, BATCH-279acb, TASK-20260815-6e4c02, TASK-20260815-85e02a]
internal_refs: [EV-MLKEM-098182, DEC-20260814-8ec2e5, EV-MLKEM-e4189c, DEC-20260815-201633]
sibling_findings_narrowed: []
sibling_findings_note: "Does not narrow KN-FIND-f54a82. That entry's own axis is operation-level (an isolated LLL/GSO-preprocessing-step probe is more numerically permissive than the full BKZ tour, at the SAME instance). This entry's own axis is instance-level (a precision minimum bisected at ONE instance of that same cheap sub-step does not transfer to a DIFFERENT instance of it, even holding the operation fixed). Both findings now coexist as siblings documenting two independent hazards in using a cheap fpylll sub-step probe to calibrate or validate a numerical-stability fix for the full BKZ pipeline. internal_refs carries LEDGER records only, matching KN-FIND-f54a82's own convention."
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe1_bisection_generality.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe1_bisection_generality_results.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/red-team/TASK-20260815-85e02a/probes/probe1_d512_beta_generality.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/red-team/TASK-20260815-85e02a/probes/probe1_d512_beta_generality_results.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/tasks/TASK-20260815-6e4c02/bisection_d512_results.json
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/red_team_report.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/red-team/TASK-20260815-85e02a/red_team_report.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/reviews/TASK-20260815-2f026b/validation_report.yaml
added: '2026-08-15'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on
any FIPS 203 parameter set, on any attack cost, or on any cost model. Measured
only against `IntegerMatrix.random(d, "qary", k=d//2, q=3329)`, `fpylll` 0.6.4,
one host.

**THIS ENTRY DOES NOT CLAIM the isolated-step precision, once properly
calibrated per-instance, is sufficient for the full BKZ tour.** The separate,
already-promoted `KN-FIND-f54a82` shows it frequently is not — now confirmed a
fourth time in the same batch this entry's own second recurrence comes from, at
`(d=512, beta=40)` itself. This entry is about calibration-instance generality,
not about the isolated-step-vs-full-tour gap.

The finding, in one sentence:

> In `fpylll` (>= 0.6.4), a minimum mpfr precision determined by bisection at
> ONE `(d, beta, seed)` instance of the isolated LLL/GSO-preprocessing step
> (`GSO.Mat(...)` -> `LLL.Reduction(...)` -> `lll_obj()`, the identical
> sub-step `KN-FIND-f54a82` already names) is measurably, non-trivially
> inadequate at a DIFFERENT instance of the SAME cheap sub-step — confirmed
> independently, by live execution with bit-identical seeds, across **two
> structurally different axes of instance variation**: across dimension, and,
> now, within a fixed dimension across `beta`.

## 1. What was measured, and how the pattern was found

**First recurrence — across dimension (`BATCH-d1a736`).** `TASK-20260814-534f80`
bisected a minimum isolated-LLL-step mpfr precision at `(d=256, beta=40)` — 65
bits — then applied it unchanged to all 6 of PREREG-8's own Stage-0 main-grid
cells, including three at `d=512`. The independent Red Team
(`TASK-20260814-9cf080`) ran a live, seed-identical control
(`probe1_bisection_generality.py`) at `(d=512, beta=40)`: 65 bits — `ERROR`
(`ReductionError: infinite loop in babai`); 100 bits — `COMPLETED`. Confirmed
by direct source inspection to be the exact same fpylll operation every
`d=512` main-grid cell's own full-tour traceback already failed on.

**Second recurrence — within a fixed dimension, across `beta` (`BATCH-279acb`).**
The commissioned follow-up (`TASK-20260815-6e4c02`) ran a genuine,
1-bit-resolution bisection at `(d=512, beta=40)` specifically — determining 69
bits, a real minimum, not a fallback — then applied THAT value unchanged to
the other two `d=512` main-grid cells, `beta in {55, 70}`. The independent Red
Team (`TASK-20260815-85e02a`) ran the identical isolated-step harness, live, at
both other bases, with seeds independently re-derived from the shared
`default_rng([SEED_ROOT, 0, d, beta, 0, 0])` formula and confirmed
bit-identical to the producer's own reported values: at BOTH `(d=512, beta=55)`
and `(d=512, beta=70)`, 69 bits — `ERROR`; 100 bits — `COMPLETED`. Again
confirmed, by direct inspection of the same `bkz.py` source, to be the exact
operation both cells' own full-tour reattempts already failed on.

Both counterexamples are **executed, not argued**: a minimal, single-parameter
mutation of the producer's own construction (`d: 256 -> 512` in the first case;
`beta: 40 -> 55`, and separately `40 -> 70`, in the second), all else — seed
formula, `ROW_EXPO`-free mpfr construction — held fixed, converts a reported
`COMPLETED` outcome at the borrowed precision into `ERROR`, on a live,
bit-identical-seed execution against the same `fpylll` 0.6.4 build each time.

## 2. Why this recurrence, not the single instance, is the finding

A single reconciled falsification could be read as an anecdote about one
particular dimension jump. **This recurred twice, on two structurally
different axes of instance variation, each time via a live, executed,
bit-identical-seed control, not a restatement of the same measurement:** the
first is across-dimension (`d=256`-calibrated fails at `d=512`); the second is
within-dimension-across-`beta` (`(d=512,beta=40)`-calibrated fails at
`(d=512,beta=55)` and `(d=512,beta=70)`, holding `d` fixed). That the identical
mechanism — a bisected minimum is a property of the one instance it was
determined at, not of any broader class the instance belongs to — explains both
recurrences is what elevates this from two isolated corrections to a
**generalizable methodological lesson**: a cheap, single-instance precision
bisection is not, by itself, evidence about ANY other instance of the identical
sub-step — not across dimension, and not even across a cheaper-to-vary
parameter like `beta` at fixed dimension. A calibration campaign that reuses
one instance's bisected minimum across a multi-cell sweep, without separately
verifying each cell, risks under-provisioning some cells while correctly
provisioning others, with no way to tell which from the bisection alone.

## 3. What this changes, and what it does not

**It changes no measured figure and not the fired termination branch.**
`T-PROJNOISE-NODATA` firing for both batches' own reported 0/N outcomes is
confirmed correct by every review in both batches and by this reconciliation.

**It changes what a "properly calibrated" claim is entitled to say.** A
follow-up that bisects at one instance and reports a multi-cell sweep's own 0/N
outcome as "0/N at a properly, dimension- or construction-appropriate
precision" is not entitled to that framing unless every tested cell was
individually calibrated. `BATCH-279acb`'s own headline ("d=512's own minimum
adequate precision") is the second instance of exactly this overclaim, caught
before it propagated into a Coordinator decision unchallenged.

**It does not establish that any specific cell would clear a full tour at its
own correct precision.** Both `(d=512, beta=55)` and `(d=512, beta=70)` remain
genuinely untested, at any level, at a precision actually adequate for their
own basis (bracketed only to `(69, 100]` by the second recurrence's own
control) — and per `KN-FIND-f54a82`'s own pattern, now confirmed a fourth time
at `(d=512, beta=40)` itself in the same batch, even a correctly-calibrated
isolated-step precision is not guaranteed to clear the full tour either. See
§4.

## 4. What remains open

1. **Whether `(d=512, beta=55)` or `(d=512, beta=70)` can clear a full BKZ
   tour at their OWN properly-bisected precision is completely unmeasured.**
   Their true minimum lies somewhere in `(69, 100]`; no session has bisected
   either individually or reattempted a full tour at the result.
2. **The underlying C++/mpfr mechanism producing basis-specific (not merely
   dimension-specific) precision requirements is not identified**, in either
   source batch. No `fplll` C++ source was inspected directly in either case;
   no upstream issue-tracker search was performed.
3. **The real cost of properly calibrating a multi-cell sweep this way is
   understated by both source batches' own forward-looking budgets.** The
   second recurrence's own Red Team review (`TASK-20260815-85e02a`, OBJ-3)
   found the true cost of individually calibrating all three `d=512`
   main-grid cells is at least 3 bisections + 3 reattempts, not the 1
   bisection + 3 reattempts either batch's own `budget_justification` assumed.
4. **Whether this generalizes beyond this one lattice family**
   (`IntegerMatrix.random(d,"qary",k=d//2,q=3329)`), this one `fpylll` version,
   or beyond the `beta`/dimension axes actually tested (e.g. across seeds at a
   fixed `(d, beta)`, which neither recurrence varied) **is untested.**

## 5. What a successor must do, and what it must not

1. **Before applying a bisected precision minimum to more than the one
   instance it was determined at, either bisect each instance separately, or
   explicitly disclose the reuse as an untested assumption** — never present a
   multi-cell sweep's own outcome as "at a properly calibrated precision" when
   only one cell was actually calibrated.
2. **This is not a claim that single-instance bisection is useless** — it
   correctly, cheaply determines that ONE instance's own minimum, as both
   recurrences' own producers did correctly. It is a claim that the result
   must not be silently extrapolated to other instances of the same class
   without testing them.
3. **Cost planning for a multi-cell calibration sweep must budget one
   bisection per cell**, not one bisection amortized across a sweep, per §4.3
   above.
4. A follow-up individually bisecting and reattempting `(d=512, beta=55)` and
   `(d=512, beta=70)` at their own precision is named in `DEC-20260815-201633`'s
   own `next_actions`; this entry does not perform or wait on that measurement.

## 6. Scope and limits — read before citing

1. **THE RAW OBSERVATIONS WERE INDEPENDENTLY, LIVE EXECUTED.** Both
   recurrences' own controls (`probe1_bisection_generality.py`,
   `probe1_d512_beta_generality.py`) were built and run by independent Red
   Team sessions, in separate batches, each blind to the concurrently-running
   Validator's own write scope.
2. **THE RECONCILIATION AND THIS PROMOTION DECISION WERE NOT.** Both are this
   goal's own Coordinator's act (a single continuing role across batches, not
   a fourth independent reviewer) — disclosed here, not smoothed over.
3. **THE SECOND RECURRENCE WAS A DIRECTED CONFIRMATION EXPERIMENT, NOT AN
   INDEPENDENTLY-ARISING DISCOVERY IN THE SENSE `KN-FIND-f54a82`'S OWN
   TWO-RECURRENCE BAR HISTORICALLY REQUIRED.** `KN-FIND-f54a82`'s own bar
   required each recurrence to arise from an investigation not designed around
   the other's own question. `BATCH-279acb`'s own Red Team task was explicitly
   commissioned, by its own completion_gate, to test exactly the question this
   entry's second recurrence answers ("does the (d=512,beta=40)-bisected
   precision actually hold at (d=512,beta=55) and (d=512,beta=70)?"). This is
   a genuinely weaker form of independence than `KN-FIND-f54a82`'s own
   precedent, and this entry is promoted anyway, ONLY because
   `DEC-20260814-8ec2e5`'s own `next_actions` text pre-committed this exact
   operational criterion for this exact follow-up ("if that follow-up
   confirms the pattern at additional (d, beta) pairs ... promotion should be
   revisited then") — a more specific, more recently-stated standard than the
   older precedent, and one this goal's Coordinator chose not to renege on
   absent a new reason to. A future reader relying on this entry's own
   "two independent recurrences" framing should read that phrase as "two
   recurrences, one of them directed," not as two accidental discoveries.
4. **INDEPENDENCE IS PROCEDURAL — NEVER MODEL-LEVEL.** AGENTS.md rule 12 is
   UNMET AND UNWAIVED. Every producer, reviewer, and the reconciling
   Coordinator across both source batches ran on the same model and the same
   host.
5. **THIS ENTRY MAKES NO CLAIM ABOUT WHETHER A PROPERLY-CALIBRATED PRECISION
   WOULD LET ANY UNTESTED CELL CLEAR A FULL TOUR.** See §4.1. That is a
   separate, still-open question, further complicated by `KN-FIND-f54a82`'s
   own sibling finding that even correct calibration is no guarantee.
6. **DERIVATIONS AND LIVE CODE EXECUTION, NOT THEOREMS.** Every claim in this
   entry traces to a specific script's recorded output at a specific
   `(d, beta, precision, seed)` instance, not a general proof about
   `fplll`'s own numerical behavior.
7. **IT ESTABLISHES NOTHING ABOUT ANY LATTICE, ML-KEM PARAMETER SET, OR C1/C2
   CANDIDATE.** Neither source batch adjudicates any such proposition, and
   neither does this entry. `T-PROJNOISE-NODATA`'s own FORBIDS clause is
   honoured throughout.

## Identifier provenance

`KN-FIND-ead2ac` was drawn as a random 6-hex token (matching this corpus's own
established `KN-FIND-<tok>` pattern; `tools/allocate_id.py` registers no
`--next` type for `KN-*` records, so no scan-free minting path exists for this
record class) and then confirmed in **two scopes** by the orchestrating
session at the Coordinator's request (`DEC-20260815-201633`'s own
`knowledge_promotion.promoted_note`): worktree `tools/allocate_id.py --check
KN-FIND-ead2ac` (well-formedness not enforced for `KN-*`, 0 occurrences across
6,965 identifier-bearing paths) **and** a cross-ref sweep of the 25
most-recently-updated remote branches (0 hits), matching the identical
two-scope discipline `KN-FIND-f54a82`'s own "Identifier provenance" section
documents. The Coordinator that specified this entry's content held no shell
and claimed neither check as its own; both were performed by the orchestrating
session.

## Superseding relationship

This entry does not narrow `KN-FIND-f54a82` or any other prior finding in this
goal. **No prior entry is edited and no `superseded_by` is set** on any of
them. It stands as a sibling instrument-design/methodology lesson, on a
distinct axis (calibration-instance generality, not operation-level
permissiveness), cross-referenced from `DEC-20260815-201633`'s own
`knowledge_promotion` field.
