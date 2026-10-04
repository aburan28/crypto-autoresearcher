# Opening brief for the Coordinator: /coordinate portfolio pass, 2026-09-29 (session rm3mrv, third pass)

Written by the top-level session before it dispatched the Coordinator subagent.
It carries state the subagent cannot fetch, because the subagent has no shell,
and it lists the ids the session pre-minted. It is not a record; the
Coordinator's decision is.

## 1. Checkout and portfolio state (verified by the session on 2026-09-29)

- Branch `claude/index-calculus-ecdlp-ecc2k-rm3mrv` == origin/main == 2fa3e7929c.
  PR #1486 is merged (the BATCH-d34db1 lane archives and close-lane), and the
  working tree is clean.
- Merge digest since fdb4f245fa:
  - DEC-20260929-523aab (PFDR; goal_id null; approves AMD-20260929-1de84f of
    EXP-PFDR-1b78f7). It does not bear on this goal.
  - The only change to GOAL-ECDLP2M-001 is this session's own
    TASK-20260928-aa366d archive (26d8835cb3).
- Bus (`inbox --as coordinator`): the only new message is MSG-20260929-eebd72,
  from coordinator-pfdr-1rfntm (PFDR, unrelated). Nothing answers PTR-ICPERF
  (MSG-20260928-f8bdc9), PTR-FROB (2f10c0) or PTR-SATIC (37e5a0), and no
  objection to the BINSTD proposals has been posted.
- `tools/goal_portfolio_health.py`:
  - GOAL-ECDLP2M-001 is listed under needs-repair only for TASK-20260925-d2efb5
    (content_at_commit ancestry). That is the BATCH-b67954 archive on another
    session's unmerged branch, the same as at the last pass, and it is not a
    defect for this session.
  - Other needs-repair ECC goals: GOAL-ICEX-001 and GOAL-SIG-001. Both are
    pre-existing and unchanged.

## 2. GOAL-ECDLP2M-001 now

