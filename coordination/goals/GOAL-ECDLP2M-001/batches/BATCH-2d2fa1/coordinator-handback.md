# Coordinator handback: R-CUSTODY re-ruled, BATCH-2d2fa1 opened (DEC-20261002-86a7e0)

This handback is not a record and not a declared artifact of any card. No archive stages it.

Act: the /coordinate portfolio pass of 2026-10-02 on GOAL-ECDLP2M-001. It re-rules R-CUSTODY on the DEC-20260929-01ea31 NA-3 facts and **opens** the EXP-QSP-70b731 custody successor as BATCH-2d2fa1 on slot 1. The batch has seven cards and zero runs. Nothing is approved except the opening itself. No status moves, no QSP record is edited and nothing is dispatched.

## 1. Rulings (DEC-20261002-86a7e0)

- **FINDING-QSP-DOUBLE-DECLARATION-CORRECTED** (an additive finding; 01ea31 is not edited). Your brief's correction is right about one field and incomplete about another:
  - **C1.** At task-level `artifact_paths`, TASK-20260921-9f84a3 names only six directories (12a389, 15a2ab, 186d9d, 7faa1b, d10c74, ef2490), and none of them is on main.
  - **C2.** Its `handoff.artifact_paths`/`deliverables`, and TASK-20260921-1a4c29's `archive.paths`/`read_scope`, name **twenty** directories. That includes RUN-QSP-097ecd and RUN-QSP-1df59e, which are on main (queue lines 76-277 and 580-781). So 01ea31 was right that the 2c4a9c snapshot declares existing files; it put the declaration in the wrong field.
  - **C3.** Every existing file is declared, unbound, two to four ways inside the QSP lane.
  - **C4.** All four QSP ledger cards reserve the same EV-QSP-d206e6 and DEC-20260921-c97a41.
  - **C5.** All four QSP snapshots are commit-mode. My reading of `verify_archive` is that they cannot bind files that are already committed unchanged. This is not a test result; the session confirms or refutes it.
  - **C6 and C7.** These are the claim/release states and the owner's bus statements. They are quoted as hearsay.
- **R-CUSTODY: OPEN.** Preconditions (1) to (5) are met. Precondition (6) is met by R-BIND and R-READ-LIFT. The owner's silence across four pointers is recorded, not read as consent.
- **R-BIND: binding supersession of ARCHIVAL OWNERSHIP, exact paths only, no QSP edit.**
  - The snapshot TASK-20261002-5e1246 binds the R-ENUM set **content_first**.
  - When its receipt verifies, archival ownership of exactly those paths passes to it. The unbound declarations of the same paths by 1a4c29, a3e767, 3c833e and ee3c32 (and the run cards, as far as they name those paths) are superseded as ownership.
  - These stay untouched: the QSP execution approvals (7a8d6b, 5de324, e9f312, f0e100), the declarations of paths that are not on main, and the record-id reservations.
  - A later QSP archive of a bound path is a second binding of the same bytes. A byte difference is a stop.
  - Finishing the 2c4a9c chain would need a scoped successor snapshot that excludes the bound set. That is a later act.
- **R-ENUM.** Before TASK-20261002-230174, the session fills TASK-20261002-345dbd's `write_scope` and `artifact_paths` mechanically from `git ls-files` (without .gitkeep, sorted bytewise). The stop conditions are in section 6.
- **R-READ-LIFT.** The runs/ exclusion is lifted ONLY for these three cards:
  - 345dbd (mechanical: names, blob ids, sizes, sha256, history);
  - 5e1246 (mechanical re-hash);
  - 7eb899 (validator, full read for V1 to V8 only).
  - It is not lifted for the composer, the archives, this author or any other batch. It ends when 9a734c verifies.
- **R-SHAPE.** Seven serial cards: the six-card lineage shape plus the inventory card. An inventory card is needed because the dispatcher binds only `artifact_paths` of same-queue non-archive sources.
- **R-SLOT.** The batch takes slot 1 and claims only when the goal-wide live count is at most 2. It never borrows slot 2 or 3. When it closes, slot 1 goes to S1 v4 (54dcd8 CH-B) if no earlier slot has taken it, otherwise to U-HOLDH.
- **R-QSP-RETURN.** If the owner answers or a QSP claim goes live before 5e1246, the snapshot waits and the next pass rules.
- **R-PRIOR** (P1 to P5) and **R-KEYS** (K-COMPLETE, K-PARTIAL, K-INVALID, K-NOT-CHECKABLE) are fixed before any report returns. No review plan is written; this is disclosed as PD-4.
- **R-OUTCOME and TW-C1.** No card reads the science. Any later evidence review that could contradict EV-QSP-a6aa4b runs at review-breakthrough, max.

## 2. Files written

