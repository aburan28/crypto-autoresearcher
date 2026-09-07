# Coordinator note — BATCH-1d7925: b66e3f was already done, and 9b6879 is unbindable

Recorded 2026-09-07 by `coordinator-ecdlp-1d7925-2`. **Additive. Supersedes
nothing. No status change, no claim promotion, no execution authorization.**

## 1. A duplicate-work incident, disclosed

`tools/research_dispatch.py` offered `TASK-20260907-b66e3f` as the single Ready
Task of `BATCH-1d7925`. It was not: the task had already been performed and
committed at `1772df012` (2026-09-07 16:21Z), together with its archive
receipt for `TASK-20260907-9b6879`. The dispatcher offered it only because the
queue's `state` fields were never written back after that commit.

This session claimed the task and ran a second Coordinator pass, which
**overwrote the four committed artifacts in the working tree**. The overwrite
was never committed. All four files were restored with `git checkout` and
re-verified byte-for-byte against the `path_sha256` recorded in
`archives/TASK-20260907-9b6879/ledger-receipt.json`:

    deconfliction-report.yaml     cf7c286d12…  OK
    provenance-audit.yaml         a2843b23f4…  OK
    recovery-assessment.json      16fecbef07…  OK
    runtime-session-receipt.json  4b79cc08b5…  OK

Nothing durable was changed. `TASK-20260907-b66e3f` is recorded `completed` in
the queue by this note's accompanying edit, so no third session repeats it.

**The generalizable defect:** a completed task whose queue `state` is never
written back is indistinguishable from an unstarted one, and the next session
redoes it. The claim system cannot catch this — there is no claim to collide
with. Check artifact existence before claiming, not only queue state.

## 2. `TASK-20260907-9b6879` cannot currently be bound — NOT actioned here

The archive receipt is `status: prepared_for_post_commit_verification` with
`commit_sha: null`. Its real commit is `1772df012`. It binds under **neither**
dispatcher mode:

- **`commit` mode fails.** Expected paths are the archive's five artifacts plus
  `b66e3f`'s four, nine in total. `1772df012` changed those nine plus three
  extras — `dispatch_queue.json`, `ledger/handoffs/TASK-20260907-b66e3f.yaml`,
  `ledger/handoffs/TASK-20260907-9b6879.yaml` — and the exact-changed-paths
  gate rejects extras. (Identical failure shape to `TASK-20260907-2cd955` on
  GOAL-ECRANK-002, re-bound there under `content_first`.)
- **`content_first` mode fails as declared.** It verifies declared bytes at
  HEAD, and one declared artifact has legitimately advanced since the archive:

      experiments/EXP-ECDLP-a98ea9/specification.yaml
        receipt declares  a31930d4a9…
        HEAD reads        bfceacd182…

  This drift is **not corruption**. The contract was amended after the archive
  by `amendments/v1_execution_authorized.yaml` and
  `amendments/v2_stage2_authorized.yaml` under `DEC-20260907-933a06` and
  `DEC-20260907-951f3a`, which set `execution_authorized: true` and
  `execution_authorized_stages: [0, 1, 2]`. Five runs now exist
  (`RUN-ECDLP-a98ea9-S0`, `-S1`, `-S2`, `-S2b`, `-S2c`).

  Consequence for readers: `DEC-20260907-1cf1c0` records
  `execution_authorized: false` and `experiment_runs_authorized: 0`. **That is
  superseded, not contradicted** — it was true when written and the later
  decisions moved it. Do not cite `1cf1c0` as current execution authority.

The owning session should re-bind `9b6879` under `content_first` against
CURRENT HEAD hashes, in a superseding receipt that names both the archive-time
and HEAD hashes of `specification.yaml` and cites the two amendments. This
session did not do it: `9b6879` is not Ready, this session never claimed it,
and forcing a binding on another lane's archive is not a Coordinator repair
it is entitled to make unilaterally.

## 3. Second-pass observations, recorded as leads only

An independent second Coordinator pass over the same read_scope concurred with
all four recorded verdicts of `DEC-20260907-1cf1c0` (Q1 `distinct`, Q2
`faithful_with_disclosed_tightenings`, Q3 `revise_then_approve`, Q4
`complementary_hold_CAND-D2-A`). Its output is **not** committed and does not
supersede the official report. Two observations are worth an owner's attention
and are recorded here as leads, each still to be checked by whoever acts:

- **The `EXP-ECDLP-a98ea9` blocking r=1 fixture gate may be unresolvable as
  written.** It names "the sibling record's committed x-bucket values" with no
  record ID and no numbers, where the sibling `EXP-ECDLP-56ee42` pinned the
  same class of gate to a concrete value. A blocking gate an Executor cannot
  resolve cannot fail, so it gates nothing. Stage 2 is now authorized and reads
  it, so pinning it by versioned amendment is time-critical. UNVERIFIED by this
  note.
- **`RUN-ECDLP-56ee42-S2` self-reports `validity: gate_failure`**, which if
  correct strengthens rather than weakens the Q1 `distinct` verdict. UNVERIFIED
  by this note.
- The predecessor handoff `TASK-20260904-2f7237` points at
  `experiments/EXP-ECDLP-56ee42/runs/`, which holds only `.gitkeep`; the runs
  are under `implementation/runs/`. A literal successor would conclude no run
  existed. UNVERIFIED by this note.

Neither the second pass nor this note asserts anything mathematical about the
ECDLP, promotes any claim, or authorizes any execution.
