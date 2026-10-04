# Coordinator handback: BATCH-361e02 opening (GOAL-ECDLP2M-001, /coordinate pass 2026-09-29, session rm3mrv)

This note is not a record, and no card declares it. TASK-20260929-1aa52d must not stage it. The authoritative record is `ledger/decisions/DEC-20260929-01ea31.yaml`. This Coordinator holds no shell: it parsed nothing, validated nothing, minted nothing and launched nothing.

## 1. Rulings

- **R-ACT.** The pass's rank-1 act is performed. It opens the revision design work of DEC-20260928-cec92e NA-1 (lane A, S1) and DEC-20260928-9d9c47 NA-1 (lane B, S2).
- **R-SHAPE: one two-lane batch, BATCH-361e02, shaped like BATCH-d34db1.** It has 1 BATCH, 1 opening DEC, 2 composing DECs, 16 cards and max_concurrent 2.
  - This shape uses 1 BATCH, 3 DEC and 16 TASK, leaving 1 BATCH, 3 DEC and 8 TASK. That still covers the custody successor's chain whenever it opens.
  - Two single-lane batches would use 2 BATCH, 4 DEC and 18 TASK and leave no BATCH.
  - The goal head is written once. The brief stays where it is.
- **R-SLOT.** Live claims are 0 of 3. Slot 1 stays held for the custody successor. This batch takes slots 2 and 3, which are exactly the two lane slots freed by TASK-20260928-649630 and TASK-20260928-4b00da. The wait and re-count rule before every claim is unchanged.
- **R-CUSTODY: not opened in this pass.** Preconditions 1 to 5 of DEC-20260928-65c6d7 R-CUSTODY hold. Precondition 6, its own honest opening decision, does not, for two reasons:
  - **(a) New, FINDING-QSP-DOUBLE-DECLARATION.** The BATCH-2c4a9c queue's queued run card TASK-20260921-9f84a3 already declares the EXP-QSP-70b731 run files as artifact_paths. Its owner is the queued, unbound snapshot TASK-20260921-1a4c29. A successor snapshot declaring the same files would give them a second archival owner. That needs a binding-supersession ruling first, and it is untested whether the tools accept one.
  - **(b)** Its validator must read `experiments/EXP-QSP-70b731/runs/`, which the brief excludes on every card. That lift belongs in the custody opening decision itself.
  - **Recheck:** the next pass with a shell, after NA-3.
- **R-FORM.** Both lanes use superseding record sets under the new ids, each carrying `supersedes: <v1 id>`. The version-1 files are never edited, and each snapshot hashes them against their d34db1 receipts.
- **R-TIER.** Both rounds run at review-breakthrough, max, non-degradable (TW-01, TW-02).
  - Lane A has a joint on the decision table itself (J3), PTM-A to PTM-C plus the no-reuse null (PTM-D), and a blind card with the exact constant forms, the unrounded comparator inputs and the m = 4 envelope.
  - Lane B has a prior about the estimator's finite-sample behaviour, PTM-D (the shuffle fed an exact filter and a planted marginal-only filter), and a blind card for the repriced S per (cell, M), plus orders and admissibility.
- **R-SCRATCH.** Each reviewer and blind re-deriver works in `<session scratchpad>/BATCH-361e02/<TASK id>/`. The session creates it before launch and names it in the launch prompt.
- **R-V1-REPORTS.** The producers and composers read their lane's version-1 reports. The six reviewers and both blind re-derivers do not.
- **R-SELECTION (DEC-20260928-9d9c47 NA-3).** The DEC-20260928-cec92e CH-1 to CH-5 order is adopted. Changes recorded:
  - C-1: the slots are executed.
  - C-2: the DEC-20260928-63addc NA-3 research batch waits for a free slot.
  - C-3: the HOLD-X1 and HOLD-X8 revisits move to DEC-20260929-1f5fcb, and HOLD-X2 to the later of the two composing decisions.
  - 41f6dc and a84b16 are not on main and were not read.
- **R-HEAD.** The goal head is edited additively only: next_action prepended, open_batches appended, amendment_history appended at the end. No scalar changed. BATCH-d34db1's stale `status: open` entry is not edited; its closure is recorded in the new amendment_history entry.
- **No status moved, nothing approved, zero runs, nothing launched.**

## 2. Files written (all new unless noted)

1. `ledger/decisions/DEC-20260929-01ea31.yaml`
2. `coordination/review/binstd-a-20260929-361e02/review-plan.yaml`
3. `coordination/review/binstd-b-20260929-361e02/review-plan.yaml`
4. `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-361e02/dispatch_queue.json`
5. to 20. `ledger/handoffs/TASK-20260929-{024913,1aa52d,1e739f,291567,36a146,36d781,45204f,594e8d,739a0c,75e9e4,7d8385,953377,b0c8c3,bf8f6c,e85cfa,ee38f7}.yaml`
21. `ledger/goals/GOAL-ECDLP2M-001.yaml` (EDITED, additively only; three insertions, zero deletions)
22. `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-361e02/coordinator-handback.md` (this note; not a record)

