# TASK-20260806-b51ac8 report

B2-A: repaired sensitivity demonstration and missing arms for the
projected-error tail statistic. GOAL-MLKEM-005, BATCH-5a4656.

**Rule 12 status.** AGENTS.md rule 12 is UNMET and UNWAIVED, inherited from
GOAL-MLKEM-003/004 and from BATCH-a51f91. No status change to any
`EV-MLKEM-*` record or `KN-*` entry is made or proposed by this report. No
ML-KEM break claim. The mechanism under study is SESSION recovery, not key
recovery; no number below is subtracted from the in-repo `primal_bdd` margins
of 2.80/6.04/1.28 bits. Everything below is `toy` scale (d <= 140, beta <=
40) and none of it is transported to beta = 606, d = 1420.

**This report is an executor's own reading, not an official adjudication.**
Whether C3's discharge criterion is met is the Coordinator's decision, made
after independent Validator and Red Team review of this package. Where this
report states "the instrument reads as sensitive" or similar, that is an
observation about this run's own gates, not a program-level verdict.

## 0. What changed from BATCH-a51f91, and why

BATCH-a51f91's sensitivity demonstration manipulated the *error law*
(anisotropic CBD) while holding the projector Haar. Re-derived independently
in `prediction_frozen.json` (`the_repair.why_the_prior_demonstration_failed_restated_here_for_the_record`):
for a Haar-random rank-beta projector `P` and any fixed nonzero vector `v`,
`||Pv||^2/||v||^2` depends on `v` only through its *direction*, and the Haar
measure is invariant under the orthogonal group, so this ratio's law is
identical for every direction of `v` -- including every anisotropic-error
draw at fixed norm the prior demonstration varied. No error-law manipulation
under a Haar projector can move the statistic to leading order, regardless of
how extreme. This is the same conclusion BATCH-a51f91's own report drew (as a
finding, not a repair) and that RT-20260806-d008e0 OBJ-3 and
VAL-20260806-bb0559 DEF-1 independently confirmed.

**The fix manipulates the projector's law instead.** A graded family
`Q_t = QR(sqrt(1-t) E_S + sqrt(t) G)`, `t` in `{0, 0.05, 0.10, 0.25, 0.50,
0.75, 1.00}`, interpolates between a coordinate-aligned projector (`t=0`) and
a Haar-random one (`t=1`, identical in construction to the pre-existing
`haar_null` arm, which is reused as the `t=1.00` point rather than redrawn).
Full derivation of the family's validity (rank, sign convention, why `t=0`
and `t=1` reproduce their named limits exactly) is in
`prediction_frozen.json` `the_repair.validity_of_the_family_re_derived_here`,
derived independently of RT-20260806-d008e0's own construction -- no number
in this report or in `prediction_frozen.json` is copied from that
re-derivation; it is cited only as the reason this design was chosen.

Three arms are added: the unreduced q-ary tail GSO, the LLL-only tail GSO
(both from the SAME 8 bases per cell as the real arm, at earlier reduction
stages), and a Gaussian-error null of the null (P4).

