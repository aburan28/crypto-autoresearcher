# Opening brief for the Coordinator: /coordinate portfolio pass, 2026-09-28 (session rm3mrv)

Written by the top-level session before dispatching the Coordinator subagent.
It carries state the subagent cannot fetch (it holds no shell) and the ids the
session pre-minted. It is not a record; the Coordinator's decision is.

## 1. Checkout and portfolio state (session-verified)

- Branch `claude/index-calculus-ecdlp-ecc2k-rm3mrv` restarted from `origin/main`
  at `0e8e8c5eb` (main includes PR #1455 and PR #1473 from this session; the
  merge digest since 09-26 lists 12 decisions, 7 experiments, 2 goals added,
  GOAL-SEMBIN-fcb7a2 modified, 100+ KN-LIT entries, the known-results map,
  the prior_art gate, and the prime-field MITM engine).
- `tools/goal_portfolio_health.py`: 63 active goals, 46 ECC. Ready cards
  elsewhere: GOAL-AUXIN-a93442 TASK-20260926-b2d068 (snapshot archive, ranked
  1 by DEC-20260928-3f71c4, held by lane BATCH-2fc87b of another session),
  GOAL-GFPN-380702 TASK-20260925-480d02 (a /run), GOAL-SEMBIN-fcb7a2
  TASK-20260916-0c2802 (paused by DEC-20260928-3f71c4 until its card carries
  an amendment). 32 batch-complete goals need checkpoints; needs-repair:
  GOAL-ECDLP2M-001 (see below), GOAL-ICEX-001, GOAL-SIG-001, four non-ECC.
- Bus (`inbox --as coordinator`): no message since MSG-20260928-792a99
  (EXP-CRYPTO-9225d2 X-C8) bears on this act; MSG-20260926-57446c is this
  session's own pointer.

## 2. GOAL-ECDLP2M-001, the goal this session has been working

- `status: active`, `max_concurrent: 3`, `current_batch_id: BATCH-b67954`.
- **BATCH-b67954 is in flight on another session's branch**
  `cursor/ecdlp2m-revision-design-3d1a` (45 commits ahead of main, 137
  behind; producers, snapshots and several reviews completed; composers and
  lane archives queued). The health report's "archive TASK-20260925-d2efb5
  commit not an ancestor of HEAD" is that lane's unmerged branch, not a
  defect for this session to repair. **Do not touch any BATCH-b67954 record,
  card, review plan or claim.**
- Open lanes on the goal: BATCH-1faf6f, BATCH-2c4a9c, BATCH-9dbda3,
  BATCH-ed05f2, BATCH-ee209c (QSP custody/run lanes, other sessions),
  BATCH-b67954. A new lane is opened with `tools/goal_lanes.py open-lane`
  (the session runs it), editing `goal.yaml` only additively (open_batches
  gains one entry; next_action is prepended in the standing "AMENDED
  ADDITIVELY ... prior text retained" form of DEC-20260925-89573b; the goal is
  not sharded and must not be sharded while another lane edits it).
- Open ECC ideas (`ecc_priority.py --open-ideas`, 111 total): BINSTD 38,
  CERTBIN 13, ICPERF 9, SEMBIN 5, SATIC 2, QSP 1, FROB 1 (plus DREG 12, ECDLP
  15, GFPN 6, OAKLEY 2, NISTBIN 2, CRYPTO 3, SSI/CSIDH 2). Of these, 35 were
  filed by this session on 2026-09-26/28 (13 in PR #1455, 22 in PR #1473),
  each with a concrete experiment cell; the 22 round-2 records carry a
  `prior_art` block; the 26 non-selected 2026-09-22 BINSTD proposals carry a
  full review each under `analysis/binstd-idea-review-20260926/reviews/`
  (verdicts in that directory's README section 3; one disagreement with a
  DEC-20260924-99ce20 hold: IDEA-20260922-29b1c5's lemma is false as
  stated).
- The last selection on this cluster, DEC-20260924-99ce20, ranked 36
  proposals and said "Proposals filed later are not ranked here"; its NA-3
  (revision batch for six return_for_revision items), NA-4 (reading tasks
  for HOLD-H/L) and NA-7 (re-rank HOLD-A..G at the next selection point)
  remain open. The composing decisions DEC-20260924-124667 / -286589 and
  DEC-20260925-89573b were selection points for their own lanes only.

## 3. The validator pass on the product-law finding (merged in PR #1473)

`coordination/review/icperf-aa2efc-20260926/composition.md`
(REVIEW-ICPERF-20260926-bcf1b2; independence checker PASS). Section 4 names
what a Coordinator act would write, none of it written yet:
1. An additive scoping correction on KN-FIND-aa2efc / EV-ICPERF-10c5fc: the
   product law's ambient is the full curve group (N = 4r); a
   subgroup-restricted base lowers every free-oracle floor by exactly 4/(m+1)
   bits; verdicts unchanged.
2. A definition pin separating the floor-to-rho gap (2^-4.41 at m = 4), the
   producer's per-target budget (2^+5.71) and the re-optimised per-attempt
   budget (2^+11.01), with the list of program records that quote the gap as
   a budget (composition section 3).
3. A strength relabel of EV-ICPERF-10c5fc from `replicated` toward
   `preliminary` for its cost claims (the derivation tier is unaffected);
   two quoted numbers are unbound (solver_11 amortisation shares; the
   vanishing-ideal base case).
Evidence records are immutable: each of these is an additive `correction`
record (templates/research-records.md "Correction"; exemplar
ledger/corrections/CORR-20260922-81aeab.yaml) citing the review's reports,
never an edit.

## 4. Pre-minted ids (tools/allocate_id.py --next, all --check OK)

- Batch: BATCH-67c132
- Decisions: DEC-20260928-157d40 (opening), DEC-20260928-63addc (reserved for
  the selection composed later in the batch)
- Corrections: CORR-20260928-4cb669, CORR-20260928-5d81df, CORR-20260928-ab20cd
- Handoffs: TASK-20260928-6e3277, -800661, -b7dae4, -b87f27, -cdf0a4, -deb56a,
  -dffbcf, -fd6f99
Unused ids are returned by name in the decision.

## 5. What the session will do after the Coordinator returns (its shell)

Validate the queue with `tools/research_dispatch.py --claims refs`, run
`tools/validate_ledger.py` and `check_merge_hygiene.py`, open the lane with
`goal_lanes.py open-lane ... --publish`, make the isolated opening ledger
archive commit (staging exactly the declared paths, record ids in the
message), push, open the PR, then dispatch the ranking card in a fresh
research-deep session and continue the chain. Scientific runs are never
launched by this skill.
