# TASK-20260730-033 — Independent verification of the probe receipts, controls and reported quantities

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-015 `dispatch_queue.json`. **Where they disagree, the queue governs.**

- **Role:** validator — **independent session required**
- **Depends on:** TASK-20260730-032
- **May run concurrently with:** TASK-20260730-034 (disjoint write scopes;
  neither touches the Git index)
- **Archived by:** TASK-20260730-035 (ledger, runs alone)
- **Budget:** 2400 s, 2 GB, `maximum_runs: 1`

## Objective

Verify, independently and from primary sources, that the committed probe
package says what it says and is what it claims to be.

## Required checks

1. **Archive chain against Git.** Re-derive every path SHA-256 in the
   TASK-20260730-032 receipt **from the Git blobs at that commit**, and verify
   the parent. Read the artifacts from Git, not from the working tree.
2. **Recompute before reading.** Compute `R_base(B) = (B + 2) // 3 + 1` and
   `Q(B) = max(60, B + 10)` at all fourteen cells **yourself, before** reading
   the probe's table, and report the comparison.
3. **Re-execute what you can.** At minimum PART A at B = 192 and B = 193, and
   PART B at L12, L13, A12M3 and A13M3, both arms, by calling the committed
   functions directly. **Name exactly which cells you re-executed and which you
   did not.** A difference is a **finding to report**, not a defect to fix.
4. **Check the prohibitions from the driver source, not only the
   deliverables.** Confirm that `_measure_displacement_rank` was not called,
   `main()` was not called, no closure was implemented, no row was shifted,
   permuted or appended, no alpha or rank was computed, no cost quantity was
   produced, no Sage was invoked, no certificate was emitted, no run identifier
   was created, nothing was written under `experiments/`, and `harness/` was not
   modified. **Verify the harness code hashes against Git.**
5. **`include_phi_orbits` was False at every one of the twenty-eight calls** —
   from the per-call record **and** from the source.
6. **Recompute the falsification condition yourself**, by exactly the rule the
   queue states and by no other, and compare against the probe's flag. **A
   disagreement is a BLOCKING finding.**
7. **Recount every count and name its members** (PRED-ID-STR): the twenty-eight
   units, the two structure assertions, the shortfalls, the budget sum
   `2700 + 300 + 2400 + 2400 + 2400 = 10200`, and the nine-path and seven-path
   declarations. The cardinality-not-identity failure has been recorded six
   times in this program and **two instances passed independent review before
   they were caught**.
8. **Check the claim ceiling is respected.** Any probe artifact asserting an
   alpha, a rank, a cost, a diagnosticity verdict, a hypothesis movement, a
   discharge of DEFER-BATCH009-001, an approval of EXP-STR-004, or a
   re-adjudication of BATCH-014 is a **BLOCKING** finding.

## Discipline

- **An unfinished verification is reported as unfinished** — never as PASS and
  never as FAIL.
- **State what you did not check and why.** A check whose object does not exist
  is recorded as **NOT PERFORMED**, never as PASSED.
- **Session independence is required and asserted separately. Model
  independence is not available on this harness and is never claimed**
  (INT-BATCH015-D).
- **Mint no `VAL-*` report identifier.** Two duplicated immutable identifiers
  are already on record in this campaign. Your report is cited **by path and
  task id only** and must say so in its own text.

## Deliverables

```
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-033/validation_report.yaml
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-033/recount_note.md
```

## MAKE NO COMMIT

Write nothing outside your review directory. **Your files must not be committed
before the TASK-20260730-035 ledger commit** — three consecutive batches
committed the post-execution review artifacts one commit early, and that is a
pattern, not an accident.

If you cannot finish inside 2400 s, **stop and report a bounded partial review
naming exactly which checks you did not reach.**
