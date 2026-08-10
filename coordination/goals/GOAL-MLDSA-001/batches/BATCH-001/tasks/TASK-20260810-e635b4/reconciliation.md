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

## 0. This memo was corrected mid-task. Read this first.

A first pass of this reconciliation dispositioned `TASK-20260805-d47e12` as
`cancelled` — "never ran, no receipt, do not backfill" — and flagged, as its
own open item, that two committed records cite snapshot commits which the
supplied git facts did not confirm. **That flag resolved against the first
pass.** The dispatching session ran the checks the memo asked for and found
that the snapshot card *did* run (§3.1). It also identified the cause of the
error: its `supplied_git_facts` had been collected with `git log -- <path>`,
which missed the relevant commit. Nothing had been committed at that point, so
this is a corrected draft rather than a superseded record; the superseded-record
route would have applied had the first pass reached a commit.

Two things are worth stating plainly rather than quietly fixing.

1. **The independent validator was right and this memo's first pass was
   wrong.** `reviews/TASK-20260805-5b8a06/validation_report.yaml`
   (`checks[CHK-1].git_reachability`) reported on 2026-08-05 that it had seen a
   reachable commit whose message names the snapshot card. The first pass could
   not confirm that against its inputs and said so; it was correct to record the
   doubt at that scope, and correct not to transcribe a sha it had not observed.
   But the doubt resolved in the validator's favour, and an independent reviewer
   that got it right deserves the record to say so.
2. **The verification method that survived is content, not commit identity.**
   The first pass's methodological instinct — never write a hash you did not
   observe — was right and produced no fabricated value. Its factual conclusion
   was wrong because it treated the absence of a path in one `git log` query as
   evidence of absence. Absence of a query result is not evidence of absence;
   that is the same rule the knowledge-retrieval policy states, applied to git.

## 1. Evidence basis, and what this task could not do

The Coordinator role has no shell under this runtime
(`orchestration/roles.yaml`), which is why `TASK-20260807-dcfaee` stopped where
it did and correctly refused to reconstruct hashes it could not read. The
dispatching session ran git on this task's behalf, in two rounds.

**Round 1 (`handoff.supplied_git_facts`, `git log --format=%H` per path,
repository head `4a309e15`).** Used here for two commits, cited in prose only:
`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/tasks/TASK-20260805-a1c3f9`
introduced by `65ce43f0045d31427382314440bfd76f51ca22a3` (2026-08-05) and last
changed by `10f58126933ee6aee1e134edd92607dcc53564b3` (2026-08-07); both review
directories last changed by `65ce43f0045d31427382314440bfd76f51ca22a3`. **This
round is known to be incomplete** — see round 2 — so nothing in it is treated
as evidence of absence.

**Round 2 (correction, 2026-08-10).** Commit
`f44ffbad97856fc9170f89ce8684639427f1e1be`, message
`snapshot(TASK-20260805-d47e12): GOAL-MLDSA-001 BATCH-001 lit-acquisition — 5
proposed KN-LIT, FIPS-204 distinct from KN-LIT-056`, reachable from HEAD and
from `origin/main`; no parent (root commit); 30,305 files and 13,784,338
insertions; `git rev-list --max-parents=0 HEAD` returns 16 root commits. Plus
six sha256 content hashes, each identical between the root-commit blob and
today's working tree, recorded in §3.1 and in the queue entry itself.

**No hash appears in this task's output that was not observed and supplied by
that session.** Where a field could not be filled from observed values it is
left `null` or `{}` with the reason stated in place. In particular, the
pre-import snapshot sha recorded inside `EV-MLDSA-faf2ec` and the validation
report was never transcribed, before or after the correction: it is now known
not to resolve (§3.1), so copying it forward would have propagated a dead
binding.

## 2. What was stale

`ledger/goals/GOAL-MLDSA-001.yaml` still read:

> BATCH-001 is queued and dispatch-ready ... Run TASK-20260805-a1c3f9

with `current_batch_id: BATCH-001`. Against the committed ledger that is three
batches stale:

1. `TASK-20260805-a1c3f9` is complete — its `receipt.yaml` records
   `status: complete`, `completed_at: "2026-08-05"`, six written deliverables.
2. Both required independent reviews are committed with verdicts:
   `reviews/TASK-20260805-5b8a06/validation_report.yaml` →
   `accept_with_qualifications`;
   `reviews/TASK-20260805-9f2d71/red_team_report.yaml` →
   `pass_with_constraints`.
