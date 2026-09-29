# S0 control-plane report — TASK-20260904-f0a889

Declared batch artifact (deliverable 4 of TASK-20260904-f0a889), to be snapshot-archived by TASK-20260904-850ff6 (S1). Not a summary for a parent session.

- **Batch**: BATCH-a40709 · **Goal**: GOAL-SCURVE-137bd9 · **Question**: RQ-SCURVE-960dbd
- **Opening decision**: DEC-20260904-c42007 (approves OPENING this batch; approves no contract and no run)
- **Frozen contract authored**: EXP-SCURVE-3f87f6, `approved_by: null`
- **Role**: coordinator · **Requested policy**: coordinator-orchestration-code · **Runtime**: claude_code
- **Committed state read**: branch `claude/degree-regularity-polynomial-systems-pssesi` at `50258bad7` (as supplied by the dispatch context; **this session ran no git command and did not verify that sha**)

## 0. Claim ceiling this record is written under

`analyzed` at best, never `supported`. **No statement that any curve is safe or unsafe appears in anything authored by this slot, and none is permitted from any slot in this batch.** Arithmetic verification of a published parameter set is a transcription check, not a security evaluation. No asymptotic-complexity claim is proposed, so the four promotion gates are not engaged and are certainly not met.

**This slot asserted nothing about NIST P-224's parameter values.** It authored a control plane. No parameter value, prior verdict, marginal, count or expected value for the audited curve appears in the frozen contract or in any task card; downstream slots are pointed at the committed capsule, the archived audit plan and the retrieved pages **by path**.

## 1. What was authored (the four declared artifact paths, and nothing else)

| Path | What it is |
| --- | --- |
| `experiments/EXP-SCURVE-3f87f6/specification.yaml` | frozen experiment contract, `approved_by: null` |
| `coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/dispatch_queue.json` | finalised queue (one repair, section 4) |
| `coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/tasks/TASK-20260904-f0a889/task-cards.yaml` | fourteen cards, S0–S13 |
| `coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/tasks/TASK-20260904-f0a889/report.md` | this record |

Plus one write inside `write_scope` that is **deliberately not** an artifact path: `ledger/goals/GOAL-SCURVE-137bd9/goal.yaml` (section 3).

### The frozen contract, in one paragraph

EXP-SCURVE-3f87f6 fixes, per in-scope lane (L0; L-EQ, L-FIELD, L-BASE; L-LADDER, L-COMPLETE, L-IND, D3, D6; L-RHO; and the single gated comparison): the quantities to be **computed** (never the values they are expected to take), the guarding controls and the ordering rule that they run on the identical code path **before** any target output is interpreted, per-slot budget ceilings copied from the committed batch design, six stopping rules, eleven invalidation rules (INV-1 … INV-11), the required artifacts by exact path, and the seal ordering. It re-scopes nothing, re-ranks nothing and admits no `out_of_scope` item.

Two contract choices worth naming because they are judgement calls, not transcription:

1. **`preregistered_prediction` is a pointer, not a copy.** The per-lane predictions already exist, frozen, in the archived audit plan (TASK-20260824-53ecc0, bound by the BATCH-ef5b1e snapshot), and the Coordinator's prior is recorded verbatim in `batch.yaml`. Copying predicted values into the contract that the measurement slots read would put a prior answer in front of the producer and create a second, editable copy of a frozen preregistration. The contract cites both sources and **adds no prediction of its own**.
2. **`tail_checks` is empty on purpose.** No distributional claim is in scope: the null family is an instrument check (does the checker fire at a non-degenerate rate), not a reference distribution for a target statistic. A tail check would presuppose the comparison the contract forbids.

The contract also states, as the template requires, why two budget floors are not met: every producer slot meets or exceeds the 600 s per-run floor (S9 is 600 s exactly and runs no computation), and the 8 GB memory floor is **not** met because the committed batch design fixes 2 GB per slot with 4 GB at S5. Those are ceilings fixed before acquisition, not measurements of anything.

## 2. Capability declarations, per slot

Sources: `batch.yaml` `capability_contract` and `task_slots`. Reproduced in each card.

