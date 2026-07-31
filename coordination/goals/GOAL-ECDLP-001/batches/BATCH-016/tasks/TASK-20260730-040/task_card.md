# TASK-20260730-040 — Coordinator — Ledger archive, ALONE

> **NON-AUTHORITATIVE MIRROR.** The authoritative card is the `tasks[]` entry
> for `TASK-20260730-040` in
> `coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/dispatch_queue.json`.
> Where this mirror and that queue disagree, **THE QUEUE GOVERNS**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-016
- **Role:** coordinator · **depends_on:** TASK-20260730-038, TASK-20260730-039
- **Archive:** `kind: ledger`,
  `source_task_ids: [TASK-20260730-038, TASK-20260730-039]`
- **Budget:** 2400 s, 2 GB, maximum_runs 1

## Objective

Close BATCH-016: write the evidence record if and only if the pre-registered
rule is met, write the one coordinator decision scoped to exactly the per-case
PASS/FAIL outcomes, record the CTRL-4 disposition the pre-registered consequence
requires, checkpoint the goal record with a single concrete next action, and
commit the review artifacts and ledger records together in **one** ledger commit
with a verified receipt.

## The declared set — eight paths (seven if no evidence record is warranted)

```
coordination/.../BATCH-016/reviews/TASK-20260730-038/validation_report.yaml
coordination/.../BATCH-016/reviews/TASK-20260730-038/recount_note.md
coordination/.../BATCH-016/reviews/TASK-20260730-039/red_team_report.yaml
coordination/.../BATCH-016/reviews/TASK-20260730-039/falsification_review.md
ledger/evidence/EV-STR-006.yaml
ledger/decisions/DEC-20260730-032.yaml
ledger/goals/GOAL-ECDLP-001.yaml
coordination/.../BATCH-016/archives/TASK-20260730-040/ledger_commit_receipt.json
```

**DECLARE-THEN-DEVIATE.** `ledger/evidence/EV-STR-006.yaml` is declared
**unconditionally** because `tools/research_dispatch.py._validate_ledger_archive`
requires every `kind: ledger` archive to declare at least one `ledger/evidence/`
path and one `ledger/decisions/` path with the record id visible in each
filename, and refuses the whole queue otherwise. **The conditionality is not
expressed as omission; it moves from the declaration to the close**
(QUEUE-AMEND-20260730-002; BATCH-014 `TASK-20260729-048` precedent with
EV-STR-004). Declaration is not prophecy: the declared set is the **maximum**
scope, and committing less is a **recorded deviation**, not a defect. **Never
write a record merely to satisfy a path count.**

**Pre-registered evidence rule (fixed before any card ran):** an evidence record
is written **if and only if** the TASK-20260730-037 snapshot commit exists and is
accepted **and** the case-0 baseline reported PASS. Never decided by whether the
case (1), (2) or (3) outcomes were favourable.

## Constraints

- **RUN ALONE.** No other task may hold the Git index concurrently.
- **Run `tools/allocate_id.py --check` for DEC-20260730-032 and EV-STR-006
  before writing either** and record the verbatim result. On a collision, **stop
  and report** — do not silently rename; a rename changes declared
  `artifact_paths` and requires a recorded QUEUE-AMEND before anything is
  staged. Record that the allocator scans the working tree only, so **a clean
  result is not a guarantee** (INT-BATCH016-C). Five identifier collisions are
  on record in this campaign.
- **Scope the decision to exactly what was measured:** the PASS/FAIL behaviour
  of the copied CTRL-4 checker on one baseline and three mutated inputs at
  B = 192 on CURVE-J12S1, one host, one stack, one realisation, plus a
  determinism repeat. **State explicitly that this batch tested an INSTRUMENT
  and not the object.** Carry the claim ceiling and N-1 through N-7 verbatim in
  substance.