3. `ledger/decisions/DEC-20260805-0d59ff.yaml`
   (`advance_with_filed_entries`, `evidence_refs: [EV-MLDSA-faf2ec]`) already
   closed BATCH-001 and promoted five KN-LIT entries.
4. The goal then ran BATCH-66b482 (`DEC-20260805-4843d6`) and BATCH-214d98
   (`DEC-20260805-ae4a96` `refine`, superseded on its ANO-1 blocker by
   `DEC-20260805-64abe7`).

The cost was operational, not cosmetic. Because BATCH-001's queue still carried
`TASK-20260805-d47e12` at `"state": "queued"` with its only dependency now
`completed`, `_ready_queued` in `tools/research_dispatch.py` selected it: the
rendered plan offered, as this goal's ready task, a snapshot archive of
artifacts that are already committed and already cited by a committed decision.
The correction in §0 sharpens this rather than softening it — that snapshot had
**already run once**, so dispatching it would have produced a second archive
receipt for the same artifacts. Removing the phantom is the point of this task.

## 3. Changes to `.../BATCH-001/dispatch_queue.json` (four entries)

Only the `state` and `archive` fields of the four named entries were touched.
No `artifact_paths`, `write_scope`, `read_scope`, `handoff`, `depends_on`,
`priority`, or `title` changed anywhere in the file, and the
`TASK-20260805-a1c3f9` entry (set to `completed` by `TASK-20260807-dcfaee`) was
not touched.

| entry | state | archive fields | basis |
| --- | --- | --- | --- |
| `TASK-20260805-d47e12` (snapshot) | `queued` → **`invalid`** | hashes stay `null`/`{}`; `reconciliation` block carries the carrier commit, six content hashes, and the vindication note | §3.1 |
| `TASK-20260805-5b8a06` (validator) | `queued` → **`completed`** | none — no `archive` field | report committed, `accept_with_qualifications`, cited by `EV-MLDSA-faf2ec.validator_verdict` |
| `TASK-20260805-9f2d71` (red team) | `queued` → **`completed`** | none — no `archive` field | report committed, `pass_with_constraints`, cited by `EV-MLDSA-faf2ec.red_team_verdict`; its constraints are ruled on in `DEC-20260805-0d59ff.red_team_gates_resolved` |
| `TASK-20260805-c60b84` (ledger) | `queued` → **`invalid`** | hashes stay `null`/`{}`; `record_ids` unchanged; `reconciliation` block names the records that actually carry the work | §3.2 |

Net effect: all five entries are terminal, so a regenerated dispatch plan for
BATCH-001 offers zero ready tasks and the phantom is gone.

### 3.1 `TASK-20260805-d47e12`: ran, content-verified, commit identity destroyed

The card ran. `f44ffbad97856fc9170f89ce8684639427f1e1be` carries its snapshot
commit message and is reachable from HEAD and `origin/main`.

