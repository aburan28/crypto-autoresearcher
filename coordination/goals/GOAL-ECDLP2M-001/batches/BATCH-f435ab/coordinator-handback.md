# Coordinator handback: BATCH-f435ab opening (DEC-20261002-0983f2)

This handback is not a record and not a declared artifact of any card. No archive stages it.

Act: the /coordinate portfolio pass of 2026-10-02 on GOAL-ECDLP2M-001. It performs DEC-20260929-7257b2 NA-1: it opens the NISTBIN version-3 revision design batch of DEC-20260925-41f6dc NA-1 on slot 2. The batch has eleven cards and zero runs. Nothing is approved, no status moves and nothing is dispatched.

## 1. Rulings (DEC-20261002-0983f2)

- **R-ACT / R-NOT-DUPLICATED.** The batch is opened here because the session's post-fetch report shows that no other session has opened it. If a duplicate surfaces on an unfetched branch, the batch whose opening archive verified first stands, and a superseding decision closes the other.
- **R-SLOT.** This batch holds slot 2 as BATCH-04a6be's successor occupant. BATCH-35bdda keeps slot 3, and its second lane stops borrowing slot 2 once this batch holds a claim or has a Ready card. Slot 1 stays held for the EXP-QSP-70b731 custody successor. The queue declares max_concurrent 2. The second claim may borrow slot 3 only while all three of these hold:
  - the goal-wide live count is at most 1 before the claim;
  - BATCH-35bdda has no live claim and no Ready card;
  - no CH-B-or-later batch has a live claim or a Ready card.
- **Standing claim rule.** Claim only when the goal-wide live count is at most 2 and this session holds at most one other live claim. When only one claim is possible, alternate with BATCH-35bdda, this batch first. Archives run alone.
- **R-NEXT-SLOT** (a recorded reading for the next selection point). The next freed slot goes to the S1 version-4 revision (54dcd8 CH-B, which ranks it "ahead of every hold"); U-HOLDH takes the slot after that. U-HOLDH is not deferred on any new ground, because 7257b2 rank 3 itself concedes to a parallel assignment.
- **R-FORM.** This is DEC-20260925-89573b R-FORM extended to version 3, under the same ids:
  - Version 3 goes at the canonical spec path.
  - Version 2 is frozen mechanically at `experiments/EXP-NISTBIN-451dfa/specification.v2-frozen-1ad01ce2.yaml`.
  - The hypothesis gets one append-only `version_3` block, with the version-2 bytes kept as an exact prefix.
  - Pre-minted H-NISTBIN-7f61cf and EXP-NISTBIN-921fc9 are **returned unused**. H-NISTBIN-e456ff and EXP-NISTBIN-8d210c stay reserved as the form-(ii) fallback.
  - Why this form: it is the 41f6dc default; it keeps every pointer to EXP-NISTBIN-451dfa valid; the canonical spec is schema-validated; and the dispatcher already verified the same extension in BATCH-2ee1e1.
- **R-TIER.** All five review cards run at review-breakthrough, max, non-degradable (T1).
- **R-SHAPE.** There are five review cards:
  - J2 gets its own validator, so a single joint owns C8 (the 41f6dc limitation).
  - J4 and J6, the likeliest breaks, go to one red team.
  - The controls and the regression go to another red team.
- **R-BLIND.** J9 (TASK-20260925-a43591) is carried by digest for Q1 and Q2, and its Q3 record is kept. The producer is barred from reading the J9 directory. A NEW blind card, J10, covers QM, Q3, QB and QNF.
- **PF-2 fix.** The grep has four dispositions, declared before dispatch: D1 redaction, D2 exclusion, D3 disclosed leak, and D4 non-value match. D4 is closed to two subclasses: D4a identifier and D4b foreign quantity.
- **R-GATE.** Snapshot TASK-20261002-2a3049 owns the pre-review gate: the grep record, plus a value-free amendment written by one fresh gate sub-session.
- **R-PRODUCER-COMPUTE.** The session may run these computations for the producer, and only these:
  - C-1: extract each code block and hash it.
  - C-2: compile it and check it is import-safe.
  - C-3: run the RD-1 Stage-0 coverage code via `__main__`, plus its in-memory omission self-test.
  - C-4: run closed-form abstract-model code. It must not import `joint_balance.py` and must not read anything under `runs/`.
