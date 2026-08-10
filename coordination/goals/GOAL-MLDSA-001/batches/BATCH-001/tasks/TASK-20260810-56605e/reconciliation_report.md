# Coordinator bookkeeping and goal-head reconciliation — TASK-20260810-56605e

**Goal:** GOAL-MLDSA-001 **Batch:** BATCH-001 **Date:** 2026-08-10
**Decision:** `ledger/decisions/DEC-20260810-689473.yaml`
**Handoff:** `ledger/handoffs/TASK-20260810-56605e.yaml`

This is the dedicated bookkeeping task that
`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/tasks/TASK-20260807-dcfaee/reconciliation.md`
explicitly requested twice and could not perform itself, because its tool
surface had no git access. That memo's §1 asked for "a dedicated bookkeeping
task with git access [to] reconcile all four remaining entries against the
actual commit history", and flagged "a dedicated goal-head reconciliation
task … before GOAL-MLDSA-001's next batch is opened". Both are discharged
here. Its refusal to fabricate hashes rather than fill placeholders is the
standard this task keeps.

This report is bookkeeping and disposition only. It creates no hypothesis,
runs no experiment, files no knowledge entry, changes no hypothesis status,
and makes no assessment of ML-DSA, MLWE, MSIS, or SelfTargetMSIS in either
direction.

## 0. Provenance of every git fact below

**This task had no shell and no git access.** Every commit sha, parent, date,
subject, changed-path set, blob sha, ancestry result, dispatcher exit code, and
rejection message in this report was established against real history on
2026-08-10 by the dispatching session that holds git access, and supplied to
this task as given fact. This task re-derived none of them and invented none of
them.

That happened in **two rounds**. The first established the commit chain (§1),
the four deviations (§2) and the reachability tests (§3). This task then
surfaced two commit-pointer discrepancies it could not resolve and explicitly
declined to call errors; the dispatching session ran the git-enabled check and
returned the verified explanation now recorded as **D5 (§7)** — a rebase that
orphaned the originally recorded commits. The earlier "unverified observations"
framing has been replaced accordingly. Recording the discrepancy without
adjudicating it is what made the second round possible.

A reader wanting independent confirmation should re-run `git show --stat` on
the shas in §1 and §7, `git merge-base --is-ancestor` on the orphaned pair, and
`tools/research_dispatch.py` for §3.

## 1. The BATCH-001 archival chain DID execute, in the correct order

Three isolated commits, all dated 2026-08-05T17:52:11-07:00, chained parent to
child:

| # | Task | Commit | Parent | Paths | Subject |
|---|---|---|---|---|---|
| 0 | — | — | — | — | chain base `1245602e1040f3dfcfea556fc52d0db2a0becb6a` |
| 1 | `TASK-20260805-d47e12` (snapshot) | `f44ffbad97856fc9170f89ce8684639427f1e1be` | `1245602e1…` | exactly 6 | `snapshot(TASK-20260805-d47e12): GOAL-MLDSA-001 BATCH-001 lit-acquisition — 5 proposed KN-LIT, FIPS-204 distinct from KN-LIT-056` |
| 2 | `TASK-20260805-5b8a06` + `TASK-20260805-9f2d71` (reviews) | `aa1567c2fe7bc75ec4284b1523e7d7cc5882b96b` | `f44ffbad9…` | exactly 3 | `coord: GOAL-MLDSA-001 BATCH-001 reviews VAL-5b8a06(accept_qual) RT-9f2d71(pass_constraints)` |
| 3 | `TASK-20260805-c60b84` (ledger) | `c37bb2c9d7d6b66cb9481cc049c91eee1bdf04aa` | `aa1567c2f…` | 8 | `ledger: GOAL-MLDSA-001 BATCH-001 — EV-MLDSA-faf2ec DEC-20260805-0d59ff 5 KN-LIT filed; BATCH-002 cleared for SelfTargetMSIS ideation` |