It is **not** a scoped archive commit, and `f44ffbad` is deliberately not
written into `archive.commit_sha`. It is a root commit with no parent that
changes the entire repository (30,305 files, 13,784,338 insertions) — a bulk
import that inherited the then-current snapshot's commit message. The declared
completion gate ("has the declared parent"; "changes exactly the declared
paths, no more and no fewer") is unsatisfiable by it and always will be. The
pre-import object the validator actually measured — with a parent and six
changed files — no longer exists under the sha it recorded.

What survives is content, and it verifies cleanly. All six producer artifacts
are byte-identical between the root-commit blob and today's working tree:

| file (under `.../BATCH-001/tasks/TASK-20260805-a1c3f9/`) | sha256 |
| --- | --- |
| `corpus_dedup_report.md` | `db8c187b11ac72b8d6d666864122d789b6e6060b777846e1c80eaeac45fbae90` |
| `fault_literature_summary.md` | `0365c0d332d92de1cfd13daf46118dd9a989dd5796593017381bfd1d09bb4d5c` |
| `fips204_transcription.md` | `5dd2a35aebf0d4db35322ddcc9cc3e3ee85f1756b7223b4a9979f795c1814c5f` |
| `proposed_kn_lit_entries.md` | `ea764001a8957117a2e75917e1a75ffc8dd01d2702cf9ca74176f450f1e66f98` |
| `receipt.yaml` | `1d64ab9a08cef86155d12e95a63074d715a22c1cf2b65aa017983e137cdc7f75` |
| `source_access_log.yaml` | `58a27520d003f352a13f39f973d2c46d75dc8c42cba56ebb4cbb1dd890cf53f7` |

This is the disposition CLAUDE.md prescribes: "Archive receipts bind to CONTENT
first ... when a commit cannot be reached it verifies the declared hashes
against the tree and reports the archive as content-verified." Content-verified;
scoped-commit identity unrecoverable.

**Why `invalid` and not something else.** The terminal set in
`crypto.autoresearch.dispatch_queue.v1` is
`{completed, failed, invalid, cancelled}`. `cancelled` means "will not run" and
is now known to be false. `failed` is false — nothing failed in execution.
`queued` would re-offer the phantom. `completed` is unavailable on both honest
and mechanical grounds: the declared archive artifact
(`archives/TASK-20260805-d47e12/snapshot-receipt.json`) does not exist,
`tools/research_dispatch.py` requires a completed archive task to carry a
non-null `commit_sha` and a `path_sha256` covering every archive **and** source
artifact, and the only available commit cannot satisfy the declared gate. So
`invalid` is the least-wrong of four imperfect options, and it is qualified
precisely in the entry: it classifies the **archive receipt** as unverifiable.
It says nothing against the artifacts, which are content-verified above, and
nothing against the producer's findings, which stand on `EV-MLDSA-faf2ec` and
`DEC-20260805-0d59ff`. Under AGENTS.md core rule 5 a receipt-integrity failure
is never negative evidence about ML-DSA or about anything this batch found.

The six hashes are recorded in the entry's `reconciliation` block rather than in
`archive.path_sha256`, because `path_sha256` is the hash binding of a scoped
archive receipt and no such receipt exists — and because `receipt.yaml` is
outside this archive's declared artifact-path set, so a partial copy there
would be both incomplete and misleading.

On the receipt: its absence from the working tree is directly observed. The
first pass's stronger claim that it never existed "in history" came from the
same incomplete collection method and is **not** independently confirmed; this
memo makes no claim about whether `f44ffbad` carries an `archives/` directory.

### 3.2 `TASK-20260805-c60b84`: ran in substance, unverified commit, `record_ids` left alone

The dispatching session did not verify a commit for this card and said so, so
the disposition was re-derived from record content, which is what binds first.

- The card **as declared** did not run. Neither
  `ledger/evidence/EV-MLDSA-7e91a4.yaml` nor
  `ledger/decisions/DEC-20260805-3d5f82.yaml` exists anywhere in the
  repository — a repository-wide content search finds those two ids only in
  this queue and in the goal's now-superseded `next_action` text — and no
  `archives/TASK-20260805-c60b84/ledger-receipt.json` exists in the tree. That
  is a content observation and is unaffected by the git-collection error.
- A ledger-archive act **attributable to this card** nevertheless occurred:
  `EV-MLDSA-faf2ec` records `recorded_by_task: TASK-20260805-c60b84`, and
  `DEC-20260805-0d59ff` is committed — only a ledger archive commits a decision.

`cancelled` therefore became untenable here for a second reason beyond the
first pass's error: it asserts "will not run", and something did run. `invalid`
is used with the same qualification as §3.1 — the archive receipt is
unverifiable; the ledger records that carry the work are committed and stand on
their own.

`record_ids` was **not** rewritten to the real ids.
`_validate_ledger_archive` in `tools/research_dispatch.py` requires every
`ledger/evidence/` and `ledger/decisions/` artifact path to be named by some id
in `record_ids`; `artifact_paths` still names the two never-created records and
is outside this task's write scope, so replacing the ids would break queue
validation. They are retained as declared-but-never-created targets, which the
`reconciliation` block states explicitly.

## 4. Changes to `ledger/goals/GOAL-MLDSA-001.yaml` (goal head only)

| field | from → to | basis |
| --- | --- | --- |
| `current_batch_id` | `BATCH-001` → `BATCH-214d98` | `DEC-20260805-ae4a96` and `DEC-20260805-64abe7` both carry `batch_id: BATCH-214d98` and are the newest committed decisions for this goal |
| `dispatch_queue_path` | `.../BATCH-001/dispatch_queue.json` → `null` | BATCH-214d98 has no committed `dispatch_queue.json` (nor does BATCH-66b482), and BATCH-001's queue is now fully terminal; keeping the old path under a different `current_batch_id` would re-create the stale pointer |
| `next_action` | BATCH-001 dispatch-ready text | one action, §4.1 |
| `next_action_superseded_2` | absent → new block with verbatim `prior_text`, `reason`, `superseded_at`, `superseded_by_task` | prior text preserved, not overwritten |
| `updated_at` | `2026-08-05` → `2026-08-10` | date of this reconciliation |

Deliberately not changed: `status` (`active`), `completion_criteria`,
`pause_conditions`, `campaign_budget`, `question_ids`, `active_hypothesis_ids`
(§5.1), `latest_verified_commit` (stays `null` — see §5.2 for why the
correction does not change that), and the existing `next_action_superseded`
block, which records the earlier 2026-07-29 → 2026-08-05 supersession and is
left byte-identical.

**On the field name `next_action_superseded_2`.** `next_action_superseded` is a
local extension used only by this goal record, and it was already occupied.
Overwriting it would have destroyed the earlier supersession's `prior_text`,
which this program's convention forbids ("The goal's next_action is superseded,
not overwritten" — `TASK-20260805-c60b84`'s constraints). A numbered sibling
preserves both, and `GOAL_REQUIRED` in `tools/validate_ledger.py` is a subset
check, so the extra key validates. The clean long-term fix is
`tools/shard_goal.py`, which gives each batch a write-once checkpoint; that
conversion is outside this write scope and is left as a recommendation.

### 4.1 The one next action, re-verified after the correction

Exactly one `next_action` is set. Its substance was re-checked against the
correction and **did not move**: what the goal should do next is determined by
`DEC-20260805-64abe7`'s carried next actions and by `TASK-20260807-dcfaee`'s
open corpus items, and neither depends on whether BATCH-001's snapshot card ran.
In summary — open the campaign's fourth batch (id minted by the dispatching
session with `tools/allocate_id.py`, **not** minted here) to (a) obtain the full
text of ePrint 2023/246, the corrected KN-LIT-3907 identifier established in
`DEC-20260805-64abe7`, read its adversary-model definition so the
abstract-level Lane B determination in `EV-MLDSA-32d752` can be confirmed or
narrowed, and extract the tightness factor `EXP-MLDSA-3f7ab2` needs; and (b)
carry the three open corpus items (KN-LIT-4f3b80 title discrepancy,
KN-LIT-4dadec `partial → read` upgrade, Kosuge & Xagawa ePrint 2025/904)
through a full producer → snapshot → validator → red team → ledger chain.