- `status: active`, `campaign_budget.max_concurrent: 3`.
- Lane BATCH-d34db1 is CLOSED with outcome archived (PR #1486). Its two
  composing decisions are official on main:
  - DEC-20260928-cec92e: lane A, S1, revise.
  - DEC-20260928-9d9c47: lane B, S2, revise.
  - Nothing is approved. EXP-BINSTD-532d7f and EXP-BINSTD-de9678 keep
    approved_by null, and no run exists.
- Open lane records (`goal_lanes.py lanes`), all stale:
  - BATCH-1faf6f (both cards completed).
  - The QSP run lanes 2c4a9c, 9dbda3, ed05f2 and ee209c. Their branch
    exec/qsp-70b731-run-20260921 has head 8164cc5b96, unchanged since
    2026-09-21.
  - BATCH-b67954. Its branch cursor/ecdlp2m-revision-design-3d1a has head
    a03275d369, unchanged since 2026-09-26. DEC-20260925-41f6dc and
    DEC-20260925-a84b16 are still NOT on main.
- Live claims after `git fetch` and `research_dispatch.py --claims refs` on
  every GOAL-ECDLP2M-001 queue this checkout renders: 0 of 3.
- EXP-QSP-70b731 custody successor (DEC-20260928-65c6d7 R-CUSTODY): it holds
  slot 1 but has NOT been opened. The handback of the last pass said it opens
  "at the next pass with a shell after TASK-20260928-aa366d verifies".
  - aa366d verified and is on main.
  - The QSP branch head is unchanged, and no QSP card has a live claim.
  - No bus message from coordinator-qsp-run-20260921 exists. The last pointer
    to it is MSG-20260928-663de2, from this session.
  - Nothing under experiments/EXP-QSP-70b731/runs/ was read.

## 3. The two operative next actions (read both in full; quoted in part)

- DEC-20260928-cec92e NA-1 (lane A, S1). Open one zero-run revision design
  batch on the lane-A slot (CH-1). It needs:
  - an opening DEC, a composing DEC, and a superseding H-BINSTD and
    EXP-BINSTD pair;
  - a review plan at review-breakthrough, max, non-degradable (TW-01), with a
    recorded prior, a joint owned on the decision table itself, the three
    proves-too-much controls plus the no-reuse null, and a blind card carrying
    the contract's own constants, the unrounded comparator inputs and the
    m = 4 envelope;
  - a private scratch subdirectory for each reviewer;
  - a producer in a fresh session that did not run 58d044 and did not compose
    cec92e or 63addc;
  - discharge of R-J1-1, R-J2-1, R-J2-2, R-J2-3, R-J3-1, R-J4-1 and every item
    from R-J1-2 to R-SRC;
  - pricing against CORR-20260928-4cb669 (D3, never D1) and framing per
    CORR-20260925-649e25.

  NA-2 applies to the composer: repeat the PTR-ICPERF objection check before
  any approval.
- DEC-20260928-9d9c47 NA-1 (lane B, S2). Open one zero-run revision design
  batch on the slot lane B frees. It needs:
  - a producer in a fresh session that did not run 6880fc, did not review
    lane B and did not compose 9d9c47;
  - version 2 as a superseding record set, discharging R-1 to R-12 and 63addc
    S2 C1 to C8;
  - the fixture, the histogram-preserving shuffle, the measured-null
    calibration, the certificate function and the PC-7 and PC-9 code
    committed as code, with pass criteria stated before execution;
  - a review plan at review-breakthrough, max (TW-02), with a prior about the
    estimator's finite-sample behaviour;
  - one proves-too-much control that feeds the repaired shuffle both an exact
    filter and a planted marginal-only filter;
  - a blind re-derivation of the repriced sample sizes per (cell, M) from
    S >= about 100 x M^2;
  - a fresh composer and a ledger archive.
- 9d9c47 NA-3 applies at this selection point: read cec92e and apply its
  hold rulings to the selection point, recording only the changes. The two
  b67954 decisions are not on main and are not read.

Shape question for your ruling: both NA-1 texts can be served either by one
two-lane batch with the same shape as BATCH-d34db1 (1 BATCH, 1 opening DEC,
2 composing DECs, 16 cards, max_concurrent 2) or by two single-lane batches.
The session holds ids for either shape.

Slot arithmetic, as read by the session: live claims are 0 of 3. The custody
successor keeps slot 1, so slots 2 and 3 are free for the two revision lanes.
If you also open the custody successor in this pass, the session sends its
bus pointer and opens its lane before any claim. The session re-fetches and
re-counts before every claim and waits at 3.

## 4. Pre-minted ids (`tools/allocate_id.py --next`, all `--check` OK)

- Batches: BATCH-361e02, BATCH-aa88a8
- Decisions (6): DEC-20260929-01ea31, -1f5fcb, -8c3cb2, -a4d612, -41a102, -ebe31b
- Handoffs (24): TASK-20260929-024913, -1aa52d, -1e739f, -291567, -36a146,
  -36d781, -45204f, -594e8d, -739a0c, -75e9e4, -7d8385, -953377, -b0c8c3,
  -bf8f6c, -e85cfa, -ee38f7, -f032df, -fffa78, -1f841a, -3de4d6, -51fe61,
  -c1eb78, -d9166e, -f08008
- Hypotheses: H-BINSTD-7951d2, H-BINSTD-de2808
- Experiments: EXP-BINSTD-517186, EXP-BINSTD-6f1e66

This brief sits in the BATCH-361e02 directory as the session's working
choice. If you rule on a different shape, say so, and the session moves the
file. Name unused ids in the decision.

## 5. Pinned facts to apply

- CORR-20260928-4cb669:
  - D1 gap 2^-4.41, never a budget.
  - D2 per-target 2^+5.71.
  - D3 column 11.01/33.08/37.39/42.52 bits at m = 4/5/6/8.
  - The attribution of m = 5, 6 and 8 is a provenance item (cec92e NA-3 (e)).
- Matched rho on ECC2K-130 is sqrt(pi r/(4*131)) = 2^60.8090
  (CORR-20260922-81aeab).
- CORR-20260925-649e25 governs per-orbit framing.
- Exemplars of the same shape:
  - the BATCH-d34db1 opening package: queue, cards,
    coordination/review/binstd-{a,b}-20260928-d34db1/review-plan.yaml, and
    DEC-20260928-65c6d7;
  - the composition worksheets under
    BATCH-d34db1/composition/{ae6f2a,606978}/.

## 6. Excluded reads (carry them on every card)

- every BATCH-b67954 path beyond its lane record's existence;
- both b67954 review directories;
- branch cursor/ecdlp2m-revision-design-3d1a;
- experiments/EXP-QSP-70b731/runs/;
- experiments/EXP-FROB-30006a/;
- ref origin/cursor/semaev-2015-audit-program-5b8b;
- PR #1377.

## 7. What the session does after you return

The session has a shell. It will, in order:

1. Parse every file.
2. Validate the queue(s) with `research_dispatch.py --claims refs`.
3. Run `validate_ledger.py` (baseline 94 errors) and `check_merge_hygiene.py`.
4. Send the bus pointer(s) you name.
5. Open the lane(s) with `goal_lanes.py open-lane --publish`.
6. Make the isolated opening ledger archive commit.
7. Push and open the PR.
8. Dispatch producers in fresh sessions after lane claims.

This skill never launches scientific runs.
