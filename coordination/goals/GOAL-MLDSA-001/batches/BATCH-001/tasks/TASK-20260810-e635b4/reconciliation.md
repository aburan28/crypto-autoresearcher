# Goal-head and BATCH-001 queue reconciliation — TASK-20260810-e635b4

Bookkeeping only. This memo creates no hypothesis, designs no experiment, files
no knowledge entry, and makes no assessment of ML-DSA, MLWE, MSIS, or
SelfTargetMSIS in either direction. It changes no research status:
`GOAL-MLDSA-001.status` stays `active`, `completion_criteria` and
`pause_conditions` are untouched, and no hypothesis, evidence, or decision
record was created, edited, renamed, or superseded.

It is the dedicated task that `TASK-20260807-dcfaee`'s memo recommended twice
(§1, "a dedicated bookkeeping task with git access should reconcile all four
remaining entries"; and "flagged for a dedicated goal-head reconciliation
task ... before GOAL-MLDSA-001's next batch is opened"), following the
`TASK-20260807-48b8f2` precedent for the same failure mode on GOAL-ECDLP-001.

## 0. Evidence basis, and the one thing this task could not do

The Coordinator role has no shell under this runtime
(`orchestration/roles.yaml`), which is exactly why `TASK-20260807-dcfaee`
stopped where it did and correctly refused to reconstruct hashes it could not
read. The orchestrating session ran `git log --format=%H` per path and supplied
the results in `ledger/handoffs/TASK-20260810-e635b4.yaml`
(`handoff.supplied_git_facts`, collected 2026-08-10 at repository head
`4a309e15`). Two commit shas from that block are used in this reconciliation:

| path | commit used | as |
| --- | --- | --- |
| `.../BATCH-001/tasks/TASK-20260805-a1c3f9` | `65ce43f0045d31427382314440bfd76f51ca22a3` (2026-08-05) | introduced |
| `.../BATCH-001/tasks/TASK-20260805-a1c3f9` | `10f58126933ee6aee1e134edd92607dcc53564b3` (2026-08-07) | last changed |

Both review paths (`reviews/TASK-20260805-5b8a06`,
`reviews/TASK-20260805-9f2d71`) are recorded there as last changed by
`65ce43f0045d31427382314440bfd76f51ca22a3` (2026-08-05); those shas are cited in
the memo but were not written into any record.

**No other commit sha, parent sha, or path hash appears anywhere in this task's
output.** Where a field could not be filled from the supplied facts, it is left
`null` or `{}` and the reason is stated in place. Two committed records do carry
snapshot-commit shas that are *not* in the supplied facts; §4.2 explains why
this task deliberately did not transcribe, verify, or reuse them.

## 1. What was stale

`ledger/goals/GOAL-MLDSA-001.yaml` still read:

> BATCH-001 is queued and dispatch-ready ... Run TASK-20260805-a1c3f9

with `current_batch_id: BATCH-001`. Against the committed ledger that is three
batches stale:

1. `TASK-20260805-a1c3f9` is complete —
   `.../tasks/TASK-20260805-a1c3f9/receipt.yaml` records `status: complete`,
   `completed_at: "2026-08-05"`, and six written deliverables. The producer
   directory is committed (`65ce43f0...`, last changed `10f58126...`).
2. Both required independent reviews are committed with verdicts:
   `reviews/TASK-20260805-5b8a06/validation_report.yaml` →
   `verdict: accept_with_qualifications`;
   `reviews/TASK-20260805-9f2d71/red_team_report.yaml` →
   `verdict: pass_with_constraints`.
3. `ledger/decisions/DEC-20260805-0d59ff.yaml`
   (`decision: advance_with_filed_entries`, `evidence_refs: [EV-MLDSA-faf2ec]`)
   already closed BATCH-001 and promoted five KN-LIT entries.
4. The goal then ran two further batches on 2026-08-05: BATCH-66b482
   (`DEC-20260805-4843d6`, ideation admitted with screening) and BATCH-214d98
   (`DEC-20260805-ae4a96` `refine`, superseded on its ANO-1 blocker by
   `DEC-20260805-64abe7`).

The operational cost of the staleness was concrete, not cosmetic. Because
BATCH-001's queue still carried `TASK-20260805-d47e12` at `"state": "queued"`
with its only dependency now `completed`, `tools/research_dispatch.py`'s
`_ready_queued` selected it: the rendered plan offered, as the goal's ready
task, a **snapshot archive of artifacts that are already committed and already
cited by a committed decision**. Dispatching it would have manufactured an
archive receipt for work already archived. Removing that phantom is the
point of this task.

## 2. Changes to `ledger/goals/GOAL-MLDSA-001.yaml` (goal head only)

| field | from | to | basis |
| --- | --- | --- | --- |
| `current_batch_id` | `BATCH-001` | `BATCH-214d98` | `DEC-20260805-ae4a96` and `DEC-20260805-64abe7` both carry `batch_id: BATCH-214d98` and are the newest committed decisions for this goal; `DEC-20260805-4843d6` (BATCH-66b482) precedes them |
| `dispatch_queue_path` | `.../BATCH-001/dispatch_queue.json` | `null` | BATCH-214d98 has no committed `dispatch_queue.json` (nor does BATCH-66b482 — neither directory contains one), and BATCH-001's queue is now fully terminal. Leaving the old path while `current_batch_id` names a different batch would re-create the stale pointer this task exists to remove |
| `next_action` | BATCH-001 dispatch-ready text (see below) | one action, quoted in §2.1 | `DEC-20260805-64abe7.next_actions` (the newest, superseding decision) plus the two open corpus items from `TASK-20260807-dcfaee` §2 |
| `next_action_superseded_2` | absent | new block: `prior_text` (verbatim), `reason`, `superseded_at`, `superseded_by_task` | the prior text is preserved, not overwritten |
| `updated_at` | `2026-08-05` | `2026-08-10` | date of this reconciliation |

Deliberately **not** changed: `status` (`active`), `completion_criteria`,
`pause_conditions`, `campaign_budget`, `question_ids`, `active_hypothesis_ids`
(see §4.1), `latest_verified_commit` (stays `null`; see §4.2), and the existing
`next_action_superseded` block, which records the earlier 2026-07-29 → 2026-08-05
supersession and is left byte-identical.

**On the field name `next_action_superseded_2`.** `next_action_superseded` is a
local extension used only by this goal record; it is a single block and was
already occupied. Overwriting it would have destroyed the earlier supersession's
`prior_text`, which the program's own convention forbids ("The goal's
next_action is superseded, not overwritten" — `TASK-20260805-c60b84`'s
constraints). A numbered sibling preserves both, and the goal template's
required-field check (`GOAL_REQUIRED` in `tools/validate_ledger.py`) is a subset
check, so the extra key validates. The clean long-term fix is
`tools/shard_goal.py`, which converts this goal to
`ledger/goals/GOAL-MLDSA-001/{goal.yaml,checkpoints/*.yaml}` and gives each
batch its own write-once checkpoint; that conversion is outside this task's
write scope and is left as a recommendation.

