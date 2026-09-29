# CORRECTION-20260814-c2-status — BATCH-27c132's own "three still-untouched completion criteria" framing is inaccurate for C2

Written by TASK-20260814-0e7de6 (Coordinator-only snapshot archive). This is a
standalone correction note. It does not edit, and must never edit,
`PORTFOLIO-RULING-20260814.md`, `dispatch_queue.json`, or `task_card.md` in
this batch directory — those stay exactly as originally committed, per
AGENTS.md rule 2 (immutability; corrections supersede, never overwrite).

## The correction

`GOAL-MLKEM-005`'s completion criterion **C2 (the census of M) was already MET
at `BATCH-a51f91`** and has been restated unchanged through every subsequent
`batch_log` entry, including this goal's own most recent entry, `BATCH-a5b13c`
— the batch this task's own handoff chain is opened against. The framing that
GOAL-MLKEM-005 has "three still-untouched primary completion criteria"
(C1, C2, and C3 together), which appears in this batch's own opening
documents, is **inaccurate for C2**. Only C1 and C3 remain open.

## Evidence, cited exactly

- `ledger/goals/GOAL-MLKEM-005.yaml` line 1262-1266, the `completion_criteria`
  item text for C2: "A census of M ... across standardised and deployed
  ML-KEM uses, reported as a DISTRIBUTION ... SATISFIED BY 'M = 1 in every
  standardised mode we could source', which is the cheapest and most likely
  outcome."
- `ledger/goals/GOAL-MLKEM-005.yaml` line 2212 (`batch_log` entry
  `BATCH-a51f91`, `decision_id: DEC-20260805-4823db`, `evidence_id:
  EV-MLKEM-d146a5`), `criteria_state.C2`: "MET, with its distribution
  restated. 24 sourced rows carrying specification, section, bounding
  mechanism and retrieval date; the validator re-fetched the load-bearing
  sources byte-identically ... [2 modes fix M=1 normatively, 2 more
  single-use with a caveat, 2 state one ciphertext per handshake under a
  reuse-permitting clause, and 8 state no count bound at all]."
