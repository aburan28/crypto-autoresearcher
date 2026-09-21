# Method — TASK-20260810-c64cf0 (RECON-20260810-001)

Fact-gathering only. This task changed nothing. Every stale field it describes
was left exactly as found. It writes no ledger record, opens no batch, moves no
goal or hypothesis status, and makes no research claim.

## 0. Repository state the audit was taken at

```
git rev-parse HEAD
bb1c6e479296589819a8f5fbc93e6e2915bc4018
git rev-parse --abbrev-ref HEAD
claude/goal-head-reconciliation-20260810
git status --porcelain
?? coordination/reconciliation/RECON-20260810-001/dispatch_plan.json
?? coordination/reconciliation/RECON-20260810-001/dispatch_plan.md
```

Recorded deviation: at the end of the task, `git status --porcelain
--untracked-files=all` no longer listed those two dispatch-plan files — the only
untracked paths were this task's own three deliverables. Something outside this
session removed or regenerated them mid-task. This task did not touch them.
Noted because it happened, not because it affects any result: no tracked file
was modified at any point (`git status --porcelain --untracked-files=no` is
empty), and no audited path is a dispatch-plan file.

The tracked working tree was clean when the audit began: the only untracked
paths are the two generated dispatch-plan files, which CLAUDE.md declares are
rebuilt on demand and not committed. Therefore, for every tracked path in this
audit, "in the working tree" and "at commit `bb1c6e47…`" are the same thing, and
no dirty-tree caveat is needed for any row.

`inference.policy` requested by the handoff: `executor-implementation`,
`fallback_allowed: false`. Model that actually answered: `claude-opus-5`
(Claude Code runtime, executor subagent). This session honoured the requested
policy; nothing was downgraded.

## 1. Commands actually run

Only read-only git subcommands were used. These are the full set; each is given
an id, and every sha in the two YAML deliverables carries the id of the command
that produced it.

| id | command |
| --- | --- |
| C1 | `git rev-parse HEAD` |
| C2 | `git rev-list --topo-order HEAD` |
| C3 | `git log --diff-filter=A --format='C %H %aI' --name-only -- coordination/goals/<GOAL-ID>/batches` |
| C4 | `git log --format='%H %cI' -S'current_batch_id: <VALUE>' -- <goal record path>` |
| C5 | `git log --diff-filter=A --format='C %H %cI' --name-only -- ledger/decisions` |
| C6 | `git log --diff-filter=A --format='C %H' --name-only -- ledger/goals/<GOAL-ID>/checkpoints` |
| C7 | `git log -1 --format='%H' -- <goal record path>` |
| C8 | `git merge-base --is-ancestor <A> <B>` |
| C9 | `git log --diff-filter=A --format='C %H' --name-only` (repo-wide first-add index, 527782 lines) |
| C10 | `git status --porcelain` |
| C11 | `git ls-files ledger/decisions` |

Non-git reads: `ledger/goals/**` (YAML), `coordination/goals/*/batches/*/dispatch_queue.json`,
`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/tasks/TASK-20260807-dcfaee/reconciliation.md`,
`ledger/handoffs/TASK-20260807-48b8f2.yaml`, `AGENTS.md`, `agents/executor.md`.

**"topo pos N"** in the deliverables means: the 0-based index of that commit in
the output of C2, where 0 is the newest commit. C2 is a topological ordering, so
a smaller index never denotes an ancestor of a larger one. Where a comparison
mattered it was additionally checked with C8.

## 2. What was audited, and how each column was derived

### goal_head_audit.yaml

Scope: all 22 goal records with `research_goal.status: active` (of 69 records in
`ledger/goals/`). One row each — the completion gate. Both goal layouts are
handled: flat `GOAL-X.yaml` and sharded `GOAL-X/{goal.yaml,checkpoints/*.yaml}`.

- `committed_current_batch_id`, `committed_next_action_first_200_chars`,
  `dispatch_queue_path_field` — read from the goal record at `bb1c6e47…`.
- `batch_directories_found` — `os.listdir` of `coordination/goals/<id>/batches`,
  ordered newest-first by each directory's **first-add commit** from C3.
