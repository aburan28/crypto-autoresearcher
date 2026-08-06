# BATCH-fca4e2 Scope Decision — GOAL-ECTD-001 / EXP-ECTD-001

- **Date:** 2026-08-06
- **Role:** coordinator (standing authority under the already-launched,
  already-budgeted GOAL-ECTD-001 campaign; continuation of `/coordinate-research-goal`,
  not a new campaign requiring fresh sign-off)
- **Session provenance:** requested_policy `coordinator-orchestration-code`;
  resolved_model_id `claude-sonnet-5`; fallback_used `true`; fallback_reason
  "this harness cannot resolve policy aliases — every role in this harness
  instance is served by the same backend"; model_verified `false`
  (`python3 -m orchestration.adapter doctor --probe` not run this session).

## 1. The discrepancy: what is actually true

The brief's three possibilities were (a) approved-then-reverted-and-goal-stale,
(b) the goal's `next_action` is simply wrong, (c) approval happened in a
review artifact that never updated the spec's own `status`/`approved_by`
fields, itself a defect. Having read the full BATCH-001/BATCH-002 record,
**the answer is closest to (c), with a mitigating fact and a real residual
defect that this batch corrects.**

### 1.1 The spec was never edited to `approved` — by an existing repo convention, not oversight

`experiments/EXP-ECTD-001/specification.yaml` carries, unmodified since the
BATCH-002 design freeze:

```
status: review_required
approved_by: null
approved_by_note: >-
  Frozen at review_required with approved_by null until independent
  validation TASK-20260731-052 and ledger archive TASK-20260731-053.
  Do not execute before status: approved.
```

Taken alone, this note commits to a stronger reading than what actually
happened: it says status itself should become `approved`. It never did.

### 1.2 A real, committed, git-verified Coordinator approval decision exists

`ledger/decisions/DEC-20260731-013.yaml` (`decision: approve_experiment_for_execution`,
`decided_by: coordinator`, `target_ids` including `EXP-ECTD-001`) explicitly
states the frozen spec/hypothesis blobs are deliberately **not** rewritten
after their TASK-20260731-051 snapshot, "same pattern as EXP-DS-001," and
that "execution is unblocked by this DEC and EV-ECTD-002. Do not read
`approved_by:null` as lack of approval."

This decision is **durably committed and verified**, not merely a working-tree
claim:
`coordination/goals/GOAL-ECTD-001/batches/BATCH-002/dispatch_queue.json` task
`TASK-20260731-053` carries a filled-in `archive` block —
`commit_sha: 80013bf311348fc5e5b9a78d2b60615220b161b4`,
`parent_sha: fe09a69194b062bce004a5ecc7c1ee608fc4b69f`,
`record_ids: [EV-ECTD-002, DEC-20260731-013, GOAL-ECTD-001]` — and
`coordination/goals/GOAL-ECTD-001/batches/BATCH-002/dispatch_plan.json` records
gate `"completed_archive_commits_verified": true` for that terminal task set
(all five BATCH-002 tasks, `049`–`053`, `state: completed`). The receipt blob
`archives/TASK-20260731-053/ledger-receipt.json` itself still shows
`commit_sha: null` / `verification.status: pending_post_commit` — that is the
expected pre-commit placeholder pattern (a commit cannot contain its own SHA);
the queue's `archive` object is where the *post-commit* verified value lives,
exactly per `templates/research-records.md`'s archive-receipt note ("Do not
put a commit's own SHA into an artifact within that same commit"). So: the
approval decision is real, Coordinator-authored, and independently verified
by the dispatcher against Git.