Commit 1 changed exactly six paths, all under
`tasks/TASK-20260805-a1c3f9/`: `corpus_dedup_report.md`,
`fault_literature_summary.md`, `fips204_transcription.md`,
`proposed_kn_lit_entries.md`, `source_access_log.yaml`, `receipt.yaml`.

Commit 2 changed exactly three: `reviews/TASK-20260805-5b8a06/validation_report.yaml`,
`reviews/TASK-20260805-9f2d71/falsification_review.md`,
`reviews/TASK-20260805-9f2d71/red_team_report.yaml`.

Commit 3 changed eight: the five `knowledge/literature/KN-LIT-*.md` entries
(`180ad5`, `340675`, `4dadec`, `4f3b80`, `8ce0b5`), `ledger/evidence/EV-MLDSA-faf2ec.yaml`,
`ledger/decisions/DEC-20260805-0d59ff.yaml`, `ledger/goals/GOAL-MLDSA-001.yaml`.

### The ordering fact

The parent chain `1245602e1 → f44ffbad9 → aa1567c2f → c37bb2c9d` is itself the
proof of ordering. The snapshot commit **is the parent of** the reviews commit,
and the reviews commit **is the parent of** the ledger commit. The snapshot
therefore preceded independent review, and independent review preceded the
ledger archive.

This is the single most important finding of this reconciliation. AGENTS.md
"Durable research commits" — freeze the producer package before a reviewer
reads it, then commit the ledger after the reviews, in isolated commits — was
**materially honoured** by BATCH-001. Everything in §2 is a defect in the
*declarations about* those commits, not in the discipline the commits
implemented.

## 2. The four deviations

### D1 — permanent, uncorrectable. Missing snapshot receipt.

`archives/TASK-20260805-d47e12/snapshot-receipt.json` was never written and is
absent from `f44ffbad9`. The `BATCH-001/archives/` directory does not exist in
the working tree at all.

**Why it can never be fixed.** That task card's own constraint required the
receipt to be committed *inside the commit it describes* (which is also why the
card correctly specified `commit_sha: null` for it). `f44ffbad9` is immutable.
The receipt can never be placed inside the commit it was contracted to
describe. Writing it now, into a later commit, would produce a document that
looks like a snapshot receipt and is not one.

**Disposition:** not repaired. `TASK-20260805-d47e12` → `state: "invalid"`.

### D2 — clerical, corrected. Under-declared producer artifact.

`TASK-20260805-a1c3f9`'s `artifact_paths` declared 5 files; commit `f44ffbad9`
committed 6 — the extra being the task's own `receipt.yaml`.

**Disposition:** `receipt.yaml` appended to that task's `artifact_paths` so the
declaration matches the committed set. State stays `completed`, as
TASK-20260807-dcfaee already set it.

### D3 — clerical, corrected. Wrong red-team artifact names.

`TASK-20260805-9f2d71`'s `artifact_paths` declared
`reviews/TASK-20260805-9f2d71/red_team_report.md`. What `aa1567c2f` actually
contains is `red_team_report.yaml` (different extension) **plus**
`falsification_review.md` (undeclared).

**Disposition:** `red_team_report.md` replaced by `red_team_report.yaml` and
`falsification_review.md`. Neither committed artifact is touched and neither
review verdict changes — validator `accept_with_qualifications`, red team
`pass_with_constraints`, as recorded in `EV-MLDSA-faf2ec` and in the
`aa1567c2f` subject line.

### D4 — permanent, uncorrectable, and the ROOT CAUSE.

Four separate declaration failures in the one ledger-archive card
`TASK-20260805-c60b84`:

1. **Missing ledger receipt.** `archives/TASK-20260805-c60b84/ledger-receipt.json`
   was never written and is absent from `c37bb2c9d`.
2. **Planned record IDs never minted.** The card planned `EV-MLDSA-7e91a4` and
   `DEC-20260805-3d5f82`. Neither was ever minted. The archive actually
   recorded `EV-MLDSA-faf2ec` and `DEC-20260805-0d59ff`.
