# Adjudication — GOAL-ECDLP-001 head conflict, BATCH-ae8019 vs BATCH-ea56c5

TASK-20260810-9b8038 · campaign RECON-20260810-003 · 2026-08-10

**Verdict: `BOTH_LIVE`. Head takes `BATCH-ea56c5`. `BATCH-ae8019` is declared an
open, unclosed, separately authorized parallel design lane and is not closed,
paused, superseded or dropped by this ruling.**

This ruling opens no batch, authorises no run, moves no hypothesis status,
approves no experiment, files no evidence, promotes no knowledge entry, advances
no `latest_verified_commit`, moves no claim tier, and closes no goal. It resolves
one mutable coordination pointer and declares the state of two research lanes.

---

## 0. Method, and what it deliberately does not use

- **No shell.** No git command, validator, allocator or dispatcher was run. No
  commit sha, parent sha, path sha256, reachability fact, id, timestamp or
  verdict was minted, reconstructed or estimated. No commit was made.
- **No ordering evidence.** Commit order, branch-ahead-ness, filenames and
  self-declared `created_at` dates were **not** used to rank either lane. Both
  opening records declare `created_at: '2026-08-09T00:00:00-07:00'`; that
  identity is noted and then discarded as uninformative.
- **origin/main's side was read only from**
  `coordination/reconciliation/RECON-20260810-003/main_side/`, treated as
  origin/main's committed content per the task card. What that directory does
  **not** contain is named as unresolved in §7 rather than guessed.
- Every ranking claim below rests on text inside a committed record: a
  `parent_batch` / `parent_decision` declaration, a decision's `batch_id`,
  `next_actions` and `authorization` block, a checkpoint's `blocking_findings`
  and `remaining_uncertainty`, or a batch record's `objective` / `scope`.

---

## 1. The conflict, stated exactly

`ledger/goals/GOAL-ECDLP-001/goal.yaml` carries a single-valued mutable head,
`research_goal.current_batch_id`. Two sides disagree on that one scalar:

| | origin/main | this branch |
|---|---|---|
| `current_batch_id` | `BATCH-ae8019` | `BATCH-ea56c5` |
| parent batch | `BATCH-c3c474` | `BATCH-ece945` |
| parent decision | `DEC-20260809-d5ff80` | `DEC-20260809-6bd04d` |
| parent evidence | `EV-ECDLP-f32446` | `EV-ECDLP-defc0b` |
| written by | `DEC-20260809-57b240` / `TASK-20260809-991a81` (declared) | `TASK-20260810-55845c` (head reconciliation) |

Both sides agree on the *prior* value: main's note says "Repointed from
BATCH-c3c474"; this branch records
`prior_current_batch_id_before_head_reconciliation_20260810: BATCH-c3c474`. Both
sides agree BATCH-c3c474 is closed by
`ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-c3c474.yaml` under
`DEC-20260809-d5ff80`. The conflict is not about what happened; it is about
which of two successors inherits one pointer.

---

## 2. The trap, named: TASK-20260810-55845c's premise was FALSE

This branch's committed head note
(`current_batch_id_note_head_reconciliation_20260810`) says, of BATCH-c3c474:

> "No committed record names any successor to BATCH-c3c474: no batch.yaml in
> this goal declares parent_batch BATCH-c3c474, and that lane therefore
> terminates closed."

