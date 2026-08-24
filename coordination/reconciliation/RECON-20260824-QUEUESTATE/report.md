# RECON-20260824-QUEUESTATE — dispatch-queue state versus committed reality

**Scope:** every `active` goal in `ledger/goals/`, audited from `origin/main` at
`9e78b74fd` on 2026-08-24.
**Performed by:** the orchestrating `launch-research-harness` session, which holds a shell.
**Authority:** none beyond queue-state hygiene. This sweep changes **no** hypothesis
status, **no** evidence, **no** decision, **no** goal head, and asserts nothing about any
research question. It reconciles `state` fields in `coordination/**/dispatch_queue.json`
against what is already committed, and nothing else.

## Why this was run

The harness selected a goal, rendered its queue, and was offered a "ready" task. Before
dispatching, the batch record was read — and said the batch was **not** dispatchable.
That prompted an audit of whether the dispatcher's ready set could be trusted anywhere.

It could not. Of **110 tasks across 24 active goals**, 8 carried a `state` that contradicted
committed history, and **every one of the three "ready" tasks the dispatcher offered
portfolio-wide was stale or barred.** A harness trusting that ready set would have re-run
finished work.

## Findings, and what was done about each

### 1. Repaired — GOAL-ECQ-002 / BATCH-da59ec (live campaign, now dispatchable)

`TASK-20260823-f88f54` (executor) read `state: queued` with `receipt: null`, but its three
declared artifacts were committed at `95d2a58ec`, whose subject names the task
("TASK-20260823-f88f54 lands: all three admissible boxes EMPTY"), and whose `report.md`
records the executor session, the requested policy `executor-implementation`, the answering
model, and 12 of 80 permitted runs.

- Marked `completed` with a `reconciliation` block recording the landing commit and
  per-artifact digests.
- `TASK-20260823-452f5f` (snapshot archive) moved `blocked` → `queued`: its sole dependency
  is now recorded complete, and the goal head's own `next_action` is "Run BATCH-da59ec".
- The three downstream cards were **deliberately left blocked**. Each must be released by the
  card before it, after that card's receipt verifies; releasing them now would let a reviewer
  read an unarchived producer.

Result: the batch renders with the snapshot card ready and all ten gates passing.

### 2. Repaired — GOAL-AES-001 / BATCH-004 (closed batch, false ready signals removed)

All six cards read `queued` while the batch was **closed**: the goal head records checkpoint
`BATCH-004` with `decision_id DEC-20260731-029` and `evidence_id EV-AES-004`, and the
checkpoint text reports the producers' results directly. All declared artifacts are committed.

- `806`, `807`, `809`, `810` → `completed` (state reconciliation only).
- `808` (snapshot archive) → `completed`. Its `archive.commit_sha` was **read from its own
  receipt**, not reconstructed: `cc660597e`, subject "snapshot: freeze GOAL-AES-001 BATCH-004
  producer artifacts". That commit is **not an ancestor of HEAD** — the squash-merge damage
  class recorded in `CORR-20260802-a1f151` — so the binding is the `path_sha256` map, computed
  from the working tree. All eight producer digests **reproduce the receipt's own staged
  values exactly**, which independently confirms the frozen content has not changed. The
  dispatcher accepted it and reported "9 path hashes verified".
- `811` (ledger archive) → `cancelled`, **not** `completed`. Its two declared records are
  committed and named by the checkpoint, so the transition genuinely happened — but unlike
  `808` it wrote no receipt, so **no archive commit sha exists anywhere to read**. Supplying
  one would be reconstruction, which finding **F-1** of `RECON-20260810-002` forbids in terms:
  such entries "must be TERMINATED in the queue, never re-dispatched and never marked
  completed with a reconstructed commit_sha or path_sha256", and "the archive-chain gap each
  one leaves is real and should stay visible." That gap is left visible in the card's note.

### 3. Deliberately NOT touched — campaigns in flight on unmerged branches

`GOAL-AES-002` declares archive commit `188f9f294`, which exists only on
`origin/claude/keen-clarke-881dve`. `GOAL-QALG-001` fails the same way. Their queues cannot
render from a main-based branch **because their campaigns have not merged**, not because they
are defective. Reconciling them from here would risk exactly the concurrent-worktree damage
`CLAUDE.md` warns about. `GOAL-AES-002`'s one stale card was left alone for the same reason.