3. **Scope expansion.** `c37bb2c9d` committed five `knowledge/literature/KN-LIT-*.md`
   files outside the card's declared `artifact_paths` — which the card's own
   constraint anticipated and required be handled by amending
   `write_scope`/`artifact_paths` **first**. That did not happen.
4. **`dispatch_queue.json` omitted from `artifact_paths`** — even though it
   appears in the card's `write_scope` and in its deliverables list
   ("dispatch_queue.json at its terminal state").

**Root-cause finding.** (4) is the cause of everything TASK-20260807-dcfaee was
convened to fix. Because the terminal queue state was never staged in the
ledger archive, every downstream entry still read `queued` three days after the
work completed. That made BATCH-001 look dispatch-ready to every session that
read the queue, which is the same reason the goal head still pointed at
BATCH-001 and still named two record IDs that do not exist. **One omitted path
in one declared artifact list produced three days of contradiction between the
coordination records and committed reality.**

**Why (1) and (2) can never be fixed.** (1) is the same immutability argument
as D1. For (2), AGENTS.md rule 15 forbids the repair anyone reaches for first:
`EV-MLDSA-7e91a4` and `DEC-20260805-3d5f82` must **not** be retroactively
minted to match the plan, and `EV-MLDSA-faf2ec` / `DEC-20260805-0d59ff` must
**not** be remapped to match the card. The plan was superseded by reality; the
real records stand and the card is the thing that is wrong.

**Disposition:** not repaired. `TASK-20260805-c60b84` → `state: "invalid"`. Its
`archive.record_ids` are left holding the two never-minted planned IDs exactly
as written, unfilled and uncorrected, because that list is the historical
record of what was *planned*, and because a non-completed archive block is not
a verified one. The planned → actual mapping lives in DEC-20260810-689473.

## 3. Tested reachability: `completed` is unreachable, and that is a test result

The dispatching session actually ran `tools/research_dispatch.py` against three
candidate queue configurations. These are results, not predictions.

| Candidate | Configuration | Result |
|---|---|---|
| **A** (adopted) | reviews `5b8a06`/`9f2d71` → `completed`; D2/D3 path corrections applied; **both** archive tasks → `invalid` | **exit 0**; all five tasks terminal; zero ready, zero deferred |
| B | `d47e12` → `completed` with real `commit_sha`/`parent_sha`/`path_sha256`, never-written receipt dropped from `artifact_paths` | **REJECTED**: `tasks[1].artifact_paths must be a nonempty text list` |
| C | never-written receipt **kept** in `artifact_paths` while marked `completed` | **REJECTED**: commit fails the exact-scope check — declared receipt missing from the commit, undeclared `receipt.yaml` present in it |

**Conclusion.** `completed` is unreachable for both BATCH-001 archive tasks
under any honest declaration: dropping the missing receipt empties a list the
schema requires to be nonempty, and keeping it fails exact-scope verification
against an immutable commit. `invalid` is therefore not a judgement call dressed
up as one — it is the only terminal state the tooling and the truth jointly
permit. This is recorded so a future session does not spend a second
reconciliation task rediscovering it.

Candidate A is what was written to
`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/dispatch_queue.json`.
Every `archive` block's `commit_sha`, `parent_sha`, `path_sha256` and
`record_ids` were left exactly as found (null/empty): a `completed` archive is
unreachable, and a non-completed archive block is not a verified one, so
filling those fields would assert a verification that did not occur.

## 4. What is NOT affected

**BATCH-001's research chain is sound and is not reopened.** The producer
package was frozen before review (`f44ffbad9`), two independent reviews were
committed against that frozen package (`aa1567c2f`), and the evidence,
decision, and knowledge entries were committed after those reviews
(`c37bb2c9d`).

Specifically unaffected and still standing:

- `EV-MLDSA-faf2ec` (strength `preliminary`, claim tier `literature_survey`,
  proof status `empirical_only`);