**That premise is false.**
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-ae8019/batch.yaml` on
origin/main declares, verbatim, `parent_batch: BATCH-c3c474`,
`parent_decision: DEC-20260809-d5ff80`, `parent_evidence: EV-ECDLP-f32446`,
`parent_checkpoint: ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-c3c474.yaml`,
and `authorization.authorized_by: DEC-20260809-d5ff80` with
`fresh_versioned_design_repair_batch_authorized: true`. It is exactly the
"fresh non-overlapping design-repair batch" that `DEC-20260809-d5ff80`'s second
next action and BATCH-c3c474's checkpoint `next_action` required. The
BATCH-c3c474 lane does not terminate closed; its restart condition **was**
executed.

**Why the audit could not have known, and why this is not negligence.**
TASK-20260810-55845c ran with no shell, at one fixed checkout of one branch,
and searched that working tree for a `batch.yaml` declaring
`parent_batch: BATCH-c3c474`. There was none *in that tree*, and there could not
have been: BATCH-ae8019 was authored by a different concurrent session, lives on
origin/main, and had never been merged into this branch. A read-only audit
bounded to one worktree cannot observe another worktree's committed work. Its
scan was correct; its **quantifier** was wrong. It reported "no committed record
names any successor" — a claim over the whole repository — on evidence that could
only support "no record *in this checkout* names a successor."

**The generalisation the next concurrent session must apply.** In this
repository, at N concurrent worktrees, *absence of a record in your tree is never
evidence of absence in the program.* Any inference of the form "no successor
exists", "no batch declares this parent", "this lane terminates", "this
obligation is unexecuted" is unsound from a single-branch read and must be
either (a) scoped explicitly to the checkout and the commit examined, or
(b) supported by a fetch of `origin/main` and every open branch. This is the
same class of error as the co-occurrence failure TASK-20260810-08130e found and
the direction-of-citation failure §3 of TASK-20260810-55845c's own change log
found in GOAL-ECTD-001 — three instances of one failure mode, made by three
tasks that were each careful about the others.

**Consequence for this ruling.** The fact that this branch already reads
`BATCH-ea56c5` carries **zero** evidential weight here. The stated ground for
that value is refuted. The value survives below, but on an entirely different
basis, and I record the coincidence explicitly so it is not mistaken for
confirmation: had the substantive comparison in §5 come out the other way, the
ruling would have moved the head off this branch's own value.

---

## 3. Lane AE8019, on its records

- **Identity.** `BATCH-ae8019`, goal `GOAL-ECDLP-001`, parent `BATCH-c3c474`,
  parent decision `DEC-20260809-d5ff80`, parent evidence `EV-ECDLP-f32446`,
  parent review `TASK-20260809-923ede`, opening decision `DEC-20260809-57b240`.
- **What it repairs.** One new immutable successor apparatus specification,
  `EXP-ECDLP-d7b3c3`, closing the five blocking findings the independent
  reviewer returned against `EXP-ECDLP-ffa5c3`:
  `REV-GAP-REPRESENTATION-007` (no canonical archived representation, ordering,
  tie rule or archive allocation for the 8191 retained gap values),
  `REV-CANONICAL-SCHEDULE-008` (COMPSCH2 / PROVRC02 / ALIASv02 grammars admit
  multiple byte streams), `REV-RESOURCE-CONSUMER-009` (per-arm sorts, quantile
  endpoints, rank comparison, S3 bootstrap index consumption and gap storage
  omitted from the resource ledger), `REV-PACKAGE-FINALIZATION-010` (S4 final
  package attestation is causally self-referential), `REV-MUTATION-LAYER-011`
  (mutation enclosure, offsets and digests unfrozen, so the required first error
  is not uniquely determined).
- **Lineage.** `EXP-ECDLP-adaa91` → `EXP-ECDLP-ffa5c3` → `EXP-ECDLP-d7b3c3`. The
  apparatus/instrument lane that would measure the gamma-gap bootstrap statistic.
- **Gate.** One fresh independent design-readiness review at `review-adversarial`
  xhigh (`TASK-20260809-e05828`, declared).
- **Ceiling.** `apparatus_design_repair_and_independent_review_only`. No
  implementation, execution, run, evidence promotion, ECDLP claim or status
  transition in scope. `experiment_design_approved: false`,
  `implementation_authorized: false`, `experiment_execution_authorized: false`.
- **Budget.** 14400 s wall clock, 4 GB, maximum 7 runs (task runs, not
  experiment runs).
- **Status.** OPEN. No `ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-ae8019.yaml`
  exists on this branch, and no record available to me closes or disposes it.
- **No hypothesis is attached** in its opening record: `batch.yaml` declares no
  `hypothesis_id` field at all. Observed and reported; not overweighted, since
  the two openings were authored by different sessions and may simply differ in
  schema habit.

## 4. Lane EA56C5, on its records

- **Identity.** `BATCH-ea56c5`, goal `GOAL-ECDLP-001`, parent `BATCH-ece945`,
  parent decision `DEC-20260809-6bd04d`, parent evidence `EV-ECDLP-defc0b`,
  hypothesis `H-SYC-b854f4`.
- **What it repairs.** One versioned successor, `EXP-SYC-a59d02`, for the eight
  blockers enumerated in `checkpoints/BATCH-ece945.yaml`: production
  envelope/custody underdefinition; no deterministic event-to-shard mapping; no
  exact class-to-candidate/control/rho/BSGS cost assembly; an incomplete finite
  baseline frontier; a constructor-unreachable null point KAT; two uncharged
  verification passes; incomplete executable/coverage closure; a producer
  lifecycle rationale that misstates the immutable handoff.
- **Method.** It applies two *cheap pre-freeze falsifiers* before freezing
  anything — the exact three-mount verification-count identity and
  canonical-decoder reachability for every literal null point — exactly as
  `DEC-20260809-6bd04d`'s first next action directs. Falsification before
  construction, per `docs/inventor-protocol.md`.
- **Gate.** Fresh **independent Validator AND Red Team** verdicts, both required
  (`DEC-20260809-6bd04d`: "Both mandatory independent pre-implementation reviews
  returned REVISE"; authorization `implementation_granted: false`,
  `execution_granted: false`, `budget_increase_granted: false`).
- **Ceiling.** `zero_experiment_static_falsification_and_pre_implementation_review_only`.
  Zero experiment runs admitted.
- **Budget.** 21600 s design wall clock, 8 CPU-hours, 4 GB, **0** experiment
  runs; carrying an unspent prospective experiment budget of 988 planned /
  1235 hard CPU-hours and 450000 planned / 562500 hard wall seconds.
- **Status.** OPEN. No `checkpoints/BATCH-ea56c5.yaml` exists; no record closes
  it. Materially in progress in this tree: `dispatch_queue.json`,
  `focus_queue.json`, a task card `TASK-20260809-4bfa9f.md`, four producer
  artifacts under `tasks/TASK-20260809-ce341d/`
  (`design-repair-report.yaml`, `verification-and-null-kats.yaml`,
  `custody-and-executable-contract.yaml`, `physical-frontier-compiler.yaml`) and
  two snapshot receipts under `archives/`.

---

## 5. Why both lanes are live, and why the head takes EA56C5

### 5.1 BOTH_LIVE is forced by the records, not chosen for comfort

The two lanes are **disjoint in every respect a contradiction could live in**:

| | AE8019 | EA56C5 |
|---|---|---|
| predecessor experiment | `EXP-ECDLP-ffa5c3` | `EXP-SYC-268d6f` |
| successor experiment | `EXP-ECDLP-d7b3c3` | `EXP-SYC-a59d02` |
| hypothesis | none declared | `H-SYC-b854f4` |
| blocking findings | 5 (`REV-*-007…011`) | 8 (BATCH-ece945 set) |
| parent decision | `DEC-20260809-d5ff80` | `DEC-20260809-6bd04d` |
| review gate | one design-readiness xhigh | Validator **and** Red Team |

Neither opening record mentions the other's experiment, findings, hypothesis or
budget. AE8019 explicitly excludes "any edit to experiments/EXP-ECDLP-ffa5c3 or
to any BATCH-c3c474 artifact"; EA56C5 explicitly excludes any increase above its
inherited caps. Each was separately authorized by a distinct committed
Coordinator decision that named exactly one successor batch and got exactly one.
**Two authorized design repairs of two different experiments cannot contradict
each other, and closing either would silently discard a lane a committed
decision required.** Both are zero-run, pre-implementation design work with no
active experiment and no compute in flight, so holding both does not breach
focus discipline (`agents/coordinator.md`, "Focus discipline": at most three
critical *experiments* active — here, zero).

### 5.2 The head names one — the arguments, weighed

`current_batch_id` is single-valued. It is an **attention and dispatch pointer**,
not an evidential one — the same convention this goal already applies to
`active_hypothesis_ids` ("Membership of this list is an attention record, not an
evidential one"). Naming one lane therefore ranks attention; it does not close,
pause, weaken or judge the other.

**Argument A, for AE8019 — lineal continuity.** The head's prior value was
`BATCH-c3c474`; AE8019 declares `parent_batch: BATCH-c3c474`. Main's repoint
follows a parent edge from the outgoing head, whereas this branch's repoint jumps
lanes. That is content-based, not date-based, and it is the strongest case for
AE8019.

**Why A is not decisive.** Adopting "the head follows its own lineage" as the
rule makes the winner whichever concurrent session's parent happened to be the
outgoing head — and *that* value is itself an artifact of an earlier merge
reconciliation, not a research judgement. `merge_reconciliation_20260809_batchc3c474_cursor`
retained BATCH-c3c474 **as against** BATCH-25dd46 / BATCH-fc86ca; it does not
mention the BATCH-ece945 / BATCH-ea56c5 lane at all, so it does not adjudicate
this conflict, and the goal record's own history (`historical_parallel_main_current_batch_id_20260809: BATCH-25dd46`)
shows the head has repeatedly moved *between* parallel source lineages with a
note. The head has never been a strict lineage cursor. Deciding on lineal
descent would therefore be deciding on which lane happened to hold the pointer
last — a proxy for "who got there first", which this adjudication is forbidden
to use and which is not a research reason.

**Argument B, for EA56C5 — expected information gain toward the goal's own
objective.** `GOAL-ECDLP-001` requires every candidate to carry "complete
preprocessing, relation collection, linear algebra, target descent, verification,
memory, and multi-target accounting **against Pollard rho and BSGS**."

- EA56C5's blocker list is, in substance, that accounting: "no exact
  class-to-candidate/control/rho/BSGS cost assembly" and "an incomplete finite
  baseline frontier", with its admitted scope naming "byte-exact finite
  Pollard-rho and BSGS baseline protocols and nondominated-frontier decisions"
  and a "complete class-to-setup, treatment, control, candidate, rho, and BSGS
  per-size multi-axis compiler". Closing those blockers is what converts this
  lane into something that could be compared against the goal's mandated
  baselines, and it carries an unspent, already-costed prospective experiment
  budget behind it.
- AE8019's five blockers are, in substance, representation and packaging
  hygiene: canonical gap records, byte grammars, omitted resource rows, acyclic
  finalization, frozen mutation offsets. Closing them makes the apparatus
  specification reproducible — necessary, but the lane's **own committed
  checkpoint** states its ceiling: "A future passing apparatus run would still be
  deterministic fixture evidence, not cryptographic-scale ECDLP evidence," and
  "No theorem or observation supports positive gamma_s on prime curves."

That is a record-grounded discriminator on what each repair *buys*: EA56C5's
repairs unlock a costed comparison against the baselines the goal names;
AE8019's repairs unlock, by its own checkpoint's words, deterministic fixture
evidence that is not ECDLP evidence. Two further record-level facts point the
same way, and are cited as secondary rather than load-bearing: EA56C5 is gated
on **two** independent adversarial reviews rather than one, and it front-loads
two cheap falsifiers that can kill the design before any freeze — the
falsification-first ordering `docs/inventor-protocol.md` requires and the
cheapest place for this goal to lose an hour.

**Ruling on the head: `BATCH-ea56c5`,** on Argument B, with Argument A
acknowledged, answered, and recorded so that a future session can reopen the
question on its merits rather than rediscover it.

### 5.3 What this explicitly does not say about AE8019

It does not say AE8019 is unsound, redundant, lower quality, superseded, paused,
stale, or closed. It does not touch its authorization, which stands intact under
`DEC-20260809-d5ff80`. It does not license anyone to edit, delete, retire or
skip it. A session driving that lane takes its authority from
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-ae8019/batch.yaml` and
`DEC-20260809-d5ff80`, **not** from the goal head, and may carry it to its own
checkpoint and ledger disposition without any further permission from this
ruling.