- **Record the CTRL-4 disposition.** The pre-registered consequence already
  fires on case (1) alone, which is pre-stated and committed: **CTRL-4 is not
  retained in its present form in any successor contract.** Decide RETIRE or
  REWRITE on the measured cases (2) and (3) and both reviews' recommendations,
  state which and why, and bind it on successor contracts. **Do not edit
  `experiments/EXP-STR-004/specification.yaml`** — no contract is amended and no
  `protocol_amendment` cycle is opened.
- **Do not record case (1) or case 0 as a result of this batch.**
- **Move no hypothesis.** H-STR-002 stays `weakened`; its file is not staged,
  not edited, not superseded. Do not discharge DEFER-BATCH009-001. Do not
  approve EXP-STR-004. Do not re-adjudicate BATCH-014 or BATCH-015.
- **`reject_scoped` is forbidden here (N-6).** One execution, one host.
- **If the evidence cannot discriminate, the decision is `inconclusive` and
  saying so plainly is the required outcome.** In particular, if the case-0
  baseline did not PASS, or the validator found the checker was rewritten rather
  than copied, **the batch measured nothing about CTRL-4** and the decision says
  exactly that.
- **Fill `knowledge_promotion` with a concrete reason.** `not applicable` is not
  a reason. Default expectation is `not_warranted`: one execution, one host, one
  instance, one B; `replicated` is not reached and `reject_scoped` is forbidden.
  No `knowledge/` path is in the declared set, so a promotion would require a
  recorded QUEUE-AMEND before anything is staged. The reserved KN-FIND-010
  sentence is **not promoted in its present wording under any outcome**.
- **Declare the evidence basis honestly:** `empirical_only` for every measured
  PASS/FAIL; `derivation` for nothing; `proved` for nothing. An undeclared basis
  is the failure, not the lack of a proof.
- **Carry RULE-BATCH016-SCOPE**, both reviews' adopted findings and dissents,
  and the unrepaired-defects block forward unchanged.
- **Checkpoint the goal record:** append a BATCH-016 close entry
  (`batches_consumed 16` against `maximum_batches 50`, the CTRL-4 disposition,
  the claim boundary), preserve **exactly one** `next_action`, move the current
  one to a `prior_next_action_*` key. Never overwrite an immutable entry.
- **The goal does not reach `completed`.** Three pairwise-distinct resolved
  models are unavailable here; **no BATCH-016 session may be counted toward a
  `completion_quorum` attestation** and no attestation is recorded that was not
  obtained (INT-BATCH016-E). A fifty-first batch is not self-granted.
- **Commit exactly the declared set and nothing else.** The four review
  artifacts land in **this** commit and no earlier one; if already committed,
  record it as an integrity note and **do not enlarge or shrink the declaration
  after the fact**.
- Check `.git/index.lock` before staging and record what you found; a stale
  zero-byte lock with no live git process: **report and stop**. Stage no
  AppleDouble sidecar. Stage nothing under `harness/`. An unfinished git
  verification is reported as unfinished.
- **Never touch `tools/validate_ledger_baseline.txt` and never state or imply
  that the ledger validates.**
- **YAML discipline, and parsing is not sufficient.** Any scalar containing a
  hash, a pipe, a colon-space or a leading quote goes in a block scalar or in
  quotes. An unquoted space-hash opens a comment and silently truncates the
  field — that defect parses cleanly and has already corrupted a reviewer's
  words once in this program. A mapping key may never sit at the same indent as
  the `- ` entries of an open block sequence.
- Bounded card: 2400 s. If you cannot finish, **stop and report**, naming
  exactly what was not written and what was not committed.

## Deliverables

`DEC-20260730-032.yaml`; `EV-STR-006.yaml` **iff** the pre-registered rule is
met (basis `empirical_only`, `run_ids` empty with its reason and INT-BATCH016-F
named, the seven mutation paths bound by SHA-256 at the snapshot commit, claim
tier toy); the BATCH-016 goal checkpoint with exactly one `next_action`; and
`ledger_commit_receipt.json`.

## Completion gate

G1–G13 as stated in the queue entry.