### 2.1 The one next action

Exactly one `next_action` is set. In summary (the record carries the full
text): open the campaign's fourth batch — id minted by the dispatching session
with `tools/allocate_id.py`, **not** minted here — to (a) obtain the full text
of ePrint 2023/246, the corrected KN-LIT-3907 identifier established in
`DEC-20260805-64abe7`, read its adversary-model definition so the
abstract-level Lane B determination in `EV-MLDSA-32d752` can be confirmed or
narrowed, and extract the tightness factor `EXP-MLDSA-3f7ab2` needs; and (b)
carry `TASK-20260807-dcfaee`'s three open corpus items (KN-LIT-4f3b80 title
discrepancy, KN-LIT-4dadec `partial → read` upgrade, Kosuge & Xagawa ePrint
2025/904) through a full producer → snapshot → validator → red team → ledger
chain. It states as a precondition that the two divergences in §4.1–4.2 be
settled first, since both need a Coordinator judgement rather than bookkeeping.

Budget note, for the dispatcher rather than for this record: `campaign_budget`
allows six batches and three are consumed (BATCH-001, BATCH-66b482,
BATCH-214d98). The `budget_risk_note` clause requiring an explicit amendment if
BATCH-001 overran is not triggered by anything this task observed, and no
amendment is recorded here.

## 3. Changes to `.../BATCH-001/dispatch_queue.json` (four entries)

Only the `state` and `archive` fields of the four named entries were touched.
No `artifact_paths`, `write_scope`, `read_scope`, `handoff`, `depends_on`,
`priority`, or `title` changed anywhere in the file, and the
`TASK-20260805-a1c3f9` entry (already set to `completed` by
`TASK-20260807-dcfaee`) was not touched.

