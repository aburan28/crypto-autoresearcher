# GOAL-P13-001 — reconciliation-and-repair ledger archive

**Task:** `TASK-20260809-4119f6` · **Batch:** `BATCH-8e1671` · **Goal:** `GOAL-P13-001`
**Decision:** `DEC-20260809-a2f829` · **Date:** 2026-08-09 · **Role:** coordinator

This is the task that `BATCH-8e1671/SCOPE-DECISION.md` ("Recommendation",
steps 1–3) requested on 2026-08-07 and that no session had performed. Step 1
was performed by the orchestrating session, which has git access this role does
not; steps 2 and 3 are performed here.

**It authorises no experiment, spends no compute, and produces no measurement.**

---

## 1. Step 1 — durability verification (performed by the orchestrating session)

Everything in this section is that session's finding, carried verbatim. **This
Coordinator ran no git command and verified nothing about the repository
itself.**

| # | Finding | Verdict |
|---|---|---|
| 1 | Executor snapshot `b7b3240b4266b85af1e0810831a66aa6e3300535` ("snapshot: BATCH-403f13 TASK-241b87 NC2d FC4-NOT-FIRED(gap=0.06) NC2b PASS 3/3 bib found"), parent `d2e3a025ee6dd810cc266af22af1edd45f0e7971`, dated 2026-08-05 | **IS an ancestor of `origin/main`. DURABLE.** |
| 2 | Commit `133f7d47b93b96ce0a3ffc3f4a38b92ae794fd68`, dated 2026-08-05 | **IS an ancestor of `origin/main`**, and is the commit that **ADDED** all four of `DEC-20260804-e19a65.yaml`, `EV-WESO-b6ceff.yaml`, `KN-FIND-4e7a92.md`, `KN-FIND-d1c853.md`. **DURABLE.** |

sha256 at HEAD:

```
DEC-20260804-e19a65.yaml  a203f468e545e3ea36758149ee2b5bda41182fa57665ffb57d19f6fe17a5226d
EV-WESO-b6ceff.yaml       772f822141dc40ecb7f7f156cef16d24d2c960769c5b9970cc646fbf6133b2b8
KN-FIND-4e7a92.md         3800f41d07e5f109d5959e369520c68838b6d018768fce731660dae5575868ed
KN-FIND-d1c853.md         6cfadb1b724397f27b2a8e56bb855babe5c09d24befcaad3f5527d53c7d462dc
```

Independent corroboration noticed while reading, and checkable:
`tools/schema_supersession_registry.yaml` records the superseded
`EV-WESO-b6ceff.yaml` at sha256 `772f8221…f6133b2b8` — **the same bytes** the
orchestrating session reported at HEAD. Two independent readings agree.

**The conclusion that follows, and it is two conclusions, not one:**

- Because fact 1 holds, the BATCH-403f13 **measurements and reviews are durable
  committed evidence**. Re-running NC2d-PROPER, NC2b-SLOPE or the bibliographic
  subtask would spend budget re-answering already-reviewed questions. **They
  were not re-run.**
- Because facts 4–6 hold (below), the 2026-08-04 **archive is not an official
  disposition** — and because fact 2 holds, it also cannot be deleted or
  edited. The available instrument is **supersession**, which is what
  `DEC-20260809-a2f829` is.

---

## 2. The seven defects and their dispositions

| ID | Defect | Disposition |
|---|---|---|
| **D-1** | No commit receipts for BATCH-403f13's own two archive tasks | **`superseded_not_run`** — receipts reported **MISSING**, not manufactured |
| **D-2** | `decision: support_scoped`, outside the nine-value template vocabulary | **Repaired by supersession** — this decision uses `supersede` |
| **D-3** | Claimed hypothesis-status transition never applied to `H-WESO-001` | **Claimed transition repudiated; correct entry appended** |
| **D-4** | `ledger/goals/GOAL-P13-001.yaml` never advanced | **Repaired here** — head advanced, budget accounting corrected |
| **D-5** | Promoted KN-FIND content ≠ the binding schedule | **Scheduled entry shipped; the two that shipped are narrowed** |
| **D-6** | No handoff record for any BATCH-403f13 task, incl. the named producer | **Partially repaired; remainder MISSING** |
| **D-7** | Item (4), the substantive item, genuinely open | **Confirmed open; made the goal's single next action** |