- `DEC-20260805-0d59ff` and its three red-team gate rulings;
- the five filed entries `KN-LIT-180ad5`, `KN-LIT-340675`, `KN-LIT-4dadec`,
  `KN-LIT-4f3b80`, `KN-LIT-8ce0b5`.

Marking two coordination task cards `invalid` for missing receipts is a
statement about those cards, not about the artifacts they failed to describe.
No claim tier moves and no hypothesis status changes. RQ-MLDSA-001's
toy/until-certified ceiling stands untouched.

## 5. Goal-head diff applied to `ledger/goals/GOAL-MLDSA-001.yaml`

| Field | From | To |
|---|---|---|
| `current_batch_id` | `BATCH-001` | `BATCH-214d98` |
| `latest_verified_commit` | `null` | `'7ef705ca51c5861a14461085967413209a7934da'` |
| `next_action` | "BATCH-001 is queued and dispatch-ready … Run TASK-20260805-a1c3f9 … records EV-MLDSA-7e91a4 and DEC-20260805-3d5f82" | one concrete action: open a single scoped literature-filing batch (full text in the record) |
| `next_action_superseded` | single mapping | append-only list, oldest first; 2026-08-05 entry preserved verbatim, 2026-08-10 entry appended |
| `updated_at` | `'2026-08-05'` | `'2026-08-10'` |

**Why each.**

- `current_batch_id`: BATCH-001 completed 2026-08-05 (`c37bb2c9d`). The goal
  then ran BATCH-66b482 (ideation, `DEC-20260805-4843d6`) and BATCH-214d98
  (design/execution, `DEC-20260805-ae4a96`, superseded by
  `DEC-20260805-64abe7`, then `DEC-20260805-79d745`), all on 2026-08-05.
  BATCH-214d98 is the goal's most recent batch.
- `latest_verified_commit`: the goal's latest committed ledger archive,
  `7ef705ca51c5861a14461085967413209a7934da` (2026-08-05T20:03:31-07:00,
  subject `ledger: GOAL-MLDSA-001 — DEC-20260805-79d745 Lane A deferred (PDF
  blocked); KN-FIND-720727 Shin+Jendral outside formal model; pivot to
  GOAL-HAWK-001`). The field held `null` even though three ledger archives had
  landed. **Reachability from `origin/main` was independently verified with
  git by the dispatching session**, in the same round that established the
  orphaning in §7 — which is exactly the check that matters here, since §7
  shows this goal's history contains orphaned shas that *look* like valid
  pointers. `7ef705ca5…` is not one of them: it is reachable, and the value
  stands as written.
- `next_action`: the prior text was flatly contradicted by committed state on
  three counts — it described a completed batch as queued and dispatch-ready;
  it directed a session to run `TASK-20260805-a1c3f9`, already completed and
  reviewed; and it named two record IDs that were never minted. Any session
  waking on this goal would have been sent to redo BATCH-001.
- `next_action_superseded`: converted to an append-only list so the 2026-08-05
  supersession is preserved rather than overwritten. A goal head that records
  only its most recent supersession loses the history the field exists to keep.
  Each list entry keeps the original `prior_text`/`reason` shape.

**Fields deliberately not changed:**

- `status` — left `active`, see §6.
- `dispatch_queue_path` — still points at BATCH-001's queue. Outside this
  task's declared write scope for the goal record, and there is no alternative
  to point it at: BATCH-66b482 and BATCH-214d98 have no `dispatch_queue.json`
  in the tree, and the next batch's queue does not exist yet. Disclosed as a
  known-stale pointer, to be updated by the next batch's ledger archive. Now
  that BATCH-001's queue is fully terminal (zero ready, zero deferred), a
  session following the pointer is told "nothing to do here" rather than "redo
  BATCH-001", which is the material half of the hazard.
- `active_hypothesis_ids` — left empty. `H-MLDSA-f3a291`, `H-MLDSA-c7b4e8` and
  `H-MLDSA-d1e509` have statuses set by `DEC-20260805-ae4a96`,
  `DEC-20260805-64abe7` and `DEC-20260805-79d745`; this task has no mandate to
  change or re-list them.