- **R-XCERTBIN.** Applied; it does not fire. No CERTBIN spec freezes a Certicom-row m, a, b, h or r. The only Certicom label is EXP-CERTBIN-4e92d7 line 71, which is a rho work figure inside a dominated_by sentence.
- **R-HOLDS.** The HOLD-F and HOLD-G row-set condition is carried unchanged. No lane-B hold is carried.
- **R-HEAD.** The goal head was edited additively only:
  - a prepended next_action block;
  - one `open_batches` entry appended;
  - one `amendment_history` entry appended, which also records that BATCH-04a6be closed (56ddc25fc4).
  - Scalars are untouched.

## 2. Files written by this Coordinator

- `ledger/decisions/DEC-20261002-0983f2.yaml`
- `coordination/review/nistbin-20261002-f435ab/review-plan.yaml` (REVIEW-NISTBIN-20261002-f435ab)
- `coordination/review/nistbin-20261002-f435ab/blind-inputs.yaml` (J10 inputs)
- `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-f435ab/dispatch_queue.json`
- `ledger/handoffs/TASK-20261002-{034817,144a4f,23efd5,2a3049,3cd1f8,3de9d2,496923,4cb903,84c5d6,b2b9f1,b68b72}.yaml` (eleven files)
- `ledger/goals/GOAL-ECDLP2M-001.yaml` (three additive insertions; nothing deleted)
- this handback

The session still has to create `experiments/EXP-NISTBIN-451dfa/specification.v2-frozen-1ad01ce2.yaml` mechanically (see section 6).

## 3. Cards in order

| n | TASK | what | role | policy | depends_on |
|---|------|------|------|--------|-----------|
| 1 | TASK-20261002-034817 | opening card (completed at writing) | coordinator | coordinator-orchestration-code | none |
| 2 | TASK-20261002-144a4f | opening ledger archive (+ mechanical v2 copy) | coordinator | coordinator-orchestration-code | 1 (runs alone) |
| 3 | TASK-20261002-23efd5 | producer, version 3 (fresh /design-experiment) | coordinator | coordinator-orchestration-code | 2 |
| 4 | TASK-20261002-2a3049 | snapshot + pre-review gate (one gate sub-session) | coordinator | coordinator-orchestration-code | 3 (runs alone) |
| 5 | TASK-20261002-3cd1f8 | J1, J3, J11 | validator (validator-breakthrough) | review-breakthrough max | 3, 4 |
| 6 | TASK-20261002-3de9d2 | J2 (sole C8 owner), J8 | validator (validator-breakthrough) | review-breakthrough max | 3, 4 |
| 7 | TASK-20261002-496923 | J4, J6, PTM-G, PTM-I | red-team (red-team-breakthrough) | review-breakthrough max | 3, 4 |
| 8 | TASK-20261002-4cb903 | J5, J7, PTM-A to PTM-F, rule sweep | red-team (red-team-breakthrough) | review-breakthrough max | 3, 4 |
| 9 | TASK-20261002-84c5d6 | blind J10 | validator (validator-breakthrough) | review-breakthrough max | 3, 4 |
| 10 | TASK-20261002-b2b9f1 | composer, writes DEC-20261002-353743 | coordinator (fresh) | coordinator-orchestration-code | 5, 6, 7, 8, 9 |
| 11 | TASK-20261002-b68b72 | ledger archive + close-lane | coordinator | coordinator-orchestration-code | 5, 6, 7, 8, 9, 10 (runs alone) |

The carried J9 (TASK-20260925-a43591) has no card. Its directory goes into the independence check.

## 4. Identifiers