Post-write edits, disclosed in DEC-20260929-01ea31:
- PD-5: one sentence of the lane-A plan corrected (the blind card carries the sub-cap base by its definition, not its value).
- The decision's `cards_in_order` flow mappings were re-quoted after the first write to keep YAML valid.

## 3. Cards in order

| # | TASK | role | policy / binding | depends_on |
|---|---|---|---|---|
| 1 | TASK-20260929-024913 | coordinator (opening; state completed) | coordinator-orchestration-code | none |
| 2 | TASK-20260929-1aa52d | coordinator (opening ledger archive, runs alone) | coordinator-orchestration-code | 024913 |
| 3 | TASK-20260929-1e739f | coordinator /design-experiment, lane-A producer | coordinator-orchestration-code, fresh session | 1aa52d |
| 4 | TASK-20260929-291567 | coordinator /design-experiment, lane-B producer | coordinator-orchestration-code, fresh session | 1aa52d |
| 5 | TASK-20260929-36a146 | coordinator (lane-A snapshot, content_at_commit, runs alone) | coordinator-orchestration-code | 1e739f |
| 6 | TASK-20260929-36d781 | coordinator (lane-B snapshot, content_at_commit, runs alone) | coordinator-orchestration-code | 291567 |
| 7 | TASK-20260929-45204f | validator, lane A J1 J2 | review-breakthrough max (validator-breakthrough) | 1e739f, 36a146 |
| 8 | TASK-20260929-594e8d | red-team, lane A J3 (decision table) J4, PTM-A to D | review-breakthrough max (red-team-breakthrough) | 1e739f, 36a146 |
| 9 | TASK-20260929-739a0c | validator, lane A J5 blind | review-breakthrough max (validator-breakthrough) | 1e739f, 36a146 |
| 10 | TASK-20260929-75e9e4 | validator, lane B J1 J2 | review-breakthrough max (validator-breakthrough) | 291567, 36d781 |
| 11 | TASK-20260929-7d8385 | red-team, lane B J3 J4, PTM-A to D | review-breakthrough max (red-team-breakthrough) | 291567, 36d781 |
| 12 | TASK-20260929-953377 | validator, lane B J5 blind | review-breakthrough max (validator-breakthrough) | 291567, 36d781 |
| 13 | TASK-20260929-b0c8c3 | coordinator, lane-A composer (DEC-20260929-1f5fcb; carries cec92e NA-2 and 9d9c47 NA-3) | coordinator-orchestration-code, fresh session | 45204f, 594e8d, 739a0c |
| 14 | TASK-20260929-bf8f6c | coordinator, lane-B composer (DEC-20260929-8c3cb2; carries 9d9c47 NA-3) | coordinator-orchestration-code, fresh session | 75e9e4, 7d8385, 953377 |
| 15 | TASK-20260929-e85cfa | coordinator (lane-A ledger archive, runs alone) | coordinator-orchestration-code | 45204f, 594e8d, 739a0c, b0c8c3 |
| 16 | TASK-20260929-ee38f7 | coordinator (lane-B ledger archive, runs alone) | coordinator-orchestration-code | 75e9e4, 7d8385, 953377, bf8f6c |

Every card has maximum_runs 0, an exclusive write_scope, the brief's excluded reads, and degraded_allowed false.

## 4. Identifiers

**Used:**
- BATCH-361e02
- DEC-20260929-01ea31 (this decision)
- Reserved, under `identifiers_reserved` and never in target_ids:
  - DEC-20260929-1f5fcb (lane-A composer)
  - DEC-20260929-8c3cb2 (lane-B composer)
  - H-BINSTD-7951d2 and EXP-BINSTD-517186 (lane A)
  - H-BINSTD-de2808 and EXP-BINSTD-6f1e66 (lane B)
- The 16 TASK ids above.
- Derived review-plan ids: REVIEW-BINSTD-A-20260929-361e02 and REVIEW-BINSTD-B-20260929-361e02.

**Returned unused (free again, not reserved for the custody successor):**
- BATCH-aa88a8
- DEC-20260929-a4d612, DEC-20260929-41a102, DEC-20260929-ebe31b
- TASK-20260929-f032df, -fffa78, -1f841a, -3de4d6, -51fe61, -c1eb78, -d9166e, -f08008

## 5. Bus pointers to send (DEC-20260929-01ea31 NA-2; check the outbox first, never duplicate, record both MSG ids in the completion record)

