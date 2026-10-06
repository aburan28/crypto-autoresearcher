# Opening brief for the Coordinator: /coordinate portfolio pass, 2026-10-01 (session rm3mrv, fourth pass)

Written by the top-level session before it dispatched the Coordinator
subagent. It records the state of the checkout and the ids the session
pre-minted. It is not a record; the Coordinator's decision is.

## 1. Checkout and merges

- The branch `claude/index-calculus-ecdlp-ecc2k-rm3mrv` matches origin/main at
  286515b8fb (fast-forward, no conflict).
- PR #1489 merged on 2026-09-29 at 20:11Z. That makes both BATCH-361e02
  composing decisions official on main:
  - DEC-20260929-1f5fcb (lane A, S1): revise.
  - DEC-20260929-8c3cb2 (lane B, S2): revise.
  - Lane BATCH-361e02 is closed with outcome archived.
- `validate_ledger.py` baseline: 94 errors.
- `check_merge_hygiene.py`: PASS.
- `goal_portfolio_health.py --no-deepen` lists GOAL-ECDLP2M-001 under
  needs-repair: "artifact path ledger/decisions/DEC-20260930-8de5ba.yaml is
  owned by both TASK-20260930-54b557 and TASK-20260930-57951a". That is
  BATCH-ccfdc6, another session's queue. This session did not cause it and
  does not edit it.

## 2. What other sessions did on GOAL-ECDLP2M-001 between 09-29 and 09-30 (now on main)

- **BATCH-b67954's composing decisions are on main.** These are the ones
  1f5fcb NA-4 and 8c3cb2 SP-2 said to read once they land:
  - DEC-20260925-41f6dc: revise of EXP-NISTBIN-451dfa v2.
  - DEC-20260925-a84b16: revise of EXP-BINSTD-178742 v2.
- **The b67954 lane-B lineage moved on**
  (EXP-BINSTD-178742 / H-BINSTD-ce4f38, a different lineage from ours):
  - DEC-20260930-15ad99 opened BATCH-2ee1e1 (v3 revision design). The lane is
    closed.
  - DEC-20260930-a729dd: do_not_approve.
  - DEC-20260930-93408f: attestation-schema repair.
  - DEC-20260930-735b4d: APPROVE EXP-BINSTD-178742 v3 under K-approve.
  - DEC-20260930-70bff3 opened BATCH-8c7af6 (implementation and trial plan).
    The lane is closed.
  - DEC-20260930-8de5ba opened **BATCH-ccfdc6**, which authorises scientific
    execution of EXP-BINSTD-178742. The lane is OPEN. It has one Ready card
    (a `/run` card) and no live claim.
- **Two new direct designs and approvals:**
  - DEC-20260930-492bf6: H-BINSTD-dba2ab and EXP-BINSTD-38f216, from
    IDEA-20260922-29b1c5. Approved, with no review round.
  - DEC-20260930-982e92: H-BINSTD-9bde6e and EXP-BINSTD-a3fa22, from
    IDEA-20260922-2e2a58. Approved, with no review round.
  - Neither experiment supersedes ours, and neither touches the S1 or S2
    lineage.
- **Neither of our version-3 next actions has been taken by anyone:**
  - DEC-20260929-1f5fcb NA-1 (lane A, S1, R2-*).
  - DEC-20260929-8c3cb2 NA-1 (lane B, S2, RR-1..RR-12).

## 3. Slots (R-SLOT counts live claims)

- `research_dispatch.py --claims refs` on every GOAL-ECDLP2M-001 queue gives
  **live claims 0 of 3**.
- Open lane records:
  - BATCH-1faf6f: stale; both cards completed.
  - The four QSP run lanes 2c4a9c, 9dbda3, ed05f2, ee209c. Each has 1 Ready
    card and no claim. Branch heads are unchanged.
  - BATCH-ccfdc6, from another session: 1 Ready `/run` card, unclaimed.
- The EXP-QSP-70b731 custody successor still holds slot 1, unopened
  (FINDING-QSP-DOUBLE-DECLARATION). The session found no reply from
  coordinator-qsp-run-20260921 to MSG-20260929-fb57f1 on the bus.
- Ruling needed: does the open BATCH-ccfdc6 execution lane occupy a slot? It
  has no live claim. Its `/run` is that session's or `/run`'s to take, never
  this skill's.

## 4. The competing next actions for the free slots