- **Used:**
  - BATCH-f435ab
  - DEC-20261002-0983f2
  - the eleven TASK ids above
  - REVIEW-NISTBIN-20261002-f435ab (derived from the batch token)
- **Reserved:** DEC-20261002-353743 (composing decision; under `identifiers_reserved`, never in `target_ids`).
- **Returned unused:**
  - DEC-20261002-8857a5
  - DEC-20261002-9f7d0f
  - H-NISTBIN-7f61cf
  - EXP-NISTBIN-921fc9
  - TASK-20261002-b7585b
  - TASK-20261002-e1974c
  - TASK-20261002-e6378c
- **Still reserved from earlier:** H-NISTBIN-e456ff, EXP-NISTBIN-8d210c.
- No further ids are needed.

## 5. Bus pointers to send (after TASK-20261002-144a4f verifies; check the outbox first; never duplicate)

**(a) To `coordinator` (broadcast), as a reply to MSG-20261001-91bf6c**

- thread / in_reply_to: MSG-20261001-91bf6c
- refs: DEC-20261002-0983f2, DEC-20260925-41f6dc, DEC-20260929-7257b2, GOAL-ECDLP2M-001, BATCH-f435ab
- subject: `GOAL-ECDLP2M-001: NISTBIN version-3 revision (DEC-20260925-41f6dc NA-1) opened as BATCH-f435ab on slot 2; do not duplicate`
- body: `Pointer only; no task, no permission. DEC-20261002-0983f2 opens the NISTBIN version-3 revision design batch of DEC-20260925-41f6dc NA-1 as BATCH-f435ab on slot 2 of GOAL-ECDLP2M-001 (DEC-20260929-7257b2 NA-1). This answers MSG-20261001-91bf6c: no other session should open it. Official once TASK-20261002-144a4f's ledger receipt verifies.`

**(b) To the GOAL-SEMBIN-fcb7a2 owner address. Send this ONLY if DEC-20260925-41f6dc NA-3's pointer is not already in the outbox.**

- refs: DEC-20260925-41f6dc, EXP-NISTBIN-451dfa, DEC-20261002-0983f2, BATCH-f435ab, GOAL-SEMBIN-fcb7a2
- subject: `EXP-NISTBIN-451dfa version 2 not approved (DEC-20260925-41f6dc); no threshold handed over; version-3 revision BATCH-f435ab in design`
- body: `Pointer only; no task, no permission. DEC-20260925-41f6dc refused EXP-NISTBIN-451dfa version 2 (revise; zero runs). No D*(m) threshold is handed to GOAL-SEMBIN-fcb7a2 from it. Its revision design batch BATCH-f435ab (DEC-20261002-0983f2) is open; a threshold table could follow only from an approving DEC-20261002-353743 and a later run.`

Record the MSG ids in the next opening brief.

## 6. Session duties before TASK-20261002-144a4f (the opening archive)

1. Make the frozen copy mechanically:

   ```
   git show 93fe59bae4a3b08bc23b1131d6855bc0fe2c1e43:experiments/EXP-NISTBIN-451dfa/specification.yaml > experiments/EXP-NISTBIN-451dfa/specification.v2-frozen-1ad01ce2.yaml
   ```

   Its sha256 must be `1ad01ce2e913fc66c127688f6e718432fbb4de3a4b16174455ceec690ff5942d`. Stop otherwise.
2. Check these hashes, and stop on any mismatch:
   - canonical `experiments/EXP-NISTBIN-451dfa/specification.yaml` = 1ad01ce2…;
   - `ledger/hypotheses/H-NISTBIN-dec5e1.yaml` = `28b713f12fb63b3eebd4a814093bf7311b244d78c0b69cfcd1060d02869db157` (record its byte length as `hypothesis_v2_prefix_bytes` in the receipt);
   - its leading 28166 bytes = b83b2a35…;
   - `specification.v1-frozen-1088d03f.yaml` = 1088d03f….
