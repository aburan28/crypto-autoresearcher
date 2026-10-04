# Coordinator handback: BATCH-d34db1 opening (2026-09-28, session rm3mrv, second pass)

Not a record and not a declared artifact of any card. TASK-20260928-aa366d does
not stage it; the session may commit it in a control-plane commit of its own.

## 1. Ranked act and rulings

- Rank 1, performed: open BATCH-d34db1, the DEC-20260928-63addc NA-1 two-lane
  design batch, sixteen cards, zero runs, both review plans frozen before any
  producer runs at review-breakthrough max non-degradable (TW-01, TW-02).
- Slot ruling (DEC-20260928-65c6d7 R-SLOT): live claims 0 of 3 (session
  count). The EXP-QSP-70b731 custody successor keeps slot 1 (its
  DEC-20260925-89573b rank-2 preconditions hold at this fetch once the bus
  pointer below is posted, which the session does before the lane opens).
  This batch opens with max_concurrent 2 on slots 2 and 3; lane A and lane B
  in parallel. Re-fetch and re-count before every claim; wait at 3.
- Custody ruling (R-CUSTODY): not opened in this pass. The pre-minted pool
  leaves 4 TASK, 2 DEC, 1 BATCH after this batch; the successor needs 6 TASK,
  2 DEC, 1 BATCH (opening card, opening ledger archive, snapshot of the run
  entries, validator, composer, ledger archive). It stays rank 2, holds slot
  1, and opens at the next pass with a shell after TASK-20260928-aa366d
  verifies, with its ids minted then. Six preconditions listed in R-CUSTODY.

## 2. Files written (all new unless stated)

- ledger/decisions/DEC-20260928-65c6d7.yaml
- coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-d34db1/dispatch_queue.json
  (written whole: one Write for the header and cards 1-8, one Edit appending
  cards 9-16 and rerank_triggers; parse it first)
- coordination/review/binstd-a-20260928-d34db1/review-plan.yaml (REVIEW-BINSTD-A-20260928-d34db1)
- coordination/review/binstd-b-20260928-d34db1/review-plan.yaml (REVIEW-BINSTD-B-20260928-d34db1)
- ledger/goals/GOAL-ECDLP2M-001.yaml (additive only: next_action block
  prepended; open_batches entry appended; amendment_history entry appended at
  the end; nothing else changed; diff for zero deletions)
- ledger/handoffs/, sixteen cards, in NA-1 order:
  1. TASK-20260928-cd226a  opening card (completed at writing)
  2. TASK-20260928-aa366d  opening ledger archive (content_at_commit)
  3. TASK-20260928-58d044  lane-A producer (H-BINSTD-6e4713, EXP-BINSTD-532d7f, audit sheet with fixture code)
  4. TASK-20260928-6880fc  lane-B producer (H-BINSTD-0126fe, EXP-BINSTD-de9678, audit sheet with fixture and calibration code)
  5. TASK-20260928-7a6424  lane-A snapshot (content_at_commit)
  6. TASK-20260928-b933db  lane-B snapshot (content_at_commit)
  7. TASK-20260928-d5024b  lane-A validator-breakthrough, J1 J2
  8. TASK-20260928-a75ba7  lane-A red-team-breakthrough, J3 J4, PTM-A to PTM-C
  9. TASK-20260928-95abde  lane-A blind validator-breakthrough, J5 (four-file whitelist; quantities on the card)
  10. TASK-20260928-91b346 lane-B validator-breakthrough, J1 J2
  11. TASK-20260928-062eb8 lane-B red-team-breakthrough, J3 J4, PTM-A to PTM-C
  12. TASK-20260928-d1ad97 lane-B blind validator-breakthrough, J5 (four-file whitelist; quantities on the card)
  13. TASK-20260928-ae6f2a lane-A composer, writes DEC-20260928-cec92e
  14. TASK-20260928-606978 lane-B composer, writes DEC-20260928-9d9c47
  15. TASK-20260928-649630 lane-A ledger archive (content_at_commit)
  16. TASK-20260928-4b00da lane-B ledger archive (content_at_commit)
- this file

## 3. Record ids used and returned

- Used: BATCH-d34db1; DEC-20260928-65c6d7 (opening), DEC-20260928-cec92e
  (lane-A composing), DEC-20260928-9d9c47 (lane-B composing); the sixteen
  TASK ids above; H-BINSTD-6e4713, EXP-BINSTD-532d7f (lane A); H-BINSTD-0126fe,
  EXP-BINSTD-de9678 (lane B). Review-plan ids derived from the batch token.
- Returned unused (free again; none reserved): BATCH-ebecc4,
  DEC-20260928-d1070b, DEC-20260928-34a235, TASK-20260928-f21ffe,
  TASK-20260928-d23d39, TASK-20260928-062824, TASK-20260928-7a6a8b.

## 4. Bus pointers the session must send (check the outbox first; never duplicate)

### 4a. To coordinator-qsp-run-20260921 (DEC-20260928-65c6d7 NA-2), before the lane opens