### D-1 — the two archive receipts

`TASK-20260804-7cb2d2` (snapshot) and `TASK-20260804-bf4dce` (ledger archive)
are still `"state": "queued"` in BATCH-403f13's own `dispatch_queue.json`, and
no `archives/` directory exists under that batch. **Those two tasks were never
run.**

`archives/TASK-20260804-7cb2d2/snapshot_commit_receipt.json` and
`archives/TASK-20260804-bf4dce/ledger_commit_receipt.json` **DO NOT EXIST AND
ARE REPORTED MISSING. No receipt was written, reconstructed or back-dated.** A
receipt records that an event happened and was verified; writing one now for a
task that did not run would be a fabricated run record under AGENTS.md rule 9,
and it would be the worse failure precisely because it would be
indistinguishable from a genuine one.

What covers the gap, and what does not: the work those tasks would have
committed exists and is **content-verified** by facts 1–3, which is what
CLAUDE.md's content-first archive-receipt rule was designed for. What is **not**
recovered is the receipt's own attestations — the declared parent, the exact
declared path set, and the confirmation that the commit changed those paths and
no others. Those are not asserted. The Validator's CHK-1 partially covers the
last of them by its own route (`git show --name-only` showing the snapshot
commits all 21 declared artifacts); that is a reviewer's check, cited as one.

### D-2 — the decision vocabulary

`support_scoped` is not among `approve | revise | replicate | expand | support |
weaken | reject_scoped | pause | supersede`. The breach was **not cosmetic**:
`support_scoped` reads as a support decision, and a support decision on
replicated/strong evidence carries a mandatory promotion trigger and invites a
move toward `supported` that the promotion gates forbid. It was paired with the
phrase *"campaign advances to completed-with-open-items state"* — not a status
this programme has, not a status any record ever carried, and one that would if
read literally overstate a goal whose criterion 1 is unmet. **That phrasing is
expressly repudiated.**

### D-3 — the unapplied transition

`DEC-20260804-e19a65` narrates a move from
`supported_conditional_qualified_L5_mechanism_inconsistent` to
`supported_conditional_qualified_L5_mechanism_consistent_heuristic1_unvalidated`.
**Neither string is a status this programme uses**, neither appears in
`H-WESO-001`, and the transition was never applied anywhere. It is
**repudiated, not adopted in any form**.

In its place, `H-WESO-001.status_history` receives **one appended entry**
citing `DEC-20260809-a2f829` with `transition: none`, state `analyzed`, and a
note covering the measurements, both reviewer verdicts in full, the NC-3/NC-6
infrastructure failure, and the gate-by-gate reason nothing moves. **The `status`
field is untouched and still reads `analyzed`.**

Why nothing moves, stated once: L5 is a modelling assumption of *this
programme's own cost model*. The theorem's conditional dependence is
**Heuristic 1**, which has never been tested. Gate 1 (proof decomposition) —
does not exist. Gate 2 (validated numbered heuristics) — the binding gap.
Gate 3 (concrete-cost honesty) — this batch *adds* an unpaid item (α = 1.1321
propagated nowhere) rather than closing one. Gate 4 (independent
`review-breakthrough` at max) — **non-degradable and unavailable in this
harness**, and not claimed.

### D-4 — the stale goal head

Repaired in `ledger/goals/GOAL-P13-001.yaml`: checkpoints appended for
BATCH-403f13, BATCH-8e1671 and this reconciliation; `current_batch_id` →
`BATCH-8e1671`; `dispatch_queue_path` → BATCH-8e1671's queue with the old path
moved into `previous_dispatch_queue_paths` **with its state**;
`latest_verified_commit` → `133f7d47b9…` with a note stating exactly what was
and was not verified; `last_decision` → `DEC-20260809-a2f829`; `updated_at` →
`2026-08-09`; `status` → `paused`; and the stale `next_action` **replaced
entirely**.