| Slot | Task | Role | network | PARI | arbitrary-precision arithmetic | dispatch-time check owed before it |
| --- | --- | --- | --- | --- | --- | --- |
| S0 | TASK-20260904-f0a889 | coordinator | no | no | no | **none** |
| S1 | TASK-20260904-850ff6 | coordinator | yes (repo transport only) | no | no | none |
| S2 | TASK-20260904-8e3d66 | executor | **yes (source retrieval)** | no | no (no arithmetic at all) | **CAP-1** |
| S3 | TASK-20260904-90ac09 | executor | no | no | **yes** | **CAP-2** |
| S4 | TASK-20260904-fa10f7 | coordinator | yes (repo transport only) | no | no | none |
| S5 | TASK-20260904-7efb23 | executor | no | no | **yes** | **CAP-2** |
| S6 | TASK-20260904-251f65 | coordinator | yes (repo transport only) | no | no | none |
| S7 | TASK-20260904-ad952c | executor | no | no | **yes** | **CAP-2** |
| S8 | TASK-20260904-f4b6ba | coordinator | yes (repo transport only) | no | no | none |
| S9 | TASK-20260904-158442 | coordinator | no | no | no | none |
| S10 | TASK-20260904-cc8dfb | coordinator | yes (repo transport only) | no | no | none |
| S11 | TASK-20260904-abf728 | validator | no | no | conditional (blind re-derivation) | **CAP-3** |
| S12 | TASK-20260904-aa366e | red-team | no | no | conditional (blind re-derivation) | **CAP-3** |
| S13 | TASK-20260904-f9dba7 | coordinator | yes (fetch, push, PR) | no | no | none |

**No dispatch-time capability check is owed before S0, none has been run, and none is recorded as run.** CAP-2 is owed before S3, S5 and S7 — *not* before this slot. Bedrock is prohibited in every slot: no provider, backend, endpoint, fallback or probe may select an identifier containing "bedrock", case-insensitively; refuse before making a request.

## 3. Goal head pointer update

`ledger/goals/GOAL-SCURVE-137bd9/goal.yaml`, exactly two fields changed:

- `current_batch_id`: `BATCH-ef5b1e` → `BATCH-a40709`
- `dispatch_queue_path`: `…/BATCH-ef5b1e/dispatch_queue.json` → `…/BATCH-a40709/dispatch_queue.json`

**No other field was touched** — not `next_action`, not `updated_at`, not `latest_verified_commit`. The head path is **owned by S13**, which binds the durable transition; this write is a findability pointer only and is carried in `write_scope`, not in `artifact_paths`. **S1 must disclose it in its snapshot receipt under `staged_not_in_binding_set`.**

Consequence, stated rather than left for a reader to trip over: the head's `next_action` still reads as the pre-decision text ("ONE ACTION: a Coordinator decision on whether to open a successor batch…"), which DEC-20260904-c42007 has now discharged. Rewriting it is not among the two fields this slot may touch. **It is owed to S13**, which owns the head and must leave exactly one next action. The goal remains `active`; nothing here pauses or blocks it, and `paused`/`blocked` are not permitted statuses.

## 4. The one queue defect found, and the exact minimal edit made

The dispatcher's acceptance of this queue was reported by the driving session, and the two identifiers `EV-SCURVE-b52b57` and `DEC-20260904-8578cc` were minted, `--check`ed and added to S13's task-level `artifact_paths` and `archive.record_ids` before dispatch. **That repair is not redone here and no identifier was minted by this session.**

