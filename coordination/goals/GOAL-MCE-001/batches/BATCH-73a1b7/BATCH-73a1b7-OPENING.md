# GOAL-MCE-001 BATCH-73a1b7 — opening

**Goal:** GOAL-MCE-001 · **Questions:** RQ-MCE-e65b3c, RQ-MCE-3f7c02,
RQ-MCE-f8fca0 · **Opened:** 2026-08-09
**Opened by:** `GOAL-MCE-001.next_action` as recorded by `DEC-20260808-a67816`
(`next_actions` item 1; rationale D-4, D-5, D-9).
**Opening decision:** `DEC-20260809-cb25a0`.

This batch corrects this program's own record. **It designs no experiment,
forms no hypothesis, runs no solver, and asserts nothing about Classic
McEliece's security in either direction.** Claim-tier ceiling stays **TOY**.
`active_hypothesis_ids` stays **EMPTY**. Nothing here is admissible toward any
AGENTS.md rule 13 attestation, and none is recorded.

**This opening was written by a Coordinator-only session with no Bash, no
network, and no subagent dispatch.** No executor, validator, red-team or
reviewer session has run in this batch. Every statement below that would
require execution or retrieval is attributed to the record that carries it.

---

## 1. The head deliverable

**`TASK-20260809-14785b` — complete the boundary correction by supersession.**

`DEC-20260808-a67816` D-5 is the operative finding this batch discharges:
BATCH-a68f79's correction of arXiv:2304.14757's boundary **quoted the
Goppa-exclusion sentence and stopped at the full stop**. In the source the
exclusion is:

- **phase-scoped** — it is the **FILTRATION** part of the attack that fails,
  and the authors expect the Gröbner phase to remain polynomial;
- **present-tense** — "right now this part of the attack does not work at all";
- **explicitly not a proof** — "does not represent a proof … but rather an
  intuition about what hampers it";
- **conjectured to fall** — Goppa codes "should eventually be attacked in
  polynomial by some variation the attack that has been given here".

None of the three superseding sites carried any of it. `RQ-MCE-3f7c02` instead
titled the boundary "STRUCTURAL", called conjunct 1 "the decisive one", and
stated that conjunct 1 "settles applicability before any rate arithmetic is
performed". That reading runs **in one direction** on the axis this campaign
turns on — toward dismissal of the structural line — which
`BATCH-001-OPENING.md` §7 defines as this campaign's failure condition,
symmetric with alarm.

The completion is `ledger/questions/RQ-MCE-f8fca0.yaml`: a **clause-scoped
supersession** that carries all four passages verbatim with their loci and
provenance, and replaces `RQ-MCE-3f7c02.replacement_constraint` with a
completed constraint. It **edits nothing**.

**`RQ-MCE-3f7c02` and `KN-LIT-c41d8b` STAY IN FORCE.** They are not withdrawn,
not retired, not replaced, and not edited. `DEC-20260808-a67816` D-4 upheld
them: the rate-scoped framing genuinely was wrong, every affirmative statement
they make is verbatim correct against the source, and no superseding site
re-installs the rate-scoped reading. D-5 is explicit that withdrawing them
would restore a worse record. What is superseded is a small, named set of
clauses — see `RQ-MCE-f8fca0.superseded_clauses`.

