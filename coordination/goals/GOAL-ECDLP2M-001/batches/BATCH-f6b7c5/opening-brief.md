# Opening brief: GOAL-ECDLP2M-001 selection point after BATCH-2d2fa1 closed, 2026-10-02 (session rm3mrv)

The top-level session wrote this brief before dispatching the Coordinator
subagent. It records checkout state the subagent cannot fetch, because the
subagent has no shell. It is not a record; the Coordinator's decision is.

## 1. Checkout and merges

- The branch `claude/index-calculus-ecdlp-ecc2k-rm3mrv` contains origin/main.
  The last merge is "Already up to date" after PR #1548, merged at 92cc00b91b.
- PR #1551 is open and not yet merged. It carries:
  - the BATCH-2d2fa1 custody round, closed;
  - the BATCH-f435ab NISTBIN version-3 snapshot.
- `validate_ledger.py`: 122 errors, the same as origin/main.

## 2. What closed since the last selection point

- **BATCH-2d2fa1 (slot 1, EXP-QSP-70b731 custody) is CLOSED.**
  - It was archived by TASK-20261002-9a734c at d9b76c0d4e.
  - DEC-20261002-e0aa2b classifies the bound run set K-INVALID: 0 valid,
    1 infrastructure_failure, 1 incomplete_attempt, 14 invalid. The causes are
    record, certificate-accounting and control defects F-01 to F-06. They are
    NOT negative evidence.
  - Its first next action is NA-1, quoted in full in its decision. That
    decision must:
    - (a) rule on R-CONTINUATION: whether DEC-20260921-f0e100's execution
      approval of TASK-20260921-9f84a3 (trial-plan-cont.json) is superseded
      for execution;
    - (b) fix QSP-SUCC as ranked work at W-SLOT-1's position, with defect_return
      D-1 to D-8;
    - (c) record additively on the goal head that lane BATCH-2d2fa1 closed.
      TASK-20261002-9a734c did NOT write the goal head.
  - NA-1 approves nothing, and opens no batch unless it is written as an
    opening decision.
  - NA-2 is done: the bus pointers are MSG-20261002-172d36 and
    MSG-20261002-b9ae4a. OBS-1 is resolved by correction CX-345dbd-1 in the
    9a734c receipt: the QSP branch head is 8164cc5b96, and its runs/ names
    equal main's.
- Still no reply from coordinator-qsp-run-20260921 on the bus. No QSP claim is
  live.

## 3. Slots (goal-wide max_concurrent 3, counted in live claims)

| Slot | Holder | Live claim |
|---|---|---|
| 1 | FREE (BATCH-2d2fa1 closed) | none |
| 2 | BATCH-f435ab (NISTBIN v3 review round) | TASK-20261002-3cd1f8 (validator) |
| 3 | BATCH-35bdda lane B (v3 review round) | TASK-20260929-8f2efa (red team) |

- Lane B and the NISTBIN round still have reviewers queued: lane B has 9030f8
  blind; NISTBIN has 3de9d2, 496923, 4cb903 and 84c5d6 blind.
- Those reviewers take claims within their own slots as claims free.

**Slot-1 claimant under the standing rulings:**
- DEC-20261002-86a7e0 R-SLOT: the S1 version-4 revision (DEC-20260929-54dcd8
  CH-B) "if no earlier freed slot has taken it, otherwise U-HOLDH
  (DEC-20260929-7257b2 rank 3), reconciled at that selection point on its
  facts."
- No earlier freed slot has taken the S1 version-4 revision.
- DEC-20261002-e0aa2b W-SLOT-1 puts QSP-SUCC on the next freed slot after the
  R-SLOT claimants.

## 4. What this pass must rule

1. **DEC-20261002-e0aa2b NA-1 (a) to (c)**, in one zero-run decision. This may
   be the same act as item 2's opening decision; NA-1 says it then rides with
   the next batch opened on this goal.
2. **Slot 1.**
   - If the S1 version-4 revision takes it: open its zero-run revision design
     batch. The requirements are in DEC-20260929-54dcd8 NA-1 and its R-*
     items, against lane A v3 (H-BINSTD-099d93 and EXP-BINSTD-8cb697) and the
     BATCH-35bdda lane-A reports.
   - Use the BATCH-35bdda lane-A package as the exemplar:
     - queue entries;
     - review plan coordination/review/binstd-a-20261001-35bdda/review-plan.yaml;
     - producer card TASK-20260929-6f5e6d;
     - snapshot TASK-20260929-76139a.
   - Include allowed_session_computations if the producer needs code digests or
     dry runs; the producer has no shell.
3. **R-SLOT reconciliation** of S1 v4 against U-HOLDH, with reasons. Apply
   rule 9 to anything deprioritized.

## 5. Pre-minted ids (`allocate_id.py --next`, all 33 `--check` OK on 2026-10-02)

- Batches: BATCH-f6b7c5, BATCH-2e63c3
- Decisions: DEC-20261002-5e691c, -f61a75, -a75609, -21a63d, -c9ec6b
- Hypothesis: H-BINSTD-14f77e
- Experiment: EXP-BINSTD-a222b4
- Handoffs (24), all TASK-20261002-:

  | | | | | | |
  |---|---|---|---|---|---|
  | b903e7 | 80ee44 | b75ae9 | c21ce2 | ab21d1 | aba8f9 |
  | 6084fa | b61002 | d98069 | 5e1ef2 | cee59d | 9f9ce5 |
  | ffb7bb | b8360c | 2214e9 | 17bf2f | 8d288b | 97a1ea |
  | 49bbba | 66334f | bbb1a1 | c5d9e7 | f0f7e0 | 3b6a02 |

Name any you leave unused. This brief sits in the BATCH-f6b7c5 directory as the
session's working choice.

## 6. Lessons the session carries from this round (procedure, for the plan)

- **Concurrent reviewers.** Do not let a sibling's finding leak into a later
  reviewer's launch prompt. The session disclosed one such risk on lane B
  (8f2efa's J3 line paraphrased plan J3 after 8218e0 returned). Plan text that
  names the attack is the safe form.
- **Pre-gate digests.** Record the producer files' whole-file sha256 before
  any gate step (PD-SNAP-1 on 2a3049).
- **Git refs.** Read a branch head from `origin/<branch>`, never FETCH_HEAD
  (CX-345dbd-1).
- **Arms coded by name.** The lane-B validator found arms coded by a numeric
  offset that varies with n (D-J2-1). A J3/J2 check that every declared arm
  reaches its outcome as coded is worth stating in any plan with per-arm
  outcomes.

## 7. Excluded reads still binding on every card

- experiments/EXP-QSP-70b731/runs/ (the BATCH-2d2fa1 lift ended with that lane)
- experiments/EXP-FROB-30006a/
- ref origin/cursor/semaev-2015-audit-program-5b8b
- PR #1377
- branch cursor/ecdlp2m-revision-design-3d1a
- the untracked review reports under BATCH-35bdda/reviews/ and
  BATCH-f435ab/reviews/ (in-flight review rounds; blind to you too)

## 8. After you return

The session has a shell. It will, in order:

1. Parse and validate every file.
2. Run `research_dispatch.py`.
3. Make the isolated opening archive.
4. Send the bus pointers you name.
5. Open the lane.
6. Push and refresh the PR.
7. Dispatch the producer after a claim.

It never launches scientific runs.
