# TASK-20260813-3dfbdb — LEDGER ARCHIVE (runs alone, after BOTH reviews)

    goal / batch    GOAL-MLKEM-005 / BATCH-6b6e78
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-59c321, TASK-20260813-85e343
    review_required false
    archive         ledger, sources both reviews
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## What it commits

The **review half and the ledger half only**. The lead producer is already
committed at `TASK-20260813-48240d`, and PREREG-2 at `TASK-20260813-502381`.

    archives/TASK-20260813-3dfbdb/ledger-receipt.json
    ledger/evidence/EV-MLKEM-4ba196.yaml
    ledger/decisions/DEC-20260813-c60bba.yaml
    ledger/goals/GOAL-MLKEM-005.yaml
    reviews/TASK-20260813-59c321/validation_report.yaml
    reviews/TASK-20260813-85e343/red_team_report.md

**SIX BEFORE THE `G-1` EXTENSION.** Before staging, extend the declared set by
**exactly** the probe script and probe output paths the two reviews list in their
reports — **and by nothing else**. If the knowledge-promotion gate is met, one
`knowledge/findings/KN-FIND-*.md` path is minted **at close**, two-scope
confirmed, and added to **both** `artifact_paths` **and** `archive.record_ids`.

**DO NOT RE-DECLARE** the three paths already committed by `TASK-20260813-502381`
or the ten already committed by `TASK-20260813-48240d`. Re-declaring a committed
path produces a commit whose change set is **smaller** than its declared set —
the missing half of the same equality test D1, D2 and D3 failed.
`dispatch_queue.json` is deliberately not in this set.

## The reserved identifiers are RESERVATIONS, NOT CLAIMS

`EV-MLKEM-4ba196` and `DEC-20260813-c60bba` were minted and `--check`ed by the
dispatching session. **Use these exact identifiers**; do not mint replacements and
never grep for the next free number. **If this batch produces no evidence record,
LEAVE THEM UNUSED AND SAY SO** rather than writing an empty record to fill a
reserved slot. Re-run `tools/allocate_id.py --check` before staging and remember
it answers from the **working tree only**: a passing `--check` is **necessary and
not sufficient**, so sweep the remote refs too.

## Validity before interpretation, and it is CONFIRMED not remembered

Read the `TASK-20260813-48240d` receipt; confirm it records change-set equality
and its per-producer validity check; record that confirmation. Then verify **this**
archive's own sources — the two review reports — for completeness against their
completion gates. An invalid or incomplete run set goes **back to its producer**
with concrete defects listed. It is not evidence and it is not interpreted.

## The decision

Name the **frozen termination branch that fired**, quote the PREREG-2 clause, and
state exactly what it **licenses** and **forbids**. Do not re-read the clause and
do not report a branch the numbers do not fire. **If the evidence cannot
discriminate, the decision is `inconclusive` and says so plainly.**

* **If `T-UNSTATABLE` fired:** the admissibility-gate **LANE** closes with its
  named obstruction, its evidence, its budget, its test boundary, its remaining
  uncertainty and a concrete successor or revisit condition — and the decision
  states explicitly that **closing the lane retires the LANE, never the goal**.
  **Check first** that the branch fired for **every** in-scope candidate class and
  not for one, and that the declared out-of-scope status of the
  reduction-dependent candidates was **not** counted toward it.
* **If `T-A1-HELD` fired:** state in the same paragraph what `P-HASH` bounds — that
  precision-invariance is **necessary and not sufficient** for reading the
  instance, if that is what was measured — and apply **§7.5's repair bar in full**
  to anything the decision licenses. **`A-1` having survived is never reported as
  `A-1` being true.**

`knowledge_promotion` is **filled**: promote a `KN-FIND` when the decision is
`support` or `reject_scoped` on `replicated` or `strong` evidence (a proven
boundary counts), otherwise record a **concrete** `not_warranted` reason. **Do not
promote a restatement of `KN-FIND-9d44b4`.**

The goal record carries **exactly one** `next_action`, retains the prior text
verbatim under a `superseded_*` key, and gains a batch_log entry for
`BATCH-6b6e78` naming its decision and evidence IDs, both prior archive commits
and its two reviews.

## Order of operations

`tools/validate_ledger.py` → fetch and **MERGE** `origin/main` (never rebase;
record base commit and merge outcome) → declare every path → stage explicitly,
never `git add -A` → commit with the receipt **inside** it carrying
`commit_sha: null` → verify change set **equals** declared set, 0 extra 0 missing
→ **RUN THE POST-COMMIT VERIFIER BEFORE THE PUSH, NOT AFTER**, record the verdict
→ push → open or refresh the PR naming every new record → write the real sha and
parent into the queue's `archive` block.

**A sync conflict inside a ledger record, run artifact or knowledge entry is
resolved by a SUPERSEDING record under a new id — never by an edit that picks one
side.** `knowledge/INDEX.md` is not staged, written or regenerated.

## Binding

`reject_scoped` on a single unreplicated empirical-only run is **forbidden** — use
`weaken` plus replication, and archive the strongest checkable refutation artifact
**before** the decision that relies on it. A scoped rejection, an invalid run, an
exhausted batch, a lane closure or an empty ready set **ends the task, never
`GOAL-MLKEM-005`**; its pause conditions are infrastructure-only plus a user
request. **An instrument outcome is not converted into a finding**: seven
consecutive instrument batches is a recorded fact about this goal and it is not
repaired by calling the eighth a result. Rule 12 is **UNMET AND UNWAIVED** —
record independence as procedural and never model-level. **CLAIM TIER TOY.**
