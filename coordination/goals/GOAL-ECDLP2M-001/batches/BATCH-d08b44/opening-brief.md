# Opening brief: LANE-B-V4 on GOAL-ECDLP2M-001 slot 1, 2026-10-02 (session rm3mrv)

The top-level session wrote this brief before dispatching the Coordinator
subagent. It records checkout state the subagent cannot fetch. It is not a
record; the Coordinator's decision is.

## 1. Checkout

- Branch `claude/index-calculus-ecdlp-ecc2k-rm3mrv` contains origin/main
  f19ce624f0 (merged with a merge commit).
- PR #1570 is open and carries:
  - the BATCH-f6b7c5 round (DEC-20261002-a75609, archive TASK-20261002-d98069
    f04e7d9d99) and that lane's close;
  - the QSP-SUCC opening, BATCH-4708f7 (DEC-20261002-a63f13, archive
    TASK-20261002-bbb1a1 13df559f26, lane opened 078ac9fa04, pointers
    MSG-20261002-077a75 and MSG-20261002-3fdadf).
- `validate_ledger.py`: 122 errors, the branch baseline.

## 2. Why now

- **BATCH-f6b7c5 (slot 1) is CLOSED.** Its archive TASK-20261002-d98069
  verified, and the lane claim is released.
- **DEC-20261002-a75609 CH-1** gives the freed slot 1 to LANE-B-V4 if
  QSP-SUCC's opening is committed or holds a live claim. It is committed
  (13df559f26), and design card TASK-20261002-c5d9e7 holds a live claim. If
  another session has opened LANE-B-V4, the slot passes to NISTBIN-V4 with the
  reason recorded.
- **DEC-20261002-a63f13 R-ORDER-3 (2)** names LANE-B-V4 the head of the
  standing order.
- **DEC-20260929-585602 NA-1** is the operative text: one zero-run lane-B
  version-4 revision design batch. EXP-BINSTD-c9c8a2 is not approved, and
  RV-1 to RV-15 are listed.

## 3. Slots (goal-wide max_concurrent 3, counted in live claims)

| Slot | Holder | Live claim |
|---|---|---|
| 1 | FREE (BATCH-f6b7c5 closed) | none |
| 2 | BATCH-4708f7 (QSP-SUCC design) | TASK-20261002-c5d9e7 |
| 3 | BATCH-2e63c3 (U-HOLDH review round) | TASK-20261002-2214e9 (validator) |

## 4. Facts found at this pass (git fetch just before this brief)

- **R-NOT-DUPLICATED for LANE-B-V4.**
  - `goal_lanes.py lanes GOAL-ECDLP2M-001` shows no lane-B-v4 lane.
  - The only open lanes are BATCH-2e63c3 and BATCH-4708f7 (rm3mrv),
    BATCH-1faf6f (dcc3), and BATCH-2c4a9c, -9dbda3, -ed05f2, -ee209c (QSP owner,
    no live claim).
  - No decision on origin/main or on a branch committed in the last three days
    names LANE-B-V4 or EXP-BINSTD-c9c8a2 in its own diff (excluded refs not
    read).
  - Your own re-check is binding.
- **Another session's approval on this goal, NOT on main.** Branch
  `origin/cursor/design-certbin-theta-ladder-ed0c` (head 9a7849e443, session
  ed0c) carries DEC-20261002-08c3f8, `decision: approve`. It:
  - specifies H-CERTBIN-6e6287 and approves EXP-CERTBIN-fad576 under standing
    authorization, from IDEA-20260926-4b65e3 (HOLD-X1 theta(m) ladder,
    Stages 1-3; "Stage 0 absorbed into S1");
  - names GOAL-ECDLP2M-001, RQ-CERTBIN-836ce2 and RQ-BINSTD-b6f698;
  - has the next_action `/run EXP-CERTBIN-fad576`;
  - was archived by TASK-20261002-49d9e0;
  - was not opened through `goal_lanes.py`;
  - states that it did not edit the shared goal head.

  IDEA-20260926-4b65e3 is a record id of the BATCH-f6b7c5 lane-A round
  (DEC-20261002-a75609), and HOLD-X1 is among DEC-20260929-7257b2's holds. The
  session has not read that branch beyond this decision's header lines and file
  list, and it makes no ruling. Rule, with reasons, whether it bears on the
  slot accounting (R-SLOT), the standing order, or S1-V5, and name any pointer
  the session should send. Do not edit that branch.