refs: DEC-20260928-65c6d7, DEC-20260928-157d40, DEC-20260925-89573b,
DEC-20260924-f0a9c7, DEC-20260924-4f8a03, EXP-QSP-70b731, BATCH-d34db1

text:

    Pointer, no task, no permission. DEC-20260928-65c6d7 (GOAL-ECDLP2M-001,
    session coordinator-portfolio-rm3mrv) records that the scoped custody
    successor for the existing EXP-QSP-70b731 run entries (DEC-20260924-4f8a03
    NA-6; DEC-20260924-f0a9c7 rank 2; DEC-20260925-89573b rank 2;
    DEC-20260928-157d40 rank 4) is the next act on this goal and holds slot 1
    of campaign_budget.max_concurrent 3. It is not opened in this pass (ids
    not in the pre-minted pool; see R-CUSTODY) and will be opened as its own
    act at the next pass: a snapshot of the run entries as they sit on main,
    one independent validator on run count, manifest completeness, seed
    integrity, raw/summary agreement and control comparability, then a
    ledger archive; zero new runs; nothing under experiments/EXP-QSP-70b731/runs/
    read by the Coordinator. A two-lane design batch BATCH-d34db1 is open on
    slots 2 and 3 beside BATCH-b67954. No QSP lane record (BATCH-1faf6f,
    -2c4a9c, -9dbda3, -ed05f2, -ee209c) is touched, claimed or closed. The
    last pointer to you was MSG-20260924-c55a2a; no message from you is on
    the bus. If your lane is live or has unmerged run entries on
    exec/qsp-70b731-run-20260921 beyond the bus-publish commits, please
    answer with its status before the successor opens; a live QSP claim is
    honoured and re-ranked, never displaced. Nothing here asserts anything
    about any EXP-QSP-70b731 run.

### 4b. Route-to-owner pointers of DEC-20260928-63addc NA-4, due now (deb56a verified)

If not already in the outbox, post PTR-ICPERF (to the coordinator role for
GOAL-ICPERF-e6b6a4), PTR-FROB (for GOAL-FROB-6333a9) and PTR-SATIC (for
GOAL-SATIC-c49b77) with exactly the refs and content recorded under
DEC-20260928-63addc route_to_owner. Also check that DEC-20260928-157d40 NA-6's
pointer was posted. The PTR-ICPERF pointer is what makes the lane-A composer's
objection check (plan icperf_objection_check) meaningful; record MSG ids.

## 5. Exact commands (in order)

1. Parse every file above (YAML and JSON); `git diff -- ledger/goals/GOAL-ECDLP2M-001.yaml` must show zero deletions.
2. `python3 tools/validate_ledger.py` (at or below baseline) and `python3 tools/check_merge_hygiene.py`.
3. `python3 tools/research_dispatch.py coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-d34db1/dispatch_queue.json --claims refs` (card 1 completed, card 2 ready, rest blocked).
4. Post the bus pointer(s) of section 4 with `python3 tools/agent_bus.py` (outbox check first).
5. `git fetch origin && git merge origin/main` (merge, never rebase; a goal-head conflict is a stop), then re-count live claims across every GOAL-ECDLP2M-001 queue including the BATCH-b67954 queue on its branch.
6. Commit TASK-20260928-aa366d alone: stage exactly the twenty source artifacts of TASK-20260928-cd226a, ledger/decisions/DEC-20260928-65c6d7.yaml and the receipt; message names TASK-20260928-aa366d and every archive record_id literally. Verify with research_dispatch.py (content_at_commit). Push. Open the PR against main naming every record id.
7. `python3 tools/goal_lanes.py open-lane GOAL-ECDLP2M-001 BATCH-d34db1 --queue coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-d34db1/dispatch_queue.json --decision DEC-20260928-65c6d7 --as coordinator-portfolio-rm3mrv --publish`
8. Record the completion (commit_sha, parent_sha, path_sha256 over 22 paths) in the queue's archive block for TASK-20260928-aa366d in a later commit.
9. Dispatch the producers in fresh /design-experiment Coordinator sessions, each after `git fetch`, a re-count, and
   `python3 tools/goal_lanes.py claim coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-d34db1/dispatch_queue.json TASK-20260928-58d044 --as coordinator-portfolio-rm3mrv --ttl-minutes 240 --publish`
   `python3 tools/goal_lanes.py claim coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-d34db1/dispatch_queue.json TASK-20260928-6880fc --as coordinator-portfolio-rm3mrv --ttl-minutes 240 --publish`
   and on return `python3 tools/goal_lanes.py release <queue> <TASK> --as coordinator-portfolio-rm3mrv --outcome completed --publish`.
10. Then per lane, in the cards' order: snapshot alone (7a6424 / b933db); the three reviews (claims with TTL 300, 300, 180 minutes; review-breakthrough servable at max or do not dispatch; blind launch prompts name only the card); composer (TTL 150; paste the six report digests, the check_review_independence output, the inbox state for ICPERF (lane A), and whether DEC-20260925-41f6dc, DEC-20260925-a84b16 and the sibling composing decision are on origin/main); lane ledger archive alone. Close the lane with close-lane only after both lane archives verify.
11. Scientific runs are never launched by this skill.
