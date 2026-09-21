# Coordinator adjudication of the BATCH-9e3584 archive defect

Recorded 2026-08-11. Goal `GOAL-MLKEM-005`, batch `BATCH-9e3584`.
Defect records: `archives/TASK-20260809-91cf76/COORDINATOR-DEFECT.md`,
`archives/TASK-20260809-4d928d/COORDINATOR-DEFECT.md`.

**What this instrument is.** A batch-level adjudication of archive bookkeeping.
It writes no ledger record, changes no goal status, moves no hypothesis, promotes
nothing into `knowledge/`, and adjudicates no producer headline. `R-OUT-1` is
neither admitted nor refused here. **Claim tier stays TOY**: nothing in
BATCH-9e3584 bears on ML-KEM security, on any FIPS 203 parameter set, on any
attack cost, or on any cost model. AM-10 through AM-14 of `DEC-20260808-05b684`
and their binding carries are in force and are not re-litigated. BATCH-a44d08 is
not rescored in any respect. BATCH-cbe023's non-citable phrases are not restated
as claims.

**Any ledger consequence of this adjudication is a separate archived act** — it
becomes official only through a committed Coordinator decision that the
post-commit verifier accepts.

## 0. Provenance of the facts I used

**Verified by me in this session, by reading files (no shell, no git):**
`dispatch_queue.json`; both `snapshot-receipt.json` files; the archive
verification block of `tools/research_dispatch.py`; the on-disk contents of the
five BATCH-9e3584 task directories; `GOAL-MLKEM-005.yaml`;
`DEC-20260808-05b684.yaml`; AGENTS.md; CLAUDE.md; `agents/coordinator.md`; and
`BATCH-cbe023/archives/TASK-20260808-6a8e73/COORDINATOR-DEFECT.md`.

**Attributed, not verified by me:** every statement about git — the three
commits and their change sets, the 30-for-30 content match at `HEAD`, the
ancestry checks, `git log --all --follow`, the dispatcher's observed error
messages, and the fact that the work is pushed. These are the harness-driving
session's measurements. I did not re-run them and I do not narrate them into
checks of my own. This distinction is kept deliberately: BATCH-cbe023 produced a
Coordinator claim about the git record that a Validator then proved false
(Validator F-1), and that is the one defect class this record must not reproduce.

**UNKNOWN to me, and marked as such rather than assumed:** whether the commit
messages of `1aa7db53` and `c034ef38` contain their task ids and
`GOAL-MLKEM-005` (`research_dispatch.py:1103-1114`); whether a PR against `main`
is open and current for this branch; and the exact `origin/main` merge base used
before each commit. Neither receipt records the last two.

**New finding of mine, D3.** Nine of the 28 declared producer artifact paths do
not exist under their declared names; nine committed files are undeclared. The
table is in `archives/TASK-20260809-4d928d/COORDINATOR-DEFECT.md` section 2.
This was not in the brief I was given, it is independently terminal for the
producer snapshot's strict binding, and it binds every downstream citation.

## (a) Has the first pause_condition fired, and is there a repair I was asked to look for?

### There is no admissible repair. I searched for one and I can show why none exists.

The frozen contract requires an archive commit to change exactly
`artifact_paths UNION source_paths`, and three properties of
`tools/research_dispatch.py` close the space jointly:

1. `expected_paths` is that union (`:564`), and the change-set test is set
   equality (`:1073-1089`);
2. an archive task's `artifact_paths` must be **non-empty** (`:502`, with
   `require_text_list`'s default `allow_empty=False`), and every artifact path
   has **exactly one owning task** (`:511-517`) — so a successor archive must own
   a new receipt of its own and cannot borrow the producers' paths;
3. the content-only fallback (`:961-1021`) is reachable **only** when the
   declared commit does not resolve (`:1029-1034`) or is not an ancestor of
   `HEAD` (`:1045-1048`) — never when a reachable commit's change set is wrong.

Hence any conforming successor commit must contain a new receipt **and** exactly
the source paths; the source paths are already committed and cannot be changed
again. Candidates considered and their disposition:

| candidate repair | disposition |
| --- | --- |
| Amend / rebase the three commits into two conforming ones | **Refused.** Rewrites pushed history over run records (AGENTS.md "Durable research commits", CLAUDE.md). |
| Revert-and-re-add the pre-registration | **Refused, and I confirm the harness-driving session's judgement without qualification.** It would satisfy the verifier's negative test while destroying the property the test exists to establish — that the frozen text provably predates every measurement it governs. Worse than the defect. |
| Revert-and-re-add the 28 producer files (tempting: no review has run yet) | **Refused, on independent grounds.** It deletes committed run records (which `_changed_paths` itself treats as disqualifying, `:954-957`); it destroys "each producer artifact first appears at the producer snapshot", a clause of the **Validator's own** completion gate; it contradicts an immutable receipt; and it misrepresents when artifacts became durable. Accepting it because it is cheaper here would be precisely the asymmetry this program keeps recording against itself. |
| Fill the queue's `archive` blocks from the committed receipts | **Admissible bookkeeping, not a repair.** It changes the failure message from the misleading `requires archive.commit_sha` to the true diagnosis, and it does not unblock anything. Adopted, in the narrow form specified in (b). |
| Declare an unreachable sha to reach the content-only branch | **Refused as fabrication** (AGENTS.md core rule 9). Not on the table at any price. |
| Change `research_dispatch.py` so a reachable commit with verified content degrades instead of failing | **Refused for this batch.** CLAUDE.md's "receipts bind to CONTENT first" and the tool's behaviour genuinely disagree, and that gap is worth filing on its merits. But relaxing an enforcement rule *after* observing that it failed, in order to pass the thing that failed it, is changing a success criterion after the outcome. It is a shared-contract change affecting every campaign, it needs its own independent review, and **it must be prospective only and must never be used to retro-validate these two archives.** |
| Restructure the queue so the plan renders | **Impossible, and I checked the mechanism.** Marking the archives `failed` renders a plan with zero dispatches (`blockers`, `:630-639`); the failure-provenance exception (`:183-229`) cannot apply, because an archive task may never be the source of another archive (`:545-548`); and re-pointing sources trips "assigned to both" (`:553-557`), while `_validate_review_chains` (`:400-446`) forces every review of a `review_required` producer to depend on that producer's snapshot archive. |

### The ruling, stated in two parts because the honest answer has two parts

**The pause_condition's antecedent is MET IN ITS LETTER for the two archive
tasks.** They "will not verify against [their] declared commit, paths and hashes
after a good-faith repair attempt", and I have just recorded the good-faith
attempt and its exhaustion. I say this plainly rather than lawyering it away.

**It is NOT met in its purpose for the goal, and the goal does not pause.** The
condition is labelled INFRASTRUCTURE ONLY and it sits beside "the repository
cannot be pushed, so work cannot be made durable or reviewable". Both conditions
protect **durability and reviewability**. Neither is lost here:

- the bytes are committed, pushed and content-verified 30 for 30 with zero
  mismatches;
- the artifacts sit in a reachable commit made before either review was
  dispatched, so a reviewer reads immutable bytes that cannot move under them;
- the notarization property is independently checkable by five means, all of
  which the Validator's own completion gate already requires it to redo;
- and AGENTS.md states in terms that the dispatch queue "is a coordination
  record, not evidence: raw run receipts remain immutable in their experiment
  directories". What is broken is the coordination record's binding, not the
  evidence.

Pausing on this would halt a campaign whose science is untouched and whose next
step is fully executable, which is the failure the goal's own
`non_terminal_conditions` and `stop_rule` are written against. So: **the two
archive TASKS are terminally defective and are superseded; GOAL-MLKEM-005 is not
paused.** A later Coordinator who thinks I read the condition too narrowly has
everything needed to overturn me in the paragraph above; the letter/purpose split
is recorded precisely so that it can be.

**Prospective and separate.** I recommend the goal's first `pause_condition` be
restated to distinguish *an archive whose declared CONTENT cannot be verified*
(pause) from *an archive whose commit-scope binding cannot be verified while its
content verifies* (record, supersede, continue). That is a protocol change: it
requires a versioned amendment in a committed decision, it is prospective only,
and **this adjudication does not rely on it.** My ruling above stands on the
condition exactly as written today.

## (b) The superseding instrument