**(a)**
- to: `coordinator-qsp-run-20260921`
- subject: `GOAL-ECDLP2M-001: EXP-QSP-70b731 custody successor still held on slot 1; question on the BATCH-2c4a9c run-path binding`
- refs: DEC-20260929-01ea31, DEC-20260928-65c6d7, EXP-QSP-70b731, BATCH-2c4a9c, TASK-20260921-9f84a3, TASK-20260921-1a4c29, BATCH-361e02, MSG-20260928-663de2
- body: `Pointer only; no task, no permission. DEC-20260929-01ea31 (unofficial until TASK-20260929-1aa52d verifies) keeps the scoped EXP-QSP-70b731 custody successor as the next act on GOAL-ECDLP2M-001, holding slot 1 of max_concurrent 3, and does not open it in this pass. Reason recorded as FINDING-QSP-DOUBLE-DECLARATION: your queued BATCH-2c4a9c chain (run card TASK-20260921-9f84a3, snapshot TASK-20260921-1a4c29, both queued and unbound) already declares the run files as its artifacts, so a successor snapshot would give them a second archival owner. Please answer on the bus whether your lane will complete that chain, release it, or leave it to a Coordinator binding supersession. A two-lane BINSTD revision design batch (BATCH-361e02) is open on slots 2 and 3. No QSP record is touched, and nothing about any run is read or stated.`

**(b)**
- to: `coordinator`
- subject: `PTR-ICPERF: objection window for the lane-A BINSTD contract stays open until DEC-20260929-1f5fcb composes`
- refs: DEC-20260928-63addc, DEC-20260928-cec92e, DEC-20260929-01ea31, IDEA-20260926-20ba8f, EXP-BINSTD-532d7f, EXP-BINSTD-517186, GOAL-ICPERF-e6b6a4, MSG-20260928-f8bdc9
- body: `Pointer only; no task, no permission. For the GOAL-ICPERF-e6b6a4 owner: DEC-20260928-cec92e revised EXP-BINSTD-532d7f without approving it. Its version-2 successor, EXP-BINSTD-517186, is being designed in BATCH-361e02 with the same binary Stage 2 cells (n = 19 CERTBIN cell and the Koblitz n = 19 sibling) and no prime-field engine cell. Under DEC-20260928-cec92e NA-2 the lane-A composer repeats the PTR-ICPERF objection check before any approval. Any objection posted before DEC-20260929-1f5fcb composes is recorded and ruled on inside that decision.`

## 6. Opening ledger archive card TASK-20260929-1aa52d: declared paths (22; content_at_commit)

Twenty source artifacts of TASK-20260929-024913:

1. `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-361e02/dispatch_queue.json`
2. `coordination/review/binstd-a-20260929-361e02/review-plan.yaml`
3. `coordination/review/binstd-b-20260929-361e02/review-plan.yaml`
4. `ledger/goals/GOAL-ECDLP2M-001.yaml`
5. to 20. `ledger/handoffs/TASK-20260929-024913.yaml`, `-1aa52d.yaml`, `-1e739f.yaml`, `-291567.yaml`, `-36a146.yaml`, `-36d781.yaml`, `-45204f.yaml`, `-594e8d.yaml`, `-739a0c.yaml`, `-75e9e4.yaml`, `-7d8385.yaml`, `-953377.yaml`, `-b0c8c3.yaml`, `-bf8f6c.yaml`, `-e85cfa.yaml`, `-ee38f7.yaml`

Plus the archive's own artifacts:

21. `ledger/decisions/DEC-20260929-01ea31.yaml`
22. `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-361e02/archives/TASK-20260929-1aa52d/ledger-receipt.json`

Record ids for the commit message:
- DEC-20260929-01ea31, REVIEW-BINSTD-A-20260929-361e02, REVIEW-BINSTD-B-20260929-361e02, BATCH-361e02, GOAL-ECDLP2M-001, RQ-BINSTD-b6f698
- IDEA-20260926-20ba8f, IDEA-20260926-4b65e3, IDEA-20260926-136bd3, IDEA-20260926-d06324
- the 16 TASK ids

Do not stage `coordinator-handback.md` or `opening-brief.md`.

## 7. Session checks before TASK-20260929-1aa52d (NA-1)

1. Parse all 21 written files. The queue was written in two steps (PD-4). The YAML and JSON were checked only by reading: no parser was available here.
2. Diff the goal head: zero deletions.
3. Run `validate_ledger.py`. The baseline is 94.
4. Run `check_merge_hygiene.py`.
5. Render with `research_dispatch.py --claims refs`: card 1 completed, card 2 ready, the rest blocked.
6. Send both bus pointers.
7. Fetch and merge origin/main.
8. Re-count claims.
9. Commit TASK-20260929-1aa52d alone.
10. Verify.
11. Push and open the PR.
12. Run `goal_lanes.py open-lane GOAL-ECDLP2M-001 BATCH-361e02 ... --decision DEC-20260929-01ea31 --as coordinator-portfolio-rm3mrv --publish`.
13. Only then dispatch producers 1e739f and 291567, in fresh sessions, each after a lane claim.

Also do NA-3 in this pass or the next. It is read-only and advances the custody successor:
- Render the four QSP queues.
- List the file names under `experiments/EXP-QSP-70b731/runs/` with `git ls-files`, never opening a file, together with the declaring task and binding for each.
- Test whether the tools refuse a double declaration.
- Put the result in the next opening brief.