- `ledger/goals/GOAL-MLKEM-005.yaml` line 3352 (`batch_log` entry
  `BATCH-a5b13c`, this goal's own most recent entry, `decision_id:
  DEC-20260814-b0a095`), `criteria_state.C2`: "MET at BATCH-a51f91,
  unchanged." Every intervening `batch_log` entry between `BATCH-a51f91` and
  `BATCH-a5b13c` (lines 2264, 2298, 2363, 2457, 2669, 2791, 2891, 3001, 3085,
  3145, 3209, 3280) restates the identical "C2: MET at BATCH-a51f91,
  unchanged" (or the equivalent "C2 MET at BATCH-a51f91, both unchanged" at
  line 2791) with no reversal anywhere in the chain.
- `ledger/decisions/DEC-20260814-b0a095.yaml` lines 393-396
  (`binding_carries_restated_and_not_re_litigated`): "GOAL-MLKEM-005's own
  untouched primary completion criteria (a numeric best-of-M dbeta under a
  named cost model; the projected-error-norm/Beta-law measurement on real
  BKZ-reduced bases) are NOT advanced by anything in this batch" — naming only
  the C1 object (the dbeta bound) and the C3 object (the Beta-law
  measurement), never C2.
- `ledger/decisions/DEC-20260814-b0a095.yaml` lines 592-597 (`next_actions`):
  "redirect RQ-MLKEM-001 capacity toward GOAL-MLKEM-005's own STILL FULLY
  UNTOUCHED primary completion criteria (a numeric best-of-M dbeta under a
  named cost model; the projected-error-norm/Beta-law measurement on real
  BKZ-reduced bases)" — again naming exactly the same two objects (C1, C3),
  never a third.

**`DEC-20260814-b0a095.yaml` itself is accurate on this point and needs no
correction.** Both of its own untouched-criteria statements name only C1 and
C3.

## Where the inaccurate framing lives in this batch

- `coordination/goals/GOAL-MLKEM-005/batches/BATCH-27c132/PORTFOLIO-RULING-20260814.md`
  line 130-131: "redirect RQ-MLKEM-001 capacity toward GOAL-MLKEM-005's own
  untouched C1-C3 completion criteria" — conflates all three, though the same
  document's own line 150 correctly narrows to "GOAL-MLKEM-005's C1/C3" a few
  lines later, an internal inconsistency in the Portfolio Ruling's own text.
- `coordination/goals/GOAL-MLKEM-005/batches/BATCH-27c132/dispatch_queue.json`
  line 9, `objective` field: "GOAL-MLKEM-005's own three still-untouched
  primary completion criteria."
- `coordination/goals/GOAL-MLKEM-005/batches/BATCH-27c132/tasks/TASK-20260814-ac35d8/task_card.md`
  line 1 ("...for GOAL-MLKEM-005's own C1-C3") and line 17 ("GOAL-MLKEM-005's
  own still-untouched primary completion criteria"), which share the same
  three-criteria wording and the same gap.

None of these three files is edited by this correction. They remain exactly
as originally committed. This note stands beside them as the correction
record, per AGENTS.md rule 2.

The idea-generator dispatched under this batch (`TASK-20260814-ac35d8`)
independently identified and disclosed this same gap in its own deliverable
(`ideas_proposal.md` section 0.1), before this note was written; this
correction confirms that finding against the primary ledger records directly,
with exact line citations, rather than relying on the producer's own
self-report.

## Consequence: does NOT change the portfolio choice

This correction does **not** change BATCH-27c132's portfolio choice (option
(ii): redirect `RQ-MLKEM-001` capacity toward `GOAL-MLKEM-005`'s own open
completion criteria via a fresh `/propose-ideas` pass, rather than option (i),
a further `H-MLKEM-11aabf` follow-up, or option (iii), advancing an
off-object control-tier hypothesis). If anything, the corrected framing
**strengthens** that choice: C1 and C3 are now stated as the goal's *only*
remaining open primary completion criteria, sharpening rather than diluting
the case for redirecting capacity toward them.

Despite the stale "three still-untouched criteria" premise carried into this
batch's own opening documents, **all four ideas returned by
`TASK-20260814-ac35d8` were filed as real ledger records** under this task
(`TASK-20260814-0e7de6`), per the schema-completeness-only filing gate
(`.claude/skills/propose-ideas/SKILL.md` steps 4-5: filing is a pure
schema-completeness gate, not a priority or scope filter). This includes
`ledger/proposals/IDEA-20260814-a609eb.yaml` (the C2-facing idea,
`IDEA-PENDING-3` in the producer's deliverable), whose own record honestly
states — in its own `claim`, `interpretation_limits`, `dominated_by`,
`sota_delta`, and `recommended_priority: low` fields — that it does **not**
advance C2 (already met) or any other completion criterion; it is filed as a
low-priority, optional maintenance audit only.

## Recommendations for the next Coordinator act on this goal

1. This batch's eventual closing decision record (a future `DEC-*`) should
   restate the corrected C1/C3-only framing in its own `context` or
   `rationale` field, rather than repeating the "three still-untouched
   criteria" language this batch's own opening documents carried.
2. Any future dispatch brief for `GOAL-MLKEM-005` should **not** require a
   "C2-facing idea" as a mandatory ideation deliverable, since C2 is already
   met and a mandatory C2-facing idea can only ever produce a low-priority
   maintenance audit at best (as `IDEA-20260814-a609eb` demonstrates) —
   dispatch capacity is better spent on ideation explicitly scoped to C1 and
   C3 alone.

## Recommendation carried forward from the producer session, not acted on here

`ledger/proposals/IDEA-20260805-3d71ca.yaml` — filed 2026-08-05, the same day
`GOAL-MLKEM-005` was created — already states, almost verbatim, this goal's
own tracked object (a shared BKZ-reduced basis plus a per-target
Gram-Schmidt tail profile; its heuristic H1 states
`||pi_{d-beta}(t~)||^2` behaves like `||e||^2 * Beta(beta/2, (d-beta)/2)`,
the exact object and distribution named in `GOAL-MLKEM-005.yaml`'s own
`objective` and tracked-object fields). It has sat unconverted to a
hypothesis for approximately nine days and thirteen batches. This is recorded
here as a **recommendation for the next batch's Coordinator decision to
weigh**, not acted on by this task: converting `IDEA-20260805-3d71ca` to a
hypothesis, and/or dispatching `/design-experiment` on
`ledger/proposals/IDEA-20260814-10e5e1.yaml` (which composes
`IDEA-20260805-3d71ca`'s own H1 with `H-MLKEM-dc51f5`'s GAIN(u) balance
argument at census-real M) are both live candidates for that decision, but no
hypothesis status, experiment approval, or goal-state change is made by this
task — this task holds no such authority.