Budget accounting corrected: `batches_consumed` 3 → **5**, itemised, marking
BATCH-403f13 as having spent Executor budget and BATCH-8e1671 as not;
`batches_remaining` → `not_applicable` (a remaining count against a null cap is
meaningless, and the residual `1` was an artifact of the retired cap of 4);
`total_wall_clock_seconds_consumed` → **`NOT_ESTABLISHED`**.

### D-5 — the knowledge promotion

`DEC-20260802-48c72c` fixed this slot's content **in advance** as the estimator
lemma and intercept/slope pairing rule. What shipped was a cost formula
(`KN-FIND-4e7a92`) and a walk-length relation (`KN-FIND-d1c853`). **The
scheduled entry was never shipped — a third consecutive non-delivery.**

- `KN-FIND-9ee5ed` **ships the scheduled content**, reproduced faithfully:
  durable claim, both instances, `proof_status: derivation`, `proof_refs` the
  same as `EV-PEC-857664`'s, **and no `c` value**. No new mathematics.
- `KN-FIND-e87720` **narrows** the two that shipped. Both remain committed,
  immutable and unedited; the narrowing lives in the new entry.

Also recorded there: `KN-FIND-d1c853` reuses the phrase **"pairing rule"** for a
completely different object (walk length vs smooth-norm pair count) than the
scheduled estimator discipline. A corpus where one phrase denotes two unrelated
objects will be miscited, so the collision is named in both new entries.

`knowledge/INDEX.md` is **not written or staged** — it is `.gitignore`d and
rebuilt on demand (CLAUDE.md; `.gitignore` line 134). This departs from the
literal wording of `DEC-20260802-48c72c`'s binding requirement, which predates
that rule, and is flagged rather than silently done.

### D-6 — the missing handoffs

**Repaired:** the evidence's provenance. `EV-WESO-556063` names
**`TASK-20260804-241b87`** — the task that actually produced the runs, named by
the receipt, both manifests and both review reports — as producer, and this
reconciliation has its own handoff record.

**MISSING and staying MISSING:** the seven BATCH-403f13 handoff records. Their
task cards are fully specified inside `BATCH-403f13/dispatch_queue.json`
(objective, inputs, constraints, deliverables, artifact paths, inference block,
budget, completion gate), so the authorisations are traceable even though the
ledger files are absent. Back-filling `ledger/handoffs/` entries dated
2026-08-04 from a 2026-08-09 session is refused.

**`TASK-20260804-eacb99` is unexplained.** This decision cannot establish what
it was, who authorised it, or whether it existed as anything other than a value
typed into one field. Reported as an unresolved provenance gap
(`DEC-20260809-a2f829` open item OI-2).

### D-7 — the substantive item

NC-3/NC-6 has never successfully executed once across the campaign: unrun in
BATCH-001, unrun in BATCH-002/003, `failed_infrastructure` in BATCH-403f13
("Executor subagent returned empty result (no text output, no artifacts)").
FG-1 never ran, no pilot statistic exists, `P0_predicted` was never computed.

**Per AGENTS.md rule 5 this is not evidence about Heuristic 1 in either
direction.** It is the reason gate 2 is unsatisfied, the trigger for the pause,
and the entirety of the goal's single next action.

---

## 3. Terminal status: `paused`

The goal's own `status_note`, `closure_requirements` and
`pause_condition_watch` pre-committed on 2026-08-02 that after BATCH-004 the
status becomes `paused` or `closed_at_budget`, **never `completed`**.
BATCH-403f13 **was** BATCH-004 in substance — its own design report self-labels
`batch_number: 4`. The call came due on 2026-08-05 and is made now.

**Why `paused` and not `closed_at_budget`.** `closed_at_budget` asserts the
budget ran out, and that cannot be asserted on either axis:

- **Batch count** — `maximum_batches` is `null` (**no cap**), set that way on
  the user's explicit direction of 2026-08-02. A campaign with no batch cap
  cannot close at a batch budget.
