# Opening brief: QSP-SUCC-R on GOAL-ECDLP2M-001 slot 2, 2026-10-02 (session rm3mrv)

The top-level session wrote this brief before dispatching the Coordinator
subagent. It records checkout facts that the subagent cannot fetch. It is not a
record; the Coordinator's decision is.

## 1. Checkout

- **Branch:** `claude/index-calculus-ecdlp-ecc2k-rm3mrv`. It contains origin/main
  through PR #1573.
- **PR #1578 is open.** It carries three acts:
  - The U-HOLDH v1 round: DEC-20261002-c9ec6b, revise.
  - The NISTBIN-V4 opening: DEC-20261002-3ba55f, BATCH-bc5bd5.
  - The QSP-SUCC round-1 composition and BATCH-4708f7 lane close: archive
    TASK-20261002-0abdcf at c251b97703, DEC-20261002-6e68d8, closed at
    5d6d91b0c7.
- **`validate_ledger.py`:** 122 errors, the branch baseline.

## 2. Why now

- **BATCH-4708f7 (slot 2) is CLOSED.** DEC-20261002-6e68d8 ruled K-design-revise.
  - The TASK-20261002-c5d9e7 repair design is refused.
  - amendment-v2.yaml (AMD-20261002-1303c4) is refused. The id is used, the file
    is unedited, and a revision needs a new AMD id and path.
  - DEC-20261002-0d2451 is returned unused.
  - Cards 10 to 16 are cancelled.
- **DEC-20261002-6e68d8 SP-1 gives slot 2 to QSP-SUCC-R:** a zero-run QSP-SUCC
  design revision carrying DR-1 to DR-14. It is conditional on NISTBIN-V4 already
  holding a goal slot or a live claim on a committed opening.
  - The proviso holds. NISTBIN-V4 was opened as BATCH-bc5bd5 by archive
    TASK-20261002-e1cc23 at 4d6089ad8f, and producer TASK-20261002-e11714 holds a
    live claim.
- **NA-5 and NA-6** are re-carried to the QSP-SUCC-R decision that accepts a
  repaired closure.

## 3. Slots (goal-wide max_concurrent 3, counted in live claims)

| Slot | Holder | Live claim |
|---|---|---|
| 1 | BATCH-d08b44 (LANE-B-V4 producer) | TASK-20261002-f48089 |
| 2 | FREE (BATCH-4708f7 closed) | none |
| 3 | BATCH-bc5bd5 (NISTBIN-V4 producer) | TASK-20261002-e11714 |

## 4. Facts at this pass (git fetch just before this brief)

- **R-NOT-DUPLICATED:** no lane, decision or bus message names QSP-SUCC-R. The
  label exists only in DEC-20261002-6e68d8. Your own re-check is binding.
- **R-QSP-RETURN:**
  - The owner coordinator-qsp-run-20260921 has no message after
    MSG-20260921-ec3b3d.
  - No QSP queue holds a live claim.
  - origin/exec/qsp-70b731-run-20260921 is at 8164cc5b96.
  - The session has not seen a foreign commit under experiments/EXP-QSP-70b731/.
  - This session's pointers: MSG-20261002-f6fd38 (to coordinator) and
    MSG-20261002-6005ad (to the owner, thread MSG-20261002-172d36).
- **Prior-round material now committed and readable:**
  - the TASK-20261002-c5d9e7 design and amendment-v2 (snapshot f0f7e0,
    2d5deb6b62);
  - the three round-1 reports (3b6a02, 323713, c81b2e);
  - the composition worksheet;
  - DEC-20261002-6e68d8 with its DR-1 to DR-14 defect list.
- **TQ-3 history:**
  - The c5d9e7 producer (PD-1) and reviewer 323713 (RTD-1 to RTD-3) self-reported
    mental evaluations on declared cells.
  - DEC-20261002-6e68d8 says those sessions must hold no card that authors or
    checks Stage 0, C2 or C4 values.
  - Independence notes on the new cards must exclude them.