- `ledger/decisions/DEC-20261002-86a7e0.yaml`
- `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-2d2fa1/dispatch_queue.json`
- `ledger/handoffs/TASK-20261002-{0e76e7,230174,345dbd,5e1246,7eb899,84621d,9a734c}.yaml` (seven files)
- `ledger/goals/GOAL-ECDLP2M-001.yaml`: three additive insertions (a next_action block prepended, an open_batches entry after BATCH-f435ab, an amendment_history entry at the end). Scalars are untouched.
- this handback

This agent parsed nothing. Parse all of them before the archive.

## 3. Cards in order

| n | TASK | what | role | policy | depends_on |
|---|------|------|------|--------|-----------|
| 1 | TASK-20261002-0e76e7 | opening card (completed at writing) | coordinator | coordinator-orchestration-code | none |
| 2 | TASK-20261002-230174 | opening ledger archive, content_at_commit, after R-ENUM | coordinator | coordinator-orchestration-code | 1 (runs alone) |
| 3 | TASK-20261002-345dbd | custody inventory, mechanical by the session; review_required true | coordinator | coordinator-orchestration-code | 2 |
| 4 | TASK-20261002-5e1246 | snapshot, content_first, after the R-QSP-RETURN check | coordinator | coordinator-orchestration-code | 3 (runs alone) |
| 5 | TASK-20261002-7eb899 | independent validator, V1 to V8 | validator | review-adversarial, xhigh | 3, 4 |
| 6 | TASK-20261002-84621d | composer (fresh session), writes DEC-20261002-e0aa2b | coordinator | coordinator-orchestration-code | 5 |
| 7 | TASK-20261002-9a734c | ledger archive, content_at_commit, close-lane | coordinator | coordinator-orchestration-code | 5, 6 (runs alone) |

### Opening archive declared paths (TASK-20261002-230174; 11 paths, content_at_commit)

1. `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-2d2fa1/dispatch_queue.json` (after the R-ENUM fill)
2. `ledger/goals/GOAL-ECDLP2M-001.yaml`
3. `ledger/handoffs/TASK-20261002-0e76e7.yaml`
4. `ledger/handoffs/TASK-20261002-230174.yaml`
5. `ledger/handoffs/TASK-20261002-345dbd.yaml`
6. `ledger/handoffs/TASK-20261002-5e1246.yaml`
7. `ledger/handoffs/TASK-20261002-7eb899.yaml`
8. `ledger/handoffs/TASK-20261002-84621d.yaml`
9. `ledger/handoffs/TASK-20261002-9a734c.yaml`
10. `ledger/decisions/DEC-20261002-86a7e0.yaml`
11. `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-2d2fa1/archives/TASK-20261002-230174/ledger-receipt.json`

Record ids, all literally in the commit message:
- DEC-20261002-86a7e0, BATCH-2d2fa1, GOAL-ECDLP2M-001, EXP-QSP-70b731, RQ-QSP-f9bbdb
- the seven TASK ids

### Scratch paths (pre-create; name them in the launch prompt)

- `<scratchpad>/BATCH-2d2fa1/TASK-20261002-7eb899/`: the validator. It must never list the root, its siblings or `composition/`.
- `<scratchpad>/BATCH-2d2fa1/TASK-20261002-345dbd/`: optional, for the session's own mechanical inventory work.

## 4. Identifiers

- **Used:**
  - BATCH-2d2fa1
  - DEC-20261002-86a7e0
  - TASK-20261002-0e76e7, -230174, -345dbd, -5e1246, -7eb899, -84621d, -9a734c
- **Reserved:** DEC-20261002-e0aa2b (composer). It is listed under `identifiers_reserved`, never in `target_ids`.
- **Returned unused:** DEC-20261002-f8314c, TASK-20261002-ba36a5, TASK-20261002-f65334.

## 5. Bus pointers to send (after TASK-20261002-230174 verifies; check the outbox first; never duplicate; record the MSG ids in 230174's completion record)

**(a) To `coordinator-qsp-run-20260921`**