**This precedent is not invented for ECTD.** `experiments/EXP-DS-001/specification.yaml`
uses the identical "D-1 prophylaxis" pattern (`status: review_required`,
`approved_by: null`, note: "THE NULL IS BY DESIGN... approved_by:null MUST
NOT be read as evidence that the contract was never approved"), and its
approval determination lives in a dedicated Coordinator archive receipt
(`coordination/goals/GOAL-ECDLP-001/batches/BATCH-017/archives/TASK-20260731-017/snapshot_commit_receipt.json`)
with an explicit machine-checkable `APPROVAL_DETERMINATION` field (in that
instance, `"NOT APPROVED"`, with a named REVISE disposition and amendment
cycle — proving the pattern is used honestly in both directions, not only to
rubber-stamp).

### 1.3 The residual defect this batch corrects

The EXP-DS-001 precedent records its determination in a **dedicated archive
task with an explicit, machine-checkable `APPROVAL_DETERMINATION` field**
(`APPROVED`/`NOT APPROVED`), separate from and more legible than an ordinary
decision record's prose. EXP-ECTD-001's approval instead lives only inside
`DEC-20260731-013`'s `approval_note` prose (`decision: approve_experiment_for_execution`
is unambiguous once read, but there is no dedicated, explicitly-named
determination artifact of the EXP-DS-001 kind), and — more importantly —
**this convention is not written into `AGENTS.md` or `docs/task-lifecycle.md`
at all.** It exists only as two ad hoc `approved_by_note` fields on two
experiment specs. `docs/task-lifecycle.md` §5 and `AGENTS.md`'s "Research
states" section describe the experiment status machine
(`draft -> review_required -> approved -> running -> ...`) without
acknowledging that a canonical record's own `status` field may permanently
diverge from the true state. That is exactly the ambiguity this audit was
asked to resolve, and it is a real process defect: an approval that is
durable in git but not durable **in the one place a reader naturally looks**
(the frozen contract's own `status` field) is fragile, even when the
underlying decision is genuine. `GOAL-ECTD-001.yaml`'s `next_action` — itself
written by the same TASK-20260731-053 ledger archive — then flatly says
"execute **approved** EXP-ECTD-001" with no pointer to the DEC-013 side-channel,
compounding the ambiguity for any later reader (including this session).

**Resolution:** EXP-ECTD-001 **is genuinely approved** — the approval is real,
Coordinator-authorized, and git-verified (§1.2) — but the spec's own
`status`/`approved_by` fields are corrected in this same archive to say so
directly, per this task's explicit instruction, rather than perpetuating an
undocumented convention that produces exactly this class of confusion. This
is a bookkeeping/status-field correction only: **no scientific content**
(objective, controls, decision table, budget, success/falsification criteria)
is touched. `frozen`, `frozen_by_task`, `frozen_on`, `archived_by_task` are
left untouched as historical facts about when the *content* was frozen.

The correction is recorded directly in `experiments/EXP-ECTD-001/specification.yaml`
(this file's `status`/`approved_by`/`approved_by_note` only), dated
2026-08-06, citing `DEC-20260731-013` as the substantive approval basis and
this document as the correcting record. A new formal `DEC-*` ledger record
for *this* session's determination (ratifying the standing approval, noting
the correction, and opening BATCH-fca4e2) is minted by `TASK-20260806-411ffd`
(the ledger archive task inside this batch) — this session's write scope does
not include `ledger/decisions/`, so no decision file is created directly here
by design (see Hard constraints in the dispatching brief).

## 2. Pause-condition check (all four, explicit)

1. **Eight-batch budget exhausted without an admissible next mechanism** — NOT
   FIRED. Two of eight batches used (`BATCH-001`, `BATCH-002`); EXP-ECTD-001 is
   an admitted, independently-reviewed, validator-approved next mechanism.
2. **Primary Teske source / approach-adjacent papers unobtainable** — NOT
   FIRED. `knowledge/literature/KN-LIT-7261.md` (`citation_verified: true`,
   `upgraded: 2026-07-31`) records the Teske primary source obtained via
   Wayback Machine mirror after a direct-eprint HTTP 403, with local copy
   `inputs/ECTD-TESKE-20260731/sources/teske-2003-058.pdf` (sha256
   `8d889ae0b1b03f77a9b821aae04b255df235f8abc0831598ded7ff1c723f2646`,
   16 pages) — **verified present on disk this session** via directory
   listing, alongside its `.sha256` companion and an honest `.FAIL` marker
   documenting the failed direct attempt (not a coverup of a missing source).
   This session independently confirmed eprint/arXiv are unreachable from
   this environment too, but that is irrelevant here: the fetch already
   succeeded via an alternate channel *before* this session started, and nothing
   in EXP-ECTD-001 depends on re-fetching it. The one remaining gap,
   KN-LIT-7633 (Dent–Galbraith), is documented `citation_verified: false` with
   an honest fetch obstruction — but it gates only IDEA-20260731-018 (PI-C),
   which is explicitly deferred and out of scope for EXP-ECTD-001
   (`what_this_experiment_is_NOT`). EXP-ECTD-001 (IDEA-016 only) has no
   unresolved source dependency.
3. **Decisive computation exceeds campaign budget after cheaper gates
   exhausted** — NOT FIRED (see §4 flagged ambiguity; not a blocker for a
   first toy screen).
4. **Infrastructure/auth/dependency blocker** — NOT FIRED; no such blocker is
   on record for this environment/spec.

No pause condition is live. User-requested pause: not applicable (no such
request in this thread).

## 3. Decision: OPEN BATCH-fca4e2

EXP-ECTD-001 is approved (ratifying the standing, verified DEC-20260731-013
determination) and BATCH-fca4e2 is opened for its bounded toy execution,
using exactly the four pre-allocated task IDs.

### Claim ceiling (carried forward from the frozen spec, binding on every task in this batch)

Toy-tier presence/absence of a Semaev/FB/Macaulay heavy tail (>=100x class
median, or `d_reg` <= median − 2) under frozen meters, null-control outcomes,
and planted-control validity on 40–56 bit prime-order subgroups, at
`n_bit_range [40,56]`, `min_classes 5`, `min_class_size 64`. **NOT CLAIMABLE
UNDER ANY OUTCOME OF THIS BATCH:** crypto-scale ECDLP exponent improvement;
Teske-class trapdoor existence; path-hiding success; Galbraith conductor-gap
path hardness; reopening H-ISO-001 beyond its short-neighbor scope;
GOAL-ECTD-001 completion. All four asymptotic-claim promotion gates
(`agents/coordinator.md`) remain OPEN. No trapdoor claim, no break, no
completion from this single batch — even a `heavy_tail_hit` branch licenses
only a follow-on path-hiding/detection experiment, never a trapdoor claim
(`H-ECTD-001`, `what_this_experiment_is_NOT`).

### Standing prohibition (verbatim, carried forward)

**Do not read homogeneity or a single outlier as a trapdoor.**

### Rule-9 record (research-direction integrity, AGENTS.md / CLAUDE.md)

- **Candidate/path:** RQ-ECTD-001 family (1) — secret isogeny-aligned factor
  bases / Semaev/Gröbner heavy tails (IDEA-20260731-016 / H-ECTD-001).
- **Cited evidence:** EV-ECTD-001 (literature), EV-ECTD-002 (independent
  review + validator clearance); no empirical runs yet (this batch produces
  the first).
- **Stated rationale:** this is the binding, independently-admitted uncertainty
  for RQ-ECTD-001 family (1) per red-team `TASK-20260731-049`
  (`per_idea_verdicts.IDEA-20260731-016.verdict: admit`) and validator
  `TASK-20260731-052` (`approve_for_execution`, all checklist items PASS).
  Opening BATCH-fca4e2 pursues this lead in good faith rather than
  deprioritizing or steering away from it; nothing here suppresses or
  mischaracterizes the direction.
- **Budget:** `EXP-ECTD-001.budget` (unchanged): `wall_clock_seconds_per_run
  7200`, `total_cpu_hours 40`, `maximum_memory_gb 16`, `maximum_runs 2`.
- **Test boundary:** toy scope only, `n_bit_range [40,56]`, `>=5` classes,
  `class size >=64`; direct enumeration + per-curve GB/Macaulay; no
  crypto-scale correspondence claimed (`scale_relevance.correspondence: null`).
- **Remaining uncertainty:** whether any rare endpoint-specific algebraic
  weakness exists at toy scale before investing in path-hiding; HEUR-ECTD-TAIL-1
  is a test hypothesis only (JMV does not justify Semaev exchangeability).
- **Concrete successor/revisit condition (per decision branch):**
  - `heavy_tail_hit` → next batch opens a dedicated Red Team pass on the
    surviving outlier (per §5 below) before any stronger disposition, then a
    separate path-hiding/detection EXP — never a trapdoor claim from this
    batch alone.
  - `scoped_homogeneity` → forward guidance stands as already named in
    `H-ECTD-001`/`EXP-ECTD-001` (private factor-base precomputation,
    path-hiding, detection, vertical (017) / DDH (018) lanes remain open);
    record as `weaken` pending replication, never `reject_scoped` from one
    unreplicated run (AGENTS.md binding rule).
  - `instrument_void` → harness repair task; explicitly not a mathematical
    negative.
  - `resource_incomplete` → budget-scoped continuation task; explicitly not a
    homogeneity claim.

## 4. Flagged (non-blocking) defects and ambiguities for future batches

- **Campaign-budget vs. experiment-budget units are not reconciled.**
  `GOAL-ECTD-001.campaign_budget.total_wall_clock_seconds = 28800` (8h) for
  the *entire* 8-batch campaign, yet BATCH-002 alone spent ~10500s
  (~2.9h) on coordination/review tasks per their own declared
  `budget.wall_clock_seconds` fields, before any heavy compute ran, and
  EXP-ECTD-001's own frozen budget (`wall_clock_seconds_per_run 7200 x
  maximum_runs 2` = up to 14400s, plus `total_cpu_hours 40` — plausibly
  parallel/sharded) is not obviously drawn from the same pool. Neither
  `AGENTS.md` nor `docs/task-lifecycle.md` states whether
  `campaign_budget.total_wall_clock_seconds` bounds orchestration overhead
  only or also actual Executor compute. This batch proceeds using
  EXP-ECTD-001's own already-reviewed budget (unchanged, per
  `docs/task-lifecycle.md` §5: "Protocol changes after approval require a
  versioned amendment" — a budget reconciliation is not one), and flags the
  ambiguity rather than silently resolving it. A future batch or a ledger
  correction should reconcile these two budget fields explicitly.
- **`ledger/goals/GOAL-ECTD-001.yaml`'s `latest_verified_commit` field
  (`189678cb...`, the BATCH-002 *design* snapshot) was never advanced to the
  BATCH-002 *ledger* archive commit (`80013bf3...`) that actually produced the
  goal file's current content**, even though that commit is independently
  verified (dispatch_plan gate, §1.2). This is consistent with the
  self-reference problem (a commit cannot record its own SHA), and the
  correct value should be filled by the *next* archive that touches the goal
  record — which `TASK-20260806-411ffd` in this batch will do. Flagging so it
  is not silently perpetuated a second time.
- **`ledger/proposals/IDEA-20260731-016.yaml`** still carries pre-revise
  wording (non-blocking per validator `NBO-1`); the binding contract is
  `H-ECTD-001` + `EXP-ECTD-001` at the frozen snapshot, not the proposal file.
  Unchanged by this batch.

## 5. The four pre-allocated IDs are consumed

`BATCH-fca4e2`, `TASK-20260806-983eed`, `TASK-20260806-4455ac`,
`TASK-20260806-5bc785`, `TASK-20260806-411ffd` are opened below (`batch.yaml`,
`dispatch_queue.json`, per-task cards, and `ledger/handoffs/TASK-20260806-*.yaml`).
No Red Team task is added to this batch (the brief names exactly these four
IDs); `TASK-20260806-411ffd` is instructed to schedule a dedicated Red Team
pass in a follow-up batch **before** any disposition stronger than
`replicate` if the outcome is `heavy_tail_hit`, consistent with
`GOAL-ECTD-001.completion_criteria` ("Independent Validator **and Red Team**
admit the decisive package") and `docs/dynamic-subagent-dispatch.md`
("Reserve an independent Reviewer, Validator, or Red Team task whenever a
result could change an ECDLP claim").

## 6. Working coordinator determination (for the record; formal DEC-* minted by TASK-20260806-411ffd)

```yaml
coordinator_decision:
  id: PENDING (minted by TASK-20260806-411ffd at ledger archive; see AGENTS.md rule 14)
  context: >-
    GOAL-ECTD-001 next_action asserted EXP-ECTD-001 was approved for BATCH-003
    while the frozen spec's own status/approved_by fields still read
    review_required/null. Investigation found a real, git-verified Coordinator
    approval (DEC-20260731-013, commit 80013bf3) following an established but
    undocumented repo convention (EXP-DS-001 precedent), not a stale or
    fabricated next_action. The spec's own status field is corrected in this
    archive to remove the ambiguity; no scientific content changes.
  decision: approve
  target_ids:
  - EXP-ECTD-001
  - H-ECTD-001
  - GOAL-ECTD-001
  - DEC-20260731-013
  - EV-ECTD-002
  rationale:
  - DEC-20260731-013 is a genuine, committed, dispatcher-verified Coordinator
    approval (commit 80013bf3, gate completed_archive_commits_verified:true).
  - The undocumented "null is not non-approval" convention created exactly the
    ambiguity this audit resolved; correcting the spec's status/approved_by
    fields now (bookkeeping only) removes it durably rather than deferring it.
  - No pause condition fires (Teske source obtained and on disk; budget not
    exhausted; no infra blocker; no user pause request).
  evidence_refs:
  - ledger/decisions/DEC-20260731-013.yaml
  - ledger/evidence/EV-ECTD-002.yaml
  - coordination/goals/GOAL-ECTD-001/batches/BATCH-002/dispatch_queue.json
  - coordination/goals/GOAL-ECTD-001/batches/BATCH-002/dispatch_plan.json
  - coordination/goals/GOAL-ECTD-001/batches/BATCH-002/reviews/TASK-20260731-049/review_report.yaml
  - coordination/goals/GOAL-ECTD-001/batches/BATCH-002/reviews/TASK-20260731-052/validation_report.yaml
  - knowledge/literature/KN-LIT-7261.md
  limitations:
  - No runs executed by this decision; approval + bookkeeping correction only.
  - Claim ceiling per spec: toy-tier only; see Section 3 above.
  - This session cannot write ledger/decisions/ directly (write-scope
    restricted); the formal DEC-* record is minted by TASK-20260806-411ffd.
  next_actions:
  - Dispatch TASK-20260806-983eed (executor) per BATCH-fca4e2 dispatch_queue.json.
  knowledge_promotion:
    promoted: []
    not_warranted: >-
      This determination is a process/approval correction, not an
      evidence-review decision; no empirical or theoretical finding is
      produced here to promote.
  decided_by: coordinator
  decided_at: '2026-08-06'
  inference:
    requested_policy: coordinator-orchestration-code
    resolved_model_id: claude-sonnet-5
    fallback_used: true
    fallback_reason: this harness cannot resolve policy aliases
    model_verified: false
```
