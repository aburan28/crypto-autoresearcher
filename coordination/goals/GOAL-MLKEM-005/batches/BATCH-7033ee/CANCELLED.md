# BATCH-7033ee — CANCELLED, per DEC-20260813-1aae44

**This batch's remaining tasks are cancelled.** `BATCH-6e08fe`, opened by a
concurrent session, discharged `DEC-20260813-28d7b2`'s exact two-part
`next_action` first — RC-3 carried verbatim, and a genuinely non-code-shared
`ROUTE-I'` re-implementation of `lam1n`/`hkz` at `L7`/`L9`/`L11` — and was
fully reviewed and ledger-archived (`DEC-20260813-1aae44`, `EV-MLKEM-5aa471`)
before this batch's own lead producer's snapshot could be committed.

**The cancellation itself is already committed**, at `75cf42ef1` ("coord:
GOAL-MLKEM-005 BATCH-7033ee — cancel remaining tasks, superseded by
BATCH-6e08fe's close"), pushed directly to this branch by the session that
wrote `DEC-20260813-1aae44` — exactly the follow-up that decision's collision
note promised. **This file is a correction to that commit, not a
duplicate of it**, because that commit's own `cancellation_note` for
`TASK-20260813-415c21` states *"CANCELLED, not executed"* — which was accurate
when written (it only saw committed/pushed state) but is no longer accurate:
this session's lead producer had, in fact, already run in the background and
produced real output that was never pushed, so the other session could not
have known about it.

## What that commit assumed, and what actually happened

`DEC-20260813-1aae44` states: *"BATCH-7033ee's remaining tasks ... are all
still `queued` — NO MEASUREMENT, REVIEW OR LEDGER RECORD FOR BATCH-7033ee HAS
RUN, so no compute or review effort is wasted."* `75cf42ef1`'s own
`cancellation_note` repeats the same premise for each cancelled task. Both
were accurate at the moment they were written, reading only what was
committed and pushed. **Neither is accurate now.** This session's lead
producer (`TASK-20260813-415c21`) had already run to completion in the
background — dispatched before this session learned of the collision, and
finishing after `75cf42ef1` was already pushed. Recording that honestly
rather than silently discarding it (AGENTS.md rule 8, rule 9):

**What the (now-cancelled) producer found:** its own from-scratch `ROUTE-I2`
(independently built, no relation to `BATCH-6e08fe`'s `ROUTE-I'`) reported
full coverage (18/18 `COVERED2`) and fired `T-INDEP-UNDERMINES` (no `-PARTIAL`
suffix) — a stronger, undifferentiated result than `BATCH-6e08fe`'s
per-candidate `T-INDVERIFY-ARTIFACT-PARTIAL` split. At `L7`/`L9` (12 cells),
`D_route_independent` matched `PREREG-3`'s archived `0.0` to machine epsilon.
At `L11`/`d=40` (6 cells, both `lam1n` and `hkz`), `D_route_independent`
exceeded `s_c^fib` at every cell.

**Why this is not read as a second, corroborating undermine of `BATCH-fbb639`'s
`L11` verdicts.** The producer's own report discloses that its from-scratch
reduction did not reach full convergence at `d=40` within its time budget: 3
of 8 bases at `L11` show `converged: false` in `results_route_i2.json`'s
`route_i2_reduction_diagnostics`. Critically, the `L11` disagreement affects
**`lam1n`, not only `hkz`**. `KN-FIND-7de6b6` (promoted from `BATCH-6e08fe`,
reviewed independently by two methods) establishes that `lam1n` is an exact,
algorithm-independent lattice invariant: any two *correct* computations of it
must agree to floating-point precision regardless of reduction quality or
implementation, unlike `hkz`, which is fidelity-sensitive. A disagreement on
`lam1n` itself is therefore the signature of an incomplete/incorrect
computation on at least one side, not of a genuine independence failure or of
implementation fidelity mismatch (`KN-FIND-7de6b6`'s own diagnosed confound,
which is specific to fidelity-sensitive quantities like `hkz`). The most
plausible explanation, stated as an assessment and not re-derived or reviewed:
this now-cancelled implementation's own disclosed non-convergence at `d=40`,
not a property of `ROUTE-P`, `ROUTE-I'`, or the underlying lattices.

**This is not promoted to a knowledge finding.** It never received the
independent validator/red-team review this campaign requires before any
observation is trusted (this batch's reviews, `TASK-20260813-e04ebc` and
`TASK-20260813-28eb06`, are cancelled below, never dispatched). It is recorded
here, plainly, as an unreviewed, non-evidentiary observation from a cancelled
duplicate run — consistent with, and not contradicting, `BATCH-6e08fe`'s
official, reviewed result.

## What is and is not archived

- `TASK-20260813-61dab8`'s `PREREG-4` and `TASK-20260813-30cdca`'s
  notarization (commits `e04d509b4`, `e40098f4f`) are already committed and
  are retained unedited — immutable per `DEC-20260813-1aae44`'s instruction,
  a documented record of this concurrency-failure instance.
- `dispatch_queue.json` already carries `state: "cancelled"` for
  `TASK-20260813-415c21`, `TASK-20260813-5d1920`, `TASK-20260813-e04ebc`,
  `TASK-20260813-28eb06` and `TASK-20260813-fe3dec` (commit `75cf42ef1`).
  This commit corrects only `TASK-20260813-415c21`'s `cancellation_note`,
  which is factually wrong ("not executed"), and adds nothing to the other
  four tasks' notes, which remain accurate.
- `TASK-20260813-415c21`'s seven artifacts (`measure_route_i2.py`,
  `results_route_i2.json`, `report_route_i2.md`, `command.txt`, `stdout.log`,
  `stderr.log`, `run_manifest.yaml`) are committed in this same follow-up
  commit, for transparency, but are **explicitly not an archive under
  `tools/research_dispatch.py`'s meaning of the term** — no
  `snapshot-receipt.json` is written for them, they carry no `path_sha256`
  binding, and `TASK-20260813-5d1920` (their would-be snapshot archive) stays
  cancelled rather than run.

`EV-MLKEM-bae519` and `DEC-20260813-a7826b` (reserved by this batch's setup,
never written) stay unallocated to any record; they are simply not used.

## Goal state

`GOAL-MLKEM-005.yaml`'s `current_batch_id` is `BATCH-6e08fe` and its
`next_action` is `DEC-20260813-1aae44`'s. This batch does not touch either
field — it never reached a ledger archive and makes no state-transition claim.

## A second, separate process defect: the frozen prereg was edited post-notarization

Commit `582fcdccd` ("Fix PREREG-4 frozen s_c^fib path and close
termination-clause gap"), authored by a Cursor Agent session and pushed
directly to this same branch, **edits `TASK-20260813-61dab8/prereg.md`
in place** — after `TASK-20260813-30cdca` had already notarized it at
`e40098f4f`. This batch's own `dispatch_queue.json` states the rule this
violates explicitly, twice: *"Do NOT edit prereg.md. It is frozen; a
correction is a superseding record under a new identifier."* Recorded
plainly rather than silently accepted or silently reverted:

- The two changes are, on their face, genuine bug fixes (a JSON path that
  named a nonexistent key; a termination-clause gap between the
  `CONFIRMS`/`UNDERMINES` branches for an intermediate `D_route_independent`
  value) — this note does not dispute their content.
- **The correct mechanism for either fix was a new, superseding
  pre-registration under a new identifier**, exactly as this batch's own
  rule states, never an in-place edit of the notarized file. Editing it
  destroys the notarization property this batch was built around: that
  `prereg.md` FIRST APPEARS, unchanged, at the notarizing commit, and cannot
  have moved under the measurement it governs.
- Whether `TASK-20260813-415c21`'s lead producer consumed the original or
  the edited text is not established here and is not investigated further:
  the batch is cancelled and superseded regardless, so nothing turns on it.
  This is recorded as a standalone integrity finding about the branch, not
  as a defect in the producer's own (also cancelled, also unreviewed)
  result.
- This is the **third** distinct concurrency failure this branch has now
  shown in one session (batch-level duplication with `BATCH-6e08fe`; a
  stale-assumption cancellation note; now an in-place edit of a file another
  session had already frozen) — all on the identical branch name
  `cursor/launch-mlkem-harness-78fd`, meaning multiple agent sessions were
  writing to the same branch concurrently, not merely reading the same
  `main`. This is a sharper instance of the "many agents, many worktrees"
  hazard `AGENTS.md`/`CLAUDE.md` already name: those documents assume
  collisions are discovered at a *merge* into a shared branch; here the
  collision was between two sessions both holding write access to the
  *same* branch, which no merge-time check catches, since there is no merge
  — only a race on who pushes next.

## Process lesson

This is the second instance in one session of the same concurrency pattern
this goal's own `KN-FIND-3546c2` (a different goal, `GOAL-MLKEM-004`) and this
decision's own collision note describe: a session drafts and opens a batch
against a `next_action` that a concurrent session is simultaneously
discharging, and only a merge-time or branch-scan check catches it. Unlike
the `GOAL-MLKEM-004` instance, real compute *was* spent here (a 981s-class
measurement run), because the collision was only detected after the producer
had already been dispatched in the background — the freshness check this
session ran before dispatching (re-confirming `origin/main`) could not see a
sibling open branch's in-flight work, only committed, pushed state. A
freshness check against `origin/main` alone is insufficient once multiple
agents can have long-running producers in flight simultaneously against the
same active goal; catching this earlier would require checking open PR
branches for in-flight producer dispatches, not only completed archives —
consistent with, and reinforcing, `CLAUDE.md`'s existing instruction to
compare against every open research branch, not only `main`.