3. Parse every YAML and JSON file listed in section 2. This agent had no parser. A parse failure goes back to a Coordinator session.
4. Run `git fetch` and merge origin/main (merge, never rebase).
5. `validate_ledger.py` must be at or below 122, with no new error on the staged paths. Also run `check_merge_hygiene.py`.
6. `research_dispatch.py --claims refs` must render: card 1 completed, card 2 ready, the rest blocked.
7. Commit TASK-20261002-144a4f ALONE, staging exactly the 18 paths below, with every record id in the message. Verify, push, open or refresh the PR. Then run `tools/goal_lanes.py open-lane GOAL-ECDLP2M-001 BATCH-f435ab --queue coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-f435ab/dispatch_queue.json --decision DEC-20261002-0983f2 --as <addr> --publish`.

### Opening archive declared paths (TASK-20261002-144a4f; 18 paths, content_at_commit)

1. `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-f435ab/dispatch_queue.json`
2. `coordination/review/nistbin-20261002-f435ab/review-plan.yaml`
3. `coordination/review/nistbin-20261002-f435ab/blind-inputs.yaml`
4. `ledger/goals/GOAL-ECDLP2M-001.yaml`
5. `experiments/EXP-NISTBIN-451dfa/specification.v2-frozen-1ad01ce2.yaml`
6. `ledger/handoffs/TASK-20261002-034817.yaml`
7. `ledger/handoffs/TASK-20261002-144a4f.yaml`
8. `ledger/handoffs/TASK-20261002-23efd5.yaml`
9. `ledger/handoffs/TASK-20261002-2a3049.yaml`
10. `ledger/handoffs/TASK-20261002-3cd1f8.yaml`
11. `ledger/handoffs/TASK-20261002-3de9d2.yaml`
12. `ledger/handoffs/TASK-20261002-496923.yaml`
13. `ledger/handoffs/TASK-20261002-4cb903.yaml`
14. `ledger/handoffs/TASK-20261002-84c5d6.yaml`
15. `ledger/handoffs/TASK-20261002-b2b9f1.yaml`
16. `ledger/handoffs/TASK-20261002-b68b72.yaml`
17. `ledger/decisions/DEC-20261002-0983f2.yaml`
18. `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-f435ab/archives/TASK-20261002-144a4f/ledger-receipt.json`

The archive's record_ids are listed in the queue. EXP-NISTBIN-451dfa is included because of the frozen copy. H-NISTBIN-dec5e1 is not staged here.

## 7. Scratch paths to pre-create (before each launch; name the path in the launch prompt)

- `<scratchpad>/BATCH-f435ab/TASK-20261002-23efd5/` (the session's own C-1 to C-4 runs for the producer)
- `<scratchpad>/BATCH-f435ab/TASK-20261002-3cd1f8/`
- `<scratchpad>/BATCH-f435ab/TASK-20261002-3de9d2/`
- `<scratchpad>/BATCH-f435ab/TASK-20261002-496923/`
- `<scratchpad>/BATCH-f435ab/TASK-20261002-4cb903/`
- `<scratchpad>/BATCH-f435ab/TASK-20261002-84c5d6/`

## 8. Points the dispatcher must not miss

- **Producer TASK-20261002-23efd5:**
  - It must NEVER open `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-b67954/reviews/TASK-20260925-a43591/`. If it does, that is tripwire TA-3.
  - Its launch prompt names the card, its paths and its inputs, and carries no value.
- **Blind card TASK-20261002-84c5d6:**
  - Its launch prompt names only its card, the two blind-input files and its scratch path.
  - Do not dispatch it until `whitelist-grep-v3.yaml` and `blind-inputs-amendment-01.yaml` are committed in TASK-20261002-2a3049's commit.
  - `--blind-history` is uncheckable and must be recorded as such, never as passed.
- **Independence check before the composer:** run it with the five new report directories PLUS `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-b67954/reviews/TASK-20260925-a43591/`. Every report uses per-joint `verdicts` mappings.
- **Composer custody:** the composer receives 12 digests (10 new plus 2 carried). The carried two must equal `070f64da…` (rederivation-report.yaml) and `fb5bffe2…` (computations.json).
