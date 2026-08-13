# Gate status — the TASK-20260807-dcfaee gate on opening GOAL-MLDSA-001's next batch

**Ruled by:** TASK-20260810-e45e48 (campaign RECON-20260810-002), 2026-08-10.
**Act type:** coordination. This ruling opens no batch and lifts no research hold.

---

## The gate

`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/tasks/TASK-20260807-dcfaee/reconciliation.md`,
section 1, closing sentence:

> "**This is flagged for a dedicated goal-head reconciliation task, following
> that precedent, before GOAL-MLDSA-001's next batch is opened.**"

RECON-20260810-001 (`TASK-20260810-1b82fe`) recorded that gate as
`STILL_STANDS_NARROWED`, with one limb already discharged (fact-finding) and
three named preconditions remaining.

---

## Verdict

> ### DISCHARGED ON CONTENT — AND NOT YET DISCHARGED IN FORCE.
> All three of the gate's narrowed preconditions are now satisfied **in the
> working tree**. None of them is satisfied **in the committed record**, because
> this task never commits. The gate is discharged the moment the two files below
> are committed and the post-commit verifier accepts them, and not one moment
> earlier.

And, separately from this gate:

> ### THE NEXT BATCH STILL DOES NOT OPEN.
> A different and independent hold blocks it — `DEC-20260805-79d745`'s "No new
> batch authorized under this constraint". That is a research-state hold on an
> infrastructure blocker, it is not part of the dcfaee gate, and nothing in this
> coordination act touches it.

---

## Precondition by precondition

RECON-20260810-001, `goal_mldsa_001.dcfaee_gate.narrowed_preconditions_on_opening_the_next_batch`:

### P1 — "next_action superseded in `ledger/goals/GOAL-MLDSA-001.yaml`, preserving exactly one next action"

**SATISFIED ON CONTENT.** The discharged directive ("Run TASK-20260805-a1c3f9",
plus four downstream directives that are now completed, cancelled, or name record
ids that were never minted) is superseded. Exactly **one** `next_action` remains,
and it carries the standing no-new-batch hold from `DEC-20260805-79d745` inside
it rather than dropping it. The prior supersession note
(`next_action_superseded`) is preserved verbatim and unedited; the new one is
recorded alongside it in `next_action_history`, this repository's own pattern for
repeat supersession.

### P2 — "the three defective BATCH-001 entries dispositioned in the committed queue so no renderer presents them as READY"

**SATISFIED ON CONTENT, AND WIDER THAN ASKED.** All **four** downstream entries
are now terminal in `…/BATCH-001/dispatch_queue.json`:

| entry | state | basis |
|---|---|---|
| `TASK-20260805-d47e12` (snapshot) | `cancelled` | unperformable; receipt absent, content already in history, only producible artifact would be a receipt for a commit nobody made |
| `TASK-20260805-5b8a06` (validator) | `completed` | committed `validation_report.yaml` + `DEC-20260805-0d59ff`; state field only |
| `TASK-20260805-9f2d71` (red team) | `completed` | its own completion_gate met by the committed `red_team_report.yaml` / `falsification_review.md`; declared-path mismatch recorded, `artifact_paths` not rewritten |
| `TASK-20260805-c60b84` (ledger) | `cancelled` | the archive it names was performed as `DEC-20260805-0d59ff` / `EV-MLDSA-faf2ec`; dispatching it would duplicate a committed archive under new ids |

`tools/research_dispatch.py` selects only `state == "queued"` tasks as ready
(`_ready_queued`), so **no entry in this queue can be presented as READY** by the
dispatcher. `TASK-20260805-a1c3f9` was already `completed`. The queue has no
remaining `queued` entry at all.

Two things this precondition does **not** now claim: that every declared artifact
exists (9f2d71's does not, by design, and the mismatch is recorded in the entry),
and that the two cancelled cards' work is receipted (it is not — see the residual
below).

### P3 — "current_batch_id resolved by a task that reads the decisions citing BATCH-66b482/BATCH-214d98 … it may NOT be resolved by commit ordering, because git cannot"