## 5. What this pass must rule

1. **R-NOT-DUPLICATED** and the slot-2 assignment under SP-1.
2. **If QSP-SUCC-R opens, write the complete opening package:**
   - The opening DEC.
   - The queue.
   - Every handoff card: opening archive, revision design card, snapshot, round-1
     reviewers, composer, archive, and the conditional later cards if you keep the
     a63f13 shape.
   - Review plan(s) frozen before any producer runs, at the tier the decision class
     requires, with every launch prompt stored verbatim. Include the producer and
     composer prompts, as BATCH-bc5bd5 did.
   - allowed_session_computations for the shell-less producer, with the
     INCOMPLETE/resume rule.
   - Whether DR-1 to DR-14 can be discharged under the existing approval
     DEC-20260920-2b276f, as a63f13 R-FORM held, or need a new record. Give
     reasons.

   Exemplar: the BATCH-4708f7 package (DEC-20261002-a63f13, its queue and cards,
   coordination/review/qsp-succ-d-20261002-4708f7/review-plan.yaml).

## 6. Pre-minted ids (all `--check` OK on 2026-10-02)

| Kind | Ids |
|---|---|
| Batch | BATCH-521e9d |
| Decisions | DEC-20261002-c01bb7, DEC-20261002-ff2bd5, DEC-20261002-e23776 |
| Amendment (random token, whole-tree search 0 hits) | AMD-20261002-09957b |

Handoffs, all prefixed TASK-20261002-:

| | | | | | | | |
|---|---|---|---|---|---|---|---|
| d102b6 | aa2b91 | 01d26d | 9831c4 | 865f15 | 820856 | efd590 | eced26 |
| ea2ed7 | 38ffea | 909f2c | 34584f | 60ec76 | 4c19d4 | c6bdf7 | fa1d96 |

Name the ids you leave unused. Name any extra ids you need, and the session will
mint them. That includes RUN-QSP ids, which are minted only before an
implementation card is dispatched.

## 7. Lessons (apply in every card and plan)

- **Embedded queue handoffs** carry nonempty `objective` and `uncertainty_reduced`,
  plus nonempty `inputs`, `constraints`, `deliverables` and `completion_gate` lists
  that match the ledger handoffs.
- **All YAML authors** write prose as folded blocks. No mapping key sits at
  list-item indent.
- **Composers have no shell.** The session supplies the pre-read digests and parses
  their files.
- **Shell-less producers** may be forced into an interim hand-back. They mark it
  INCOMPLETE and are resumed with the relay.
- **Interpreter:** /usr/local/bin/python3 is Python 3.11.15. `/usr/bin/time` is not
  installed; use the bash `time` keyword. numpy is available if a card admits it;
  record its version.
- **Cost figures** need measured rates on synthetic inputs (DEC-20261002-6e68d8
  adopted O-1). A model-only figure is not enough where a measurement is cheap.
  Measurements on a contended host are disclosed.
- **No synthetic group or cell** may coincide with a declared cell.
- **Never export whole git trees.** The disk is shared.
- **Record pre-gate digests** before any gate.
- **read_scope** is widened only by a Coordinator decision.

## 8. Excluded reads (binding)

- experiments/EXP-QSP-70b731/runs/ (no lift unless your decision names one).
- experiments/EXP-FROB-30006a/
- ref origin/cursor/semaev-2015-audit-program-5b8b
- PR #1377
- branch cursor/ecdlp2m-revision-design-3d1a
- the in-flight design, review and composition directories under BATCH-d08b44/
  and BATCH-bc5bd5/
- every path in the EXP-QSP-70b731 specification's blind_from

## 9. After you return

1. The session parses and validates every file.
2. It runs `research_dispatch.py`.
3. It makes the isolated opening archive.
4. It sends the pointers you name.
5. It opens the lane.
6. It pushes and refreshes the PR.
7. It dispatches the producer after a claim.

It never launches scientific runs.
