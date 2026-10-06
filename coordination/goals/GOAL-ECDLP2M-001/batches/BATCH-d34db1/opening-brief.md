# Opening brief for the Coordinator: /coordinate portfolio pass, 2026-09-28 (second pass, session rm3mrv)

Written by the top-level session before dispatching the Coordinator subagent.
It carries state the subagent cannot fetch (it holds no shell) and the ids the
session pre-minted. It is not a record; the Coordinator's decision is.

## 1. Checkout and portfolio state (session-verified, 2026-09-28T22:32Z)

- Branch `claude/index-calculus-ecdlp-ecc2k-rm3mrv` == origin/main == fdb4f245fa
  (PR #1478 and PR #1479 merged; merge digest since then: one events file only).
  Working tree clean.
- `tools/goal_portfolio_health.py`: 63 active goals, 46 ECC. Ready elsewhere:
  GOAL-AUXIN-a93442 TASK-20260926-b2d068 (held by lane BATCH-2fc87b of another
  session), GOAL-GFPN-380702 TASK-20260925-0ed1be, GOAL-SEMBIN-fcb7a2
  TASK-20260916-0c2802 (dispatch paused by DEC-20260928-3f71c4 R-2). 32
  batch-complete goals need checkpoints. Needs-repair: GOAL-ECDLP2M-001 (the
  BATCH-b67954 archive on its unmerged branch; not a defect for this session),
  GOAL-ICEX-001, GOAL-SIG-001, four non-ECC.
- Bus (`inbox --as coordinator`): no message newer than MSG-20260928-792a99
  (EXP-CRYPTO-9225d2, non-ECC); nothing bears on this act. No message from
  coordinator-qsp-run-20260921 exists on the bus at all; the last pointer TO it
  is MSG-20260924-c55a2a.

## 2. GOAL-ECDLP2M-001 now

- `status: active`, `campaign_budget.max_concurrent: 3`, `current_batch_id:
  BATCH-b67954` (pointer, not a lock). Goal head next_action prefix (lane
  BATCH-67c132, under DEC-20260928-157d40): "AFTER TASK-20260928-deb56a
  VERIFIES, this lane's next action is DEC-20260928-63addc next_actions item 1
  (the design batch for the selected proposals, opened only when a slot of
  max_concurrent 3 is free)". TASK-20260928-deb56a verified (ledger commit
  9fcc1e3262, content_first, dispatcher gate passed) and is on main; lane
  BATCH-67c132 is CLOSED (outcome archived). DEC-20260928-63addc is official.
- Open lanes (`goal_lanes.py lanes`): BATCH-1faf6f (both cards completed; lane
  record still open), BATCH-2c4a9c, -9dbda3, -ed05f2, -ee209c (QSP run lanes,
  branch exec/qsp-70b731-run-20260921, each 4 queued cards, no live claim),
  BATCH-b67954 (branch cursor/ecdlp2m-revision-design-3d1a, last commit
  a03275d369 "Merge origin/main", preceded by "lane-A composer and lane-B
  red-team continuation dispatched"; 45 commits ahead of main; its two
  unreleased claims TASK-20260925-2333ea and -6e7e13 expired 2026-09-26; its
  composing decisions DEC-20260925-41f6dc and DEC-20260925-a84b16 are NOT on
  main; its lane archives TASK-20260925-a9c531 and -b25565 are NOT on main).
- Live claims after `git fetch` and `research_dispatch.py --claims refs` on
  every GOAL-ECDLP2M-001 queue this checkout renders: 0. The BATCH-b67954
  queue does not render on main (its archive commits live on its branch);
  its claim files were inspected on that branch: none live.
