# Opening brief: NISTBIN-V4 on GOAL-ECDLP2M-001 slot 3, 2026-10-02 (session rm3mrv)

The top-level session wrote this brief before dispatching the Coordinator
subagent. It records checkout facts that the subagent cannot fetch. It is not
a record; the Coordinator's decision is.

## 1. Checkout

- **Branch:** `claude/index-calculus-ecdlp-ecc2k-rm3mrv` contains origin/main.
  - PR #1573 merged at 5c1fb24668. It carried the LANE-B-V4 opening
    (DEC-20261002-8cabf8) and the QSP-SUCC design snapshot.
  - The latest merge of main into the branch is 5dcb083d60.
- **PR #1578 is open.** It carries the BATCH-2e63c3 U-HOLDH round:
  - archive TASK-20261002-49bbba at c445ff679d;
  - DEC-20261002-c9ec6b (revise);
  - the lane closing at 319a06ea2f.
- **`validate_ledger.py`:** 122 errors, the branch baseline.

## 2. Why now

- **BATCH-2e63c3 (slot 3) is CLOSED.** DEC-20261002-c9ec6b ruled revise:
  EXP-BINSTD-f442a9 is not approved, and U-HOLDH-V2 enters at position (3c).
- **Its SP-1** gives the freed slot to NISTBIN-V4 under DEC-20261002-8cabf8
  R-ORDER-4 (2). If NISTBIN-V4 is open elsewhere, the slot goes to S1-V5 at
  the same pass.
- **DEC-20261002-353743 NA-1 is the operative text.** It calls for a NISTBIN
  version-4 revision design batch for EXP-NISTBIN-451dfa and H-NISTBIN-dec5e1,
  with these terms:
  - It discharges RV3-1 to RV3-14 by number.
  - C1-C8 and tripwire T1 still bind.
  - The review plan is frozen before the producer runs, at review-breakthrough,
    max, non-degradable.
  - It carries 353743's next_plan_items.
  - The record form is for this batch's opening decision to rule.

## 3. Slots (goal-wide max_concurrent 3, counted in live claims)

| Slot | Holder | Live claim |
|---|---|---|
| 1 | BATCH-d08b44 (LANE-B-V4 producer) | TASK-20261002-f48089 |
| 2 | BATCH-4708f7 (QSP-SUCC design round) | TASK-20261002-323713 (red team) |
| 3 | FREE (BATCH-2e63c3 closed) | none |

## 4. Facts found at this pass (git fetch just before this brief)

- **R-NOT-DUPLICATED for NISTBIN-V4.**
  - `goal_lanes.py lanes GOAL-ECDLP2M-001` shows no NISTBIN-V4 lane. The open
    lanes are BATCH-4708f7 and BATCH-d08b44 (rm3mrv), BATCH-1faf6f (dcc3), and
    the four QSP-owner lanes, none of which holds a live claim.
  - No decision or coordination/goals file in the own diff of any origin branch
    committed in the last three days names NISTBIN-V4 (excluded refs not read).
  - The only bus messages naming NISTBIN-V4 are this session's three.
  - Your own re-check is binding.
- **DEC-20261002-08c3f8** (session ed0c) is still not on origin/main.

## 5. What this pass must rule

1. **R-NOT-DUPLICATED** and the slot-3 assignment under c9ec6b SP-1 and
   R-ORDER-4.
2. **If NISTBIN-V4 opens, write the complete opening package:**
   - the opening DEC;
   - the queue;
   - every handoff card (opening archive, revision design card, snapshot,
     reviewers, composer, archive);
   - a review plan frozen before any producer runs, at review-breakthrough max,
     with reviewer launch prompts stored verbatim (the BATCH-2e63c3 pattern);
   - allowed_session_computations for a shell-less producer.

   Exemplar: the BATCH-f435ab NISTBIN version-3 package (its queue, its
   handoffs, plan coordination/review/nistbin-20261002-f435ab/review-plan.yaml,
   archive TASK-20261002-b68b72, DEC-20261002-353743). Use the BATCH-d08b44
   package as a structural cross-check.

## 6. Pre-minted ids (all `--check` OK on 2026-10-02)

| Kind | Ids |
|---|---|
| Batch | BATCH-bc5bd5 |
| Decisions | DEC-20261002-3ba55f, -09e2be, -92615f |
| Hypothesis | H-NISTBIN-039327 |
| Experiment | EXP-NISTBIN-155759 |

Handoffs, all TASK-20261002-:

| | | | | | | |
|---|---|---|---|---|---|---|
| 1afe54 | e1cc23 | e11714 | 1d1f48 | ccdc5f | aeaf93 | f19cfa |
| ee63af | 16c2f1 | fb61ea | 970085 | 7e81a0 | a5334d | 6ad28c |

Name the ids you leave unused. Name any extra ids you need and the session will
mint them.

## 7. Lessons (apply in every card and plan)

- **Embedded queue handoffs.** Each one carries nonempty `objective` and
  `uncertainty_reduced`, and nonempty `inputs`, `constraints`, `deliverables`
  and `completion_gate` lists, matching the ledger handoff records.
- **Launch prompts.** Store them verbatim in the plan and pass only the scratch
  path.
- **YAML.** Producers AND composers write prose as folded blocks. No mapping key
  sits at list-item indent. The BATCH-2e63c3 composer's worksheet failed to
  parse on exactly this pattern.
- **Composer cards.** Remind the composer that it has no shell. The session
  supplies the pre-read digests and parses its files.
- **Shell-less producers.** Their runtime may force an interim hand-back before
  a relay arrives. Cards should say that the producer is resumed with the relay,
  and that it marks an interim hand-back INCOMPLETE.
- **No synthetic group may coincide with a declared cell.**
- **Interpreter.** /usr/local/bin/python3 is Python 3.11.15. `/usr/bin/time` is
  not installed; use the bash `time` keyword.
- **Never export whole git trees,** because the disk is shared.
- **Pre-gate digests** are recorded before any gate.
- **read_scope** is widened only by a Coordinator decision.

## 8. Excluded reads (binding)

- experiments/EXP-QSP-70b731/runs/
- experiments/EXP-FROB-30006a/
- ref origin/cursor/semaev-2015-audit-program-5b8b
- PR #1377
- branch cursor/ecdlp2m-revision-design-3d1a
- the in-flight review, design and composition directories under BATCH-4708f7/
  and BATCH-d08b44/

The BATCH-2e63c3 and BATCH-f435ab reports are committed and may be read.

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