Under AGENTS.md rule 4 corrections supersede and never overwrite. Nothing
restores the two archive tasks. What supersedes them:

1. **Three defect/adjudication files** — this file and the two
   `COORDINATOR-DEFECT.md` records — which are the durable statement of what the
   contract required, what was committed, what is and is not damaged.
2. **A new coordinator producer task, `TASK-20260811-dac670`** *(PLACEHOLDER)*,
   role `coordinator`, `review_required: false`, `state: completed`,
   `write_scope: ["coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584"]`,
   `artifact_paths` exactly:
   - `coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/COORDINATOR-ADJUDICATION-20260811.md`
   - `coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260809-91cf76/COORDINATOR-DEFECT.md`
   - `coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260809-4d928d/COORDINATOR-DEFECT.md`
3. **A new coordinator snapshot archive, `TASK-20260811-998fb8`** *(PLACEHOLDER)*,
   `depends_on: [TASK-20260811-dac670]`,
   `archive.kind: "snapshot"`, `archive.source_task_ids: [TASK-20260811-dac670]`,
   `archive.record_ids: ["GOAL-MLKEM-005"]`,
   `write_scope: ["coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260811-998fb8"]`,
   `artifact_paths: [".../archives/TASK-20260811-998fb8/snapshot-receipt.json"]`.

**Which commit it must ride in.** One new commit changing **exactly four paths**:
the three files in (2) and the receipt in (3), all additions. It is conforming
because every path in it is new. Its message must contain, verbatim,
`TASK-20260811-998fb8` and `GOAL-MLKEM-005` (`research_dispatch.py:1103-1114`).

**The one rule that makes this work, and the forward fix for the whole program.**
*A receipt that states its own commit's sha cannot be inside that commit.* The
frozen tool requires the receipt to be inside it. Therefore:

> **The receipt body carries `commit_sha: null` and rides INSIDE the archive
> commit. The real sha and parent go into `dispatch_queue.json`'s `archive`
> block AFTER the commit, together with `path_sha256` over every declared path
> including the receipt.**

That is the pattern BATCH-cbe023 used, which is why its plan rendered as far as
the commit-message rule. BATCH-9e3584's session made the opposite trade —
recording the true sha in the receipt, at the cost of committing the receipt
separately. That trade is genuinely better in one respect (the binding is
strictly checkable) and it is refused by the tool as frozen. Recording that
tension is the most transportable output of this adjudication, and it belongs in
the ledger archive as a declared program defect with a newly minted id, alongside
the still-open PD-4.

**Bookkeeping to apply to `dispatch_queue.json`** (a mutable coordination record;
no immutable record is edited):

- set `TASK-20260809-91cf76` and `TASK-20260809-4d928d` to `state: "failed"`,
  each with a `failed_note` naming its `COORDINATOR-DEFECT.md`;
- fill each `archive` block **from the committed receipt and from nothing else**
  (`commit_sha`, `parent_sha`, `path_sha256`: 2 entries and 28 entries
  respectively). Note that for `-4d928d` this makes the queue raise
  `path_sha256 contains paths outside its commit scope` — the true D3 diagnosis,
  which is the reason to record it;
- do **not** reuse, remap or delete either task id (AGENTS.md rule 15);
- do **not** invent a hash, a sha, or a path that no one measured.