### 4. Diagnosed, but each needs its owning campaign

These eight render failures are substantive and campaign-specific, not mechanical:

| Goal | Dispatch error |
|---|---|
| `GOAL-CRYPTO-001` | completed archive `TASK-20260731-002` requires `archive.commit_sha` |
| `GOAL-DREG-001` | ledger archive `TASK-20260812-4177ac` must own exact artifacts under `ledger/evidence/` and `ledger/decisions/` |
| `GOAL-ECTD-001` | `content_first` `commit_sha` does not resolve to a commit at all |
| `GOAL-FAEST-001` | archive commit changes the wrong artifact set — declared `TASK-20260731-013`'s, contains `TASK-20260731-002`'s |
| `GOAL-ICEX-001` | same shape — declared `DEC-20260731-015`, commit carries `DEC-20260731-003` |
| `GOAL-MCE-001` | claim-relevant producer `TASK-20260809-3e30b8` requires a ledger archive after review |
| `GOAL-MD5-001` | `tasks[0].handoff.uncertainty_reduced` must be nonempty text |
| `GOAL-SIG-001` | declared `EV-SIG-010`, commit carries `EV-SIG-007` |

FAEST-001, ICEX-001 and SIG-001 share one shape — a declared record and a committed record
that differ by identifier. That is the cross-goal identifier-collision class the discharge
sweep already recorded as **F-2**, whose own warning applies here: a per-path "committed /
exact file" match "must never be read as evidence of authorship. It is a filesystem fact
about a name." Deciding which record is authoritative is a Coordinator judgement inside each
campaign, not a sweep.

### 5. Not defects — deliberate null queue paths

`GOAL-ARGON-001`, `GOAL-HAWK-001`, `GOAL-MLDSA-001` and `GOAL-SSIQ-001` have
`dispatch_queue_path: null`. Their heads say why: HAWK "remains quiescent", MLDSA is "HELD —
no new batch authorized", ARGON has an experiment dispatched to an executor, SSIQ awaits
adjudication of a returned producer. `DEC-20260819-abe846` already ruled a null queue path
"CORRECT rather than defective". Nothing to fix.

### 6. Barred, and left barred — GOAL-SSI-001 / BATCH-f85613

The dispatcher offers `TASK-20260819-e076f1`, but the batch's own `dispatch_precondition`
(`binding: true`) forbids dispatching any card until four earlier archive cards
(`TASK-20260806-b03b21`, `-e80052`, `-274d8a`, `-91f36a`) are terminal. They are **all**
`state: queued` with no `commit_sha`, so the first branch fails; and the discharge sweep
audits all four `ARTIFACTS_PRESENT`, so F-1's receipt-less class — the second branch — does
not cover them. **Not dispatched.**

Two further observations on that batch, recorded but not acted on. Its `batch.yaml` still
reads `status: draft_pending_id_allocation`, which is stale: the opening decision
`DEC-20260819-abbb7d` was minted and committed at `16859714b` with matching `goal_id` and
`batch_id`. And that decision's own `limitations` states that its identifier is a placeholder
which "may not be committed unsubstituted" — yet it was committed under exactly that
identifier. All eight of the batch's identifiers were checked here and are well-formed and
collision-free, so no damage resulted; remapping them now would break a committed decision
and rule 15 forbids it.

## What this sweep did not do

- It did not verify any research content, re-run anything, or read a result for correctness.
- It did not invent a commit sha, a hash, a timestamp, or a review verdict. Every digest was
  computed from the tree; every commit sha was read from a committed receipt.
- It did not touch any immutable ledger record.
- It asserts nothing about who performed any task. A card marked `completed` here means its
  declared artifacts are present and committed and its `state` field had never been advanced.

## Disclosed substitution

The `coordinator` subagent role in this runtime holds no shell (`Read, Grep, Glob, Write,
Edit, SendMessage`) and therefore cannot compute a SHA-256 or resolve a commit. Per the
precedent recorded in agent-bus `MSG-20260821-0ca52f`, the shell-holding orchestrating
session performs that part and discloses the substitution. This report is that disclosure.