- `campaign_budget` — unchanged; see §7.

## 6. Status judgement: `active` stands

`DEC-20260805-79d745` blocks Lane A on ePrint 2023/246 PDF access and reads
like a pause. It is not one, because the goal's own declared
`pause_conditions` are the test, and none is met.

| Declared `pause_condition` | Met? | Why |
|---|---|---|
| Six-batch campaign budget exhausted without an admissible next mechanism | **no** | Three of six batches run; an admissible next mechanism exists and is blocked on *process*, not access — the Kosuge & Xagawa candidate (ASIACRYPT 2025 / ePrint 2025/904, "content-ready … process, not source verification") and the `KN-LIT-4dadec` `citation_verified: partial → read` upgrade ("process only"), both per TASK-20260807-dcfaee §2(b), §6a and its summary table |
| Neither the FIPS 204 text nor the primary fault-security proof obtainable after the source order is exhausted | **no** | Conjunctive; requires **both** unobtainable. FIPS 204 is filed at `KN-LIT-4dadec` and its full 65-page text was subsequently read (the basis of the pending upgrade); `KN-LIT-3907` was identified as ePrint 2023/246 and its abstract read from the primary page (`DEC-20260805-64abe7`). Only the 2023/246 PDF full text is blocked |
| Decisive computation exceeds campaign budget after cheaper falsification gates | **no** | No decisive computation attempted or costed; Lane A stopped on source access, not compute cost |
| Definitive infrastructure/authentication/dependency blocker prevents the next approved task | **no** | Closest condition, so answered most carefully. The 2023/246 HTTP 403 *is* a definitive-looking infrastructure blocker, and under AGENTS.md rule 5 it is infrastructure signal and never evidence about the CMA-to-NMA tightness factor. But it blocks **Lane A's** next task, not "the next approved task" of the goal: the two process-blocked filing items need no access to 2023/246 at all. A goal with an unblocked, admissible, already-identified next action is not blocked, and recording it `paused` would understate it — a failure mode AGENTS.md names as symmetric with overclaiming |

### Interaction with `DEC-20260805-79d745`'s "No new batch authorized"

**Ruling.** That sentence is read as scoped to the constraint it names — ePrint
2023/246 PDF access, i.e. Lane A / `EXP-MLDSA-3f7ab2` — and not as a blanket
freeze on the goal. A literature-filing batch that touches neither 2023/246 nor
Lane A does not run "under this constraint" and is therefore not covered by
that refusal.

**Disclosure.** That is an interpretive Coordinator ruling made here, not a
self-evident reading of the record, and it is recorded as such so a reviewer
can contest it on the merits. **Lane A itself stays deferred**, exactly as
`DEC-20260805-79d745` left it. Nothing here lifts that deferral, resumes
`EXP-MLDSA-3f7ab2`, or changes `H-MLDSA-d1e509`'s `inconclusive` status.

## 7. D5 — the recorded commit pointers are orphaned by a rebase, not wrong

An earlier draft of this report listed two commit-pointer discrepancies as
*unverified observations*, because this task has no git access. The dispatching
session then ran the git-enabled check and returned a verified explanation, so
they are no longer observations — they are a finding, and it is the one item in
this reconciliation that is a real process failure rather than a clerical one.

**The pointers were CORRECT when written.** A later rebase replayed the branch,
rewrote the commits, and orphaned the originals. The recorded shas became
unreachable from `origin/main`; the content survived byte-identical.

### The two chains