- thread / in_reply_to: MSG-20260929-fb57f1
- refs: DEC-20261002-86a7e0, DEC-20260929-01ea31, EXP-QSP-70b731, BATCH-2d2fa1, BATCH-2c4a9c, BATCH-9dbda3, BATCH-ed05f2, BATCH-ee209c, TASK-20260921-1a4c29, TASK-20260921-a3e767, TASK-20260921-3c833e, TASK-20260921-ee3c32
- subject: `GOAL-ECDLP2M-001: EXP-QSP-70b731 custody successor opened as BATCH-2d2fa1 on slot 1; archival ownership of the run files already on main passes to it at snapshot verification`
- body: `Pointer only; no task, no permission. DEC-20261002-86a7e0 opens the scoped EXP-QSP-70b731 custody successor (BATCH-2d2fa1, seven cards, zero runs). It binds content_first only the run files already on main (R-ENUM, .gitkeep excluded). When TASK-20261002-5e1246 verifies, archival ownership of exactly those paths passes to it, superseding for those paths only the unbound declarations of TASK-20260921-1a4c29, -a3e767, -3c833e and -ee3c32 (R-BIND). No QSP queue, handoff, claim or lane record is edited; DEC-20260921-7a8d6b, -5de324, -e9f312 and -f0e100 are untouched; paths not on main stay yours. Noted: all four of your ledger-archive cards reserve EV-QSP-d206e6 and DEC-20260921-c97a41; this batch uses neither. If you answer before TASK-20261002-5e1246 runs, the snapshot waits and the next /coordinate pass rules on your answer (R-QSP-RETURN). Please say whether output of the BATCH-2c4a9c continuation exists anywhere outside main. Official once TASK-20261002-230174 verifies.`

**(b) To `coordinator` (broadcast)**

- refs: DEC-20261002-86a7e0, DEC-20260929-01ea31, GOAL-ECDLP2M-001, BATCH-2d2fa1, EXP-QSP-70b731
- subject: `GOAL-ECDLP2M-001: EXP-QSP-70b731 custody successor opened as BATCH-2d2fa1 on slot 1; FINDING-QSP-DOUBLE-DECLARATION corrected; do not duplicate`
- body: `Pointer only; no task, no permission. DEC-20261002-86a7e0 re-rules R-CUSTODY and opens BATCH-2d2fa1 (seven cards, zero runs) on slot 1 of GOAL-ECDLP2M-001. FINDING-QSP-DOUBLE-DECLARATION is corrected additively: the cross-queue declaration of the run files already exists inside the QSP lane, is unbound, and is not refused by the tools. The experiments/EXP-QSP-70b731/runs/ read exclusion is lifted only for TASK-20261002-345dbd, -5e1246 and -7eb899; every other card of every other batch keeps it. Slot 1 is occupied until this lane closes, then goes to the S1 version-4 revision (DEC-20260929-54dcd8 CH-B) or U-HOLDH. Official once TASK-20261002-230174 verifies.`

## 6. Session duties before TASK-20261002-230174

1. Parse every file in section 2. A failure goes back to a Coordinator session.
2. Diff the goal head for zero deleted lines.
3. Run `git fetch` and merge origin/main (merge, never rebase).
4. **R-ENUM.**
   - Run `git ls-files experiments/EXP-QSP-70b731/runs/`, drop `.gitkeep`, and sort bytewise.
   - Append the paths to BOTH `write_scope` and `artifact_paths` of the TASK-20261002-345dbd queue entry, after the inventory path.
   - Add a `tasks_state_revisions` entry with the command, the base commit and the count.
   - STOP unless all of these hold:
     - exactly 157 paths;
     - exactly 16 RUN-QSP-* directories: thirteen with 10 files, 1df59e with 11, 715b58 with 8, cec70a with 8;
     - none of 12a389, 15a2ab, 186d9d, 7faa1b, d10c74 or ef2490 is present;
     - no path lies outside a RUN-QSP-* directory.
   - Open no file.
5. Read `verify_archive` in `tools/research_dispatch.py` and record in the receipt whether it confirms or refutes C5.
6. `validate_ledger.py` must be at or below 122, with no new error on the staged paths. Also run `check_merge_hygiene.py`.
7. Render the queue: card 1 completed, card 2 ready, the rest blocked. Check that the R-ENUM fill keeps the queue valid.
8. Claim only if the goal-wide live count is at most 2. Commit 230174 ALONE with the 11 paths. Verify, push, and open or refresh the PR naming every id. Then run `goal_lanes.py open-lane GOAL-ECDLP2M-001 BATCH-2d2fa1 --queue … --decision DEC-20261002-86a7e0 --as <addr> --publish`. Then post section 5.

## 7. Points the dispatcher must not miss

- **345dbd** is mechanical. No model opens a run file.
- **5e1246** runs the R-QSP-RETURN check first (bus plus the four QSP renders). It is content_first. It stages only the inventory and its receipt; `path_sha256` covers the inventory, all 157 run paths and the receipt. Its commit message lists the sixteen RUN-QSP ids.
- **7eb899 launch prompt:**
  - It names the card, its inputs and its scratch path.
  - It carries no run value and no R-PRIOR or R-KEYS text.
  - review-adversarial at xhigh. If that cannot be served, do not dispatch; record an impediment.
- **84621d** gets the sha256 of `run-validation.yaml` and `computations.json` pasted into its launch prompt. It opens nothing under runs/.
- **9a734c** closes the lane with `--decision DEC-20261002-e0aa2b`.