- **Wall clock** — `total_wall_clock_seconds` is 21600 and was expressly *not*
  raised by that amendment. **The total consumed against it is NOT
  ESTABLISHED.** The orchestrating session did not establish it, this role
  cannot compute it, and the figures on record are *run* times, not campaign
  time. Reported as not established rather than asserted either way.

**The triggering pause condition is the third:** *"A definitive infrastructure
or dependency blocker prevents the next approved task."* The next approved task
is NC-3/NC-6 against the frozen `EXP-P13-NC36`; it failed at infrastructure and
the Heuristic-1 tail is genuinely unanswered. Pause condition 2 also stands,
triggered for criterion 1 by `DEC-20260802-48c72c` and unaddressed by this
batch.

**`completed` is forbidden and no manoeuvre around it was attempted.**
Criterion 1 is genuinely unmet on the numbers — the defensible modelled span is
13.9429–16.6210 bits against bands of 2.2309 and 3.5133 bits. The suspended
three-model quorum is **not invoked**, **no attestation is recorded**, no
`completion_quorum` block is written, and the `PRE_QUORUM_GOAL_IDS` exemption is
**not used**. Equally, `paused` is not being used to understate a goal that met
a criterion — it did not meet one.

**Single next action:** one successful Executor run of NC-3/NC-6 against the
existing frozen contract `EXP-P13-NC36` (schema alias `EXP-PTH-48eee1`), FG-1
first and alone, with the feasibility gate stated so it cannot be misread — an
FG-1 failure, an unvalidatable sampler, or a second empty return **is an
infrastructure/feasibility outcome and never evidence about Heuristic 1**. The
precondition is that whatever produced the previous empty Executor result be
addressed before re-dispatch; re-dispatching unchanged is how one harness
failure becomes two and then gets mistaken for a pattern in the science.

---

## 4. Files written and edited

**Written (new records):**

- `ledger/handoffs/TASK-20260809-4119f6.yaml`
- `ledger/evidence/EV-WESO-556063.yaml` — supersedes `EV-WESO-b6ceff`
- `ledger/decisions/DEC-20260809-a2f829.yaml` — supersedes `DEC-20260804-e19a65`
- `knowledge/findings/KN-FIND-9ee5ed.md` — the scheduled entry, discharged
- `knowledge/findings/KN-FIND-e87720.md` — the narrowing record
- `coordination/goals/GOAL-P13-001/batches/BATCH-8e1671/tasks/TASK-20260809-4119f6/reconciliation-report.md` (this file)

**Edited (the only two in-place writes permitted):**

- `ledger/hypotheses/H-WESO-001.yaml` — **one appended `status_history` entry**;
  `status` left at `analyzed`
- `ledger/goals/GOAL-P13-001.yaml` — goal-head advance and terminal status

**Not edited, by design:** `DEC-20260804-e19a65`, `EV-WESO-b6ceff`,
`KN-FIND-4e7a92`, `KN-FIND-d1c853`, every run artifact, every review report,
every experiment specification, and `BATCH-403f13/dispatch_queue.json`.

---

## 5. Everything that could NOT be established, in one place

1. **The two BATCH-403f13 archive receipts.** Do not exist. Not written.
2. **The seven BATCH-403f13 handoff records.** Do not exist. Not written.
3. **What `TASK-20260804-eacb99` was.** Unresolved.
4. **Total campaign wall clock against the 21600 s ceiling.** Not established.
5. **Whether the `phi(ell)` gloss in `KN-FIND-4e7a92` is wrong.** Raised as a
   **SUSPECTED** defect and expressly **not adjudicated** — see §6.
6. **Whether the primary-minus-null gap crosses 0.15 above `ell = 211`.**
   Unmeasured; the pre-registered no-trend check does not cover it (RT-OBJ-A).
7. **The baseline constant `k`.** Still unquantified after four batches: three
   sources retrieved, abstracts only, none states it.
8. **Whether `alpha ≈ 1.13` persists at larger `p`.** Three primes, all
   `≤ 2^40`, the highest-leverage one re-used committed data.
9. **Probe-verified model identity for any BATCH-403f13 task.** All record
   `fallback_used: true`, `model_verified: false`; the `review-adversarial`
   xhigh requirement is **UNVERIFIED**, never met.

---