| entry | state | archive fields | basis |
| --- | --- | --- | --- |
| `TASK-20260805-d47e12` (snapshot) | `queued` → `cancelled` | `commit_sha`/`parent_sha` stay `null`, `path_sha256` stays `{}`, `record_ids` stays `[]`; a `reconciliation` block records the true disposition | the archive directory does not exist (§3.1) |
| `TASK-20260805-5b8a06` (validator) | `queued` → `completed` | none — this entry has no `archive` field | `validation_report.yaml` exists and is committed (`65ce43f0...`), `verdict: accept_with_qualifications`, cited by `EV-MLDSA-faf2ec.validator_verdict` and `DEC-20260805-0d59ff.context` |
| `TASK-20260805-9f2d71` (red team) | `queued` → `completed` | none — no `archive` field | `red_team_report.yaml` exists and is committed (`65ce43f0...`), `verdict: pass_with_constraints`, cited by `EV-MLDSA-faf2ec.red_team_verdict`; its three constraints are ruled on in `DEC-20260805-0d59ff.red_team_gates_resolved` |
| `TASK-20260805-c60b84` (ledger) | `queued` → `cancelled` | `commit_sha`/`parent_sha` stay `null`, `path_sha256` stays `{}`, `record_ids` **unchanged**; a `reconciliation` block names the records that actually carry the work | §3.2 |

Net effect: all five entries are terminal, so a regenerated dispatch plan for
BATCH-001 offers zero ready tasks and the phantom is gone.

### 3.1 Why `TASK-20260805-d47e12` is `cancelled` and not `completed`

`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/archives/` does not exist.
Its declared artifact, `archives/TASK-20260805-d47e12/snapshot-receipt.json`,
was never written, and no snapshot-archive commit for this card appears in the
supplied git facts. The producer artifacts it was to freeze are committed
anyway, by the ordinary batch commits `65ce43f0...` (introduced) and
`10f58126...` (last changed).

`completed` is unavailable to it on two independent grounds. Factually, there
is no receipt. Mechanically, `tools/research_dispatch.py` requires a
`completed` archive task to carry a non-null `archive.commit_sha` and a
`path_sha256` covering every archive and source artifact; supplying either
would mean writing hashes this task cannot observe. `cancelled` is the only
terminal state in `crypto.autoresearch.dispatch_queue.v1`
(`{completed, failed, invalid, cancelled}`) that asserts what is true: the card
will not run, and nothing failed. The `archive.reconciliation` block written
into the entry says so in the record itself, so the disposition survives
independently of this memo.

### 3.2 Why `TASK-20260805-c60b84` is `cancelled`, and why its `record_ids` were left alone

This card as declared did not run. Neither `ledger/evidence/EV-MLDSA-7e91a4.yaml`
nor `ledger/decisions/DEC-20260805-3d5f82.yaml` exists anywhere in the
repository — a repository-wide search finds those two ids only in this queue
and in the goal's now-superseded `next_action` text — and no
`archives/TASK-20260805-c60b84/ledger-receipt.json` exists.

The ledger act it planned nevertheless happened, under different ids:
`EV-MLDSA-faf2ec` carries the BATCH-001 evidence and both review verdicts and
records `recorded_by_task: TASK-20260805-c60b84`, and `DEC-20260805-0d59ff`
closed the batch with `knowledge_promotion` for five KN-LIT entries. That is
recorded in the entry's `archive.reconciliation.work_actually_recorded_elsewhere`.

`record_ids` was **not** rewritten to the real ids.
`_validate_ledger_archive` in `tools/research_dispatch.py` requires every
`ledger/evidence/` and `ledger/decisions/` artifact path to be named by some id
in `record_ids`; `artifact_paths` still names the two never-created records and
is outside this task's write scope, so replacing the ids would break queue
validation. They are retained as the declared-but-never-created targets, which
the `reconciliation` block states explicitly so they cannot be misread as
assertions that those records exist.

## 4. What remains UNRECONCILED

These are stated, not fixed. Each needs either a shell or a Coordinator
research-state judgement, and neither is available to a bookkeeping task.

### 4.1 `DEC-20260805-64abe7`'s hypothesis status changes were never applied — and name a status outside the vocabulary

`DEC-20260805-64abe7.hypothesis_status_changes` records
`H-MLDSA-f3a291: supported_scoped` and `H-MLDSA-c7b4e8: supported_scoped`, and
`DEC-20260805-ae4a96` earlier recorded `H-MLDSA-f3a291: indeterminate`,
`H-MLDSA-c7b4e8: indeterminate`, `H-MLDSA-d1e509: inconclusive`. All three
hypothesis records still read `status: specified`
(`ledger/hypotheses/H-MLDSA-{f3a291,c7b4e8,d1e509}.yaml`).

Two distinct problems: the decisions' transitions were never written to the
hypothesis records, and `supported_scoped` and `indeterminate` are not in
AGENTS.md's hypothesis state vocabulary
(`proposed → specified → approved → running → analyzed → replicated →
supported | weakened | rejected | inconclusive | superseded`).