**Discharged in this session.** `TASK-20260809-14785b` is recorded `completed`
in the queue because the Coordinator authored the record directly, as
`DEC-20260808-a67816` `next_actions` item 1 specifies ("a single Coordinator
correction task"). It has had **no independent review**.

## 2. Subordinate scope carried forward — NOT started, NOT dispatched

These are `DEC-20260808-a67816` `next_actions` items 2 and 3. They are named
scope items with **no allocated `TASK-*` identifiers**: this session minted
only the two identifiers it was given, and an unallocated item is not
dispatchable until a Coordinator mints its id with
`python3 tools/allocate_id.py --next handoff --date YYYYMMDD` and writes its
card into `dispatch_queue.json`. They are listed in the queue under
`unallocated_scope_items`, not under `tasks`, so the dispatcher cannot treat
them as ready work.

**SUB-1 — the parsing audit and its regression fixture (executor + reviewer).**
Replace the two regex claim-class audits with ONE script that parses each
`knowledge/**/*.md` frontmatter and tests the tag **LIST** — print the path
when `{'distinguisher','key-recovery'}` is a subset of `set(tags)` — and
**commit the five evasion forms from `VAL-20260808-71bdb1` C-4 as a regression
fixture** inside the repository. Supersede `knowledge/TAG-CLAIM-CLASS.md`
rather than editing it. This is the item that converts `EV-MCE-3d6e9a`'s
`proof_status` from `empirical_only` to an archived counterexample certificate
and thereby discharges the KN-FIND promotion `DEC-20260808-a67816`
`knowledge_promotion` scheduled. It **needs execution capability**, which this
session did not have.

**SUB-2 — the `superseded_by` policy (D-9), as a corpus-wide question.**
`DEC-20260808-a67816` D-9 deferred it here and did **not** settle it: whether
the five superseded originals get that field filled, or whether the corpus
declares the field unused and routes through a supersession index. The
validator called filling it "the single highest-value follow-up in this batch"
and it would let AUDIT-1 drop its most complex stage. It affects other
campaigns, so it is settled as a corpus-wide convention with an independent
reviewer — not by one goal's batch acting alone. **§3 of this opening shows
the forward-pointer question is a special case of it.**

**SUB-3 — the two provenance seams.** `VAL-20260808-71bdb1` S-1a: the arXiv
version **is** recoverable — the PDF's left-margin stamp at the bound sha256
reads `arXiv:2304.14757v3 [cs.IT] 29 May 2023`, closing a gap two artifacts
declared unclosable. `RQ-MCE-f8fca0` records v3 for the passages it carries;
what remains is a superseding note for the artifacts that declare the gap open.
S-1b: `KN-LIT-c41d8b` lines 80-83 and `correction_report.md` §3 present an
abstract block labelled verbatim and bound to sha256 `ebbd94ac…` that contains
LaTeX (`{\em`, `$q \in \{2,3\}$`) the validator reports does not occur in that
PDF (grep count 0). The words are identical and no meaning is affected; the
defect is that a hash-bound verbatim block reproduces bytes that are not at
that hash. **Re-source or re-label by supersession — do not edit.**

## 3. Forward pointers — DECIDED, PARTLY REFUSED, and recorded as this batch's open item

`DEC-20260808-a67816` `next_actions` item 1 requires "installing FORWARD
POINTERS from the three superseded sites, above all BATCH-001-OPENING.md
section 4, which has none at all." The same next action says "new records; edit
nothing." The Coordinator resolved this explicitly; the full reasoning is
`DEC-20260809-cb25a0` D-3 and is summarised here because it governs this batch.

**No in-place edit was made at any of the three sites, and the blocker is not
the same at all three.**

| Site | Blocker | Status |
|---|---|---|
| `coordination/goals/GOAL-MCE-001/batches/BATCH-001/BATCH-001-OPENING.md` §4 | **Hash-bound in a completed archive receipt** | Refused |
| `ledger/questions/RQ-MCE-e65b3c.yaml` | **Hash-bound in a completed archive receipt** | Refused |
| `knowledge/literature/KN-LIT-4c8135.md` | **Pre-empts D-9** | Deferred to SUB-2 |

Sites 1 and 2 are both declared in `path_sha256` of
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/archives/OPENING/opening-receipt.json`
(lines 21 and 20 respectively). Any edit — including a purely additive
annotation that changes no assertion — changes the file's sha256 and
invalidates that receipt's declared hash. CLAUDE.md states that archive
receipts bind to **content** first and that "a content mismatch is still
fatal". This is also precisely defect **C-2** that this goal already recorded
against its own Coordinator eight days ago
(`DEC-20260808-a67816` D-6: the disclosure commit "EDITED THE RECEIPT IN
PLACE, invalidating its declared hash"). Repeating it to advertise a
correction would be the same error while describing it.

Site 3 is **not** hash-bound anywhere in this repository. Its blocker is
different: it is a knowledge entry, immutable under CLAUDE.md rule 2, and the
one field that would carry the pointer is `superseded_by` — the exact field
D-9 deferred as a corpus-wide convention question. Filling it now would settle
a corpus-wide question by fait accompli inside a single-goal batch, which is
the overreach pattern this goal's `known_hazards` already records.

**What the pointer function is discharged by instead.** `RQ-MCE-f8fca0`
carries a `forward_pointer_index`: an explicit site → superseding-record → locus
routing table for all three sites, plus RQ-MCE-3f7c02's own superseded clauses.
`GOAL-MCE-001.question_ids` gains `RQ-MCE-f8fca0`, so the completed reading is
reachable from the goal in one hop and from a grep of `ledger/questions/`.

**What is NOT discharged, stated plainly.** A reader who lands on
`BATCH-001-OPENING.md` §4, `RQ-MCE-e65b3c` or `KN-LIT-4c8135` **directly** still
sees no pointer. That is this batch's named open item. A sibling notice file
placed next to a closed batch's artifacts was considered and declined: it would
reach directory-level readers but not in-file readers, and it would create a
second binding object for one correction — the same hazard D-9 cited when it
declined to re-issue `snapshot-receipt.json`. Inventing a one-off routing
mechanism one batch before SUB-2 decides the general one is the wrong order.
**Revisit condition: SUB-2's settlement.** It decides, corpus-wide, whether
`superseded_by` is filled (and how an edit is reconciled with an archive hash
binding) or whether the corpus routes through a supersession index — and the
answer applies to all three sites at once.

## 4. Gates — BOTH omitted checks are written in, as gate items and not as cautions

`DEC-20260808-a67816` `next_actions` item 5 and this goal's `known_hazards`
both record the finding: **both** of BATCH-a68f79's substantive failures were
found by the two checks its completion gate did not ask for, and scored only
against its four literal gate items that batch would have **passed**. Both are
therefore gate items here, and they bind every task in this batch.

**GATE-A — TRY TO BREAK YOUR OWN CHECK.** No deliverable of this batch may
state that a constraint is enforced, a corpus is clean, or a property holds,
without exhibiting (i) an explicit attempt to construct an input that defeats
the check, with the attempts and their outcomes recorded whether they succeeded
or not, and (ii) a **positive control** demonstrating the check can fire at all.
A check that printed the expected thing has not been scored. "It printed
nothing" is not a result until something has been shown that makes it print.

**GATE-B — READ PAST THE END OF THE QUOTED SENTENCE.** No deliverable of this
batch may quote a source without reading and reporting **what surrounds the
quotation** — at minimum the sentence before and after in the same paragraph,
and the source's own concluding remarks on that point. Where the surrounding
text qualifies, scopes, hedges, or reverses the quoted sentence, that material
is carried **into the deliverable**, not summarised as a caution. Silence is
not permitted: a deliverable states either what the surrounding text says or
that it was not read.

These are checkable, and this opening's own head deliverable is scored by
GATE-B: `RQ-MCE-f8fca0` exists because GATE-B was applied retroactively to
BATCH-a68f79 by an independent session.

## 5. Standing prohibition, carried forward unchanged

**DO NOT re-attempt `iacr:2026/1232`'s PDF by another route.** The 403 is
path-scoped and reproducible, circumvention is forbidden, and AGENTS.md rule 5
makes a blocked route a **recorded outcome**, never negative mathematical
evidence. Unchanged from `DEC-20260803-a5b9b1` and `DEC-20260808-a67816`.

Note also `known_hazards`: `eprint.iacr.org` **abstract** pages returned 200 on
75/75 requests on 2026-08-03; the PDF endpoint is a **different question** and
GOAL-HQC-001 BATCH-001 established it still returns 403. Do not repeat the
retracted "the eprint blocker did not reproduce" claim.

## 6. Batch shape

| Task | Role | Duty | State at open |
|---|---|---|---|
| `TASK-20260809-14785b` | coordinator | **HEAD** — complete the boundary correction by supersession; decide the forward-pointer question | `completed` (this session; **unreviewed**) |
| `TASK-20260809-c30f26` | coordinator | Ledger archive — `RQ-MCE-f8fca0`, `DEC-20260809-cb25a0`, checkpoint, goal head | `queued` |
| SUB-1 | executor + independent reviewer | Parsing audit + committed regression fixture | **unallocated** — no id minted |
| SUB-2 | coordinator + independent reviewer | `superseded_by` policy (D-9) and the forward-pointer mechanism | **unallocated** — no id minted |
| SUB-3 | executor or coordinator | Close the S-1a / S-1b provenance seams by supersession | **unallocated** — no id minted |

`max_concurrent` is 3, matching `GOAL-MCE-001.campaign_budget.max_concurrent`.
Nothing is running: the only dispatchable task is the ledger archive, and an
archive runs alone.

## 7. What would make this batch a failure

Unchanged in kind from `BATCH-001-OPENING.md` §7, and now sharper. This batch
fails if it produces a **confident characterisation of the attack frontier that
the primary text does not support, in either direction**. Two specific ways
that could happen here:

1. **Over-correcting.** `RQ-MCE-f8fca0` carries the authors' conjecture that
   Goppa codes "should eventually be attacked in polynomial". A **conjecture in
   a concluding remark is not a result**, and reading it as one would be the
   alarm-side error — the mirror image of the dismissal-side error D-5 records.
   `RQ-MCE-f8fca0` states this in its own `what_this_does_not_establish`.
2. **Treating a bookkeeping correction as progress on the target.** Three
   batches in, the campaign's primary target is still unopened.
   `iacr:2026/1232`'s body remains unobtained, its complexity claim is still
   only a conjecture in its abstract, and **no distance between any attack
   regime and Classic McEliece's parameters has been computed, because the
   left-hand side does not exist**. The Goppa exclusion of arXiv:2304.14757
   **does not transfer** to `iacr:2026/1232`, whose abstract names binary Goppa
   codes explicitly.

## 8. Budget and state at open

- **Batches:** 3 of 6 after this batch opens.
- **Runs authorized:** 0. No solver has run in this campaign and no experiment
  record exists.
- **Claim tier:** toy. **`active_hypothesis_ids`:** empty.
- **Promotion gates G1-G4:** none addressed, none engaged. This program
  advances no asymptotic-complexity claim of its own. Stated so it cannot be
  misread as gate progress.
- **`latest_verified_commit`:** unchanged at `04c41125a`, with the strict
  binding gap stated in the goal record rather than glossed. **This batch's
  archive commit is not yet verified and no sha is recorded for it.**
- **Reviews in this batch:** **none**. No validator, no red team, no reviewer.
- **Validation state:** `tools/validate_ledger.py` was reported by the
  dispatching session as exiting 0 on this branch **before** these records were
  written ("OK: validated 5430 records, no new violations"). This
  Coordinator session has no Bash and **did not run it**; re-running it after
  this batch's writes is the dispatching session's step, and its result is not
  claimed here.