- QSP custody successor (DEC-20260928-157d40 rank 4; DEC-20260925-89573b
  rank 2; DEC-20260924-f0a9c7 rank 2) preconditions at this fetch: git fetch
  done immediately before this brief; no live claim on any QSP card; head of
  exec/qsp-70b731-run-20260921 inspected = 8164cc5b96 (6 commits ahead of
  main, all "bus: publish records"; 1318 behind); a bus pointer to
  coordinator-qsp-run-20260921 has NOT yet been sent for this opening (the
  session sends it on the Coordinator's instruction, before the batch opens).
  Nothing under experiments/EXP-QSP-70b731/runs/ was read.

## 3. The operative next action and its slot rule (DEC-20260928-63addc NA-1)

Quoted in the decision: open one zero-run design batch, two disjoint lanes
(lane A IDEA-20260926-20ba8f per S1 C1-C8 carrying IDEA-20260926-4b65e3 Stage 0;
lane B IDEA-20260926-136bd3 per S2 C1-C8 absorbing IDEA-20260926-d06324's two
calibration rows), sixteen cards in the stated order, both review rounds at
review-breakthrough at max (TW-01, TW-02), composers re-rank HOLD-X1..X13 and
HOLD-A..G. Slot rule: the custody successor keeps its claim on the first free
slot if its 89573b rank-2 preconditions hold at the fetch; then this batch
takes the next slot(s): one free slot -> max_concurrent 1 (lane A then B); two
-> max_concurrent 2. Every card: maximum_runs 0 and the excluded reads of
TASK-20260928-cdf0a4 (every BATCH-b67954 path beyond its lane record's
existence, both b67954 review directories, branch
cursor/ecdlp2m-revision-design-3d1a, experiments/EXP-QSP-70b731/runs/,
experiments/EXP-FROB-30006a/, ref origin/cursor/semaev-2015-audit-program-5b8b,
PR #1377).

Session reading of the slot arithmetic, for the Coordinator to rule on (R-SLOT
of DEC-20260928-157d40 counts LIVE CLAIMS, not open lane records): live = 0 of
3; the custody successor's preconditions hold, so it holds slot 1 once its
pointer is sent; slots 2 and 3 are free for the design batch (max_concurrent
2), subject to the standing rule that the session re-fetches and re-counts
before every claim and waits at 3.

## 4. Pre-minted ids (tools/allocate_id.py --next, all --check OK)

- Batches: BATCH-d34db1, BATCH-ebecc4
- Handoffs (20): TASK-20260928-cd226a, -aa366d, -58d044, -6880fc, -7a6424,
  -b933db, -d5024b, -a75ba7, -95abde, -91b346, -062eb8, -d1ad97, -ae6f2a,
  -606978, -649630, -4b00da, -f21ffe, -d23d39, -062824, -7a6a8b
- Decisions (5): DEC-20260928-65c6d7, -cec92e, -9d9c47, -d1070b, -34a235
- Hypotheses: H-BINSTD-6e4713, H-BINSTD-0126fe
- Experiments: EXP-BINSTD-532d7f, EXP-BINSTD-de9678
Unused ids are returned by name in the decision.

## 5. Pinned facts to apply

- CORR-20260928-4cb669: D1 gap 2^-4.41, D2 per-target 2^+5.71, D3 per-attempt
  2^+11.01 at m = 4; D3 column 11.01/33.08/37.39/42.52 bits at m = 4/5/6/8;
  N = 4r ambient, subgroup-restricted floors 4/(m+1) bits lower.
- Matched rho on ECC2K-130: sqrt(pi r/(4*131)) = 2^60.8090 (CORR-20260922-81aeab).
- CORR-20260925-649e25 governs per-orbit relation-yield framing.
- Exemplar review plan with prior, joints, blindness, proves-too-much control
  and blind re-derivation: coordination/review/icperf-aa2efc-20260926/review-plan.yaml.
- Exemplar opening package of the same shape (queue, cards, receipts):
  coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-67c132/ and the
  BATCH-7d29e8 two-lane design batch (DEC-20260924-f0a9c7).

## 6. What the session will do after the Coordinator returns (its shell)

Parse every file; validate the queue with research_dispatch.py --claims refs;
run validate_ledger.py and check_merge_hygiene.py; send the bus pointer(s) the
decision names; open the lane(s) with goal_lanes.py open-lane --publish; make
the isolated opening ledger archive commit (staging exactly the declared paths,
record ids in the message); push; open the PR; then dispatch the producer
cards in fresh /design-experiment sessions after lane claims. Scientific runs
are never launched by this skill.