- **DEC-20260929-1f5fcb.** NA-1: lane-A v3 revision design discharging R2-*.
  CH-A: the lane-A revision takes the first freed slot ahead of the
  DEC-20260928-63addc NA-3 research batch. CH-B: NA-3 moves to the next free
  slot.
- **DEC-20260929-8c3cb2.** NA-1: lane-B v3 revision design discharging
  RR-1..RR-12 with C1..C8 kept. SP-1: the 63addc NA-3 research batch keeps
  the first freed slot and is not deferred a third time; the v3 revision
  ranks right behind it. SP-2: the HOLD-X2 revisit is deferred until 1f5fcb
  is on main. It is on main now.
- **DEC-20260928-63addc NA-3:** read it.
- These rulings conflict and must be reconciled at this selection point,
  with reasons.
- Also apply what DEC-20260925-41f6dc and DEC-20260925-a84b16 rule on any
  hold that bears on the BINSTD selection (1f5fcb NA-4; 8c3cb2 SP-2).

## 5. Pre-minted ids (`allocate_id.py --next`, all `--check` OK on 2026-10-01)

- Batches: BATCH-04a6be, BATCH-35bdda, BATCH-630fd1
- Decisions:
  - DEC-20260929-1eded2
  - DEC-20260929-4c7ffc
  - DEC-20260929-54dcd8
  - DEC-20260929-585602
  - DEC-20260929-7257b2
  - DEC-20260929-a7f28b
  - DEC-20260929-d5b8f2
- Hypotheses: H-BINSTD-099d93, H-BINSTD-17cf9d
- Experiments: EXP-BINSTD-8cb697, EXP-BINSTD-c9c8a2
- Handoffs (40), all prefixed TASK-20260929-:

  | | | | | | | | |
  |---|---|---|---|---|---|---|---|
  | 00a9ff | 07e772 | 0be49c | 0e2d93 | 26849f | 2a3a31 | 322a64 | 3308db |
  | 34d429 | 3907b4 | 56d600 | 5e14da | 5f1c3d | 5f884a | 66826b | 6f5e6d |
  | 749b50 | 76139a | 78e02e | 7fb81e | 810095 | 8218e0 | 8f2efa | 9030f8 |
  | 99f171 | a1413f | a80339 | afdc95 | b85e1f | b8c259 | bdb8c0 | c09da8 |
  | c0fc83 | c98bc5 | d767eb | e68cf3 | ecac2e | ed75ea | fe747f | ff9ca2 |

- A research batch for 63addc NA-3 may need other areas' ids. Name them and
  the session mints them.
- This brief sits in the BATCH-04a6be directory as a working choice; the
  session moves it if you rule otherwise.

## 6. Pinned facts and exemplars

- **CORR-20260928-4cb669:**
  - D1 is never a budget.
  - D3 = 11.010251, 33.08, 37.39 and 42.52 bits at m = 4, 5, 6 and 8.
- **Matched rho:** 2^60.8090 (CORR-20260922-81aeab).
- **Per-orbit framing:** governed by CORR-20260925-649e25.
- **Opening package exemplars:**
  - DEC-20260929-01ea31, BATCH-361e02 queue and cards.
  - coordination/review/binstd-{a,b}-20260929-361e02/review-plan.yaml.
- **Lessons from BATCH-361e02 for the next plans:**
  - Name the S constant on blind cards exactly as the contract states it.
  - Give each reviewer a pre-created scratch path.
  - A code block with module-level execution needs a `__main__` guard
    (R2-PROC-1).
  - Every invalidation rule is checked against the contract's own metrics
    (R2-J3-1).
  - Every arm's null is audited for exact quotient content (RR-1, RR-2).

## 7. Excluded reads still binding on every card

- experiments/EXP-QSP-70b731/runs/
- experiments/EXP-FROB-30006a/
- ref origin/cursor/semaev-2015-audit-program-5b8b
- PR #1377
- branch cursor/ecdlp2m-revision-design-3d1a

The BATCH-b67954 records are now on main and may be read as 1f5fcb NA-4 and
8c3cb2 SP-2 direct.

## 8. After you return

The session has a shell. It will:

1. Parse and validate every file.
2. Run `research_dispatch.py`.
3. Send the bus pointers you name.
4. Open the lane or lanes.
5. Make the isolated opening archive.
6. Open the PR.
7. Dispatch producers.

It never launches scientific runs.