**Defect (concrete, internal to S13's handoff envelope):** the repair reached S13's *task-level* fields but not its *handoff* envelope, leaving the envelope self-contradicting.

- `handoff.objective` and two `handoff.deliverables` entries instructed S13 to author the evidence record and the closing decision "under a newly minted EV identifier" / "a newly minted DEC identifier", while `handoff.constraints` in the same envelope says **"DO NOT MINT AGAIN"** and names the two identifiers that already exist. An S13 agent following its objective literally would mint two fresh identifiers matching neither `archive.record_ids` nor the task's `artifact_paths` — the archive would then publish records under identifiers its own receipt does not bind.
- `handoff.artifact_paths` listed three paths while the task-level `artifact_paths` lists five, omitting exactly the two ledger record paths the repair added.

**Exact minimal edit applied** (three edits inside S13's handoff object only; no slot renumbered, reordered, re-scoped or re-ranked; no `out_of_scope` item admitted; `max_concurrent` unchanged at 2; nothing minted):

1. `handoff.objective`: "under a newly minted EV identifier" → "under EV-SCURVE-b52b57 (ALREADY MINTED AND VERIFIED FREE BY THE DRIVING SESSION -- DO NOT MINT)"; same substitution for "a newly minted DEC identifier" → "DEC-20260904-8578cc (… -- DO NOT MINT)".
2. `handoff.deliverables[1]` and `[2]`: now name `ledger/evidence/EV-SCURVE-b52b57.yaml` and `ledger/decisions/DEC-20260904-8578cc.yaml` "under the identifier already minted for this archive".
3. `handoff.artifact_paths`: appended `ledger/evidence/EV-SCURVE-b52b57.yaml` and `ledger/decisions/DEC-20260904-8578cc.yaml`, making the envelope match the task-level list. Both paths already lie inside S13's declared `write_scope` (`ledger/evidence`, `ledger/decisions`).

Nothing else in the queue was changed.

**Verification owed, and honestly unmet here:** this session has **no command-execution tool**, so it could not re-run `tools/research_dispatch.py` and **does not claim the edited queue is accepted**. The acceptance figures this session was given — one Ready Task, 11 gates, 13 deferred, 0 terminal — are the driving session's report on the queue **as it stood before edits 1–3**, and are reproduced as a citation, not as a measurement of my own. The driving session must re-run the dispatcher before S1's commit is treated as durable. **Exact revert if it rejects:** restore the three strings/arrays above to their prior wording ("a newly minted EV identifier", "a newly minted DEC identifier", three-entry `handoff.artifact_paths`); the defect then returns and must instead be repaired as a superseding record naming S13.

## 5. Unresolved items — reported rather than guessed at

Each names the exact repair. None was filled in by this slot.

1. **Seal declarations live in `read_scope`/`constraints`, not in `artifact_paths` — a real divergence from `batch.yaml`, already disclosed inline in the queue.** `batch.yaml` says S5, S7, S9, S11 and S12 "MUST DECLARE" their pre-read seals **in `artifact_paths`**; the queue declares them in `read_scope` and in the constraint text instead, with the reason stated (dispatch_queue.v1 gives every artifact path exactly one owning task, and those receipts are owned by S4, S6, S8 and S10). The queue's placement is the only one representable in the schema. **`batch.yaml` governs, so this is a disagreement, and a disagreement is a superseding record, never an edit — to either file.** *Exact repair:* the driving session mints one `DEC-*` recording that the seal-declaration clause of `batch.yaml` is superseded in its placement (not in its force) by schema constraint, citing BATCH-a40709 S5/S7/S9/S11/S12. This slot may not mint and did not.
2. **S11 and S12 `depends_on` is a superset of `batch.yaml`'s.** `batch.yaml` gives both `[S10]`; the queue gives `[S7, S8, S10]`. It is order-preserving (S10 already requires S7 and S8 transitively) and changes nothing about what either reviewer may read, so it is **not** repaired here. It is still a textual divergence and belongs in the same superseding record as item 1.
3. **CAP-2 and CAP-3 are not named as dispatch-time checks inside the S5, S7, S11 and S12 handoff envelopes** (only S2's CAP-1 and S3's CAP-2 are named). `batch.yaml` owes CAP-2 before S3, **S5** and **S7**, and CAP-3 before S11 and S12. *Repair applied where this slot has authority:* every card in `task-cards.yaml` names the check owed before its slot, and the frozen contract's `capability_declarations.dispatch_time_checks` records all four. *Repair still owed:* the dispatcher must actually run CAP-2 before S5 and S7 and CAP-3 before S11 and S12 and record the outcome in the task receipt — a card is a pointer, not a check.
4. **The goal head's stale `next_action`** — section 3. Owed to S13.
5. **`batch.yaml` `created_at` is still `null`**, disclosed there as null-by-capability with the stamp owed to the driving session at the ledger archive. Unchanged and unfillable here.
6. **`EXP-SCURVE-3f87f6` is not approved and no approving decision exists.** The contract's `approved_by` is `null` and stays null. DEC-20260904-c42007 approved opening the batch and explicitly approves no contract and no run. **Approving it is a separate committed Coordinator decision that does not exist**, and a dispatch instruction, a message or a task card is not one. S2, S3, S5 and S7 read the contract as their protocol; whether their runs are *authorized* is that missing decision's question, not this slot's.
7. **This report could not be written to its declared path by this session.** The runtime refused two `Write` calls to `…/TASK-20260904-f0a889/report.md` with "Subagents should return findings as text, not write report files". That is an **operational observation, never negative mathematical evidence**. *What is blocked:* S0's fourth deliverable and, through it, S0's completion gate and S1's staging list — not the batch and not the goal. *What clears it:* the driving session writes this text verbatim to that exact path (no substitute path is permitted; `artifact_paths` names exactly four). *What to re-run:* nothing computational; re-verify the file exists and parses before S1 stages.

## 6. Every value this slot left null, with its reason

| Value | Left | Reason |
| --- | --- | --- |
| `experiment.approved_by` | `null` | **By rule.** No approving Coordinator decision exists; only one can change it. |
| `experiment.hypothesis_id` | `null` | This goal has no hypothesis and this contract creates none. |
| `experiment.provenance.frozen_at` | `null` | No clock. Null by capability under DEC-20260903-9c3e26 ruling_1; stamped by the driving session at the S1 archive. |
| `inputs.capsule_sha256` | `null` | No digest tool. Each measurement slot records the sha256 of the capsule **it** read. |
| `budget.total_cpu_hours` | `null` | The batch design declares wall clock and memory only; no CPU-hour ceiling exists to copy and none may be invented. |
| `independent_variables`, `tail_checks`, `replication.seeds` | empty | Structural, not omitted — each carries its stated reason in the contract. |
| card `provenance.authored_at` | `null` | Same clock reason. |
| dispatcher acceptance of the **edited** queue | unrecorded | No command-execution tool; not run, not claimed. Section 4. |
| capability check outcomes (CAP-1 … CAP-4) | unrecorded | **None is owed before S0 and none was run.** Recording one would be fabrication. |

## 7. What this session did not do, stated plainly

No shell, no arithmetic, no retrieval, no git, no clock. It ran no `tools/allocate_id.py`, no `tools/validate_ledger.py`, no `tools/research_dispatch.py` and no `search_knowledge` query — the knowledge-retrieval obligation binds a producer asserting that a quantity **for this curve** has or has not been computed, and this slot asserts no such thing and computes nothing. It **minted no identifier**: every identifier used already existed in the committed queue. It committed nothing and staged nothing; **S1 (TASK-20260904-850ff6) commits**. Nothing authored here is durable research state until committed, pushed and accepted by the post-commit verifier, and none of those happened in this session.

## 8. Provenance

- authored_by: coordinator subagent, slot S0, TASK-20260904-f0a889
- requested_policy: `coordinator-orchestration-code` · resolved model reported by the runtime: `claude-opus-5` · runtime: `claude_code` · **model_verified: false** (no `adapter resolve`, no doctor probe — this session has no shell; whether `claude-opus-5` is the configured binding for that policy was **not** checked here)
- reasoning_effort_requested: `high` (the policy default) · reasoning_effort_resolved: **unverified by this session**
- fallback_used: false · degraded_allowed: false · independent_session: false
- bedrock: **prohibited and not used** — no provider, backend, endpoint or model identifier containing "bedrock" was selected, requested or probed
- date basis: the `20260904` segment in the identifiers used comes from the dispatch context, not from a clock this session read

---

## Coordinator decision block (NOT a ledger record — no identifier minted)

```yaml
coordinator_decision:
  id: null
  id_note: >-
    NULL DELIBERATELY. This slot's write_scope excludes ledger/decisions and the
    driving session settled that this session mints no identifier. A DEC record
    is therefore NOT authored here; this block is the control-plane report's
    decision summary and is NOT durable research state. If the program wants S0's
    disposition as an official record, the driving session mints one DEC and
    commits it citing TASK-20260904-f0a889.
  decision: proceed
  what_is_decided: >-
    The control plane for BATCH-a40709 is authored: one frozen contract
    (EXP-SCURVE-3f87f6, approved_by null), fourteen task cards, a finalised
    queue carrying one named repair, and the goal head's two findability
    pointers. NOTHING IS APPROVED BY THIS: no experiment contract, no run, no
    hypothesis status, no criterion cell, no claim.
  target_ids: [GOAL-SCURVE-137bd9, RQ-SCURVE-960dbd, BATCH-a40709,
    EXP-SCURVE-3f87f6, TASK-20260904-f0a889, TASK-20260904-f9dba7]
  evidence_refs:
  - coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/batch.yaml (read in full)
  - ledger/decisions/DEC-20260904-c42007.yaml (read in full)
  - coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/dispatch_queue.json (read in full)
  - .../BATCH-ef5b1e/tasks/TASK-20260824-53ecc0/audit-plan.yaml (read in part: gate L0,
    control bank, lanes L-EQ, L-BASE, L-RHO, L-LADDER, L-COMPLETE, L-IND, D3, D6)
  - ledger/goals/GOAL-SCURVE-137bd9/goal.yaml (read in full)
  - templates/research-records.md (Experiment section)
  - NO EXPERIMENTAL EVIDENCE IS CITED BECAUSE NONE EXISTS UNDER THIS GOAL.
  claim_ceiling: analyzed at best, never supported; no curve is called safe or unsafe
  knowledge_promotion:
    promoted: []
    not_warranted: >-
      This is a control-plane gate, not an evidence review. No run, no evidence
      record, no assessed evidence strength and no adjudicated cell exists under
      this goal, so there is nothing durable to promote. The promotion question
      is answered at S13.
  goal_status_transition: {from: active, to: active, changed: false}
  hypothesis_status_transition: {hypothesis_id: null, changed: false}
  next_actions:
  - >-
    DRIVING SESSION, BEFORE S1 COMMITS: write section 0-8 above verbatim to
    .../TASK-20260904-f0a889/report.md (this session was refused by the runtime),
    then re-run tools/research_dispatch.py against the EDITED queue and record
    the result; revert instructions for the three edits are in section 4.
  - >-
    THEN S1 (TASK-20260904-850ff6): merge origin/main (merge, never rebase),
    stage only the four declared paths plus the goal head disclosed under
    staged_not_in_binding_set, commit, push, refresh the PR naming BATCH-a40709,
    EXP-SCURVE-3f87f6 and the two task ids, and record path_sha256 recomputed
    from the committed blobs.
  - >-
    BEFORE S2 AND S3: run CAP-1 and CAP-2 and record the outcomes in the task
    receipt. A failed CAP-1 halts S2 as an impediment on a still-active goal and
    leaves the measurement slots dispatchable.
  - >-
    OWED, NOT DONE HERE: one superseding record covering the two batch.yaml/queue
    divergences in section 5 items 1-2, and a separate committed Coordinator
    decision if EXP-SCURVE-3f87f6 is ever to be approved.
  decided_by: coordinator (slot S0)
  decided_at: null
  decided_at_note: null by capability; this session cannot read a clock
```

---

# ADDENDUM BY THE DRIVING SESSION

Appended, not merged into the record above. Sections 0-8 and the decision block are the S0 coordinator subagent's text, written here verbatim because that session's runtime refused its own `Write` calls (its section 5 item 7). Everything below is the driving session's, performed after S0 returned, and is separated so no reader mistakes one author for the other.

## A1. Two verifications S0 declared owed, now performed

**A1.1 — the dispatcher accepts the EDITED queue.** S0 explicitly declined to claim this (section 4, "Verification owed, and honestly unmet here"). Re-run by the driving session against the queue as S0 left it:

```
python3 tools/research_dispatch.py \
  coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/dispatch_queue.json \
  --claims refs --now <utc>
  -> dispatches: ['TASK-20260904-f0a889']
     gates: 11   deferred: 13   terminal: 0
     claims: TASK-20260904-f0a889 applied "running_with_lease" (epoch 1,
             owner coordinator-aes-1, branch
             claude/degree-regularity-polynomial-systems-pssesi)
```

Same shape as before S0's edits, so the revert path in section 4 is not taken. The live claim overlays correctly as `running_with_lease`.

**A1.2 — S0's edits are exactly the three it declared, and nothing else.** Diffed against the committed queue at `50258bad7`:

- task ids and their order: UNCHANGED (14 tasks, same sequence)
- `max_concurrent`: 2 -> 2
- exactly ONE task object differs, `TASK-20260904-f9dba7` (S13), in exactly three keys: `handoff.objective`, `handoff.deliverables`, `handoff.artifact_paths`

No other slot changed in any field. The goal head diff is exactly the two pointer fields S0 declared in section 3 (`current_batch_id`, `dispatch_queue_path`); `next_action`, `updated_at` and `latest_verified_commit` are untouched, as S0 said.

## A2. A defect S0 could not have found, repaired here with proof

`experiments/EXP-SCURVE-3f87f6/specification.yaml` **DID NOT PARSE AS YAML** when S0 returned it:

```
yaml.scanner.ScannerError: while scanning a simple key
  in experiments/EXP-SCURVE-3f87f6/specification.yaml, line 173, column 9
  could not find expected ':' in line 174, column 7
```

Cause: four plain multi-line scalars whose continuation line sat at the SAME indent column as its key, so the parser read the continuation as a new key and demanded a colon. Example, before:

```yaml
      - route (i): the parity predicate on the certified group order, with the
        Lagrange step written out
```

This is the standing finding in operation: **a parse gate cannot be discharged by a role with no parser.** S0 has no command-execution tool, could not run `yaml.safe_load`, and correctly did not claim it had. The repair is therefore the dispatcher's, and it is recorded rather than done quietly.

**Repair: four continuation lines indented two spaces deeper. Nothing else.**

**Proof that it is content-preserving**, not a rewrite:

```
line count before: 790      line count after: 790
after stripping leading whitespace from every line, the two files are IDENTICAL
git diff: 4 changed lines, each differing only in leading spaces
```

The changed lines are 173, 245, 246 and 257. No word, character, key, value or ordering was altered.

After the repair, all four S0 artifacts parse:

| artifact | parses |
| --- | --- |
| `experiments/EXP-SCURVE-3f87f6/specification.yaml` | YES (after A2) — `id: EXP-SCURVE-3f87f6`, `status: draft`, `approved_by: None`, `hypothesis_id: None` |
| `.../TASK-20260904-f0a889/task-cards.yaml` | YES, unmodified |
| `ledger/goals/GOAL-SCURVE-137bd9/goal.yaml` | YES, unmodified beyond the two pointers |
| `.../BATCH-a40709/dispatch_queue.json` | YES, valid JSON, 14 tasks |

`approved_by` is confirmed `null` by reading the parsed object, not by reading the text — S0's most important constraint, checked by machine.

## A3. What the driving session did NOT do

- Did **not** rewrite, condense or correct S0's sections 0-8. The report is its record.
- Did **not** run CAP-1, CAP-2, CAP-3 or CAP-4. None is owed before S0 or S1, and recording one would be fabrication.
- Did **not** approve `EXP-SCURVE-3f87f6`. Its `approved_by` stays `null`; S0's section 5 item 6 stands unchanged, and a dispatch instruction is not a decision.
- Did **not** mint any identifier while performing A1 or A2.
- Did **not** author the superseding record S0's section 5 items 1-2 ask for. It is owed and still open.

## A4. Provenance of this addendum

Driving session, top-level orchestrator, claude_code runtime. It has a shell; every command quoted above was actually run and its output is reproduced, not reconstructed. Bedrock was not used and is prohibited. No clock-free field is stamped here that S0 left null by capability.
