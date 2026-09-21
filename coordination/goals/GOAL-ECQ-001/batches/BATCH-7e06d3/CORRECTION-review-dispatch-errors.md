# Corrections: three orchestration errors in the BATCH-7e06d3 review round

All three were found by the **validator**, not by the orchestrating session that
made them. Recorded before the ledger archive so the archive cites reality.

## CI-1 — the validator was dispatched under the WRONG TASK IDENTIFIER

I dispatched it as `TASK-20260822-0de988`. That identifier belongs to
**BATCH-e0caa5**, the review task of the *paused* GOAL-ECRANK-002. The committed
validator task for **BATCH-7e06d3** is `TASK-20260822-0a0041`. Verified:

| identifier | owning queue | role |
|---|---|---|
| `TASK-20260822-0de988` | BATCH-e0caa5 (paused goal) | validator |
| `TASK-20260822-0a0041` | **BATCH-7e06d3 (this batch)** | validator |
| `TASK-20260822-53748a` | BATCH-7e06d3 | red team — dispatched correctly |

**What is and is not affected.** The WORK is correct: the joints, the control
set and the blind re-derivation were pasted into the prompt from BATCH-7e06d3's
review plan, and the validator independently confirmed its joints match
`TASK-20260822-0a0041`'s plan. What is wrong is the LABEL and therefore the
filing path: the report sits at
`.../BATCH-7e06d3/tasks/TASK-20260822-0de988/validation_report.yaml`.

**Consequence the validator names:** `check_review_independence.py` would compose
this review against the wrong plan. The ledger archive MUST cite the report at
its actual path while recording that the review discharging
`TASK-20260822-0a0041` was executed under the identifier `TASK-20260822-0de988`.
The file is NOT moved: it is committed, and renaming a committed artifact to hide
a dispatch error is the overwrite habit this program already paid for once.
`TASK-20260822-0de988` in BATCH-e0caa5 remains undischarged; the paused goal
still owes it.

## BI-1 — a partial blindness break, caused by my commit messages

The validator disclosed that a routine `git status` / `git log` exposed the red
team's **commit subject and body**, which summarise its joints 3–4 findings. It
never opened the red team's report.

The cause is mine: I wrote long commit messages summarising one reviewer's
findings *while the other reviewer was still working in the same worktree*.
Mutual blindness was enforced on what each agent was told to READ, and then
leaked through the commit log, which every agent sees for free.

The ordering is **checkable rather than asserted**: the copy of the validator's
own file inside that very commit already carries `verdict: passed`, so its
verdicts predate the exposure. Recorded as a real if partial break, not waved
away.

**Reusable rule:** while a blind review round is live, commit messages must
describe *that* an artifact landed, never *what it found*.

## CI-5 — a reviewer's in-progress deliverable was committed by another process

Twice, once bundled into the red team's return commit. Already disclosed in
`b8c544fc`. The validator notes this is the **third** occurrence of the
orchestration-layer pattern the snapshot receipt records, and the **first to
touch a reviewer** rather than a producer. Subsequent commits stage by explicit
path instead of `git add -A`.