| | Orphaned original (recorded in the ledger) | Replayed, on `origin/main` |
|---|---|---|
| chain base | `8aca58a23` | `1245602e1040f3dfcfea556fc52d0db2a0becb6a` |
| snapshot | `8242344ce106e324e3f42e5b163061a251b7e9f9` @ 17:38:44 | `f44ffbad97856fc9170f89ce8684639427f1e1be` @ 17:52:11 |
| reviews | `4f080b385` @ 17:48:40 | `aa1567c2fe7bc75ec4284b1523e7d7cc5882b96b` @ 17:52:11 |
| ledger | not checked — not asserted either way | `c37bb2c9d7d6b66cb9481cc049c91eee1bdf04aa` @ 17:52:11 |
| ancestor of `origin/main`? | **no** (`git merge-base --is-ancestor`) | yes |
| cited by | `EV-MLDSA-faf2ec.snapshot_commit` (`8242344ce…`); `DEC-20260805-0d59ff.context` "Reviews at 4f080b385" | this report §1 |

Both orphaned commits are real, carry the *same subject lines* as their
replayed counterparts, and chain to each other in the same
snapshot → reviews order. **The ordering fact of §1 holds on both chains.**

### Why this is demonstrably a rebase

- The three commits on `main` all carry the **identical** committer timestamp
  `2026-08-05T17:52:11-07:00` — the signature of a replay. The orphaned
  originals carry distinct, earlier, plausibly spaced timestamps (17:38:44,
  17:48:40).
- `8242344ce` changed exactly the same 6 paths as `f44ffbad9`; `4f080b385`
  changed exactly the same 3 paths as `aa1567c2f`.
- **Blob-level identity, not just path identity:** `corpus_dedup_report.md`,
  `receipt.yaml` and `proposed_kn_lit_entries.md` are **byte-identical** across
  the two chains (same blob sha; e.g. `receipt.yaml` =
  `6115397541932e9b896d2fb54942a5b72f5dc3bd`).

### This corroborates D1

`8242344ce` did **not** contain `snapshot-receipt.json` either. D1 stands on
**both** chains: the receipt was never written, and the rebase did not eat it.
That forecloses the otherwise natural hypothesis that D1 is an artifact of this
same rebase. D1's disposition is unchanged — strengthened, not altered.

### Why it matters, and what it does not touch

This is precisely the failure mode AGENTS.md forbids by name: "Rebasing a
branch that carries pushed run records is forbidden: it rewrites the commits
those records were archived in, and a run receipt whose commit no longer exists
is not reproducible." CLAUDE.md records the same failure as having already cost
five goals unresolvable `latest_verified_commit` values
(`CORR-20260802-a1f151`). GOAL-MLDSA-001 BATCH-001 is another instance, and the
cost here is concrete: two committed, immutable ledger records cite shas no
reader can resolve from `origin/main` without the mapping above.

**It does not weaken any BATCH-001 conclusion.** CLAUDE.md binds archive
receipts to **content first** and treats commit reachability as advisory — an
archive whose commit cannot be reached is content-verified against declared
hashes. Here that check is as strong as it gets: identical blob shas. The
reviewers read exactly the bytes that are on `main` today. `EV-MLDSA-faf2ec`,
`DEC-20260805-0d59ff` and the five KN-LIT entries stand unchanged and
unqualified.

**No correction record is warranted and neither record is edited.** A
`correction` asserts a prior value was incorrect; these were correct when
written. The remedy is this disclosure — recorded sha and reachable equivalent
side by side in `DEC-20260810-689473` — so a future reader can resolve either
pointer.

### Blast radius: checked and counted — 2 orphaned of 4 pointers

The rebase was **scoped to the BATCH-001 chain**. Four pointers were checked
with git; two are orphaned.

| Pointer | Recorded in | Scope | Ancestor of `origin/main`? | Verdict |
|---|---|---|---|---|
| `8242344ce106e324e3f42e5b163061a251b7e9f9` | `EV-MLDSA-faf2ec.snapshot_commit` | BATCH-001 snapshot | **no** | orphaned — mapped above |
| `4f080b385` | `DEC-20260805-0d59ff.context` | BATCH-001 reviews | **no** | orphaned — mapped above |
| `31bc801c6` | `DEC-20260805-4843d6.context` | BATCH-66b482 reviews | yes | reachable, no action needed |
| `7ef705ca51c5861a14461085967413209a7934da` | `GOAL-MLDSA-001.latest_verified_commit` (set by this task) | BATCH-214d98 ledger | yes | reachable, no action needed |