- `batches_cited_by_a_committed_decision` — every file in C11 was read; a batch
  is listed when a decision file contains BOTH the goal id and that batch id AND
  the batch has a directory. All 481 decision files are tracked and the tree is
  clean, so every one of them is committed at `bb1c6e47…`.
- `checkpoint_file_add_commits_newest_first` — C6, for sharded goals only. Flat
  goals carry `batch_checkpoints` inline in the goal record and get the literal
  string `INLINE_batch_checkpoints_in_goal_record__no_separate_files`, because
  git cannot date an inline list element.
- `commit_that_introduced_current_batch_id_value` — C4.
- `goal_record_last_commit` — C7.

### queue_state_audit.yaml

Scope: for each active goal, every `dispatch_queue.json` under
`coordination/goals/<id>/batches/*/`, plus the goal's `dispatch_queue_path` if it
resolves outside that glob. 223 queue files examined; every one parsed as JSON
(zero parse failures) and every one is committed. Each entry still at
`"state": "queued"` is listed: 283 of them.

For each declared `artifact_paths` entry: working-tree existence via `os.path.exists`,
and committedness via the C9 index, which maps every path ever added in history to
the **oldest** commit that added it. A declared path that is a directory is
resolved by finding a committed file beneath it; that file is named in the row and
the sha reported is that file's first-add commit, explicitly not a directory sha.

## 3. Evidence-strength labelling (as the handoff requires)

- **STRONG** — established by a committed decision under `ledger/decisions/`, a
  committed checkpoint record, or a committed dispatch-queue state.
- **MODERATE** — supported by committed artifacts (queue entries at `completed`,
  checkpoint `closed_at` fields, legacy three-digit batch numbering) but *not*
  independently orderable in git, because the relevant files entered history in a
  bulk import commit.
- **WEAK** — directory existence or absence only. Per the handoff: a concurrent
  session can create a batch directory it never uses.

Directory mtime was not used for anything.

## 4. Limitations — read these before using either file

1. **Bulk import commits destroy fine-grained ordering.** Three commits added
   large numbers of batch directories at once: `33e4c62901b482994bcf945a4cdbd98afa8b1d10`
   (88 batch dirs), `9514c07444c3c2bb4bbe1a78d6630c5a086c8f7f` (60), and
   `65ce43f0045d31427382314440bfd76f51ca22a3` (36). Within any one of them git
   cannot say which batch came first. Every verdict that depends on ordering
   inside such a commit is labelled MODERATE or WEAK and says so in its `basis`.
2. **A first attempt at ordering by author date was discarded.** Author dates and
   commit dates disagree on this history (merge-heavy, many concurrent
   worktrees), and ordering by `%aI` produced a different and less defensible
   answer than C2 + C8. Only the topological result is reported. This is recorded
   rather than silently dropped.
3. **"Topologically newer" is not "caused by".** The history is a DAG with
   merges; for several ECDLP-001 comparisons the current-batch commit is not an
   ancestor of the newer batch-directory commits at all (checked with C8) — they
   are siblings merged into `main`. For that goal the verdict does not rest on
   directory order: it rests on the committed checkpoint for the recorded head
   itself, plus eleven topologically newer checkpoint files.
4. **Decision-id dates are self-declared.** `DEC-YYYYMMDD-tok` encodes an
   author's date, not a git fact. Where a decision date is quoted it is quoted as
   the record's own field; the git fact quoted alongside it is the decision file's
   first-add commit from C5/C9.
5. **Citation matching is textual.** A batch counts as "cited by a committed
   decision" when a decision file mentions the goal id and that batch id in the
   same file. That is a co-occurrence, not a parse of decision semantics: a
   decision that merely *mentions* a batch in passing is counted the same as one
   that closes it. This over-counts rather than under-counts, so it can only make
   a HEAD_CURRENT verdict harder to reach, never easier.
6. **`ARTIFACTS_PRESENT` is not `completed`.** It says a still-queued entry's
   declared artifacts already exist in committed history. It says nothing about
   whether the task was discharged, reviewed, or accepted. That judgement is the
   Coordinator's in TASK-20260810-1b82fe.
7. **Four queued entries declare no `artifact_paths`** and are reported as
   `NO_DECLARED_ARTIFACTS`; the presence check is undefined for them.
8. **Nothing about `paused`, `draft`, `completed`, or `closed_at_budget` goals**
   was audited. 47 goal records fall outside the scope the gate sets.