- **Recently updated branch.** `origin/cursor/design-binstd-subfield-factor-base-a6f3`
  (head 36304ca404) carries many EXP-BINSTD design snapshots under
  `coordination/design/`. None of its own decision or goal files names
  LANE-B-V4, EXP-BINSTD-c9c8a2 or GOAL-ECDLP2M-001.

## 5. What this pass must rule

1. **R-NOT-DUPLICATED,** and the slot-1 assignment under CH-1 and R-ORDER-3.
   If you defer the head item, record the reason and the cost (rule 9).
2. **The 08c3f8 fact above:** its standing relative to this goal's slots and
   order.
3. **If LANE-B-V4 opens, the complete opening package:**
   - the opening DEC;
   - the queue;
   - every handoff card (opening archive, revision design card, snapshot,
     reviewers, composer, archive);
   - a review plan frozen before any producer runs, at the tier the decision
     class requires, with reviewer launch prompts stored verbatim (the
     BATCH-2e63c3 pattern);
   - allowed_session_computations for a shell-less producer.

   Exemplar: the BATCH-35bdda lane-B package (producer TASK-20260929-749b50,
   snapshot TASK-20260929-78e02e, plan
   coordination/review/binstd-b-20261001-35bdda/review-plan.yaml, archive
   TASK-20260929-afdc95, DEC-20260929-585602).

## 6. Pre-minted ids (all `--check` OK on 2026-10-02)

| Kind | Ids |
|---|---|
| Batch | BATCH-d08b44 |
| Decisions | DEC-20261002-8cabf8, -962278, -e5d428 |
| Hypothesis | H-BINSTD-9b29a0 |
| Experiment | EXP-BINSTD-811a2e |

Handoffs, all prefixed TASK-20261002-:

| | | | | | | |
|---|---|---|---|---|---|---|
| a71f78 | b1f036 | f48089 | 8b2165 | 1e7a71 | ed5777 | bce101 |
| 997dbb | b28b83 | 9dbae9 | f74511 | 83f198 | 936b90 | 94eb94 |

Name the ids you leave unused. Name any extra ids you need and the session
mints them.

## 7. Lessons (apply in every card and plan)

- Store launch prompts verbatim in the plan, and pass only the scratch path.
- **Copy every handoff field the dispatcher needs into the queue copy.** The
  BATCH-4708f7 queue first failed research_dispatch because 14 embedded
  handoffs lacked `uncertainty_reduced`. Each embedded handoff needs
  `objective` and `uncertainty_reduced` as nonempty text, and `inputs`,
  `constraints`, `deliverables` and `completion_gate` as nonempty lists.
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

- experiments/EXP-QSP-70b731/runs/
- experiments/EXP-FROB-30006a/
- ref origin/cursor/semaev-2015-audit-program-5b8b
- PR #1377
- branch cursor/ecdlp2m-revision-design-3d1a
- the in-flight review, design and composition directories under
  BATCH-2e63c3/ and BATCH-4708f7/

The BATCH-f6b7c5 review reports are committed (d98069) and may be read.

## 9. After you return

The session:
1. parses and validates every file;
2. runs `research_dispatch.py`;
3. makes the isolated opening archive;
4. sends the pointers you name;
5. opens the lane;
6. pushes and refreshes the PR;
7. dispatches the producer after a claim.

It never launches scientific runs.
