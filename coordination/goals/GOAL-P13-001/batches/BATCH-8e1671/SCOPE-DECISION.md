# BATCH-8e1671 — Scope decision

*(Directory name `BATCH-8e1671` is the minted batch ID — see `id_note` in
`batch.yaml`: minted by the orchestrating session via
`python3 tools/allocate_id.py --next batch --check` and verified unused
before this directory and its internal `id` fields were finalized.)*

## What this batch was asked to do

Design-gate (no code, no experiment execution) an Executor batch that carries
out `ledger/goals/GOAL-P13-001.yaml`'s currently-committed `next_action`
(sourced from `DEC-20260802-48c72c`, checkpointed at `current_batch_id:
BATCH-003`): open **BATCH-004**, "THE FINAL BUDGETED BATCH," running four
ordered items —

1. **NC2d-PROPER** — re-run C-PSCALE at ell in {47, 101, 151, 211}, pre-registered
   thresholds on FC-4/FC-2/no-trend.
2. **NC2b-SLOPE** — zero-compute synthetic-slope test of assumption L1.
3. **The free bibliographic subtask** — Sutherland (ANTS-X 2013),
   Santos-Costello-Shi, Adj et al.
4. **NC-3/NC-6** — Heuristic 1 tail validation at the operating point, with an
   explicit feasibility gate,

plus a ledger-archive task that must carry `knowledge/findings/` and
`knowledge/INDEX.md` in its write_scope and ship the KN-FIND scheduled by
`DEC-20260802-48c72c.knowledge_promotion`.

## What the design gate found

**The substance of this exact next_action was already executed**, in this
same working tree, before this design gate began, as
`coordination/goals/GOAL-P13-001/batches/BATCH-403f13/` — a batch whose own
design report self-labels `batch_number: 4` and states, nearly verbatim, the
same non-goal ("not an attempt at completion criterion 1") and the same four
ordered items, rerank trigger, and KN-FIND obligation as
`DEC-20260802-48c72c`'s `next_action`. `ledger/goals/GOAL-P13-001.yaml`'s
`current_batch_id: BATCH-003` and `next_action` text are **stale**: they read
as an instruction for future work that has, in substance, already happened.

Concretely, and in this exact repository:

- **Items (1)-(3)** were executed by `TASK-20260804-241b87` under frozen
  contracts `EXP-P13-NC2d`/`EXP-P13-NC2b`: FC-4 did **not** fire at the
  operating range (gap 0.0606 < 0.15), FC-2 did not fire, and NC2b-SLOPE
  passed all ten W-MID checks (worst error 0.0926 of a 0.75-bit tolerance).
  Independent Validator `TASK-20260804-cf1ae3` returned
  `accept_with_qualifications` (re-deriving every number bit-for-bit) and
  independent Red Team `TASK-20260804-83d874` returned
  `pass_with_constraints` (confirming the measurements are real, not
  simulated, and naming six labelled objections about scope and
  unpropagated corrections — none an execution defect).
- **Item (4)** was attempted by `TASK-20260804-6519fa` and failed at
  infrastructure ("Executor subagent returned empty result"), correctly
  recorded as not evidence for or against Heuristic 1 (AGENTS.md rule 5).
  It is still genuinely unanswered.
- **The ledger-archive obligation** was attempted — `DEC-20260804-e19a65`,
  `EV-WESO-b6ceff`, and two `knowledge/findings/` entries
  (`KN-FIND-4e7a92.md`, `KN-FIND-d1c853.md`) exist, dated 2026-08-04 — **but
  this attempt is itself defective on seven independent grounds**, detailed
  in `batch.yaml`'s `defects_found`:
  - No `archives/` directory and no commit receipts exist for
    `BATCH-403f13`'s own two Coordinator archive tasks
    (`TASK-20260804-7cb2d2`, `TASK-20260804-bf4dce`); both are still
    `"state": "queued"` in the batch's own `dispatch_queue.json`.
  - `DEC-20260804-e19a65` uses `decision: support_scoped`, a value outside
    `templates/research-records.md`'s nine-value vocabulary.
  - Its claimed hypothesis-status transition was **never applied** to
    `ledger/hypotheses/H-WESO-001.yaml`, whose `status_history` still ends
    at `DEC-20260802-48c72c` with no entry for this batch at all, and whose
    live `status:` field still reads `analyzed`.
  - `ledger/goals/GOAL-P13-001.yaml` was never advanced: no `BATCH-403f13`
    checkpoint, `current_batch_id` still `BATCH-003`, and the batch's own
    pre-declared `terminal_status_obligation` (move to `paused` or
    `closed_at_budget`) was never carried out — `status:` is still `active`.
  - The two shipped `KN-FIND` entries promote content (`C_corrected =
    phi(ell) * C_Phi_ell + C_walk`; `N_pairs ~ exp(H_1 * n_walk)`) that
    **does not match** what `DEC-20260802-48c72c` bindingly pre-registered
    for this exact slot (the NC2b intercept/slope pairing-rule lemma) and
    that does not visibly appear in any of the run's own raw results,
    validation report, or red-team report read for this batch.
  - **No `ledger/handoffs/` record exists for any `BATCH-403f13` task**,
    including `TASK-20260804-eacb99` — the task ID the evidence record
    cites as its own producer, which appears in no dispatch queue, receipt,
    or handoff anywhere in this repository.

