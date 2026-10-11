# Opening brief: GOAL-ECDLP2M-001 slot-3 selection point after BATCH-35bdda closed, 2026-10-02 (session rm3mrv)

The top-level session wrote this brief before dispatching the Coordinator
subagent. It records checkout state the subagent cannot fetch; it is not a
record. The Coordinator's decision is.

## 1. Checkout

- **Branch:** `claude/index-calculus-ecdlp-ecc2k-rm3mrv` contains origin/main, which includes:
  - PR #1555 (DEC-20261002-5e691c and DEC-20261002-f61a75, the BATCH-f6b7c5 opening);
  - PR #1559 (the lane-A version-4 snapshot TASK-20261002-c21ce2).
- **PR #1561, open:** carries the BATCH-35bdda lane-B archive and the lane's closing.
- **`validate_ledger.py`:** 122 errors, the same as origin/main.

## 2. What closed

- **BATCH-35bdda is CLOSED.** Both lane archives have verified:
  - lane A: TASK-20260929-a80339, DEC-20260929-54dcd8;
  - lane B: TASK-20260929-afdc95 at 02e4ce2053, DEC-20260929-585602.
- **DEC-20260929-585602 ruled K-revise-defect.** EXP-BINSTD-c9c8a2 is not approved, and RV-1 to RV-15 are listed.
  - **Its NA-1** opens a zero-run lane-B version-4 revision design batch "on the slot this lane frees (SPC-2) under the R-SLOT claim rule".
  - **Its PD-C2 discloses** that its composer did NOT read DEC-20260929-54dcd8, DEC-20260929-7257b2 or DEC-20261002-f61a75. SPC-2 says the next selection point reconciles the slot.

## 3. Slots (goal-wide max_concurrent 3, counted in live claims)

| Slot | Holder | Live claim |
|---|---|---|
| 1 | BATCH-f6b7c5 (S1 v4 review round) | TASK-20261002-aba8f9 (red team) |
| 2 | BATCH-f435ab (NISTBIN v3 review round) | TASK-20261002-4cb903 (red team) |
| 3 | FREE (BATCH-35bdda closed) | none |

**Competing claimants for slot 3:**
- **DEC-20261002-f61a75 R-ORDER**, later and written with both in view of R-SLOT: "the next goal slot that frees goes to U-HOLDH (DEC-20260929-7257b2 rank 3), the one after that to QSP-SUCC (DEC-20261002-5e691c), then 7257b2 ranks 4 to 9. Any decision that assigns a freed slot otherwise must record a new reason and its cost."
- **DEC-20260929-585602 NA-1 / SPC-2:** the lane-B version-4 revision on the slot this lane frees, which f61a75 did not foresee. f61a75 was written before 585602 existed.

## 4. What this pass must rule

1. **The slot-3 assignment.** Reconcile R-ORDER and 585602 NA-1/SPC-2, with reasons, and apply rule 9 to whichever is deferred. Record:
   - the cost of waiting;
   - the revisit condition;
   - the successor's position in the standing order.
2. **If a batch opens on slot 3,** write its complete opening package:
   - the opening DEC;
   - the queue;
   - every handoff card;
   - a review plan frozen before any producer runs (review-breakthrough at max, non-degradable, where the class requires it);
   - allowed_session_computations for a shell-less producer.

   Exemplars:
   - **For lane-B v4:** the BATCH-35bdda lane-B package (producer TASK-20260929-749b50, snapshot -78e02e, plan coordination/review/binstd-b-20261001-35bdda/review-plan.yaml).
   - **For a fresh design batch:** the BATCH-f6b7c5 package.

## 5. Pre-minted ids (all 32 `--check` OK on 2026-10-02)

| Kind | Ids |
|---|---|
| Batches | BATCH-2e63c3, BATCH-4708f7 |
| Decisions | DEC-20261002-21a63d, -c9ec6b, -a63f13, -6e68d8, -0d2451 |
| Hypotheses | H-BINSTD-0dd2ce, H-BINSTD-75ba73 |
| Experiments | EXP-BINSTD-f442a9, EXP-BINSTD-955119 |

Handoffs, all TASK-20261002-:

| | | | | | | |
|---|---|---|---|---|---|---|
| 5e1ef2 | cee59d | 9f9ce5 | ffb7bb | b8360c | 2214e9 | 17bf2f |
| 8d288b | 97a1ea | 49bbba | 66334f | bbb1a1 | c5d9e7 | f0f7e0 |
| 3b6a02 | 323713 | c81b2e | 55bec1 | 0abdcf | e0b22e | b72830 |

Name any ids you need in another area and the session will mint them. Name any you leave unused.

## 6. Lessons the session carries, for any plan written now

- **Concurrent reviewers.** Write launch prompts from plan text only. Never paraphrase a sibling's finding after its report returns; this cost the lane-B round SD-1.
- **Producer computations.** A dry call on a group the contract declares as a cell fires TB-4. State in allowed_session_computations that synthetic groups must not coincide with any declared cell group, at any alphabet.
- **Producer YAML.** The producers' plain scalars containing ": " broke parsing twice. Ask producers to use folded blocks for prose.
- **Scratch discipline.** Never export whole git trees. One reviewer filled the shared disk.
- **Pre-gate digests.** Record them before any gate step.

## 7. Excluded reads, binding on every card

- experiments/EXP-QSP-70b731/runs/
- experiments/EXP-FROB-30006a/
- ref origin/cursor/semaev-2015-audit-program-5b8b
- PR #1377
- branch cursor/ecdlp2m-revision-design-3d1a
- the in-flight review directories under BATCH-f435ab/reviews/ and BATCH-f6b7c5/reviews/

The BATCH-35bdda review reports are now committed (afdc95) and may be read.

## 8. After you return

The session:
1. parses and validates every file;
2. runs `research_dispatch.py`;
3. makes the isolated opening archive;
4. sends the pointers you name;
5. opens the lane;
6. pushes and opens a PR;
7. dispatches the producer after a claim.

It never launches scientific runs.
