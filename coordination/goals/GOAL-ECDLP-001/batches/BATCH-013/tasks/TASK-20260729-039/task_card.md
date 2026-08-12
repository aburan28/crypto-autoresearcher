# TASK-20260729-039 — Ledger archive of BATCH-013

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** coordinator (archival — **runs alone, after both reviews**)
- **Archive kind:** ledger; `source_task_ids: [TASK-20260729-037, TASK-20260729-038]`
- **Depends on:** TASK-20260729-037, TASK-20260729-038
- **Archived by:** itself
- **Budget:** 1800 s, 2 GB

## Objective

Write `EV-ECDLP-010` and `DEC-20260729-003`, checkpoint `GOAL-ECDLP-001` with
**exactly one** next action, and commit the eight declared paths **alone** —
adopting every required narrowing and every BLOCKING objection, filling
`knowledge_promotion` either way, and carrying the scope ruling and its
stopping rule into the ledger.

## Declared commit set — exactly 8 paths (default)

1. `.../BATCH-013/reviews/TASK-20260729-037/validation_report.yaml`
2. `.../BATCH-013/reviews/TASK-20260729-037/recount_note.md`
3. `.../BATCH-013/reviews/TASK-20260729-038/red_team_report.yaml`
4. `.../BATCH-013/reviews/TASK-20260729-038/falsification_review.md`
5. `.../BATCH-013/archives/TASK-20260729-039/ledger_commit_receipt.json`
6. `ledger/evidence/EV-ECDLP-010.yaml`
7. `ledger/decisions/DEC-20260729-003.yaml`
8. `ledger/goals/GOAL-ECDLP-001.yaml`

Path 5 is declared here and **lands in the immediately following commit**
(INT-BATCH007-T, now demonstrated). If any declared path was already committed
earlier, record that as an integrity note — **never enlarge or shrink the
declaration after the fact**.

**Knowledge promotion (10 paths iff warranted):** promote a KN-FIND only on
`support` or `reject_scoped` backed by `replicated` or `strong` evidence
(proven boundaries count). If warranted, a recorded QUEUE-AMEND adds
`knowledge/findings/KN-FIND-010.md` and `knowledge/INDEX.md` to this card's
`artifact_paths` and `write_scope` **before anything is staged**, the index is
**regenerated** with `tools/build_knowledge_index.py`, and both land in this
same commit. `KN-FIND-010` is **reserved and uncreated**. Otherwise record a
**concrete** `not_warranted` reason — *"not applicable"* is not a reason.

## Exclusive write scope

`ledger/evidence/EV-ECDLP-010.yaml`, `ledger/decisions/DEC-20260729-003.yaml`,
`ledger/goals/GOAL-ECDLP-001.yaml`,
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/TASK-20260729-039`

## Constraints

- **Verify validity before interpreting.** If VAL-20260729-002 sets
  `blocks_ledger_record: true`, or the run set is incomplete or invalid, the
  defects go back to the Executor as a concrete list and this card records that
  instead of an evidence record.
- **Adopt every required narrowing verbatim**, not paraphrased. Disposition
  **every** red-team objection with the action it implies; none is silently
  dropped. BLOCKING items are adopted in full, or the disagreement is argued
  explicitly on the merits and recorded.
- **Apply the pre-registered resume condition exactly as written.** If the
  replicated mean falls in the interval between about 0.14 and about 0.25 SEM,
  which neither branch names, **say so plainly and record the outcome as
  INCONCLUSIVE ON THE SHIFT** rather than assigning it to the nearer branch.
- **Scope the platform claim honestly — this is the first thing the record must
  get right.** If the interpreter build, OS and architecture did not change,
  both records state in terms that the replication separated *chance* from a
  *seed-independent deterministic property* of the driver-build-platform
  combination, separated none of those three from each other, and **is not a
  fresh-platform replication**. Record what it therefore cannot establish.
- **Draw no conclusion about the process** from the replicated statistic in
  either direction, and none about decomposition yield in any case.
- **Ceiling.** Claim tier **toy**. INV-4 not un-fired or re-disposed. INV-5
  neither way. No efficiency `E`, no yield ratio (including 0.85) as a
  measurement. H-YIELD-001 stays `specified`; H-STR-002 does not move in either
  direction (DEFER-BATCH009-001 binding); no other hypothesis moves. No cost
  model touched. No completion criterion met or claimed. **No closure quorum
  claimed or claimable.**
- **Do not quote the C-20 power sentence** unaccompanied by the RT21-1
  correction. Do not quote the EXP-YIELD-002 high-precision difference column
  as a confirmation of `T`. Do not say the repaired null lands **on** `P_pred`.
- **Carry every carried defect** into `DEC-20260729-003`'s own block,
  unretracted: RT21-1; RT21-8/DEV-4; O-4 component (d); RC-F; RC-B; NARROW-1
  through NARROW-7; INT-BATCH007-T as now demonstrated; INT-BATCH012-D and -F;
  the two duplicated immutable ids; the two unrenderable queues; the
  TASK-20260729-012 overrun; D-1 and D-2; the exact-A1 column; the untriggered
  odd-`C_red` arm.
- **Carry the scope ruling and its stopping rule into the ledger**
  (INT-BATCH013-K), including the ground on which a second track was refused,
  DEFER-BATCH009-001 ranked first for the successor batch, DEFER-BATCH013-001
  with its stated cost, and the bound that no batch after BATCH-014 may be
  justified by this lineage.
- **Checkpoint the goal with exactly one `next_action`**, preserving the prior
  value verbatim by supersession, never by overwrite. Record honestly that
  `maximum_batches = 13` is **CONSUMED**, that the first pause condition fires
  again on its own terms unless a completion criterion is met, and that **a
  fourteenth batch requires its own budget amendment on explicit user
  authorization — do not self-grant one.**
- Stage exactly the declared paths; stage nothing under `experiments/`; never
  `tools/validate_ledger_baseline.txt`; no AppleDouble sidecar.
- `yaml.safe_load` every YAML file written; check for space-hash truncation and
  for a mapping key at the indent of an open block sequence's entries.
- Commit message contains `TASK-20260729-039`, `EV-ECDLP-010`,
  `DEC-20260729-003`, `GOAL-ECDLP-001`, `BATCH-013` literally.
- Every SHA-256 from Git object content at the commit; declare the receipt's
  own ordering.
- **Fabricate nothing**: no timestamp beyond date precision, no commit SHA, no
  verdict, no statistic. Missing data stays missing and is reported as such.