Not touched here, for three reasons: `ledger/hypotheses/` is outside this
task's `write_scope`; changing a hypothesis status is a research-state
transition, which this task is explicitly forbidden to make; and choosing the
in-vocabulary status these results actually warrant is a judgement on the
evidence (`EV-MLDSA-32d752`, `strength: moderate`,
`determination_basis: abstract_level`), not bookkeeping. This is flagged as a
precondition in the new `next_action`. It also affects
`active_hypothesis_ids: []` on the goal head, which is why that field was left
unchanged: whether these three are "active" depends on the status question, and
answering it here would be exactly the research-state change this task must not
make.

### 4.2 Two committed records cite snapshot commits that no supplied git fact confirms

`ledger/evidence/EV-MLDSA-faf2ec.yaml` carries a `snapshot_commit` value, and
`reviews/TASK-20260805-5b8a06/validation_report.yaml` carries the same value in
its `snapshot_commit` field and in `checks[CHK-1].git_reachability`
(`commit`, `parent_commit`, `commit_message`, `files_changed_in_commit: 6`,
`reachable_from_HEAD: true`) — with a commit message quoted there as naming
`snapshot(TASK-20260805-d47e12)`. Separately,
`ledger/evidence/EV-MLDSA-32d752.yaml` carries an abbreviated `snapshot_commit`.

**None of those shas appears in `supplied_git_facts`, so this task neither
verified nor transcribed them.** The values are left where they are, in the
committed records named above, so a session with a shell can read and check
them; they are deliberately not copied into the goal record or the queue.

This is a genuine open question, and it is worth stating plainly rather than
resolving by assumption. The validator's report is an independent
2026-08-05 session claiming it recomputed blob hashes against a reachable
commit whose message names the snapshot card. Read alone, that suggests
`TASK-20260805-d47e12` did produce a commit even though it produced no receipt
and left no `archives/` directory. The supplied facts instead show the producer
directory introduced by `65ce43f0...`. Both can be true — a commit can be
reachable in one branch's history and be reported under a different sha for the
same path elsewhere, and merge or branch topology is precisely what this task
cannot see. What this task can say is bounded and is what it says: no receipt
exists, no supplied fact names a snapshot commit for that card, and therefore
no sha was written. The recommended check is a single
`git log --format='%H %s' --all -- coordination/goals/GOAL-MLDSA-001/batches/BATCH-001`
plus `git cat-file -t <sha>` on the two recorded values. If that commit is
reachable, the honest correction is a superseding record that says so — not an
edit to this one.

`latest_verified_commit` on the goal head stays `null` for the same reason: no
ledger-archive commit for this goal was verified here.

### 4.3 Smaller divergences, named and left

- **Declared vs. actual review artifact names.** The queue declares
  `reviews/TASK-20260805-9f2d71/red_team_report.md`; what exists is
  `red_team_report.yaml` plus `falsification_review.md`. The review demonstrably
  happened and its verdict is cited by committed records, so the entry is
  `completed`; the filename mismatch is in `artifact_paths`, which is outside
  this task's write scope. A future queue correction should reconcile it.
- **BATCH-66b482 and BATCH-214d98 have no committed `batch.yaml` or
  `dispatch_queue.json`.** Both contain only `tasks/` (and, for BATCH-66b482,
  `reviews/`). Those batches ran without a committed queue record. Out of scope
  here; it is why `dispatch_queue_path` is `null` rather than repointed.
- **`DEC-20260805-0d59ff` gate 2 / KN-LIT-4f3b80.** `TASK-20260807-dcfaee` §2(d)/(e)
  flagged a title-field discrepancy in the filed `KN-LIT-4f3b80` and declined to
  relitigate gate 2 on it. Unchanged here, for the same reason: `knowledge/` is
  outside this write scope and adjudicating it is a research-state judgement.
  It is carried into the new `next_action` as a `/curate-knowledge` item.

## 5. Identifiers

No `TASK-*`, `BATCH-*`, `EV-*`, `DEC-*`, or `KN-*` identifier was minted by this
task. The next batch is referred to by its exact intended form,
`BATCH-<6-hex>`, to be minted by the dispatching session with
`python3 tools/allocate_id.py --next batch` and `--check`ed before use
(AGENTS.md rule 14); its task cards likewise with
`--next task --date <YYYYMMDD>`.

## 6. Why no `coordinator_decision` accompanies this memo

Nothing here is a research-state judgement. No hypothesis status, evidence
strength, claim tier, knowledge entry, goal status, completion criterion, or
pause condition changed; the goal's `next_action` was replaced with the action
that committed decisions already directed, and four queue entries were matched
to observable facts. The two items that *would* require a decision — §4.1 and
§4.2 — are precisely the two this memo refuses to settle, and both are named as
preconditions in the new `next_action`.