## 5. Queues NOT reached, stated plainly

The budget was sufficient: every queue in scope was reached. 223 of the 269
`dispatch_queue.json` files in the repository were examined — that is all queues
reachable from an active goal's `dispatch_queue_path` or lying in an active
goal's batch directories, with none skipped. The 46 not examined are, by
category, outside the gate's scope:

- queues under non-active goals (`draft`, `paused`, `completed`,
  `closed_at_budget`) — not in scope;
- `coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-IV-20260808/dispatch_queue.json`
  — belongs to an active goal but lies under `proposals/`, not under
  `batches/`, and is not that goal's `dispatch_queue_path`. **Named here because
  it is the one in-goal queue a reader might reasonably expect to be covered and
  is not.**
- `coordination/dispatch_queue.json`,
  `coordination/reconciliation/RECON-20260802-001/dispatch_queue.json`,
  `coordination/reconciliation/RECON-20260810-001/dispatch_queue.json` — campaign
  and root-level queues, not goal batch queues.

Two active goals have no queue at all in their batch directories
(GOAL-ENDO-001, GOAL-AES-002); eleven have no entry still at `queued`. Both
facts are recorded per goal in `coverage_per_goal`.

## 6. Unresolved items

None were left as `UNRESOLVED` in `goal_head_audit.yaml`. Two near-misses are
recorded inside their rows rather than hidden:

- **GOAL-AES-002** has `current_batch_id: null`, so command C4 has no search
  string and `commit_that_introduced_current_batch_id_value` is the literal
  string `UNRESOLVED: current_batch_id is null, so no -S search string exists`.
  The row is still HEAD_STALE, on the separate and sufficient ground that the
  record's own note asserts "No GOAL-AES-002 batch exists" while a BATCH-001
  directory exists and is cited by a committed decision added later than the
  goal record's last commit.
- **GOAL-MLDSA-001** cannot be ordered by git: its three batch directories and
  three of the four relevant decision files all entered history in the single
  bulk commit `9514c07444c3c2bb4bbe1a78d6630c5a086c8f7f`, and the decision that
  cites BATCH-001 was added *later* than the ones citing the other two. Its
  STRONG label therefore rests only on the ordering-free contradiction: the
  `next_action` orders a task to be run that the committed queue records as
  `completed`. The caveat is written into the row's `basis`, not omitted.

## 7. The three already-documented goals

Each was re-derived from git rather than repeated from the prior claim; see the
`basis` field of each row for the exact evidence. All three are confirmed
HEAD_STALE, and the prior work is confirmed correct in substance:

- **GOAL-MLDSA-001** — confirmed (STRONG, on the `next_action`/queue-state
  contradiction; the ordering claim in the prior memo is *not* confirmable from
  git, see §6). The prior task's refusal to file reconstructed hashes was
  correct: the four downstream entries it named
  (TASK-20260805-d47e12, -5b8a06, -9f2d71, -c60b84) are all still `queued`.
  **Its stronger claim that all four have artifacts that "exist and are cited by
  a committed decision" is contradicted by git and is corrected here:** only
  TASK-20260805-5b8a06 is `ARTIFACTS_PRESENT`
  (`reviews/TASK-20260805-5b8a06/validation_report.yaml`, first added in
  `aa1567c2fe7bc75ec4284b1523e7d7cc5882b96b`). TASK-20260805-c60b84 is `PARTIAL`
  (2 of 5 declared paths committed). TASK-20260805-d47e12 and TASK-20260805-9f2d71
  are `ARTIFACTS_ABSENT` at their declared paths. For -9f2d71 the cause is a
  **filename mismatch, not missing work**: the queue declares
  `reviews/TASK-20260805-9f2d71/red_team_report.md`, while what is committed in
  that directory is `red_team_report.yaml` and `falsification_review.md`. That
  distinction is why every uncommitted declared path in
  `queue_state_audit.yaml` also lists the committed files in its declared parent
  directory. What the mismatch means for the task's status is the Coordinator's
  call, not this audit's.
- **GOAL-ECDLP-001** — confirmed (STRONG).
- **GOAL-AES-003** — confirmed (STRONG): BATCH-015 exists and is cited by a
  committed decision, exactly as the handoff anticipated.
