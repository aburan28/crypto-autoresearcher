# Opening brief: QSP-SUCC on GOAL-ECDLP2M-001 slot 2, 2026-10-02 (session rm3mrv)

The top-level session wrote this brief before dispatching the Coordinator
subagent. It is not a record; the Coordinator's decision is.

## 1. Checkout

- Branch: `claude/index-calculus-ecdlp-ecc2k-rm3mrv` contains origin/main (merge
  "Already up to date").
- PR #1568 is open. It carries:
  - the BATCH-f435ab archive TASK-20261002-b68b72 (DEC-20261002-353743) and
    the lane closing;
  - the BATCH-2e63c3 U-HOLDH snapshot TASK-20261002-ffb7bb.
- `validate_ledger.py`: 122 errors, the same as origin/main.

## 2. Why now

- **BATCH-f435ab (slot 2) is CLOSED.** It was archived by TASK-20261002-b68b72
  at 1a25c61480.
- **DEC-20261002-353743 SP-1** gives the freed slot 2 to QSP-SUCC under
  DEC-20261002-21a63d R-ORDER-2. If QSP-SUCC is already open elsewhere, the
  slot goes to LANE-B-V4 instead.
- **NISTBIN-V4 entered the order** at position (3a).

## 3. QSP facts at this pass (git fetch just before this brief)

- **The run owner, coordinator-qsp-run-20260921, has not replied** on the bus
  since MSG-20260921-*. That covers the pointers MSG-20261002-cadc09,
  -172d36, -316c99 and -65261e.
- **QSP claims.** BATCH-2c4a9c TASK-20260921-9f84a3 and BATCH-9dbda3
  TASK-20260921-f80a35 have claim files from 2026-09-21 and no release. Their
  TTLs expired long ago, and `research_dispatch.py --claims refs` rendered no
  live QSP claim at the BATCH-2d2fa1 snapshot (R-QSP-RETURN clear).
- **The QSP branch** exec/qsp-70b731-run-20260921 is unchanged at 8164cc5b96.
- **Inbox.** The only non-rm3mrv messages are PFDR (EXP-PFDR-011cd0, another
  goal), which is unrelated.
- **Standing rulings** (read in full):
  - DEC-20261002-5e691c R-CONTINUATION: superseded for execution.
  - DEC-20261002-5e691c R-QSP-SUCC: the discharge table D-1 to D-8 and the
    carried_conditions of DEC-20261002-e0aa2b.

## 4. Slots

| Slot | Holder | Live claim |
|---|---|---|
| 1 | BATCH-f6b7c5 (S1 v4 review round) | TASK-20261002-6084fa |
| 2 | FREE | none |
| 3 | BATCH-2e63c3 (U-HOLDH review round) | TASK-20261002-b8360c |

## 5. What this pass must rule

1. **R-NOT-DUPLICATED.** Confirm QSP-SUCC is not open elsewhere. If it is,
   assign slot 2 to LANE-B-V4 per SP-1 and R-ORDER-2.
2. **Open QSP-SUCC on slot 2** as the shape DEC-20261002-5e691c R-QSP-SUCC and
   DEC-20261002-e0aa2b NA-4 / defect_return describe. Decide, with reasons:
   - whether the successor is a new experiment record superseding
     EXP-QSP-70b731, a protocol amendment, or an implementation-repair batch
     under the existing approval;
   - who implements the D-1 to D-8 repairs. Implementation is executor work;
     a design and zero-run review stage comes first. Never approve a run or
     launch one here.
3. **Write the complete opening package:**
   - the opening DEC;
   - the queue;
   - every handoff card;
   - a review plan frozen before any producer runs, at the tier the decision
     class requires;
   - allowed_session_computations for a shell-less producer;
   - reviewer launch prompts stored verbatim in the plan (the BATCH-2e63c3
     pattern).
4. **R-QSP-RETURN.** Rule how a late owner reply is treated, consistent with
   DEC-20261002-5e691c.

## 6. Pre-minted ids (all 23 `--check` OK on 2026-10-02)

| Kind | Ids |
|---|---|
| Batch | BATCH-4708f7 |
| Decisions | DEC-20261002-a63f13, -6e68d8, -0d2451 |
| Experiment | EXP-QSP-d7df70 |
| Hypothesis | H-QSP-a90237 |

Handoffs, all prefixed TASK-20261002-:

| | | | | | |
|---|---|---|---|---|---|
| 66334f | bbb1a1 | c5d9e7 | f0f7e0 | 3b6a02 | 323713 |
| c81b2e | 55bec1 | 0abdcf | e0b22e | b72830 | da15a4 |
| 9c44a4 | 044e12 | 1874c9 | 1b8018 | 1b1225 | |

Name the ids you leave unused. Name any extra ids you need and the session
mints them.

## 7. Lessons (apply in every card and plan)

- Store launch prompts verbatim in the plan, and pass only the scratch path.
- No synthetic group may coincide with a declared cell.
- Producers write prose as folded blocks, check list-item and key
  indentation, and parse-check their own files.
- Never export whole git trees, because the disk is shared.
- Record pre-gate digests before any gate.
- A card's read_scope is widened only by a Coordinator decision.
- Name the batch's composer id exactly in every card.
- State the interpreter actually present: /usr/local/bin/python3 is
  Python 3.11.15, so there is no `random.binomialvariate`.

## 8. Excluded reads (binding)

- **Not read at all:**
  - experiments/EXP-FROB-30006a/
  - ref origin/cursor/semaev-2015-audit-program-5b8b
  - PR #1377
  - branch cursor/ecdlp2m-revision-design-3d1a
  - the in-flight review directories under BATCH-f6b7c5/reviews/ and
    BATCH-2e63c3/reviews/
- **experiments/EXP-QSP-70b731/runs/:** the BATCH-2d2fa1 lift ended with that
  lane. Read it only through the archived TASK-20261002-7eb899
  run-validation.yaml, the inventory, and DEC-20261002-e0aa2b. A card that
  needs run-file content must have its read lifted by name in your decision.

## 9. After you return

The session parses and validates the package, runs research_dispatch, makes
the isolated opening archive, sends the pointers you name, opens the lane,
pushes, opens a PR, and dispatches after a claim. It never launches
scientific runs.