**The original `dispatch_queue.json` is terminally unrenderable** and must be
marked as such, exactly as BATCH-cbe023's was. Live dispatch moves to a
continuation queue at
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/dispatch_queue_continuation.json`,
carrying five tasks and validating cleanly:

| task | id | notes |
| --- | --- | --- |
| defect record producer | `TASK-20260811-dac670` | `completed` (these three files) |
| conforming snapshot archive | `TASK-20260811-998fb8` | sources `[dac670]`, receipt inside its commit, `commit_sha: null` in the receipt body |
| Validator | `TASK-20260809-3f1dc4` | **id carried, not re-minted**; handoff, write scope, artifact path and budget verbatim; `depends_on: [TASK-20260811-998fb8]` |
| Red Team | `TASK-20260809-444fe7` | same treatment |
| ledger archive | `TASK-20260809-60f9cc` | verbatim, `source_task_ids` unchanged `[3f1dc4, 444fe7]`, reserved `EV-MLKEM-9346bb` / `DEC-20260809-afe29b` unchanged |

The three review/ledger ids are **carried, never re-minted**: their handoffs are
unchanged frozen contracts, their write scopes and artifact paths are already
declared, the ledger archive's binding fields already name them, and AGENTS.md
rule 15 makes remapping an identifier that a completed archive names a last
resort. Opening the continuation queue is a dispatch act and needs a committed
Coordinator decision recording it — that decision is written in the ledger
archive, not here.

## (c) May the two independent reviews proceed?

**YES. They may and should proceed against the committed snapshot `c034ef38`.**

The rule's purpose is that a reviewer reads a **committed immutable snapshot
rather than a live tree**, so the artifacts cannot move under the review and
every finding is falsifiable against fixed bytes. Measured against that purpose:

- `c034ef38` is a real, reachable, pushed commit containing all 28 producer
  artifacts;
- every declared hash matches at `HEAD` — 30 of 30, zero mismatches;
- it was made **before either review was dispatched**, and neither has run;
- the receipt binding those artifacts is itself committed (`502d15a0`), so the
  reviewer has a committed statement of what was declared and can compare it with
  what was committed — including D3, without relying on me;
- the notarization chain the reviewers must check in both directions is entirely
  checkable at `HEAD`.

**The purpose is met in full.** What fails is the dispatcher's bookkeeping
binding of a receipt to a commit — a property of the coordination record, which
AGENTS.md itself distinguishes from evidence. Making reviewers wait would not
add one bit of immutability to anything they read.

I am not deciding this on convenience, and I record the convenience argument only
to set it aside: it is true that under the open PD-4 the review artifacts must
sit uncommitted across a dispatch window and that GOAL-MLKEM-004 lost two reviews
that way, so delay has a real cost. That is **not** my reason. My reason is that
the snapshot is committed, immutable, complete and fixed before review, which is
the whole content of the rule.

**Three constraints are added to both review cards**, and they are not optional:

1. Read the producer artifacts as committed at `c034ef38`, and the frozen
   pre-registration as committed at `1aa7db53`. State which you read.
2. **Verify the three-way commit split and the 30-for-30 content match
   yourselves, and report what you find.** The account in this file and in the
   two defect records is a *Coordinator claim about the git record* and is
   exactly the class of claim a Validator has already proved false once in this
   goal (BATCH-cbe023 F-1). Do not accept it; check it, including the D3 table.
3. Cite producer artifacts by their **committed** filenames
   (`measure_nullfam.py`, `report_nullfam.md`, `results_nullfam.json`,
   `rescore_c1.py`, `report_c1.md`, `results_c1.json`, `posctl_c2.py`,
   `report_c2.md`, `results_c2.json`, and `-cda2f6`'s unchanged names). The names
   in the queue's `deliverables` and `artifact_paths` for `-311784`, `-97d6cf`
   and `-3eb72c` are dangling.

Everything else in both handoffs stands verbatim, including
`review-adversarial` at `independent_session_required: true`. Independence in
this goal remains **procedural and never model-level**; AGENTS.md rule 12 is
UNMET AND UNWAIVED, and the same session authored the pre-registration, ran all
four producers and made both archives — which is disclosed in the receipts and
which makes these two reviews this batch's entire independence budget.

## (d) May the ledger archive `TASK-20260809-60f9cc` proceed?

**NO.** I agree with the harness-driving session's reading, and I sharpen it,
because the primary reason is simpler than the archive chain:

1. **There is nothing to promote.** Both reviews are unrun. No evidence record
   can be written, and a Coordinator decision resting on unreviewed producer
   output would be an official transition on unreviewed artifacts. This reason
   alone is dispositive and holds independently of any defect.
2. **No official transition may rest on an unverifiable archive chain.** The
   evidence for BATCH-9e3584 is carried by `1aa7db53` and `c034ef38`, whose
   archive tasks are terminally defective. Promoting on that chain before the
   supersession is recorded is what the archive rules forbid
   (`agents/coordinator.md`: never mark a result official while its artifact or
   ledger commit fails post-commit verification).
3. **As currently declared it would inherit the identical defect.** Its
   `artifact_paths` include its own `ledger-receipt.json`, and its binding set
   adds both review reports. It must therefore commit receipt **and** sources in
   one commit — i.e. it must use the `commit_sha: null`-inside-the-commit pattern
   of (b), or it will fail exactly as its two predecessors did. **Re-specify it
   before it runs.**

**When it may run:** after both reviews return, in the continuation queue, alone,
with the pattern in (b), committing its receipt, `EV-MLKEM-9346bb`,
`DEC-20260809-afe29b`, the `GOAL-MLKEM-005` checkpoint, both review reports and
every red-team probe (PD-4 — uncommitted and the sole carriers of their own
evidence), never `knowledge/INDEX.md`. Its decision must additionally record: the
supersession of the two archive tasks; D3 and its citation consequences; the new
program-defect id for the receipt/commit tension in (b); the recommended
prospective restatement of `pause_condition` 1; and the fact that
`EV-MLKEM-9346bb` and `DEC-20260809-afe29b` are reservations that must be left
unused if the batch closes without an evidence record.

## Exact next actions for the orchestrator

Ordered. Steps 1-4 must be complete before step 5.

1. **Mint two ids** (the type name is `handoff`, not `task` — `--next task` is
   rejected by the tool's own choice list, which I read at
   `tools/allocate_id.py:253` against `PREFIX_TYPE`):
   ```sh
   python3 tools/allocate_id.py --next handoff --date 20260811   # -> TASK-20260811-dac670  (realized)
   python3 tools/allocate_id.py --next handoff --date 20260811   # -> TASK-20260811-998fb8  (realized)
   python3 tools/allocate_id.py --check TASK-20260811-dac670
   python3 tools/allocate_id.py --check TASK-20260811-998fb8
   ```
   Substitute them for `dac670` / `998fb8` in the three files written today.
2. **Sync before generating** (merge, never rebase):
   ```sh
   git fetch origin
   git merge --no-rebase origin/main
   python3 tools/merge_digest.py --since $(git merge-base HEAD origin/main) --until origin/main
   python3 tools/validate_ledger.py
   ```
   Record the base commit and merge outcome in the receipt of step 4.
3. **Apply the queue bookkeeping** of (b) to `dispatch_queue.json`, and **write
   the continuation queue** with the five tasks of (b).
4. **Commit and verify the conforming snapshot** `TASK-20260811-998fb8` — exactly
   four paths, receipt with `commit_sha: null` inside it, message naming
   `TASK-20260811-998fb8` and `GOAL-MLKEM-005`. Then, in this order:
   ```sh
   python3 tools/research_dispatch.py \
     coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/dispatch_queue_continuation.json
   git push
   gh pr create   # or: gh pr edit, naming GOAL-MLKEM-005 and TASK-20260811-998fb8
   ```
   **Run the verifier before the push, not after.** That is the single lesson of
   `BATCH-cbe023/archives/TASK-20260808-6a8e73/COORDINATOR-DEFECT.md`, and this
   batch is the fourth instance in this goal of a mechanical check run too late.
   If it refuses, fix the queue and re-run; do not push a fifth.
5. **Dispatch both reviews** in independent sessions at `review-adversarial`,
   with the three added constraints of (c), against `c034ef38`.
6. **Optional, for completeness only** — resolve two of my UNKNOWNs and record
   the answers in the step-4 receipt:
   ```sh
   git log -1 --format=%B 1aa7db53
   git log -1 --format=%B c034ef38
   gh pr list --head "$(git rev-parse --abbrev-ref HEAD)"
   ```
   These change nothing: the change-set test already refuses both commits.
7. **Do not** run `TASK-20260809-60f9cc` until both reviews return and it has been
   re-specified per (d).

## Draft decision record — NOT YET OFFICIAL

Written here because this instrument may not write to `ledger/`. It becomes
official only when a `DEC-` id is minted
(`python3 tools/allocate_id.py --next coordinator_decision --date 20260811`), the
record is written to `ledger/decisions/`, and the post-commit verifier accepts
the archive that carries it.

```yaml
coordinator_decision:
  id: DEC-20260811-<TOK3>            # PLACEHOLDER - mint and --check before use
  context: >-
    BATCH-9e3584's two coordinator snapshot archives (TASK-20260809-91cf76,
    TASK-20260809-4d928d) do not satisfy the frozen archive contract: each
    receipt rides in a different commit from the artifacts it declares, and nine
    of the producer snapshot's 28 declared artifact names do not exist under
    those names (D3, found in this adjudication). All 30 declared artifacts match
    their recorded sha256 at HEAD. The bytes are intact and pushed; the binding
    of receipt to commit is not.
  decision: revise
  target_ids:
  - GOAL-MLKEM-005
  - BATCH-9e3584
  - TASK-20260809-91cf76
  - TASK-20260809-4d928d
  - TASK-20260809-60f9cc
  rationale:
  - No admissible repair exists. Amendment and rebase rewrite pushed history;
    revert-and-re-add of the pre-registration destroys the property the archive
    exists to establish, and of the producer files destroys the Validator's own
    "first appearance" check while deleting committed run records; the
    content-only fallback is reachable only by declaring an unreachable sha,
    which is fabrication; and no future commit can change already-committed
    source paths, because artifact_paths must be non-empty and are uniquely
    owned.
  - The first pause_condition's antecedent is met IN ITS LETTER for the two
    archive tasks and NOT met in its purpose for the goal. Durability and
    reviewability - what that INFRASTRUCTURE-ONLY condition protects - are both
    intact. The archive TASKS are terminally defective and superseded; the GOAL
    is not paused.
  - The reviews may proceed. The rule's purpose is that a reviewer reads a
    committed immutable snapshot rather than a live tree; c034ef38 is committed,
    complete, content-verified and fixed before either review was dispatched.
  - The ledger archive may not proceed: both reviews are unrun, no official
    transition may rest on an unverifiable archive chain, and as declared it
    would inherit the identical defect.
  evidence_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/COORDINATOR-ADJUDICATION-20260811.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260809-91cf76/COORDINATOR-DEFECT.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260809-4d928d/COORDINATOR-DEFECT.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260809-91cf76/snapshot-receipt.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260809-4d928d/snapshot-receipt.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/archives/TASK-20260808-6a8e73/COORDINATOR-DEFECT.md
  - tools/research_dispatch.py
  limitations:
  - CLAIM TIER TOY. Nothing here bears on ML-KEM security, any FIPS 203 parameter
    set, any attack cost or any cost model. No producer headline is adjudicated,
    R-OUT-1 included, in either direction.
  - I RAN NO GIT COMMAND AND NO PRODUCER CODE. Every statement about the git
    record is attributed to the harness-driving session. Three facts are marked
    UNKNOWN rather than assumed: both archive commit messages, the PR state, and
    the origin/main merge base of each commit.
  - AGENTS.md rule 12 is UNMET AND UNWAIVED. The same session wrote the
    pre-registration, ran all four producers and made both archives; the two
    pending reviews are this batch's entire independence budget, and independence
    remains procedural, never model-level.
  - No hypothesis status moves and no evidence record is created. EV-MLKEM-9346bb
    and DEC-20260809-afe29b remain reservations.
  next_actions:
  - Mint TASK-20260811-dac670/998fb8; write the continuation queue; commit the
    three defect/adjudication files with a conforming receipt (commit_sha null
    inside the commit); run the verifier BEFORE pushing; open or refresh the PR.
  - Dispatch TASK-20260809-3f1dc4 and TASK-20260809-444fe7 in independent
    sessions against c034ef38, with the three added constraints of section (c).
  - Re-specify TASK-20260809-60f9cc to commit its receipt inside its own archive
    commit before it runs, and hold it until both reviews return.
  - File the receipt/commit tension of section (b) as a declared program defect
    with a newly minted id, beside the open PD-4, and propose the prospective
    restatement of pause_condition 1 as a versioned amendment - never applied
    retroactively to this batch.
  inference:
    requested_policy: coordinator-orchestration-code
    fallback_used: false
    model_verified: false
    note: >-
      Recorded as a verification gap, not claimed satisfied. This runtime binds no
      model provenance: no adapter probe receipt exists for this session and the
      resolved model cannot be probed from inside a subagent. Per CLAUDE.md,
      per-role model selection is process-level under Claude Code and subagents
      keep model: inherit; the policy's reasoning effort binds per subagent.
  decided_by: coordinator
  decided_at: '2026-08-11'
```
