# Adjudication: reconciling TASK-20260814-a94ddf (Validator) vs TASK-20260814-fe02ff (Red Team) on the mpfr-precision fix

Performed by the orchestrating session, directly, using the same `fpylll`
0.6.4 install both reviews used (same execution image), because the two
independent reviews reached apparently contradictory conclusions on the
task's own central question and this had to be resolved with evidence
before any ledger archive could be written -- not by picking a side.

## The apparent contradiction

- **Red Team (`fe02ff`), probe5**: constructs `GSO.Mat(A, float_type="mpfr")`
  with **no** `flags=GSO.ROW_EXPO` (their own comment: "documented
  incompatible w/ mpfr"), calls the isolated `lll_obj()` step directly.
  Result: **succeeds in 0.004s** on the exact (d=256, beta=40,
  seed=1398073216) instance the producer reports failing.
- **Validator (`a94ddf`), `probe_root_cause_precision2.py`**: constructs
  `GSO.Mat(A, flags=GSO.ROW_EXPO, float_type="mpfr")` **with** `ROW_EXPO`,
  wraps it in `BKZReduction(L)`, calls the full `bkz(par, tracer=True)`.
  Result: **fails identically** (`ReductionError: 'infinite loop in babai'`)
  at 212 bits AND 424 bits.

Read at face value these looked like a direct factual conflict about
whether "explicit mpfr precision fixes the failure."

## Direct adjudication (this session, same host/commit, three tests)

1. **Isolated LLL step, with vs. without `ROW_EXPO`** (`adjudicate_precision.py`,
   `adjudicate_precision.stdout.log`): **both succeed**, in ~0.004s each.
   `ROW_EXPO` alone does **not** explain the discrepancy for the isolated
   LLL step.
2. **`BKZReduction(L).lll_obj()` (the exact call `BKZReduction.__call__`
   makes at `bkz.py:123`), with vs. without `ROW_EXPO`**
   (`adjudicate_wrapping.py`, `adjudicate_wrapping.stdout.log`): **both
   succeed**, in ~0.004s each. Wrapping in `BKZReduction` does not by
   itself reintroduce the failure at the LLL-preprocessing step either.
3. **The full `bkz(par, tracer=True)` tour call — the actual call each
   review's own construction was ultimately trying to characterize**
   (`adjudicate_full_tour.py`, run separately for each `ROW_EXPO` setting,
   100s bound):
   - `ROW_EXPO=True` (Validator's exact construction):
     **fails in 0.282s** with the identical `ReductionError('infinite loop
     in babai')` -- reproduces the Validator's own finding exactly
     (`adjudicate_full_tour_row_expo_true.log`).
   - `ROW_EXPO=False` (Red Team's construction, extended from their own
     isolated-LLL-step probe5 to the full tour): **does not fail within
     100s** -- times out without completing or erroring, consistent with
     Red Team's own probe6 observation (~684s of steady CPU before their
     manual termination) (`adjudicate_full_tour_row_expo_false.log`).

## Resolution

**Both reviews are correct about the exact construction each one tested.**
They are not in factual conflict; they characterized two different code
paths that diverge only at the full-BKZ-tour level (not at LLL
preprocessing, where both constructions succeed identically):

- `GSO.ROW_EXPO` + mpfr: the tour re-triggers the identical
  `'infinite loop in babai'` failure almost immediately (0.28s) -- mpfr
  precision alone does not fix this construction. This is exactly what the
  Validator tested and reported, correctly.
- mpfr **without** `ROW_EXPO`: the tour does not hit that immediate
  failure, but also does not complete in a bounded, practical time (>100s
  here, >684s in Red Team's own independent test) -- consistent with, not
  contradicting, Red Team's own explicit finding that the corrected
  construction's real per-cell cost is "far from free" and unmeasured to
  completion by either review.

Neither review overstated its own finding. The producer's own root-cause
characterization ("a genuine incompatibility... not resolved by the one
[precision] setting that could be tested") is **partially corrected** by
this reconciled picture: the isolated LLL-preprocessing failure genuinely
is precision-fixable (Red Team correct), but a full BKZ tour under the
`ROW_EXPO` construction the producer's own `stage0_feasibility.py` actually
uses (see `run_manifest.yaml` / `stage0_feasibility.py` source: `GSO.Mat(A,
flags=GSO.ROW_EXPO)` is exactly what `BKZReduction.__init__` builds
internally from a raw `IntegerMatrix`) is **not** fixed by precision alone
(Validator correct for that specific, actually-relevant construction) --
and even the construction that avoids the immediate error has an unmeasured,
apparently-large real cost (both reviews agree on this once reconciled).

## What this means for the decision this task's own follow-up must state

- `T-PROJNOISE-NODATA` firing for TASK-20260814-ffd791's own reported
  observation (the `ROW_EXPO`-based default construction, exactly as run)
  is confirmed correct by both reviews AND this adjudication.
- The producer's own follow-up recommendation ("investigate an upstream
  fplll bug / alternate build") is **not** the cheapest next step: dropping
  `ROW_EXPO` avoids the immediate exception, a genuine, concrete,
  already-available fix within ordinary `fpylll` usage.
- But that fix's own real per-cell cost is **not yet measured to
  completion by anyone** (producer, Validator, Red Team, or this
  adjudication) -- every attempt at the full corrected-construction tour
  has been terminated by a time bound before finishing, at both d=224 and
  d=256. The preliminary evidence (>100s-684s and counting, vs. the
  double-precision failure's own 70.2s-to-error) is consistent with a
  materially larger real cost than PREREG-8 section 6.2's own
  double-precision estimate assumed.
- Therefore: Stage 1 should **not** be dispatched as currently written, and
  a follow-up task should re-run Stage 0 (or a scoped subset of it) with
  the `ROW_EXPO`-dropped, explicit-mpfr-precision construction, under a
  realistically sized cap (not the original 3600s cap, which no attempt at
  this construction has yet cleared), to obtain a real, completed
  measurement before any Stage-1 sizing decision.

## Second reconciliation: the dimension-boundary discrepancy

Independently found by the coordinator subagent drafting the ledger archive
(not by this adjudication's own first pass): the two reviews' own dimension
sweeps report **different boundaries** --

- **Red Team** (`probe4_dimension_scan.py`): "d=192 succeeds... d=224 fails."
- **Validator** (`probe_dimension_sweep.py` / `probe_dimension_single.py`):
  "d<=184 completes... d>=192 fails."

These are not in conflict once the two probes' own code is compared: **they
measure different operations, exactly as in the first reconciliation above.**

- Red Team's `probe4_dimension_scan.py` runs **only the isolated LLL step**
  (`GSO.Mat(A, flags=GSO.ROW_EXPO)` -> `LLL.Reduction(...)` -> `lll_obj()`),
  no `BKZ.Param`, no actual block-reduction tour attempted at all -- the same
  isolated-step methodology as their own probe3/probe5.
- Validator's `probe_dimension_sweep.py` / `probe_dimension_single.py` runs
  the **full native BKZ tour** (`BKZ.reduction(A, par)`, a real
  `BKZ.Param(block_size=10, ...)` block-enumeration attempt), at `beta=10`.

**Direct adjudication at d=192, the exact disputed point**
(`adjudicate_d192.py`, `adjudicate_d192.stdout.log`), using each review's own
exact construction:

- Red Team's construction (isolated LLL step, d=192): **COMPLETES in
  0.0061s** -- reproduces Red Team's own finding exactly.
- Validator's construction (full native BKZ tour, d=192, beta=10):
  **FAILS** (`RuntimeError: Aborted`, the same underlying "infinite loop in
  babai" condition surfacing as an uncaught C++ abort per the Validator's
  own ART-5 finding) after 6.65s -- reproduces the Validator's own finding
  exactly.

**Resolution:** both reviews are again correct about the exact operation
each one measured. The isolated LLL-preprocessing step remains solvable at
dimensions well beyond where a full BKZ tour (which performs substantially
more numerically-sensitive work -- block enumeration, repeated internal
basis updates) already fails. There are, properly stated, **two distinct
boundaries**, not one contested boundary: an isolated-LLL-step boundary
(Red Team's own d=192 works / d=224 fails) and a full-tour boundary
(Validator's own d<=184 works / d>=192 fails, independently reconfirmed
here). Neither review overstated its own finding; neither needs correction.
This closes the second discrepancy the coordinator's own ledger-archive
drafting session flagged as unreconciled.

## Command log

All four adjudication scripts and their full recorded stdout/stderr live
alongside this file (`adjudicate_precision.py`, `adjudicate_wrapping.py`,
`adjudicate_full_tour.py` with two per-`ROW_EXPO`-setting logs, and
`adjudicate_d192.py`). Same seed formula (`SEED_ROOT=715923`,
`default_rng([SEED_ROOT, 0, d, beta, arm_index, 0])`) as every other
artifact in this batch; `seed_used=1398073216` at (d=256, beta=40) and
`seed_used=1781019131` at (d=192, beta=40, Red Team's arm_index=0) /
matching Red Team's own reported values reproduced identically across all
scripts run for this adjudication.