Two clauses **did** change:

- the two archive cards are now described as terminal at `invalid` and
  not to be revived or re-run, rather than as cancelled;
- the dispatch precondition dropped from two items to one. The
  hypothesis-status divergence (§5.1) still gates the batch. The
  snapshot-commit item is resolved and explicitly recorded as **not** a
  precondition: what remains of it is a repository-level receipt-integrity
  matter (§5.2) that affects the whole program and gates nothing here.

Budget note for the dispatcher, not a record change: `campaign_budget` allows
six batches and three are consumed. Nothing observed here triggers the
`budget_risk_note` amendment clause, and no amendment is recorded.

## 5. What remains UNRECONCILED

### 5.1 `DEC-20260805-64abe7`'s hypothesis status changes were never applied — and name a status outside the vocabulary

`DEC-20260805-64abe7.hypothesis_status_changes` records
`H-MLDSA-f3a291: supported_scoped` and `H-MLDSA-c7b4e8: supported_scoped`;
`DEC-20260805-ae4a96` earlier recorded `indeterminate` for those two and
`inconclusive` for `H-MLDSA-d1e509`. All three hypothesis records still read
`status: specified`.

Two distinct problems: the transitions were never written to the hypothesis
records, and `supported_scoped` and `indeterminate` are not in AGENTS.md's
vocabulary (`proposed → specified → approved → running → analyzed → replicated →
supported | weakened | rejected | inconclusive | superseded`).