The threshold is restated in units of the SE of the difference of the t=0
and Haar arm means (P3), declared **unpaired** in advance, with the
derivation and the reason (independent projector-seed families; no shared
random source between the two arms' between-draw variability) given in
`prediction_frozen.json` `the_repair.threshold_fix`. The paired formula and
the empirical covariance are computed and reported alongside as a diagnostic,
never as the gate.

The falsifier (P5) -- the coordinate-alignment departure should decay as
`sd(R)/E(R) ~ sqrt(2*(1-beta/d)/beta)` -- is re-derived and its numeric
predictions frozen in `prediction_frozen.json`
`the_falsifier_P5_numeric_predictions_frozen_before_measuring`, with the
Edgeworth-expansion argument for why this is the expected order of magnitude
of a kurtosis-driven departure (not merely an assertion): the Cornish-Fisher
correction to a quantile of a sum of `n` iid non-Gaussian terms is `O(n^-1/2)`,
the same order as the sum's own CLT-scale relative spread.

## 1. Freeze discipline

`prediction_frozen.json` sha256 `a88e4224001a1e3195c7e2f757d13587bf92e768950bf44db8f83cc01b2a3222`,
frozen at `2026-09-08T01:03:35Z`, git commit `5df288f1723f...` (12 chars
shown as in the file). `measure.py` checks this hash before computing any
research number and aborts on mismatch (it did not abort; see `stdout.log`
lines 1-13, printed before stage A). The first research number (stage A's
first basis reduction) is timestamped after the freeze-block print, per
`stdout.log`.

No number in `prediction_frozen.json` is copied from
RT-20260806-d008e0's own re-derivation. Every closed-form number there is
either unchanged from BATCH-a51f91 (the Beta law, `E[R]=beta/d`, the cell
grid) or a fresh evaluation, shown with its formula, of the falsifier and the
graded-family construction.

## 2. P4 -- the Gaussian-error null of the null, adjudicated FIRST

Per the completion gate, P4 is read before P3, P5, or the real arm.

| cell | ratio_2em10 mean | |dev from 1| | 8-draw sd of mean | 95% CI half-width | PASS |
|---|---|---|---|---|---|
| d100_b30 | 0.998833 | 0.00117 | 0.000415 | 0.000813 | **True** |
| d100_b40 | 0.999917 | 0.00008 | 0.000785 | 0.001539 | **True** |
| d140_b30 | 0.998421 | 0.00158 | 0.001141 | 0.002236 | **True** |
| d140_b40 | 1.000208 | 0.00021 | 0.000823 | 0.001614 | **True** |

All four cells: **P4 PASSES**. The coordinate-aligned projector applied to a
matched-variance Gaussian error returns ratio_2em10 within its own 8-draw
sampling spread of 1.000, in every cell, as required for the Gaussian
rotation-invariance argument to hold. This is the STOP gate; since it holds
everywhere, the run proceeds to P3, P5, and the real arm's P1/P2 in every
cell. Had it failed in any cell, this report would stop there for that cell
and record an instrument defect (branches in `prediction_frozen.json`).

`verify.py` V5 recomputes this pass/fail decision independently from the
recorded means/sds and agrees in all four cells (`verification.json`).

## 3. P3 -- the repaired sensitivity demonstration

Gate: t=0 (coordinate-aligned) mean(ratio_2em10) must clear the Haar (t=1)
mean(ratio_2em10) by >= 4 * SE (unpaired, declared in advance).

| cell | t0 mean | haar mean | shift | SE (unpaired) | shift/SE | 4*SE | MET |
|---|---|---|---|---|---|---|---|
| d100_b30 | 1.097173 | 0.998649 | 0.098524 | 0.002107 | 46.77 | 0.008426 | **True** |
| d100_b40 | 1.086154 | 0.998981 | 0.087172 | 0.001272 | 68.53 | 0.005088 | **True** |
| d140_b30 | 1.092502 | 1.000761 | 0.091741 | 0.001605 | 57.16 | 0.006420 | **True** |
| d140_b40 | 1.083692 | 0.999842 | 0.083851 | 0.001430 | 58.66 | 0.005718 | **True** |

All four cells: **P3 PASSES**, by margins of 46.8-68.5 SE against a 4-SE
gate -- an order of magnitude beyond the threshold in every cell. The paired
diagnostic (empirical covariance between the t0 and Haar arms' 8 paired-by-
index draws) is small and of inconsistent sign across cells
(`-2.83e-6, +2.64e-6, +6.66e-7, -9.98e-7`), consistent with the pre-declared
expectation that the two projector-seed families carry no shared random
source; using the paired SE instead would not have changed any verdict
(`results.json` per-cell `se_paired_diagnostic_only`).

`verify.py` V5 recomputes the SE and the MET decision independently from the
recorded per-arm means/sds and agrees in all four cells.

## 4. P5 -- the pre-registered falsifier

Prediction, frozen before measuring: the coordinate-alignment departure
(t0-vs-Haar shift in ratio_2em10) at beta=40 should be smaller than at
beta=30 (same d) by a factor of ~1.25 (d=100) / ~1.21 (d=140), from
`sd(R)/E(R) = sqrt(2*(d-beta)/(beta*(d+2)))` evaluated at each (d,beta).

| d | departure(beta=30) | departure(beta=40) | measured ratio | predicted ratio | decays as predicted (order of magnitude) | flat/inverted artifact tell |
|---|---|---|---|---|---|---|
| 100 | 0.098524 | 0.087172 | 1.130 | 1.247 | **True** | False |
| 140 | 0.091741 | 0.083851 | 1.094 | 1.211 | **True** | False |

The departure **decays** as beta grows at both d, in the predicted
direction, at both d values. The measured decay (1.09-1.13x) is smaller
than the predicted decay (1.21-1.25x) -- i.e. the departure decays somewhat
*less* steeply than the leading-order Edgeworth/kurtosis argument predicts --
but it is not flat and not inverted, which is the artifact tell this report
is obligated to name if observed. Two beta values at two d values is a
narrow scan (four points, not a curve); this report does not attempt to
determine whether the shortfall from the predicted rate reflects a
subleading correction, a small-beta finite-size effect, or something else.
That question is not attempted by this task and is named here as an
open item rather than resolved.

`verify.py` V3 recomputes both the predicted-ratio and measured-ratio
arithmetic independently from `(d, beta)` and the recorded departures, and
agrees to machine precision.

## 5. Adjudication of the branches (this report's own reading)

Per `prediction_frozen.json` `branches`: P4 holds and P3 holds in all four
cells; P5 is directionally consistent (decaying, not flat, not inverted) in
both available d values, though at a shallower rate than the leading-order
prediction.

**This report's own reading** (not an official verdict): the branch that
best fits all four cells is *"P4 holds, P3 holds, P5 is consistent"* ->
"the repaired instrument is sensitive and the decay is as predicted;
proceed to read the real arm's P1/P2 result as interpretable." The
qualification is that "as predicted" is approximate (same order of
magnitude, not a tight numerical match), which this report states plainly
rather than rounding to a clean pass. Whether this qualified consistency is
sufficient to discharge C3, or whether the shortfall from the predicted
decay rate warrants treating P5 as only partially consistent, is left to the
Validator, Red Team and Coordinator -- this is exactly the kind of borderline
call rule 12 and this program's authority structure reserve for them, not
for the executor.

## 6. The real arm's P1/P2, read conditionally on section 5

With the above qualification, the real arm's P1/P2 readings are:

| cell | ratio_2em10 (real) | dev | pass (<=0.05) | ratio_2em16 (real) | dev | pass (<=0.10) | P1 pass | between-fraction | P2 pass (<=0.20) |
|---|---|---|---|---|---|---|---|---|---|
| d100_b30 | 0.998295 | 0.0017 | True | 1.009472 | 0.0095 | True | **True** | 6.89e-07 | **True** |
| d100_b40 | 1.000538 | 0.0005 | True | 0.999501 | 0.0005 | True | **True** | 7.44e-07 | **True** |
| d140_b30 | 0.999538 | 0.0005 | True | 0.995920 | 0.0041 | True | **True** | 5.56e-07 | **True** |
| d140_b40 | 1.000998 | 0.0010 | True | 1.001045 | 0.0010 | True | **True** | 4.96e-07 | **True** |

These are IDENTICAL to BATCH-a51f91's real-arm P1/P2 numbers (same bases
regenerated from the same seeds; confirmed bit-consistent with
BATCH-a51f91's `receipt.json headline_numbers`, e.g. d100_b30
`b_ratio_2em10_real_pooled 0.9982948470962174` there vs `0.998294847...`
here). **This is expected and is not a new finding**: the real arm was not
re-measured with a different statistic, only the surrounding instrument
(sensitivity demonstration, threshold, added arms) changed. The between-
fraction figures also carry BATCH-a51f91's own caveat: `verdict_on_the_null_arm_FIRST`
shows the identical P1/P2 pass on the Haar null arm in every cell (recorded
in `results.json`), so -- per KN-TECH-1a5b7e mode 4 -- these P1/P2 passes
remain, as BATCH-a51f91 already established, **not admissible as validation
of anything on their own**: `E[R]=beta/d` is FORCED and `Var(R)` under Beta
is DERIVED, not fitted, for every projector arm including the null. What
this task's repair changes is only whether the *sensitivity demonstration
surrounding these numbers* is now capable of detecting a departure at all --
sections 2-5 above answer that question; they do not retroactively make the
P1/P2 agreement itself more informative than BATCH-a51f91 already found it
to be.