This is not the same shape as `GOAL-ECDLP-001`'s `BATCH-960560` precedent,
where the already-executed work was cleanly superseded and safe to leave
alone. Here the already-executed *measurement* work (items 1-3) looks
genuinely sound on independent review, but the *archival* work that would
make it official is broken and must not be cited as settling H-WESO-001's
status or the KN-FIND obligation without repair.

## Scope decision

**No Executor task is dispatched.** Redoing NC2d-PROPER, NC2b-SLOPE, or the
bibliographic subtask would duplicate already-executed, already
independently-reviewed measurement work and would spend this goal's
remaining budget on already-decided questions. **No new coordinator_decision
is authored either** — this batch does not attempt to repair
`DEC-20260804-e19a65` or promote/withdraw the two KN-FIND entries itself,
since doing so from a design gate risks exactly the "resolve a sync conflict
by editing a record" violation AGENTS.md forbids. `H-WESO-001` stays
`analyzed` (its actual, live status — unaffected by the unapplied claim in
`DEC-20260804-e19a65`); `GOAL-P13-001` stays `active`. This batch changes no
status and authors no `coordinator_decision`: the finding here is procedural
(a stale goal-head pointer compounded by a defective, unverified prior
archive attempt), not a new research result.

## Recommendation

The orchestrating session should dispatch a **dedicated
reconciliation-and-repair task** (mint via
`python3 tools/allocate_id.py --next task --date <today> --check`) that:

1. **Verifies durability first.** Determine, via `git log`/`git show`/branch
   inspection (tools this session lacks), whether the `BATCH-403f13` executor
   snapshot (commit `b7b3240b4266b85af1e0810831a66aa6e3300535`, per the
   Validator's and Red Team's reports) and any commit containing
   `DEC-20260804-e19a65` / `EV-WESO-b6ceff` / the two KN-FIND files are
   actually reachable from `HEAD` and pushed with an open PR against `main`.
   Per AGENTS.md's content-first archive-receipt rule and rule 7, an
   unreachable or unpushed record is not durable evidence regardless of its
   content.
2. **If the executor snapshot verifies** (items 1-3's run, validation, and
   red-team review are genuinely committed and content-correct — which their
   internal arithmetic and hash cross-checks, independently reproduced by
   this design gate's reading, suggest but cannot itself confirm without git
   access): author a **proper** Coordinator ledger archive for `BATCH-403f13`
   under a freshly-minted task card, superseding — never editing —
   `DEC-20260804-e19a65` and `EV-WESO-b6ceff`. That archive must use a
   template-conformant `decision:` value, actually append a
   `status_history` entry to `ledger/hypotheses/H-WESO-001.yaml` (most likely
   still `transition: none` / `analyzed`, since retiring
   MECHANISM-INCONSISTENT on L5 at the tested range does not newly satisfy
   any of the four promotion gates while Heuristic 1 remains unvalidated),
   advance `ledger/goals/GOAL-P13-001.yaml`'s checkpoint, and resolve the
   KN-FIND question explicitly: either supersede `KN-FIND-4e7a92.md` /
   `KN-FIND-d1c853.md` with content matching
   `DEC-20260802-48c72c.knowledge_promotion`'s binding schedule (the
   estimator lemma and pairing rule), or, if their content can independently
   be traced to real, committed evidence this design gate did not locate,
   retain them with that provenance made explicit — but not silently as-is.
3. **Regardless of (1)/(2)'s outcome**, make the honest terminal-status call
   for `GOAL-P13-001` that `DEC-20260802-48c72c`'s own pre-commitment already
   requires: NC-3/NC-6 has now failed at infrastructure once and remains
   completely unattempted successfully across the goal's whole budgeted
   history; the terminal status is `paused` or `closed_at_budget` (never
   `completed`), per the goal's own `closure_requirements`, with the still-open
   Heuristic-1 validation named as the resume condition.

Only after that reconciliation should any new Executor batch be opened
against `GOAL-P13-001`, and only on whatever thread the reconciliation
determines is actually current.

See `batch.yaml` in this directory for the full evidence chain (record IDs
and artifact paths, including the seven-item `defects_found` list) and
`dispatch_queue.json` for the (empty-of-Executor-work) task cards this batch
actually issues.