**SATISFIED ON CONTENT.** `current_batch_id` moves `BATCH-001` →
**`BATCH-214d98`**, derived from the contents of the five committed
GOAL-MLDSA-001 decisions and nothing else: `DEC-20260805-0d59ff` →
`DEC-20260805-4843d6` → `DEC-20260805-ae4a96` (producer-to-consumer dependency:
BATCH-214d98's experiments are BATCH-66b482's admitted proposals) →
`DEC-20260805-64abe7` (explicit `supersedes:` field) → `DEC-20260805-79d745`
(explicit "BATCH-005 substitute … existing BATCH-214d98 closure", answering
64abe7's own next action). **No commit ordering, no self-declared date and no
directory listing was used**, and this session had no shell with which to use
one. The full derivation is in `change_log.md` item (e).

---

## Why "on content" is not "discharged"

AGENTS.md rule 7 and the Coordinator contract: a ledger record is not official
until it is committed and the dispatcher's post-commit verifier accepts the
commit, and a record that exists only in a local commit is unpublished rather
than durable. The gate's own wording is "dispositioned **in the committed
queue**". This task wrote two files and committed nothing — that is its
instruction, and it is also the correct division of labour, since the session
driving this role runs the git commands.

**Exactly what must happen for the gate to become DISCHARGED:**

1. Commit these two declared paths, and only these, as an isolated ledger archive:
   - `ledger/goals/GOAL-MLDSA-001.yaml`
   - `coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/dispatch_queue.json`
   (plus this task's two deliverables under
   `coordination/reconciliation/RECON-20260810-002/tasks/TASK-20260810-e45e48/`).
2. Merge `origin/main` into `claude/goal-head-reconciliation-20260810` first —
   merge, never rebase — and re-run `tools/validate_ledger.py` on the merged tree.
3. **Run `tools/validate_ledger.py` and `tools/research_dispatch.py` against both
   edited files.** Neither was run here (no shell). Both files were written to
   the schemas as read — `state` values drawn from the legal set
   `{queued, running, blocked, completed, failed, invalid, cancelled}`, no
   required field removed, `cancelled` chosen precisely because a *completed*
   archive task would require an `archive.commit_sha` and a complete
   `path_sha256` that no one may reconstruct — but **written-to-schema is not
   validated**.
4. Push the branch and open or refresh a PR against `main` naming
   `GOAL-MLDSA-001` and `TASK-20260810-e45e48`.
5. Have the post-commit verifier accept the commit.

If step 3 or step 5 fails, the gate **stays standing** and the defect comes back
here, not into a decision record.

---

## What still stands after the gate is discharged

**1. The research hold — this is the operative blocker.** `DEC-20260805-79d745`:
Lane A deferred, ePrint 2023/246 PDF unavailable (HTTP 403 across four recorded
routes), "**No new batch authorized under this constraint**". Under AGENTS.md
rule 5 that blocker is infrastructure and is **never** negative evidence about
the CMA-to-NMA tightness loss; `H-MLDSA-d1e509` stays `inconclusive` on those
grounds and on the unverified-formula anomaly (`DEC-20260805-ae4a96` ANO-3).
The next batch opens when, and only when, full-text access exists — that
condition is `DEC-20260805-79d745`'s own, quoted forward into the goal's
`next_action`, not granted or widened by this task.

**2. A standing archive-chain defect, recorded and deliberately not converted
into a new gate.** BATCH-001 has **no snapshot receipt and no ledger receipt**,
and no post-commit verification is recorded for either archive; its ledger act
was performed under `DEC-20260805-0d59ff` / `EV-MLDSA-faf2ec` rather than the
declared `EV-MLDSA-7e91a4` / `DEC-20260805-3d5f82`. This is **not** one of the
dcfaee gate's preconditions and this ruling does not promote it into one —
inventing a fourth precondition after the first three were met would be changing
the criteria after observing the outcome. It is recorded as an open defect for
the goal's driver to weigh, and it must never be "fixed" by writing a receipt for
a commit nobody in this program made.

**3. Everything RECON-20260810-001 left open elsewhere.** Six other goal heads,
the M1/M2 sibling split, the third c64cf0 anomaly, and the 282 queued entries in
other goals are untouched. This ruling is scoped to GOAL-MLDSA-001 and to
BATCH-001's five queue entries.

---

## One-line answer

**The dcfaee gate is DISCHARGED ON CONTENT and becomes DISCHARGED IN FORCE on a
verified commit of `ledger/goals/GOAL-MLDSA-001.yaml` and
`…/BATCH-001/dispatch_queue.json`; even then GOAL-MLDSA-001's next batch does not
open, because `DEC-20260805-79d745`'s no-new-batch hold is a separate blocker
that this coordination act does not touch.**