Not touched here: `ledger/hypotheses/` is outside this write scope; changing a
hypothesis status is a research-state transition this task is forbidden to make;
and choosing the in-vocabulary status these results warrant is a judgement on
`EV-MLDSA-32d752` (`strength: moderate`, `determination_basis: abstract_level`),
not bookkeeping. It is the one precondition carried in the new `next_action`.
It is also why `active_hypothesis_ids: []` was left unchanged — whether those
three are "active" is downstream of this question.

### 5.2 Repository-level: 16 root commits, and every pre-import archive receipt

This is the general form of the §3.1 finding and it is worth stating plainly
because it reaches far beyond this goal.

`git rev-list --max-parents=0 HEAD` returns **16 root commits**. This repository
has been bulk-imported repeatedly, and each import replaces history: recorded
shas become unreachable and recorded parents become wrong. CLAUDE.md already
documents the mechanism and its consequence for squash merges
(`CORR-20260802-a1f151`, five goals with unresolvable
`latest_verified_commit`). What §3.1 demonstrates is that the same damage was
done wholesale by the imports, not only by merge strategy.

The consequence, stated at its true scope: **any archive receipt in this
repository predating the last import has the same broken commit binding.**
Reachability, declared parent, and exact-paths checks cannot be satisfied for
those receipts by any commit that exists today. Content verification —
`path_sha256` against the tree — is the only binding that survives, which is
exactly why CLAUDE.md makes content primary and reachability advisory.

This memo does not act on that beyond this goal: repository-wide receipt
remediation is not a bookkeeping task, it is not in this write scope, and it
belongs to the harness owners rather than to GOAL-MLDSA-001. It is recorded
here so it is not lost, and it is flagged in the return to the dispatching
session for program-level handling. `latest_verified_commit` on this goal head
stays `null` for the matching reason: no *scoped* ledger-archive commit for this
goal has been verified, and `f44ffbad` is not one.

Concretely open, in ascending cost:

1. Whether any commit names `TASK-20260805-c60b84`
   (`git log --all --format='%H %s' | grep TASK-20260805-c60b84`, then
   `git rev-list --max-parents=0` on any hit). If none exists, §3.2's
   disposition should be revisited by a superseding record, not an edit.
2. Whether other goals' archive receipts are similarly content-verifiable, and
   whether the dispatch plan should report `content_verified` as a first-class
   archive state rather than forcing the choice between `completed` and
   `invalid` that §3.1 had to make.

### 5.3 Smaller divergences, named and left

- **Declared vs. actual review artifact names.** The queue declares
  `reviews/TASK-20260805-9f2d71/red_team_report.md`; what exists is
  `red_team_report.yaml` plus `falsification_review.md`. The review happened and
  its verdict is cited by committed records, so the entry is `completed`; the
  mismatch is in `artifact_paths`, outside this write scope.
- **BATCH-66b482 and BATCH-214d98 have no committed `batch.yaml` or
  `dispatch_queue.json`.** Both contain only `tasks/` (and, for BATCH-66b482,
  `reviews/`). Out of scope here; it is why `dispatch_queue_path` is `null`
  rather than repointed.
- **`DEC-20260805-0d59ff` gate 2 / KN-LIT-4f3b80.** `TASK-20260807-dcfaee`
  §2(d)/(e) flagged a title-field discrepancy in the filed `KN-LIT-4f3b80` and
  declined to relitigate gate 2 on it. Unchanged here for the same reasons
  (`knowledge/` is outside this write scope; adjudicating gate 2 is a
  research-state judgement). It is carried into the new `next_action` as a
  `/curate-knowledge` item.

## 6. Identifiers

No `TASK-*`, `BATCH-*`, `EV-*`, `DEC-*`, or `KN-*` identifier was minted here.
The next batch is referred to by its exact intended form, `BATCH-<6-hex>`, to be
minted by the dispatching session with
`python3 tools/allocate_id.py --next batch` and `--check`ed before use
(AGENTS.md rule 14); its task cards likewise with
`--next task --date <YYYYMMDD>`.

## 7. Why no `coordinator_decision` accompanies this memo

Nothing here is a research-state judgement. No hypothesis status, evidence
strength, claim tier, knowledge entry, goal status, completion criterion, or
pause condition changed; the goal's `next_action` was replaced with the action
committed decisions already directed, and four queue entries were matched to
observable facts. The two items that *would* require a decision — §5.1's
hypothesis statuses and §5.2's program-wide receipt integrity — are precisely
the two this memo refuses to settle, and §5.1 is named as a precondition in the
new `next_action`.
