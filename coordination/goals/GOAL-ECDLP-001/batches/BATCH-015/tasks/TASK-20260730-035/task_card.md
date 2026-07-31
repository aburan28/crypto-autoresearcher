# TASK-20260730-035 — Ledger archive: evidence, decision and the goal checkpoint

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-015 `dispatch_queue.json`. **Where they disagree, the queue governs.**

- **Role:** coordinator (archival task — **runs alone**)
- **Depends on:** TASK-20260730-033 **and** TASK-20260730-034
- **Archive kind:** ledger;
  `source_task_ids: [TASK-20260730-033, TASK-20260730-034]`
- **Budget:** 2400 s, 2 GB, `maximum_runs: 1`

## Identifier check first

Run `tools/allocate_id.py --check` for **DEC-20260730-031** and **EV-STR-005**
before writing either, and record the verbatim result. **On a collision, STOP
AND REPORT** — do not silently rename; a rename changes declared
`artifact_paths` and requires a recorded QUEUE-AMEND before anything is staged.
Record also that **the allocator scans the working tree only** and cannot see
non-ancestor branches, so a clean result is not a guarantee (INT-BATCH015-C).
**Five identifier collisions are on record in this campaign.**

## The evidence record is a pre-registered two-branch declaration

Decided by **the existence and acceptance of the TASK-20260730-032 snapshot
commit**, not by the content of the measurements.

- **BRANCH 1** — probe executed, package committed, snapshot accepted:
  `ledger/evidence/EV-STR-005.yaml` is added → **8 paths**.
- **BRANCH 2** — otherwise: **no evidence record**, set stays at **7 paths**,
  reason recorded in the receipt.

Under BRANCH 1, EV-STR-005 binds the eight probe paths **by SHA-256 at the
snapshot commit**, with `run_ids` **empty**, its reason stated, INT-BATCH015-F
named, and the acknowledgement that it is the **fourth** such record after
EV-IC-001, EV-STR-002 and EV-GGM-001 and that **path binding is weaker than run
binding**. EV-STR-004 remains unallocated and unused and is **not resurrected,
not reused and not cited as existing**.

## Declared commit set — 7 paths by default, 8 under BRANCH 1

```
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-033/validation_report.yaml
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-033/recount_note.md
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-034/red_team_report.yaml
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-034/falsification_review.md
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/archives/TASK-20260730-035/ledger_commit_receipt.json
ledger/decisions/DEC-20260730-031.yaml
ledger/goals/GOAL-ECDLP-001.yaml
[BRANCH 1 only] ledger/evidence/EV-STR-005.yaml
```

**The four review artifacts land in THIS commit and in no earlier one.** If
they are already committed, record it as an integrity note in the receipt and
**do not enlarge or shrink the declaration after the fact.**

## What the decision may and may not do

- **Scope it to exactly what was measured:** two structure assertions at
  B = 192 and B = 193 on CURVE-J12S1, and twenty-eight base-row supply counts
  at fourteen toy cells with two factor bases, one host, one stack, one
  realisation. Carry the claim ceiling and **N-1 through N-6** verbatim in
  substance.
- **Move no hypothesis.** H-STR-002 stays `weakened`; its file is **not
  staged, not edited, not superseded**. Do **not** discharge
  DEFER-BATCH009-001. Do **not** approve EXP-STR-004. Do **not** re-adjudicate
  BATCH-014.
- **`reject_scoped` is forbidden here** (N-6). If the pre-registered
  falsification condition **fired**: record that the derivation's committed-code
  hypotheses failed **at the named cells**, adopt the red team's third dissent
  as pre-registered, and set the next action to **reopen the execution question
  on the merits in a successor** — reject nothing, approve nothing. If it did
  **not** fire: record the two facts as measured and state plainly that **driver
  fidelity remains unreachable and no counterexample certificate exists**.
- **If the evidence cannot discriminate, the decision is `inconclusive` and
  saying so plainly is the required outcome.**
- **`knowledge_promotion` carries a concrete `not_warranted` reason.** `not
  applicable` is not a reason. The gate does not fire: one probe, one host, one
  realisation per cell, `replicated` not reached, `reject_scoped` forbidden. No
  `knowledge/` path is in the default declared set, and **the reserved
  KN-FIND-010 sentence is not promoted in its present wording under any
  outcome**.
- **Declare the basis honestly:** `empirical_only` for every measured count and
  both structure assertions; `derivation` for nothing; `proved` for nothing.
  **An undeclared basis is the failure, not the lack of a proof.**
- Carry **RULE-BATCH015-SCOPE** into the decision (INT-BATCH015-J), together
  with every adopted finding and dissent of both reviews — **carried, not
  described as discharged**.

## Goal checkpoint

Append a **BATCH-015** entry to `batch_checkpoints`: what the batch was, what it
turned out to be, archive task ids and commits, review task ids and verdicts,
evidence and decision ids, campaign budget status with `batches_consumed: 15`
against `maximum_batches: 50`, and the claim boundary. **Preserve exactly one
`next_action`**, moving the current one to a `prior_next_action_*` key per this
record's established convention. **Never overwrite an immutable entry** —
supersede under a new id.

**The goal does not reach `completed`.** AGENTS.md rule 13's three
pairwise-distinct **resolved** models are unavailable on this harness; no
BATCH-015 session may be counted toward a `completion_quorum` attestation, and
**no attestation is recorded that was not obtained** (INT-BATCH015-E). Batches
through a fiftieth are authorized; **a fifty-first is not and is not
self-granted here.**

## Hazards and discipline

- Check `.git/index.lock` before staging and record what you found. A stale
  zero-byte lock with no live git process: **report and stop.**
- Stage no AppleDouble `._` sidecar. **An unfinished git verification is
  reported as unfinished** — never as PASS and never as FAIL.
- **Never touch `tools/validate_ledger_baseline.txt`, and never state or imply
  that the ledger validates.**
- **YAML discipline, and parsing is not sufficient.** Any scalar containing a
  hash, a pipe, a colon-space or a leading quote goes in a block scalar or in
  quotes — an unquoted space-hash opens a comment and silently truncates the
  field, a defect that parses cleanly and has already corrupted a reviewer's
  words once in this program. A mapping key may never sit at the same indent as
  the `- ` entries of an open block sequence.

If you cannot finish inside 2400 s, **stop and report**, naming exactly what
was not written and what was not committed.