## 7. Additional arms: unreduced q-ary and LLL-only tail GSO

Recorded in `results.json` (`verdict_on_unreduced_qary_arm`,
`verdict_on_lll_only_arm`) for all four cells, using the SAME 8 bases as the
real arm at earlier reduction stages, same 2^20 CBD errors, same statistic.
Both pass the P1/P2 gate in every cell as well (same forced/derived caveat
as section 6 applies). No interpretation beyond "recorded" is offered here;
these arms were required by the handoff as controls for the reduction
pipeline, not read as an independent finding by this report.

## 8. Deviations, anomalies, and infrastructure notes

- **D1 (infrastructure, not a research finding).** This session's
  environment had no system-wide `scipy`, unlike BATCH-a51f91's session
  (which reported `scipy 1.17.1` pre-installed). `scipy 1.16.3` was
  additionally installed via the same wheels-only, task-local `--target`
  route (`pip download --only-binary=:all:` then `pip install --no-index
  --find-links ... --no-deps`), recorded in `environment.json`. This did
  not require any protocol change and did not fail; recorded per rule 5
  discipline for completeness, not as an infrastructure failure (there was
  none).
- **D2.** The `fpylll`/`cysignals` wheel sha256 values are IDENTICAL to
  BATCH-a51f91's `receipt.json`, confirming the identical instrument
  (KN-TECH-14efa5's route). `BKZ.DEFAULT_STRATEGY` is unusable in this
  wheel for the same reason BATCH-a51f91 recorded (path absent); the same
  pruning-free in-process strategies fix is used, unchanged.
- **D3.** The 8 BKZ-reduced bases per cell were **regenerated**, not
  reloaded from BATCH-a51f91's cache (that cache lived in a different
  session's scratch directory, unavailable here). Regeneration from the
  identical seed formula reproduced BATCH-a51f91's real-arm P1/P2 numbers to
  the digits shown in section 6, which is itself an independent confirmation
  that the regenerated bases match the originals bit-for-bit in effect.
- **D4.** Git HEAD advanced (`5df288f1...` at freeze time to `1da9b43d...`
  at run completion) via other agents' concurrent commits to this shared
  branch during the course of this task (see `environment.json`
  `git_dirty_note`). This task made no commits and touched no path outside
  its declared `write_scope`.
- **A1 (anomaly, recorded not discarded).** P5's measured decay ratios
  (1.09-1.13x) are smaller than the predicted ratios (1.21-1.25x) at both d
  values, consistently in the same direction (measured < predicted). Two d
  values is not enough to tell whether this is a systematic subleading
  correction or sampling noise at n=8 draws per t; not resolved by this
  task.
- No protocol deviation required an amendment request. `prediction_frozen.json`
  was never edited after freezing (unlike BATCH-a51f91's D1, which found and
  reported an arithmetic error in a pre-tabulated list; no analogous defect
  was found in this file, and none of its formulas needed correction after
  the run).

## 9. Independent recomputation (verify.py)

Five independent checks (`verify.py`, `verification.json`), all **PASS**:

- V1: forced `E[R]=beta/d` matches for every cell.
- V2: Beta-law quantiles recomputed by bisection on `betainc` (not
  `betaincinv`) agree to <3e-14 relative error.
- V3: the falsifier's predicted-departure-scale and P5's ratio arithmetic
  recomputed independently from `(d, beta)` alone, agreeing to machine
  precision.
- V4: a full independent recompute of cell d100_b30's real, haar_null,
  graded-t0, and gaussian_null arms from seeds alone, using a classical
  Gram-Schmidt recurrence (not the QR-of-transpose trick) for the real arm
  and an independently-coded CBD sampler (different bit-consumption pattern
  from the same seed, so not a bit-identical draw, but the same
  distribution and sample size) -- agrees to within 0.2% on every arm
  (tolerance declared at 0.5% in advance of running V4).
- V5: the P3/P4 gate arithmetic (SE, MET, PASS) recomputed independently
  from the recorded per-draw statistics, agreeing in all four cells.

## 10. Completion gate

- Frozen prediction, including the falsifier's numeric values at both beta,
  timestamped before the first research number: **YES** (section 1).
- P4 adjudicated before P3, P5, or the real arm: **YES** (section 2, and
  `measure.py`'s per-cell print order in `stdout.log`).
- The SE-of-the-difference derivation for P3 shown with its inputs, not
  asserted: **YES** (section 3, `prediction_frozen.json` `threshold_fix`).
- The falsifier (P5) checked and reported even though it came in short of
  the predicted rate: **YES** (section 4, section 8 A1).
- No quantity transported outside the measured cells; no red-team probe
  number presented as this task's own result: **YES** -- every number in
  `prediction_frozen.json` and `results.json` was computed by this task's
  own code from its own seeds; RT-20260806-d008e0 is cited only in section 0
  as design rationale.
- All planned runs terminal: **YES** (one smoke, one medium-scale timing
  check outside the deliverables, one full protocol run, one verification
  run; protocol runs used: 1 of 2 permitted).
- Required artifacts present: **YES** (`measure.py`, `verify.py`,
  `prediction_frozen.json`, `results.json`, `verification.json`, `report.md`,
  `receipt.json`, `command.txt`, `environment.json`, `stdout.log`,
  `stderr.log`, `verify_stdout.log`, `verify_stderr.log`).
- Raw data and summary tables agree: **YES** (sections 2-7 quote
  `results.json` directly; `verify.py` V1-V5 cross-check independently).
- Reproduces from the recorded command and revision: **YES** for the
  Gaussian-null and forced/derived values (bit-for-bit via `verify.py` V1-
  V3); to within 0.2% for the full real/haar/t0 recompute in V4, which uses
  a deliberately different (not bit-identical) CBD sampler and a different
  GSO algorithm as the independence requirement, not an exact-reproduction
  requirement.