### 5.4 One correction the merged head must also carry

This branch's `next_action` asserts that BATCH-c3c474's and BATCH-fc86ca's
restart conditions "BOTH REMAIN UNEXECUTED". For **BATCH-c3c474 that is now
false**: BATCH-ae8019 executed it. For BATCH-fc86ca I make **no finding either
way** — I could not see origin/main's full batch set, and asserting "no successor
exists" from partial visibility is precisely the error §2 diagnoses. The merged
record must correct the c3c474 clause by supersession and mark the fc86ca clause
unresolved.

---

## 6. Merge instruction for the orchestrating session

Binding, and stated as an instruction because the merge is not mine to perform.
I wrote no conflict markers and reconstructed no file.

**M1. `research_goal.current_batch_id` after the merge: `BATCH-ea56c5`.**
Take this branch's side of that one conflicting scalar. Do not edit either
lane's records to make it fit.

**M2. Preserve from origin/main, verbatim, deleting nothing:**
- `current_batch_id_note_batchae8019_open_20260809` — keep the full note as
  written. It is **not** demoted to a superseded head note; retitle nothing.
- main's `next_action` text in full, moved to a new key
  `parallel_lane_next_action_batchae8019_20260809` (I have not seen its bytes;
  copy them exactly, do not paraphrase).
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-ae8019/**` and every
  `ledger/**` record main adds — non-conflicting additions, union-merge them
  unchanged.
- `merge_reconciliation_20260809_batchc3c474_cursor`,
  `historical_parallel_main_current_batch_id_20260809`,
  `current_batch_id_note_batchc3c474_open_20260809` and the older
  `current_batch_id_note_at_*` chain are byte-identical on both sides; keep one
  copy.

**M3. Preserve from this branch, verbatim:**
- `current_batch_id_note_head_reconciliation_20260810` — **unedited**, including
  its false premise. It is superseded in place by M4, never rewritten.
- `prior_current_batch_id_before_head_reconciliation_20260810: BATCH-c3c474`.
- `dispatch_queue_path: coordination/goals/GOAL-ECDLP-001/batches/BATCH-ea56c5/dispatch_queue.json`
  and its note — the head and the queue path move together, so no head-internal
  mismatch is created.
- the branch `next_action` as the operative one, unedited.

**M4. Add, as new keys, by supersession, each citing TASK-20260810-9b8038:**
- `current_batch_id_note_head_reconciliation_20260810_correction_20260810` —
  records that the "no committed record names any successor to BATCH-c3c474"
  premise is FALSE, that `BATCH-ae8019` declares exactly that parentage and was
  on origin/main throughout, why a single-worktree audit could not see it (§2),
  and that the head value survives on the §5.2 basis and not on the refuted one.
- `parallel_live_lane_batchae8019_20260810` — declares `BATCH-ae8019` OPEN,
  unclosed, authorized by `DEC-20260809-d5ff80`, opened by `DEC-20260809-57b240`,
  targeting `EXP-ECDLP-d7b3c3` against findings `REV-GAP-REPRESENTATION-007`,
  `REV-CANONICAL-SCHEDULE-008`, `REV-RESOURCE-CONSUMER-009`,
  `REV-PACKAGE-FINALIZATION-010`, `REV-MUTATION-LAYER-011`; states that it is
  not the head, is not closed, paused or superseded by this ruling, that its own
  `batch.yaml` and `DEC-20260809-d5ff80` are its authority, and that repointing
  the head to it requires a superseding Coordinator decision citing this ruling.
- `next_action_correction_batchc3c474_restart_executed_20260810` — corrects the
  "BOTH REMAIN UNEXECUTED" clause for BATCH-c3c474 only, and records the
  BATCH-fc86ca clause as UNRESOLVED per §7 U5.

**M5. Do not:** edit, delete, renumber or overwrite any `batch.yaml`,
checkpoint, decision, evidence record, dispatch queue, task card, producer
artifact or archive receipt belonging to either lane; advance
`latest_verified_commit` (no commit is verified by this ruling); change
`active_hypothesis_ids`, any hypothesis status, any experiment status,
`goal_status`, any claim tier or any budget; resolve any conflict by choosing a
side inside an immutable record — if one appears, stop and mint a superseding
record.

**M6.** `updated_at` already reads `'2026-08-10'` on this branch; leave it, and
do not treat it as a claim about any commit.

**M7. Optional, and a separate act:** if this ruling is to carry official
standing beyond the reconciliation campaign, the orchestrating session may mint a
`DEC-20260810-*` `coordinator_decision` citing `TASK-20260810-9b8038`,
`BATCH-ae8019`, `BATCH-ea56c5`, `DEC-20260809-d5ff80` and `DEC-20260809-6bd04d`.
My write scope forbids me from creating it, and this ruling does not presume it.

---

## 7. Unresolved, carried forward

| id | question | why unresolved | what would settle it |
|---|---|---|---|
| `U1-AE8019-PROGRESS` | how far BATCH-ae8019 has actually got — whether `dispatch_queue.json`, task cards, producer artifacts, snapshot receipts or the `TASK-20260809-e05828` review exist | `main_side/` extracted only `batch.yaml`; I have no shell and cannot list origin/main | a directory listing and queue read of `coordination/goals/GOAL-ECDLP-001/batches/BATCH-ae8019/` on origin/main |
| `U2-AE8019-OPENING-DEC` | whether `DEC-20260809-57b240` and `TASK-20260809-991a81` exist as committed records | not in `main_side/`, not in this tree | read `ledger/decisions/DEC-20260809-57b240.yaml` and `ledger/handoffs/TASK-20260809-991a81.yaml` on origin/main. **If absent, the lane is not thereby closed** — its opening would be procedurally incomplete and would need a superseding opening act, which is a Coordinator decision, not a merge fix |
| `U3-MAIN-NEXT-ACTION` | main's `next_action` bytes, required verbatim by M2 | not extracted into `main_side/` | the orchestrating session has main's file; copy exactly, do not paraphrase |
| `U4-LANE-SEQUENCING` | whether both design lanes should proceed concurrently or one be explicitly paused for capacity | both are zero-run design lanes so focus discipline is not breached; the sequencing question is a research-priority judgement outside a head reconciliation | a Coordinator decision after U1 is known |
| `U5-FC86CA-SUCCESSOR` | whether `BATCH-fc86ca`'s restart condition also has a successor somewhere in the program | **I explicitly decline to repeat §2's error**; I could not see origin/main's full batch set and make no claim either way | a repository-wide search across `origin/main` and every open branch for `parent_batch: BATCH-fc86ca` |
| `U6-HEAD-REVISIT` | whether the head should later move to `BATCH-ae8019` | ruled on §5.2 substance under partial visibility of U1 | if U1 shows AE8019 materially advanced (producer artifacts frozen, independent review obtained) while EA56C5's producer work is stalled, that is a legitimate ground for a **superseding** Coordinator decision to repoint the head. It would not change `BOTH_LIVE` |

---

## 8. Provenance

- `records_read_in_full`: `ledger/handoffs/TASK-20260810-9b8038.yaml`;
  `AGENTS.md` binding summary via `CLAUDE.md`; `agents/coordinator.md`;
  `coordination/reconciliation/RECON-20260810-003/main_side/BATCH-ae8019.batch.yaml`,
  `.../goal.yaml.head-excerpt.txt`, `.../DEC-20260809-d5ff80.yaml`,
  `.../DEC-20260809-6bd04d.yaml`, `.../checkpoint.BATCH-c3c474.yaml`;
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-ea56c5/batch.yaml`;
  `ledger/goals/GOAL-ECDLP-001/goal.yaml` (head-note, next_action and
  dispatch_queue regions);
  `coordination/reconciliation/RECON-20260810-002/tasks/TASK-20260810-55845c/change_log.md`.
  Directory listings only (no content read) for
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-ea56c5/**`,
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-ae8019/**` (empty in this
  tree) and `ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-e*.yaml`.
- `shell_access`: **false**. No git, parser, validator, allocator, dispatcher,
  commit, push or PR. No sha, id, timestamp or verdict minted or reconstructed.
- `ordering_evidence_used`: **none**. Commit order, branch position, filenames
  and self-declared dates were not used to rank either lane.
- `fabrication_guard`: every quoted string above was read out of a named record
  in this session. Where a record was not available (U1–U3, U5) the gap is named,
  not filled.
- `writes_performed`: this file and `ruling.yaml`, both inside
  `coordination/reconciliation/RECON-20260810-003/tasks/TASK-20260810-9b8038/`.
  Nothing outside `write_scope`. **No commit was made.** No goal record was
  opened for writing.
- `immutability`: no batch record, checkpoint, decision, evidence record,
  dispatch queue, producer artifact or archive receipt was edited or deleted.
  Every correction is by supersession and cites both lanes.
- `inference`: `requested_policy: coordinator-orchestration-code`;
  `model_that_answered: claude-opus-5`; `runtime: claude_code` coordinator
  subagent at `effort: high`, which is the effort that policy requests per
  CLAUDE.md's derived table; `fallback_used: false`; `degraded: false`;
  `independent_session: false`. The requested policy was honoured; no
  substitution was requested and none was made. `model_verified: null` — no
  doctor probe was run because no shell was available, so the model identifier is
  unverified session configuration.