BATCH-66b482's review pointer being reachable is a real tightening, not just a
loose end closed: it **bounds the damage**. The rebase rewrote the BATCH-001
chain and stopped there, so this goal has exactly two unresolvable recorded
shas and both are mapped in this section. Without the check, the honest
position would have been that an unknown number of this goal's pointers might
be orphaned.

This is a counted result over the four pointers **actually checked**. It is not
generalized to any pointer nobody checked. **No pointer follow-up remains
outstanding** — in particular, the 31bc801c6 question is answered here and
should not be re-opened.

**Not checked:** whether a pre-rebase equivalent of the ledger commit
`c37bb2c9d` exists (not reported, not asserted). No pointer outside the four
above was examined, and nothing is claimed about any of them in either
direction.

## 7b. Other items open and not discharged here

The goal's `campaign_budget.budget_risk_note`
requires an explicit amendment if BATCH-001 consumed materially more than a
small fraction of its 9000s of card ceilings. Wall-clock consumption for
BATCH-001, BATCH-66b482 and BATCH-214d98 is not recorded anywhere this task
could read, so it is **not** estimated and is carried forward as a precondition
on the next batch.

## 8. What this task did NOT do

- **Did not run git, and had no shell.** Every commit sha, parent, date,
  subject, changed-path set, blob sha, ancestry result, dispatcher exit code,
  and rejection message came from the dispatching session — in two rounds, the
  second being the orphan and blob-identity check in §7, which this task
  requested after noticing the pointer discrepancy and could not resolve
  itself. All of it is recorded at that confidence. Nothing was re-derived and
  nothing was invented.
- **Did not commit anything.** The dispatching session performs and verifies
  the single isolated Coordinator ledger commit covering all five declared
  paths. Until its post-commit verifier accepts that commit, nothing here is
  durable or official.
- **Did not mint any identifier.** `DEC-20260810-689473` and
  `TASK-20260810-56605e` were pre-allocated and verified free by the
  dispatching session. No `BATCH-*`, `KN-*`, `EV-*`, or further `TASK-*` ID was
  minted; the follow-on batch is described by objective only, for its
  dispatcher to mint with `tools/allocate_id.py` and `--check` before use.
- **Did not retroactively mint `EV-MLDSA-7e91a4` or `DEC-20260805-3d5f82`**, and
  did not remap `EV-MLDSA-faf2ec` or `DEC-20260805-0d59ff` (AGENTS.md rule 15).
- **Did not fill any `archive` block.** `commit_sha`, `parent_sha`,
  `path_sha256` and `record_ids` are exactly as found. Filling them would
  assert a verification that did not occur.
- **Did not write into `knowledge/`**, did not edit `KN-LIT-4f3b80` or any
  other filed entry, did not create any `KN-*` record, did not touch
  `knowledge/INDEX.md`.
- **Did not change any hypothesis status**, any claim tier, any evidence
  record, or `RQ-MLDSA-001`.
- **Did not reopen, revisit, or relitigate** `DEC-20260805-0d59ff`, including
  its `gate_2` ruling on the Jendral values, and did not adjudicate the
  `KN-LIT-4f3b80` title-field concern — that stays routed to an append-only
  `/curate-knowledge` correction pass.
- **Did not lift the Lane A deferral** or authorise any work requiring ePrint
  2023/246.
- **Did not record any attestation.** None was obtained. Nothing here is
  admissible toward the AGENTS.md rule 13 closure quorum (itself suspended).
- **Did not reconcile BATCH-66b482 or BATCH-214d98.** Neither has a
  `dispatch_queue.json` in the working tree; whether they ran without one, or
  their queues were never committed, was not investigated and is not asserted
  either way.
- **Did not touch `dispatch_queue_path`, `active_hypothesis_ids`, `status`, or
  `campaign_budget`** in the goal record, for the reasons given in §5 and §6.
