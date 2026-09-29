# TASK-20260813-59c321 — INDEPENDENT VALIDATION

    goal / batch    GOAL-MLKEM-005 / BATCH-6b6e78
    role            validator
    policy          review-adversarial     effort xhigh
    state           queued
    depends_on      TASK-20260813-2ce014, TASK-20260813-48240d
    review_required false
    archived_by     TASK-20260813-3dfbdb
    budget          7200 s, 4 GB, 1 run
    independence    INDEPENDENT SESSION REQUIRED
    claim tier      TOY

## What you are verifying

The lead's exact-route certification, the two-precision table, the per-candidate
fibre guard, the three `F0` readings `V6`/`V7`/`VX`, the `K`-interval computation
and the `X_hash` calibration — **re-derived from the FROZEN TEXT without importing
the producer's module, rebuilding the bases FROM THEIR SEEDS**. In `BATCH-4ed139`
that standard produced 1368 of 1368 bit-identical per-cell values. That is the
standard.

## The git record is a COORDINATOR CLAIM until you check it

Check the notarization chain **in both directions** with git plumbing in this
worktree: `prereg.md` **absent** at the notarizing commit's parent; **zero**
producer files at the notarizing commit; every lead artifact **first appearing**
at the producer snapshot; ancestry asserted against the **notarizing commit
itself**; `git log --all --follow` returning **exactly one** commit for the frozen
text. A Validator has proved a Coordinator's account of the git record false twice
in this goal. **Do not accept it; check it.**

Then **change-set equality on both archives**: `TASK-20260813-502381` (3 declared
paths) and `TASK-20260813-48240d` (11). Each commit's change set equals its
declared set — own `artifact_paths` **union** source `artifact_paths` — with
**0 extra and 0 missing**. Report both counts per archive.

## The load-bearing new object is a DERIVATION, and nobody has checked it

PREREG-2 §2.9 asserts `X_gso_k = (1/(2k)) log det(I_k + A A^T)` on the frozen
families. **It is the Coordinator's own derivation** and it is what makes `A-1.1`
decidable for the one candidate that reads the instance. **Verify it as
mathematics** — symbolically, or on small cases you build yourself — and
**separately** verify the producer's numerical agreement with the committed
`RQ`/`RG` values. If the derivation is wrong, `FC-1` fires and this batch's branch
changes.

## Attack A-1 where PREREG-2 says it is weakest — it names the places itself

* **§1.3's `precision_degenerate` rule.** Does the frozen exemption remove exactly
  the cells where `A-1.2` could have failed? Under the strict reading, would
  `A-1` be falsified **by the definition of `R0`**?
* **§1.4's window `[1/2, 2]`** — the one calibrated constant in the whole
  falsifier, and its declared honest consequence (`A-1.3` is a weak test of the
  constant and a strong test of the classification). Is that true as measured?
* **§6.2's could-not-FALSIFY arrangement.** Are both certified classes really
  populated, and by objects that are **not relabellings of each other**?

## Also required

* **Re-run the per-candidate fibre guard yourself** from §§2.3 and 2.4. It is the
  must-pass guard, and **its non-firing is evidence about the IMPLEMENTATION
  only** (§6.1) — do not report it as a control.
* **Build your own null** wherever a producer's construction is load-bearing: at
  minimum one observable named nowhere in PREREG-2, pushed through the identical
  code path, plus one perturbation of the `X_hash` family at an amplitude of your
  choosing.
* **Re-derive the three `F0` readings** and check that none is reported without
  its route set in the same sentence, and that `BATCH-4ed139`'s frozen verdict is
  **nowhere rescored**.
* **Re-derive the `K`-intervals** and check the obvious failure: an interval
  reported EMPTY because a max and a min were taken over the wrong or
  non-comparable sets.
* **State, per artifact read, whether it was read COMMITTED or UNCOMMITTED.**
  Every producer artifact is committed before you run, at `TASK-20260813-48240d`.
  If you had to read one uncommitted, **you have found something and must say so**.
* **Name, before you run, the arrangement in which YOUR OWN check could not fail,
  in both directions, and show you are not in it.**
* Say which of your checks are **arithmetic-class** and which are
  **generation-class**: a defect in how a producer's numbers were generated is
  invisible to arithmetic on those numbers.

## Artifacts and declared gap G-1

    reviews/TASK-20260813-59c321/validation_report.yaml
    reviews/TASK-20260813-59c321/probes/...            (every probe you write)

**LIST EVERY PROBE PATH EXPLICITLY IN YOUR REPORT.** The queue declares one path
for you today and that will not be enough: the ledger archive's declared set must
be extended by **exactly** your probe paths before it stages (`G-1`). An
undeclared probe cannot be committed and its evidence is lost; a declared probe
that does not exist dangles the archive. Both are defect D3.

## Binding

**COMMIT NOTHING.** Your report sits uncommitted across a dispatch window (PD-4,
open and inherited) and is the **sole carrier** of its own evidence — write it so
it stands alone. Record independence as **PROCEDURAL and never model-level**, with
`model_verified` and its reason and your host and stack. **Do not restate
`KN-FIND-9d44b4`'s promoted content as a new result of this batch.** PREREG-2 §§10
and 10.1 bind in full. Premature closure and unbounded repair are the same failure
mode in two directions; closing the admissibility-gate LANE retires the **LANE**,
never the goal. **CLAIM TIER TOY.** `knowledge/INDEX.md` is not written,
regenerated or staged.