## 6. Open item raised, NOT adjudicated

`KN-FIND-4e7a92` glosses `phi(ell) = ell − 1` as the *"number of distinct roots
of Phi_ell counted with multiplicity in the supersingular case"*. The classical
modular polynomial `Phi_ell(j, Y)` has **degree `ell + 1` in `Y`**, and the
supersingular `ell`-isogeny graph is **`(ell + 1)`-regular**, so the natural
root count is `ell + 1`; and `phi` with value `ell − 1` is standard notation for
**Euler's totient** at a prime, a different object from a root count.
Corroborating but **not deciding**: the BATCH-403f13 red-team report's own OBJ-4
reads `n_distinct_roots = ell+1 or ell+2` off `raw-result.json`.

**This is recorded as a SUSPECTED defect requiring an independent reviewer. The
Coordinator does not adjudicate it.** Deciding whether a formula in the corpus
is mathematically wrong is a review act on a mathematical claim, and this role
neither originated nor reviewed that formula. Asserting the defect settled would
be exactly the overreach this reconciliation exists to correct; asserting the
formula sound would be worse.

It is a **further and independent** reason the entry's claim is narrowed by
`KN-FIND-e87720` — a narrowing that stands on provenance grounds whatever the
answer turns out to be. Routed as `DEC-20260809-a2f829` open item **OI-1**, next
action **NA-2**. If it is wrong, the remedy is a superseding knowledge entry
under a new id, never an edit.

---

## 7. What was deliberately NOT done, and why

| Not done | Why |
|---|---|
| Re-run NC2d-PROPER / NC2b-SLOPE / the bibliographic subtask | Executed under contracts frozen before any datum, snapshot-archived into a commit that is an ancestor of `origin/main`, reviewed twice with no execution defect found. Re-running is the duplicated-work failure mode the Coordinator's own checklist forbids at question 1. |
| Write the two missing archive receipts | They record events that did not happen. AGENTS.md rule 9. |
| Write the seven missing handoff records | Back-dating authorisations from five days later. |
| Edit `DEC-20260804-e19a65` / `EV-WESO-b6ceff` / either KN-FIND | AGENTS.md rule 4 and CLAUDE.md's prohibition on resolving a conflict by editing a record. Both are ancestors of `origin/main`; editing them breaks every archive binding their hashes, including the schema-supersession registry entry pinning `EV-WESO-b6ceff`. |
| Mark BATCH-403f13's unrun archive tasks `completed` | Falsifies a coordination record. |
| Move `H-WESO-001` off `analyzed` | No promotion gate is newly satisfied and gate 4 is unavailable. |
| Move any `c` value, margin row or `concrete_threat_nist1` | Nothing in this batch bears on them; all eight mandatory attachments and twelve standing prohibitions of `DEC-20260802-48c72c` remain in force. |
| Mark the goal `completed`, or record any attestation | Criterion 1 is genuinely unmet. Never record an attestation you did not obtain. |
| Use `closed_at_budget` | Neither budget axis can be shown exhausted. |
| Write `knowledge/INDEX.md` | Generated and `.gitignore`d; rebuilt on demand. |
| Promote the KN-TECH candidate (null-object control on an *explanation*) | Recorded as "to be judged in BATCH-004, not pre-approved". It has no producer artifact in this batch and no independent review. Carried as an unjudged candidate, not dropped. |
| Adjudicate the `phi(ell)` question | See §6. |
| Run `tools/validate_ledger.py`, or any git command | This role has no shell. The orchestrating session runs the validator afterwards and reports failures back. |

---

## 8. Durability

**Nothing in this task is durable evidence yet.** These are working-tree
artifacts until the orchestrating session's commit is accepted by the
post-commit verifier and the branch is pushed with an open or refreshed PR
against `main` naming `EV-WESO-556063`, `DEC-20260809-a2f829`,
`KN-FIND-9ee5ed`, `KN-FIND-e87720`, `TASK-20260809-4119f6`, `H-WESO-001` and
`GOAL-P13-001`. The goal record's own `latest_verified_commit_note` says so,
and the next Coordinator ledger archive advances that field.
